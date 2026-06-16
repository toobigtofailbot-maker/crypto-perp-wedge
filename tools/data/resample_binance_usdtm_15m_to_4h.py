"""Derive a Binance USDT-M BTCUSDT 4h OHLCV slice from validated 15m CSV data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from tools.data.import_binance_usdtm_15m import sha256_bytes


SYMBOL = "BTCUSDT"
VENUE = "Binance"
MARKET_TYPE = "USDT-M perpetual"
STREAM = "ohlcv"
PARENT_TIMEFRAME = "15m"
TIMEFRAME = "4h"
DATASET_ID = "binance_usdtm_btcusdt_ohlcv_4h"
PARENT_DATASET_ID = "binance_usdtm_btcusdt_ohlcv_15m"
SOURCE_TYPE = "derived_offline_resample"
DATA_CONTRACT_VERSION = "2026-06-binance-usdtm-4h-derived-contract-v1"
RESAMPLING_VERSION = "wp-data-resample-4h-01-v1"
VALIDATOR_VERSION = "wp-data-resample-4h-01-validator-v1"
CATALOG_VERSION = "wp-data-resample-4h-01-catalog-v1"
SLICE_IDENTITY_VERSION = "binance-usdtm-btcusdt-ohlcv-4h-derived-slice-identity-v1"
EXPECTED_BARS_PER_OUTPUT_ROW = 16
PARENT_CADENCE_MS = 15 * 60 * 1000
OUTPUT_CADENCE_MS = 4 * 60 * 60 * 1000

OUTPUT_COLUMNS = [
    "open_time_ms",
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time_ms",
    "quote_asset_volume",
    "num_trades",
    "taker_buy_base_vol",
    "taker_buy_quote_vol",
    "ignore",
]

SUM_COLUMNS = [
    "volume",
    "quote_asset_volume",
    "taker_buy_base_vol",
    "taker_buy_quote_vol",
    "ignore",
]

AGGREGATION_MAP = {
    "open_time_ms": "first",
    "open_time": "first",
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum",
    "close_time_ms": "last_15m_close_time_ms",
    "quote_asset_volume": "sum",
    "num_trades": "sum",
    "taker_buy_base_vol": "sum",
    "taker_buy_quote_vol": "sum",
    "ignore": "sum_numeric",
}

DEFAULT_PARENT_CSV = Path(
    "data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv"
)
DEFAULT_OUTPUT_CSV = Path(
    "data/processed/d4h/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_d4h_resampled.csv"
)
DEFAULT_PARENT_CATALOG = Path(
    "research/data_slices/binance_usdtm_btcusdt_15m/"
    "binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json"
)
DEFAULT_PARENT_VALIDATION = Path(
    "research/data_slices/binance_usdtm_btcusdt_15m/"
    "binance_usdtm_btcusdt_15m_20200101_20260411.validation_report.json"
)
DEFAULT_OUTPUT_DIR = Path("research/data_slices/binance_usdtm_btcusdt_4h")
DEFAULT_VALIDATION_REPORT = (
    DEFAULT_OUTPUT_DIR / "binance_usdtm_btcusdt_4h_20200101_20260411.validation_report.json"
)
DEFAULT_CATALOG_SLICE = DEFAULT_OUTPUT_DIR / "binance_usdtm_btcusdt_4h_20200101_20260411.catalog_slice.json"
DEFAULT_DERIVATION_REPORT = (
    DEFAULT_OUTPUT_DIR / "binance_usdtm_btcusdt_4h_20200101_20260411.derivation_report.json"
)


class ResampleError(RuntimeError):
    """Raised when a deterministic 4h slice cannot be derived."""


@dataclass(frozen=True)
class Gap:
    start_utc: str
    end_utc: str
    missing_bars: int


@dataclass(frozen=True)
class DuplicateGroup:
    open_time_utc: str
    count: int


@dataclass(frozen=True)
class ResampleResult:
    ok: bool
    output_csv_path: str
    output_csv_sha256: str
    validation_report_path: str
    validation_report_sha256: str
    derivation_report_path: str
    derivation_report_sha256: str
    catalog_path: str
    catalog_sha256: str
    data_slice_identity: str
    row_count: int
    expected_row_count: int
    start_utc: str
    end_utc: str


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _identity_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_json_bytes(payload)).hexdigest()


def _hash_file(path: Path) -> str:
    if not path.exists():
        raise ResampleError(f"file does not exist: {path}")
    return sha256_bytes(path.read_bytes())


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ResampleError(f"cannot read JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ResampleError(f"JSON payload must be an object: {path}")
    return payload


def _iso(timestamp: datetime) -> str:
    return timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_utc(value: str, label: str, row_number: int, errors: list[str]) -> datetime | None:
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"row {row_number}: {label} contains unparseable timestamp")
        return None
    if timestamp.tzinfo is None:
        errors.append(f"row {row_number}: {label} must be timezone-aware UTC")
        return None
    return timestamp.astimezone(timezone.utc)


def _parse_int(value: str, label: str, row_number: int, errors: list[str]) -> int | None:
    try:
        return int(str(value).strip())
    except ValueError:
        errors.append(f"row {row_number}: {label} contains non-integer value")
        return None


def _parse_decimal(value: str, label: str, row_number: int, errors: list[str]) -> Decimal | None:
    try:
        decimal = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        errors.append(f"row {row_number}: {label} contains non-numeric value")
        return None
    if not decimal.is_finite():
        errors.append(f"row {row_number}: {label} contains non-finite value")
        return None
    return decimal


def _decimal_string(value: Decimal) -> str:
    if value == value.to_integral_value():
        return str(value.quantize(Decimal(1)))
    return format(value.normalize(), "f")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != OUTPUT_COLUMNS:
            raise ResampleError(f"15m CSV columns must exactly match {OUTPUT_COLUMNS}")
        return [{column: row[column] for column in OUTPUT_COLUMNS} for row in reader]


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _find_duplicate_groups(open_times: list[datetime]) -> list[DuplicateGroup]:
    counts: dict[datetime, int] = {}
    for timestamp in open_times:
        counts[timestamp] = counts.get(timestamp, 0) + 1
    return [
        DuplicateGroup(open_time_utc=_iso(timestamp), count=count)
        for timestamp, count in sorted(counts.items())
        if count > 1
    ]


def _find_gaps(open_times: list[datetime]) -> list[Gap]:
    gaps: list[Gap] = []
    unique_sorted = sorted(set(open_times))
    for previous, current in zip(unique_sorted, unique_sorted[1:]):
        delta_ms = int((current - previous).total_seconds() * 1000)
        if delta_ms > PARENT_CADENCE_MS:
            missing = (delta_ms // PARENT_CADENCE_MS) - 1
            gaps.append(
                Gap(
                    start_utc=_iso(previous + timedelta(minutes=15)),
                    end_utc=_iso(current - timedelta(minutes=15)),
                    missing_bars=int(missing),
                )
            )
    return gaps


def _validate_parent_rows(rows: list[dict[str, str]]) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    if not rows:
        return {
            "row_count": 0,
            "expected_row_count": 0,
            "start_utc": None,
            "end_utc": None,
            "duplicates": [],
            "gaps": [],
            "partial_window_count": 0,
        }, ["15m parent CSV contains no rows"]

    open_times: list[datetime] = []
    open_time_ms_values: list[int] = []
    for index, row in enumerate(rows):
        row_number = index + 1
        open_time = _parse_utc(row["open_time"], "open_time", row_number, errors)
        open_time_ms = _parse_int(row["open_time_ms"], "open_time_ms", row_number, errors)
        close_time_ms = _parse_int(row["close_time_ms"], "close_time_ms", row_number, errors)
        if open_time is not None:
            open_times.append(open_time)
            derived_ms = int(open_time.timestamp() * 1000)
            if open_time_ms is not None and derived_ms != open_time_ms:
                errors.append(f"row {row_number}: open_time_ms and open_time disagree")
        if open_time_ms is not None:
            open_time_ms_values.append(open_time_ms)
            if open_time_ms % PARENT_CADENCE_MS != 0:
                errors.append(f"row {row_number}: open_time_ms is not aligned to 15m UTC bars")
        if close_time_ms is not None and open_time_ms is not None and close_time_ms != open_time_ms + PARENT_CADENCE_MS - 1:
            errors.append(f"row {row_number}: close_time_ms does not match Binance 15m close convention")

        numeric_values: dict[str, Decimal] = {}
        for column in ("open", "high", "low", "close", "volume", "quote_asset_volume", "taker_buy_base_vol", "taker_buy_quote_vol", "ignore"):
            decimal = _parse_decimal(row[column], column, row_number, errors)
            if decimal is not None:
                numeric_values[column] = decimal
        num_trades = _parse_int(row["num_trades"], "num_trades", row_number, errors)
        if {"open", "high", "low", "close", "volume"}.issubset(numeric_values):
            open_ = numeric_values["open"]
            high = numeric_values["high"]
            low = numeric_values["low"]
            close = numeric_values["close"]
            volume = numeric_values["volume"]
            if min(open_, high, low, close) <= 0:
                errors.append(f"row {row_number}: OHLC values must be positive")
            if high < max(open_, close):
                errors.append(f"row {row_number}: high is below open/close")
            if low > min(open_, close):
                errors.append(f"row {row_number}: low is above open/close")
            if high < low:
                errors.append(f"row {row_number}: high is below low")
            if volume < 0:
                errors.append(f"row {row_number}: volume is negative")
        if num_trades is not None and num_trades < 0:
            errors.append(f"row {row_number}: num_trades is negative")

    if len(open_times) == len(rows):
        if any(current <= previous for previous, current in zip(open_times, open_times[1:])):
            errors.append("open_time values are not strictly ordered")
        duplicates = _find_duplicate_groups(open_times)
        gaps = _find_gaps(open_times)
    else:
        duplicates = []
        gaps = []

    if duplicates:
        errors.append(f"duplicate open_time values detected: {sum(group.count for group in duplicates)} rows")
    if gaps:
        errors.append(f"missing 15m bars detected: {sum(gap.missing_bars for gap in gaps)} bars")

    partial_window_count = 1 if len(rows) % EXPECTED_BARS_PER_OUTPUT_ROW else 0
    if partial_window_count:
        errors.append("15m parent row count is not divisible by 16")

    start_utc = _iso(open_times[0]) if open_times else None
    end_utc = _iso(open_times[-1]) if open_times else None
    expected_count = 0
    if open_times:
        expected_count = int((open_times[-1] - open_times[0]).total_seconds() // (15 * 60)) + 1

    return {
        "row_count": len(rows),
        "expected_row_count": expected_count,
        "start_utc": start_utc,
        "end_utc": end_utc,
        "duplicates": [asdict(group) for group in duplicates],
        "gaps": [asdict(gap) for gap in gaps],
        "partial_window_count": partial_window_count,
    }, errors


def _assert_group_alignment(group: list[dict[str, str]], group_index: int) -> None:
    start = datetime.fromisoformat(group[0]["open_time"].replace("Z", "+00:00")).astimezone(timezone.utc)
    if start.hour % 4 != 0 or start.minute != 0 or start.second != 0 or start.microsecond != 0:
        raise ResampleError(f"group {group_index} does not start on a UTC 4h boundary")
    for offset, row in enumerate(group):
        expected_ms = int(start.timestamp() * 1000) + offset * PARENT_CADENCE_MS
        actual_ms = int(row["open_time_ms"])
        if actual_ms != expected_ms:
            raise ResampleError(f"group {group_index} is not a contiguous 16-row 15m window")


def _max_value(rows: list[dict[str, str]], column: str) -> str:
    return max(rows, key=lambda row: Decimal(row[column]))[column]


def _min_value(rows: list[dict[str, str]], column: str) -> str:
    return min(rows, key=lambda row: Decimal(row[column]))[column]


def _sum_decimal(rows: list[dict[str, str]], column: str) -> str:
    return _decimal_string(sum((Decimal(row[column]) for row in rows), Decimal(0)))


def _sum_int(rows: list[dict[str, str]], column: str) -> str:
    return str(sum(int(row[column]) for row in rows))


def resample_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict[str, Any]]:
    parent_facts, errors = _validate_parent_rows(rows)
    if errors:
        raise ResampleError("; ".join(errors))

    output_rows: list[dict[str, str]] = []
    for group_index, start_index in enumerate(range(0, len(rows), EXPECTED_BARS_PER_OUTPUT_ROW), start=1):
        group = rows[start_index : start_index + EXPECTED_BARS_PER_OUTPUT_ROW]
        if len(group) != EXPECTED_BARS_PER_OUTPUT_ROW:
            raise ResampleError(f"group {group_index} is partial")
        _assert_group_alignment(group, group_index)
        first = group[0]
        last = group[-1]
        expected_close_time_ms = int(first["open_time_ms"]) + OUTPUT_CADENCE_MS - 1
        if int(last["close_time_ms"]) != expected_close_time_ms:
            raise ResampleError(f"group {group_index} close_time_ms does not match 4h Binance close convention")
        output_rows.append(
            {
                "open_time_ms": first["open_time_ms"],
                "open_time": first["open_time"],
                "open": first["open"],
                "high": _max_value(group, "high"),
                "low": _min_value(group, "low"),
                "close": last["close"],
                "volume": _sum_decimal(group, "volume"),
                "close_time_ms": last["close_time_ms"],
                "quote_asset_volume": _sum_decimal(group, "quote_asset_volume"),
                "num_trades": _sum_int(group, "num_trades"),
                "taker_buy_base_vol": _sum_decimal(group, "taker_buy_base_vol"),
                "taker_buy_quote_vol": _sum_decimal(group, "taker_buy_quote_vol"),
                "ignore": _sum_decimal(group, "ignore"),
            }
        )

    output_facts = {
        "row_count": len(output_rows),
        "expected_row_count": parent_facts["row_count"] // EXPECTED_BARS_PER_OUTPUT_ROW,
        "start_utc": output_rows[0]["open_time"] if output_rows else None,
        "end_utc": output_rows[-1]["open_time"] if output_rows else None,
        "parent": parent_facts,
        "partial_window_count": 0,
        "duplicate_row_count": 0,
        "gap_count": 0,
        "missing_bar_count": 0,
    }
    return output_rows, output_facts


def _validate_parent_metadata(
    *,
    parent_csv_path: Path,
    parent_catalog_path: Path,
    parent_validation_path: Path,
    parent_sha256: str,
) -> dict[str, Any]:
    catalog = _load_json(parent_catalog_path)
    validation = _load_json(parent_validation_path)
    validation_sha = _hash_file(parent_validation_path)

    expected_identity = (
        "binance_usdtm_btcusdt_ohlcv_15m:sha256:"
        "3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664"
    )
    checks = [
        (catalog.get("dataset_id") == PARENT_DATASET_ID, "parent catalog dataset_id differs"),
        (catalog.get("symbol") == SYMBOL, "parent catalog symbol differs"),
        (catalog.get("timeframe") == PARENT_TIMEFRAME, "parent catalog timeframe differs"),
        (catalog.get("validation_report", {}).get("sha256") == validation_sha, "parent validation file SHA differs from catalog"),
        (catalog.get("validation_report", {}).get("sha256") == "785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c", "parent validation SHA differs from expected"),
        (catalog.get("normalized", {}).get("sha256") == parent_sha256, "parent normalized SHA differs from catalog"),
        (parent_sha256 == "c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab", "parent normalized SHA differs from expected"),
        (catalog.get("source", {}).get("raw_source_sha256") == "343b639e35ce79824d26bddf6d70af2641c9d76003301e303f83cdf61d4feab4", "parent raw source SHA differs"),
        (catalog.get("slice_identity", {}).get("data_slice_identity") == expected_identity, "parent data slice identity differs"),
        (validation.get("ok") is True, "parent validation ok is not true"),
        (validation.get("validation", {}).get("status") == "PASS", "parent validation status is not PASS"),
        (int(validation.get("range", {}).get("row_count", 0)) == 220128, "parent validation row count differs"),
        (validation.get("range", {}).get("start_utc") == "2020-01-01T00:00:00Z", "parent validation start differs"),
        (validation.get("range", {}).get("end_utc") == "2026-04-11T23:45:00Z", "parent validation end differs"),
        (int(validation.get("gap_summary", {}).get("missing_bar_count", -1)) == 0, "parent validation gaps differ"),
        (int(validation.get("duplicate_summary", {}).get("duplicate_row_count", -1)) == 0, "parent validation duplicates differ"),
    ]
    failures = [message for ok, message in checks if not ok]
    if failures:
        raise ResampleError("; ".join(failures))

    return {
        "catalog": catalog,
        "validation": validation,
        "parent_validation_sha256": validation_sha,
        "parent_catalog_path": str(parent_catalog_path),
        "parent_validation_path": str(parent_validation_path),
        "parent_csv_path": str(parent_csv_path),
        "parent_normalized_sha256": parent_sha256,
        "parent_data_slice_identity": expected_identity,
    }


def _build_validation_report(
    *,
    output_csv_path: Path,
    output_csv_sha256: str,
    output_facts: dict[str, Any],
    parent_metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "ok": True,
        "data_contract_version": DATA_CONTRACT_VERSION,
        "validator_version": VALIDATOR_VERSION,
        "symbol": SYMBOL,
        "venue": VENUE,
        "market_type": MARKET_TYPE,
        "stream": STREAM,
        "timeframe": TIMEFRAME,
        "source": {
            "parent_local_processed_file_path": parent_metadata["parent_csv_path"],
            "parent_normalized_sha256": parent_metadata["parent_normalized_sha256"],
            "parent_catalog_slice_path": parent_metadata["parent_catalog_path"],
            "parent_data_slice_identity": parent_metadata["parent_data_slice_identity"],
            "no_credentials": True,
            "no_live_api": True,
            "offline_only": True,
        },
        "derivation": {
            "method": "deterministic 15m-to-4h UTC-boundary resampling",
            "resampling_version": RESAMPLING_VERSION,
            "aggregation_map": AGGREGATION_MAP,
            "expected_bars_per_output_row": EXPECTED_BARS_PER_OUTPUT_ROW,
            "close_time_ms_rule": "last 15m row close_time_ms; validated to equal 4h open_time_ms + 4h - 1ms",
            "no_fill": True,
            "no_interpolation": True,
            "no_deduplication": True,
            "no_synthetic_bars": True,
        },
        "normalized": {
            "path": str(output_csv_path),
            "sha256": output_csv_sha256,
        },
        "range": {
            "start_utc": output_facts["start_utc"],
            "end_utc": output_facts["end_utc"],
            "row_count": output_facts["row_count"],
            "expected_row_count": output_facts["expected_row_count"],
        },
        "validation": {
            "status": "PASS",
            "errors": [],
            "utc_4h_boundary_alignment": "PASS",
            "duplicate_count": 0,
            "gap_count": 0,
            "missing_bar_count": 0,
            "partial_window_count": 0,
            "ohlc_integrity": "PASS",
            "no_fill": True,
            "no_interpolation": True,
            "no_deduplication": True,
            "no_synthesis": True,
        },
        "gap_summary": {
            "gap_count": 0,
            "missing_bar_count": 0,
            "gaps": [],
            "policy": "detect_report_do_not_fill_or_interpolate",
        },
        "duplicate_summary": {
            "duplicate_group_count": 0,
            "duplicate_row_count": 0,
            "duplicates": [],
            "policy": "detect_report_do_not_deduplicate",
        },
        "boundary": {
            "offline_local_input_only": True,
            "no_exchange_contact": True,
            "no_runtime_contact": True,
            "no_paper_live_contact": True,
            "no_result_population_write": True,
            "no_strategy_artifact_mutation": True,
        },
    }


def _build_derivation_report(
    *,
    output_csv_path: Path,
    output_csv_sha256: str,
    output_facts: dict[str, Any],
    parent_metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "ok": True,
        "package": "WP-DATA-RESAMPLE-4H-01",
        "derivation_type": SOURCE_TYPE,
        "method": "deterministic 15m-to-4h UTC-boundary resampling",
        "resampling_version": RESAMPLING_VERSION,
        "symbol": SYMBOL,
        "venue": VENUE,
        "market_type": MARKET_TYPE,
        "stream": STREAM,
        "timeframe": TIMEFRAME,
        "parent_timeframe": PARENT_TIMEFRAME,
        "parent": {
            "dataset_id": PARENT_DATASET_ID,
            "local_processed_file_path": parent_metadata["parent_csv_path"],
            "normalized_sha256": parent_metadata["parent_normalized_sha256"],
            "validation_report_path": parent_metadata["parent_validation_path"],
            "validation_report_sha256": parent_metadata["parent_validation_sha256"],
            "catalog_slice_path": parent_metadata["parent_catalog_path"],
            "data_slice_identity": parent_metadata["parent_data_slice_identity"],
            "row_count": output_facts["parent"]["row_count"],
            "range": {
                "start_utc": output_facts["parent"]["start_utc"],
                "end_utc": output_facts["parent"]["end_utc"],
            },
            "gap_count": 0,
            "duplicate_row_count": 0,
        },
        "output": {
            "dataset_id": DATASET_ID,
            "path": str(output_csv_path),
            "sha256": output_csv_sha256,
            "row_count": output_facts["row_count"],
            "expected_row_count": output_facts["expected_row_count"],
            "range": {
                "start_utc": output_facts["start_utc"],
                "end_utc": output_facts["end_utc"],
            },
        },
        "aggregation_map": AGGREGATION_MAP,
        "expected_bars_per_output_row": EXPECTED_BARS_PER_OUTPUT_ROW,
        "close_time_ms_rule": "last 15m row close_time_ms; validated to equal 4h open_time_ms + 4h - 1ms",
        "determinism": {
            "canonical_json_sort_keys_minified_ascii_for_identity": True,
            "no_timezone_local_alignment": True,
            "no_fill": True,
            "no_interpolation": True,
            "no_deduplication": True,
            "no_synthetic_bars": True,
        },
        "boundary": {
            "offline_local_input_only": True,
            "no_exchange_contact": True,
            "no_runtime_contact": True,
            "no_paper_live_contact": True,
            "no_result_population_write": True,
            "no_strategy_artifact_mutation": True,
        },
    }


def _catalog_ref(start_utc: str, end_utc: str, slice_hash: str) -> str:
    start = start_utc.replace(":", "").replace("-", "")
    end = end_utc.replace(":", "").replace("-", "")
    return f"{DATASET_ID}.derived_offline_resample.{TIMEFRAME}.{start}.{end}.sha256_{slice_hash[:16]}"


def _build_catalog_entry(
    *,
    output_csv_path: Path,
    output_csv_sha256: str,
    validation_report_path: Path,
    validation_report_sha256: str,
    derivation_report_path: Path,
    derivation_report_sha256: str,
    output_facts: dict[str, Any],
    parent_metadata: dict[str, Any],
) -> dict[str, Any]:
    range_facts = {
        "start_utc": output_facts["start_utc"],
        "end_utc": output_facts["end_utc"],
        "row_count": output_facts["row_count"],
        "expected_row_count": output_facts["expected_row_count"],
    }
    gap_summary = {
        "gap_count": 0,
        "missing_bar_count": 0,
        "gaps": [],
        "policy": "detect_report_do_not_fill_or_interpolate",
    }
    duplicate_summary = {
        "duplicate_group_count": 0,
        "duplicate_row_count": 0,
        "duplicates": [],
        "policy": "detect_report_do_not_deduplicate",
    }
    identity_inputs = {
        "slice_identity_version": SLICE_IDENTITY_VERSION,
        "dataset_id": DATASET_ID,
        "symbol": SYMBOL,
        "venue": VENUE,
        "market_type": MARKET_TYPE,
        "stream": STREAM,
        "timeframe": TIMEFRAME,
        "source_type": SOURCE_TYPE,
        "parent_dataset_id": PARENT_DATASET_ID,
        "parent_normalized_sha256": parent_metadata["parent_normalized_sha256"],
        "parent_validation_report_sha256": parent_metadata["parent_validation_sha256"],
        "parent_data_slice_identity": parent_metadata["parent_data_slice_identity"],
        "parent_catalog_ref": parent_metadata["catalog"]["catalog_ref"],
        "normalized_sha256": output_csv_sha256,
        "validation_report_sha256": validation_report_sha256,
        "validation_status": "PASS",
        "resampling_method": "deterministic 15m-to-4h UTC-boundary resampling",
        "resampling_version": RESAMPLING_VERSION,
        "aggregation_map": AGGREGATION_MAP,
        "range": range_facts,
        "gap_summary": gap_summary,
        "duplicate_summary": duplicate_summary,
    }
    slice_hash = _identity_hash(identity_inputs)
    data_slice_identity = f"{DATASET_ID}:sha256:{slice_hash}"
    return {
        "catalog_version": CATALOG_VERSION,
        "catalog_ref": _catalog_ref(range_facts["start_utc"], range_facts["end_utc"], slice_hash),
        "catalog_status": "valid_offline_derived_slice",
        "dataset_id": DATASET_ID,
        "source_type": SOURCE_TYPE,
        "symbol": SYMBOL,
        "venue": VENUE,
        "market_type": MARKET_TYPE,
        "stream": STREAM,
        "timeframe": TIMEFRAME,
        "data_contract_version": DATA_CONTRACT_VERSION,
        "resampling_version": RESAMPLING_VERSION,
        "validator_version": VALIDATOR_VERSION,
        "normalized": {
            "path": str(output_csv_path),
            "sha256": output_csv_sha256,
        },
        "validation_report": {
            "path": str(validation_report_path),
            "sha256": validation_report_sha256,
            "status": "PASS",
        },
        "derivation_report": {
            "path": str(derivation_report_path),
            "sha256": derivation_report_sha256,
        },
        "parent": {
            "dataset_id": PARENT_DATASET_ID,
            "normalized_path": parent_metadata["parent_csv_path"],
            "normalized_sha256": parent_metadata["parent_normalized_sha256"],
            "validation_report_path": parent_metadata["parent_validation_path"],
            "validation_report_sha256": parent_metadata["parent_validation_sha256"],
            "catalog_slice_path": parent_metadata["parent_catalog_path"],
            "catalog_ref": parent_metadata["catalog"]["catalog_ref"],
            "data_slice_identity": parent_metadata["parent_data_slice_identity"],
        },
        "range": range_facts,
        "gap_summary": gap_summary,
        "duplicate_summary": duplicate_summary,
        "derivation": {
            "method": "deterministic 15m-to-4h UTC-boundary resampling",
            "aggregation_map": AGGREGATION_MAP,
            "expected_bars_per_output_row": EXPECTED_BARS_PER_OUTPUT_ROW,
            "close_time_ms_rule": "last 15m row close_time_ms; validated to equal 4h open_time_ms + 4h - 1ms",
            "no_fill": True,
            "no_interpolation": True,
            "no_deduplication": True,
            "no_synthetic_bars": True,
        },
        "slice_identity": {
            "data_slice_identity": data_slice_identity,
            "hash": slice_hash,
            "hash_algorithm": "sha256",
            "identity_inputs": identity_inputs,
            "identity_input_ordering": "canonical_json_sort_keys_minified_ascii",
        },
        "evidence_limit": {
            "not_strategy_quality_evidence": True,
            "no_result_population": True,
        },
        "boundary": {
            "offline_local_input_only": True,
            "no_exchange_contact": True,
            "no_runtime_contact": True,
            "no_paper_live_contact": True,
            "no_result_population_write": True,
            "no_strategy_artifact_mutation": True,
        },
    }


def derive_slice(
    *,
    parent_csv_path: Path = DEFAULT_PARENT_CSV,
    output_csv_path: Path = DEFAULT_OUTPUT_CSV,
    parent_catalog_path: Path = DEFAULT_PARENT_CATALOG,
    parent_validation_path: Path = DEFAULT_PARENT_VALIDATION,
    validation_report_path: Path = DEFAULT_VALIDATION_REPORT,
    derivation_report_path: Path = DEFAULT_DERIVATION_REPORT,
    catalog_path: Path = DEFAULT_CATALOG_SLICE,
) -> ResampleResult:
    parent_sha256 = _hash_file(parent_csv_path)
    parent_metadata = _validate_parent_metadata(
        parent_csv_path=parent_csv_path,
        parent_catalog_path=parent_catalog_path,
        parent_validation_path=parent_validation_path,
        parent_sha256=parent_sha256,
    )
    rows = _read_csv(parent_csv_path)
    output_rows, output_facts = resample_rows(rows)
    _write_csv(output_csv_path, output_rows)
    output_csv_sha256 = _hash_file(output_csv_path)

    validation_report = _build_validation_report(
        output_csv_path=output_csv_path,
        output_csv_sha256=output_csv_sha256,
        output_facts=output_facts,
        parent_metadata=parent_metadata,
    )
    _write_json(validation_report_path, validation_report)
    validation_report_sha256 = _hash_file(validation_report_path)

    derivation_report = _build_derivation_report(
        output_csv_path=output_csv_path,
        output_csv_sha256=output_csv_sha256,
        output_facts=output_facts,
        parent_metadata=parent_metadata,
    )
    _write_json(derivation_report_path, derivation_report)
    derivation_report_sha256 = _hash_file(derivation_report_path)

    catalog_entry = _build_catalog_entry(
        output_csv_path=output_csv_path,
        output_csv_sha256=output_csv_sha256,
        validation_report_path=validation_report_path,
        validation_report_sha256=validation_report_sha256,
        derivation_report_path=derivation_report_path,
        derivation_report_sha256=derivation_report_sha256,
        output_facts=output_facts,
        parent_metadata=parent_metadata,
    )
    _write_json(catalog_path, catalog_entry)
    catalog_sha256 = _hash_file(catalog_path)

    return ResampleResult(
        ok=True,
        output_csv_path=str(output_csv_path),
        output_csv_sha256=output_csv_sha256,
        validation_report_path=str(validation_report_path),
        validation_report_sha256=validation_report_sha256,
        derivation_report_path=str(derivation_report_path),
        derivation_report_sha256=derivation_report_sha256,
        catalog_path=str(catalog_path),
        catalog_sha256=catalog_sha256,
        data_slice_identity=catalog_entry["slice_identity"]["data_slice_identity"],
        row_count=int(output_facts["row_count"]),
        expected_row_count=int(output_facts["expected_row_count"]),
        start_utc=str(output_facts["start_utc"]),
        end_utc=str(output_facts["end_utc"]),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-csv", type=Path, default=DEFAULT_PARENT_CSV)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--parent-catalog", type=Path, default=DEFAULT_PARENT_CATALOG)
    parser.add_argument("--parent-validation", type=Path, default=DEFAULT_PARENT_VALIDATION)
    parser.add_argument("--validation-report", type=Path, default=DEFAULT_VALIDATION_REPORT)
    parser.add_argument("--derivation-report", type=Path, default=DEFAULT_DERIVATION_REPORT)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG_SLICE)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = derive_slice(
            parent_csv_path=args.parent_csv,
            output_csv_path=args.output_csv,
            parent_catalog_path=args.parent_catalog,
            parent_validation_path=args.parent_validation,
            validation_report_path=args.validation_report,
            derivation_report_path=args.derivation_report,
            catalog_path=args.catalog,
        )
    except ResampleError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
