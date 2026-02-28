import os
from pathlib import Path
import pandas as pd
import math

from src.costs import fee_pnl_impact, slippage_pnl_impact, funding_pnl_impact

# --- Parameters (keep deterministic) ---
FEE_RATE = 0.0004
SLIPPAGE_BPS = 2.0
QTY = 0.01  # BTC long
ENTRY_TS = "2026-02-10T00:00:00Z"
EXIT_TS  = "2026-02-20T00:00:00Z"

DATA_DIR = Path("data") / "processed"


def utc(ts: str) -> pd.Timestamp:
    t = pd.Timestamp(ts)
    return t.tz_convert("UTC") if t.tzinfo else pd.Timestamp(ts, tz="UTC")


def newest_match(pattern: str) -> Path:
    matches = list(DATA_DIR.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No files match pattern: {DATA_DIR}/{pattern}")
    # newest by modified time
    return max(matches, key=lambda p: p.stat().st_mtime)


def main():
    slip_frac = SLIPPAGE_BPS / 10_000.0

    # Auto-discover latest datasets
    klines_path = newest_match("binance_um_perp_BTCUSDT_1h_*.parquet")
    funding_path = newest_match("binance_um_perp_BTCUSDT_funding_8h_*.parquet")

    k = pd.read_parquet(klines_path)
    f = pd.read_parquet(funding_path)

    k["open_time"] = pd.to_datetime(k["open_time_ms"], unit="ms", utc=True)
    k["close_time"] = pd.to_datetime(k["close_time_ms"], unit="ms", utc=True)
    k = k.sort_values("open_time").reset_index(drop=True)

    f["funding_time"] = pd.to_datetime(f["fundingTime"], unit="ms", utc=True)
    f["fundingRate"] = pd.to_numeric(f["fundingRate"], errors="coerce")
    f = f.sort_values("funding_time").reset_index(drop=True)

    entry_t = utc(ENTRY_TS)
    exit_t = utc(EXIT_TS)

    entry_row = k[k["open_time"] >= entry_t].iloc[0]
    exit_row = k[k["open_time"] >= exit_t].iloc[0]

    entry_mid = float(entry_row["open"])
    exit_mid = float(exit_row["open"])

    entry_exec = entry_mid * (1.0 + slip_frac)   # worse for buy
    exit_exec = exit_mid * (1.0 - slip_frac)     # worse for sell

    entry_fee = fee_pnl_impact(+QTY, entry_exec, FEE_RATE)
    entry_slip = slippage_pnl_impact(+QTY, entry_mid, entry_exec)

    exit_fee = fee_pnl_impact(-QTY, exit_exec, FEE_RATE)
    exit_slip = slippage_pnl_impact(-QTY, exit_mid, exit_exec)

    # Funding events between entry and exit, position held = +QTY
    funding_pnl = 0.0

    k_close = k[["close_time", "close"]].sort_values("close_time").reset_index(drop=True)
    close_times = k_close["close_time"].values
    closes = k_close["close"].values

    held_funding = f[(f["funding_time"] >= entry_t) & (f["funding_time"] < exit_t)].copy()

    for _, r in held_funding.iterrows():
        ft = r["funding_time"].to_datetime64()
        fr = float(r["fundingRate"]) if pd.notna(r["fundingRate"]) else 0.0

        idx = close_times.searchsorted(ft, side="right") - 1
        if idx < 0:
            continue
        mark = float(closes[idx])

        funding_pnl += funding_pnl_impact(+QTY, mark, fr)

    total = entry_fee + entry_slip + exit_fee + exit_slip + funding_pnl

    print("=== BACKTEST SINGLE TRADE (AUTO-DISCOVERY) ===")
    print("klines_path:", klines_path.as_posix())
    print("funding_path:", funding_path.as_posix())
    print("entry_bar_open_time:", entry_row["open_time"])
    print("exit_bar_open_time:", exit_row["open_time"])
    print("entry_mid:", entry_mid, "entry_exec:", entry_exec)
    print("exit_mid:", exit_mid, "exit_exec:", exit_exec)
    print("entry_fee:", entry_fee)
    print("entry_slippage:", entry_slip)
    print("exit_fee:", exit_fee)
    print("exit_slippage:", exit_slip)
    print("funding_events_held:", len(held_funding))
    print("funding_pnl:", funding_pnl)
    print("TOTAL pnl impact:", total)


if __name__ == "__main__":
    main()