from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import pandas as pd
import pyarrow.parquet as pq

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data" / "processed"
REPORTS_DIR = REPO_ROOT / "reports"


@dataclass
class Result:
    ok: bool
    errors: List[str]
    warnings: List[str]


def discover_latest(pattern: str) -> Path:
    files = sorted(DATA_DIR.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"No files for pattern: {pattern} in {DATA_DIR}")
    return files[0]


def fail(errors: List[str], msg: str) -> None:
    errors.append(msg)


def warn(warnings: List[str], msg: str) -> None:
    warnings.append(msg)


def to_utc_from_ms(ms_series: pd.Series) -> pd.Series:
    s = pd.to_numeric(ms_series, errors="coerce")
    return pd.to_datetime(s, unit="ms", utc=True, errors="coerce")


def check_monotonic(ts: pd.Series, label: str, errors: List[str]) -> None:
    if ts.isna().any():
        fail(errors, f"{label}: timestamps contain NaT/NaN")
        return
    if not ts.is_monotonic_increasing:
        fail(errors, f"{label}: timestamps not monotonic increasing")


def check_no_future(ts: pd.Series, label: str, errors: List[str]) -> None:
    now_utc = pd.Timestamp(datetime.now(timezone.utc)) + pd.Timedelta(seconds=1)
    if (ts > now_utc).any():
        fail(errors, f"{label}: contains future timestamps")


def check_ms_units(raw: pd.Series, label: str, errors: List[str]) -> None:
    s = pd.to_numeric(raw, errors="coerce")
    if s.isna().any():
        fail(errors, f"{label}: timestamp column has non-numeric values")
        return

    as_ms = pd.to_datetime(s, unit="ms", utc=True, errors="coerce")
    as_s = pd.to_datetime(s, unit="s", utc=True, errors="coerce")
    lo = pd.Timestamp("2000-01-01", tz="UTC")
    hi = pd.Timestamp("2100-01-01", tz="UTC")

    ms_valid = ((as_ms >= lo) & (as_ms <= hi)).mean()
    s_valid = ((as_s >= lo) & (as_s <= hi)).mean()
    if ms_valid < 0.99 or ms_valid <= s_valid:
        fail(errors, f"{label}: timestamp units look incorrect (expected milliseconds)")


def parquet_metadata(path: Path) -> dict[str, str]:
    schema = pq.read_schema(path)
    md = schema.metadata or {}
    return {k.decode("utf-8"): v.decode("utf-8") for k, v in md.items()}


def check_required_columns(df: pd.DataFrame, required: list[str], label: str, errors: List[str]) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        fail(errors, f"{label}: missing columns {missing}")


OHLCV_INTERVALS = {
    "15m": {"cadence_ms": 900_000, "min_rows": 210_000},
    "30m": {"cadence_ms": 1_800_000, "min_rows": 105_000},
    "1h":  {"cadence_ms": 3_600_000, "min_rows": 55_000},
    "4h":  {"cadence_ms": 14_400_000, "min_rows": 13_750},
    "1d":  {"cadence_ms": 86_400_000, "min_rows": 2_200},
}
FUNDING_HISTORY_CADENCE_MS = 28_800_000  # 8h
FUNDING_HISTORY_CADENCE_TOLERANCE_MS = 60_000  # 60s
FUNDING_HISTORY_MIN_ROWS = 6_500


