"""Manual N4-01 public-to-native-sandbox proof; no trading or restart authority."""
from __future__ import annotations

import argparse
import asyncio
from decimal import Decimal as D
import hashlib
import json
import os
from pathlib import Path
import platform
import time
import uuid

from tools.nautilus_adapter import paper_sandbox as n2
from tools.nautilus_adapter import binance_usdm_public_probe as n3

SOURCE = "cpw_n4_01_noncapital_1.231.0_v1"
LOCAL_ID = "BTCUSDT-PERP.N4SIM"
AUTHORITY = "RECONCILIATION_REQUIRED / " + n3.NO_AUTHORITY
QTY = D("0.001")
FEE = D("0.0004")
MONEY = D("0.00000001")
require = n3.require


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def durable(path, data, mode="xb"):
    with path.open(mode) as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def validate_quote(row, source, observed_ns):
    require(row["kind"] == "quote" and row["instrument_id"] == n3.NATIVE_ID
            and row["native_type"] == "nautilus_trader.model.data.QuoteTick", "wrong quote source")
    require(row["source_hash"] == n3.digest({k: v for k, v in row.items()
            if k not in ("source_hash", "ts_init")}), "wrong quote source hash")
    require(0 < row["ts_event"] <= observed_ns + 1_000_000_000
            and 0 <= observed_ns - row["ts_event"] <= 5_000_000_000
            and row["ts_event"] - 1_000_000_000 <= row["ts_init"] <= observed_ns + 1_000_000_000,
            "stale/inconsistent quote timestamp")
    bid, ask = n3.positive(row["bid"]), n3.positive(row["ask"])
    require(bid <= ask, "crossed quote")
    for key in ("bid", "ask"):
        value = D(row[key])
        require(value % D(source["price_increment"]) == 0
                and -value.as_tuple().exponent == source["price_precision"]
                and D(source["min_price"]) <= value <= D(source["max_price"]), "price filter/precision drift")
    for key in ("bid_size", "ask_size"):
        require(n3.positive(row[key]) >= QTY and D(row[key]) % D(source["size_increment"]) == 0,
                "quote size/filter mismatch")
    require(QTY >= D(source["min_quantity"]) and QTY <= D(source["max_quantity"])
            and QTY % D(source["size_increment"]) == 0, "fixed quantity violates filters")
    filters = {f["filterType"]: f for f in source["info"]["filters"]}
    market = filters["MARKET_LOT_SIZE"]
    require(D(market["minQty"]) <= QTY <= D(market["maxQty"])
            and QTY % D(market["stepSize"]) == 0, "market quantity filter")
    minimum = n2._money(source["min_notional"])
    require(minimum <= QTY * bid <= QTY * ask <= D(250), "notional outside fixed bounds")
    return row


def local_spec(source):
    require(source["id"] == n3.NATIVE_ID and source["type"] == "CryptoPerpetual"
            and source["base_currency"] == "BTC" and source["quote_currency"] == "USDT"
            and source["settlement_currency"] == "USDT" and source["is_inverse"] is False,
            "wrong source instrument/units")
    info = source["info"]
    require(all(info.get(k) == v for k, v in {"symbol": "BTCUSDT", "baseAsset": "BTC",
            "quoteAsset": "USDT", "marginAsset": "USDT", "contractType": "PERPETUAL",
            "status": "TRADING"}.items()), "wrong public instrument provenance")
    # Only these fields differ; copied filters retain their original Binance provenance.
    return {**source, "id": LOCAL_ID, "margin_init": "1", "maker_fee": str(FEE),
            "taker_fee": str(FEE)}


class Journal:
    def __init__(self, root, header):
        self.root, self.run_id, self.rows = root, str(uuid.uuid4()), []
        self.append("header", header)

    def append(self, kind, payload):
        row = {"seq": len(self.rows), "run_id": self.run_id, "source": SOURCE,
               "previous": self.rows[-1]["sha256"] if self.rows else None,
               "kind": kind, "payload": payload}
        row["sha256"] = n2._hash(row)
        durable(self.root / "events.jsonl", n2._bytes(row) + b"\n", "ab")
        self.rows.append(row)

    def seal(self, summary):
        manifest = {"source": SOURCE, "version": n2.VERSION, "run_id": self.run_id,
                    "producer_pid": os.getpid(), "authority": AUTHORITY,
                    "event_count": len(self.rows), "tail": self.rows[-1]["sha256"],
                    "journal_sha256": file_hash(self.root / "events.jsonl"), "summary": summary}
        durable(self.root / "manifest.json", n2._bytes(manifest))
        return file_hash(self.root / "manifest.json")


