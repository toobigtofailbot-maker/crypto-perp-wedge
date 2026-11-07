"""Default-off, bounded native sandbox; private/recovery operations remain HOLD."""
from __future__ import annotations

import asyncio
from decimal import Decimal as D
import importlib.metadata
import re
import time

from src.execution.nautilus_recovery_hold_guard import HoldDecision, refuse_before_send

VERSION = "1.231.0"
LOCAL_ID = "BTCUSDT-PERP.CPWSIM"
PUBLIC_ID = "BTCUSDT-PERP.BINANCE"


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def validate_config(config):
    # Allowlist before native imports/factories: no credentials, arbitrary endpoints or clients.
    allowed = {"profile", "trader_id", "public_data", "persist", "macro_flags_path",
               "signal_provider", "duration_seconds"}
    if set(config) - allowed or config.get("profile") != "NONCAPITAL_NATIVE":
        refuse_before_send()
    require(re.fullmatch(r"CPWNATIVE-[0-9a-f]{12}", config.get("trader_id", "")), "task-owned trader required")
    require(type(config.get("public_data", False)) is bool and type(config.get("persist", False)) is bool,
            "boolean profile flags required")
    duration = config.get("duration_seconds", 10)
    require(type(duration) in (int, float) and 0 < duration <= 60, "bounded duration required")


def _database(config, *, recovery=False):
    if not config.get("persist"):
        require(not recovery, "recovery requires native persistence")
        return None
    import redis
    from nautilus_trader.config import DatabaseConfig

    db = redis.Redis(host="127.0.0.1", port=6379, socket_connect_timeout=2, socket_timeout=2)
    keys = list(db.scan_iter("trader-" + config["trader_id"] + ":*"))
    if recovery:
        acl = db.acl_getuser("default")
        require(set(acl["categories"]) == {"-@all", "+@read"} and not acl["selectors"]
                and set(acl["commands"]) <= {"+ping", "+info", "+config|get", "+acl|getuser",
                                             "+client|setinfo", "+client|setname"}, "read-only Redis ACL required")
        require(bool(keys), "native state absent")
    else:
        require(not keys, "existing native namespace; no automatic resume")
        require(db.config_get("appendonly") == {"appendonly": "yes"}
                and db.config_get("appendfsync") == {"appendfsync": "always"}, "durable native backend required")
        # CPW ownership only, never economic state or a recovery permit; survives crashes.
        require(db.set("trader-" + config["trader_id"] + ":cpw:producer_claim",
                       "NONCAPITAL_ONLY_NO_RESUME", nx=True), "native namespace already claimed")
    return DatabaseConfig(type="redis", host="127.0.0.1", port=6379,
                          connection_timeout=2, response_timeout=2, number_of_retries=1)


def _node(config, *, recovery=False):
    validate_config(config)
    require(importlib.metadata.version("nautilus-trader") == VERSION, "unverified native version")
    from nautilus_trader.adapters.sandbox.config import SandboxExecutionClientConfig
    from nautilus_trader.adapters.sandbox.factory import SandboxLiveExecClientFactory
    from nautilus_trader.common import Environment
    from nautilus_trader.config import CacheConfig, LiveExecEngineConfig, LoggingConfig, TradingNodeConfig
    from nautilus_trader.live.node import TradingNode

    database = _database(config, recovery=recovery)
    data_clients = {}
    if config.get("public_data") and not recovery:
        from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
        from nautilus_trader.adapters.binance.config import BinanceDataClientConfig, BinanceInstrumentProviderConfig
        from nautilus_trader.model.identifiers import InstrumentId
        data_clients["BINANCE"] = BinanceDataClientConfig(
            account_type=BinanceAccountType.USDT_FUTURES,
            instrument_provider=BinanceInstrumentProviderConfig(load_ids=frozenset({InstrumentId.from_str(PUBLIC_ID)})),
            update_instruments_interval_mins=None)
    node = TradingNode(config=TradingNodeConfig(environment=Environment.SANDBOX,
        trader_id=config["trader_id"], cache=CacheConfig(database=database, encoding="json",
            persist_account_events=True, buffer_interval_ms=None, use_instance_id=False, flush_on_start=False),
        exec_engine=LiveExecEngineConfig(load_cache=True, reconciliation=False, inflight_check_interval_ms=0),
        logging=LoggingConfig(log_level="ERROR"), timeout_connection=15, timeout_reconciliation=2,
        timeout_portfolio=2, timeout_disconnection=2, timeout_post_stop=0,
        data_clients=data_clients,
        exec_clients={} if recovery else {"CPWSIM": SandboxExecutionClientConfig(venue="CPWSIM",
            starting_balances=["10000 USDT"], base_currency="USDT", default_leverage=D(1))}),
        loop=asyncio.get_running_loop())
    if not recovery:
        node.add_exec_client_factory("CPWSIM", SandboxLiveExecClientFactory)
        if data_clients:
            from nautilus_trader.adapters.binance.factories import BinanceLiveDataClientFactory
            node.add_data_client_factory("BINANCE", BinanceLiveDataClientFactory)
        node.build()
    return node


