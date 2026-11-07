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
QUANTITY = D("0.001")


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


def _database(config, *, recovery=False, portfolio=False):
    if not config.get("persist"):
        require(not recovery, "recovery requires native persistence")
        return None
    import redis
    from nautilus_trader.config import DatabaseConfig

    port = 16379 if portfolio else 6379
    db = redis.Redis(host="127.0.0.1", port=port, socket_connect_timeout=2, socket_timeout=2)
    if portfolio:
        require(db.get("cpw:laneb:p1:isolation") == b"LOCAL_TEST_ONLY", "dedicated P1 Redis required")
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
    return DatabaseConfig(type="redis", host="127.0.0.1", port=port,
                          connection_timeout=2, response_timeout=2, number_of_retries=1)


def _node(config, *, recovery=False, portfolio=False):
    validate_config(config)
    require(importlib.metadata.version("nautilus-trader") == VERSION, "unverified native version")
    from nautilus_trader.adapters.sandbox.config import SandboxExecutionClientConfig
    from nautilus_trader.adapters.sandbox.factory import SandboxLiveExecClientFactory
    from nautilus_trader.common import Environment
    from nautilus_trader.config import CacheConfig, LiveExecEngineConfig, LoggingConfig, TradingNodeConfig
    from nautilus_trader.live.node import TradingNode

    database = _database(config, recovery=recovery, portfolio=portfolio)
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
                    require(0 < tick.bid_price <= tick.ask_price and tick.bid_size.as_decimal() >= QUANTITY
                            and tick.ask_size.as_decimal() >= QUANTITY, "invalid native quote")
                    require(all(p.as_decimal() % local.price_increment.as_decimal() == 0
                                for p in (tick.bid_price, tick.ask_price)), "native price increment mismatch")
                    require(QUANTITY * tick.ask_price.as_decimal() <= D(250), "native quote exceeds notional bound")
                    self.previous = tick.ts_event
                    self.previous_tick = key
                    observations.append(QuoteTick.to_dict(tick))
                    local_tick = QuoteTick(local.id, tick.bid_price, tick.ask_price, tick.bid_size,
                                           tick.ask_size, tick.ts_event, tick.ts_init)
                    sandbox.test_clock.set_time(tick.ts_init)
                    self.cache.add_quote_tick(local_tick)
                    self.portfolio.update_quote_tick(local_tick)
                    sandbox.on_data(local_tick)
                    if decisions:
                        # A submitted command can still be queued before the native order is inflight.
                        last = self.cache.order(ClientOrderId(decisions[-1]))
                        if last is None or not last.is_closed:
                            return
                        require(last.status.name == "FILLED", "incomplete native fill; HOLD")
                    require(not self.cache.orders_inflight() and not self.cache.orders_open(), "unsettled native order")
                    current = sum((D(str(p.signed_qty)) for p in self.cache.positions_open()), D(0))
                    intent = policy(tick, current)
                    if intent is None:
                        return
                    qty = intent.qty
                    side = intent.side.value
                    target = current + (qty if side == "BUY" else -qty)
                    require(qty == QUANTITY and intent.symbol == "BTCUSDT"
                            and ((not decisions and current == 0 and target == qty and side == "BUY")
                                 or (len(decisions) == 1 and current == qty and target == 0 and side == "SELL")),
                            "unsupported target/history; HOLD")
                    require(qty >= local.min_quantity and qty % local.size_increment.as_decimal() == 0
                            and (local.max_quantity is None or qty <= local.max_quantity.as_decimal())
                            and qty * tick.bid_price.as_decimal() >= local.min_notional.as_decimal(),
                            "native quantity/notional bounds")
                    order = self.order_factory.market(local.id,
                        OrderSide.BUY if side == "BUY" else OrderSide.SELL,
                        local.make_qty(qty), client_order_id=ClientOrderId(intent.client_order_id),
                        reduce_only=intent.reduce_only)
                    decisions.append(intent.client_order_id)
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
        orders = node.kernel.cache.orders()
        require({str(o.client_order_id) for o in orders} == set(decisions)
                and all(o.status.name == "FILLED" for o in orders), "missing or incomplete native fill; HOLD")
        return {**snapshot(node), "source": "PUBLIC_UNSIGNED" if ticks is None else "SYNTHETIC_NATIVE",
                "observations": observations, "intent_ids": decisions}
    finally:
        try:
            if task is not None:
                await node.stop_async()
                await asyncio.wait_for(task, 5)
        finally:
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
        require(all(o.status.name == "FILLED" and o.quantity.as_decimal() == QUANTITY
                    and o.order_type.name == "MARKET" for o in cache.orders())
                and state["quantity"] in ("0", "0.001")
                and all(str(o.instrument_id) == LOCAL_ID for o in cache.orders()), "unknown native state; HOLD")
        return {**state, "recovery": "NATIVE_READ_ONLY_HOLD", "commands": engine.command_count}
    finally:
        node.kernel.dispose()
