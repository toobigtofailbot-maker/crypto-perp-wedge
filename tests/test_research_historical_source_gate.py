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
@pytest.mark.parametrize("revoked", [True, False])
def test_revoked_custody_reconcile_cannot_commit_or_rerun(hcase, monkeypatch, revoked):
    from tools.research_factory import manual_loop
    from tools.research_factory.mapper import file_hash, write_once

    designation = hcase["designate"]()
    with hcase["authorize"](hcase["attest"](designation)) as lease:
        receipt = lease.consume_for_run(execution=_execution(lease), approval_sha256="sha256:" + "a" * 64)
    if revoked:
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
        expected = "BLOCKED_DATA_USE_OR_REVOKED" if revoked else "BLOCKED_ATOMIC_CUSTODY_COMMIT"
        assert report["withholding_reasons"][0].startswith(expected)
        assert report["runner_calls"] == 0 and report["terminal_commitments"] == []
    assert checkpoint.read_bytes() == before
