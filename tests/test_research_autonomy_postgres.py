"""Physical T3 acceptance in two isolated, separate local test databases."""

import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import psycopg
import pytest
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from test_research_autonomy_contract_builder import fixture_inputs
from tools.research_autonomy import migrations
from tools.research_autonomy.contract_builder import ContractBuilder
from tools.research_autonomy.envelope import canonical_json, content_hash
from tools.research_autonomy.handoff import load_handoff, make_handoff, replay_handoff, write_handoff
from tools.research_autonomy.store import AuthorityConflict, ResearchAuthorityStore
from tools.research_search.governor import SearchGovernor

ROOT = Path(__file__).resolve().parents[1]


class SecretDsn(str):
    def __repr__(self):
        return "<isolated local test PostgreSQL>"


def _test_dsns():
    values = [os.environ.get(k) for k in ("CPW_RESEARCH_AUTHORITY_TEST_DSN", "RESEARCH_MEMORY_TEST_DSN")]
    if not all(values):
        pytest.skip("two isolated local PostgreSQL test variables required")
    identities = []
    for value in values:
        info = conninfo_to_dict(value)
        if info.get("host", "") not in {"localhost", "127.0.0.1", "::1"} or "test" not in info.get("dbname", "").lower():
            pytest.fail("acceptance DSNs must explicitly identify loopback test databases")
        with psycopg.connect(value) as conn:
            row = conn.execute("SELECT current_database(),inet_server_addr()::text,inet_server_port()").fetchone()
            if "test" not in row[0].lower():
                pytest.fail("actual database is not test-only")
            identities.append(row)
    assert identities[0] != identities[1], "logical authority and Research Memory databases must differ"
    return tuple(SecretDsn(v) for v in values)


@pytest.fixture
def authority_db():
    authority, memory = _test_dsns()
    lock = psycopg.connect(authority, autocommit=True)
    lock.execute("SELECT pg_advisory_lock(721026003)")
    try:
        with psycopg.connect(authority, autocommit=True) as conn:
            conn.execute("DROP SCHEMA IF EXISTS research_authority CASCADE")
        assert migrations.apply_migrations(authority).applied == ("0001_research_authority",)
        assert migrations.apply_migrations(authority).already_applied == ("0001_research_authority",)
        with psycopg.connect(authority) as conn:
            conn.execute((ROOT / "tools/research_autonomy/research_authority_writer_role.sql").read_text())
        yield authority, memory
    finally:
        with psycopg.connect(authority, autocommit=True) as conn:
            conn.execute("DROP SCHEMA IF EXISTS research_authority CASCADE")
        lock.execute("SELECT pg_advisory_unlock(721026003)")
        lock.close()


def opened(authority_db, tmp_path, *, writer=False):
    authority, _ = authority_db
    repo, intent, envelope, request = fixture_inputs(tmp_path)
    dsn = SecretDsn(make_conninfo(authority, options="-c role=cpw_research_authority_writer")) if writer else authority
    store = ResearchAuthorityStore(dsn)
    store.register_envelope(envelope)
    store.open_campaign(envelope, campaign_id=request.campaign_id, contamination_domain_id="DOMAIN-FIXTURE", holdout_id="HOLDOUT-FIXTURE", hypothesis_fingerprint=intent.fingerprint_sha256)
    builder = ContractBuilder(store, repo)
    contract = builder.build(intent, envelope, request)
    return repo, intent, envelope, request, store, builder, contract


def wave(store, contract):
    governor = SearchGovernor(contract)
    pre = governor.snapshot()
    governor.propose_wave(2)
    result = store.record_proposal_wave(contract.search_id, pre_snapshot=pre, requested_count=2, records=governor.proposal_records)
    return governor, pre, result


