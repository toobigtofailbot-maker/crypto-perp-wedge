"""
Regression tests for WP-5b F-001 liquidation / bounded-equity semantics.
"""

import json
from pathlib import Path

import pandas as pd

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


def _run(signal, ohlcv, tmp_path, initial_equity=10_000.0):
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
