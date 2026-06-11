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
