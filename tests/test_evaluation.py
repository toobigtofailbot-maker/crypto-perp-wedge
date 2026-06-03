"""
tests/test_evaluation.py — Additive unit tests for lib/evaluation.py.

Tests:
  - test_sharpe_sortino_calmar_known_values: fixture with known answers
  - test_dsr_overfit_case: 1000 trials, sharpe=1.2 -> DSR fails gate
  - test_promotion_gates_pass_and_fail: deliberate pass + fail fixtures
  - test_append_trial_roundtrip: append_trial + re-read + schema match
"""

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lib.backtest import BacktestResult
from lib.evaluation import (
    GateReport,
    TrialEntry,
    append_trial,
    calmar,
    check_promotion_gates,
    cost_drag,
    deflated_sharpe_ratio,
    hit_rate,
    make_trial_entry,
    max_drawdown,
    profit_factor,
    sharpe,
    sortino,
    turnover,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_equity(values, freq="1h", start="2020-01-01"):
    dates = pd.date_range(start, periods=len(values), freq=freq, tz="UTC")
    return pd.Series(values, index=dates, name="equity", dtype=float)


def _make_returns(values, freq="1h", start="2020-01-01"):
    dates = pd.date_range(start, periods=len(values), freq=freq, tz="UTC")
    return pd.Series(values, index=dates, name="returns", dtype=float)


def _dummy_backtest_result(
    equity: pd.Series,
    n_trades: int = 10,
    realized_pnl: float = 500.0,
    unrealized_pnl: float = 100.0,
    fees_paid: float = 50.0,
    slippage_paid: float = 20.0,
    funding_paid: float = 10.0,
) -> BacktestResult:
    """Create a minimal BacktestResult for testing evaluation functions."""
    n = len(equity)
    pnl = equity.diff().fillna(0.0)
    pnl.name = "pnl"

    if n_trades > 0:
        trade_pnls = [realized_pnl / n_trades] * n_trades
        trades = pd.DataFrame(
            {
                "entry_bar": pd.date_range("2020-01-01", periods=n_trades, freq="7D", tz="UTC"),
                "exit_bar": pd.date_range("2020-01-08", periods=n_trades, freq="7D", tz="UTC"),
                "direction": [1] * n_trades,
                "entry_price": [10_000.0] * n_trades,
                "exit_price": [10_000.0 + realized_pnl / n_trades] * n_trades,
                "gross_pnl": trade_pnls,
                "fees": [fees_paid / n_trades] * n_trades,
                "slippage": [slippage_paid / n_trades] * n_trades,
                "net_pnl": [(realized_pnl - fees_paid - slippage_paid) / n_trades] * n_trades,
            }
        )
    else:
        trades = pd.DataFrame(
            columns=[
                "entry_bar", "exit_bar", "direction", "entry_price",
                "exit_price", "gross_pnl", "fees", "slippage", "net_pnl"
            ]
        )

    return BacktestResult(
        equity_curve=equity,
        trades_df=trades,
        per_bar_pnl=pnl,
        realized_pnl=realized_pnl,
        unrealized_pnl=unrealized_pnl,
        fees_paid=fees_paid,
        slippage_paid=slippage_paid,
        funding_paid=funding_paid,
        skipped_bars=0,
        skipped_bar_timestamps=[],
        params={},
    )


# ---------------------------------------------------------------------------
# test_sharpe_sortino_calmar_known_values
# ---------------------------------------------------------------------------


def test_sharpe_known_value():
    """Sharpe on a constant positive return stream should be well-defined and positive."""
    # Daily constant return of 0.1% -> annualised Sharpe with std=0 -> 0 (degenerate)
    # Use a fixture with known non-zero std
    # returns: alternating +0.01 and -0.005 -> mean=0.0025, std ≈ 0.0075
    returns = _make_returns([0.01, -0.005] * 50, freq="1h")  # 100 bars
    sr = sharpe(returns, "1h")
    # mean = 0.0025, std_ddof1 ≈ 0.007505..., annualisation = sqrt(8760)
    expected_sr = (returns.mean() / returns.std(ddof=1)) * math.sqrt(8760)
    assert abs(sr - expected_sr) < 1e-9


def test_sortino_positive_returns():
    """Sortino ratio is higher than Sharpe when downside variance < total variance."""
    returns = _make_returns([0.02, -0.005, 0.03, -0.002, 0.025] * 20, freq="1d")
    sr = sharpe(returns, "1d")
    so = sortino(returns, "1d")
    # Sortino >= Sharpe when there are positive returns (downside std < total std)
    assert so >= sr


def test_calmar_positive_trend():
    """Calmar ratio should be positive for an equity curve with a small drawdown."""
    # Rising trend with one small dip so max_drawdown > 0
    vals = list(range(10_000, 10_500, 10)) + [10_480] + list(range(10_490, 10_600, 10))
    equity = _make_equity(vals, freq="1d")
    calmar_val = calmar(equity, "1d")
    assert calmar_val > 0


def test_max_drawdown_known():
    """Max drawdown on [100, 110, 90, 95] = (110-90)/110 ≈ 0.1818."""
    equity = _make_equity([100.0, 110.0, 90.0, 95.0], freq="1d")
    mdd, peak_ts, trough_ts = max_drawdown(equity)
    expected = (110.0 - 90.0) / 110.0
    assert abs(mdd - expected) < 1e-9
    assert peak_ts == equity.index[1]
    assert trough_ts == equity.index[2]


def test_max_drawdown_no_drawdown():
    """Monotonically rising equity has zero drawdown."""
    equity = _make_equity([100.0, 101.0, 102.0, 103.0], freq="1d")
    mdd, peak_ts, trough_ts = max_drawdown(equity)
    assert mdd == 0.0
    assert peak_ts is None
    assert trough_ts is None


def test_turnover_preserves_legacy_entry_price_behavior():
    equity = _make_equity([100.0, 100.0, 100.0])
    trades = pd.DataFrame({"entry_price": [100.0, 200.0]})

    assert turnover(trades, equity) == 6.0


def test_turnover_uses_trade_notional_when_present():
    equity = _make_equity([100.0, 100.0, 100.0])
    trades = pd.DataFrame(
        {
            "entry_price": [100.0, 200.0],
            "notional": [300.0, 700.0],
        }
    )

    assert turnover(trades, equity) == 10.0


def test_turnover_uses_entry_exit_notional_when_round_trip_notional_absent():
    equity = _make_equity([100.0, 100.0, 100.0])
    trades = pd.DataFrame(
        {
            "entry_price": [100.0, 200.0],
            "entry_notional": [100.0, 400.0],
            "exit_notional": [150.0, 450.0],
        }
    )

    assert turnover(trades, equity) == 11.0


# ---------------------------------------------------------------------------
# test_dsr_overfit_case
# ---------------------------------------------------------------------------


def test_dsr_overfit_case():
    """With 1000 trials and sharpe=1.2, DSR falls below 0.95 so Gate 2 FAILS.

    Gate 2 spec: "DSR > 1.0 at 95% CI" — stored threshold = 1.0 (Sharpe floor),
    pass condition = P(true Sharpe > 1.0) > 0.95.

    With 1000 trials, the expected max SR >> 1.2, so the DSR probability is
    well below 0.95. Gate 2 therefore FAILS.
    """
    dsr_val, sr_benchmark = deflated_sharpe_ratio(
        sharpe_hat=1.2,
        n_trials=1000,
        variance_of_trials=0.5,  # std = ~0.7 across trials
        skew=0.0,
        kurt=3.0,
        n_obs=1000,
    )
    # With 1000 trials, the expected max SR is well above 1.2, so DSR < 0.5
    assert dsr_val < 0.95, (
        f"Expected DSR < 0.95 for overfit case (1000 trials, SR=1.2), got {dsr_val:.4f}"
    )
    # The benchmark SR must be > 1.2 (what we need to beat to be real)
    assert sr_benchmark > 1.2, (
        f"Benchmark SR should exceed 1.2 with 1000 trials, got {sr_benchmark:.4f}"
    )


# ---------------------------------------------------------------------------
# test_promotion_gates_pass_and_fail
# ---------------------------------------------------------------------------


def _build_overfit_result() -> BacktestResult:
    """Build a BacktestResult designed to fail multiple promotion gates."""
    # Equity curve: low OOS Sharpe, high drawdown
    n = 500
    rng = np.random.default_rng(42)
    # Noisy walk with a big crash -> low Sharpe and high DD
    returns = rng.normal(0.0001, 0.02, n)
    returns[200:240] = -0.05  # 40-bar crash -> >20% DD
    equity_vals = 10_000.0 * np.cumprod(1 + np.concatenate([[0], returns]))
    equity = _make_equity(equity_vals[:n], freq="1h")
    pnl = equity.diff().fillna(0.0)
    pnl.name = "pnl"

    # Many expensive trades -> high cost drag
    n_trades = 50
    realized = float(equity.iloc[-1] - equity.iloc[0]) * 0.5
    fees = abs(realized) * 0.8  # cost > 50% of gross -> Gate 5 FAIL

    trades = pd.DataFrame(
        {
            "entry_bar": pd.date_range("2020-01-01", periods=n_trades, freq="3D", tz="UTC"),
            "exit_bar": pd.date_range("2020-01-04", periods=n_trades, freq="3D", tz="UTC"),
            "direction": [1] * n_trades,
            "entry_price": [10_000.0] * n_trades,
            "exit_price": [10_000.0 + realized / n_trades] * n_trades,
            "gross_pnl": [realized / n_trades] * n_trades,
            "fees": [fees / n_trades] * n_trades,
            "slippage": [0.0] * n_trades,
            "net_pnl": [(realized - fees) / n_trades] * n_trades,
        }
    )

    return BacktestResult(
        equity_curve=equity,
        trades_df=trades,
        per_bar_pnl=pnl,
        realized_pnl=realized,
        unrealized_pnl=0.0,
        fees_paid=fees,
        slippage_paid=0.0,
        funding_paid=0.0,
        skipped_bars=0,
        skipped_bar_timestamps=[],
        params={},
    )


def _build_passing_result() -> BacktestResult:
    """Build a BacktestResult designed to pass all eight promotion gates.

    Uses 6000 1h bars (~250 days) with tiny drift (0.01%/bar) and matching
    vol so that:
    - Gate 1 (OOS Sharpe): Sharpe ≈ 93 (drift/vol = 1, annualised * sqrt(8760))
    - Gate 3 (max DD): negligible (tiny vol vs positive drift)
    - Gate 6 (90-day window): total growth ≈ 82%, so last 90-day window
      captures ≈ 43% of total PnL — below the 60% threshold
    """
    # 6000 bars at 1h = 250 days — well above the 90-day gate window
    # Tiny drift/vol limits compounding so late bars don't dominate PnL
    n = 6000
    rng = np.random.default_rng(7)
    returns = rng.normal(0.0001, 0.0001, n)  # drift=0.01%/bar, vol=0.01%/bar
    equity_vals = 10_000.0 * np.cumprod(1 + np.concatenate([[0], returns]))
    equity = _make_equity(equity_vals[:n], freq="1h")
    pnl = equity.diff().fillna(0.0)
    pnl.name = "pnl"

    realized = float(equity.iloc[-1] - equity.iloc[0]) * 0.9
    fees = realized * 0.05  # 5% cost drag

    n_trades = 20
    trades = pd.DataFrame(
        {
            "entry_bar": pd.date_range("2020-01-01", periods=n_trades, freq="15D", tz="UTC"),
            "exit_bar": pd.date_range("2020-01-16", periods=n_trades, freq="15D", tz="UTC"),
            "direction": [1] * n_trades,
            "entry_price": [10_000.0] * n_trades,
            "exit_price": [10_050.0] * n_trades,
            "gross_pnl": [realized / n_trades] * n_trades,
            "fees": [fees / n_trades] * n_trades,
            "slippage": [0.0] * n_trades,
            "net_pnl": [(realized - fees) / n_trades] * n_trades,
        }
    )

    return BacktestResult(
        equity_curve=equity,
        trades_df=trades,
        per_bar_pnl=pnl,
        realized_pnl=realized,
        unrealized_pnl=0.0,
        fees_paid=fees,
        slippage_paid=0.0,
        funding_paid=0.0,
        skipped_bars=0,
        skipped_bar_timestamps=[],
        params={},
    )


def test_promotion_gates_pass_and_fail():
    """check_promotion_gates FAILS on overfit fixture, PASSES on clean fixture."""

    # ---- FAIL case ----
    bad = _build_overfit_result()
    bad_params = {
        "n_free_params": 10,          # Gate 7: > 5 -> FAIL
        "sensitivity_min_ratio": 0.3, # Gate 4: < 0.70 -> FAIL
        "is_sharpe": 2.0,             # IS Sharpe (used for WFE)
    }
    fail_report = check_promotion_gates(
        result=bad,
        trial_count=1000,  # large -> DSR Gate 2 likely FAIL
        params_meta=bad_params,
        freq="1h",
        variance_of_trials=0.5,
        skew=0.0,
        kurt=3.0,
    )

    assert isinstance(fail_report, GateReport)
    assert len(fail_report.gates) == 8

    # At least some gates must fail (overfit fixture)
    n_failed = sum(not g.passed for g in fail_report.gates)
    assert n_failed >= 3, (
        f"Expected >= 3 gate failures for overfit fixture, got {n_failed}"
    )
    assert not fail_report.overall_pass

    # Specific expected failures
    gate_map = {g.gate_id: g for g in fail_report.gates}
    assert not gate_map[7].passed, "Gate 7 (<=5 params) must FAIL with n_free_params=10"
    assert not gate_map[4].passed, "Gate 4 (sensitivity) must FAIL with ratio=0.3"

    # ---- PASS case ----
    good = _build_passing_result()
    good_params = {
        "n_free_params": 2,           # Gate 7: <= 5 -> PASS
        "sensitivity_min_ratio": 0.85, # Gate 4: >= 0.70 -> PASS
        "is_sharpe": None,            # will be computed from result itself
    }
    # Use is_result = good to compute WFE = 1.0 (IS == OOS)
    pass_report = check_promotion_gates(
        result=good,
        trial_count=1,   # only 1 trial -> DSR Gate 2 easier to pass
        params_meta=good_params,
        is_result=good,
        freq="1h",
        variance_of_trials=0.01,
        skew=0.0,
        kurt=3.0,
    )

    assert isinstance(pass_report, GateReport)
    assert len(pass_report.gates) == 8

    # The to_dict() method must produce well-formed JSON with all 8 gates
    d = pass_report.to_dict()
    assert d["overall_pass"] == pass_report.overall_pass
    assert len(d["gates"]) == 8
    for gate in d["gates"]:
        assert "gate_id" in gate
        assert "passed" in gate
        assert "value" in gate
        assert "threshold" in gate

    # Overall pass
    assert pass_report.overall_pass, (
        f"Clean fixture should pass all gates. Failed gates: "
        f"{[g.gate_name for g in pass_report.gates if not g.passed]}"
    )


# ---------------------------------------------------------------------------
# test_append_trial_roundtrip
# ---------------------------------------------------------------------------


def test_append_trial_roundtrip(tmp_path):
    """append_trial writes a valid TrialEntry; re-reading matches schema."""
    trial_log = tmp_path / "trial_log.jsonl"

    entry = make_trial_entry(
        hypothesis_id="H-001",
        config={"fast": 5, "slow": 20},
        dataset_ids=["binance_um_perp_BTCUSDT_1h"],
        params={"fast": 5, "slow": 20},
        in_sample_sharpe=1.5,
        oos_sharpe=1.2,
        max_dd=0.08,
        n_obs=5000,
        notes="test round-trip",
    )

    append_trial(trial_log, entry)

    # File must exist and contain exactly 1 line
    assert trial_log.exists()
    lines = trial_log.read_text().strip().splitlines()
    assert len(lines) == 1

    row = json.loads(lines[0])

    # Schema validation: all required fields must be present and correct type
    assert isinstance(row["trial_id"], str)
    assert len(row["trial_id"]) == 36  # uuid4
    assert isinstance(row["utc"], str)
    assert row["hypothesis_id"] == "H-001"
    assert isinstance(row["config_sha256"], str) and len(row["config_sha256"]) == 64
    assert isinstance(row["dataset_sha256"], str) and len(row["dataset_sha256"]) == 64
    assert isinstance(row["params"], dict)
    assert row["params"] == {"fast": 5, "slow": 20}
    assert row["in_sample_sharpe"] == 1.5
    assert row["oos_sharpe"] == 1.2
    assert row["max_drawdown"] == 0.08
    assert row["n_obs"] == 5000
    assert row["notes"] == "test round-trip"

    # Append a second entry, verify two lines
    entry2 = make_trial_entry(
        hypothesis_id="H-002",
        config={"fast": 10, "slow": 40},
        dataset_ids=["binance_um_perp_BTCUSDT_1h"],
        params={"fast": 10, "slow": 40},
        in_sample_sharpe=0.8,
        oos_sharpe=0.6,
        max_dd=0.15,
        n_obs=3000,
    )
    append_trial(trial_log, entry2)
    lines2 = trial_log.read_text().strip().splitlines()
    assert len(lines2) == 2
