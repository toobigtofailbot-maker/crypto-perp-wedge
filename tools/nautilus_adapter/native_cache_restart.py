"""Closed N2-02 native Redis proof; no runtime or trading-resumption authority.

The external test controller owns the single loopback Redis container. Restart
constructs no execution client: sandbox construction resets its simulated venue.
"""
from __future__ import annotations

import argparse
import asyncio
from collections import Counter
from decimal import Decimal as D
import hashlib
from importlib import metadata
import base64
import json
import os
from pathlib import Path
import re
import subprocess
import time

from tools.nautilus_adapter import paper_sandbox as fixture

SOURCE = "cpw_n2_02_native_redis_v1"
CONTAINER = "cpw-n2-02-redis-20261022"
PORT = 16482
SCENARIOS = ("round_trip", "reversal")
STATUS = "RECONCILIATION_UNVERIFIED / NO_NEW_ORDERS"


def environment():
    result = fixture._environment()
    if result["python"] != "3.12.10":
        raise ValueError("wrong interpreter patch")
    distribution = metadata.distribution("nautilus-trader")
    paths = {"system/kernel.py", "cache/config.py", "cache/database.pyx", "cache/cache.pyx",
             "common/config.py", "live/config.py", "live/node.py", "live/node_builder.py",
             "live/execution_engine.py", "execution/engine.pyx"}
    for entry in distribution.files:
        if str(entry).replace("\\", "/").removeprefix("nautilus_trader/") in paths:
            digest = hashlib.sha256(distribution.locate_file(entry).read_bytes()).digest()
            if entry.hash is None or entry.hash.mode != "sha256" or base64.urlsafe_b64encode(digest).decode().rstrip("=") != entry.hash.value:
                raise ValueError("pinned native source RECORD mismatch")
            result["installed_sha256"][str(entry).replace("\\", "/")] = digest.hex()
    if not all("nautilus_trader/" + p in result["installed_sha256"] for p in paths):
        raise ValueError("missing native source provenance")
    return result


def backend():
    """Verify the owned container before opening the sole permitted endpoint."""
    import redis

    result = subprocess.run(["docker", "inspect", CONTAINER], capture_output=True,
                            text=True, check=True, timeout=10)
    info = json.loads(result.stdout)[0]
    if (info["Config"]["Labels"].get("cpw.wp") != "CPW-NAUTILUS-N2-02"
        or info["NetworkSettings"]["Ports"]["6379/tcp"] != [
            {"HostIp": "127.0.0.1", "HostPort": str(PORT)}]):
        raise ValueError("unowned/non-loopback backend")
    db = redis.Redis(host="127.0.0.1", port=PORT, socket_timeout=3,
                     socket_connect_timeout=3)
    server = db.info("server")
    if tuple(map(int, server["redis_version"].split(".")[:2])) < (6, 2):
        raise ValueError("unsupported Redis")
    if (db.config_get("appendonly") != {"appendonly": "yes"}
        or db.config_get("appendfsync") != {"appendfsync": "always"}):
        raise ValueError("durability configuration changed")
    return db, {"container_id": info["Id"], "image_id": info["Image"],
                "run_id": server["run_id"], "redis_version": server["redis_version"],
                "host": "127.0.0.1", "port": PORT, "appendfsync": "always"}


def namespace(trader):
    if not isinstance(trader, str) or not re.fullmatch(r"N2R[0-9a-f]{12}-001", trader):
        raise ValueError("not an owned proof trader")
    return "trader-" + trader + ":"


def records(db, trader):
    prefix = namespace(trader)
    result = {}
    for key in sorted(db.scan_iter(match=prefix + "*")):
        kind = db.type(key).decode()
        if kind == "none":
            continue  # Native asynchronous index updates may remove an empty set during SCAN.
        # Hash only: no Redis dump or serialized native record enters evidence.
        if kind == "string":
            values = [db.get(key)]
        elif kind == "list":
            values = db.lrange(key, 0, -1)
        elif kind == "set":
            values = sorted(db.smembers(key))
        elif kind == "hash":
            values = [k + b"=" + v for k, v in sorted(db.hgetall(key).items())]
        else:
            raise ValueError("unexpected native Redis record type")
        result[key.decode()] = {"type": kind, "count": len(values),
                                "sha256": hashlib.sha256(b"".join(
                                    len(v).to_bytes(8, "big") + v for v in values)).hexdigest()}
    return result


