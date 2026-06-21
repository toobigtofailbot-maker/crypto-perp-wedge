from __future__ import annotations

import inspect
import json
import math
from pathlib import Path

import pandas as pd
import pytest

from tools.research_runner import spec_signal_compiler as compiler
from tools.research_runner.spec_signal_compiler import (
    SpecSignalCompilerError,
    UnsupportedSpecSignalCompilerFeature,
    compile_signal,
)


def _ohlcv() -> pd.DataFrame:
    index = pd.date_range("2026-01-01", periods=8, freq="h", tz="UTC")
    close = [10.0, 11.0, 12.0, 11.0, 13.0, 14.0, 12.0, 15.0]
    return pd.DataFrame(
        {
            "open": [value - 0.25 for value in close],
            "high": [value + 1.0 for value in close],
            "low": [value - 1.0 for value in close],
            "close": close,
            "volume": [1000.0] * len(index),
        },
        index=index,
    )


def _funding(index: pd.DatetimeIndex) -> pd.DataFrame:
    return pd.DataFrame({"funding_rate": [0.0, 0.0]}, index=index[::4][:2])


def _operand(operand_type: str, ref, field=None, lookback=None) -> dict:
    return {
        "operand_type": operand_type,
        "ref": ref,
        "field": field,
        "timeframe": None,
        "lookback": lookback,
    }


def _primitive_ref(ref: str, field: str) -> dict:
    return {
        "operand_type": "primitive_ref",
        "ref": ref,
        "field": field,
        "timeframe": None,
        "lookback": None,
    }


def _online_primitives(*, retest_max: int = 3, tolerance_multiple: float = 0.0) -> dict:
    tolerance = {
        "mode": "atr_multiple",
        "atr_lookback_bars": 1,
        "multiple": tolerance_multiple,
        "units": "ATR",
    }
    return {
        "session_windows": [
            {
                "session_id": "UTC_DAILY_0000",
                "timezone": "UTC",
                "anchor_time": "00:00",
                "duration": {"value": 1, "units": "day"},
            }
        ],
        "opening_ranges": [
            {
                "range_id": "OR-1",
                "session_ref": "UTC_DAILY_0000",
                "start_offset": {"value": 0, "units": "bars"},
                "length": {"value": 1, "units": "bars"},
                "high_source": "high",
                "low_source": "low",
                "close_after_range_required": True,
                "zero_range_policy": "no_trade_false",
                "incomplete_range_policy": "no_trade_false",
            }
        ],
        "opening_range_breakouts": [
            {
                "breakout_id": "ORB-1",
                "range_ref": "OR-1",
                "confirmation_price": "close",
                "confirmation_timing": "bar_close",
                "entry_timing": "next_bar_open",
                "long_operator": "close_gt_range_high_plus_tolerance",
                "short_operator": "close_lt_range_low_minus_tolerance",
                "tolerance": tolerance,
                "breakout_before_range_complete_policy": "false",
                "simultaneous_long_short_policy": "no_trade",
            }
        ],
        "opening_range_retests": [
            {
                "retest_id": "RETEST-1",
                "breakout_ref": "ORB-1",
                "window": {"min_bars_after_breakout": 1, "max_bars_after_breakout": retest_max},
                "touch_price_source": "close",
                "entry_timing": "next_bar_open_after_retest_confirmation",
                "long_retest_level": "opening_range.high",
                "short_retest_level": "opening_range.low",
                "tolerance": tolerance,
                "timeout_policy": "no_trade_false",
                "opposite_breakout_before_retest_policy": "cancel_session_signal",
            }
        ],
        "candle_shapes": [
            {
                "predicate_id": "NO-WICK",
                "range_source": "high_low",
                "zero_range_policy": "false",
                "missing_ohlc_policy": "false",
                "upper_wick_pct": {"operator": "lte", "value": 0.1, "units": "fraction_of_range"},
                "lower_wick_pct": {"operator": "lte", "value": 0.1, "units": "fraction_of_range"},
                "body_pct": {"operator": "gte", "value": 0.6, "units": "fraction_of_range"},
                "side_mode": "side_specific",
            }
        ],
    }


def _composed_operand(
    *,
    base_operand: dict | None = None,
    parameter_operand: dict | None = None,
    composition_type: str = "scale_by_one_minus_parameter",
) -> dict:
    return {
        "operand_type": "composed_operand",
        "composition_type": composition_type,
        "base_operand": base_operand
        if base_operand is not None
        else _operand("indicator_ref", "sma", "value", {"bars": 20}),
        "parameter_operand": parameter_operand
        if parameter_operand is not None
        else _operand("parameter_ref", "entry_distance_threshold"),
    }


def _z_score_operand(
    *,
    value_operand: dict | None = None,
    center_operand: dict | None = None,
    scale_operand: dict | None = None,
    zero_scale_policy: str = "null_output",
) -> dict:
    return {
        "operand_type": "composed_operand",
        "composition_type": "z_score",
        "value_operand": value_operand
        if value_operand is not None
        else _operand("data_ref", "close", "close"),
        "center_operand": center_operand
        if center_operand is not None
        else _operand("indicator_ref", "sma", "value", {"bars": 3}),
        "scale_operand": scale_operand
        if scale_operand is not None
        else _operand("indicator_ref", "stddev", "value", {"bars": 3}),
        "zero_scale_policy": zero_scale_policy,
    }


def _atr_stop(
    *,
    atr_lookback: int | float = 1,
    atr_multiplier: int | float = 1.0,
    entry_reference_price: str = "next_bar_open_pre_fee_slippage",
    evaluation_price: str = "close",
    evaluation_timing: str = "bar_close",
    enabled: bool = True,
) -> dict:
    return {
        "enabled": enabled,
        "atr_lookback": atr_lookback,
        "atr_multiplier": atr_multiplier,
        "entry_reference_price": entry_reference_price,
        "evaluation_price": evaluation_price,
        "evaluation_timing": evaluation_timing,
    }


def _session_end_exit(session_ref: str = "UTC_DAILY_0000") -> dict:
    return {
        "session_end": {
            "enabled": True,
            "session_ref": session_ref,
            "exit_signal_timing": "last_bar_close_before_session_end",
            "fill_timing": "next_bar_open",
            "partial_session_policy": "no_exit",
        }
    }


def _opening_range_opposite_side(range_ref: str = "OR-1") -> dict:
    return {
        "enabled": True,
        "range_ref": range_ref,
        "entry_reference_price": "next_bar_open_pre_fee_slippage",
        "evaluation_price": "close",
        "evaluation_timing": "bar_close",
        "long_stop_level": "opening_range.low",
        "short_stop_level": "opening_range.high",
        "same_bar_entry_stop_policy": "not_evaluated_until_after_entry_bar",
    }


def _fixed_r_target(r_multiple: float = 2.0) -> dict:
    return {
        "enabled": True,
        "r_multiple": r_multiple,
        "entry_reference_price": "next_bar_open_pre_fee_slippage",
        "stop_ref": "opening_range_opposite_side",
        "evaluation_price": "close",
        "evaluation_timing": "bar_close",
        "same_bar_stop_target_policy": "defer_intrabar_realism",
    }


def _distance_ohlcv() -> pd.DataFrame:
    index = pd.date_range("2026-01-01", periods=25, freq="h", tz="UTC")
    close = ([100.0] * 20) + [94.0, 98.0, 90.0, 102.0, 94.0]
    return pd.DataFrame(
        {
            "open": close,
            "high": [value + 1.0 for value in close],
            "low": [value - 1.0 for value in close],
            "close": close,
            "volume": [1000.0] * len(index),
        },
        index=index,
    )


def _condition(left: dict, operator: str, right: dict, role: str = "required") -> dict:
    return {
        "condition_id": f"C-{operator}-{role}",
        "condition_role": role,
        "left_operand": left,
        "operator": operator,
        "right_operand": right,
        "units": None,
        "notes": None,
    }


def _group(
    role: str,
    logic: str,
    conditions: list[dict],
    subgroups: list[dict] | None = None,
    side: str | None = None,
) -> dict:
    group = {
        "group_id": f"G-{role}-{logic}",
        "group_role": role,
        "logic": logic,
        "conditions": conditions,
        "subgroups": subgroups or [],
        "notes": None,
    }
    if side is not None:
        group["side"] = side
    return group


def _spec(
    *,
    direction: str = "long",
    entry_groups: list[dict] | None = None,
    exit_groups: list[dict] | None = None,
    filters: list[dict] | None = None,
    max_holding_bars: int | None = None,
    entry_controls: dict | None = None,
) -> dict:
    spec = {
        "entry_logic": {
            "direction": direction,
            "groups": entry_groups or [],
            "notes": None,
        },
        "filters": {"groups": filters or [], "notes": None},
        "exit_logic": {
            "groups": exit_groups or [],
            "max_holding_period": {
                "enabled": max_holding_bars is not None,
                "bars": max_holding_bars,
            },
            "notes": None,
        },
    }
    if entry_controls is not None:
        spec["entry_logic"]["entry_controls"] = entry_controls
    return spec


def _atr_stop_long_ohlcv(close_at_fill_bar: float = 97.0) -> pd.DataFrame:
    index = pd.date_range("2026-04-01", periods=4, freq="h", tz="UTC")
    return pd.DataFrame(
        {
            "open": [100.0, 100.0, 100.0, 100.0],
            "high": [102.0, 101.0, 101.0, 101.0],
            "low": [100.0, 99.0, 99.0, 99.0],
            "close": [101.0, close_at_fill_bar, 95.0, 95.0],
            "volume": [1000.0] * len(index),
        },
        index=index,
    )


def _atr_stop_short_ohlcv(close_at_fill_bar: float = 103.0) -> pd.DataFrame:
    index = pd.date_range("2026-04-01", periods=4, freq="h", tz="UTC")
    return pd.DataFrame(
        {
            "open": [100.0, 100.0, 100.0, 100.0],
            "high": [100.0, 101.0, 101.0, 101.0],
            "low": [98.0, 99.0, 99.0, 99.0],
            "close": [98.0, close_at_fill_bar, 105.0, 105.0],
            "volume": [1000.0] * len(index),
        },
        index=index,
    )


def _default_variant(**parameter_values) -> dict:
    return {
        "variant_id": "VAR-000001",
        "assignment_status": "included",
        "parameter_values": parameter_values,
        "parameter_value_hash": None,
    }


def _ohlcv_from_close(close: list[float | None]) -> pd.DataFrame:
    index = pd.date_range("2026-02-01", periods=len(close), freq="h", tz="UTC")
    normalized = [math.nan if value is None else float(value) for value in close]
    return pd.DataFrame(
        {
            "open": [0.0 if math.isnan(value) else value for value in normalized],
            "high": [0.0 if math.isnan(value) else value + 1.0 for value in normalized],
            "low": [0.0 if math.isnan(value) else value - 1.0 for value in normalized],
            "close": normalized,
            "volume": [1000.0] * len(index),
        },
        index=index,
    )


def _single_condition_spec(operator: str, left: dict, right: dict, *, max_holding_bars: int | None = None) -> dict:
    return _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        left,
                        operator,
                        right,
                    )
                ],
            )
        ],
        max_holding_bars=max_holding_bars,
    )


def _both_direction_spec(
    *,
    long_entry: dict | None = None,
    short_entry: dict | None = None,
    long_exit: dict | None = None,
    short_exit: dict | None = None,
    filters: list[dict] | None = None,
    max_holding_bars: int | None = None,
) -> dict:
    exit_groups = []
    if long_exit is not None:
        exit_groups.append(_group("exit", "all", [long_exit], side="long"))
    if short_exit is not None:
        exit_groups.append(_group("exit", "all", [short_exit], side="short"))
    return _spec(
        direction="both",
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    long_entry
                    or _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 10.0),
                    )
                ],
                side="long",
            ),
            _group(
                "required",
                "all",
                [
                    short_entry
                    or _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _operand("constant", 10.0),
                    )
                ],
                side="short",
            ),
        ],
        exit_groups=exit_groups,
        filters=filters,
        max_holding_bars=max_holding_bars,
    )


def test_compiles_long_only_data_ref_threshold_signal() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 12.0),
                    )
                ],
            )
        ],
        exit_groups=[
            _group(
                "exit",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _operand("constant", 13.0),
                        role="exit",
                    )
                ],
            )
        ],
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0]
    assert signal.index.equals(ohlcv.index)


DATA_DERIVED_FIELD_VALUES = {
    "funding_rate": [-0.01, 0.01, -0.02, 0.02, -0.03, 0.03, -0.04, 0.04],
    "funding_mark_price": [9.0, 11.0, 9.0, 11.0, 9.0, 11.0, 9.0, 11.0],
    "mark_price": [9.0, 11.0, 9.0, 11.0, 9.0, 11.0, 9.0, 11.0],
    "index_price": [9.0, 11.0, 9.0, 11.0, 9.0, 11.0, 9.0, 11.0],
    "premium_index": [-0.01, 0.01, -0.02, 0.02, -0.03, 0.03, -0.04, 0.04],
    "open_interest": [9.0, 11.0, 9.0, 11.0, 9.0, 11.0, 9.0, 11.0],
    "open_interest_value": [9.0, 11.0, 9.0, 11.0, 9.0, 11.0, 9.0, 11.0],
    "top_trader_position_long_short_ratio": [0.9, 1.1, 0.9, 1.1, 0.9, 1.1, 0.9, 1.1],
    "top_trader_account_long_short_ratio": [0.9, 1.1, 0.9, 1.1, 0.9, 1.1, 0.9, 1.1],
    "global_long_short_account_ratio": [0.9, 1.1, 0.9, 1.1, 0.9, 1.1, 0.9, 1.1],
    "taker_buy_sell_ratio": [0.9, 1.1, 0.9, 1.1, 0.9, 1.1, 0.9, 1.1],
    "taker_buy_volume": [9.0, 11.0, 9.0, 11.0, 9.0, 11.0, 9.0, 11.0],
    "taker_sell_volume": [9.0, 11.0, 9.0, 11.0, 9.0, 11.0, 9.0, 11.0],
}


