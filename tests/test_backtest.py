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
from lib.evaluation import cost_drag


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


def _fee_side_fixture(tmp_path: Path, **kwargs):
    """Run a deterministic one-round-trip fixture for fee-side tests."""
    dates = pd.date_range("2020-01-01", periods=6, freq="1h", tz="UTC")
    ohlcv = pd.DataFrame(
        {
            "open": [100.0, 100.0, 110.0, 120.0, 130.0, 140.0],
            "high": [100.0, 110.0, 120.0, 130.0, 140.0, 150.0],
            "low": [100.0, 100.0, 110.0, 120.0, 130.0, 140.0],
            "close": [100.0, 110.0, 120.0, 130.0, 140.0, 150.0],
            "volume": [1_000.0] * 6,
        },
        index=dates,
    )
    signal = pd.Series([0.0, 1.0, 1.0, 0.0, 0.0, 0.0], index=dates)
    return run_backtest(
        signal=signal,
        ohlcv=ohlcv,
        funding=_empty_funding(),
        fee_bps_taker=10.0,
        fee_bps_maker=2.0,
        slippage_bps=1.0,
        initial_equity=10_000.0,
        stream="klines",
        interval="1h",
        gaps_path=_no_gaps_path(tmp_path),
        **kwargs,
    )


# ---------------------------------------------------------------------------
# test_fee_side_model
# ---------------------------------------------------------------------------


def test_default_taker_taker_fee_behavior_preserved(tmp_path):
    result = _fee_side_fixture(tmp_path)

    expected_equity = [
        10_000.0,
        10_000.0,
        10_009.879,
        10_019.879,
        10_019.736,
        10_019.736,
    ]
    np.testing.assert_allclose(
        result.equity_curve.tolist(), expected_equity, rtol=0, atol=1e-12
    )
    np.testing.assert_allclose(
        result.trades_df["fees"].tolist(), [0.13], rtol=0, atol=1e-12
    )
    assert abs(result.fees_paid - 0.24) < 1e-12
    assert abs(result.slippage_paid - 0.024) < 1e-12
    assert result.funding_paid == 0.0
    assert result.liquidated is False
    assert result.params["entry_fee_side"] == "taker"
    assert result.params["exit_fee_side"] == "taker"
    assert result.params["exchange_constraints"] == {
        "tick_size": None,
        "lot_size": None,
        "min_notional": None,
    }


def test_maker_entry_uses_maker_fee(tmp_path):
    result = _fee_side_fixture(tmp_path, entry_fee_side="maker")

    expected_entry_fee = 110.0 * 2.0 / 10_000.0
    expected_exit_fee = 130.0 * 10.0 / 10_000.0
    assert abs(result.fees_paid - (expected_entry_fee + expected_exit_fee)) < 1e-12
    np.testing.assert_allclose(
        result.trades_df["fees"].tolist(), [expected_exit_fee], rtol=0, atol=1e-12
    )
    assert result.params["entry_fee_side"] == "maker"
    assert result.params["exit_fee_side"] == "taker"


def test_maker_exit_uses_maker_fee(tmp_path):
    result = _fee_side_fixture(tmp_path, exit_fee_side="maker")

    expected_entry_fee = 110.0 * 10.0 / 10_000.0
    expected_exit_fee = 130.0 * 2.0 / 10_000.0
    assert abs(result.fees_paid - (expected_entry_fee + expected_exit_fee)) < 1e-12
    np.testing.assert_allclose(
        result.trades_df["fees"].tolist(), [expected_exit_fee], rtol=0, atol=1e-12
    )
    assert result.params["entry_fee_side"] == "taker"
    assert result.params["exit_fee_side"] == "maker"


def test_mixed_maker_taker_fee_sides_and_cost_drag(tmp_path):
    taker_taker = _fee_side_fixture(tmp_path)
    maker_maker = _fee_side_fixture(
        tmp_path,
        entry_fee_side="maker",
        exit_fee_side="maker",
    )

    expected_maker_maker_fees = (110.0 + 130.0) * 2.0 / 10_000.0
    expected_delta = taker_taker.fees_paid - expected_maker_maker_fees
    assert abs(maker_maker.fees_paid - expected_maker_maker_fees) < 1e-12
    assert abs(expected_delta - 0.192) < 1e-12

    drag = cost_drag(maker_maker)
    assert drag["fees_paid"] == maker_maker.fees_paid
    assert (
        abs(drag["total_cost"] - (maker_maker.fees_paid + maker_maker.slippage_paid))
        < 1e-12
    )


