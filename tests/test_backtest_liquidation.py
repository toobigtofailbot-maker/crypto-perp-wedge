"""
Regression tests for WP-5b F-001 liquidation / bounded-equity semantics.
"""

import json
from pathlib import Path

import pandas as pd
import pytest

from lib.backtest import run_backtest
from lib.evaluation import max_drawdown


def _make_ohlcv(closes, freq="1h", start="2020-01-01"):
    dates = pd.date_range(start, periods=len(closes), freq=freq, tz="UTC")
    opens = [closes[0]] + list(closes[:-1])
    return pd.DataFrame(
        {
            "open": opens,
            "high": [max(o, c) for o, c in zip(opens, closes)],
            "low": [min(o, c) for o, c in zip(opens, closes)],
            "close": closes,
            "volume": [1_000.0] * len(closes),
        },
        index=dates,
    )


def _empty_funding():
    return pd.DataFrame(
        {"funding_rate": []},
        index=pd.DatetimeIndex([], tz="UTC"),
    )


def _no_gaps_path(tmp_path: Path) -> Path:
    p = tmp_path / "gaps.json"
    p.write_text(json.dumps({"schema_version": 1, "entries": []}))
    return p


def _run(signal, ohlcv, tmp_path, initial_equity=10_000.0, **kwargs):
    return run_backtest(
        signal=signal,
        ohlcv=ohlcv,
        funding=_empty_funding(),
        fee_bps_taker=0.0,
        fee_bps_maker=0.0,
        slippage_bps=0.0,
        initial_equity=initial_equity,
        stream="klines",
        interval="1h",
        gaps_path=_no_gaps_path(tmp_path),
        **kwargs,
    )


def test_normal_path_always_flat(tmp_path):
    ohlcv = _make_ohlcv([100.0, 120.0, 80.0, 140.0, 90.0])
    signal = pd.Series(0.0, index=ohlcv.index)

    result = _run(signal, ohlcv, tmp_path)

    assert result.equity_curve.tolist() == [10_000.0] * len(ohlcv)
    assert result.per_bar_pnl.tolist() == [0.0] * len(ohlcv)
    assert result.trades_df.empty
    assert result.realized_pnl == 0.0
    assert result.unrealized_pnl == 0.0
    assert result.liquidated is False
    assert result.liquidation_timestamp is None