def test_migration_catalog_checksum_and_separation(authority_db, tmp_path, monkeypatch):
    authority, memory = authority_db
    with psycopg.connect(authority) as conn:
        tables = {r[0] for r in conn.execute("SELECT tablename FROM pg_tables WHERE schemaname='research_authority'")}
        assert tables == {"schema_migrations", "envelope_registry", "envelope_control_state", "campaign_state", "search_lineage", "search_budget_reservation", "proposal_record", "scientific_trial", "trial_attempt", "holdout_state", "contamination_edge", "evidence_reference", "authority_audit"}
        triggers = {(r[0],r[1]) for r in conn.execute("""SELECT c.relname,t.tgname FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='research_authority' AND NOT t.tgisinternal""")}
        immutable = {"envelope_registry", "authority_audit", "proposal_record", "scientific_trial", "trial_attempt", "contamination_edge", "evidence_reference", "schema_migrations"}
        guarded = {"campaign_state", "search_lineage", "envelope_control_state", "holdout_state", "search_budget_reservation"}
        expected = {(t,n) for t in immutable for n in ("immutable_rows","immutable_truncate")} | {(t,n) for t in guarded for n in ("guarded_rows","guarded_truncate")}
        expected |= {("authority_audit","hash_chain"),("campaign_state","campaign_integrity"),("authority_audit","audit_current_binding"),("proposal_record","proposal_conservation"),("search_lineage","search_conservation"),("envelope_control_state","control_audit"),("holdout_state","holdout_audit")}
        expected |= {(t,"scientific_insert") for t in ("campaign_state","search_lineage","holdout_state")}
        expected |= {('proposal_record','proposal_audit'),('trial_attempt','attempt_audit'),('search_lineage','search_audit')}
        assert triggers == expected
        constraints=conn.execute("SELECT cl.relname,co.conname,pg_get_constraintdef(co.oid) FROM pg_constraint co JOIN pg_class cl ON cl.oid=co.conrelid WHERE co.connamespace='research_authority'::regnamespace ORDER BY cl.relname,co.conname").fetchall()
        columns=conn.execute("SELECT table_name,column_name,data_type,is_nullable FROM information_schema.columns WHERE table_schema='research_authority' ORDER BY table_name,ordinal_position").fetchall()
        assert len(constraints)==102 and len(columns)==91
        assert content_hash({'constraints':constraints,'columns':columns})=='sha256:9e1b65a6e5210660fe7681bbfe516299c8b295fc5e7dc05d1cfecddfd48d589b'
    altered = tmp_path / "migrations"
    altered.mkdir()
    source = migrations.MIGRATIONS_DIR / "0001_research_authority.sql"
    (altered / source.name).write_bytes(source.read_bytes() + b"\n-- changed bytes\n")
    monkeypatch.setattr(migrations, "MIGRATIONS_DIR", altered)
    with pytest.raises(RuntimeError, match="checksum mismatch"):
        migrations.apply_migrations(authority)


def test_initial_wave_retry_successor_and_reconnect(authority_db, tmp_path):
    repo, intent, envelope, request, store, builder, contract = opened(authority_db, tmp_path)
    assert contract.campaign_proposals_before_search == contract.campaign_scientific_trials_before_search == 0
    initial = store.load_snapshot(contract.campaign_id)
    assert initial.budget.reserved_proposals == 6 and initial.budget.reserved_trials == 4
    governor, pre, after = wave(store, contract)
    assert after.budget.proposals_used == governor.proposal_count
    assert after.budget.scientific_trials_used == governor.scientific_denominator
    assert after.lineage_version == initial.lineage_version + 1
    assert store.record_proposal_wave(contract.search_id, pre_snapshot=pre, requested_count=2, records=governor.proposal_records) == after
    trial = governor.proposal_records[0].scientific_trial_id
    store.record_software_attempt(trial, attempt_number=1)
    store.record_software_attempt(trial, attempt_number=2)
    retried = store.load_snapshot(contract.campaign_id)
    assert retried.budget.scientific_trials_used == after.budget.scientific_trials_used
    with pytest.raises(AuthorityConflict):
        store.record_software_attempt(trial, attempt_number=3)
    closed = store.finalize_search(contract.search_id)
    assert closed.budget.reserved_proposals == closed.budget.reserved_trials == 0
    successor = request.model_copy(update={"search_id":"SEARCH-SUCCESSOR", "parent_search_id":contract.search_id, "reason_for_change":"bounded fixture continuation"})
    child = builder.build(intent, envelope, successor)
    assert child.parent_search_id == contract.search_id
    assert child.campaign_proposals_before_search == closed.budget.proposals_used
    assert child.campaign_scientific_trials_before_search == closed.budget.scientific_trials_used
    assert (child.authority_lineage_version,child.authority_lineage_sha256) == (closed.lineage_version,closed.lineage_sha256)
    SearchGovernor(child).propose_wave(1)
    assert ResearchAuthorityStore(authority_db[0]).load_contract(child.search_id) == child


