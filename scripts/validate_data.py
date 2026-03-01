from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pandas as pd


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


def check_monotonic_unique(ts: pd.Series, label: str, errors: List[str]) -> None:
    if ts.isna().any():
        fail(errors, f"{label}: timestamps contain NaT/NaN")
        return
    if not ts.is_monotonic_increasing:
        fail(errors, f"{label}: timestamps not monotonic increasing")
    if ts.duplicated().any():
        fail(errors, f"{label}: duplicate timestamps found")


def check_grid_klines(ts: pd.Series, tf: str, label: str, errors: List[str]) -> None:
    if ts.isna().any():
        return

    if tf == "1h":
        bad = ~((ts.dt.minute == 0) & (ts.dt.second == 0) & (ts.dt.microsecond == 0))
        if bad.any():
            fail(errors, f"{label}: not aligned to 1h UTC grid (minute/second != 0)")
    elif tf == "4h":
        bad = ~(
            (ts.dt.minute == 0)
            & (ts.dt.second == 0)
            & (ts.dt.microsecond == 0)
            & (ts.dt.hour % 4 == 0)
        )
        if bad.any():
            fail(errors, f"{label}: not aligned to 4h UTC grid (hour%4 != 0)")
    else:
        fail(errors, f"{label}: unknown tf={tf}")


def check_missing_bars(ts: pd.Series, tf: str, label: str, errors: List[str]) -> None:
    if ts.isna().any():
        return

    # use lower-case freq strings for pandas compatibility
    freq = {"1h": "1h", "4h": "4h"}[tf]
    start = ts.iloc[0]
    end = ts.iloc[-1]

    expected = pd.date_range(start=start, end=end, freq=freq, tz="UTC")
    actual = pd.DatetimeIndex(ts)
    missing = expected.difference(actual)

    if len(missing) > 0:
        fail(errors, f"{label}: missing {len(missing)} bars in {tf} grid (example: {missing[0]})")


def check_ohlc(df: pd.DataFrame, label: str, errors: List[str], warnings: List[str]) -> None:
    for c in ["open", "high", "low", "close"]:
        if c not in df.columns:
            fail(errors, f"{label}: missing column '{c}'")
            return

    if df[["open", "high", "low", "close"]].isna().any().any():
        fail(errors, f"{label}: NaNs in OHLC columns")

    if (df["high"] < df[["open", "close"]].max(axis=1)).any():
        fail(errors, f"{label}: high < max(open,close) found")

    if (df["low"] > df[["open", "close"]].min(axis=1)).any():
        fail(errors, f"{label}: low > min(open,close) found")

    if (df["high"] < df["low"]).any():
        fail(errors, f"{label}: high < low found")

    if "volume" in df.columns:
        if df["volume"].isna().any():
            fail(errors, f"{label}: NaNs in volume")
        if (df["volume"] < 0).any():
            fail(errors, f"{label}: negative volume")
    else:
        warn(warnings, f"{label}: volume column not found (skipped volume checks)")


def check_funding_8h_grid(fts: pd.Series, errors: List[str]) -> Optional[int]:
    """
    Funding validation (Phase-0):
    - Accept timestamps near the hour boundary (UTC) within tolerance.
    - Accept constant 8h phase (00/08/16 or shifted) based on nearest-hour projection.
    - Accept ~8h spacing within tolerance (milliseconds drift breaks exact equality).
    """
    if fts.isna().any():
        fail(errors, "FUNDING: timestamps contain NaT/NaN")
        return None

    tol = pd.Timedelta(seconds=60)

    # distance to nearest hour: min(|t-floor|, |ceil-t|)
    floor_h = fts.dt.floor("h")
    ceil_h = fts.dt.ceil("h")
    dist = pd.concat([(fts - floor_h).abs(), (ceil_h - fts).abs()], axis=1).min(axis=1)

    if (dist > tol).any():
        worst = dist.max()
        fail(errors, f"FUNDING: not near hour boundary UTC (max drift {worst})")
        return None

    # project to nearest hour for phase/spacing checks
    nearest_h = fts.dt.round("h")

    phase = int(nearest_h.dt.hour.iloc[0] % 8)
    if not ((nearest_h.dt.hour % 8) == phase).all():
        fail(errors, f"FUNDING: not aligned to constant 8h phase (nearest_hour%8 != {phase})")
        return None

    deltas = nearest_h.diff().dropna()
    if not ((deltas - pd.Timedelta(hours=8)).abs() <= tol).all():
        fail(errors, "FUNDING: spacing between events is not ~8h (missing/duplicate events?)")
        return None

    return phase