def node(trader, *, producer=False, flush_on_start=False):
    if flush_on_start:
        raise ValueError("startup flush forbidden")
    namespace(trader)
    from nautilus_trader.adapters.sandbox.config import SandboxExecutionClientConfig
    from nautilus_trader.adapters.sandbox.factory import SandboxLiveExecClientFactory
    from nautilus_trader.common import Environment
    from nautilus_trader.config import (CacheConfig, DatabaseConfig, LiveExecEngineConfig,
                                       LoggingConfig, TradingNodeConfig)
    from nautilus_trader.live.node import TradingNode

    config = TradingNodeConfig(environment=Environment.SANDBOX, trader_id=trader,
        cache=CacheConfig(database=DatabaseConfig(type="redis", host="127.0.0.1", port=PORT,
            connection_timeout=2, response_timeout=2, number_of_retries=1),
            encoding="json", flush_on_start=False, use_instance_id=False,
            persist_account_events=True, buffer_interval_ms=None),
        exec_engine=LiveExecEngineConfig(load_cache=True, reconciliation=False,
                                        inflight_check_interval_ms=0),
        logging=LoggingConfig(log_level="ERROR"),
        exec_clients={"N2PROOF": SandboxExecutionClientConfig(venue="N2PROOF",
            starting_balances=["10000 USDT"], base_currency="USDT", default_leverage=D(1))}
            if producer else {})
    instance = TradingNode(config=config, loop=asyncio.get_running_loop())
    if producer:
        instance.add_exec_client_factory("N2PROOF", SandboxLiveExecClientFactory)
        instance.build()
    return instance


def observation(cache):
    def event(e):
        return type(e).to_dict(e)
    return {"instruments": sorted(str(i.id) for i in cache.instruments()),
            "accounts": {str(a.id): [event(e) for e in a.events] for a in cache.accounts()},
            "orders": {str(o.client_order_id): {"state": o.status.name,
                        "events": [event(e) for e in o.events]} for o in cache.orders()},
            "positions": {str(p.id): {"state": type(p).to_dict(p),
                        "events": [event(e) for e in p.events]} for p in cache.positions()}}


def history_observation(instance):
    from nautilus_trader.model.identifiers import InstrumentId

    instrument = InstrumentId.from_str(fixture.INSTRUMENT)
    realized = instance.kernel.portfolio.realized_pnl(instrument)
    unrealized = instance.kernel.portfolio.unrealized_pnl(instrument)
    return {"position_snapshots": [type(p).to_dict(p) for p in instance.kernel.cache.position_snapshots()],
            "portfolio_realized_net": str(realized.as_decimal()) if realized is not None else None,
            "portfolio_unrealized": str(unrealized.as_decimal()) if unrealized is not None else None}


