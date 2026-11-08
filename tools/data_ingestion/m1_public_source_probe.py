"""Bounded Binance USD-M REST source probes for M1, without science admission."""

import re
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

from tools.data_ingestion.ccxt_public_funding_adapter import (
    FUNDING_INTERVAL_MS,
    MAX_EXCHANGE_TIMESTAMP_OFFSET_MS,
    FundingIngestError,
    normalize_raw_row,
)


SCHEMA_VERSION = "cpw_m1_public_source_probe_v1"
_BAR_MS = {"15m": 900_000, "1h": 3_600_000}


def fetch_public_probe(exchange, *, exchange_info, symbol, start_ms, end_ms):
    """Collect up to 1000 bars per clock in a UTC half-open interval.

    Exchange info is current discovery metadata. The returned probe does not
    establish uninterrupted historical listing, custody or nonholdout authority.
    """
    if not re.fullmatch(r"[A-Z0-9]+USDT", symbol):
        raise FundingIngestError("invalid USD-M symbol")
    if (
        type(start_ms) is not int
        or type(end_ms) is not int
        or not 0 < start_ms < end_ms <= int(datetime.now(UTC).timestamp() * 1000)
        or start_ms % FUNDING_INTERVAL_MS
        or end_ms % FUNDING_INTERVAL_MS
        or end_ms - start_ms > 1000 * _BAR_MS["15m"]
    ):
        raise FundingIngestError("probe must be bounded and aligned to the 8h funding grid")

    matches = [row for row in exchange_info["symbols"] if row["symbol"] == symbol]
    if len(matches) != 1:
        raise FundingIngestError("expected one current instrument record")
    market = matches[0]
    contract_fields = ("pair", "contractType", "status", "quoteAsset", "marginAsset")
    identity = tuple(market.get(field) for field in contract_fields)
    if (
        identity != (symbol, "PERPETUAL", "TRADING", "USDT", "USDT")
        or type(market.get("onboardDate")) is not int
        or type(market.get("deliveryDate")) is not int
        or not 0 < market["onboardDate"] <= start_ms < end_ms <= market["deliveryDate"]
    ):
        raise FundingIngestError("probe is outside the current USD-M perpetual listing bounds")

    request = {"symbol": symbol, "startTime": start_ms, "endTime": end_ms - 1}
    candles = {}
    for clock, step in _BAR_MS.items():
        times = range(start_ms, end_ms, step)
        rows = exchange.fapiPublicGetKlines(request | {"interval": clock, "limit": len(times)})
        if not isinstance(rows, list) or len(rows) != len(times):
            raise FundingIngestError(f"{clock} bar count differs from the requested grid")
        for row, opened in zip(rows, times, strict=True):
            _check_bar(row, opened=opened, step=step, clock=clock)
        candles[clock] = rows

    raw_funding = exchange.fapiPublicGetFundingRate(request | {"limit": 1000})
    expected = list(range(start_ms, end_ms, FUNDING_INTERVAL_MS))
    if not isinstance(raw_funding, list) or len(raw_funding) != len(expected):
        raise FundingIngestError("funding event count differs from the requested grid")
    events = []
    for i, (row, nominal) in enumerate(zip(raw_funding, expected, strict=True)):
        if not isinstance(row, dict):
            raise FundingIngestError("funding row must be an object")
        event = normalize_raw_row(row, page_index=0, row_index=i, expected_symbol=symbol)
        if event["mark_price"] is not None and Decimal(event["mark_price"]) <= 0:
            raise FundingIngestError("funding mark price must be positive when provided")
        observed = event["exchange_funding_time_ms"]
        if not (
            start_ms <= observed < end_ms
            and abs(observed - nominal) <= MAX_EXCHANGE_TIMESTAMP_OFFSET_MS
        ):
            raise FundingIngestError("funding events are duplicated, missing or out of window")
        events.append(event)

    return {
        "schema_version": SCHEMA_VERSION,
        "symbol": symbol,
        "start_ms": start_ms,
        "end_ms_exclusive": end_ms,
        "current_instrument": market,
        "klines": candles,
        "funding_events": events,
    }


def _check_bar(row, *, opened, step, clock):
    if (
        not isinstance(row, list)
        or len(row) != 12
        or type(row[0]) is not int
        or type(row[6]) is not int
        or (row[0], row[6]) != (opened, opened + step - 1)
    ):
        raise FundingIngestError(f"{clock} bar does not match the requested UTC grid")
    try:
        open_, high, low, close, volume = (Decimal(str(value)) for value in row[1:6])
    except InvalidOperation as exc:
        raise FundingIngestError(f"{clock} bar contains invalid OHLCV") from exc
    if not (
        all(value.is_finite() for value in (open_, high, low, close, volume))
        and 0 < low <= min(open_, close) <= max(open_, close) <= high
        and volume >= 0
    ):
        raise FundingIngestError(f"{clock} bar contains invalid OHLCV")


def validate_public_coverage(*, symbol, clock, start_ms, end_ms, klines, funding):
    """Verify a complete public candidate grid, retaining observed funding offsets."""
    step = _BAR_MS[clock]
    if not (0 < start_ms < end_ms and start_ms % FUNDING_INTERVAL_MS == 0
            and end_ms % FUNDING_INTERVAL_MS == 0):
        raise FundingIngestError("public coverage window must be aligned and nonempty")
    times = range(start_ms, end_ms, step)
    if len(klines) != len(times):
        raise FundingIngestError(f"{clock} bar count differs from the requested grid")
    for row, opened in zip(klines, times, strict=True):
        _check_bar(row, opened=opened, step=step, clock=clock)

    events = range(start_ms, end_ms, FUNDING_INTERVAL_MS)
    if len(funding) != len(events):
        raise FundingIngestError("funding event count differs from the requested grid")
    for event, nominal in zip(funding, events, strict=True):
        observed = event["exchange_funding_time_ms"]
        offset = observed - nominal
        rate = Decimal(event["funding_rate"])
        if (event["symbol"] != symbol or event["raw_symbol"] != symbol
                or event["funding_time_ms"] != nominal or type(observed) is not int
                or not start_ms <= observed < end_ms
                or offset != event["exchange_funding_time_offset_ms"]
                or abs(offset) > MAX_EXCHANGE_TIMESTAMP_OFFSET_MS
                or not rate.is_finite() or not -1 <= rate <= 1):
            raise FundingIngestError("public funding symbol, rate or settlement grid mismatch")
        mark = event["mark_price"]
        if mark is not None and not (Decimal(mark).is_finite() and Decimal(mark) > 0):
            raise FundingIngestError("public funding mark must be positive")
    return {
        "bars": len(klines),
        "funding_events": len(funding),
        "missing_settlement_marks": sum(event["mark_price"] is None for event in funding),
        "nonzero_settlement_offsets": sum(event["exchange_funding_time_offset_ms"] != 0 for event in funding),
    }
