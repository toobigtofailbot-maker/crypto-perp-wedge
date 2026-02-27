import csv
import hashlib
import os
from datetime import datetime, timezone
from urllib.request import urlopen
import json

BASE_URL = "https://fapi.binance.com/fapi/v1/klines"
SYMBOL = "BTCUSDT"
INTERVAL = "1h"
LIMIT = 500  # small sample, Phase-0 smoke test

OUT_DIR = os.path.join("data", "processed")

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    url = f"{BASE_URL}?symbol={SYMBOL}&interval={INTERVAL}&limit={LIMIT}"
    with urlopen(url, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    open_times = [row[0] for row in data]
    close_times = [row[6] for row in data]

    start_utc = datetime.fromtimestamp(min(open_times) / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    end_utc = datetime.fromtimestamp(max(close_times) / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    created_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%MZ")

    filename = f"binance_um_perp_{SYMBOL}_{INTERVAL}_{start_utc}_{end_utc}_{created_utc}.csv"
    out_path = os.path.join(OUT_DIR, filename)

    header = [
        "open_time_ms","open","high","low","close","volume",
        "close_time_ms","quote_asset_volume","num_trades",
        "taker_buy_base_vol","taker_buy_quote_vol","ignore"
    ]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(data)

    digest = sha256_file(out_path)

    print("OK")
    print("Saved:", out_path)
    print("SHA256:", digest)
    print("Range UTC:", start_utc, "→", end_utc)

if __name__ == "__main__":
    main()