"""Private N3-03 offline native Binance USD-M startup/reconnect reconciliation proof.

Pinned NautilusTrader 1.231.0 futures execution-client startup, report
generation and after-resubscribe mass status run unmodified against in-process
fakes that replace only the pyo3 HTTP and WebSocket transport objects. The CPW
witness is read-only admission telemetry: its decision is fixed and it has no
production consumer, OMS, adoption, cancel/flatten or resume authority.
"""
from __future__ import annotations

import argparse
import asyncio
from contextlib import contextmanager
import copy
import ctypes
from decimal import Decimal
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import urllib.parse

from tools.nautilus_adapter import binance_usdm_offline_reports as n3_01
from tools.nautilus_adapter.binance_usdm_offline_reports import Rejected, canonical, digest, require

ROOT = n3_01.ROOT
FIXTURE = ROOT / "tests/fixtures/nautilus_n3_03/binance_usdm_private_states.json"
FIXTURE_SHA256 = "f72aa78fed5f34ee1975dbd9080b23753d89358545b714d12dfbef806b472911"
FIXTURE_ID = "N3-03-BTCUSDT-USDM-PRIVATE-SYNTHETIC-v1"
DECISION = "RECONCILIATION_REQUIRED / NO_NEW_ORDERS / NO_RESUME / NOT_PAPER_OR_LIVE_READY"
HOST = "n3-03.offline.invalid"  # RFC 2606 .invalid: never resolvable
BASE_HTTP = "https://" + HOST
BASE_WS = "wss://" + HOST + "/ws"
PLACEHOLDER_KEY = "N3-03-OFFLINE-PLACEHOLDER-NOT-A-KEY"
CLOCK_NS = 1700000005000000000
SCENARIOS = ("clean_flat", "active", "reconnect_gap", "missing_fill", "external_order",
             "internal_not_found", "duplicate_trade", "position_fee_changed", "stale_response",
             "hedge_mode", "margin_config", "timeout", "rate_limited", "server_error",
             "malformed", "partial_json", "lookup_ceiling", "ordering_collision")
READ_ROUTES = {"exchangeInfo", "account", "symbolConfig", "dual", "time", "positionRisk", "openOrders",
               "allOrders", "userTrades", "openAlgoOrders", "allAlgoOrders", "order", "algoOrder"}
MASS_ROUTES = {"positionRisk", "openOrders", "allOrders", "userTrades", "openAlgoOrders", "allAlgoOrders"}
OPEN = {"ACCEPTED", "PARTIALLY_FILLED", "SUBMITTED", "TRIGGERED", "PENDING_UPDATE", "PENDING_CANCEL"}
# Native routines whose real execution the receipt must show (profile hook, upstream file only).
TRACE = {"_connect", "_update_account_state", "_init_dual_side_position", "generate_mass_status",
         "generate_order_status_reports", "generate_fill_reports", "generate_position_status_reports",
         "generate_order_status_report", "_build_active_symbols", "_get_binance_position_status_reports",
         "_reconcile_after_resubscribe", "_handle_stream_reconnect", "_resubscribe", "_resubscribe_locked",
         "_subscribe_rest", "_connect_stream_with_hook", "_safe_pre_dispatch_hook", "send_request",
         "query_futures_account_info", "query_futures_position_risk", "query_open_orders",
         "query_all_orders", "query_user_trades", "query_order", "create_listen_key", "load_all_async",
         # N3-04 LiveExecutionEngine reconciliation path (only reached under the engine opt-in).
         "reconcile_execution_mass_status", "_reconcile_execution_mass_status", "_adjust_mass_status_fills",
         "_deduplicate_mass_status_orders", "_reconcile_order_report", "_generate_order",
         "_handle_order_status_transitions", "_reconcile_fill_report", "_check_and_skip_duplicate_fill",
         "_generate_order_filled", "_handle_fill_quantity_mismatch", "_generate_inferred_fill",
         "_handle_event_with_tracking", "_reconcile_position_report", "_reconcile_position_report_netting",
         "_create_position_reconciliation_report", "_validate_reconciliation_state"}
FORBIDDEN = {"submit_order", "submit_order_list", "modify_order", "cancel_order", "cancel_all_orders",
             "batch_cancel_orders", "_submit_order", "_submit_order_inner", "_submit_order_list",
             "_modify_order", "_cancel_order", "_cancel_all_orders", "_batch_cancel_orders",
             "_cancel_orders_batch", "_cancel_order_single", "_cancel_algo_orders_batch", "set_leverage",
             "set_margin_type", "_get_sign", "hmac_signature", "rsa_signature", "ed25519_signature",
             "session_logout", "close_listen_key"}
