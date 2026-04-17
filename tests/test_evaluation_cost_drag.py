"""
Regression tests for WP-5b F-002 Gate 5 cost-drag pass/fail semantics.
"""

import pandas as pd

from lib.backtest import BacktestResult
from lib.evaluation import check_promotion_gates


def _equity():
    index = pd.date_range("2020-01-01", periods=8, freq="1h", tz="UTC")
    values = [10_000.0, 10_010.0, 10_020.0, 10_030.0, 10_040.0, 10_050.0, 10_060.0, 10_070.0]
    return pd.Series(values, index=index, name="equity")


def _result(*, gross_pnl, total_cost):
    equity = _equity()
    return BacktestResult(
        equity_curve=equity,
        trades_df=pd.DataFrame(
            columns=[
                "entry_bar",
                "exit_bar",
                "direction",
                "entry_price",
                "exit_price",
                "gross_pnl",
                "fees",
                "slippage",
                "net_pnl",
            ]
        ),
        per_bar_pnl=equity.diff().fillna(0.0).rename("pnl"),
        realized_pnl=float(gross_pnl),
        unrealized_pnl=0.0,
        fees_paid=float(total_cost),
        slippage_paid=0.0,
        funding_paid=0.0,
        skipped_bars=0,
        skipped_bar_timestamps=[],
        params={},
    )


def _gate_5(result):
    report = check_promotion_gates(
        result=result,
        trial_count=1,
        params_meta={"n_free_params": 1, "sensitivity_min_ratio": 1.0, "is_sharpe": 1.0},
        freq="1h",
    )
    return {gate.gate_id: gate for gate in report.gates}[5]


def test_gate_5_positive_gross_pnl_low_drag():
    gate = _gate_5(_result(gross_pnl=1_000.0, total_cost=100.0))

    assert gate.passed is True
    assert gate.value == 0.1
    assert gate.threshold == 0.50


def test_gate_5_positive_gross_pnl_high_drag():
    gate = _gate_5(_result(gross_pnl=1_000.0, total_cost=600.0))

    assert gate.passed is False
    assert gate.value == 0.6
    assert gate.threshold == 0.50


def test_gate_5_positive_gross_pnl_at_threshold():
    gate = _gate_5(_result(gross_pnl=1_000.0, total_cost=500.0))

    assert gate.passed is True
    assert gate.value == 0.5


def test_gate_5_zero_gross_pnl_fails():
    gate = _gate_5(_result(gross_pnl=0.0, total_cost=0.0))

    assert gate.passed is False
    assert gate.value == 0.0
    assert "gross_pnl=0" in gate.note


def test_gate_5_negative_gross_pnl_fails():
    gate = _gate_5(_result(gross_pnl=-1_000.0, total_cost=100.0))

    assert gate.passed is False
    assert gate.value == -0.1
    assert "gross_pnl=-1000.00" in gate.note


def test_gate_5_reported_value_scale_preserved():
    gross_pnl = 2_000.0
    total_cost = 250.0
    expected_fraction = total_cost / gross_pnl

    gate = _gate_5(_result(gross_pnl=gross_pnl, total_cost=total_cost))

    assert gate.value == round(expected_fraction, 4)
    assert gate.value == 0.125
    assert gate.threshold == 0.50
