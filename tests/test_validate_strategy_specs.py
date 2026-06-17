import json
import inspect
import sys
from pathlib import Path

from jsonschema import Draft7Validator

from tools.registry import validate_strategy_specs as validator_module
from tools.registry.validate_strategy_specs import (
    DEFAULT_SCHEMA_PATH,
    main,
    validate_strategy_specs,
)


def _load_schema(path: Path = DEFAULT_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _operand(ref="close") -> dict:
    return {
        "operand_type": "data_ref",
        "ref": ref,
        "field": "close",
        "timeframe": "1h",
        "lookback": {"bars": 1},
    }


def _standard_operand(operand_type: str, ref, field=None, lookback=None) -> dict:
    return {
        "operand_type": operand_type,
        "ref": ref,
        "field": field,
        "timeframe": None,
        "lookback": lookback,
    }


def _composed_operand(
    *,
    base_operand_type: str = "indicator_ref",
    parameter_operand_type: str = "parameter_ref",
    composition_type: str = "scale_by_one_minus_parameter",
    parameter_ref: str = "entry_distance_threshold",
) -> dict:
    return {
        "operand_type": "composed_operand",
        "composition_type": composition_type,
        "base_operand": _standard_operand(
            base_operand_type,
            "sma" if base_operand_type == "indicator_ref" else "close",
            "value" if base_operand_type == "indicator_ref" else "close",
            {"bars": 20} if base_operand_type == "indicator_ref" else None,
        ),
        "parameter_operand": _standard_operand(parameter_operand_type, parameter_ref),
    }


def _z_score_operand(
    *,
    value_operand_type: str = "data_ref",
    center_operand_type: str = "indicator_ref",
    scale_operand_type: str = "indicator_ref",
    zero_scale_policy: str = "null_output",
) -> dict:
    def child(operand_type: str, ref: str) -> dict:
        return _standard_operand(
            operand_type,
            ref,
            "value" if operand_type == "indicator_ref" else "close",
            {"bars": 20} if operand_type == "indicator_ref" else None,
        )

    return {
        "operand_type": "composed_operand",
        "composition_type": "z_score",
        "value_operand": child(value_operand_type, "sma" if value_operand_type == "indicator_ref" else "close"),
        "center_operand": child(center_operand_type, "sma" if center_operand_type == "indicator_ref" else "close"),
        "scale_operand": child(scale_operand_type, "stddev" if scale_operand_type == "indicator_ref" else "close"),
        "zero_scale_policy": zero_scale_policy,
    }


def _atr_stop(
    *,
    atr_lookback=14,
    atr_multiplier=2.5,
    entry_reference_price="next_bar_open_pre_fee_slippage",
    evaluation_price="close",
    evaluation_timing="bar_close",
    enabled=True,
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


def _fixed_r_target(r_multiple=2.0) -> dict:
    return {
        "enabled": True,
        "r_multiple": r_multiple,
        "entry_reference_price": "next_bar_open_pre_fee_slippage",
        "stop_ref": "opening_range_opposite_side",
        "evaluation_price": "close",
        "evaluation_timing": "bar_close",
        "same_bar_stop_target_policy": "defer_intrabar_realism",
    }


def _condition(condition_id: str = "COND-1", operator: str = "gt") -> dict:
    return {
        "condition_id": condition_id,
        "condition_role": "required",
        "left_operand": _operand("close"),
        "operator": operator,
        "right_operand": {
            "operand_type": "constant",
            "ref": 100.0,
            "field": None,
            "timeframe": None,
            "lookback": None,
        },
        "units": None,
        "notes": None,
    }


def _primitive_ref(ref: str, field: str) -> dict:
    return {
        "operand_type": "primitive_ref",
        "ref": ref,
        "field": field,
        "timeframe": None,
        "lookback": None,
    }


def _online_primitives() -> dict:
    tolerance = {
        "mode": "atr_multiple",
        "atr_lookback_bars": 1,
        "multiple": 0.0,
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
                "window": {"min_bars_after_breakout": 1, "max_bars_after_breakout": 3},
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
                "upper_wick_pct": {
                    "operator": "lte",
                    "value": 0.1,
                    "units": "fraction_of_range",
                },
                "lower_wick_pct": {
                    "operator": "lte",
                    "value": 0.1,
                    "units": "fraction_of_range",
                },
                "body_pct": {
                    "operator": "gte",
                    "value": 0.6,
                    "units": "fraction_of_range",
                },
                "side_mode": "side_specific",
            }
        ],
    }


def _group(group_id: str = "GROUP-1", subgroups: list | None = None, side: str | None = None) -> dict:
    group = {
        "group_id": group_id,
        "group_role": "required",
        "logic": "all",
        "conditions": [_condition()],
        "subgroups": subgroups or [],
        "notes": None,
    }
    if side is not None:
        group["side"] = side
    return group


def _parameter(name: str = "lookback") -> dict:
    return {
        "name": name,
        "label": None,
        "description": None,
        "type": "integer",
        "units": "bars",
        "default": 20,
        "range": {
            "min": 5,
            "max": 50,
            "step": 5,
            "inclusive_min": True,
            "inclusive_max": True,
        },
        "allowed_values": [],
        "is_free_parameter": True,
        "included_in_variant_generation": True,
        "role": "entry",
        "rationale": "Pytest fixture parameter.",
        "constraints": [],
    }


def _lookback_parameter(
    *,
    name: str = "lookback_n",
    parameter_type: str = "integer",
    default=20,
    range_value: dict | None = None,
    allowed_values: list | None = None,
    included_in_variant_generation: bool = True,
) -> dict:
    parameter = _parameter(name)
    parameter.update(
        {
            "type": parameter_type,
            "default": default,
            "range": {
                "min": 5,
                "max": 50,
                "step": 5,
                "inclusive_min": True,
                "inclusive_max": True,
            }
            if range_value is None
            else range_value,
            "allowed_values": [] if allowed_values is None else allowed_values,
            "included_in_variant_generation": included_in_variant_generation,
        }
    )
    return parameter


def _threshold_parameter(
    *,
    name: str = "entry_distance_threshold",
    parameter_type: str = "number",
    role: str = "entry",
    included_in_variant_generation: bool = True,
    range_value: dict | None = None,
    allowed_values: list | None = None,
) -> dict:
    parameter = _parameter(name)
    parameter.update(
        {
            "type": parameter_type,
            "units": "ratio",
            "default": 0.05,
            "range": {
                "min": 0.01,
                "max": 0.20,
                "step": 0.01,
                "inclusive_min": True,
                "inclusive_max": True,
            }
            if range_value is None
            else range_value,
            "allowed_values": [] if allowed_values is None else allowed_values,
            "included_in_variant_generation": included_in_variant_generation,
            "role": role,
        }
    )
    return parameter


def _true_flags(*names: str) -> dict:
    return {name: True for name in names}


