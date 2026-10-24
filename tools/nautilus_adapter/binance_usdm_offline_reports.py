"""Private N3-01 synthetic native-parser proof. No execution or reconciliation authority.

Only the committed, hash-bound tape is accepted by the CLI. Native report UUIDs
are diagnostic only; economics, source identities and timestamps are deterministic.
Passive upstream imports are allowed by the controlling §5.H correction.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/nautilus_n3_01/binance_usdm_tape.json"
FIXTURE_SHA256 = "13edc5e485e45c862b2a776e181746057d9522f51c8779d5d2aaa9ce48bd3206"
FIXTURE_ID = "N3-01-BTCUSDT-USDM-SYNTHETIC-v1"
NO_AUTHORITY = "RECONCILIATION_REQUIRED / NO_NEW_ORDERS / NO_RESUME"
ACCOUNT = "BINANCE-N3TEST"
SYMBOL = "BTCUSDT"
NATIVE_ID = "BTCUSDT-PERP.BINANCE"
TOP_FIELDS = set("fixture_id schema notice venue symbol account_id account_mode exchange_info rest_orders stream trades positions duplicates snapshots".split())
ORDER_FIELDS = set("symbol orderId clientOrderId price origQty executedQty status timeInForce type side time updateTime avgPrice reduceOnly positionSide stopPrice workingType".split())
TRADE_FIELDS = set("symbol id orderId time commission commissionAsset price qty quoteQty buyer maker realizedPnl side positionSide".split())
POSITION_FIELDS = set("symbol positionSide positionAmt entryPrice markPrice unRealizedProfit liquidationPrice isolatedMargin updateTime marginType isAutoAddMargin leverage maxNotionalValue".split())
WS_FIELDS = set("s c S o f q p ap sp x X i l z L N n T t b a m R wt ot ps cp pP si ss rp gtd".split())
_AUDIT_STATE = None
_AUDIT_INSTALLED = False
CONTROL_MODULES = ("nautilus_trader.trading.trader", "nautilus_trader.trading.strategy",
                   "nautilus_trader.trading.controller", "nautilus_trader.risk.engine",
                   "nautilus_trader.execution.engine", "nautilus_trader.execution.manager",
                   "nautilus_trader.live.", "nautilus_trader.adapters.binance.execution")
CONTROL_NAMES = {"Trader", "Strategy", "RiskEngine", "ExecutionEngine", "OrderManager",
                 "OrderRouter", "BinanceCommonExecutionClient"}
ACTIVATION_NAMES = {"__init__", "start", "run", "connect", "register", "execute", "submit_order",
                    "cancel_order", "cancel_all_orders", "flatten", "_start", "_connect", "_execute"}


class Rejected(ValueError):
    """Invalid fixture or forbidden proof behavior."""


def require(condition, message):
    if not condition:
        raise Rejected(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def _credential_path(path):
    parts = {part.lower() for part in path.parts}
    return bool(parts & {".aws", ".ssh", ".azure", ".config/gcloud"}) or any(
        part in {".env", "credentials", "credentials.json", "id_rsa", "id_ed25519"}
        or part.startswith(".env.") for part in parts)


def _audit(event, args):
    state = _AUDIT_STATE
    if state is None:
        return
    reason = None
    if event.startswith("socket.") or event in {"subprocess.Popen", "os.system", "os.posix_spawn", "os.exec", "os.fork"}:
        reason = event
    elif event == "import":
        # Import graph is descriptive; stock upstream modules are never replaced.
        state["imports"].append({"module": args[0], "importer": sys._getframe(1).f_globals.get("__name__")})
        if args[0] == "src" or args[0].startswith(("src.", "lib.")):
            reason = "protected CPW import"
    elif event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        path = Path(os.fsdecode(args[0])).absolute()
        if _credential_path(path):
            reason = "credential file access"
        mode, flags = args[1:3]
        writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
            isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if writing and not path.resolve().is_relative_to(state["output"]):
            reason = "write outside external evidence"
    elif event in {"os.remove", "os.rmdir", "os.rename", "os.link", "os.symlink", "os.chmod", "os.truncate", "os.mkdir"}:
        # Proof outputs are write-once ordinary files. No renames/links/deletion.
        if event != "os.mkdir" or not Path(args[0]).resolve().is_relative_to(state["output"]):
            reason = "filesystem mutation: " + event
    if reason:
        state["violations"].append(reason)
        raise Rejected("BOUNDARY: " + reason)


def _profile(frame, event, arg):
    if event != "call":
        return
    state = _AUDIT_STATE
    if state is None:
        return
    module = frame.f_globals.get("__name__", "")
    name = frame.f_code.co_name
    obj = frame.f_locals.get("self")
    cls = type(obj).__name__ if obj is not None else ""
    reason = None
    if module == "os" and name in {"__getitem__", "getenv"}:
        key = str(frame.f_locals.get("key", "")).upper()
        if any(s in key for s in ("SECRET", "TOKEN", "PASSWORD", "API_KEY", "BINANCE")):
            reason = "credential environment access"
    if (module == "hmac" and name in {"new", "__init__", "digest", "hexdigest", "update", "_init_hmac", "_init_old"}) or name in {"sign", "sign_request", "_sign", "_sign_request"}:
        reason = "signing"
    if (cls in CONTROL_NAMES and name in ACTIVATION_NAMES) or (
        module.startswith(CONTROL_MODULES) and name in ACTIVATION_NAMES
        and name not in {"__new__", "__init_subclass__"}):
        reason = "authority runtime entry: " + module + "." + name
    if reason:
        state["violations"].append(reason)
        raise Rejected("BOUNDARY: " + reason)


@contextmanager
def safety_boundary(output):
    """Python-visible audit/profile boundary, not a claim about arbitrary native syscalls.

    Installed before native imports. No upstream monkeypatches or fake modules.
    Static tests separately prohibit direct bindings to authority APIs.
    """
    global _AUDIT_STATE, _AUDIT_INSTALLED
    require(_AUDIT_STATE is None, "nested boundary")
    output = Path(output).resolve()
    if not _AUDIT_INSTALLED:
        sys.addaudithook(_audit)
        _AUDIT_INSTALLED = True
    state = {"output": output, "imports": [], "violations": []}
    previous_profile = sys.getprofile()
    _AUDIT_STATE = state
    sys.setprofile(_profile)
    try:
        yield state
    finally:
        sys.setprofile(previous_profile)
        _AUDIT_STATE = None


def number(value, *, signed=False, positive=False):
    require(isinstance(value, str), "amount must be a decimal string")
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise Rejected("malformed decimal") from exc
    require(amount.is_finite() and (signed or amount >= 0), "nonfinite/negative amount")
    require(not positive or amount > 0, "amount must be positive")
    return amount


def identity(row, *, ws=False):
    require(set(row) == (WS_FIELDS if ws else ORDER_FIELDS), "closed order payload fields")
    require(row.get("s" if ws else "symbol") == SYMBOL, "unrecognized symbol")
    require(row.get("ps" if ws else "positionSide") == "BOTH", "unrecognized position mode")
    oid = row.get("i" if ws else "orderId")
    require(type(oid) is int and oid > 0, "missing/invalid order ID")
    cid = row.get("c" if ws else "clientOrderId")
    require(isinstance(cid, str) and 0 < len(cid) <= 36, "missing client ID")


def timestamp(value):
    require(type(value) is int and 1700000000000 <= value <= 1700000010000, "invalid timestamp")
    return value


def validate(tape):
    """Bounded fixture consistency checks, never an OMS state transition engine."""
    require(isinstance(tape, dict) and set(tape) == TOP_FIELDS, "closed tape fields")
    _validate_amounts(tape)
    require(tape["fixture_id"] == FIXTURE_ID and tape["schema"] == "nautilus-binance-1.231.0", "fixture/schema identity")
    require(tape["notice"].startswith("TEST FIXTURE ONLY;"), "synthetic disclosure")
    require((tape["venue"], tape["symbol"], tape["account_id"], tape["account_mode"]) ==
            ("BINANCE", SYMBOL, ACCOUNT, "ONE_WAY"), "venue/symbol/account mode")
    info = tape["exchange_info"]
    require((info["symbol"], info["pair"], info["contractType"], info["baseAsset"], info["quoteAsset"], info["marginAsset"]) ==
            (SYMBOL, SYMBOL, "PERPETUAL", "BTC", "USDT", "USDT"), "not BTCUSDT linear USD-M")
    filters = {f["filterType"]: f for f in info["filters"]}
    require(len(filters) == len(info["filters"]) == 3 and set(filters) == {"PRICE_FILTER", "LOT_SIZE", "MIN_NOTIONAL"}, "closed filters")
    pf, lot = filters["PRICE_FILTER"], filters["LOT_SIZE"]
    require(set(pf) == {"filterType", "minPrice", "maxPrice", "tickSize"}
            and set(lot) == {"filterType", "minQty", "maxQty", "stepSize"}
            and set(filters["MIN_NOTIONAL"]) == {"filterType", "notional"}, "closed filter payloads")
    tick, step = number(pf["tickSize"], positive=True), number(lot["stepSize"], positive=True)
    for value in (pf["minPrice"], pf["maxPrice"]):
        require(number(value, positive=True) % tick == 0, "invalid price filter step")
    for value in (lot["minQty"], lot["maxQty"]):
        require(number(value, positive=True) % step == 0, "invalid quantity filter step")
    require(number(lot["minQty"]) <= number(lot["maxQty"]) and number(pf["minPrice"]) <= number(pf["maxPrice"]), "filter range")
    number(filters["MIN_NOTIONAL"]["notional"], positive=True)
    require(type(info["pricePrecision"]) is int and type(info["quantityPrecision"]) is int, "precision type")
    require(tick.as_tuple().exponent < 0 and step.as_tuple().exponent < 0, "fixture requires fractional tick/step")
    orders, stream, trades = tape["rest_orders"], tape["stream"], tape["trades"]
    require(len(orders) == len(stream) == 5 and len(trades) == 2 and len(tape["positions"]) == 3, "finite lifecycle inventory")
    expected = [(101, "NEW"), (101, "PARTIALLY_FILLED"), (101, "FILLED"), (202, "NEW"), (202, "CANCELED")]
    previous = {}
    for row, event, (oid, status) in zip(orders, stream, expected, strict=True):
        identity(row)
        require((row["orderId"], row["status"]) == (oid, status), "lifecycle order precedence")
        require(row["side"] in {"BUY", "SELL"} and row["type"] == "LIMIT" and row["timeInForce"] == "GTC", "closed order enums")
        require(type(row["reduceOnly"]) is bool, "reduceOnly type")
        qty, filled, px = number(row["origQty"], positive=True), number(row["executedQty"]), number(row["price"], positive=True)
        require(qty % step == filled % step == px % tick == 0, "order off filter step")
        require(number(lot["minQty"]) <= qty <= number(lot["maxQty"]) and
                number(pf["minPrice"]) <= px <= number(pf["maxPrice"]), "order outside filters")
        require(qty * px >= number(filters["MIN_NOTIONAL"]["notional"]), "order below minimum notional")
        require(0 <= filled <= qty and (status != "FILLED" or filled == qty), "inconsistent filled quantity")
        require(status != "NEW" or filled == 0, "NEW with fills")
        require(status != "PARTIALLY_FILLED" or 0 < filled < qty, "invalid partial quantity")
        at, updated = timestamp(row["time"]), timestamp(row["updateTime"])
        require(at <= updated and (oid not in previous or previous[oid][0] < updated), "timestamp/order precedence")
        if oid in previous:
            require(previous[oid][1:] == (row["clientOrderId"], row["origQty"], row["side"], row["reduceOnly"], row["price"]), "order identity conflict")
        previous[oid] = (updated, row["clientOrderId"], row["origQty"], row["side"], row["reduceOnly"], row["price"])
        number(row["avgPrice"])
        number(row["stopPrice"])
        require(set(event) == {"e", "E", "T", "o"} and event["e"] == "ORDER_TRADE_UPDATE", "unknown streaming message")
        body = event["o"]
        identity(body, ws=True)
        require(timestamp(event["E"]) == timestamp(event["T"]) == timestamp(body["T"]) == updated, "WS timestamp pairing")
        for key, rkey in [("i", "orderId"), ("c", "clientOrderId"), ("X", "status"), ("S", "side"), ("q", "origQty"),
                          ("z", "executedQty"), ("p", "price"), ("R", "reduceOnly"), ("ap", "avgPrice")]:
            require(body[key] == row[rkey], "REST/WS source identity conflict")
        for key in ("l", "z", "L", "n", "b", "a", "rp", "sp"):
            number(body[key])
        require(body["x"] in {"NEW", "TRADE", "CANCELED"} and body["wt"] == "CONTRACT_PRICE", "unknown WS enum")
    seen = set()
    total = Decimal(0)
    for trade, index in zip(trades, (1, 2), strict=True):
        _validate_trade(trade, step, tick)
        require(trade["id"] not in seen, "duplicate primary trade ID")
        seen.add(trade["id"])
        body = stream[index]["o"]
        for key, tkey in [("t", "id"), ("i", "orderId"), ("T", "time"), ("l", "qty"), ("L", "price"), ("n", "commission"), ("N", "commissionAsset"), ("m", "maker"), ("S", "side")]:
            require(body[key] == trade[tkey], "trade/WS identity or economics conflict")
        total += number(trade["qty"])
        require(total == number(body["z"]), "inconsistent cumulative fill")
    require(total == number(orders[2]["executedQty"]), "missing lifecycle fill")
    for position in tape["positions"]:
        _validate_position(position, step)
    require([number(p["positionAmt"], signed=True) for p in tape["positions"]] == [Decimal(0), total, -total], "flat/long/short observations")
    require(len(tape["duplicates"]) == 2, "bounded duplicate inventory")
    for duplicate in tape["duplicates"]:
        _validate_trade(duplicate, step, tick)
        require(duplicate["id"] in seen, "duplicate references unknown trade")
    require(len(tape["snapshots"]) == 3, "bounded snapshot inventory")
    for case, name in zip(tape["snapshots"], ("consistent", "missing_fill", "external_order"), strict=True):
        require(set(case) == set("case_id snapshot_id snapshot_time stream_indices held_trade_ids open_orders position trades symbol account_mode account_id".split()), "closed snapshot fields")
        require(case["case_id"] == name and case["snapshot_id"] == "N3-" + name, "cross-paired snapshot identity")
        require((case["symbol"], case["account_mode"], case["account_id"]) == (SYMBOL, "ONE_WAY", ACCOUNT), "cross-paired snapshot account")
        stamp = timestamp(case["snapshot_time"])
        require(case["stream_indices"] == [0, 1] and case["held_trade_ids"] == [501], "closed held-receipt cursor")
        require(all(stream[i]["T"] <= stamp for i in case["stream_indices"]), "snapshot before stream cursor")
        _validate_position(case["position"], step)
        require(case["position"]["updateTime"] == stamp, "cross-paired position timestamp")
        require(len(case["trades"]) <= 2 and len(case["open_orders"]) <= 2, "bounded REST view")
        require(len({t["id"] for t in case["trades"]}) == len(case["trades"]), "duplicate snapshot fill")
        for trade in case["trades"]:
            _validate_trade(trade, step, tick)
            require(trade in trades and trade["time"] <= stamp, "cross-paired snapshot trade")
        require(sum((number(t["qty"]) for t in case["trades"]), Decimal(0)) == number(case["position"]["positionAmt"], signed=True), "snapshot position/fill mismatch")
        require(len({o["orderId"] for o in case["open_orders"]}) == len(case["open_orders"]), "duplicate snapshot order")
        for row in case["open_orders"]:
            identity(row)
            require(row["status"] in {"NEW", "PARTIALLY_FILLED"} and timestamp(row["updateTime"]) <= stamp, "invalid open order view")
            # The one deliberate external order is explicit synthetic proof data.
            expected_row = orders[1] if row["orderId"] == 101 else dict(orders[0], orderId=303, clientOrderId="N3-EXTERNAL", time=stamp, updateTime=stamp)
            require(row == expected_row, "snapshot order identity conflict")


def _validate_trade(row, step, tick):
    require(set(row) == TRADE_FIELDS, "closed fill payload fields")
    require(row.get("symbol") == SYMBOL and row.get("positionSide") == "BOTH", "fill symbol/mode")
    require(type(row.get("id")) is int and row["id"] > 0 and row.get("orderId") == 101, "missing trade/order ID")
    require(row.get("side") == "BUY" and row.get("buyer") is True and type(row.get("maker")) is bool, "fill side/liquidity")
    require(row.get("commissionAsset") == "USDT", "fee asset")
    qty, px = number(row["qty"], positive=True), number(row["price"], positive=True)
    require(qty % step == px % tick == 0, "fill off step")
    require(number(row["quoteQty"]) == qty * px, "fill quote mismatch")
    number(row["commission"])
    number(row["realizedPnl"], signed=True)
    timestamp(row["time"])


def _validate_position(row, step):
    require(set(row) == POSITION_FIELDS, "closed position payload fields")
    require(row.get("symbol") == SYMBOL and row.get("positionSide") == "BOTH", "position symbol/mode")
    require(number(row["positionAmt"], signed=True) % step == 0, "position off step")
    for key in ("entryPrice", "markPrice", "liquidationPrice", "isolatedMargin"):
        number(row[key])
    number(row["unRealizedProfit"], signed=True)
    timestamp(row["updateTime"])


def _validate_amounts(value):
    """Reject invalid decimal fields even when a native parser ignores them."""
    amount_fields = set("price origQty executedQty avgPrice stopPrice commission qty quoteQty realizedPnl positionAmt entryPrice markPrice unRealizedProfit liquidationPrice isolatedMargin leverage maxNotionalValue maintMarginPercent requiredMarginPercent triggerProtect liquidationFee marketTakeBound minPrice maxPrice tickSize minQty maxQty stepSize notional q p ap sp l z L n b a rp".split())
    signed_fields = {"positionAmt", "unRealizedProfit", "realizedPnl", "rp"}
    if isinstance(value, dict):
        for key, child in value.items():
            if key in amount_fields:
                number(child, signed=key in signed_fields)
            else:
                _validate_amounts(child)
    elif isinstance(value, list):
        for child in value:
            _validate_amounts(child)


def parse_tape(tape):
    """Return stable observations, raw reports and actual native domain objects.

    Native conversions own every report and instrument. Additional validation is
    fixture admissibility, not a competing report mapper or execution policy.
    """
    validate(tape)
    require(sys.version_info[:3] == (3, 12, 10), "requires isolated CPython 3.12.10")
    for package, version in (("nautilus-trader", "1.231.0"), ("pyarrow", "25.0.1")):
        require(importlib.metadata.version(package) == version, "native pin mismatch")
    import msgspec
    from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
    from nautilus_trader.adapters.binance.common.schemas.account import BinanceOrder, BinanceUserTrade
    from nautilus_trader.adapters.binance.futures.enums import BinanceFuturesEnumParser
    from nautilus_trader.adapters.binance.futures.providers import BinanceFuturesInstrumentProvider
    from nautilus_trader.adapters.binance.futures.schemas.account import BinanceFuturesPositionRisk
    from nautilus_trader.adapters.binance.futures.schemas.market import BinanceFuturesSymbolInfo
    from nautilus_trader.common.providers import InstrumentProvider
    from nautilus_trader.core.uuid import UUID4
    from nautilus_trader.model.identifiers import AccountId, ClientOrderId, InstrumentId, Venue, VenueOrderId
    from nautilus_trader.adapters.binance.futures.schemas.user import BinanceFuturesOrderData

    def decode(row, kind):
        require(set(row) <= set(kind.__struct_fields__), "unknown native payload field")
        return msgspec.convert(row, type=kind, strict=True)

    class FixedClock:
        def timestamp_ns(self):
            return 1700000000000000000

    class OfflineProvider(BinanceFuturesInstrumentProvider):
        def __init__(self):
            # The native base owns instrument storage. Skip ONLY the venue
            # constructor, whose HTTP API objects are irrelevant to conversion.
            InstrumentProvider.__init__(self)
            self._clock = FixedClock()
            self._account_type = BinanceAccountType.USDT_FUTURES
            self._venue = Venue("BINANCE")
            self._log_warnings = True

    provider = OfflineProvider()
    provider._parse_instrument(decode(tape["exchange_info"], BinanceFuturesSymbolInfo), 1700000000000000000)
    instrument_id = InstrumentId.from_str(NATIVE_ID)
    instrument = provider.find(instrument_id)
    require(instrument is not None and provider.count == 1, "native instrument conversion refused")
    account, enums = AccountId(ACCOUNT), BinanceFuturesEnumParser()
    raw, native = [], [instrument]

    def retain(report, source):
        native.append(report)
        full = report.to_dict()
        raw.append({"source": source, "report": full})
        stable = {k: v for k, v in full.items() if k != "report_id"}
        for attr in ("order_status", "order_side", "liquidity_side", "position_side"):
            if hasattr(report, attr):
                stable[attr] = getattr(report, attr).name
        return {"source": source, "native": stable}

    def order(row, source):
        report = decode(row, BinanceOrder).parse_to_order_status_report(
            account, instrument_id, UUID4(), enums, False, row["updateTime"] * 1000000)
        return retain(report, source)

    def fill(row, source):
        report = decode(row, BinanceUserTrade).parse_to_fill_report(
            account, instrument_id, UUID4(), row["time"] * 1000000, use_position_ids=False)
        return retain(report, source)

    def position(row, source):
        report = decode(row, BinanceFuturesPositionRisk).parse_to_position_status_report(
            account, instrument_id, enums, UUID4(), row["updateTime"] * 1000000)
        observation = retain(report, source)
        observation["source_position_amt"] = row["positionAmt"]
        observation["source_update_time_ms"] = row["updateTime"]
        return observation

    rest = [order(row, f"rest_orders/{i}") for i, row in enumerate(tape["rest_orders"])]
    streaming = []
    for i, event in enumerate(tape["stream"]):
        body = event["o"]
        report = decode(body, BinanceFuturesOrderData).parse_to_order_status_report(
            account, instrument_id, ClientOrderId(body["c"]), VenueOrderId(str(body["i"])),
            event["T"] * 1000000, event["E"] * 1000000, enums)
        observation = retain(report, f"stream/{i}")
        observation["source_last_qty"] = body["l"]
        observation["source_trade_id"] = body["t"]
        streaming.append(observation)
    fills = [fill(row, f"trades/{i}") for i, row in enumerate(tape["trades"])]
    positions = [position(row, f"positions/{i}") for i, row in enumerate(tape["positions"])]
    # Same ID is never counted again. Conflicting data remains explicitly
    # untrusted; no account economic idempotency or native dedup is claimed.
    counted = {r["id"]: r for r in tape["trades"]}
    duplicates = []
    for i, row in enumerate(tape["duplicates"]):
        observed = fill(row, f"duplicates/{i}")
        same = canonical(row) == canonical(counted[row["id"]])
        duplicates.append({"trade_id": row["id"], "classification": "IDENTICAL_DUPLICATE" if same else "CONFLICTING_DUPLICATE",
                           "counted": False, "native_observation": observed, "authority": NO_AUTHORITY})
    cases = []
    for case in tape["snapshots"]:
        prefix = "snapshots/" + case["case_id"]
        open_reports = [order(row, prefix + "/order/" + str(i)) for i, row in enumerate(case["open_orders"])]
        fill_reports = [fill(row, prefix + "/trade/" + str(i)) for i, row in enumerate(case["trades"])]
        pos_report = position(case["position"], prefix + "/position")
        held_orders = {streaming[i]["native"]["venue_order_id"]: streaming[i]["native"] for i in case["stream_indices"]}
        held_fills = [r["native"] for r in fills if int(r["native"]["trade_id"]) in case["held_trade_ids"]]
        unknown = [r["native"]["venue_order_id"] for r in open_reports if r["native"]["venue_order_id"] not in held_orders]
        missing = [r["native"]["trade_id"] for r in fill_reports if int(r["native"]["trade_id"]) not in case["held_trade_ids"]]
        held_qty = sum((Decimal(r["last_qty"]) for r in held_fills), Decimal(0))
        drift = held_qty != Decimal(pos_report["source_position_amt"])
        classes = (["UNSEEN_EXTERNAL_ORDER"] if unknown else []) + (["MISSING_FILL"] if missing else []) + (["POSITION_DRIFT"] if drift else [])
        cases.append({"case_id": case["case_id"], "snapshot_id": case["snapshot_id"], "classifications": classes or ["CONSISTENT_INPUTS"],
                      "unseen_order_ids": unknown, "missing_trade_ids": missing, "open_orders": open_reports,
                      "fills": fill_reports, "position": pos_report, "authority": NO_AUTHORITY})
    semantic = {
        "fixture_id": FIXTURE_ID, "synthetic_only": True, "native_pin": "1.231.0", "authority": NO_AUTHORITY,
        "instrument": {"type": type(instrument).__name__, "id": str(instrument.id), "is_inverse": instrument.is_inverse,
                       "price_precision": instrument.price_precision, "size_precision": instrument.size_precision,
                       **{key: str(getattr(instrument, key)) for key in ("price_increment", "size_increment", "min_quantity", "max_quantity", "min_notional")}},
        "rest_orders": rest, "stream": streaming, "fills": fills, "positions": positions,
        "counted_trade_ids": [r["native"]["trade_id"] for r in fills], "duplicates": duplicates, "snapshots": cases,
        "limits": ["UUID report_id excluded only from stable projection; retained raw",
                   "WS native ts_accepted is supplied event time, not REST creation time",
                   "Position native ts_last uses ts_init; supplied fixed observation timestamp is recorded",
                   "REST native FillReport has no client ID; venue ID joins remain observations",
                   "Duplicate exclusion is this bounded projection, not native account idempotency",
                   "Informational inputs only; no venue reconcile, recovery, policy or resume"]}
    return semantic, raw, native


def load_fixture(path):
    path = Path(path)
    require(path.is_absolute() and not path.is_symlink() and path.resolve() == FIXTURE, "only controlled absolute fixture path")
    data = path.read_bytes()
    require(len(data) < 100000 and hashlib.sha256(data).hexdigest() == FIXTURE_SHA256, "fixture SHA-256 mismatch")
    def pairs(items):
        obj = {}
        for key, value in items:
            require(key not in obj, "duplicate JSON key")
            obj[key] = value
        return obj
    return json.loads(data, object_pairs_hook=pairs)


def prepare_output(path):
    path = Path(path)
    require(path.is_absolute(), "external output must be absolute")
    resolved = path.resolve()
    require(not any((parent / ".git").exists() for parent in [resolved, *resolved.parents]), "output must be outside Git")
    require(all(not parent.is_symlink() for parent in [path, *path.parents]), "output symlink")
    require(not resolved.exists() and resolved.parent.is_dir(), "output must be new with existing parent")
    return resolved


def upstream_inventory():
    result = []
    for name, module in sorted(sys.modules.items()):
        if not name.startswith("nautilus_trader."):
            continue
        file = getattr(module, "__file__", None)
        if file and Path(file).is_file():
            result.append({"module": name, "path": file, "sha256": hashlib.sha256(Path(file).read_bytes()).hexdigest()})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=FIXTURE)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    output = prepare_output(args.output_dir)
    # Caller must use -B. Also prevent dependency bytecode writes in this CLI.
    sys.dont_write_bytecode = True
    with safety_boundary(output) as boundary:
        output.mkdir()
        try:
            tape = load_fixture(args.fixture)
            semantic, raw, _ = parse_tape(tape)
            require(not boundary["violations"], "observed forbidden behavior")
            require(hashlib.sha256(FIXTURE.read_bytes()).hexdigest() == FIXTURE_SHA256, "input changed during parse")
            records = {"observations.json": semantic, "native-diagnostics.json": raw,
                       "boundary.json": {"imports": boundary["imports"], "upstream_modules": upstream_inventory(),
                                         "violations": boundary["violations"],
                                         "limits": "Python audit/profile + source checks; not arbitrary native-syscall containment"}}
            hashes = {}
            for name, record in records.items():
                data = canonical(record) + b"\n"
                (output / name).write_bytes(data)
                hashes[name] = hashlib.sha256(data).hexdigest()
            manifest = {"fixture_id": FIXTURE_ID, "input_sha256": FIXTURE_SHA256, "semantic_sha256": digest(semantic),
                        "files": hashes, "module_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                        "authority": NO_AUTHORITY, "verdict": "N3_01_LINUX_NATIVE_OFFLINE_PASSED"}
            manifest["self_sha256"] = digest(manifest)
            (output / "manifest.json").write_bytes(canonical(manifest) + b"\n")
            print(json.dumps({"verdict": manifest["verdict"], "semantic_sha256": manifest["semantic_sha256"]}))
            return 0
        except Exception as exc:
            # Invalid data gets failure details only, never normalized records.
            failure = {"verdict": "FAILED", "error_type": type(exc).__name__, "error": str(exc),
                       "authority": NO_AUTHORITY, "violations": boundary["violations"]}
            (output / "failure.json").write_bytes(canonical(failure) + b"\n")
            print(json.dumps(failure), file=sys.stderr)
            return 2


if __name__ == "__main__":
    raise SystemExit(main())
