"""Real pinned LiveExecutionEngine application of N3-03 native Binance USD-M mass status, fail-closed N3-04 controls."""
import ast
import asyncio
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tools.nautilus_adapter import binance_usdm_engine_reconcile as proof
from tools.nautilus_adapter import binance_usdm_private_reconcile as n3_03

ROOT = Path(__file__).resolve().parents[1]
ADMITTED = {"clean_flat", "active", "reconnect_gap", "external_order"}
INCOMPLETE = ["INCOMPLETE_OR_UNKNOWN", "MASS_STATUS_UNAVAILABLE", "QUERY_FAILED"]
REFUSED = {
    "internal_not_found": ["INCOMPLETE_OR_UNKNOWN", "INTERNAL_ORDER_NOT_FOUND", "QUERY_FAILED"],
    "duplicate_trade": ["DUPLICATE_TRADE_ID_CONFLICT", "FILL_ECONOMICS_CHANGED"],
    "position_fee_changed": ["FILL_ECONOMICS_CHANGED", "POSITION_FILL_MISMATCH"],
    "stale_response": ["STALE_ACCOUNT_SNAPSHOT", "STALE_POSITION_SNAPSHOT"],
    "hedge_mode": ["INCOMPLETE_OR_UNKNOWN", "DUAL_SIDE_POSITION_MODE", "STARTUP_REFUSED"],
    "margin_config": ["LEVERAGE_MISMATCH", "MARGIN_TYPE_MISMATCH"],
    "missing_fill": ["HELD_FILL_ABSENT", "MISSING_FILL", "POSITION_FILL_MISMATCH"],
    "timeout": INCOMPLETE, "server_error": INCOMPLETE, "malformed": INCOMPLETE, "partial_json": INCOMPLETE,
    "rate_limited": ["INCOMPLETE_OR_UNKNOWN", "HELD_FILL_ABSENT", "MISSING_FILL", "NATIVE_REPORTS_AFTER_SWALLOWED_FAILURE",
                     "POSITION_FILL_MISMATCH", "QUERY_FAILED"],
    "lookup_ceiling": ["INCOMPLETE_OR_UNKNOWN", "LOOKUP_CEILING_REACHED"],
    "ordering_collision": ["ORDERING_COLLISION"],
}
VENUE_FILLS = [("501", "101", "BUY", "0.004", "60000.00", "0.04800000 USDT", "MAKER"),
               ("502", "101", "BUY", "0.006", "60000.00", "0.18000000 USDT", "TAKER")]


@pytest.fixture(scope="module")
def run():
    from nautilus_trader.live.execution_engine import LiveExecutionEngine
    loop = asyncio.new_event_loop()  # before the boundary: its AF_UNIX self-pipe is the only socket
    with n3_03.safety_boundary(allow=LiveExecutionEngine) as state:
        semantic, ids = proof.run_all(loop)
    loop.close()
    assert state["violations"] == []
    return semantic, ids, state


def _fills(snapshot):
    return [(f["trade_id"], f["venue_order_id"], f["order_side"], f["last_qty"], f["last_px"], f["commission"],
             f["liquidity_side"]) for f in snapshot["fills"]]


def test_real_pinned_engine_endpoint_reconciled_actual_native_reports(run):
    from nautilus_trader.live.execution_engine import LiveExecutionEngine
    semantic, _, state = run
    upstream = state["upstream"]
    assert LiveExecutionEngine.reconcile_execution_mass_status.__code__.co_filename.startswith(upstream)
    calls = state["calls"]
    engine = "nautilus_trader.live.execution_engine.LiveExecutionEngine."
    sends = sum(1 for r in semantic["scenarios"].values() for a in r.get("applications", []) + r.get("replay", [])
                if a["engine_application_attempted"]) + sum(len(p["applications"]) for p in semantic["hazard_probes"].values())
    # Every send reached the engine-bound endpoint handler and its internal reconciliation exactly once.
    assert calls[engine + "reconcile_execution_mass_status"] == calls[engine + "_reconcile_execution_mass_status"] == sends
    # Native producer chain ran too (startup and after-resubscribe).
    assert calls["nautilus_trader.live.execution_client.LiveExecutionClient.generate_mass_status"] > 0
    assert calls["nautilus_trader.adapters.binance.execution.BinanceCommonExecutionClient._reconcile_after_resubscribe"] > 0
    assert semantic["scenarios"]["active"]["applications"][0]["engine_calls"]["_reconcile_order_report"] == 2