@pytest.mark.parametrize("field", sorted(DATA_DERIVED_FIELD_VALUES))
def test_allowed_data_derived_field_compiles_through_data_ref(field: str) -> None:
    ohlcv = _ohlcv()
    ohlcv[field] = DATA_DERIVED_FIELD_VALUES[field]
    threshold = (
        0.0
        if field in {"funding_rate", "premium_index"}
        else 1.0 if "ratio" in field else 10.0
    )
    spec = _single_condition_spec(
        "gt",
        _operand("data_ref", field, field),
        _operand("constant", threshold),
        max_holding_bars=1,
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0]


def test_unknown_data_derived_field_fails_closed() -> None:
    ohlcv = _ohlcv()
    ohlcv["liquidation_notional"] = 1.0
    spec = _single_condition_spec(
        "gt",
        _operand("data_ref", "liquidation_notional", "liquidation_notional"),
        _operand("constant", 0.0),
    )

    with pytest.raises(SpecSignalCompilerError, match="unsupported data_ref field"):
        compile_signal(spec, _default_variant(), ohlcv)


def test_missing_allowed_data_derived_field_fails_closed() -> None:
    spec = _single_condition_spec(
        "gt",
        _operand("data_ref", "funding_rate", "funding_rate"),
        _operand("constant", 0.0),
    )

    with pytest.raises(
        SpecSignalCompilerError,
        match="missing referenced data_ref field: 'funding_rate'",
    ):
        compile_signal(spec, _default_variant(), _ohlcv())


@pytest.mark.parametrize("field", ["funding_rate", "open_interest", "taker_buy_sell_ratio"])
def test_data_derived_field_future_mutation_has_no_lookahead(field: str) -> None:
    ohlcv = _ohlcv()
    ohlcv[field] = DATA_DERIVED_FIELD_VALUES[field]
    mutated = ohlcv.copy()
    cutoff = ohlcv.index[3]
    mutated.loc[mutated.index[4] :, field] = 1_000_000.0
    threshold = 0.0 if field == "funding_rate" else 1.0 if "ratio" in field else 10.0
    spec = _single_condition_spec(
        "gt",
        _operand("data_ref", field, field),
        _operand("constant", threshold),
        max_holding_bars=1,
    )

    base_signal = compile_signal(spec, _default_variant(), ohlcv)
    mutated_signal = compile_signal(spec, _default_variant(), mutated)

    pd.testing.assert_series_equal(base_signal.loc[:cutoff], mutated_signal.loc[:cutoff])


def test_data_derived_field_preserves_null_without_fill_or_interpolation() -> None:
    ohlcv = _ohlcv()
    ohlcv["open_interest"] = [9.0, math.nan, 11.0, math.nan, 9.0, 11.0, 9.0, 11.0]
    context = compiler._CompileContext(
        strategy_spec={},
        variant_assignment=_default_variant(),
        ohlcv=ohlcv,
        catalog=compiler._load_default_catalog(),
    )

    resolved = compiler._resolve_operand(
        _operand("data_ref", "open_interest", "open_interest"),
        context,
    )

    pd.testing.assert_series_equal(resolved, ohlcv["open_interest"])
    assert resolved.isna().tolist() == [False, True, False, True, False, False, False, False]


def test_compiles_short_only_data_ref_threshold_signal() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        direction="short",
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _operand("constant", 12.0),
                    )
                ],
            )
        ],
        exit_groups=[
            _group(
                "exit",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 11.0),
                        role="exit",
                    )
                ],
            )
        ],
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [-1.0, -1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0]


def test_resolves_parameter_ref_values_from_variant_assignment() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("parameter_ref", "entry_threshold"),
                    )
                ],
            )
        ],
    )

    signal = compile_signal(spec, _default_variant(entry_threshold=12.0), ohlcv)

    assert signal.tolist() == [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0]


def test_fails_closed_when_required_parameter_ref_is_missing() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("parameter_ref", "entry_threshold"),
                    )
                ],
            )
        ],
    )

    with pytest.raises(SpecSignalCompilerError, match="missing required parameter_ref"):
        compile_signal(spec, _default_variant(), ohlcv)


def test_compiles_long_only_sma_distance_composed_operand_signal() -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _composed_operand(),
                    )
                ],
            )
        ],
        exit_groups=[
            _group(
                "exit",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 0.0),
                        role="exit",
                    )
                ],
            )
        ],
    )

    signal = compile_signal(
        spec,
        _default_variant(entry_distance_threshold=0.05),
        ohlcv,
    )
    plain_threshold = compiler._sma_v1(ohlcv["close"], 20)
    plain_condition = (ohlcv["close"] < plain_threshold).fillna(False)

    assert signal.tolist()[-5:] == [1.0, 0.0, 1.0, 0.0, 0.0]
    assert plain_condition.tolist()[-5:] == [True, True, True, False, True]


def test_composed_operand_result_equals_manual_sma_scaled_series() -> None:
    ohlcv = _distance_ohlcv()
    context = compiler._CompileContext(
        strategy_spec={},
        variant_assignment=_default_variant(entry_distance_threshold=0.05),
        ohlcv=ohlcv,
        catalog=compiler._load_default_catalog(),
    )

    result = compiler._resolve_operand(_composed_operand(), context)
    expected = compiler._sma_v1(ohlcv["close"], 20) * (1.0 - 0.05)

    pd.testing.assert_series_equal(result, expected)


def test_composed_operand_plus_data_ref_parameter_compiles_expected_band() -> None:
    ohlcv = _distance_ohlcv()
    context = compiler._CompileContext(
        strategy_spec={},
        variant_assignment=_default_variant(entry_distance_threshold=0.05),
        ohlcv=ohlcv,
        catalog=compiler._load_default_catalog(),
    )

    result = compiler._resolve_operand(
        _composed_operand(
            composition_type="scale_by_one_plus_parameter",
            base_operand=_operand("data_ref", "close", "close"),
        ),
        context,
    )
    expected = ohlcv["close"] * (1.0 + 0.05)

    pd.testing.assert_series_equal(result, expected)


def test_composed_operand_plus_indicator_ref_parameter_compiles_expected_band() -> None:
    ohlcv = _distance_ohlcv()
    context = compiler._CompileContext(
        strategy_spec={},
        variant_assignment=_default_variant(entry_distance_threshold=0.05),
        ohlcv=ohlcv,
        catalog=compiler._load_default_catalog(),
    )

    result = compiler._resolve_operand(
        _composed_operand(composition_type="scale_by_one_plus_parameter"),
        context,
    )
    expected = compiler._sma_v1(ohlcv["close"], 20) * (1.0 + 0.05)

    pd.testing.assert_series_equal(result, expected)


def test_composed_operand_minus_still_compiles_expected_band() -> None:
    ohlcv = _distance_ohlcv()
    context = compiler._CompileContext(
        strategy_spec={},
        variant_assignment=_default_variant(entry_distance_threshold=0.05),
        ohlcv=ohlcv,
        catalog=compiler._load_default_catalog(),
    )

    result = compiler._resolve_operand(
        _composed_operand(composition_type="scale_by_one_minus_parameter"),
        context,
    )
    expected = compiler._sma_v1(ohlcv["close"], 20) * (1.0 - 0.05)

    pd.testing.assert_series_equal(result, expected)


def test_z_score_composed_operand_result_equals_manual_pandas_series() -> None:
    ohlcv = _ohlcv()
    context = compiler._CompileContext(
        strategy_spec={},
        variant_assignment=_default_variant(),
        ohlcv=ohlcv,
        catalog=compiler._load_default_catalog(),
    )

    result = compiler._resolve_operand(_z_score_operand(), context)
    center = compiler._sma_v1(ohlcv["close"], 3)
    scale = compiler._stddev_v1(ohlcv["close"], 3, ddof=0)
    expected = ((ohlcv["close"] - center) / scale).mask(scale.isna() | (scale == 0.0))

    pd.testing.assert_series_equal(result, expected)


def test_z_score_composed_operand_warmup_null_produces_false_condition() -> None:
    ohlcv = _ohlcv()
    spec = _single_condition_spec("gt", _z_score_operand(), _operand("constant", 0.0))

    signal = compile_signal(spec, _default_variant(), ohlcv)
    z_score = compiler._resolve_operand(
        _z_score_operand(),
        compiler._CompileContext(
            strategy_spec={},
            variant_assignment=_default_variant(),
            ohlcv=ohlcv,
            catalog=compiler._load_default_catalog(),
        ),
    )

    assert z_score.iloc[:2].isna().all()
    assert signal.iloc[:2].tolist() == [0.0, 0.0]


def test_z_score_composed_operand_zero_scale_policy_outputs_null() -> None:
    ohlcv = _ohlcv_from_close([10.0, 10.0, 10.0, 11.0])
    context = compiler._CompileContext(
        strategy_spec={},
        variant_assignment=_default_variant(),
        ohlcv=ohlcv,
        catalog=compiler._load_default_catalog(),
    )

    result = compiler._resolve_operand(_z_score_operand(), context)

    assert math.isnan(result.iloc[2])
    assert math.isfinite(result.iloc[3])


def test_z_score_composed_operand_has_no_lookahead_for_past_signal_decisions() -> None:
    ohlcv = _ohlcv_from_close([10.0, 11.0, 12.0, 11.0, 13.0, 14.0, 12.0, 15.0])
    mutated = ohlcv.copy()
    mutated.loc[mutated.index[6:], "close"] = [500.0, 600.0]
    spec = _single_condition_spec("gt", _z_score_operand(), _operand("constant", 0.0))

    base_signal = compile_signal(spec, _default_variant(), ohlcv)
    mutated_signal = compile_signal(spec, _default_variant(), mutated)

    pd.testing.assert_series_equal(base_signal.iloc[:6], mutated_signal.iloc[:6])


def test_z_score_composed_operand_rejects_unknown_zero_scale_policy() -> None:
    ohlcv = _ohlcv()
    context = compiler._CompileContext(
        strategy_spec={},
        variant_assignment=_default_variant(),
        ohlcv=ohlcv,
        catalog=compiler._load_default_catalog(),
    )

    with pytest.raises(SpecSignalCompilerError, match="zero_scale_policy"):
        compiler._resolve_operand(_z_score_operand(zero_scale_policy="epsilon"), context)


def test_z_score_composed_operand_rejects_nested_operand() -> None:
    ohlcv = _ohlcv()
    context = compiler._CompileContext(
        strategy_spec={},
        variant_assignment=_default_variant(entry_distance_threshold=0.05),
        ohlcv=ohlcv,
        catalog=compiler._load_default_catalog(),
    )

    with pytest.raises(UnsupportedSpecSignalCompilerFeature, match="nested composed_operand"):
        compiler._resolve_operand(_z_score_operand(value_operand=_composed_operand()), context)


def test_z_score_composed_operand_rejects_forbidden_executable_key() -> None:
    ohlcv = _ohlcv()
    operand = _z_score_operand()
    operand["formula"] = "x"
    spec = _single_condition_spec("gt", operand, _operand("constant", 0.0))

    with pytest.raises(SpecSignalCompilerError, match="forbidden executable/protected key"):
        compile_signal(spec, _default_variant(), ohlcv)


def test_composed_operand_repeated_calls_are_deterministic() -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _composed_operand(),
                    )
                ],
            )
        ],
    )

    first = compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)
    second = compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)

    pd.testing.assert_series_equal(first, second)


def test_composed_operand_warmup_null_produces_false_condition() -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _composed_operand(),
                    )
                ],
            )
        ],
    )

    signal = compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)
    composed = compiler._resolve_operand(
        _composed_operand(),
        compiler._CompileContext(
            strategy_spec={},
            variant_assignment=_default_variant(entry_distance_threshold=0.05),
            ohlcv=ohlcv,
            catalog=compiler._load_default_catalog(),
        ),
    )

    assert composed.iloc[:19].isna().all()
    assert signal.iloc[:20].tolist() == [0.0] * 20


def test_composed_operand_preserves_base_series_nulls_without_fill() -> None:
    ohlcv = _distance_ohlcv()
    ohlcv.loc[ohlcv.index[20], "close"] = math.nan
    context = compiler._CompileContext(
        strategy_spec={},
        variant_assignment=_default_variant(entry_distance_threshold=0.05),
        ohlcv=ohlcv,
        catalog=compiler._load_default_catalog(),
    )

    result = compiler._resolve_operand(
        _composed_operand(base_operand=_operand("data_ref", "close", "close")),
        context,
    )

    assert math.isnan(result.loc[ohlcv.index[20]])
    assert result.loc[ohlcv.index[19]] == pytest.approx(95.0)
    assert result.loc[ohlcv.index[21]] == pytest.approx(93.1)


def test_composed_operand_plus_preserves_base_nan_values() -> None:
    ohlcv = _distance_ohlcv()
    ohlcv.loc[ohlcv.index[20], "close"] = math.nan
    context = compiler._CompileContext(
        strategy_spec={},
        variant_assignment=_default_variant(entry_distance_threshold=0.05),
        ohlcv=ohlcv,
        catalog=compiler._load_default_catalog(),
    )

    result = compiler._resolve_operand(
        _composed_operand(
            composition_type="scale_by_one_plus_parameter",
            base_operand=_operand("data_ref", "close", "close"),
        ),
        context,
    )

    assert math.isnan(result.loc[ohlcv.index[20]])
    assert result.loc[ohlcv.index[19]] == pytest.approx(105.0)
    assert result.loc[ohlcv.index[21]] == pytest.approx(102.9)


def test_composed_operand_has_no_lookahead_for_past_signal_decisions() -> None:
    ohlcv = _distance_ohlcv()
    mutated = ohlcv.copy()
    mutated.loc[mutated.index[23:], "close"] = [500.0, 600.0]
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _composed_operand(),
                    )
                ],
            )
        ],
    )

    base_signal = compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)
    mutated_signal = compile_signal(spec, _default_variant(entry_distance_threshold=0.05), mutated)

    pd.testing.assert_series_equal(base_signal.iloc[:23], mutated_signal.iloc[:23])