def validate_state(state, trader, scenario):
    """Validate actual native objects before comparing them with the checkpoint."""
    namespace(trader)
    if scenario not in SCENARIOS or state["instruments"] != [fixture.INSTRUMENT]:
        raise ValueError("missing instrument/scenario binding")
    if set(state["accounts"]) != {"N2PROOF-001"} or not state["orders"] or not state["positions"]:
        raise ValueError("missing account/order/position binding")
    fills, event_ids = [], set()
    for order_id, order in state["orders"].items():
        if order["state"] not in ("FILLED", "CANCELED"):
            raise ValueError("inconsistent order state")
        for e in order["events"]:
            if (e["trader_id"] != trader or e["instrument_id"] != fixture.INSTRUMENT
                or e["client_order_id"] != order_id or e["event_id"] in event_ids):
                raise ValueError("duplicate/unbound native order event")
            event_ids.add(e["event_id"])
            if e["type"] == "OrderFilled":
                if e["account_id"] != "N2PROOF-001" or e["currency"] != "USDT":
                    raise ValueError("fill binding/currency")
                if fixture._money(e["commission"]) != fixture._decimal(e["last_qty"]) * fixture._decimal(e["last_px"]) * D(".0004"):
                    raise ValueError("fee mismatch")
                fills.append(e)
    if len({e["trade_id"] for e in fills}) != len(fills):
        raise ValueError("duplicate economic fill")
    if len(fills) != {"round_trip": 2, "reversal": 3}[scenario]:
        raise ValueError("missing economic fill")
    fee = sum((fixture._money(e["commission"]) for e in fills), D(0))
    expected = {"round_trip": (D("10009.916"), D(".084")),
                "reversal": (D("10029.836"), D(".164"))}[scenario]
    account_events = state["accounts"]["N2PROOF-001"]
    if not account_events:
        raise ValueError("missing account event")
    for e in account_events:
        if e["account_id"] != "N2PROOF-001" or e["base_currency"] != "USDT":
            raise ValueError("account binding")
        for b in e["balances"]:
            if b["currency"] != "USDT" or fixture._decimal(b["total"]) != fixture._decimal(b["free"]) + fixture._decimal(b["locked"]):
                raise ValueError("inconsistent/nonfinite balance")
        for m in e["margins"]:
            if m["currency"] != "USDT" or m["instrument_id"] != fixture.INSTRUMENT:
                raise ValueError("margin binding")
            fixture._decimal(m["initial"])
            fixture._decimal(m["maintenance"])
    balance = fixture._decimal(account_events[-1]["balances"][0]["total"])
    if (balance, fee) != expected:
        raise ValueError("economic conservation mismatch")
    for position_id, position in state["positions"].items():
        p = position["state"]
        if (p["position_id"] != position_id or p["account_id"] != "N2PROOF-001"
            or p["instrument_id"] != fixture.INSTRUMENT or p["trader_id"] != trader
            or p["opening_order_id"] not in state["orders"]
            or p["closing_order_id"] not in state["orders"] or p["settlement_currency"] != "USDT"
            or D(str(p["signed_qty"])) != 0):
            raise ValueError("position binding/state")
    return {"balance": str(balance), "equity": str(balance), "fees": str(fee),
            "quantity": "0", "fills": len(fills), "orders": len(state["orders"]),
            "statuses": dict(Counter(o["state"] for o in state["orders"].values()))}


def no_resume():
    raise ValueError(STATUS)


def write_json(path, value):
    # Exclusive, closed and fsynced before the controller can observe completion.
    with Path(path).open("xb") as handle:
        handle.write(fixture._bytes(value))
        handle.flush()
        os.fsync(handle.fileno())


