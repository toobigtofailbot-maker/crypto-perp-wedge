"""N3-05 fail-closed admission before the real pinned LiveExecutionEngine: physical native proof and boundary checks."""
import ast
import asyncio
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools.nautilus_adapter import binance_usdm_private_reconcile as n3_03
from tools.nautilus_adapter import binance_usdm_reconcile_admission as proof
from tools.nautilus_adapter.binance_usdm_offline_reports import Rejected

ROOT = Path(__file__).resolve().parents[1]
ENGINE = "nautilus_trader.live.execution_engine.LiveExecutionEngine."
ADMITTED = {"active", "reconnect_gap", "external_order"}
REFUSED = "REFUSED_BEFORE_APPLICATION"
NOOP = "IDENTICAL_REPLAY_NO_OP"
APPLIED = "APPLIED_FOR_OBSERVATION_ONLY"
VENUE_FILLS = [("501", "101", "BUY", "0.004", "60000.00", "0.04800000 USDT", "MAKER"),
               ("502", "101", "BUY", "0.006", "60000.00", "0.18000000 USDT", "TAKER")]
ADVERSARIAL = {
    "stale_redelivery": ["REPORT_NOT_MONOTONE_OVER_APPLIED_STATE", "REPORT_OLDER_THAN_APPLIED_STATE",
                         "CACHED_ORDER_ABSENT_FROM_REPORT", "FILL_UNION_QTY_MISMATCH", "POSITION_NOT_EXPLAINED_BY_VENUE_FILLS"],
    "equal_watermark_commission": ["CONFLICTING_EQUAL_WATERMARK", "REPORT_NOT_MONOTONE_OVER_APPLIED_STATE",
                                   "TRADE_ECONOMICS_CONFLICT_WITH_APPLIED"],
    "lost_applied_trade": ["CONFLICTING_EQUAL_WATERMARK", "REPORT_NOT_MONOTONE_OVER_APPLIED_STATE"],
    "filled_qty_regression": ["CONFLICTING_EQUAL_WATERMARK", "REPORT_NOT_MONOTONE_OVER_APPLIED_STATE", "FILL_UNION_QTY_MISMATCH"],
    "status_regression": ["CONFLICTING_EQUAL_WATERMARK", "REPORT_NOT_MONOTONE_OVER_APPLIED_STATE"],
}


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


def _records(semantic):
    for result in semantic["scenarios"].values():
        yield from result["applications"] + result.get("replay", [])
    yield from semantic["adversarial"].values()
    yield from semantic["warm"]["identity"]["applications"] + semantic["warm"]["warm_flat"]["applications"]
    for control in semantic["hazard_controls"].values():
        yield from control["gated_equivalent"]


def _unsent(record):
    return not record["engine_application_attempted"] and record["endpoint_calls_delta"] == 0 and record["state_unchanged"]


def test_every_engine_send_followed_admission_and_reached_the_pinned_endpoint(run):
    semantic, _, state = run
    sends = sum(r["engine_application_attempted"] for r in _records(semantic))
    assert sends == sum(r["outcome"] in {APPLIED, proof.DISCARD} for r in _records(semantic))
    ungated = len(semantic["hazard_controls"])  # one native report each, applied without the gate
    calls = state["calls"]
    assert calls[ENGINE + "reconcile_execution_mass_status"] == calls[ENGINE + "_reconcile_execution_mass_status"] == sends + ungated
    assert calls["nautilus_trader.adapters.binance.execution.BinanceCommonExecutionClient._reconcile_after_resubscribe"] > 0
    assert semantic["scenarios"]["active"]["applications"][0]["engine_calls"]["_reconcile_order_report"] == 2


def test_admitted_reports_carry_only_venue_economics_and_identical_replay_is_a_no_op(run):
    scenarios = run[0]["scenarios"]
    assert {n for n, r in scenarios.items() if r["admission"]["admitted"]} == ADMITTED
    active = scenarios["active"]
    assert [a["outcome"] for a in active["applications"]] == [APPLIED]
    assert _fills(active["after"]) == VENUE_FILLS and active["after"]["positions"][0]["signed_qty"] == "0.010"
    assert active["applications"][0]["engine_observations"] == ["ENGINE_EXTERNAL_ORDER_IN_DISPOSABLE_CACHE_NOT_ADOPTABLE"]
    gap = scenarios["reconnect_gap"]
    # The second reconnect report is byte-identical to the first: never sent (N3-04 sent it and saw zero events).
    assert [a["outcome"] for a in gap["applications"]] == [APPLIED, APPLIED, NOOP]
    assert _fills(gap["applications"][0]["after"]) == VENUE_FILLS[:1] and _fills(gap["after"]) == VENUE_FILLS
    assert [(e["type"], e.get("trade_id")) for e in gap["applications"][1]["events"]] == [
        ("OrderFilled", "502"), ("PositionChanged", None), ("OrderAccepted", None), ("OrderCanceled", None)]
    assert [(r["route"], r["outcome"], r.get("refusal_reasons", [None])[0]) for r in gap["replay"]] == [
        ("startup", REFUSED, "REPORT_NOT_MONOTONE_OVER_APPLIED_STATE"), ("reconnect/1", NOOP, None), ("reconnect/2", NOOP, None)]
    for name in ADMITTED:
        result = scenarios[name]
        assert result["replay_state_unchanged"], name
        assert all(_unsent(r) for r in result["replay"]), name


