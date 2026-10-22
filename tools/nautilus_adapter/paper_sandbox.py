"""Private N2-01 offline proof. No runtime, native restart, or capital authority.

One bounded session per episode. Journals are disposable evidence; replay is a
read-only projection and deliberately imports no native execution components.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
from unittest.mock import patch

VERSION = "1.231.0"
SOURCE = "nautilus_sandbox_1.231.0_n2_01_v1"
LABELS = {"proof_only": True, "non_authoritative": True, "never_live_or_capital": True}
INSTRUMENT = "BTCUSDT-PERP.N2PROOF"
START = 1767225600000000000
SEED = 20261021
D = Decimal
# Closed fixtures: zero funding, no liquidation, leverage one, no client/config input.
SCENARIOS = {
    "flat": ((0, "100.00"), (0, "110.00")),
    "round_trip": ((1, "100.00"), (1, "105.00"), (0, "110.00")),
    "reversal": ((1, "100.00"), (-1, "110.00"), (0, "90.00")),
    "cancel": ((0, "100.00"),),
}
TYPES = {"AccountState", "OrderSubmitted", "OrderAccepted", "OrderFilled",
         "OrderCanceled", "OrderRejected", "PositionOpened", "PositionChanged", "PositionClosed"}


def _bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _hash(value):
    return hashlib.sha256(_bytes(value)).hexdigest()


def _decimal(value):
    if not isinstance(value, str):
        raise ValueError("amount must be a Decimal string")
    try:
        number = D(value)
    except InvalidOperation as exc:
        raise ValueError("invalid Decimal") from exc
    if not number.is_finite() or abs(number) > D("1000000"):
        raise ValueError("nonfinite/unbounded amount")
    return number


def _text(value):
    number = D(str(value))
    if not number.is_finite():
        raise ValueError("nonfinite native amount")
    return format(number.normalize(), "f") if number else "0"


def _money(value):
    amount, currency = value.split(" ")
    if currency != "USDT":
        raise ValueError("wrong money currency")
    return _decimal(amount)


def _observation_key(payload, sequence):
    # Native UUIDs vary. Preserve them in the journal; never relabel derived keys as native IDs.
    return _hash({"native_fields": {k: v for k, v in payload.items() if k != "event_id"},
                  "publication_sequence": sequence})


def _environment():
    if sys.implementation.name != "cpython" or sys.version_info[:2] != (3, 12):
        raise ValueError("CPython 3.12 required")
    lock = Path(__file__).with_name("requirements-win-py312.lock.txt")
    expected_lock = "4d39a0a1460506532671d8d947abf94c1c6a9dd8a61341352f8ae486194784d2"
    if hashlib.sha256(lock.read_bytes()).hexdigest() != expected_lock:
        raise ValueError("missing/wrong pinned lock")
    versions = {}
    for line in lock.read_text().splitlines():
        name, version = line.split("==")
        versions[name] = metadata.version(name)
        if versions[name] != version:
            raise ValueError(f"wrong pinned version: {name}")
    if versions["nautilus-trader"] != VERSION:
        raise ValueError("wrong Nautilus binary version")
    distribution = metadata.distribution("nautilus-trader")
    hashes = {}
    for entry in distribution.files or []:
        name = str(entry).replace("\\", "/")
        if name.startswith("nautilus_trader/") and (
            name.endswith((".pyd", ".so")) or name.startswith("nautilus_trader/adapters/sandbox/")
        ) and not name.endswith(".pyc"):
            digest = hashlib.sha256(distribution.locate_file(entry).read_bytes()).digest()
            if entry.hash is None or entry.hash.mode != "sha256" or (
                base64.urlsafe_b64encode(digest).decode().rstrip("=") != entry.hash.value
            ):
                raise ValueError(f"native installation RECORD mismatch: {name}")
            hashes[name] = digest.hex()
    if not hashes:
        raise ValueError("missing native binaries")
    return {"python": sys.version.split()[0], "versions": versions,
            "lock_sha256": expected_lock, "installed_sha256": hashes}


@contextmanager
def _offline():
    def deny(*args, **kwargs):
        raise RuntimeError("N2 proof denies network access")
    with patch.object(socket.socket, "connect", deny), patch.object(socket.socket, "connect_ex", deny), \
         patch.object(socket.socket, "sendto", deny), patch.object(socket, "getaddrinfo", deny):
        yield


def _scratch(directory):
    if Path(directory).is_symlink() or Path(directory).is_junction():
        raise ValueError("evidence directory must not redirect")
    root = Path(directory).resolve()
    temp = Path(tempfile.gettempdir()).resolve()
    if not root.is_relative_to(temp) or root == temp or root.is_symlink():
        raise ValueError("evidence must be in an isolated OS temp child")
    if root.exists() and any(root.iterdir()):
        raise ValueError("episode evidence directory must be empty")
    root.mkdir(parents=True, exist_ok=True)
    return root


def _run_episode(directory, scenario):
    if scenario not in SCENARIOS:
        raise ValueError("unsupported scenario/economic mode/venue")
    environment = _environment()
    root = _scratch(directory)
    # asyncio's Windows loop establishes its local wakeup socket before the network guard.
    loop = asyncio.new_event_loop()
    try:
        with _offline():
            return _execute(root, scenario, environment, loop)
    finally:
        loop.close()


def _execute(root, scenario, environment, loop):
    from nautilus_trader.adapters.sandbox.execution import SandboxExecutionClient
    from nautilus_trader.adapters.sandbox.config import SandboxExecutionClientConfig
    from nautilus_trader.backtest.models import FillModel
    from nautilus_trader.cache.cache import Cache
    from nautilus_trader.common.component import MessageBus, TestClock
    from nautilus_trader.common.factories import OrderFactory
    from nautilus_trader.core.uuid import UUID4
    from nautilus_trader.execution.engine import ExecutionEngine
    from nautilus_trader.execution.messages import SubmitOrder, CancelOrder
    from nautilus_trader.model.currencies import BTC, USDT
    from nautilus_trader.model.data import QuoteTick
    from nautilus_trader.model.enums import OrderSide
    from nautilus_trader.model.identifiers import TraderId, StrategyId, InstrumentId, Symbol, Venue
    from nautilus_trader.model.instruments import CryptoPerpetual
    from nautilus_trader.model.objects import Price, Quantity
    from nautilus_trader.portfolio.portfolio import Portfolio

    clock = TestClock()
    clock.set_time(START)
    trader, strategy = TraderId("PROOF-001"), StrategyId("PROOF-001")
    bus = MessageBus(trader_id=trader, clock=clock)
    cache = Cache()
    portfolio = Portfolio(bus, cache, clock)
    engine = ExecutionEngine(bus, cache, clock)
    rows = []
    journal = root / "events.jsonl"

    def observe(event):
        payload = type(event).to_dict(event)
        if payload["type"] not in TYPES:
            raise ValueError("unknown native event")
        if payload["type"] == "OrderSubmitted":
            order = cache.order(event.client_order_id)
            payload["observed_order_object"] = {
                "quantity": str(order.quantity), "side": order.side.name,
            }
        row = {"seq": len(rows), "scenario": scenario, "source": SOURCE,
               "version": VERSION, "previous": rows[-1]["sha256"] if rows else None,
               "observation_key_kind": "derived_proof_only", "payload": payload,
               "observation_key": _observation_key(payload, len(rows)),
               "native_republication_of": next((r["seq"] for r in rows
                   if r["payload"]["event_id"] == payload["event_id"]), None)}
        row["sha256"] = _hash(row)
        # Each complete observation is flushed, fsynced and closed before the next.
        with journal.open("ab") as handle:
            handle.write(_bytes(row) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        rows.append(row)

    for topic in ("events.order.*", "events.position.*", "events.account.*"):
        bus.subscribe(topic, observe)
    instrument = CryptoPerpetual(
        instrument_id=InstrumentId(Symbol("BTCUSDT-PERP"), Venue("N2PROOF")),
        raw_symbol=Symbol("BTCUSDT"), base_currency=BTC, quote_currency=USDT,
        settlement_currency=USDT, is_inverse=False, price_precision=2,
        price_increment=Price.from_str("0.01"), size_precision=3,
        size_increment=Quantity.from_str("0.001"), max_quantity=Quantity.from_str("2.000"),
        min_quantity=Quantity.from_str("0.001"), max_notional=None, min_notional=None,
        max_price=Price.from_str("1000.00"), min_price=Price.from_str("0.01"),
        margin_init=D("1"), margin_maint=D(".05"), maker_fee=D(".0004"),
        taker_fee=D(".0004"), ts_event=0, ts_init=0,
    )
    cache.add_instrument(instrument)
    client = SandboxExecutionClient(loop, portfolio, bus, cache, clock,
        SandboxExecutionClientConfig(venue="N2PROOF", starting_balances=["10000 USDT"],
                                     base_currency="USDT", default_leverage=D(1)))
    client.exchange.set_fill_model(FillModel(random_seed=SEED))
    engine.register_client(client)
    client.connect()
    factory = OrderFactory(trader, strategy, clock)
    checkpoints = []
    submitted = 0

    def snapshot(mark):
        account = cache.accounts()[0]
        fills = [r["payload"] for r in rows if r["payload"]["type"] == "OrderFilled"]
        realized = portfolio.realized_pnl(instrument.id)
        unrealized = portfolio.unrealized_pnl(instrument.id)
        balance = account.balance_total(USDT).as_decimal()
        quantity = sum((D(str(p.signed_qty)) for p in cache.positions_open()), D(0))
        return {"orders": {str(o.client_order_id): o.status.name for o in cache.orders()},
                "fill_ids": [f["trade_id"] for f in fills],
                "quantity": _text(quantity), "fees": _text(sum((_money(f["commission"]) for f in fills), D(0))),
                "realized_net": _text(realized.as_decimal() if realized else 0),
                "unrealized": _text(unrealized.as_decimal() if unrealized else 0),
                "balance": _text(balance), "equity": _text(balance + (unrealized.as_decimal() if unrealized else D(0))),
                "mark": mark}

    try:
        for step, (target, mark) in enumerate(SCENARIOS[scenario]):
            clock.set_time(START + step * 1_000_000_000)
            price = Price.from_str(mark)
            tick = QuoteTick(instrument.id, price, price, Quantity.from_str("100.000"),
                             Quantity.from_str("100.000"), clock.timestamp_ns(), clock.timestamp_ns())
            cache.add_quote_tick(tick)
            portfolio.update_quote_tick(tick)
            client.on_data(tick)
            current = sum((D(str(p.signed_qty)) for p in cache.positions_open()), D(0))
            delta = D(target) - current
            if delta:
                order = factory.market(instrument.id, OrderSide.BUY if delta > 0 else OrderSide.SELL,
                                       Quantity.from_str(f"{abs(delta):.3f}"))
                engine.execute(SubmitOrder(trader, strategy, order, UUID4(), clock.timestamp_ns()))
                submitted += 1
            if scenario == "cancel":
                order = factory.limit(instrument.id, OrderSide.BUY, Quantity.from_str("1.000"), Price.from_str("50.00"))
                engine.execute(SubmitOrder(trader, strategy, order, UUID4(), clock.timestamp_ns()))
                submitted += 1
                engine.execute(CancelOrder(trader, strategy, instrument.id, order.client_order_id,
                                          order.venue_order_id, UUID4(), clock.timestamp_ns()))
            checkpoints.append({"after_seq": len(rows) - 1, "native": snapshot(mark)})
    finally:
        client.disconnect()
    manifest = {**LABELS, "schema": 1, "source": SOURCE, "version": VERSION,
                "scenario": scenario, "seed": SEED, "fixture": [list(x) for x in SCENARIOS[scenario]],
                "environment": environment, "producer_pid": os.getpid(),
                "journal_sha256": hashlib.sha256(journal.read_bytes()).hexdigest(),
                "event_count": len(rows), "tail": rows[-1]["sha256"],
                "submissions": submitted, "checkpoints": checkpoints,
                "limitations": ["event replay only; no native durable restart/reconnect",
                                "no funding settlement or enforced liquidation proof",
                                "market OrderAccepted absent; resting limit acceptance observed"]}
    data = _bytes(manifest)
    (root / "manifest.json").write_bytes(data)
    return {"manifest_sha256": hashlib.sha256(data).hexdigest(), "producer_pid": os.getpid(),
            "source_observation": checkpoints[-1]["native"]}


def _reconstruct(directory, expected_manifest_sha256):
    """Read only. The caller must supply the independently retained manifest digest."""
    root = Path(directory)
    manifest_bytes = (root / "manifest.json").read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != expected_manifest_sha256:
        raise ValueError("untrusted/stale manifest")
    manifest = json.loads(manifest_bytes)
    scenario = manifest["scenario"]
    if (manifest["source"] != SOURCE or manifest["version"] != VERSION
        or scenario not in SCENARIOS or manifest["schema"] != 1 or manifest["seed"] != SEED
        or any(manifest.get(k) is not v for k, v in LABELS.items())
        or manifest["fixture"] != [list(x) for x in SCENARIOS[scenario]]):
        raise ValueError("mixed source/scenario/version/authority")
    raw = (root / "events.jsonl").read_bytes()
    if hashlib.sha256(raw).hexdigest() != manifest["journal_sha256"] or not raw.endswith(b"\n"):
        raise ValueError("corrupt/truncated journal")
    rows = [json.loads(line) for line in raw.splitlines()]
    if len(rows) != manifest["event_count"] or not rows:
        raise ValueError("missing events")
    orders, fill_ids, native_ids, keys = {}, [], {}, set()
    quantity = average = fees = gross = D(0)
    balance = D(10000)
    latest_position = D(0)
    checkpoints = []
    expected_checkpoints = manifest["checkpoints"]
    previous_time = 0
    for seq, row in enumerate(rows):
        payload = row["payload"]
        if (set(row) != {"seq", "scenario", "source", "version", "previous", "observation_key_kind", "payload", "observation_key", "sha256", "native_republication_of"}
            or row["seq"] != seq or row["scenario"] != scenario or row["source"] != SOURCE
            or row["version"] != VERSION or row["previous"] != (rows[seq-1]["sha256"] if seq else None)
            or row["sha256"] != _hash({k: v for k, v in row.items() if k != "sha256"})
            or row["observation_key_kind"] != "derived_proof_only"
            or row["observation_key"] != _observation_key(payload, seq)):
            raise ValueError("event identity/order/hash mismatch")
        kind = payload["type"]
        event_id = payload["event_id"]
        if kind not in TYPES or row["observation_key"] in keys:
            raise ValueError("unknown/duplicate native event")
        if event_id in native_ids:
            original = native_ids[event_id]
            # Native reversal republishes the same account object between close/open.
            # Retain both publications, never apply an economic fill twice.
            if (kind != "AccountState" or payload != rows[original]["payload"]
                or row["native_republication_of"] != original or scenario != "reversal"
                or rows[seq-1]["payload"]["type"] != "PositionClosed"
                or seq+1 == len(rows) or rows[seq+1]["payload"]["type"] != "PositionOpened"):
                raise ValueError("duplicate native event")
        elif row["native_republication_of"] is not None:
            raise ValueError("unbound native republication")
        else:
            native_ids[event_id] = seq
        keys.add(row["observation_key"])
        timestamp = payload["ts_init"]
        if not isinstance(timestamp, int) or timestamp < previous_time:
            raise ValueError("event time order")
        previous_time = timestamp
        if payload.get("account_id") != "N2PROOF-001":
            raise ValueError("wrong account")
        if kind != "AccountState" and (payload.get("instrument_id") != INSTRUMENT
            or payload.get("trader_id") != "PROOF-001" or payload.get("strategy_id") != "PROOF-001"):
            raise ValueError("wrong native identity")
        if kind == "AccountState":
            if payload["base_currency"] != "USDT" or payload["account_type"] != "MARGIN" or len(payload["balances"]) != 1:
                raise ValueError("wrong account units")
            item = payload["balances"][0]
            if item["currency"] != "USDT":
                raise ValueError("wrong balance currency")
            balance = _decimal(item["total"])
            if _decimal(item["free"]) + _decimal(item["locked"]) != balance:
                raise ValueError("invalid account balance")
            for margin in payload["margins"]:
                if margin["currency"] != "USDT" or margin["instrument_id"] != INSTRUMENT:
                    raise ValueError("wrong margin units")
                _decimal(margin["initial"])
                _decimal(margin["maintenance"])
        elif kind.startswith("Order"):
            order_id = payload["client_order_id"]
            if kind == "OrderSubmitted":
                spec = payload["observed_order_object"]
                size = _decimal(spec["quantity"])
                if order_id in orders or spec["side"] not in ("BUY", "SELL") or not D(0) < size <= D(2) or size % D('.001'):
                    raise ValueError("duplicate/invalid order")
                orders[order_id] = {"status": "SUBMITTED", "quantity": size, "side": spec["side"]}
            else:
                if order_id not in orders:
                    raise ValueError("unknown order reference")
                order = orders[order_id]
                if kind == "OrderAccepted":
                    if order["status"] != "SUBMITTED":
                        raise ValueError("wrong acceptance order")
                    order["status"] = "ACCEPTED"
                elif kind in ("OrderCanceled", "OrderRejected"):
                    if order["status"] not in ("SUBMITTED", "ACCEPTED"):
                        raise ValueError("wrong terminal order")
                    order["status"] = "CANCELED" if kind == "OrderCanceled" else "REJECTED"
                elif kind == "OrderFilled":
                    size, price = _decimal(payload["last_qty"]), _decimal(payload["last_px"])
                    commission = _money(payload["commission"])
                    if (order["status"] not in ("SUBMITTED", "ACCEPTED") or size != order["quantity"]
                        or payload["order_side"] != order["side"] or payload["currency"] != "USDT"
                        or not D(0) < price <= D(1000) or commission < 0
                        or payload["trade_id"] in fill_ids or commission != size * price * D('.0004')):
                        raise ValueError("invalid/duplicate economic fill")
                    fill_ids.append(payload["trade_id"])
                    delta = size if order["side"] == "BUY" else -size
                    if quantity * delta < 0:
                        gross += min(abs(quantity), size) * (price-average) * (1 if quantity > 0 else -1)
                    new_quantity = quantity + delta
                    if quantity == 0 or quantity * delta > 0:
                        average = (abs(quantity)*average + size*price) / abs(new_quantity)
                    elif new_quantity == 0:
                        average = D(0)
                    elif quantity * new_quantity < 0:
                        average = price
                    quantity = new_quantity
                    fees += commission
                    order["status"] = "FILLED"
        else:
            if (payload["opening_order_id"] not in orders or payload["currency"] != "USDT"
                or (payload.get("closing_order_id") is not None and payload["closing_order_id"] not in orders)):
                raise ValueError("unknown position order/units")
            _money(payload["realized_pnl"])
            latest_position = _decimal(_text(payload["signed_qty"]))
            if abs(latest_position) > 1 or _decimal(payload["quantity"]) != abs(latest_position):
                raise ValueError("invalid position units")
        for checkpoint in expected_checkpoints:
            if checkpoint["after_seq"] != seq:
                continue
            mark = checkpoint["native"]["mark"]
            unrealized = quantity * (_decimal(mark)-average) if quantity else D(0)
            projected = {"orders": {key: value["status"] for key, value in orders.items()},
                         "fill_ids": list(fill_ids), "quantity": _text(quantity), "fees": _text(fees),
                         "realized_net": _text(gross-fees), "unrealized": _text(unrealized),
                         "balance": _text(D(10000)+gross-fees),
                         "equity": _text(D(10000)+gross-fees+unrealized), "mark": mark}
            if projected != checkpoint["native"] or balance != D(projected["balance"]) or latest_position != quantity:
                raise ValueError("projection differs from native source observation")
            checkpoints.append(projected)
    if (rows[-1]["sha256"] != manifest["tail"] or len(checkpoints) != len(SCENARIOS[scenario])
        or len(orders) != manifest["submissions"] or any(o["status"] in ("SUBMITTED", "ACCEPTED") for o in orders.values())):
        raise ValueError("incomplete episode")
    return {**LABELS, "source": SOURCE, "scenario": scenario, "manifest_sha256": expected_manifest_sha256,
            "journal_sha256": manifest["journal_sha256"], "checkpoints": checkpoints,
            "new_orders": 0, "new_fills": 0, "adapter_calls": 0}


def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("episode", "replay"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("binding", help="closed scenario for episode; trusted manifest SHA256 for replay")
    args = parser.parse_args()
    if args.action == "episode":
        result = _run_episode(args.directory, args.binding)
    else:
        # Replay must work without even loading Nautilus, its adapter or CPW runtime.
        result = _reconstruct(args.directory, args.binding)
    print(json.dumps({"pid": os.getpid(), "native_loaded": "nautilus_trader" in sys.modules,
                      "result": result}, sort_keys=True))


if __name__ == "__main__":
    _main()
