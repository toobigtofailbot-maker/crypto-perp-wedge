"""Materialize authoritative taker-flow features from the canonical D4 parent.

The authoritative CLI is deliberately offline and derives the three research-visible
features directly from the exact provenance-bound Binance USD-M BTCUSDT 15m D4
dataset. Historical archive helpers remain in this module for non-authoritative
diagnostic regression only.

The output timestamp is the UTC bar open.  Features become observable only at
the exclusive bar close and therefore must not be used before
``feature_available_at``.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import heapq
import io
import json
import re
import shutil
import stat
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation, localcontext
from itertools import chain
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Iterator, Mapping, TextIO

import pandas as pd

from tools.data_ingestion.takerflow_archive_recon import (
    TradeRow,
    derive_taker_side,
)
from tools.research_domain.feature_data import (
    CANONICAL_KLINE_TAKER_DERIVATION_VERSION,
    CANONICAL_KLINE_TAKER_FEATURE_DEFINITIONS,
    CANONICAL_KLINE_TAKER_PARENT_FIELDS,
    CANONICAL_KLINE_TAKER_SOURCE_CLASS,
    CANONICAL_KLINE_TAKER_TIMEFRAMES,
    D4_TAKER_DERIVATION_VERSION,
    D4_TAKER_FEATURE_DEFINITIONS,
    D4_TAKER_PARENT_FIELDS,
    D4_TAKER_SOURCE_CLASS,
    FEATURE_TABLE_SCHEMA_VERSION,
    build_feature_table_identity,
    build_source_set_identity,
    validate_feature_table_contract,
)
from tools.execution_evidence_contract import content_sha256


MATERIALIZATION_VERSION = "takerflow-completed-bars-v1"
HYDRATION_MANIFEST_VERSION = "binance-usdm-takerflow-hydration-v1"
OUTPUT_SCHEMA_VERSION = "takerflow-feature-table-v1"
SOURCE_POLICY_VERSION = "cpw_binance_raw_trades_partition_source_policy_v1"
CANONICAL_ORDER_VERSION = "cpw_binance_raw_trades_canonical_order_v1"
PARTITION_CACHE_VERSION = "cpw_takerflow_partition_cache_v1"
D4_DATA_SLICE_IDENTITY = (
    "binance_usdtm_btcusdt_ohlcv_15m:sha256:"
    "3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664"
)
D4_NORMALIZED_SHA256 = "c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab"
D4_EXPECTED_ROWS = 220128
D4_COVERAGE_START = "2020-01-01T00:00:00.000Z"
D4_COVERAGE_END = "2026-04-12T00:00:00.000Z"
D4_PROJECTION_SHA256 = "35b29807d6347cb46c552f8b2a1f0f409221d601f9c6a8b503d3d48890de5aba"
CANONICAL_KLINE_PARENT_CONFIG: dict[str, dict[str, Any]] = {
    "30m": {
        "sha256": "05c5857d668d2d12bcc743a13ad92a34590bc1c37ff8ea1f5f54d5d1fbf379ba",
        "row_count": 110064,
        "coverage_start": "2020-01-01T00:00:00.000Z",
        "coverage_end": "2026-04-12T00:00:00.000Z",
        "data_slice_identity": "binance_usdtm_btcusdt_ohlcv_30m:sha256:090f4fac75bedf64fd19dbbeec141169bd7eaeaaaef187038878a6242022b94e",
        "format": "csv",
    },
    "1h": {
        "sha256": "28b750e90ee9957e6fc22811c4ae632355a239f2b958ed65c9b3c56cb2d9e79e",
        "row_count": 55032,
        "coverage_start": "2020-01-01T00:00:00.000Z",
        "coverage_end": "2026-04-12T00:00:00.000Z",
        "data_slice_identity": "binance_usdtm_btcusdt_ohlcv_1h:sha256:9e0faa68eb84b1aa176a5857432840b71a6049765963637236241b91ae807877",
        "format": "csv",
    },
    "4h": {
        "sha256": "828ad4a975c157c7ac4d3c873a39a8b6bbfec3cb306e25eb74209c8a01da6ca1",
        "row_count": 13758,
        "coverage_start": "2020-01-01T00:00:00.000Z",
        "coverage_end": "2026-04-12T00:00:00.000Z",
        "data_slice_identity": "binance_usdtm_btcusdt_ohlcv_4h:sha256:4379d2f0fad5e79bfd5576b308d01fb6134b0f5acf04013e73e00ce33ca96b30",
        "format": "csv",
    },
    "1d": {
        "sha256": "c6e2e7ce030db6a710d95e48325fc77b27efbbdd441199b3d7458d4394795802",
        "row_count": 2293,
        "coverage_start": "2020-01-01T00:00:00.000Z",
        "coverage_end": "2026-04-12T00:00:00.000Z",
        "data_slice_identity": "binance_usdtm_btcusdt_ohlcv_1d:identity_sha256:05ce3d5fdb5186ae36f612e2c51393eaecb110a66b0c3506e5583f3acedd443f",
        "format": "parquet",
    },
}
SUPPORTED_INTERVALS_MS = {
    "15m": 15 * 60_000,
    "30m": 30 * 60_000,
    "1h": 60 * 60_000,
    "4h": 4 * 60 * 60_000,
    "1d": 24 * 60 * 60_000,
}
SUPPORTED_ARCHIVE_TYPES = {"trades", "aggTrades"}
REQUIRED_FEATURES = (
    "taker_buy_volume",
    "taker_sell_volume",
    "taker_buy_sell_ratio",
)
REQUIRED_SOURCE_CLASS = "PUBLIC_TRADE_ARCHIVE_DERIVATION"
REQUIRED_COVERAGE_CLASS = "FULL_HISTORY_PUBLIC_ARCHIVE"
OUTPUT_COLUMNS = (
    "timestamp",
    "open_time_ms",
    "feature_available_at",
    "feature_available_at_ms",
    "taker_buy_volume",
    "taker_sell_volume",
    "taker_total_volume",
    "taker_net_volume",
    "taker_imbalance",
    "taker_buy_sell_ratio",
    "trade_count",
    "source_record_count",
)
D4_OUTPUT_COLUMNS = (
    "timestamp",
    "open_time_ms",
    "feature_available_at",
    "feature_available_at_ms",
    "taker_buy_volume",
    "taker_sell_volume",
    "taker_buy_sell_ratio",
)
TRADES_COLUMNS = (
    "trade_id",
    "price",
    "qty",
    "quote_qty",
    "time",
    "is_buyer_maker",
)
AGGTRADES_COLUMNS = (
    "agg_trade_id",
    "price",
    "quantity",
    "first_trade_id",
    "last_trade_id",
    "transact_time",
    "is_buyer_maker",
)


class TakerflowMaterializationError(ValueError):
    """Raised when local inputs cannot satisfy the materialization contract."""


@dataclass(frozen=True)
class RawTradeRecord:
    """Strict official raw-trade record used by the partition policy."""

    trade_id: int
    price: Decimal
    qty: Decimal
    quote_qty: Decimal
    time: int
    is_buyer_maker: bool


class PartitionQualityError(TakerflowMaterializationError):
    """A source partition failed scientific semantic QA."""

    def __init__(self, reasons: list[str], diagnostics: Mapping[str, Any]):
        self.reasons = tuple(reasons)
        self.diagnostics = dict(diagnostics)
        super().__init__("; ".join(reasons))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _utc_ms(value: str, field: str) -> int:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise TakerflowMaterializationError(f"{field} must be ISO-8601 UTC") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != UTC.utcoffset(parsed):
        raise TakerflowMaterializationError(f"{field} must be ISO-8601 UTC")
    return int(parsed.timestamp() * 1000)


def _iso_ms(timestamp_ms: int) -> str:
    return (
        datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _ratio(numerator: Decimal, denominator: Decimal) -> str | None:
    if denominator == 0:
        return None
    with localcontext() as context:
        context.prec = 38
        return _decimal_text(numerator / denominator)


def _availability_contract(
    path: Path, *, source_class: str = REQUIRED_SOURCE_CLASS
) -> dict[str, Any]:
    if not path.is_file():
        raise TakerflowMaterializationError(f"availability catalog does not exist: {path}")
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TakerflowMaterializationError("availability catalog is unreadable") from exc
    entries = catalog.get("entries", [])
    matched: list[dict[str, Any]] = []
    for feature in REQUIRED_FEATURES:
        matches = [
            entry
            for entry in entries
            if entry.get("feature_name") == feature
            and entry.get("compiler_visible") is True
            and entry.get("source_class") == source_class
            and entry.get("coverage_class") == REQUIRED_COVERAGE_CLASS
        ]
        if not matches and source_class == REQUIRED_SOURCE_CLASS:
            matched.append(
                {
                    "feature_name": feature,
                    "conditions": [
                        "Historical raw-archive reconstruction is diagnostic only.",
                        "It does not determine authoritative RESEARCH-02 feature values.",
                    ],
                }
            )
            continue
        if len(matches) != 1:
            raise TakerflowMaterializationError(
                f"{feature} lacks one approved {source_class} full-history label"
            )
        matched.append(matches[0])
    return {
        "catalog_path": path.as_posix(),
        "catalog_sha256": _sha256(path),
        "coverage_class": REQUIRED_COVERAGE_CLASS,
        "source_class": source_class,
        "features": [
            {
                "feature_name": entry["feature_name"],
                "conditions": entry.get("conditions", []),
            }
            for entry in matched
        ],
    }


def _decimal(value: Any, field: str, row_number: int) -> Decimal:
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, AttributeError) as exc:
        raise TakerflowMaterializationError(
            f"row {row_number}: {field} is not a decimal"
        ) from exc
    if not parsed.is_finite() or parsed <= 0:
        raise TakerflowMaterializationError(
            f"row {row_number}: {field} must be finite and positive"
        )
    return parsed


def _integer(value: Any, field: str, row_number: int, *, positive: bool = False) -> int:
    text = str(value).strip()
    if not re.fullmatch(r"\d+", text):
        raise TakerflowMaterializationError(f"row {row_number}: {field} is not an integer")
    parsed = int(text)
    if positive and parsed <= 0:
        raise TakerflowMaterializationError(
            f"row {row_number}: {field} must be positive"
        )
    return parsed


def _boolean(value: Any, field: str, row_number: int) -> bool:
    text = str(value).strip().lower()
    if text == "true":
        return True
    if text == "false":
        return False
    raise TakerflowMaterializationError(
        f"row {row_number}: {field} must be true or false"
    )


def _archive_rows(path: Path, archive_type: str) -> Iterable[TradeRow]:
    """Yield validated archive rows without loading an archive into memory."""

    required_columns = TRADES_COLUMNS if archive_type == "trades" else AGGTRADES_COLUMNS

    def parse_records(handle: io.TextIOBase) -> Iterable[TradeRow]:
        reader = csv.reader(handle)
        try:
            first = next(reader)
        except StopIteration as exc:
            raise TakerflowMaterializationError("archive contains no rows") from exc
        stripped_first = tuple(value.strip() for value in first)
        canonical_first = tuple(value.lower().replace(" ", "_") for value in stripped_first)
        official_trades_header = ("id", "price", "qty", "quoteQty", "time", "isBuyerMaker")
        official_names = set(official_trades_header)
        header_like = archive_type == "trades" and bool(set(stripped_first) & official_names)
        has_official_trades_header = archive_type == "trades" and stripped_first == official_trades_header
        has_header = set(required_columns).issubset(canonical_first) or header_like
        if has_header:
            if has_official_trades_header:
                header = TRADES_COLUMNS
            elif header_like:
                aliases = {"id": "trade_id", "quoteQty": "quote_qty", "isBuyerMaker": "is_buyer_maker"}
                header = tuple(aliases.get(value, value.lower().replace(" ", "_")) for value in stripped_first)
            else:
                header = canonical_first
            values_iter = reader
            first_row_number = 2
        else:
            header = required_columns
            values_iter = chain([first], reader)
            first_row_number = 1
        if len(header) != len(required_columns) or set(header) != set(required_columns):
            missing = sorted(set(required_columns) - set(header))
            unexpected = sorted(set(header) - set(required_columns))
            raise TakerflowMaterializationError(
                "archive columns do not match required schema; "
                f"missing={missing}, unexpected={unexpected}"
            )
        row_count = 0
        for row_number, values in enumerate(values_iter, start=first_row_number):
            if not values or all(not value.strip() for value in values):
                raise TakerflowMaterializationError(
                    f"row {row_number}: blank rows are not accepted"
                )
            if len(values) != len(header):
                raise TakerflowMaterializationError(
                    f"row {row_number}: expected {len(header)} columns, found {len(values)}"
                )
            raw = dict(zip(header, values, strict=True))
            if archive_type == "trades":
                price = _decimal(raw["price"], "price", row_number)
                quantity = _decimal(raw["qty"], "qty", row_number)
                quote_quantity = _decimal(raw["quote_qty"], "quote_qty", row_number)
                row = TradeRow(
                    event_id=_integer(raw["trade_id"], "trade_id", row_number),
                    timestamp_ms=_integer(raw["time"], "time", row_number, positive=True),
                    price=price,
                    base_quantity=quantity,
                    quote_quantity=quote_quantity,
                    buyer_maker=_boolean(
                        raw["is_buyer_maker"], "is_buyer_maker", row_number
                    ),
                    trade_count=1,
                )
            else:
                price = _decimal(raw["price"], "price", row_number)
                quantity = _decimal(raw["quantity"], "quantity", row_number)
                first_trade_id = _integer(
                    raw["first_trade_id"], "first_trade_id", row_number
                )
                last_trade_id = _integer(
                    raw["last_trade_id"], "last_trade_id", row_number
                )
                if last_trade_id < first_trade_id:
                    raise TakerflowMaterializationError(
                        f"row {row_number}: last_trade_id precedes first_trade_id"
                    )
                row = TradeRow(
                    event_id=_integer(
                        raw["agg_trade_id"], "agg_trade_id", row_number
                    ),
                    timestamp_ms=_integer(
                        raw["transact_time"], "transact_time", row_number, positive=True
                    ),
                    price=price,
                    base_quantity=quantity,
                    quote_quantity=None,
                    buyer_maker=_boolean(
                        raw["is_buyer_maker"], "is_buyer_maker", row_number
                    ),
                    trade_count=last_trade_id - first_trade_id + 1,
                )
            row_count += 1
            yield row
        if row_count == 0:
            raise TakerflowMaterializationError("archive contains no data rows")

    if path.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(path) as archive:
                members = [
                    name
                    for name in archive.namelist()
                    if not name.endswith("/") and name.lower().endswith(".csv")
                ]
                if len(members) != 1:
                    raise TakerflowMaterializationError(
                        "ZIP archive must contain exactly one CSV member"
                    )
                with archive.open(members[0]) as binary:
                    with io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as text:
                        yield from parse_records(text)
        except (zipfile.BadZipFile, UnicodeDecodeError) as exc:
            raise TakerflowMaterializationError(f"cannot read ZIP archive: {path}") from exc
    else:
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as text:
                yield from parse_records(text)
        except UnicodeDecodeError as exc:
            raise TakerflowMaterializationError(
                f"archive CSV is not UTF-8: {path}"
            ) from exc


def _ordered_source_paths(paths: Iterable[Path], archive_type: str) -> list[Path]:
    if archive_type not in SUPPORTED_ARCHIVE_TYPES:
        raise TakerflowMaterializationError("archive_type must be trades or aggTrades")
    ordered_paths = sorted((Path(path) for path in paths), key=lambda path: path.as_posix())
    if not ordered_paths:
        raise TakerflowMaterializationError("at least one local archive is required")
    if len(set(path.resolve() for path in ordered_paths)) != len(ordered_paths):
        raise TakerflowMaterializationError("the same archive path was supplied more than once")
    return ordered_paths


def _missing_bar_ranges(
    observed_open_times: set[int], start_ms: int, end_ms: int, interval_ms: int
) -> list[dict[str, Any]]:
    missing = [
        open_ms
        for open_ms in range(start_ms, end_ms, interval_ms)
        if open_ms not in observed_open_times
    ]
    ranges: list[dict[str, Any]] = []
    for open_ms in missing:
        if not ranges or open_ms != ranges[-1]["last_open_time_ms"] + interval_ms:
            ranges.append(
                {
                    "first_open_time_ms": open_ms,
                    "last_open_time_ms": open_ms,
                    "bar_count": 1,
                }
            )
        else:
            ranges[-1]["last_open_time_ms"] = open_ms
            ranges[-1]["bar_count"] += 1
    for item in ranges:
        item["first_open_time_utc"] = _iso_ms(item["first_open_time_ms"])
        item["last_open_time_utc"] = _iso_ms(item["last_open_time_ms"])
    return ranges


def _feature_rows_from_groups(
    groups: dict[int, dict[str, Any]], interval_ms: int
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for open_ms in sorted(groups):
        group = groups[open_ms]
        buy = group["buy"]
        sell = group["sell"]
        total = buy + sell
        net = buy - sell
        close_ms = open_ms + interval_ms
        output.append(
            {
                "timestamp": _iso_ms(open_ms),
                "open_time_ms": open_ms,
                "feature_available_at": _iso_ms(close_ms),
                "feature_available_at_ms": close_ms,
                "taker_buy_volume": _decimal_text(buy),
                "taker_sell_volume": _decimal_text(sell),
                "taker_total_volume": _decimal_text(total),
                "taker_net_volume": _decimal_text(net),
                "taker_imbalance": _ratio(net, total),
                "taker_buy_sell_ratio": _ratio(buy, sell),
                "trade_count": group["trade_count"],
                "source_record_count": group["source_record_count"],
            }
        )
    return output


def _stream_source_aggregation(
    paths: Iterable[Path],
    *,
    archive_type: str,
    interval_ms: int,
    start_ms: int,
    end_ms: int,
) -> dict[str, Any]:
    """Stream chronologically named partitions into bounded bar aggregates."""

    ordered_paths = _ordered_source_paths(paths, archive_type)
    groups: dict[int, dict[str, Any]] = {}
    source_files: list[dict[str, Any]] = []
    event_gaps: list[dict[str, int]] = []
    previous_unique: TradeRow | None = None
    previous_in_range_event_id: int | None = None
    parsed_count = 0
    duplicate_count = 0
    unique_count = 0
    before_count = 0
    in_range_count = 0
    after_count = 0

    for path in ordered_paths:
        if not path.is_file():
            raise TakerflowMaterializationError(f"local archive does not exist: {path}")
        before_hash = _sha256(path)
        file_row_count = 0
        previous_file_key: tuple[int, int] | None = None
        for row in _archive_rows(path, archive_type):
            file_row_count += 1
            parsed_count += 1
            key = (row.timestamp_ms, row.event_id)
            if previous_file_key is not None and key < previous_file_key:
                raise TakerflowMaterializationError(
                    f"archive timestamps/event IDs are not monotonic: {path}"
                )
            previous_file_key = key

            if previous_unique is not None:
                if row.event_id == previous_unique.event_id:
                    if row == previous_unique:
                        duplicate_count += 1
                        continue
                    raise TakerflowMaterializationError(
                        f"conflicting duplicate event_id {row.event_id}"
                    )
                if (
                    row.event_id < previous_unique.event_id
                    or row.timestamp_ms < previous_unique.timestamp_ms
                ):
                    raise TakerflowMaterializationError(
                        "archive sequence overlaps or is out of chronological/event-ID order; "
                        "only exact adjacent boundary duplicates are accepted"
                    )
            previous_unique = row
            unique_count += 1
            if row.timestamp_ms < start_ms:
                before_count += 1
                continue
            if row.timestamp_ms >= end_ms:
                after_count += 1
                continue

            in_range_count += 1
            if (
                previous_in_range_event_id is not None
                and row.event_id > previous_in_range_event_id + 1
            ):
                event_gaps.append(
                    {
                        "missing_first_event_id": previous_in_range_event_id + 1,
                        "missing_last_event_id": row.event_id - 1,
                        "missing_event_id_count": row.event_id - previous_in_range_event_id - 1,
                    }
                )
            previous_in_range_event_id = row.event_id
            open_ms = row.timestamp_ms - (row.timestamp_ms % interval_ms)
            group = groups.setdefault(
                open_ms,
                {
                    "buy": Decimal(0),
                    "sell": Decimal(0),
                    "trade_count": 0,
                    "source_record_count": 0,
                },
            )
            side = derive_taker_side(row)
            group[side] += row.base_quantity
            group["trade_count"] += row.trade_count
            group["source_record_count"] += 1

        after_hash = _sha256(path)
        if before_hash != after_hash:
            raise TakerflowMaterializationError(f"archive changed while being read: {path}")
        source_files.append(
            {
                "path": path.as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": before_hash,
                "parsed_row_count": file_row_count,
                "source_timestamp_order_monotonic": True,
            }
        )

    return {
        "groups": groups,
        "source_files": source_files,
        "event_gaps": event_gaps,
        "parsed_source_row_count": parsed_count,
        "exact_duplicate_row_count_removed": duplicate_count,
        "unique_source_row_count": unique_count,
        "source_rows_before_requested_range": before_count,
        "source_rows_in_requested_range": in_range_count,
        "source_rows_after_requested_range": after_count,
    }


def build_completed_bar_features(
    rows: Iterable[TradeRow], *, interval: str, start_ms: int, end_ms: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Aggregate rows in ``[start_ms, end_ms)`` and return explicit coverage."""

    interval_ms = SUPPORTED_INTERVALS_MS.get(interval)
    if interval_ms is None:
        raise TakerflowMaterializationError(
            f"interval must be one of {sorted(SUPPORTED_INTERVALS_MS)}"
        )
    if start_ms >= end_ms or start_ms % interval_ms or end_ms % interval_ms:
        raise TakerflowMaterializationError(
            "requested start/end must be increasing UTC interval boundaries"
        )
    materialized_rows = list(rows)
    before_count = sum(row.timestamp_ms < start_ms for row in materialized_rows)
    after_count = sum(row.timestamp_ms >= end_ms for row in materialized_rows)
    selected = [row for row in materialized_rows if start_ms <= row.timestamp_ms < end_ms]
    groups: dict[int, dict[str, Any]] = {}
    for row in selected:
        open_ms = row.timestamp_ms - (row.timestamp_ms % interval_ms)
        group = groups.setdefault(
            open_ms,
            {
                "buy": Decimal(0),
                "sell": Decimal(0),
                "trade_count": 0,
                "source_record_count": 0,
            },
        )
        side = derive_taker_side(row)
        group[side] += row.base_quantity
        group["trade_count"] += row.trade_count
        group["source_record_count"] += 1

    output = _feature_rows_from_groups(groups, interval_ms)
    expected_bar_count = (end_ms - start_ms) // interval_ms
    missing_ranges = _missing_bar_ranges(set(groups), start_ms, end_ms, interval_ms)
    missing_bar_count = sum(item["bar_count"] for item in missing_ranges)
    coverage = {
        "expected_bar_count": expected_bar_count,
        "observed_bar_count": len(output),
        "missing_bar_count": missing_bar_count,
        "missing_bar_ranges": missing_ranges,
        "bar_coverage_fraction": f"{len(output)}/{expected_bar_count}",
        "source_rows_before_requested_range": before_count,
        "source_rows_in_requested_range": len(selected),
        "source_rows_after_requested_range": after_count,
    }
    return output, coverage