def _base_strategy_spec(strategy_spec_id: str = "STRAT-SPEC-9001") -> dict:
    return {
        "schema_version": "v1",
        "strategy_spec_id": strategy_spec_id,
        "title": "Pytest Strategy Spec",
        "status": "draft",
        "non_execution_declaration": _true_flags(
            "human_review_surface_only",
            "not_executable",
            "not_runtime_authority",
            "not_paper_live_authority",
            "not_gate_authority",
            "not_candidate_approval",
            "not_exp_approval",
            "not_sweep_authority",
            "not_ranking_authority",
            "not_recommendation_authority",
            "not_readiness_authority",
            "not_transition_authority",
        ),
        "provenance": {
            "source_type": "manual_idea",
            "source_refs": ["pytest-fixture"],
            "prepared_by": "pytest",
            "created_at": "2026-06-01T00:00:00Z",
            "updated_at": "2026-06-01T00:00:00Z",
            "rationale": "Pytest fixture.",
            "source_constraints": [],
            "unresolved_claims": [],
        },
        "instruments": {
            "symbols": ["BTCUSDT"],
            "instrument_family": "crypto_perp",
            "venue_assumption": "Binance USDT-M",
            "market_type": "perpetual",
            "directions_allowed": ["long"],
            "leverage_assumption": None,
            "exchange_constraint_refs": [],
            "blockers": [],
        },
        "timeframe_and_data": {
            "primary_timeframe": "1h",
            "confirmation_timeframes": [],
            "host_data_refs": [
                {
                    "stream": "ohlcv",
                    "timeframe": "1h",
                    "field": "close",
                    "availability": "required",
                }
            ],
            "gap_handling_assumption": None,
            "missing_data_blockers": [],
        },
        "entry_logic": {
            "direction": "long",
            "groups": [_group()],
            "notes": None,
        },
        "exit_logic": {
            "groups": [],
            "max_holding_period": {"enabled": False, "bars": None},
            "notes": None,
        },
        "risk_model": {
            "sizing_intent": "review_only",
            "exposure_limits": [],
            "stop_distance": None,
            "target_distance": None,
            "leverage_visibility": None,
            "liquidation_sensitivity_notes": None,
        },
        "filters": {
            "groups": [],
            "none_declared": True,
        },
        "free_parameters": {
            "max_free_parameters": 5,
            "counting_rule": (
                "parameters contains only entries where is_free_parameter=true; "
                "maxItems 5 enforces the D2-006-style MVP free-parameter cap"
            ),
            "parameters": [],
            "no_free_parameters_declared": True,
        },
        "constraints": {
            "invalid_parameter_combinations": [],
            "unavailable_data_blockers": [],
            "deferred_pattern_blockers": [],
            "none_declared": True,
        },
        "review": {
            "human_review_required": True,
            "reviewer": None,
            "reviewed_at": None,
            "review_notes": [],
            "approval_scope": "none",
            "non_authority_acknowledgement": _true_flags(
                "not_candidate_approval",
                "not_exp_approval",
                "not_sweep_authority",
                "not_ranking_authority",
                "not_recommendation_authority",
                "not_readiness_authority",
                "not_transition_authority",
                "not_runtime_authority",
                "not_paper_live_authority",
                "not_gate_satisfaction",
            ),
        },
        "lineage": {
            "parent_refs": [],
            "supersedes": [],
            "amendment_of": None,
        },
        "hash_pinning": {
            "canonical_spec_hash": None,
            "hash_algorithm": None,
            "hash_scope_version": None,
            "hash_scope": [],
            "hash_status": "not_computed",
        },
        "pre_registration_support": {
            "intended_for_variant_manifest": False,
            "variant_manifest_ref": None,
            "frozen_snapshot_ref": None,
        },
        "backtest_realism_assumptions": {
            "fee_side_assumption": None,
            "exchange_constraints_disclosed": False,
            "funding_notional_mode": "unspecified",
            "slippage_model": "unspecified",
            "fill_mode": "unspecified",
            "order_size_assumption": None,
            "liquidity_capacity_assumption": None,
            "liquidation_mode": "unspecified",
            "maintenance_margin_assumption": None,
            "mark_price_source": "unspecified",
            "bar_path_assumption": "unspecified",
        },
        "max_condition_group_depth": 3,
    }


def _both_direction_strategy_spec() -> dict:
    payload = _base_strategy_spec()
    payload["instruments"]["directions_allowed"] = ["long", "short"]
    payload["entry_logic"] = {
        "direction": "both",
        "groups": [
            _group("GROUP-LONG", side="long"),
            _group("GROUP-SHORT", side="short"),
        ],
        "notes": None,
    }
    return payload


def _strategy_spec_with_composed_operand(**operand_kwargs) -> dict:
    payload = _base_strategy_spec()
    payload["entry_logic"]["groups"][0]["conditions"][0]["right_operand"] = _composed_operand(
        **operand_kwargs
    )
    payload["free_parameters"]["parameters"] = [_threshold_parameter()]
    payload["free_parameters"]["no_free_parameters_declared"] = False
    return payload


def _strategy_spec_with_z_score_operand(**operand_kwargs) -> dict:
    payload = _base_strategy_spec()
    payload["entry_logic"]["groups"][0]["conditions"][0]["left_operand"] = _z_score_operand(
        **operand_kwargs
    )
    payload["entry_logic"]["groups"][0]["conditions"][0]["operator"] = "lte"
    payload["entry_logic"]["groups"][0]["conditions"][0]["right_operand"] = _standard_operand(
        "constant",
        -1.0,
    )
    return payload


def _strategy_spec_with_parameter_bound_lookback(*, inside_composed_base: bool = False) -> dict:
    payload = _base_strategy_spec()
    indicator_operand = _standard_operand(
        "indicator_ref",
        "sma",
        "value",
        {"bars_parameter_ref": "lookback_n"},
    )
    if inside_composed_base:
        payload["entry_logic"]["groups"][0]["conditions"][0]["right_operand"] = _composed_operand()
        payload["entry_logic"]["groups"][0]["conditions"][0]["right_operand"]["base_operand"] = (
            indicator_operand
        )
        payload["free_parameters"]["parameters"] = [
            _threshold_parameter(),
            _lookback_parameter(),
        ]
    else:
        payload["entry_logic"]["groups"][0]["conditions"][0]["right_operand"] = indicator_operand
        payload["free_parameters"]["parameters"] = [_lookback_parameter()]
    payload["free_parameters"]["no_free_parameters_declared"] = False
    return payload


def _validate(
    tmp_path: Path,
    payload: dict,
    filename: str = "STRAT-SPEC-9001.strategy_spec.json",
) -> list[str]:
    strategy_specs_dir = tmp_path / "research" / "strategy_specs"
    _write_json(strategy_specs_dir / filename, payload)
    return validate_strategy_specs(strategy_specs_dir=strategy_specs_dir)


def test_strategy_spec_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_strategy_spec_validator_noops_when_directory_missing(tmp_path):
    errors = validate_strategy_specs(strategy_specs_dir=tmp_path / "research" / "strategy_specs")

    assert errors == []


def test_strategy_spec_validator_noops_when_directory_empty(tmp_path):
    strategy_specs_dir = tmp_path / "research" / "strategy_specs"
    strategy_specs_dir.mkdir(parents=True)

    errors = validate_strategy_specs(strategy_specs_dir=strategy_specs_dir)

    assert errors == []


def test_valid_temp_strategy_spec_passes(tmp_path):
    assert _validate(tmp_path, _base_strategy_spec()) == []


def test_both_direction_accepts_explicit_long_and_short_entry_groups(tmp_path):
    payload = _both_direction_strategy_spec()
    schema = _load_schema()

    assert Draft7Validator(schema).is_valid(payload)
    assert _validate(tmp_path, payload) == []


def test_both_direction_accepts_side_specific_exit_groups(tmp_path):
    payload = _both_direction_strategy_spec()
    payload["exit_logic"]["groups"] = [
        _group("EXIT-LONG", side="long"),
        _group("EXIT-SHORT", side="short"),
    ]

    assert _validate(tmp_path, payload) == []


def test_long_direction_existing_shape_without_side_labels_still_valid(tmp_path):
    payload = _base_strategy_spec()
    payload["entry_logic"]["direction"] = "long"

    assert _validate(tmp_path, payload) == []