class Feed(n3.Observations):
    def __init__(self):
        super().__init__()
        self.tick = None
        self.stopped = False

    def accept(self, data, now_ns):
        accepted = super().accept(data, now_ns)
        if accepted and self.latest.get("quote", {}).get("ts_init") == getattr(data, "ts_init", None):
            from nautilus_trader.model.data import QuoteTick
            if isinstance(data, QuoteTick):
                self.tick = data
        return accepted

    def gate(self, source, transport_active):
        try:
            require(not self.stopped and not self.error and transport_active, "feed unavailable or latched stop")
            require(self.tick is not None, "missing feed")
            return validate_quote(self.latest["quote"], source, time.time_ns())
        except Exception:
            self.stopped = True
            raise


class NativeSession:
    """One fixed round-trip. This owns only the disposable N4SIM native objects."""
    def __init__(self, source, journal):
        from nautilus_trader.adapters.sandbox.execution import SandboxExecutionClient
        from nautilus_trader.adapters.sandbox.config import SandboxExecutionClientConfig
        from nautilus_trader.backtest.models import FillModel
        from nautilus_trader.cache.cache import Cache
        from nautilus_trader.common.component import TestClock, MessageBus
        from nautilus_trader.common.factories import OrderFactory
        from nautilus_trader.execution.engine import ExecutionEngine
        from nautilus_trader.model.identifiers import TraderId, StrategyId
        from nautilus_trader.model.instruments import CryptoPerpetual
        from nautilus_trader.portfolio.portfolio import Portfolio

        self.source, self.journal = source, journal
        self.clock = TestClock()
        self.clock.set_time(time.time_ns())
        self.trader, self.strategy = TraderId("N4PROOF-001"), StrategyId("N4PROOF-001")
        self.bus = MessageBus(self.trader, self.clock)
        self.cache = Cache()
        self.portfolio = Portfolio(self.bus, self.cache, self.clock)
        self.engine = ExecutionEngine(self.bus, self.cache, self.clock)
        self.instrument = CryptoPerpetual.from_dict(local_spec(source))
        self.cache.add_instrument(self.instrument)
        self.submitted = 0
        for topic in ("events.order.*", "events.position.*", "events.account.*"):
            self.bus.subscribe(topic, self.observe)
        self.client = SandboxExecutionClient(asyncio.get_running_loop(), self.portfolio, self.bus,
            self.cache, self.clock, SandboxExecutionClientConfig(venue="N4SIM",
            starting_balances=["10000 USDT"], base_currency="USDT", default_leverage=D(1)))
        self.client.exchange.set_fill_model(FillModel(random_seed=n2.SEED))
        self.engine.register_client(self.client)
        self.client.connect()
        self.factory = OrderFactory(self.trader, self.strategy, self.clock)

    def observe(self, event):
        payload = type(event).to_dict(event)
        require(payload["type"] in n2.TYPES, "unknown native event")
        if payload["type"] == "OrderSubmitted":
            order = self.cache.order(event.client_order_id)
            payload["observed_order_object"] = {"quantity": str(order.quantity), "side": order.side.name}
        self.journal.append("native", payload)

    def step(self, tick):
        from nautilus_trader.core.uuid import UUID4
        from nautilus_trader.execution.messages import SubmitOrder
        from nautilus_trader.model.data import QuoteTick
        from nautilus_trader.model.enums import OrderSide
        from nautilus_trader.model.objects import Quantity

        require(self.submitted < 2 and str(tick.instrument_id) == n3.NATIVE_ID, "fixed session/venue only")
        observed_ns = time.time_ns()
        row = validate_quote(n3.observation_projection(tick, observed_ns), self.source, observed_ns)
        self.journal.append("input", {"quote": row, "observed_ns": observed_ns,
                                     "local_id": LOCAL_ID, "step": self.submitted})
        self.clock.set_time(observed_ns)
        local = QuoteTick(self.instrument.id, tick.bid_price, tick.ask_price, tick.bid_size,
                          tick.ask_size, tick.ts_event, tick.ts_init)
        self.cache.add_quote_tick(local)
        self.portfolio.update_quote_tick(local)
        self.client.on_data(local)
        side = OrderSide.BUY if self.submitted == 0 else OrderSide.SELL
        order = self.factory.market(self.instrument.id, side, Quantity.from_str(str(QTY)))
        self.engine.execute(SubmitOrder(self.trader, self.strategy, order, UUID4(), observed_ns))
        self.submitted += 1
        snapshot = self.snapshot()
        require(snapshot["quantity"] == ("0.001" if self.submitted == 1 else "0"), "native position not expected")
        require(snapshot["orders"] == self.submitted and snapshot["fills"] == self.submitted,
                "native order/fill incomplete")
        self.journal.append("checkpoint", snapshot)
        return snapshot

    def snapshot(self):
        from nautilus_trader.model.currencies import USDT
        fills = [r["payload"] for r in self.journal.rows
                 if r["kind"] == "native" and r["payload"]["type"] == "OrderFilled"]
        balance = self.cache.accounts()[0].balance_total(USDT).as_decimal()
        realized = self.portfolio.realized_pnl(self.instrument.id)
        unrealized = self.portfolio.unrealized_pnl(self.instrument.id)
        qty = sum((D(str(p.signed_qty)) for p in self.cache.positions_open()), D(0))
        upnl = unrealized.as_decimal() if unrealized else D(0)
        return {"quantity": n2._text(qty), "balance": n2._text(balance),
                "realized_net": n2._text(realized.as_decimal() if realized else 0),
                "unrealized": n2._text(upnl), "equity": n2._text(balance + upnl),
                "fees": n2._text(sum((n2._money(f["commission"]) for f in fills), D(0))),
                "orders": len(self.cache.orders()), "fills": len(fills),
                "statuses": [o.status.name for o in self.cache.orders()]}

    def close(self):
        self.client.disconnect()