def test_composed_operand_plus_has_no_lookahead() -> None:
    ohlcv = _distance_ohlcv()
    mutated = ohlcv.copy()
    mutated.loc[mutated.index[23:], "close"] = [500.0, 600.0]
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _composed_operand(composition_type="scale_by_one_plus_parameter"),
                    )
                ],
            )
        ],
    )

    base_signal = compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)
    mutated_signal = compile_signal(spec, _default_variant(entry_distance_threshold=0.05), mutated)

    pd.testing.assert_series_equal(base_signal.iloc[:23], mutated_signal.iloc[:23])


def test_composed_operand_uses_variant_assignment_parameter_value() -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _composed_operand(),
                    )
                ],
            )
        ],
    )

    loose = compile_signal(spec, _default_variant(entry_distance_threshold=0.01), ohlcv)
    strict = compile_signal(spec, _default_variant(entry_distance_threshold=0.10), ohlcv)

    assert loose.tolist()[-5:] == [1.0, 1.0, 1.0, 1.0, 1.0]
    assert strict.tolist()[-5:] == [0.0, 0.0, 0.0, 0.0, 0.0]
    assert loose.sum() > strict.sum()


def test_composed_operand_plus_compiler_repeated_calls_are_deterministic() -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _composed_operand(composition_type="scale_by_one_plus_parameter"),
                    )
                ],
            )
        ],
    )

    first = compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)
    second = compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)

    pd.testing.assert_series_equal(first, second)


@pytest.mark.parametrize(
    "variant, match",
    [
        (_default_variant(), "missing required parameter_ref"),
        (_default_variant(entry_distance_threshold="0.05"), "must be numeric"),
        (_default_variant(entry_distance_threshold=True), "must be numeric"),
        (_default_variant(entry_distance_threshold=0.0), "must be in \\(0, 1\\)"),
        (_default_variant(entry_distance_threshold=-0.1), "must be in \\(0, 1\\)"),
        (_default_variant(entry_distance_threshold=1.0), "must be in \\(0, 1\\)"),
        (_default_variant(entry_distance_threshold=1.2), "must be in \\(0, 1\\)"),
    ],
)
def test_composed_operand_parameter_value_fails_closed(variant: dict, match: str) -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _composed_operand(),
                    )
                ],
            )
        ],
    )

    with pytest.raises(SpecSignalCompilerError, match=match):
        compile_signal(spec, variant, ohlcv)


@pytest.mark.parametrize(
    "variant, match",
    [
        (_default_variant(), "missing required parameter_ref"),
        (_default_variant(entry_distance_threshold="0.05"), "must be numeric"),
        (_default_variant(entry_distance_threshold=True), "must be numeric"),
        (_default_variant(entry_distance_threshold=0.0), "must be in \\(0, 1\\)"),
        (_default_variant(entry_distance_threshold=-0.1), "must be in \\(0, 1\\)"),
        (_default_variant(entry_distance_threshold=1.0), "must be in \\(0, 1\\)"),
        (_default_variant(entry_distance_threshold=1.2), "must be in \\(0, 1\\)"),
        (_default_variant(entry_distance_threshold=math.inf), "must be in \\(0, 1\\)"),
        (_default_variant(entry_distance_threshold=math.nan), "must be in \\(0, 1\\)"),
    ],
)
def test_composed_operand_plus_rejects_invalid_parameter_values(variant: dict, match: str) -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _composed_operand(composition_type="scale_by_one_plus_parameter"),
                    )
                ],
            )
        ],
    )

    with pytest.raises(SpecSignalCompilerError, match=match):
        compile_signal(spec, variant, ohlcv)


def test_composed_operand_scale_by_one_minus_parameter_passes() -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _composed_operand(composition_type="scale_by_one_minus_parameter"),
                    )
                ],
            )
        ],
    )

    signal = compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)

    assert set(signal.unique()) <= {0.0, 1.0}


def test_composed_operand_rejects_unknown_composition_type() -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _composed_operand(composition_type="scale_by_two_parameters"),
                    )
                ],
            )
        ],
    )

    with pytest.raises(UnsupportedSpecSignalCompilerFeature, match="unsupported composition_type"):
        compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)


@pytest.mark.parametrize(
    "composition_type",
    [
        "offset_minus_parameter",
        "offset_plus_parameter",
        "multiply",
        "expression",
    ],
)
def test_composed_operand_unapproved_composition_types_fail_closed(composition_type: str) -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _composed_operand(composition_type=composition_type),
                    )
                ],
            )
        ],
    )

    with pytest.raises(UnsupportedSpecSignalCompilerFeature, match="unsupported composition_type"):
        compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)


def test_composed_operand_base_data_ref_passes() -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _composed_operand(
                            base_operand=_operand("data_ref", "close", "close"),
                        ),
                    )
                ],
            )
        ],
    )

    signal = compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)

    assert signal.tolist() == [0.0] * len(ohlcv)


def test_composed_operand_base_indicator_ref_passes() -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _composed_operand(
                            base_operand=_operand("indicator_ref", "sma", "value", {"bars": 20}),
                        ),
                    )
                ],
            )
        ],
    )

    signal = compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)

    assert signal.iloc[20] == 1.0


@pytest.mark.parametrize(
    "base_operand",
    [
        _operand("parameter_ref", "entry_distance_threshold"),
        _composed_operand(),
    ],
)
def test_composed_operand_unapproved_base_operand_types_fail_closed(base_operand: dict) -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _composed_operand(base_operand=base_operand),
                    )
                ],
            )
        ],
    )

    with pytest.raises(UnsupportedSpecSignalCompilerFeature):
        compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)


def test_composed_operand_plus_rejects_nested_base_operand() -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _composed_operand(
                            composition_type="scale_by_one_plus_parameter",
                            base_operand=_composed_operand(),
                        ),
                    )
                ],
            )
        ],
    )

    with pytest.raises(UnsupportedSpecSignalCompilerFeature, match="nested composed_operand"):
        compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)


def test_composed_operand_parameter_ref_passes() -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _composed_operand(
                            parameter_operand=_operand("parameter_ref", "entry_distance_threshold"),
                        ),
                    )
                ],
            )
        ],
    )

    signal = compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)

    assert signal.iloc[20] == 1.0


@pytest.mark.parametrize(
    "parameter_operand",
    [
        _operand("data_ref", "close", "close"),
        _operand("indicator_ref", "sma", "value", {"bars": 20}),
        _composed_operand(),
    ],
)
def test_composed_operand_unapproved_parameter_operand_types_fail_closed(
    parameter_operand: dict,
) -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _composed_operand(parameter_operand=parameter_operand),
                    )
                ],
            )
        ],
    )

    with pytest.raises(UnsupportedSpecSignalCompilerFeature):
        compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)


def test_composed_operand_plus_rejects_nested_parameter_operand() -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _composed_operand(
                            composition_type="scale_by_one_plus_parameter",
                            parameter_operand=_composed_operand(),
                        ),
                    )
                ],
            )
        ],
    )

    with pytest.raises(UnsupportedSpecSignalCompilerFeature, match="nested composed_operand"):
        compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)


def test_composed_operand_plus_rejects_non_parameter_ref_parameter() -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _composed_operand(
                            composition_type="scale_by_one_plus_parameter",
                            parameter_operand=_operand("data_ref", "close", "close"),
                        ),
                    )
                ],
            )
        ],
    )

    with pytest.raises(UnsupportedSpecSignalCompilerFeature, match="parameter_operand"):
        compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)


def test_nested_composed_operand_fails_closed_when_schema_is_bypassed() -> None:
    ohlcv = _distance_ohlcv()
    nested = _composed_operand(base_operand=_composed_operand())
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        nested,
                    )
                ],
            )
        ],
    )

    with pytest.raises(UnsupportedSpecSignalCompilerFeature, match="nested composed_operand"):
        compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda operand: operand.update({"formula": "close < sma"}),
        lambda operand: operand["base_operand"].update({"eval": "x"}),
        lambda operand: operand["parameter_operand"].update({"lookahead": True}),
    ],
)
def test_forbidden_keys_inside_composed_payload_fail_closed(mutator) -> None:
    ohlcv = _distance_ohlcv()
    composed = _composed_operand()
    mutator(composed)
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        composed,
                    )
                ],
            )
        ],
    )

    with pytest.raises(SpecSignalCompilerError, match="forbidden executable"):
        compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)


def test_sma_v1_has_no_lookahead_and_null_warmup() -> None:
    result = compiler._sma_v1(pd.Series([1.0, 2.0, 3.0, 4.0]), 3)

    assert math.isnan(result.iloc[0])
    assert math.isnan(result.iloc[1])
    assert result.iloc[2:].tolist() == [2.0, 3.0]


def test_ema_v1_uses_locked_alpha_and_sma_seed() -> None:
    result = compiler._ema_v1(pd.Series([1.0, 2.0, 3.0, 4.0, 5.0]), 3)

    assert math.isnan(result.iloc[0])
    assert math.isnan(result.iloc[1])
    assert result.iloc[2:].tolist() == [2.0, 3.0, 4.0]


def test_atr_v1_uses_wilder_true_range_and_rma() -> None:
    index = pd.date_range("2026-01-01", periods=4, freq="h", tz="UTC")
    ohlcv = pd.DataFrame(
        {
            "open": [10.0, 11.0, 12.0, 13.0],
            "high": [12.0, 14.0, 15.0, 16.0],
            "low": [9.0, 10.0, 11.0, 12.0],
            "close": [11.0, 13.0, 12.0, 15.0],
            "volume": [1.0, 1.0, 1.0, 1.0],
        },
        index=index,
    )

    result = compiler._atr_v1(ohlcv, 3)

    assert math.isnan(result.iloc[0])
    assert math.isnan(result.iloc[1])
    assert result.iloc[2] == pytest.approx((3.0 + 4.0 + 4.0) / 3.0)
    assert result.iloc[3] == pytest.approx(((result.iloc[2] * 2.0) + 4.0) / 3.0)


def test_atr_stop_absent_preserves_existing_signal() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 12.0),
                    )
                ],
            )
        ],
        exit_groups=[
            _group(
                "exit",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _operand("constant", 13.0),
                        role="exit",
                    )
                ],
            )
        ],
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert "atr_stop" not in spec["exit_logic"]
    assert signal.tolist() == [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0]


def test_atr_stop_long_fires_from_next_bar_open_reference() -> None:
    ohlcv = _atr_stop_long_ohlcv(close_at_fill_bar=97.0)
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 100.0),
                    )
                ],
            )
        ],
    )
    spec["exit_logic"]["atr_stop"] = _atr_stop(atr_lookback=1, atr_multiplier=1.0)

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [1.0, 0.0, 0.0, 0.0]


def test_atr_stop_short_fires_from_next_bar_open_reference() -> None:
    ohlcv = _atr_stop_short_ohlcv(close_at_fill_bar=103.0)
    spec = _spec(
        direction="short",
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _operand("constant", 99.0),
                    )
                ],
            )
        ],
    )
    spec["exit_logic"]["atr_stop"] = _atr_stop(atr_lookback=1, atr_multiplier=1.0)

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [-1.0, 0.0, 0.0, 0.0]


def test_atr_stop_preserves_existing_exit_when_opposite_exit_fires_first() -> None:
    ohlcv = _atr_stop_long_ohlcv(close_at_fill_bar=99.0)
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 100.0),
                    )
                ],
            )
        ],
        exit_groups=[
            _group(
                "exit",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _operand("constant", 100.0),
                        role="exit",
                    )
                ],
            )
        ],
    )
    spec["exit_logic"]["atr_stop"] = _atr_stop(atr_lookback=1, atr_multiplier=1.0)

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [1.0, 0.0, 0.0, 0.0]


def test_atr_stop_fires_when_stop_precedes_opposite_exit() -> None:
    ohlcv = _atr_stop_long_ohlcv(close_at_fill_bar=97.0)
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 100.0),
                    )
                ],
            )
        ],
        exit_groups=[
            _group(
                "exit",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _operand("constant", 90.0),
                        role="exit",
                    )
                ],
            )
        ],
    )
    spec["exit_logic"]["atr_stop"] = _atr_stop(atr_lookback=1, atr_multiplier=1.0)

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [1.0, 0.0, 0.0, 0.0]


def test_atr_stop_exit_bar_does_not_reenter_when_entry_condition_remains_true() -> None:
    ohlcv = _atr_stop_long_ohlcv(close_at_fill_bar=97.0)
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 10.0),
                    )
                ],
            )
        ],
    )
    spec["exit_logic"]["atr_stop"] = _atr_stop(atr_lookback=1, atr_multiplier=1.0)

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [1.0, 0.0, 1.0, 0.0]


def test_atr_stop_uses_fixed_atr_from_entry_signal_bar() -> None:
    index = pd.date_range("2026-04-01", periods=5, freq="h", tz="UTC")
    ohlcv = pd.DataFrame(
        {
            "open": [100.0] * len(index),
            "high": [100.0, 100.0, 102.0, 150.0, 150.0],
            "low": [99.0, 99.0, 100.0, 50.0, 50.0],
            "close": [99.0, 99.0, 101.0, 97.0, 97.0],
            "volume": [1000.0] * len(index),
        },
        index=index,
    )
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 100.0),
                    )
                ],
            )
        ],
    )
    spec["exit_logic"]["atr_stop"] = _atr_stop(atr_lookback=1, atr_multiplier=1.0)

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 0.0, 1.0, 0.0, 0.0]


def test_atr_stop_repeated_compilation_is_deterministic() -> None:
    ohlcv = _atr_stop_long_ohlcv(close_at_fill_bar=97.0)
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 100.0),
                    )
                ],
            )
        ],
    )
    spec["exit_logic"]["atr_stop"] = _atr_stop(atr_lookback=1, atr_multiplier=1.0)

    first = compile_signal(spec, _default_variant(), ohlcv)
    second = compile_signal(spec, _default_variant(), ohlcv)

    pd.testing.assert_series_equal(first, second)


