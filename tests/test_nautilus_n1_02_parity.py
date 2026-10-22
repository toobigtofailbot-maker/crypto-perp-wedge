"""Physical N1-02 probes: no CANON output or promotion authority.

Run separately from import-isolation unit tests, in pinned Python 3.12.
All observations are repeated and emitted as JSON with pytest -s.
"""
from __future__ import annotations

import inspect
import json
from decimal import Decimal, ROUND_DOWN
from pathlib import Path

import pandas as pd
import pytest

nautilus_trader = pytest.importorskip("nautilus_trader", reason="pinned N1 proof environment required")

from lib.backtest import run_backtest
from tools.nautilus_adapter import research

D = Decimal


def _frame(prices=(100.,) * 6):
    index = pd.date_range("2026-01-01", periods=len(prices), freq="15min", tz="UTC")
    return pd.DataFrame(
        {**{key: list(prices) for key in ("open", "high", "low", "close")},
         "volume": [1000.] * len(prices),
         "close_time_ms": [int(t.value // 1_000_000) + 899999 for t in index]},
        index=index,
    )


def _signal(frame, values):
    return pd.Series(values, index=frame.index)


def _probe(scenario, frame, values, quantity=D("1")):
    signal = _signal(frame, values)
    first = research._execute_n1_02_probe(scenario, frame, signal, requested_quantity=quantity)
    second = research._execute_n1_02_probe(scenario, frame, signal, requested_quantity=quantity)
    assert first == second
    assert first["engine_version"] == "1.231.0" == nautilus_trader.__version__
    assert first["non_authoritative"] is True
    assert "scientific_result" not in first
    assert all(status == "FILLED" for status in first["order_statuses"])
    assert first["orders"] == len(first["fills"])
    fixture = {
        "prices": frame[["open", "high", "low", "close"]].values.tolist(),
        "open_times_ns": [int(t.value) for t in frame.index],
        "signal": values,
        "requested_quantity": str(quantity),
    }
    print(json.dumps({
        "fixture_sha256": research.content_sha256(fixture),
        "fixture": fixture,
        "observed": first,
    }, sort_keys=True))
    return first


def _cpw(tmp_path, frame, values, quantity=1., fee=0., slip=0., funding=None, **kwargs):
    gaps = tmp_path / "gaps.json"
    gaps.write_text(json.dumps({"schema_version": 1, "entries": []}))
    if funding is None:
        funding = pd.DataFrame({"funding_rate": []}, index=pd.DatetimeIndex([], tz="UTC"))
    result = run_backtest(
        signal=_signal(frame, values), ohlcv=frame, funding=funding,
        fee_bps_taker=fee, fee_bps_maker=fee, slippage_bps=slip,
        initial_equity=10000., stream="klines", interval="15m",
        gaps_path=gaps, order_size=quantity, **kwargs,
    )
    print(json.dumps({"cpw_reference": {
        "quantity": quantity, "signal": values,
        "open_prices": frame["open"].tolist(),
        "final_equity": float(result.equity_curve.iloc[-1]),
        "fees_paid": result.fees_paid, "slippage_paid": result.slippage_paid,
        "funding_paid": result.funding_paid, "liquidated": result.liquidated,
    }}, sort_keys=True))
    return result


def _equity(observed):
    return D(observed["balance"]) + D(observed["unrealized_pnl"])


@pytest.mark.parametrize("side", [1, -1])
def test_real_fee_and_adverse_execution_split(tmp_path, side):
    frame = _frame()
    values = [side, side, 0, 0, 0, 0]
    observed = _probe("costs", frame, values)
    fills = observed["fills"]
    assert [D(f["price"]) for f in fills] == (
        [D("100.01"), D("99.99")] if side == 1 else [D("99.99"), D("100.01")]
    )
    assert sum(D(f["commission"]) for f in fills) == D(observed["commission"]) == D(".08")
    slippage = sum(abs(D(f["price"]) - D("100")) * D(f["quantity"]) for f in fills)
    assert slippage == D(".02")
    assert _equity(observed) == D("9999.90")
    cpw = _cpw(tmp_path, frame, values, fee=4., slip=1.)
    assert cpw.fees_paid == pytest.approx(.08, rel=0, abs=1e-12)
    assert cpw.slippage_paid == pytest.approx(.02, rel=0, abs=1e-12)
    assert float(_equity(observed)) == pytest.approx(cpw.equity_curve.iloc[-1], rel=0, abs=1e-9)


def test_fee_basis_native_difference_is_not_allocated_parity(tmp_path):
    # CPW charges fees at the reference open; Nautilus uses the actual fill.
    frame = _frame([100., 100., 100., 200., 200., 200.])
    values = [1, 1, 0, 0, 0, 0]
    observed = _probe("costs", frame, values)
    cpw = _cpw(tmp_path, frame, values, fee=4., slip=1.)
    assert D(observed["commission"]) == D(".119996")
    assert cpw.fees_paid == pytest.approx(.12, rel=0, abs=1e-12)
    assert float(_equity(observed)) - cpw.equity_curve.iloc[-1] == pytest.approx(.000004, rel=0, abs=1e-9)
    assert D(observed["fills"][0]["commission"]) == D(".040004")


@pytest.mark.parametrize("dp", [2, 3, 6, 8])
@pytest.mark.parametrize("requested", ["1.234567895", "0.00000001"])
def test_precision_quantum_minimum_and_exact_notional(tmp_path, dp, requested):
    frame = _frame()
    quantum = D(1).scaleb(-dp)
    quantity = D(requested).quantize(quantum, rounding=ROUND_DOWN)
    if quantity < quantum:
        with pytest.raises(research.NautilusAdapterError, match="below minimum"):
            research._execute_n1_02_probe(
                f"precision_{dp}", frame, _signal(frame, [1, 1, 0, 0, 0, 0]),
                requested_quantity=D(requested),
            )
        return
    frame = _frame([100., 100., 110., 120., 120., 120.])
    observed = _probe(f"precision_{dp}", frame, [1, 1, 0, 0, 0, 0], D(requested))
    assert [D(f["quantity"]) for f in observed["fills"]] == [quantity, quantity]
    assert [D(f["price"]) * D(f["quantity"]) for f in observed["fills"]] == [100 * quantity, 120 * quantity]
    cpw = _cpw(tmp_path, frame, [1, 1, 0, 0, 0, 0], quantity=float(quantity))
    # Native settlement currency has six decimals; fill quantities remain exact.
    assert float(_equity(observed)) == pytest.approx(cpw.equity_curve.iloc[-1], rel=0, abs=1e-6)
    assert cpw.equity_curve.iloc[-1] == pytest.approx(10000 + float(20 * quantity), rel=0, abs=1e-9)


@pytest.mark.parametrize("dp", [2, 3, 6, 8])
def test_exact_minimum_step_is_filled(dp):
    quantum = D(1).scaleb(-dp)
    observed = _probe(f"precision_{dp}", _frame(), [1, 1, 0, 0, 0, 0], quantum)
    assert [D(f["quantity"]) for f in observed["fills"]] == [quantum, quantum]


@pytest.mark.parametrize("side", [1, -1])
def test_direct_and_repeated_reversals_use_native_netting(tmp_path, side):
    frame = _frame([100., 100., 110., 90., 95., 95.])
    values = [side, -side, side, 0, 0, 0]
    observed = _probe("flip", frame, values)
    assert [D(f["quantity"]) for f in observed["fills"]] == [D(1), D(2), D(2), D(1)]
    assert [f["side"] for f in observed["fills"]] == (
        ["BUY", "SELL", "BUY", "SELL"] if side == 1 else ["SELL", "BUY", "SELL", "BUY"]
    )
    assert [f["ts_event_ns"] for f in observed["fills"]] == [
        int(frame.index[i].value) + 1 for i in range(1, 5)
    ]
    events = observed["position_events"]
    assert [e["type"] for e in events] == ["PositionOpened", "PositionClosed"] * 3
    assert [e["side"] for e in events if e["type"] == "PositionOpened"] == (
        ["LONG", "SHORT", "LONG"] if side == 1 else ["SHORT", "LONG", "SHORT"]
    )
    assert all(D(e["quantity"]) == 0 for e in events if e["type"] == "PositionClosed")
    cpw = _cpw(tmp_path, frame, values, fee=4.)
    assert len(cpw.trades_df) == 3
    assert float(_equity(observed)) == pytest.approx(cpw.equity_curve.iloc[-1], rel=0, abs=1e-9)
    assert float(observed["commission"]) == pytest.approx(cpw.fees_paid, rel=0, abs=1e-12)
    assert observed["open_position_count"] == 0
    assert sum(D(e["realized_pnl"]) for e in events if e["type"] == "PositionClosed") == (
        _equity(observed) - D(10000)
    )


def test_unchanged_target_does_not_duplicate_orders_and_has_no_lookahead():
    frame = _frame()
    values = [1, 1, 1, 1, 1, 1]
    first = _probe("flip", frame, values)
    changed = frame.copy()
    changed.loc[changed.index[3]:, ["open", "high", "low", "close"]] = 200.
    later = _probe("flip", changed, values)
    assert first["fills"] == later["fills"]
    assert first["orders"] == 1
    # Final-bar signal cannot create an unfillable future order.
    terminal = _probe("flip", frame, [0, 0, 0, 0, 0, 1])
    assert terminal["orders"] == 0


@pytest.mark.parametrize("side", [1, -1])
@pytest.mark.parametrize("rate", [".01", "-.01"])
def test_signed_funding_delivered_without_native_settlement(tmp_path, side, rate):
    frame = _frame()
    values = [side, side, 0, 0, 0, 0]
    observed = _probe("funding_positive" if D(rate) > 0 else "funding_negative", frame, values)
    updates = observed["funding_updates"]
    assert [u["ts_event_ns"] for u in updates] == [int(frame.index[i].value) for i in (0, 2, 5)]
    assert [D(u["net_quantity"]) for u in updates] == [0, side, 0]
    assert [D(u["rate"]) for u in updates] == [D(rate)] * 3
    assert [D(u["balance"]) for u in updates] == [10000] * 3
    funding = pd.DataFrame({"funding_rate": [float(rate)] * 3}, index=frame.index[[0, 2, 5]])
    cpw = _cpw(tmp_path, frame, values, funding=funding, funding_cost_mode="on")
    assert cpw.funding_paid == pytest.approx(side * float(rate) * 100, rel=0, abs=1e-12)
    assert _equity(observed) == D(10000)
    assert cpw.equity_curve.iloc[-1] == pytest.approx(10000 - side * float(rate) * 100, rel=0, abs=1e-9)


@pytest.mark.parametrize("last_price", [200., 250.])
def test_zero_and_negative_equity_do_not_force_native_liquidation(tmp_path, last_price):
    frame = _frame([100., 100., last_price, last_price, last_price, last_price])
    observed = _probe("zero_equity", frame, [-1] * 6, D(100))
    assert _equity(observed) == D(10000) - (D(str(last_price)) - 100) * 100 <= 0
    assert observed["open_position_count"] == observed["orders"] == 1
    assert [e["type"] for e in observed["position_events"]] == ["PositionOpened"]
    cpw = _cpw(tmp_path, frame, [-1] * 6, quantity=100.)
    assert cpw.liquidated is True
    assert cpw.liquidation_timestamp == frame.index[2]
    assert cpw.equity_curve.iloc[-1] == 0


def test_margin_calculation_and_missing_enforcement_are_separate(tmp_path):
    frame = _frame([100., 100., 195., 195., 195., 195.])
    observed = _probe("maintenance", frame, [-1] * 6, D(100))
    assert _equity(observed) == D(500)
    assert D(observed["margin_at_close"]) == D(975)  # native calculator, 195 * 100 * .05
    assert D(observed["margin_maint"]) == D(500)  # stored entry-price accounting
    assert _equity(observed) <= D(observed["margin_at_close"])
    assert observed["open_position_count"] == observed["orders"] == 1
    assert [e["type"] for e in observed["position_events"]] == ["PositionOpened"]
    cpw = _cpw(tmp_path, frame, [-1] * 6, quantity=100.,
               liquidation_mode="maintenance_margin", maintenance_margin_rate=.05)
    assert cpw.liquidated is True
    assert cpw.liquidation_timestamp == frame.index[2]
    assert cpw.trades_df.iloc[-1]["maintenance_margin"] == 975.
    assert cpw.equity_curve.iloc[-1] == 0


def test_installed_margin_bypass_and_absent_native_liquidation_route():
    from nautilus_trader.backtest.engine import BacktestEngine

    root = Path(nautilus_trader.__file__).parent
    risk = (root / "risk/engine.pyx").read_text()
    manager = (root / "accounting/manager.pyx").read_text()
    assert "return True  # TODO: Determine risk controls for margin" in risk
    assert "# if new_free < 0:" in manager
    assert "liquidation_enabled" not in inspect.signature(BacktestEngine.add_venue).parameters


@pytest.mark.parametrize("quantity", [D(0), D("-1"), D("NaN"), D("Infinity"), D("1000001"), 1.])
def test_malformed_probe_quantity_fails_closed(quantity):
    with pytest.raises(research.NautilusAdapterError, match="invalid probe quantity"):
        research._execute_n1_02_probe(
            "flip", _frame(), _signal(_frame(), [1] * 6), requested_quantity=quantity,
        )


@pytest.mark.parametrize("bad", ["scenario", "signal", "index", "price", "tick", "close_time"])
def test_malformed_probe_inputs_fail_closed(bad):
    frame = _frame()
    signal = _signal(frame, [1] * 6)
    scenario = "flip"
    if bad == "scenario":
        scenario = "arbitrary_engine"
    elif bad == "signal":
        signal.iloc[0] = 2
    elif bad == "index":
        signal.index = signal.index + pd.Timedelta(minutes=1)
    elif bad == "price":
        frame.iloc[0, frame.columns.get_loc("open")] = float("nan")
    elif bad == "tick":
        frame.iloc[0, frame.columns.get_loc("open")] = 100.001
    elif bad == "close_time":
        frame.iloc[0, frame.columns.get_loc("close_time_ms")] += 1
    with pytest.raises(research.NautilusAdapterError):
        research._execute_n1_02_probe(scenario, frame, signal)


def test_legacy_flip_and_cost_meaning_stays_frozen():
    frame = _frame()
    signal = _signal(frame, [1, -1, 1, -1, -1, -1])
    observed = research._execute_target_signals(
        [{"variant_id": "legacy", "parameter_values": {}}],
        frame, {"legacy": signal},
    )["legacy"]
    assert observed["total_orders"] == observed["open_position_count"] == 1
    assert observed["fills"][0]["quantity"] == 100.
    assert observed["fills"][0]["price"] == 100.
    assert observed["combined_fee_slippage_cost"] == 5.
    assert observed["allocated_fees"] == 4.
    assert observed["allocated_slippage"] == 1.
    assert observed["funding"] == 0.