def validate_ohlcv_interval(
    interval: str, cadence_ms: int, min_rows: int, errors: List[str], warnings: List[str]
) -> dict:
    """Validate a single OHLCV interval file. Returns a report dict for this interval."""
    pattern = f"binance_um_perp_BTCUSDT_{interval}_*.parquet"
    try:
        path = discover_latest(pattern)
    except FileNotFoundError:
        warn(warnings, f"OHLCV_{interval}: no file found (pattern: {pattern}) — fetch not yet run")
        return {"status": "MISSING", "rows": 0, "file": None}

    df = pd.read_parquet(path)
    row_count = int(len(df))
    check_required_columns(
        df,
        ["open_time_ms", "open", "high", "low", "close", "volume",
         "close_time_ms", "quote_asset_volume", "num_trades",
         "taker_buy_base_vol", "taker_buy_quote_vol"],
        f"OHLCV_{interval}",
        errors,
    )

    if "open_time_ms" not in df.columns:
        return {"status": "FAIL", "rows": row_count, "file": path.as_posix()}

    raw_ts = pd.to_numeric(df["open_time_ms"], errors="coerce")
    ts = to_utc_from_ms(raw_ts)
    check_monotonic(ts, f"OHLCV_{interval}", errors)
    check_no_future(ts, f"OHLCV_{interval}", errors)
    check_ms_units(raw_ts, f"OHLCV_{interval}.open_time_ms", errors)

    # Duplicate check
    if raw_ts.duplicated().any():
        fail(errors, f"OHLCV_{interval}: duplicate open_time_ms values found")

    # UTC alignment (open_time_ms divisible by cadence_ms)
    if not raw_ts.isna().any():
        misaligned = (raw_ts % cadence_ms) != 0
        if misaligned.any():
            fail(errors, f"OHLCV_{interval}: {misaligned.sum()} bars not UTC-aligned to {cadence_ms}ms cadence")

    # Gap detection (warn only, do not fail)
    if len(raw_ts) > 1 and not raw_ts.isna().any():
        diffs = raw_ts.diff().dropna()
        gaps = diffs[diffs > cadence_ms * 2]
        if not gaps.empty:
            warn(warnings, f"OHLCV_{interval}: {len(gaps)} gap(s) > 2x cadence detected")

    # Row count minimum
    if row_count < min_rows:
        fail(errors, f"OHLCV_{interval}: row count {row_count} below minimum {min_rows}")

    interval_errors = [e for e in errors if f"OHLCV_{interval}" in e]
    status = "FAIL" if interval_errors else "PASS"
    return {"status": status, "rows": row_count, "file": path.as_posix()}


def validate_funding_history(errors: List[str], warnings: List[str]) -> dict:
    """Validate the full-history funding rate file. Returns a report dict."""
    pattern = "binance_um_perp_BTCUSDT_funding_8h_*.parquet"
    try:
        path = discover_latest(pattern)
    except FileNotFoundError:
        warn(warnings, f"FUNDING_HISTORY: no file found (pattern: {pattern}) — fetch not yet run")
        return {"status": "MISSING", "rows": 0, "file": None}

    df = pd.read_parquet(path)
    row_count = int(len(df))
    check_required_columns(df, ["fundingTime", "fundingRate"], "FUNDING_HISTORY", errors)

    if "fundingTime" not in df.columns:
        return {"status": "FAIL", "rows": row_count, "file": path.as_posix()}

    raw_ts = pd.to_numeric(df["fundingTime"], errors="coerce")
    ts = to_utc_from_ms(raw_ts)
    check_monotonic(ts, "FUNDING_HISTORY", errors)
    check_no_future(ts, "FUNDING_HISTORY", errors)

    # Duplicate check
    if raw_ts.duplicated().any():
        fail(errors, "FUNDING_HISTORY: duplicate fundingTime values found")

    # 8h cadence check with tolerance
    if len(raw_ts) > 1 and not raw_ts.isna().any():
        diffs = raw_ts.diff().dropna()
        cadence_ms = FUNDING_HISTORY_CADENCE_MS
        tol = FUNDING_HISTORY_CADENCE_TOLERANCE_MS
        bad_cadence = diffs[abs(diffs - cadence_ms) > tol]
        if not bad_cadence.empty:
            warn(warnings, f"FUNDING_HISTORY: {len(bad_cadence)} interval(s) deviate from 8h cadence ±{tol}ms")

    # fundingRate bounds check
    if "fundingRate" in df.columns:
        rates = pd.to_numeric(df["fundingRate"], errors="coerce")
        out_of_bounds = (rates < -0.1) | (rates > 0.1)
        if out_of_bounds.any():
            fail(errors, f"FUNDING_HISTORY: {out_of_bounds.sum()} fundingRate values outside [-0.1, 0.1]")

    # Row count minimum
    if row_count < FUNDING_HISTORY_MIN_ROWS:
        fail(errors, f"FUNDING_HISTORY: row count {row_count} below minimum {FUNDING_HISTORY_MIN_ROWS}")

    history_errors = [e for e in errors if "FUNDING_HISTORY" in e]
    status = "FAIL" if history_errors else "PASS"
    return {"status": status, "rows": row_count, "file": path.as_posix()}