def test_short_direction_existing_shape_without_side_labels_still_valid(tmp_path):
    payload = _base_strategy_spec()
    payload["instruments"]["directions_allowed"] = ["short"]
    payload["entry_logic"]["direction"] = "short"

    assert _validate(tmp_path, payload) == []


def test_both_direction_rejects_missing_long_entry_side(tmp_path):
    payload = _both_direction_strategy_spec()
    payload["entry_logic"]["groups"] = [_group("GROUP-SHORT", side="short")]

    errors = _validate(tmp_path, payload)

    assert any("requires at least one 'long' root entry group" in error for error in errors)


def test_both_direction_rejects_missing_short_entry_side(tmp_path):
    payload = _both_direction_strategy_spec()
    payload["entry_logic"]["groups"] = [_group("GROUP-LONG", side="long")]

    errors = _validate(tmp_path, payload)

    assert any("requires at least one 'short' root entry group" in error for error in errors)


def test_both_direction_rejects_entry_group_without_side(tmp_path):
    payload = _both_direction_strategy_spec()
    del payload["entry_logic"]["groups"][0]["side"]

    errors = _validate(tmp_path, payload)

    assert any("entry_logic.groups.0.side must be one of" in error for error in errors)


def test_both_direction_rejects_unknown_side_label(tmp_path):
    payload = _both_direction_strategy_spec()
    payload["entry_logic"]["groups"][0]["side"] = "up"

    errors = _validate(tmp_path, payload)

    assert any("entry_logic.groups.0.side" in error and "up" in error for error in errors)


def test_both_direction_rejects_unlabeled_exit_group(tmp_path):
    payload = _both_direction_strategy_spec()
    payload["exit_logic"]["groups"] = [_group("EXIT-UNLABELED")]

    errors = _validate(tmp_path, payload)

    assert any("exit_logic.groups.0.side must be one of" in error for error in errors)


def test_both_direction_rejects_filter_side_label(tmp_path):
    payload = _both_direction_strategy_spec()
    payload["filters"]["groups"] = [_group("FILTER-LONG", side="long")]
    payload["filters"]["none_declared"] = False

    errors = _validate(tmp_path, payload)

    assert any("filters.groups.0.side is not allowed under filters.groups" in error for error in errors)


def test_trend_and_regime_filter_entry_gates_pass_schema_and_validator(tmp_path):
    schema = _load_schema()
    for group_role in ("trend", "regime"):
        payload = _base_strategy_spec(f"STRAT-SPEC-90{len(group_role)}1")
        payload["filters"]["groups"] = [_group(f"FILTER-{group_role.upper()}")]
        payload["filters"]["groups"][0]["group_role"] = group_role
        payload["filters"]["groups"][0]["conditions"][0]["condition_role"] = "filter"
        payload["filters"]["none_declared"] = False

        assert Draft7Validator(schema).is_valid(payload), group_role
        assert _validate(
            tmp_path,
            payload,
            filename=f"{payload['strategy_spec_id']}.strategy_spec.json",
        ) == []


def test_unknown_trend_regime_filter_gate_type_fails_schema_and_validator(tmp_path):
    payload = _base_strategy_spec()
    payload["filters"]["groups"] = [_group("FILTER-UNKNOWN")]
    payload["filters"]["groups"][0]["group_role"] = "trend_regime_expression"
    payload["filters"]["groups"][0]["conditions"][0]["condition_role"] = "filter"
    payload["filters"]["none_declared"] = False

    errors = _validate(tmp_path, payload)

    assert any("group_role" in error and "trend_regime_expression" in error for error in errors)


def test_trend_filter_gate_forbidden_executable_key_fails_validator(tmp_path):
    payload = _base_strategy_spec()
    payload["filters"]["groups"] = [_group("FILTER-TREND")]
    payload["filters"]["groups"][0]["group_role"] = "trend"
    payload["filters"]["groups"][0]["conditions"][0]["condition_role"] = "filter"
    payload["filters"]["groups"][0]["conditions"][0]["right_operand"]["formula"] = "sma(close, 20)"
    payload["filters"]["none_declared"] = False

    errors = _validate(tmp_path, payload)

    assert any("forbidden executable key name" in error and "formula" in error for error in errors)


def test_entry_controls_min_bars_between_entries_passes_schema_and_validator(tmp_path):
    payload = _base_strategy_spec()
    payload["entry_logic"]["entry_controls"] = {"min_bars_between_entries": 12}

    errors = _validate(tmp_path, payload)

    assert Draft7Validator(_load_schema()).is_valid(payload)
    assert errors == []


def test_entry_controls_max_trades_per_session_passes_schema_and_validator(tmp_path):
    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["entry_logic"]["entry_controls"] = {
        "max_trades_per_session": {
            "enabled": True,
            "count_basis": "entries_filled",
            "max_trades": 1,
            "session_ref": "UTC_DAILY_0000",
            "reset": "session_start",
        }
    }

    errors = _validate(tmp_path, payload)

    assert Draft7Validator(_load_schema()).is_valid(payload)
    assert errors == []


def test_valid_online_ohlcv_primitives_pass_schema_and_validator(tmp_path):
    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["entry_logic"]["entry_controls"] = {
        "min_bars_between_entries": 1,
        "max_trades_per_session": {
            "enabled": True,
            "count_basis": "entries_filled",
            "max_trades": 1,
            "session_ref": "UTC_DAILY_0000",
            "reset": "session_start",
        },
    }
    payload["entry_logic"]["groups"][0]["conditions"][0]["left_operand"] = _primitive_ref(
        "RETEST-1",
        "long",
    )
    payload["entry_logic"]["groups"][0]["conditions"][0]["operator"] = "is_true"

    schema = _load_schema()

    assert Draft7Validator(schema).is_valid(payload)
    assert _validate(tmp_path, payload) == []


def test_online_ohlcv_primitive_parameter_refs_pass_schema_and_validator(tmp_path):
    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["free_parameters"]["parameters"] = [
        _threshold_parameter(name="wick_threshold", allowed_values=[0.05, 0.1]),
        _threshold_parameter(name="body_threshold", allowed_values=[0.6, 0.8]),
        _threshold_parameter(name="orb_tolerance", allowed_values=[0.0, 0.25]),
        _lookback_parameter(name="retest_window", allowed_values=[2, 3]),
        _threshold_parameter(name="target_r", role="exit", range_value={"min": 1.0, "max": 3.0, "step": 1.0, "inclusive_min": True, "inclusive_max": True}, allowed_values=[1.0, 2.0]),
    ]
    payload["free_parameters"]["no_free_parameters_declared"] = False
    primitives = payload["online_ohlcv_primitives"]
    primitives["candle_shapes"][0]["upper_wick_pct"]["value"] = {"parameter_ref": "wick_threshold"}
    primitives["candle_shapes"][0]["lower_wick_pct"]["value"] = {"parameter_ref": "wick_threshold"}
    primitives["candle_shapes"][0]["body_pct"]["value"] = {"parameter_ref": "body_threshold"}
    primitives["opening_range_breakouts"][0]["tolerance"]["multiple"] = {"parameter_ref": "orb_tolerance"}
    primitives["opening_range_retests"][0]["window"]["max_bars_after_breakout"] = {"parameter_ref": "retest_window"}
    primitives["opening_range_retests"][0]["tolerance"]["multiple"] = {"parameter_ref": "orb_tolerance"}
    payload["entry_logic"]["entry_controls"] = {
        "max_trades_per_session": {
            "enabled": True,
            "count_basis": "entries_filled",
            "max_trades": {"parameter_ref": "retest_window"},
            "session_ref": "UTC_DAILY_0000",
            "reset": "session_start",
        }
    }
    payload["exit_logic"]["opening_range_opposite_side"] = _opening_range_opposite_side()
    payload["exit_logic"]["fixed_R_target"] = _fixed_r_target({"parameter_ref": "target_r"})

    errors = _validate(tmp_path, payload)

    assert Draft7Validator(_load_schema()).is_valid(payload)
    assert errors == []