def validate() -> Result:
    errors: List[str] = []
    warnings: List[str] = []

    # discover latest artifacts
    p1 = discover_latest("binance_um_perp_BTCUSDT_1h_*.parquet")
    p4 = discover_latest("binance_um_perp_BTCUSDT_4h_*.parquet")
    pf = discover_latest("binance_um_perp_BTCUSDT_funding_8h_*.parquet")

    df1 = pd.read_parquet(p1)
    df4 = pd.read_parquet(p4)
    dff = pd.read_parquet(pf)

    # --- KLINES 1h ---
    if "open_time_ms" not in df1.columns:
        fail(errors, "KLINES 1h: missing open_time_ms")
        ts1 = pd.Series([], dtype="datetime64[ns, UTC]")
    else:
        ts1 = to_utc_from_ms(df1["open_time_ms"])
        check_monotonic_unique(ts1, "KLINES 1h", errors)
        check_grid_klines(ts1, "1h", "KLINES 1h", errors)
        check_missing_bars(ts1, "1h", "KLINES 1h", errors)
        check_ohlc(df1, "KLINES 1h", errors, warnings)

    # --- KLINES 4h ---
    if "open_time_ms" not in df4.columns:
        fail(errors, "KLINES 4h: missing open_time_ms")
        ts4 = pd.Series([], dtype="datetime64[ns, UTC]")
    else:
        ts4 = to_utc_from_ms(df4["open_time_ms"])
        check_monotonic_unique(ts4, "KLINES 4h", errors)
        check_grid_klines(ts4, "4h", "KLINES 4h", errors)
        check_missing_bars(ts4, "4h", "KLINES 4h", errors)
        check_ohlc(df4, "KLINES 4h", errors, warnings)

    # --- FUNDING 8h ---
    if "fundingTime" not in dff.columns:
        fail(errors, "FUNDING 8h: missing fundingTime")
        fts = None
    else:
        fts = to_utc_from_ms(dff["fundingTime"])
        check_monotonic_unique(fts, "FUNDING 8h", errors)
        _phase = check_funding_8h_grid(fts, errors)

    if "fundingRate" not in dff.columns:
        fail(errors, "FUNDING 8h: missing fundingRate")
    else:
        fr = pd.to_numeric(dff["fundingRate"], errors="coerce")
        if fr.isna().any():
            fail(errors, "FUNDING 8h: fundingRate contains NaNs")

    # --- FUNDING↔BARS MAPPING sanity (policy: nearest prior funding event) ---
    if fts is not None and (not ts1.empty) and (not ts1.isna().any()) and (not fts.isna().any()):
        bar_start = ts1.iloc[0]
        bar_end = ts1.iloc[-1] + pd.Timedelta(hours=1)

        outside = (fts < bar_start) | (fts > bar_end)
        if outside.any():
            fail(errors, f"MAPPING: {int(outside.sum())} funding events outside 1h bar range [{bar_start} .. {bar_end}]")

        first_funding = fts.iloc[0]
        bars_before_first = int((ts1 < first_funding).sum())
        if bars_before_first > 8:
            fail(errors, f"MAPPING: too many 1h bars before first funding event ({bars_before_first} > 8)")

    # deterministic report (no timestamps)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "PASS" if not errors else "FAIL",
        "inputs": {
            "klines_1h": p1.as_posix(),
            "klines_4h": p4.as_posix(),
            "funding_8h": pf.as_posix(),
        },
        "counts": {
            "klines_1h_rows": int(len(df1)),
            "klines_4h_rows": int(len(df4)),
            "funding_rows": int(len(dff)),
        },
        "policy": {
            "funding_mapping": "nearest prior funding event",
            "funding_grid": "8h with constant phase offset (near-hour boundary ±60s)",
            "bar_range_check": "funding events must lie within [first_1h_bar_open .. last_1h_bar_open+1h]",
        },
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