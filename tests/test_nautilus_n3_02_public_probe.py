"""Native-domain assertions and fixed offline refusal cases; never connect to Binance."""
import ast
import asyncio
import copy
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import threading
from types import SimpleNamespace

import pytest

from tools.nautilus_adapter import binance_usdm_public_probe as proof

FIXTURE = Path(__file__).parent / "fixtures/nautilus_n3_02/public_feed_invalid_cases.json"
CASES = json.loads(FIXTURE.read_text())["cases"]
NOW = 1700000000000000000


def native(kind, **changes):
    from nautilus_trader.adapters.binance.futures.types import BinanceFuturesMarkPriceUpdate
    from nautilus_trader.model.data import QuoteTick
    from nautilus_trader.model.identifiers import InstrumentId
    from nautilus_trader.model.objects import Price, Quantity

    values = {"instrument_id": proof.NATIVE_ID, "bid": "60000.00", "ask": "60000.10",
              "mark": "60000.05", "index": "60000.01", "funding_rate": "0.0001",
              "next_funding_ns": NOW + 3600_000_000_000, "ts_event": NOW, "ts_init": NOW}
    values.update(changes)
    ident = InstrumentId.from_str(values["instrument_id"])
    if kind == "quote":
        return QuoteTick(ident, Price.from_str(values["bid"]), Price.from_str(values["ask"]),
                         Quantity.from_str("1.000"), Quantity.from_str("2.000"),
                         values["ts_event"], values["ts_init"])
    return BinanceFuturesMarkPriceUpdate(
        ident, Price.from_str(values["mark"]), Price.from_str(values["index"]), Price.from_str("0"),
        Decimal(values["funding_rate"]), values["next_funding_ns"], values["ts_event"], values["ts_init"])


@pytest.fixture(scope="module")
def instrument(tmp_path_factory):
    from tools.nautilus_adapter import binance_usdm_offline_reports as previous
    with previous.safety_boundary(tmp_path_factory.mktemp("offline-native")):
        _, _, objects = previous.parse_tape(previous.load_fixture(previous.FIXTURE))
    return objects[0]


def test_positive_native_types_values_and_units(instrument):
    result = proof.instrument_projection(instrument)
    assert result["native_type"].endswith("CryptoPerpetual")
    assert result["id"] == proof.NATIVE_ID
    assert result["filters"] == {"price_increment": "0.10", "size_increment": "0.001", "min_quantity": "0.001"}
    quote = proof.observation_projection(native("quote"), NOW)
    mark = proof.observation_projection(native("mark"), NOW)
    assert quote["native_type"].endswith("QuoteTick")
    assert (quote["bid"], quote["ask"]) == ("60000.00", "60000.10")
    assert mark["native_type"].endswith("BinanceFuturesMarkPriceUpdate")
    assert (mark["mark"], mark["index"], mark["funding_rate"]) == ("60000.05", "60000.01", "0.0001")
    assert mark["next_funding_ns"] - NOW == 3600_000_000_000


def reconnect_receipts():
    before = {"pid": 123, "native_client": 456,
              **{k: proof.observation_projection(native(k), NOW) for k in ("quote", "mark")}}
    after_time = NOW + 2_000_000_000
    after = {"pid": 123, "native_client": 456, "observed_ns": after_time,
             **{k: proof.observation_projection(native(k, ts_event=after_time, ts_init=after_time), after_time)
                for k in ("quote", "mark")}}
    events = [{"event": "native_callback", "time_ns": NOW + 1_000_000_000},
              {"event": "native_resubscribe", "time_ns": NOW + 1_100_000_000}]
    transport = {"method": "ss-K", "closed": True, "old_socket": "synthetic-old", "new_socket": "synthetic-new",
                 "pid": 123, "injected_ns": NOW + 500_000_000}
    return before, after, events, transport


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["name"])
def test_fixed_offline_controls(case, instrument):
    target, name = case["target"], case["name"]
    if target in {"instrument", "filter"}:
        from nautilus_trader.model.instruments import CryptoPerpetual
        values = copy.deepcopy(CryptoPerpetual.to_dict(instrument))
        if target == "instrument":
            values["info"][case["field"]] = case["value"]
        else:
            values[case["field"]] = case["value"]
        with pytest.raises((ValueError, OverflowError)):
            proof.instrument_projection(CryptoPerpetual.from_dict(values))
    elif target in {"quote", "mark"}:
        # Native constructors own rejection where supported; projection closes the rest.
        with pytest.raises((ValueError, InvalidOperation, OverflowError)):
            proof.observation_projection(native(target, **{case["field"]: case["value"]}), NOW)
    elif target == "sequence":
        state = proof.Observations()
        assert state.accept(native("quote"), NOW)
        if name == "duplicate":
            assert not state.accept(native("quote", ts_init=NOW + 1), NOW + 1)
            assert state.counts["quote"] == 1
        else:
            at = NOW - 1 if name == "out_of_order" else NOW + 16_000_000_000
            with pytest.raises(ValueError, match="out-of-order|gap"):
                state.accept(native("quote", ts_event=at, ts_init=at), at)
    else:
        before, after, events, transport = reconnect_receipts()
        if name == "timeout":
            events = []
        elif name == "forged_callback":
            transport["closed"] = False
        elif name == "graceful_disconnect":
            transport["method"] = "native-disconnect"
        elif name == "new_process":
            after["pid"] += 1
        elif name == "new_client":
            after["native_client"] += 1
        elif name == "old_socket":
            transport["new_socket"] = transport["old_socket"]
        elif name == "no_fresh_data":
            after["quote"] = before["quote"]
        with pytest.raises(ValueError):
            proof.verify_reconnect(before, after, events, transport)
    assert proof.NO_AUTHORITY == "NO_NEW_ORDERS / NO_RESUME / NOT_PAPER_OR_LIVE_READY"


