"""Bounded N3-02 public native-data proof; never a CPW feed or trading authority."""
from __future__ import annotations

import argparse
import asyncio
from contextlib import contextmanager
from decimal import Decimal
import hashlib
import importlib.metadata
import inspect
import json
import os
from pathlib import Path
import platform
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
NATIVE_ID = "BTCUSDT-PERP.BINANCE"
NO_AUTHORITY = "NO_NEW_ORDERS / NO_RESUME / NOT_PAPER_OR_LIVE_READY"
REST = "https://fapi.binance.com"
MARK_WS = "wss://fstream.binance.com/market"
QUOTE_WS = "wss://fstream.binance.com/public"


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def write_receipt(output, name, value):
    with (output / name).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def positive(value):
    result = Decimal(str(value))
    require(result.is_finite() and result > 0, "nonfinite/nonpositive price or filter")
    return result


def instrument_projection(instrument):
    from nautilus_trader.model.instruments import CryptoPerpetual

    require(isinstance(instrument, CryptoPerpetual), "not native CryptoPerpetual")
    info = instrument.info
    require(str(instrument.id) == NATIVE_ID and not instrument.is_inverse, "wrong instrument")
    require(all(info.get(k) == v for k, v in {
        "symbol": "BTCUSDT", "baseAsset": "BTC", "quoteAsset": "USDT",
        "marginAsset": "USDT", "contractType": "PERPETUAL", "status": "TRADING",
    }.items()), "wrong market/status")
    filters = {name: str(getattr(instrument, name)) for name in
               ("price_increment", "size_increment", "min_quantity")}
    for value in filters.values():
        positive(value)
    if instrument.min_notional is not None:
        positive(instrument.min_notional.as_decimal())
    return {"native_type": type(instrument).__module__ + "." + type(instrument).__name__,
            "id": str(instrument.id), "info": info, "filters": filters,
            "min_notional": str(instrument.min_notional), "ts_event": instrument.ts_event,
            "ts_init": instrument.ts_init, "input_hash": digest(info)}


def observation_projection(data, now_ns):
    from nautilus_trader.adapters.binance.futures.types import BinanceFuturesMarkPriceUpdate
    from nautilus_trader.model.data import CustomData, QuoteTick

    if isinstance(data, CustomData):
        data = data.data
    if not isinstance(data, (QuoteTick, BinanceFuturesMarkPriceUpdate)):
        return None
    require(str(data.instrument_id) == NATIVE_ID, "wrong observation identity")
    require(0 < data.ts_event <= now_ns + 1_000_000_000, "absent/future timestamp")
    require(now_ns - data.ts_event <= 10_000_000_000, "stale observation")
    require(data.ts_event - 1_000_000_000 <= data.ts_init <= now_ns + 1_000_000_000,
            "inconsistent initialization timestamp")
    row = {"kind": "quote" if isinstance(data, QuoteTick) else "mark",
           "native_type": type(data).__module__ + "." + type(data).__name__,
           "instrument_id": str(data.instrument_id), "ts_event": data.ts_event,
           "ts_init": data.ts_init}
    if isinstance(data, QuoteTick):
        bid, ask = positive(data.bid_price), positive(data.ask_price)
        require(bid <= ask, "crossed quote")
        positive(data.bid_size)
        positive(data.ask_size)
        row.update(bid=str(data.bid_price), ask=str(data.ask_price),
                   bid_size=str(data.bid_size), ask_size=str(data.ask_size))
    else:
        positive(data.mark)
        positive(data.index)
        require(data.funding_rate.is_finite(), "nonfinite funding rate")
        require(data.ts_event < data.next_funding_ns <= data.ts_event + 86_400_000_000_000,
                "missing/invalid next funding timestamp")
        row.update(mark=str(data.mark), index=str(data.index),
                   funding_rate=str(data.funding_rate), next_funding_ns=data.next_funding_ns)
    # Initialization time is local metadata, not a distinct source observation.
    row["source_hash"] = digest({k: v for k, v in row.items() if k != "ts_init"})
    return row