def test_non_monotone_and_equal_watermark_variants_are_refused_before_send(run):
    adversarial = run[0]["adversarial"]
    assert set(adversarial) == set(ADVERSARIAL)
    for label, reasons in ADVERSARIAL.items():
        record = adversarial[label]
        assert (record["outcome"], record["refusal_reasons"]) == (REFUSED, reasons), label
        assert _unsent(record), label


def test_incomplete_and_hazard_reports_are_refused_before_the_engine(run):
    scenarios = run[0]["scenarios"]
    flat = scenarios["clean_flat"]
    # Cold flat: native never queried trade history, so "complete for issued queries" is not complete.
    assert flat["state_completeness"] == "COMPLETE_FOR_ISSUED_QUERIES" and flat["user_trades_queried"] is False
    assert flat["admission"]["refusal_reasons"] == ["INCOMPLETE_OR_UNKNOWN", "TRADE_HISTORY_NOT_QUERIED_BY_NATIVE_NO_ACTIVE_SYMBOL",
                                                     "REQUIRED_QUERY_NOT_OBSERVED:allOrders:startup",
                                                     "REQUIRED_QUERY_NOT_OBSERVED:userTrades:startup"]
    assert "REQUIRED_QUERY_NOT_OBSERVED:userTrades:startup" in scenarios["rate_limited"]["admission"]["refusal_reasons"]
    assert "NATIVE_REPORTS_AFTER_SWALLOWED_FAILURE" in scenarios["rate_limited"]["admission"]["refusal_reasons"]
    assert "DUPLICATE_TRADE_ID_CONFLICT" in scenarios["duplicate_trade"]["admission"]["refusal_reasons"]
    assert "MISSING_FILL" in scenarios["missing_fill"]["admission"]["refusal_reasons"]
    assert "LOOKUP_CEILING_REACHED" in scenarios["lookup_ceiling"]["admission"]["refusal_reasons"]
    for name, result in scenarios.items():
        if name in ADMITTED:
            continue
        assert result["admission"]["label"] == REFUSED and result["admission"]["refusal_reasons"], name
        assert all(r["outcome"] == REFUSED and _unsent(r) for r in result["applications"] + result.get("replay", [])), name
        assert all(entry == [REFUSED, 0, True] for entry in result["gated_against_active"]), name
    assert scenarios["hedge_mode"]["applications"] == []  # native startup refused: no report exists to offer


def test_required_queries_are_counted_per_report_not_per_phase():
    witness = {"anomalies": {}, "state_completeness": "COMPLETE_FOR_ISSUED_QUERIES", "unknowns": sorted(proof.STANDING_UNKNOWNS)}
    ok = [{"path": "/fapi/v1/" + q, "outcome": "200"} for q in proof.REQUIRED_QUERIES]
    cut = {"event": "transport_interrupted_and_reconnected"}
    # reconnect/1 issued userTrades twice, reconnect/2 never: a per-phase count of 2 would wrongly pass.
    log = ok + ok + ok[-1:] + ok[:-1]
    receipt = {"routes": [{"route": "startup"}, {"route": "reconnect/1"}, {"route": "reconnect/2"}],
               "websocket": [{**cut, "after_request": 4}, {**cut, "after_request": 9}]}
    admission = proof.completeness(witness, receipt, log)
    assert admission["refusal_reasons"] == ["INCOMPLETE_OR_UNKNOWN", "REQUIRED_QUERY_NOT_OBSERVED:userTrades:reconnect/2"]
    assert proof.completeness(witness, {**receipt, "routes": receipt["routes"][:2], "websocket": receipt["websocket"][:1]},
                              ok + ok)["admitted"] is True