def test_atr_stop_both_direction_state_does_not_leak_between_sides() -> None:
    index = pd.date_range("2026-04-01", periods=5, freq="h", tz="UTC")
    ohlcv = pd.DataFrame(
        {
            "open": [100.0] * len(index),
            "high": [102.0, 101.0, 98.0, 122.0, 96.0],
            "low": [100.0, 99.0, 78.0, 120.0, 94.0],
            "close": [101.0, 97.0, 80.0, 121.0, 95.0],
            "volume": [1000.0] * len(index),
        },
        index=index,
    )
    spec = _both_direction_spec(
        long_entry=_condition(
            _operand("data_ref", "close", "close"),
            "gt",
            _operand("constant", 100.0),
        ),
        short_entry=_condition(
            _operand("data_ref", "close", "close"),
            "lt",
            _operand("constant", 90.0),
        ),
    )
    spec["exit_logic"]["atr_stop"] = _atr_stop(atr_lookback=1, atr_multiplier=1.0)

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [1.0, 0.0, -1.0, 0.0, 0.0]


@pytest.mark.parametrize(
    ("mutator", "match"),
    [
        (lambda atr_stop: atr_stop.update({"atr_multiplier": 0.0}), "atr_multiplier"),
        (lambda atr_stop: atr_stop.update({"atr_multiplier": math.inf}), "atr_multiplier"),
        (lambda atr_stop: atr_stop.update({"atr_lookback": 0}), "atr_lookback"),
        (lambda atr_stop: atr_stop.update({"atr_lookback": 1.5}), "atr_lookback"),
        (
            lambda atr_stop: atr_stop.update({"entry_reference_price": "close"}),
            "entry_reference_price",
        ),
        (lambda atr_stop: atr_stop.update({"evaluation_price": "open"}), "evaluation_price"),
        (
            lambda atr_stop: atr_stop.update({"evaluation_timing": "intrabar"}),
            "evaluation_timing",
        ),
        (lambda atr_stop: atr_stop.update({"enabled": False}), "enabled"),
        (lambda atr_stop: atr_stop.update({"parameter_ref": "atr_k"}), "supports exactly"),
    ],
)
def test_atr_stop_rejects_invalid_closed_grammar(mutator, match: str) -> None:
    spec = _single_condition_spec(
        "gt",
        _operand("data_ref", "close", "close"),
        _operand("constant", 100.0),
    )
    spec["exit_logic"]["atr_stop"] = _atr_stop(atr_lookback=1, atr_multiplier=1.0)
    mutator(spec["exit_logic"]["atr_stop"])

    with pytest.raises(SpecSignalCompilerError, match=match):
        compile_signal(spec, _default_variant(), _atr_stop_long_ohlcv())


def test_atr_stop_rejects_forbidden_executable_key() -> None:
    spec = _single_condition_spec(
        "gt",
        _operand("data_ref", "close", "close"),
        _operand("constant", 100.0),
    )
    spec["exit_logic"]["atr_stop"] = _atr_stop(atr_lookback=1, atr_multiplier=1.0)
    spec["exit_logic"]["atr_stop"]["lambda"] = "close <= stop"

    with pytest.raises(SpecSignalCompilerError, match="forbidden executable"):
        compile_signal(spec, _default_variant(), _atr_stop_long_ohlcv())


def test_stddev_v1_uses_locked_ddof_convention() -> None:
    result_ddof0 = compiler._stddev_v1(pd.Series([1.0, 2.0, 3.0]), 3, ddof=0)
    result_ddof1 = compiler._stddev_v1(pd.Series([1.0, 2.0, 3.0]), 3, ddof=1)

    assert math.isnan(result_ddof0.iloc[0])
    assert math.isnan(result_ddof0.iloc[1])
    assert result_ddof0.iloc[2] == pytest.approx(math.sqrt(2.0 / 3.0))
    assert result_ddof1.iloc[2] == pytest.approx(1.0)


def test_rsi_v1_uses_wilder_smoothing_and_locked_zero_policy() -> None:
    result = compiler._rsi_v1(pd.Series([1.0, 2.0, 3.0, 2.0, 2.0, 5.0]), 3)

    assert math.isnan(result.iloc[0])
    assert math.isnan(result.iloc[1])
    assert math.isnan(result.iloc[2])
    assert result.iloc[3] == pytest.approx(100.0 - (100.0 / (1.0 + 2.0)))
    assert result.iloc[4] == pytest.approx(result.iloc[3])
    assert result.iloc[5] == pytest.approx(89.74358974358975)

    assert compiler._rsi_v1(pd.Series([1.0, 2.0, 3.0, 4.0]), 3).iloc[3] == 100.0
    assert compiler._rsi_v1(pd.Series([4.0, 3.0, 2.0, 1.0]), 3).iloc[3] == 0.0
    assert compiler._rsi_v1(pd.Series([5.0, 5.0, 5.0, 5.0]), 3).iloc[3] == 50.0


def test_rsi_v1_resets_after_missing_data_and_has_no_lookahead() -> None:
    base = pd.Series([1.0, 2.0, 3.0, 4.0, math.nan, 5.0, 6.0, 7.0, 8.0])
    result = compiler._rsi_v1(base, 3)

    assert result.iloc[3] == 100.0
    assert result.iloc[4:8].isna().all()
    assert result.iloc[8] == 100.0

    mutated = base.copy()
    mutated.iloc[8] = 100.0
    mutated_result = compiler._rsi_v1(mutated, 3)

    pd.testing.assert_series_equal(result.iloc[:8], mutated_result.iloc[:8])


def test_donchian_v1_includes_current_bar_and_exposes_lagged_breakout_fields() -> None:
    index = pd.date_range("2026-01-01", periods=4, freq="h", tz="UTC")
    ohlcv = pd.DataFrame(
        {
            "open": [7.0, 8.0, 7.0, 12.0],
            "high": [10.0, 11.0, 9.0, 13.0],
            "low": [5.0, 6.0, 4.0, 8.0],
            "close": [7.0, 8.0, 7.0, 12.0],
            "volume": [1.0] * 4,
        },
        index=index,
    )

    result = compiler._donchian_v1(ohlcv, 3)

    assert result["upper"].iloc[:2].isna().all()
    assert result["upper"].iloc[2:].tolist() == [11.0, 13.0]
    assert result["lower"].iloc[2:].tolist() == [4.0, 4.0]
    assert result["mid"].iloc[2:].tolist() == [7.5, 8.5]
    assert result["width"].iloc[2:].tolist() == [7.0, 9.0]
    assert math.isnan(result["upper_lag1"].iloc[2])
    assert result["upper_lag1"].iloc[3] == 11.0


def test_donchian_lagged_field_supports_breakout_safe_comparison() -> None:
    index = pd.date_range("2026-01-01", periods=4, freq="h", tz="UTC")
    ohlcv = pd.DataFrame(
        {
            "open": [7.0, 8.0, 7.0, 12.0],
            "high": [10.0, 11.0, 9.0, 13.0],
            "low": [5.0, 6.0, 4.0, 8.0],
            "close": [7.0, 8.0, 7.0, 12.0],
            "volume": [1.0] * 4,
        },
        index=index,
    )
    spec = _single_condition_spec(
        "gt",
        _operand("data_ref", "close", "close"),
        _operand("indicator_ref", "donchian", "upper_lag1", {"bars": 3}),
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)
    current_channel = compiler._donchian_v1(ohlcv, 3)["upper"]

    assert signal.tolist() == [0.0, 0.0, 0.0, 1.0]
    assert bool((ohlcv["close"] > current_channel).fillna(False).iloc[3]) is False


def test_donchian_v1_has_no_lookahead_future_mutation() -> None:
    ohlcv = _ohlcv()
    result = compiler._donchian_v1(ohlcv, 3)["upper_lag1"]
    mutated = ohlcv.copy()
    mutated.iloc[7, mutated.columns.get_loc("high")] = 1000.0
    mutated_result = compiler._donchian_v1(mutated, 3)["upper_lag1"]

    pd.testing.assert_series_equal(result.iloc[:7], mutated_result.iloc[:7])


def test_ma_distance_v1_outputs_abs_ratio_pct_and_masks_zero_ma() -> None:
    close = pd.Series([0.0, 0.0, 2.0, 4.0])

    result = compiler._ma_distance_v1(close, 2)

    assert math.isnan(result["distance_abs"].iloc[0])
    assert result["distance_abs"].iloc[1:].tolist() == [0.0, 1.0, 1.0]
    assert math.isnan(result["distance_ratio"].iloc[1])
    assert result["distance_ratio"].iloc[2] == pytest.approx(1.0)
    assert result["distance_ratio"].iloc[3] == pytest.approx(1.0 / 3.0)
    assert result["distance_pct"].iloc[2] == pytest.approx(100.0)


def test_rvol_v1_warmup_missing_volume_and_zero_denominator() -> None:
    result = compiler._rvol_v1(pd.Series([1.0, math.nan, 3.0, 4.0, 5.0]), 3)

    assert result["rvol"].iloc[:4].isna().all()
    assert result["volume_ma"].iloc[:4].isna().all()
    assert result["volume_ma"].iloc[4] == pytest.approx(4.0)
    assert result["rvol"].iloc[4] == pytest.approx(1.25)

    zero_result = compiler._rvol_v1(pd.Series([0.0, 0.0, 0.0, 3.0]), 3)
    assert math.isnan(zero_result["rvol"].iloc[2])
    assert zero_result["rvol"].iloc[3] == pytest.approx(3.0)


def test_rvol_v1_has_no_lookahead_future_mutation() -> None:
    volume = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    result = compiler._rvol_v1(volume, 3)
    mutated = volume.copy()
    mutated.iloc[4] = 5000.0
    mutated_result = compiler._rvol_v1(mutated, 3)

    pd.testing.assert_series_equal(result["rvol"].iloc[:4], mutated_result["rvol"].iloc[:4])
    pd.testing.assert_series_equal(
        result["volume_ma"].iloc[:4], mutated_result["volume_ma"].iloc[:4]
    )


def test_rolling_vwap_v1_warmup_missing_ohlcv_and_zero_volume() -> None:
    index = pd.date_range("2026-01-01", periods=5, freq="h", tz="UTC")
    ohlcv = pd.DataFrame(
        {
            "high": [3.0, 4.0, 5.0, 6.0, 7.0],
            "low": [1.0, 2.0, 3.0, 4.0, 5.0],
            "close": [2.0, 3.0, 4.0, 5.0, 6.0],
            "volume": [1.0, 1.0, 1.0, 1.0, 1.0],
        },
        index=index,
    )
    result = compiler._rolling_vwap_v1(ohlcv, 3)["rolling_vwap"]

    assert result.iloc[:2].isna().all()
    assert result.iloc[2:].tolist() == pytest.approx([3.0, 4.0, 5.0])

    for field in ("high", "low", "close", "volume"):
        missing = ohlcv.copy()
        missing.iloc[1, missing.columns.get_loc(field)] = math.nan
        missing_result = compiler._rolling_vwap_v1(missing, 3)["rolling_vwap"]
        assert missing_result.iloc[:4].isna().all()
        assert missing_result.iloc[4] == pytest.approx(5.0)

    zero_volume = ohlcv.iloc[:4].copy()
    zero_volume["volume"] = [0.0, 0.0, 0.0, 1.0]
    zero_result = compiler._rolling_vwap_v1(zero_volume, 3)["rolling_vwap"]
    assert math.isnan(zero_result.iloc[2])
    assert zero_result.iloc[3] == pytest.approx(5.0)


def test_rolling_vwap_v1_has_no_lookahead_future_mutation() -> None:
    ohlcv = _ohlcv()
    result = compiler._rolling_vwap_v1(ohlcv, 3)["rolling_vwap"]
    mutated = ohlcv.copy()
    mutated.iloc[7, mutated.columns.get_loc("high")] = 10000.0
    mutated.iloc[7, mutated.columns.get_loc("volume")] = 10000.0
    mutated_result = compiler._rolling_vwap_v1(mutated, 3)["rolling_vwap"]

    pd.testing.assert_series_equal(result.iloc[:7], mutated_result.iloc[:7])


def test_resolves_indicator_ref_through_committed_catalog() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("indicator_ref", "sma", "value", {"bars": 3}),
                        "gte",
                        _operand("constant", 11.0),
                    )
                ],
            )
        ],
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]


def test_literal_indicator_lookback_still_compiles_unchanged() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("indicator_ref", "sma", "value", {"bars": 3}),
                        "gte",
                        _operand("constant", 11.0),
                    )
                ],
            )
        ],
    )

    first = compile_signal(spec, _default_variant(lookback_n=4), ohlcv)
    second = compile_signal(spec, _default_variant(lookback_n=7), ohlcv)

    assert first.tolist() == [0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    pd.testing.assert_series_equal(first, second)


def test_resolves_parameterized_sma_lookback_from_variant_assignment() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand(
                            "indicator_ref",
                            "sma",
                            "value",
                            {"bars_parameter_ref": "lookback_n"},
                        ),
                        "gte",
                        _operand("constant", 11.0),
                    )
                ],
            )
        ],
    )

    signal = compile_signal(spec, _default_variant(lookback_n=3), ohlcv)

    assert signal.tolist() == [0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]


def test_resolves_parameterized_ema_atr_and_stddev_lookbacks() -> None:
    ohlcv = _ohlcv()
    context = compiler._CompileContext(
        strategy_spec={},
        variant_assignment=_default_variant(lookback_n=3),
        ohlcv=ohlcv,
        catalog=compiler._load_default_catalog(),
    )

    ema = compiler._resolve_operand(
        _operand("indicator_ref", "ema", "value", {"bars_parameter_ref": "lookback_n"}),
        context,
    )
    atr = compiler._resolve_operand(
        _operand("indicator_ref", "atr", "value", {"bars_parameter_ref": "lookback_n"}),
        context,
    )
    stddev = compiler._resolve_operand(
        _operand("indicator_ref", "stddev", "value", {"bars_parameter_ref": "lookback_n"}),
        context,
    )

    pd.testing.assert_series_equal(ema, compiler._ema_v1(ohlcv["close"], 3))
    pd.testing.assert_series_equal(atr, compiler._atr_v1(ohlcv, 3))
    pd.testing.assert_series_equal(stddev, compiler._stddev_v1(ohlcv["close"], 3, ddof=0))