def local_instrument(source):
    from nautilus_trader.model.instruments import CryptoPerpetual
    spec = CryptoPerpetual.to_dict(source)
    require(spec["id"] == PUBLIC_ID and not spec["is_inverse"]
            and spec["base_currency"] == "BTC" and spec["quote_currency"] == "USDT"
            and spec["settlement_currency"] == "USDT", "wrong source instrument")
    return CryptoPerpetual.from_dict({**spec, "id": LOCAL_ID, "margin_init": "1",
                                     "maker_fee": "0.0004", "taker_fee": "0.0004"})


def snapshot(node):
    from nautilus_trader.model.currencies import USDT
    cache = node.kernel.cache
    return {"authority": HoldDecision().authority, "native_version": VERSION,
            "trader_id": str(node.trader_id), "private_clients": 0,
            "orders": [type(o).to_dict(o) for o in sorted(cache.orders(), key=lambda o: str(o.client_order_id))],
            "order_events": {str(o.client_order_id): [type(e).to_dict(e) for e in o.events]
                             for o in sorted(cache.orders(), key=lambda o: str(o.client_order_id))},
            "positions": [type(p).to_dict(p) for p in sorted(cache.positions(), key=lambda p: str(p.id))],
            "balance": str(cache.accounts()[0].balance_total(USDT).as_decimal()) if cache.accounts() else None,
            "quantity": str(sum((D(str(p.signed_qty)) for p in cache.positions_open()), D(0)))}