def test_ordinary_active_state_matches_native_reports_and_replay_is_idempotent(run):
    active = run[0]["scenarios"]["active"]
    assert active["config"] == {"allow_overfills": False, "filter_position_reports": False, "filter_unclaimed_external_orders": False,
                                "generate_missing_orders": True, "manage_own_order_books": False, "reconciliation": True}
    assert active["before"]["counts"] == {"orders": 0, "fills": 0, "positions": 0, "events": 0}
    after = active["after"]
    assert _fills(after) == VENUE_FILLS
    orders = {o["venue_order_id"]: o for o in after["orders"]}
    assert {v: (o["client_order_id"], o["status"], o["filled_qty"], o["venue_index"]) for v, o in orders.items()} == {
        "101": ("N3-ENTRY", "FILLED", "0.010", "N3-ENTRY"), "202": ("N3-REDUCE", "ACCEPTED", "0.000", "N3-REDUCE")}
    # Cold cache: the engine marks every venue order EXTERNAL/VENUE, held or not.
    assert all((o["strategy_id"], o["tags"]) == ("EXTERNAL", ["VENUE"]) for o in after["orders"])
    [position] = after["positions"]
    assert (position["side"], position["signed_qty"], position["avg_px_open"], position["realized_pnl"], position["commissions"]) == (
        "LONG", "0.010", "60000.0", "-0.22800000 USDT", ["0.22800000 USDT"])
    assert after["net_position"] == "0.010" and after["account_balances"] == ["1000.00000000 USDT"]
    assert [e["type"] for e in active["applications"][0]["events"]] == [
        "OrderAccepted", "OrderFilled", "PositionOpened", "OrderFilled", "PositionChanged", "OrderAccepted"]
    assert [r["events"] for r in active["replay"]] == [[]] and active["replay_state_unchanged"]
    assert active["engine_observations"] == ["ENGINE_EXTERNAL_ORDER_IN_DISPOSABLE_CACHE_NOT_ADOPTABLE"]
    flat = run[0]["scenarios"]["clean_flat"]
    assert flat["engine_application_attempted"] and flat["after"]["counts"]["events"] == 0


def test_reconnect_gap_applies_missed_fill_once_and_refuses_stale_redelivery(run):
    gap = run[0]["scenarios"]["reconnect_gap"]
    startup, first, second = gap["applications"]
    assert [a["route"] for a in gap["applications"]] == ["startup", "reconnect/1", "reconnect/2"]
    assert _fills(startup["after"]) == VENUE_FILLS[:1]
    assert [o["status"] for o in startup["after"]["orders"]] == ["PARTIALLY_FILLED"]
    assert [(e["type"], e.get("trade_id")) for e in first["events"]] == [
        ("OrderFilled", "502"), ("PositionChanged", None), ("OrderAccepted", None), ("OrderCanceled", None)]
    assert second["events"] == [] and _fills(gap["after"]) == VENUE_FILLS
    assert gap["after"]["positions"][0]["signed_qty"] == "0.010"
    # Fresh native run replayed: older startup refused before the engine, current reports produce nothing.
    assert [(r["route"], r["engine_application_attempted"], r.get("refusal_reasons"), r.get("events")) for r in gap["replay"]] == [
        ("startup", False, ["REPORT_OLDER_THAN_APPLIED_STATE"], None), ("reconnect/1", True, None, []), ("reconnect/2", True, None, [])]
    assert gap["replay_state_unchanged"]
    # Ungated, the same older report makes the engine fabricate a trade: position no longer matches the venue.
    stale = run[0]["hazard_probes"]["stale_redelivery"]
    assert stale["label"] == proof.PROBE_LABEL
    assert [(e["type"], e.get("order_side"), e.get("last_qty")) for e in stale["applications"][-1]["events"]][:2] == [
        ("OrderAccepted", None, None), ("OrderFilled", "SELL", "0.006")]
    assert stale["after"]["positions"][0]["signed_qty"] == "0.004"
    assert "ENGINE_SYNTHETIC_RECONCILIATION_ORDER" in stale["engine_observations"]