def test_invalid_fee_side_raises(tmp_path):
    with pytest.raises(ValueError, match="fee side"):
        _fee_side_fixture(tmp_path, entry_fee_side="post_only")

    with pytest.raises(ValueError, match="fee side"):
        _fee_side_fixture(tmp_path, exit_fee_side="auction")


# ---------------------------------------------------------------------------
# test_exchange_constraint_disclosure
# ---------------------------------------------------------------------------


def test_exchange_constraint_disclosure_recorded_without_outcome_effect(tmp_path):
    baseline = _fee_side_fixture(tmp_path)
    disclosed = _fee_side_fixture(
        tmp_path,
        tick_size=0.1,
        lot_size=0.001,
        min_notional=5.0,
    )

    pd.testing.assert_series_equal(disclosed.equity_curve, baseline.equity_curve)
    pd.testing.assert_series_equal(disclosed.per_bar_pnl, baseline.per_bar_pnl)
    pd.testing.assert_frame_equal(disclosed.trades_df, baseline.trades_df)
    assert disclosed.fees_paid == baseline.fees_paid
    assert disclosed.slippage_paid == baseline.slippage_paid
    assert disclosed.funding_paid == baseline.funding_paid
    assert disclosed.realized_pnl == baseline.realized_pnl
    assert disclosed.unrealized_pnl == baseline.unrealized_pnl
    assert disclosed.liquidated == baseline.liquidated
    assert disclosed.liquidation_timestamp == baseline.liquidation_timestamp
    assert disclosed.params["exchange_constraints"] == {
        "tick_size": 0.1,
        "lot_size": 0.001,
        "min_notional": 5.0,
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {"tick_size": 0.0},
        {"tick_size": -0.1},
        {"lot_size": 0.0},
        {"lot_size": -0.001},
        {"min_notional": 0.0},
        {"min_notional": -5.0},
    ],
)
def test_invalid_exchange_constraint_disclosure_raises(tmp_path, kwargs):
    with pytest.raises(ValueError, match="must be positive"):
        _fee_side_fixture(tmp_path, **kwargs)


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


def _funding_notional_fixture(tmp_path: Path, *, signal_values=None, **kwargs):
    """Run a compact deterministic funding fixture with changing closes."""
    dates = pd.date_range("2020-01-01", periods=5, freq="1h", tz="UTC")
    ohlcv = pd.DataFrame(
        {
            "open": [100.0, 100.0, 100.0, 120.0, 130.0],
            "high": [100.0, 110.0, 120.0, 130.0, 140.0],
            "low": [100.0, 90.0, 95.0, 115.0, 125.0],
            "close": [100.0, 110.0, 120.0, 130.0, 140.0],
            "volume": [1_000.0] * 5,
        },
        index=dates,
    )
    signal = pd.Series(
        signal_values if signal_values is not None else [0.0, 1.0, 1.0, 1.0, 1.0],
        index=dates,
    )
    funding = pd.DataFrame(
        {"funding_rate": [0.01, 0.02]},
        index=pd.DatetimeIndex(
            [
                pd.Timestamp("2020-01-01 02:00:00", tz="UTC"),
                pd.Timestamp("2020-01-01 02:30:00", tz="UTC"),
            ],
            tz="UTC",
        ),
    )
    return run_backtest(
        signal=signal,
        ohlcv=ohlcv,
        funding=funding,
        fee_bps_taker=0.0,
        fee_bps_maker=0.0,
        slippage_bps=0.0,
        initial_equity=10_000.0,
        stream="klines",
        interval="1h",
        gaps_path=_no_gaps_path(tmp_path),
        **kwargs,
    )


def test_default_funding_notional_mode_preserves_entry_price_behavior(tmp_path):
    implicit_default = _funding_notional_fixture(tmp_path)
    explicit_default = _funding_notional_fixture(
        tmp_path,
        funding_notional_mode="entry_price",
    )

    pd.testing.assert_series_equal(
        implicit_default.equity_curve,
        explicit_default.equity_curve,
    )
    pd.testing.assert_series_equal(
        implicit_default.per_bar_pnl,
        explicit_default.per_bar_pnl,
    )
    pd.testing.assert_frame_equal(
        implicit_default.trades_df,
        explicit_default.trades_df,
    )
    assert implicit_default.funding_paid == 2.0
    assert explicit_default.funding_paid == 2.0
    assert implicit_default.fees_paid == explicit_default.fees_paid == 0.0
    assert implicit_default.slippage_paid == explicit_default.slippage_paid == 0.0
    assert implicit_default.liquidated is explicit_default.liquidated is False
    assert implicit_default.params["funding_notional_mode"] == "entry_price"
    assert explicit_default.params["funding_notional_mode"] == "entry_price"