def _validate_output_rows(
    rows: list[dict[str, Any]], *, interval_ms: int, start_ms: int, end_ms: int
) -> None:
    previous_open: int | None = None
    for row in rows:
        if tuple(row) != OUTPUT_COLUMNS:
            raise TakerflowMaterializationError("internal output schema/order drift")
        open_ms = row["open_time_ms"]
        if (
            not isinstance(open_ms, int)
            or open_ms < start_ms
            or open_ms >= end_ms
            or open_ms % interval_ms
            or (previous_open is not None and open_ms <= previous_open)
        ):
            raise TakerflowMaterializationError("output timestamps are not aligned and monotonic")
        if (
            row["timestamp"] != _iso_ms(open_ms)
            or row["feature_available_at_ms"] != open_ms + interval_ms
            or row["feature_available_at"] != _iso_ms(open_ms + interval_ms)
        ):
            raise TakerflowMaterializationError("output completed-bar availability is inconsistent")
        buy = Decimal(row["taker_buy_volume"])
        sell = Decimal(row["taker_sell_volume"])
        if (
            Decimal(row["taker_total_volume"]) != buy + sell
            or Decimal(row["taker_net_volume"]) != buy - sell
            or row["trade_count"] <= 0
            or row["source_record_count"] <= 0
        ):
            raise TakerflowMaterializationError("output feature arithmetic is inconsistent")
        previous_open = open_ms


def _write_feature_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _month_bounds(month: datetime) -> tuple[int, int]:
    following = month.replace(
        year=month.year + (1 if month.month == 12 else 0),
        month=1 if month.month == 12 else month.month + 1,
    )
    return int(month.timestamp() * 1000), int(following.timestamp() * 1000)


def _verified_source(path: Path) -> dict[str, Any]:
    checksum_path = path.with_name(path.name + ".CHECKSUM")
    if not path.is_file():
        raise TakerflowMaterializationError(f"required source archive is missing: {path}")
    if not checksum_path.is_file():
        raise TakerflowMaterializationError(
            f"required checksum sidecar is missing: {checksum_path}"
        )
    expected = _checksum_sidecar_digest(checksum_path, path.name)
    actual = _sha256(path)
    if expected is None or actual != expected:
        raise TakerflowMaterializationError(
            f"official checksum verification failed for {path.name}"
        )
    return {
        "path": path.as_posix(),
        "logical_filename": path.name,
        "sha256": actual,
        "size_bytes": path.stat().st_size,
        "checksum_verified": True,
        "checksum_path": checksum_path.as_posix(),
    }


def _raw_trade_csv_values(path: Path) -> Iterator[tuple[int, list[str]]]:
    def rows(handle: TextIO) -> Iterator[tuple[int, list[str]]]:
        reader = csv.reader(handle)
        try:
            first = next(reader)
        except StopIteration as exc:
            raise TakerflowMaterializationError(f"archive contains no rows: {path}") from exc
        stripped = tuple(value.strip() for value in first)
        canonical = tuple(value.lower().replace(" ", "_") for value in stripped)
        official = ("id", "price", "qty", "quoteQty", "time", "isBuyerMaker")
        header_like = bool(set(stripped) & set(official))
        has_header = set(TRADES_COLUMNS).issubset(canonical) or header_like
        if has_header:
            if stripped == official:
                header = TRADES_COLUMNS
            elif header_like:
                aliases = {"id": "trade_id", "quoteQty": "quote_qty", "isBuyerMaker": "is_buyer_maker"}
                header = tuple(aliases.get(value, value.lower().replace(" ", "_")) for value in stripped)
            else:
                header = canonical
            values_iter: Iterable[list[str]] = reader
            first_number = 2
        else:
            header = TRADES_COLUMNS
            values_iter = chain([first], reader)
            first_number = 1
        if len(header) != len(TRADES_COLUMNS) or set(header) != set(TRADES_COLUMNS):
            raise TakerflowMaterializationError(
                f"archive columns do not match strict raw trades schema: {path}"
            )
        indexes = [header.index(name) for name in TRADES_COLUMNS]
        count = 0
        for row_number, values in enumerate(values_iter, start=first_number):
            if not values or all(not value.strip() for value in values):
                raise TakerflowMaterializationError(
                    f"{path.name} row {row_number}: blank rows are not accepted"
                )
            if len(values) != len(header):
                raise TakerflowMaterializationError(
                    f"{path.name} row {row_number}: expected {len(header)} columns, found {len(values)}"
                )
            count += 1
            yield row_number, [values[index] for index in indexes]
        if count == 0:
            raise TakerflowMaterializationError(f"archive contains no data rows: {path}")

    if path.suffix.lower() != ".zip":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            yield from rows(handle)
        return
    try:
        with zipfile.ZipFile(path) as archive:
            members = [
                name
                for name in archive.namelist()
                if not name.endswith("/") and name.lower().endswith(".csv")
            ]
            if len(members) != 1:
                raise TakerflowMaterializationError(
                    f"ZIP archive must contain exactly one CSV member: {path}"
                )
            with archive.open(members[0]) as binary:
                with io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as handle:
                    yield from rows(handle)
    except (zipfile.BadZipFile, UnicodeDecodeError) as exc:
        raise TakerflowMaterializationError(f"cannot read ZIP archive: {path}") from exc


