import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from jsonschema import Draft7Validator, RefResolver

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "research/schemas"
FIXTURES = ROOT / "scratch/WP-CANON-QUEUE-CONTROL-PLANE-DESIGN-LOCK-03A/fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def validator(name):
    schema = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
    return Draft7Validator(schema, resolver=RefResolver((SCHEMAS / name).as_uri(), schema))


def canonical_json_v1(value):
    def reject_floats(node):
        if isinstance(node, float): raise ValueError("repo_canonical_json_v1 forbids floating-point values")
        if isinstance(node, dict):
            for child in node.values(): reject_floats(child)
        elif isinstance(node, list):
            for child in node: reject_floats(child)
    reject_floats(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def semantic_errors(gate, item, *, used_approvals=(), used_ids=(), used_targets=()):
    errors = []
    if gate is None: return ["Gate Q is required"]
    target = gate["proposed_queue_item"]["target_path"]
    expected = f"research/queue/admissions/{item['queue_item_id']}.queue_item.json"
    gate_path = f"research/queue/gate_q_approvals/{gate['approval_id']}.gate_q_approval.json"
    pairs = (("priority",), ("queue_target",), ("denominator",), ("dataset",), ("budget",))
    for (field,) in pairs:
        if gate[field] != item[field]: errors.append(f"{field} mismatch")
    if gate["proposed_queue_item"]["queue_item_id"] != item["queue_item_id"] or target != expected: errors.append("queue item identity/target mismatch")
    if gate["approval_id"] != item["gate_q"]["approval_id"] or gate["approval_core_sha256"] != item["gate_q"]["approval_core_sha256"]: errors.append("Gate Q binding mismatch")
    if gate["approval_artifact_target_path"] != gate_path or item["gate_q"]["path"] != gate_path: errors.append("Gate Q identity/path mismatch")
    if gate["artifact_refs"]["strategy_spec"] != item["artifact_refs"]["strategy_spec"] or gate["artifact_refs"]["variant_manifest"] != item["artifact_refs"]["variant_manifest"] or gate["artifact_refs"]["sweep_plan"] != item["artifact_refs"]["sweep_plan"]: errors.append("artifact hash mismatch")
    d = item["denominator"]
    if len({d["committed_population_count"], d["variant_manifest_value"], d["sweep_plan_value"], item["budget"]["upper_bound"]}) != 1: errors.append("denominator/budget mismatch or exceeded")
    admitted_date = datetime.fromisoformat(item["admitted_at"].replace("Z", "+00:00")).astimezone(timezone.utc).strftime("%Y%m%d")
    if item["queue_item_id"].split("-")[1] != admitted_date: errors.append("queue item date/admitted_at mismatch")
    if gate["approval_id"] in used_approvals: errors.append("approval ID reused")
    if item["queue_item_id"] in used_ids or target in used_targets: errors.append("queue item ID/target reused")
    return errors


def test_valid_static_fixtures_and_cross_contract():
    gate, item = load("valid_gate_q.json"), load("valid_queue_item.json")
    assert not list(validator("gate_q_approval.schema.json").iter_errors(gate))
    assert not list(validator("canon_queue_item.schema.json").iter_errors(item))
    assert semantic_errors(gate, item) == []
    core = {key: value for key, value in gate.items() if key not in {"proposed_queue_item", "approval_core_sha256"}}
    core_hash = "sha256:" + hashlib.sha256(canonical_json_v1(core)).hexdigest()
    queue_hash = "sha256:" + hashlib.sha256((FIXTURES / "valid_queue_item.json").read_bytes()).hexdigest()
    assert gate["approval_core_sha256"] == item["gate_q"]["approval_core_sha256"] == core_hash
    assert gate["proposed_queue_item"]["bytes_sha256"] == queue_hash


def test_repo_canonical_json_v1_is_exact_and_stable():
    left = {"z": [True, None, 2], "é": "雪", "a": {"b": "x"}}
    right = json.loads(' { "a" : { "b" : "x" }, "é" : "雪", "z" : [ true, null, 2 ] } ')
    expected = '{"a":{"b":"x"},"z":[true,null,2],"é":"雪"}'.encode("utf-8")
    assert canonical_json_v1(left) == canonical_json_v1(right) == expected
    assert hashlib.sha256(canonical_json_v1(left)).digest() == hashlib.sha256(canonical_json_v1(right)).digest()
    mutated = copy.deepcopy(left); mutated["a"]["b"] = "y"
    assert hashlib.sha256(canonical_json_v1(mutated)).digest() != hashlib.sha256(canonical_json_v1(left)).digest()
    with pytest.raises(ValueError): canonical_json_v1({"floating": 1.5})


@pytest.mark.parametrize("document,path,value", [
    ("gate", ("approved_by",), "someone_else"), ("gate", ("queue_target",), "paper"),
    ("gate", ("priority",), "urgent"), ("gate", ("authority_flags", "authorizes_dispatch"), True),
    ("item", ("authority_flags", "authorizes_execution"), True),
])
def test_schema_rejects_wrong_actor_unbounded_vocab_and_authority(document, path, value):
    gate, item = load("valid_gate_q.json"), load("valid_queue_item.json")
    obj = gate if document == "gate" else item
    for key in path[:-1]: obj = obj[key]
    obj[path[-1]] = value
    name = "gate_q_approval.schema.json" if document == "gate" else "canon_queue_item.schema.json"
    assert list(validator(name).iter_errors(gate if document == "gate" else item))


def test_missing_gate_hash_target_denominator_dataset_budget_and_reuse_fail_closed():
    gate, item = load("valid_gate_q.json"), load("valid_queue_item.json")
    assert semantic_errors(None, item)
    cases = []
    x = copy.deepcopy(item); x["artifact_refs"]["strategy_spec"]["sha256"] = "sha256:" + "0" * 64; cases.append((gate, x))
    x = copy.deepcopy(item); x["queue_item_id"] = "QI-20260711-TEST0002"; cases.append((gate, x))
    x = copy.deepcopy(item); x["denominator"]["sweep_plan_value"] = 7; cases.append((gate, x))
    x = copy.deepcopy(item); x["dataset"]["snapshot_version"] = "other"; cases.append((gate, x))
    x = copy.deepcopy(item); x["budget"]["upper_bound"] = 9; cases.append((gate, x))
    x = copy.deepcopy(item); x["admitted_at"] = "2026-07-12T00:00:00Z"; cases.append((gate, x))
    x = copy.deepcopy(item); x["gate_q"]["path"] = "fixtures/substitute.json"; cases.append((gate, x))
    assert all(semantic_errors(g, i) for g, i in cases)
    assert semantic_errors(gate, item, used_approvals={gate["approval_id"]})
    assert semantic_errors(gate, item, used_ids={item["queue_item_id"]})
    assert semantic_errors(gate, item, used_targets={gate["proposed_queue_item"]["target_path"]})


def test_contract_contains_no_dispatch_or_runner_surface():
    forbidden = {"command", "runner", "dispatch_request", "scheduler_trigger", "provider", "broker", "exchange", "paper_mode", "live_mode", "promotion_command"}
    for name in ("valid_gate_q.json", "valid_queue_item.json"):
        text = (FIXTURES / name).read_text(encoding="utf-8")
        assert not any(f'"{key}"' in text for key in forbidden)


def test_queue_admission_audit_record_schema_and_reuse_identity():
    gate, item = load("valid_gate_q.json"), load("valid_queue_item.json")
    h = lambda c: "sha256:" + hashlib.sha256(c).hexdigest()
    record = {"schema_version":"queue_admission_audit_record_v1","audit_record_id":"QAUDIT-" + item["queue_item_id"],"queue_item_id":item["queue_item_id"],"queue_item_path":gate["proposed_queue_item"]["target_path"],"queue_item_sha256":h((FIXTURES/"valid_queue_item.json").read_bytes()),"gate_q_approval_id":gate["approval_id"],"gate_q_approval_path":gate["approval_artifact_target_path"],"gate_q_approval_file_sha256":h((FIXTURES/"valid_gate_q.json").read_bytes()),"gate_q_approval_core_sha256":gate["approval_core_sha256"],"strategy_spec_id":"STRAT-SPEC-9999","strategy_spec_path":"research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json","strategy_spec_sha256":item["artifact_refs"]["strategy_spec"]["sha256"],"variant_manifest_path":item["artifact_refs"]["variant_manifest"]["path"],"variant_manifest_sha256":item["artifact_refs"]["variant_manifest"]["sha256"],"sweep_plan_path":item["artifact_refs"]["sweep_plan"]["path"],"sweep_plan_sha256":item["artifact_refs"]["sweep_plan"]["sha256"],"admitted_at":item["admitted_at"],"writer_version":"fixture-v1","validation_outcome":"passed_before_admission","no_dispatch":True,"no_execution":True}
    assert not list(validator("queue_admission_audit_record.schema.json").iter_errors(record))
    assert {record["gate_q_approval_id"], record["queue_item_id"], record["queue_item_path"]}