async def produce(root, trader, scenario, hold=False):
    if scenario not in SCENARIOS:
        raise ValueError("unsupported closed scenario")
    provenance = environment()
    root = fixture._scratch(root)
    db, identity = backend()
    if records(db, trader):
        raise ValueError("producer namespace is not empty")
    instance = node(trader, producer=True)
    cache, engine = instance.kernel.cache, instance.kernel.exec_engine
    from nautilus_trader.common.factories import OrderFactory
    from nautilus_trader.core.uuid import UUID4
    from nautilus_trader.execution.messages import SubmitOrder, CancelOrder
    from nautilus_trader.model.currencies import BTC, USDT
    from nautilus_trader.model.data import QuoteTick
    from nautilus_trader.model.enums import OrderSide
    from nautilus_trader.model.identifiers import InstrumentId, Symbol, StrategyId
    from nautilus_trader.model.instruments import CryptoPerpetual
    from nautilus_trader.model.objects import Price, Quantity
    instrument = CryptoPerpetual(instrument_id=InstrumentId.from_str(fixture.INSTRUMENT),
        raw_symbol=Symbol("BTCUSDT"), base_currency=BTC, quote_currency=USDT,
        settlement_currency=USDT, is_inverse=False, price_precision=2,
        price_increment=Price.from_str(".01"), size_precision=3,
        size_increment=Quantity.from_str(".001"), max_quantity=Quantity.from_str("2.000"),
        min_quantity=Quantity.from_str(".001"), max_notional=None, min_notional=None,
        max_price=Price.from_str("1000.00"), min_price=Price.from_str(".01"),
        margin_init=D(1), margin_maint=D(".05"), maker_fee=D(".0004"), taker_fee=D(".0004"),
        ts_event=0, ts_init=0)
    cache.add_instrument(instrument)
    client = engine._clients[next(iter(engine._clients))]
    strategy = StrategyId("PROOF-001")
    factory = OrderFactory(instance.trader_id, strategy, client.test_clock)
    publications = []
    for topic in ("events.order.*", "events.position.*", "events.account.*"):
        instance.kernel.msgbus.subscribe(topic, lambda e: publications.append(type(e).to_dict(e)))
    engine.start()
    client.connect()

    async def settle(predicate):
        for _ in range(300):
            await asyncio.sleep(.01)
            if predicate() and engine.cmd_qsize() == 0 and engine.evt_qsize() == 0:
                return
        raise RuntimeError("native execution did not settle")

    await settle(lambda: bool(cache.accounts()))
    for step, (target, mark) in enumerate(fixture.SCENARIOS[scenario]):
        client.test_clock.set_time(fixture.START + step * 1_000_000_000)
        price = Price.from_str(mark)
        tick = QuoteTick(instrument.id, price, price, Quantity.from_str("100.000"),
                         Quantity.from_str("100.000"), client.test_clock.timestamp_ns(), client.test_clock.timestamp_ns())
        cache.add_quote_tick(tick)
        instance.kernel.portfolio.update_quote_tick(tick)
        client.on_data(tick)
        current = sum((D(str(p.signed_qty)) for p in cache.positions_open()), D(0))
        delta = D(target) - current
        if delta:
            order = factory.market(instrument.id, OrderSide.BUY if delta > 0 else OrderSide.SELL,
                                   Quantity.from_str(f"{abs(delta):.3f}"))
            engine.execute(SubmitOrder(instance.trader_id, strategy, order, UUID4(), client.test_clock.timestamp_ns()))
            await settle(lambda: order.is_closed)
    order = factory.limit(instrument.id, OrderSide.BUY, Quantity.from_str("1.000"), Price.from_str("50.00"))
    engine.execute(SubmitOrder(instance.trader_id, strategy, order, UUID4(), client.test_clock.timestamp_ns()))
    await settle(lambda: order.status.name == "ACCEPTED")
    engine.execute(CancelOrder(instance.trader_id, strategy, instrument.id, order.client_order_id,
                              order.venue_order_id, UUID4(), client.test_clock.timestamp_ns()))
    await settle(lambda: order.status.name == "CANCELED")
    state = observation(cache)
    economics = validate_state(state, trader, scenario)
    history = history_observation(instance)
    if not cache.check_integrity():
        raise ValueError("native cache integrity failed")
    # AOF-always server read-back, not an assumed native queue drain or destructive flush().
    for _ in range(300):
        raw = records(db, trader)
        lists = {key: db.lrange(key, 0, -1) for key, value in raw.items() if value["type"] == "list"}
        persisted = [json.loads(v) for values in lists.values() for v in values]
        ids = {e.get("id") or e.get("event_id") for e in persisted}
        expected = {e["event_id"] for o in state["orders"].values() for e in o["events"]}
        expected.update(e["event_id"] for events in state["accounts"].values() for e in events)
        required_keys = ["accounts:N2PROOF-001", "instruments:" + fixture.INSTRUMENT]
        required_keys.extend("orders:" + k for k in state["orders"])
        required_keys.extend("positions:" + k for k in state["positions"])
        if expected <= ids and all(namespace(trader) + k in raw for k in required_keys):
            await asyncio.sleep(.05)
            if records(db, trader) == raw:
                break
        await asyncio.sleep(.01)
    else:
        raise ValueError("native Redis durable record acknowledgement absent")
    persistence = db.info("persistence")
    if persistence["aof_last_write_status"] != "ok" or persistence["aof_pending_bio_fsync"]:
        raise ValueError("AOF durability not acknowledged")
    manifest = {"source": SOURCE, **fixture.LABELS, "trader": trader, "scenario": scenario,
        "backend": identity, "environment": provenance, "pid": os.getpid(),
        "instance_id": str(instance.instance_id), "time_ns": time.time_ns(),
        "checkpoint": "native event IDs read back from Redis; AOF appendfsync always; no in-flight claim",
        "state": state, "native_history": history, "economics": economics, "records": raw, "publications": publications,
        "output": str(root), "aof_status": persistence["aof_last_write_status"]}
    write_json(root / "manifest.json", manifest)
    digest = hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest()
    write_json(root / "checkpoint.json", {"pid": os.getpid(), "sha256": digest, "time_ns": time.time_ns()})
    if hold:
        # Controller kills this exact Popen handle after independently checking its checkpoint.
        await asyncio.Event().wait()
    client.disconnect()
    engine.stop()
    await asyncio.sleep(.05)
    cache.dispose()
    return {"pid": os.getpid(), "sha256": digest, "economics": economics}


