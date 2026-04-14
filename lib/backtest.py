"""
lib/backtest.py — pandas/numpy research backtester.

Design rules:
  - Signal at bar t -> fill at open of t+1 (no lookahead)
  - Irreparable bars (D2-003A) are skipped; trade state carried forward
  - Fees and slippage are modeled parametrically in bps
  - Funding cashflows applied at exact funding-event timestamps
  - All inputs must be UTC-indexed, monotonic, no duplicates (asserted)
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_IRREPARABLE_GAPS_PATH = Path(__file__).parent.parent / "data" / "irreparable_gaps.json"

_INTERVAL_TO_MINUTES: dict[str, int] = {
    "1m": 1,
    "3m": 3,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "2h": 120,
    "4h": 240,
    "6h": 360,
    "8h": 480,
    "12h": 720,
    "1d": 1440,
}

# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BacktestResult:
    """Frozen result of a single backtest run.

    All monetary fields are in the same unit as ``initial_equity``
    (typically USD notional).
    """

    equity_curve: pd.Series          # index = bar timestamps, values = equity
    trades_df: pd.DataFrame          # one row per round-trip trade
    per_bar_pnl: pd.Series           # unrealized + realized pnl per bar
    realized_pnl: float              # cumulative realized pnl (excl. costs)
    unrealized_pnl: float            # open pnl at end of run
    fees_paid: float                 # total taker/maker fees paid
    slippage_paid: float             # total slippage cost
    funding_paid: float              # net funding paid (positive = cost)
    skipped_bars: int                # D2-003A: number of bars skipped
    skipped_bar_timestamps: list     # audit trail of skipped bar timestamps
    params: dict                     # snapshot of run parameters


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_irreparable_gaps(gaps_path: Path) -> list[dict]:
    """Load irreparable_gaps.json entries."""
    if not gaps_path.exists():
        return []
    with gaps_path.open() as fh:
        data = json.load(fh)
    return data.get("entries", [])


def _build_irreparable_set(
    gaps: list[dict],
    stream: str,
    interval: str,
) -> set[pd.Timestamp]:
    """Return the set of bar timestamps that are irreparable for this stream/interval."""
    irreparable: set[pd.Timestamp] = set()
    freq_minutes = _INTERVAL_TO_MINUTES.get(interval)
    if freq_minutes is None:
        return irreparable

    for entry in gaps:
        if entry.get("stream") != stream or entry.get("interval") != interval:
            continue
        start = pd.Timestamp(entry["start_utc"], tz="UTC")
        end = pd.Timestamp(entry["end_utc"], tz="UTC")
        freq = pd.Timedelta(minutes=freq_minutes)
        ts = start
        while ts <= end:
            irreparable.add(ts)
            ts += freq

    return irreparable


def _validate_series_index(series: pd.Series | pd.DataFrame, name: str) -> None:
    """Assert UTC, monotonic-increasing, no duplicate timestamps."""
    idx = series.index
    assert isinstance(idx, pd.DatetimeIndex), (
        f"{name} must have a DatetimeIndex, got {type(idx)}"
    )
    assert idx.tz is not None and str(idx.tz) in ("UTC", "utc", "Etc/UTC"), (
        f"{name} index must be UTC-localized, got tz={idx.tz}"
    )
    assert idx.is_monotonic_increasing, f"{name} index must be monotonic increasing"
    assert not idx.duplicated().any(), f"{name} index must have no duplicates"


def _bps_cost(price: float, size: float, bps: float) -> float:
    """Return cost in USD for a trade at ``price`` of ``size`` contracts."""
    return abs(price * size) * bps / 10_000.0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_backtest(
    signal: pd.Series,
    ohlcv: pd.DataFrame,
    funding: pd.DataFrame,
    *,
    fee_bps_taker: float,
    fee_bps_maker: float,
    slippage_bps: float,
    initial_equity: float,
    execution: str = "next_bar_open",
    stream: str = "klines",
    interval: str = "1h",
    gaps_path: Optional[Path] = None,
) -> BacktestResult:
    """Run a vectorised bar-by-bar backtest.

    Parameters
    ----------
    signal:
        +1 long, -1 short, 0 flat. Index = UTC bar-close timestamps.
        Signal at bar t → fill at open of t+1.
    ohlcv:
        DataFrame with columns [open, high, low, close, volume].
        Index = UTC bar-close timestamps, must align with ``signal``.
    funding:
        DataFrame with columns [funding_rate].
        Index = UTC funding-event timestamps (every 8 h for Binance UM perp).
    fee_bps_taker, fee_bps_maker:
        Fee in basis-points per side.  Entries use taker; exits use taker.
    slippage_bps:
        One-way slippage in basis-points (applied symmetrically on entry/exit).
    initial_equity:
        Starting equity in USD.
    execution:
        Must be ``"next_bar_open"``; other values raise ``AssertionError``.
    stream, interval:
        Used to look up irreparable gaps in ``data/irreparable_gaps.json``.
    gaps_path:
        Override path to irreparable_gaps.json (used in tests).

    Returns
    -------
    BacktestResult
        Frozen dataclass with equity curve, trades, cost breakdown, and audit data.
    """
    assert execution == "next_bar_open", (
        f"Only 'next_bar_open' execution is supported, got '{execution}'"
    )

    # ------------------------------------------------------------------
    # Input validation
    # ------------------------------------------------------------------
    _validate_series_index(signal, "signal")
    _validate_series_index(ohlcv, "ohlcv")
    _validate_series_index(funding, "funding")

    required_ohlcv_cols = {"open", "high", "low", "close", "volume"}
    missing = required_ohlcv_cols - set(ohlcv.columns)
    assert not missing, f"ohlcv missing columns: {missing}"

    assert "funding_rate" in funding.columns, (
        "funding DataFrame must have 'funding_rate' column"
    )

    assert initial_equity > 0, "initial_equity must be positive"

    # Align signal to ohlcv index (inner join so we only process bars present in both)
    common_idx = signal.index.intersection(ohlcv.index)
    signal = signal.reindex(common_idx).fillna(0)
    ohlcv = ohlcv.reindex(common_idx)

    assert len(signal) >= 2, "Need at least 2 bars to run a backtest"

    # ------------------------------------------------------------------
    # Load D2-003A irreparable gaps
    # ------------------------------------------------------------------
    _gaps_path = gaps_path if gaps_path is not None else _IRREPARABLE_GAPS_PATH
    gaps = _load_irreparable_gaps(_gaps_path)
    irreparable_set = _build_irreparable_set(gaps, stream, interval)

    # ------------------------------------------------------------------
    # Pre-compute funding cashflows
    # Funding is applied to open positions at each funding event timestamp.
    # For a long position: cashflow = -funding_rate * position_value
    # For a short:         cashflow = +funding_rate * position_value
    # (positive funding_rate → longs pay shorts)
    # ------------------------------------------------------------------
    funding_events = funding["funding_rate"].to_dict()  # ts -> rate

    # ------------------------------------------------------------------
    # Bar-by-bar loop
    # ------------------------------------------------------------------
    n = len(signal)
    bars = ohlcv.index.tolist()
    sig_vals = signal.values
    open_prices = ohlcv["open"].values
    close_prices = ohlcv["close"].values

    equity = initial_equity
    position = 0          # current position: +1, -1, or 0
    entry_price = 0.0
    entry_bar_idx = -1

    equity_curve_vals = np.full(n, np.nan)
    per_bar_pnl_vals = np.zeros(n)

    total_fees = 0.0
    total_slippage = 0.0
    total_funding = 0.0
    total_realized = 0.0

    skipped_bars: list = []
    trades: list[dict] = []

    # We need to track position value for funding calculations.
    # Assume 1-contract sizing: position_value = abs(position) * fill_price.
    # This keeps the math clean; callers can scale to notional externally.
    entry_fill_price = 0.0

    for i in range(n):
        bar_ts = bars[i]

        # ---- D2-003A: skip irreparable bars ----
        if bar_ts in irreparable_set:
            skipped_bars.append(bar_ts)
            # Carry forward last known equity (including unrealized); trade state unchanged
            prev_eq = equity_curve_vals[i - 1] if i > 0 else initial_equity
            equity_curve_vals[i] = prev_eq
            per_bar_pnl_vals[i] = 0.0
            continue

        # ---- Apply funding cashflows that fall in (prev_bar_ts, bar_ts] ----
        if i > 0 and position != 0:
            prev_bar_ts = bars[i - 1]
            for f_ts, rate in funding_events.items():
                if not isinstance(f_ts, pd.Timestamp):
                    f_ts = pd.Timestamp(f_ts)
                if prev_bar_ts < f_ts <= bar_ts:
                    # Longs pay positive funding; shorts receive
                    # cashflow to equity = -position * rate * abs(entry_fill_price)
                    funding_cashflow = -position * rate * abs(entry_fill_price)
                    equity += funding_cashflow
                    total_funding -= funding_cashflow  # positive means we paid

        # ---- Unrealized PnL on open position at bar close ----
        unrealized = 0.0
        if position != 0:
            unrealized = position * (close_prices[i] - entry_fill_price)

        # ---- Determine fill for this bar ----
        # Signal at bar i-1 -> fill at open of bar i (next_bar_open)
        if i > 0:
            desired = int(sig_vals[i - 1])
            if desired != position:
                fill_price = open_prices[i]

                # ---- Close existing position if any ----
                if position != 0:
                    realized_this_trade = position * (fill_price - entry_fill_price)
                    fee_exit = _bps_cost(fill_price, 1.0, fee_bps_taker)
                    slip_exit = _bps_cost(fill_price, 1.0, slippage_bps)

                    equity += realized_this_trade - fee_exit - slip_exit
                    total_fees += fee_exit
                    total_slippage += slip_exit
                    total_realized += realized_this_trade

                    trades.append({
                        "entry_bar": bars[entry_bar_idx],
                        "exit_bar": bar_ts,
                        "direction": position,
                        "entry_price": entry_fill_price,
                        "exit_price": fill_price,
                        "gross_pnl": realized_this_trade,
                        "fees": fee_exit,
                        "slippage": slip_exit,
                        "net_pnl": realized_this_trade - fee_exit - slip_exit,
                    })
                    position = 0
                    entry_fill_price = 0.0

                # ---- Open new position if desired != 0 ----
                if desired != 0:
                    fee_entry = _bps_cost(fill_price, 1.0, fee_bps_taker)
                    slip_entry = _bps_cost(fill_price, 1.0, slippage_bps)
                    equity -= fee_entry + slip_entry
                    total_fees += fee_entry
                    total_slippage += slip_entry

                    position = desired
                    entry_fill_price = fill_price
                    entry_price = fill_price
                    entry_bar_idx = i

        # ---- Recompute unrealized after any fill ----
        if position != 0:
            unrealized = position * (close_prices[i] - entry_fill_price)
        else:
            unrealized = 0.0

        equity_curve_vals[i] = equity + unrealized
        per_bar_pnl_vals[i] = (
            equity + unrealized - (equity_curve_vals[i - 1] if i > 0 else initial_equity)
        )

    # ---- Close any open position at last bar's close ----
    final_unrealized = 0.0
    if position != 0:
        last_close = close_prices[-1]
        final_unrealized = position * (last_close - entry_fill_price)

    equity_series = pd.Series(equity_curve_vals, index=bars, name="equity")
    pnl_series = pd.Series(per_bar_pnl_vals, index=bars, name="pnl")

    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame(
        columns=[
            "entry_bar", "exit_bar", "direction",
            "entry_price", "exit_price",
            "gross_pnl", "fees", "slippage", "net_pnl",
        ]
    )

    params_snapshot = {
        "fee_bps_taker": fee_bps_taker,
        "fee_bps_maker": fee_bps_maker,
        "slippage_bps": slippage_bps,
        "initial_equity": initial_equity,
        "execution": execution,
        "stream": stream,
        "interval": interval,
        "n_bars": n,
        "n_irreparable_skipped": len(skipped_bars),
    }

    return BacktestResult(
        equity_curve=equity_series,
        trades_df=trades_df,
        per_bar_pnl=pnl_series,
        realized_pnl=total_realized,
        unrealized_pnl=final_unrealized,
        fees_paid=total_fees,
        slippage_paid=total_slippage,
        funding_paid=total_funding,
        skipped_bars=len(skipped_bars),
        skipped_bar_timestamps=skipped_bars,
        params=params_snapshot,
    )