FORBIDDEN_CLASSES = {"Trader", "Strategy", "RiskEngine", "ExecutionEngine", "LiveExecutionEngine",
                     "OrderEmulator", "TradingNode", "Controller"}
MONITOR_ID = 4  # sys.monitoring tool slot; refused if another tool already holds it
_STATE = None
_HOOKED = False


def _audit(event, args):
    state = _STATE
    if state is None:
        return
    reason = None
    if event.startswith("socket.") or event in {"subprocess.Popen", "os.system", "os.posix_spawn", "os.exec", "os.fork"}:
        reason = event
    elif event == "import" and (args[0] == "src" or args[0].startswith(("src.", "lib."))):
        reason = "protected CPW import"
    elif event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        path = Path(os.fsdecode(args[0])).absolute()
        mode, flags = args[1:3]
        writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
            isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if n3_01._credential_path(path):
            reason = "credential file access"
        elif writing and (state["output"] is None or not path.resolve().is_relative_to(state["output"])):
            reason = "write outside external evidence"
    elif event in {"os.remove", "os.rmdir", "os.rename", "os.link", "os.symlink", "os.chmod", "os.truncate"}:
        reason = "filesystem mutation: " + event
    if reason:
        state["violations"].append(reason)
        raise Rejected("BOUNDARY: " + reason)


def _profile(frame, event, arg):
    if event != "call":
        return
    state = _STATE
    if state is None:
        return
    code = frame.f_code
    module = frame.f_globals.get("__name__", "")
    name = code.co_name
    reason = None
    if module == "os" and name in {"__getitem__", "getenv"}:
        key = str(frame.f_locals.get("key", "")).upper()
        if any(s in key for s in ("SECRET", "TOKEN", "PASSWORD", "API_KEY", "BINANCE")):
            reason = "credential environment access"
    elif module == "hmac":
        reason = "signing"
    elif module.startswith("nautilus_trader."):
        if name in FORBIDDEN or (name == "connect" and module == "nautilus_trader.live.execution_client"):
            reason = "authority/signing entry: " + module + "." + name
        elif name in TRACE and code.co_filename.startswith(state["upstream"]):
            key = module + "." + code.co_qualname
            state["calls"][key] = state["calls"].get(key, 0) + 1
    if reason:
        state["violations"].append(reason)
        raise Rejected("BOUNDARY: " + reason)


def _on_call(code, offset, target, arg0):
    """CALL monitor: sees Cython authority classes (invisible to the profile hook) at the Python call site."""
    state = _STATE
    if state is None or not isinstance(target, type) or target is state["allow"]:
        return
    for cls in target.__mro__:
        if cls.__name__ in FORBIDDEN_CLASSES and cls.__module__.startswith("nautilus_trader."):
            reason = "authority runtime constructor: " + target.__module__ + "." + target.__name__
            state["violations"].append(reason)
            raise Rejected("BOUNDARY: " + reason)


@contextmanager
def safety_boundary(output=None, allow=None):
    """Python audit/profile/CALL-monitor boundary; the CLI adds a Linux seccomp socket filter.

    ``allow`` is the N3-04 offline-harness opt-in: it may only be exactly
    ``LiveExecutionEngine`` (no subclass); every other authority class still refuses.

    Limit: construction performed inside compiled Cython/Rust code without a
    Python call site is not visible; the static tests forbid authority imports.
    """
    global _STATE, _HOOKED
    require(_STATE is None, "nested boundary")
    require(allow is None or (allow.__module__, allow.__qualname__) == ("nautilus_trader.live.execution_engine",
                                                                        "LiveExecutionEngine"),
            "only LiveExecutionEngine may be opted in")
    import nautilus_trader  # passive import, needed to bind upstream-file call evidence
    if not _HOOKED:
        sys.addaudithook(_audit)
        _HOOKED = True
    _STATE = state = {"output": None if output is None else Path(output).resolve(), "violations": [], "calls": {},
                      "allow": allow,
                      "upstream": str(Path(nautilus_trader.__file__).resolve().parent) + os.sep}
    monitoring = sys.monitoring
    monitoring.use_tool_id(MONITOR_ID, "cpw-n3-03-boundary")
    monitoring.register_callback(MONITOR_ID, monitoring.events.CALL, _on_call)
    monitoring.set_events(MONITOR_ID, monitoring.events.CALL)
    previous = sys.getprofile()
    sys.setprofile(_profile)
    try:
        yield state
    finally:
        sys.setprofile(previous)
        monitoring.set_events(MONITOR_ID, 0)
        monitoring.register_callback(MONITOR_ID, monitoring.events.CALL, None)
        monitoring.free_tool_id(MONITOR_ID)
        _STATE = None