def verify(root, expected):
    """Read-only durable observations; never import native execution or rehydrate a cache."""
    raw_manifest = (root / "manifest.json").read_bytes()
    require(hashlib.sha256(raw_manifest).hexdigest() == expected, "untrusted manifest digest")
    m = json.loads(raw_manifest)
    require(m["source"] == SOURCE and m["version"] == n2.VERSION and m["authority"] == AUTHORITY,
            "wrong source/version/authority")
    raw = (root / "events.jsonl").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == m["journal_sha256"] and raw.endswith(b"\n"), "torn journal")
    rows = [json.loads(line) for line in raw.splitlines()]
    require(len(rows) == m["event_count"] and len(rows) > 1 and rows[0]["kind"] == "header", "missing events")
    header = rows[0]["payload"]
    source = header["instrument"]
    require(header["local_instrument"] == local_spec(source)
            and header["instrument_hash"] == n2._hash(source), "wrong mapping/source hash")
    require(header["environment"]["python"] == "3.12.10"
            and header["environment"]["versions"]["nautilus-trader"] == n2.VERSION
            and header["environment"]["versions"]["pyarrow"] == "25.0.1", "wrong pins")
    ids, trades, venue_orders, orders, inputs, positions, checkpoints = set(), set(), set(), {}, [], [], []
    fills = []
    account_balance = D(10000)
    last_time = 0
    for seq, row in enumerate(rows):
        require(set(row) == {"seq", "run_id", "source", "previous", "kind", "payload", "sha256"}
                and row["seq"] == seq and row["run_id"] == m["run_id"] and row["source"] == SOURCE
                and row["previous"] == (rows[seq-1]["sha256"] if seq else None)
                and row["sha256"] == n2._hash({k: v for k, v in row.items() if k != "sha256"}),
                "event identity/order/hash mismatch")
        p = row["payload"]
        if row["kind"] == "header":
            require(seq == 0, "duplicate header")
        elif row["kind"] == "input":
            require(len(inputs) < 2 and len(fills) == len(inputs) and p["step"] == len(inputs)
                    and p["local_id"] == LOCAL_ID, "input lifecycle mismatch")
            validate_quote(p["quote"], source, p["observed_ns"])
            if inputs:
                require(p["quote"]["ts_event"] > inputs[-1]["quote"]["ts_event"], "quote sequence")
            inputs.append(p)
        elif row["kind"] == "native":
            kind = p["type"]
            require(kind in n2.TYPES and p["event_id"] not in ids, "duplicate/unknown native event")
            ids.add(p["event_id"])
            require(p["account_id"] == "N4SIM-001" and p["ts_init"] >= last_time, "account/time mismatch")
            last_time = p["ts_init"]
            if kind == "AccountState":
                require(p["base_currency"] == "USDT" and p["account_type"] == "MARGIN"
                        and len(p["balances"]) == 1, "wrong account units")
                b = p["balances"][0]
                require(b["currency"] == "USDT" and D(b["free"]) + D(b["locked"]) == D(b["total"]),
                        "wrong account balance")
                account_balance = D(b["total"])
                for margin in p["margins"]:
                    require(margin["instrument_id"] == LOCAL_ID and margin["currency"] == "USDT", "wrong margin")
            else:
                require(p["instrument_id"] == LOCAL_ID and p["trader_id"] == "N4PROOF-001"
                        and p["strategy_id"] == "N4PROOF-001", "native identity mismatch")
                # Matching engine uses the quote clock; portfolio publications use observation time.
                require(inputs and min(inputs[-1]["quote"]["ts_init"], inputs[-1]["observed_ns"])
                        <= p["ts_init"] <= inputs[-1]["observed_ns"], "unbound native time")
                if kind == "OrderSubmitted":
                    oid = p["client_order_id"]
                    require(oid not in orders and len(orders) < 2 and len(orders) == len(fills)
                            and len(inputs) == len(orders)+1, "order lifecycle")
                    side = "BUY" if not orders else "SELL"
                    require(p["observed_order_object"] == {"side": side, "quantity": "0.001"}, "fixed order violated")
                    orders[oid] = "SUBMITTED"
                elif kind == "OrderFilled":
                    oid = p["client_order_id"]
                    require(orders.get(oid) == "SUBMITTED" and p["trade_id"] not in trades, "duplicate/unknown fill")
                    side = "BUY" if not fills else "SELL"
                    price = D(inputs[-1]["quote"]["ask" if side == "BUY" else "bid"])
                    require(p["order_side"] == side and p["order_type"] == "MARKET"
                            and D(p["last_qty"]) == QTY and D(p["last_px"]) == price
                            and p["currency"] == "USDT" and p["liquidity_side"] == "TAKER"
                            and p["venue_order_id"].startswith("N4SIM-")
                            and p["venue_order_id"] not in venue_orders
                            and p["position_id"] == LOCAL_ID + "-N4PROOF-001"
                            and n2._money(p["commission"]) == (QTY * price * FEE).quantize(MONEY),
                            "fill economics/source mismatch")
                    trades.add(p["trade_id"])
                    venue_orders.add(p["venue_order_id"])
                    fills.append(p)
                    orders[oid] = "FILLED"
                elif kind in ("PositionOpened", "PositionClosed"):
                    require(p["opening_order_id"] == fills[0]["client_order_id"] and p["currency"] == "USDT"
                            and p["position_id"] == fills[-1]["position_id"], "position identity")
                    if kind == "PositionClosed":
                        require(p["closing_order_id"] == fills[-1]["client_order_id"], "position closing order")
                    expected_qty = QTY if kind == "PositionOpened" else D(0)
                    require(D(str(p["signed_qty"])) == expected_qty and D(p["quantity"]) == expected_qty,
                            "position quantity mismatch")
                    positions.append(p)
                else:
                    raise ValueError("unexpected fixed-round-trip event")
        elif row["kind"] == "checkpoint":
            require(len(checkpoints) < 2 and len(fills) == len(checkpoints)+1
                    and len(positions) == len(fills), "checkpoint lifecycle")
            fees = sum((n2._money(f["commission"]) for f in fills), D(0))
            gross = QTY * (D(fills[1]["last_px"]) - D(fills[0]["last_px"])) if len(fills) == 2 else D(0)
            realized = (gross - fees).quantize(MONEY)
            qty = QTY if len(fills) == 1 else D(0)
            unrealized = (QTY * (D(inputs[-1]["quote"]["bid"]) - D(fills[0]["last_px"]))).quantize(MONEY) if qty else D(0)
            balance = (D(10000) + realized).quantize(MONEY)
            expected_snapshot = {"quantity": n2._text(qty), "balance": n2._text(balance),
                "realized_net": n2._text(realized), "unrealized": n2._text(unrealized),
                "equity": n2._text(balance + unrealized), "fees": n2._text(fees),
                "orders": len(fills), "fills": len(fills), "statuses": ["FILLED"] * len(fills)}
            require(p == expected_snapshot and account_balance == balance, "native accounting differs from Decimal assertions")
            require(n2._money(positions[-1]["realized_pnl"]) == realized, "position realized PnL mismatch")
            checkpoints.append(p)
        else:
            raise ValueError("unknown journal record")
    require(rows[-1]["sha256"] == m["tail"] and rows[-1]["kind"] == "checkpoint"
            and len(inputs) == len(fills) == len(checkpoints) == 2
            and [p["type"] for p in positions] == ["PositionOpened", "PositionClosed"]
            and m["summary"] == checkpoints[-1] and m["summary"]["quantity"] == "0", "incomplete/non-flat session")
    return {"source": SOURCE, "manifest_sha256": expected, "run_id": m["run_id"],
            "durably_observed": m["summary"], "native_cache_rehydrated": False,
            "new_orders": 0, "new_fills": 0, "authority": AUTHORITY}


