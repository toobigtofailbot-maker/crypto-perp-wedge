"""Validate non-executing indicator catalog JSON artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INDICATOR_CATALOGS_DIR = REPO_ROOT / "research" / "indicator_catalogs"
DEFAULT_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "indicator_catalog.schema.json"
APPROVED_INDICATOR_BUILTINS = {
    "sma": "sma_v1",
    "ema": "ema_v1",
    "atr": "atr_v1",
    "stddev": "stddev_v1",
    "rsi": "rsi_v1",
    "donchian": "donchian_v1",
    "ma_distance": "ma_distance_v1",
    "rvol": "rvol_v1",
    "rolling_vwap": "rolling_vwap_v1",
}
REQUIRED_CONTRACT_OBJECTS = {
    "implementation_binding",
    "input_contract",
    "parameter_contract",
    "output_contract",
    "warmup_contract",
    "null_handling",
    "non_authority",
}
FORBIDDEN_EXECUTABLE_KEYS = {
    "expression",
    "formula",
    "code",
    "script",
    "eval",
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
}
NON_EXECUTION_TRUE_FLAGS = {
    "interface_declaration_only",
    "not_executable",
    "not_compiler_implementation",
    "not_runner_authority",
    "not_sweep_authority",
    "not_result_authority",
    "not_runtime_authority",
    "not_paper_live_authority",
    "not_recommendation_authority",
    "not_ranking_authority",
    "not_readiness_authority",
    "not_transition_authority",
    "not_gate_authority",
    "not_order_authority",
    "not_broker_exchange_authority",
}
ENTRY_NON_AUTHORITY_TRUE_FLAGS = {
    "not_runtime_authority",
    "not_paper_live_authority",
    "not_recommendation_authority",
    "not_ranking_authority",
    "not_readiness_authority",
    "not_transition_authority",
    "not_gate_authority",
    "not_order_authority",
    "not_broker_exchange_authority",
}
REVIEW_NON_AUTHORITY_TRUE_FLAGS = {
    "not_compiler_approval",
    "not_runner_authority",
    "not_sweep_authority",
    "not_result_authority",
    "not_runtime_authority",
    "not_paper_live_authority",
    "not_gate_satisfaction",
    "not_recommendation_authority",
    "not_ranking_authority",
    "not_readiness_authority",
    "not_transition_authority",
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


def _get_path(document: Mapping[str, Any], dotted_path: str) -> tuple[bool, Any]:
    current: Any = document
    for part in dotted_path.split("."):
        if isinstance(current, Mapping):
            if part not in current:
                return False, None
            current = current[part]
            continue
        if isinstance(current, list) and part.isdigit():
            index = int(part)
            if index >= len(current):
                return False, None
            current = current[index]
            continue
        return False, None
    return True, current


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


def _validate_forbidden_keys(path: Path, payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for key_path, key in _walk_keys(payload, []):
        if key.lower() in FORBIDDEN_EXECUTABLE_KEYS:
            errors.append(f"{path}: forbidden executable/authority key name at {key_path}: {key}")
    return errors


def _validate_true_flags(
    path: Path,
    payload: Mapping[str, Any],
    object_path: str,
    required_flags: set[str],
) -> list[str]:
    found, current = _get_path(payload, object_path)
    if not found or not isinstance(current, dict):
        return [f"{path}: {object_path} must be present as an object"]
    return [
        f"{path}: {object_path}.{flag} must be true"
        for flag in sorted(required_flags)
        if current.get(flag) is not True
    ]


def _entry_by_id(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    entries = payload.get("entries")
    if not isinstance(entries, list):
        return {}
    by_id: dict[str, Mapping[str, Any]] = {}
    for entry in entries:
        if isinstance(entry, Mapping) and isinstance(entry.get("indicator_id"), str):
            by_id.setdefault(entry["indicator_id"], entry)
    return by_id


def _parameters_by_name(entry: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    parameters = entry.get("parameter_contract", {}).get("parameters", [])
    if not isinstance(parameters, list):
        return {}
    return {
        parameter["name"]: parameter
        for parameter in parameters
        if isinstance(parameter, Mapping) and isinstance(parameter.get("name"), str)
    }


def _outputs_by_field(entry: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    outputs = entry.get("output_contract", {}).get("outputs", [])
    if not isinstance(outputs, list):
        return {}
    return {
        output["field"]: output
        for output in outputs
        if isinstance(output, Mapping) and isinstance(output.get("field"), str)
    }


def _entry_path(entry_index_by_id: Mapping[str, int], indicator_id: str) -> str:
    index = entry_index_by_id.get(indicator_id)
    if index is None:
        return f"entries.{indicator_id}"
    return f"entries.{index}"


def _entry_index_by_id(payload: Mapping[str, Any]) -> dict[str, int]:
    entries = payload.get("entries")
    if not isinstance(entries, list):
        return {}
    return {
        entry["indicator_id"]: index
        for index, entry in enumerate(entries)
        if isinstance(entry, Mapping) and isinstance(entry.get("indicator_id"), str)
    }


def _validate_filename_and_id(path: Path, payload: Mapping[str, Any]) -> list[str]:
    catalog_id = payload.get("catalog_id")
    if not isinstance(catalog_id, str):
        return [f"{path}: missing valid catalog_id"]
    expected_name = f"{catalog_id}.indicator_catalog.json"
    if path.name != expected_name:
        return [f"{path}: filename must be {expected_name}"]
    return []


def _validate_exact_entry_set(path: Path, payload: Mapping[str, Any]) -> list[str]:
    entries = payload.get("entries")
    if not isinstance(entries, list):
        return [f"{path}: entries must be present as an array"]

    errors: list[str] = []
    entry_ids = [entry.get("indicator_id") for entry in entries if isinstance(entry, Mapping)]
    if len(entries) != len(APPROVED_INDICATOR_BUILTINS):
        errors.append(
            f"{path}: entries must contain exactly {len(APPROVED_INDICATOR_BUILTINS)} entries"
        )
    if set(entry_ids) != set(APPROVED_INDICATOR_BUILTINS):
        errors.append(
            f"{path}: entry indicator_id set must be exactly "
            f"{sorted(APPROVED_INDICATOR_BUILTINS)}: {entry_ids!r}"
        )
    if len(entry_ids) != len(set(entry_ids)):
        errors.append(f"{path}: duplicate indicator_id in entries: {entry_ids!r}")
    return errors


def _validate_entry_binding(path: Path, payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for indicator_id, builtin_key in APPROVED_INDICATOR_BUILTINS.items():
        entry = _entry_by_id(payload).get(indicator_id)
        if entry is None:
            continue
        binding = entry.get("implementation_binding")
        if not isinstance(binding, Mapping):
            errors.append(f"{path}: entries.{indicator_id}.implementation_binding must be an object")
            continue
        checks = {
            "builtin_key": builtin_key,
            "binding_type": "compiler_builtin_closed_set",
            "implementation_owner": "spec_signal_compiler",
            "computation_defined_in_catalog": False,
            "arbitrary_expression_allowed": False,
        }
        for key, expected in checks.items():
            if binding.get(key) != expected:
                errors.append(
                    f"{path}: entries.{indicator_id}.implementation_binding.{key} "
                    f"must be {expected!r}: {binding.get(key)!r}"
                )
    return errors


def _validate_required_contracts(path: Path, payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for indicator_id, entry in _entry_by_id(payload).items():
        for object_name in sorted(REQUIRED_CONTRACT_OBJECTS):
            if not isinstance(entry.get(object_name), Mapping):
                errors.append(f"{path}: entries.{indicator_id}.{object_name} must be present as an object")
    return errors


def _validate_conventions(path: Path, payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    entries = _entry_by_id(payload)

    ema_parameters = _parameters_by_name(entries.get("ema", {}))
    ema_expected = {
        "smoothing_convention": ["standard_ema_alpha_2_over_n_plus_1"],
        "initialization_convention": ["sma_seed_after_full_lookback"],
    }
    for name, allowed_values in ema_expected.items():
        parameter = ema_parameters.get(name)
        if parameter is None:
            errors.append(f"{path}: entries.ema parameter {name} is required")
            continue
        if parameter.get("allowed_values") != allowed_values:
            errors.append(f"{path}: entries.ema parameter {name} allowed_values must be {allowed_values!r}")
        if parameter.get("may_bind_strategy_parameter") is not False:
            errors.append(f"{path}: entries.ema parameter {name} may_bind_strategy_parameter must be false")

    atr_parameters = _parameters_by_name(entries.get("atr", {}))
    atr_expected = {
        "true_range_convention": ["wilder_true_range"],
        "smoothing_convention": ["wilder_rma"],
    }
    for name, allowed_values in atr_expected.items():
        parameter = atr_parameters.get(name)
        if parameter is None:
            errors.append(f"{path}: entries.atr parameter {name} is required")
            continue
        if parameter.get("allowed_values") != allowed_values:
            errors.append(f"{path}: entries.atr parameter {name} allowed_values must be {allowed_values!r}")
        if parameter.get("may_bind_strategy_parameter") is not False:
            errors.append(f"{path}: entries.atr parameter {name} may_bind_strategy_parameter must be false")

    stddev_parameters = _parameters_by_name(entries.get("stddev", {}))
    ddof = stddev_parameters.get("ddof")
    if ddof is None:
        errors.append(f"{path}: entries.stddev parameter ddof is required")
    else:
        if ddof.get("allowed_values") != [0, 1]:
            errors.append(f"{path}: entries.stddev parameter ddof allowed_values must be [0, 1]")
        if ddof.get("default") != 0:
            errors.append(f"{path}: entries.stddev parameter ddof default must be 0")
        if ddof.get("may_bind_strategy_parameter") is not False:
            errors.append(f"{path}: entries.stddev parameter ddof may_bind_strategy_parameter must be false")

    rsi_parameters = _parameters_by_name(entries.get("rsi", {}))
    rsi_expected = {
        "smoothing_convention": ["wilder_rma"],
        "zero_movement_policy": ["loss_zero_gain_positive_100_gain_zero_loss_positive_0_both_zero_50"],
    }
    for name, allowed_values in rsi_expected.items():
        parameter = rsi_parameters.get(name)
        if parameter is None:
            errors.append(f"{path}: entries.rsi parameter {name} is required")
            continue
        if parameter.get("allowed_values") != allowed_values:
            errors.append(f"{path}: entries.rsi parameter {name} allowed_values must be {allowed_values!r}")
        if parameter.get("may_bind_strategy_parameter") is not False:
            errors.append(f"{path}: entries.rsi parameter {name} may_bind_strategy_parameter must be false")

    donchian_outputs = set(_outputs_by_field(entries.get("donchian", {})))
    expected_donchian_outputs = {
        "upper",
        "lower",
        "mid",
        "width",
        "upper_lag1",
        "lower_lag1",
        "mid_lag1",
        "width_lag1",
    }
    if donchian_outputs != expected_donchian_outputs:
        errors.append(
            f"{path}: entries.donchian output fields must be exactly "
            f"{sorted(expected_donchian_outputs)}: {sorted(donchian_outputs)}"
        )

    ma_distance_parameters = _parameters_by_name(entries.get("ma_distance", {}))
    ma_kind = ma_distance_parameters.get("ma_kind")
    if ma_kind is None:
        errors.append(f"{path}: entries.ma_distance parameter ma_kind is required")
    else:
        if ma_kind.get("allowed_values") != ["sma"]:
            errors.append(f"{path}: entries.ma_distance parameter ma_kind allowed_values must be ['sma']")
        if ma_kind.get("default") != "sma":
            errors.append(f"{path}: entries.ma_distance parameter ma_kind default must be 'sma'")
        if ma_kind.get("may_bind_strategy_parameter") is not False:
            errors.append(
                f"{path}: entries.ma_distance parameter ma_kind may_bind_strategy_parameter must be false"
            )

    ma_distance_outputs = set(_outputs_by_field(entries.get("ma_distance", {})))
    expected_ma_distance_outputs = {"distance_abs", "distance_ratio", "distance_pct"}
    if ma_distance_outputs != expected_ma_distance_outputs:
        errors.append(
            f"{path}: entries.ma_distance output fields must be exactly "
            f"{sorted(expected_ma_distance_outputs)}: {sorted(ma_distance_outputs)}"
        )

    rvol_outputs = set(_outputs_by_field(entries.get("rvol", {})))
    expected_rvol_outputs = {"rvol", "volume_ma"}
    if rvol_outputs != expected_rvol_outputs:
        errors.append(
            f"{path}: entries.rvol output fields must be exactly "
            f"{sorted(expected_rvol_outputs)}: {sorted(rvol_outputs)}"
        )

    rolling_vwap_outputs = set(_outputs_by_field(entries.get("rolling_vwap", {})))
    expected_rolling_vwap_outputs = {"rolling_vwap"}
    if rolling_vwap_outputs != expected_rolling_vwap_outputs:
        errors.append(
            f"{path}: entries.rolling_vwap output fields must be exactly "
            f"{sorted(expected_rolling_vwap_outputs)}: {sorted(rolling_vwap_outputs)}"
        )
    return errors


def _validate_warmup_and_nulls(path: Path, payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for indicator_id, entry in _entry_by_id(payload).items():
        warmup = entry.get("warmup_contract")
        if isinstance(warmup, Mapping):
            if warmup.get("no_lookahead") is not True:
                errors.append(f"{path}: entries.{indicator_id}.warmup_contract.no_lookahead must be true")
            if warmup.get("warmup_output") != "null_until_ready":
                errors.append(
                    f"{path}: entries.{indicator_id}.warmup_contract.warmup_output "
                    "must be 'null_until_ready'"
                )
        null_handling = entry.get("null_handling")
        if isinstance(null_handling, Mapping) and (
            null_handling.get("signal_generation_policy") != "null_operand_never_true"
        ):
            errors.append(
                f"{path}: entries.{indicator_id}.null_handling.signal_generation_policy "
                "must be 'null_operand_never_true'"
            )
    return errors


def _validate_non_authority(path: Path, payload: Mapping[str, Any]) -> list[str]:
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
    entry_indexes = _entry_index_by_id(payload)
    for indicator_id in APPROVED_INDICATOR_BUILTINS:
        errors.extend(
            _validate_true_flags(
                path,
                payload,
                f"{_entry_path(entry_indexes, indicator_id)}.non_authority",
                ENTRY_NON_AUTHORITY_TRUE_FLAGS,
            )
        )
    return errors


def validate_indicator_catalogs(
    indicator_catalogs_dir: Path = DEFAULT_INDICATOR_CATALOGS_DIR,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
    allow_empty: bool = False,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    """Return validation errors for indicator catalog artifacts, or [] when valid."""

    del repo_root

    catalog_files = (
        sorted(indicator_catalogs_dir.rglob("*.indicator_catalog.json"))
        if indicator_catalogs_dir.exists()
        else []
    )
    if not catalog_files:
        if allow_empty:
            return []
        return [f"{indicator_catalogs_dir}: no indicator catalog files found"]

    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    errors: list[str] = []
    known_catalog_ids: set[str] = set()
    id_paths: dict[str, Path] = {}

    for path in catalog_files:
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None:
            continue

        catalog_id = payload.get("catalog_id")
        if isinstance(catalog_id, str):
            if catalog_id in known_catalog_ids:
                errors.append(
                    f"{path}: duplicate catalog_id {catalog_id}; first seen at {id_paths[catalog_id]}"
                )
            known_catalog_ids.add(catalog_id)
            id_paths.setdefault(catalog_id, path)

        errors.extend(_validate_filename_and_id(path, payload))
        errors.extend(_validate_exact_entry_set(path, payload))
        errors.extend(_validate_entry_binding(path, payload))
        errors.extend(_validate_required_contracts(path, payload))
        errors.extend(_validate_conventions(path, payload))
        errors.extend(_validate_warmup_and_nulls(path, payload))
        errors.extend(_validate_non_authority(path, payload))
        errors.extend(_validate_forbidden_keys(path, payload))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--indicator-catalogs-dir", type=Path, default=DEFAULT_INDICATOR_CATALOGS_DIR)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Allow a missing or empty indicator catalog directory.",
    )
    args = parser.parse_args()

    errors = validate_indicator_catalogs(
        indicator_catalogs_dir=args.indicator_catalogs_dir,
        schema_path=args.schema,
        allow_empty=args.allow_empty,
        repo_root=REPO_ROOT,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    count = (
        len(sorted(args.indicator_catalogs_dir.rglob("*.indicator_catalog.json")))
        if args.indicator_catalogs_dir.exists()
        else 0
    )
    print(f"OK: {count} indicator catalog file(s) validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