def test_conflicting_replays_and_envelope_revoke(authority_db, tmp_path):
    _, intent, envelope, request, store, builder, contract = opened(authority_db, tmp_path)
    assert builder.build(intent,envelope,request) == contract
    with pytest.raises(AuthorityConflict, match="conflicting"):
        builder.build(intent,envelope,request.model_copy(update={"seed":3}))
    control = {"schema_version":"cpw_bounded_research_envelope_control_v1","control_action_id":"REVOKE-FIXTURE","envelope_id":envelope.envelope_id,"envelope_version":envelope.envelope_version,"envelope_content_sha256":envelope.content_sha256,"repo_sha":envelope.repo_sha,"action":"revoke","approved_by":"Karl","approved_at":"2026-10-07T01:00:00Z","reason":"fixture only","successor":None,"authority":envelope.authority.model_dump()}
    store.apply_control(envelope,control)
    store.apply_control(envelope,control)
    with pytest.raises(AuthorityConflict, match="active envelope"):
        builder.build(intent,envelope,request)
    with pytest.raises(AuthorityConflict, match="conflicting"):
        store.apply_control(envelope,{**control,"reason":"conflicting"})


def test_parallel_successors_cannot_oversubscribe(authority_db, tmp_path):
    _, intent, envelope, request, store, builder, contract = opened(authority_db,tmp_path)
    wave(store,contract)
    store.finalize_search(contract.search_id)
    before=store.load_snapshot(contract.campaign_id)
    barrier=Barrier(2)
    def start(index):
        req=request.model_copy(update={"search_id":f"SEARCH-CHILD-{index}","parent_search_id":contract.search_id,"reason_for_change":"concurrent bounded continuation"})
        barrier.wait()
        try:
            return builder.build(intent,envelope,req)
        except (ValueError,psycopg.Error):
            return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(start,[1,2]))
    assert sum(r is not None for r in results)==1
    after=store.load_snapshot(contract.campaign_id)
    assert after.budget.search_count==before.budget.search_count+1
    assert after.budget.proposals_used+after.budget.reserved_proposals<=after.budget.proposal_ceiling
    assert after.budget.scientific_trials_used+after.budget.reserved_trials<=after.budget.trial_ceiling


def test_holdout_consumption_propagates_without_freshness_restore(authority_db,tmp_path):
    _, intent, envelope, request, store, builder, contract=opened(authority_db,tmp_path)
    assert store.load_snapshot(contract.campaign_id).holdout.state=='unexposed'
    isolated=store.record_holdout_event(contract.search_id,event_id='HOLDOUT-ATTEMPT',informative_escape=False)
    assert isolated.state=='attempted_isolated' and not isolated.contaminated
    consumed=store.record_holdout_event(contract.search_id,event_id='HOLDOUT-ESCAPE',informative_escape=True)
    assert consumed.state=='consumed' and consumed.contaminated
    store.finalize_search(contract.search_id)
    successor=request.model_copy(update={"search_id":"SEARCH-CONTAMINATED","parent_search_id":contract.search_id,"reason_for_change":"cannot restore freshness"})
    with pytest.raises(ValueError,match='contamination'):
        builder.build(intent,envelope,successor)
    with pytest.raises(AuthorityConflict,match='consumed'):
        store.record_holdout_event(contract.search_id,event_id='HOLDOUT-RETRY',informative_escape=False)
    with psycopg.connect(authority_db[0]) as conn:
        with pytest.raises(psycopg.Error),conn.transaction():
            conn.execute("UPDATE research_authority.holdout_state SET state='unexposed'")


