import pytest

from tools.data_ingestion.m1_public_source_probe import (
    FundingIngestError,
    fetch_public_probe,
)


START = 1577836800000
END = START + 57_600_000
STEPS = {"15m": 900_000, "1h": 3_600_000}


class Exchange:
    def __init__(self, symbol):
        self.calls = []
        self.market = {
            "symbol": symbol,
            "pair": symbol,
            "contractType": "PERPETUAL",
            "status": "TRADING",
            "quoteAsset": "USDT",
            "marginAsset": "USDT",
            "onboardDate": START - 1,
            "deliveryDate": END + 1,
        }
        self.candles = {
            clock: [
                [ts, "1", "3", "0.5", "2", "5", ts + step - 1, "7", 2, "1", "2", "0"]
                for ts in range(START, END, step)
            ]
            for clock, step in STEPS.items()
        }
        self.events = [
            {"symbol": symbol, "fundingTime": START + 2, "fundingRate": "-0.0001"},
            {"symbol": symbol, "fundingTime": START + 28_800_002, "fundingRate": "0.0002"},
        ]

    def fapiPublicGetKlines(self, params):
        self.calls.append(params)
        return self.candles[params["interval"]]

    def fapiPublicGetFundingRate(self, params):
        self.calls.append(params)
        return self.events

    def probe(self, symbol="ETHUSDT"):
        return fetch_public_probe(
            self, exchange_info={"symbols": [self.market]}, symbol=symbol, start_ms=START, end_ms=END
        )


@pytest.mark.parametrize("symbol", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
def test_bounded_probe_uses_same_public_calls_for_each_symbol(symbol):
    exchange = Exchange(symbol)
    result = exchange.probe(symbol)
    assert {clock: len(rows) for clock, rows in result["klines"].items()} == {"15m": 64, "1h": 16}
    assert [event["symbol"] for event in result["funding_events"]] == [symbol, symbol]
    assert result["funding_events"][0]["exchange_funding_time_ms"] == START + 2
    assert result["funding_events"][0]["funding_rate"] == "-0.0001"
    assert [call.get("interval") for call in exchange.calls] == ["15m", "1h", None]
    assert all(call["symbol"] == symbol and call["endTime"] == END - 1 for call in exchange.calls)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("symbol", "BTCUSDT"),
        ("status", "CLOSE"),
        ("contractType", "CURRENT_QUARTER"),
        ("marginAsset", "USDC"),
        ("onboardDate", START + 1),
        ("deliveryDate", END - 1),
    ],
)
def test_ineligible_instrument_stops_before_history_fetch(field, value):
    exchange = Exchange("ETHUSDT")
    exchange.market[field] = value
    with pytest.raises(FundingIngestError):
        exchange.probe()
    assert exchange.calls == []


@pytest.mark.parametrize("bad_input", ["missing", "duplicate", "clock", "nan"])
def test_bad_bar_fails_before_funding(bad_input):
    exchange = Exchange("ETHUSDT")
    if bad_input == "missing":
        exchange.candles["1h"].pop()
    elif bad_input == "duplicate":
        exchange.candles["1h"][1] = exchange.candles["1h"][0]
    elif bad_input == "clock":
        exchange.candles["1h"][0] = exchange.candles["15m"][0]
    else:
        exchange.candles["1h"][0][4] = "NaN"
    with pytest.raises(FundingIngestError, match="1h"):
        exchange.probe()
    assert len(exchange.calls) == 2


@pytest.mark.parametrize(
    "mutation",
    [
        {"symbol": "BTCUSDT"},
        {"fundingTime": START},
        {"fundingTime": END},
        {"fundingRate": "NaN"},
        {"markPrice": "0"},
    ],
)
def test_bad_funding_is_rejected(mutation):
    exchange = Exchange("ETHUSDT")
    exchange.events[-1].update(mutation)
    with pytest.raises(FundingIngestError):
        exchange.probe()


@pytest.mark.parametrize("mutation", ["symbol", "clock", "rate", "gap", "offset"])
def test_full_public_coverage_refuses_cross_cell_or_corrupt_source(mutation):
    from tools.data_ingestion.m1_public_source_probe import validate_public_coverage

    result = Exchange("ETHUSDT").probe()
    inputs = {
        "symbol": "ETHUSDT", "clock": "15m", "start_ms": START, "end_ms": END,
        "klines": result["klines"]["15m"], "funding": result["funding_events"],
    }
    assert validate_public_coverage(**inputs) == {
        "bars": 64, "funding_events": 2, "missing_settlement_marks": 2,
        "nonzero_settlement_offsets": 2,
    }
    if mutation == "symbol":
        inputs["symbol"] = "BTCUSDT"
    elif mutation == "clock":
        inputs["clock"] = "1h"
    elif mutation == "rate":
        inputs["funding"][0]["funding_rate"] = "NaN"
    elif mutation == "gap":
        inputs["klines"].pop()
    else:
        inputs["funding"][0]["exchange_funding_time_offset_ms"] = 0
    with pytest.raises(FundingIngestError):
        validate_public_coverage(**inputs)