async def _portfolio_instruments(source, symbols):
    """Use native Binance parsing with a captured public response and no HTTP transport."""
    from types import SimpleNamespace

    import msgspec
    from nautilus_trader.adapters.binance.futures.providers import BinanceFuturesInstrumentProvider
    from nautilus_trader.adapters.binance.futures.schemas.market import BinanceFuturesSymbolInfo
    from nautilus_trader.common.component import LiveClock
    from nautilus_trader.model.identifiers import InstrumentId
    from nautilus_trader.model.instruments import CryptoPerpetual

    rows = [row for row in source["symbols"] if row["symbol"] in symbols]
    require(len(rows) == len(symbols) and all(
        row["status"] == "TRADING" and row["contractType"] == "PERPETUAL"
        and row["quoteAsset"] == row["marginAsset"] == "USDT"
        and row["symbol"] == row["baseAsset"] + "USDT" for row in rows), "wrong source instrument")

    async def exchange_info():
        return SimpleNamespace(serverTime=source["server_time_ms"], symbols=[
            msgspec.convert(row, type=BinanceFuturesSymbolInfo, strict=True) for row in rows])

    async def refuse_transport(*args, **kwargs):
        refuse_before_send()

    offline = SimpleNamespace(api_key=None, send_request=refuse_transport, sign_request=refuse_transport)
    provider = BinanceFuturesInstrumentProvider(offline, LiveClock())
    provider._http_market = SimpleNamespace(query_futures_exchange_info=exchange_info)
    ids = [InstrumentId.from_str(f"{symbol}-PERP.BINANCE") for symbol in symbols]
    await asyncio.wait_for(provider.load_ids_async(ids), 30)
    instruments = {}
    for symbol, identifier in zip(symbols, ids, strict=True):
        native = provider.find(identifier)
        require(isinstance(native, CryptoPerpetual) and not native.is_inverse
                and native.quote_currency.code == native.settlement_currency.code == "USDT",
                "native conversion refused source instrument")
        spec = CryptoPerpetual.to_dict(native)
        local = CryptoPerpetual.from_dict({**spec, "id": f"{symbol}-PERP.CPWSIM",
                                          "maker_fee": "0.0004", "taker_fee": "0.0004"})
        instruments[symbol] = (native, local)
    return instruments


def _positions(cache, instruments):
    known = {instrument.id for instrument in instruments.values()}
    positions = cache.positions_open()
    require(all(position.instrument_id in known for position in positions), "unknown native position")
    require(len({position.instrument_id for position in positions}) == len(positions),
            "native netting discrepancy")
    return {position.instrument_id: position for position in positions}


def _portfolio_plan(instruments, quotes, current, targets, order_cap, gross_cap, available):
    """Preflight the whole basket before submission; sequence reductions before increases."""
    require(set(quotes) == set(instruments), "missing portfolio quote")
    now = time.time_ns()
    asks, bids = {}, {}
    for symbol, instrument in instruments.items():
        tick = quotes[symbol]
        bid, ask = tick.bid_price.as_decimal(), tick.ask_price.as_decimal()
        increment = instrument.price_increment.as_decimal()
        require(tick.instrument_id == instrument.id and tick.ts_event <= tick.ts_init <= now
                and now - tick.ts_event <= 5_000_000_000, "stale or mismatched portfolio quote")
        require(instrument.min_price.as_decimal() <= bid <= ask <= instrument.max_price.as_decimal()
                and bid % increment == ask % increment == 0, "native price increment/bounds")
        asks[symbol], bids[symbol] = ask, bid

    projected = current.copy()
    require(available > 0 and sum(abs(current[s]) * asks[s] for s in instruments) <= gross_cap,
            "portfolio gross or available balance veto")
    order_symbols = sorted(instruments, key=lambda s: (abs(targets[s]) >= abs(current[s]), s))
    plan = []
    for symbol in order_symbols:
        target, before = targets[symbol], current[symbol]
        if target == before:
            continue
        instrument = instruments[symbol]
        delta = target - before
        qty = abs(delta)
        require(before * target >= 0, "cross-zero target requires a flat cycle")
        require(qty % instrument.size_increment.as_decimal() == 0
                and instrument.min_quantity.as_decimal() <= qty <= instrument.max_quantity.as_decimal(),
                "native quantity precision/bounds")
        market = next(row for row in instrument.info["filters"] if row["filterType"] == "MARKET_LOT_SIZE")
        market_step = D(market["stepSize"])
        require((not market_step or qty % market_step == 0)
                and D(market["minQty"]) <= qty <= D(market["maxQty"]), "native market quantity bounds")
        require(qty * bids[symbol] >= instrument.min_notional.as_decimal(), "native min notional")
        notional = qty * asks[symbol]
        require(notional <= order_cap, "per-order notional veto")
        size = quotes[symbol].ask_size if delta > 0 else quotes[symbol].bid_size
        require(qty <= size.as_decimal(), "insufficient quote size")
        projected[symbol] = target
        require(sum(abs(projected[s]) * asks[s] for s in instruments) <= gross_cap,
                "portfolio gross veto")
        # Do not count possible margin releases from reductions before native settlement.
        available -= max(D(0), abs(target) - abs(before)) * asks[symbol] + notional * instrument.taker_fee
        require(available > 0, "available balance veto")
        plan.append((symbol, delta))
    return plan


