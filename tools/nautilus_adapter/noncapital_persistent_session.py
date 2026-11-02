"""Explicit local N4-02 native persistence proof; never a trading recovery client."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import time
import uuid
from decimal import Decimal as D
from pathlib import Path

from tools.nautilus_adapter import native_cache_restart as native
from tools.nautilus_adapter import noncapital_integrated_session as public

SOURCE = "cpw_n4_02_native_1.231.0_v1"
OWNER_KEY = "cpw:n4-02:owner"
LABELS = {"proof_only": True, "non_authoritative": True, "never_live_or_capital": True}
AUTHORITY = "RECONCILIATION_REQUIRED / NO_NEW_ORDERS / NO_RESUME / NOT_PAPER_OR_LIVE_READY"
require = public.require
encoded = public.n2._bytes
digest = public.n2._hash


def sources():
    return {p.name: public.file_hash(p) for p in
            (Path(__file__), Path(__file__).with_name("noncapital_persistent_proof.py"), Path(native.__file__), Path(public.__file__),
             Path(public.n2.__file__), Path(public.n3.__file__))}


def process_identity():
    return {"pid": os.getpid(), "pid_namespace": os.readlink("/proc/self/ns/pid")}


def output_root(path, *, empty=False):
    path = Path(path)
    root = path.resolve()
    require(path.is_dir() and not path.is_symlink() and not path.is_junction()
            and root.is_relative_to(Path("/tmp")) and root != Path("/tmp")
            and not root.is_relative_to(public.n3.ROOT), "ordinary external /tmp output required")
    if empty:
        require(not any(root.iterdir()), "output must be empty")
    return root


def backend():
    import redis
    require(redis.__version__ == "8.1.0", "wrong Redis client pin")
    db = redis.Redis(host="127.0.0.1", port=6379, socket_timeout=3, socket_connect_timeout=3)
    server = db.info("server")
    require(server["redis_version"] == "7.4.2", "wrong Redis server pin")
    require(db.config_get("appendonly") == {"appendonly": "yes"}
            and db.config_get("appendfsync") == {"appendfsync": "always"}, "AOF always required")
    owner = json.loads(db.get(OWNER_KEY) or b"{}")
    require(owner.get("source") == SOURCE and owner.get("redis_run_id") == server["run_id"]
            and re.fullmatch(r"cpw-n4-02-[0-9a-f]{12}", owner.get("controller", ""))
            and all(owner.get(k) is v for k, v in LABELS.items()), "unowned proof backend")
    return db, {"run_id": server["run_id"], "redis_version": server["redis_version"], "owner": owner}


def node(trader, *, producer=False):
    native.namespace(trader)
    from nautilus_trader.adapters.sandbox.config import SandboxExecutionClientConfig
    from nautilus_trader.adapters.sandbox.factory import SandboxLiveExecClientFactory
    from nautilus_trader.common import Environment
    from nautilus_trader.config import (
        CacheConfig,
        DatabaseConfig,
        LiveExecEngineConfig,
        LoggingConfig,
        TradingNodeConfig,
    )
    from nautilus_trader.live.node import TradingNode

    instance = TradingNode(config=TradingNodeConfig(environment=Environment.SANDBOX, trader_id=trader,
        cache=CacheConfig(database=DatabaseConfig(type="redis", host="127.0.0.1", port=6379,
            connection_timeout=2, response_timeout=2, number_of_retries=1), encoding="json",
            persist_account_events=True, buffer_interval_ms=None, use_instance_id=False, flush_on_start=False),
        exec_engine=LiveExecEngineConfig(load_cache=True, reconciliation=False, inflight_check_interval_ms=0),
        logging=LoggingConfig(log_level="ERROR"),
        exec_clients={"N4SIM": SandboxExecutionClientConfig(venue="N4SIM", starting_balances=["10000 USDT"],
            base_currency="USDT", default_leverage=D(1))} if producer else {}), loop=asyncio.get_running_loop())
    if producer:
        instance.add_exec_client_factory("N4SIM", SandboxLiveExecClientFactory)
        instance.build()
    return instance


def projection(instance):
    from nautilus_trader.model.currencies import USDT
    from nautilus_trader.model.identifiers import InstrumentId
    cache, portfolio = instance.kernel.cache, instance.kernel.portfolio
    iid = InstrumentId.from_str(public.LOCAL_ID)
    realized, unrealized = portfolio.realized_pnl(iid), portfolio.unrealized_pnl(iid)
    balance = cache.accounts()[0].balance_total(USDT).as_decimal()
    upnl = unrealized.as_decimal() if unrealized is not None else None
    return {"native": native.observation(cache),
            "snapshots": [type(p).to_dict(p) for p in cache.position_snapshots()],
            "realized": str(realized.as_decimal()) if realized is not None else None,
            "unrealized": str(upnl) if upnl is not None else None,
            "balance": str(balance), "equity": str(balance + upnl) if upnl is not None else None}


def validate(state, trader, case, quotes):
    """Independent equality assertions; these never write native economic state."""
    native.namespace(trader)
    require(case in ("open", "flat"), "MULTICYCLE_NATIVE_HISTORY_UNSUPPORTED_PINNED")
    s = state["native"]
    require(s["instruments"] == [public.LOCAL_ID] and set(s["accounts"]) == {"N4SIM-001"}, "native namespace")
    count = 1 if case == "open" else 2
    require(len(s["orders"]) == count and len(s["positions"]) == 1 and len(quotes) == count,
            "unexpected exposure/order count")
    event_ids, trades, fills = set(), set(), []
    for oid, order in s["orders"].items():
        require(order["state"] == "FILLED", "partial/pending order")
        for e in order["events"]:
            require(e["event_id"] not in event_ids and e["trader_id"] == trader
                    and e["client_order_id"] == oid and e["instrument_id"] == public.LOCAL_ID,
                    "duplicate/unbound native order event")
            event_ids.add(e["event_id"])
            if e["type"] == "OrderFilled":
                require(e["trade_id"] not in trades and e["account_id"] == "N4SIM-001"
                        and e["currency"] == "USDT" and D(e["last_qty"]) == public.QTY, "duplicate/unbound fill")
                trades.add(e["trade_id"])
                fills.append(e)
    fills.sort(key=lambda e: e["ts_event"])
    require(len(fills) == count and len({e["venue_order_id"] for e in fills}) == count, "fill/order identity count")
    fees = D(0)
    for i, (fill, quote) in enumerate(zip(fills, quotes)):
        side = "BUY" if i == 0 else "SELL"
        require(fill["order_side"] == side and D(fill["last_px"]) == D(quote["ask" if i == 0 else "bid"]),
                "native execution quote/side mismatch")
        fee = public.n2._money(fill["commission"])
        require(fee == public.QTY * D(fill["last_px"]) * public.FEE, "native fee mismatch")
        fees += fee
    gross = D(0) if count == 1 else public.QTY * (D(fills[1]["last_px"]) - D(fills[0]["last_px"]))
    expected_upnl = public.QTY * (D(quotes[-1]["bid"]) - D(fills[0]["last_px"])) if count == 1 else D(0)
    require(D(state["balance"]) == D(10000) + gross - fees
            and state["realized"] is not None and D(state["realized"]) == gross - fees
            and state["unrealized"] is not None and D(state["unrealized"]) == expected_upnl
            and D(state["equity"]) == D(state["balance"]) + expected_upnl, "native economic mismatch")
    for pid, position in s["positions"].items():
        p = position["state"]
        require(p["position_id"] == pid and p["trader_id"] == trader and p["account_id"] == "N4SIM-001"
                and p["instrument_id"] == public.LOCAL_ID and p["settlement_currency"] == "USDT"
                and D(str(p["signed_qty"])) == (public.QTY if case == "open" else 0), "native position mismatch")
        require(p["opening_order_id"] == fills[0]["client_order_id"]
                and p["closing_order_id"] == (None if case == "open" else fills[-1]["client_order_id"])
                and [e["event_id"] for e in position["events"]] == [e["event_id"] for e in fills]
                and sum((public.n2._money(c) for c in p["commissions"]), D(0)) == fees
                and public.n2._money(p["realized_pnl"]) == gross - fees
                and abs(D(str(p["avg_px_open"])) - D(fills[0]["last_px"])) <= public.MONEY,
                "native cost/position/fill linkage mismatch")
    require(not state["snapshots"], "MULTICYCLE_NATIVE_HISTORY_UNSUPPORTED_PINNED")
    for events in s["accounts"].values():
        for e in events:
            require(e["account_id"] == "N4SIM-001" and e["base_currency"] == "USDT", "account identity")
            for b in e["balances"]:
                require(b["currency"] == "USDT" and D(b["total"]) == D(b["free"]) + D(b["locked"]), "balance conservation")
        for margin in events[-1]["margins"]:
            require(margin["currency"] == "USDT" and margin["instrument_id"] == public.LOCAL_ID
                    and D(margin["initial"]) == 0
                    and D(margin["maintenance"]) == (public.QTY * D(fills[0]["last_px"]) if case == "open" else 0),
                    "fixed one-times fixture margin mismatch")
    return {"fees": str(fees), "gross_realized": str(gross), "fills": count}


async def settle(engine, predicate):
    for _ in range(500):
        await asyncio.sleep(.01)
        if predicate() and not engine.cmd_qsize() and not engine.evt_qsize():
            return
    raise ValueError("native queues/fill did not settle")


async def fresh_quote(feed):
    # Native node construction can block callbacks; await a usable quote before the latch.
    await public.n3.wait_until(lambda: feed.tick is not None
        and 0 <= time.time_ns() - feed.tick.ts_event <= 5_000_000_000
        and feed.tick.ts_event - 1_000_000_000 <= feed.tick.ts_init <= time.time_ns() + 1_000_000_000,
        15, feed)


async def produce(root, trader, case, *, hold=False, before_ack=False):
    from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
    from nautilus_trader.adapters.binance.config import (
        BinanceDataClientConfig,
        BinanceInstrumentProviderConfig,
    )
    from nautilus_trader.adapters.binance.futures.data import BinanceFuturesDataClient
    from nautilus_trader.adapters.binance.futures.providers import BinanceFuturesInstrumentProvider
    from nautilus_trader.cache.cache import Cache
    from nautilus_trader.common.component import LiveClock, MessageBus
    from nautilus_trader.common.factories import OrderFactory
    from nautilus_trader.core.uuid import UUID4
    from nautilus_trader.data.messages import SubscribeMarkPrices, SubscribeQuoteTicks
    from nautilus_trader.execution.messages import SubmitOrder
    from nautilus_trader.model.data import QuoteTick
    from nautilus_trader.model.enums import OrderSide
    from nautilus_trader.model.identifiers import InstrumentId, StrategyId, TraderId
    from nautilus_trader.model.instruments import CryptoPerpetual
    from nautilus_trader.model.objects import Quantity

    root = output_root(root, empty=True)
    environment = native.environment()
    db, identity = backend()
    require(not native.records(db, trader), "nonempty native namespace")
    clock = LiveClock()
    iid = InstrumentId.from_str(public.n3.NATIVE_ID)
    config = BinanceInstrumentProviderConfig(load_ids=frozenset({iid}))
    requests, lifecycle, quotes, publications = [], [], [], []
    provider = BinanceFuturesInstrumentProvider(public.public_http(clock, requests), clock, config=config)
    bus = MessageBus(TraderId("N4DATA-001"), clock)
    feed = public.Feed()
    bus.register("DataEngine.process", feed.receive)
    data = BinanceFuturesDataClient(asyncio.get_running_loop(), provider._client, bus, Cache(), clock,
        provider, public.n3.MARK_WS, BinanceDataClientConfig(account_type=BinanceAccountType.USDT_FUTURES,
        instrument_provider=config, update_instruments_interval_mins=None), base_url_ws_public=public.n3.QUOTE_WS)
    instance = None
    try:
        with public.n3.native_lifecycle(data, feed, lifecycle):
            await asyncio.wait_for(data._connect(), 30)
            source = CryptoPerpetual.to_dict(provider.find(iid))
            before = public.n3.instrument_projection(provider.find(iid))
            command = (iid, None, iid.venue, UUID4(), clock.timestamp_ns())
            await data._subscribe_quote_ticks(SubscribeQuoteTicks(*command))
            await data._subscribe_mark_prices(SubscribeMarkPrices(*command))
            await public.n3.wait_until(feed.fresh, 15, feed)
            instance = node(trader, producer=True)
            cache, engine = instance.kernel.cache, instance.kernel.exec_engine
            instrument = CryptoPerpetual.from_dict(public.local_spec(source))
            cache.add_instrument(instrument)
            client = next(iter(engine._clients.values()))
            strategy = StrategyId("PROOF-001")
            factory = OrderFactory(instance.trader_id, strategy, client.test_clock)
            for topic in ("events.order.*", "events.position.*", "events.account.*"):
                instance.kernel.msgbus.subscribe(topic, lambda e: publications.append(type(e).to_dict(e)))
            engine.start()
            client.connect()
            await settle(engine, lambda: bool(cache.accounts()))
            for step in range(1 if case == "open" else 2):
                if step:
                    previous = quotes[-1]["ts_event"]
                    await public.n3.wait_until(lambda previous=previous: feed.latest.get("quote", {}).get("ts_event", 0) > previous, 5, feed)
                await fresh_quote(feed)
                clients = data._ws_public_client._clients
                q = feed.gate(source, bool(clients) and not lifecycle and all(c.is_active() for c in clients.values()))
                quotes.append({**q, "observed_ns": time.time_ns()})
                tick = feed.tick
                local = QuoteTick(instrument.id, tick.bid_price, tick.ask_price, tick.bid_size, tick.ask_size, tick.ts_event, tick.ts_init)
                client.test_clock.set_time(tick.ts_init)
                cache.add_quote_tick(local)
                instance.kernel.portfolio.update_quote_tick(local)
                client.on_data(local)
                order = factory.market(instrument.id, OrderSide.BUY if step == 0 else OrderSide.SELL, Quantity.from_str("0.001"))
                engine.execute(SubmitOrder(instance.trader_id, strategy, order, UUID4(), tick.ts_init))
                await settle(engine, lambda order=order: order.is_closed)
            state = projection(instance)
            economics = validate(state, trader, case, quotes)
            mark, mark_observed_ns = dict(feed.latest["mark"]), time.time_ns()
            require(cache.check_integrity(), "native cache integrity")
            if before_ack:
                native.write_json(root / "unacknowledged.json", {**LABELS, "pid": os.getpid(), "native": state})
                await asyncio.Event().wait()
            after = BinanceFuturesInstrumentProvider(public.public_http(clock, requests), clock, config=config)
            await asyncio.wait_for(after.load_ids_async([iid]), 25)
            public.n3.unchanged_filters(before, public.n3.instrument_projection(after.find(iid)))
            require(CryptoPerpetual.to_dict(after.find(iid))["info"]["filters"] == source["info"]["filters"], "public filter drift")
            events = [e for o in state["native"]["orders"].values() for e in o["events"]]
            events += [e for a in state["native"]["accounts"].values() for e in a]
            expected_ids = {e["event_id"] for e in events}
            for _ in range(500):
                records = native.records(db, trader)
                persisted = [json.loads(v) for k, vinfo in records.items() if vinfo["type"] == "list" for v in db.lrange(k, 0, -1)]
                ids = {e.get("id") or e.get("event_id") for e in persisted}
                position_keys = [native.namespace(trader) + "positions:" + p for p in state["native"]["positions"]]
                if expected_ids <= ids and all(k in records for k in position_keys):
                    await asyncio.sleep(.05)
                    if records == native.records(db, trader):
                        break
                await asyncio.sleep(.01)
            else:
                raise ValueError("native durable read-back absent")
            aof = db.info("persistence")
            require(aof["aof_last_write_status"] == "ok" and not aof["aof_pending_bio_fsync"], "AOF unacknowledged")
            chain = []
            for payload in [source, *quotes, *publications, state, records]:
                row = {"seq": len(chain), "previous": chain[-1]["sha256"] if chain else None, "payload": payload}
                chain.append({**row, "sha256": digest(row)})
            manifest = {**LABELS, "source": SOURCE, "authority": AUTHORITY, "trader": trader, "case": case,
                "run_id": str(uuid.uuid4()), "instance_id": str(instance.instance_id), "pid": os.getpid(),
                "process": process_identity(),
                "time_ns": time.time_ns(), "environment": environment, "sources": sources(), "backend": identity,
                "instrument": source, "quotes": quotes, "mark": mark, "mark_observed_ns": mark_observed_ns,
                "filter_sha256": digest(source["info"]["filters"]), "requests": requests,
                "state": state, "economics": economics, "records": records, "chain": chain,
                "aof": {k: aof[k] for k in ("aof_enabled", "aof_last_write_status", "aof_pending_bio_fsync")}}
            native.write_json(root / "manifest.json", manifest)
            trusted = public.file_hash(root / "manifest.json")
            native.write_json(root / "ack.json", {**LABELS, "pid": os.getpid(), "sha256": trusted, "run_id": manifest["run_id"]})
            if hold:
                await asyncio.Event().wait()
            return {**LABELS, "pid": os.getpid(), "sha256": trusted, "case": case, "economics": economics}
    finally:
        await asyncio.wait_for(data._disconnect(), 5)
        if instance:
            client.disconnect()
            engine.stop()
            await asyncio.sleep(.05)
            instance.kernel.cache.dispose()


def checkpoint(root, trusted):
    root = output_root(root)
    raw = (root / "manifest.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == trusted, "untrusted manifest")
    m = json.loads(raw)
    ack = json.loads((root / "ack.json").read_bytes())
    require(ack == {**LABELS, "pid": m["pid"], "sha256": trusted, "run_id": m["run_id"]}, "missing/torn acknowledgement")
    require(m["source"] == SOURCE and m["authority"] == AUTHORITY and all(m.get(k) is v for k, v in LABELS.items()), "source/authority mismatch")
    require(0 <= time.time_ns() - m["time_ns"] < 3_600_000_000_000, "expired checkpoint")
    require(m["pid"] == m["process"]["pid"] and m["process"] != process_identity(), "nonfresh process")
    native.namespace(m["trader"])
    require(m["sources"] == sources() and m["environment"] == native.environment(), "source/version drift")
    for i, row in enumerate(m["chain"]):
        require(row["seq"] == i and row["previous"] == (m["chain"][i-1]["sha256"] if i else None)
                and row["sha256"] == digest({k: v for k, v in row.items() if k != "sha256"}), "broken witness chain")
    require([r["payload"] for r in m["chain"]][-2:] == [m["state"], m["records"]], "unbound native checkpoint")
    require([r["payload"] for r in m["chain"]][:1 + len(m["quotes"])] == [m["instrument"], *m["quotes"]], "unbound quote/instrument context")
    public.local_spec(m["instrument"])
    require(m["filter_sha256"] == digest(m["instrument"]["info"]["filters"]), "filter identity mismatch")
    mark = m["mark"]
    require(mark["source_hash"] == public.n3.digest({k: v for k, v in mark.items() if k not in ("source_hash", "ts_init")})
            and mark["kind"] == "mark" and mark["instrument_id"] == public.n3.NATIVE_ID
            and mark["native_type"] == "nautilus_trader.adapters.binance.futures.types.BinanceFuturesMarkPriceUpdate"
            and 0 <= m["mark_observed_ns"] - mark["ts_event"] <= 10_000_000_000
            and m["mark_observed_ns"] < mark["next_funding_ns"], "untrusted/stale mark context")
    public.n3.positive(mark["mark"])
    public.n3.positive(mark["index"])
    require(D(mark["funding_rate"]).is_finite(), "nonfinite observed funding context")
    require(all(a["ts_event"] < b["ts_event"] for a, b in zip(m["quotes"], m["quotes"][1:])), "conflicting/out-of-order quote")
    for q in m["quotes"]:
        public.validate_quote({k: v for k, v in q.items() if k != "observed_ns"}, m["instrument"], q["observed_ns"])
    validate(m["state"], m["trader"], m["case"], m["quotes"])
    return m


async def restore(root, trusted):
    from nautilus_trader.model.data import QuoteTick
    from nautilus_trader.model.identifiers import InstrumentId
    from nautilus_trader.model.objects import Price, Quantity
    m = checkpoint(root, trusted)
    db, identity = backend()
    before = native.records(db, m["trader"])
    require(identity == m["backend"] and before == m["records"], "native source/backend mismatch")
    flags = db.acl_getuser("default")
    require(set(flags["categories"]) == {"-@all", "+@read"} and not flags["selectors"]
            and set(flags["commands"]) == {"+ping", "+info", "+config|get", "+acl|getuser",
                                          "+client|setinfo", "+client|setname"}, "read-only backend permission required")
    instance = node(m["trader"])
    cache, engine = instance.kernel.cache, instance.kernel.exec_engine
    try:
        require(str(instance.instance_id) != m["instance_id"] and not engine.registered_clients
                and engine.command_count == engine.event_count == 0, "recovery execution authority")
        require(native.observation(cache) == m["state"]["native"], "native reconstruction differs")
        q = m["quotes"][-1]
        # Only original producer quote context enters the disposable in-memory native cache.
        tick = QuoteTick(InstrumentId.from_str(public.LOCAL_ID), Price.from_str(q["bid"]), Price.from_str(q["ask"]),
            Quantity.from_str(q["bid_size"]), Quantity.from_str(q["ask_size"]), q["ts_event"], q["ts_init"])
        cache.add_quote_tick(tick)
        instance.kernel.portfolio.update_quote_tick(tick)
        state = projection(instance)
        validate(state, m["trader"], m["case"], m["quotes"])
        require(state == m["state"] and cache.check_integrity(), "native economic/history reconstruction differs")
        require(native.records(db, m["trader"]) == before and not engine.registered_clients
                and engine.command_count == engine.event_count == 0, "recovery mutated state")
        return {**LABELS, "status": "N4_02_NATIVE_SINGLE_EXPOSURE_RECOVERY_PROVEN" if m["case"] == "open" else "N4_02_NATIVE_CLOSED_CYCLE_RECOVERY_PROVEN",
            "authority": AUTHORITY, "pid": os.getpid(), "process": process_identity(), "instance_id": str(instance.instance_id), "native": state,
            "projection_sha256": digest(state), "records_sha256": digest(before), "manifest_sha256": trusted,
            "new_orders": 0, "new_fills": 0, "execution_clients": 0, "native_commands": 0, "native_events": 0}
    finally:
        cache.dispose()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("produce", "restore"))
    parser.add_argument("--proof-only", required=True, action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--case", choices=("open", "flat"))
    parser.add_argument("--trader")
    parser.add_argument("--expected-manifest-sha256")
    parser.add_argument("--hold", action="store_true")
    parser.add_argument("--before-ack", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "restore":
            require(args.expected_manifest_sha256 and not any((args.case, args.trader, args.hold, args.before_ack)), "restore cannot submit/resume")
            result = asyncio.run(restore(args.output, args.expected_manifest_sha256))
        else:
            require(args.case and args.trader and not args.expected_manifest_sha256, "closed producer parameters required")
            async def bounded():
                async with asyncio.timeout(120):
                    return await produce(args.output, args.trader, args.case, hold=args.hold, before_ack=args.before_ack)
            result = asyncio.run(bounded())
        print(json.dumps(result, sort_keys=True))
        return 0
    except Exception as exc:  # noqa: BLE001 - Every CLI failure must refuse without activation.
        print(json.dumps({**LABELS, "status": "BLOCKED", "authority": AUTHORITY, "pid": os.getpid(), "error": f"{type(exc).__name__}: {exc}"}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