def deny_socket_syscalls():
    """Irreversible Linux seccomp filter: every socket syscall returns EPERM."""
    sec = ctypes.CDLL("libseccomp.so.2", use_errno=True)
    sec.seccomp_init.argtypes = [ctypes.c_uint]
    sec.seccomp_init.restype = ctypes.c_void_p
    sec.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    sec.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_uint]
    sec.seccomp_load.argtypes = [ctypes.c_void_p]
    sec.seccomp_release.argtypes = [ctypes.c_void_p]
    ctx = sec.seccomp_init(0x7FFF0000)  # SCMP_ACT_ALLOW
    require(bool(ctx), "seccomp unavailable")
    for call in ("socket", "socketpair", "connect", "sendto", "sendmsg", "sendmmsg", "bind", "listen", "accept", "accept4"):
        number = sec.seccomp_syscall_resolve_name(call.encode())
        require(number >= 0 and sec.seccomp_rule_add(ctx, 0x00050001, number, 0) == 0, "seccomp rule")  # ERRNO(EPERM)
    require(sec.seccomp_load(ctx) == 0, "seccomp load")
    sec.seccomp_release(ctx)
    libc = ctypes.CDLL(None, use_errno=True)
    require(libc.socket(2, 1, 0) == -1 and ctypes.get_errno() == 1, "socket negative control did not fail")
    return "SOCKET_SYSCALLS_DENIED; negative control EPERM"


def load_fixture(path=FIXTURE):
    path = Path(path)
    require(path.is_absolute() and not path.is_symlink() and path.resolve() == FIXTURE, "only controlled absolute fixture path")
    data = path.read_bytes()
    require(len(data) < 100000 and hashlib.sha256(data).hexdigest() == FIXTURE_SHA256, "fixture SHA-256 mismatch")
    return validate(json.loads(data, object_pairs_hook=_pairs))


def _pairs(items):
    obj = {}
    for key, value in items:
        require(key not in obj, "duplicate JSON key")
        obj[key] = value
    return obj


def validate(fixture):
    require(isinstance(fixture, dict) and set(fixture) == {"fixture_id", "notice", "n3_01_fixture_sha256", "expected_config",
                                                          "defaults", "scenarios"}, "closed fixture fields")
    require(fixture["fixture_id"] == FIXTURE_ID and fixture["notice"].startswith("TEST FIXTURE ONLY;"), "fixture identity")
    require(fixture["n3_01_fixture_sha256"] == n3_01.FIXTURE_SHA256, "N3-01 tape reference mismatch")
    require(set(fixture["expected_config"]) == {"margin_type", "leverage"}, "closed expected config")
    require(set(fixture["defaults"]) <= READ_ROUTES, "unknown default route")
    require(tuple(fixture["scenarios"]) == SCENARIOS, "closed ordered scenario inventory")
    for name, case in fixture["scenarios"].items():
        require(set(case) <= {"held", "phases", "lookup"} and "held" in case and "phases" in case, "closed scenario fields: " + name)
        require(set(case["held"]) == {"as_of_ms", "orders", "trades", "position_amt"}, "closed held receipt: " + name)
        n3_01.timestamp(case["held"]["as_of_ms"])
        n3_01.number(case["held"]["position_amt"], signed=True)
        require(len(case["phases"]) == (2 if name == "reconnect_gap" else 1), "phase inventory: " + name)
        for phase in case["phases"]:
            require(set(phase) <= READ_ROUTES, "unknown scenario route: " + name)
    return fixture


class _Response:
    def __init__(self, status, body):
        self.status, self.body, self.headers = status, body, {}


