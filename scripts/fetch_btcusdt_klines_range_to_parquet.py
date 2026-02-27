import hashlib
import os
import time
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import urlopen
import json

import pandas as pd

BASE_URL = "https://fapi.binance.com/fapi/v1/klines"
SYMBOL = "BTCUSDT"
OUT_DIR = os.path.join("data", "processed")
API_LIMIT = 1500  # futures klines limit


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


def fetch_klines(symbol: str, interval: str, start_ms: int, end_ms: int) -> list:
    all_rows = []
    next_start = start_ms

    while True:
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": API_LIMIT,
            "startTime": next_start,
            "endTime": end_ms,
        }
        url = f"{BASE_URL}?{urlencode(params)}"

        with urlopen(url, timeout=30) as resp:
            rows = json.loads(resp.read().decode("utf-8"))

        if not rows:
            break

        all_rows.extend(rows)

        last_open_time = rows[-1][0]
        next_start = last_open_time + 1  # avoid duplicates

        if len(rows) < API_LIMIT:
            break

        time.sleep(0.2)

    return all_rows


def rows_to_df(rows: list) -> pd.DataFrame:
    cols = [
        "open_time_ms", "open", "high", "low", "close", "volume",
        "close_time_ms", "quote_asset_volume", "num_trades",
        "taker_buy_base_vol", "taker_buy_quote_vol", "ignore"
    ]
    df = pd.DataFrame(rows, columns=cols)

    num_cols = ["open", "high", "low", "close", "volume",
                "quote_asset_volume", "taker_buy_base_vol", "taker_buy_quote_vol"]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["num_trades"] = pd.to_numeric(df["num_trades"], errors="coerce").astype("Int64")
    return df


def export(symbol: str, interval: str, start_date: str, end_date: str):
    os.makedirs(OUT_DIR, exist_ok=True)

    start_ms = ms_from_utc(start_date)
    end_ms = ms_from_utc(end_date) + 24 * 60 * 60 * 1000  # inclusive end_date

    rows = fetch_klines(symbol, interval, start_ms, end_ms)
    df = rows_to_df(rows)

    created_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%MZ")
    filename = f"binance_um_perp_{symbol}_{interval}_{start_date}_{end_date}_{created_utc}.parquet"
    out_path = os.path.join(OUT_DIR, filename)

    df.to_parquet(out_path, index=False)

    digest = sha256_file(out_path)
    return out_path, digest, created_utc, f"{start_date} / {end_date}", len(df)


def main():
    # Keep this range modest initially
    START = "2026-01-01"
    END = "2026-02-27"

    for interval in ["1h", "4h"]:
        path, sha, created, rng, n = export(SYMBOL, interval, START, END)
        print("\n=== EXPORT OK ===")
        print("source: Binance Futures API /fapi/v1/klines")
        print("symbol:", SYMBOL)
        print("interval:", interval)
        print("rows:", n)
        print("range (start/end):", rng)
        print("created_utc:", created)
        print("path:", path)
        print("sha256:", sha)


if __name__ == "__main__":
    main()