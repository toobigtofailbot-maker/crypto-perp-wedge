"""Validate non-executing Strategy Spec JSON artifacts."""

from __future__ import annotations

import argparse
import json
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
COMPOSITION_TYPE = "scale_by_one_minus_parameter"
COMPOSED_BASE_OPERAND_TYPES = {"data_ref", "indicator_ref"}
COMPOSED_PARAMETER_OPERAND_TYPE = "parameter_ref"
MAX_CONDITION_GROUP_DEPTH = 3
MAX_FREE_PARAMETERS = 5
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

                    if operand.get("composition_type") != COMPOSITION_TYPE:
                        errors.append(
                            f"{path}: {operand_path}.composition_type must be {COMPOSITION_TYPE!r}"
                        )
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
        errors.extend(_validate_non_authority_flags(path, payload))
        errors.extend(_validate_host_data_ref_safety(path, payload))

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