class OfflineTransport:
    """Deterministic private venue at the pyo3 transport boundary. Records every request."""

    def __init__(self, fixture, tape, name):
        self.tape, self.case = tape, fixture["scenarios"][name]
        self.defaults, self.phase, self.log, self.ws, self.listen_keys = fixture["defaults"], 0, [], [], 0

    def _item(self, spec):
        if isinstance(spec, str):
            group, index = spec.split("/")
            return copy.deepcopy(self.tape[group][int(index)])
        if "ref" in spec:
            require(set(spec) == {"ref", "patch"}, "closed item spec")
            return {**self._item(spec["ref"]), **spec["patch"]}
        return copy.deepcopy(spec)

    def _body(self, route, spec):
        if route == "exchangeInfo":
            return {"timezone": "UTC", "serverTime": 1700000000000, "rateLimits": [], "exchangeFilters": [],
                    "assets": [], "symbols": [self.tape["exchange_info"]]}
        if isinstance(spec, dict) and "generate" in spec:
            # shortcut: synthetic history rows share one template; only identities vary.
            template = self._item(spec["generate"])
            return [{**template, "orderId": 10000 + i, "clientOrderId": f"N3-HIST-{i}"} for i in range(spec["count"])]
        if isinstance(spec, list):
            return [self._item(item) for item in spec]
        return self._item(spec)

    async def request(self, method, url, headers=None, body=None, keys=None, timeout_secs=None):
        parts = urllib.parse.urlsplit(url)
        params = dict(urllib.parse.parse_qsl(parts.query))
        route = parts.path.rsplit("/", 1)[-1]
        verb = str(method).rsplit(".", 1)[-1].upper()
        entry = {"seq": len(self.log), "phase": self.phase, "method": verb, "path": parts.path,
                 "params": {k: v for k, v in sorted(params.items())}}
        self.log.append(entry)
        if parts.netloc != HOST or "signature" in params or body is not None:
            entry["outcome"] = "REFUSED_BOUNDARY"
            raise Rejected("BOUNDARY: non-offline host, signature or request body")
        if (verb, route) == ("POST", "listenKey"):
            self.listen_keys += 1
            payload = {"listenKey": f"N3-03-LISTEN-KEY-{self.listen_keys}"}
        else:
            if verb != "GET" or route not in READ_ROUTES:
                entry["outcome"] = "REFUSED_BOUNDARY"
                raise Rejected("BOUNDARY: forbidden private request " + verb + " " + parts.path)
            spec = self.case["phases"][self.phase].get(route, self.defaults.get(route))
            require(spec is not None or route == "exchangeInfo", "unconfigured offline route " + route)
            if isinstance(spec, dict) and "fail" in spec:
                return self._fail(entry, spec)
            payload = self._body(route, spec)
        data = json.dumps(payload, separators=(",", ":")).encode()
        entry.update(outcome="200", source_sha256=hashlib.sha256(data).hexdigest(), body=payload)
        return _Response(200, data)

    def _fail(self, entry, spec):
        from nautilus_trader.core.nautilus_pyo3 import HttpTimeoutError
        kind = spec["fail"]
        entry["outcome"] = kind
        if kind == "timeout":
            raise HttpTimeoutError("offline synthetic timeout")
        data = spec["raw"].encode() if "raw" in spec else json.dumps(spec["body"]).encode()
        entry["source_sha256"] = hashlib.sha256(data).hexdigest()
        return _Response(spec.get("status", 200), data)

    def websocket_class(self):
        transport = self

        class OfflineWebSocket:
            def __init__(self, url, handler, post_reconnection):
                self.url, self.handler, self.post_reconnection, self.closed = url, handler, post_reconnection, False

            @classmethod
            async def connect(cls, loop_, config, handler, post_reconnection=None, **_):
                require(config.url.startswith(BASE_WS), "BOUNDARY: non-offline WebSocket")
                socket = cls(config.url, handler, post_reconnection)
                connection = sum(e["event"] == "connect" for e in transport.ws)
                transport.ws.append({"event": "connect", "connection": connection, "phase": transport.phase,
                                     "listen_key": config.url.rsplit("/", 1)[-1], "after_request": len(transport.log)})
                transport.socket = socket
                return socket

            async def disconnect(self):
                self.closed = True
                transport.ws.append({"event": "disconnect", "phase": transport.phase, "after_request": len(transport.log)})

            def is_reconnecting(self):
                return False

            def is_disconnecting(self):
                return False

            def is_closed(self):
                return self.closed

        return OfflineWebSocket

    def interrupt(self, next_phase):
        """Transport-originated drop/reconnect: events in the gap are never delivered."""
        self.phase = next_phase
        self.ws.append({"event": "transport_interrupted_and_reconnected", "phase": self.phase, "after_request": len(self.log)})
        self.socket.post_reconnection()  # the native callback registered by the user-data client


def _stable(report):
    stable = {k: v for k, v in report.to_dict().items() if k not in {"report_id", "event_id", "id"}}
    for attr in ("order_status", "order_side", "liquidity_side", "position_side"):
        if hasattr(report, attr):
            stable[attr] = getattr(report, attr).name
    return stable


