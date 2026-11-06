"""D3-2 historical custody: real isolated PostgreSQL, labeled synthetic bytes, no real history.

Every object here is a TEST_ONLY placeholder written to a temporary fixture repository. A pass
proves the gate's ordering/refusal semantics, never a real nonholdout partition or proof A.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import pytest
import test_research_autonomy_postgres as pgtests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from psycopg.conninfo import make_conninfo

import tools.research_autonomy.historical_source_gate as hsg
from tools.lab_pipeline import runner_adapter as adapter
from tools.research_autonomy.envelope import content_hash
from tools.research_autonomy.nonholdout_qualification import (
    Custodian,
    NonHoldoutQualification,
    Revocation,
)
from tools.research_autonomy.store import ResearchAuthorityStore

authority_db = pgtests.authority_db
WINDOWS = sys.platform == "win32"
windows_only = pytest.mark.skipif(not WINDOWS, reason="share-deny-write lease is the Windows storage path")
DAY = 86_400_000


class Tripwire(AssertionError):
    pass


def _write_objects(root: Path, data_identity: str):
    folder = root / "research/data_slices/hist_test_only"
    folder.mkdir(parents=True)
    data = root / "data/processed/d4a/TEST_ONLY.csv"
    data.parent.mkdir(parents=True)
    start, step, count = 1_609_459_200_000, hsg.CADENCE["15m"], 30 * 96
    ohlcv = ("open_time_ms\n" + "\n".join(str(start + i * step) for i in range(count)) + "\n").encode()
    data.write_bytes(ohlcv)
    coverage = {"start_utc": "2021-01-01T00:00:00Z", "end_utc": "2021-01-30T23:45:00Z",
                "row_count": count, "expected_row_count": count}
    normalized = {"sha256": hashlib.sha256(ohlcv).hexdigest(), "path": data.relative_to(root).as_posix()}
    catalog = {"slice_identity": {"data_slice_identity": data_identity},
               "normalized": normalized, "range": coverage, "catalog_version": "v1",
               "source_type": "offline_bulk_or_local_file", "stream": "ohlcv"}
    (folder / "slice.catalog_slice.json").write_text(json.dumps(catalog))
    (folder / "slice.import_report.json").write_text(json.dumps(
        {"label": "TEST_ONLY", "range": coverage, "normalized": normalized}))
    paths = [data, folder / "slice.catalog_slice.json", folder / "slice.import_report.json"]
    objects = []
    for role, path in zip(hsg.ROLES, paths):
        facts = path.stat()
        objects.append({"role": role, "repo_path": path.relative_to(root).as_posix(),
                        "sha256": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(),
                        "byte_length": facts.st_size, "device": facts.st_dev, "inode": facts.st_ino})
    return objects


@pytest.fixture
def hcase(authority_db, tmp_path, monkeypatch):
    from tools.research_autonomy.envelope import envelope_hash, validate_envelope

    original_inputs = pgtests.fixture_inputs

    def historical_inputs(path):
        repo, intent, envelope, request = original_inputs(path)
        payload = envelope.model_dump(mode="json")
        window = "2021-01-01T00:00:00Z/2021-01-31T00:00:00Z"
        payload["search_policy"]["split_protocols"][0]["development_window"] = window
        payload["content_sha256"] = envelope_hash(payload)
        envelope = validate_envelope(payload, repo_sha=envelope.repo_sha)
        split = request.split_protocol.model_copy(update={"development_window": window})
        return repo, intent, envelope, request.model_copy(update={"split_protocol": split})

    monkeypatch.setattr(pgtests, "fixture_inputs", historical_inputs)
    repo, _intent, envelope, _request, store, _, contract = pgtests.opened(authority_db, tmp_path, writer=True)
    monkeypatch.setattr(hsg, "_code_sha", lambda: envelope.repo_sha)
    owner_store = ResearchAuthorityStore(make_conninfo(authority_db[0], options="-c role=cpw_nonholdout_owner"))
    owner, gate_owner = NonHoldoutQualification(owner_store), hsg.HistoricalSourceGate(owner_store, repo)
    key = Ed25519PrivateKey.generate()  # Ephemeral TEST_ONLY issuer; never persisted.
    now = int(time.time() * 1000)
    custodian = Custodian(record_id="CUSTODIAN-HIST-TEST", approved_by="Karl", approval_reference="TEST-ONLY",
                          public_key_hex=key.public_key().public_bytes(serialization.Encoding.Raw,
                                                                       serialization.PublicFormat.Raw).hex(),
                          valid_from_ms=now - 60_000, valid_until_ms=now + 600_000)
    owner.control("custodian", custodian)
    snapshot = store.load_snapshot(contract.campaign_id)
    req = {
        "schema_version": hsg.SCHEMA, "purpose": "historical_nonholdout_study_read",
        "repository": "toobigtofailbot-maker/crypto-perp-wedge", "repo_sha": envelope.repo_sha,
        "campaign_id": contract.campaign_id, "search_id": contract.search_id,
        "contract_hash": contract.contract_hash, "strategy_spec_hash": contract.strategy_spec_hash,
        "original_parent_sha256": "sha256:" + "7" * 64,
        "contamination_domain_id": snapshot.contamination_domain_id, "holdout_id": snapshot.holdout.holdout_id,
        "envelope_sha256": envelope.content_sha256,
        "protocol_sha256": content_hash(envelope.scientific_protocol.model_dump(mode="json")),
        "data_identity": contract.data_identity, "data_version": contract.data_version,
        "instrument": "BTCUSDT", "venue": "Binance USDT-M", "market": "perpetual", "timeframe": "15m",
        "effective_window": {"start_ms": 1_609_459_200_000, "end_ms": 1_609_459_200_000 + 30 * DAY},
        "label_horizon_bars": 0, "fitting": "none",
        "storage": hsg.STORAGE.get(sys.platform, "linux_immutable_flag_v1"),
        "objects": _write_objects(repo, contract.data_identity),
    }

    def designate(record_id="DESIGNATION-HIST-TEST", protected=None, request=None, valid_until=None):
        designation = {"record_id": record_id, "approved_by": "Karl", "approval_reference": "TEST-ONLY",
                       "custodian_id": custodian.record_id, "valid_from_ms": now - 60_000,
                       "valid_until_ms": valid_until or now + 600_000, "request": request or req,
                       "protected_mapping_complete": True,
                       "protected_intervals": protected or [{"start_ms": 1_800_000_000_000,
                                                              "end_ms": 1_800_000_000_000 + DAY}]}
        gate_owner.designate(designation)
        return designation

    def attest(designation, attestation_id="ATTEST-HIST-TEST", signer=key):
        body = hsg.HistoricalAttestation(
            attestation_id=attestation_id, custodian_id=custodian.record_id,
            designation_id=designation["record_id"],
            designation_sha256=content_hash(hsg._parse(hsg.HistoricalDesignation, designation).model_dump(mode="json")),
            request_sha256=content_hash(hsg._parse(hsg.HistoricalRequest, designation["request"]).model_dump(mode="json")),
            valid_from_ms=now - 60_000, valid_until_ms=now + 600_000, signature_hex="0" * 128)
        return body.model_copy(update={"signature_hex": signer.sign(hsg.signing_bytes(body)).hex()})

    gate = hsg.HistoricalSourceGate(store, repo)

    def authorize(attestation, request=None, **changes):
        args = {"attestation": attestation, "request": request or attestation_request[attestation.designation_id],
                    "envelope": envelope, "contract": contract, "repo_sha": envelope.repo_sha}
        return gate.authorize(**(args | changes))

    attestation_request = {}

    def designated(**kw):
        designation = designate(**kw)
        attestation_request[designation["record_id"]] = designation["request"]
        return designation

    return {"repo": repo, "gate": gate, "owner": owner, "key": key, "req": req, "contract": contract, "envelope": envelope,
                "designate": designated, "attest": attest, "authorize": authorize, "store": store}


def _execution(lease):
    out = {o.role + "_path": o.repo_path for o in lease.request.objects}
    out |= {o.role + "_sha256": o.sha256 for o in lease.request.objects}
    return out | {"data_slice_identity": lease.request.data_identity}


@windows_only
def test_valid_custody_leases_bytes_then_single_use_and_commit_check(hcase):
    designation = hcase["designate"]()
    lease = hcase["authorize"](hcase["attest"](designation))
    with lease:
        paths = [o.repo_path for o in lease.request.objects]
        lease.require_preread([hcase["repo"] / p for p in paths])
        target = hcase["repo"] / paths[0]
        with pytest.raises(PermissionError):
            target.open("ab")
        with pytest.raises(PermissionError):
            target.rename(target.with_suffix(".swapped"))
        with pytest.raises(PermissionError):
            target.parent.rename(target.parent.with_name("swapped_dir"))
        assert target.read_bytes().startswith(b"open_time_ms")  # ordinary readers still work
        receipt = lease.consume_for_run(execution=_execution(lease), approval_sha256="sha256:" + "a" * 64)
        assert receipt["not_authority"] is True and receipt["audit_event_id"].startswith("nonholdout-read:")
        with pytest.raises(hsg.Refused, match="ATTESTATION_ALREADY_USED"):
            lease.consume_for_run(execution=_execution(lease), approval_sha256="sha256:" + "a" * 64)
        hcase["gate"].verify_commit(receipt)
    # A used attestation can never be re-leased.
    with pytest.raises(hsg.Refused):
        hcase["authorize"](hcase["attest"](designation))
    hcase["owner"].control("revocation", Revocation(record_id="REVOKE-HIST-TEST", approved_by="Karl",
                                                    approval_reference="TEST-ONLY",
                                                    target_id=designation["record_id"], action="revoke",
                                                    successor_id=None))
    with pytest.raises(hsg.Refused, match=hsg.REVOKED):
        hcase["gate"].verify_commit(receipt)


@windows_only
def test_revocation_after_preread_refuses_runner_use(hcase):
    designation = hcase["designate"]()
    with hcase["authorize"](hcase["attest"](designation)) as lease:
        hcase["owner"].control("revocation", Revocation(record_id="REVOKE-MIDUSE", approved_by="Karl",
                                                        approval_reference="TEST-ONLY",
                                                        target_id=designation["record_id"], action="revoke",
                                                        successor_id=None))
        with pytest.raises(hsg.Refused):
            lease.consume_for_run(execution=_execution(lease), approval_sha256="sha256:" + "a" * 64)
        assert lease.receipt is None


@windows_only
@pytest.mark.parametrize("field,value", [
    ("ohlcv_input_sha256", "sha256:" + "0" * 64),
    ("data_slice_identity", "OTHER-SLICE"),
])
def test_runner_use_must_match_leased_objects(hcase, field, value):
    with hcase["authorize"](hcase["attest"](hcase["designate"]())) as lease, pytest.raises(hsg.Refused):
        lease.consume_for_run(execution=_execution(lease) | {field: value}, approval_sha256="sha256:" + "a" * 64)


def test_wrong_signer_self_signed_or_unknown_designation_refused(hcase):
    designation = hcase["designate"]()
    with pytest.raises(hsg.Refused):
        hcase["authorize"](hcase["attest"](designation, signer=Ed25519PrivateKey.generate()))
    stranger = hcase["attest"](designation).model_copy(update={"designation_id": "UNKNOWN-DESIGNATION"})
    with pytest.raises(hsg.Refused):
        hcase["authorize"](stranger, request=hcase["req"])


def test_protected_overlap_and_study_binding_refused_before_any_open(hcase, monkeypatch):
    window = hcase["req"]["effective_window"]
    overlap = hcase["designate"](record_id="DESIGNATION-OVERLAP",
                                 protected=[{"start_ms": window["end_ms"], "end_ms": window["end_ms"] + DAY}])
    plain = hcase["designate"](record_id="DESIGNATION-PLAIN")
    monkeypatch.setattr(hsg, "_lease", lambda *a, **k: (_ for _ in ()).throw(Tripwire("opened")))
    with pytest.raises(hsg.Refused):  # purge/embargo horizon touches the protected interval
        hcase["authorize"](hcase["attest"](overlap, attestation_id="ATTEST-OVERLAP"))
    from dataclasses import replace

    other = replace(hcase["contract"], search_id="SEARCH-OTHER")
    with pytest.raises(hsg.Refused):
        hcase["authorize"](hcase["attest"](plain, attestation_id="ATTEST-PLAIN"), contract=other)


def test_synthetic_02j_designation_cannot_authorize_history(hcase):
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        hsg._parse(hsg.HistoricalRequest, hcase["req"] | {"schema_version": "cpw_nonholdout_synthetic_v1"})
    with pytest.raises(hsg.Refused):
        hcase["gate"].designate({"record_id": "BAD", "approved_by": "Karl"})


def test_non_owner_cannot_designate(hcase):
    with pytest.raises(hsg.Refused, match="CONTROL_REFUSED"):
        hsg.HistoricalSourceGate(hcase["store"], hcase["repo"]).designate(
            {"record_id": "X", "approved_by": "Karl", "approval_reference": "T", "custodian_id": "C",
             "valid_from_ms": 0, "valid_until_ms": 1, "request": hcase["req"], "protected_mapping_complete": True,
             "protected_intervals": [{"start_ms": 0, "end_ms": 1}]})


@pytest.mark.skipif(WINDOWS, reason="non-Windows storage path")
def test_mutable_storage_without_immutable_flag_fails_closed(hcase):
    with pytest.raises(hsg.Refused):
        hcase["authorize"](hcase["attest"](hcase["designate"]()))


@windows_only
def test_changed_bytes_or_symlink_refused(hcase):
    designation = hcase["designate"]()
    target = hcase["repo"] / hcase["req"]["objects"][2]["repo_path"]
    target.write_text(json.dumps({"label": "TAMPERED"}))
    with pytest.raises(hsg.Refused):
        hcase["authorize"](hcase["attest"](designation))


def test_unsupported_platform_storage_refused():
    with pytest.raises(hsg.Refused, match="UNSUPPORTED_IMMUTABLE_STORAGE"):
        hsg._lease([Path(".")], "unknown_storage_v0")


# ----- D4 runner adapter hook (protected T3) -----

def test_execution_binding_asks_custody_before_any_hash_or_parse(monkeypatch):
    calls = []

    class Deny:
        def require_preread(self, paths):
            calls.append(paths)
            raise hsg.Refused(hsg.REFUSAL)

    def tripwire(*args, **kwargs):
        raise Tripwire("historical byte read before custody")

    monkeypatch.setattr(adapter, "file_sha256", tripwire)
    monkeypatch.setattr(adapter, "read_json", tripwire)
    monkeypatch.setattr(adapter, "_ordinary_input", tripwire)
    with pytest.raises(adapter.RunnerAdapterError, match="BLOCKED_NONHOLDOUT_CUSTODY"):
        adapter._execution_binding(canonical_15m=True, ohlcv_input_path="a", d4_catalog_slice_path="b",
                                   d2_import_report_path="c", deterministic_seed=1, custody=Deny())
    assert calls == []  # duck-typed custody is not a lease


def test_approval_template_forwards_custody_to_binding(monkeypatch):
    seen = {}

    def binding(**kwargs):
        seen.update(kwargs)
        raise Tripwire("stop after custody forwarding")

    monkeypatch.setattr(adapter, "_execution_binding", binding)
    monkeypatch.setattr(adapter, "_route_before_read", lambda *a, **k: None)
    monkeypatch.setattr(adapter, "_sweep_budget_contract", lambda **k: {})
    monkeypatch.setattr(adapter, "read_json", lambda path: {"population_governance": {"declared_population": {"committed_population_count": 1}}})
    marker = object()
    with pytest.raises(Tripwire):
        adapter.approval_template(prepared_strategy_spec_path="scratch/x.strategy_spec.json", prepared_variant_manifest_path="scratch/y.variant_manifest.json",
                                  prepared_sweep_plan_path="scratch/z.sweep_plan.json", bridge_preparation_run_id="p",
                                  product_pipeline_run_id="q",
                                  canonical_15m=True, ohlcv_input_path="a", d4_catalog_slice_path="b",
                                  d2_import_report_path="c", custody=marker)
    assert seen["custody"] is marker


def test_original_route_runner_entry_without_custody_is_refused(monkeypatch):
    import shutil
    import tempfile

    (adapter.REPO_ROOT / "scratch").mkdir(exist_ok=True)
    tmp_path = Path(tempfile.mkdtemp(prefix="hsg-test-", dir=adapter.REPO_ROOT / "scratch"))
    try:
        _runner_entry(tmp_path, monkeypatch)
    finally:
        shutil.rmtree(tmp_path)


def _runner_entry(tmp_path, monkeypatch):
    spec = tmp_path / "STRAT-SPEC-9001.strategy_spec.json"
    spec.write_text("{}")
    vm = tmp_path / "VARIANT-9001.variant_manifest.json"
    sweep = tmp_path / "SWEEP-9001.sweep_plan.json"
    vm.write_text("{}")
    sweep.write_text("{}")
    (tmp_path / "mapping.json").write_text(json.dumps({"schema_version": adapter.ORIGINAL_ROUTE_MAPPING_SCHEMA}))
    monkeypatch.setattr(adapter, "_execution_binding", lambda **k: (_ for _ in ()).throw(Tripwire("read")))
    with pytest.raises(adapter.RunnerAdapterError, match="BLOCKED_NONHOLDOUT_CUSTODY"):
        adapter.run_product_runner_adapter(prepared_strategy_spec_path=spec, prepared_variant_manifest_path=vm,
                                           prepared_sweep_plan_path=sweep, bridge_preparation_run_id="p",
                                           product_pipeline_run_id="q", execute_approval_path=spec,
                                           canonical_15m=True, ohlcv_input_path="a", d4_catalog_slice_path="b",
                                           d2_import_report_path="c")
    (tmp_path / "mapping.json").write_text(json.dumps({"schema_version": "research_factory_mapping_v1"}))
    with pytest.raises(adapter.RunnerAdapterError, match="BLOCKED_NONHOLDOUT_CUSTODY"):
        adapter._route_before_read(spec)


def test_manual_original_route_without_custody_blocks_before_reads(tmp_path, monkeypatch):
    from tests.test_research_factory_mapper import factory_fixture
    from tools.research_factory import manual_loop

    root, store, contract, handoff = factory_fixture(tmp_path)
    for name in ("_execution_binding", "approval_template", "run_product_runner_adapter"):
        monkeypatch.setattr(manual_loop.adapter, name, lambda *a, _n=name, **k: (_ for _ in ()).throw(Tripwire(_n)))
    original = {"idea_id": "IDEA-FIXTURE", "original_hypothesis_sha256": "sha256:" + "1" * 64,
                "fingerprint_sha256": contract.hypothesis_fingerprint,
                "original_parent_sha256": "sha256:" + "2" * 64}
    report = manual_loop.manual_research_loop(
        store=store, handoff=handoff, repo_root=root, preparation_root=root / "scratch/prepared",
        output_root=root / "scratch/out", created_at_utc="2026-10-08T00:00:00Z", human_invocation=True,
        ohlcv_input_path="research/a", d4_catalog_slice_path="research/b", d2_import_report_path="research/c",
        original=original)
    assert report["disposition"] == "research_blocked" and report["runner_calls"] == 0
    assert report["withholding_reasons"][0].startswith("BLOCKED_ORIGINAL_SOURCE_REQUIRED")
    assert report["prepared"] is None


@windows_only
@pytest.mark.parametrize("target", ["designation", "custodian", "attestation", "envelope", "expired"])
def test_use_and_commit_recheck_current_authority(hcase, monkeypatch, target):
    designation = hcase["designate"]()
    attestation = hcase["attest"](designation)
    with hcase["authorize"](attestation) as lease:
        receipt = lease.consume_for_run(execution=_execution(lease), approval_sha256="sha256:" + "a" * 64)
        if target == "envelope":
            envelope = hcase["envelope"]
            hcase["store"].apply_control(envelope, {
                "schema_version": "cpw_bounded_research_envelope_control_v1", "control_action_id": "TEST-REVOKE",
                "envelope_id": envelope.envelope_id, "envelope_version": envelope.envelope_version,
                "envelope_content_sha256": envelope.content_sha256, "repo_sha": envelope.repo_sha,
                "action": "revoke", "approved_by": "Karl", "approved_at": "2026-10-07T01:00:00Z",
                "reason": "TEST_ONLY", "successor": None, "authority": envelope.authority.model_dump()})
        elif target == "expired":
            monkeypatch.setattr(hsg, "_now", lambda conn: attestation.valid_until_ms + 1)
        else:
            identity = {"designation": designation["record_id"], "custodian": attestation.custodian_id,
                        "attestation": attestation.attestation_id}[target]
            hcase["owner"].control("revocation", Revocation(
                record_id="REVOKE-TEST", approved_by="Karl", approval_reference="TEST-ONLY",
                target_id=identity, action="revoke", successor_id=None))
        with pytest.raises(ValueError):
            lease.require_preread([o.repo_path for o in lease.request.objects])
        with pytest.raises(hsg.Refused):
            hcase["gate"].verify_commit(receipt)


@windows_only
def test_revoked_custody_reconcile_cannot_commit_or_rerun(hcase, monkeypatch):
    from tools.research_factory import manual_loop
    from tools.research_factory.mapper import file_hash, write_once

    designation = hcase["designate"]()
    with hcase["authorize"](hcase["attest"](designation)) as lease:
        receipt = lease.consume_for_run(execution=_execution(lease), approval_sha256="sha256:" + "a" * 64)
    hcase["owner"].control("revocation", Revocation(
        record_id="REVOKE-RECONCILE", approved_by="Karl", approval_reference="TEST-ONLY",
        target_id=designation["record_id"], action="revoke", successor_id=None))
    root = hcase["repo"]
    prepared = {"schema_version": manual_loop.ORIGINAL_SCHEMA, "mapping": [{"scientific_trial_id": "TEST"}],
                "scientific_denominator": 1, "proposal_counts": {"accepted": 1}}
    mapping_path = write_once(root / "scratch/mapping.json", prepared)
    binding = {"path": "scratch/mapping.json", "sha256": file_hash(mapping_path)}
    checkpoint = write_once(root / "scratch/checkpoint.json", {
        "mapping_binding": binding, "mapping_sha256": binding["sha256"],
        "contract": hcase["contract"].to_dict(), "summary_binding": {"TEST_ONLY": True}})
    # Isolate reconciliation ordering; native PostgreSQL custody validation is real.
    monkeypatch.setattr(manual_loop, "verify_population", lambda *a: (
        None, {}, {"source_bindings": {"custody_receipt": receipt}}, "sha256:" + "a" * 64))
    monkeypatch.setattr(hcase["store"], "commit_trial_result", lambda *a, **k: pytest.fail("terminal write"))
    monkeypatch.setattr(adapter, "run_product_runner_adapter", lambda **k: pytest.fail("rerun"))
    before = checkpoint.read_bytes()
    for _ in range(2):
        report = manual_loop.reconcile_manual_run(store=hcase["store"], repo_root=root, checkpoint_path=checkpoint)
        expected = "BLOCKED_DATA_USE_OR_REVOKED"
        assert report["withholding_reasons"][0].startswith(expected)
        assert report["runner_calls"] == 0 and report["terminal_commitments"] == []
    assert checkpoint.read_bytes() == before


@pytest.fixture
def atomic_case(hcase, monkeypatch):
    """Real native ledger/custody, stubbed physical population. Never physical proof."""
    from tools.research_factory import evidence
    from tools.research_factory.mapper import file_hash, write_once

    store, root, contract = hcase["store"], hcase["repo"], hcase["contract"]
    designation = hcase["designate"]()
    attestation = hcase["attest"](designation)
    execution = {"TEST_ONLY": True}
    approval_hash = "sha256:" + "a" * 64
    # TEST_ONLY use event: no model or market data access; not a physical receipt proof.
    used = {"phase": "historical_runner_use", "request_sha256": attestation.request_sha256,
            "attestation": attestation.model_dump(mode="json"),
            "execution_sha256": content_hash(execution), "approval_sha256": approval_hash}
    event = "nonholdout-read:" + attestation.attestation_id
    with store._transaction() as conn:
        hcase["gate"]._durable(conn, attestation, hsg._parse(hsg.HistoricalRequest, designation["request"]))
        store._audit(conn, event_id=event, event_type="nonholdout_read", payload=used,
                     campaign=store._campaign(conn, contract.campaign_id))
    receipt = {"schema_version": "cpw_historical_custody_use_receipt_v1", "audit_event_id": event,
               "attestation_id": attestation.attestation_id, "designation_id": designation["record_id"],
               "campaign_id": contract.campaign_id, "request_sha256": attestation.request_sha256,
               "execution_sha256": used["execution_sha256"], "approval_sha256": approval_hash,
               "not_authority": True}
    governor, _, current = pgtests.wave(store, contract)
    accepted = [p for p in governor.proposal_records if p.scientific_trial_id]
    mappings = [{"campaign_id": contract.campaign_id, "search_id": contract.search_id,
                 "contract_hash": contract.contract_hash, "proposal_id": p.proposal_id,
                 "scientific_trial_id": p.scientific_trial_id, "variant_id": f"VAR-{p.proposal_sequence + 1:06d}",
                 "params_fingerprint": p.params_fingerprint} for p in accepted]
    hashes = {k: approval_hash for k in ("spec", "vm", "sweep")}
    prepared = {"schema_version": evidence.ORIGINAL_SCHEMA, "mapping": mappings, "hashes": hashes,
                "scientific_denominator": len(mappings), "proposal_counts": {"accepted": len(mappings), "rejected": 0, "duplicate": 0},
                "original_parent": {"original_parent_sha256": hcase["req"]["original_parent_sha256"]}}
    mapping_path = write_once(root / "scratch/TEST_ONLY_mapping.json", prepared)
    result = {"variant_result_rows": [{"variant_id": m["variant_id"], "outcome_category": "successful"}
                                      for m in mappings]}
    result_path = write_once(root / "scratch/TEST_ONLY_population_stub.json", result)
    summary = {"source_bindings": {"custody_receipt": receipt}, "runner_adapter_run_id": "TEST_ONLY",
               "direct_runner_reconciliation": {"TEST_ONLY": True}}
    summary_path = write_once(root / "scratch/TEST_ONLY_summary_stub.json", summary)
    def binding(p):
        return {"path": p.relative_to(root).as_posix(), "sha256": file_hash(p)}
    def population(repo, value, bound_summary, frozen):
        # Only population is stubbed; native verify_commitment/SQL/custody are unmodified.
        assert frozen == contract and repo == root
        _, read_summary = evidence.bound_json(root, bound_summary)
        _, read_result = evidence.bound_json(root, binding(result_path))
        return result_path, read_result, read_summary, approval_hash
    monkeypatch.setattr(evidence, "verify_population", population)
    payloads = []
    for mapping in mappings:
        payloads.append({**mapping, "attempt_number": 1, "idempotency_id": "TEST_ONLY-" + mapping["variant_id"],
            "classification": "PERFORMANCE_RESULT", "approval_id": "TEST_ONLY", "approval_sha256": approval_hash,
            "prepared_hashes": hashes, "runner_result_sha256": file_hash(result_path),
            "authority_lineage_version": current.lineage_version, "authority_lineage_sha256": current.lineage_sha256,
            "mapping_binding": binding(mapping_path), "summary_binding": binding(summary_path),
            "fold_binding": None, "fold_manifest_binding": None, "fold_sha256": None,
            "robustness_binding": None, "robustness_sha256": None, "purge_bars": 1, "embargo_bars": 1})
    return hcase | {"receipt": receipt, "payloads": payloads, "prepared": prepared, "summary_path": summary_path,
                    "result_path": result_path, "mapping_path": mapping_path}


def revoke_atomic(case):
    case["owner"].control("revocation", Revocation(
        record_id="REVOKE-ATOMIC-TEST", approved_by="Karl", approval_reference="TEST-ONLY",
        target_id=case["receipt"]["designation_id"], action="revoke", successor_id=None))


def test_native_atomic_positive_full_fixture_denominator_replay_recovery(atomic_case, monkeypatch):
    from contextlib import contextmanager

    from tools.research_autonomy.store import _terminal_evidence

    c = atomic_case
    store = c["store"]
    native_transaction = store._transaction
    @contextmanager
    def no_nested_transaction():
        assert _terminal_evidence.get() is None, "nested native transaction would deadlock"
        with native_transaction() as conn:
            yield conn
    monkeypatch.setattr(store, "_transaction", no_nested_transaction)
    original = hsg.HistoricalSourceGate._verify_commit
    observed = []
    def checked(gate, conn, receipt):
        ctx = _terminal_evidence.get()
        assert ctx is not None and ctx[0] is store and ctx[1] is conn
        observed.append(conn.info.backend_pid)
        # Any accidental nested acquisition would fail promptly, not hang the suite.
        conn.execute("SET LOCAL lock_timeout='500ms'")
        return original(gate, conn, receipt)
    monkeypatch.setattr(hsg.HistoricalSourceGate, "_verify_commit", checked)
    rows = []
    for payload in c["payloads"]:
        current = store.load_snapshot(c["contract"].campaign_id)
        payload.update(authority_lineage_version=current.lineage_version, authority_lineage_sha256=current.lineage_sha256)
        before_calls = len(observed)
        row = store.commit_trial_result(payload, repo_root=c["repo"])
        assert observed[before_calls] == observed[before_calls + 1]
        assert store.commit_trial_result(payload, repo_root=c["repo"]) == row
        assert store.load_trial_result(payload["scientific_trial_id"], repo_root=c["repo"]) == row
        rows.append(row)
    assert len(rows) == len(c["payloads"]) == 2 and _terminal_evidence.get() is None
    with store._transaction() as conn:
        assert conn.execute("SELECT count(*) AS n FROM research_authority.trial_result_binding").fetchone()["n"] == 2
        assert conn.execute("SELECT count(*) AS n FROM research_authority.authority_audit WHERE event_type='trial_result'").fetchone()["n"] == 2


@pytest.mark.parametrize("mutation", ["revoke", "holdout", "receipt", "parent", "post_write", "post_holdout", "post_revoke", "post_bytes"])
def test_native_atomic_refusal_and_postwrite_rollback(atomic_case, monkeypatch, mutation):
    from tools.research_factory import evidence

    c = atomic_case
    store, root = c["store"], c["repo"]
    if mutation == "revoke":
        revoke_atomic(c)
    elif mutation == "holdout":
        store.record_holdout_event(c["contract"].search_id, event_id="TEST-ESCAPE", informative_escape=True)
    elif mutation == "receipt":
        value = json.loads(c["summary_path"].read_text())
        value["source_bindings"]["custody_receipt"]["approval_sha256"] = "sha256:" + "f" * 64
        c["summary_path"].write_text(json.dumps(value))
        c["payloads"][0]["summary_binding"]["sha256"] = evidence.file_hash(c["summary_path"])
    elif mutation == "parent":
        value = json.loads(c["mapping_path"].read_text())
        value["original_parent"]["original_parent_sha256"] = "sha256:" + "e" * 64
        c["mapping_path"].write_text(json.dumps(value))
        c["payloads"][0]["mapping_binding"]["sha256"] = evidence.file_hash(c["mapping_path"])
    else:
        if mutation == "post_revoke":
            # TEST_ONLY owner connection permits injecting an owner mutation in this transaction.
            store._dsn = pgtests._test_dsns()[0]
        original = hsg.HistoricalSourceGate._verify_commit
        calls = []
        def changed(gate, conn, receipt):
            calls.append(True)
            if len(calls) == 2:
                if mutation == "post_holdout":
                    conn.execute("UPDATE research_authority.holdout_state SET state='consumed'")
                elif mutation == "post_revoke":
                    raw = Revocation(record_id="REVOKE-POST-TEST", approved_by="Karl", approval_reference="TEST-ONLY",
                        target_id=c["receipt"]["designation_id"], action="revoke", successor_id=None).model_dump(mode="json")
                    value = {"record_id": raw["record_id"], "kind": "revocation", "record": raw, "content_sha256": content_hash(raw)}
                    event_id = "nonholdout:" + raw["record_id"]
                    store._audit(conn, event_id=event_id, event_type="nonholdout_control", payload=value)
                    conn.execute("INSERT INTO research_authority.nonholdout_control VALUES (%s,%s,%s,%s,%s)",
                        (raw["record_id"], "revocation", hsg.canonical_json(raw), content_hash(raw), event_id))
                elif mutation == "post_bytes":
                    c["result_path"].write_text("TEST_ONLY changed after population verification")
                else:
                    raise hsg.Refused(hsg.REVOKED)
            return original(gate, conn, receipt)
        monkeypatch.setattr(hsg.HistoricalSourceGate, "_verify_commit", changed)
    before = pgtests.authority_rows(pgtests._test_dsns()[0])
    with pytest.raises((hsg.Refused, evidence.EvidenceBlocked, pgtests.AuthorityConflict)):
        store.commit_trial_result(c["payloads"][0], repo_root=root)
    assert pgtests.authority_rows(pgtests._test_dsns()[0]) == before


def test_native_atomic_revocation_serializes_then_recovery_refuses(atomic_case, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event

    import psycopg

    from tools.research_autonomy.store import _terminal_evidence

    c = atomic_case
    entered, release, revoke_started = Event(), Event(), Event()
    original = hsg.HistoricalSourceGate._verify_commit
    calls = []
    def paused(gate, conn, receipt):
        calls.append(True)
        if len(calls) == 1:
            entered.set()
            assert release.wait(10), "test coordination failed; not a pass"
        return original(gate, conn, receipt)
    monkeypatch.setattr(hsg.HistoricalSourceGate, "_verify_commit", paused)
    def revoke():
        revoke_started.set()
        revoke_atomic(c)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            committed = pool.submit(c["store"].commit_trial_result, c["payloads"][0], repo_root=c["repo"])
            assert entered.wait(10)
            revoked = pool.submit(revoke)
            assert revoke_started.wait(10)
            with psycopg.connect(pgtests._test_dsns()[0], autocommit=True) as observer:
                for _ in range(200):
                    waiting = observer.execute("SELECT count(*) FROM pg_stat_activity WHERE wait_event='advisory' AND query LIKE 'SELECT pg_advisory_xact_lock(721026002)%'").fetchone()[0]
                    if waiting:
                        break
                    time.sleep(.01)
                assert waiting, "revoker was not observed waiting on native lock"
            release.set()
            row = committed.result(timeout=10)
            revoked.result(timeout=10)
    finally:
        release.set()
    assert row["scientific_trial_id"] == c["payloads"][0]["scientific_trial_id"]
    assert _terminal_evidence.get() is None
    with pytest.raises(hsg.Refused):
        c["store"].load_trial_result(row["scientific_trial_id"], repo_root=c["repo"])
    with pytest.raises(hsg.Refused):
        c["store"].commit_trial_result(c["payloads"][0], repo_root=c["repo"])


def test_native_atomic_rejects_foreign_context_and_standalone_verification(atomic_case):
    from tools.research_factory import evidence

    c = atomic_case
    with pytest.raises(hsg.Refused):
        c["gate"].verify_commit(c["receipt"], _transaction=(c["store"], object(), c["repo"], c["contract"]))
    with pytest.raises(evidence.EvidenceBlocked, match="BLOCKED_ATOMIC_CUSTODY_COMMIT"):
        evidence.verify_commitment(c["repo"], c["payloads"][0], c["contract"])


@pytest.mark.parametrize("mutation", ["holdout", "revoke", "missing_bytes"])
def test_native_atomic_recovery_preserves_history_but_requires_current_evidence(atomic_case, mutation):
    c = atomic_case
    row = c["store"].commit_trial_result(c["payloads"][0], repo_root=c["repo"])
    if mutation == "holdout":
        c["store"].record_holdout_event(c["contract"].search_id, event_id="ESCAPE-AFTER-RESULT", informative_escape=True)
    elif mutation == "revoke":
        revoke_atomic(c)
    else:
        c["result_path"].unlink()
    before = pgtests.authority_rows(pgtests._test_dsns()[0])
    with pytest.raises((hsg.Refused, OSError)):
        c["store"].load_trial_result(row["scientific_trial_id"], repo_root=c["repo"])
    assert pgtests.authority_rows(pgtests._test_dsns()[0]) == before


def test_native_atomic_manual_reconciliation_does_not_rerun_or_duplicate(atomic_case, monkeypatch):
    from tools.research_factory import evidence, manual_loop
    from tools.research_factory.mapper import write_once

    c = atomic_case
    monkeypatch.setattr(manual_loop, "verify_population", evidence.verify_population)
    monkeypatch.setattr(adapter, "run_product_runner_adapter", lambda **k: pytest.fail("must not rerun"))
    mapping_binding = c["payloads"][0]["mapping_binding"]
    path = write_once(c["repo"] / "scratch/TEST_ONLY_checkpoint.json", {
        "mapping_binding": mapping_binding, "mapping_sha256": mapping_binding["sha256"],
        "contract": c["contract"].to_dict(), "summary_binding": c["payloads"][0]["summary_binding"],
        "fold_binding": None, "fold_manifest_binding": None, "robustness_binding": None,
        "purge_bars": 1, "embargo_bars": 1})
    before = path.read_bytes()
    for _ in range(2):
        report = manual_loop.reconcile_manual_run(store=c["store"], repo_root=c["repo"], checkpoint_path=path)
        assert report["disposition"] == "research_insufficient_evidence"
        assert report["runner_calls"] == 0 and len(report["terminal_commitments"]) == 2
        assert path.read_bytes() == before
    with c["store"]._transaction() as conn:
        assert conn.execute("SELECT count(*) AS n FROM research_authority.trial_result_binding").fetchone()["n"] == 2
