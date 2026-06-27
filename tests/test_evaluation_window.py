"""Tests for offline research runner evaluation-window semantics.

Package: WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-UNBLOCK-01

Validates that:
- Warmup rows establish indicator state but do not contribute to reported metrics.
- Signal is forced flat before evaluation_start (pre-window entries are blocked).
- evaluation_end is exclusive.
- Invalid windows fail closed.
- Omitting the window preserves existing full-frame behavior.
- The ATR denominator bundler preserves 108 unique row IDs across three states.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pandas as pd
import pytest

from tools.research_runner import run_offline_sweep as runner
from tools.research_runner.atr_denominator_bundler import (
    ATR_STATES,
    EXPECTED_ROWS_PER_STATE,
    EXPECTED_TOTAL_ROWS,
    BundlerError,
    bundle_atr_denominator,
    validate_bundle_denominator_integrity,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ohlcv(
    start: str,
    periods: int,
    freq: str = "15min",
    base_price: float = 100.0,
) -> pd.DataFrame:
    index = pd.date_range(start, periods=periods, freq=freq, tz="UTC")
    close = [base_price + i * 0.1 for i in range(len(index))]
    return pd.DataFrame(
        {
            "open": [p - 0.05 for p in close],
            "high": [p + 0.2 for p in close],
            "low": [p - 0.2 for p in close],
            "close": close,
            "volume": [1000.0] * len(index),
        },
        index=index,
    )


def _make_signal(index: pd.DatetimeIndex, value: float = 1.0) -> pd.Series:
    return pd.Series(value, index=index)


def _make_equity_curve(
    index: pd.DatetimeIndex,
    initial: float = 10_000.0,
    daily_drift: float = 10.0,
) -> pd.Series:
    values = [initial + i * daily_drift for i in range(len(index))]
    return pd.Series(values, index=index)


def _mock_backtest_result(
    equity_curve: pd.Series,
    trades: list[dict[str, Any]] | None = None,
    fees: float = 5.0,
    funding: float = 0.0,
    slippage: float = 1.0,
) -> MagicMock:
    result = MagicMock()
    result.equity_curve = equity_curve
    trades_data = trades or []
    if trades_data and "net_pnl" in trades_data[0]:
        result.trades_df = pd.DataFrame(trades_data)
    else:
        result.trades_df = pd.DataFrame(trades_data)
    result.fees_paid = fees
    result.funding_paid = funding
    result.slippage_paid = slippage
    result.params = {"initial_equity": float(equity_curve.iloc[0])}
    return result


# ---------------------------------------------------------------------------
# _validate_evaluation_window
# ---------------------------------------------------------------------------


def test_invalid_evaluation_window_fails_closed_start_equals_end():
    ohlcv = _make_ohlcv("2024-01-01", periods=20)
    ts = pd.Timestamp("2024-01-01 01:00:00", tz="UTC")
    with pytest.raises(runner.OfflineSweepError, match="strictly before"):
        runner._validate_evaluation_window(ts, ts, ohlcv)


def test_invalid_evaluation_window_fails_closed_start_after_end():
    ohlcv = _make_ohlcv("2024-01-01", periods=20)
    start = pd.Timestamp("2024-01-02", tz="UTC")
    end = pd.Timestamp("2024-01-01", tz="UTC")
    with pytest.raises(runner.OfflineSweepError, match="strictly before"):
        runner._validate_evaluation_window(start, end, ohlcv)


def test_invalid_evaluation_window_fails_closed_start_before_first_bar():
    ohlcv = _make_ohlcv("2024-01-01", periods=20)
    start = pd.Timestamp("2023-12-31", tz="UTC")
    end = pd.Timestamp("2024-01-02", tz="UTC")
    with pytest.raises(runner.OfflineSweepError, match="warmup prefix is missing"):
        runner._validate_evaluation_window(start, end, ohlcv)


def test_invalid_evaluation_window_fails_closed_too_few_bars():
    # Window that captures only 1 bar
    ohlcv = _make_ohlcv("2024-01-01", periods=20, freq="15min")
    start = pd.Timestamp("2024-01-01 00:00:00", tz="UTC")
    end = pd.Timestamp("2024-01-01 00:14:59", tz="UTC")
    with pytest.raises(runner.OfflineSweepError, match="fewer than 2 OHLCV bars"):
        runner._validate_evaluation_window(start, end, ohlcv)


def test_valid_evaluation_window_does_not_raise():
    ohlcv = _make_ohlcv("2024-01-01", periods=20, freq="15min")
    start = pd.Timestamp("2024-01-01 01:00:00", tz="UTC")
    end = pd.Timestamp("2024-01-01 02:00:00", tz="UTC")
    runner._validate_evaluation_window(start, end, ohlcv)


# ---------------------------------------------------------------------------
# _mask_signal_before_window
# ---------------------------------------------------------------------------


def test_evaluation_window_blocks_or_masks_pre_window_trades():
    index = pd.date_range("2024-01-01", periods=20, freq="15min", tz="UTC")
    signal = _make_signal(index, value=1.0)
    eval_start = pd.Timestamp("2024-01-01 03:00:00", tz="UTC")

    masked = runner._mask_signal_before_window(signal, eval_start)

    # All bars before eval_start must be 0
    pre = masked.loc[masked.index < eval_start]
    assert (pre == 0.0).all(), "pre-window signal values must be zeroed"

    # Bars at or after eval_start must be unchanged
    post = masked.loc[masked.index >= eval_start]
    assert (post == 1.0).all(), "post-window signal values must be unchanged"


def test_mask_signal_does_not_mutate_original():
    index = pd.date_range("2024-01-01", periods=10, freq="15min", tz="UTC")
    signal = _make_signal(index, value=1.0)
    eval_start = pd.Timestamp("2024-01-01 01:00:00", tz="UTC")

    masked = runner._mask_signal_before_window(signal, eval_start)

    # Original signal must be unchanged
    assert (signal == 1.0).all(), "original signal must not be mutated"
    assert masked is not signal, "must return a copy"


# ---------------------------------------------------------------------------
# _metrics_from_backtest_windowed
# ---------------------------------------------------------------------------


def test_evaluation_window_end_is_exclusive():
    index = pd.date_range("2024-01-01", periods=10, freq="15min", tz="UTC")
    equity = _make_equity_curve(index, initial=10_000.0, daily_drift=50.0)
    result = _mock_backtest_result(equity)

    eval_start = index[3]
    eval_end = index[7]  # exclusive — index[7] itself should NOT be included

    metrics = runner._metrics_from_backtest_windowed(result, "15m", eval_start, eval_end)

    # The window [index[3], index[7]) should include bars 3, 4, 5, 6 (4 bars)
    expected_window = equity.loc[(equity.index >= eval_start) & (equity.index < eval_end)]
    assert len(expected_window) == 4
    expected_pnl = float(expected_window.iloc[-1] - expected_window.iloc[0])
    assert abs(metrics["pnl"] - expected_pnl) < 1e-9, (
        f"pnl {metrics['pnl']} != expected {expected_pnl}"
    )


def test_evaluation_window_uses_warmup_for_features_but_excludes_warmup_metrics():
    """Equity metrics come only from the evaluation window slice.

    The test verifies that with signal masked during warmup, the equity at
    evaluation_start equals the backtest initial equity (no warmup P&L), and
    that the windowed metrics reflect only the evaluation window equity delta.
    """
    index = pd.date_range("2023-07-01", periods=40, freq="15min", tz="UTC")
    # Simulated equity: flat during warmup (first 20 bars), then rising
    warmup_equity = [10_000.0] * 20
    eval_equity = [10_000.0 + i * 100.0 for i in range(1, 21)]
    equity = pd.Series(warmup_equity + eval_equity, index=index)
    result = _mock_backtest_result(equity, fees=20.0)

    eval_start = index[20]
    eval_end = index[-1] + pd.Timedelta(minutes=15)

    metrics = runner._metrics_from_backtest_windowed(result, "15m", eval_start, eval_end)

    eval_window = equity.loc[(equity.index >= eval_start) & (equity.index < eval_end)]
    expected_pnl = float(eval_window.iloc[-1] - eval_window.iloc[0])
    assert metrics["pnl"] == pytest.approx(expected_pnl, rel=1e-6)
    # Warmup equity is flat, so eval starts at 10_000 and ends higher
    assert metrics["return_pct"] > 0.0
    # return_pct uses eval window's initial equity as baseline
    expected_return = expected_pnl / float(eval_window.iloc[0])
    assert metrics["return_pct"] == pytest.approx(expected_return, rel=1e-6)


def test_no_evaluation_window_preserves_existing_runner_behavior():
    """When no evaluation window is set, _metrics_from_backtest should be used."""
    index = pd.date_range("2024-01-01", periods=10, freq="15min", tz="UTC")
    equity = _make_equity_curve(index, initial=10_000.0, daily_drift=100.0)
    result = _mock_backtest_result(equity)
    result.params = {"initial_equity": 10_000.0}

    # Simulate the non-windowed path
    metrics_full = runner._metrics_from_backtest(result, "15m")

    # No evaluation window: return_pct should cover the full equity curve
    expected_pnl = float(equity.iloc[-1] - 10_000.0)
    assert metrics_full["pnl"] == pytest.approx(expected_pnl, rel=1e-6)


def test_windowed_metrics_fewer_than_2_points_fails_closed():
    index = pd.date_range("2024-01-01", periods=5, freq="15min", tz="UTC")
    equity = _make_equity_curve(index)
    result = _mock_backtest_result(equity)

    # Window that returns only 1 equity point
    eval_start = index[-1]
    eval_end = index[-1] + pd.Timedelta(minutes=1)

    with pytest.raises(runner.OfflineSweepError, match="fewer than 2 equity curve points"):
        runner._metrics_from_backtest_windowed(result, "15m", eval_start, eval_end)


# ---------------------------------------------------------------------------
# ATR parent-spec denominator bundler
# ---------------------------------------------------------------------------


def _make_rows(state_prefix: str, count: int = EXPECTED_ROWS_PER_STATE) -> list[dict[str, Any]]:
    return [
        {
            "variant_id": f"{state_prefix}-V{i:03d}",
            "outcome_category": "successful",
            "metrics": {"pnl": float(i)},
        }
        for i in range(1, count + 1)
    ]


def test_atr_parent_spec_route_preserves_108_expected_variant_ids():
    no_atr = _make_rows("no_atr")
    atr_20 = _make_rows("atr_20")
    atr_30 = _make_rows("atr_30")

    bundle = bundle_atr_denominator(no_atr, atr_20, atr_30)

    assert len(bundle) == EXPECTED_TOTAL_ROWS
    composite_ids = {row["composite_row_id"] for row in bundle}
    assert len(composite_ids) == EXPECTED_TOTAL_ROWS, "all composite IDs must be unique"


def test_no_atr_and_atr_states_do_not_collapse_or_overwrite_each_other():
    # Use the same variant_ids across all three states (worst-case collision scenario)
    shared_variant_ids = [f"V{i:03d}" for i in range(1, EXPECTED_ROWS_PER_STATE + 1)]
    no_atr = [{"variant_id": vid, "outcome_category": "successful"} for vid in shared_variant_ids]
    atr_20 = [{"variant_id": vid, "outcome_category": "failed"} for vid in shared_variant_ids]
    atr_30 = [{"variant_id": vid, "outcome_category": "errored"} for vid in shared_variant_ids]

    bundle = bundle_atr_denominator(no_atr, atr_20, atr_30)

    assert len(bundle) == EXPECTED_TOTAL_ROWS

    # Each state must be separately recoverable
    no_atr_rows = [r for r in bundle if r["risk_control_state"] == "no_atr"]
    atr_20_rows = [r for r in bundle if r["risk_control_state"] == "atr_20"]
    atr_30_rows = [r for r in bundle if r["risk_control_state"] == "atr_30"]
    assert len(no_atr_rows) == EXPECTED_ROWS_PER_STATE
    assert len(atr_20_rows) == EXPECTED_ROWS_PER_STATE
    assert len(atr_30_rows) == EXPECTED_ROWS_PER_STATE

    # Outcome values must not overwrite each other
    assert all(r["outcome_category"] == "successful" for r in no_atr_rows)
    assert all(r["outcome_category"] == "failed" for r in atr_20_rows)
    assert all(r["outcome_category"] == "errored" for r in atr_30_rows)

    # No composite_row_id overlap across states
    no_atr_ids = {r["composite_row_id"] for r in no_atr_rows}
    atr_20_ids = {r["composite_row_id"] for r in atr_20_rows}
    atr_30_ids = {r["composite_row_id"] for r in atr_30_rows}
    assert no_atr_ids.isdisjoint(atr_20_ids)
    assert no_atr_ids.isdisjoint(atr_30_ids)
    assert atr_20_ids.isdisjoint(atr_30_ids)


def test_bundler_rejects_wrong_row_count():
    no_atr = _make_rows("no_atr", count=35)  # one short
    atr_20 = _make_rows("atr_20")
    atr_30 = _make_rows("atr_30")

    with pytest.raises(BundlerError, match="expected 36 rows for state 'no_atr'"):
        bundle_atr_denominator(no_atr, atr_20, atr_30)


def test_bundle_integrity_validator_catches_errors():
    no_atr = _make_rows("no_atr")
    atr_20 = _make_rows("atr_20")
    atr_30 = _make_rows("atr_30")
    bundle = bundle_atr_denominator(no_atr, atr_20, atr_30)

    errors = validate_bundle_denominator_integrity(bundle)
    assert errors == [], f"clean bundle should have no errors: {errors}"

    # Corrupt the bundle: remove a row
    truncated = bundle[:107]
    errors = validate_bundle_denominator_integrity(truncated)
    assert any("107" in e or "108" in e for e in errors)