def unchanged_filters(before, after):
    require(before["filters"] == after["filters"] and
            before["min_notional"] == after["min_notional"], "instrument filters changed during proof")


class Observations:
    def __init__(self):
        self.latest = {}
        self.counts = {"quote": 0, "mark": 0}
        self.error = None

    def accept(self, data, now_ns):
        row = observation_projection(data, now_ns)
        if row is None:
            return False
        previous = self.latest.get(row["kind"])
        if previous:
            require(row["ts_event"] >= previous["ts_event"], "out-of-order observation")
            if row["source_hash"] == previous["source_hash"]:
                return False
            require(row["ts_event"] - previous["ts_event"] <= 15_000_000_000,
                    "observation gap exceeds proof tolerance")
        self.latest[row["kind"]] = row
        self.counts[row["kind"]] += 1
        return True

    def receive(self, data):
        try:
            self.accept(data, time.time_ns())
        except (ValueError, ArithmeticError) as exc:
            self.error = str(exc)

    def fresh(self):
        require(not self.error, self.error)
        return (set(self.latest) == {"quote", "mark"} and
                all(0 <= time.time_ns() - r["ts_event"] <= 10_000_000_000
                    for r in self.latest.values()))


def verify_reconnect(before, after, lifecycle, transport):
    require(before["pid"] == after["pid"] and before["native_client"] == after["native_client"],
            "process/native client replaced")
    require(transport["method"] in {"ss-K", "docker-network"} and transport["closed"] is True,
            "transport close unproven")
    require(transport["old_socket"] != transport["new_socket"], "socket not replaced")
    require(transport["pid"] == before["pid"], "wrong socket process")
    events = {r["event"]: r["time_ns"] for r in lifecycle}
    require(transport["injected_ns"] < events.get("native_callback", 0)
            <= events.get("native_resubscribe", 0) < after["observed_ns"],
            "native reconnect/resubscribe ordering unproven")
    for kind in ("quote", "mark"):
        require(after[kind]["ts_event"] > before[kind]["ts_event"]
                and after[kind]["source_hash"] != before[kind]["source_hash"],
                "no fresh unique post-reconnect observation")
    require(after["quote"]["ts_event"] > events["native_callback"],
            "post-reconnect quote predates callback")
    return NO_AUTHORITY


async def wait_until(predicate, seconds, observations=None):
    async with asyncio.timeout(seconds):
        while not predicate():
            if observations:
                require(not observations.error, observations.error)
            await asyncio.sleep(0.25)


@contextmanager
def native_lifecycle(client, observations, lifecycle):
    """Observe two unchanged native functions, including calls from Rust workers."""
    from nautilus_trader.adapters.binance.websocket.client import BinanceWebSocketClient

    ws = client._ws_public_client
    codes = (BinanceWebSocketClient._handle_reconnect.__code__, BinanceWebSocketClient._send.__code__)
    monitor = sys.monitoring
    monitor.use_tool_id(5, "N3-02-readonly-observer")

    def started(code, offset):
        frame = sys._getframe(1)
        owner = frame.f_locals.get("self")
        if owner is not ws and owner is not client._ws_client:
            return
        quote = owner is ws
        label = None
        if code is codes[0]:
            # The native callback invalidates the sample across the known transport gap.
            observations.latest.pop("quote" if quote else "mark", None)
            label = "native_callback" if quote else "native_callback_mark"
        elif quote and frame.f_locals.get("msg", {}).get("method") == "SUBSCRIBE":
            label = "native_resubscribe"
        if label and len(lifecycle) < 32:
            lifecycle.append({"event": label, "time_ns": time.time_ns(), "wrapper_id": id(owner),
                              "thread_id": threading.get_ident(),
                              "function": code.co_filename + ":" + code.co_name})

    try:
        monitor.register_callback(5, monitor.events.PY_START, started)
        for code in codes:
            monitor.set_local_events(5, code, monitor.events.PY_START)
        yield
    finally:
        for code in codes:
            monitor.set_local_events(5, code, 0)
        monitor.register_callback(5, monitor.events.PY_START, None)
        monitor.free_tool_id(5)


