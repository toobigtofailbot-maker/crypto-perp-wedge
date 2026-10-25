"""Pinned native Binance USD-M startup/reconnect reconciliation and fail-closed N3-03 controls."""
import ast
import asyncio
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tools.nautilus_adapter import binance_usdm_private_reconcile as proof

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_NATIVE = {
    "nautilus_trader.adapters.binance.execution.BinanceCommonExecutionClient._connect",
    "nautilus_trader.adapters.binance.futures.execution.BinanceFuturesExecutionClient._update_account_state",
    "nautilus_trader.adapters.binance.futures.execution.BinanceFuturesExecutionClient._init_dual_side_position",
    "nautilus_trader.live.execution_client.LiveExecutionClient.generate_mass_status",
    "nautilus_trader.adapters.binance.futures.execution.BinanceFuturesExecutionClient.generate_order_status_reports",
    "nautilus_trader.adapters.binance.execution.BinanceCommonExecutionClient.generate_fill_reports",
    "nautilus_trader.adapters.binance.execution.BinanceCommonExecutionClient.generate_position_status_reports",
    "nautilus_trader.adapters.binance.futures.execution.BinanceFuturesExecutionClient.generate_order_status_report",
    "nautilus_trader.adapters.binance.execution.BinanceCommonExecutionClient._reconcile_after_resubscribe",
    "nautilus_trader.adapters.binance.websocket.user.BinanceUserDataWebSocketClient._handle_stream_reconnect",
    "nautilus_trader.adapters.binance.websocket.user.BinanceUserDataWebSocketClient._resubscribe_locked",
    "nautilus_trader.adapters.binance.websocket.user.BinanceUserDataWebSocketClient._subscribe_rest",
    "nautilus_trader.adapters.binance.http.client.BinanceHttpClient.send_request",
}
EXPECTED = {
    "clean_flat": {},
    "active": {},
    "reconnect_gap": {"ORDER_STATE_ADVANCED": ["101:PARTIALLY_FILLED->FILLED"], "POSITION_CHANGED_VS_HELD": ["0.004->0.010"],
                      "UNHELD_FILL_DISCOVERED": ["502"]},
    "missing_fill": {"HELD_FILL_ABSENT": ["502"], "MISSING_FILL": ["101"], "POSITION_FILL_MISMATCH": ["0.010!=0.004"]},
    "external_order": {"UNKNOWN_EXTERNAL_OPEN_ORDER": ["303"]},
    "internal_not_found": {"INTERNAL_ORDER_NOT_FOUND": ["404"], "QUERY_FAILED": ["algoOrder:status", "order:status"]},
    "duplicate_trade": {"DUPLICATE_TRADE_ID_CONFLICT": ["501"], "FILL_ECONOMICS_CHANGED": ["501"]},
    "position_fee_changed": {"FILL_ECONOMICS_CHANGED": ["502"], "POSITION_CHANGED_VS_HELD": ["0.010->0.012"],
                             "POSITION_FILL_MISMATCH": ["0.012!=0.010"]},
    "stale_response": {"STALE_ACCOUNT_SNAPSHOT": ["1700000001500"], "STALE_POSITION_SNAPSHOT": ["1700000001500"]},
    "hedge_mode": {"DUAL_SIDE_POSITION_MODE": ["dualSidePosition=true"], "STARTUP_REFUSED": ["ValueError"]},
    "margin_config": {"LEVERAGE_MISMATCH": ["BTCUSDT-PERP.BINANCE:20"], "MARGIN_TYPE_MISMATCH": ["ISOLATED"]},
    "timeout": {"MASS_STATUS_UNAVAILABLE": ["startup"], "QUERY_FAILED": ["allOrders:timeout"]},
    "rate_limited": {"HELD_FILL_ABSENT": ["501", "502"], "MISSING_FILL": ["101"], "NATIVE_REPORTS_AFTER_SWALLOWED_FAILURE": ["startup"],
                     "POSITION_FILL_MISMATCH": ["0.010!=0"], "QUERY_FAILED": ["userTrades:status"]},
    "server_error": {"MASS_STATUS_UNAVAILABLE": ["startup"], "QUERY_FAILED": ["positionRisk:status"]},
    "malformed": {"MASS_STATUS_UNAVAILABLE": ["startup"], "QUERY_FAILED": ["openOrders:raw"]},
    "partial_json": {"MASS_STATUS_UNAVAILABLE": ["startup"], "QUERY_FAILED": ["userTrades:raw"]},
    "lookup_ceiling": {"LOOKUP_CEILING_REACHED": ["allOrders"]},
    "ordering_collision": {"ORDERING_COLLISION": ["equal fill ts_event", "native trade_id order not numeric: 1000,999"]},
}