def test_ungated_controls_trip_detectors_while_the_gate_refuses_the_same_input(run):
    controls = run[0]["hazard_controls"]
    for name, control in controls.items():
        assert control["label"] == "NON_AUTHORITATIVE_HAZARD_OBSERVATION" and control["outcome"] == proof.DISCARD, name
        assert {"ENGINE_FILL_NOT_VENUE_CONFIRMED", "ENGINE_NO_LIQUIDITY_SIDE_FILL"} <= set(control["engine_observations"]), name
        assert all(r["outcome"] == REFUSED and _unsent(r) for r in control["gated_equivalent"]), name
    # generate_missing_orders=False is not a safety switch: the inferred zero-fee fill still appears.
    off = controls["missing_fill_generate_missing_orders_off"]
    assert off["config"]["generate_missing_orders"] is False
    assert [(f["commission"], f["liquidity_side"]) for f in off["after"]["fills"] if f["trade_id"] != "501"][:1] == [
        ("0.00000000 USDT", "NO_LIQUIDITY_SIDE")]
    assert controls["external_order_filtered"]["gated_equivalent"][0]["refusal_reasons"] == ["ENGINE_CONFIG_DROPS_VENUE_TRUTH"]
    assert controls["missing_fill"]["gated_equivalent"][0]["refusal_reasons"] == ["HELD_FILL_ABSENT", "MISSING_FILL",
                                                                                 "POSITION_FILL_MISMATCH"]


def test_warm_in_process_cache_identity_is_observed_never_adopted(run):
    identity = run[0]["warm"]["identity"]
    assert identity["seeded"] == ["101", "202"] and identity["witness_anomalies"] == {"UNKNOWN_EXTERNAL_OPEN_ORDER": ["303"]}
    assert _fills(identity["before"]) == VENUE_FILLS and identity["before"]["net_position"] == "0.010"
    [application] = identity["applications"]
    assert application["outcome"] == APPLIED
    # The engine matched the held orders: only the unknown 303 produced an event, no fill or position change.
    assert [e["type"] for e in application["events"]] == ["OrderAccepted"] and _fills(identity["after"]) == VENUE_FILLS
    ids = identity["identities"]
    assert {v: (o["client_order_id"], o["strategy_id"], o["tags"], o["held_receipt_identity_match"]) for v, o in ids.items()} == {
        "101": ("N3-ENTRY", proof.PROOF_STRATEGY, None, True), "202": ("N3-REDUCE", proof.PROOF_STRATEGY, None, True),
        "303": ("N3-EXTERNAL", "EXTERNAL", ["VENUE"], False)}
    assert {o["classification"] for o in ids.values()} == {"OBSERVATION_ONLY_NOT_ADOPTABLE"}


def test_warm_flat_really_queries_trade_history_and_is_still_refused_on_economics(run):
    flat = run[0]["warm"]["warm_flat"]
    assert flat["user_trades_queried"] is True and flat["admission"]["admitted"] is True
    [record] = flat["applications"]
    assert record["refusal_reasons"] == ["CACHED_ORDER_ABSENT_FROM_REPORT", "POSITION_NOT_EXPLAINED_BY_VENUE_FILLS"]
    assert _unsent(record)


def test_every_decision_is_fixed_and_no_authority_vocabulary(run):
    semantic = run[0]
    for record in _records(semantic):
        assert record["decision"] == proof.DECISION == n3_03.DECISION
    for result in list(semantic["scenarios"].values()) + list(semantic["hazard_controls"].values()):
        assert result["decision"] == proof.DECISION
    values = json.dumps(semantic)
    for forbidden in ('"RESUME"', '"READY"', '"ORDER_ALLOWED"', '"SAFE_TO_ADOPT"', '"TRUSTED"', '"CLEARED"', '"ADOPTED"'):
        assert forbidden not in values


@pytest.mark.parametrize("target, attribute, message", [
    (n3_03, "FIXTURE_SHA256", "fixture SHA-256 mismatch"),
    (proof.n3_04, "ENGINE_SOURCE_SHA256", "differs from the pinned wheel"),
])
def test_tampered_fixture_or_engine_source_fails_closed(monkeypatch, target, attribute, message):
    from nautilus_trader.live.execution_engine import LiveExecutionEngine
    monkeypatch.setattr(target, attribute, "0" * 64)
    loop = asyncio.new_event_loop()
    with n3_03.safety_boundary(allow=LiveExecutionEngine) as state:
        with pytest.raises(Rejected, match=message):
            proof.run_all(loop)
    loop.close()
    assert state["calls"].get(ENGINE + "reconcile_execution_mass_status", 0) == 0


