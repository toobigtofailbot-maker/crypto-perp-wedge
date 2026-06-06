"""Offline Binance USDT-M BTCUSDT 15m OHLCV import and normalization."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
import zipfile
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd


CONTRACT_VERSION = "2026-06-binance-usdtm-15m-data-contract-d1"
NORMALIZATION_VERSION = "wp-d2-offline-binance-usdtm-15m-v1"
SYMBOL = "BTCUSDT"
MARKET_TYPE = "USDT-M perpetual"
STREAM = "ohlcv"
TIMEFRAME = "15m"
CADENCE = pd.Timedelta(minutes=15)
CADENCE_MS = 900_000

BINANCE_KLINE_COLUMNS = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_volume",
    "trade_count",
    "taker_buy_base_volume",
    "taker_buy_quote_volume",
    "ignore",
]

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

SOURCE_COLUMN_ALIASES = {
    "open_time": "open_time",
    "timestamp": "open_time",
    "open_time_ms": "open_time",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volume": "volume",
    "close_time": "close_time",
    "close_time_ms": "close_time",
    "quote_volume": "quote_volume",
    "quote_asset_volume": "quote_volume",
    "trade_count": "trade_count",
    "num_trades": "trade_count",
    "taker_buy_base_volume": "taker_buy_base_volume",
    "taker_buy_base_vol": "taker_buy_base_volume",
    "taker_buy_quote_volume": "taker_buy_quote_volume",
    "taker_buy_quote_vol": "taker_buy_quote_volume",
    "ignore": "ignore",
}

REQUIRED_SOURCE_COLUMNS = {"open_time", "open", "high", "low", "close", "volume"}
OPTIONAL_SOURCE_COLUMNS = set(BINANCE_KLINE_COLUMNS) - REQUIRED_SOURCE_COLUMNS
DECIMAL_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_volume",
    "taker_buy_base_volume",
    "taker_buy_quote_volume",
]


class ImportErrorReport(RuntimeError):
    """Raised when an offline source cannot be normalized under the D1 contract."""


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
class ImportResult:
    ok: bool
    normalized_path: str | None
    report_path: str
    raw_source_sha256: str
    normalized_sha256: str | None
    data_slice_identity: str | None
    row_count: int
    expected_row_count: int
    start_utc: str | None
    end_utc: str | None
    duplicate_count: int
    gap_count: int
    errors: list[str]


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def read_offline_source(path: Path) -> tuple[bytes, str]:
    if not path.exists():
        raise ImportErrorReport(f"input path does not exist: {path}")
    raw = path.read_bytes()
    if path.suffix.lower() != ".zip":
        return raw, path.name

    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            csv_names = [
                name
                for name in archive.namelist()
                if not name.endswith("/") and Path(name).suffix.lower() == ".csv"
            ]
            if len(csv_names) != 1:
                raise ImportErrorReport(
                    f"zip input must contain exactly one CSV file; found {len(csv_names)}"
                )
            return archive.read(csv_names[0]), f"{path.name}:{csv_names[0]}"
    except zipfile.BadZipFile as exc:
        raise ImportErrorReport(f"invalid zip input: {path}") from exc


def _looks_like_header(first_row: list[str]) -> bool:
    normalized = {cell.strip().lower() for cell in first_row}
    return bool(normalized & set(SOURCE_COLUMN_ALIASES))


def load_source_frame(source_bytes: bytes) -> pd.DataFrame:
    text = source_bytes.decode("utf-8-sig")
    sample_rows = list(csv.reader(io.StringIO(text)))
    if not sample_rows:
        raise ImportErrorReport("source CSV is empty")
    has_header = _looks_like_header(sample_rows[0])
    if has_header:
        frame = pd.read_csv(io.BytesIO(source_bytes))
        rename_map = {
            column: SOURCE_COLUMN_ALIASES[column.strip().lower()]
            for column in frame.columns
            if column.strip().lower() in SOURCE_COLUMN_ALIASES
        }
        frame = frame.rename(columns=rename_map)
    else:
        frame = pd.read_csv(io.BytesIO(source_bytes), header=None)
        if len(frame.columns) < len(REQUIRED_SOURCE_COLUMNS):
            raise ImportErrorReport("headerless source has too few columns")
        if len(frame.columns) > len(BINANCE_KLINE_COLUMNS):
            raise ImportErrorReport("headerless source has more columns than Binance kline format")
        frame.columns = BINANCE_KLINE_COLUMNS[: len(frame.columns)]

    missing = sorted(REQUIRED_SOURCE_COLUMNS - set(frame.columns))
    if missing:
        raise ImportErrorReport(f"source missing required columns: {missing}")
    return frame


def parse_open_time(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().all():
        values = numeric.astype("int64")
        unit = "ms" if values.abs().median() >= 10_000_000_000 else "s"
        return pd.to_datetime(values, unit=unit, utc=True, errors="coerce")
    return pd.to_datetime(series, utc=True, errors="coerce")


def parse_optional_close_time(series: pd.Series | None) -> pd.Series | None:
    if series is None:
        return None
    return parse_open_time(series)


def _decimal_text(value: Any, column: str) -> str:
    if pd.isna(value):
        raise ImportErrorReport(f"{column} contains null value")
    try:
        decimal = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ImportErrorReport(f"{column} contains non-numeric value: {value!r}") from exc
    if not decimal.is_finite():
        raise ImportErrorReport(f"{column} contains non-finite value: {value!r}")
    return format(decimal.normalize(), "f")


def _decimal_series(frame: pd.DataFrame, column: str, default: str | None = None) -> list[str]:
    if column not in frame.columns:
        if default is None:
            raise ImportErrorReport(f"missing decimal column: {column}")
        return [default] * len(frame)
    return [_decimal_text(value, column) for value in frame[column]]


def _int_text(value: Any, column: str) -> str:
    if pd.isna(value):
        raise ImportErrorReport(f"{column} contains null value")
    numeric = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric) or int(numeric) != numeric:
        raise ImportErrorReport(f"{column} must be an integer value: {value!r}")
    return str(int(numeric))


def find_gaps(open_times: pd.Series) -> list[Gap]:
    gaps: list[Gap] = []
    previous = None
    for current in open_times:
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


def find_duplicates(open_times: pd.Series) -> list[DuplicateGroup]:
    duplicates = open_times[open_times.duplicated(keep=False)]
    groups: list[DuplicateGroup] = []
    for timestamp, values in duplicates.groupby(duplicates):
        groups.append(DuplicateGroup(open_time_utc=_iso(timestamp), count=int(len(values))))
    return groups


def _iso(timestamp: pd.Timestamp) -> str:
    return timestamp.isoformat().replace("+00:00", "Z")


def _timestamp_ms(series: pd.Series) -> pd.Series:
    utc_naive = series.dt.tz_convert("UTC").dt.tz_localize(None)
    return utc_naive.astype("datetime64[ns]").astype("int64") // 1_000_000


def normalize_frame(source_frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any], list[str]]:
    frame = source_frame.copy()
    open_times = parse_open_time(frame["open_time"])
    if open_times.isna().any():
        raise ImportErrorReport("open_time contains unparseable timestamp values")
    frame["_open_time"] = open_times
    frame = frame.sort_values("_open_time", kind="mergesort").reset_index(drop=True)
    open_times = frame["_open_time"]

    duplicates = find_duplicates(open_times)
    gaps = find_gaps(open_times)
    errors: list[str] = []
    if duplicates:
        errors.append(f"duplicate open_time values detected: {sum(group.count for group in duplicates)} rows")
    if gaps:
        errors.append(f"missing 15m bars detected: {sum(gap.missing_bars for gap in gaps)} bars")

    open_time_ms = _timestamp_ms(open_times).astype("int64")
    misaligned = (open_time_ms % CADENCE_MS) != 0
    if misaligned.any():
        errors.append(f"{int(misaligned.sum())} open_time values are not aligned to 15m UTC bars")

    close_times = parse_optional_close_time(frame["close_time"]) if "close_time" in frame.columns else None
    if close_times is not None and close_times.isna().any():
        errors.append("close_time contains unparseable timestamp values")

    decimals = {column: _decimal_series(frame, column, "0") for column in DECIMAL_COLUMNS}
    opens = [Decimal(value) for value in decimals["open"]]
    highs = [Decimal(value) for value in decimals["high"]]
    lows = [Decimal(value) for value in decimals["low"]]
    closes = [Decimal(value) for value in decimals["close"]]
    volumes = [Decimal(value) for value in decimals["volume"]]

    for idx, (open_, high, low, close, volume) in enumerate(zip(opens, highs, lows, closes, volumes)):
        row_number = idx + 1
        if high < max(open_, close):
            errors.append(f"row {row_number}: high is below open/close")
        if low > min(open_, close):
            errors.append(f"row {row_number}: low is above open/close")
        if high < low:
            errors.append(f"row {row_number}: high is below low")
        if volume < 0:
            errors.append(f"row {row_number}: volume is negative")

    normalized = pd.DataFrame(
        {
            "open_time_ms": [str(value) for value in open_time_ms],
            "open_time": [_iso(value) for value in open_times],
            "open": decimals["open"],
            "high": decimals["high"],
            "low": decimals["low"],
            "close": decimals["close"],
            "volume": decimals["volume"],
            "close_time_ms": (
                [str(value) for value in _timestamp_ms(close_times).astype("int64")]
                if close_times is not None
                else [""] * len(frame)
            ),
            "quote_asset_volume": decimals["quote_volume"],
            "num_trades": (
                [_int_text(value, "trade_count") for value in frame["trade_count"]]
                if "trade_count" in frame.columns
                else ["0"] * len(frame)
            ),
            "taker_buy_base_vol": decimals["taker_buy_base_volume"],
            "taker_buy_quote_vol": decimals["taker_buy_quote_volume"],
            "ignore": (
                ["" if pd.isna(value) else str(value) for value in frame["ignore"]]
                if "ignore" in frame.columns
                else [""] * len(frame)
            ),
        },
        columns=OUTPUT_COLUMNS,
    )

    expected_count = 0
    if len(open_times):
        expected_count = int(((open_times.iloc[-1] - open_times.iloc[0]) / CADENCE) + 1)
    facts = {
        "row_count": int(len(normalized)),
        "expected_row_count": expected_count,
        "start_utc": _iso(open_times.iloc[0]) if len(open_times) else None,
        "end_utc": _iso(open_times.iloc[-1]) if len(open_times) else None,
        "duplicates": [asdict(group) for group in duplicates],
        "gaps": [asdict(gap) for gap in gaps],
    }
    return normalized, facts, errors


def deterministic_csv_bytes(frame: pd.DataFrame) -> bytes:
    buffer = io.StringIO(newline="")
    frame.to_csv(buffer, index=False, lineterminator="\n")
    return buffer.getvalue().encode("utf-8")


def build_report(
    *,
    input_path: Path,
    source_member: str,
    raw_sha256: str,
    normalized_sha256: str | None,
    normalized_path: Path | None,
    facts: dict[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    data_slice_identity = None
    if normalized_sha256:
        data_slice_identity = (
            f"binance_usdtm:{SYMBOL}:ohlcv:{TIMEFRAME}:"
            f"{facts['start_utc']}:{facts['end_utc']}:"
            f"{NORMALIZATION_VERSION}:sha256:{normalized_sha256}"
        )
    return {
        "ok": not errors,
        "data_contract_version": CONTRACT_VERSION,
        "normalization_version": NORMALIZATION_VERSION,
        "symbol": SYMBOL,
        "market_type": MARKET_TYPE,
        "stream": STREAM,
        "timeframe": TIMEFRAME,
        "source": {
            "path": str(input_path),
            "member": source_member,
            "sha256": raw_sha256,
            "offline_only": True,
            "no_live_api": True,
            "no_credentials": True,
        },
        "normalized": {
            "path": str(normalized_path) if normalized_path else None,
            "sha256": normalized_sha256,
            "data_slice_identity": data_slice_identity,
            "columns": OUTPUT_COLUMNS,
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
            "policy": "detect_report_do_not_fill",
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
        },
        "boundary": {
            "offline_local_input_only": True,
            "no_exchange_contact": True,
            "no_runtime_contact": True,
            "no_paper_live_contact": True,
            "no_result_population_write": True,
        },
    }


def import_file(
    input_path: Path,
    output_path: Path | None,
    report_path: Path,
    *,
    allow_invalid_report_only: bool = False,
) -> ImportResult:
    source_bytes, source_member = read_offline_source(input_path)
    raw_sha256 = sha256_bytes(source_bytes)
    facts = {
        "row_count": 0,
        "expected_row_count": 0,
        "start_utc": None,
        "end_utc": None,
        "duplicates": [],
        "gaps": [],
    }
    normalized_sha256 = None
    normalized_path = None
    errors: list[str] = []

    try:
        source_frame = load_source_frame(source_bytes)
        normalized, facts, errors = normalize_frame(source_frame)
        normalized_bytes = deterministic_csv_bytes(normalized)
        normalized_sha256 = sha256_bytes(normalized_bytes)
        if errors and not allow_invalid_report_only:
            output_path = None
        if output_path is not None and (not errors or allow_invalid_report_only):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(normalized_bytes)
            normalized_path = output_path
    except ImportErrorReport as exc:
        errors = [str(exc)]

    report = build_report(
        input_path=input_path,
        source_member=source_member,
        raw_sha256=raw_sha256,
        normalized_sha256=normalized_sha256,
        normalized_path=normalized_path,
        facts=facts,
        errors=errors,
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    data_slice_identity = report["normalized"]["data_slice_identity"]
    return ImportResult(
        ok=not errors,
        normalized_path=str(normalized_path) if normalized_path else None,
        report_path=str(report_path),
        raw_source_sha256=raw_sha256,
        normalized_sha256=normalized_sha256,
        data_slice_identity=data_slice_identity,
        row_count=int(facts["row_count"]),
        expected_row_count=int(facts["expected_row_count"]),
        start_utc=facts["start_utc"],
        end_utc=facts["end_utc"],
        duplicate_count=len(facts["duplicates"]),
        gap_count=len(facts["gaps"]),
        errors=errors,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Offline CSV or ZIP containing one CSV.")
    parser.add_argument("--output", type=Path, help="Normalized deterministic CSV output path.")
    parser.add_argument("--report", required=True, type=Path, help="JSON provenance/validation report path.")
    parser.add_argument(
        "--allow-invalid-report-only",
        action="store_true",
        help="Write the validation report and return zero even if the source is invalid.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = import_file(
        args.input,
        args.output,
        args.report,
        allow_invalid_report_only=args.allow_invalid_report_only,
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    if result.ok or args.allow_invalid_report_only:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