def _mass(mass):
    if mass is None:
        return None
    orders = [_stable(r) for _, r in sorted(mass.order_reports.items(), key=lambda kv: kv[0].value)]
    fills = [_stable(r) for _, rows in sorted(mass.fill_reports.items(), key=lambda kv: kv[0].value) for r in rows]
    positions = [_stable(r) for _, rows in sorted(mass.position_reports.items(), key=lambda kv: kv[0].value) for r in rows]
    return {"account_id": str(mass.account_id), "venue": str(mass.venue), "ts_init": mass.ts_init,
            "orders": orders, "fills": fills, "positions": positions}


async def _native_run(fixture, tape, name, native=None):
    """``native``, if given, collects the raw native objects (mass statuses, instrument, account state) for N3-04."""
    from nautilus_trader.adapters.binance.common.enums import BinanceAccountType, BinanceEnvironment
    from nautilus_trader.adapters.binance.config import BinanceExecClientConfig
    from nautilus_trader.adapters.binance.futures.execution import BinanceFuturesExecutionClient
    from nautilus_trader.adapters.binance.futures.providers import BinanceFuturesInstrumentProvider
    from nautilus_trader.adapters.binance.http.client import BinanceHttpClient
    from nautilus_trader.adapters.binance.websocket import user as user_ws
    from nautilus_trader.cache.cache import Cache
    from nautilus_trader.common.component import MessageBus, TestClock
    from nautilus_trader.config import InstrumentProviderConfig
    from nautilus_trader.core.uuid import UUID4
    from nautilus_trader.execution.messages import GenerateOrderStatusReport
    from nautilus_trader.model.events import AccountState
    from nautilus_trader.model.identifiers import ClientOrderId, InstrumentId, TraderId, VenueOrderId
    from nautilus_trader.portfolio.portfolio import Portfolio

    class OfflineHttpClient(BinanceHttpClient):
        async def sign_request(self, http_method, url_path, payload=None, ratelimiter_keys=None):
            # Signing is out of scope and forbidden: the native unsigned send_request
            # (status/error mapping) still runs; the transport refuses any signature.
            return await self.send_request(http_method, url_path, payload=payload, ratelimiter_keys=ratelimiter_keys)

    transport = OfflineTransport(fixture, tape, name)
    clock = TestClock()
    clock.set_time(CLOCK_NS)
    msgbus = MessageBus(TraderId("N3-003"), clock)
    cache = Cache()
    Portfolio(msgbus, cache, clock)
    received = {"mass": [], "other": []}
    msgbus.register("ExecEngine.reconcile_execution_mass_status", received["mass"].append)
    for endpoint in ("ExecEngine.process", "ExecEngine.reconcile_execution_report", "ExecEngine.execute"):
        msgbus.register(endpoint, lambda msg, e=endpoint: received["other"].append(e + ":" + type(msg).__name__))
    http = OfflineHttpClient(clock=clock, api_key=PLACEHOLDER_KEY, api_secret=PLACEHOLDER_KEY, base_url=BASE_HTTP)
    http._client = transport  # transport injection: upstream pyo3 HttpClient replaced, never used
    account_type = BinanceAccountType.USDT_FUTURES
    provider = BinanceFuturesInstrumentProvider(client=http, clock=clock, account_type=account_type,
                                                config=InstrumentProviderConfig(load_all=True))
    config = BinanceExecClientConfig(account_type=account_type, base_url_http=BASE_HTTP, base_url_ws=BASE_WS,
                                     base_url_ws_stream=BASE_WS, environment=BinanceEnvironment.TESTNET)
    original_ws = user_ws.WebSocketClient
    user_ws.WebSocketClient = transport.websocket_class()  # WS transport injection
    client = None
    receipt = {"scenario": name, "startup": {"status": "OK"}, "routes": []}
    try:
        client = BinanceFuturesExecutionClient(
            loop=asyncio.get_running_loop(), client=http, msgbus=msgbus, cache=cache, clock=clock,
            instrument_provider=provider, base_url_ws=BASE_WS, config=config, account_type=account_type,
            environment=BinanceEnvironment.TESTNET, api_key=PLACEHOLDER_KEY, api_secret=PLACEHOLDER_KEY)
        require(client._ws_client._use_rest_listen_key, "expected native REST listenKey user-data mode")
        try:
            await client._connect()  # native startup: instruments, account, mode, clock, user stream
        except Rejected:
            raise
        except Exception as exc:
            receipt["startup"] = {"status": "REFUSED", "error_type": type(exc).__name__, "error": str(exc)}
        if receipt["startup"]["status"] == "OK":
            # Native startup reconciliation input, as the live engine requests it (no lookback cap).
            mass = await client.generate_mass_status(lookback_mins=None)
            if native is not None:
                native["mass"] = [("startup", mass)]
            receipt["routes"].append({"route": "startup", "mass_status": _mass(mass)})
            for index in (1, 2) if name == "reconnect_gap" else ():
                before = len(received["mass"])
                transport.interrupt(1)
                for _ in range(1000):
                    if len(received["mass"]) > before:
                        break
                    await asyncio.sleep(0)
                require(len(received["mass"]) == before + 1, "native after-resubscribe mass status not delivered")
                receipt["routes"].append({"route": f"reconnect/{index}", "mass_status": _mass(received["mass"][-1])})
                if native is not None:
                    native["mass"].append((f"reconnect/{index}", received["mass"][-1]))
            held = fixture["scenarios"][name]["held"]["orders"]
            observed = {o["venue_order_id"] for r in receipt["routes"] if r["mass_status"] for o in r["mass_status"]["orders"]}
            # Absence from a failed mass status is not evidence; only complete routes trigger the native lookup.
            complete = all(r["mass_status"] is not None for r in receipt["routes"])
            for voi, info in sorted(held.items()) if complete else ():
                if info["status"] in OPEN and voi not in observed:
                    report = await client.generate_order_status_report(GenerateOrderStatusReport(
                        instrument_id=InstrumentId.from_str(n3_01.NATIVE_ID), client_order_id=ClientOrderId(info["client_order_id"]),
                        venue_order_id=VenueOrderId(voi), command_id=UUID4(), ts_init=clock.timestamp_ns()))
                    receipt.setdefault("single_lookups", []).append({"venue_order_id": voi, "report": None if report is None else _stable(report)})
        account = cache.account(client.account_id)
        if native is not None:
            native.update(instrument=provider.find(InstrumentId.from_str(n3_01.NATIVE_ID)),
                          account_state=None if account is None else account.last_event)
        receipt["account"] = None if account is None else {
            "type": type(account).__name__, "id": str(account.id), "last_event": _stable_event(AccountState, account.last_event),
            "leverages": {str(k): str(v) for k, v in sorted(account.leverages().items(), key=lambda kv: kv[0].value)}}
        receipt["dual_side_position"] = client._is_dual_side_position
        receipt["unexpected_engine_messages"] = received["other"]
        receipt["mass_status_messages"] = len(received["mass"])
    finally:
        user_ws.WebSocketClient = original_ws
        if client is not None:
            client._ws_client._cancel_keepalive()
        for task in asyncio.all_tasks() - {asyncio.current_task()}:
            task.cancel()
    receipt["transport"] = [{k: v for k, v in e.items() if k != "body"} for e in transport.log]
    receipt["websocket"] = transport.ws
    receipt["injections"] = ["pyo3 HttpClient object -> OfflineTransport", "user_ws.WebSocketClient -> OfflineWebSocket",
                             "BinanceHttpClient.sign_request -> unsigned native send_request"]
    return receipt, transport.log