def validate() -> Result:
    errors: List[str] = []
    warnings: List[str] = []

    premium_path = discover_latest("binance_um_perp_BTCUSDT_premium_index_snapshots_*.parquet")
    book_path = discover_latest("binance_um_perp_BTCUSDT_book_ticker_*s_*.parquet")
    schedule_path = discover_latest("binance_um_perp_BTCUSDT_funding_schedule_metadata_*.parquet")

    premium_df = pd.read_parquet(premium_path)
    book_df = pd.read_parquet(book_path)
    schedule_df = pd.read_parquet(schedule_path)

    check_required_columns(
        premium_df,
        ["symbol", "event_time_ms", "markPrice", "indexPrice", "lastFundingRate", "nextFundingTime"],
        "PREMIUM_INDEX",
        errors,
    )
    if "event_time_ms" in premium_df.columns:
        premium_ts = to_utc_from_ms(premium_df["event_time_ms"])
        check_monotonic(premium_ts, "PREMIUM_INDEX", errors)
        check_no_future(premium_ts, "PREMIUM_INDEX", errors)
        check_ms_units(premium_df["event_time_ms"], "PREMIUM_INDEX.event_time_ms", errors)

    check_required_columns(
        book_df,
        [
            "symbol",
            "event_time_ms",
            "bucket_start_ms",
            "bestBidPrice",
            "bestBidQty",
            "bestAskPrice",
            "bestAskQty",
        ],
        "BOOK_TICKER",
        errors,
    )
    book_md = parquet_metadata(book_path)
    if "bucket_seconds" not in book_md:
        fail(errors, "BOOK_TICKER: parquet metadata missing bucket_seconds")
        bucket_seconds = None
    else:
        bucket_seconds = int(book_md["bucket_seconds"])

    if "bucket_start_ms" in book_df.columns:
        bucket_ts = to_utc_from_ms(book_df["bucket_start_ms"])
        check_monotonic(bucket_ts, "BOOK_TICKER", errors)
        check_no_future(bucket_ts, "BOOK_TICKER", errors)
        check_ms_units(book_df["bucket_start_ms"], "BOOK_TICKER.bucket_start_ms", errors)

        if bucket_seconds is not None:
            bucket_ms = bucket_seconds * 1000
            bucket_raw = pd.to_numeric(book_df["bucket_start_ms"], errors="coerce")
            if ((bucket_raw % bucket_ms) != 0).any():
                fail(errors, "BOOK_TICKER: UTC alignment failed for bucket_start_ms")

            if len(book_df) > 1:
                span_ms = int(bucket_raw.max() - bucket_raw.min())
                allowed = math.floor(span_ms / bucket_ms) + 1
                if len(book_df) > allowed:
                    fail(errors, f"BOOK_TICKER: explosive row growth ({len(book_df)} > {allowed})")

    check_required_columns(
        schedule_df,
        ["symbol", "observed_at_ms", "nextFundingTime", "fundingIntervalHours"],
        "FUNDING_SCHEDULE",
        errors,
    )
    if "observed_at_ms" in schedule_df.columns:
        schedule_ts = to_utc_from_ms(schedule_df["observed_at_ms"])
        check_monotonic(schedule_ts, "FUNDING_SCHEDULE", errors)
        check_no_future(schedule_ts, "FUNDING_SCHEDULE", errors)
        check_ms_units(schedule_df["observed_at_ms"], "FUNDING_SCHEDULE.observed_at_ms", errors)

    if "nextFundingTime" in schedule_df.columns:
        next_ts = to_utc_from_ms(schedule_df["nextFundingTime"])
        if next_ts.isna().any():
            fail(errors, "FUNDING_SCHEDULE: nextFundingTime contains NaT/NaN")
        else:
            check_ms_units(schedule_df["nextFundingTime"], "FUNDING_SCHEDULE.nextFundingTime", errors)

    # --- History validation (OHLCV full-history + funding history) ---
    history_ohlcv: dict = {}
    for interval, cfg in OHLCV_INTERVALS.items():
        history_ohlcv[interval] = validate_ohlcv_interval(
            interval, cfg["cadence_ms"], cfg["min_rows"], errors, warnings
        )

    history_funding = validate_funding_history(errors, warnings)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "PASS" if not errors else "FAIL",
        "inputs": {
            "premium_index": premium_path.as_posix(),
            "book_ticker": book_path.as_posix(),
            "funding_schedule": schedule_path.as_posix(),
        },
        "counts": {
            "premium_rows": int(len(premium_df)),
            "book_rows": int(len(book_df)),
            "funding_schedule_rows": int(len(schedule_df)),
        },
        "history_ohlcv": history_ohlcv,
        "history_funding": history_funding,
        "errors": errors,
        "warnings": warnings,
    }
    (REPORTS_DIR / "validation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    return Result(ok=(len(errors) == 0), errors=errors, warnings=warnings)


def main() -> int:
    try:
        res = validate()
    except Exception as e:
        print("VALIDATION FAIL (exception):", repr(e))
        return 1

    if res.warnings:
        print("VALIDATION WARNINGS:")
        for w in res.warnings:
            print(" -", w)

    if not res.ok:
        print("VALIDATION FAIL:")
        for err in res.errors:
            print(" -", err)
        return 1

    print("VALIDATION PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
