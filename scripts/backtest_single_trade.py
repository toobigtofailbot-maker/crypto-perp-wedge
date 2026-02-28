import json
from pathlib import Path
import pandas as pd

from src.costs import fee_pnl_impact, slippage_pnl_impact, funding_pnl_impact

DATA_DIR = Path("data") / "processed"
CFG_PATH = Path("configs") / "backtest_single_trade.json"


def utc(ts: str) -> pd.Timestamp:
    t = pd.Timestamp(ts)
    return t.tz_convert("UTC") if t.tzinfo else pd.Timestamp(ts, tz="UTC")


def newest_match(pattern: str) -> Path:
    matches = list(DATA_DIR.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No files match pattern: {DATA_DIR}/{pattern}")
    return max(matches, key=lambda p: p.stat().st_mtime)


def load_cfg() -> dict:
    with open(CFG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    cfg = load_cfg()

    qty = float(cfg["qty"])
    fee_rate = float(cfg["fee_rate"])
    slippage_bps = float(cfg["slippage_bps"])
    entry_ts = str(cfg["entry_ts"])
    exit_ts = str(cfg["exit_ts"])

    slip_frac = slippage_bps / 10_000.0

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

    entry_t = utc(entry_ts)
    exit_t = utc(exit_ts)

    entry_row = k[k["open_time"] >= entry_t].iloc[0]
    exit_row = k[k["open_time"] >= exit_t].iloc[0]

    entry_mid = float(entry_row["open"])
    exit_mid = float(exit_row["open"])

    # Exec simulation: slippage against us (depends on trade direction)
    # Entry trade is +qty (buy if qty>0, sell if qty<0)
    entry_exec = entry_mid * (1.0 + slip_frac) if qty > 0 else entry_mid * (1.0 - slip_frac)
    # Exit trade closes position: -qty
    exit_exec = exit_mid * (1.0 - slip_frac) if qty > 0 else exit_mid * (1.0 + slip_frac)

    entry_fee = fee_pnl_impact(qty, entry_exec, fee_rate)
    entry_slip = slippage_pnl_impact(qty, entry_mid, entry_exec)

    exit_fee = fee_pnl_impact(-qty, exit_exec, fee_rate)
    exit_slip = slippage_pnl_impact(-qty, exit_mid, exit_exec)

    # Funding during hold: position = qty
    k_close = k[["close_time", "close"]].sort_values("close_time").reset_index(drop=True)
    close_times = k_close["close_time"].values
    closes = k_close["close"].values

    held_funding = f[(f["funding_time"] >= entry_t) & (f["funding_time"] < exit_t)].copy()

    funding_pnl = 0.0
    for _, r in held_funding.iterrows():
        ft = r["funding_time"].to_datetime64()
        fr = float(r["fundingRate"]) if pd.notna(r["fundingRate"]) else 0.0

        idx = close_times.searchsorted(ft, side="right") - 1
        if idx < 0:
            continue
        mark = float(closes[idx])

        funding_pnl += funding_pnl_impact(qty, mark, fr)

    total = entry_fee + entry_slip + exit_fee + exit_slip + funding_pnl

    print("=== BACKTEST SINGLE TRADE (CONFIG + AUTO-DISCOVERY) ===")
    print("cfg_path:", CFG_PATH.as_posix())
    print("qty:", qty, "fee_rate:", fee_rate, "slippage_bps:", slippage_bps)
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