def test_resolves_new_indicator_refs_and_rejects_implicit_multi_output_field() -> None:
    ohlcv = _ohlcv()
    context = compiler._CompileContext(
        strategy_spec={},
        variant_assignment=_default_variant(lookback_n=3),
        ohlcv=ohlcv,
        catalog=compiler._load_default_catalog(),
    )

    rsi = compiler._resolve_operand(
        _operand("indicator_ref", "rsi", "value", {"bars_parameter_ref": "lookback_n"}),
        context,
    )
    donchian_upper = compiler._resolve_operand(
        _operand("indicator_ref", "donchian", "upper_lag1", {"bars_parameter_ref": "lookback_n"}),
        context,
    )
    ma_distance_ratio = compiler._resolve_operand(
        _operand("indicator_ref", "ma_distance", "distance_ratio", {"bars_parameter_ref": "lookback_n"}),
        context,
    )
    rvol = compiler._resolve_operand(
        _operand("indicator_ref", "rvol", "rvol", {"bars_parameter_ref": "lookback_n"}),
        context,
    )
    rolling_vwap = compiler._resolve_operand(
        _operand(
            "indicator_ref",
            "rolling_vwap",
            "rolling_vwap",
            {"bars_parameter_ref": "lookback_n"},
        ),
        context,
    )

    pd.testing.assert_series_equal(rsi, compiler._rsi_v1(ohlcv["close"], 3))
    pd.testing.assert_series_equal(donchian_upper, compiler._donchian_v1(ohlcv, 3)["upper_lag1"])
    pd.testing.assert_series_equal(ma_distance_ratio, compiler._ma_distance_v1(ohlcv["close"], 3)["distance_ratio"])
    pd.testing.assert_series_equal(rvol, compiler._rvol_v1(ohlcv["volume"], 3)["rvol"])
    pd.testing.assert_series_equal(
        rolling_vwap, compiler._rolling_vwap_v1(ohlcv, 3)["rolling_vwap"]
    )

    with pytest.raises(SpecSignalCompilerError, match="requires an explicit output field"):
        compiler._resolve_operand(
            _operand("indicator_ref", "donchian", "value", {"bars": 3}),
            context,
        )


def test_new_indicator_refs_work_in_both_direction_specs() -> None:
    ohlcv = _ohlcv()
    long_entry = _condition(
        _operand("indicator_ref", "rsi", "value", {"bars": 3}),
        "gt",
        _operand("constant", 50.0),
    )
    short_entry = _condition(
        _operand("indicator_ref", "ma_distance", "distance_ratio", {"bars": 3}),
        "lt",
        _operand("constant", -0.05),
    )
    spec = _both_direction_spec(
        long_entry=long_entry,
        short_entry=short_entry,
        max_holding_bars=1,
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0]


def test_parameterized_lookback_inside_composed_base_operand_compiles() -> None:
    ohlcv = _distance_ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _composed_operand(
                            base_operand=_operand(
                                "indicator_ref",
                                "sma",
                                "value",
                                {"bars_parameter_ref": "lookback_n"},
                            ),
                        ),
                    )
                ],
            )
        ],
    )

    signal = compile_signal(
        spec,
        _default_variant(entry_distance_threshold=0.05, lookback_n=20),
        ohlcv,
    )

    assert signal.iloc[20] == 1.0


def test_different_parameterized_lookbacks_change_warmup_and_signals() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand(
                            "indicator_ref",
                            "sma",
                            "value",
                            {"bars_parameter_ref": "lookback_n"},
                        ),
                        "gte",
                        _operand("constant", 11.0),
                    )
                ],
            )
        ],
    )

    lookback_3 = compile_signal(spec, _default_variant(lookback_n=3), ohlcv)
    lookback_5 = compile_signal(spec, _default_variant(lookback_n=5), ohlcv)

    assert lookback_3.tolist() == [0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    assert lookback_5.tolist() == [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0]
    assert lookback_3.sum() > lookback_5.sum()


@pytest.mark.parametrize(
    "variant, match",
    [
        (_default_variant(), "missing required lookback parameter_ref"),
        (_default_variant(lookback_n=3.0), "must resolve to an integer"),
        (_default_variant(lookback_n=True), "must resolve to an integer"),
        (_default_variant(lookback_n=None), "must resolve to an integer"),
        (_default_variant(lookback_n="3"), "must resolve to an integer"),
        (_default_variant(lookback_n=0), "must resolve to an integer"),
        (_default_variant(lookback_n=-3), "must resolve to an integer"),
    ],
)
def test_parameterized_lookback_invalid_assignment_values_fail_closed(
    variant: dict,
    match: str,
) -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand(
                            "indicator_ref",
                            "sma",
                            "value",
                            {"bars_parameter_ref": "lookback_n"},
                        ),
                        "gte",
                        _operand("constant", 11.0),
                    )
                ],
            )
        ],
    )

    with pytest.raises(SpecSignalCompilerError, match=match):
        compile_signal(spec, variant, ohlcv)


def test_parameterized_lookback_mixed_literal_and_parameter_form_fails_closed() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand(
                            "indicator_ref",
                            "sma",
                            "value",
                            {"bars": 3, "bars_parameter_ref": "lookback_n"},
                        ),
                        "gte",
                        _operand("constant", 11.0),
                    )
                ],
            )
        ],
    )

    with pytest.raises(UnsupportedSpecSignalCompilerFeature, match="exactly one"):
        compile_signal(spec, _default_variant(lookback_n=3), ohlcv)


def test_parameterized_lookback_outside_indicator_ref_fails_closed() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand(
                            "data_ref",
                            "close",
                            "close",
                            {"bars_parameter_ref": "lookback_n"},
                        ),
                        "gt",
                        _operand("constant", 11.0),
                    )
                ],
            )
        ],
    )

    with pytest.raises(UnsupportedSpecSignalCompilerFeature, match="only supported for indicator_ref"):
        compile_signal(spec, _default_variant(lookback_n=3), ohlcv)


def test_parameterized_lookback_repeated_compilation_is_deterministic() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand(
                            "indicator_ref",
                            "sma",
                            "value",
                            {"bars_parameter_ref": "lookback_n"},
                        ),
                        "gte",
                        _operand("constant", 11.0),
                    )
                ],
            )
        ],
    )

    first = compile_signal(spec, _default_variant(lookback_n=4), ohlcv)
    second = compile_signal(spec, _default_variant(lookback_n=4), ohlcv)

    pd.testing.assert_series_equal(first, second)


def test_parameterized_lookback_has_no_lookahead_for_past_signal_decisions() -> None:
    ohlcv = _distance_ohlcv()
    mutated = ohlcv.copy()
    mutated.loc[mutated.index[23:], "close"] = [500.0, 600.0]
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _operand(
                            "indicator_ref",
                            "sma",
                            "value",
                            {"bars_parameter_ref": "lookback_n"},
                        ),
                    )
                ],
            )
        ],
    )

    base_signal = compile_signal(spec, _default_variant(lookback_n=20), ohlcv)
    mutated_signal = compile_signal(spec, _default_variant(lookback_n=20), mutated)

    pd.testing.assert_series_equal(base_signal.iloc[:23], mutated_signal.iloc[:23])


def test_existing_strat_spec_0001_still_compiles_with_literal_lookbacks() -> None:
    spec_path = (
        Path(__file__).resolve().parents[1]
        / "research"
        / "strategy_specs"
        / "STRAT-SPEC-0001.strategy_spec.json"
    )
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    ohlcv = _distance_ohlcv()

    signal = compile_signal(
        spec,
        _default_variant(entry_distance_threshold=0.05),
        ohlcv,
    )

    assert signal.index.equals(ohlcv.index)
    assert set(signal.unique()) <= {0.0, 1.0}


def test_rejects_unknown_indicator_ref() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("indicator_ref", "vwap", "value", {"bars": 3}),
                        "gt",
                        _operand("constant", 11.0),
                    )
                ],
            )
        ],
    )

    with pytest.raises(SpecSignalCompilerError, match="unknown indicator_ref"):
        compile_signal(spec, _default_variant(), ohlcv)


def test_rejects_indicator_catalog_builtin_mismatch() -> None:
    catalog = compiler._load_default_catalog()
    catalog["entries"][0]["implementation_binding"]["builtin_key"] = "ema_v1"

    with pytest.raises(SpecSignalCompilerError, match="builtin mismatch"):
        compile_signal(_spec(), _default_variant(), _ohlcv(), indicator_catalog=catalog)


def test_rejects_computation_defined_in_catalog_true() -> None:
    catalog = compiler._load_default_catalog()
    catalog["entries"][0]["implementation_binding"]["computation_defined_in_catalog"] = True

    with pytest.raises(SpecSignalCompilerError, match="computation_defined_in_catalog"):
        compile_signal(_spec(), _default_variant(), _ohlcv(), indicator_catalog=catalog)


def test_rejects_forbidden_executable_keys_recursively() -> None:
    spec = _spec()
    spec["entry_logic"]["groups"] = []
    spec["notes"] = {"formula": "close > 1"}

    with pytest.raises(SpecSignalCompilerError, match="forbidden executable"):
        compile_signal(spec, _default_variant(), _ohlcv())


def test_crosses_above_data_ref_constant_prior_bar_semantics() -> None:
    ohlcv = _ohlcv_from_close([8.0, 10.0, 11.0, 12.0, 10.0, 10.0, 11.0, 10.0])
    spec = _single_condition_spec(
        "crosses_above",
        _operand("data_ref", "close", "close"),
        _operand("constant", 10.0),
        max_holding_bars=1,
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0]


def test_crosses_below_data_ref_constant_prior_bar_semantics() -> None:
    ohlcv = _ohlcv_from_close([12.0, 10.0, 9.0, 8.0, 10.0, 10.0, 9.0, 10.0])
    spec = _single_condition_spec(
        "crosses_below",
        _operand("data_ref", "close", "close"),
        _operand("constant", 10.0),
        max_holding_bars=1,
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0]


def test_crosses_current_equality_is_false() -> None:
    ohlcv = _ohlcv_from_close([9.0, 10.0, 10.0, 11.0])
    spec = _single_condition_spec(
        "crosses_above",
        _operand("data_ref", "close", "close"),
        _operand("constant", 10.0),
        max_holding_bars=1,
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 0.0, 0.0, 1.0]


def test_crosses_first_row_is_false() -> None:
    ohlcv = _ohlcv_from_close([11.0, 12.0, 13.0])
    spec = _single_condition_spec(
        "crosses_above",
        _operand("data_ref", "close", "close"),
        _operand("constant", 10.0),
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 0.0, 0.0]


def test_crosses_null_prior_or_current_values_are_false() -> None:
    index = pd.date_range("2026-02-01", periods=8, freq="h", tz="UTC")
    ohlcv = pd.DataFrame(
        {
            "open": [0.0] * len(index),
            "high": [10.0, 10.0, math.nan, 10.0, 10.0, math.nan, 10.0, math.nan],
            "low": [0.0] * len(index),
            "close": [math.nan, 11.0, 9.0, math.nan, 9.0, 11.0, 9.0, 11.0],
            "volume": [1000.0] * len(index),
        },
        index=index,
    )
    spec = _single_condition_spec(
        "crosses_above",
        _operand("data_ref", "close", "close"),
        _operand("data_ref", "high", "high"),
        max_holding_bars=1,
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0] * len(index)


def test_crosses_above_supports_series_vs_series_operand() -> None:
    ohlcv = _ohlcv_from_close([9.0, 10.0, 11.0, 9.0])
    ohlcv["open"] = [10.0, 10.0, 10.0, 10.0]
    spec = _single_condition_spec(
        "crosses_above",
        _operand("data_ref", "close", "close"),
        _operand("data_ref", "open", "open"),
        max_holding_bars=1,
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 0.0, 1.0, 0.0]


def test_crosses_operator_has_no_lookahead() -> None:
    ohlcv = _ohlcv_from_close([9.0, 10.0, 11.0, 8.0, 9.0, 10.0, 11.0])
    mutated = ohlcv.copy()
    cutoff = ohlcv.index[3]
    mutated.loc[mutated.index[4] :, "close"] = [100.0, 101.0, 102.0]
    spec = _single_condition_spec(
        "crosses_above",
        _operand("data_ref", "close", "close"),
        _operand("constant", 10.0),
        max_holding_bars=1,
    )

    base_signal = compile_signal(spec, _default_variant(), ohlcv)
    mutated_signal = compile_signal(spec, _default_variant(), mutated)

    pd.testing.assert_series_equal(base_signal.loc[:cutoff], mutated_signal.loc[:cutoff])


@pytest.mark.parametrize("operator", ["in_set"])
def test_other_unsupported_operators_still_fail_closed(operator: str) -> None:
    spec = _single_condition_spec(
        operator,
        _operand("data_ref", "close", "close"),
        _operand("constant", 12.0),
    )

    with pytest.raises(UnsupportedSpecSignalCompilerFeature, match=operator):
        compile_signal(spec, _default_variant(), _ohlcv())


def test_unknown_operator_still_fails_closed() -> None:
    spec = _single_condition_spec(
        "crosses_sideways",
        _operand("data_ref", "close", "close"),
        _operand("constant", 12.0),
    )

    with pytest.raises(SpecSignalCompilerError, match="unknown operator"):
        compile_signal(spec, _default_variant(), _ohlcv())


def test_crosses_compiler_repeated_calls_are_deterministic() -> None:
    ohlcv = _ohlcv_from_close([8.0, 10.0, 11.0, 9.0, 10.0, 11.0])
    spec = _single_condition_spec(
        "crosses_above",
        _operand("data_ref", "close", "close"),
        _operand("constant", 10.0),
        max_holding_bars=1,
    )

    first = compile_signal(spec, _default_variant(), ohlcv)
    second = compile_signal(spec, _default_variant(), ohlcv)

    pd.testing.assert_series_equal(first, second)


def test_true_blocking_condition_prevents_entry() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _operand("constant", 14.0),
                    )
                ],
            ),
            _group(
                "blocking",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 9.0),
                        role="blocking",
                    )
                ],
            ),
        ]
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0] * len(ohlcv)