def test_missing_pin_and_missing_boundary_fail_closed(monkeypatch):
    import socket

    from nautilus_trader.live.execution_engine import LiveExecutionEngine
    from nautilus_trader.trading.trader import Trader
    loop = asyncio.new_event_loop()
    with pytest.raises(Rejected, match="exact LiveExecutionEngine opt-in"):
        proof.run_all(loop)
    with n3_03.safety_boundary(allow=LiveExecutionEngine) as state:
        for call in (lambda: socket.socket(), lambda: Trader(None, None, None)):
            with pytest.raises(Rejected, match="BOUNDARY"):
                call()
        assert state["violations"]
    monkeypatch.setattr(proof.importlib.metadata, "version", lambda package: "0.0.0")
    with n3_03.safety_boundary(allow=LiveExecutionEngine):
        with pytest.raises(Rejected, match="native pin mismatch"):
            proof.run_all(loop)
    loop.close()


def test_no_direct_authority_calls_or_imports_in_proof_source():
    tree = ast.parse(Path(proof.__file__).read_text())
    called = {node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
    assert not called & (n3_03.FORBIDDEN | {"connect", "start", "execute", "process", "submit_order", "cancel_order"})
    imported = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)} | {
        alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    authority = ("nautilus_trader.risk", "nautilus_trader.trading", "nautilus_trader.execution.engine",
                 "nautilus_trader.live.node", "nautilus_trader.system", "src", "lib")
    assert not [m for m in imported if m and (m == "src" or m == "lib" or m.startswith(authority))]
    # The only send path is gated(): the raw N3-04 apply is called there and in the labelled ungated controls.
    applies = [node.lineno for node in ast.walk(tree) if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "apply"
               and getattr(node.func.value, "id", "") == "n3_04"]
    assert len(applies) == 2


def _cli(output, *prefix):
    command = [sys.executable, "-B", *prefix] if prefix else [sys.executable, "-B", "-m",
                                                               "tools.nautilus_adapter.binance_usdm_reconcile_admission"]
    return subprocess.run([*command, "--output-dir", str(output)], cwd=ROOT, text=True, capture_output=True, timeout=300)


def test_two_fresh_seccomp_processes_produce_identical_semantic_receipts(tmp_path):
    sources = [Path(proof.__file__).read_bytes(), Path(proof.n3_04.__file__).read_bytes(), Path(n3_03.__file__).read_bytes(),
               n3_03.FIXTURE.read_bytes()]
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
        assert manifest["verdict"] == "N3_05_FAIL_CLOSED_ADMISSION_OBSERVED" and manifest["decision"] == proof.DECISION
        assert manifest["input_sha256"] == n3_03.FIXTURE_SHA256
        provenance = json.loads((output / "provenance.json").read_bytes())
        assert provenance["violations"] == []
        semantic.append((output / "semantic.json").read_bytes())
        pids.append(provenance["pid"])
    assert semantic[0] == semantic[1] and pids[0] != pids[1]
    assert json.loads(semantic[0])["engine"]["source_sha256"] == proof.n3_04.ENGINE_SOURCE_SHA256
    assert [Path(proof.__file__).read_bytes(), Path(proof.n3_04.__file__).read_bytes(), Path(n3_03.__file__).read_bytes(),
            n3_03.FIXTURE.read_bytes()] == sources


def test_cli_failure_receipt_binds_identity_and_fixed_decision(tmp_path):
    tamper = ("import sys; from tools.nautilus_adapter import binance_usdm_reconcile_admission as m; "
              "m.n3_04.ENGINE_SOURCE_SHA256 = '0' * 64; raise SystemExit(m.main(sys.argv[1:]))")
    output = tmp_path / "failed"
    process = _cli(output, "-c", tamper)
    assert process.returncode == 2, process.stdout + process.stderr
    failure = json.loads((output / "failure.json").read_bytes())
    assert failure["verdict"] == "N3_05_BLOCKED" and "pinned wheel" in failure["error"]
    assert (failure["input_sha256"], failure["native_pin"], failure["decision"]) == (n3_03.FIXTURE_SHA256, "1.231.0", proof.DECISION)
    assert not (output / "semantic.json").exists()


def test_cli_refuses_reused_or_git_output(tmp_path):
    existing = tmp_path / "exists"
    existing.mkdir()
    assert _cli(existing).returncode != 0
    assert _cli(ROOT / "n3-05-evidence").returncode != 0
    assert not (ROOT / "n3-05-evidence").exists()