def test_memory_rebuild_and_cpw_deletion_do_not_reset_authority(authority_db,tmp_path):
    from tools.research_memory.migrations import apply_migrations
    from tools.research_memory.repository import ResearchMemoryRepository
    repo,intent,envelope,request,store,builder,contract=opened(authority_db,tmp_path)
    governor,pre,_=wave(store,contract)
    handoff=make_handoff(store=store,contract=contract,intent_sha256=intent.content_sha256,pre_wave_snapshot=pre,requested_wave_count=2,proposal_records=governor.proposal_records,resulting_denominator=governor.scientific_denominator,repo_root=repo)
    path=write_handoff(handoff,repo_root=repo)
    replay_handoff(load_handoff(path,repo_root=repo),store=store,repo_root=repo)
    before=store.load_snapshot(contract.campaign_id)
    import shutil
    cpw=(repo/'.cpw').resolve(strict=True)
    assert cpw.is_relative_to(repo.resolve()) and cpw==repo.resolve()/'.cpw'
    shutil.rmtree(cpw)
    assert store.load_snapshot(contract.campaign_id)==before
    memory=authority_db[1]
    apply_migrations(memory)
    with ResearchMemoryRepository.connect(memory) as repository:
        fixture_repo=ROOT/'tests/fixtures/research_memory/repo'
        repository.refresh_from_repo(fixture_repo)
        assert repository.refresh_from_repo(fixture_repo,rebuild=True)['memory_records']>=2
    # The established PostgreSQL test bootstrap drops only the test schema,
    # then rebuilds through the unchanged migration/repository owners.
    with psycopg.connect(memory,autocommit=True) as conn:
        conn.execute('DROP SCHEMA research_memory CASCADE')
    apply_migrations(memory)
    with ResearchMemoryRepository.connect(memory) as repository:
        assert repository.refresh_from_repo(fixture_repo,rebuild=True)['memory_records']>=2
    assert store.load_snapshot(contract.campaign_id)==before
    store.record_holdout_event(contract.search_id,event_id='ISOLATED-BEFORE-RESET',informative_escape=False)
    holdout_before=store.load_snapshot(contract.campaign_id)
    with ResearchMemoryRepository.connect(memory) as repository:
        repository.refresh_from_repo(fixture_repo,rebuild=True)
    assert store.load_snapshot(contract.campaign_id)==holdout_before
    closed=store.finalize_search(contract.search_id)
    child=builder.build(intent,envelope,request.model_copy(update={"search_id":"SEARCH-AFTER-RESET","parent_search_id":contract.search_id,"reason_for_change":"memory reset preserves history"}))
    assert child.campaign_scientific_trials_before_search==closed.budget.scientific_trials_used
    store.record_holdout_event(child.search_id,event_id='ESCAPED-BEFORE-RESET',informative_escape=True)
    consumed=store.load_snapshot(child.campaign_id)
    with psycopg.connect(memory,autocommit=True) as conn:
        conn.execute('DROP SCHEMA research_memory CASCADE')
    apply_migrations(memory)
    with ResearchMemoryRepository.connect(memory) as repository:
        repository.refresh_from_repo(fixture_repo,rebuild=True)
    assert store.load_snapshot(child.campaign_id)==consumed
    assert consumed.holdout.state=='consumed' and consumed.holdout.contaminated