def test_online_ohlcv_primitive_parameter_refs_reject_invalid_sources(tmp_path):
    cases = []

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["online_ohlcv_primitives"]["candle_shapes"][0]["upper_wick_pct"]["value"] = {
        "parameter_ref": "missing"
    }
    cases.append((payload, "must match exactly one free_parameters"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["free_parameters"]["parameters"] = [_threshold_parameter(name="wick_threshold")]
    payload["free_parameters"]["no_free_parameters_declared"] = False
    payload["online_ohlcv_primitives"]["candle_shapes"][0]["upper_wick_pct"]["value"] = {
        "parameter_ref": "wick_threshold"
    }
    cases.append((payload, "allowed_values must be non-empty"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["free_parameters"]["parameters"] = [
        _threshold_parameter(name="wick_threshold", allowed_values=[0.1])
    ]
    payload["free_parameters"]["no_free_parameters_declared"] = False
    payload["online_ohlcv_primitives"]["candle_shapes"][0]["upper_wick_pct"]["value"] = {
        "parameter_ref": "wick_threshold",
        "expression": "x + 1",
    }
    cases.append((payload, "expression"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["free_parameters"]["parameters"] = [
        _threshold_parameter(name="wick_threshold", parameter_type="integer", allowed_values=[1])
    ]
    payload["free_parameters"]["no_free_parameters_declared"] = False
    payload["online_ohlcv_primitives"]["candle_shapes"][0]["upper_wick_pct"]["value"] = {
        "parameter_ref": "wick_threshold"
    }
    cases.append((payload, "type must be 'number'"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["free_parameters"]["parameters"] = [
        _threshold_parameter(name="wick_threshold", allowed_values=[1.5])
    ]
    payload["free_parameters"]["no_free_parameters_declared"] = False
    payload["online_ohlcv_primitives"]["candle_shapes"][0]["upper_wick_pct"]["value"] = {
        "parameter_ref": "wick_threshold"
    }
    cases.append((payload, "must be <= 1"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["free_parameters"]["parameters"] = [
        _lookback_parameter(name="retest_min", allowed_values=[4]),
        _lookback_parameter(name="retest_max", allowed_values=[2]),
    ]
    payload["free_parameters"]["no_free_parameters_declared"] = False
    payload["online_ohlcv_primitives"]["opening_range_retests"][0]["window"] = {
        "min_bars_after_breakout": {"parameter_ref": "retest_min"},
        "max_bars_after_breakout": {"parameter_ref": "retest_max"},
    }
    cases.append((payload, "max_bars_after_breakout must be >= min_bars_after_breakout"))

    for index, (case, expected) in enumerate(cases, start=1):
        case["strategy_spec_id"] = f"STRAT-SPEC-93{index:02d}"
        errors = _validate(tmp_path, case, filename=f"STRAT-SPEC-93{index:02d}.strategy_spec.json")
        assert errors, expected
        assert any(expected in error for error in errors), (expected, errors)


def test_valid_close_only_exit_primitives_pass_schema_and_validator(tmp_path):
    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["exit_logic"]["time_exit"] = _session_end_exit()
    payload["exit_logic"]["opening_range_opposite_side"] = _opening_range_opposite_side()
    payload["exit_logic"]["fixed_R_target"] = _fixed_r_target()

    assert Draft7Validator(_load_schema()).is_valid(payload)
    assert _validate(tmp_path, payload) == []


def test_close_only_exit_primitives_reject_missing_refs_and_invalid_multiple(tmp_path):
    cases = []

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["exit_logic"]["time_exit"] = _session_end_exit("MISSING")
    cases.append((payload, "session_ref must reference a declared session_window"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["exit_logic"]["opening_range_opposite_side"] = _opening_range_opposite_side("MISSING")
    cases.append((payload, "range_ref must reference a declared opening_range"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["exit_logic"]["fixed_R_target"] = _fixed_r_target(0)
    cases.append((payload, "exit_logic.fixed_R_target.r_multiple must be > 0"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["exit_logic"]["fixed_R_target"] = _fixed_r_target()
    cases.append((payload, "requires exit_logic.opening_range_opposite_side"))

    for index, (case, expected) in enumerate(cases, start=1):
        case["strategy_spec_id"] = f"STRAT-SPEC-92{index:02d}"
        errors = _validate(tmp_path, case, filename=f"STRAT-SPEC-92{index:02d}.strategy_spec.json")
        assert any(expected in error for error in errors), (expected, errors)


def test_close_only_exit_primitives_reject_unknown_units_and_executable_keys(tmp_path):
    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["exit_logic"]["time_exit"] = _session_end_exit()
    payload["exit_logic"]["time_exit"]["session_end"]["fill_timing"] = "intrabar"
    payload["exit_logic"]["opening_range_opposite_side"] = _opening_range_opposite_side()
    payload["exit_logic"]["opening_range_opposite_side"]["lambda"] = "close <= or_low"

    errors = _validate(tmp_path, payload)

    assert any("intrabar" in error for error in errors)
    assert any("forbidden executable key name" in error and "lambda" in error for error in errors)
    assert any("opening_range_opposite_side supports exactly" in error for error in errors)


def test_online_ohlcv_primitives_reject_invalid_closed_forms(tmp_path):
    cases = []

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["online_ohlcv_primitives"]["session_windows"][0]["timezone"] = "America/New_York"
    cases.append((payload, "timezone"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["online_ohlcv_primitives"]["session_windows"][0]["anchor_time"] = "24:00"
    cases.append((payload, "anchor_time"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["online_ohlcv_primitives"]["session_windows"][0]["duration"]["units"] = "hour"
    cases.append((payload, "duration"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["online_ohlcv_primitives"]["opening_ranges"][0]["session_ref"] = "MISSING"
    cases.append((payload, "session_ref"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["online_ohlcv_primitives"]["opening_range_breakouts"][0]["tolerance"]["mode"] = "expression"
    cases.append((payload, "tolerance"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["online_ohlcv_primitives"]["opening_range_retests"][0]["window"] = {
        "min_bars_after_breakout": 4,
        "max_bars_after_breakout": 2,
    }
    cases.append((payload, "max_bars_after_breakout"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["entry_logic"]["entry_controls"] = {
        "min_bars_between_entries": 1,
        "max_trades_per_session": {
            "enabled": True,
            "count_basis": "entries_filled",
            "max_trades": 0,
            "session_ref": "UTC_DAILY_0000",
            "reset": "session_start",
        },
    }
    cases.append((payload, "max_trades"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["online_ohlcv_primitives"]["candle_shapes"][0]["upper_wick_pct"]["operator"] = "execute"
    cases.append((payload, "operator"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["online_ohlcv_primitives"]["candle_shapes"][0]["formula"] = "close > open"
    cases.append((payload, "formula"))

    payload = _base_strategy_spec()
    payload["online_ohlcv_primitives"] = _online_primitives()
    payload["entry_logic"]["groups"][0]["conditions"][0]["left_operand"] = _primitive_ref("UNKNOWN", "long")
    payload["entry_logic"]["groups"][0]["conditions"][0]["operator"] = "is_true"
    cases.append((payload, "unknown primitive"))

    for index, (case, expected) in enumerate(cases, start=1):
        case["strategy_spec_id"] = f"STRAT-SPEC-91{index:02d}"
        errors = _validate(tmp_path, case, filename=f"STRAT-SPEC-91{index:02d}.strategy_spec.json")
        assert errors, expected
        assert any(expected in error for error in errors), (expected, errors)


def test_entry_controls_unknown_key_fails_schema_and_validator(tmp_path):
    payload = _base_strategy_spec()
    payload["entry_logic"]["entry_controls"] = {"cooldown_bars_after_exit": 12}

    errors = _validate(tmp_path, payload)

    assert not Draft7Validator(_load_schema()).is_valid(payload)
    assert any("entry_controls" in error and "cooldown_bars_after_exit" in error for error in errors)


def test_entry_controls_malformed_min_bars_fails_schema_and_validator(tmp_path):
    for value in (None, 0, 1.5, True, 100001):
        payload = _base_strategy_spec()
        payload["entry_logic"]["entry_controls"] = {"min_bars_between_entries": value}

        errors = _validate(tmp_path, payload)

        assert not Draft7Validator(_load_schema()).is_valid(payload)
        assert errors


def test_entry_controls_forbidden_executable_key_fails_validator(tmp_path):
    payload = _base_strategy_spec()
    payload["entry_logic"]["entry_controls"] = {
        "min_bars_between_entries": 12,
        "lambda": "x",
    }

    errors = _validate(tmp_path, payload)

    assert any("forbidden executable key name" in error and "lambda" in error for error in errors)


def test_valid_atr_stop_passes_schema_and_validator(tmp_path):
    payload = _base_strategy_spec()
    payload["exit_logic"]["atr_stop"] = _atr_stop()
    schema = _load_schema()

    assert Draft7Validator(schema).is_valid(payload)
    assert _validate(tmp_path, payload) == []


def test_absent_atr_stop_preserves_existing_schema_and_validator(tmp_path):
    payload = _base_strategy_spec()
    schema = _load_schema()

    assert "atr_stop" not in payload["exit_logic"]
    assert Draft7Validator(schema).is_valid(payload)
    assert _validate(tmp_path, payload) == []


def test_atr_stop_invalid_multiplier_fails_schema_and_validator(tmp_path):
    payload = _base_strategy_spec()
    payload["exit_logic"]["atr_stop"] = _atr_stop(atr_multiplier=0)

    assert not Draft7Validator(_load_schema()).is_valid(payload)
    errors = _validate(tmp_path, payload)

    assert any("atr_multiplier" in error for error in errors)


def test_atr_stop_nonfinite_multiplier_fails_validator(tmp_path):
    payload = _base_strategy_spec()
    payload["exit_logic"]["atr_stop"] = _atr_stop(atr_multiplier=float("nan"))

    errors = _validate(tmp_path, payload)

    assert any("atr_multiplier must be a finite number" in error for error in errors)


def test_atr_stop_invalid_lookback_fails_schema_and_validator(tmp_path):
    payload = _base_strategy_spec()
    payload["exit_logic"]["atr_stop"] = _atr_stop(atr_lookback=0)

    assert not Draft7Validator(_load_schema()).is_valid(payload)
    errors = _validate(tmp_path, payload)

    assert any("atr_lookback" in error for error in errors)


def test_atr_stop_parameter_ref_requires_declared_parameter(tmp_path):
    payload = _base_strategy_spec()
    payload["exit_logic"]["atr_stop"] = _atr_stop(atr_multiplier={"parameter_ref": "atr_k"})

    assert Draft7Validator(_load_schema()).is_valid(payload)
    errors = _validate(tmp_path, payload)

    assert any("atr_multiplier.parameter_ref 'atr_k' must match exactly" in error for error in errors)


def test_atr_stop_invalid_reference_and_timing_fail_schema_and_validator(tmp_path):
    payload = _base_strategy_spec()
    payload["exit_logic"]["atr_stop"] = _atr_stop(
        entry_reference_price="close",
        evaluation_price="open",
        evaluation_timing="intrabar",
    )

    assert not Draft7Validator(_load_schema()).is_valid(payload)
    errors = _validate(tmp_path, payload)

    assert any("entry_reference_price" in error for error in errors)
    assert any("evaluation_price" in error for error in errors)
    assert any("evaluation_timing" in error for error in errors)


def test_atr_stop_unknown_key_and_executable_key_fail_validator(tmp_path):
    payload = _base_strategy_spec()
    payload["exit_logic"]["atr_stop"] = _atr_stop()
    payload["exit_logic"]["atr_stop"]["lambda"] = "close <= stop"

    errors = _validate(tmp_path, payload)

    assert any("forbidden executable key name" in error and "lambda" in error for error in errors)
    assert any("exit_logic.atr_stop supports exactly" in error for error in errors)


def test_single_direction_rejects_side_labeled_entry_group(tmp_path):
    payload = _base_strategy_spec()
    payload["entry_logic"]["groups"][0]["side"] = "long"

    errors = _validate(tmp_path, payload)

    assert any(
        "entry_logic.groups.0.side is not allowed when entry_logic.direction is 'long'" in error
        for error in errors
    )


def test_single_direction_rejects_side_labeled_exit_group(tmp_path):
    payload = _base_strategy_spec()
    payload["exit_logic"]["groups"] = [_group("EXIT-LONG", side="long")]

    errors = _validate(tmp_path, payload)

    assert any(
        "exit_logic.groups.0.side is not allowed when entry_logic.direction is 'long'" in error
        for error in errors
    )


def test_both_direction_rejects_nested_side_contradiction_if_nested_side_labels_are_supported(
    tmp_path,
):
    payload = _both_direction_strategy_spec()
    payload["entry_logic"]["groups"][0]["subgroups"] = [
        _group("GROUP-LONG-NESTED", side="short")
    ]

    errors = _validate(tmp_path, payload)

    assert any("contradicts root side 'long'" in error for error in errors)


def test_both_direction_preserves_condition_group_depth_limit(tmp_path):
    payload = _both_direction_strategy_spec()
    depth_4 = _group("GROUP-4")
    depth_3 = _group("GROUP-3", [depth_4])
    depth_2 = _group("GROUP-2", [depth_3])
    payload["entry_logic"]["groups"][0]["subgroups"] = [depth_2]

    errors = _validate(tmp_path, payload)

    assert any("condition group depth 4 exceeds 3" in error for error in errors)


def test_both_direction_preserves_closed_operator_validation(tmp_path):
    payload = _both_direction_strategy_spec()
    payload["entry_logic"]["groups"][0]["conditions"][0]["operator"] = "executes"

    errors = _validate(tmp_path, payload)

    assert any("invalid operator: 'executes'" in error for error in errors)


def test_both_direction_preserves_composed_operand_validation(tmp_path):
    payload = _both_direction_strategy_spec()
    payload["entry_logic"]["groups"][0]["conditions"][0]["right_operand"] = _composed_operand(
        composition_type="multiply"
    )
    payload["free_parameters"]["parameters"] = [_threshold_parameter()]
    payload["free_parameters"]["no_free_parameters_declared"] = False

    errors = _validate(tmp_path, payload)

    assert any("composition_type" in error for error in errors)


def test_validator_does_not_import_compiler_or_runner_for_both_direction():
    source = inspect.getsource(validator_module)

    assert "spec_signal_compiler" not in source
    assert "run_offline_sweep" not in source
    assert "from lib.backtest" not in source
    assert "from lib.evaluation" not in source


def test_valid_literal_lookback_still_passes_schema_and_validator(tmp_path):
    payload = _base_strategy_spec()
    schema = _load_schema()

    assert Draft7Validator(schema).is_valid(payload)
    assert _validate(tmp_path, payload) == []


def test_valid_parameter_bound_indicator_lookback_passes(tmp_path):
    payload = _strategy_spec_with_parameter_bound_lookback()
    schema = _load_schema()

    assert Draft7Validator(schema).is_valid(payload)
    assert _validate(tmp_path, payload) == []


def test_valid_parameter_bound_lookback_inside_composed_base_operand_passes(tmp_path):
    payload = _strategy_spec_with_parameter_bound_lookback(inside_composed_base=True)
    schema = _load_schema()

    assert Draft7Validator(schema).is_valid(payload)
    assert _validate(tmp_path, payload) == []


def test_data_ref_parameter_bound_lookback_fails_schema_and_validator(tmp_path):
    payload = _base_strategy_spec()
    payload["entry_logic"]["groups"][0]["conditions"][0]["left_operand"]["lookback"] = {
        "bars_parameter_ref": "lookback_n"
    }
    payload["free_parameters"]["parameters"] = [_lookback_parameter()]
    payload["free_parameters"]["no_free_parameters_declared"] = False

    assert not Draft7Validator(_load_schema()).is_valid(payload)
    errors = _validate(tmp_path, payload)
    assert any("bars_parameter_ref" in error for error in errors)


def test_parameter_bound_lookback_unknown_parameter_fails(tmp_path):
    payload = _strategy_spec_with_parameter_bound_lookback()
    payload["free_parameters"]["parameters"] = []

    errors = _validate(tmp_path, payload)

    assert any("must match exactly one" in error and "found 0" in error for error in errors)


def test_parameter_bound_lookback_float_parameter_fails(tmp_path):
    payload = _strategy_spec_with_parameter_bound_lookback()
    payload["free_parameters"]["parameters"] = [_lookback_parameter(parameter_type="number")]

    errors = _validate(tmp_path, payload)

    assert any("type must be 'integer'" in error for error in errors)


def test_parameter_bound_lookback_unbounded_parameter_fails(tmp_path):
    payload = _strategy_spec_with_parameter_bound_lookback()
    payload["free_parameters"]["parameters"] = [_lookback_parameter(range_value=None)]
    payload["free_parameters"]["parameters"][0]["range"] = None

    errors = _validate(tmp_path, payload)

    assert any("range must be bounded" in error for error in errors)


def test_parameter_bound_lookback_range_min_less_than_one_fails(tmp_path):
    payload = _strategy_spec_with_parameter_bound_lookback()
    payload["free_parameters"]["parameters"] = [
        _lookback_parameter(range_value={
            "min": 0,
            "max": 50,
            "step": 5,
            "inclusive_min": True,
            "inclusive_max": True,
        })
    ]

    errors = _validate(tmp_path, payload)

    assert any("range.min must be an integer >= 1" in error for error in errors)


def test_parameter_bound_lookback_non_integer_grid_fails(tmp_path):
    payload = _strategy_spec_with_parameter_bound_lookback()
    payload["free_parameters"]["parameters"] = [
        _lookback_parameter(allowed_values=[5, 10.5])
    ]

    errors = _validate(tmp_path, payload)

    assert any("allowed_values.1 must be an integer >= 1" in error for error in errors)


def test_parameter_bound_lookback_mixed_literal_and_parameter_ref_fails(tmp_path):
    payload = _strategy_spec_with_parameter_bound_lookback()
    payload["entry_logic"]["groups"][0]["conditions"][0]["right_operand"]["lookback"] = {
        "bars": 20,
        "bars_parameter_ref": "lookback_n",
    }

    errors = _validate(tmp_path, payload)

    assert any(
        "not valid under any" in error or "not valid under any of the given schemas" in error
        for error in errors
    )


def test_parameter_bound_lookback_expression_string_fails_schema(tmp_path):
    payload = _strategy_spec_with_parameter_bound_lookback()
    payload["entry_logic"]["groups"][0]["conditions"][0]["right_operand"]["lookback"] = (
        "lookback_n * 2"
    )

    errors = _validate(tmp_path, payload)

    assert any(
        "not valid under any" in error or "not valid under any of the given schemas" in error
        for error in errors
    )


def test_parameter_bound_lookback_nested_compound_fails_schema(tmp_path):
    payload = _strategy_spec_with_parameter_bound_lookback()
    payload["entry_logic"]["groups"][0]["conditions"][0]["right_operand"]["lookback"] = {
        "bars_parameter_ref": {"parameter_ref": "lookback_n"}
    }

    errors = _validate(tmp_path, payload)

    assert any(
        "not valid under any" in error or "not valid under any of the given schemas" in error
        for error in errors
    )


def test_valid_composed_operand_minus_passes_schema_and_validator(tmp_path):
    payload = _strategy_spec_with_composed_operand()
    schema = _load_schema()

    assert Draft7Validator(schema).is_valid(payload)
    assert _validate(tmp_path, payload) == []


def test_valid_composed_operand_plus_passes_schema_and_validator(tmp_path):
    payload = _strategy_spec_with_composed_operand(
        composition_type="scale_by_one_plus_parameter"
    )
    schema = _load_schema()

    assert Draft7Validator(schema).is_valid(payload)
    assert _validate(tmp_path, payload) == []


def test_composed_operand_base_data_ref_passes_for_plus(tmp_path):
    payload = _strategy_spec_with_composed_operand(
        base_operand_type="data_ref",
        composition_type="scale_by_one_plus_parameter",
    )

    assert _validate(tmp_path, payload) == []


def test_composed_operand_base_indicator_ref_passes_for_plus(tmp_path):
    payload = _strategy_spec_with_composed_operand(
        base_operand_type="indicator_ref",
        composition_type="scale_by_one_plus_parameter",
    )

    assert _validate(tmp_path, payload) == []


def test_composed_operand_rejects_unclosed_composition_types(tmp_path):
    for composition_type in (
        "offset_minus_parameter",
        "offset_plus_parameter",
        "multiply",
        "expression",
    ):
        payload = _strategy_spec_with_composed_operand(composition_type=composition_type)

        errors = _validate(tmp_path, payload)

        assert any("composition_type" in error for error in errors), composition_type


def test_composed_operand_base_parameter_ref_fails_for_plus(tmp_path):
    payload = _strategy_spec_with_composed_operand(
        base_operand_type="parameter_ref",
        composition_type="scale_by_one_plus_parameter",
    )

    errors = _validate(tmp_path, payload)

    assert any("base_operand.operand_type" in error for error in errors)


def test_composed_operand_base_composed_operand_fails_for_plus(tmp_path):
    payload = _strategy_spec_with_composed_operand(
        composition_type="scale_by_one_plus_parameter"
    )
    payload["entry_logic"]["groups"][0]["conditions"][0]["right_operand"]["base_operand"] = (
        _composed_operand()
    )

    errors = _validate(tmp_path, payload)

    assert any("base_operand must not be composed_operand" in error for error in errors)
    assert any("nested or unauthorized composed_operand is forbidden" in error for error in errors)


def test_composed_operand_parameter_ref_passes_for_plus(tmp_path):
    payload = _strategy_spec_with_composed_operand(
        parameter_operand_type="parameter_ref",
        composition_type="scale_by_one_plus_parameter",
    )

    assert _validate(tmp_path, payload) == []


def test_composed_operand_parameter_data_ref_fails_for_plus(tmp_path):
    payload = _strategy_spec_with_composed_operand(
        parameter_operand_type="data_ref",
        composition_type="scale_by_one_plus_parameter",
    )

    errors = _validate(tmp_path, payload)

    assert any("parameter_operand.operand_type" in error for error in errors)


def test_composed_operand_parameter_indicator_ref_fails_for_plus(tmp_path):
    payload = _strategy_spec_with_composed_operand(
        parameter_operand_type="indicator_ref",
        composition_type="scale_by_one_plus_parameter",
    )

    errors = _validate(tmp_path, payload)

    assert any("parameter_operand.operand_type" in error for error in errors)


def test_composed_operand_parameter_composed_operand_fails_for_plus(tmp_path):
    payload = _strategy_spec_with_composed_operand(
        composition_type="scale_by_one_plus_parameter"
    )
    payload["entry_logic"]["groups"][0]["conditions"][0]["right_operand"]["parameter_operand"] = (
        _composed_operand()
    )

    errors = _validate(tmp_path, payload)

    assert any("parameter_operand must not be composed_operand" in error for error in errors)
    assert any("nested or unauthorized composed_operand is forbidden" in error for error in errors)


def test_composed_operand_extra_property_fails(tmp_path):
    payload = _strategy_spec_with_composed_operand()
    payload["entry_logic"]["groups"][0]["conditions"][0]["right_operand"]["operator"] = "multiply"

    errors = _validate(tmp_path, payload)

    assert errors
    assert any("invalid composed_operand properties" in error for error in errors)


def test_forbidden_key_inside_composed_operand_fails(tmp_path):
    payload = _strategy_spec_with_composed_operand()
    payload["entry_logic"]["groups"][0]["conditions"][0]["right_operand"]["formula"] = "x"

    errors = _validate(tmp_path, payload)

    assert any("forbidden executable key name" in error and "formula" in error for error in errors)


def test_forbidden_key_inside_composed_base_operand_fails(tmp_path):
    payload = _strategy_spec_with_composed_operand()
    payload["entry_logic"]["groups"][0]["conditions"][0]["right_operand"]["base_operand"][
        "eval"
    ] = "x"

    errors = _validate(tmp_path, payload)

    assert any("forbidden executable key name" in error and "eval" in error for error in errors)


def test_forbidden_key_inside_composed_parameter_operand_fails(tmp_path):
    payload = _strategy_spec_with_composed_operand()
    payload["entry_logic"]["groups"][0]["conditions"][0]["right_operand"]["parameter_operand"][
        "lookahead"
    ] = True

    errors = _validate(tmp_path, payload)

    assert any("forbidden executable key name" in error and "lookahead" in error for error in errors)


def test_composed_operand_missing_bound_parameter_fails(tmp_path):
    payload = _strategy_spec_with_composed_operand()
    payload["free_parameters"]["parameters"] = []

    errors = _validate(tmp_path, payload)

    assert any("must match exactly one" in error and "found 0" in error for error in errors)


def test_composed_operand_duplicate_bound_parameter_fails(tmp_path):
    payload = _strategy_spec_with_composed_operand()
    payload["free_parameters"]["parameters"] = [
        _threshold_parameter(),
        _threshold_parameter(),
    ]

    errors = _validate(tmp_path, payload)

    assert any("must match exactly one" in error and "found 2" in error for error in errors)


def test_composed_operand_bound_parameter_type_number_required(tmp_path):
    payload = _strategy_spec_with_composed_operand()
    payload["free_parameters"]["parameters"] = [_threshold_parameter(parameter_type="integer")]

    errors = _validate(tmp_path, payload)

    assert any("type must be 'number'" in error for error in errors)


def test_composed_operand_bound_parameter_role_entry_required(tmp_path):
    payload = _strategy_spec_with_composed_operand()
    payload["free_parameters"]["parameters"] = [_threshold_parameter(role="exit")]

    errors = _validate(tmp_path, payload)

    assert any("role must be 'entry'" in error for error in errors)


def test_composed_operand_bound_parameter_included_in_variants_required(tmp_path):
    payload = _strategy_spec_with_composed_operand()
    payload["free_parameters"]["parameters"] = [
        _threshold_parameter(included_in_variant_generation=False)
    ]

    errors = _validate(tmp_path, payload)

    assert any("included_in_variant_generation must be true" in error for error in errors)


def test_composed_operand_bound_parameter_range_required(tmp_path):
    payload = _strategy_spec_with_composed_operand()
    payload["free_parameters"]["parameters"] = [_threshold_parameter(range_value=None)]
    payload["free_parameters"]["parameters"][0]["range"] = None

    errors = _validate(tmp_path, payload)

    assert any("range must be bounded" in error for error in errors)


def test_composed_operand_bound_parameter_range_min_must_be_positive_for_plus(tmp_path):
    payload = _strategy_spec_with_composed_operand(
        composition_type="scale_by_one_plus_parameter"
    )
    payload["free_parameters"]["parameters"] = [
        _threshold_parameter(range_value={
            "min": 0,
            "max": 0.20,
            "step": 0.01,
            "inclusive_min": True,
            "inclusive_max": True,
        })
    ]

    errors = _validate(tmp_path, payload)

    assert any("range.min must be > 0" in error for error in errors)


def test_composed_operand_bound_parameter_range_max_must_be_less_than_one_for_plus(tmp_path):
    payload = _strategy_spec_with_composed_operand(
        composition_type="scale_by_one_plus_parameter"
    )
    payload["free_parameters"]["parameters"] = [
        _threshold_parameter(range_value={
            "min": 0.01,
            "max": 1,
            "step": 0.01,
            "inclusive_min": True,
            "inclusive_max": True,
        })
    ]

    errors = _validate(tmp_path, payload)

    assert any("range.max must be < 1" in error for error in errors)


def test_composed_operand_bound_parameter_allowed_values_must_be_in_open_unit_interval_for_plus(tmp_path):
    payload = _strategy_spec_with_composed_operand(
        composition_type="scale_by_one_plus_parameter"
    )
    payload["free_parameters"]["parameters"] = [
        _threshold_parameter(allowed_values=[0.01, 1.0])
    ]

    errors = _validate(tmp_path, payload)

    assert any("allowed_values.1 must be numeric and in (0, 1)" in error for error in errors)


def test_valid_z_score_composed_operand_passes_schema_and_validator(tmp_path):
    payload = _strategy_spec_with_z_score_operand()
    schema = _load_schema()

    assert Draft7Validator(schema).is_valid(payload)
    assert _validate(tmp_path, payload) == []


def test_z_score_composed_operand_accepts_data_ref_value_and_indicator_refs(tmp_path):
    payload = _strategy_spec_with_z_score_operand(
        value_operand_type="data_ref",
        center_operand_type="indicator_ref",
        scale_operand_type="indicator_ref",
    )

    assert _validate(tmp_path, payload) == []


def test_z_score_composed_operand_rejects_unknown_zero_scale_policy(tmp_path):
    payload = _strategy_spec_with_z_score_operand(zero_scale_policy="epsilon")

    errors = _validate(tmp_path, payload)

    assert any("zero_scale_policy" in error for error in errors)


def test_z_score_composed_operand_rejects_parameter_ref_operand(tmp_path):
    payload = _strategy_spec_with_z_score_operand(value_operand_type="parameter_ref")

    errors = _validate(tmp_path, payload)

    assert any("value_operand.operand_type" in error for error in errors)


def test_z_score_composed_operand_rejects_nested_composed_operand(tmp_path):
    payload = _strategy_spec_with_z_score_operand()
    payload["entry_logic"]["groups"][0]["conditions"][0]["left_operand"]["value_operand"] = (
        _composed_operand()
    )
    payload["free_parameters"]["parameters"] = [_threshold_parameter()]
    payload["free_parameters"]["no_free_parameters_declared"] = False

    errors = _validate(tmp_path, payload)

    assert any("value_operand must not be composed_operand" in error for error in errors)
    assert any("nested or unauthorized composed_operand is forbidden" in error for error in errors)


def test_z_score_composed_operand_extra_property_fails(tmp_path):
    payload = _strategy_spec_with_z_score_operand()
    payload["entry_logic"]["groups"][0]["conditions"][0]["left_operand"]["parameter_operand"] = (
        _standard_operand("parameter_ref", "threshold")
    )

    errors = _validate(tmp_path, payload)

    assert any("invalid composed_operand properties" in error for error in errors)


def test_forbidden_key_inside_z_score_composed_operand_fails(tmp_path):
    payload = _strategy_spec_with_z_score_operand()
    payload["entry_logic"]["groups"][0]["conditions"][0]["left_operand"]["eval"] = "x"

    errors = _validate(tmp_path, payload)

    assert any("forbidden executable key name" in error and "eval" in error for error in errors)


def test_strategy_spec_validator_does_not_import_compiler_runner_or_lib_modules():
    source = inspect.getsource(validator_module)

    assert "spec_signal_compiler" not in source
    assert "run_offline_sweep" not in source
    assert "from lib.backtest" not in source
    assert "from lib.evaluation" not in source


def test_invalid_json_fails(tmp_path):
    strategy_specs_dir = tmp_path / "research" / "strategy_specs"
    path = strategy_specs_dir / "STRAT-SPEC-9001.strategy_spec.json"
    path.parent.mkdir(parents=True)
    path.write_text("{", encoding="utf-8")

    errors = validate_strategy_specs(strategy_specs_dir=strategy_specs_dir)

    assert any("invalid JSON" in error for error in errors)


def test_missing_required_schema_field_fails(tmp_path):
    payload = _base_strategy_spec()
    del payload["title"]

    errors = _validate(tmp_path, payload)

    assert any("'title' is a required property" in error for error in errors)


def test_filename_strategy_spec_id_mismatch_fails(tmp_path):
    errors = _validate(
        tmp_path,
        _base_strategy_spec("STRAT-SPEC-9001"),
        filename="STRAT-SPEC-9999.strategy_spec.json",
    )

    assert any(
        "filename must be STRAT-SPEC-9001.strategy_spec.json" in error
        for error in errors
    )


def test_duplicate_strategy_spec_id_fails(tmp_path):
    strategy_specs_dir = tmp_path / "research" / "strategy_specs"
    payload = _base_strategy_spec("STRAT-SPEC-9001")
    _write_json(strategy_specs_dir / "a" / "STRAT-SPEC-9001.strategy_spec.json", payload)
    _write_json(strategy_specs_dir / "b" / "STRAT-SPEC-9001.strategy_spec.json", payload)

    errors = validate_strategy_specs(strategy_specs_dir=strategy_specs_dir)

    assert any("duplicate strategy_spec_id STRAT-SPEC-9001" in error for error in errors)


def test_invalid_operator_fails(tmp_path):
    payload = _base_strategy_spec()
    payload["entry_logic"]["groups"][0]["conditions"][0]["operator"] = "executes"

    errors = _validate(tmp_path, payload)

    assert any("invalid operator: 'executes'" in error for error in errors)


def test_condition_nesting_depth_greater_than_three_fails(tmp_path):
    payload = _base_strategy_spec()
    depth_4 = _group("GROUP-4")
    depth_3 = _group("GROUP-3", [depth_4])
    depth_2 = _group("GROUP-2", [depth_3])
    payload["entry_logic"]["groups"] = [_group("GROUP-1", [depth_2])]

    errors = _validate(tmp_path, payload)

    assert any("condition group depth 4 exceeds 3" in error for error in errors)


def test_max_condition_group_depth_not_exactly_three_fails(tmp_path):
    payload = _base_strategy_spec()
    payload["max_condition_group_depth"] = 4

    errors = _validate(tmp_path, payload)

    assert any("max_condition_group_depth must be exactly 3" in error for error in errors)


def test_more_than_five_free_parameters_fails(tmp_path):
    payload = _base_strategy_spec()
    payload["free_parameters"]["parameters"] = [_parameter(f"p{i}") for i in range(6)]
    payload["free_parameters"]["no_free_parameters_declared"] = False

    errors = _validate(tmp_path, payload)

    assert any("free_parameters.parameters has 6 entries" in error for error in errors)


def test_no_free_parameters_declared_with_non_empty_parameters_fails(tmp_path):
    payload = _base_strategy_spec()
    payload["free_parameters"]["parameters"] = [_parameter("lookback")]
    payload["free_parameters"]["no_free_parameters_declared"] = True

    errors = _validate(tmp_path, payload)

    assert any("no_free_parameters_declared=true requires empty parameters" in error for error in errors)


def test_forbidden_executable_key_fails(tmp_path):
    payload = _base_strategy_spec()
    payload["provenance"]["Formula"] = "close > 100"

    errors = _validate(tmp_path, payload)

    assert any("forbidden executable key name" in error and "Formula" in error for error in errors)


def test_non_authority_flag_false_fails(tmp_path):
    payload = _base_strategy_spec()
    payload["review"]["non_authority_acknowledgement"]["not_recommendation_authority"] = False

    errors = _validate(tmp_path, payload)

    assert any(
        "review.non_authority_acknowledgement.not_recommendation_authority must be true"
        in error
        for error in errors
    )


def test_unsafe_host_data_reference_strings_fail(tmp_path):
    payload = _base_strategy_spec()
    payload["timeframe_and_data"]["host_data_refs"] = [
        {
            "stream": "ohlcv",
            "timeframe": "1h",
            "field": "https://example.test/close",
            "availability": "required",
        },
        {
            "stream": "ohlcv",
            "timeframe": "1h",
            "field": "..\\outside",
            "availability": "optional",
        },
        {
            "stream": "ohlcv",
            "timeframe": "1h",
            "field": "C:\\data\\close",
            "availability": "optional",
        },
    ]

    errors = _validate(tmp_path, payload)

    assert sum("unsafe host-data reference string" in error for error in errors) == 3


def test_cli_returns_success_for_clean_temp_fixture(tmp_path, monkeypatch, capsys):
    strategy_specs_dir = tmp_path / "research" / "strategy_specs"
    _write_json(strategy_specs_dir / "STRAT-SPEC-9001.strategy_spec.json", _base_strategy_spec())
    monkeypatch.setattr(
        sys,
        "argv",
        ["validate_strategy_specs", "--strategy-specs-dir", str(strategy_specs_dir)],
    )

    assert main() == 0
    assert "OK:" in capsys.readouterr().out


def test_cli_returns_failure_for_invalid_temp_fixture(tmp_path, monkeypatch, capsys):
    strategy_specs_dir = tmp_path / "research" / "strategy_specs"
    payload = _base_strategy_spec()
    del payload["title"]
    _write_json(strategy_specs_dir / "STRAT-SPEC-9001.strategy_spec.json", payload)
    monkeypatch.setattr(
        sys,
        "argv",
        ["validate_strategy_specs", "--strategy-specs-dir", str(strategy_specs_dir)],
    )

    assert main() == 1
    assert "ERROR:" in capsys.readouterr().out
