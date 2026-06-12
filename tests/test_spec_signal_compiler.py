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
) -> dict:
    return {
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


def test_stddev_v1_uses_locked_ddof_convention() -> None:
    result_ddof0 = compiler._stddev_v1(pd.Series([1.0, 2.0, 3.0]), 3, ddof=0)
    result_ddof1 = compiler._stddev_v1(pd.Series([1.0, 2.0, 3.0]), 3, ddof=1)

    assert math.isnan(result_ddof0.iloc[0])
    assert math.isnan(result_ddof0.iloc[1])
    assert result_ddof0.iloc[2] == pytest.approx(math.sqrt(2.0 / 3.0))
    assert result_ddof1.iloc[2] == pytest.approx(1.0)


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


@pytest.mark.parametrize("operator", ["in_set", "is_true", "is_false"])
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