def _native_quantities(cache, instruments):
    positions = _positions(cache, instruments)
    return {symbol: positions[instrument.id].signed_decimal_qty() if instrument.id in positions else D(0)
            for symbol, instrument in instruments.items()}


def _portfolio_observation(node, request, instruments, quotes, order_ids, *, recovery=False):
    from nautilus_trader.model.currencies import USDT
    from src.execution.nautilus_portfolio_contract import canonical, digest

    cache, engine = node.kernel.cache, node.kernel.exec_engine
    accounts = cache.accounts()
    require(len(accounts) == 1 and str(accounts[0].id) == "CPWSIM-001", "unexpected native account")
    account = accounts[0]
    positions = _positions(cache, instruments)
    quantities = _native_quantities(cache, instruments)
    per_symbol = []
    gross = net = realized = D(0)
    for symbol, instrument in instruments.items():
        orders = sorted(cache.orders(instrument_id=instrument.id), key=lambda order: str(order.client_order_id))
        events = [type(event).to_dict(event) for order in orders for event in order.events]
        position = positions.get(instrument.id)
        quote = quotes[symbol]
        qty = quantities[symbol]
        exposure = qty * quote.ask_price.as_decimal()
        gross += abs(exposure)
        net += exposure
        unrealized = position.unrealized_pnl(quote.bid_price if qty > 0 else quote.ask_price) if position else None
        fills = [event for event in events if event["type"] == "OrderFilled"]
        history = cache.positions(instrument_id=instrument.id)
        snapshots = [snapshot for p in history for snapshot in cache.position_snapshots(position_id=p.id)]
        require(all(fill["commission"].endswith(" USDT") for fill in fills), "unexpected native fee currency")
        pnl = [p.realized_pnl for p in history + snapshots if p.realized_pnl is not None]
        require(all(value.currency == USDT for value in pnl), "unexpected native PnL currency")
        realized += sum((value.as_decimal() for value in pnl), D(0))
        per_symbol.append({"symbol": symbol, "instrument_id": str(instrument.id),
            "source_instrument_id": f"{symbol}-PERP.BINANCE",
            "position_qty": str(qty), "orders": [type(order).to_dict(order) for order in orders],
            "order_ids": [str(order.client_order_id) for order in orders], "order_events": events,
            "fills": fills, "fees_usdt": str(sum((D(fill["commission"].split()[0]) for fill in fills), D(0))),
            "quote": type(quote).to_dict(quote) if not recovery else None,
            "mark_status": "SIMULATED_FIXTURE_QUOTE", "funding_status": "NOT_PROVEN",
            "unrealized_pnl_usdt": str(unrealized.as_decimal()) if unrealized and not recovery else "UNAVAILABLE",
            "positions": [type(p).to_dict(p) for p in history],
            "position_snapshots": [type(p).to_dict(p) for p in snapshots]})
    result = {"schema": "native_execution_observation_v1", "mode": request["mode"],
        **{key: request[key] for key in ("request_id", "request_content_sha256", "portfolio_id", "run_id")},
        "native_engine": {"name": "nautilus_trader", "version": VERSION, "node_id": str(node.trader_id)},
        "execution": {"venue": "CPWSIM", "account_source": "LOCAL_SANDBOX_NOT_PRIVATE_BINANCE",
                      "commands": engine.command_count, "registered_clients": len(engine.registered_clients),
                      "cycle_order_ids": order_ids},
        "per_symbol": per_symbol,
        "portfolio": {"native_accounts": 1, "account_id": str(account.id),
                      "account_events": [type(event).to_dict(event) for event in account.events],
                      "total_balance_usdt": str(account.balance_total(USDT).as_decimal()),
                      "available_balance_usdt": str(account.balance_free(USDT).as_decimal()),
                      "gross_exposure_usdt": str(gross), "net_exposure_usdt": str(net),
                      "realized_pnl_usdt": str(realized)},
        "risk": {"disposition": "HOLD" if recovery else "TEST_ONLY_COMPLETED",
                 "authority": HoldDecision().authority, "no_private_clients": True,
                 "no_live_orders": True, "no_resume": True},
        "evidence": {"source_fixture_sha256": request["source_fixture_sha256"]}}
    result["evidence"]["observation_sha256"] = digest(canonical(result))
    return result