def test_unknown_external_order_is_cached_by_engine_but_never_adoptable(run):
    external = run[0]["scenarios"]["external_order"]
    assert external["witness_anomalies"] == {"UNKNOWN_EXTERNAL_OPEN_ORDER": ["303"]}
    order = {o["venue_order_id"]: o for o in external["after"]["orders"]}["303"]
    assert (order["client_order_id"], order["strategy_id"], order["tags"], order["status"]) == (
        "N3-EXTERNAL", "EXTERNAL", ["VENUE"], "ACCEPTED")
    assert external["decision"] == proof.DECISION and _fills(external["after"]) == VENUE_FILLS
    # filter_unclaimed_external_orders drops held orders too; the position diff becomes a synthetic zero-fee fill.
    filtered = run[0]["hazard_probes"]["external_order"]
    assert filtered["config"]["filter_unclaimed_external_orders"] is True
    [synthetic] = filtered["after"]["orders"]
    assert (synthetic["tags"], synthetic["side"], synthetic["filled_qty"]) == (["RECONCILIATION"], "BUY", "0.010")
    assert [(f["commission"], f["liquidity_side"]) for f in filtered["after"]["fills"]] == [("0.00000000 USDT", "NO_LIQUIDITY_SIDE")]
    assert filtered["engine_observations"] == ["ENGINE_FILL_NOT_VENUE_CONFIRMED", "ENGINE_SYNTHETIC_RECONCILIATION_ORDER"]


def test_missing_fill_engine_infers_and_synthesises_economics_never_venue_truth(run):
    probe = run[0]["hazard_probes"]["missing_fill"]
    fills = probe["after"]["fills"]
    venue = [f for f in fills if f["trade_id"] == "501"]
    engine_made = [f for f in fills if f["trade_id"] != "501"]
    assert _fills({"fills": venue}) == VENUE_FILLS[:1]
    # Inferred fill for 101 plus partial-window synthetic open plus a position-diff SELL: three non-venue fills.
    assert len(engine_made) == 3 and all(f["trade_id"].startswith("ENGINE_ID#") for f in engine_made)
    assert {(f["commission"], f["liquidity_side"]) for f in engine_made} == {("0.00000000 USDT", "NO_LIQUIDITY_SIDE")}
    assert sorted(f["order_side"] for f in engine_made) == ["BUY", "BUY", "SELL"]
    [position] = probe["after"]["positions"]
    # Net quantity lands on the venue's 0.010, but fee history is wrong (-0.048 vs venue -0.228).
    assert (position["signed_qty"], position["realized_pnl"]) == ("0.010", "-0.04800000 USDT")
    assert probe["engine_observations"] == ["ENGINE_EXTERNAL_ORDER_IN_DISPOSABLE_CACHE_NOT_ADOPTABLE",
                                            "ENGINE_FILL_NOT_VENUE_CONFIRMED", "ENGINE_SYNTHETIC_RECONCILIATION_ORDER"]


def test_incomplete_or_contradictory_reports_are_refused_before_the_engine(run):
    scenarios = run[0]["scenarios"]
    assert {n for n, r in scenarios.items() if r["admission"]["admitted"]} == ADMITTED
    for name, reasons in REFUSED.items():
        result = scenarios[name]
        assert result["admission"] == {"admitted": False, "refusal_reasons": reasons, "label": "REFUSED_BEFORE_APPLICATION"}, name
        assert result["engine_application_attempted"] is False and result["state_unchanged"] is True, name
        assert result["gated_against"] == "active" and "applications" not in result, name
    # Without the gate the swallowed-429 report would have changed state: one inferred 0.010 fill, no fee.
    swallowed = run[0]["hazard_probes"]["rate_limited"]
    assert [(f["last_qty"], f["commission"]) for f in swallowed["after"]["fills"]] == [("0.010", "0.00000000 USDT")]
    assert "ENGINE_FILL_NOT_VENUE_CONFIRMED" in swallowed["engine_observations"]


def test_every_decision_is_fixed_and_no_authority_vocabulary(run):
    semantic = run[0]
    for result in list(semantic["scenarios"].values()) + list(semantic["hazard_probes"].values()):
        assert result["decision"] == proof.DECISION == n3_03.DECISION
    assert all(p["label"] == "NON_AUTHORITATIVE_HAZARD_OBSERVATION" for p in semantic["hazard_probes"].values())
    values = json.dumps(semantic)
    for forbidden in ('"RESUME"', '"READY"', '"ORDER_ALLOWED"', '"SAFE_TO_ADOPT"', '"TRUSTED"', '"CLEARED"'):
        assert forbidden not in values