async def run(config, policy, *, ticks=None, instrument=None):
    """Native node owns lifecycle; policy returns an existing CPW OrderIntent or None."""
    validate_config(config)
    require((ticks is None) == config.get("public_data", False), "explicit public or synthetic input required")
    from nautilus_trader.config import StrategyConfig
    from nautilus_trader.model.data import QuoteTick
    from nautilus_trader.model.enums import OrderSide
    from nautilus_trader.model.identifiers import InstrumentId, ClientOrderId
    from nautilus_trader.trading.strategy import Strategy

    node = _node(config)
    task = None
    try:
        if config.get("public_data"):
            client = next(iter(node.kernel.data_engine._clients.values()))
            await asyncio.wait_for(client._instrument_provider.load_ids_async([InstrumentId.from_str(PUBLIC_ID)]), 15)
            instrument = client._instrument_provider.find(InstrumentId.from_str(PUBLIC_ID))
        require(instrument is not None, "native source instrument required")
        local = local_instrument(instrument)
        node.kernel.cache.add_instrument(instrument)
        node.kernel.cache.add_instrument(local)
        source_id = InstrumentId.from_str(PUBLIC_ID)
        sandbox = next(iter(node.kernel.exec_engine._clients.values()))
        observations, decisions = [], []
        failure = []

        class Consumer(Strategy):
            def __init__(self):
                super().__init__(StrategyConfig(strategy_id="CPWPOLICY-001"))
                self.previous = 0
                self.previous_tick = None
                self.opened = False
                self.closed = False

            def on_start(self):
                self.subscribe_quote_ticks(source_id)

            def on_quote_tick(self, tick):
                if failure:
                    return
                try:
                    now = time.time_ns()
                    key = (tick.ts_event, tick.bid_price, tick.ask_price, tick.bid_size, tick.ask_size)
                    if key == self.previous_tick:
                        return
                    require(tick.instrument_id == source_id and self.previous <= tick.ts_event <= now
                            and now - tick.ts_event <= 5_000_000_000
                            and tick.ts_event <= tick.ts_init <= now,
                            f"stale/duplicate/reordered quote: event={tick.ts_event} init={tick.ts_init} now={now} previous={self.previous}")
                    require(0 < tick.bid_price <= tick.ask_price and tick.bid_size >= local.min_quantity
                            and tick.ask_size >= local.min_quantity, "invalid native quote")
                    require(all(p.as_decimal() % local.price_increment.as_decimal() == 0
                                for p in (tick.bid_price, tick.ask_price)), "native price increment mismatch")
                    self.previous = tick.ts_event
                    self.previous_tick = key
                    observations.append(QuoteTick.to_dict(tick))
                    local_tick = QuoteTick(local.id, tick.bid_price, tick.ask_price, tick.bid_size,
                                           tick.ask_size, tick.ts_event, tick.ts_init)
                    sandbox.test_clock.set_time(tick.ts_init)
                    self.cache.add_quote_tick(local_tick)
                    self.portfolio.update_quote_tick(local_tick)
                    sandbox.on_data(local_tick)
                    require(not self.cache.orders_inflight() and not self.cache.orders_open(), "unsettled native order")
                    current = sum((D(str(p.signed_qty)) for p in self.cache.positions_open()), D(0))
                    intent = policy(tick, current)
                    if intent is None:
                        return
                    qty = intent.qty
                    side = intent.side.value
                    target = current + (qty if side == "BUY" else -qty)
                    require(not self.closed and qty == D("0.001") and intent.symbol == "BTCUSDT"
                            and ((not self.opened and current == 0 and target == qty and side == "BUY")
                                 or (self.opened and current == qty and target == 0 and side == "SELL")),
                            "unsupported target/history; HOLD")
                    require(qty >= local.min_quantity and qty % local.size_increment.as_decimal() == 0
                            and (local.max_quantity is None or qty <= local.max_quantity.as_decimal())
                            and qty * tick.bid_price.as_decimal() >= local.min_notional.as_decimal()
                            and qty * tick.ask_price.as_decimal() <= D(250), "native quantity/notional bounds")
                    order = self.order_factory.market(local.id,
                        OrderSide.BUY if side == "BUY" else OrderSide.SELL,
                        local.make_qty(qty), client_order_id=ClientOrderId(intent.client_order_id),
                        reduce_only=intent.reduce_only)
                    decisions.append(intent.client_order_id)
                    self.opened = True
                    self.closed = target == 0
                    self.submit_order(order)
                except Exception as exc:
                    failure.append(exc)

        consumer = Consumer()
        node.trader.add_strategy(consumer)
        task = asyncio.create_task(node.run_async())
        async with asyncio.timeout(20):
            while not consumer.is_running:
                if task.done():
                    await task
                    raise ValueError("native node did not start")
                await asyncio.sleep(.01)
        if ticks is not None:
            for tick in ticks:
                node.kernel.data_engine.process(tick)
                await asyncio.sleep(.05)
                if failure:
                    raise failure[0]
                async with asyncio.timeout(5):
                    while node.kernel.cache.orders_inflight() or node.kernel.cache.orders_open():
                        await asyncio.sleep(.01)
        else:
            await asyncio.sleep(config.get("duration_seconds", 10))
        if failure:
            raise failure[0]
        require(bool(observations), "no native data reached consumer")
        require(node.kernel.cache.check_integrity(), "native cache integrity")
        return {**snapshot(node), "source": "PUBLIC_UNSIGNED" if ticks is None else "SYNTHETIC_NATIVE",
                "observations": observations, "intent_ids": decisions}
    finally:
        if task is not None:
            await node.stop_async()
            await asyncio.wait_for(task, 5)
        node.kernel.dispose()


async def recover(config):
    """Native cache reconstruction under a read-only backend; never starts a node."""
    node = _node(config, recovery=True)
    try:
        cache, engine = node.kernel.cache, node.kernel.exec_engine
        require(not engine.registered_clients and engine.command_count == engine.event_count == 0,
                "recovery cannot execute")
        require(cache.check_integrity() and not cache.orders_open() and not cache.orders_inflight()
                and 1 <= len(cache.orders()) <= 2 and len(cache.positions()) == 1
                and not cache.position_snapshots(), "unsupported/incomplete native recovery; HOLD")
        state = snapshot(node)
        ids = {o.client_order_id for o in cache.orders()}
        position = cache.positions()[0]
        require(position.opening_order_id in ids
                and (position.closing_order_id is None or position.closing_order_id in ids),
                "incomplete native recovery order lineage; HOLD")
        require(all(o.status.name == "FILLED" and o.quantity.as_decimal() == D("0.001")
                    and o.order_type.name == "MARKET" for o in cache.orders())
                and state["quantity"] in ("0", "0.001")
                and all(str(o.instrument_id) == LOCAL_ID for o in cache.orders()), "unknown native state; HOLD")
        return {**state, "recovery": "NATIVE_READ_ONLY_HOLD", "commands": engine.command_count}
    finally:
        node.kernel.dispose()