def _fixture_quotes(source, instruments):
    from nautilus_trader.model.data import QuoteTick
    from nautilus_trader.model.objects import Price

    now = time.time_ns()
    quotes = {}
    for symbol, instrument in instruments.items():
        values = [D(value) for value in source["synthetic_bid_ask"][symbol]]
        require(all(value % instrument.price_increment.as_decimal() == 0 for value in values),
                "fixture price increment mismatch")
        bid, ask = (Price(value, instrument.price_precision) for value in values)
        require([bid.as_decimal(), ask.as_decimal()] == values, "fixture quote would round")
        size = instrument.make_qty(100)
        quotes[symbol] = QuoteTick(instrument.id, bid, ask, size, size, now, now)
    return quotes


async def run_portfolio(cycles, source, *, recovery=False):
    from src.execution.nautilus_portfolio_contract import check_time, order_id, profile

    require(importlib.metadata.version("nautilus-trader") == VERSION, "unverified native version")
    from nautilus_trader.config import StrategyConfig
    from nautilus_trader.model.currencies import USDT
    from nautilus_trader.model.enums import OrderSide
    from nautilus_trader.model.identifiers import ClientOrderId
    from nautilus_trader.trading.strategy import Strategy

    first, universe, _, _ = cycles[0]
    sources = await _portfolio_instruments(source, sorted(universe))
    instruments = {symbol: pair[1] for symbol, pair in sources.items()}
    node = _node(profile(first), recovery=recovery, portfolio=True)
    cache, engine = node.kernel.cache, node.kernel.exec_engine
    task = None
    try:
        if recovery:
            return [_recover_portfolio(node, cycles, source, instruments)]
        for native, local in sources.values():
            cache.add_instrument(native)
            cache.add_instrument(local)
        sandbox, = engine._clients.values()
        strategy = Strategy(StrategyConfig(strategy_id="CPWPORTFOLIO-001"))
        node.trader.add_strategy(strategy)
        task = asyncio.create_task(node.run_async())
        observations = []
        async with asyncio.timeout(40):
            while not strategy.is_running:
                if task.done():
                    await task
                    raise ValueError("P1 HOLD: native node did not start")
                await asyncio.sleep(.01)
            for request, targets, order_cap, gross_cap in cycles:
                check_time(request)
                quotes = _fixture_quotes(source, instruments)
                current = _native_quantities(cache, instruments)
                accounts = cache.accounts()
                require(len(accounts) == 1 and len(engine.registered_clients) == 1,
                        "unexpected native ownership")
                account = accounts[0]
                require(not cache.orders_open() and not cache.orders_inflight() and cache.check_integrity(),
                        "unsettled native cache; HOLD")
                plan = _portfolio_plan(instruments, quotes, current, targets, order_cap, gross_cap,
                                       account.balance_free(USDT).as_decimal())
                require(all(cache.order(ClientOrderId(order_id(request, symbol))) is None
                            for symbol, _ in plan), "native order ID collision; HOLD")
                for tick in quotes.values():
                    sandbox.test_clock.set_time(tick.ts_init)
                    cache.add_quote_tick(tick)
                    strategy.portfolio.update_quote_tick(tick)
                    sandbox.on_data(tick)
                ids = []
                for symbol, delta in plan:
                    check_time(request)
                    require(_native_quantities(cache, instruments) == current and cache.check_integrity(),
                            "native cache discrepancy; HOLD")
                    remaining = _portfolio_plan(instruments, quotes, current, targets, order_cap, gross_cap,
                                                account.balance_free(USDT).as_decimal())
                    require(remaining and remaining[0] == (symbol, delta), "native risk state changed; HOLD")
                    instrument = instruments[symbol]
                    leverage = account.leverage(instrument.id)
                    require((account.default_leverage if leverage is None else leverage) == D(1),
                            "native leverage mismatch")
                    identifier = ClientOrderId(order_id(request, symbol))
                    order = strategy.order_factory.market(
                        instrument.id, OrderSide.BUY if delta > 0 else OrderSide.SELL,
                        instrument.make_qty(abs(delta)), client_order_id=identifier,
                        reduce_only=abs(targets[symbol]) < abs(current[symbol]))
                    strategy.submit_order(order)
                    try:
                        async with asyncio.timeout(2):
                            while not order.is_closed and not order.filled_qty.as_decimal():
                                await asyncio.sleep(.01)
                    except TimeoutError as exc:
                        raise ValueError("missing native acknowledgement or fill; HOLD") from exc
                    require(cache.order(identifier) is order and order.status.name == "FILLED"
                            and order.filled_qty.as_decimal() == abs(delta)
                            and not cache.orders_open() and not cache.orders_inflight(),
                            "missing, partial or rejected native fill; HOLD")
                    current[symbol] = targets[symbol]
                    require(_native_quantities(cache, instruments) == current, "native fill position discrepancy")
                    ids.append(str(identifier))
                observations.append(_portfolio_observation(node, request, instruments, quotes, ids))
        return observations
    finally:
        try:
            if task is not None:
                await node.stop_async()
                await asyncio.wait_for(task, 5)
        finally:
            node.kernel.dispose()