def _stable_event(cls, event):
    data = cls.to_dict(event)
    return {k: v for k, v in data.items() if k not in {"event_id", "ts_init"}}


def witness(fixture, name, receipt, log):
    """Read-only admission diagnostics. Never classifies anything as safe or resumable."""
    case, expected = fixture["scenarios"][name], fixture["expected_config"]
    held = case["held"]
    codes, unknown = {}, []

    def flag(code, ident=""):
        codes.setdefault(code, set()).add(str(ident))

    failed = [e for e in log if e.get("outcome") != "200"]
    for e in failed:
        flag("QUERY_FAILED", e["path"].rsplit("/", 1)[-1] + ":" + e["outcome"])
    if receipt["startup"]["status"] != "OK":
        flag("STARTUP_REFUSED", receipt["startup"]["error_type"])
    for e in log:
        if e.get("outcome") != "200":
            continue
        route, body = e["path"].rsplit("/", 1)[-1], e["body"]
        if "limit" in e["params"] and isinstance(body, list) and len(body) >= int(e["params"]["limit"]):
            flag("LOOKUP_CEILING_REACHED", route)
        if route == "dual" and body["dualSidePosition"]:
            flag("DUAL_SIDE_POSITION_MODE", "dualSidePosition=true")
        if route == "symbolConfig":
            for row in body:
                if row["marginType"] != expected["margin_type"]:
                    flag("MARGIN_TYPE_MISMATCH", row["marginType"])
        if route == "positionRisk":
            for row in body:
                if row["positionSide"] != "BOTH":
                    flag("DUAL_SIDE_POSITION_MODE", row["positionSide"])
                if row["updateTime"] < held["as_of_ms"]:
                    flag("STALE_POSITION_SNAPSHOT", row["updateTime"])
        if route == "account" and body["updateTime"] < held["as_of_ms"]:
            flag("STALE_ACCOUNT_SNAPSHOT", body["updateTime"])
    account = receipt.get("account")
    for instrument, leverage in (account or {}).get("leverages", {}).items():
        if Decimal(leverage) != Decimal(expected["leverage"]):
            flag("LEVERAGE_MISMATCH", instrument + ":" + leverage)
    routes = receipt["routes"]
    if not any(e["path"].endswith("/userTrades") for e in log) and receipt["startup"]["status"] == "OK":
        unknown.append("TRADE_HISTORY_NOT_QUERIED_BY_NATIVE_NO_ACTIVE_SYMBOL")
    for route in routes:
        mass = route["mass_status"]
        if mass is None:
            flag("MASS_STATUS_UNAVAILABLE", route["route"])
            continue
        if any(e["path"].rsplit("/", 1)[-1] in MASS_ROUTES for e in failed):
            # Native generate_* swallow BinanceError into []: never an authoritative empty snapshot.
            flag("NATIVE_REPORTS_AFTER_SWALLOWED_FAILURE", route["route"])
        _compare(mass, held, flag)
    if any(r["mass_status"] is None for r in routes) and any(o["status"] in OPEN for o in held["orders"].values()):
        unknown.append("HELD_OPEN_ORDERS_UNVERIFIED")
    for lookup in receipt.get("single_lookups", []):
        if lookup["report"] is None:
            flag("INTERNAL_ORDER_NOT_FOUND", lookup["venue_order_id"])
    if len(routes) == 3:
        repeat_identical = routes[1]["mass_status"] == routes[2]["mass_status"]
        if not repeat_identical:
            flag("REPEAT_REFRESH_DIVERGED")
    complete = not failed and receipt["startup"]["status"] == "OK" and routes and all(r["mass_status"] for r in routes) \
        and "LOOKUP_CEILING_REACHED" not in codes
    return {"scenario": name, "anomalies": {k: sorted(v) for k, v in sorted(codes.items())},
            "state_completeness": "COMPLETE_FOR_ISSUED_QUERIES" if complete else "INCOMPLETE_OR_UNKNOWN",
            "unknowns": unknown + ["FUNDING_LIQUIDATION_MULTI_CYCLE_ACCOUNTING_NOT_PROVED",
                                   "HISTORY_BEYOND_NATIVE_1000_ROW_NO_PAGINATION_NOT_RECOVERED"],
            "decision": DECISION}