async def restore(root, digest, trader):
    data = (Path(root) / "manifest.json").read_bytes()
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError("divergent manifest digest")
    manifest = json.loads(data)
    if (manifest["source"] != SOURCE or manifest["trader"] != trader
        or manifest["scenario"] not in SCENARIOS or manifest["pid"] == os.getpid()
        or not 0 <= time.time_ns() - manifest["time_ns"] < 3_600_000_000_000
        or any(manifest.get(k) is not v for k, v in fixture.LABELS.items())):
        raise ValueError("expired/wrong-source/checkpoint binding")
    provenance = environment()
    if provenance != manifest["environment"]:
        raise ValueError("source/binary drift")
    db, identity = backend()
    before = records(db, trader)
    if identity != manifest["backend"] or not before or before != manifest["records"]:
        raise ValueError("missing/corrupt native records/backend binding")
    instance = node(trader)
    cache = instance.kernel.cache
    engine = instance.kernel.exec_engine
    if engine.registered_clients or engine.command_count or engine.event_count:
        raise ValueError("restart has execution clients")
    state = observation(cache)
    economics = validate_state(state, trader, manifest["scenario"])
    if state != manifest["state"] or not cache.check_integrity():
        raise ValueError("native reconstruction differs from durable checkpoint")
    history = history_observation(instance)
    history_equal = history == manifest["native_history"]
    try:
        no_resume()
    except ValueError as exc:
        refusal = str(exc)
    if records(db, trader) != before:
        raise ValueError("read-only restart mutated native state")
    cache.dispose()
    return {"pid": os.getpid(), "instance_id": str(instance.instance_id),
            "status": refusal, "new_orders": 0, "new_fills": 0,
            "execution_clients": 0, "state_sha256": fixture._hash(state),
            "native_command_count": engine.command_count, "native_event_count": engine.event_count,
            "native_history": history, "history_equal": history_equal,
            "proof_status": "NATIVE_DURABILITY_PROVEN" if history_equal else "PARTIAL_NATIVE_HISTORY_LOSS",
            "economics": economics, "records_sha256": fixture._hash(before),
            "manifest_sha256": digest, "native_load": "TradingNode kernel exec_engine.load_cache=True",
            "time_ns": time.time_ns()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("produce", "hold", "restore"))
    parser.add_argument("root")
    parser.add_argument("trader")
    parser.add_argument("binding", help="closed scenario or trusted manifest SHA256")
    args = parser.parse_args()
    if args.action == "restore":
        result = asyncio.run(restore(args.root, args.binding, args.trader))
    else:
        result = asyncio.run(produce(args.root, args.trader, args.binding, args.action == "hold"))
    print(json.dumps(result, sort_keys=True))
    if result.get("proof_status") == "PARTIAL_NATIVE_HISTORY_LOSS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
