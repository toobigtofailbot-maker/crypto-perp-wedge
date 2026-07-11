import copy
import json
import shutil
from pathlib import Path

import pytest

from tests.test_validate_variant_sweep_artifacts import _write_valid_fixture
from tools.canon_intake.queue_admission import (
    QueueAdmissionError,
    admit_queue_item,
    approval_core_sha256,
    repo_canonical_json_v1,
)
import tools.canon_intake.queue_admission as queue_admission


REPO_ROOT = Path(__file__).resolve().parents[1]


def _raw(path: Path) -> bytes:
    return path.read_bytes()


def _hash(raw: bytes) -> str:
    import hashlib
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _write(path: Path, value: dict) -> bytes:
    raw = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


def _ref(root: Path, relative: str) -> dict:
    return {"path": relative, "sha256": _hash(_raw(root / relative))}


def _resign(gate_path: Path, frozen: Path, gate: dict, item: dict) -> None:
    gate["approval_core_sha256"] = approval_core_sha256(gate)
    item["gate_q"]["approval_core_sha256"] = gate["approval_core_sha256"]
    item_raw = _write(frozen, item)
    gate["proposed_queue_item"]["bytes_sha256"] = _hash(item_raw)
    _write(gate_path, gate)


def _fixture(tmp_path: Path):
    root = tmp_path / "repo"
    shutil.copytree(REPO_ROOT / "research/schemas", root / "research/schemas")
    spec, vm, sweep, specs, vms, sweeps = _write_valid_fixture(root)
    spec_path = specs / "STRAT-SPEC-9001.strategy_spec.json"
    vm_path = vms / "VM-0001.variant_manifest.json"
    sweep_path = sweeps / "SWEEP-PLAN-0001.sweep_plan.json"
    lineage = {}
    for name in ("source_draft", "review_trail", "eligibility_report", "gate_c_approval"):
        rel = f"scratch/lineage/{name}.json"
        _write(root / rel, {"kind": name})
        lineage[name] = _ref(root, rel)
    dataset_rel = "data/immutable/BTCUSDT-1h.snapshot"
    (root / dataset_rel).parent.mkdir(parents=True)
    (root / dataset_rel).write_bytes(b"immutable dataset fixture\n")
    gate_c_rel = "research/canonical_crossing_audit/strategy_spec_writes.jsonl"
    gate_c_record = {"approval_id": "GATE-C-TEST", "strategy_spec_id": "STRAT-SPEC-9001", "canonical_target_path": "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json", "approved_content_sha256": _hash(_raw(spec_path))}
    gate_c_raw = (json.dumps(gate_c_record, sort_keys=True) + "\n").encode()
    (root / gate_c_rel).parent.mkdir(parents=True)
    (root / gate_c_rel).write_bytes(gate_c_raw)
    gate_c_ref = {"audit_path": gate_c_rel, "line_number": 1, "raw_record_sha256": _hash(gate_c_raw), "gate_c_approval_id": "GATE-C-TEST", "strategy_spec_id": "STRAT-SPEC-9001", "canonical_target_path": "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json"}
    flags = {name: False for name in ("authorizes_dispatch", "authorizes_execution", "authorizes_scheduler_autonomy", "authorizes_candidate_lifecycle", "authorizes_promotion_readiness", "authorizes_paper_live_runtime", "authorizes_notifications")}
    denominator = {"basis": "committed_pre_registered_population_count", "committed_population_count": 2, "variant_manifest_value": 2, "sweep_plan_value": 2, "mismatch_policy": "reject"}
    dataset = {"dataset_id": "BTCUSDT-1h", "snapshot_version": "v1", "path": dataset_rel, "sha256": _hash(_raw(root / dataset_rel)), "market": "BTCUSDT_BINANCE_USDTM_PERPETUAL", "timeframe": "1h", "unresolved_policy": "reject"}
    budget = {"metric": "variant_attempts", "upper_bound": 2, "unit": "attempts", "comparison": "actual_lte_upper_bound", "retries_included": True, "mismatch_or_exceed_policy": "reject"}
    artifact_refs = {"strategy_spec": _ref(root, spec_path.relative_to(root).as_posix()), "variant_manifest": _ref(root, vm_path.relative_to(root).as_posix()), "sweep_plan": _ref(root, sweep_path.relative_to(root).as_posix())}
    approval_id, item_id = "GATE-Q-TEST-001", "QI-20260711-ABCD1234"
    gate_rel = f"research/queue/gate_q_approvals/{approval_id}.gate_q_approval.json"
    item_rel = f"research/queue/admissions/{item_id}.queue_item.json"
    item = {"schema_version": "canon_queue_item_v1", "queue_item_id": item_id, "status": "admitted_non_dispatched", "admitted_at": "2026-07-11T12:00:00Z", "queue_target": "offline_research", "priority": "normal", "artifact_refs": artifact_refs, "denominator": denominator, "dataset": dataset, "budget": budget, "gate_q": {"approval_id": approval_id, "path": gate_rel, "approval_core_sha256": "sha256:" + "0" * 64, "approval_core_hash_scope": "gate_q_approval_core_v1", "approval_core_canonicalization": "repo_canonical_json_v1"}, "lineage": {**lineage, "gate_c_crossing_audit_record": gate_c_ref}, "traceability_hashes": list(dict.fromkeys([r["sha256"] for r in artifact_refs.values()] + [dataset["sha256"]] + [r["sha256"] for r in lineage.values()])), "immutable_posture": {"append_only": True, "overwrite_forbidden": True, "single_use_queue_item_id": True, "single_use_target_path": True}, "authority_flags": flags}
    gate = {"schema_version": "gate_q_queue_admission_approval_v1", "approval_id": approval_id, "approval_artifact_target_path": gate_rel, "approved_by": "Karl", "approved_at": "2026-07-11T11:00:00Z", "approval_scope": "one_append_only_queue_admission", "artifact_refs": {**artifact_refs, "gate_c_crossing_audit_record": gate_c_ref}, "denominator": denominator, "dataset": dataset, "budget": budget, "priority": "normal", "queue_target": "offline_research", "proposed_queue_item": {"queue_item_id": item_id, "target_path": item_rel, "bytes_sha256": "sha256:" + "0" * 64, "byte_encoding": "utf8_exact_file_bytes"}, "lineage": lineage, "approval_core_sha256": "sha256:" + "0" * 64, "approval_core_hash_scope": "gate_q_approval_core_v1", "approval_core_canonicalization": "repo_canonical_json_v1", "exact_content_and_target_only": True, "append_only": True, "single_use_approval_id": True, "authority_flags": flags}
    core = approval_core_sha256(gate)
    gate["approval_core_sha256"] = core
    item["gate_q"]["approval_core_sha256"] = core
    frozen = tmp_path / "frozen.queue_item.json"
    item_raw = _write(frozen, item)
    gate["proposed_queue_item"]["bytes_sha256"] = _hash(item_raw)
    gate_path = root / gate_rel
    _write(gate_path, gate)
    return root, gate_path, frozen, gate, item