def _compare(mass, held, flag):
    fills, seen = {}, {}
    for fill in mass["fills"]:
        fills.setdefault(fill["trade_id"], []).append(fill)
    for trade_id, rows in fills.items():
        if len(rows) > 1:
            same = all(r == rows[0] for r in rows)
            flag("DUPLICATE_TRADE_ID_IDENTICAL" if same else "DUPLICATE_TRADE_ID_CONFLICT", trade_id)
        seen[trade_id] = rows[0]
        if trade_id not in held["trades"]:
            flag("UNHELD_FILL_DISCOVERED", trade_id)
        else:
            want = held["trades"][trade_id]
            got = (Decimal(rows[0]["last_qty"]), Decimal(rows[0]["last_px"]), Decimal(rows[0]["commission"].split()[0]))
            if any(Decimal(r["last_qty"]) != got[0] or Decimal(r["commission"].split()[0]) != got[2] for r in rows) or \
                    got != (Decimal(want["qty"]), Decimal(want["price"]), Decimal(want["commission"])):
                flag("FILL_ECONOMICS_CHANGED", trade_id)
    for trade_id in held["trades"]:
        if trade_id not in seen:
            flag("HELD_FILL_ABSENT", trade_id)
    stamps = [f["ts_event"] for f in seen.values()]
    if len(set(stamps)) != len(stamps):
        flag("ORDERING_COLLISION", "equal fill ts_event")
    if stamps != sorted(stamps):
        flag("ORDERING_COLLISION", "native fill order not chronological")
    if list(seen) != sorted(seen, key=int):
        flag("ORDERING_COLLISION", "native trade_id order not numeric: " + ",".join(seen))
    for order in mass["orders"]:
        voi, status = order["venue_order_id"], order["order_status"]
        mine = Decimal(0)
        for trade_id, fill in seen.items():
            if fill["venue_order_id"] == voi:
                mine += Decimal(fill["last_qty"])
        if mine != Decimal(order["filled_qty"]):
            flag("MISSING_FILL" if mine < Decimal(order["filled_qty"]) else "FILL_EXCEEDS_ORDER", voi)
        if voi not in held["orders"]:
            if status in OPEN:
                flag("UNKNOWN_EXTERNAL_OPEN_ORDER", voi)
        elif held["orders"][voi]["status"] != status:
            flag("ORDER_STATE_ADVANCED", voi + ":" + held["orders"][voi]["status"] + "->" + status)
    net = Decimal(0)
    for fill in seen.values():
        net += Decimal(fill["last_qty"]) * (1 if fill["order_side"] == "BUY" else -1)
    position = Decimal(0)
    for row in mass["positions"]:
        position += Decimal(row["quantity"]) * {"LONG": 1, "SHORT": -1, "FLAT": 0}[row["position_side"]]
    if position != net:
        flag("POSITION_FILL_MISMATCH", f"{position}!={net}")
    if position != Decimal(held["position_amt"]):
        flag("POSITION_CHANGED_VS_HELD", f"{held['position_amt']}->{position}")


