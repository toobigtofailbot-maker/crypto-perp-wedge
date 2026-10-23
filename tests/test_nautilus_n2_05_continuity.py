"""Offline N2-05 continuity acceptance controls; physical Rust/Redis proof is separately mandatory."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


PATH = Path(__file__).resolve().parents[1] / "tools/nautilus_adapter/v2_history_route/run_proof.py"
SPEC = importlib.util.spec_from_file_location("n2_05_controller", PATH)
proof = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proof)

QUOTE = json.dumps({"type": "QuoteTick", "instrument_id": "BTCUSDT-PERP.SIM", "bid_price": "110.00",
                    "ask_price": "110.00", "bid_size": "100.000", "ask_size": "100.000",
                    "ts_event": 30, "ts_init": 30}, separators=(",", ":"))


def frame(index, data):
    return {"position_id": "P", "index": index, "sha256": hashlib.sha256(data).hexdigest(), "bytes": list(data)}


def multi_state():
    return {"portfolio_realized_pnl": "59.75200000", "portfolio_unrealized_pnl": "0.00000000",
            "portfolio_net_exposure": "0.00000000", "orders": [], "fills": [],
            "accounts": [{"id": "SIM-001", "equity": "10059.75200000"}],
            "archived": [{"id": "P-a", "pnl": "9.91600000"}, {"id": "P-b", "pnl": "19.92000000"}],
            "positions": [{"id": "P", "closed": True, "pnl": "29.91600000",
                           "native": {"quantity": "0.000", "commissions": {"USDT": "0.084 USDT"}}}],
            "snapshots": [frame(0, b"cycle-0"), frame(1, b"cycle-1")]}


def open_state():
    return {"portfolio_realized_pnl": "-0.04000000", "portfolio_unrealized_pnl": "10.00000000",
            "portfolio_net_exposure": "110.00000000", "orders": [], "fills": [], "archived": [], "snapshots": [],
            "accounts": [{"id": "SIM-001", "equity": "9999.96000000",
                          "initial_margins": [["BTCUSDT-PERP.SIM", "0.00000000"]],
                          "maintenance_margins": [["BTCUSDT-PERP.SIM", "5.00000000"]]}],
            "positions": [{"id": "P", "closed": False, "pnl": "-0.04000000",
                           "native": {"quantity": "1.000", "commissions": {"USDT": "0.04 USDT"}}}]}


def chain():
    return [{"blob_ref": "cache://position-snapshots/P/0", "content_hash": "blake3:a", "high_watermark": 13},
            {"blob_ref": "cache://position-snapshots/P/1", "content_hash": "blake3:b", "high_watermark": 21}]


def case(state, anchors, market=None):
    checkpoint = {"state": state, "anchor_chain": anchors, "anchor": anchors[-1] if anchors else None,
                  "market_context": market}
    native = {"state": copy.deepcopy(state), "anchor_chain": copy.deepcopy(anchors),
              "restored_mark": json.loads(QUOTE) if market else None}
    run = {"pid": 22, "process": {"pid": 22}, "exit": 0, "native_receipt": native}
    return {"runs": [run, copy.deepcopy(run)]}, {"pid": 11, "checkpoint": checkpoint}


def multi():
    return case(multi_state(), chain())


def opened():
    return case(open_state(), [], {"native": QUOTE, "ts_event": 30})


def test_genuine_two_cycle_and_open_receipts_pass():
    assert proof.require_continuity(*multi(), proof.MULTI_WITNESS)
    assert proof.require_continuity(*opened(), proof.OPEN_WITNESS)


@pytest.mark.parametrize("mutation", ["missing_cycle", "missing_frame", "overwritten_frame", "lost_anchor",
                                      "foreign_anchor", "pnl_drift", "commission_drift", "same_process",
                                      "second_run_drift"])
def test_incomplete_or_substituted_history_cannot_pass(mutation):
    row, producer = multi()
    state = row["runs"][0]["native_receipt"]["state"]
    if mutation == "missing_cycle":
        state["archived"].pop(0)
    elif mutation == "missing_frame":
        state["snapshots"].pop(0)
    elif mutation == "overwritten_frame":
        state["snapshots"][0] = frame(0, b"cycle-1")
    elif mutation == "lost_anchor":
        row["runs"][0]["native_receipt"]["anchor_chain"].pop(0)
    elif mutation == "foreign_anchor":
        row["runs"][0]["native_receipt"]["anchor_chain"][0]["content_hash"] = "blake3:other"
    elif mutation == "pnl_drift":
        state["portfolio_realized_pnl"] = "49.83600000"
    elif mutation == "commission_drift":
        state["positions"][0]["native"]["commissions"] = {}
    elif mutation == "same_process":
        row["runs"][0]["pid"] = producer["pid"]
    else:
        row["runs"][1]["native_receipt"]["state"]["accounts"][0]["equity"] = "10029.83600000"
    with pytest.raises(AssertionError):
        proof.require_continuity(row, producer, proof.MULTI_WITNESS)


def test_producer_that_omits_the_first_cycle_fails_the_witness():
    row, producer = multi()
    for state in [producer["checkpoint"]["state"]] + [r["native_receipt"]["state"] for r in row["runs"]]:
        state["archived"].pop(0)
        state["portfolio_realized_pnl"] = "49.83600000"
    with pytest.raises(AssertionError):
        proof.require_continuity(row, producer, proof.MULTI_WITNESS)


@pytest.mark.parametrize("mutation", ["unpriced", "zero_exposure", "wrong_mark", "stale_mark",
                                      "margin_drift", "quantity_drift", "equity_drift"])
def test_unpriced_or_divergent_open_exposure_cannot_pass(mutation):
    row, producer = opened()
    native = row["runs"][1]["native_receipt"]
    state = native["state"]
    if mutation == "unpriced":
        native["restored_mark"] = None
        state["portfolio_unrealized_pnl"] = None
    elif mutation == "zero_exposure":
        state["portfolio_net_exposure"] = "0.00000000"
    elif mutation == "wrong_mark":
        native["restored_mark"]["bid_price"] = "120.00"
    elif mutation == "stale_mark":
        native["restored_mark"]["ts_event"] = 29
    elif mutation == "margin_drift":
        state["accounts"][0]["maintenance_margins"] = [["BTCUSDT-PERP.SIM", "5.50000000"]]
    elif mutation == "quantity_drift":
        state["positions"][0]["native"]["quantity"] = "2.000"
    else:
        state["accounts"][0]["equity"] = "10009.96000000"
    with pytest.raises(AssertionError):
        proof.require_continuity(row, producer, proof.OPEN_WITNESS)


def admitted_row(decision="OPEN_EXPOSURE_RECONSTRUCTED_NO_RESUME", applied=True):
    native = {"equal": True, "tail_replay_invoked": False, "bus_publishes": [], "bus_sends": [],
              "bus_responses": 0, "registered_endpoints": [], "market_context_applied": applied,
              "resume": "VENUE_RECONCILIATION_REQUIRED / NO_NEW_ORDERS / NO_RESUME"}
    admission = {"pid": 7, "decision": decision, "error": None, "order_authority": proof.NO_AUTHORITY,
                 "venue_reconciliation_required_before_activation": True}
    run = {"pid": 7, "process": {"pid": 7}, "exit": 0, "admission": admission, "native_receipt": native}
    return {"changed_keys": [], "content_changed_keys": [], "source_files_before": {"a": "1"},
            "source_files_after": {"a": "1"}, "runs": [run]}


def test_open_reconstruction_carries_no_order_or_resume_authority():
    assert proof.require_result(admitted_row(), open_exposure=True)


@pytest.mark.parametrize("mutation", ["sealed_label", "order_authority", "resume", "unreconciled",
                                      "unapplied_quote", "persistent_write", "bus_send"])
def test_open_reconstruction_cannot_widen_authority(mutation):
    row = admitted_row()
    run = row["runs"][0]
    if mutation == "sealed_label":
        run["admission"]["decision"] = "RECOVERY_ADMITTED_SEALED"
    elif mutation == "order_authority":
        run["admission"]["order_authority"] = "ORDERS_PERMITTED"
    elif mutation == "resume":
        run["native_receipt"]["resume"] = "RESUME"
    elif mutation == "unreconciled":
        run["admission"]["venue_reconciliation_required_before_activation"] = False
    elif mutation == "unapplied_quote":
        run["native_receipt"]["market_context_applied"] = False
    elif mutation == "persistent_write":
        row["changed_keys"] = ["trader:accounts:SIM-001"]
    else:
        run["native_receipt"]["bus_sends"] = ["ExecEngine.execute"]
    with pytest.raises(AssertionError):
        proof.require_result(row, open_exposure=True)


def test_sealed_closed_history_never_applies_a_quote():
    row = admitted_row("RECOVERY_ADMITTED_SEALED", applied=True)
    with pytest.raises(AssertionError):
        proof.require_result(row, admitted=True)
    assert proof.require_result(admitted_row("RECOVERY_ADMITTED_SEALED", applied=False), admitted=True)