@pytest.fixture(scope="module")
def loop():
    # Created before any boundary: its AF_UNIX self-pipe is the only socket.
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def run(loop):
    with proof.safety_boundary() as state:
        receipts, witnesses = proof.run_all(proof.load_fixture(), loop)
    assert state["violations"] == []
    return receipts, witnesses, state


def test_actual_pinned_native_routines_ran_unpatched(run):
    from nautilus_trader.adapters.binance.futures.execution import BinanceFuturesExecutionClient
    from nautilus_trader.live.execution_client import LiveExecutionClient
    _, _, state = run
    assert REQUIRED_NATIVE <= set(state["calls"])
    assert all(name.startswith("nautilus_trader.") for name in state["calls"])
    upstream = state["upstream"]
    assert BinanceFuturesExecutionClient.generate_mass_status is LiveExecutionClient.generate_mass_status
    for name in ("_connect", "generate_mass_status", "generate_fill_reports", "generate_position_status_reports",
                 "generate_order_status_reports", "_reconcile_after_resubscribe"):
        assert getattr(BinanceFuturesExecutionClient, name).__code__.co_filename.startswith(upstream)


def test_every_scenario_has_exact_distinct_diagnostics_and_fixed_decision(run):
    receipts, witnesses, _ = run
    assert tuple(witnesses) == proof.SCENARIOS
    for name, expected in EXPECTED.items():
        assert witnesses[name]["anomalies"] == expected, name
        assert witnesses[name]["decision"] == proof.DECISION
        assert receipts[name]["unexpected_engine_messages"] == []
    adverse = [n for n in proof.SCENARIOS if n not in {"clean_flat", "active"}]
    assert all(witnesses[n]["anomalies"] for n in adverse)
    values = json.dumps(witnesses)
    for forbidden in ('"RESUME"', '"READY"', '"ORDER_ALLOWED"', '"SAFE_TO_ADOPT"', '"CANCEL"', '"FLATTEN"'):
        assert forbidden not in values


def test_complete_empty_flat_is_distinguishable_from_failed_or_swallowed_queries(run):
    receipts, witnesses, _ = run
    flat, failed, swallowed = (witnesses[n] for n in ("clean_flat", "server_error", "rate_limited"))
    mass = receipts["clean_flat"]["routes"][0]["mass_status"]
    assert (mass["orders"], mass["fills"], mass["positions"]) == ([], [], [])
    assert all(e["outcome"] == "200" for e in receipts["clean_flat"]["transport"])
    assert flat["state_completeness"] == "COMPLETE_FOR_ISSUED_QUERIES"
    # Native skips trade history with no active symbol: recorded, never assumed complete.
    assert not any(e["path"].endswith("/userTrades") for e in receipts["clean_flat"]["transport"])
    assert "TRADE_HISTORY_NOT_QUERIED_BY_NATIVE_NO_ACTIVE_SYMBOL" in flat["unknowns"]
    assert receipts["server_error"]["routes"][0]["mass_status"] is None
    assert failed["state_completeness"] == swallowed["state_completeness"] == "INCOMPLETE_OR_UNKNOWN"
    # The native 429 path returns [] fills inside a non-None mass status; the witness refuses it.
    assert receipts["rate_limited"]["routes"][0]["mass_status"]["fills"] == []
    assert "NATIVE_REPORTS_AFTER_SWALLOWED_FAILURE" in swallowed["anomalies"]
    for name in ("timeout", "server_error", "malformed", "partial_json"):
        assert "HELD_OPEN_ORDERS_UNVERIFIED" in witnesses[name]["unknowns"]
        assert "single_lookups" not in receipts[name]


def test_ordinary_active_native_reports_account_and_cache_match_sources(run):
    tape = proof.n3_01.load_fixture(proof.n3_01.FIXTURE)
    receipt = run[0]["active"]
    mass = receipt["routes"][0]["mass_status"]
    assert mass["account_id"] == "BINANCE-USDT_FUTURES-master" and mass["ts_init"] == proof.CLOCK_NS
    orders = {o["venue_order_id"]: o for o in mass["orders"]}
    assert set(orders) == {"101", "202"}
    for voi, source in (("101", tape["rest_orders"][2]), ("202", tape["rest_orders"][3])):
        report = orders[voi]
        assert report["client_order_id"] == source["clientOrderId"]
        assert (report["quantity"], report["filled_qty"], report["price"]) == (source["origQty"], source["executedQty"], source["price"])
        assert report["ts_last"] == source["updateTime"] * 1000000
        assert report["reduce_only"] is source["reduceOnly"]
    assert (orders["101"]["order_status"], orders["202"]["order_status"]) == ("FILLED", "ACCEPTED")
    fills = mass["fills"]
    assert [(f["trade_id"], f["venue_order_id"], f["last_qty"], f["last_px"], f["commission"], f["liquidity_side"]) for f in fills] == [
        ("501", "101", "0.004", "60000.00", "0.04800000 USDT", "MAKER"), ("502", "101", "0.006", "60000.00", "0.18000000 USDT", "TAKER")]
    assert [(p["position_side"], p["quantity"], p["avg_px_open"]) for p in mass["positions"]] == [("LONG", "0.010", "60000.00")]
    account = receipt["account"]
    assert account["type"] == "MarginAccount" and account["leverages"] == {"BTCUSDT-PERP.BINANCE": "1"}
    event = account["last_event"]
    assert event["account_type"] == "MARGIN" and event["reported"] is True and event["ts_event"] == 1700000004500000000
    assert [(b["total"], b["locked"], b["free"]) for b in event["balances"]] == [("1000.00000000", "600.00000000", "400.00000000")]
    assert [(m["initial"], m["maintenance"]) for m in event["margins"]] == [("600.00000000", "0.00000000")]
    assert run[1]["active"]["state_completeness"] == "COMPLETE_FOR_ISSUED_QUERIES"