def test_repo_canonical_json_key_order_whitespace_and_unicode_are_stable():
    left = json.loads('{ "z": 1, "é": "雪" }')
    right = {"é": "雪", "z": 1}
    assert repo_canonical_json_v1(left) == repo_canonical_json_v1(right)
    assert b"\\u" not in repo_canonical_json_v1(left)


def test_repo_canonical_json_rejects_float_and_mutation_changes_hash():
    with pytest.raises(QueueAdmissionError, match="floating-point"):
        repo_canonical_json_v1({"x": 1.0})
    assert repo_canonical_json_v1({"x": 1}) != repo_canonical_json_v1({"x": 2})


def test_valid_exact_content_admits_once_without_dispatch_outputs(tmp_path):
    root, gate_path, frozen, _, item = _fixture(tmp_path)
    record = admit_queue_item(repo_root=root, gate_q_path=gate_path, proposed_queue_item_path=frozen)
    target = root / f"research/queue/admissions/{item['queue_item_id']}.queue_item.json"
    assert target.read_bytes() == frozen.read_bytes()
    assert record["no_dispatch"] is True and record["no_execution"] is True
    assert len((root / "research/queue/admission_audit/queue_admissions.jsonl").read_text().splitlines()) == 1
    for forbidden in ("runs", "result_populations", "candidates", "scheduler", "dispatch"):
        assert not (root / forbidden).exists()


@pytest.mark.parametrize("mutation,match", [
    (lambda g, i: g.__setitem__("approved_by", "Model"), "schema validation"),
    (lambda g, i: g["authority_flags"].__setitem__("authorizes_dispatch", True), "schema validation"),
    (lambda g, i: g.__setitem__("priority", "expedited"), "approval core"),
    (lambda g, i: i.__setitem__("status", "dispatched"), "schema validation"),
    (lambda g, i: i.__setitem__("admitted_at", "2026-07-12T00:00:00Z"), "bytes hash"),
])
def test_authority_and_exact_binding_mutations_fail_without_write(tmp_path, mutation, match):
    root, gate_path, frozen, gate, item = _fixture(tmp_path)
    mutation(gate, item)
    _write(gate_path, gate); _write(frozen, item)
    with pytest.raises(QueueAdmissionError, match=match):
        admit_queue_item(repo_root=root, gate_q_path=gate_path, proposed_queue_item_path=frozen)
    assert not (root / gate["proposed_queue_item"]["target_path"]).exists()