def _strict_raw_trade(values: list[str], row_number: int, path: Path) -> RawTradeRecord:
    try:
        trade_id = _integer(values[0], "trade_id", row_number)
        price = _decimal(values[1], "price", row_number)
        qty = _decimal(values[2], "qty", row_number)
        quote_qty = _decimal(values[3], "quote_qty", row_number)
        time = _integer(values[4], "time", row_number, positive=True)
        is_buyer_maker = _boolean(values[5], "is_buyer_maker", row_number)
    except TakerflowMaterializationError as exc:
        raise TakerflowMaterializationError(f"{path.name}: {exc}") from exc
    return RawTradeRecord(
        trade_id=trade_id,
        price=price,
        qty=qty,
        quote_qty=quote_qty,
        time=time,
        is_buyer_maker=is_buyer_maker,
    )


def _record_text(record: RawTradeRecord) -> str:
    return "\t".join(
        (
            str(record.time),
            str(record.trade_id),
            _decimal_text(record.price),
            _decimal_text(record.qty),
            _decimal_text(record.quote_qty),
            "1" if record.is_buyer_maker else "0",
        )
    )


def _record_from_text(text: str) -> RawTradeRecord:
    values = text.rstrip("\n").split("\t")
    if len(values) != 6:
        raise TakerflowMaterializationError("corrupt external-sort scratch row")
    return RawTradeRecord(
        time=int(values[0]),
        trade_id=int(values[1]),
        price=Decimal(values[2]),
        qty=Decimal(values[3]),
        quote_qty=Decimal(values[4]),
        is_buyer_maker=values[5] == "1",
    )


def _canonical_record_stream(
    paths: list[Path], scratch_root: Path, *, chunk_rows: int = 500_000
) -> tuple[Iterator[RawTradeRecord], dict[str, Any], list[Path]]:
    """External-sort strict records by the locked canonical key."""

    scratch_root.mkdir(parents=True, exist_ok=True)
    if chunk_rows <= 0:
        raise TakerflowMaterializationError("chunk_rows must be positive")
    chunks: list[Path] = []
    buffer: list[RawTradeRecord] = []
    parsed_by_file: dict[str, int] = {}
    physical_previous: tuple[int, int] | None = None
    inversion_count = 0
    first_inversion: dict[str, Any] | None = None

    def spill() -> None:
        if not buffer:
            return
        buffer.sort(key=lambda item: (item.time, item.trade_id))
        chunk = scratch_root / f"chunk-{len(chunks):06d}.tsv"
        with chunk.open("w", encoding="utf-8", newline="\n") as handle:
            for record in buffer:
                handle.write(_record_text(record) + "\n")
        chunks.append(chunk)
        buffer.clear()

    for path in paths:
        count = 0
        for row_number, values in _raw_trade_csv_values(path):
            record = _strict_raw_trade(values, row_number, path)
            key = (record.time, record.trade_id)
            if physical_previous is not None and key < physical_previous:
                inversion_count += 1
                if first_inversion is None:
                    first_inversion = {
                        "previous": list(physical_previous),
                        "current": list(key),
                        "logical_filename": path.name,
                        "row_number": row_number,
                    }
            physical_previous = key
            count += 1
            buffer.append(record)
            if len(buffer) >= chunk_rows:
                spill()
        parsed_by_file[path.name] = count
    spill()
    if not chunks:
        raise TakerflowMaterializationError("source partition contains no raw trades rows")

    handles = [chunk.open("r", encoding="utf-8", newline="") for chunk in chunks]

    def merged() -> Iterator[RawTradeRecord]:
        heap: list[tuple[int, int, int, RawTradeRecord]] = []
        try:
            for index, handle in enumerate(handles):
                line = handle.readline()
                if line:
                    record = _record_from_text(line)
                    heap.append((record.time, record.trade_id, index, record))
            heapq.heapify(heap)
            while heap:
                _, _, index, record = heapq.heappop(heap)
                yield record
                line = handles[index].readline()
                if line:
                    following = _record_from_text(line)
                    heapq.heappush(
                        heap,
                        (following.time, following.trade_id, index, following),
                    )
        finally:
            for handle in handles:
                handle.close()

    diagnostics = {
        "physical_row_order_monotonic": inversion_count == 0,
        "out_of_order_pair_count": inversion_count,
        "first_observed_inversion": first_inversion,
        "source_parsed_row_count": sum(parsed_by_file.values()),
        "parsed_row_count_by_file": parsed_by_file,
        "canonical_run_count": len(chunks),
        "canonical_run_max_rows": chunk_rows,
    }
    return merged(), diagnostics, chunks


def _scan_physical_source(
    paths: list[Path], *, on_record: Callable[[RawTradeRecord], None] | None = None
) -> dict[str, Any]:
    """Strictly parse once to diagnose whether external sorting is necessary."""

    parsed_by_file: dict[str, int] = {}
    previous: tuple[int, int] | None = None
    inversion_count = 0
    first_inversion: dict[str, Any] | None = None
    for path in paths:
        count = 0
        for row_number, values in _raw_trade_csv_values(path):
            record = _strict_raw_trade(values, row_number, path)
            key = (record.time, record.trade_id)
            if previous is not None and key < previous:
                inversion_count += 1
                if first_inversion is None:
                    first_inversion = {
                        "previous": list(previous),
                        "current": list(key),
                        "logical_filename": path.name,
                        "row_number": row_number,
                    }
            if on_record is not None and inversion_count == 0:
                on_record(record)
            previous = key
            count += 1
        parsed_by_file[path.name] = count
    return {
        "physical_row_order_monotonic": inversion_count == 0,
        "out_of_order_pair_count": inversion_count,
        "first_observed_inversion": first_inversion,
        "source_parsed_row_count": sum(parsed_by_file.values()),
        "parsed_row_count_by_file": parsed_by_file,
    }


def _direct_record_stream(paths: list[Path]) -> Iterator[RawTradeRecord]:
    for path in paths:
        for row_number, values in _raw_trade_csv_values(path):
            yield _strict_raw_trade(values, row_number, path)


