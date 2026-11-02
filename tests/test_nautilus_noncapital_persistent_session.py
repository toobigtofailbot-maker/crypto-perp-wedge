"""Native single-cycle objects, independent economics and fail-closed checkpoints."""
import asyncio
import copy
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path

import pytest

from tools.nautilus_adapter import noncapital_persistent_proof as controller
from tools.nautilus_adapter import noncapital_persistent_session as p


def source():
    from nautilus_trader.model.instruments import CryptoPerpetual

    from tools.nautilus_adapter import binance_usdm_offline_reports as prior
    _, _, objects = prior.parse_tape(prior.load_fixture(prior.FIXTURE))
    result = CryptoPerpetual.to_dict(objects[0])
    result["info"]["filters"].append({"filterType": "MARKET_LOT_SIZE", "minQty": ".001", "maxQty": "120", "stepSize": ".001"})
    return result


def tick():
    from nautilus_trader.model.data import QuoteTick
    from nautilus_trader.model.identifiers import InstrumentId
    from nautilus_trader.model.objects import Price, Quantity
    now = time.time_ns()
    return QuoteTick(InstrumentId.from_str(p.public.n3.NATIVE_ID), Price.from_str("80000.00"),
        Price.from_str("80000.10"), Quantity.from_str("1.000"), Quantity.from_str("1.000"), now, now)


@pytest.fixture(params=["open", "flat"])
def native_state(tmp_path, request):
    async def run():
        from nautilus_trader.common.factories import OrderFactory
        from nautilus_trader.core.uuid import UUID4
        from nautilus_trader.execution.messages import SubmitOrder
        from nautilus_trader.model.data import QuoteTick
        from nautilus_trader.model.enums import OrderSide
        from nautilus_trader.model.identifiers import StrategyId
        from nautilus_trader.model.instruments import CryptoPerpetual
        from nautilus_trader.model.objects import Quantity
        instrument = source()
        trader = "N2R" + uuid.uuid4().hex[:12] + "-001"
        native = p.node(trader, producer=True)
        cache, engine = native.kernel.cache, native.kernel.exec_engine
        local = CryptoPerpetual.from_dict(p.public.local_spec(instrument))
        cache.add_instrument(local)
        client = next(iter(engine._clients.values()))
        strategy = StrategyId("PROOF-001")
        factory = OrderFactory(native.trader_id, strategy, client.test_clock)
        engine.start()
        client.connect()
        await p.settle(engine, lambda: bool(cache.accounts()))
        quotes = []
        try:
            for i in range(1 if request.param == "open" else 2):
                q = tick()
                quotes.append({**p.public.n3.observation_projection(q, time.time_ns()), "observed_ns": time.time_ns()})
                local_tick = QuoteTick(local.id, q.bid_price, q.ask_price, q.bid_size, q.ask_size, q.ts_event, q.ts_init)
                client.test_clock.set_time(q.ts_init)
                cache.add_quote_tick(local_tick)
                native.kernel.portfolio.update_quote_tick(local_tick)
                client.on_data(local_tick)
                order = factory.market(local.id, OrderSide.BUY if i == 0 else OrderSide.SELL, Quantity.from_str("0.001"))
                engine.execute(SubmitOrder(native.trader_id, strategy, order, UUID4(), q.ts_init))
                await p.settle(engine, lambda order=order: order.is_closed)
            before = p.projection(native)
            fill = next(e for e in order.events if type(e).__name__ == "OrderFilled")
            engine.process(fill)
            await p.settle(engine, lambda: True)
            from nautilus_trader.model.events import OrderFilled
            conflict = OrderFilled.to_dict(fill)
            conflict["commission"] = "1.00000000 USDT"
            engine.process(OrderFilled.from_dict(conflict))
            await p.settle(engine, lambda: True)
            assert p.projection(native) == before, "genuine native duplicate/conflicting trade changed economics"
            return p.projection(native), trader, request.param, quotes, instrument
        finally:
            client.disconnect()
            engine.stop()
            await asyncio.sleep(.05)
            cache.dispose()
    return asyncio.run(run())


def test_true_native_single_cycle_economics(native_state):
    state, trader, case, quotes, _ = native_state
    assert p.validate(state, trader, case, quotes)["fills"] == (1 if case == "open" else 2)


@pytest.mark.parametrize("mutation", ["balance", "fees", "trade", "account", "position", "pending", "quote", "history"])
def test_corrupted_native_financial_or_identity_projection_refuses(native_state, mutation):
    state, trader, case, quotes, _ = copy.deepcopy(native_state)
    orders = state["native"]["orders"]
    order = next(iter(orders.values()))
    fill = next(e for e in order["events"] if e["type"] == "OrderFilled")
    if mutation == "balance":
        state["balance"] = "10000"
    elif mutation == "fees":
        fill["commission"] = "0 USDT"
    elif mutation == "trade":
        order["events"].append(copy.deepcopy(fill))
    elif mutation == "account":
        fill["account_id"] = "OTHER-001"
    elif mutation == "position":
        next(iter(state["native"]["positions"].values()))["state"]["signed_qty"] = 2
    elif mutation == "pending":
        order["state"] = "PARTIALLY_FILLED"
    elif mutation == "quote":
        quotes[0]["ask"] = "90000.00"
    else:
        state["snapshots"] = [{"missing_native_history": True}]
    with pytest.raises(ValueError):
        p.validate(state, trader, case, quotes)