def public_http(clock, requests):
    from nautilus_trader.adapters.binance.http.client import BinanceHttpClient
    from nautilus_trader.core.nautilus_pyo3 import HttpMethod

    class PublicHttp(BinanceHttpClient):
        async def send_request(self, http_method, url_path, payload=None, ratelimiter_keys=None):
            require(http_method == HttpMethod.GET and url_path == "/fapi/v1/exchangeInfo"
                    and not payload, "only unsigned public exchangeInfo GET allowed")
            requests.append({"method": "GET", "url": n3.REST + url_path, "signed": False})
            return await super().send_request(http_method, url_path, payload, ratelimiter_keys)

        async def sign_request(self, *args, **kwargs):
            raise ValueError("signed/private/order requests forbidden")

    return PublicHttp(clock, None, None, n3.REST)


async def public_session(root, receipt):
    from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
    from nautilus_trader.adapters.binance.config import BinanceDataClientConfig, BinanceInstrumentProviderConfig
    from nautilus_trader.adapters.binance.futures.data import BinanceFuturesDataClient
    from nautilus_trader.adapters.binance.futures.providers import BinanceFuturesInstrumentProvider
    from nautilus_trader.cache.cache import Cache
    from nautilus_trader.common.component import LiveClock, MessageBus, init_logging
    from nautilus_trader.common.enums import LogLevel
    from nautilus_trader.core.uuid import UUID4
    from nautilus_trader.data.messages import SubscribeQuoteTicks, SubscribeMarkPrices
    from nautilus_trader.model.identifiers import InstrumentId, TraderId
    from nautilus_trader.model.instruments import CryptoPerpetual

    clock = LiveClock()
    logging_guard = init_logging(level_stdout=LogLevel.INFO, colors=False)
    iid = InstrumentId.from_str(n3.NATIVE_ID)
    config = BinanceInstrumentProviderConfig(load_ids=frozenset({iid}))
    provider = BinanceFuturesInstrumentProvider(public_http(clock, receipt["requests"]), clock, config=config)
    bus = MessageBus(TraderId("N4DATA-001"), clock)
    feed = Feed()
    bus.register("DataEngine.process", feed.receive)
    client = BinanceFuturesDataClient(asyncio.get_running_loop(), provider._client, bus, Cache(), clock,
        provider, n3.MARK_WS, BinanceDataClientConfig(account_type=BinanceAccountType.USDT_FUTURES,
        instrument_provider=config, update_instruments_interval_mins=None), base_url_ws_public=n3.QUOTE_WS)
    native = None
    lifecycle = receipt["lifecycle"]
    try:
        with n3.native_lifecycle(client, feed, lifecycle):
            await asyncio.wait_for(client._connect(), 30)
            source_instrument = provider.find(iid)
            receipt["public_instrument"] = n3.instrument_projection(source_instrument)
            source = CryptoPerpetual.to_dict(source_instrument)
            command = (iid, None, iid.venue, UUID4(), clock.timestamp_ns())
            await asyncio.wait_for(client._subscribe_quote_ticks(SubscribeQuoteTicks(*command)), 15)
            await asyncio.wait_for(client._subscribe_mark_prices(SubscribeMarkPrices(*command)), 15)
            await n3.wait_until(feed.fresh, 15, feed)
            header = {"instrument": source, "instrument_hash": n2._hash(source),
                      "local_instrument": local_spec(source), "environment": receipt["environment"],
                      "provenance": "fresh native public input; derived N4SIM ID; fixture 4bps, 1x, 10000 USDT",
                      "mark_observation": feed.latest["mark"]}
            journal = Journal(root, header)
            native = NativeSession(source, journal)
            for step in range(2):
                if step:
                    previous = feed.latest["quote"]["ts_event"]
                    await n3.wait_until(lambda: feed.latest.get("quote", {}).get("ts_event", 0) > previous, 5, feed)
                clients = client._ws_public_client._clients
                active = bool(clients) and not lifecycle and all(c.is_active() for c in clients.values())
                feed.gate(source, active)
                native.step(feed.tick)
            # Re-query filters with a fresh unsigned provider before acknowledging the seal.
            after = BinanceFuturesInstrumentProvider(public_http(clock, receipt["requests"]), clock, config=config)
            await asyncio.wait_for(after.load_ids_async([iid]), 25)
            n3.unchanged_filters(receipt["public_instrument"], n3.instrument_projection(after.find(iid)))
            require(CryptoPerpetual.to_dict(after.find(iid))["info"]["filters"] == source["info"]["filters"],
                    "public filter drift")
            receipt["summary"] = native.snapshot()
            receipt["manifest_sha256"] = journal.seal(receipt["summary"])
            receipt["verification"] = verify(root, receipt["manifest_sha256"])
            receipt["observations"] = feed.latest
            receipt["result"] = "N4_01_INTEGRATED_NONCAPITAL_PASSED"
    finally:
        if native:
            native.close()
        await asyncio.wait_for(client._disconnect(), 5)
        receipt["cleanup"] = "owned native sandbox and public clients disconnected"
        del logging_guard


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    run = sub.add_parser("run")
    run.add_argument("--public-noncapital-proof", action="store_true", required=True)
    run.add_argument("--output", type=Path, required=True)
    read = sub.add_parser("verify")
    read.add_argument("--output", type=Path, required=True)
    read.add_argument("--expected-manifest-sha256", required=True)
    args = parser.parse_args(argv)
    receipt = {"result": "BLOCKED", "authority": AUTHORITY, "pid": os.getpid(),
               "started_ns": time.time_ns(), "requests": [], "lifecycle": []}
    writable_output = None
    try:
        if args.action == "verify":
            result = verify(args.output, args.expected_manifest_sha256)
            print(json.dumps({"pid": os.getpid(), "result": result}, sort_keys=True))
            return 0
        root = args.output.resolve()
        require(root.is_dir() and not root.is_relative_to(n3.ROOT) and not args.output.is_symlink()
                and not any(root.iterdir()), "empty ordinary external output directory required")
        writable_output = root
        require(platform.system() == "Linux" and platform.python_version() == "3.12.10", "exact Linux Python required")
        receipt["environment"] = n2._environment()
        receipt["module_sha256"] = file_hash(Path(__file__))

        async def bounded():
            async with asyncio.timeout(100):
                await public_session(root, receipt)
        asyncio.run(bounded())
    except Exception as exc:
        receipt.update(result="BLOCKED", error=f"{type(exc).__name__}: {exc}")
    receipt["finished_ns"] = time.time_ns()
    if writable_output is not None:
        durable(writable_output / "receipt.json", n2._bytes(receipt))
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["result"] == "N4_01_INTEGRATED_NONCAPITAL_PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