async def run(output, receipt):
    from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
    from nautilus_trader.adapters.binance.config import BinanceDataClientConfig, BinanceInstrumentProviderConfig
    from nautilus_trader.adapters.binance.futures.data import BinanceFuturesDataClient
    from nautilus_trader.adapters.binance.futures.providers import BinanceFuturesInstrumentProvider
    from nautilus_trader.adapters.binance.http.client import BinanceHttpClient
    from nautilus_trader.cache.cache import Cache
    from nautilus_trader.common.component import LiveClock, MessageBus, init_logging
    from nautilus_trader.common.enums import LogLevel
    from nautilus_trader.core.nautilus_pyo3 import HttpMethod
    from nautilus_trader.core.uuid import UUID4
    from nautilus_trader.data.messages import SubscribeMarkPrices, SubscribeQuoteTicks
    from nautilus_trader.model.identifiers import InstrumentId, TraderId

    class PublicHttp(BinanceHttpClient):
        async def send_request(self, http_method, url_path, payload=None, ratelimiter_keys=None):
            require(http_method == HttpMethod.GET and url_path == "/fapi/v1/exchangeInfo"
                    and not payload, "non-allowlisted public GET")
            receipt["requests"].append({"method": "GET", "url": REST + url_path})
            return await super().send_request(http_method, url_path, payload, ratelimiter_keys)

        async def sign_request(self, *args, **kwargs):
            raise ValueError("signed requests forbidden")

    clock = LiveClock()
    log_guard = init_logging(level_stdout=LogLevel.DEBUG, colors=False)
    http = PublicHttp(clock, None, None, REST)
    instrument_id = InstrumentId.from_str(NATIVE_ID)
    provider_config = BinanceInstrumentProviderConfig(load_ids=frozenset({instrument_id}))
    provider = BinanceFuturesInstrumentProvider(http, clock, config=provider_config)
    bus = MessageBus(TraderId("N3PROOF-001"), clock)
    observations = Observations()
    bus.register("DataEngine.process", observations.receive)
    client = BinanceFuturesDataClient(
        asyncio.get_running_loop(), http, bus, Cache(), clock, provider, MARK_WS,
        BinanceDataClientConfig(account_type=BinanceAccountType.USDT_FUTURES,
                                instrument_provider=provider_config,
                                update_instruments_interval_mins=None),
        base_url_ws_public=QUOTE_WS,
    )
    ws = client._ws_public_client
    lifecycle = receipt["lifecycle"]
    try:
        with native_lifecycle(client, observations, lifecycle):
            await asyncio.wait_for(client._connect(), 30)
            receipt["instrument"] = instrument_projection(provider.find(instrument_id))
            write_receipt(output, "instrument-ready.json", receipt["instrument"])
            await wait_until(lambda: (output / "rest-sockets-recorded.json").exists(), 15)
            command = (instrument_id, None, instrument_id.venue, UUID4(), clock.timestamp_ns())
            await asyncio.wait_for(client._subscribe_quote_ticks(SubscribeQuoteTicks(*command)), 20)
            await wait_until(lambda: "quote" in observations.latest, 15, observations)
            native = ws._clients[0]
            identity = {"pid": os.getpid(), "native_client": id(native), "wrapper": id(ws)}
            write_receipt(output, "quote-ready.json", identity)
            await wait_until(lambda: (output / "quote-socket.json").exists(), 15)
            await asyncio.wait_for(client._subscribe_mark_prices(SubscribeMarkPrices(*command)), 20)
            await wait_until(observations.fresh, 15, observations)
            before = {**identity, **observations.latest, "observed_ns": time.time_ns()}
            receipt["before"] = before
            write_receipt(output, "inject-ready.json", before)
            await wait_until(lambda: any(e["event"] == "native_callback" for e in lifecycle), 85, observations)
            callback_ns = next(e["time_ns"] for e in lifecycle if e["event"] == "native_callback")
            await wait_until(lambda: observations.fresh() and all(
                observations.latest[k]["ts_event"] > max(before[k]["ts_event"], callback_ns)
                for k in ("quote", "mark")), 15, observations)
            require(ws._clients[0] is native and native.is_active(), "native client identity/state changed")
            after = {**identity, **observations.latest, "observed_ns": time.time_ns()}
            receipt["after"] = after
            write_receipt(output, "after-ready.json", after)
            await wait_until(lambda: (output / "transport.json").exists(), 10)
            transport = json.loads((output / "transport.json").read_text())
            verify_reconnect(before, after, lifecycle, transport)
            # The external network fault also invalidates the old idle REST connection pool.
            snapshot_provider = BinanceFuturesInstrumentProvider(
                PublicHttp(clock, None, None, REST), clock, config=provider_config)
            await asyncio.wait_for(snapshot_provider.load_ids_async([instrument_id]), 30)
            receipt["instrument_after"] = instrument_projection(snapshot_provider.find(instrument_id))
            unchanged_filters(receipt["instrument"], receipt["instrument_after"])
            receipt.update(transport=transport, counts=observations.counts, result="N3_02_PUBLIC_FEED_RECONNECT_PASSED")
    finally:
        await asyncio.wait_for(client._disconnect(), 5)
        receipt["cleanup"] = "native data clients disconnected"
        del log_guard


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-readonly-proof", action="store_true", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    require(output.is_dir() and not output.is_relative_to(ROOT), "existing external output directory required")
    require(not any(output.iterdir()), "output directory must be empty")
    receipt = {"result": "N3_02_PUBLIC_FEED_RECONNECT_UNPROVEN", "authority": NO_AUTHORITY,
               "pid": os.getpid(), "started_ns": time.time_ns(), "requests": [], "lifecycle": [],
               "endpoints": {"REST_GET": REST + "/fapi/v1/exchangeInfo",
                             "quote_subscription": QUOTE_WS + "/stream?streams=btcusdt@bookTicker",
                             "mark_subscription": MARK_WS + "/stream?streams=btcusdt@markPrice@1s"}}
    try:
        require(platform.system() == "Linux" and platform.python_version() == "3.12.10", "exact Linux Python pin required")
        pins = dict(line.split("==") for line in (ROOT / "tools/nautilus_adapter/requirements-win-py312.lock.txt").read_text().splitlines() if "==" in line)
        receipt["versions"] = {name: importlib.metadata.version(name) for name in pins}
        require(receipt["versions"] == pins and importlib.metadata.version("uvloop") == "0.22.1", "package pin mismatch")
        import nautilus_trader
        import nautilus_trader.core.nautilus_pyo3 as native_core
        package = Path(nautilus_trader.__file__).parent
        with Path(native_core.__file__).open("rb") as stream:
            receipt["runtime"] = {"python": platform.python_version(), "platform": platform.platform(),
                                  "uvloop": importlib.metadata.version("uvloop"),
                                  "native_module": native_core.__file__,
                                  "native_module_sha256": hashlib.file_digest(stream, "sha256").hexdigest()}
        receipt["source_hashes"] = {str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in (package / "adapters/binance").rglob("*.py")}
        receipt["probe_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        from nautilus_trader.adapters.binance.futures.data import BinanceFuturesDataClient
        receipt["constructor"] = str(inspect.signature(BinanceFuturesDataClient))

        async def bounded():
            async with asyncio.timeout(170):
                await run(output, receipt)
        asyncio.run(bounded())
    except Exception as exc:
        receipt.update(result="N3_02_PUBLIC_FEED_RECONNECT_UNPROVEN", error=f"{type(exc).__name__}: {exc}")
    receipt["finished_ns"] = time.time_ns()
    write_receipt(output, "receipt.json", receipt)
    return 0 if receipt["result"].endswith("PASSED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