@pytest.mark.parametrize("case", ["open", "flat"])
def test_manifest_does_not_create_a_native_positive(tmp_path, case):
    result = subprocess.run([sys.executable, "-B", "-m", "tools.nautilus_adapter.noncapital_persistent_session",
        "restore", "--proof-only", "--output", str(tmp_path), "--expected-manifest-sha256", "0" * 64],
        capture_output=True, text=True, timeout=20, check=False)
    assert result.returncode == 1
    assert json.loads(result.stdout.splitlines()[-1])["status"] == "BLOCKED"
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("argv", [[], ["restore"], ["produce"], ["resume"],
    ["restore", "--proof-only", "--output", "/tmp/no", "--case", "open", "--expected-manifest-sha256", "0" * 64],
    ["produce", "--proof-only", "--output", "/tmp/no", "--venue", "BINANCE"]])
def test_no_implicit_execution_or_resume(argv):
    result = subprocess.run([sys.executable, "-B", "-m", "tools.nautilus_adapter.noncapital_persistent_session", *argv],
                            capture_output=True, text=True, timeout=20, check=False)
    assert result.returncode != 0


def test_output_and_controller_refuse_repository(tmp_path):
    with pytest.raises(ValueError):
        p.output_root(p.public.n3.ROOT)
    (tmp_path / "already-owned").write_text("retain")
    with pytest.raises(ValueError):
        controller.Controller(tmp_path)
    assert (tmp_path / "already-owned").read_text() == "retain"


def test_unsupported_economic_shape_is_never_admitted():
    with pytest.raises(ValueError, match="MULTICYCLE_NATIVE_HISTORY_UNSUPPORTED_PINNED"):
        p.validate({}, "N2R040200000001-001", "reversal", [])


def test_checkpoint_refuses_torn_or_untrusted_bytes(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_bytes(b'{"torn":')
    before = path.read_bytes()
    with pytest.raises(ValueError, match="untrusted"):
        p.checkpoint(tmp_path, "0" * 64)
    assert path.read_bytes() == before


def test_pid_numbers_from_different_namespaces_are_not_the_same_process(native_state, tmp_path):
    state, trader, case, quotes, instrument = native_state
    now = time.time_ns()
    process = p.process_identity()
    mark = {"kind": "mark", "instrument_id": p.public.n3.NATIVE_ID,
            "native_type": "nautilus_trader.adapters.binance.futures.types.BinanceFuturesMarkPriceUpdate",
            "ts_event": now, "ts_init": now, "mark": "80000", "index": "80000",
            "funding_rate": "0", "next_funding_ns": now + 60_000_000_000}
    mark["source_hash"] = p.public.n3.digest({k: v for k, v in mark.items() if k != "ts_init"})
    m = {**p.LABELS, "source": p.SOURCE, "authority": p.AUTHORITY, "pid": process["pid"],
         "process": {**process, "pid_namespace": "synthetic-different-test-namespace"}, "run_id": str(uuid.uuid4()),
         "time_ns": now, "trader": trader, "case": case, "sources": p.sources(), "environment": p.native.environment(),
         "instrument": instrument, "filter_sha256": p.digest(instrument["info"]["filters"]),
         "mark": mark, "mark_observed_ns": now, "quotes": quotes, "state": state, "records": {}, "chain": []}
    for payload in [instrument, *quotes, state, {}]:
        row = {"seq": len(m["chain"]), "previous": m["chain"][-1]["sha256"] if m["chain"] else None, "payload": payload}
        m["chain"].append({**row, "sha256": p.digest(row)})
    def write():
        (tmp_path / "manifest.json").write_bytes(p.encoded(m))
        trusted = p.public.file_hash(tmp_path / "manifest.json")
        (tmp_path / "ack.json").write_bytes(p.encoded({**p.LABELS, "pid": m["pid"], "run_id": m["run_id"], "sha256": trusted}))
        return trusted
    assert p.checkpoint(tmp_path, write())["process"] != process
    m["process"] = process
    with pytest.raises(ValueError, match="nonfresh process"):
        p.checkpoint(tmp_path, write())


def test_network_account_and_transport_surface_is_closed():
    text = Path(p.__file__).read_text()
    assert "BinanceExecutionClient" not in text and "os.environ" not in text
    assert "SandboxLiveExecClientFactory" in text
    assert 'choices=("produce", "restore")' in text
    assert 'host="127.0.0.1", port=6379' in text


def test_callback_delay_waits_for_fresh_native_quote_before_latching():
    async def run():
        from nautilus_trader.model.data import QuoteTick
        q = tick()
        feed = p.public.Feed()
        feed.tick = QuoteTick(q.instrument_id, q.bid_price, q.ask_price, q.bid_size, q.ask_size,
                              q.ts_event - 6_000_000_000, q.ts_init - 6_000_000_000)
        async def receive():
            await asyncio.sleep(.02)
            feed.tick = tick()
        task = asyncio.create_task(receive())
        await p.fresh_quote(feed)
        await task
        assert not feed.stopped and time.time_ns() - feed.tick.ts_event < 5_000_000_000
    asyncio.run(run())