def test_receipt_gate_requires_all_native_and_external_evidence():
    assert proof.verify_reconnect(*reconnect_receipts()) == proof.NO_AUTHORITY


def test_changed_instrument_filters_refuse(instrument):
    before = proof.instrument_projection(instrument)
    proof.unchanged_filters(before, before)
    after = copy.deepcopy(before)
    after["filters"]["price_increment"] = "0.01"
    with pytest.raises(ValueError, match="filters changed"):
        proof.unchanged_filters(before, after)


def test_wrong_native_observation_identity():
    with pytest.raises(ValueError, match="identity"):
        proof.observation_projection(native("quote", instrument_id="ETHUSDT-PERP.BINANCE"), NOW)


def test_native_callback_observed_on_worker_and_forged_callback_still_refuses():
    import sys
    from nautilus_trader.adapters.binance.websocket.client import BinanceWebSocketClient
    from nautilus_trader.common.component import LiveClock

    loop = asyncio.new_event_loop()
    try:
        def wrapper():
            return BinanceWebSocketClient(LiveClock(), proof.QUOTE_WS, lambda raw: None, None, loop)
        client = SimpleNamespace(_ws_public_client=wrapper(), _ws_client=wrapper())
        state = proof.Observations()
        state.accept(native("quote"), NOW)
        lifecycle = []
        with proof.native_lifecycle(client, state, lifecycle):
            # A deliberate offline forged callback is a negative control, not reconnect proof.
            worker = threading.Thread(target=client._ws_public_client._handle_reconnect, args=(999,))
            worker.start()
            worker.join(timeout=2)
            assert not worker.is_alive()
        assert lifecycle[0]["event"] == "native_callback"
        assert lifecycle[0]["thread_id"] != threading.get_ident()
        assert "quote" not in state.latest
        assert sys.monitoring.get_tool(5) is None
        before, after, _, transport = reconnect_receipts()
        transport["closed"] = False
        with pytest.raises(ValueError, match="transport close unproven"):
            proof.verify_reconnect(before, after, lifecycle, transport)
    finally:
        loop.close()


def test_bounded_timeout_preserves_non_authority():
    async def bounded():
        with pytest.raises(TimeoutError):
            await proof.wait_until(lambda: False, 0.01)
    asyncio.run(bounded())
    assert "NO_RESUME" in proof.NO_AUTHORITY


def test_real_native_client_constructor_and_cleanup_without_network(monkeypatch, tmp_path):
    from nautilus_trader.adapters.binance.futures.data import BinanceFuturesDataClient
    from nautilus_trader.adapters.binance.http.client import BinanceHttpClient

    async def offline_connect(self):
        assert type(self).__name__ == "BinanceFuturesDataClient"
        assert self._http_client.api_key is None and self._http_client._secret is None
        assert self._ws_client.url == proof.MARK_WS
        assert self._ws_public_client.url == proof.QUOTE_WS
        # Exercise the real proof guard before a native HTTP request can occur.
        from nautilus_trader.core.nautilus_pyo3 import HttpMethod
        with pytest.raises(ValueError, match="non-allowlisted"):
            await self._http_client.send_request(HttpMethod.POST, "/fapi/v1/order")
        with pytest.raises(ValueError, match="signed"):
            await self._http_client.sign_request(HttpMethod.GET, "/fapi/v1/account")
        raise RuntimeError("offline constructor verified")

    async def forbidden_network(*args, **kwargs):
        pytest.fail("offline test reached a transport")

    monkeypatch.setattr(BinanceFuturesDataClient, "_connect", offline_connect)
    monkeypatch.setattr(BinanceHttpClient, "send_request", forbidden_network)
    receipt = {"lifecycle": [], "requests": []}
    with pytest.raises(RuntimeError, match="offline constructor verified"):
        asyncio.run(proof.run(tmp_path, receipt))
    assert receipt["cleanup"] == "native data clients disconnected"
    assert receipt["requests"] == []


def test_cli_requires_explicit_flag_and_external_empty_directory(tmp_path):
    with pytest.raises(SystemExit):
        proof.main(["--output", str(tmp_path)])
    with pytest.raises(ValueError, match="external"):
        proof.main(["--public-readonly-proof", "--output", str(proof.ROOT)])
    (tmp_path / "existing").touch()
    with pytest.raises(ValueError, match="empty"):
        proof.main(["--public-readonly-proof", "--output", str(tmp_path)])


def test_no_execution_or_custom_transport_or_manual_callback():
    tree = ast.parse(Path(proof.__file__).read_text())
    imports = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    assert not any(m.startswith(("src", "lib", "requests", "websockets", "subprocess")) for m in imports)
    calls = [n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
    assert not set(calls) & {"_handle_reconnect", "_resubscribe_client", "submit_order", "sign_request"}
    assert "native_callback" in Path(proof.__file__).read_text()
