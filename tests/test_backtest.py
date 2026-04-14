"""
tests/test_backtest.py — Additive unit tests for lib/backtest.py.

Tests:
  - test_sma2_hand_computed: 20-bar SMA(2) crossover, hand-computed expected equity
  - test_no_lookahead:       mutating a future bar must not change past results
  - test_irreparable_gap_skip: D2-003A gap skip correctness
  - test_funding_cashflow:   single 8h funding event on held position
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lib.backtest import run_backtest, BacktestResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ohlcv(closes, freq="1h", start="2020-01-01"):
    """Build synthetic OHLCV where open[i] = close[i-1] (open[0] = close[0])."""
    n = len(closes)
    dates = pd.date_range(start, periods=n, freq=freq, tz="UTC")
    opens = [closes[0]] + list(closes[:-1])
    return pd.DataFrame(
        {
            "open": opens,
            "high": [max(o, c) for o, c in zip(opens, closes)],
            "low": [min(o, c) for o, c in zip(opens, closes)],
            "close": closes,
            "volume": [1_000.0] * n,
        },
        index=dates,
    )


def _empty_funding(start="2020-01-01"):
    return pd.DataFrame(
        {"funding_rate": []},
        index=pd.DatetimeIndex([], tz="UTC"),
    )


def _no_gaps_path(tmp_path: Path) -> Path:
    """Write an empty irreparable_gaps.json and return its path."""
    p = tmp_path / "gaps.json"
    p.write_text(json.dumps({"schema_version": 1, "entries": []}))
    return p


# ---------------------------------------------------------------------------
# test_sma2_hand_computed
# ---------------------------------------------------------------------------


def test_sma2_hand_computed(tmp_path):
    """20-bar SMA(2) crossover: final equity must match hand-computed value within 1e-9.

    Setup
    -----
    Closes: [100, 101, 102, ..., 109, 108, 107, ..., 99]  (rise then fall)
    Open[i] = Close[i-1]  (open[0] = close[0] = 100)
    Fees = 0, slippage = 0, no funding.

    Signal: SMA(2) crossover
      fast = close[i]
      slow = SMA(2) = (close[i] + close[i-1]) / 2
      +1 if close[i] > SMA(2), i.e. close[i] > close[i-1]
      -1 otherwise
      0 for bar 0 (insufficient history)

    Hand-computed execution trace (no fees/slippage):
      signal[0] = 0  -> no position bar 0
      signal[1..9] = +1 (rising) -> enter LONG at open[2] = close[1] = 101
      signal[10] = -1 (close[10]=108 < close[9]=109)
        -> at bar 11: close LONG at open[11] = close[10] = 108
           realized = +(108 - 101) = +7.0
        -> open SHORT at 108
      signal[11..19] = -1 (falling)
        -> SHORT held to end
      At bar 19 (last): short position, close[19] = 99
        unrealized_short = -(99 - 108) = +9.0
      equity_curve[-1] = 10000 + 7 + 9 = 10016.0
    """
    initial = 10_000.0
    closes = [
        100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
        108, 107, 106, 105, 104, 103, 102, 101, 100,  99,
    ]
    n = len(closes)
    ohlcv = _make_ohlcv(closes)
    funding = _empty_funding()
    gaps_path = _no_gaps_path(tmp_path)

    close_s = pd.Series(closes, index=ohlcv.index)
    sma2 = close_s.rolling(2).mean()
    signal = pd.Series(0.0, index=ohlcv.index)
    valid = sma2.notna()
    signal[valid] = np.where(close_s[valid] > sma2[valid], 1.0, -1.0)

    result = run_backtest(
        signal=signal,
        ohlcv=ohlcv,
        funding=funding,
        fee_bps_taker=0.0,
        fee_bps_maker=0.0,
        slippage_bps=0.0,
        initial_equity=initial,
        stream="klines",
        interval="1h",
        gaps_path=gaps_path,
    )

    expected_final_equity = 10_016.0
    assert abs(result.equity_curve.iloc[-1] - expected_final_equity) < 1e-9, (
        f"Expected {expected_final_equity}, got {result.equity_curve.iloc[-1]}"
    )

    # Sanity: realized = 7, unrealized = 9
    assert abs(result.realized_pnl - 7.0) < 1e-9
    assert abs(result.unrealized_pnl - 9.0) < 1e-9


# ---------------------------------------------------------------------------
# test_no_lookahead
# ---------------------------------------------------------------------------


def test_no_lookahead(tmp_path):
    """Mutating a future bar's close must not change any past bar's equity result.

    We run the backtester twice:
      Run 1: clean data
      Run 2: close[15] set to an extreme value (99_999)
    Equity curve for bars 0..14 must be bit-for-bit identical.
    """
    n = 20
    closes = list(range(100, 120))  # monotonically rising -> consistent signal
    ohlcv_base = _make_ohlcv(closes)
    funding = _empty_funding()
    gaps_path = _no_gaps_path(tmp_path)

    close_s = pd.Series(closes, index=ohlcv_base.index)
    sma2 = close_s.rolling(2).mean()
    signal = pd.Series(0.0, index=ohlcv_base.index)
    valid = sma2.notna()
    signal[valid] = np.where(close_s[valid] > sma2[valid], 1.0, -1.0)

    kwargs = dict(
        signal=signal,
        funding=funding,
        fee_bps_taker=1.0,
        fee_bps_maker=0.5,
        slippage_bps=0.5,
        initial_equity=10_000.0,
        stream="klines",
        interval="1h",
        gaps_path=gaps_path,
    )

    result1 = run_backtest(ohlcv=ohlcv_base, **kwargs)

    # Mutate bar 15 close (a future bar relative to bars 0..14)
    ohlcv_mutated = ohlcv_base.copy()
    ohlcv_mutated.iloc[15, ohlcv_mutated.columns.get_loc("close")] = 99_999.0

    result2 = run_backtest(ohlcv=ohlcv_mutated, **kwargs)

    # Bars 0..14 must be identical
    for i in range(15):
        v1 = result1.equity_curve.iloc[i]
        v2 = result2.equity_curve.iloc[i]
        assert abs(v1 - v2) < 1e-9, (
            f"Bar {i}: run1={v1}, run2={v2} differ after future-bar mutation"
        )


# ---------------------------------------------------------------------------
# test_irreparable_gap_skip
# ---------------------------------------------------------------------------


def test_irreparable_gap_skip(tmp_path):
    """D2-003A: bars in the irreparable_gaps.json are skipped without corrupting equity.

    Setup
    -----
    20 bars, 1h interval.
    Bar at index 10 (2020-01-01 10:00 UTC) is flagged as irreparable.
    The backtester must:
      - skip that bar (not execute any fill at bar 11 based on bar 10's signal)
      - keep equity continuous (no NaN, no jump from skip alone)
      - report skipped_bars == 1
    """
    n = 20
    closes = list(range(100, 120))
    ohlcv = _make_ohlcv(closes)
    funding = _empty_funding()

    bar_10_ts = ohlcv.index[10]  # 2020-01-01 10:00 UTC

    gaps_data = {
        "schema_version": 1,
        "entries": [
            {
                "stream": "klines",
                "interval": "1h",
                "start_utc": bar_10_ts.isoformat(),
                "end_utc": bar_10_ts.isoformat(),
                "missing_bars": 1,
                "verified_utc": "2026-01-01T00:00:00Z",
                "sources_checked": ["monthly_archive"],
            }
        ],
    }
    gaps_path = tmp_path / "gaps.json"
    gaps_path.write_text(json.dumps(gaps_data))

    # Compute signal from SMA(2) crossover
    close_s = pd.Series(closes, index=ohlcv.index)
    sma2 = close_s.rolling(2).mean()
    signal = pd.Series(0.0, index=ohlcv.index)
    valid = sma2.notna()
    signal[valid] = np.where(close_s[valid] > sma2[valid], 1.0, -1.0)

    result = run_backtest(
        signal=signal,
        ohlcv=ohlcv,
        funding=funding,
        fee_bps_taker=0.0,
        fee_bps_maker=0.0,
        slippage_bps=0.0,
        initial_equity=10_000.0,
        stream="klines",
        interval="1h",
        gaps_path=gaps_path,
    )

    # D2-003A: exactly 1 bar skipped
    assert result.skipped_bars == 1
    assert bar_10_ts in result.skipped_bar_timestamps

    # Equity curve must be finite everywhere (no NaN corruption)
    assert result.equity_curve.isna().sum() == 0, "equity_curve must not contain NaN"

    # Equity at bar 10 must equal equity at bar 9 (carry-forward with no pnl)
    eq9 = result.equity_curve.iloc[9]
    eq10 = result.equity_curve.iloc[10]
    assert eq9 == eq10, (
        f"Skipped bar should carry equity forward: bar9={eq9}, bar10={eq10}"
    )


# ---------------------------------------------------------------------------
# test_funding_cashflow
# ---------------------------------------------------------------------------


def test_funding_cashflow(tmp_path):
    """A single 8h funding event on a held long position must match hand-computed value.

    Setup
    -----
    5 bars (1h), all prices flat at 50_000.
    signal = [0, +1, +1, +1, +1]  -> enter LONG at bar 2 (open = 50_000)
    Funding event at 02:30 UTC (between bar 2 and bar 3), rate = 0.0001 (0.01%)

    Hand-computed funding cashflow:
      funding_cashflow = -position * rate * entry_fill_price
                       = -1 * 0.0001 * 50_000 = -5.0
      equity_curve[3] = 10_000 - 5 = 9_995
      result.funding_paid = 5.0
    """
    initial = 10_000.0
    n = 5
    price = 50_000.0
    dates = pd.date_range("2020-01-01", periods=n, freq="1h", tz="UTC")

    ohlcv = pd.DataFrame(
        {
            "open": [price] * n,
            "high": [price] * n,
            "low": [price] * n,
            "close": [price] * n,
            "volume": [1000.0] * n,
        },
        index=dates,
    )

    # Funding event between bar 2 (02:00) and bar 3 (03:00)
    funding_ts = pd.Timestamp("2020-01-01 02:30:00", tz="UTC")
    rate = 0.0001
    funding = pd.DataFrame(
        {"funding_rate": [rate]},
        index=pd.DatetimeIndex([funding_ts], tz="UTC"),
    )

    # Signal: 0, +1, +1, +1, +1  -> fill at bar 2 (open=50000)
    signal = pd.Series([0.0, 1.0, 1.0, 1.0, 1.0], index=dates)

    gaps_path = _no_gaps_path(tmp_path)

    result = run_backtest(
        signal=signal,
        ohlcv=ohlcv,
        funding=funding,
        fee_bps_taker=0.0,
        fee_bps_maker=0.0,
        slippage_bps=0.0,
        initial_equity=initial,
        stream="klines",
        interval="1h",
        gaps_path=gaps_path,
    )

    expected_funding_paid = rate * price  # 0.0001 * 50_000 = 5.0
    expected_eq_bar3 = initial - expected_funding_paid  # 9_995.0

    assert abs(result.funding_paid - expected_funding_paid) < 1e-9, (
        f"funding_paid: expected {expected_funding_paid}, got {result.funding_paid}"
    )
    assert abs(result.equity_curve.iloc[3] - expected_eq_bar3) < 1e-9, (
        f"equity[3]: expected {expected_eq_bar3}, got {result.equity_curve.iloc[3]}"
    )
