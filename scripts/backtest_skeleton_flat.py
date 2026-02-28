import json
import math
import pandas as pd

from src.costs import fee_pnl_impact, slippage_pnl_impact, funding_pnl_impact

def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    cfg = load_config("configs/backtest.json")

    kpath = cfg["data"]["klines_parquet_path"]
    fpath = cfg["data"]["funding_parquet_path"]

    fee_rate = float(cfg["costs"]["fee_rate_taker"])
    slippage_bps = float(cfg["costs"]["slippage_bps"])
    slippage_frac = slippage_bps / 10_000.0

    k = pd.read_parquet(kpath)
    f = pd.read_parquet(fpath)

    # Convert timestamps
    k["open_time"] = pd.to_datetime(k["open_time_ms"], unit="ms", utc=True)
    k["close_time"] = pd.to_datetime(k["close_time_ms"], unit="ms", utc=True)

    # Funding time
    f["funding_time"] = pd.to_datetime(f["fundingTime"], unit="ms", utc=True)
    f["fundingRate"] = pd.to_numeric(f["fundingRate"], errors="coerce")

    # Map funding events to nearest prior bar close (simple, deterministic)
    # We'll join on close_time <= funding_time, take last close_time per event.
    k_sorted = k[["close_time", "close"]].sort_values("close_time").reset_index(drop=True)
    f_sorted = f.sort_values("funding_time").reset_index(drop=True)

    # For each funding event, find index of last bar close <= funding_time
    close_times = k_sorted["close_time"].values
    closes = k_sorted["close"].values

    funding_pnl_total = 0.0

    # Flat strategy baseline: position = 0 always => funding should be 0
    pos_qty = 0.0

    for _, row in f_sorted.iterrows():
        ft = row["funding_time"].to_datetime64()
        fr = float(row["fundingRate"]) if not math.isnan(row["fundingRate"]) else 0.0

        # find bar close index
        idx = close_times.searchsorted(ft, side="right") - 1
        if idx < 0:
            continue
        mark = float(closes[idx])

        funding_pnl_total += funding_pnl_impact(pos_qty, mark, fr)

    # Sanity: with pos=0, funding_pnl_total should be 0 (or -0.0)
    print("=== BACKTEST SKELETON (FLAT) ===")
    print("bars:", len(k))
    print("funding_events:", len(f_sorted))
    print("position_qty_base:", pos_qty)
    print("funding_pnl_total:", funding_pnl_total)

    # Next: we will add a single-entry/single-exit test trade in the next step.

if __name__ == "__main__":
    main()