def test_transport_reconnect_drives_native_after_resubscribe_mass_status_and_is_idempotent(run):
    receipt = run[0]["reconnect_gap"]
    ws = receipt["websocket"]
    assert [e["event"] for e in ws] == ["connect", "transport_interrupted_and_reconnected", "disconnect", "connect",
                                        "transport_interrupted_and_reconnected", "disconnect", "connect"]
    assert [e["listen_key"].rsplit("=", 1)[1] for e in ws if e["event"] == "connect"] == [
        "N3-03-LISTEN-KEY-1", "N3-03-LISTEN-KEY-2", "N3-03-LISTEN-KEY-3"]
    log = receipt["transport"]
    for connect in [e for e in ws if e["event"] == "connect"][1:]:
        # New listenKey, stream connect, THEN the native hook's full queries (before dispatch resumes).
        assert log[connect["after_request"] - 1]["path"] == "/fapi/v1/listenKey"
        assert log[connect["after_request"]]["path"].endswith("/positionRisk")
    assert receipt["mass_status_messages"] == 2  # delivered via native _send_mass_status_report
    startup, first, second = (r["mass_status"] for r in receipt["routes"])
    assert [f["trade_id"] for f in startup["fills"]] == ["501"]
    assert [o["order_status"] for o in startup["orders"]] == ["PARTIALLY_FILLED"]
    assert [f["trade_id"] for f in first["fills"]] == ["501", "502"]
    assert {o["venue_order_id"]: o["order_status"] for o in first["orders"]} == {"101": "FILLED", "202": "CANCELED"}
    assert first == second  # repeated read-only refresh: no extra economic change
    assert "REPEAT_REFRESH_DIVERGED" not in run[1]["reconnect_gap"]["anomalies"]


def test_requests_are_bounded_read_only_unsigned_and_offline(run):
    receipts, _, _ = run
    for name, receipt in receipts.items():
        log = receipt["transport"]
        assert 0 < len(log) <= 40, name
        for entry in log:
            assert (entry["method"], entry["path"]) == ("POST", "/fapi/v1/listenKey") or entry["method"] == "GET"
            assert "signature" not in entry["params"]
        for path in {e["path"] for e in log if e["outcome"] != "200"}:
            # Bounded by native call sites per mass status, never a retry loop.
            assert sum(e["path"] == path for e in log) <= 4, (name, path)
    # positionRisk call sites: base + futures-override active symbols, fills, positions.
    assert sum(e["path"].endswith("/positionRisk") for e in receipts["server_error"]["transport"]) == 4


def test_fixture_and_route_inventory_fail_closed(tmp_path):
    fixture = proof.load_fixture()
    for mutate in (lambda f: f.update(extra=1), lambda f: f.update(n3_01_fixture_sha256="0" * 64),
                   lambda f: f["scenarios"]["active"]["phases"][0].update(order_submit=[]),
                   lambda f: f["scenarios"]["active"]["held"].update(extra=1),
                   lambda f: f["scenarios"].pop("timeout")):
        bad = copy.deepcopy(fixture)
        mutate(bad)
        with pytest.raises(proof.Rejected):
            proof.validate(bad)
    copied = tmp_path / "copy.json"
    copied.write_bytes(proof.FIXTURE.read_bytes())
    with pytest.raises(proof.Rejected):
        proof.load_fixture(copied)