def _load_d4_oracle(
    path: Path,
    *,
    expected_sha256: str = D4_NORMALIZED_SHA256,
    expected_rows: int = D4_EXPECTED_ROWS,
) -> tuple[dict[int, tuple[Decimal, int, Decimal]], dict[str, Any]]:
    if not path.is_file():
        raise TakerflowMaterializationError(f"D4 normalized input is missing: {path}")
    digest = _sha256(path)
    if digest != expected_sha256:
        raise TakerflowMaterializationError(
            f"D4 normalized SHA-256 mismatch: expected {expected_sha256}, observed {digest}"
        )
    oracle: dict[int, tuple[Decimal, int, Decimal]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row_number, row in enumerate(csv.DictReader(handle), start=2):
            try:
                open_ms = int(row["open_time_ms"])
                volume = Decimal(row["volume"])
                trades = int(row["num_trades"])
                taker_buy = Decimal(row["taker_buy_base_vol"])
            except (KeyError, ValueError, InvalidOperation) as exc:
                raise TakerflowMaterializationError(
                    f"D4 row {row_number} violates the exact reconciliation schema"
                ) from exc
            if open_ms in oracle:
                raise TakerflowMaterializationError("D4 contains duplicate open_time_ms")
            oracle[open_ms] = (volume, trades, taker_buy)
    if len(oracle) != expected_rows:
        raise TakerflowMaterializationError(
            f"D4 row count mismatch: expected {expected_rows}, observed {len(oracle)}"
        )
    return oracle, {"sha256": digest, "row_count": len(oracle)}


def _partition_identity_inputs(
    *,
    month_key: str,
    source_mode: str,
    source_files: list[dict[str, Any]],
    source_row_count: int,
    canonical_unique_row_count: int,
    trade_id_gap_range_count: int,
    absent_trade_id_count: int,
    trade_id_gap_ranges_sha256: str,
    canonical_record_sha256: str,
    canonical_run_merge_identity: str,
    d4_mismatch_counts: Mapping[str, int],
    d4_normalized_sha256: str,
    coverage_start: str,
    coverage_end: str,
) -> dict[str, Any]:
    return {
        "partition_identity_version": PARTITION_CACHE_VERSION,
        "source_policy_version": SOURCE_POLICY_VERSION,
        "canonical_order_version": CANONICAL_ORDER_VERSION,
        "symbol": "BTCUSDT",
        "market": "Binance USD-M perpetual",
        "archive_type": "trades",
        "utc_year_month": month_key,
        "source_mode": source_mode,
        "consumed_sources": [
            {
                "logical_filename": item["logical_filename"],
                "sha256": item["sha256"],
                "size_bytes": item["size_bytes"],
                "checksum_verified": item["checksum_verified"],
            }
            for item in source_files
        ],
        "materialization_version": MATERIALIZATION_VERSION,
        "output_schema_version": OUTPUT_SCHEMA_VERSION,
        "interval": "15m",
        "interval_contract": "UTC [bar_open,bar_close); available at exclusive close",
        "source_row_count": source_row_count,
        "canonical_unique_row_count": canonical_unique_row_count,
        "trade_id_gap_range_count": trade_id_gap_range_count,
        "absent_trade_id_count": absent_trade_id_count,
        "trade_id_gap_ranges_sha256": trade_id_gap_ranges_sha256,
        "canonical_record_sha256": canonical_record_sha256,
        "canonical_run_merge_identity": canonical_run_merge_identity,
        "d4_reconciliation": {
            "data_slice_identity": D4_DATA_SLICE_IDENTITY,
            "normalized_sha256": d4_normalized_sha256,
            "mismatch_counts": dict(d4_mismatch_counts),
        },
        "accepted_feature_names": list(REQUIRED_FEATURES),
        "coverage": {
            "start_utc_inclusive": coverage_start,
            "end_utc_exclusive": coverage_end,
        },
    }


def _build_raw_trade_partition(
    *,
    month: datetime,
    source_mode: str,
    source_files: list[dict[str, Any]],
    output_path: Path,
    manifest_path: Path,
    scratch_parent: Path,
    d4_oracle: Mapping[int, tuple[Decimal, int, Decimal]],
    d4_meta: Mapping[str, Any],
    requested_start_ms: int,
    requested_end_ms: int,
    rejected_monthly_source: Mapping[str, Any] | None = None,
    chunk_rows: int = 500_000,
) -> dict[str, Any]:
    month_start, month_end = _month_bounds(month)
    output_start = max(month_start, requested_start_ms)
    output_end = min(month_end, requested_end_ms)
    month_key = month.strftime("%Y-%m")
    if output_start >= output_end:
        raise TakerflowMaterializationError(f"empty requested coverage for {month_key}")
    diagnostics: dict[str, Any]
    groups: dict[int, dict[str, Any]]
    seen_days: set[int]
    previous: RawTradeRecord | None
    unique_count: int
    first_record: RawTradeRecord | None
    last_record: RawTradeRecord | None
    canonical_digest: Any

    def reset_accumulator() -> None:
        nonlocal diagnostics, groups, seen_days, previous, unique_count
        nonlocal first_record, last_record, canonical_digest
        diagnostics = {
            "duplicate_trade_id_count": 0,
            "conflicting_duplicate_count": 0,
            "trade_id_gap_range_count": 0,
            "absent_trade_id_count": 0,
            "trade_id_gap_ranges": [],
            "backwards_or_overlap_count": 0,
            "zero_or_invalid_price_count": 0,
            "zero_or_invalid_quantity_count": 0,
            "timestamp_inconsistency_count": 0,
            "out_of_month_row_count": 0,
        }
        groups = {}
        seen_days = set()
        previous = None
        unique_count = 0
        first_record = None
        last_record = None
        canonical_digest = hashlib.sha256()

    def consume(record: RawTradeRecord) -> None:
        nonlocal previous, unique_count, first_record, last_record
        canonical_digest.update((_record_text(record) + "\n").encode("utf-8"))
        if record.time < month_start or record.time >= month_end:
            diagnostics["out_of_month_row_count"] += 1
            return
        seen_days.add(datetime.fromtimestamp(record.time / 1000, tz=UTC).day)
        if previous is not None:
            if record.trade_id == previous.trade_id:
                diagnostics["duplicate_trade_id_count"] += 1
                if record != previous:
                    diagnostics["conflicting_duplicate_count"] += 1
            elif record.trade_id > previous.trade_id + 1:
                missing = record.trade_id - previous.trade_id - 1
                diagnostics["trade_id_gap_range_count"] += 1
                diagnostics["absent_trade_id_count"] += missing
                diagnostics["trade_id_gap_ranges"].append(
                    {"first": previous.trade_id + 1, "last": record.trade_id - 1}
                )
            elif record.trade_id < previous.trade_id:
                diagnostics["backwards_or_overlap_count"] += 1
            if record.time < previous.time:
                diagnostics["timestamp_inconsistency_count"] += 1
        previous = record
        first_record = first_record or record
        last_record = record
        unique_count += 1
        if output_start <= record.time < output_end:
            open_ms = record.time - (record.time % SUPPORTED_INTERVALS_MS["15m"])
            group = groups.setdefault(
                open_ms,
                {
                    "buy": Decimal(0),
                    "sell": Decimal(0),
                    "trade_count": 0,
                    "source_record_count": 0,
                },
            )
            group["sell" if record.is_buyer_maker else "buy"] += record.qty
            group["trade_count"] += 1
            group["source_record_count"] += 1

    reset_accumulator()
    paths = [Path(item["path"]) for item in source_files]
    with tempfile.TemporaryDirectory(prefix=f"{month_key}-", dir=scratch_parent) as scratch:
        try:
            physical = _scan_physical_source(paths, on_record=consume)
            if not physical["physical_row_order_monotonic"]:
                reset_accumulator()
                records, sorted_physical, _ = _canonical_record_stream(
                    paths, Path(scratch), chunk_rows=chunk_rows
                )
                if {
                    key: sorted_physical[key]
                    for key in (
                        "physical_row_order_monotonic",
                        "out_of_order_pair_count",
                        "first_observed_inversion",
                        "source_parsed_row_count",
                        "parsed_row_count_by_file",
                    )
                } != physical:
                    raise TakerflowMaterializationError(
                        "source changed between physical-order scan and canonicalization"
                    )
                physical["canonical_run_count"] = sorted_physical["canonical_run_count"]
                physical["canonical_run_max_rows"] = sorted_physical[
                    "canonical_run_max_rows"
                ]
                for record in records:
                    consume(record)
            else:
                physical["canonical_run_count"] = 1
                physical["canonical_run_max_rows"] = None
            diagnostics.update(physical)
            diagnostics["canonical_order_mode"] = (
                "direct_stream" if physical["physical_row_order_monotonic"] else "bounded_external_merge"
            )
            diagnostics["canonical_run_merge_identity"] = content_sha256(
                {
                    "canonical_order_version": CANONICAL_ORDER_VERSION,
                    "canonical_key": ["time", "trade_id"],
                    "mode": diagnostics["canonical_order_mode"],
                    "source_files": [
                        {key: item[key] for key in ("logical_filename", "sha256", "size_bytes")}
                        for item in source_files
                    ],
                    "source_parsed_row_count": physical["source_parsed_row_count"],
                    "canonical_run_count": physical["canonical_run_count"],
                    "canonical_run_max_rows": physical["canonical_run_max_rows"],
                    "out_of_order_pair_count": physical["out_of_order_pair_count"],
                }
            )
        except TakerflowMaterializationError as exc:
            diagnostics.setdefault("source_parsed_row_count", 0)
            raise PartitionQualityError([str(exc)], diagnostics) from exc

    expected_days = set(range(1, calendar.monthrange(month.year, month.month)[1] + 1))
    missing_days = sorted(expected_days - seen_days)
    diagnostics.update(
        {
            "canonical_unique_row_count": unique_count,
            "first_trade_id": first_record.trade_id if first_record else None,
            "last_trade_id": last_record.trade_id if last_record else None,
            "calendar_days_with_records": len(seen_days),
            "missing_utc_days": [f"{month_key}-{day:02d}" for day in missing_days],
            "trade_id_gap_ranges_sha256": content_sha256(diagnostics["trade_id_gap_ranges"]),
            "canonical_record_sha256": canonical_digest.hexdigest(),
            "canonical_output_row_count": unique_count,
            "canonical_rows_added_removed_changed": 0,
        }
    )
    reasons: list[str] = []
    for key in (
        "duplicate_trade_id_count",
        "conflicting_duplicate_count",
        "backwards_or_overlap_count",
        "timestamp_inconsistency_count",
        "out_of_month_row_count",
    ):
        if diagnostics[key]:
            reasons.append(f"{key}={diagnostics[key]}")
    if missing_days:
        reasons.append("missing_utc_days=" + ",".join(diagnostics["missing_utc_days"]))
    if not first_record:
        reasons.append("source partition has no accepted records")
    if reasons:
        raise PartitionQualityError(reasons, diagnostics)

    rows = _feature_rows_from_groups(groups, SUPPORTED_INTERVALS_MS["15m"])
    _validate_output_rows(
        rows,
        interval_ms=SUPPORTED_INTERVALS_MS["15m"],
        start_ms=output_start,
        end_ms=output_end,
    )
    missing_bars = _missing_bar_ranges(set(groups), output_start, output_end, SUPPORTED_INTERVALS_MS["15m"])
    if missing_bars:
        raise PartitionQualityError(
            [f"missing_15m_bar_count={sum(item['bar_count'] for item in missing_bars)}"],
            {**diagnostics, "missing_bar_ranges": missing_bars},
        )
    mismatch = {"volume": 0, "trade_count": 0, "taker_buy": 0, "taker_sell": 0}
    for row in rows:
        expected = d4_oracle.get(row["open_time_ms"])
        if expected is None:
            mismatch["volume"] += 1
            mismatch["trade_count"] += 1
            mismatch["taker_buy"] += 1
            mismatch["taker_sell"] += 1
            continue
        volume, trades, taker_buy = expected
        buy = Decimal(row["taker_buy_volume"])
        sell = Decimal(row["taker_sell_volume"])
        if buy + sell != volume:
            mismatch["volume"] += 1
        if row["trade_count"] != trades:
            mismatch["trade_count"] += 1
        if buy != taker_buy:
            mismatch["taker_buy"] += 1
        if sell != volume - taker_buy:
            mismatch["taker_sell"] += 1
    diagnostics["d4_reconciliation_mismatch_counts"] = mismatch
    diagnostics["output_15m_row_count"] = len(rows)
    if any(mismatch.values()):
        raise PartitionQualityError(
            [
                "D4_RECONCILIATION_BLOCKER: "
                + ", ".join(f"{key}={value}" for key, value in mismatch.items())
            ],
            diagnostics,
        )

    _write_feature_csv(output_path, rows)
    for item in source_files:
        item["parsed_row_count"] = diagnostics["parsed_row_count_by_file"][item["logical_filename"]]
    identity_inputs = _partition_identity_inputs(
        month_key=month_key,
        source_mode=source_mode,
        source_files=source_files,
        source_row_count=diagnostics["source_parsed_row_count"],
        canonical_unique_row_count=unique_count,
        trade_id_gap_range_count=diagnostics["trade_id_gap_range_count"],
        absent_trade_id_count=diagnostics["absent_trade_id_count"],
        trade_id_gap_ranges_sha256=diagnostics["trade_id_gap_ranges_sha256"],
        canonical_record_sha256=diagnostics["canonical_record_sha256"],
        canonical_run_merge_identity=diagnostics["canonical_run_merge_identity"],
        d4_mismatch_counts=mismatch,
        d4_normalized_sha256=str(d4_meta["sha256"]),
        coverage_start=_iso_ms(output_start),
        coverage_end=_iso_ms(output_end),
    )
    manifest = {
        "partition_cache_version": PARTITION_CACHE_VERSION,
        "source_policy_version": SOURCE_POLICY_VERSION,
        "canonical_order_version": CANONICAL_ORDER_VERSION,
        "partition_identity_inputs": identity_inputs,
        "partition_identity": content_sha256(identity_inputs),
        "utc_year_month": month_key,
        "source_mode": source_mode,
        "consumed_source_files": source_files,
        "rejected_monthly_source": dict(rejected_monthly_source) if rejected_monthly_source else None,
        "source_diagnostics": diagnostics,
        "coverage": {
            "start_utc_inclusive": _iso_ms(output_start),
            "end_utc_exclusive": _iso_ms(output_end),
            "row_count": len(rows),
            "missing_bar_count": 0,
            "completed_bar_only": True,
        },
        "d4_reconciliation": {
            "data_slice_identity": D4_DATA_SLICE_IDENTITY,
            "normalized_sha256": d4_meta["sha256"],
            "normalized_row_count": d4_meta["row_count"],
            "mismatch_counts": mismatch,
        },
        "output": {
            "path": output_path.as_posix(),
            "sha256": _sha256(output_path),
            "size_bytes": output_path.stat().st_size,
            "row_count": len(rows),
            "columns": list(OUTPUT_COLUMNS),
        },
        "network_used": False,
        "authority": "non-authoritative local research feature partition",
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return manifest


def _daily_paths(daily_root: Path, month: datetime, symbol: str) -> list[Path]:
    return [
        daily_root / f"{symbol}-trades-{month:%Y-%m}-{day:02d}.zip"
        for day in range(1, calendar.monthrange(month.year, month.month)[1] + 1)
    ]


def _read_json_object(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _reuse_partition(
    *,
    month: datetime,
    monthly_path: Path,
    daily_root: Path,
    output_path: Path,
    manifest_path: Path,
    d4_meta: Mapping[str, Any],
) -> dict[str, Any] | None:
    manifest = _read_json_object(manifest_path)
    if manifest is None or not output_path.is_file():
        return None
    if (
        manifest.get("partition_cache_version") != PARTITION_CACHE_VERSION
        or manifest.get("source_policy_version") != SOURCE_POLICY_VERSION
        or manifest.get("canonical_order_version") != CANONICAL_ORDER_VERSION
        or manifest.get("utc_year_month") != month.strftime("%Y-%m")
    ):
        return None
    source_mode = manifest.get("source_mode")
    if source_mode == "monthly":
        try:
            _verified_source(monthly_path)
        except TakerflowMaterializationError:
            return None
        source_paths = [monthly_path]
    elif source_mode == "daily_union":
        rejected = manifest.get("rejected_monthly_source")
        if not isinstance(rejected, Mapping):
            return None
        try:
            current_monthly = _verified_source(monthly_path)
        except TakerflowMaterializationError:
            current_monthly = None
        recorded_sha = rejected.get("sha256")
        if (
            (isinstance(recorded_sha, str) and (
                current_monthly is None or current_monthly["sha256"] != recorded_sha
            ))
            or (recorded_sha is None and current_monthly is not None)
        ):
            return None
        source_paths = _daily_paths(daily_root, month, "BTCUSDT")
    else:
        return None
    try:
        current_sources = [_verified_source(path) for path in source_paths]
    except TakerflowMaterializationError:
        return None
    recorded_sources = manifest.get("consumed_source_files")
    if not isinstance(recorded_sources, list) or len(recorded_sources) != len(current_sources):
        return None
    parsed_counts: dict[str, int] = {}
    for recorded in recorded_sources:
        if not isinstance(recorded, Mapping) or not isinstance(recorded.get("parsed_row_count"), int):
            return None
        parsed_counts[str(recorded.get("logical_filename"))] = recorded["parsed_row_count"]
    for current in current_sources:
        current["parsed_row_count"] = parsed_counts.get(current["logical_filename"])
        if current["parsed_row_count"] is None:
            return None
    stable_keys = (
        "logical_filename",
        "sha256",
        "size_bytes",
        "checksum_verified",
        "parsed_row_count",
    )
    if [
        {key: item.get(key) for key in stable_keys} for item in recorded_sources
    ] != [{key: item.get(key) for key in stable_keys} for item in current_sources]:
        return None
    inputs = manifest.get("partition_identity_inputs")
    diagnostics = manifest.get("source_diagnostics")
    coverage = manifest.get("coverage")
    if not isinstance(inputs, Mapping) or not isinstance(diagnostics, Mapping) or not isinstance(coverage, Mapping):
        return None
    expected_inputs = _partition_identity_inputs(
        month_key=month.strftime("%Y-%m"),
        source_mode=source_mode,
        source_files=current_sources,
        source_row_count=diagnostics.get("source_parsed_row_count"),
        canonical_unique_row_count=diagnostics.get("canonical_unique_row_count"),
        trade_id_gap_range_count=diagnostics.get("trade_id_gap_range_count"),
        absent_trade_id_count=diagnostics.get("absent_trade_id_count"),
        trade_id_gap_ranges_sha256=diagnostics.get("trade_id_gap_ranges_sha256"),
        canonical_record_sha256=diagnostics.get("canonical_record_sha256"),
        canonical_run_merge_identity=diagnostics.get("canonical_run_merge_identity"),
        d4_mismatch_counts=manifest.get("d4_reconciliation", {}).get(
            "mismatch_counts", {}
        ),
        d4_normalized_sha256=str(d4_meta["sha256"]),
        coverage_start=coverage.get("start_utc_inclusive"),
        coverage_end=coverage.get("end_utc_exclusive"),
    )
    if dict(inputs) != expected_inputs or manifest.get("partition_identity") != content_sha256(expected_inputs):
        return None
    output = manifest.get("output")
    if not isinstance(output, Mapping):
        return None
    if (
        output.get("sha256") != _sha256(output_path)
        or output.get("size_bytes") != output_path.stat().st_size
    ):
        return None
    with output_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return None
        row_count = sum(1 for _ in reader)
    if header != list(OUTPUT_COLUMNS) or row_count != output.get("row_count"):
        return None
    d4 = manifest.get("d4_reconciliation")
    if not isinstance(d4, Mapping) or (
        d4.get("data_slice_identity") != D4_DATA_SLICE_IDENTITY
        or d4.get("normalized_sha256") != d4_meta["sha256"]
        or d4.get("normalized_row_count") != d4_meta["row_count"]
        or any(d4.get("mismatch_counts", {}).values())
    ):
        return None
    return manifest


def _source_identity_context(
    partitions: list[Mapping[str, Any]],
    *,
    boundary_trade_id_gaps: list[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "source_policy_version": SOURCE_POLICY_VERSION,
        "canonical_order_version": CANONICAL_ORDER_VERSION,
        "boundary_trade_id_gap_range_count": len(boundary_trade_id_gaps),
        "boundary_absent_trade_id_count": sum(
            item["last"] - item["first"] + 1 for item in boundary_trade_id_gaps
        ),
        "boundary_trade_id_gap_ranges_sha256": content_sha256(
            boundary_trade_id_gaps
        ),
        "partitions": [
            {
                "utc_year_month": item["utc_year_month"],
                "source_mode": item["source_mode"],
                "partition_identity": item["partition_identity"],
            }
            for item in partitions
        ],
    }


def _assemble_partitioned_output(
    *,
    partitions: list[dict[str, Any]],
    output_path: Path,
    manifest_path: Path,
    availability_catalog_path: Path,
    start_ms: int,
    end_ms: int,
    d4_meta: Mapping[str, Any],
) -> dict[str, Any]:
    if not partitions:
        raise TakerflowMaterializationError("no validated partitions to assemble")
    partitions = sorted(partitions, key=lambda item: item["utc_year_month"])
    previous: Mapping[str, Any] | None = None
    boundary_trade_id_gaps: list[dict[str, Any]] = []
    for partition in partitions:
        diagnostics = partition["source_diagnostics"]
        if previous is not None:
            prior = previous["source_diagnostics"]
            if diagnostics["first_trade_id"] <= prior["last_trade_id"]:
                raise TakerflowMaterializationError(
                    "DATA_QUALITY_BLOCKER: raw trade-ID duplicate/backwards overlap across accepted months"
                )
            if diagnostics["first_trade_id"] > prior["last_trade_id"] + 1:
                boundary_trade_id_gaps.append(
                    {
                        "previous_month": previous["utc_year_month"],
                        "next_month": partition["utc_year_month"],
                        "first": prior["last_trade_id"] + 1,
                        "last": diagnostics["first_trade_id"] - 1,
                    }
                )
        previous = partition
    output_path.parent.mkdir(parents=True, exist_ok=True)
    row_count = 0
    prior_open: int | None = None
    with output_path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target, lineterminator="\n")
        writer.writerow(OUTPUT_COLUMNS)
        for partition in partitions:
            source = Path(partition["output"]["path"])
            if _sha256(source) != partition["output"]["sha256"]:
                raise TakerflowMaterializationError("CACHE_INTEGRITY_BLOCKER: partition bytes changed")
            with source.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames != list(OUTPUT_COLUMNS):
                    raise TakerflowMaterializationError("partition output schema changed")
                for row in reader:
                    open_ms = int(row["open_time_ms"])
                    if prior_open is not None and open_ms != prior_open + SUPPORTED_INTERVALS_MS["15m"]:
                        raise TakerflowMaterializationError("final feature grid is not exact 15m UTC")
                    writer.writerow([row[column] for column in OUTPUT_COLUMNS])
                    prior_open = open_ms
                    row_count += 1
    expected_rows = (end_ms - start_ms) // SUPPORTED_INTERVALS_MS["15m"]
    if row_count != expected_rows:
        raise TakerflowMaterializationError(
            f"final feature row count mismatch: expected {expected_rows}, observed {row_count}"
        )
    accepted_sources = [
        source
        for partition in partitions
        for source in partition["consumed_source_files"]
    ]
    stable_sources = [
        {
            "logical_filename": item["logical_filename"],
            "sha256": item["sha256"],
            "size_bytes": item["size_bytes"],
            "parsed_row_count": item["parsed_row_count"],
            "source_type": "trades",
        }
        for item in accepted_sources
    ]
    context = _source_identity_context(
        partitions, boundary_trade_id_gaps=boundary_trade_id_gaps
    )
    availability = _availability_contract(availability_catalog_path)
    output_sha = _sha256(output_path)
    source_set_identity = build_source_set_identity(stable_sources, identity_context=context)
    research_feature_table = {
        "schema_version": FEATURE_TABLE_SCHEMA_VERSION,
        "family_id": "binance_usdm_takerflow_v1",
        "market_identity": {"venue": "Binance", "market_type": "USD-M perpetual", "symbol": "BTCUSDT"},
        "timeframe": "15m",
        "feature_names": list(REQUIRED_FEATURES),
        "source_class": REQUIRED_SOURCE_CLASS,
        "availability_assertions": [
            {
                "feature_name": item["feature_name"],
                "source_class": REQUIRED_SOURCE_CLASS,
                "condition_assertions": list(item["conditions"]),
            }
            for item in availability["features"]
        ],
        "source_set_identity": source_set_identity,
        "output_identity": {
            "format": "CSV UTF-8 LF",
            "sha256": output_sha,
            "row_count": row_count,
            "columns": list(OUTPUT_COLUMNS),
        },
        "coverage": {
            "start_utc_inclusive": _iso_ms(start_ms),
            "end_utc_exclusive": _iso_ms(end_ms),
            "expected_row_count": expected_rows,
            "observed_row_count": row_count,
            "complete": True,
        },
        "causality": {
            "timestamp_semantics": "UTC bar open",
            "feature_available_at_semantics": "exclusive bar close",
            "completed_bar_only": True,
            "future_events_can_change_prior_completed_bars": False,
        },
        "quality_policy": {
            "fill": "forbidden",
            "forward_fill": "forbidden",
            "backfill": "forbidden",
            "interpolation": "forbidden",
            "timestamp_tolerance": "forbidden",
            "missing_row": "fail_closed",
            "duplicate_join_key": "fail_closed",
        },
        "feature_table_identity": "",
        "non_authority": {
            "authorizes_execution": False,
            "authorizes_result_population": False,
            "authorizes_candidate": False,
            "authorizes_promotion": False,
            "authorizes_runtime_paper_live": False,
            "authorizes_oms_risk_reconciliation": False,
        },
    }
    research_feature_table["feature_table_identity"] = build_feature_table_identity(research_feature_table)
    validate_feature_table_contract(
        research_feature_table,
        source_files=stable_sources,
        source_identity_context=context,
    )
    mode_counts = {
        "monthly": sum(item["source_mode"] == "monthly" for item in partitions),
        "daily_union": sum(item["source_mode"] == "daily_union" for item in partitions),
    }
    partition_gap_ranges = [
        gap
        for partition in partitions
        for gap in partition["source_diagnostics"]["trade_id_gap_ranges"]
    ]
    all_trade_id_gap_ranges = [*partition_gap_ranges, *boundary_trade_id_gaps]
    trade_id_gap_range_count = len(all_trade_id_gap_ranges)
    absent_trade_id_count = sum(
        item["last"] - item["first"] + 1 for item in all_trade_id_gap_ranges
    )
    manifest = {
        "materialization_version": MATERIALIZATION_VERSION,
        "output_schema_version": OUTPUT_SCHEMA_VERSION,
        "source_policy_version": SOURCE_POLICY_VERSION,
        "canonical_order_version": CANONICAL_ORDER_VERSION,
        "partition_cache_version": PARTITION_CACHE_VERSION,
        "symbol": "BTCUSDT",
        "market": "Binance USD-M perpetual",
        "archive_type": "trades",
        "request": {
            "start_utc_inclusive": _iso_ms(start_ms),
            "end_utc_exclusive": _iso_ms(end_ms),
            "interval": "15m",
            "timezone": "UTC",
        },
        "source_files": accepted_sources,
        "source_set_identity_context": context,
        "partition_summary": {
            "partition_count": len(partitions),
            "source_mode_counts": mode_counts,
            "daily_union_months": [
                item["utc_year_month"] for item in partitions if item["source_mode"] == "daily_union"
            ],
            "partitions": [
                {
                    "utc_year_month": item["utc_year_month"],
                    "source_mode": item["source_mode"],
                    "partition_identity": item["partition_identity"],
                    "output_sha256": item["output"]["sha256"],
                    "row_count": item["output"]["row_count"],
                }
                for item in partitions
            ],
        },
        "rejected_monthly_sources": [
            item["rejected_monthly_source"]
            for item in partitions
            if item.get("rejected_monthly_source") is not None
        ],
        "source_accounting": {
            "parsed_source_row_count": sum(item["source_diagnostics"]["source_parsed_row_count"] for item in partitions),
            "canonical_unique_row_count": sum(item["source_diagnostics"]["canonical_unique_row_count"] for item in partitions),
            "duplicate_trade_id_count": 0,
            "conflicting_duplicate_count": 0,
            "trade_id_gap_range_count": trade_id_gap_range_count,
            "absent_trade_id_count": absent_trade_id_count,
            "trade_id_gap_ranges_sha256": content_sha256(all_trade_id_gap_ranges),
            "boundary_trade_id_gap_ranges": boundary_trade_id_gaps,
            "backwards_or_overlap_count": 0,
            "invalid_row_count": 0,
        },
        "coverage": {
            "expected_bar_count": expected_rows,
            "observed_bar_count": row_count,
            "missing_bar_count": 0,
            "duplicate_bar_timestamp_count": 0,
        },
        "d4_reconciliation": {
            "data_slice_identity": D4_DATA_SLICE_IDENTITY,
            "normalized_sha256": d4_meta["sha256"],
            "normalized_row_count": d4_meta["row_count"],
            "mismatch_counts": {"volume": 0, "trade_count": 0, "taker_buy": 0, "taker_sell": 0},
        },
        "availability": availability,
        "research_feature_table": research_feature_table,
        "output": {
            "path": output_path.as_posix(),
            "format": "CSV UTF-8 LF",
            "columns": list(OUTPUT_COLUMNS),
            "row_count": row_count,
            "size_bytes": output_path.stat().st_size,
            "sha256": output_sha,
            "git_tracking_status": "local_ignored_data",
        },
        "requested_range_data_complete": True,
        "network_used": False,
        "diagnostic_only": True,
        "authority": "historical raw-archive diagnostic only; not an authoritative RESEARCH-02 feature source and no candidate, Result Population, promotion, runtime, or execution authority",
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return manifest


def materialize_partitioned_takerflow_features(
    *,
    monthly_root: Path,
    daily_root: Path,
    cache_root: Path,
    start_utc: str,
    end_utc: str,
    output_path: Path,
    manifest_path: Path,
    availability_catalog_path: Path,
    d4_path: Path,
    d4_expected_sha256: str = D4_NORMALIZED_SHA256,
    d4_expected_rows: int = D4_EXPECTED_ROWS,
    stop_after_partitions: int | None = None,
    chunk_rows: int = 500_000,
) -> dict[str, Any]:
    """Resolve, cache, validate, and assemble strict official raw-trade partitions."""

    start_ms = _utc_ms(start_utc, "start_utc")
    end_ms = _utc_ms(end_utc, "end_utc")
    if start_ms >= end_ms or start_ms % SUPPORTED_INTERVALS_MS["15m"] or end_ms % SUPPORTED_INTERVALS_MS["15m"]:
        raise TakerflowMaterializationError("requested start/end must be increasing UTC 15m boundaries")
    d4_oracle, d4_meta = _load_d4_oracle(
        d4_path, expected_sha256=d4_expected_sha256, expected_rows=d4_expected_rows
    )
    cache_root.mkdir(parents=True, exist_ok=True)
    scratch_parent = cache_root / ".scratch"
    scratch_parent.mkdir(parents=True, exist_ok=True)
    partitions: list[dict[str, Any]] = []
    months = _month_starts(start_ms, end_ms)
    for index, month in enumerate(months):
        month_key = month.strftime("%Y-%m")
        partition_csv = cache_root / f"{month_key}.csv"
        partition_manifest = cache_root / f"{month_key}.manifest.json"
        monthly_path = monthly_root / f"BTCUSDT-trades-{month_key}.zip"
        reused = _reuse_partition(
            month=month,
            monthly_path=monthly_path,
            daily_root=daily_root,
            output_path=partition_csv,
            manifest_path=partition_manifest,
            d4_meta=d4_meta,
        )
        if reused is not None:
            partitions.append(reused)
        else:
            monthly_source: dict[str, Any] | None = None
            monthly_error: PartitionQualityError | None = None
            try:
                monthly_source = _verified_source(monthly_path)
            except TakerflowMaterializationError as exc:
                monthly_error = PartitionQualityError([str(exc)], {})
            if monthly_source is not None:
                try:
                    built = _build_raw_trade_partition(
                        month=month,
                        source_mode="monthly",
                        source_files=[monthly_source],
                        output_path=partition_csv,
                        manifest_path=partition_manifest,
                        scratch_parent=scratch_parent,
                        d4_oracle=d4_oracle,
                        d4_meta=d4_meta,
                        requested_start_ms=start_ms,
                        requested_end_ms=end_ms,
                        chunk_rows=chunk_rows,
                    )
                except PartitionQualityError as exc:
                    monthly_error = exc
            if monthly_error is not None:
                rejected = {
                    **(monthly_source or {
                        "path": monthly_path.as_posix(),
                        "logical_filename": monthly_path.name,
                        "checksum_verified": False,
                    }),
                    "parsed_row_count": monthly_error.diagnostics.get("source_parsed_row_count"),
                    "physical_row_order_monotonic": monthly_error.diagnostics.get("physical_row_order_monotonic"),
                    "out_of_order_pair_count": monthly_error.diagnostics.get("out_of_order_pair_count"),
                    "first_observed_inversion": monthly_error.diagnostics.get("first_observed_inversion"),
                    "semantic_rejection_reasons": list(monthly_error.reasons),
                }
                daily_sources = [
                    _verified_source(path)
                    for path in _daily_paths(daily_root, month, "BTCUSDT")
                ]
                try:
                    built = _build_raw_trade_partition(
                        month=month,
                        source_mode="daily_union",
                        source_files=daily_sources,
                        output_path=partition_csv,
                        manifest_path=partition_manifest,
                        scratch_parent=scratch_parent,
                        d4_oracle=d4_oracle,
                        d4_meta=d4_meta,
                        requested_start_ms=start_ms,
                        requested_end_ms=end_ms,
                        rejected_monthly_source=rejected,
                        chunk_rows=chunk_rows,
                    )
                except PartitionQualityError as daily_error:
                    raise TakerflowMaterializationError(
                        f"DATA_QUALITY_BLOCKER {month_key}: daily_union rejected: {daily_error}"
                    ) from daily_error
            partitions.append(built)
        if stop_after_partitions is not None and index + 1 >= stop_after_partitions:
            raise TakerflowMaterializationError(
                f"intentional interruption after {stop_after_partitions} validated partitions"
            )
    try:
        return _assemble_partitioned_output(
            partitions=partitions,
            output_path=output_path,
            manifest_path=manifest_path,
            availability_catalog_path=availability_catalog_path,
            start_ms=start_ms,
            end_ms=end_ms,
            d4_meta=d4_meta,
        )
    finally:
        if scratch_parent.exists() and not any(scratch_parent.iterdir()):
            scratch_parent.rmdir()


def materialize_takerflow_features(
    *,
    input_paths: Iterable[Path],
    archive_type: str,
    interval: str,
    start_utc: str,
    end_utc: str,
    output_path: Path,
    manifest_path: Path,
    availability_catalog_path: Path,
    symbol: str = "BTCUSDT",
) -> dict[str, Any]:
    """Write a deterministic feature CSV and manifest from local archives only."""

    if not re.fullmatch(r"[A-Z0-9_-]+", symbol):
        raise TakerflowMaterializationError("symbol must use uppercase exchange notation")
    start_ms = _utc_ms(start_utc, "start_utc")
    end_ms = _utc_ms(end_utc, "end_utc")
    availability = _availability_contract(availability_catalog_path)
    interval_ms = SUPPORTED_INTERVALS_MS.get(interval)
    if interval_ms is None:
        raise TakerflowMaterializationError(
            f"interval must be one of {sorted(SUPPORTED_INTERVALS_MS)}"
        )
    if start_ms >= end_ms or start_ms % interval_ms or end_ms % interval_ms:
        raise TakerflowMaterializationError(
            "requested start/end must be increasing UTC interval boundaries"
        )
    streamed = _stream_source_aggregation(
        input_paths,
        archive_type=archive_type,
        interval_ms=interval_ms,
        start_ms=start_ms,
        end_ms=end_ms,
    )
    output_rows = _feature_rows_from_groups(streamed["groups"], interval_ms)
    if not output_rows:
        raise TakerflowMaterializationError("requested range contains no source events")
    _validate_output_rows(
        output_rows,
        interval_ms=interval_ms,
        start_ms=start_ms,
        end_ms=end_ms,
    )
    expected_bar_count = (end_ms - start_ms) // interval_ms
    missing_ranges = _missing_bar_ranges(
        set(streamed["groups"]), start_ms, end_ms, interval_ms
    )
    missing_bar_count = sum(item["bar_count"] for item in missing_ranges)
    coverage = {
        "expected_bar_count": expected_bar_count,
        "observed_bar_count": len(output_rows),
        "missing_bar_count": missing_bar_count,
        "missing_bar_ranges": missing_ranges,
        "bar_coverage_fraction": f"{len(output_rows)}/{expected_bar_count}",
        "source_rows_before_requested_range": streamed[
            "source_rows_before_requested_range"
        ],
        "source_rows_in_requested_range": streamed["source_rows_in_requested_range"],
        "source_rows_after_requested_range": streamed["source_rows_after_requested_range"],
    }
    event_gaps = streamed["event_gaps"]
    _write_feature_csv(output_path, output_rows)
    source_accounting = {
        "parsed_source_row_count": streamed["parsed_source_row_count"],
        "exact_duplicate_row_count_removed": streamed[
            "exact_duplicate_row_count_removed"
        ],
        "unique_source_row_count": streamed["unique_source_row_count"],
        "accounting_identity": (
            "parsed_source_row_count = unique_source_row_count + "
            "exact_duplicate_row_count_removed"
        ),
        "range_accounting_identity": (
            "unique_source_row_count = source_rows_before_requested_range + "
            "source_rows_in_requested_range + source_rows_after_requested_range"
        ),
    }
    stable_source_files = [
        {
            "logical_filename": Path(item["path"]).name,
            "sha256": item["sha256"],
            "size_bytes": item["size_bytes"],
            "parsed_row_count": item["parsed_row_count"],
            "source_type": archive_type,
        }
        for item in streamed["source_files"]
    ]
    output_identity = {
        "format": "CSV UTF-8 LF",
        "sha256": _sha256(output_path),
        "row_count": len(output_rows),
        "columns": list(OUTPUT_COLUMNS),
    }
    complete = coverage["missing_bar_count"] == 0 and (
        archive_type == "trades" or len(event_gaps) == 0
    )
    research_feature_table = {
        "schema_version": FEATURE_TABLE_SCHEMA_VERSION,
        "family_id": "binance_usdm_takerflow_v1",
        "market_identity": {
            "venue": "Binance",
            "market_type": "USD-M perpetual",
            "symbol": symbol,
        },
        "timeframe": interval,
        "feature_names": list(REQUIRED_FEATURES),
        "source_class": REQUIRED_SOURCE_CLASS,
        "availability_assertions": [
            {
                "feature_name": item["feature_name"],
                "source_class": REQUIRED_SOURCE_CLASS,
                "condition_assertions": list(item["conditions"]),
            }
            for item in availability["features"]
        ],
        "source_set_identity": build_source_set_identity(stable_source_files),
        "output_identity": output_identity,
        "coverage": {
            "start_utc_inclusive": _iso_ms(start_ms),
            "end_utc_exclusive": _iso_ms(end_ms),
            "expected_row_count": expected_bar_count,
            "observed_row_count": len(output_rows),
            "complete": complete,
        },
        "causality": {
            "timestamp_semantics": "UTC bar open",
            "feature_available_at_semantics": "exclusive bar close",
            "completed_bar_only": True,
            "future_events_can_change_prior_completed_bars": False,
        },
        "quality_policy": {
            "fill": "forbidden",
            "forward_fill": "forbidden",
            "backfill": "forbidden",
            "interpolation": "forbidden",
            "timestamp_tolerance": "forbidden",
            "missing_row": "fail_closed",
            "duplicate_join_key": "fail_closed",
        },
        "feature_table_identity": "",
        "non_authority": {
            "authorizes_execution": False,
            "authorizes_result_population": False,
            "authorizes_candidate": False,
            "authorizes_promotion": False,
            "authorizes_runtime_paper_live": False,
            "authorizes_oms_risk_reconciliation": False,
        },
    }
    research_feature_table["feature_table_identity"] = build_feature_table_identity(
        research_feature_table
    )
    validate_feature_table_contract(
        research_feature_table,
        source_files=stable_source_files,
    )
    manifest = {
        "materialization_version": MATERIALIZATION_VERSION,
        "output_schema_version": OUTPUT_SCHEMA_VERSION,
        "symbol": symbol,
        "market": "Binance USD-M perpetual",
        "archive_type": archive_type,
        "request": {
            "start_utc_inclusive": _iso_ms(start_ms),
            "end_utc_exclusive": _iso_ms(end_ms),
            "interval": interval,
            "timezone": "UTC",
        },
        "source_files": streamed["source_files"],
        "source_accounting": source_accounting,
        "source_event_id_gaps": {
            "gap_count": len(event_gaps),
            "gaps": event_gaps,
        },
        "coverage": coverage,
        "alignment": {
            "bar_membership": "event_time in [bar_open, bar_close)",
            "output_timestamp": "UTC bar open",
            "feature_available_at": "exclusive UTC bar close",
            "completed_bar_only": True,
            "future_events_can_change_prior_completed_bars": False,
            "empty_bar_policy": "omit row and disclose exact missing bar/range in coverage",
        },
        "buyer_maker_direction": {
            "is_buyer_maker_true": "buyer is maker; seller is taker; taker sell volume",
            "is_buyer_maker_false": "buyer is taker; taker buy volume",
        },
        "feature_schema": [
            {"name": "timestamp", "logical_type": "UTC ISO-8601 bar-open string"},
            {"name": "open_time_ms", "logical_type": "int64 UTC epoch milliseconds"},
            {
                "name": "feature_available_at",
                "logical_type": "UTC ISO-8601 exclusive bar-close string",
            },
            {
                "name": "feature_available_at_ms",
                "logical_type": "int64 UTC epoch milliseconds",
            },
            *[
                {"name": name, "logical_type": "canonical base-asset decimal text"}
                for name in (
                    "taker_buy_volume",
                    "taker_sell_volume",
                    "taker_total_volume",
                    "taker_net_volume",
                )
            ],
            {
                "name": "taker_imbalance",
                "logical_type": "decimal text (buy-sell)/(buy+sell), precision 38",
            },
            {
                "name": "taker_buy_sell_ratio",
                "logical_type": "nullable decimal text buy/sell, precision 38",
            },
            {"name": "trade_count", "logical_type": "positive integer underlying trades"},
            {"name": "source_record_count", "logical_type": "positive integer archive rows"},
        ],
        "availability": availability,
        "research_feature_table": research_feature_table,
        "output": {
            "path": output_path.as_posix(),
            "format": "CSV UTF-8 LF",
            "columns": list(OUTPUT_COLUMNS),
            "row_count": len(output_rows),
            "size_bytes": output_path.stat().st_size,
            "sha256": output_identity["sha256"],
            "git_tracking_status": "local_ignored_data",
        },
        "requested_range_data_complete": complete,
        "network_used": False,
        "diagnostic_only": True,
        "authority": (
            "historical raw-archive diagnostic only; not an authoritative RESEARCH-02 "
            "feature source and no candidate, Result Population, promotion, runtime, "
            "or execution authority"
        ),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def materialize_d4_native_takerflow_features(
    *,
    d4_path: Path,
    output_path: Path,
    manifest_path: Path,
    availability_catalog_path: Path,
    data_slice_identity: str = D4_DATA_SLICE_IDENTITY,
    expected_sha256: str = D4_NORMALIZED_SHA256,
    expected_rows: int = D4_EXPECTED_ROWS,
    coverage_start_utc_inclusive: str = D4_COVERAGE_START,
    coverage_end_utc_exclusive: str = D4_COVERAGE_END,
) -> dict[str, Any]:
    """Derive the authoritative row-local taker features from canonical D4."""

    if not d4_path.is_file():
        raise TakerflowMaterializationError(f"canonical D4 parent is missing: {d4_path}")
    actual_sha256 = _sha256(d4_path)
    if actual_sha256 != expected_sha256:
        raise TakerflowMaterializationError(
            f"D4_PARENT_IDENTITY_BLOCKER: expected {expected_sha256}, observed {actual_sha256}"
        )
    start_ms = _utc_ms(coverage_start_utc_inclusive, "coverage_start_utc_inclusive")
    end_ms = _utc_ms(coverage_end_utc_exclusive, "coverage_end_utc_exclusive")
    interval_ms = SUPPORTED_INTERVALS_MS["15m"]
    if start_ms >= end_ms or (end_ms - start_ms) // interval_ms != expected_rows:
        raise TakerflowMaterializationError("D4 coverage and expected row count disagree")
    availability = _availability_contract(
        availability_catalog_path, source_class=D4_TAKER_SOURCE_CLASS
    )
    required_parent_columns = {
        "open_time_ms",
        "open_time",
        "volume",
        "close_time_ms",
        "num_trades",
        "taker_buy_base_vol",
    }
    output_rows: list[dict[str, Any]] = []
    projection = hashlib.sha256()
    projection.update(
        b"taker_buy_volume,taker_sell_volume,taker_buy_sell_ratio\n"
    )
    zero_sell_count = 0
    try:
        with d4_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or not required_parent_columns.issubset(
                reader.fieldnames
            ):
                raise TakerflowMaterializationError(
                    "canonical D4 parent lacks required timestamp/taker columns"
                )
            for index, parent in enumerate(reader):
                row_number = index + 2
                try:
                    open_ms = int(parent["open_time_ms"])
                    close_ms = int(parent["close_time_ms"])
                    volume = Decimal(parent["volume"])
                    trades = int(parent["num_trades"])
                    buy = Decimal(parent["taker_buy_base_vol"])
                except (ValueError, InvalidOperation, KeyError) as exc:
                    raise TakerflowMaterializationError(
                        f"D4 row {row_number} contains invalid parent values"
                    ) from exc
                expected_open = start_ms + index * interval_ms
                if (
                    open_ms != expected_open
                        or _utc_ms(parent["open_time"], f"D4 row {row_number} open_time")
                        != open_ms
                    or close_ms != open_ms + interval_ms - 1
                ):
                    raise TakerflowMaterializationError(
                        f"D4 row {row_number} violates exact completed-bar alignment"
                    )
                if (
                    not volume.is_finite()
                    or not buy.is_finite()
                    or volume < 0
                    or buy < 0
                    or buy > volume
                    or trades < 0
                ):
                    raise TakerflowMaterializationError(
                        f"D4 row {row_number} violates taker derivation bounds"
                    )
                sell = volume - buy
                ratio = _ratio(buy, sell)
                if sell == 0:
                    zero_sell_count += 1
                buy_text = _decimal_text(buy)
                sell_text = _decimal_text(sell)
                ratio_text = ratio or ""
                projection.update(
                    f"{buy_text},{sell_text},{ratio_text}\n".encode("utf-8")
                )
                available_ms = open_ms + interval_ms
                output_rows.append(
                    {
                        "timestamp": _iso_ms(open_ms),
                        "open_time_ms": open_ms,
                        "feature_available_at": _iso_ms(available_ms),
                        "feature_available_at_ms": available_ms,
                        "taker_buy_volume": buy_text,
                        "taker_sell_volume": sell_text,
                        "taker_buy_sell_ratio": ratio,
                    }
                )
    except UnicodeDecodeError as exc:
        raise TakerflowMaterializationError("canonical D4 parent is not UTF-8") from exc
    if len(output_rows) != expected_rows:
        raise TakerflowMaterializationError(
            f"D4 row count mismatch: expected {expected_rows}, observed {len(output_rows)}"
        )
    if output_rows[-1]["feature_available_at_ms"] != end_ms:
        raise TakerflowMaterializationError("D4 final completed-bar boundary is incorrect")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=D4_OUTPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)
    output_sha256 = _sha256(output_path)
    parent_identity = {
        "data_slice_identity": data_slice_identity,
        "normalized_sha256": actual_sha256,
        "row_count": len(output_rows),
        "coverage_start_utc_inclusive": coverage_start_utc_inclusive,
        "coverage_end_utc_exclusive": coverage_end_utc_exclusive,
    }
    stable_source_files = [
        {
            "logical_filename": d4_path.name,
            "sha256": actual_sha256,
            "size_bytes": d4_path.stat().st_size,
            "parsed_row_count": len(output_rows),
            "source_type": "canonical_d4_kline",
        }
    ]
    source_identity_context = {
        "data_slice_identity": data_slice_identity,
        "normalized_sha256": actual_sha256,
        "derivation_version": D4_TAKER_DERIVATION_VERSION,
    }
    contract = {
        "schema_version": FEATURE_TABLE_SCHEMA_VERSION,
        "family_id": "binance_usdm_takerflow_v1",
        "market_identity": {
            "venue": "Binance",
            "market_type": "USD-M perpetual",
            "symbol": "BTCUSDT",
        },
        "timeframe": "15m",
        "feature_names": list(REQUIRED_FEATURES),
        "source_class": D4_TAKER_SOURCE_CLASS,
        "availability_assertions": [
            {
                "feature_name": item["feature_name"],
                "source_class": D4_TAKER_SOURCE_CLASS,
                "condition_assertions": list(item["conditions"]),
            }
            for item in availability["features"]
        ],
        "source_set_identity": build_source_set_identity(
            stable_source_files, identity_context=source_identity_context
        ),
        "parent_identity": parent_identity,
        "derivation": {
            "derivation_version": D4_TAKER_DERIVATION_VERSION,
            "parent_fields": list(D4_TAKER_PARENT_FIELDS),
            "features": [dict(item) for item in D4_TAKER_FEATURE_DEFINITIONS],
        },
        "output_identity": {
            "format": "CSV UTF-8 LF",
            "sha256": output_sha256,
            "row_count": len(output_rows),
            "columns": list(D4_OUTPUT_COLUMNS),
        },
        "coverage": {
            "start_utc_inclusive": coverage_start_utc_inclusive,
            "end_utc_exclusive": coverage_end_utc_exclusive,
            "expected_row_count": expected_rows,
            "observed_row_count": len(output_rows),
            "complete": True,
        },
        "causality": {
            "timestamp_semantics": "UTC bar open",
            "feature_available_at_semantics": "exclusive bar close",
            "completed_bar_only": True,
            "future_events_can_change_prior_completed_bars": False,
        },
        "quality_policy": {
            "fill": "forbidden",
            "forward_fill": "forbidden",
            "backfill": "forbidden",
            "interpolation": "forbidden",
            "timestamp_tolerance": "forbidden",
            "missing_row": "fail_closed",
            "duplicate_join_key": "fail_closed",
        },
        "feature_table_identity": "",
        "non_authority": {
            "authorizes_execution": False,
            "authorizes_result_population": False,
            "authorizes_candidate": False,
            "authorizes_promotion": False,
            "authorizes_runtime_paper_live": False,
            "authorizes_oms_risk_reconciliation": False,
        },
    }
    contract["feature_table_identity"] = build_feature_table_identity(contract)
    validate_feature_table_contract(
        contract,
        source_files=stable_source_files,
        source_identity_context=source_identity_context,
    )
    manifest = {
        "materialization_version": D4_TAKER_DERIVATION_VERSION,
        "source_type": "canonical_d4_kline",
        "source_files": [
            {
                "path": d4_path.as_posix(),
                **stable_source_files[0],
            }
        ],
        "source_set_identity_context": source_identity_context,
        "availability": availability,
        "research_feature_table": contract,
        "proof": {
            "parent_row_count": len(output_rows),
            "feature_row_count": len(output_rows),
            "missing_bar_count": 0,
            "duplicate_timestamp_count": 0,
            "invalid_buy_count": 0,
            "invalid_sell_count": 0,
            "zero_sell_count": zero_sell_count,
            "null_ratio_count": zero_sell_count,
            "three_column_projection_sha256": projection.hexdigest(),
        },
        "output": {
            "path": output_path.as_posix(),
            "format": "CSV UTF-8 LF",
            "columns": list(D4_OUTPUT_COLUMNS),
            "row_count": len(output_rows),
            "size_bytes": output_path.stat().st_size,
            "sha256": output_sha256,
            "git_tracking_status": "local_ignored_data",
        },
        "network_used": False,
        "authority": (
            "noncanonical offline research feature data only; no candidate, Result "
            "Population, promotion, runtime, paper/live, OMS, risk, or reconciliation authority"
        ),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def _require_regular_non_reparse_file(path: Path, label: str) -> None:
    try:
        facts = path.lstat()
    except OSError as exc:
        raise TakerflowMaterializationError(f"{label} is missing: {path}") from exc
    file_attributes = getattr(facts, "st_file_attributes", 0)
    if (
        path.is_symlink()
        or not stat.S_ISREG(facts.st_mode)
        or file_attributes & 0x400
    ):
        raise TakerflowMaterializationError(
            f"{label} must be a regular non-reparse file: {path}"
        )


def _canonical_parent_records(path: Path, parent_format: str) -> Iterator[Mapping[str, Any]]:
    required = {
        "open_time_ms",
        "volume",
        "close_time_ms",
        "num_trades",
        "taker_buy_base_vol",
    }
    if parent_format == "csv":
        try:
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames is None or not required.issubset(reader.fieldnames):
                    raise TakerflowMaterializationError(
                        "canonical kline CSV lacks required timestamp/taker columns"
                    )
                yield from reader
        except UnicodeDecodeError as exc:
            raise TakerflowMaterializationError(
                "canonical kline CSV is not UTF-8"
            ) from exc
        return
    if parent_format != "parquet":
        raise TakerflowMaterializationError("unsupported canonical kline parent format")
    try:
        frame = pd.read_parquet(path)
    except Exception as exc:
        raise TakerflowMaterializationError(
            "canonical kline Parquet cannot be parsed"
        ) from exc
    if not required.issubset(frame.columns):
        raise TakerflowMaterializationError(
            "canonical kline Parquet lacks required timestamp/taker columns"
        )
    yield from frame.to_dict("records")


def materialize_canonical_kline_takerflow_features(
    *,
    canonical_kline_path: Path,
    timeframe: str,
    output_path: Path,
    manifest_path: Path,
    availability_catalog_path: Path,
    _parent_config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive row-local taker features from one exact D2-021 canonical base."""

    if timeframe not in CANONICAL_KLINE_TAKER_TIMEFRAMES:
        raise TakerflowMaterializationError(
            "canonical kline taker materialization is limited to 30m/1h/4h/1d"
        )
    config = dict(_parent_config or CANONICAL_KLINE_PARENT_CONFIG[timeframe])
    _require_regular_non_reparse_file(canonical_kline_path, "canonical kline parent")
    actual_sha256 = _sha256(canonical_kline_path)
    if actual_sha256 != config["sha256"]:
        raise TakerflowMaterializationError(
            "CANONICAL_KLINE_PARENT_IDENTITY_BLOCKER: "
            f"expected {config['sha256']}, observed {actual_sha256}"
        )
    expected_rows = int(config["row_count"])
    coverage_start = str(config["coverage_start"])
    coverage_end = str(config["coverage_end"])
    start_ms = _utc_ms(coverage_start, "coverage_start")
    end_ms = _utc_ms(coverage_end, "coverage_end")
    interval_ms = SUPPORTED_INTERVALS_MS[timeframe]
    if start_ms >= end_ms or (end_ms - start_ms) // interval_ms != expected_rows:
        raise TakerflowMaterializationError(
            "canonical kline coverage and expected row count disagree"
        )
    availability = _availability_contract(
        availability_catalog_path,
        source_class=CANONICAL_KLINE_TAKER_SOURCE_CLASS,
    )
    output_rows: list[dict[str, Any]] = []
    projection = hashlib.sha256()
    projection.update(b"taker_buy_volume,taker_sell_volume,taker_buy_sell_ratio\n")
    zero_sell_count = 0
    for index, parent in enumerate(
        _canonical_parent_records(canonical_kline_path, str(config["format"]))
    ):
        row_number = index + 2
        try:
            open_ms = int(parent["open_time_ms"])
            close_ms = int(parent["close_time_ms"])
            volume = Decimal(str(parent["volume"]))
            trades = int(parent["num_trades"])
            buy = Decimal(str(parent["taker_buy_base_vol"]))
        except (ValueError, TypeError, InvalidOperation, KeyError) as exc:
            raise TakerflowMaterializationError(
                f"canonical kline row {row_number} contains invalid parent values"
            ) from exc
        expected_open = start_ms + index * interval_ms
        if open_ms != expected_open or close_ms != open_ms + interval_ms - 1:
            raise TakerflowMaterializationError(
                f"canonical kline row {row_number} violates exact completed-bar alignment"
            )
        open_time = parent.get("open_time")
        if open_time not in (None, "") and _utc_ms(
            str(open_time), f"canonical kline row {row_number} open_time"
        ) != open_ms:
            raise TakerflowMaterializationError(
                f"canonical kline row {row_number} open timestamp disagrees"
            )
        if (
            not volume.is_finite()
            or not buy.is_finite()
            or volume < 0
            or buy < 0
            or buy > volume
            or trades < 0
        ):
            raise TakerflowMaterializationError(
                f"canonical kline row {row_number} violates taker derivation bounds"
            )
        sell = volume - buy
        ratio = _ratio(buy, sell)
        if sell == 0:
            zero_sell_count += 1
        buy_text = _decimal_text(buy)
        sell_text = _decimal_text(sell)
        ratio_text = ratio or ""
        projection.update(f"{buy_text},{sell_text},{ratio_text}\n".encode("utf-8"))
        available_ms = open_ms + interval_ms
        output_rows.append(
            {
                "timestamp": _iso_ms(open_ms),
                "open_time_ms": open_ms,
                "feature_available_at": _iso_ms(available_ms),
                "feature_available_at_ms": available_ms,
                "taker_buy_volume": buy_text,
                "taker_sell_volume": sell_text,
                "taker_buy_sell_ratio": ratio,
            }
        )
    if len(output_rows) != expected_rows:
        raise TakerflowMaterializationError(
            f"canonical kline row count mismatch: expected {expected_rows}, observed {len(output_rows)}"
        )
    if not output_rows or output_rows[-1]["feature_available_at_ms"] != end_ms:
        raise TakerflowMaterializationError(
            "canonical kline final completed-bar boundary is incorrect"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=D4_OUTPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)
    output_sha256 = _sha256(output_path)
    parent_identity = {
        "data_slice_identity": str(config["data_slice_identity"]),
        "normalized_sha256": actual_sha256,
        "row_count": len(output_rows),
        "coverage_start_utc_inclusive": coverage_start,
        "coverage_end_utc_exclusive": coverage_end,
    }
    source_type = f"canonical_{timeframe}_kline_{config['format']}"
    stable_source_files = [
        {
            "logical_filename": canonical_kline_path.name,
            "sha256": actual_sha256,
            "size_bytes": canonical_kline_path.stat().st_size,
            "parsed_row_count": len(output_rows),
            "source_type": source_type,
        }
    ]
    source_identity_context = {
        "data_slice_identity": str(config["data_slice_identity"]),
        "normalized_sha256": actual_sha256,
        "timeframe": timeframe,
        "derivation_version": CANONICAL_KLINE_TAKER_DERIVATION_VERSION,
    }
    contract = {
        "schema_version": FEATURE_TABLE_SCHEMA_VERSION,
        "family_id": "binance_usdm_takerflow_v1",
        "market_identity": {
            "venue": "Binance",
            "market_type": "USD-M perpetual",
            "symbol": "BTCUSDT",
        },
        "timeframe": timeframe,
        "feature_names": list(REQUIRED_FEATURES),
        "source_class": CANONICAL_KLINE_TAKER_SOURCE_CLASS,
        "availability_assertions": [
            {
                "feature_name": item["feature_name"],
                "source_class": CANONICAL_KLINE_TAKER_SOURCE_CLASS,
                "condition_assertions": list(item["conditions"]),
            }
            for item in availability["features"]
        ],
        "source_set_identity": build_source_set_identity(
            stable_source_files, identity_context=source_identity_context
        ),
        "parent_identity": parent_identity,
        "derivation": {
            "derivation_version": CANONICAL_KLINE_TAKER_DERIVATION_VERSION,
            "parent_fields": list(CANONICAL_KLINE_TAKER_PARENT_FIELDS),
            "features": [
                dict(item) for item in CANONICAL_KLINE_TAKER_FEATURE_DEFINITIONS
            ],
        },
        "output_identity": {
            "format": "CSV UTF-8 LF",
            "sha256": output_sha256,
            "row_count": len(output_rows),
            "columns": list(D4_OUTPUT_COLUMNS),
        },
        "coverage": {
            "start_utc_inclusive": coverage_start,
            "end_utc_exclusive": coverage_end,
            "expected_row_count": expected_rows,
            "observed_row_count": len(output_rows),
            "complete": True,
        },
        "causality": {
            "timestamp_semantics": "UTC bar open",
            "feature_available_at_semantics": "exclusive bar close",
            "completed_bar_only": True,
            "future_events_can_change_prior_completed_bars": False,
        },
        "quality_policy": {
            "fill": "forbidden",
            "forward_fill": "forbidden",
            "backfill": "forbidden",
            "interpolation": "forbidden",
            "timestamp_tolerance": "forbidden",
            "missing_row": "fail_closed",
            "duplicate_join_key": "fail_closed",
        },
        "feature_table_identity": "",
        "non_authority": {
            "authorizes_execution": False,
            "authorizes_result_population": False,
            "authorizes_candidate": False,
            "authorizes_promotion": False,
            "authorizes_runtime_paper_live": False,
            "authorizes_oms_risk_reconciliation": False,
        },
    }
    contract["feature_table_identity"] = build_feature_table_identity(contract)
    validate_feature_table_contract(
        contract,
        source_files=stable_source_files,
        source_identity_context=source_identity_context,
    )
    manifest = {
        "materialization_version": CANONICAL_KLINE_TAKER_DERIVATION_VERSION,
        "source_type": source_type,
        "source_files": [
            {"path": canonical_kline_path.as_posix(), **stable_source_files[0]}
        ],
        "source_set_identity_context": source_identity_context,
        "availability": availability,
        "research_feature_table": contract,
        "proof": {
            "parent_row_count": len(output_rows),
            "feature_row_count": len(output_rows),
            "missing_bar_count": 0,
            "duplicate_timestamp_count": 0,
            "invalid_buy_count": 0,
            "invalid_sell_count": 0,
            "zero_sell_count": zero_sell_count,
            "null_ratio_count": zero_sell_count,
            "three_column_projection_sha256": projection.hexdigest(),
        },
        "output": {
            "path": output_path.as_posix(),
            "format": "CSV UTF-8 LF",
            "columns": list(D4_OUTPUT_COLUMNS),
            "row_count": len(output_rows),
            "size_bytes": output_path.stat().st_size,
            "sha256": output_sha256,
            "git_tracking_status": "local_ignored_data",
        },
        "network_used": False,
        "authority": (
            "noncanonical offline research feature data only; no candidate, Result "
            "Population, promotion, runtime, paper/live, OMS, risk, or reconciliation authority"
        ),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def _month_starts(start_ms: int, end_ms: int) -> list[datetime]:
    current = datetime.fromtimestamp(start_ms / 1000, tz=UTC).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    end = datetime.fromtimestamp(end_ms / 1000, tz=UTC)
    months: list[datetime] = []
    while current < end:
        months.append(current)
        current = current.replace(
            year=current.year + (1 if current.month == 12 else 0),
            month=1 if current.month == 12 else current.month + 1,
        )
    return months


def _checksum_sidecar_digest(path: Path, archive_name: str) -> str | None:
    try:
        text = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None
    match = re.fullmatch(r"([0-9A-Fa-f]{64})\s+\*?(.+)", text)
    if match is None or Path(match.group(2)).name != archive_name:
        return None
    return match.group(1).lower()


def inspect_hydration_manifest(path: Path) -> dict[str, Any]:
    """Resolve an exact monthly hydration contract without fetching anything."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TakerflowMaterializationError(f"cannot read hydration manifest: {path}") from exc
    if payload.get("manifest_version") != HYDRATION_MANIFEST_VERSION:
        raise TakerflowMaterializationError("unsupported hydration manifest version")
    if payload.get("archive_type") not in SUPPORTED_ARCHIVE_TYPES:
        raise TakerflowMaterializationError("hydration archive_type must be trades or aggTrades")
    request = payload.get("request", {})
    start_ms = _utc_ms(request.get("start_utc_inclusive"), "start_utc_inclusive")
    end_ms = _utc_ms(request.get("end_utc_exclusive"), "end_utc_exclusive")
    interval = request.get("interval")
    if interval not in SUPPORTED_INTERVALS_MS:
        raise TakerflowMaterializationError("hydration interval is not project-supported")
    partition = payload.get("partition_contract", {})
    if partition.get("scheme") not in {
        "monthly",
        "monthly-primary-full-daily-union-fallback",
    } or partition.get("timezone") != "UTC":
        raise TakerflowMaterializationError("hydration partition contract must be monthly UTC")
    root_text = payload.get("local_archive_root")
    if not isinstance(root_text, str):
        raise TakerflowMaterializationError("local_archive_root must be a path string")
    logical_root = PurePosixPath(root_text)
    if logical_root.is_absolute() or ".." in logical_root.parts:
        raise TakerflowMaterializationError("local_archive_root must be repository-relative")
    daily_root_text = payload.get(
        "daily_fallback_archive_root",
        root_text.replace("/monthly/", "/daily/"),
    )
    daily_logical_root = PurePosixPath(str(daily_root_text))
    if daily_logical_root.is_absolute() or ".." in daily_logical_root.parts:
        raise TakerflowMaterializationError(
            "daily_fallback_archive_root must be repository-relative"
        )
    materialization = payload.get("materialization", {})
    cache_root_text = materialization.get(
        "partition_cache_root",
        "data/processed/research02_takerflow_partitions/BTCUSDT/15m",
    )
    d4_path_text = materialization.get(
        "d4_normalized_path",
        "data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv",
    )
    for label, value in (("partition_cache_root", cache_root_text), ("d4_normalized_path", d4_path_text)):
        logical = PurePosixPath(str(value))
        if logical.is_absolute() or ".." in logical.parts:
            raise TakerflowMaterializationError(f"{label} must be repository-relative")
    symbol = payload.get("symbol")
    archive_type = payload["archive_type"]
    if not isinstance(symbol, str) or not re.fullmatch(r"[A-Z0-9_-]+", symbol):
        raise TakerflowMaterializationError("hydration symbol is invalid")
    months = _month_starts(start_ms, end_ms)
    expected_count = partition.get("expected_partition_count")
    if expected_count != len(months):
        raise TakerflowMaterializationError(
            f"expected_partition_count must equal {len(months)} for the requested range"
        )
    expected_paths = [
        Path(logical_root.as_posix())
        / f"{symbol}-{archive_type}-{month:%Y-%m}.zip"
        for month in months
    ]
    expected_checksum_paths = [
        archive_path.with_name(archive_path.name + ".CHECKSUM")
        for archive_path in expected_paths
    ]
    missing = [path for path in expected_paths if not path.is_file()]
    present = [path for path in expected_paths if path.is_file()]
    missing_checksums = [path for path in expected_checksum_paths if not path.is_file()]
    checksum_mismatches: list[dict[str, str]] = []
    checksum_verified_count = 0
    for archive_path, checksum_path in zip(
        expected_paths, expected_checksum_paths, strict=True
    ):
        if not archive_path.is_file() or not checksum_path.is_file():
            continue
        expected_digest = _checksum_sidecar_digest(checksum_path, archive_path.name)
        actual_digest = _sha256(archive_path)
        if expected_digest is None or expected_digest != actual_digest:
            checksum_mismatches.append(
                {
                    "archive_path": archive_path.as_posix(),
                    "checksum_path": checksum_path.as_posix(),
                    "expected_sha256": expected_digest or "INVALID_CHECKSUM_SIDECAR",
                    "actual_sha256": actual_digest,
                }
            )
        else:
            checksum_verified_count += 1
    if checksum_mismatches:
        status = "BLOCKED"
    elif missing or missing_checksums:
        status = "READY-FOR-HYDRATION"
    else:
        status = "READY"
    return {
        "status": status,
        "network_used": False,
        "expected_file_count": len(expected_paths),
        "present_file_count": len(present),
        "missing_file_count": len(missing),
        "present_paths": [path.as_posix() for path in present],
        "missing_paths": [path.as_posix() for path in missing],
        "expected_checksum_file_count": len(expected_checksum_paths),
        "missing_checksum_file_count": len(missing_checksums),
        "missing_checksum_paths": [path.as_posix() for path in missing_checksums],
        "checksum_verified_file_count": checksum_verified_count,
        "checksum_mismatch_count": len(checksum_mismatches),
        "checksum_mismatches": checksum_mismatches,
        "input_paths": expected_paths,
        "monthly_root": Path(logical_root.as_posix()),
        "daily_root": Path(daily_logical_root.as_posix()),
        "partition_cache_root": Path(str(cache_root_text)),
        "d4_path": Path(str(d4_path_text)),
        "archive_type": archive_type,
        "symbol": symbol,
        "interval": interval,
        "start_utc": request["start_utc_inclusive"],
        "end_utc": request["end_utc_exclusive"],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--input", action="append", type=Path)
    inputs.add_argument("--hydration-manifest", type=Path)
    inputs.add_argument("--d4-path", type=Path)
    inputs.add_argument("--canonical-kline-path", type=Path)
    parser.add_argument(
        "--canonical-kline-timeframe",
        choices=CANONICAL_KLINE_TAKER_TIMEFRAMES,
    )
    parser.add_argument("--archive-type", choices=sorted(SUPPORTED_ARCHIVE_TYPES))
    parser.add_argument("--interval", choices=sorted(SUPPORTED_INTERVALS_MS))
    parser.add_argument("--start-utc")
    parser.add_argument("--end-utc")
    parser.add_argument("--output-path", type=Path)
    parser.add_argument("--manifest-path", type=Path)
    parser.add_argument("--availability-catalog-path", type=Path)
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--check-hydration", action="store_true")
    parser.add_argument("--daily-archive-root", type=Path)
    parser.add_argument("--partition-cache-root", type=Path)
    parser.add_argument("--stop-after-partitions", type=int)
    parser.add_argument("--chunk-rows", type=int, default=500_000)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        required_outputs = {
            "output_path": args.output_path,
            "manifest_path": args.manifest_path,
            "availability_catalog_path": args.availability_catalog_path,
        }
        missing_outputs = [name for name, value in required_outputs.items() if value is None]
        if missing_outputs:
            raise TakerflowMaterializationError(
                "materialization arguments missing: " + ", ".join(missing_outputs)
            )
        if (args.canonical_kline_path is None) != (
            args.canonical_kline_timeframe is None
        ):
            raise TakerflowMaterializationError(
                "--canonical-kline-path and --canonical-kline-timeframe are a required pair"
            )
        if args.canonical_kline_path is not None:
            manifest = materialize_canonical_kline_takerflow_features(
                canonical_kline_path=args.canonical_kline_path,
                timeframe=args.canonical_kline_timeframe,
                output_path=args.output_path,
                manifest_path=args.manifest_path,
                availability_catalog_path=args.availability_catalog_path,
            )
            print(json.dumps({"ok": True, "manifest": manifest}, indent=2, sort_keys=True))
            return 0
        if args.d4_path is not None:
            manifest = materialize_d4_native_takerflow_features(
                d4_path=args.d4_path,
                output_path=args.output_path,
                manifest_path=args.manifest_path,
                availability_catalog_path=args.availability_catalog_path,
            )
            print(json.dumps({"ok": True, "manifest": manifest}, indent=2, sort_keys=True))
            return 0
        hydration = None
        if args.hydration_manifest is not None:
            hydration = inspect_hydration_manifest(args.hydration_manifest)
            if args.check_hydration:
                printable = {
                    key: value.as_posix() if isinstance(value, Path) else value
                    for key, value in hydration.items()
                    if key != "input_paths"
                }
                print(json.dumps(printable, indent=2, sort_keys=True))
                return 0
            if hydration["status"] != "READY":
                raise TakerflowMaterializationError(
                    f"hydration is not READY ({hydration['status']}); "
                    f"missing_archives={hydration['missing_file_count']}, "
                    f"missing_checksums={hydration['missing_checksum_file_count']}, "
                    f"checksum_mismatches={hydration['checksum_mismatch_count']}"
                )
        elif args.check_hydration:
            raise TakerflowMaterializationError(
                "--check-hydration requires --hydration-manifest"
            )
        if hydration is None:
            if not all((args.archive_type, args.interval, args.start_utc, args.end_utc)):
                raise TakerflowMaterializationError(
                    "direct inputs require archive-type, interval, start-utc, and end-utc"
                )
            input_paths = args.input or []
            archive_type = args.archive_type
            interval = args.interval
            start_utc = args.start_utc
            end_utc = args.end_utc
        else:
            input_paths = hydration["input_paths"]
            archive_type = hydration["archive_type"]
            interval = hydration["interval"]
            start_utc = hydration["start_utc"]
            end_utc = hydration["end_utc"]
        if hydration is not None:
            if archive_type != "trades" or interval != "15m" or args.symbol != "BTCUSDT":
                raise TakerflowMaterializationError(
                    "partitioned hydration supports only BTCUSDT raw trades at 15m"
                )
            manifest = materialize_partitioned_takerflow_features(
                monthly_root=hydration["monthly_root"],
                daily_root=args.daily_archive_root or hydration["daily_root"],
                cache_root=args.partition_cache_root or hydration["partition_cache_root"],
                start_utc=start_utc,
                end_utc=end_utc,
                output_path=args.output_path,
                manifest_path=args.manifest_path,
                availability_catalog_path=args.availability_catalog_path,
                d4_path=args.d4_path or hydration["d4_path"],
                stop_after_partitions=args.stop_after_partitions,
                chunk_rows=args.chunk_rows,
            )
        else:
            manifest = materialize_takerflow_features(
                input_paths=input_paths,
                archive_type=archive_type,
                interval=interval,
                start_utc=start_utc,
                end_utc=end_utc,
                output_path=args.output_path,
                manifest_path=args.manifest_path,
                availability_catalog_path=args.availability_catalog_path,
                symbol=args.symbol,
            )
    except TakerflowMaterializationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    print(json.dumps({"ok": True, "manifest": manifest}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