def test_writer_role_operations_and_denied_privileges(authority_db,tmp_path):
    repo,intent,envelope,request,store,builder,contract=opened(authority_db,tmp_path,writer=True)
    governor,_,_=wave(store,contract)
    store.record_software_attempt(governor.proposal_records[0].scientific_trial_id,attempt_number=1)
    store.attach_evidence(contract.search_id,reference_id='WRITER-EVIDENCE',binding=request.data_evidence,repo_root=repo)
    store.record_holdout_event(contract.search_id,event_id='WRITER-ISOLATED',informative_escape=False)
    store.finalize_search(contract.search_id)
    child=builder.build(intent,envelope,request.model_copy(update={'search_id':'SEARCH-WRITER-CHILD','parent_search_id':contract.search_id,'reason_for_change':'bounded writer continuation'}))
    wave(store,child)
    store.record_holdout_event(child.search_id,event_id='WRITER-ESCAPE',informative_escape=True)
    store.finalize_search(child.search_id)
    authority=authority_db[0]
    with psycopg.connect(authority,autocommit=True) as conn:
        role=conn.execute("SELECT rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolinherit,rolbypassrls FROM pg_roles WHERE rolname='cpw_research_authority_writer'").fetchone()
        assert role==(False,False,False,False,False,False)
        # Fixtures stand in for unrelated schemas in this logical DB only.
        conn.execute('CREATE SCHEMA research_memory')
        conn.execute('CREATE TABLE research_memory.denied_fixture(id integer)')
        conn.execute('CREATE SCHEMA hermes_broker')
        conn.execute('CREATE TABLE hermes_broker.denied_fixture(id integer)')
        conn.execute('SET ROLE cpw_research_authority_writer')
        denied=["CREATE DATABASE cpw_forbidden_test", "CREATE SCHEMA forbidden_fixture", "INSERT INTO research_memory.denied_fixture VALUES(1)","INSERT INTO hermes_broker.denied_fixture VALUES(1)","CREATE ROLE forbidden_fixture NOLOGIN", "ALTER ROLE cpw_research_authority_writer CREATEDB","DROP SCHEMA research_authority CASCADE", "ALTER TABLE research_authority.authority_audit DISABLE TRIGGER ALL"]
        for statement in denied:
            with pytest.raises(psycopg.Error):
                conn.execute(statement)
        conn.execute('RESET ROLE')
        conn.execute('DROP SCHEMA research_memory CASCADE')
        conn.execute('DROP SCHEMA hermes_broker CASCADE')


def test_immutable_and_guarded_database_operations(authority_db,tmp_path):
    repo,intent,envelope,request,store,builder,contract=opened(authority_db,tmp_path)
    governor,pre,_=wave(store,contract)
    store.record_software_attempt(governor.proposal_records[0].scientific_trial_id,attempt_number=1)
    store.attach_evidence(contract.search_id,reference_id='EVIDENCE-FIXTURE',binding=request.data_evidence,repo_root=repo)
    store.record_holdout_event(contract.search_id,event_id='IMMUTABILITY-ESCAPE',informative_escape=True)
    from psycopg import sql
    with psycopg.connect(authority_db[0],autocommit=True) as conn:
        immutable={'envelope_registry':'envelope_id','authority_audit':'event_id','proposal_record':'proposal_id','scientific_trial':'scientific_trial_id','trial_attempt':'attempt_number','contamination_edge':'event_id','evidence_reference':'reference_id','schema_migrations':'version'}
        for table,column in immutable.items():
            for statement in (
                sql.SQL('UPDATE research_authority.{} SET {}={}').format(sql.Identifier(table),sql.Identifier(column),sql.Identifier(column)),
                sql.SQL('DELETE FROM research_authority.{}').format(sql.Identifier(table)),
                sql.SQL('TRUNCATE research_authority.{} CASCADE').format(sql.Identifier(table)),
            ):
                with pytest.raises(psycopg.Error):
                    conn.execute(statement)
        for statement in (
            "UPDATE research_authority.campaign_state SET proposal_ceiling=proposal_ceiling+1",
            "UPDATE research_authority.campaign_state SET proposals_used=proposals_used-1",
            "UPDATE research_authority.envelope_control_state SET state='revoked',control_action='{}'",
            "UPDATE research_authority.holdout_state SET state='unexposed'",
            "UPDATE research_authority.search_lineage SET contract_sha256='sha256:'||repeat('f',64)",
            "UPDATE research_authority.search_budget_reservation SET proposals_remaining=proposals_remaining+1",
            "UPDATE research_authority.campaign_state SET lineage_sha256=lineage_sha256",
            "UPDATE research_authority.campaign_state SET state='closed'",
        ):
            with pytest.raises(psycopg.Error):
                conn.execute(statement)