def test_blocking_condition_inside_entry_group_fails_closed() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 9.0),
                        role="blocking",
                    )
                ],
            )
        ]
    )

    with pytest.raises(UnsupportedSpecSignalCompilerFeature, match="incompatible"):
        compile_signal(spec, _default_variant(), ohlcv)


def test_exit_or_invalidation_condition_inside_entry_group_fails_closed() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 9.0),
                        role="exit",
                    )
                ],
            )
        ]
    )

    with pytest.raises(UnsupportedSpecSignalCompilerFeature, match="incompatible"):
        compile_signal(spec, _default_variant(), ohlcv)

    spec["entry_logic"]["groups"][0]["conditions"][0]["condition_role"] = "invalidation"
    with pytest.raises(UnsupportedSpecSignalCompilerFeature, match="incompatible"):
        compile_signal(spec, _default_variant(), ohlcv)


def test_valid_invalidation_condition_exits_position() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _operand("constant", 14.0),
                    )
                ],
            )
        ],
        exit_groups=[
            _group(
                "invalidation",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 13.0),
                        role="invalidation",
                    )
                ],
            )
        ],
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.0]


def test_supported_entry_condition_roles_still_work() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gte",
                        _operand("constant", 10.0),
                        role="required",
                    ),
                    _condition(
                        _operand("data_ref", "volume", "volume"),
                        "eq",
                        _operand("constant", 1000.0),
                        role="confirming",
                    ),
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "neq",
                        _operand("constant", 0.0),
                        role="filter",
                    ),
                ],
            )
        ]
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [1.0] * len(ohlcv)


def test_trend_filter_gate_allows_and_blocks_entries() -> None:
    ohlcv = _ohlcv_from_close([10.0, 11.0, 12.0, 11.0, 9.0, 8.0])
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 0.0),
                    )
                ],
            )
        ],
        filters=[
            _group(
                "trend",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("indicator_ref", "sma", "value", {"bars": 3}),
                        role="filter",
                    )
                ],
            )
        ],
        max_holding_bars=1,
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 0.0, 1.0, 0.0, 0.0, 0.0]


def test_regime_filter_gate_warmup_null_blocks_entries() -> None:
    ohlcv = _ohlcv_from_close([10.0, 11.0, 12.0, 10.0])
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 0.0),
                    )
                ],
            )
        ],
        filters=[
            _group(
                "regime",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("indicator_ref", "sma", "value", {"bars": 3}),
                        role="filter",
                    )
                ],
            )
        ],
        max_holding_bars=1,
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.iloc[:2].tolist() == [0.0, 0.0]
    assert signal.tolist() == [0.0, 0.0, 1.0, 0.0]


def test_trend_filter_gate_has_no_lookahead_for_past_signal_decisions() -> None:
    base = _ohlcv_from_close([10.0, 11.0, 12.0, 11.0, 13.0, 14.0, 12.0])
    mutated = base.copy()
    mutated.loc[mutated.index[5:], "close"] = [100.0, 1.0]
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 0.0),
                    )
                ],
            )
        ],
        filters=[
            _group(
                "trend",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("indicator_ref", "ema", "value", {"bars": 3}),
                        role="filter",
                    )
                ],
            )
        ],
        max_holding_bars=1,
    )

    base_signal = compile_signal(spec, _default_variant(), base)
    mutated_signal = compile_signal(spec, _default_variant(), mutated)

    pd.testing.assert_series_equal(base_signal.iloc[:5], mutated_signal.iloc[:5])


def test_trend_filter_gate_supports_both_direction_specs() -> None:
    ohlcv = _ohlcv_from_close([11.0, 9.0, 11.0])
    spec = _both_direction_spec(
        filters=[
            _group(
                "trend",
                "all",
                [
                    _condition(
                        _operand("data_ref", "volume", "volume"),
                        "eq",
                        _operand("constant", 1000.0),
                        role="filter",
                    )
                ],
            )
        ],
        max_holding_bars=1,
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [1.0, 0.0, 1.0]
    assert set(signal.unique()) <= {-1.0, 0.0, 1.0}


def test_trend_filter_gate_rejects_unknown_or_malformed_gate_config() -> None:
    ohlcv = _ohlcv()
    unknown_gate = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 0.0),
                    )
                ],
            )
        ],
        filters=[
            _group(
                "trend_regime_expression",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 0.0),
                        role="filter",
                    )
                ],
            )
        ],
    )
    malformed_gate = _spec(
        entry_groups=unknown_gate["entry_logic"]["groups"],
        filters=[
            _group(
                "trend",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 0.0),
                        role="filter",
                    )
                ],
            )
        ],
    )
    del malformed_gate["filters"]["groups"][0]["logic"]

    with pytest.raises(UnsupportedSpecSignalCompilerFeature, match="unsupported entry/filter group role"):
        compile_signal(unknown_gate, _default_variant(), ohlcv)
    with pytest.raises(SpecSignalCompilerError, match="unsupported condition group logic"):
        compile_signal(malformed_gate, _default_variant(), ohlcv)


def test_trend_filter_gate_rejects_unsupported_operand_and_forbidden_key() -> None:
    ohlcv = _ohlcv()
    unsupported_operand = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 0.0),
                    )
                ],
            )
        ],
        filters=[
            _group(
                "trend",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("indicator_ref", "trend_magic", "value", {"bars": 3}),
                        role="filter",
                    )
                ],
            )
        ],
    )
    forbidden_key = _spec(
        entry_groups=json.loads(json.dumps(unsupported_operand["entry_logic"]["groups"])),
        filters=json.loads(json.dumps(unsupported_operand["filters"]["groups"])),
    )
    forbidden_key["filters"]["groups"][0]["formula"] = "close > sma(close, 3)"

    with pytest.raises(SpecSignalCompilerError, match="unknown indicator_ref"):
        compile_signal(unsupported_operand, _default_variant(), ohlcv)
    with pytest.raises(SpecSignalCompilerError, match="forbidden executable/protected key"):
        compile_signal(forbidden_key, _default_variant(), ohlcv)


def test_evaluates_nested_all_any_groups_deterministically() -> None:
    ohlcv = _ohlcv()
    nested = _group(
        "required",
        "any",
        [
            _condition(
                _operand("data_ref", "close", "close"),
                "lt",
                _operand("constant", 0.0),
            )
        ],
        subgroups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gte",
                        _operand("constant", 12.0),
                    ),
                    _condition(
                        _operand("data_ref", "volume", "volume"),
                        "eq",
                        _operand("constant", 1000.0),
                    ),
                ],
            )
        ],
    )
    spec = _spec(entry_groups=[nested])

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]


def test_null_operand_never_true() -> None:
    ohlcv = _ohlcv()
    ohlcv.loc[ohlcv.index[2], "close"] = math.nan
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 11.0),
                    )
                ],
            )
        ],
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0]


def test_applies_max_holding_period_when_enabled() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _operand("constant", 11.0),
                    )
                ],
            )
        ],
        max_holding_bars=2,
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


def test_min_bars_between_entries_suppresses_too_frequent_reentry() -> None:
    ohlcv = _ohlcv_from_close([11.0] * 8)
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 10.0),
                    )
                ],
            )
        ],
        max_holding_bars=1,
        entry_controls={"min_bars_between_entries": 2},
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0]


def test_min_bars_between_entries_allows_first_valid_entry_without_prior_entry() -> None:
    ohlcv = _ohlcv_from_close([9.0, 11.0, 11.0])
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 10.0),
                    )
                ],
            )
        ],
        max_holding_bars=1,
        entry_controls={"min_bars_between_entries": 5},
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 1.0, 0.0]


def test_min_bars_between_entries_does_not_suppress_exit_logic() -> None:
    ohlcv = _ohlcv_from_close([11.0, 9.0, 12.0])
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 10.0),
                    )
                ],
            )
        ],
        exit_groups=[
            _group(
                "exit",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _operand("constant", 10.0),
                        role="exit",
                    )
                ],
            )
        ],
        entry_controls={"min_bars_between_entries": 5},
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [1.0, 0.0, 0.0]


def test_min_bars_between_entries_null_warmup_before_first_entry_is_safe() -> None:
    ohlcv = _ohlcv_from_close([None, 11.0, 11.0, 11.0])
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 10.0),
                    )
                ],
            )
        ],
        max_holding_bars=1,
        entry_controls={"min_bars_between_entries": 2},
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 1.0, 0.0, 0.0]


def test_min_bars_between_entries_uses_shared_final_stream_for_both_direction() -> None:
    spec = _both_direction_spec(
        max_holding_bars=1,
    )
    spec["entry_logic"]["entry_controls"] = {"min_bars_between_entries": 2}

    signal = compile_signal(
        spec,
        _default_variant(),
        _ohlcv_from_close([11.0, 9.0, 9.0, 9.0, 12.0]),
    )

    assert signal.tolist() == [1.0, 0.0, 0.0, -1.0, 0.0]
    assert set(signal.unique()) <= {-1.0, 0.0, 1.0}


def test_min_bars_between_entries_has_no_lookahead_for_past_entry_decisions() -> None:
    base = _ohlcv_from_close([11.0, 9.0, 9.0, 9.0, 9.0])
    mutated = base.copy()
    cutoff = base.index[2]
    mutated.loc[mutated.index[3] :, "close"] = [11.0, 11.0]
    spec = _both_direction_spec(max_holding_bars=1)
    spec["entry_logic"]["entry_controls"] = {"min_bars_between_entries": 2}

    base_signal = compile_signal(spec, _default_variant(), base)
    mutated_signal = compile_signal(spec, _default_variant(), mutated)

    pd.testing.assert_series_equal(base_signal.loc[:cutoff], mutated_signal.loc[:cutoff])


@pytest.mark.parametrize(
    ("entry_controls", "match"),
    [
        (None, "entry_controls must be an object"),
        ({"min_bars_between_entries": 0}, "requires integer bars"),
        ({"min_bars_between_entries": True}, "requires integer bars"),
        ({"min_bars_between_entries": 1.5}, "requires integer bars"),
        ({"min_bars_between_entries": 100001}, "requires integer bars"),
        ({"cooldown_bars_after_exit": 2}, "supports only min_bars_between_entries"),
    ],
)
def test_min_bars_between_entries_rejects_malformed_controls(entry_controls, match: str) -> None:
    spec = _single_condition_spec(
        "gt",
        _operand("data_ref", "close", "close"),
        _operand("constant", 10.0),
    )
    spec["entry_logic"]["entry_controls"] = entry_controls

    with pytest.raises(SpecSignalCompilerError, match=match):
        compile_signal(spec, _default_variant(), _ohlcv())


def test_min_bars_between_entries_rejects_forbidden_executable_key() -> None:
    spec = _single_condition_spec(
        "gt",
        _operand("data_ref", "close", "close"),
        _operand("constant", 10.0),
    )
    spec["entry_logic"]["entry_controls"] = {
        "min_bars_between_entries": 2,
        "eval": "close > 10",
    }

    with pytest.raises(SpecSignalCompilerError, match="forbidden executable"):
        compile_signal(spec, _default_variant(), _ohlcv())


def test_both_direction_enters_long_from_long_side_group() -> None:
    signal = compile_signal(_both_direction_spec(), _default_variant(), _ohlcv_from_close([11.0]))

    assert signal.tolist() == [1.0]


def test_both_direction_enters_short_from_short_side_group() -> None:
    signal = compile_signal(_both_direction_spec(), _default_variant(), _ohlcv_from_close([9.0]))

    assert signal.tolist() == [-1.0]


def test_both_direction_emits_single_stream_mutually_exclusive_values() -> None:
    signal = compile_signal(
        _both_direction_spec(max_holding_bars=2),
        _default_variant(),
        _ohlcv_from_close([11.0, 12.0, 8.0, 8.0]),
    )

    assert signal.tolist() == [1.0, 1.0, 0.0, -1.0]
    assert set(signal.unique()) <= {-1.0, 0.0, 1.0}


def test_both_direction_simultaneous_long_short_entry_while_flat_stays_flat() -> None:
    spec = _both_direction_spec(
        long_entry=_condition(
            _operand("data_ref", "close", "close"),
            "gte",
            _operand("constant", 10.0),
        ),
        short_entry=_condition(
            _operand("data_ref", "close", "close"),
            "lte",
            _operand("constant", 10.0),
        ),
    )

    signal = compile_signal(spec, _default_variant(), _ohlcv_from_close([10.0, 11.0]))

    assert signal.tolist() == [0.0, 1.0]


def test_both_direction_long_exit_only_closes_long() -> None:
    spec = _both_direction_spec(
        long_exit=_condition(
            _operand("data_ref", "close", "close"),
            "lt",
            _operand("constant", 10.0),
            role="exit",
        ),
        short_exit=_condition(
            _operand("data_ref", "close", "close"),
            "gt",
            _operand("constant", 0.0),
            role="exit",
        ),
    )

    signal = compile_signal(spec, _default_variant(), _ohlcv_from_close([11.0, 12.0, 9.0]))

    assert signal.tolist() == [1.0, 1.0, 0.0]


def test_both_direction_short_exit_only_closes_short() -> None:
    spec = _both_direction_spec(
        long_exit=_condition(
            _operand("data_ref", "close", "close"),
            "gt",
            _operand("constant", 0.0),
            role="exit",
        ),
        short_exit=_condition(
            _operand("data_ref", "close", "close"),
            "gt",
            _operand("constant", 10.0),
            role="exit",
        ),
    )

    signal = compile_signal(spec, _default_variant(), _ohlcv_from_close([9.0, 8.0, 11.0]))

    assert signal.tolist() == [-1.0, -1.0, 0.0]


def test_both_direction_opposite_entry_while_long_does_not_flip() -> None:
    signal = compile_signal(
        _both_direction_spec(),
        _default_variant(),
        _ohlcv_from_close([11.0, 8.0, 8.0]),
    )

    assert signal.tolist() == [1.0, 1.0, 1.0]


def test_both_direction_opposite_entry_while_short_does_not_flip() -> None:
    signal = compile_signal(
        _both_direction_spec(),
        _default_variant(),
        _ohlcv_from_close([9.0, 12.0, 12.0]),
    )

    assert signal.tolist() == [-1.0, -1.0, -1.0]