def test_mark_price_funding_uses_current_bar_close_and_updates_cost_drag(tmp_path):
    entry_mode = _funding_notional_fixture(tmp_path)
    mark_mode = _funding_notional_fixture(
        tmp_path,
        funding_notional_mode="mark_price",
    )

    expected_entry_funding = 0.02 * 100.0
    expected_mark_funding = 0.02 * 130.0
    expected_delta = expected_mark_funding - expected_entry_funding

    assert abs(entry_mode.funding_paid - expected_entry_funding) < 1e-12
    assert abs(mark_mode.funding_paid - expected_mark_funding) < 1e-12
    assert abs(mark_mode.funding_paid - entry_mode.funding_paid - expected_delta) < 1e-12
    assert abs(mark_mode.equity_curve.iloc[3] - 10027.4) < 1e-12
    assert abs(mark_mode.equity_curve.iloc[-1] - 10037.4) < 1e-12
    assert mark_mode.params["funding_notional_mode"] == "mark_price"

    entry_drag = cost_drag(entry_mode)
    mark_drag = cost_drag(mark_mode)
    assert entry_drag["funding_paid"] == 2.0
    assert mark_drag["funding_paid"] == 2.6
    assert entry_drag["cost_drag_fraction"] == 0.05
    assert mark_drag["cost_drag_fraction"] == 0.065


def test_short_positive_funding_receives_under_both_notional_modes(tmp_path):
    entry_mode = _funding_notional_fixture(
        tmp_path,
        signal_values=[0.0, -1.0, -1.0, -1.0, -1.0],
    )
    mark_mode = _funding_notional_fixture(
        tmp_path,
        signal_values=[0.0, -1.0, -1.0, -1.0, -1.0],
        funding_notional_mode="mark_price",
    )

    assert abs(entry_mode.funding_paid - -2.0) < 1e-12
    assert abs(mark_mode.funding_paid - -2.6) < 1e-12
    assert abs(entry_mode.equity_curve.iloc[3] - 9972.0) < 1e-12
    assert abs(mark_mode.equity_curve.iloc[3] - 9972.6) < 1e-12


def test_multiple_funding_events_in_one_interval_use_same_current_close(tmp_path):
    dates = pd.date_range("2020-01-01", periods=5, freq="1h", tz="UTC")
    ohlcv = pd.DataFrame(
        {
            "open": [100.0, 100.0, 100.0, 120.0, 130.0],
            "high": [100.0, 110.0, 120.0, 130.0, 140.0],
            "low": [100.0, 90.0, 95.0, 115.0, 125.0],
            "close": [100.0, 110.0, 120.0, 130.0, 140.0],
            "volume": [1_000.0] * 5,
        },
        index=dates,
    )
    signal = pd.Series([0.0, 1.0, 1.0, 1.0, 1.0], index=dates)
    funding = pd.DataFrame(
        {"funding_rate": [0.01, 0.02, -0.005]},
        index=pd.DatetimeIndex(
            [
                pd.Timestamp("2020-01-01 02:15:00", tz="UTC"),
                pd.Timestamp("2020-01-01 02:30:00", tz="UTC"),
                pd.Timestamp("2020-01-01 02:45:00", tz="UTC"),
            ],
            tz="UTC",
        ),
    )

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
        gaps_path=_no_gaps_path(tmp_path),
        funding_notional_mode="mark_price",
    )

    expected_funding_paid = (0.01 + 0.02 - 0.005) * 130.0
    assert abs(result.funding_paid - expected_funding_paid) < 1e-12
    assert abs(result.equity_curve.iloc[3] - 10026.75) < 1e-12


def test_funding_event_at_entry_bar_timestamp_remains_excluded(tmp_path):
    result = _funding_notional_fixture(
        tmp_path,
        funding_notional_mode="mark_price",
    )

    # The 02:00 event is at the same bar timestamp where the position opens,
    # so the existing open-position rule excludes it; only 02:30 is applied.
    assert abs(result.funding_paid - (0.02 * 130.0)) < 1e-12


def test_invalid_funding_notional_mode_raises(tmp_path):
    with pytest.raises(ValueError, match="funding_notional_mode"):
        _funding_notional_fixture(tmp_path, funding_notional_mode="index_price")