def test_new_campaign_cannot_rebind_a_consumed_holdout_domain(authority_db,tmp_path):
    repo,intent,envelope,request,store,builder,contract=opened(authority_db,tmp_path)
    store.record_holdout_event(contract.search_id,event_id='DOMAIN-ESCAPE',informative_escape=True)
    with pytest.raises(AuthorityConflict,match='domain/holdout'):
        store.open_campaign(envelope,campaign_id='CAMPAIGN-RENAME',contamination_domain_id='DOMAIN-RENAME',holdout_id='HOLDOUT-FIXTURE',hypothesis_fingerprint=intent.fingerprint_sha256)
    snapshot=store.open_campaign(envelope,campaign_id='CAMPAIGN-NEW',contamination_domain_id='DOMAIN-FIXTURE',holdout_id='HOLDOUT-FIXTURE',hypothesis_fingerprint=intent.fingerprint_sha256)
    assert snapshot.holdout.contaminated and snapshot.holdout.state=='consumed'
    renamed=request.model_copy(update={'campaign_id':'CAMPAIGN-NEW','search_id':'SEARCH-RENAME'})
    with pytest.raises(ValueError,match='contamination'):
        builder.build(intent,envelope,renamed)


def test_registered_replacement_and_exact_idempotency(authority_db,tmp_path):
    _,intent,envelope,request,store,_,contract=opened(authority_db,tmp_path)
    from tools.research_autonomy.envelope import envelope_hash,validate_envelope
    replacement=envelope.model_dump(mode='json')
    replacement['envelope_version']=2
    replacement['content_sha256']=envelope_hash(replacement)
    replacement=validate_envelope(replacement,repo_sha=envelope.repo_sha)
    store.register_envelope(replacement)
    control={'schema_version':'cpw_bounded_research_envelope_control_v1','control_action_id':'REPLACE-FIXTURE','envelope_id':envelope.envelope_id,'envelope_version':1,'envelope_content_sha256':envelope.content_sha256,'repo_sha':envelope.repo_sha,'action':'replace','approved_by':'Karl','approved_at':'2026-10-07T02:00:00Z','reason':'synthetic human replacement','successor':{'envelope_id':replacement.envelope_id,'envelope_version':2,'content_sha256':replacement.content_sha256},'authority':envelope.authority.model_dump()}
    before=store.load_snapshot(contract.campaign_id)
    store.apply_control(envelope,control)
    store.apply_control(envelope,control)
    assert store.load_snapshot(contract.campaign_id)==before
    with psycopg.connect(authority_db[0]) as conn:
        assert conn.execute("SELECT state FROM research_authority.envelope_control_state WHERE envelope_id=%s AND envelope_version=1",(envelope.envelope_id,)).fetchone()[0]=='replaced'
        assert conn.execute("SELECT count(*) FROM research_authority.authority_audit WHERE event_id='control:REPLACE-FIXTURE'").fetchone()[0]==1
    conflicting=envelope.model_dump(mode='json')
    conflicting['approved_at']='2026-10-07T03:00:00Z'
    conflicting['content_sha256']=envelope_hash(conflicting)
    with pytest.raises(AuthorityConflict):
        store.register_envelope(validate_envelope(conflicting,repo_sha=envelope.repo_sha))