@pytest.mark.parametrize("method,url", [
    ("POST", proof.BASE_HTTP + "/fapi/v1/order?symbol=BTCUSDT"),
    ("DELETE", proof.BASE_HTTP + "/fapi/v1/allOpenOrders?symbol=BTCUSDT"),
    ("GET", proof.BASE_HTTP + "/fapi/v1/userTrades?symbol=BTCUSDT&signature=abc"),
    ("GET", "https://fapi.binance.com/fapi/v1/openOrders"),
])
def test_offline_transport_refuses_writes_signatures_and_real_hosts(loop, method, url):
    transport = proof.OfflineTransport(proof.load_fixture(), proof.n3_01.load_fixture(proof.n3_01.FIXTURE), "active")
    with pytest.raises(proof.Rejected, match="BOUNDARY"):
        loop.run_until_complete(transport.request(method, url))
    assert transport.log[-1]["outcome"] == "REFUSED_BOUNDARY"


@pytest.mark.parametrize("operation", ["socket", "env", "hmac", "write", "subprocess", "sign", "trade"])
def test_boundary_guards_fire_before_effects(tmp_path, operation):
    from nautilus_trader.adapters.binance.http.client import BinanceHttpClient
    from nautilus_trader.common.component import TestClock
    target = tmp_path / "outside.txt"
    with proof.safety_boundary(tmp_path / "evidence") as state:
        with pytest.raises(proof.Rejected, match="BOUNDARY"):
            if operation == "socket":
                import socket
                socket.socket()
            elif operation == "env":
                os.environ.get("BINANCE_API_SECRET")
            elif operation == "hmac":
                import hmac
                hmac.new(b"k", b"m", "sha256")
            elif operation == "write":
                target.write_text("x")
            elif operation == "subprocess":
                subprocess.run([sys.executable, "-c", "pass"])
            else:
                http = BinanceHttpClient(clock=TestClock(), api_key=proof.PLACEHOLDER_KEY,
                                         api_secret=proof.PLACEHOLDER_KEY, base_url=proof.BASE_HTTP)
                if operation == "sign":
                    http._get_sign("timestamp=1")
                else:
                    from nautilus_trader.adapters.binance.futures.http.account import BinanceFuturesAccountHttpAPI
                    BinanceFuturesAccountHttpAPI.set_leverage(None, "BTCUSDT", 5).send(None)
        assert state["violations"]
    assert not target.exists()


@pytest.mark.parametrize("target", ["nautilus_trader.risk.engine:RiskEngine",
                                    "nautilus_trader.live.execution_engine:LiveExecutionEngine",
                                    "nautilus_trader.trading.trader:Trader"])
def test_cython_and_python_authority_constructors_rejected_before_construction(tmp_path, target):
    import importlib
    module, name = target.split(":")
    cls = getattr(importlib.import_module(module), name)  # passive import stays allowed
    with proof.safety_boundary(tmp_path) as state:
        with pytest.raises(proof.Rejected, match="authority runtime constructor"):
            cls(None, None, None)
        assert state["violations"] == ["authority runtime constructor: " + module + "." + name]
    import sys as runtime
    assert runtime.monitoring.get_tool(proof.MONITOR_ID) is None  # boundary released its monitor slot


def test_no_direct_authority_calls_in_proof_source():
    tree = ast.parse(Path(proof.__file__).read_text())
    called = {node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
    assert not called & (proof.FORBIDDEN | {"connect", "start", "execute"})
    imported = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)} | {
        alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    authority = ("nautilus_trader.risk", "nautilus_trader.trading", "nautilus_trader.execution.engine",
                 "nautilus_trader.live.execution_engine", "nautilus_trader.live.node", "nautilus_trader.system")
    assert not [m for m in imported if m and m.startswith(authority)]


def _cli(output):
    return subprocess.run([sys.executable, "-B", "-m", "tools.nautilus_adapter.binance_usdm_private_reconcile",
                           "--output-dir", str(output)], cwd=ROOT, text=True, capture_output=True, timeout=120)


def test_two_fresh_seccomp_processes_produce_identical_semantic_receipts(tmp_path):
    source, data = Path(proof.__file__).read_bytes(), proof.FIXTURE.read_bytes()
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
        record = json.loads((output / "semantic.json").read_bytes())
        assert proof.digest(record) == manifest["semantic_sha256"]
        provenance = json.loads((output / "provenance.json").read_bytes())
        assert provenance["violations"] == [] and REQUIRED_NATIVE <= set(provenance["native_calls"])
        semantic.append(record)
        pids.append(provenance["pid"])
    assert semantic[0] == semantic[1] and pids[0] != pids[1]
    assert Path(proof.__file__).read_bytes() == source and proof.FIXTURE.read_bytes() == data


def test_cli_refuses_reused_or_git_output(tmp_path):
    existing = tmp_path / "exists"
    existing.mkdir()
    assert _cli(existing).returncode != 0
    assert _cli(ROOT / "n3-03-evidence").returncode != 0
    assert not (ROOT / "n3-03-evidence").exists()
