"""Materialize causal completed-bar taker-flow features from local Binance archives.

This helper is deliberately offline.  It accepts one homogeneous set of local
Binance USD-M ``trades`` or ``aggTrades`` CSV/ZIP archives, removes exact
overlap duplicates, fails on conflicting duplicates, and writes a deterministic
CSV feature table plus a deterministic lineage/coverage manifest.

The output timestamp is the UTC bar open.  Features become observable only at
the exclusive bar close and therefore must not be used before
``feature_available_at``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation, localcontext
from itertools import chain
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from tools.data_ingestion.takerflow_archive_recon import (
    TradeRow,
    derive_taker_side,
)


MATERIALIZATION_VERSION = "takerflow-completed-bars-v1"
HYDRATION_MANIFEST_VERSION = "binance-usdm-takerflow-hydration-v1"
OUTPUT_SCHEMA_VERSION = "takerflow-feature-table-v1"
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


def _availability_contract(path: Path) -> dict[str, Any]:
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
            and entry.get("source_class") == REQUIRED_SOURCE_CLASS
            and entry.get("coverage_class") == REQUIRED_COVERAGE_CLASS
        ]
        if len(matches) != 1:
            raise TakerflowMaterializationError(
                f"{feature} lacks one approved full-history public trade-archive label"
            )
        matched.append(matches[0])
    return {
        "catalog_path": path.as_posix(),
        "catalog_sha256": _sha256(path),
        "coverage_class": REQUIRED_COVERAGE_CLASS,
        "source_class": REQUIRED_SOURCE_CLASS,
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
        canonical_first = tuple(value.strip().lower().replace(" ", "_") for value in first)
        has_header = set(required_columns).issubset(canonical_first)
        if has_header:
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
        "output": {
            "path": output_path.as_posix(),
            "format": "CSV UTF-8 LF",
            "columns": list(OUTPUT_COLUMNS),
            "row_count": len(output_rows),
            "size_bytes": output_path.stat().st_size,
            "sha256": _sha256(output_path),
            "git_tracking_status": "local_ignored_data",
        },
        "requested_range_data_complete": (
            coverage["missing_bar_count"] == 0 and len(event_gaps) == 0
        ),
        "network_used": False,
        "authority": (
            "research data readiness only; no candidate, Result Population, edge, "
            "promotion, runtime, or execution authority"
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
    if partition.get("scheme") != "monthly" or partition.get("timezone") != "UTC":
        raise TakerflowMaterializationError("hydration partition contract must be monthly UTC")
    root_text = payload.get("local_archive_root")
    if not isinstance(root_text, str):
        raise TakerflowMaterializationError("local_archive_root must be a path string")
    logical_root = PurePosixPath(root_text)
    if logical_root.is_absolute() or ".." in logical_root.parts:
        raise TakerflowMaterializationError("local_archive_root must be repository-relative")
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
    parser.add_argument("--archive-type", choices=sorted(SUPPORTED_ARCHIVE_TYPES))
    parser.add_argument("--interval", choices=sorted(SUPPORTED_INTERVALS_MS))
    parser.add_argument("--start-utc")
    parser.add_argument("--end-utc")
    parser.add_argument("--output-path", type=Path)
    parser.add_argument("--manifest-path", type=Path)
    parser.add_argument("--availability-catalog-path", type=Path)
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--check-hydration", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        hydration = None
        if args.hydration_manifest is not None:
            hydration = inspect_hydration_manifest(args.hydration_manifest)
            if args.check_hydration:
                printable = {key: value for key, value in hydration.items() if key != "input_paths"}
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
