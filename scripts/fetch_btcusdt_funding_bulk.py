"""
Download full BTCUSDT USDT-M perpetual funding rate history from Binance Futures API.
Paginates /fapi/v1/fundingRate over the full requested range.

Usage:
    python scripts/fetch_btcusdt_funding_bulk.py
    python scripts/fetch_btcusdt_funding_bulk.py --from 2019-09-08 --to 2024-12-31
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SYMBOL = "BTCUSDT"
BASE_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
API_LIMIT = 1000
PAGE_SLEEP_S = 0.2  # respect rate limits
MAX_RETRIES = 5


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_page(params: dict, max_retries: int = MAX_RETRIES) -> list[dict]:
    """Fetch one page of funding rate events with exponential backoff for 429s."""
    url = f"{BASE_URL}?{urlencode(params)}"
    delay = 1.0
    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            with urlopen(url, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            if e.code == 429:
                last_exc = e
                if attempt < max_retries:
                    print(f"  Rate limited (429), retrying in {delay:.0f}s...", flush=True)
                    time.sleep(delay)
                    delay *= 2
                    continue
            raise
        except URLError as e:
            last_exc = e
            if attempt < max_retries:
                time.sleep(delay)
                delay *= 2
    raise last_exc  # type: ignore[misc]


def fetch_all_funding(symbol: str, start_ms: int, end_ms: int) -> list[dict]:
    """Paginate fundingRate endpoint over full range. Returns all rows."""
    all_rows: list[dict] = []
    next_start = start_ms
    last_ok_ts: int | None = None

    while True:
        params = {
            "symbol": symbol,
            "startTime": next_start,
            "endTime": end_ms,
            "limit": API_LIMIT,
        }
        try:
            rows = fetch_page(params)
        except Exception as e:
            ts_str = str(last_ok_ts) if last_ok_ts is not None else "none"
            print(
                f"ERROR: API request failed after retries.\n"
                f"  Last successful fundingTime: {ts_str}\n"
                f"  Exception: {e}",
                file=sys.stderr,
            )
            raise

        if not rows:
            break

        all_rows.extend(rows)
        last_ok_ts = int(rows[-1]["fundingTime"])
        next_start = last_ok_ts + 1  # advance by 1ms to avoid duplicates

        last_dt = datetime.fromtimestamp(last_ok_ts / 1000, tz=timezone.utc).isoformat()
        print(f"  page: {len(rows)} rows, last fundingTime: {last_ok_ts} ({last_dt})", flush=True)

        if len(rows) < API_LIMIT:
            break  # last page

        time.sleep(PAGE_SLEEP_S)

    return all_rows


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download BTCUSDT USDT-M perpetual funding rate history from Binance Futures API"
    )
    parser.add_argument(
        "--from", dest="from_date", default="2019-09-08",
        help="Start date YYYY-MM-DD (default: 2019-09-08; earliest available used if data doesn't go back that far)"
    )
    parser.add_argument("--to", dest="to_date", default=None, help="End date YYYY-MM-DD (default: today UTC)")
    parser.add_argument(
        "--output-dir", default=str(REPO_ROOT / "data" / "processed"), help="Output directory"
    )
    args = parser.parse_args()

    from_date_str = args.from_date
    to_date_str = args.to_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    start_ms = int(
        datetime.strptime(from_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000
    )
    # End is inclusive of the end date — include up to end of day
    end_ms = int(
        datetime.strptime(to_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000
    ) + 86_400_000

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching {SYMBOL} funding rates from {from_date_str} to {to_date_str}", flush=True)

    try:
        rows = fetch_all_funding(SYMBOL, start_ms, end_ms)
    except Exception:
        return 1

    if not rows:
        print(
            "ERROR: No funding rate rows returned. "
            "Check date range and network access to fapi.binance.com.",
            file=sys.stderr,
        )
        return 1

    df = pd.DataFrame(rows)

    # Normalize types to match existing fetch script schema
    if "fundingRate" in df.columns:
        df["fundingRate"] = pd.to_numeric(df["fundingRate"], errors="coerce")
    if "markPrice" in df.columns:
        df["markPrice"] = pd.to_numeric(df["markPrice"], errors="coerce")
    if "fundingTime" in df.columns:
        df["fundingTime"] = pd.to_numeric(df["fundingTime"], errors="coerce").astype("Int64")

    # Deduplicate by fundingTime and sort ascending
    df = df.drop_duplicates(subset=["fundingTime"])
    df = df.sort_values("fundingTime").reset_index(drop=True)

    actual_start = datetime.fromtimestamp(
        int(df["fundingTime"].iloc[0]) / 1000, tz=timezone.utc
    ).strftime("%Y-%m-%d")
    actual_end = datetime.fromtimestamp(
        int(df["fundingTime"].iloc[-1]) / 1000, tz=timezone.utc
    ).strftime("%Y-%m-%d")
    created_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%MZ")

    filename = f"binance_um_perp_{SYMBOL}_funding_8h_{actual_start}_{actual_end}_{created_utc}.parquet"
    out_path = out_dir / filename
    df.to_parquet(out_path, index=False)
    digest = sha256_file(out_path)

    print(f"\n=== FUNDING EXPORT OK ===")
    print(f"symbol:      {SYMBOL}")
    print(f"rows:        {len(df)}")
    print(f"range:       {actual_start} / {actual_end}")
    print(f"created_utc: {created_utc}")
    print(f"path:        {out_path}")
    print(f"sha256:      {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
