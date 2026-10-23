"""Offline matrix acceptance controls; physical Rust/Redis proof is separately mandatory."""
import copy
import importlib.util
from pathlib import Path

import pytest


PATH = Path(__file__).resolve().parents[1] / "tools/nautilus_adapter/v2_history_route/run_proof.py"
SPEC = importlib.util.spec_from_file_location("n2_04_controller", PATH)
proof = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proof)


def refusal():
    return {"pid": 321, "process": {"pid": 321}, "exit": 1,
            "changed_keys": [], "content_changed_keys": [],
            "source_files_before": {"native.redb": "sha"},
            "source_files_after": {"native.redb": "sha"},
            "admission": {"pid": 321, "decision": "RECONCILIATION_REQUIRED", "error": "PAIR_MISMATCH"}}


def test_clean_fail_closed_refusal_is_accepted():
    assert proof.require_result(refusal(), reason="PAIR_MISMATCH")


@pytest.mark.parametrize("mutation", ["raw_write", "semantic_write", "source_write", "wrong_pid",
                                    "wrong_decision", "wrong_exit", "wrong_error"])
def test_mutation_and_false_refusal_evidence_cannot_pass(mutation):
    row = refusal()
    if mutation == "raw_write":
        row["changed_keys"] = ["account"]
    elif mutation == "semantic_write":
        row["content_changed_keys"] = ["order"]
    elif mutation == "source_write":
        row["source_files_after"]["native.redb"] = "changed"
    elif mutation == "wrong_pid":
        row["process"]["pid"] = 322
    elif mutation == "wrong_decision":
        row["admission"]["decision"] = "RECOVERY_ADMITTED_SEALED"
    elif mutation == "wrong_exit":
        row["exit"] = 0
    else:
        row["admission"]["error"] = "UNRELATED_ERROR"
    with pytest.raises(AssertionError):
        proof.require_result(row, reason="PAIR_MISMATCH")


def admitted():
    row = refusal()
    row["exit"] = 0
    row["admission"].update(decision="RECOVERY_ADMITTED_SEALED", error=None)
    row["native_receipt"] = {"equal": True, "tail_replay_invoked": False, "bus_publishes": [],
                             "bus_sends": [], "bus_responses": 0, "registered_endpoints": [],
                             "duplicate": {"position_id": "native-position", "unchanged": True,
                                           "attempts": [{"unchanged": True, "native_error": "duplicate trade"}] * 3}}
    return row


@pytest.mark.parametrize("mutation", ["lost_identity", "tail_replay", "new_order", "new_response",
                                    "new_endpoint", "null_association", "double_economics", "missing_probe"])
def test_incomplete_recovery_and_duplicate_evidence_cannot_pass(mutation):
    row = copy.deepcopy(admitted())
    native = row["native_receipt"]
    if mutation == "lost_identity":
        native["equal"] = False
    elif mutation == "tail_replay":
        native["tail_replay_invoked"] = True
    elif mutation == "new_order":
        native["bus_sends"] = ["ExecEngine.execute"]
    elif mutation == "new_response":
        native["bus_responses"] = 1
    elif mutation == "new_endpoint":
        native["registered_endpoints"] = ["ExecEngine.execute"]
    elif mutation == "null_association":
        native["duplicate"]["position_id"] = None
    elif mutation == "double_economics":
        native["duplicate"]["attempts"][0]["unchanged"] = False
    else:
        native["duplicate"]["attempts"].pop()
    with pytest.raises(AssertionError):
        proof.require_result(row, admitted=True, duplicate=True)


def test_complete_admission_requires_exact_native_and_duplicate_receipts():
    assert proof.require_result(admitted(), admitted=True, duplicate=True)
