"""Validate D2-normalized Binance USDT-M BTCUSDT 15m OHLCV CSV data."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd

from tools.data.import_binance_usdtm_15m import (
    CADENCE,
    CADENCE_MS,
    CONTRACT_VERSION,
    MARKET_TYPE,
    OUTPUT_COLUMNS,
    STREAM,
    SYMBOL,
    TIMEFRAME,
    sha256_bytes,
)


VALIDATOR_VERSION = "wp-d3-offline-binance-usdtm-15m-validator-v1"
NUMERIC_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_asset_volume",
    "taker_buy_base_vol",
    "taker_buy_quote_vol",
]


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
class ValidationResult:
    ok: bool
    report_path: str
    validated_output_path: str | None
    input_sha256: str
    row_count: int
    expected_row_count: int
    start_utc: str | None
    end_utc: str | None
    duplicate_group_count: int
    duplicate_row_count: int
    gap_count: int
    missing_bar_count: int
    errors: list[str]


def _iso(timestamp: pd.Timestamp) -> str:
    return timestamp.isoformat().replace("+00:00", "Z")


def _timestamp_ms(series: pd.Series) -> pd.Series:
    utc_naive = series.dt.tz_convert("UTC").dt.tz_localize(None)
    return utc_naive.astype("datetime64[ns]").astype("int64") // 1_000_000


def _parse_timestamps(series: pd.Series, label: str, errors: list[str]) -> pd.Series:
    parsed = pd.to_datetime(series, utc=True, errors="coerce")
    if parsed.isna().any():
        errors.append(f"{label} contains unparseable timestamp values")
    return parsed


def _parse_integer_ms(series: pd.Series, label: str, errors: list[str]) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.isna().any():
        errors.append(f"{label} contains non-numeric values")
        return numeric
    fractional = numeric != numeric.astype("int64")
    if fractional.any():
        errors.append(f"{label} contains non-integer millisecond values")
    return numeric.astype("int64")


def _parse_optional_integer_ms(series: pd.Series, label: str, errors: list[str]) -> pd.Series:
    blank = series.astype(str).str.strip() == ""
    numeric = pd.to_numeric(series.where(~blank), errors="coerce")
    if numeric[~blank].isna().any():
        errors.append(f"{label} contains non-numeric values")
        return numeric
    fractional = numeric[~blank] != numeric[~blank].astype("int64")
    if fractional.any():
        errors.append(f"{label} contains non-integer millisecond values")
    return numeric


def _decimal(value: Any, column: str, row_number: int, errors: list[str]) -> Decimal | None:
    if pd.isna(value):
        errors.append(f"row {row_number}: {column} contains null value")
        return None
    try:
        decimal = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        errors.append(f"row {row_number}: {column} contains non-numeric value")
        return None
    if not decimal.is_finite():
        errors.append(f"row {row_number}: {column} contains non-finite value")
        return None
    return decimal


def _find_duplicates(open_times: pd.Series) -> list[DuplicateGroup]:
    duplicates = open_times[open_times.duplicated(keep=False)]
    groups: list[DuplicateGroup] = []
    for timestamp, values in duplicates.groupby(duplicates):
        groups.append(DuplicateGroup(open_time_utc=_iso(timestamp), count=int(len(values))))
    return sorted(groups, key=lambda group: group.open_time_utc)


def _find_gaps(open_times: pd.Series) -> list[Gap]:
    gaps: list[Gap] = []
    previous = None
    for current in sorted(open_times.dropna().drop_duplicates().tolist()):
        if previous is not None:
            delta = current - previous
            if delta > CADENCE:
                missing = int(delta / CADENCE) - 1
                gaps.append(
                    Gap(
                        start_utc=_iso(previous + CADENCE),
                        end_utc=_iso(current - CADENCE),
                        missing_bars=missing,
                    )
                )
        previous = current
    return gaps


def _empty_facts() -> dict[str, Any]:
    return {
        "row_count": 0,
        "expected_row_count": 0,
        "start_utc": None,
        "end_utc": None,
        "duplicates": [],
        "gaps": [],
    }


def validate_frame(frame: pd.DataFrame) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    expected_columns = list(OUTPUT_COLUMNS)
    actual_columns = list(frame.columns)
    if actual_columns != expected_columns:
        errors.append(f"normalized CSV columns must exactly match D2 output columns: {expected_columns}")
        return _empty_facts(), errors
    if frame.empty:
        errors.append("normalized CSV contains no rows")
        return _empty_facts(), errors

    open_times = _parse_timestamps(frame["open_time"], "open_time", errors)
    open_time_ms = _parse_integer_ms(frame["open_time_ms"], "open_time_ms", errors)
    close_time_ms = _parse_optional_integer_ms(frame["close_time_ms"], "close_time_ms", errors)

    if not open_times.isna().any() and not open_time_ms.isna().any():
        derived_ms = _timestamp_ms(open_times)
        mismatch = derived_ms != open_time_ms
        if mismatch.any():
            errors.append(
                "open_time_ms and open_time disagree for "
                f"{int(mismatch.sum())} row(s)"
            )
        misaligned = (open_time_ms % CADENCE_MS) != 0
        if misaligned.any():
            errors.append(f"{int(misaligned.sum())} open_time values are not aligned to 15m UTC bars")
        if not open_times.is_monotonic_increasing:
            errors.append("open_time values are not strictly ordered")

    nonblank_close_time = close_time_ms.notna()
    close_times = pd.to_datetime(close_time_ms[nonblank_close_time], unit="ms", utc=True, errors="coerce")
    if close_times.isna().any():
        errors.append("close_time_ms contains unparseable millisecond values")

    duplicates = _find_duplicates(open_times) if not open_times.isna().any() else []
    gaps = _find_gaps(open_times) if not open_times.isna().any() else []
    if duplicates:
        errors.append(f"duplicate open_time values detected: {sum(group.count for group in duplicates)} rows")
    if gaps:
        errors.append(f"missing 15m bars detected: {sum(gap.missing_bars for gap in gaps)} bars")

    parsed_numbers: dict[str, list[Decimal | None]] = {column: [] for column in NUMERIC_COLUMNS}
    for row_index, row in frame.iterrows():
        row_number = int(row_index) + 1
        for column in NUMERIC_COLUMNS:
            parsed_numbers[column].append(_decimal(row[column], column, row_number, errors))

    for row_index in range(len(frame)):
        row_number = row_index + 1
        open_ = parsed_numbers["open"][row_index]
        high = parsed_numbers["high"][row_index]
        low = parsed_numbers["low"][row_index]
        close = parsed_numbers["close"][row_index]
        volume = parsed_numbers["volume"][row_index]
        if None in {open_, high, low, close, volume}:
            continue
        assert open_ is not None and high is not None and low is not None
        assert close is not None and volume is not None
        if high < max(open_, close):
            errors.append(f"row {row_number}: high is below open/close")
        if low > min(open_, close):
            errors.append(f"row {row_number}: low is above open/close")
        if high < low:
            errors.append(f"row {row_number}: high is below low")
        if volume < 0:
            errors.append(f"row {row_number}: volume is negative")

    ordered_unique = sorted(open_times.dropna().drop_duplicates().tolist())
    start_utc = _iso(ordered_unique[0]) if ordered_unique else None
    end_utc = _iso(ordered_unique[-1]) if ordered_unique else None
    expected_count = 0
    if ordered_unique:
        expected_count = int(((ordered_unique[-1] - ordered_unique[0]) / CADENCE) + 1)

    facts = {
        "row_count": int(len(frame)),
        "expected_row_count": expected_count,
        "start_utc": start_utc,
        "end_utc": end_utc,
        "duplicates": [asdict(group) for group in duplicates],
        "gaps": [asdict(gap) for gap in gaps],
    }
    return facts, errors


def build_report(
    *,
    input_path: Path,
    input_sha256: str,
    validated_output_path: Path | None,
    facts: dict[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    return {
        "ok": not errors,
        "data_contract_version": CONTRACT_VERSION,
        "validator_version": VALIDATOR_VERSION,
        "symbol": SYMBOL,
        "market_type": MARKET_TYPE,
        "stream": STREAM,
        "timeframe": TIMEFRAME,
        "source": {
            "path": str(input_path),
            "sha256": input_sha256,
            "offline_only": True,
            "no_live_api": True,
            "no_credentials": True,
        },
        "validated_output": {
            "path": str(validated_output_path) if validated_output_path else None,
            "sha256": input_sha256 if validated_output_path else None,
            "write_policy": "exact_input_bytes_only_after_validation_pass",
        },
        "range": {
            "start_utc": facts["start_utc"],
            "end_utc": facts["end_utc"],
            "row_count": facts["row_count"],
            "expected_row_count": facts["expected_row_count"],
        },
        "gap_summary": {
            "gap_count": len(facts["gaps"]),
            "missing_bar_count": sum(int(gap["missing_bars"]) for gap in facts["gaps"]),
            "gaps": facts["gaps"],
            "policy": "detect_report_do_not_fill_or_interpolate",
        },
        "duplicate_summary": {
            "duplicate_group_count": len(facts["duplicates"]),
            "duplicate_row_count": sum(int(group["count"]) for group in facts["duplicates"]),
            "duplicates": facts["duplicates"],
            "policy": "detect_report_do_not_deduplicate",
        },
        "validation": {
            "status": "PASS" if not errors else "FAIL",
            "errors": errors,
            "no_fill": True,
            "no_interpolation": True,
            "no_deduplication": True,
            "no_synthesis": True,
        },
        "boundary": {
            "offline_local_input_only": True,
            "no_exchange_contact": True,
            "no_runtime_contact": True,
            "no_paper_live_contact": True,
            "no_result_population_write": True,
            "invalid_data_report_only": True,
        },
    }


def validate_file(
    input_path: Path,
    report_path: Path,
    *,
    validated_output_path: Path | None = None,
    allow_invalid_report_only: bool = False,
) -> ValidationResult:
    del allow_invalid_report_only

    input_bytes = input_path.read_bytes()
    input_sha256 = sha256_bytes(input_bytes)
    facts = _empty_facts()
    errors: list[str] = []
    actual_output_path: Path | None = None

    try:
        frame = pd.read_csv(input_path, dtype=str, keep_default_na=False)
        facts, errors = validate_frame(frame)
        if not errors and validated_output_path is not None:
            validated_output_path.parent.mkdir(parents=True, exist_ok=True)
            validated_output_path.write_bytes(input_bytes)
            actual_output_path = validated_output_path
    except Exception as exc:
        errors = [f"cannot validate normalized CSV: {exc!r}"]

    report = build_report(
        input_path=input_path,
        input_sha256=input_sha256,
        validated_output_path=actual_output_path,
        facts=facts,
        errors=errors,
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return ValidationResult(
        ok=not errors,
        report_path=str(report_path),
        validated_output_path=str(actual_output_path) if actual_output_path else None,
        input_sha256=input_sha256,
        row_count=int(facts["row_count"]),
        expected_row_count=int(facts["expected_row_count"]),
        start_utc=facts["start_utc"],
        end_utc=facts["end_utc"],
        duplicate_group_count=len(facts["duplicates"]),
        duplicate_row_count=sum(int(group["count"]) for group in facts["duplicates"]),
        gap_count=len(facts["gaps"]),
        missing_bar_count=sum(int(gap["missing_bars"]) for gap in facts["gaps"]),
        errors=errors,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="D2-normalized deterministic CSV.")
    parser.add_argument("--report", required=True, type=Path, help="JSON validation report path.")
    parser.add_argument(
        "--validated-output",
        type=Path,
        help="Optional exact-byte copy of the input, written only after validation PASS.",
    )
    parser.add_argument(
        "--allow-invalid-report-only",
        action="store_true",
        help="Write the validation report and return zero even if validation fails.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = validate_file(
        args.input,
        args.report,
        validated_output_path=args.validated_output,
        allow_invalid_report_only=args.allow_invalid_report_only,
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    if result.ok or args.allow_invalid_report_only:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