def _recover_portfolio(node, cycles, source, instruments):
    from src.execution.nautilus_portfolio_contract import order_id

    cache, engine = node.kernel.cache, node.kernel.exec_engine
    require(not engine.registered_clients and engine.command_count == engine.event_count == 0,
            "recovery cannot execute")
    require(cache.check_integrity() and not cache.orders_open() and not cache.orders_inflight(),
            "unsettled native recovery; HOLD")
    expected = {}
    current = dict.fromkeys(instruments, D(0))
    position_orders = {symbol: [] for symbol in instruments}
    for request, targets, _, _ in cycles:
        for symbol in instruments:
            delta = targets[symbol] - current[symbol]
            if delta:
                identifier = order_id(request, symbol)
                require(not position_orders[symbol] or (current[symbol] and not targets[symbol]),
                        "unsupported resized or reopened native position history; HOLD")
                position_orders[symbol].append(identifier)
                expected[identifier] = (instruments[symbol].id, delta)
        current = targets
    orders = {str(order.client_order_id): order for order in cache.orders()}
    require(orders and orders.keys() == expected.keys() and _native_quantities(cache, instruments) == current,
            "incomplete native orders or positions; HOLD")
    from nautilus_trader.model.events import OrderFilled

    require(all(sum(isinstance(event, OrderFilled) for event in order.events) == 1
                and len({event.id for event in order.events}) == len(order.events)
                and order.status.name == "FILLED" and order.order_type.name == "MARKET"
                and order.instrument_id == expected[key][0]
                and order.filled_qty.as_decimal() * (1 if order.side.name == "BUY" else -1) == expected[key][1]
                for key, order in orders.items()), "incomplete native fill lineage; HOLD")
    positions = cache.positions()
    require(len(positions) == sum(bool(ids) for ids in position_orders.values())
            and not cache.position_snapshots(), "incomplete native position history; HOLD")
    for symbol, ids in position_orders.items():
        matches = [p for p in positions if p.instrument_id == instruments[symbol].id]
        require(len(matches) == bool(ids), "missing native position stream; HOLD")
        if ids:
            position = matches[0]
            require(str(position.opening_order_id) == ids[0] and
                    (len(ids) == 1 and position.closing_order_id is None or
                     len(ids) == 2 and str(position.closing_order_id) == ids[1]),
                    "incomplete native position lineage; HOLD")
    accounts = cache.accounts()
    require(len(accounts) == 1 and len(accounts[0].events) == 1 + len(orders)
            and len({event.id for event in accounts[0].events}) == 1 + len(orders),
            "missing or duplicate native account events; HOLD")
    return _portfolio_observation(node, cycles[-1][0], instruments, _fixture_quotes(source, instruments), [],
                                  recovery=True)
