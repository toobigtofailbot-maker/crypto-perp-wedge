import hashlib
import os
import time
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import urlopen
import json

import pandas as pd

BASE_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
SYMBOL = "BTCUSDT"
OUT_DIR = os.path.join("data", "processed")
API_LIMIT = 1000  # typical max for this endpoint


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ms_from_utc(date_str: str) -> int:
    # YYYY-MM-DD at 00:00 UTC
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def fetch_funding_rates(symbol: str, start_ms: int, end_ms: int) -> list:
    """
    Fetch funding rate events in [start_ms, end_ms) by paginating using startTime.
    Returns list of dict rows.
    """
    all_rows = []
    next_start = start_ms

    while True:
        params = {
            "symbol": symbol,
            "startTime": next_start,
            "endTime": end_ms,
            "limit": API_LIMIT,
        }
        url = f"{BASE_URL}?{urlencode(params)}"

        with urlopen(url, timeout=30) as resp:
            rows = json.loads(resp.read().decode("utf-8"))

        if not rows:
            break

        all_rows.extend(rows)

        # Each row has "fundingTime" (ms). Advance by 1ms to avoid duplicates.
        last_time = int(rows[-1]["fundingTime"])
        next_start = last_time + 1

        # If fewer rows than limit, likely done.
        if len(rows) < API_LIMIT:
            break

        time.sleep(0.2)

    return all_rows


def export(symbol: str, start_date: str, end_date: str):
    os.makedirs(OUT_DIR, exist_ok=True)

    start_ms = ms_from_utc(start_date)
    end_ms = ms_from_utc(end_date) + 24 * 60 * 60 * 1000  # inclusive end_date

    rows = fetch_funding_rates(symbol, start_ms, end_ms)
    df = pd.DataFrame(rows)

    # Normalize types
    if "fundingRate" in df.columns:
        df["fundingRate"] = pd.to_numeric(df["fundingRate"], errors="coerce")
    if "fundingTime" in df.columns:
        df["fundingTime"] = pd.to_numeric(df["fundingTime"], errors="coerce").astype("Int64")

    created_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%MZ")
    filename = f"binance_um_perp_{symbol}_funding_8h_{start_date}_{end_date}_{created_utc}.parquet"
    out_path = os.path.join(OUT_DIR, filename)

    df.to_parquet(out_path, index=False)

    digest = sha256_file(out_path)
    return out_path, digest, created_utc, f"{start_date} / {end_date}", len(df)


def main():
    # Keep consistent with your kline range for now
    START = "2026-01-01"
    END = "2026-02-27"

    path, sha, created, rng, n = export(SYMBOL, START, END)

    print("\n=== FUNDING EXPORT OK ===")
    print("source: Binance Futures API /fapi/v1/fundingRate")
    print("symbol:", SYMBOL)
    print("rows:", n)
    print("range (start/end):", rng)
    print("created_utc:", created)
    print("path:", path)
    print("sha256:", sha)

    if n == 0:
        print("\nWARNING: No funding rows returned for this range.")
        print("This may be endpoint history limitations. In that case, we switch to collect-forward only.")


if __name__ == "__main__":
    main()