def test_engine_opt_in_is_exact_and_other_guards_stay_active(tmp_path):
    import hmac
    import socket
    from nautilus_trader.live.execution_engine import LiveExecutionEngine
    from nautilus_trader.risk.engine import RiskEngine
    from nautilus_trader.trading.trader import Trader

    class Subclass(LiveExecutionEngine):
        pass

    with pytest.raises(proof.Rejected, match="only LiveExecutionEngine"):
        with n3_03.safety_boundary(allow=RiskEngine):
            pass
    for call in (lambda: RiskEngine(None, None, None), lambda: Trader(None, None, None), lambda: Subclass(None, None, None, None),
                 lambda: socket.socket(), lambda: hmac.new(b"k", b"m", "sha256"), lambda: (tmp_path / "x").write_text("x")):
        with n3_03.safety_boundary(tmp_path / "evidence", allow=LiveExecutionEngine) as state:
            with pytest.raises(proof.Rejected, match="BOUNDARY"):
                call()
            assert state["violations"]
    # The harness refuses to run without the boundary or without the exact opt-in.
    loop = asyncio.new_event_loop()
    with pytest.raises(proof.Rejected, match="exact LiveExecutionEngine opt-in"):
        proof.run_all(loop)
    # Default boundary (no opt-in) still refuses the engine itself, and the harness with it.
    with n3_03.safety_boundary() as state:
        with pytest.raises(proof.Rejected, match="exact LiveExecutionEngine opt-in"):
            proof.run_all(loop)
    loop.close()
    with n3_03.safety_boundary() as state:
        with pytest.raises(proof.Rejected, match="authority runtime constructor"):
            LiveExecutionEngine(None, None, None, None)
    assert not (tmp_path / "x").exists()


def test_no_direct_authority_calls_or_imports_in_proof_source():
    tree = ast.parse(Path(proof.__file__).read_text())
    called = {node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
    assert not called & (n3_03.FORBIDDEN | {"connect", "start", "execute", "process", "submit_order", "cancel_order"})
    imported = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)} | {
        alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    authority = ("nautilus_trader.risk", "nautilus_trader.trading", "nautilus_trader.execution.engine",
                 "nautilus_trader.live.node", "nautilus_trader.system", "src", "lib")
    assert not [m for m in imported if m and (m == "src" or m == "lib" or m.startswith(authority))]


def _cli(output):
    return subprocess.run([sys.executable, "-B", "-m", "tools.nautilus_adapter.binance_usdm_engine_reconcile",
                           "--output-dir", str(output)], cwd=ROOT, text=True, capture_output=True, timeout=180)


def test_two_fresh_seccomp_processes_produce_identical_semantic_receipts(tmp_path):
    sources = [Path(proof.__file__).read_bytes(), Path(n3_03.__file__).read_bytes(), n3_03.FIXTURE.read_bytes()]
    semantic, pids = [], []
    for index in range(2):
        output = tmp_path / str(index)
        process = _cli(output)
        assert process.returncode == 0, process.stdout + process.stderr
        assert "SOCKET_SYSCALLS_DENIED; negative control EPERM" in process.stdout
        manifest = json.loads((output / "manifest.json").read_bytes())
        assert proof.digest({k: v for k, v in manifest.items() if k != "self_sha256"}) == manifest["self_sha256"]
        for name, checksum in manifest["files"].items():
            assert hashlib.sha256((output / name).read_bytes()).hexdigest() == checksum
        assert manifest["verdict"] == "N3_04_NATIVE_ENGINE_APPLICATION_OBSERVED" and manifest["decision"] == proof.DECISION
        provenance = json.loads((output / "provenance.json").read_bytes())
        assert provenance["violations"] == [] and provenance["engine_ids"]
        semantic.append((output / "semantic.json").read_bytes())
        pids.append(provenance["pid"])
    assert semantic[0] == semantic[1] and pids[0] != pids[1]
    assert [Path(proof.__file__).read_bytes(), Path(n3_03.__file__).read_bytes(), n3_03.FIXTURE.read_bytes()] == sources


def test_cli_refuses_reused_or_git_output(tmp_path):
    existing = tmp_path / "exists"
    existing.mkdir()
    assert _cli(existing).returncode != 0
    assert _cli(ROOT / "n3-04-evidence").returncode != 0
    assert not (ROOT / "n3-04-evidence").exists()
