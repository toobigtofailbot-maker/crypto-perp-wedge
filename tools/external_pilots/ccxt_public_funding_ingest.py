"""CCXT public REST funding-rate ingestion pilot for BTCUSDT USDT-M."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ID = "EXT-CCXT-DATA-INGESTION-PILOT-01"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / PACKAGE_ID
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_EXCHANGE_ID = "binanceusdm"
DEFAULT_MARKET_TYPE = "USDT-M perpetual"
DEFAULT_DATA_TYPE = "funding_rate"
DEFAULT_START_UTC = "2020-01-01T00:00:00Z"
DEFAULT_END_UTC = "2026-04-11T23:45:00Z"
FUNDING_INTERVAL = timedelta(hours=8)
FUNDING_INTERVAL_MS = int(FUNDING_INTERVAL.total_seconds() * 1000)
MAX_EXCHANGE_TIMESTAMP_OFFSET_MS = 1000
PUBLIC_METHOD = "fapiPublicGetFundingRate"
SOURCE_METHOD = "ccxt.binanceusdm.fapiPublicGetFundingRate"
MAX_LIMIT = 1000

NON_CANONICAL_LABELS = [
    "NON-CANONICAL EXTERNAL PUBLIC-DATA PILOT OUTPUT",
    "NOT A RESULT POPULATION",
    "NOT STRATEGY / VM / SWEEP AUTHORITY",
    "NOT BACKTEST COST-MODEL AUTHORITY",
    "NOT PAPER / LIVE / RUNTIME AUTHORITY",
    "FUNDING-INTO-BACKTEST REQUIRES A SEPARATE GATED WP",
]


class FundingIngestError(RuntimeError):
    """Raised when the CCXT public funding pilot cannot proceed safely."""


@dataclass(frozen=True)
class FetchPage:
    page_index: int
    request: dict[str, Any]
    row_count: int
    first_funding_time_ms: int | None
    last_funding_time_ms: int | None


def _parse_utc(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise FundingIngestError(f"timestamp must include UTC timezone: {value}")
    return parsed.astimezone(UTC)


def _iso(timestamp: datetime) -> str:
    return timestamp.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _ms(timestamp: datetime) -> int:
    return int(timestamp.astimezone(UTC).timestamp() * 1000)


def _utc_from_ms(value: int) -> datetime:
    return datetime.fromtimestamp(value / 1000, tz=UTC)


def _decimal_string(value: Any, field_name: str) -> str:
    if value is None:
        raise FundingIngestError(f"{field_name} is required")
    text = str(value).strip()
    if not text:
        raise FundingIngestError(f"{field_name} is required")
    try:
        parsed = Decimal(text)
    except (InvalidOperation, ValueError) as exc:
        raise FundingIngestError(f"{field_name} must be numeric") from exc
    if not parsed.is_finite():
        raise FundingIngestError(f"{field_name} must be finite")
    return format(parsed, "f")


def _optional_decimal_string(value: Any, field_name: str) -> str | None:
    if value is None or str(value).strip() == "":
        return None
    return _decimal_string(value, field_name)


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
            handle.write("\n")


def _load_ccxt() -> Any:
    try:
        return importlib.import_module("ccxt")
    except Exception as exc:
        raise FundingIngestError(
            "ccxt is not installed. Install it in an isolated external-pilot environment; "
            "this repo has no non-runtime dependency group for committing ccxt."
        ) from exc


def build_exchange(ccxt_module: Any | None = None) -> Any:
    module = ccxt_module if ccxt_module is not None else _load_ccxt()
    exchange_factory = getattr(module, DEFAULT_EXCHANGE_ID, None)
    if exchange_factory is None:
        raise FundingIngestError("ccxt.binanceusdm is unavailable")
    exchange = exchange_factory({"enableRateLimit": True})
    if not hasattr(exchange, PUBLIC_METHOD):
        raise FundingIngestError(f"CCXT exchange lacks required public method {PUBLIC_METHOD}")
    return exchange


def normalize_raw_row(raw: dict[str, Any], *, page_index: int, row_index: int) -> dict[str, Any]:
    symbol = str(raw.get("symbol", "")).strip()
    if symbol != DEFAULT_SYMBOL:
        raise FundingIngestError(f"unexpected funding symbol {symbol!r}")
    try:
        funding_time_ms = int(str(raw["fundingTime"]).strip())
    except Exception as exc:
        raise FundingIngestError("fundingTime must be an integer millisecond timestamp") from exc
    if funding_time_ms <= 0:
        raise FundingIngestError("fundingTime must be positive")
    nominal_funding_time_ms = round(funding_time_ms / FUNDING_INTERVAL_MS) * FUNDING_INTERVAL_MS
    offset_ms = funding_time_ms - nominal_funding_time_ms
    funding_rate = _decimal_string(raw.get("fundingRate"), "fundingRate")
    mark_price = _optional_decimal_string(raw.get("markPrice"), "markPrice")
    return {
        "exchange": "binance",
        "market_type": DEFAULT_MARKET_TYPE,
        "symbol": DEFAULT_SYMBOL,
        "data_type": DEFAULT_DATA_TYPE,
        "funding_time_utc": _iso(_utc_from_ms(nominal_funding_time_ms)),
        "funding_time_ms": nominal_funding_time_ms,
        "exchange_funding_time_utc": _iso(_utc_from_ms(funding_time_ms)),
        "exchange_funding_time_ms": funding_time_ms,
        "exchange_funding_time_offset_ms": offset_ms,
        "funding_rate": funding_rate,
        "mark_price": mark_price,
        "source_method": SOURCE_METHOD,
        "raw_symbol": symbol,
        "raw_page_index": page_index,
        "raw_row_index": row_index,
    }


def fetch_raw_funding_rows(
    exchange: Any,
    *,
    symbol: str,
    start_ms: int,
    end_ms: int,
    limit: int = MAX_LIMIT,
    max_pages: int = 100,
) -> tuple[list[dict[str, Any]], list[FetchPage]]:
    if symbol != DEFAULT_SYMBOL:
        raise FundingIngestError("this pilot is scoped to BTCUSDT only")
    if limit <= 0 or limit > MAX_LIMIT:
        raise FundingIngestError(f"limit must be between 1 and {MAX_LIMIT}")
    if start_ms > end_ms:
        raise FundingIngestError("start must be before or equal to end")

    method = getattr(exchange, PUBLIC_METHOD, None)
    if method is None:
        raise FundingIngestError(f"exchange lacks required public method {PUBLIC_METHOD}")

    rows: list[dict[str, Any]] = []
    pages: list[FetchPage] = []
    cursor_ms = start_ms
    for page_index in range(max_pages):
        request = {"symbol": symbol, "startTime": cursor_ms, "endTime": end_ms, "limit": limit}
        page_rows = method(request)
        if not isinstance(page_rows, list):
            raise FundingIngestError("CCXT public funding method returned a non-list payload")
        times: list[int] = []
        for row in page_rows:
            if not isinstance(row, dict):
                raise FundingIngestError("CCXT public funding row must be an object")
            try:
                times.append(int(str(row["fundingTime"]).strip()))
            except Exception as exc:
                raise FundingIngestError("CCXT public funding row lacks integer fundingTime") from exc
        first_ms = min(times) if times else None
        last_ms = max(times) if times else None
        pages.append(
            FetchPage(
                page_index=page_index,
                request=dict(request),
                row_count=len(page_rows),
                first_funding_time_ms=first_ms,
                last_funding_time_ms=last_ms,
            )
        )
        if not page_rows:
            break
        rows.extend(page_rows)
        if last_ms is None or last_ms >= end_ms:
            break
        next_cursor = last_ms + 1
        if next_cursor <= cursor_ms:
            raise FundingIngestError("pagination cursor did not advance")
        cursor_ms = next_cursor
    else:
        raise FundingIngestError(f"pagination exceeded max_pages={max_pages}")
    return rows, pages


def normalize_rows(raw_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = [
        normalize_raw_row(raw, page_index=int(raw.get("_page_index", 0)), row_index=index)
        for index, raw in enumerate(raw_rows)
    ]
    return sorted(normalized, key=lambda row: int(row["funding_time_ms"]))


def _expected_funding_times(start_ms: int, end_ms: int) -> list[int]:
    if start_ms > end_ms:
        return []
    first = math.ceil(start_ms / FUNDING_INTERVAL_MS) * FUNDING_INTERVAL_MS
    values: list[int] = []
    current = first
    while current <= end_ms:
        values.append(current)
        current += FUNDING_INTERVAL_MS
    return values


def validate_normalized_rows(
    rows: list[dict[str, Any]],
    *,
    start_ms: int,
    end_ms: int,
    checksum: str,
    provenance_complete: bool,
) -> dict[str, Any]:
    errors: list[str] = []
    timestamps = [int(row.get("funding_time_ms")) for row in rows if "funding_time_ms" in row]
    if len(timestamps) != len(rows):
        errors.append("all rows must contain funding_time_ms")
    sorted_rows = timestamps == sorted(timestamps)
    if not sorted_rows:
        errors.append("funding timestamps are not sorted")
    duplicate_values = sorted({value for value in timestamps if timestamps.count(value) > 1})
    if duplicate_values:
        errors.append(f"duplicate funding timestamps detected: {len(duplicate_values)} groups")
    misaligned = [value for value in timestamps if value % FUNDING_INTERVAL_MS != 0]
    if misaligned:
        errors.append(f"{len(misaligned)} funding timestamp(s) are not UTC 8h aligned")
    exchange_offsets = []
    for row in rows:
        try:
            exchange_offsets.append(abs(int(row.get("exchange_funding_time_offset_ms", 0))))
        except Exception:
            errors.append("exchange_funding_time_offset_ms must be integer milliseconds")
    excessive_offsets = [
        value for value in exchange_offsets if value > MAX_EXCHANGE_TIMESTAMP_OFFSET_MS
    ]
    if excessive_offsets:
        errors.append(
            f"{len(excessive_offsets)} exchange funding timestamp offset(s) exceed "
            f"{MAX_EXCHANGE_TIMESTAMP_OFFSET_MS}ms"
        )
    outside = [value for value in timestamps if value < start_ms or value > end_ms]
    if outside:
        errors.append(f"{len(outside)} funding timestamp(s) fall outside target window")

    numeric_errors = []
    for row in rows:
        try:
            _decimal_string(row.get("funding_rate"), "funding_rate")
            _optional_decimal_string(row.get("mark_price"), "mark_price")
        except FundingIngestError as exc:
            numeric_errors.append(str(exc))
    if numeric_errors:
        errors.append(f"numeric parse errors: {numeric_errors[:5]}")

    expected = _expected_funding_times(start_ms, end_ms)
    observed_set = set(timestamps)
    missing = [value for value in expected if value not in observed_set]
    unexpected = [value for value in timestamps if value not in set(expected)]
    gap_ranges = []
    current_start: int | None = None
    previous: int | None = None
    for value in missing:
        if current_start is None:
            current_start = value
        elif previous is not None and value != previous + FUNDING_INTERVAL_MS:
            gap_ranges.append((current_start, previous))
            current_start = value
        previous = value
    if current_start is not None and previous is not None:
        gap_ranges.append((current_start, previous))
    if missing:
        errors.append(f"missing expected 8h funding events: {len(missing)}")
    if unexpected:
        errors.append(f"unexpected funding events outside expected cadence: {len(unexpected)}")
    if not checksum.startswith("sha256:"):
        errors.append("checksum must use sha256: prefix")
    if not provenance_complete:
        errors.append("provenance is incomplete")

    return {
        "labels": NON_CANONICAL_LABELS,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "public_only_method_used": SOURCE_METHOD,
        "public_only_confirmed": True,
        "credentials_used": False,
        "utc_alignment": {
            "expected_interval": "8h",
            "timestamp_basis": (
                "funding_time_ms is the nominal 8h UTC funding boundary; "
                "exchange_funding_time_ms preserves the exact raw CCXT/Binance timestamp"
            ),
            "misaligned_count": len(misaligned),
            "pass": not misaligned,
            "exchange_timestamp_offset_ms": {
                "max_abs": max(exchange_offsets) if exchange_offsets else None,
                "within_tolerance_count": len(exchange_offsets) - len(excessive_offsets),
                "exceeds_tolerance_count": len(excessive_offsets),
                "tolerance_ms": MAX_EXCHANGE_TIMESTAMP_OFFSET_MS,
            },
        },
        "sorted": {"pass": sorted_rows},
        "duplicates": {
            "duplicate_group_count": len(duplicate_values),
            "duplicate_timestamps_utc": [_iso(_utc_from_ms(value)) for value in duplicate_values],
        },
        "coverage": {
            "target_start_utc": _iso(_utc_from_ms(start_ms)),
            "target_end_utc": _iso(_utc_from_ms(end_ms)),
            "expected_event_count": len(expected),
            "observed_event_count": len(rows),
            "observed_start_utc": _iso(_utc_from_ms(min(timestamps))) if timestamps else None,
            "observed_end_utc": _iso(_utc_from_ms(max(timestamps))) if timestamps else None,
            "outside_target_count": len(outside),
            "unexpected_cadence_count": len(unexpected),
        },
        "gaps": {
            "missing_event_count": len(missing),
            "gap_count": len(gap_ranges),
            "gaps": [
                {
                    "start_utc": _iso(_utc_from_ms(start)),
                    "end_utc": _iso(_utc_from_ms(end)),
                    "missing_events": int(((end - start) / FUNDING_INTERVAL_MS) + 1),
                }
                for start, end in gap_ranges
            ],
        },
        "numeric": {
            "funding_values_parse": not numeric_errors,
            "numeric_error_count": len(numeric_errors),
        },
        "checksum": {"normalized_payload_sha256": checksum, "stable": True},
        "provenance_complete": provenance_complete,
    }


def build_provenance(
    *,
    ccxt_version: str,
    start_ms: int,
    end_ms: int,
    fetch_pages: list[FetchPage],
    output_files: dict[str, str],
) -> dict[str, Any]:
    return {
        "labels": NON_CANONICAL_LABELS,
        "package": PACKAGE_ID,
        "fetch_timestamp_utc": _iso(datetime.now(tz=UTC)),
        "exchange": "binance",
        "ccxt_exchange_id": DEFAULT_EXCHANGE_ID,
        "ccxt_version": ccxt_version,
        "market_type": DEFAULT_MARKET_TYPE,
        "symbol": DEFAULT_SYMBOL,
        "data_type": DEFAULT_DATA_TYPE,
        "source_method": SOURCE_METHOD,
        "ccxt_public_method_allowlist": [PUBLIC_METHOD],
        "credentials_used": False,
        "private_or_account_methods_used": False,
        "runtime_paper_live_contact": False,
        "target_window": {
            "start_utc": _iso(_utc_from_ms(start_ms)),
            "end_utc": _iso(_utc_from_ms(end_ms)),
        },
        "pagination": [
            {
                "page_index": page.page_index,
                "request": page.request,
                "row_count": page.row_count,
                "first_funding_time_utc": (
                    _iso(_utc_from_ms(page.first_funding_time_ms))
                    if page.first_funding_time_ms is not None
                    else None
                ),
                "last_funding_time_utc": (
                    _iso(_utc_from_ms(page.last_funding_time_ms))
                    if page.last_funding_time_ms is not None
                    else None
                ),
            }
            for page in fetch_pages
        ],
        "output_files": output_files,
    }


def build_catalog_lineage(
    *,
    row_count: int,
    validation_report: dict[str, Any],
    provenance_path: Path,
    normalized_path: Path,
    checksum: str,
    ccxt_version: str,
) -> dict[str, Any]:
    return {
        "labels": NON_CANONICAL_LABELS,
        "catalog_status": "non_canonical_external_public_data_pilot",
        "dataset_name": "ccxt_public_binance_usdtm_btcusdt_funding_rate_8h_pilot",
        "exchange": "Binance",
        "ccxt_exchange_id": DEFAULT_EXCHANGE_ID,
        "market_type": DEFAULT_MARKET_TYPE,
        "symbol": DEFAULT_SYMBOL,
        "data_type": DEFAULT_DATA_TYPE,
        "timeframe": "8h funding events",
        "window_start_utc": validation_report["coverage"]["target_start_utc"],
        "window_end_utc": validation_report["coverage"]["target_end_utc"],
        "observed_start_utc": validation_report["coverage"]["observed_start_utc"],
        "observed_end_utc": validation_report["coverage"]["observed_end_utc"],
        "row_count": row_count,
        "missing_intervals": validation_report["gaps"],
        "duplicate_timestamps": validation_report["duplicates"],
        "checksum": checksum,
        "normalized_snapshot_path": str(normalized_path),
        "provenance_path": str(provenance_path),
        "source_method": SOURCE_METHOD,
        "ccxt_version": ccxt_version,
        "pilot_package_id": PACKAGE_ID,
        "canonical_data_authority": False,
        "backtest_cost_model_authority": False,
        "runtime_authority": False,
    }


def _markdown_validation(report: dict[str, Any]) -> str:
    lines = [
        f"# {PACKAGE_ID} Validation Report",
        "",
        *[f"- {label}" for label in NON_CANONICAL_LABELS],
        "",
        f"Status: `{report['status']}`",
        f"Public method: `{report['public_only_method_used']}`",
        f"Credentials used: `{report['credentials_used']}`",
        "",
        "## Coverage",
        "",
        f"- Target start UTC: `{report['coverage']['target_start_utc']}`",
        f"- Target end UTC: `{report['coverage']['target_end_utc']}`",
        f"- Observed start UTC: `{report['coverage']['observed_start_utc']}`",
        f"- Observed end UTC: `{report['coverage']['observed_end_utc']}`",
        f"- Expected events: `{report['coverage']['expected_event_count']}`",
        f"- Observed events: `{report['coverage']['observed_event_count']}`",
        f"- Missing events: `{report['gaps']['missing_event_count']}`",
        f"- Duplicate groups: `{report['duplicates']['duplicate_group_count']}`",
        "",
        "## Boundary",
        "",
        "- No Result Population, Strategy Spec, Variant Manifest, Sweep Plan, "
        "backtester, runner, runtime, paper, live, OMS, risk, or execution path is changed.",
        "- Funding integration into backtests remains a separate gated work package.",
        "",
    ]
    if report["errors"]:
        lines.extend(["## Errors", "", *[f"- {error}" for error in report["errors"]], ""])
    return "\n".join(lines)


def run_ingest(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    start_utc: str = DEFAULT_START_UTC,
    end_utc: str = DEFAULT_END_UTC,
    exchange: Any | None = None,
    ccxt_module: Any | None = None,
    limit: int = MAX_LIMIT,
) -> dict[str, Any]:
    start_ms = _ms(_parse_utc(start_utc))
    end_ms = _ms(_parse_utc(end_utc))
    module = ccxt_module if ccxt_module is not None else _load_ccxt()
    ccxt_version = getattr(module, "__version__", "unknown")
    actual_exchange = exchange if exchange is not None else build_exchange(module)

    raw_rows, pages = fetch_raw_funding_rows(
        actual_exchange,
        symbol=DEFAULT_SYMBOL,
        start_ms=start_ms,
        end_ms=end_ms,
        limit=limit,
    )
    raw_rows_with_page: list[dict[str, Any]] = []
    page_boundaries = []
    cursor = 0
    for page in pages:
        page_boundaries.append((cursor, cursor + page.row_count, page.page_index))
        cursor += page.row_count
    for index, raw in enumerate(raw_rows):
        page_index = 0
        for start, stop, candidate_page in page_boundaries:
            if start <= index < stop:
                page_index = candidate_page
                break
        copied = dict(raw)
        copied["_page_index"] = page_index
        raw_rows_with_page.append(copied)

    normalized_rows = normalize_rows(raw_rows_with_page)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "funding_snapshot.raw.jsonl"
    normalized_path = output_dir / "funding_snapshot.normalized.jsonl"
    checksum_path = output_dir / "funding_snapshot.sha256"
    validation_json_path = output_dir / "validation_report.json"
    validation_md_path = output_dir / "validation_report.md"
    provenance_path = output_dir / "provenance.json"
    catalog_lineage_path = output_dir / "catalog_lineage.json"

    raw_records = [
        {
            "exchange": "binance",
            "ccxt_exchange_id": DEFAULT_EXCHANGE_ID,
            "source_method": SOURCE_METHOD,
            "raw": {key: value for key, value in row.items() if key != "_page_index"},
            "raw_page_index": row["_page_index"],
        }
        for row in raw_rows_with_page
    ]
    _write_jsonl(raw_path, raw_records)
    _write_jsonl(normalized_path, normalized_rows)
    checksum = _sha256_file(normalized_path)
    checksum_path.write_text(checksum + "\n", encoding="utf-8")

    output_file_hashes = {
        "raw_snapshot": _sha256_file(raw_path),
        "normalized_snapshot": checksum,
        "checksum_file": _sha256_file(checksum_path),
    }
    provenance = build_provenance(
        ccxt_version=ccxt_version,
        start_ms=start_ms,
        end_ms=end_ms,
        fetch_pages=pages,
        output_files={key: value for key, value in output_file_hashes.items()},
    )
    _write_json(provenance_path, provenance)
    output_file_hashes["provenance"] = _sha256_file(provenance_path)
    validation = validate_normalized_rows(
        normalized_rows,
        start_ms=start_ms,
        end_ms=end_ms,
        checksum=checksum,
        provenance_complete=True,
    )
    _write_json(validation_json_path, validation)
    validation_md_path.write_text(_markdown_validation(validation), encoding="utf-8")
    catalog_lineage = build_catalog_lineage(
        row_count=len(normalized_rows),
        validation_report=validation,
        provenance_path=provenance_path,
        normalized_path=normalized_path,
        checksum=checksum,
        ccxt_version=ccxt_version,
    )
    _write_json(catalog_lineage_path, catalog_lineage)

    return {
        "labels": NON_CANONICAL_LABELS,
        "package": PACKAGE_ID,
        "recommendation": (
            "ADOPT_AS_PUBLIC_DATA_ADAPTER"
            if validation["status"] == "PASS"
            else "EXPLORATION_ONLY"
        ),
        "dependency_mode": "optional_ccxt_import_no_repo_dependency_change",
        "ccxt_version": ccxt_version,
        "row_count": len(normalized_rows),
        "start_utc": validation["coverage"]["observed_start_utc"],
        "end_utc": validation["coverage"]["observed_end_utc"],
        "checksum": checksum,
        "output_dir": str(output_dir),
        "paths": {
            "raw_snapshot": str(raw_path),
            "normalized_snapshot": str(normalized_path),
            "checksum": str(checksum_path),
            "validation_json": str(validation_json_path),
            "validation_md": str(validation_md_path),
            "provenance": str(provenance_path),
            "catalog_lineage": str(catalog_lineage_path),
        },
        "validation_status": validation["status"],
        "validation_errors": validation["errors"],
        "canonical_write": False,
        "runtime_paper_live_contact": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--start-utc", default=DEFAULT_START_UTC)
    parser.add_argument("--end-utc", default=DEFAULT_END_UTC)
    parser.add_argument("--limit", type=int, default=MAX_LIMIT)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_ingest(
            output_dir=args.output_dir,
            start_utc=args.start_utc,
            end_utc=args.end_utc,
            limit=args.limit,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["validation_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