def test_default_liquidation_assumptions_recorded_without_outcome_effect(tmp_path):
    ohlcv = _make_ohlcv([100.0, 120.0, 80.0, 140.0, 90.0])
    signal = pd.Series(0.0, index=ohlcv.index)

    implicit_default = _run(signal, ohlcv, tmp_path)
    explicit_default = _run(
        signal,
        ohlcv,
        tmp_path,
        liquidation_mode="zero_equity",
        maintenance_margin_rate=None,
        mark_price_source="close",
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
    assert implicit_default.realized_pnl == explicit_default.realized_pnl == 0.0
    assert implicit_default.unrealized_pnl == explicit_default.unrealized_pnl == 0.0
    assert implicit_default.fees_paid == explicit_default.fees_paid == 0.0
    assert implicit_default.slippage_paid == explicit_default.slippage_paid == 0.0
    assert implicit_default.funding_paid == explicit_default.funding_paid == 0.0
    assert implicit_default.liquidated == explicit_default.liquidated is False
    assert implicit_default.liquidation_timestamp == explicit_default.liquidation_timestamp
    assert implicit_default.params["liquidation_mode"] == "zero_equity"
    assert implicit_default.params["maintenance_margin_rate"] is None
    assert implicit_default.params["mark_price_source"] == "close"
    assert implicit_default.params["bar_path_assumption"] == "next_open_close_mark"


def test_buy_and_hold_unchanged_on_benign_window():
    data_root = Path("data/processed")
    ohlcv_path = (
        data_root
        / "binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet"
    )
    df = pd.read_parquet(ohlcv_path).copy()
    df.index = pd.to_datetime(df["close_time_ms"].astype("int64"), unit="ms", utc=True)
    ohlcv = df[["open", "high", "low", "close", "volume"]].astype(float).sort_index()
    funding = pd.DataFrame(
        {"funding_rate": []},
        index=pd.DatetimeIndex([], tz="UTC"),
    )
    signal = pd.Series(1.0, index=ohlcv.index)

    result = run_backtest(
        signal=signal,
        ohlcv=ohlcv,
        funding=funding,
        fee_bps_taker=4.0,
        fee_bps_maker=2.0,
        slippage_bps=2.0,
        initial_equity=10_000.0,
        stream="klines",
        interval="4h",
        gaps_path=Path("data/irreparable_gaps.json"),
    )
    dd, _, _ = max_drawdown(result.equity_curve)

    assert abs(float(result.equity_curve.iloc[-1]) - 75_787.26692) < 1e-9
    assert len(result.trades_df) == 0
    assert abs(dd - 0.7408575150756737) < 1e-12
    assert result.liquidated is False
    assert result.liquidation_timestamp is None


def test_liquidation_on_catastrophic_short(tmp_path):
    ohlcv = _make_ohlcv([100.0, 100.0, 20_000.0, 21_000.0, 22_000.0])
    signal = pd.Series([0.0, -1.0, -1.0, 1.0, 1.0], index=ohlcv.index)

    result = _run(signal, ohlcv, tmp_path)
    dd, _, _ = max_drawdown(result.equity_curve)

    assert result.liquidated is True
    assert result.liquidation_timestamp == ohlcv.index[2]
    assert float(result.equity_curve.iloc[-1]) == 0.0
    assert float(result.equity_curve.min()) >= 0.0
    assert dd <= 1.0
    assert not result.trades_df.empty
    assert not (result.trades_df["entry_bar"] > result.liquidation_timestamp).any()
    assert not (result.trades_df["exit_bar"] > result.liquidation_timestamp).any()


def test_explicit_zero_equity_liquidation_preserves_default_catastrophic_path(tmp_path):
    ohlcv = _make_ohlcv([100.0, 100.0, 20_000.0, 21_000.0, 22_000.0])
    signal = pd.Series([0.0, -1.0, -1.0, 1.0, 1.0], index=ohlcv.index)

    implicit_default = _run(signal, ohlcv, tmp_path)
    explicit_default = _run(
        signal,
        ohlcv,
        tmp_path,
        liquidation_mode="zero_equity",
        maintenance_margin_rate=None,
        mark_price_source="close",
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
    assert implicit_default.liquidated == explicit_default.liquidated is True
    assert implicit_default.liquidation_timestamp == explicit_default.liquidation_timestamp
    assert implicit_default.fees_paid == explicit_default.fees_paid == 0.0
    assert implicit_default.slippage_paid == explicit_default.slippage_paid == 0.0
    assert implicit_default.funding_paid == explicit_default.funding_paid == 0.0
    assert implicit_default.realized_pnl == explicit_default.realized_pnl
    assert implicit_default.unrealized_pnl == explicit_default.unrealized_pnl


@pytest.mark.parametrize(
    "kwargs,match",
    [
        ({"liquidation_mode": "exchange"}, "liquidation_mode"),
        ({"mark_price_source": "mark"}, "mark_price_source"),
        ({"maintenance_margin_rate": 0.0}, "maintenance_margin_rate"),
        ({"maintenance_margin_rate": -0.01}, "maintenance_margin_rate"),
        ({"maintenance_margin_rate": 1.0}, "maintenance_margin_rate"),
        (
            {"liquidation_mode": "maintenance_margin"},
            "maintenance_margin_rate",
        ),
    ],
)
def test_invalid_liquidation_assumptions_raise(tmp_path, kwargs, match):
    ohlcv = _make_ohlcv([100.0, 100.0, 200.0])
    signal = pd.Series([0.0, -1.0, -1.0], index=ohlcv.index)

    with pytest.raises(ValueError, match=match):
        _run(signal, ohlcv, tmp_path, **kwargs)


def test_maintenance_margin_liquidation_triggers_before_zero_equity(tmp_path):
    ohlcv = _make_ohlcv([100.0, 100.0, 9_900.0, 20_000.0, 21_000.0])
    signal = pd.Series([0.0, -1.0, -1.0, -1.0, -1.0], index=ohlcv.index)

    zero_equity = _run(signal, ohlcv, tmp_path)
    maintenance_margin = _run(
        signal,
        ohlcv,
        tmp_path,
        liquidation_mode="maintenance_margin",
        maintenance_margin_rate=0.05,
    )
    dd, _, _ = max_drawdown(maintenance_margin.equity_curve)

    assert zero_equity.liquidated is True
    assert zero_equity.liquidation_timestamp == ohlcv.index[3]
    assert maintenance_margin.liquidated is True
    assert maintenance_margin.liquidation_timestamp == ohlcv.index[2]
    assert maintenance_margin.liquidation_timestamp < zero_equity.liquidation_timestamp
    assert float(maintenance_margin.equity_curve.iloc[-1]) == 0.0
    assert float(maintenance_margin.equity_curve.min()) >= 0.0
    assert (maintenance_margin.equity_curve.iloc[2:] == 0.0).all()
    assert (maintenance_margin.per_bar_pnl.iloc[3:] == 0.0).all()
    assert dd <= 1.0

    trade = maintenance_margin.trades_df.iloc[-1]
    assert trade["liquidation_mode"] == "maintenance_margin"
    assert abs(trade["maintenance_margin"] - 495.0) < 1e-12
    assert trade["mark_price_source"] == "close"
    assert trade["mark_price"] == 9_900.0
    assert maintenance_margin.params["liquidation_mode"] == "maintenance_margin"
    assert maintenance_margin.params["maintenance_margin_rate"] == 0.05
    assert maintenance_margin.params["mark_price_source"] == "close"


def test_maintenance_margin_preserves_adjacent_assumption_params(tmp_path):
    ohlcv = _make_ohlcv([100.0, 100.0, 9_900.0, 20_000.0])
    signal = pd.Series([0.0, -1.0, -1.0, -1.0], index=ohlcv.index)

    result = _run(
        signal,
        ohlcv,
        tmp_path,
        liquidation_mode="maintenance_margin",
        maintenance_margin_rate=0.05,
        funding_notional_mode="entry_price",
        order_size=1.0,
        fill_mode="complete",
        liquidity_cap_fraction=None,
        slippage_model="fixed_bps",
    )

    assert result.params["entry_fee_side"] == "taker"
    assert result.params["exit_fee_side"] == "taker"
    assert result.params["funding_notional_mode"] == "entry_price"
    assert result.params["order_size"] == 1.0
    assert result.params["fill_mode"] == "complete"
    assert result.params["liquidity_cap_fraction"] is None
    assert result.params["slippage_model"] == "fixed_bps"
    assert result.params["bar_path_assumption"] == "next_open_close_mark"


def test_liquidation_idempotent_after_trigger(tmp_path):
    ohlcv = _make_ohlcv([100.0, 100.0, 20_000.0, 10.0, 30_000.0, 50.0])
    signal = pd.Series([0.0, -1.0, 1.0, -1.0, 1.0, -1.0], index=ohlcv.index)

    result = _run(signal, ohlcv, tmp_path)
    liq_idx = ohlcv.index.get_loc(result.liquidation_timestamp)

    assert result.liquidated is True
    assert result.trades_df["entry_bar"].max() <= result.liquidation_timestamp
    assert (result.equity_curve.iloc[liq_idx:] == 0.0).all()
    assert (result.per_bar_pnl.iloc[liq_idx + 1:] == 0.0).all()


def test_drawdown_bounded_under_previously_unbounded_scenario(tmp_path):
    equity = pd.Series(
        [10_000.0, 11_000.0, 12_000.0, 5_000.0, -10_000.0, -40_000.0],
        index=pd.date_range("2020-01-01", periods=6, freq="4h", tz="UTC"),
    )
    pre_fix_dd, _, _ = max_drawdown(equity)
    assert pre_fix_dd > 1.0

    ohlcv = _make_ohlcv([100.0, 100.0, 20_000.0, 30_000.0, 40_000.0])
    signal = pd.Series([0.0, -1.0, -1.0, -1.0, -1.0], index=ohlcv.index)
    result = _run(signal, ohlcv, tmp_path)
    post_fix_dd, _, _ = max_drawdown(result.equity_curve)

    assert result.liquidated is True
    assert post_fix_dd <= 1.0
    assert float(result.equity_curve.min()) >= 0.0
