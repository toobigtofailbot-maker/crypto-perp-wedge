import copy
import hashlib
import json
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


def semantic_errors(gate, item, *, used_approvals=(), used_ids=(), used_targets=()):
    errors = []
    if gate is None: return ["Gate Q is required"]
    target = gate["proposed_queue_item"]["target_path"]
    expected = f"research/queue/admissions/{item['queue_item_id']}.queue_item.json"
    pairs = (("priority",), ("queue_target",), ("denominator",), ("dataset",), ("budget",))
    for (field,) in pairs:
        if gate[field] != item[field]: errors.append(f"{field} mismatch")
    if gate["proposed_queue_item"]["queue_item_id"] != item["queue_item_id"] or target != expected: errors.append("queue item identity/target mismatch")
    if gate["approval_id"] != item["gate_q"]["approval_id"] or gate["approval_core_sha256"] != item["gate_q"]["approval_core_sha256"]: errors.append("Gate Q binding mismatch")
    if gate["artifact_refs"]["strategy_spec"] != item["artifact_refs"]["strategy_spec"] or gate["artifact_refs"]["variant_manifest"] != item["artifact_refs"]["variant_manifest"] or gate["artifact_refs"]["sweep_plan"] != item["artifact_refs"]["sweep_plan"]: errors.append("artifact hash mismatch")
    d = item["denominator"]
    if len({d["committed_population_count"], d["variant_manifest_value"], d["sweep_plan_value"], item["budget"]["upper_bound"]}) != 1: errors.append("denominator/budget mismatch or exceeded")
    if gate["approval_id"] in used_approvals: errors.append("approval ID reused")
    if item["queue_item_id"] in used_ids or target in used_targets: errors.append("queue item ID/target reused")
    return errors


def test_valid_static_fixtures_and_cross_contract():
    gate, item = load("valid_gate_q.json"), load("valid_queue_item.json")
    assert not list(validator("gate_q_approval.schema.json").iter_errors(gate))
    assert not list(validator("canon_queue_item.schema.json").iter_errors(item))
    assert semantic_errors(gate, item) == []
    core = {key: value for key, value in gate.items() if key not in {"proposed_queue_item", "approval_core_sha256"}}
    core_hash = "sha256:" + hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    queue_hash = "sha256:" + hashlib.sha256((FIXTURES / "valid_queue_item.json").read_bytes()).hexdigest()
    assert gate["approval_core_sha256"] == item["gate_q"]["approval_core_sha256"] == core_hash
    assert gate["proposed_queue_item"]["bytes_sha256"] == queue_hash


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
    assert all(semantic_errors(g, i) for g, i in cases)
    assert semantic_errors(gate, item, used_approvals={gate["approval_id"]})
    assert semantic_errors(gate, item, used_ids={item["queue_item_id"]})
    assert semantic_errors(gate, item, used_targets={gate["proposed_queue_item"]["target_path"]})


def test_contract_contains_no_dispatch_or_runner_surface():
    forbidden = {"command", "runner", "dispatch_request", "scheduler_trigger", "provider", "broker", "exchange", "paper_mode", "live_mode", "promotion_command"}
    for name in ("valid_gate_q.json", "valid_queue_item.json"):
        text = (FIXTURES / name).read_text(encoding="utf-8")
        assert not any(f'"{key}"' in text for key in forbidden)
