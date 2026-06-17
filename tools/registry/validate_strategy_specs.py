"""Validate non-executing Strategy Spec JSON artifacts."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STRATEGY_SPECS_DIR = REPO_ROOT / "research" / "strategy_specs"
DEFAULT_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "strategy_spec.schema.json"
CLOSED_OPERATOR_ENUM = {
    "gt",
    "gte",
    "lt",
    "lte",
    "eq",
    "neq",
    "crosses_above",
    "crosses_below",
    "in_set",
    "is_true",
    "is_false",
}
COMPOSED_OPERAND_TYPE = "composed_operand"
SCALED_PARAMETER_COMPOSITION_TYPES = {
    "scale_by_one_minus_parameter",
    "scale_by_one_plus_parameter",
}
COMPOSITION_TYPE_Z_SCORE = "z_score"
COMPOSITION_TYPES = SCALED_PARAMETER_COMPOSITION_TYPES | {COMPOSITION_TYPE_Z_SCORE}
COMPOSED_BASE_OPERAND_TYPES = {"data_ref", "indicator_ref"}
COMPOSED_PARAMETER_OPERAND_TYPE = "parameter_ref"
Z_SCORE_OPERAND_TYPES = {"data_ref", "indicator_ref"}
Z_SCORE_ZERO_SCALE_POLICY = "null_output"
SIDE_LABELS = {"long", "short"}
BOTH_DIRECTION = "both"
SINGLE_DIRECTIONS = {"long", "short"}
MAX_CONDITION_GROUP_DEPTH = 3
MAX_FREE_PARAMETERS = 5
LOOKBACK_PARAMETER_REF_KEY = "bars_parameter_ref"
ATR_STOP_ALLOWED_KEYS = {
    "enabled",
    "atr_lookback",
    "atr_multiplier",
    "entry_reference_price",
    "evaluation_price",
    "evaluation_timing",
}
ATR_STOP_ENTRY_REFERENCE_PRICE = "next_bar_open_pre_fee_slippage"
ATR_STOP_EVALUATION_PRICE = "close"
ATR_STOP_EVALUATION_TIMING = "bar_close"
ATR_STOP_MAX_LOOKBACK_BARS = 100000
ATR_STOP_MAX_MULTIPLIER = 1000.0
ONLINE_OHLCV_PRIMITIVES_KEY = "online_ohlcv_primitives"
PRIMITIVE_REF_OPERAND_TYPE = "primitive_ref"
PRIMITIVE_COLLECTIONS = {
    "session_windows": "session_id",
    "opening_ranges": "range_id",
    "opening_range_breakouts": "breakout_id",
    "opening_range_retests": "retest_id",
    "candle_shapes": "predicate_id",
}
FORBIDDEN_EXECUTABLE_KEYS = {
    "expression",
    "formula",
    "code",
    "script",
    "eval",
    "exec",
    "function",
    "callback",
    "lambda",
    "sql",
    "shell",
    "python",
    "javascript",
    "url",
    "file_path",
    "command",
    "runtime_action",
    "order_instruction",
    "broker_instruction",
    "exchange_instruction",
    "live_action",
    "paper_action",
    "readiness_update",
    "transition_trigger",
    "approval_action",
    "ranking_score",
    "recommendation",
    "lookahead",
    "forward_fill",
    "backfill",
    "interpolation",
    "future_value",
}
NON_EXECUTION_TRUE_FLAGS = {
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
}
REVIEW_NON_AUTHORITY_TRUE_FLAGS = {
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
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _format_schema_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    if location:
        return f"{location}: {error.message}"
    return error.message


def _validate_json_file(
    path: Path,
    validator: Draft7Validator,
) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        return None, [f"{path}: invalid JSON: {exc}"]

    errors = [
        f"{path}: {_format_schema_error(schema_error)}"
        for schema_error in sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
    ]
    return payload, errors


def _path_label(parts: list[str]) -> str:
    return ".".join(parts)


def _walk_conditions(group: Any, path_parts: list[str]) -> list[tuple[str, dict[str, Any]]]:
    if not isinstance(group, dict):
        return []

    conditions: list[tuple[str, dict[str, Any]]] = []
    for index, condition in enumerate(group.get("conditions", [])):
        if isinstance(condition, dict):
            conditions.append((_path_label([*path_parts, "conditions", str(index)]), condition))

    for index, subgroup in enumerate(group.get("subgroups", [])):
        conditions.extend(_walk_conditions(subgroup, [*path_parts, "subgroups", str(index)]))
    return conditions


def _walk_groups(group: Any, path_parts: list[str], depth: int) -> list[tuple[str, Any, int]]:
    groups = [(_path_label(path_parts), group, depth)]
    if not isinstance(group, dict):
        return groups

    for index, subgroup in enumerate(group.get("subgroups", [])):
        groups.extend(_walk_groups(subgroup, [*path_parts, "subgroups", str(index)], depth + 1))
    return groups


def _logic_roots(payload: dict[str, Any]) -> list[tuple[str, Any]]:
    roots: list[tuple[str, Any]] = []
    for section_name in ("entry_logic", "exit_logic", "filters"):
        section = payload.get(section_name)
        if not isinstance(section, dict):
            continue
        groups = section.get("groups")
        if not isinstance(groups, list):
            continue
        for index, group in enumerate(groups):
            roots.append((f"{section_name}.groups.{index}", group))
    return roots


def _validate_closed_operator_enum(path: Path, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for root_path, group in _logic_roots(payload):
        for condition_path, condition in _walk_conditions(group, root_path.split(".")):
            operator = condition.get("operator")
            if operator not in CLOSED_OPERATOR_ENUM:
                errors.append(f"{path}: {condition_path}.operator invalid operator: {operator!r}")
    return errors


def _validate_condition_group_depth(path: Path, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    max_depth = payload.get("max_condition_group_depth")
    if max_depth != MAX_CONDITION_GROUP_DEPTH:
        errors.append(
            f"{path}: max_condition_group_depth must be exactly {MAX_CONDITION_GROUP_DEPTH}: "
            f"{max_depth!r}"
        )

    for root_path, group in _logic_roots(payload):
        for group_path, _, depth in _walk_groups(group, root_path.split("."), 1):
            if depth > MAX_CONDITION_GROUP_DEPTH:
                errors.append(
                    f"{path}: {group_path} condition group depth {depth} exceeds "
                    f"{MAX_CONDITION_GROUP_DEPTH}"
                )
    return errors


def _validate_free_parameters(path: Path, payload: dict[str, Any]) -> list[str]:
    free_parameters = payload.get("free_parameters")
    if not isinstance(free_parameters, dict):
        return []

    errors: list[str] = []
    max_free_parameters = free_parameters.get("max_free_parameters")
    if max_free_parameters != MAX_FREE_PARAMETERS:
        errors.append(
            f"{path}: free_parameters.max_free_parameters must be {MAX_FREE_PARAMETERS}: "
            f"{max_free_parameters!r}"
        )

    parameters = free_parameters.get("parameters")
    if not isinstance(parameters, list):
        return errors

    if len(parameters) > MAX_FREE_PARAMETERS:
        errors.append(
            f"{path}: free_parameters.parameters has {len(parameters)} entries; "
            f"maximum is {MAX_FREE_PARAMETERS}"
        )

    for index, parameter in enumerate(parameters):
        if not isinstance(parameter, dict):
            continue
        if parameter.get("is_free_parameter") is not True:
            errors.append(
                f"{path}: free_parameters.parameters.{index}.is_free_parameter must be true"
            )

    no_free_parameters_declared = free_parameters.get("no_free_parameters_declared")
    if no_free_parameters_declared is True and parameters:
        errors.append(
            f"{path}: free_parameters.no_free_parameters_declared=true requires empty parameters"
        )
    if parameters and no_free_parameters_declared is not False:
        errors.append(
            f"{path}: free_parameters.parameters non-empty requires "
            "no_free_parameters_declared=false"
        )
    return errors


def _walk_keys(value: Any, path_parts: list[str]) -> list[tuple[str, str]]:
    keys: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_path = _path_label([*path_parts, str(key)])
            keys.append((key_path, str(key)))
            keys.extend(_walk_keys(child, [*path_parts, str(key)]))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            keys.extend(_walk_keys(child, [*path_parts, str(index)]))
    return keys


def _validate_forbidden_keys(path: Path, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key_path, key in _walk_keys(payload, []):
        if key.lower() in FORBIDDEN_EXECUTABLE_KEYS:
            errors.append(f"{path}: forbidden executable key name at {key_path}: {key}")
    return errors


def _walk_composed_operands(value: Any, path_parts: list[str]) -> list[tuple[str, dict[str, Any]]]:
    composed_operands: list[tuple[str, dict[str, Any]]] = []
    if isinstance(value, dict):
        if value.get("operand_type") == COMPOSED_OPERAND_TYPE:
            composed_operands.append((_path_label(path_parts), value))
        for key, child in value.items():
            composed_operands.extend(_walk_composed_operands(child, [*path_parts, str(key)]))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            composed_operands.extend(_walk_composed_operands(child, [*path_parts, str(index)]))
    return composed_operands


def _walk_operands(value: Any, path_parts: list[str]) -> list[tuple[str, dict[str, Any]]]:
    operands: list[tuple[str, dict[str, Any]]] = []
    if isinstance(value, dict):
        if "operand_type" in value:
            operands.append((_path_label(path_parts), value))
        for key, child in value.items():
            operands.extend(_walk_operands(child, [*path_parts, str(key)]))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            operands.extend(_walk_operands(child, [*path_parts, str(index)]))
    return operands


def _parameter_declarations(payload: dict[str, Any]) -> dict[str, list[tuple[int, dict[str, Any]]]]:
    declarations: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    free_parameters = payload.get("free_parameters")
    if not isinstance(free_parameters, dict):
        return declarations
    parameters = free_parameters.get("parameters")
    if not isinstance(parameters, list):
        return declarations
    for index, parameter in enumerate(parameters):
        if not isinstance(parameter, dict):
            continue
        name = parameter.get("name")
        if isinstance(name, str):
            declarations.setdefault(name, []).append((index, parameter))
    return declarations


def _is_condition_operand_path(composed_path: str, condition_path: str) -> bool:
    return composed_path in {
        f"{condition_path}.left_operand",
        f"{condition_path}.right_operand",
    }


def _validate_composed_parameter(
    path: Path,
    operand_path: str,
    parameter_name: Any,
    declarations: dict[str, list[tuple[int, dict[str, Any]]]],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(parameter_name, str) or not parameter_name:
        return [f"{path}: {operand_path}.parameter_operand.ref must bind a non-empty parameter name"]

    matches = declarations.get(parameter_name, [])
    if len(matches) != 1:
        errors.append(
            f"{path}: {operand_path}.parameter_operand.ref {parameter_name!r} must match exactly "
            f"one free_parameters.parameters[].name; found {len(matches)}"
        )
        return errors

    parameter_index, parameter = matches[0]
    parameter_path = f"free_parameters.parameters.{parameter_index}"
    if parameter.get("type") != "number":
        errors.append(f"{path}: {operand_path} bound parameter {parameter_path}.type must be 'number'")
    if parameter.get("role") != "entry":
        errors.append(f"{path}: {operand_path} bound parameter {parameter_path}.role must be 'entry'")
    if parameter.get("is_free_parameter") is not True:
        errors.append(f"{path}: {operand_path} bound parameter {parameter_path}.is_free_parameter must be true")
    if parameter.get("included_in_variant_generation") is not True:
        errors.append(
            f"{path}: {operand_path} bound parameter "
            f"{parameter_path}.included_in_variant_generation must be true"
        )

    range_value = parameter.get("range")
    if not isinstance(range_value, dict):
        errors.append(f"{path}: {operand_path} bound parameter {parameter_path}.range must be bounded")
    else:
        range_min = range_value.get("min")
        range_max = range_value.get("max")
        if not isinstance(range_min, (int, float)) or isinstance(range_min, bool) or range_min <= 0:
            errors.append(f"{path}: {operand_path} bound parameter {parameter_path}.range.min must be > 0")
        if not isinstance(range_max, (int, float)) or isinstance(range_max, bool) or range_max >= 1:
            errors.append(f"{path}: {operand_path} bound parameter {parameter_path}.range.max must be < 1")

    allowed_values = parameter.get("allowed_values")
    if isinstance(allowed_values, list):
        for index, value in enumerate(allowed_values):
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not (0 < value < 1):
                errors.append(
                    f"{path}: {operand_path} bound parameter "
                    f"{parameter_path}.allowed_values.{index} must be numeric and in (0, 1)"
                )
    return errors


def _validate_composed_operands(path: Path, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    declarations = _parameter_declarations(payload)
    condition_operand_paths: set[str] = set()

    for root_path, group in _logic_roots(payload):
        for condition_path, condition in _walk_conditions(group, root_path.split(".")):
            for operand_key in ("left_operand", "right_operand"):
                operand = condition.get(operand_key)
                operand_path = f"{condition_path}.{operand_key}"
                if isinstance(operand, dict):
                    condition_operand_paths.add(operand_path)
                    if operand.get("operand_type") != COMPOSED_OPERAND_TYPE:
                        continue

                    composition_type = operand.get("composition_type")
                    if composition_type not in COMPOSITION_TYPES:
                        errors.append(
                            f"{path}: {operand_path}.composition_type must be one of "
                            f"{sorted(COMPOSITION_TYPES)}"
                        )

                    if composition_type in SCALED_PARAMETER_COMPOSITION_TYPES:
                        if set(operand) != {
                            "operand_type",
                            "composition_type",
                            "base_operand",
                            "parameter_operand",
                        }:
                            errors.append(f"{path}: {operand_path} has invalid composed_operand properties")

                        base_operand = operand.get("base_operand")
                        if not isinstance(base_operand, dict):
                            errors.append(f"{path}: {operand_path}.base_operand must be an object")
                        else:
                            base_type = base_operand.get("operand_type")
                            if base_type == COMPOSED_OPERAND_TYPE:
                                errors.append(f"{path}: {operand_path}.base_operand must not be composed_operand")
                            if base_type not in COMPOSED_BASE_OPERAND_TYPES:
                                errors.append(
                                    f"{path}: {operand_path}.base_operand.operand_type must be one of "
                                    f"{sorted(COMPOSED_BASE_OPERAND_TYPES)}"
                                )

                        parameter_operand = operand.get("parameter_operand")
                        if not isinstance(parameter_operand, dict):
                            errors.append(f"{path}: {operand_path}.parameter_operand must be an object")
                        else:
                            parameter_type = parameter_operand.get("operand_type")
                            if parameter_type == COMPOSED_OPERAND_TYPE:
                                errors.append(
                                    f"{path}: {operand_path}.parameter_operand must not be composed_operand"
                                )
                            if parameter_type != COMPOSED_PARAMETER_OPERAND_TYPE:
                                errors.append(
                                    f"{path}: {operand_path}.parameter_operand.operand_type must be "
                                    f"{COMPOSED_PARAMETER_OPERAND_TYPE!r}"
                                )
                            errors.extend(
                                _validate_composed_parameter(
                                    path,
                                    operand_path,
                                    parameter_operand.get("ref"),
                                    declarations,
                                )
                            )
                    elif composition_type == COMPOSITION_TYPE_Z_SCORE:
                        if set(operand) != {
                            "operand_type",
                            "composition_type",
                            "value_operand",
                            "center_operand",
                            "scale_operand",
                            "zero_scale_policy",
                        }:
                            errors.append(f"{path}: {operand_path} has invalid composed_operand properties")
                        if operand.get("zero_scale_policy") != Z_SCORE_ZERO_SCALE_POLICY:
                            errors.append(
                                f"{path}: {operand_path}.zero_scale_policy must be "
                                f"{Z_SCORE_ZERO_SCALE_POLICY!r}"
                            )
                        for operand_key in ("value_operand", "center_operand", "scale_operand"):
                            child_operand = operand.get(operand_key)
                            child_path = f"{operand_path}.{operand_key}"
                            if not isinstance(child_operand, dict):
                                errors.append(f"{path}: {child_path} must be an object")
                                continue
                            child_type = child_operand.get("operand_type")
                            if child_type == COMPOSED_OPERAND_TYPE:
                                errors.append(f"{path}: {child_path} must not be composed_operand")
                            if child_type not in Z_SCORE_OPERAND_TYPES:
                                errors.append(
                                    f"{path}: {child_path}.operand_type must be one of "
                                    f"{sorted(Z_SCORE_OPERAND_TYPES)}"
                                )

    for composed_path, _ in _walk_composed_operands(payload, []):
        if composed_path not in condition_operand_paths:
            if any(
                _is_condition_operand_path(composed_path, condition_path)
                for root_path, group in _logic_roots(payload)
                for condition_path, _condition in _walk_conditions(group, root_path.split("."))
            ):
                continue
            errors.append(f"{path}: {composed_path} nested or unauthorized composed_operand is forbidden")
    return errors


def _is_non_bool_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_integer_lookback_parameter(
    path: Path,
    operand_path: str,
    parameter_name: Any,
    declarations: dict[str, list[tuple[int, dict[str, Any]]]],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(parameter_name, str) or not parameter_name:
        return [f"{path}: {operand_path}.lookback.bars_parameter_ref must be a non-empty string"]

    matches = declarations.get(parameter_name, [])
    if len(matches) != 1:
        errors.append(
            f"{path}: {operand_path}.lookback.bars_parameter_ref {parameter_name!r} must match "
            f"exactly one free_parameters.parameters[].name; found {len(matches)}"
        )
        return errors

    parameter_index, parameter = matches[0]
    parameter_path = f"free_parameters.parameters.{parameter_index}"
    if parameter.get("type") != "integer":
        errors.append(
            f"{path}: {operand_path} lookback parameter {parameter_path}.type "
            "must be 'integer'"
        )
    if parameter.get("is_free_parameter") is not True:
        errors.append(
            f"{path}: {operand_path} lookback parameter {parameter_path}.is_free_parameter must be true"
        )
    if parameter.get("included_in_variant_generation") is not True:
        errors.append(
            f"{path}: {operand_path} lookback parameter "
            f"{parameter_path}.included_in_variant_generation must be true"
        )

    range_value = parameter.get("range")
    range_min: Any = None
    range_max: Any = None
    if not isinstance(range_value, dict):
        errors.append(
            f"{path}: {operand_path} lookback parameter {parameter_path}.range "
            "must be bounded"
        )
    else:
        range_min = range_value.get("min")
        range_max = range_value.get("max")
        range_step = range_value.get("step")
        if not _is_non_bool_int(range_min) or range_min < 1:
            errors.append(
                f"{path}: {operand_path} lookback parameter {parameter_path}.range.min "
                "must be an integer >= 1"
            )
        if not _is_non_bool_int(range_max):
            errors.append(
                f"{path}: {operand_path} lookback parameter {parameter_path}.range.max "
                "must be a finite integer"
            )
        elif _is_non_bool_int(range_min) and range_max < range_min:
            errors.append(
                f"{path}: {operand_path} lookback parameter {parameter_path}.range.max "
                "must be >= range.min"
            )
        if not _is_non_bool_int(range_step) or range_step < 1:
            errors.append(
                f"{path}: {operand_path} lookback parameter {parameter_path}.range.step "
                "must be an integer >= 1"
            )

    default = parameter.get("default")
    allowed_values = parameter.get("allowed_values")
    if not _is_non_bool_int(default) or default < 1:
        errors.append(
            f"{path}: {operand_path} lookback parameter {parameter_path}.default "
            "must be an integer >= 1"
        )
    elif (
        _is_non_bool_int(range_min)
        and _is_non_bool_int(range_max)
        and not (range_min <= default <= range_max)
    ):
        errors.append(
            f"{path}: {operand_path} lookback parameter {parameter_path}.default "
            "must be within range"
        )

    if isinstance(allowed_values, list):
        for index, value in enumerate(allowed_values):
            if not _is_non_bool_int(value) or value < 1:
                errors.append(
                    f"{path}: {operand_path} lookback parameter "
                    f"{parameter_path}.allowed_values.{index} must be an integer >= 1"
                )
            elif _is_non_bool_int(range_min) and _is_non_bool_int(range_max) and not (
                range_min <= value <= range_max
            ):
                errors.append(
                    f"{path}: {operand_path} lookback parameter "
                    f"{parameter_path}.allowed_values.{index} must be within range"
                )
        if allowed_values and _is_non_bool_int(default) and default not in allowed_values:
            errors.append(
                f"{path}: {operand_path} lookback parameter {parameter_path}.default "
                "must be in allowed_values"
            )
    return errors


def _validate_parameter_bound_lookbacks(path: Path, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    declarations = _parameter_declarations(payload)
    for operand_path, operand in _walk_operands(payload, []):
        lookback = operand.get("lookback")
        if not isinstance(lookback, dict) or LOOKBACK_PARAMETER_REF_KEY not in lookback:
            continue
        if set(lookback) != {LOOKBACK_PARAMETER_REF_KEY}:
            errors.append(f"{path}: {operand_path}.lookback has invalid parameter-bound properties")
            continue
        if operand.get("operand_type") != "indicator_ref":
            errors.append(
                f"{path}: {operand_path}.lookback.bars_parameter_ref is only allowed for "
                "indicator_ref.lookback"
            )
            continue
        errors.extend(
            _validate_integer_lookback_parameter(
                path,
                operand_path,
                lookback.get(LOOKBACK_PARAMETER_REF_KEY),
                declarations,
            )
        )
    return errors


def _is_finite_non_bool_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _validate_atr_stop(path: Path, payload: dict[str, Any]) -> list[str]:
    exit_logic = payload.get("exit_logic")
    if not isinstance(exit_logic, dict) or "atr_stop" not in exit_logic:
        return []
    atr_stop = exit_logic.get("atr_stop")
    if not isinstance(atr_stop, dict):
        return [f"{path}: exit_logic.atr_stop must be an object when provided"]

    errors: list[str] = []
    if set(atr_stop) != ATR_STOP_ALLOWED_KEYS:
        errors.append(
            f"{path}: exit_logic.atr_stop supports exactly {sorted(ATR_STOP_ALLOWED_KEYS)}"
        )
    if atr_stop.get("enabled") is not True:
        errors.append(f"{path}: exit_logic.atr_stop.enabled must be true")

    atr_lookback = atr_stop.get("atr_lookback")
    if (
        not _is_non_bool_int(atr_lookback)
        or atr_lookback < 1
        or atr_lookback > ATR_STOP_MAX_LOOKBACK_BARS
    ):
        errors.append(
            f"{path}: exit_logic.atr_stop.atr_lookback must be an integer in "
            f"[1, {ATR_STOP_MAX_LOOKBACK_BARS}]"
        )

    atr_multiplier = atr_stop.get("atr_multiplier")
    if (
        not _is_finite_non_bool_number(atr_multiplier)
        or float(atr_multiplier) <= 0.0
        or float(atr_multiplier) > ATR_STOP_MAX_MULTIPLIER
    ):
        errors.append(
            f"{path}: exit_logic.atr_stop.atr_multiplier must be a positive finite "
            f"number <= {ATR_STOP_MAX_MULTIPLIER:g}"
        )

    if atr_stop.get("entry_reference_price") != ATR_STOP_ENTRY_REFERENCE_PRICE:
        errors.append(
            f"{path}: exit_logic.atr_stop.entry_reference_price must be "
            f"{ATR_STOP_ENTRY_REFERENCE_PRICE!r}"
        )
    if atr_stop.get("evaluation_price") != ATR_STOP_EVALUATION_PRICE:
        errors.append(
            f"{path}: exit_logic.atr_stop.evaluation_price must be "
            f"{ATR_STOP_EVALUATION_PRICE!r}"
        )
    if atr_stop.get("evaluation_timing") != ATR_STOP_EVALUATION_TIMING:
        errors.append(
            f"{path}: exit_logic.atr_stop.evaluation_timing must be "
            f"{ATR_STOP_EVALUATION_TIMING!r}"
        )
    return errors


def _online_primitives(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get(ONLINE_OHLCV_PRIMITIVES_KEY)
    return value if isinstance(value, dict) else {}


def _primitive_ids(payload: dict[str, Any], collection: str) -> set[str]:
    id_key = PRIMITIVE_COLLECTIONS[collection]
    items = _online_primitives(payload).get(collection, [])
    if not isinstance(items, list):
        return set()
    return {
        item[id_key]
        for item in items
        if isinstance(item, dict) and isinstance(item.get(id_key), str)
    }


def _validate_online_ohlcv_primitives(path: Path, payload: dict[str, Any]) -> list[str]:
    primitives = payload.get(ONLINE_OHLCV_PRIMITIVES_KEY)
    if primitives is None:
        return []
    if not isinstance(primitives, dict):
        return [f"{path}: online_ohlcv_primitives must be an object"]

    errors: list[str] = []
    seen_ids: dict[str, str] = {}
    for collection, id_key in PRIMITIVE_COLLECTIONS.items():
        items = primitives.get(collection, [])
        if not isinstance(items, list):
            continue
        local: set[str] = set()
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            item_id = item.get(id_key)
            item_path = f"online_ohlcv_primitives.{collection}.{index}"
            if not isinstance(item_id, str) or not item_id:
                continue
            if item_id in local:
                errors.append(f"{path}: duplicate {id_key} in {collection}: {item_id}")
            local.add(item_id)
            if item_id in seen_ids:
                errors.append(
                    f"{path}: primitive id {item_id!r} reused by {collection} and {seen_ids[item_id]}"
                )
            seen_ids[item_id] = collection
            if any(token in item_id.lower() for token in ("eval", "lambda", "code", "formula")):
                errors.append(f"{path}: {item_path}.{id_key} contains executable-looking text")

    session_ids = _primitive_ids(payload, "session_windows")
    range_ids = _primitive_ids(payload, "opening_ranges")
    breakout_ids = _primitive_ids(payload, "opening_range_breakouts")

    for index, item in enumerate(primitives.get("opening_ranges", []) or []):
        if isinstance(item, dict) and item.get("session_ref") not in session_ids:
            errors.append(
                f"{path}: online_ohlcv_primitives.opening_ranges.{index}.session_ref "
                "must reference a declared session_window"
            )

    for index, item in enumerate(primitives.get("opening_range_breakouts", []) or []):
        if isinstance(item, dict) and item.get("range_ref") not in range_ids:
            errors.append(
                f"{path}: online_ohlcv_primitives.opening_range_breakouts.{index}.range_ref "
                "must reference a declared opening_range"
            )

    for index, item in enumerate(primitives.get("opening_range_retests", []) or []):
        if not isinstance(item, dict):
            continue
        if item.get("breakout_ref") not in breakout_ids:
            errors.append(
                f"{path}: online_ohlcv_primitives.opening_range_retests.{index}.breakout_ref "
                "must reference a declared opening_range_breakout"
            )
        window = item.get("window")
        if isinstance(window, dict):
            min_after = window.get("min_bars_after_breakout")
            max_after = window.get("max_bars_after_breakout")
            if isinstance(min_after, int) and isinstance(max_after, int) and max_after < min_after:
                errors.append(
                    f"{path}: online_ohlcv_primitives.opening_range_retests.{index}.window "
                    "max_bars_after_breakout must be >= min_bars_after_breakout"
                )

    declared_primitive_ids = set(seen_ids)
    for operand_path, operand in _walk_operands(payload, []):
        if operand.get("operand_type") != PRIMITIVE_REF_OPERAND_TYPE:
            continue
        ref = operand.get("ref")
        if ref not in declared_primitive_ids:
            errors.append(f"{path}: {operand_path}.ref references unknown primitive {ref!r}")
        if operand.get("timeframe") not in (None, ""):
            errors.append(f"{path}: {operand_path}.timeframe must be null for primitive_ref")
        if operand.get("lookback") is not None:
            errors.append(f"{path}: {operand_path}.lookback must be null for primitive_ref")

    controls = payload.get("entry_logic", {}).get("entry_controls")
    if isinstance(controls, dict) and isinstance(controls.get("max_trades_per_session"), dict):
        session_ref = controls["max_trades_per_session"].get("session_ref")
        if session_ref not in session_ids:
            errors.append(
                f"{path}: entry_logic.entry_controls.max_trades_per_session.session_ref "
                "must reference a declared session_window"
            )
    return errors


def _validate_true_flags(
    path: Path,
    payload: dict[str, Any],
    object_path: str,
    required_flags: set[str],
) -> list[str]:
    current: Any = payload
    for part in object_path.split("."):
        if not isinstance(current, dict):
            return [f"{path}: {object_path} must be present as an object"]
        current = current.get(part)
    if not isinstance(current, dict):
        return [f"{path}: {object_path} must be present as an object"]

    errors: list[str] = []
    for flag in sorted(required_flags):
        if current.get(flag) is not True:
            errors.append(f"{path}: {object_path}.{flag} must be true")
    return errors


def _validate_non_authority_flags(path: Path, payload: dict[str, Any]) -> list[str]:
    errors = _validate_true_flags(
        path,
        payload,
        "non_execution_declaration",
        NON_EXECUTION_TRUE_FLAGS,
    )
    errors.extend(
        _validate_true_flags(
            path,
            payload,
            "review.non_authority_acknowledgement",
            REVIEW_NON_AUTHORITY_TRUE_FLAGS,
        )
    )
    return errors


def _is_unsafe_reference_string(value: str) -> bool:
    lower_value = value.lower()
    if lower_value.startswith(("http://", "https://")):
        return True
    if PureWindowsPath(value).is_absolute() or PurePosixPath(value).is_absolute():
        return True
    return ".." in value.replace("\\", "/").split("/")


def _walk_string_values(value: Any, path_parts: list[str]) -> list[tuple[str, str]]:
    values: list[tuple[str, str]] = []
    if isinstance(value, str):
        values.append((_path_label(path_parts), value))
    elif isinstance(value, dict):
        for key, child in value.items():
            values.extend(_walk_string_values(child, [*path_parts, str(key)]))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            values.extend(_walk_string_values(child, [*path_parts, str(index)]))
    return values


def _validate_host_data_ref_safety(path: Path, payload: dict[str, Any]) -> list[str]:
    timeframe_and_data = payload.get("timeframe_and_data")
    if not isinstance(timeframe_and_data, dict):
        return []
    host_data_refs = timeframe_and_data.get("host_data_refs")
    if not isinstance(host_data_refs, list):
        return []

    errors: list[str] = []
    for value_path, value in _walk_string_values(
        host_data_refs,
        ["timeframe_and_data", "host_data_refs"],
    ):
        if _is_unsafe_reference_string(value):
            errors.append(f"{path}: {value_path} unsafe host-data reference string: {value!r}")
    return errors


def _validate_nested_side_labels(
    path: Path,
    root_path: str,
    root_group: Any,
    root_side: str,
) -> list[str]:
    errors: list[str] = []
    for group_path, group, depth in _walk_groups(root_group, root_path.split("."), 1):
        if depth == 1 or not isinstance(group, dict) or "side" not in group:
            continue
        nested_side = group.get("side")
        if nested_side not in SIDE_LABELS:
            errors.append(f"{path}: {group_path}.side invalid side label: {nested_side!r}")
        elif nested_side != root_side:
            errors.append(
                f"{path}: {group_path}.side {nested_side!r} contradicts root side "
                f"{root_side!r}"
            )
    return errors


def _validate_no_side_labels(
    path: Path,
    roots: list[tuple[str, Any]],
    reason: str,
) -> list[str]:
    errors: list[str] = []
    for root_path, root_group in roots:
        for group_path, group, _depth in _walk_groups(root_group, root_path.split("."), 1):
            if isinstance(group, dict) and "side" in group:
                errors.append(f"{path}: {group_path}.side is not allowed {reason}")
    return errors


def _section_roots(payload: dict[str, Any], section_name: str) -> list[tuple[str, Any]]:
    section = payload.get(section_name)
    if not isinstance(section, dict):
        return []
    groups = section.get("groups")
    if not isinstance(groups, list):
        return []
    return [(f"{section_name}.groups.{index}", group) for index, group in enumerate(groups)]


def _validate_both_direction_sides(path: Path, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entry_logic = payload.get("entry_logic")
    direction = entry_logic.get("direction") if isinstance(entry_logic, dict) else None

    entry_roots = _section_roots(payload, "entry_logic")
    exit_roots = _section_roots(payload, "exit_logic")
    filter_roots = _section_roots(payload, "filters")

    errors.extend(_validate_no_side_labels(path, filter_roots, "under filters.groups"))

    if direction in SINGLE_DIRECTIONS:
        errors.extend(
            _validate_no_side_labels(
                path,
                [*entry_roots, *exit_roots],
                f"when entry_logic.direction is {direction!r}",
            )
        )
        return errors

    if direction != BOTH_DIRECTION:
        return errors

    observed_entry_sides: set[str] = set()
    for root_path, root_group in entry_roots:
        if not isinstance(root_group, dict):
            continue
        side = root_group.get("side")
        if side not in SIDE_LABELS:
            errors.append(
                f"{path}: {root_path}.side must be one of {sorted(SIDE_LABELS)} "
                "when entry_logic.direction is 'both'"
            )
            continue
        observed_entry_sides.add(side)
        errors.extend(_validate_nested_side_labels(path, root_path, root_group, side))

    for required_side in sorted(SIDE_LABELS):
        if required_side not in observed_entry_sides:
            errors.append(
                f"{path}: entry_logic.direction 'both' requires at least one "
                f"{required_side!r} root entry group"
            )

    for root_path, root_group in exit_roots:
        if not isinstance(root_group, dict):
            continue
        side = root_group.get("side")
        if side not in SIDE_LABELS:
            errors.append(
                f"{path}: {root_path}.side must be one of {sorted(SIDE_LABELS)} "
                "when entry_logic.direction is 'both'"
            )
            continue
        errors.extend(_validate_nested_side_labels(path, root_path, root_group, side))

    return errors


def validate_strategy_specs(
    strategy_specs_dir: Path = DEFAULT_STRATEGY_SPECS_DIR,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    """Return validation errors for Strategy Spec artifacts, or [] when valid."""

    del repo_root

    if not strategy_specs_dir.exists():
        return []

    strategy_spec_files = sorted(strategy_specs_dir.rglob("*.strategy_spec.json"))
    if not strategy_spec_files:
        return []

    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    errors: list[str] = []
    known_strategy_spec_ids: set[str] = set()
    id_paths: dict[str, Path] = {}

    for path in strategy_spec_files:
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None:
            continue

        strategy_spec_id = payload.get("strategy_spec_id")
        if isinstance(strategy_spec_id, str):
            expected_name = f"{strategy_spec_id}.strategy_spec.json"
            if path.name != expected_name:
                errors.append(f"{path}: filename must be {expected_name}")
            if strategy_spec_id in known_strategy_spec_ids:
                errors.append(
                    f"{path}: duplicate strategy_spec_id {strategy_spec_id}; "
                    f"first seen at {id_paths[strategy_spec_id]}"
                )
            known_strategy_spec_ids.add(strategy_spec_id)
            id_paths.setdefault(strategy_spec_id, path)
        else:
            errors.append(f"{path}: missing valid strategy_spec_id")

        errors.extend(_validate_closed_operator_enum(path, payload))
        errors.extend(_validate_condition_group_depth(path, payload))
        errors.extend(_validate_free_parameters(path, payload))
        errors.extend(_validate_forbidden_keys(path, payload))
        errors.extend(_validate_composed_operands(path, payload))
        errors.extend(_validate_parameter_bound_lookbacks(path, payload))
        errors.extend(_validate_atr_stop(path, payload))
        errors.extend(_validate_online_ohlcv_primitives(path, payload))
        errors.extend(_validate_non_authority_flags(path, payload))
        errors.extend(_validate_host_data_ref_safety(path, payload))
        errors.extend(_validate_both_direction_sides(path, payload))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy-specs-dir", type=Path, default=DEFAULT_STRATEGY_SPECS_DIR)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_strategy_specs(
        strategy_specs_dir=args.strategy_specs_dir,
        schema_path=args.schema,
        repo_root=REPO_ROOT,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.strategy_specs_dir.exists():
        print(f"OK: {args.strategy_specs_dir} does not exist; nothing to validate")
    else:
        print(f"OK: Strategy Spec artifacts under {args.strategy_specs_dir} validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