def test_both_direction_same_bar_exit_and_opposite_entry_goes_flat_not_reversed() -> None:
    spec = _both_direction_spec(
        long_exit=_condition(
            _operand("data_ref", "close", "close"),
            "lt",
            _operand("constant", 10.0),
            role="exit",
        )
    )

    signal = compile_signal(spec, _default_variant(), _ohlcv_from_close([11.0, 9.0, 9.0]))

    assert signal.tolist() == [1.0, 0.0, -1.0]


def test_both_direction_respects_max_holding_for_current_side() -> None:
    signal = compile_signal(
        _both_direction_spec(max_holding_bars=2),
        _default_variant(),
        _ohlcv_from_close([11.0, 12.0, 8.0, 8.0, 8.0, 12.0, 12.0]),
    )

    assert signal.tolist() == [1.0, 1.0, 0.0, -1.0, -1.0, 0.0, 1.0]


def test_both_direction_compiler_rejects_unlabeled_entry_group_if_schema_bypassed() -> None:
    spec = _both_direction_spec()
    del spec["entry_logic"]["groups"][0]["side"]

    with pytest.raises(SpecSignalCompilerError, match="entry_logic\\.groups\\.0\\.side"):
        compile_signal(spec, _default_variant(), _ohlcv())


def test_both_direction_compiler_rejects_unknown_side_if_schema_bypassed() -> None:
    spec = _both_direction_spec()
    spec["entry_logic"]["groups"][0]["side"] = "up"

    with pytest.raises(SpecSignalCompilerError, match="entry_logic\\.groups\\.0\\.side"):
        compile_signal(spec, _default_variant(), _ohlcv())


def test_both_direction_compiler_rejects_unlabeled_exit_group_if_schema_bypassed() -> None:
    spec = _both_direction_spec(
        long_exit=_condition(
            _operand("data_ref", "close", "close"),
            "lt",
            _operand("constant", 10.0),
            role="exit",
        )
    )
    del spec["exit_logic"]["groups"][0]["side"]

    with pytest.raises(SpecSignalCompilerError, match="exit_logic\\.groups\\.0\\.side"):
        compile_signal(spec, _default_variant(), _ohlcv())


def test_both_direction_compiler_rejects_filter_side_label_if_schema_bypassed() -> None:
    spec = _both_direction_spec(
        filters=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "volume", "volume"),
                        "gt",
                        _operand("constant", 0.0),
                    )
                ],
                side="long",
            )
        ]
    )

    with pytest.raises(SpecSignalCompilerError, match="filters\\.groups\\.0\\.side"):
        compile_signal(spec, _default_variant(), _ohlcv())


def test_both_direction_preserves_no_lookahead() -> None:
    base = _ohlcv_from_close([9.0, 9.0, 9.0, 9.0, 9.0])
    mutated = base.copy()
    mutated.loc[mutated.index[3:], "close"] = [11.0, 8.0]

    base_signal = compile_signal(_both_direction_spec(), _default_variant(), base)
    mutated_signal = compile_signal(_both_direction_spec(), _default_variant(), mutated)

    pd.testing.assert_series_equal(base_signal.iloc[:3], mutated_signal.iloc[:3])


def test_both_direction_repeated_calls_are_deterministic() -> None:
    spec = _both_direction_spec(max_holding_bars=2)
    ohlcv = _ohlcv_from_close([11.0, 12.0, 8.0, 8.0, 12.0])

    first = compile_signal(spec, _default_variant(), ohlcv)
    second = compile_signal(spec, _default_variant(), ohlcv)

    pd.testing.assert_series_equal(first, second)


def test_existing_long_direction_signal_unchanged() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 12.0),
                    )
                ],
            )
        ],
        exit_groups=[
            _group(
                "exit",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _operand("constant", 13.0),
                        role="exit",
                    )
                ],
            )
        ],
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0]


def test_existing_short_direction_signal_unchanged() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        direction="short",
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "lt",
                        _operand("constant", 12.0),
                    )
                ],
            )
        ],
        exit_groups=[
            _group(
                "exit",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 11.0),
                        role="exit",
                    )
                ],
            )
        ],
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [-1.0, -1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0]


def test_both_direction_supports_crosses_above_below_conditions() -> None:
    spec = _both_direction_spec(
        long_entry=_condition(
            _operand("data_ref", "close", "close"),
            "crosses_above",
            _operand("constant", 10.0),
        ),
        short_entry=_condition(
            _operand("data_ref", "close", "close"),
            "crosses_below",
            _operand("constant", 10.0),
        ),
        max_holding_bars=1,
    )

    signal = compile_signal(
        spec,
        _default_variant(),
        _ohlcv_from_close([9.0, 10.0, 11.0, 9.0, 10.0, 9.0]),
    )

    assert signal.tolist() == [0.0, 0.0, 1.0, 0.0, 0.0, -1.0]


def test_both_direction_supports_plus_minus_composed_operands() -> None:
    index = pd.date_range("2026-03-01", periods=4, freq="h", tz="UTC")
    ohlcv = pd.DataFrame(
        {
            "open": [100.0] * len(index),
            "high": [101.0, 107.0, 101.0, 95.0],
            "low": [99.0, 105.0, 99.0, 93.0],
            "close": [100.0, 106.0, 100.0, 94.0],
            "volume": [1000.0] * len(index),
        },
        index=index,
    )
    spec = _both_direction_spec(
        long_entry=_condition(
            _operand("data_ref", "close", "close"),
            "gt",
            _composed_operand(
                composition_type="scale_by_one_plus_parameter",
                base_operand=_operand("data_ref", "open", "open"),
            ),
        ),
        short_entry=_condition(
            _operand("data_ref", "close", "close"),
            "lt",
            _composed_operand(
                composition_type="scale_by_one_minus_parameter",
                base_operand=_operand("data_ref", "open", "open"),
            ),
        ),
        max_holding_bars=1,
    )

    signal = compile_signal(spec, _default_variant(entry_distance_threshold=0.05), ohlcv)

    assert signal.tolist() == [0.0, 1.0, 0.0, -1.0]


def test_both_direction_supports_z_score_composed_operands() -> None:
    spec = _both_direction_spec(
        long_entry=_condition(
            _z_score_operand(),
            "gt",
            _operand("constant", 0.5),
        ),
        short_entry=_condition(
            _z_score_operand(),
            "lt",
            _operand("constant", -0.5),
        ),
        max_holding_bars=1,
    )

    signal = compile_signal(spec, _default_variant(), _ohlcv())

    assert set(signal.unique()) <= {-1.0, 0.0, 1.0}
    assert 1.0 in set(signal.tolist())
    assert -1.0 in set(signal.tolist())


def test_produces_identical_output_on_repeated_calls() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 12.0),
                    )
                ],
            )
        ],
    )

    first = compile_signal(spec, _default_variant(), ohlcv)
    second = compile_signal(spec, _default_variant(), ohlcv)

    pd.testing.assert_series_equal(first, second)


def test_returned_signal_is_consumable_by_run_backtest() -> None:
    from lib.backtest import run_backtest

    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 12.0),
                    )
                ],
            )
        ],
    )
    signal = compile_signal(spec, _default_variant(), ohlcv)

    result = run_backtest(
        signal=signal,
        ohlcv=ohlcv,
        funding=_funding(ohlcv.index),
        fee_bps_taker=4.0,
        fee_bps_maker=2.0,
        slippage_bps=1.0,
        initial_equity=10_000.0,
        stream="klines",
        interval="1h",
        gaps_path=Path("does-not-exist.json"),
    )

    assert result.equity_curve.index.equals(ohlcv.index)


def test_compiler_module_does_not_import_offline_runner_or_lib_modules() -> None:
    source = inspect.getsource(compiler)

    assert "run_offline_sweep" not in source
    assert "from lib.backtest" not in source
    assert "from lib.evaluation" not in source


def test_no_files_are_written_during_compilation(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_write(*args, **kwargs):
        raise AssertionError("write attempted")

    monkeypatch.setattr(Path, "write_text", fail_write)
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "gt",
                        _operand("constant", 12.0),
                    )
                ],
            )
        ],
    )

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.iloc[-1] == 1.0


def _orb_ohlcv(closes: list[float], *, zero_range_first_bar: bool = False) -> pd.DataFrame:
    index = pd.date_range("2026-01-01T00:00:00Z", periods=len(closes), freq="h")
    rows = []
    for i, close in enumerate(closes):
        if i % 24 == 0:
            open_, high, low = 100.0, 101.0, 99.0
            if zero_range_first_bar:
                high = low = 100.0
        else:
            open_, high, low = close, close + 0.5, close - 0.5
        rows.append({"open": open_, "high": high, "low": low, "close": close, "volume": 1000.0})
    return pd.DataFrame(rows, index=index)


def _primitive_condition(ref: str, field: str) -> dict:
    return _condition(_primitive_ref(ref, field), "is_true", _operand("constant", True))


def _param_ref(name: str) -> dict:
    return {"parameter_ref": name}


def test_opening_range_breakout_waits_for_range_completion_and_close_threshold() -> None:
    ohlcv = _orb_ohlcv([100.0, 100.5, 101.0, 101.1, 100.8])
    spec = _spec(entry_groups=[_group("required", "all", [_primitive_condition("ORB-1", "long")])])
    spec["online_ohlcv_primitives"] = _online_primitives()

    signal = compile_signal(spec, _default_variant(), ohlcv)
    context = compiler._CompileContext(
        strategy_spec=spec,
        variant_assignment=_default_variant(),
        ohlcv=ohlcv,
        catalog=compiler._load_default_catalog(),
    )
    breakout = compiler._resolve_operand(_primitive_ref("ORB-1", "long"), context)

    assert breakout.tolist() == [False, False, False, True, False]
    assert signal.tolist() == [0.0, 0.0, 0.0, 1.0, 1.0]


def test_opening_range_retest_window_expires_deterministically() -> None:
    ohlcv = _orb_ohlcv([100.0, 102.0, 103.0, 103.0, 100.8])
    spec = _spec(entry_groups=[_group("required", "all", [_primitive_condition("RETEST-1", "long")])])
    spec["online_ohlcv_primitives"] = _online_primitives(retest_max=2)

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0] * len(ohlcv)


def test_opening_range_retest_opposite_breakout_cancels_session_signal() -> None:
    ohlcv = _orb_ohlcv([100.0, 102.0, 98.0, 100.8])
    spec = _spec(entry_groups=[_group("required", "all", [_primitive_condition("RETEST-1", "long")])])
    spec["online_ohlcv_primitives"] = _online_primitives()

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0] * len(ohlcv)


def test_max_trades_per_session_blocks_second_entry_and_resets_next_session() -> None:
    closes = [100.0, 102.0, 100.8, 103.0, 100.7] + [100.0] * 19 + [100.0, 102.0, 100.8]
    ohlcv = _orb_ohlcv(closes)
    spec = _spec(
        entry_groups=[_group("required", "all", [_primitive_condition("RETEST-1", "long")])],
        max_holding_bars=1,
        entry_controls={
            "min_bars_between_entries": 1,
            "max_trades_per_session": {
                "enabled": True,
                "count_basis": "entries_filled",
                "max_trades": 1,
                "session_ref": "UTC_DAILY_0000",
                "reset": "session_start",
            },
        },
    )
    spec["online_ohlcv_primitives"] = _online_primitives()

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.iloc[2] == 1.0
    assert signal.iloc[4] == 0.0
    assert signal.iloc[26] == 1.0


def test_max_trades_per_session_accepts_parameter_ref_binding() -> None:
    closes = [100.0, 102.0, 103.0, 104.0]
    ohlcv = _orb_ohlcv(closes)
    spec = _spec(
        entry_groups=[_group("required", "all", [_primitive_condition("ORB-1", "long")])],
        max_holding_bars=1,
        entry_controls={
            "max_trades_per_session": {
                "enabled": True,
                "count_basis": "entries_filled",
                "max_trades": _param_ref("max_session_trades"),
                "session_ref": "UTC_DAILY_0000",
                "reset": "session_start",
            },
        },
    )
    spec["online_ohlcv_primitives"] = _online_primitives()

    capped = compile_signal(spec, _default_variant(max_session_trades=1), ohlcv)
    uncapped = compile_signal(spec, _default_variant(max_session_trades=2), ohlcv)

    assert capped.tolist() == [0.0, 1.0, 0.0, 0.0]
    assert uncapped.tolist() == [0.0, 1.0, 1.0, 0.0]


def test_online_primitive_thresholds_accept_parameter_ref_bindings() -> None:
    ohlcv = _orb_ohlcv([100.0, 101.25, 102.0, 100.9])
    primitives = _online_primitives(retest_max=3, tolerance_multiple=0.0)
    primitives["opening_range_breakouts"][0]["tolerance"]["multiple"] = _param_ref("orb_atr_tolerance")
    primitives["opening_range_retests"][0]["window"]["max_bars_after_breakout"] = _param_ref("retest_window")
    primitives["opening_range_retests"][0]["tolerance"]["multiple"] = _param_ref("retest_atr_tolerance")
    spec = _spec(entry_groups=[_group("required", "all", [_primitive_condition("RETEST-1", "long")])])
    spec["online_ohlcv_primitives"] = primitives

    permissive = compile_signal(
        spec,
        _default_variant(orb_atr_tolerance=0.0, retest_window=2, retest_atr_tolerance=0.2),
        ohlcv,
    )
    strict = compile_signal(
        spec,
        _default_variant(orb_atr_tolerance=0.3, retest_window=1, retest_atr_tolerance=0.0),
        ohlcv,
    )

    assert permissive.iloc[3] == 1.0
    assert strict.tolist() == [0.0] * len(ohlcv)