def run_all(fixture, loop):
    """Run every scenario on one loop created BEFORE the boundary (its self-pipe is AF_UNIX)."""
    require(sys.version_info[:3] == (3, 12, 10), "requires isolated CPython 3.12.10")
    for package, version in (("nautilus-trader", "1.231.0"), ("pyarrow", "25.0.1")):
        require(importlib.metadata.version(package) == version, "native pin mismatch")
    tape = n3_01.load_fixture(n3_01.FIXTURE)
    receipts, witnesses = {}, {}
    for name in SCENARIOS:
        receipt, log = loop.run_until_complete(_native_run(fixture, tape, name))
        loop.run_until_complete(asyncio.sleep(0))  # let cancelled native tasks finish
        receipts[name], witnesses[name] = receipt, witness(fixture, name, receipt, log)
        for route in receipt["routes"]:
            mass = route["mass_status"]
            if mass and len(mass["orders"]) > 20:
                # Bounded receipt: large history keeps count, digest and a sample only.
                mass["orders"] = {"count": len(mass["orders"]), "sha256": digest(mass["orders"]), "sample": mass["orders"][:2]}
    return receipts, witnesses


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    output = n3_01.prepare_output(args.output_dir)
    sys.dont_write_bytecode = True
    loop = asyncio.new_event_loop()
    seccomp = deny_socket_syscalls()
    output.mkdir()
    with safety_boundary(output) as boundary:
        try:
            fixture = load_fixture()
            receipts, witnesses = run_all(fixture, loop)
            require(not boundary["violations"], "observed forbidden behavior")
            require(hashlib.sha256(FIXTURE.read_bytes()).hexdigest() == FIXTURE_SHA256, "input changed during run")
            semantic = {"fixture_id": FIXTURE_ID, "native_pin": "1.231.0", "decision": DECISION,
                        "receipts": receipts, "witness": witnesses}
            records = {"semantic.json": semantic,
                       "provenance.json": {"pid": os.getpid(), "seccomp": seccomp, "native_calls": boundary["calls"],
                                           "violations": boundary["violations"], "upstream_modules": n3_01.upstream_inventory()}}
            hashes = {}
            for file, record in records.items():
                data = canonical(record) + b"\n"
                (output / file).write_bytes(data)
                hashes[file] = hashlib.sha256(data).hexdigest()
            manifest = {"fixture_id": FIXTURE_ID, "input_sha256": FIXTURE_SHA256, "semantic_sha256": digest(semantic),
                        "files": hashes, "module_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                        "decision": DECISION, "verdict": "N3_03_NATIVE_PRIVATE_RECONCILE_OBSERVED"}
            manifest["self_sha256"] = digest(manifest)
            (output / "manifest.json").write_bytes(canonical(manifest) + b"\n")
            print(json.dumps({"verdict": manifest["verdict"], "semantic_sha256": manifest["semantic_sha256"], "seccomp": seccomp}))
            return 0
        except Exception as exc:
            failure = {"verdict": "N3_03_BLOCKED", "error_type": type(exc).__name__, "error": str(exc),
                       "decision": DECISION, "violations": boundary["violations"]}
            (output / "failure.json").write_bytes(canonical(failure) + b"\n")
            print(json.dumps(failure), file=sys.stderr)
            return 2


if __name__ == "__main__":
    raise SystemExit(main())
