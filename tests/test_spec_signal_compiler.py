from __future__ import annotations

import inspect
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


def _group(role: str, logic: str, conditions: list[dict], subgroups: list[dict] | None = None) -> dict:
    return {
        "group_id": f"G-{role}-{logic}",
        "group_role": role,
        "logic": logic,
        "conditions": conditions,
        "subgroups": subgroups or [],
        "notes": None,
    }


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


def test_rejects_unsupported_closed_operators() -> None:
    ohlcv = _ohlcv()
    spec = _spec(
        entry_groups=[
            _group(
                "required",
                "all",
                [
                    _condition(
                        _operand("data_ref", "close", "close"),
                        "crosses_above",
                        _operand("constant", 12.0),
                    )
                ],
            )
        ],
    )

    with pytest.raises(UnsupportedSpecSignalCompilerFeature, match="crosses_above"):
        compile_signal(spec, _default_variant(), ohlcv)


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


def test_rejects_both_direction_in_first_slice() -> None:
    with pytest.raises(UnsupportedSpecSignalCompilerFeature, match="'both'"):
        compile_signal(_spec(direction="both"), _default_variant(), _ohlcv())


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