def test_candle_shape_thresholds_accept_parameter_ref_bindings() -> None:
    index = pd.date_range("2026-01-01", periods=3, freq="h", tz="UTC")
    ohlcv = pd.DataFrame(
        {
            "open": [100.0, 100.0, 100.0],
            "high": [110.0, 110.0, 110.0],
            "low": [100.0, 100.0, 100.0],
            "close": [109.0, 105.0, 101.0],
            "volume": [1000.0, 1000.0, 1000.0],
        },
        index=index,
    )
    primitives = _online_primitives()
    shape = primitives["candle_shapes"][0]
    shape["upper_wick_pct"]["value"] = _param_ref("wick_threshold")
    shape["lower_wick_pct"]["value"] = _param_ref("wick_threshold")
    shape["body_pct"]["value"] = _param_ref("body_threshold")
    spec = _spec(entry_groups=[_group("required", "all", [_primitive_condition("NO-WICK", "long")])])
    spec["online_ohlcv_primitives"] = primitives

    loose = compile_signal(spec, _default_variant(wick_threshold=0.1, body_threshold=0.8), ohlcv)
    strict = compile_signal(spec, _default_variant(wick_threshold=0.05, body_threshold=0.95), ohlcv)

    assert loose.tolist() == [1.0, 1.0, 1.0]
    assert strict.tolist() == [0.0, 0.0, 0.0]


def test_exit_thresholds_accept_parameter_ref_bindings() -> None:
    ohlcv = _atr_stop_long_ohlcv(close_at_fill_bar=100.0)
    spec = _spec(entry_groups=[_group("required", "all", [_condition(_operand("data_ref", "close", "close"), "gt", _operand("constant", 0.0))])])
    spec["exit_logic"]["atr_stop"] = _atr_stop(atr_multiplier=_param_ref("atr_stop_multiple"))
    context = compiler._CompileContext(
        strategy_spec=spec,
        variant_assignment=_default_variant(atr_stop_multiple=1.75),
        ohlcv=ohlcv,
        catalog=compiler._load_default_catalog(),
    )
    atr_config = compiler._atr_stop_config(spec, context)

    assert atr_config is not None
    assert atr_config.atr_multiplier == 1.75

    target_spec = _spec(entry_groups=[_group("required", "all", [_primitive_condition("ORB-1", "long")])])
    target_spec["online_ohlcv_primitives"] = _online_primitives()
    target_spec["exit_logic"]["opening_range_opposite_side"] = _opening_range_opposite_side()
    target_spec["exit_logic"]["fixed_R_target"] = _fixed_r_target(r_multiple=_param_ref("target_r"))
    target_context = compiler._CompileContext(
        strategy_spec=target_spec,
        variant_assignment=_default_variant(target_r=2.5),
        ohlcv=_orb_ohlcv([100.0, 102.0, 104.0, 105.0]),
        catalog=compiler._load_default_catalog(),
    )
    target_config = compiler._fixed_r_target_config(
        target_spec,
        compiler._opening_range_opposite_side_config(target_spec),
        target_context,
    )

    assert target_config is not None
    assert target_config.r_multiple == 2.5


@pytest.mark.parametrize(
    ("value", "parameter_values", "match"),
    [
        ({"parameter_ref": "missing"}, {}, "missing required parameter_ref"),
        ({"parameter_ref": "wick_threshold", "expression": "x + 1"}, {"wick_threshold": 0.1}, "forbidden executable/protected key"),
        ({"lambda": "x"}, {"wick_threshold": 0.1}, "forbidden executable/protected key"),
        ({"parameter_ref": "wick_threshold"}, {"wick_threshold": "0.1"}, "must be numeric"),
        ({"parameter_ref": "wick_threshold"}, {"wick_threshold": 2.0}, "must be in \\[0, 1\\]"),
    ],
)
def test_parameter_bound_primitive_thresholds_reject_invalid_bindings(
    value: dict,
    parameter_values: dict,
    match: str,
) -> None:
    primitives = _online_primitives()
    primitives["candle_shapes"][0]["upper_wick_pct"]["value"] = value
    spec = _spec(entry_groups=[_group("required", "all", [_primitive_condition("NO-WICK", "long")])])
    spec["online_ohlcv_primitives"] = primitives

    with pytest.raises(SpecSignalCompilerError, match=match):
        compile_signal(spec, _default_variant(**parameter_values), _ohlcv())


def test_session_window_blocks_bars_outside_aligned_grid() -> None:
    ohlcv = _orb_ohlcv([100.0, 102.0, 100.8])
    ohlcv.index = pd.date_range("2026-01-01T00:30:00Z", periods=3, freq="h")
    spec = _spec(entry_groups=[_group("required", "all", [_primitive_condition("RETEST-1", "long")])])
    spec["online_ohlcv_primitives"] = _online_primitives()

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 0.0, 0.0]


def test_opening_range_zero_range_and_missing_bar_fail_closed() -> None:
    zero_range = _orb_ohlcv([100.0, 102.0, 100.8], zero_range_first_bar=True)
    missing_bar = _orb_ohlcv([100.0, 102.0, 100.8])
    missing_bar = missing_bar.drop(missing_bar.index[1])
    spec = _spec(entry_groups=[_group("required", "all", [_primitive_condition("RETEST-1", "long")])])
    spec["online_ohlcv_primitives"] = _online_primitives()

    assert compile_signal(spec, _default_variant(), zero_range).tolist() == [0.0, 0.0, 0.0]
    assert compile_signal(spec, _default_variant(), missing_bar).tolist() == [0.0, 0.0]


def test_candle_shape_ratios_side_specific_and_fail_closed_cases() -> None:
    index = pd.date_range("2026-01-01", periods=6, freq="h", tz="UTC")
    ohlcv = pd.DataFrame(
        {
            "open": [100.0, 109.0, 100.0, 100.0, 100.0, math.nan],
            "high": [110.0, 110.0, 110.0, 100.0, 110.0, 110.0],
            "low": [100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
            "close": [109.0, 100.0, 100.0, 100.0, 104.0, 109.0],
            "volume": [1000.0] * 6,
        },
        index=index,
    )
    spec = _spec(
        direction="both",
        entry_groups=[
            _group("required", "all", [_primitive_condition("NO-WICK", "long")], side="long"),
            _group("required", "all", [_primitive_condition("NO-WICK", "short")], side="short"),
        ],
        max_holding_bars=1,
    )
    spec["online_ohlcv_primitives"] = _online_primitives()
    context = compiler._CompileContext(
        strategy_spec=spec,
        variant_assignment=_default_variant(),
        ohlcv=ohlcv,
        catalog=compiler._load_default_catalog(),
    )

    long_shape = compiler._resolve_operand(_primitive_ref("NO-WICK", "long"), context)
    short_shape = compiler._resolve_operand(_primitive_ref("NO-WICK", "short"), context)
    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert long_shape.tolist() == [True, False, False, False, False, False]
    assert short_shape.tolist() == [False, True, False, False, False, False]
    assert signal.tolist()[:3] == [1.0, 0.0, 0.0]


def test_composed_depth_three_example_with_primitive_ref_compiles_causally() -> None:
    ohlcv = _orb_ohlcv([100.0, 102.0, 100.8, 100.7])
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [],
                subgroups=[
                    _group(
                        "required",
                        "all",
                        [],
                        subgroups=[
                            _group("required", "all", [_primitive_condition("RETEST-1", "long")])
                        ],
                    )
                ],
            )
        ]
    )
    spec["online_ohlcv_primitives"] = _online_primitives()

    base_signal = compile_signal(spec, _default_variant(), ohlcv)
    mutated = ohlcv.copy()
    mutated.iloc[3, mutated.columns.get_loc("close")] = 500.0
    mutated_signal = compile_signal(spec, _default_variant(), mutated)

    assert base_signal.iloc[2] == 1.0
    pd.testing.assert_series_equal(base_signal.iloc[:3], mutated_signal.iloc[:3])


def test_session_end_exit_fires_only_on_deterministic_final_session_bar_close() -> None:
    ohlcv = _orb_ohlcv([100.0] * 24)
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [_condition(_operand("data_ref", "close", "close"), "gt", _operand("constant", 0.0))],
            )
        ],
    )
    spec["online_ohlcv_primitives"] = _online_primitives()
    spec["exit_logic"]["time_exit"] = _session_end_exit()

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == ([1.0] * 23) + [0.0]


def test_both_direction_session_end_exit_uses_same_signal_values() -> None:
    ohlcv = _orb_ohlcv([100.0] * 24)
    spec = _both_direction_spec(
        long_entry=_condition(
            _operand("data_ref", "close", "close"),
            "gt",
            _operand("constant", 0.0),
        ),
        short_entry=_condition(
            _operand("data_ref", "close", "close"),
            "lt",
            _operand("constant", 0.0),
        ),
    )
    spec["online_ohlcv_primitives"] = _online_primitives()
    spec["exit_logic"]["time_exit"] = _session_end_exit()

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == ([1.0] * 23) + [0.0]


def test_session_end_exit_fails_closed_for_incomplete_session() -> None:
    ohlcv = _orb_ohlcv([100.0] * 23)
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [_condition(_operand("data_ref", "close", "close"), "gt", _operand("constant", 0.0))],
            )
        ],
    )
    spec["online_ohlcv_primitives"] = _online_primitives()
    spec["exit_logic"]["time_exit"] = _session_end_exit()

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [1.0] * 23


def test_fixed_r_target_exits_only_on_close_confirmed_reach() -> None:
    ohlcv = _orb_ohlcv([100.0, 102.0, 100.8, 104.5])
    spec = _spec(entry_groups=[_group("required", "all", [_primitive_condition("ORB-1", "long")])])
    spec["online_ohlcv_primitives"] = _online_primitives()
    spec["exit_logic"]["opening_range_opposite_side"] = _opening_range_opposite_side()
    spec["exit_logic"]["fixed_R_target"] = _fixed_r_target(r_multiple=2.0)

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 1.0, 1.0, 0.0]


def test_fixed_r_target_does_not_use_high_low_touch_or_intrabar_ordering() -> None:
    ohlcv = _orb_ohlcv([100.0, 102.0, 100.8, 100.9])
    ohlcv.iloc[2, ohlcv.columns.get_loc("high")] = 200.0
    ohlcv.iloc[3, ohlcv.columns.get_loc("high")] = 200.0
    spec = _spec(entry_groups=[_group("required", "all", [_primitive_condition("ORB-1", "long")])])
    spec["online_ohlcv_primitives"] = _online_primitives()
    spec["exit_logic"]["opening_range_opposite_side"] = _opening_range_opposite_side()
    spec["exit_logic"]["fixed_R_target"] = _fixed_r_target(r_multiple=2.0)

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 1.0, 1.0, 1.0]


def test_fixed_r_target_fails_closed_when_r_base_is_non_positive() -> None:
    ohlcv = _orb_ohlcv([100.0, 102.0, 98.0, 90.0])
    ohlcv.iloc[3, ohlcv.columns.get_loc("open")] = 102.0
    spec = _spec(entry_groups=[_group("required", "all", [_primitive_condition("ORB-1", "short")])], direction="short")
    spec["online_ohlcv_primitives"] = _online_primitives()
    spec["exit_logic"]["opening_range_opposite_side"] = _opening_range_opposite_side()
    spec["exit_logic"]["fixed_R_target"] = _fixed_r_target(r_multiple=1.0)

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 0.0, -1.0, -1.0]


def test_opening_range_opposite_side_stop_is_close_confirmed_only() -> None:
    ohlcv = _orb_ohlcv([100.0, 102.0, 100.8, 98.9])
    ohlcv.iloc[2, ohlcv.columns.get_loc("low")] = 1.0
    spec = _spec(entry_groups=[_group("required", "all", [_primitive_condition("ORB-1", "long")])])
    spec["online_ohlcv_primitives"] = _online_primitives()
    spec["exit_logic"]["opening_range_opposite_side"] = _opening_range_opposite_side()

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, 1.0, 1.0, 0.0]


def test_opening_range_opposite_side_stop_handles_short_side() -> None:
    ohlcv = _orb_ohlcv([100.0, 98.0, 100.2, 101.2])
    spec = _spec(
        direction="short",
        entry_groups=[_group("required", "all", [_primitive_condition("ORB-1", "short")])],
    )
    spec["online_ohlcv_primitives"] = _online_primitives()
    spec["exit_logic"]["opening_range_opposite_side"] = _opening_range_opposite_side()

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [0.0, -1.0, -1.0, 0.0]


def test_opening_range_opposite_side_zero_range_fails_closed() -> None:
    ohlcv = _orb_ohlcv([100.0, 102.0, 98.0], zero_range_first_bar=True)
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [_condition(_operand("data_ref", "close", "close"), "gt", _operand("constant", 0.0))],
            )
        ],
    )
    spec["online_ohlcv_primitives"] = _online_primitives()
    spec["exit_logic"]["opening_range_opposite_side"] = _opening_range_opposite_side()
    spec["exit_logic"]["fixed_R_target"] = _fixed_r_target(r_multiple=1.0)

    signal = compile_signal(spec, _default_variant(), ohlcv)

    assert signal.tolist() == [1.0, 1.0, 1.0]


def test_close_only_exit_primitives_reject_invalid_closed_grammar() -> None:
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [_condition(_operand("data_ref", "close", "close"), "gt", _operand("constant", 0.0))],
            )
        ],
    )
    spec["online_ohlcv_primitives"] = _online_primitives()
    spec["exit_logic"]["time_exit"] = _session_end_exit()
    spec["exit_logic"]["time_exit"]["session_end"]["fill_timing"] = "intrabar"

    with pytest.raises(SpecSignalCompilerError, match="fill_timing"):
        compile_signal(spec, _default_variant(), _orb_ohlcv([100.0] * 24))


def test_close_only_exit_primitives_reject_forbidden_executable_key() -> None:
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [_condition(_operand("data_ref", "close", "close"), "gt", _operand("constant", 0.0))],
            )
        ],
    )
    spec["online_ohlcv_primitives"] = _online_primitives()
    spec["exit_logic"]["opening_range_opposite_side"] = _opening_range_opposite_side()
    spec["exit_logic"]["opening_range_opposite_side"]["eval"] = "close <= or_low"

    with pytest.raises(SpecSignalCompilerError, match="forbidden executable"):
        compile_signal(spec, _default_variant(), _orb_ohlcv([100.0, 102.0, 98.0]))