def test_gate_q_must_be_at_authoritative_path(tmp_path):
    root, gate_path, frozen, gate, _ = _fixture(tmp_path)
    copy_path = tmp_path / "copied-gate.json"; copy_path.write_bytes(gate_path.read_bytes())
    with pytest.raises(QueueAdmissionError, match="authoritative"):
        admit_queue_item(repo_root=root, gate_q_path=copy_path, proposed_queue_item_path=frozen)


def test_later_gate_c_audit_append_does_not_invalidate_line_reference(tmp_path):
    root, gate_path, frozen, _, _ = _fixture(tmp_path)
    audit = root / "research/canonical_crossing_audit/strategy_spec_writes.jsonl"
    with audit.open("ab") as handle: handle.write(b'{"unrelated":true}\n')
    admit_queue_item(repo_root=root, gate_q_path=gate_path, proposed_queue_item_path=frozen)


def test_reuse_and_existing_target_fail_closed(tmp_path):
    root, gate_path, frozen, gate, _ = _fixture(tmp_path)
    admit_queue_item(repo_root=root, gate_q_path=gate_path, proposed_queue_item_path=frozen)
    with pytest.raises(QueueAdmissionError, match="already used"):
        admit_queue_item(repo_root=root, gate_q_path=gate_path, proposed_queue_item_path=frozen)
    assert len((root / "research/queue/admission_audit/queue_admissions.jsonl").read_text().splitlines()) == 1


def test_existing_target_without_audit_is_never_overwritten(tmp_path):
    root, gate_path, frozen, gate, _ = _fixture(tmp_path)
    target = root / gate["proposed_queue_item"]["target_path"]
    target.parent.mkdir(parents=True); target.write_bytes(b"existing")
    with pytest.raises(QueueAdmissionError, match="already exists"):
        admit_queue_item(repo_root=root, gate_q_path=gate_path, proposed_queue_item_path=frozen)
    assert target.read_bytes() == b"existing"


@pytest.mark.parametrize("kind,match", [
    ("denominator", "committed denominator"),
    ("budget", "budget upper bound"),
    ("dataset", "dataset timeframe"),
])
def test_independent_denominator_budget_and_dataset_checks_fail_closed(tmp_path, kind, match):
    root, gate_path, frozen, gate, item = _fixture(tmp_path)
    if kind == "denominator":
        for value in (gate["denominator"], item["denominator"]):
            value["committed_population_count"] = value["variant_manifest_value"] = value["sweep_plan_value"] = 3
    elif kind == "budget":
        gate["budget"]["upper_bound"] = item["budget"]["upper_bound"] = 3
    else:
        gate["dataset"]["timeframe"] = item["dataset"]["timeframe"] = "30m"
    _resign(gate_path, frozen, gate, item)
    with pytest.raises(QueueAdmissionError, match=match):
        admit_queue_item(repo_root=root, gate_q_path=gate_path, proposed_queue_item_path=frozen)


@pytest.mark.parametrize("relative,label", [
    ("research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json", "Strategy Spec hash"),
    ("research/variant_manifests/VM-0001.variant_manifest.json", "Variant Manifest hash"),
    ("research/sweep_plans/SWEEP-PLAN-0001.sweep_plan.json", "Sweep Plan hash"),
    ("data/immutable/BTCUSDT-1h.snapshot", "dataset hash"),
])
def test_referenced_artifact_mutation_fails_before_admission(tmp_path, relative, label):
    root, gate_path, frozen, _, _ = _fixture(tmp_path)
    with (root / relative).open("ab") as handle:
        handle.write(b"mutation")
    with pytest.raises(QueueAdmissionError, match=label):
        admit_queue_item(repo_root=root, gate_q_path=gate_path, proposed_queue_item_path=frozen)


def test_audit_open_failure_rolls_back_new_item(tmp_path, monkeypatch):
    root, gate_path, frozen, gate, _ = _fixture(tmp_path)
    monkeypatch.setattr(queue_admission, "_open_audit", lambda path: (_ for _ in ()).throw(OSError("denied")))
    with pytest.raises(QueueAdmissionError, match="rolled back"):
        admit_queue_item(repo_root=root, gate_q_path=gate_path, proposed_queue_item_path=frozen)
    assert not (root / gate["proposed_queue_item"]["target_path"]).exists()
    assert not (root / "research/queue/admission_audit/queue_admissions.jsonl").exists()


def test_existing_malformed_audit_fails_before_item_write(tmp_path):
    root, gate_path, frozen, gate, _ = _fixture(tmp_path)
    audit = root / "research/queue/admission_audit/queue_admissions.jsonl"
    audit.parent.mkdir(parents=True); audit.write_text("not-json\n", encoding="utf-8")
    with pytest.raises(QueueAdmissionError, match="unreadable"):
        admit_queue_item(repo_root=root, gate_q_path=gate_path, proposed_queue_item_path=frozen)
    assert not (root / gate["proposed_queue_item"]["target_path"]).exists()
