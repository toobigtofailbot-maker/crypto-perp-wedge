"""
Download full BTCUSDT USDT-M perpetual kline history from data.binance.vision
monthly/daily bulk archives with SHA256 checksum verification.

Usage:
    python scripts/fetch_btcusdt_klines_bulk.py --interval 1h
    python scripts/fetch_btcusdt_klines_bulk.py --interval 15m --from 2019-09-08 --to 2024-12-31
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SYMBOL = "BTCUSDT"
VALID_INTERVALS = ["15m", "30m", "1h", "4h", "1d"]
MONTHLY_BASE = "https://data.binance.vision/data/futures/um/monthly/klines/{symbol}/{interval}/"
DAILY_BASE = "https://data.binance.vision/data/futures/um/daily/klines/{symbol}/{interval}/"
MAX_WORKERS = 4
MAX_RETRIES = 3

KLINE_COLS = [
    "open_time_ms", "open", "high", "low", "close", "volume",
    "close_time_ms", "quote_asset_volume", "num_trades",
    "taker_buy_base_vol", "taker_buy_quote_vol", "ignore",
]
FLOAT_COLS = [
    "open", "high", "low", "close", "volume",
    "quote_asset_volume", "taker_buy_base_vol", "taker_buy_quote_vol",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_url(url: str, max_retries: int = MAX_RETRIES) -> bytes:
    """Fetch URL bytes with exponential backoff on transient network errors."""
    delay = 1.0
    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            with urlopen(url, timeout=120) as resp:
                return resp.read()
        except HTTPError:
            raise  # HTTP errors (e.g. 404) are not retried
        except URLError as exc:
            last_exc = exc
            if attempt < max_retries:
                time.sleep(delay)
                delay *= 2
    raise last_exc  # type: ignore[misc]


def verify_checksum(zip_data: bytes, checksum_text: str, zip_filename: str) -> None:
    """Verify SHA256 checksum. File format: '<sha256>  <filename>' (two spaces)."""
    line = checksum_text.strip()
    parts = line.split("  ", 1)
    if len(parts) != 2:
        raise ValueError(f"CHECKSUM MISMATCH: cannot parse checksum file for {zip_filename}: {line!r}")
    expected_hash = parts[0].strip().lower()
    actual_hash = sha256_bytes(zip_data)
    if actual_hash != expected_hash:
        raise ValueError(
            f"CHECKSUM MISMATCH for {zip_filename}\n"
            f"  expected: {expected_hash}\n"
            f"  actual:   {actual_hash}"
        )


def parse_csv_from_zip_bytes(zip_data: bytes) -> list[list[str]]:
    """Extract CSV rows from a ZIP archive in memory."""
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
        csv_names = [n for n in zf.namelist() if n.endswith(".csv")]
        if not csv_names:
            raise ValueError("No CSV found in ZIP archive")
        with zf.open(csv_names[0]) as f:
            reader = csv.reader(io.TextIOWrapper(f, encoding="utf-8"))
            rows = [
                row for row in reader
                if row and not row[0].strip().lower().startswith("open_time")
            ]
    return rows


def download_and_parse(url: str, zip_filename: str) -> tuple[list[list[str]], bool]:
    """
    Download zip + checksum, verify SHA256, return (rows, found).
    Returns ([], False) on 404. Raises on checksum mismatch or network failure.
    """
    try:
        zip_data = fetch_url(url)
    except HTTPError as e:
        if e.code == 404:
            return [], False
        raise

    cksum_url = url + ".CHECKSUM"
    try:
        cksum_data = fetch_url(cksum_url)
        verify_checksum(zip_data, cksum_data.decode("utf-8"), zip_filename)
    except HTTPError as e:
        if e.code == 404:
            # Some older archives lack checksum files — skip verification with warning
            print(f"  WARNING: no checksum file for {zip_filename}, skipping verification", flush=True)
        else:
            raise

    rows = parse_csv_from_zip_bytes(zip_data)
    return rows, True


def months_sequence(from_date: date, until_exclusive: date):
    """Yield (year, month) tuples from from_date's month up to (but not including) until_exclusive's month."""
    y, m = from_date.year, from_date.month
    ey, em = until_exclusive.year, until_exclusive.month
    while (y, m) < (ey, em):
        yield y, m
        m += 1
        if m > 12:
            m = 1
            y += 1


def fetch_monthly_batch(
    symbol: str, interval: str, months: list[tuple[int, int]]
) -> dict[tuple[int, int], list[list[str]] | None]:
    """Download monthly archives in parallel (up to MAX_WORKERS). None = 404."""
    base = MONTHLY_BASE.format(symbol=symbol, interval=interval)
    results: dict[tuple[int, int], list[list[str]] | None] = {}

    def _task(ym: tuple[int, int]) -> tuple[tuple[int, int], list[list[str]] | None]:
        y, m = ym
        zip_name = f"{symbol}-{interval}-{y:04d}-{m:02d}.zip"
        url = base + zip_name
        rows, found = download_and_parse(url, zip_name)
        return ym, (rows if found else None)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_task, ym): ym for ym in months}
        for fut in as_completed(futures):
            ym, rows = fut.result()  # propagates exceptions
            results[ym] = rows

    return results


def fetch_daily_batch(
    symbol: str, interval: str, days: list[date]
) -> dict[date, list[list[str]] | None]:
    """Download daily archives in parallel (up to MAX_WORKERS). None = 404."""
    base = DAILY_BASE.format(symbol=symbol, interval=interval)
    results: dict[date, list[list[str]] | None] = {}

    def _task(d: date) -> tuple[date, list[list[str]] | None]:
        ds = d.strftime("%Y-%m-%d")
        zip_name = f"{symbol}-{interval}-{ds}.zip"
        url = base + zip_name
        rows, found = download_and_parse(url, zip_name)
        return d, (rows if found else None)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_task, d): d for d in days}
        for fut in as_completed(futures):
            d, rows = fut.result()
            results[d] = rows

    return results


def rows_to_df(all_rows: list[list[str]]) -> pd.DataFrame:
    if not all_rows:
        return pd.DataFrame(columns=KLINE_COLS)
    df = pd.DataFrame(all_rows, columns=KLINE_COLS)
    for c in FLOAT_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["num_trades"] = pd.to_numeric(df["num_trades"], errors="coerce").astype("Int64")
    df["open_time_ms"] = pd.to_numeric(df["open_time_ms"], errors="coerce").astype("int64")
    df["close_time_ms"] = pd.to_numeric(df["close_time_ms"], errors="coerce").astype("int64")
    return df


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download BTCUSDT USDT-M perpetual kline history from data.binance.vision"
    )
    parser.add_argument("--interval", required=True, choices=VALID_INTERVALS, help="Kline interval")
    parser.add_argument(
        "--from", dest="from_date", default="2019-09-08",
        help="Start date YYYY-MM-DD (default: 2019-09-08; earliest available used if not in archives)"
    )
    parser.add_argument("--to", dest="to_date", default=None, help="End date YYYY-MM-DD (default: today UTC)")
    parser.add_argument(
        "--output-dir", default=str(REPO_ROOT / "data" / "processed"), help="Output directory"
    )
    args = parser.parse_args()

    from_date = datetime.strptime(args.from_date, "%Y-%m-%d").date()
    to_date = (
        datetime.strptime(args.to_date, "%Y-%m-%d").date()
        if args.to_date
        else datetime.now(timezone.utc).date()
    )
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    interval = args.interval
    today_utc = datetime.now(timezone.utc).date()
    current_month_start = date(today_utc.year, today_utc.month, 1)

    print(f"Fetching {SYMBOL} {interval} from {from_date} to {to_date}", flush=True)

    # Monthly archives: all complete months before the current calendar month
    monthly_months = [
        (y, m) for y, m in months_sequence(from_date, current_month_start)
        if date(y, m, 1) <= to_date
    ]

    all_rows: list[list[str]] = []
    seen_data = False

    if monthly_months:
        print(f"Downloading {len(monthly_months)} monthly archives (up to {MAX_WORKERS} parallel)...", flush=True)
        monthly_results = fetch_monthly_batch(SYMBOL, interval, monthly_months)

        for ym in monthly_months:  # process in chronological order
            rows = monthly_results[ym]
            if rows is None:
                if seen_data:
                    # Gap after data was found — stop condition
                    print(
                        f"ERROR: Missing monthly archive {ym[0]:04d}-{ym[1]:02d} after data was already found. "
                        f"This indicates a gap in history.",
                        file=sys.stderr,
                    )
                    return 1
                else:
                    print(f"  Skipping {ym[0]:04d}-{ym[1]:02d}: archive not yet available", flush=True)
            else:
                seen_data = True
                all_rows.extend(rows)
                print(f"  {ym[0]:04d}-{ym[1]:02d}: {len(rows)} rows", flush=True)

    # Daily archives: current month days up to to_date
    if to_date >= current_month_start:
        daily_days: list[date] = []
        d = current_month_start
        while d <= min(to_date, today_utc):
            daily_days.append(d)
            d += timedelta(days=1)

        if daily_days:
            print(f"Downloading {len(daily_days)} daily archives for current month...", flush=True)
            daily_results = fetch_daily_batch(SYMBOL, interval, daily_days)
            for d in daily_days:
                rows = daily_results[d]
                if rows:
                    all_rows.extend(rows)
                    print(f"  {d}: {len(rows)} rows", flush=True)

    if not all_rows:
        print(
            "ERROR: No data rows collected. "
            "Check date range and network access to data.binance.vision.",
            file=sys.stderr,
        )
        return 1

    print(f"\nAssembling {len(all_rows)} raw rows...", flush=True)
    df = rows_to_df(all_rows)

    # Deduplicate by open_time_ms and sort ascending
    df = df.drop_duplicates(subset=["open_time_ms"])
    df = df.sort_values("open_time_ms").reset_index(drop=True)

    # Filter to the requested date window
    from_ms = int(
        datetime(from_date.year, from_date.month, from_date.day, tzinfo=timezone.utc).timestamp() * 1000
    )
    to_ms = int(
        datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59, tzinfo=timezone.utc).timestamp() * 1000
    )
    df = df[(df["open_time_ms"] >= from_ms) & (df["open_time_ms"] <= to_ms)].reset_index(drop=True)

    if df.empty:
        print("ERROR: DataFrame is empty after date-range filtering.", file=sys.stderr)
        return 1

    actual_start = datetime.fromtimestamp(
        df["open_time_ms"].iloc[0] / 1000, tz=timezone.utc
    ).strftime("%Y-%m-%d")
    actual_end = datetime.fromtimestamp(
        df["open_time_ms"].iloc[-1] / 1000, tz=timezone.utc
    ).strftime("%Y-%m-%d")
    created_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%MZ")

    filename = f"binance_um_perp_{SYMBOL}_{interval}_{actual_start}_{actual_end}_{created_utc}.parquet"
    out_path = out_dir / filename
    df.to_parquet(out_path, index=False)
    digest = sha256_file(out_path)

    print(f"\n=== KLINE EXPORT OK ===")
    print(f"symbol:      {SYMBOL}")
    print(f"interval:    {interval}")
    print(f"rows:        {len(df)}")
    print(f"range:       {actual_start} / {actual_end}")
    print(f"created_utc: {created_utc}")
    print(f"path:        {out_path}")
    print(f"sha256:      {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
