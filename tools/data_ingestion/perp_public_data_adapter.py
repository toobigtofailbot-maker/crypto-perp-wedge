"""Public perp-native data coverage and sample parser.

This module is intentionally offline by default.  It records public endpoint
coverage and parses tiny fixture responses into normalized sample records for
lineage/provenance review; it does not fetch data, write canonical datasets, or
touch runtime paths.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ID = "WP-LAB-DATA-EXPANSION-01"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / PACKAGE_ID
DEFAULT_SAMPLE_DIR = REPO_ROOT / "tests" / "fixtures" / "data_ingestion" / "perp_public_data"
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_PAIR = "BTCUSDT"
MARKET_TYPE = "USDT-M perpetual"
SOURCE_DOCS_CHECKED_UTC = "2026-06-21"

ADAPTER_LABELS = [
    "REPO-OWNED PUBLIC PERP-DATA COVERAGE OUTPUT",
    "NOT CANONICAL DATA AUTHORITY WITHOUT SEPARATE PROMOTION",
    "NOT A RESULT POPULATION",
    "NOT STRATEGY / VM / SWEEP AUTHORITY",
    "NOT BACKTEST COST-MODEL AUTHORITY",
    "NOT PAPER / LIVE / RUNTIME AUTHORITY",
    "PUBLIC-ONLY SAMPLE PARSING; NO NETWORK CALLS IN DEFAULT MODE",
]

HISTORY_DEPTH_CLASSES = {
    "backfillable",
    "recent_only",
    "streaming_only",
    "vendor_likely",
    "unknown",
    "blocked",
}

COVERAGE_FIELDS = [
    "source_name",
    "endpoint_or_method",
    "data_fields",
    "symbol_scope",
    "timeframe_period_support",
    "public_private_classification",
    "requires_credentials",
    "rate_limit_notes",
    "pagination_support",
    "history_depth_class",
    "known_history_limit",
    "timestamp_field",
    "timezone_policy",
    "lineage_key",
    "feature_families_unlocked",
    "status",
    "blocker_reason",
]


class PerpPublicDataError(RuntimeError):
    """Raised when public perp sample parsing or coverage generation fails."""


@dataclass(frozen=True)
class EndpointDefinition:
    source_name: str
    endpoint_or_method: str
    data_fields: list[str]
    symbol_scope: str
    timeframe_period_support: str
    public_private_classification: str
    requires_credentials: bool
    rate_limit_notes: str
    pagination_support: str
    history_depth_class: str
    known_history_limit: str
    timestamp_field: str
    timezone_policy: str
    lineage_key: str
    feature_families_unlocked: list[str]
    status: str
    blocker_reason: str | None = None


ENDPOINT_DEFINITIONS: dict[str, EndpointDefinition] = {
    "funding_history_preserved": EndpointDefinition(
        source_name="ccxt_public_funding_adapter",
        endpoint_or_method="ccxt.binanceusdm.fapiPublicGetFundingRate -> /fapi/v1/fundingRate",
        data_fields=["symbol", "fundingTime", "fundingRate", "markPrice"],
        symbol_scope="BTCUSDT in existing adapter; Binance endpoint also supports omitted symbol",
        timeframe_period_support="8h funding events",
        public_private_classification="public market data",
        requires_credentials=False,
        rate_limit_notes="Binance docs: shared 500 requests / 5 minutes / IP with fundingInfo",
        pagination_support="startTime/endTime/limit; ascending windows",
        history_depth_class="backfillable",
        known_history_limit="Existing repo adapter validated target D4 window; endpoint returns startTime + limit when larger than limit",
        timestamp_field="fundingTime",
        timezone_policy="millisecond epoch normalized to UTC",
        lineage_key="binance_usds_m_btcusdt_funding_history_public_preserved",
        feature_families_unlocked=["funding_carry", "perp_cost_context"],
        status="preserved",
        blocker_reason=None,
    ),
    "mark_price_klines_preserved": EndpointDefinition(
        source_name="binance_usds_m_public_rest",
        endpoint_or_method="GET /fapi/v1/markPriceKlines",
        data_fields=["open_time", "open", "high", "low", "close", "close_time"],
        symbol_scope="symbol, BTCUSDT sample; repo catalog has locked timeframe set",
        timeframe_period_support="1m through 1M per Binance kline interval family; repo catalog has 15m/30m/1h/4h/1d",
        public_private_classification="public market data",
        requires_credentials=False,
        rate_limit_notes="Binance docs: weight based on LIMIT, 1/2/5/10 tiers",
        pagination_support="startTime/endTime/limit; max 1500",
        history_depth_class="backfillable",
        known_history_limit="Repo catalog already records full history via data.binance.vision + REST repair",
        timestamp_field="open_time",
        timezone_policy="millisecond epoch normalized to UTC",
        lineage_key="binance_usds_m_btcusdt_mark_price_klines_public_preserved",
        feature_families_unlocked=["basis", "premium_dislocation", "mark_price_mechanics"],
        status="preserved",
        blocker_reason=None,
    ),
    "index_price_klines_preserved": EndpointDefinition(
        source_name="binance_usds_m_public_rest",
        endpoint_or_method="GET /fapi/v1/indexPriceKlines",
        data_fields=["open_time", "open", "high", "low", "close", "close_time"],
        symbol_scope="pair, BTCUSDT sample; repo catalog has locked timeframe set",
        timeframe_period_support="1m through 1M per Binance kline interval family; repo catalog has 15m/30m/1h/4h/1d",
        public_private_classification="public market data",
        requires_credentials=False,
        rate_limit_notes="Binance docs: weight based on LIMIT, 1/2/5/10 tiers",
        pagination_support="startTime/endTime/limit; max 1500",
        history_depth_class="backfillable",
        known_history_limit="Repo catalog already records full history via data.binance.vision + REST repair",
        timestamp_field="open_time",
        timezone_policy="millisecond epoch normalized to UTC",
        lineage_key="binance_usds_m_btcusdt_index_price_klines_public_preserved",
        feature_families_unlocked=["basis", "fair_value_reference", "premium_dislocation"],
        status="preserved",
        blocker_reason=None,
    ),
    "premium_index_klines_preserved": EndpointDefinition(
        source_name="binance_usds_m_public_rest",
        endpoint_or_method="GET /fapi/v1/premiumIndexKlines",
        data_fields=["open_time", "open", "high", "low", "close", "close_time"],
        symbol_scope="symbol, BTCUSDT sample; repo catalog has locked timeframe set",
        timeframe_period_support="1m through 1M per Binance kline interval family; repo catalog has 15m/30m/1h/4h/1d",
        public_private_classification="public market data",
        requires_credentials=False,
        rate_limit_notes="Binance docs: weight based on LIMIT, 1/2/5/10 tiers",
        pagination_support="startTime/endTime/limit; max 1500",
        history_depth_class="backfillable",
        known_history_limit="Repo catalog already records full history via data.binance.vision + REST repair",
        timestamp_field="open_time",
        timezone_policy="millisecond epoch normalized to UTC",
        lineage_key="binance_usds_m_btcusdt_premium_index_klines_public_preserved",
        feature_families_unlocked=["premium_pressure", "basis", "perp_dislocation"],
        status="preserved",
        blocker_reason=None,
    ),
    "mark_price_snapshot": EndpointDefinition(
        source_name="binance_usds_m_public_rest",
        endpoint_or_method="GET /fapi/v1/premiumIndex",
        data_fields=[
            "symbol",
            "markPrice",
            "indexPrice",
            "estimatedSettlePrice",
            "lastFundingRate",
            "interestRate",
            "nextFundingTime",
            "time",
        ],
        symbol_scope="symbol optional; BTCUSDT sample",
        timeframe_period_support="current snapshot",
        public_private_classification="public market data",
        requires_credentials=False,
        rate_limit_notes="Binance docs: weight 1 with symbol, 10 without symbol",
        pagination_support="none; current snapshot only",
        history_depth_class="recent_only",
        known_history_limit="current snapshot only via REST",
        timestamp_field="time",
        timezone_policy="millisecond epoch normalized to UTC",
        lineage_key="binance_usds_m_btcusdt_mark_price_snapshot_public",
        feature_families_unlocked=["current_basis", "funding_context", "mark_price_mechanics"],
        status="adopted",
        blocker_reason=None,
    ),
    "current_open_interest": EndpointDefinition(
        source_name="binance_usds_m_public_rest",
        endpoint_or_method="GET /fapi/v1/openInterest",
        data_fields=["symbol", "openInterest", "time"],
        symbol_scope="single symbol; BTCUSDT sample",
        timeframe_period_support="current snapshot",
        public_private_classification="public market data",
        requires_credentials=False,
        rate_limit_notes="Binance docs: weight 1",
        pagination_support="none; current snapshot only",
        history_depth_class="recent_only",
        known_history_limit="current open interest only",
        timestamp_field="time",
        timezone_policy="millisecond epoch normalized to UTC",
        lineage_key="binance_usds_m_btcusdt_current_open_interest_public",
        feature_families_unlocked=["open_interest_context", "positioning_pressure"],
        status="adopted",
        blocker_reason=None,
    ),
    "open_interest_statistics": EndpointDefinition(
        source_name="binance_usds_m_public_rest",
        endpoint_or_method="GET /futures/data/openInterestHist",
        data_fields=["symbol", "sumOpenInterest", "sumOpenInterestValue", "CMCCirculatingSupply", "timestamp"],
        symbol_scope="single symbol; BTCUSDT sample",
        timeframe_period_support='5m,15m,30m,1h,2h,4h,6h,12h,1d',
        public_private_classification="public market data",
        requires_credentials=False,
        rate_limit_notes="Binance docs: request weight 0; IP limit 1000 requests / 5 minutes",
        pagination_support="startTime/endTime/limit; max 500",
        history_depth_class="recent_only",
        known_history_limit="latest 1 month per Binance docs",
        timestamp_field="timestamp",
        timezone_policy="millisecond epoch normalized to UTC",
        lineage_key="binance_usds_m_btcusdt_open_interest_statistics_public",
        feature_families_unlocked=["open_interest_trend", "crowding", "positioning_pressure"],
        status="adopted",
        blocker_reason=None,
    ),
    "top_trader_long_short_position_ratio": EndpointDefinition(
        source_name="binance_usds_m_public_rest",
        endpoint_or_method="GET /futures/data/topLongShortPositionRatio",
        data_fields=["symbol", "longShortRatio", "longAccount", "shortAccount", "timestamp"],
        symbol_scope="single symbol; BTCUSDT sample",
        timeframe_period_support='5m,15m,30m,1h,2h,4h,6h,12h,1d',
        public_private_classification="public market data",
        requires_credentials=False,
        rate_limit_notes="Binance docs: request weight 0; IP limit 1000 requests / 5 minutes",
        pagination_support="startTime/endTime/limit; max 500",
        history_depth_class="recent_only",
        known_history_limit="latest 30 days per Binance docs",
        timestamp_field="timestamp",
        timezone_policy="millisecond epoch normalized to UTC",
        lineage_key="binance_usds_m_btcusdt_top_trader_position_ratio_public",
        feature_families_unlocked=["top_trader_crowding", "positioning_pressure"],
        status="adopted",
        blocker_reason=None,
    ),
    "top_trader_long_short_account_ratio": EndpointDefinition(
        source_name="binance_usds_m_public_rest",
        endpoint_or_method="GET /futures/data/topLongShortAccountRatio",
        data_fields=["symbol", "longShortRatio", "longAccount", "shortAccount", "timestamp"],
        symbol_scope="single symbol; BTCUSDT sample",
        timeframe_period_support='5m,15m,30m,1h,2h,4h,6h,12h,1d',
        public_private_classification="public market data",
        requires_credentials=False,
        rate_limit_notes="Binance docs: IP limit 1000 requests / 5 minutes",
        pagination_support="startTime/endTime/limit; max 500",
        history_depth_class="recent_only",
        known_history_limit="latest 30 days per Binance docs",
        timestamp_field="timestamp",
        timezone_policy="millisecond epoch normalized to UTC",
        lineage_key="binance_usds_m_btcusdt_top_trader_account_ratio_public",
        feature_families_unlocked=["top_trader_crowding", "account_positioning"],
        status="adopted",
        blocker_reason=None,
    ),
    "global_long_short_account_ratio": EndpointDefinition(
        source_name="binance_usds_m_public_rest",
        endpoint_or_method="GET /futures/data/globalLongShortAccountRatio",
        data_fields=["symbol", "longShortRatio", "longAccount", "shortAccount", "timestamp"],
        symbol_scope="single symbol; BTCUSDT sample",
        timeframe_period_support='5m,15m,30m,1h,2h,4h,6h,12h,1d',
        public_private_classification="public market data",
        requires_credentials=False,
        rate_limit_notes="Binance docs: request weight 0; IP limit 1000 requests / 5 minutes",
        pagination_support="startTime/endTime/limit; max 500",
        history_depth_class="recent_only",
        known_history_limit="latest 30 days per Binance docs",
        timestamp_field="timestamp",
        timezone_policy="millisecond epoch normalized to UTC",
        lineage_key="binance_usds_m_btcusdt_global_account_ratio_public",
        feature_families_unlocked=["global_crowding", "account_positioning"],
        status="adopted",
        blocker_reason=None,
    ),
    "taker_buy_sell_volume_ratio": EndpointDefinition(
        source_name="binance_usds_m_public_rest",
        endpoint_or_method="GET /futures/data/takerlongshortRatio",
        data_fields=["buySellRatio", "buyVol", "sellVol", "timestamp"],
        symbol_scope="single symbol; BTCUSDT sample",
        timeframe_period_support='5m,15m,30m,1h,2h,4h,6h,12h,1d',
        public_private_classification="public market data",
        requires_credentials=False,
        rate_limit_notes="Binance docs: request weight 0; IP limit 1000 requests / 5 minutes",
        pagination_support="startTime/endTime/limit; max 500",
        history_depth_class="recent_only",
        known_history_limit="latest 30 days per Binance docs",
        timestamp_field="timestamp",
        timezone_policy="millisecond epoch normalized to UTC",
        lineage_key="binance_usds_m_btcusdt_taker_buy_sell_ratio_public",
        feature_families_unlocked=["taker_flow", "microstructure_pressure"],
        status="adopted",
        blocker_reason=None,
    ),
    "aggregate_trades_rest": EndpointDefinition(
        source_name="binance_usds_m_public_rest",
        endpoint_or_method="GET /fapi/v1/aggTrades",
        data_fields=["a", "p", "q", "f", "l", "T", "m"],
        symbol_scope="single symbol; BTCUSDT sample",
        timeframe_period_support="trade events; request window under 1 hour when startTime/endTime are used",
        public_private_classification="public market data",
        requires_credentials=False,
        rate_limit_notes="Binance docs: request weight 20",
        pagination_support="fromId or startTime/endTime/limit; max 1000",
        history_depth_class="recent_only",
        known_history_limit="REST query futures trade histories not older than 24 hours per Binance docs",
        timestamp_field="T",
        timezone_policy="millisecond epoch normalized to UTC",
        lineage_key="binance_usds_m_btcusdt_agg_trades_rest_public",
        feature_families_unlocked=["trade_flow", "approx_vwap", "microstructure_pressure"],
        status="adopted",
        blocker_reason=None,
    ),
    "recent_trades_rest": EndpointDefinition(
        source_name="binance_usds_m_public_rest",
        endpoint_or_method="GET /fapi/v1/trades",
        data_fields=["id", "price", "qty", "quoteQty", "time", "isBuyerMaker"],
        symbol_scope="single symbol; BTCUSDT sample",
        timeframe_period_support="recent trade events",
        public_private_classification="public market data",
        requires_credentials=False,
        rate_limit_notes="Binance docs: request weight 5",
        pagination_support="limit only; max 1000",
        history_depth_class="recent_only",
        known_history_limit="recent market trades only",
        timestamp_field="time",
        timezone_policy="millisecond epoch normalized to UTC",
        lineage_key="binance_usds_m_btcusdt_recent_trades_rest_public",
        feature_families_unlocked=["trade_flow", "approx_vwap", "microstructure_pressure"],
        status="adopted",
        blocker_reason=None,
    ),
    "futures_um_agg_trades_archive": EndpointDefinition(
        source_name="data.binance.vision_public_archive",
        endpoint_or_method="https://data.binance.vision/data/futures/um/{daily,monthly}/aggTrades/{symbol}/",
        data_fields=["agg_trade_id", "price", "quantity", "first_trade_id", "last_trade_id", "transact_time", "is_buyer_maker"],
        symbol_scope="public archive by symbol; BTCUSDT sample",
        timeframe_period_support="daily and monthly archive files",
        public_private_classification="public market data archive",
        requires_credentials=False,
        rate_limit_notes="static public archive; download behavior should be throttled by future fetcher",
        pagination_support="file partition by date/month",
        history_depth_class="backfillable",
        known_history_limit="public archive availability must be verified per requested file before canonical use",
        timestamp_field="transact_time",
        timezone_policy="millisecond epoch normalized to UTC",
        lineage_key="binance_usds_m_btcusdt_agg_trades_archive_public",
        feature_families_unlocked=["trade_flow", "approx_vwap", "microstructure_pressure"],
        status="adopted",
        blocker_reason=None,
    ),
    "futures_um_trades_archive": EndpointDefinition(
        source_name="data.binance.vision_public_archive",
        endpoint_or_method="https://data.binance.vision/data/futures/um/{daily,monthly}/trades/{symbol}/",
        data_fields=["trade_id", "price", "qty", "quote_qty", "time", "is_buyer_maker"],
        symbol_scope="public archive by symbol; BTCUSDT sample",
        timeframe_period_support="daily and monthly archive files",
        public_private_classification="public market data archive",
        requires_credentials=False,
        rate_limit_notes="static public archive; download behavior should be throttled by future fetcher",
        pagination_support="file partition by date/month",
        history_depth_class="backfillable",
        known_history_limit="public archive availability must be verified per requested file before canonical use",
        timestamp_field="time",
        timezone_policy="millisecond epoch normalized to UTC",
        lineage_key="binance_usds_m_btcusdt_trades_archive_public",
        feature_families_unlocked=["trade_flow", "approx_vwap", "microstructure_pressure"],
        status="adopted",
        blocker_reason=None,
    ),
    "exchange_metadata": EndpointDefinition(
        source_name="binance_usds_m_public_rest",
        endpoint_or_method="GET /fapi/v1/exchangeInfo",
        data_fields=["symbols", "filters", "contractType", "status", "pricePrecision", "quantityPrecision"],
        symbol_scope="all symbols response; BTCUSDT normalized sample",
        timeframe_period_support="current symbol/rule snapshot",
        public_private_classification="public market data",
        requires_credentials=False,
        rate_limit_notes="Binance docs: request weight 1",
        pagination_support="none; full exchange info snapshot",
        history_depth_class="recent_only",
        known_history_limit="current exchange rules only",
        timestamp_field="serverTime",
        timezone_policy="millisecond epoch normalized to UTC",
        lineage_key="binance_usds_m_exchange_info_btcusdt_public",
        feature_families_unlocked=["symbol_constraints", "exchange_metadata", "backtest_realism_context"],
        status="adopted",
        blocker_reason=None,
    ),
}

SAMPLE_FILES = {
    "funding_history_preserved": "funding_history.json",
    "mark_price_klines_preserved": "mark_price_klines.json",
    "index_price_klines_preserved": "index_price_klines.json",
    "premium_index_klines_preserved": "premium_index_klines.json",
    "mark_price_snapshot": "mark_price_snapshot.json",
    "current_open_interest": "open_interest.json",
    "open_interest_statistics": "open_interest_hist.json",
    "top_trader_long_short_position_ratio": "top_long_short_position_ratio.json",
    "top_trader_long_short_account_ratio": "top_long_short_account_ratio.json",
    "global_long_short_account_ratio": "global_long_short_account_ratio.json",
    "taker_buy_sell_volume_ratio": "taker_long_short_ratio.json",
    "aggregate_trades_rest": "agg_trades.json",
    "recent_trades_rest": "recent_trades.json",
    "futures_um_agg_trades_archive": "data_vision_agg_trades.csv",
    "futures_um_trades_archive": "data_vision_trades.csv",
    "exchange_metadata": "exchange_info.json",
}


def _iso_from_ms(value: int) -> str:
    if value <= 0:
        raise PerpPublicDataError("timestamp must be a positive millisecond epoch")
    return datetime.fromtimestamp(value / 1000, tz=UTC).isoformat().replace("+00:00", "Z")


def _integer_ms(value: Any, field_name: str) -> int:
    try:
        parsed = int(str(value).strip())
    except Exception as exc:
        raise PerpPublicDataError(f"{field_name} must be an integer millisecond timestamp") from exc
    if parsed <= 0:
        raise PerpPublicDataError(f"{field_name} must be positive")
    return parsed


def _decimal_string(value: Any, field_name: str) -> str:
    if value is None:
        raise PerpPublicDataError(f"{field_name} is required")
    text = str(value).strip()
    if not text:
        raise PerpPublicDataError(f"{field_name} is required")
    try:
        parsed = Decimal(text)
    except (InvalidOperation, ValueError) as exc:
        raise PerpPublicDataError(f"{field_name} must be numeric") from exc
    if not parsed.is_finite():
        raise PerpPublicDataError(f"{field_name} must be finite")
    return format(parsed, "f")


def _optional_decimal_string(value: Any, field_name: str) -> str | None:
    if value is None or str(value).strip() == "":
        return None
    return _decimal_string(value, field_name)


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PerpPublicDataError(f"{field_name} must be an object")
    return value


def _require_list(value: Any, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise PerpPublicDataError(f"{field_name} must be a list")
    return value


def _require_symbol(raw: dict[str, Any]) -> str:
    symbol = str(raw.get("symbol", "")).strip()
    if symbol != DEFAULT_SYMBOL:
        raise PerpPublicDataError(f"unexpected symbol {symbol!r}")
    return symbol


def _base_record(endpoint_key: str, *, symbol: str = DEFAULT_SYMBOL) -> dict[str, Any]:
    definition = ENDPOINT_DEFINITIONS[endpoint_key]
    return {
        "exchange": "binance",
        "market_type": MARKET_TYPE,
        "symbol": symbol,
        "source_name": definition.source_name,
        "endpoint_or_method": definition.endpoint_or_method,
        "lineage_key": definition.lineage_key,
        "sample_only": True,
        "canonical_data_authority": False,
        "runtime_authority": False,
    }


def _with_event_time(record: dict[str, Any], timestamp_ms: int) -> dict[str, Any]:
    record["event_time_ms"] = timestamp_ms
    record["event_time_utc"] = _iso_from_ms(timestamp_ms)
    return record


def _normalize_funding_history(payload: Any, endpoint_key: str) -> list[dict[str, Any]]:
    records = []
    for index, item in enumerate(_require_list(payload, endpoint_key)):
        raw = _require_mapping(item, f"{endpoint_key}[{index}]")
        symbol = _require_symbol(raw)
        timestamp_ms = _integer_ms(raw.get("fundingTime"), "fundingTime")
        record = _with_event_time(_base_record(endpoint_key, symbol=symbol), timestamp_ms)
        record.update(
            {
                "data_type": "funding_rate",
                "funding_rate": _decimal_string(raw.get("fundingRate"), "fundingRate"),
                "mark_price": _optional_decimal_string(raw.get("markPrice"), "markPrice"),
                "raw": raw,
            }
        )
        records.append(record)
    return records


def _normalize_kline_array(payload: Any, endpoint_key: str) -> list[dict[str, Any]]:
    rows = _require_list(payload, endpoint_key)
    records = []
    data_type = endpoint_key.replace("_preserved", "")
    for index, row in enumerate(rows):
        values = _require_list(row, f"{endpoint_key}[{index}]")
        if len(values) < 7:
            raise PerpPublicDataError(f"{endpoint_key}[{index}] must contain at least 7 kline fields")
        open_time_ms = _integer_ms(values[0], "open_time")
        close_time_ms = _integer_ms(values[6], "close_time")
        record = _with_event_time(_base_record(endpoint_key), open_time_ms)
        record.update(
            {
                "data_type": data_type,
                "open_time_ms": open_time_ms,
                "open_time_utc": _iso_from_ms(open_time_ms),
                "open": _decimal_string(values[1], "open"),
                "high": _decimal_string(values[2], "high"),
                "low": _decimal_string(values[3], "low"),
                "close": _decimal_string(values[4], "close"),
                "close_time_ms": close_time_ms,
                "close_time_utc": _iso_from_ms(close_time_ms),
                "raw": values,
            }
        )
        records.append(record)
    return records


def _normalize_mark_price_snapshot(payload: Any, endpoint_key: str) -> list[dict[str, Any]]:
    raw = _require_mapping(payload, endpoint_key)
    symbol = _require_symbol(raw)
    timestamp_ms = _integer_ms(raw.get("time"), "time")
    next_funding_ms = _integer_ms(raw.get("nextFundingTime"), "nextFundingTime")
    record = _with_event_time(_base_record(endpoint_key, symbol=symbol), timestamp_ms)
    record.update(
        {
            "data_type": "mark_price_snapshot",
            "mark_price": _decimal_string(raw.get("markPrice"), "markPrice"),
            "index_price": _decimal_string(raw.get("indexPrice"), "indexPrice"),
            "estimated_settle_price": _optional_decimal_string(
                raw.get("estimatedSettlePrice"), "estimatedSettlePrice"
            ),
            "last_funding_rate": _decimal_string(raw.get("lastFundingRate"), "lastFundingRate"),
            "interest_rate": _decimal_string(raw.get("interestRate"), "interestRate"),
            "next_funding_time_ms": next_funding_ms,
            "next_funding_time_utc": _iso_from_ms(next_funding_ms),
            "raw": raw,
        }
    )
    return [record]


def _normalize_current_open_interest(payload: Any, endpoint_key: str) -> list[dict[str, Any]]:
    raw = _require_mapping(payload, endpoint_key)
    symbol = _require_symbol(raw)
    timestamp_ms = _integer_ms(raw.get("time"), "time")
    record = _with_event_time(_base_record(endpoint_key, symbol=symbol), timestamp_ms)
    record.update(
        {
            "data_type": "current_open_interest",
            "open_interest": _decimal_string(raw.get("openInterest"), "openInterest"),
            "raw": raw,
        }
    )
    return [record]


def _normalize_open_interest_hist(payload: Any, endpoint_key: str) -> list[dict[str, Any]]:
    records = []
    for index, item in enumerate(_require_list(payload, endpoint_key)):
        raw = _require_mapping(item, f"{endpoint_key}[{index}]")
        symbol = _require_symbol(raw)
        timestamp_ms = _integer_ms(raw.get("timestamp"), "timestamp")
        record = _with_event_time(_base_record(endpoint_key, symbol=symbol), timestamp_ms)
        record.update(
            {
                "data_type": "open_interest_statistics",
                "sum_open_interest": _decimal_string(raw.get("sumOpenInterest"), "sumOpenInterest"),
                "sum_open_interest_value": _decimal_string(
                    raw.get("sumOpenInterestValue"), "sumOpenInterestValue"
                ),
                "cmc_circulating_supply": _optional_decimal_string(
                    raw.get("CMCCirculatingSupply"), "CMCCirculatingSupply"
                ),
                "raw": raw,
            }
        )
        records.append(record)
    return records


def _normalize_ratio_rows(payload: Any, endpoint_key: str, data_type: str) -> list[dict[str, Any]]:
    records = []
    for index, item in enumerate(_require_list(payload, endpoint_key)):
        raw = _require_mapping(item, f"{endpoint_key}[{index}]")
        symbol = _require_symbol(raw)
        timestamp_ms = _integer_ms(raw.get("timestamp"), "timestamp")
        record = _with_event_time(_base_record(endpoint_key, symbol=symbol), timestamp_ms)
        record.update(
            {
                "data_type": data_type,
                "long_short_ratio": _decimal_string(raw.get("longShortRatio"), "longShortRatio"),
                "long_ratio": _decimal_string(raw.get("longAccount"), "longAccount"),
                "short_ratio": _decimal_string(raw.get("shortAccount"), "shortAccount"),
                "raw": raw,
            }
        )
        records.append(record)
    return records


def _normalize_taker_ratio(payload: Any, endpoint_key: str) -> list[dict[str, Any]]:
    records = []
    for index, item in enumerate(_require_list(payload, endpoint_key)):
        raw = _require_mapping(item, f"{endpoint_key}[{index}]")
        timestamp_ms = _integer_ms(raw.get("timestamp"), "timestamp")
        record = _with_event_time(_base_record(endpoint_key), timestamp_ms)
        record.update(
            {
                "data_type": "taker_buy_sell_volume_ratio",
                "buy_sell_ratio": _decimal_string(raw.get("buySellRatio"), "buySellRatio"),
                "buy_volume": _decimal_string(raw.get("buyVol"), "buyVol"),
                "sell_volume": _decimal_string(raw.get("sellVol"), "sellVol"),
                "raw": raw,
            }
        )
        records.append(record)
    return records


def _normalize_agg_trades(payload: Any, endpoint_key: str) -> list[dict[str, Any]]:
    records = []
    for index, item in enumerate(_require_list(payload, endpoint_key)):
        raw = _require_mapping(item, f"{endpoint_key}[{index}]")
        timestamp_ms = _integer_ms(raw.get("T"), "T")
        record = _with_event_time(_base_record(endpoint_key), timestamp_ms)
        record.update(
            {
                "data_type": "aggregate_trade",
                "agg_trade_id": int(raw["a"]),
                "price": _decimal_string(raw.get("p"), "p"),
                "quantity": _decimal_string(raw.get("q"), "q"),
                "first_trade_id": int(raw["f"]),
                "last_trade_id": int(raw["l"]),
                "buyer_maker": bool(raw.get("m")),
                "raw": raw,
            }
        )
        records.append(record)
    return records


def _normalize_recent_trades(payload: Any, endpoint_key: str) -> list[dict[str, Any]]:
    records = []
    for index, item in enumerate(_require_list(payload, endpoint_key)):
        raw = _require_mapping(item, f"{endpoint_key}[{index}]")
        timestamp_ms = _integer_ms(raw.get("time"), "time")
        record = _with_event_time(_base_record(endpoint_key), timestamp_ms)
        record.update(
            {
                "data_type": "trade",
                "trade_id": int(raw["id"]),
                "price": _decimal_string(raw.get("price"), "price"),
                "quantity": _decimal_string(raw.get("qty"), "qty"),
                "quote_quantity": _optional_decimal_string(raw.get("quoteQty"), "quoteQty"),
                "buyer_maker": bool(raw.get("isBuyerMaker")),
                "rpi_trade": bool(raw.get("isRPITrade")) if "isRPITrade" in raw else None,
                "raw": raw,
            }
        )
        records.append(record)
    return records


def _normalize_archive_csv(payload: str, endpoint_key: str, *, data_type: str) -> list[dict[str, Any]]:
    records = []
    reader = csv.DictReader(payload.splitlines())
    for index, raw in enumerate(reader):
        if data_type == "archive_aggregate_trade":
            timestamp_ms = _integer_ms(raw.get("transact_time"), "transact_time")
            record = _with_event_time(_base_record(endpoint_key), timestamp_ms)
            record.update(
                {
                    "data_type": data_type,
                    "agg_trade_id": int(raw["agg_trade_id"]),
                    "price": _decimal_string(raw.get("price"), "price"),
                    "quantity": _decimal_string(raw.get("quantity"), "quantity"),
                    "first_trade_id": int(raw["first_trade_id"]),
                    "last_trade_id": int(raw["last_trade_id"]),
                    "buyer_maker": str(raw.get("is_buyer_maker", "")).strip().lower() == "true",
                    "raw_row_index": index,
                    "raw": dict(raw),
                }
            )
        else:
            timestamp_ms = _integer_ms(raw.get("time"), "time")
            record = _with_event_time(_base_record(endpoint_key), timestamp_ms)
            record.update(
                {
                    "data_type": data_type,
                    "trade_id": int(raw["trade_id"]),
                    "price": _decimal_string(raw.get("price"), "price"),
                    "quantity": _decimal_string(raw.get("qty"), "qty"),
                    "quote_quantity": _optional_decimal_string(raw.get("quote_qty"), "quote_qty"),
                    "buyer_maker": str(raw.get("is_buyer_maker", "")).strip().lower() == "true",
                    "raw_row_index": index,
                    "raw": dict(raw),
                }
            )
        records.append(record)
    if not records:
        raise PerpPublicDataError(f"{endpoint_key} archive sample produced no records")
    return records


def _normalize_exchange_info(payload: Any, endpoint_key: str) -> list[dict[str, Any]]:
    raw = _require_mapping(payload, endpoint_key)
    symbols = _require_list(raw.get("symbols"), "symbols")
    btcusdt = None
    for item in symbols:
        candidate = _require_mapping(item, "symbols[]")
        if candidate.get("symbol") == DEFAULT_SYMBOL:
            btcusdt = candidate
            break
    if btcusdt is None:
        raise PerpPublicDataError("exchangeInfo sample must include BTCUSDT")
    timestamp_ms = _integer_ms(raw.get("serverTime"), "serverTime")
    record = _with_event_time(_base_record(endpoint_key), timestamp_ms)
    record.update(
        {
            "data_type": "exchange_metadata",
            "pair": btcusdt.get("pair"),
            "contract_type": btcusdt.get("contractType"),
            "status": btcusdt.get("status"),
            "base_asset": btcusdt.get("baseAsset"),
            "quote_asset": btcusdt.get("quoteAsset"),
            "margin_asset": btcusdt.get("marginAsset"),
            "price_precision": btcusdt.get("pricePrecision"),
            "quantity_precision": btcusdt.get("quantityPrecision"),
            "filters": btcusdt.get("filters", []),
            "order_types": btcusdt.get("orderTypes", []),
            "raw": btcusdt,
        }
    )
    return [record]


NORMALIZERS = {
    "funding_history_preserved": _normalize_funding_history,
    "mark_price_klines_preserved": _normalize_kline_array,
    "index_price_klines_preserved": _normalize_kline_array,
    "premium_index_klines_preserved": _normalize_kline_array,
    "mark_price_snapshot": _normalize_mark_price_snapshot,
    "current_open_interest": _normalize_current_open_interest,
    "open_interest_statistics": _normalize_open_interest_hist,
    "top_trader_long_short_position_ratio": lambda payload, key: _normalize_ratio_rows(
        payload, key, "top_trader_long_short_position_ratio"
    ),
    "top_trader_long_short_account_ratio": lambda payload, key: _normalize_ratio_rows(
        payload, key, "top_trader_long_short_account_ratio"
    ),
    "global_long_short_account_ratio": lambda payload, key: _normalize_ratio_rows(
        payload, key, "global_long_short_account_ratio"
    ),
    "taker_buy_sell_volume_ratio": _normalize_taker_ratio,
    "aggregate_trades_rest": _normalize_agg_trades,
    "recent_trades_rest": _normalize_recent_trades,
    "futures_um_agg_trades_archive": lambda payload, key: _normalize_archive_csv(
        payload, key, data_type="archive_aggregate_trade"
    ),
    "futures_um_trades_archive": lambda payload, key: _normalize_archive_csv(
        payload, key, data_type="archive_trade"
    ),
    "exchange_metadata": _normalize_exchange_info,
}


def _sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _stable_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise PerpPublicDataError(f"path must stay inside repo root: {path}") from exc


def coverage_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for definition in ENDPOINT_DEFINITIONS.values():
        row = asdict(definition)
        if set(row) != set(COVERAGE_FIELDS):
            raise PerpPublicDataError("coverage row fields do not match required field set")
        if row["history_depth_class"] not in HISTORY_DEPTH_CLASSES:
            raise PerpPublicDataError(f"invalid history_depth_class {row['history_depth_class']!r}")
        rows.append(row)
    return rows


def _load_sample(sample_dir: Path, endpoint_key: str) -> Any:
    sample_path = sample_dir / SAMPLE_FILES[endpoint_key]
    if not sample_path.exists():
        raise PerpPublicDataError(f"sample fixture missing: {sample_path}")
    if sample_path.suffix == ".csv":
        return sample_path.read_text(encoding="utf-8")
    return json.loads(sample_path.read_text(encoding="utf-8"))


def normalize_sample(endpoint_key: str, payload: Any) -> list[dict[str, Any]]:
    if endpoint_key not in NORMALIZERS:
        raise PerpPublicDataError(f"no normalizer registered for {endpoint_key}")
    records = NORMALIZERS[endpoint_key](payload, endpoint_key)
    if not records:
        raise PerpPublicDataError(f"{endpoint_key} produced no normalized records")
    for index, record in enumerate(records):
        for field in ["exchange", "market_type", "symbol", "data_type", "event_time_utc", "event_time_ms", "lineage_key", "raw"]:
            if field not in record:
                raise PerpPublicDataError(f"{endpoint_key}[{index}] missing normalized field {field}")
    return sorted(records, key=lambda row: (row["event_time_ms"], row["data_type"], row["lineage_key"]))


def normalize_all_samples(sample_dir: Path = DEFAULT_SAMPLE_DIR) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for endpoint_key in ENDPOINT_DEFINITIONS:
        payload = _load_sample(sample_dir, endpoint_key)
        records = normalize_sample(endpoint_key, payload)
        checksum = _sha256_text(_stable_json(records))
        results[endpoint_key] = {
            "fixture_path": _repo_relative(sample_dir / SAMPLE_FILES[endpoint_key]),
            "record_count": len(records),
            "normalized_sample_sha256": checksum,
            "first_event_time_utc": records[0]["event_time_utc"],
            "last_event_time_utc": records[-1]["event_time_utc"],
            "lineage_key": ENDPOINT_DEFINITIONS[endpoint_key].lineage_key,
            "status": "PASS",
        }
    return results


def _coverage_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        f"# {PACKAGE_ID} Coverage Matrix",
        "",
        *[f"- {label}" for label in ADAPTER_LABELS],
        "",
        "| Source | Endpoint / method | History depth | Status | Known limit |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {source} | `{endpoint}` | `{depth}` | `{status}` | {limit} |".format(
                source=row["source_name"],
                endpoint=row["endpoint_or_method"],
                depth=row["history_depth_class"],
                status=row["status"],
                limit=row["known_history_limit"],
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Coverage and samples are public-only and non-authoritative.",
            "- Existing funding, mark, index, and premium catalog surfaces are preserved.",
            "- No network, dependency, runtime, runner, compiler, query, or canonical evidence path is changed.",
            "",
        ]
    )
    return "\n".join(lines)


def _validation_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# {PACKAGE_ID} Validation Report",
        "",
        *[f"- {label}" for label in ADAPTER_LABELS],
        "",
        f"Status: `{report['status']}`",
        f"Endpoint definitions: `{report['endpoint_definition_count']}`",
        f"Sample endpoints parsed: `{report['sample_endpoint_count']}`",
        f"Sample records parsed: `{report['sample_record_count']}`",
        f"Aggregate sample checksum: `{report['aggregate_normalized_sample_sha256']}`",
        "",
    ]
    if report["errors"]:
        lines.extend(["## Errors", "", *[f"- {error}" for error in report["errors"]], ""])
    lines.extend(
        [
            "## Boundary",
            "",
            "- Default validation uses committed fixture responses only.",
            "- Credentials, private endpoints, account endpoints, order endpoints, and runtime paths are not used.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifacts(sample_dir: Path = DEFAULT_SAMPLE_DIR) -> dict[str, Any]:
    rows = coverage_matrix()
    errors: list[str] = []
    samples: dict[str, dict[str, Any]] = {}
    try:
        samples = normalize_all_samples(sample_dir)
    except Exception as exc:
        errors.append(str(exc))

    aggregate_checksum = _sha256_text(_stable_json(samples))
    validation = {
        "labels": ADAPTER_LABELS,
        "package": PACKAGE_ID,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "endpoint_definition_count": len(rows),
        "coverage_fields": COVERAGE_FIELDS,
        "history_depth_classes": sorted(HISTORY_DEPTH_CLASSES),
        "sample_endpoint_count": len(samples),
        "sample_record_count": sum(item["record_count"] for item in samples.values()),
        "aggregate_normalized_sample_sha256": aggregate_checksum,
        "public_only_confirmed": True,
        "credentials_used": False,
        "network_calls_performed": False,
        "canonical_write": False,
        "runtime_paper_live_contact": False,
        "dependency_files_changed": False,
    }
    return {
        "coverage_matrix": {
            "labels": ADAPTER_LABELS,
            "package": PACKAGE_ID,
            "source_docs_checked_utc": SOURCE_DOCS_CHECKED_UTC,
            "history_depth_class_policy": sorted(HISTORY_DEPTH_CLASSES),
            "coverage": rows,
        },
        "sample_catalog_lineage": {
            "labels": ADAPTER_LABELS,
            "package": PACKAGE_ID,
            "catalog_status": "sample_public_perp_data_lineage_noncanonical",
            "symbol": DEFAULT_SYMBOL,
            "market_type": MARKET_TYPE,
            "sample_dir": _repo_relative(sample_dir),
            "sample_outputs": samples,
            "aggregate_normalized_sample_sha256": aggregate_checksum,
            "canonical_data_authority": False,
            "runtime_authority": False,
            "promotion_readiness_authority": False,
        },
        "provenance": {
            "labels": ADAPTER_LABELS,
            "package": PACKAGE_ID,
            "generated_mode": "coverage_only_offline",
            "source_docs_checked_utc": SOURCE_DOCS_CHECKED_UTC,
            "sample_dir": _repo_relative(sample_dir),
            "public_sources": sorted({definition.source_name for definition in ENDPOINT_DEFINITIONS.values()}),
            "private_or_account_methods_used": False,
            "credentials_used": False,
            "network_calls_performed": False,
            "runtime_paper_live_contact": False,
            "canonical_artifacts_written": False,
            "repo_truth_preserved": [
                "tools/data_ingestion/ccxt_public_funding_adapter.py",
                "docs/data_catalog.md existing funding/mark/index/premium entries",
            ],
        },
        "validation_report": validation,
    }


def write_coverage_artifacts(output_dir: Path = DEFAULT_OUTPUT_DIR, sample_dir: Path = DEFAULT_SAMPLE_DIR) -> dict[str, Any]:
    artifacts = build_artifacts(sample_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "coverage_matrix_json": output_dir / "coverage_matrix.json",
        "coverage_matrix_md": output_dir / "coverage_matrix.md",
        "sample_catalog_lineage": output_dir / "sample_catalog_lineage.json",
        "provenance": output_dir / "provenance.json",
        "validation_report_json": output_dir / "validation_report.json",
        "validation_report_md": output_dir / "validation_report.md",
    }
    _write_json(paths["coverage_matrix_json"], artifacts["coverage_matrix"])
    paths["coverage_matrix_md"].write_text(
        _coverage_markdown(artifacts["coverage_matrix"]["coverage"]), encoding="utf-8"
    )
    _write_json(paths["sample_catalog_lineage"], artifacts["sample_catalog_lineage"])
    _write_json(paths["provenance"], artifacts["provenance"])
    _write_json(paths["validation_report_json"], artifacts["validation_report"])
    paths["validation_report_md"].write_text(
        _validation_markdown(artifacts["validation_report"]), encoding="utf-8"
    )
    return {
        "labels": ADAPTER_LABELS,
        "package": PACKAGE_ID,
        "status": artifacts["validation_report"]["status"],
        "output_dir": _repo_relative(output_dir),
        "paths": {key: _repo_relative(path) for key, path in paths.items()},
        "endpoint_definition_count": artifacts["validation_report"]["endpoint_definition_count"],
        "sample_endpoint_count": artifacts["validation_report"]["sample_endpoint_count"],
        "sample_record_count": artifacts["validation_report"]["sample_record_count"],
        "aggregate_normalized_sample_sha256": artifacts["validation_report"][
            "aggregate_normalized_sample_sha256"
        ],
        "canonical_write": False,
        "runtime_paper_live_contact": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage-only", action="store_true", help="write offline coverage/provenance artifacts")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--sample-dir", type=Path, default=DEFAULT_SAMPLE_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not args.coverage_only:
        parser.error("only --coverage-only is supported; this adapter performs no default network fetch")
    try:
        result = write_coverage_artifacts(output_dir=args.output_dir, sample_dir=args.sample_dir)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
