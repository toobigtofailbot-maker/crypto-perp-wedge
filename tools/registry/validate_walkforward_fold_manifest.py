"""Validate non-executing walk-forward fold manifest JSON artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFESTS_DIR = REPO_ROOT / "research" / "walkforward_fold_manifests"
DEFAULT_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "walkforward_fold_manifest.schema.json"

COUNT_FIELDS = (
    "successful_count",
    "failed_count",
    "errored_count",
    "invalid_count",
    "data_unavailable_count",
    "not_attempted_count",
)
NON_AUTHORITY_TRUE_FLAGS = {
    "not_executable",
    "not_runner_authority",
    "not_result_population_write_authority",
    "not_canonical_result_population",
    "not_candidate_approval",
    "not_ranking_authority",
    "not_recommendation_authority",
    "not_readiness_authority",
    "not_promotion_authority",
    "not_gate_authority",
    "not_runtime_authority",
    "not_paper_live_authority",
    "not_broker_exchange_order_authority",
}
FORBIDDEN_AUTHORITY_KEYS = {
    "approval_action",
    "ranking_score",
    "recommendation",
    "readiness_update",
    "promotion",
    "promote",
    "gate_action",
    "runtime_action",
    "paper_action",
    "live_action",
    "order_instruction",
    "broker_instruction",
    "exchange_instruction",
    "runner_command",
    "result_population_write",
    "canonical_write",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _format_schema_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    if location:
        return f"{location}: {error.message}"
    return error.message


def _parse_utc(value: str, path: Path, label: str) -> tuple[datetime | None, list[str]]:
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None, [f"{path}: {label} must be an ISO-8601 datetime"]
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        return None, [f"{path}: {label} must be UTC"]
    return parsed.astimezone(timezone.utc), []


def _walk_keys(value: Any, path_parts: list[str]) -> list[tuple[str, str]]:
    keys: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_path = ".".join([*path_parts, str(key)])
            keys.append((key_path, str(key)))
            keys.extend(_walk_keys(child, [*path_parts, str(key)]))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            keys.extend(_walk_keys(child, [*path_parts, str(index)]))
    return keys


def _validate_forbidden_authority_keys(path: Path, payload: dict[str, Any]) -> list[str]:
    return [
        f"{path}: forbidden authority-like key at {key_path}: {key}"
        for key_path, key in _walk_keys(payload, [])
        if key.lower() in FORBIDDEN_AUTHORITY_KEYS
    ]


def _validate_non_authority(path: Path, payload: dict[str, Any]) -> list[str]:
    declaration = payload.get("non_authority_declaration")
    if not isinstance(declaration, dict):
        return [f"{path}: non_authority_declaration must be present as an object"]
    return [
        f"{path}: non_authority_declaration.{flag} must be true"
        for flag in sorted(NON_AUTHORITY_TRUE_FLAGS)
        if declaration.get(flag) is not True
    ]


def _validate_gap_object(path: Path, fold: dict[str, Any], key: str) -> list[str]:
    gap = fold.get(key)
    if not isinstance(gap, dict):
        return []
    mode = gap.get("mode")
    bars = gap.get("bars")
    duration = gap.get("duration")
    errors: list[str] = []
    if mode == "none" and (bars is not None or duration is not None):
        errors.append(f"{path}: {fold.get('fold_id')}.{key} mode none requires null bars and duration")
    if mode == "bars" and (not isinstance(bars, int) or bars < 0 or duration is not None):
        errors.append(f"{path}: {fold.get('fold_id')}.{key} mode bars requires non-negative bars and null duration")
    if mode == "duration" and (bars is not None or not isinstance(duration, str) or not duration):
        errors.append(f"{path}: {fold.get('fold_id')}.{key} mode duration requires null bars and non-empty duration")
    return errors


def _known_counts(fold: dict[str, Any]) -> list[int] | None:
    values = [fold.get(field) for field in COUNT_FIELDS]
    if any(value is None for value in values):
        return None
    return [int(value) for value in values]


def _validate_fold_semantics(path: Path, payload: dict[str, Any]) -> list[str]:
    folds = payload.get("folds")
    if not isinstance(folds, list):
        return []

    errors: list[str] = []
    seen_ids: set[str] = set()
    seen_orders: set[int] = set()
    previous_order = 0

    for fold in folds:
        if not isinstance(fold, dict):
            continue
        fold_id = fold.get("fold_id")
        fold_order = fold.get("fold_order")
        if fold_id in seen_ids:
            errors.append(f"{path}: duplicate fold_id {fold_id}")
        seen_ids.add(str(fold_id))
        if fold_order in seen_orders:
            errors.append(f"{path}: duplicate fold_order {fold_order}")
        if isinstance(fold_order, int) and fold_order <= previous_order:
            errors.append(f"{path}: fold_order must be strictly increasing")
        if isinstance(fold_order, int):
            seen_orders.add(fold_order)
            previous_order = fold_order

        parsed: dict[str, datetime] = {}
        for key in (
            "selection_window_start_utc",
            "selection_window_end_utc",
            "evaluation_window_start_utc",
            "evaluation_window_end_utc",
        ):
            value = fold.get(key)
            if isinstance(value, str):
                parsed_value, parse_errors = _parse_utc(value, path, f"{fold_id}.{key}")
                errors.extend(parse_errors)
                if parsed_value is not None:
                    parsed[key] = parsed_value

        warmup_start = fold.get("warmup_window_start_utc")
        warmup_end = fold.get("warmup_window_end_utc")
        if (warmup_start is None) != (warmup_end is None):
            errors.append(f"{path}: {fold_id} warmup start/end must both be null or both be set")
        if isinstance(warmup_start, str) and isinstance(warmup_end, str):
            parsed_start, start_errors = _parse_utc(warmup_start, path, f"{fold_id}.warmup_window_start_utc")
            parsed_end, end_errors = _parse_utc(warmup_end, path, f"{fold_id}.warmup_window_end_utc")
            errors.extend(start_errors)
            errors.extend(end_errors)
            if parsed_start and parsed_end:
                if parsed_start >= parsed_end:
                    errors.append(f"{path}: {fold_id} warmup window start must be before warmup window end")
                if "selection_window_start_utc" in parsed and parsed_end > parsed["selection_window_start_utc"]:
                    errors.append(f"{path}: {fold_id} warmup must end no later than selection start")

        if len(parsed) == 4:
            if parsed["selection_window_start_utc"] >= parsed["selection_window_end_utc"]:
                errors.append(f"{path}: {fold_id} selection window start must be before selection window end")
            if parsed["evaluation_window_start_utc"] >= parsed["evaluation_window_end_utc"]:
                errors.append(f"{path}: {fold_id} evaluation window start must be before evaluation window end")
            if parsed["evaluation_window_start_utc"] < parsed["selection_window_end_utc"]:
                errors.append(f"{path}: {fold_id} evaluation must not overlap selection")

        errors.extend(_validate_gap_object(path, fold, "purge"))
        errors.extend(_validate_gap_object(path, fold, "embargo"))

        if fold.get("result_population_ref") is None and fold.get("planned_result_population_ref") is None:
            errors.append(f"{path}: {fold_id} must reference a result population or planned result population")
        if fold.get("result_population_ref") is not None and fold.get("planned_result_population_ref") is not None:
            errors.append(f"{path}: {fold_id} must not set both result_population_ref and planned_result_population_ref")

        counts = _known_counts(fold)
        if counts is not None and sum(counts) != fold.get("declared_variant_count"):
            errors.append(f"{path}: {fold_id} known outcome counts must sum to declared_variant_count")

        lineage_refs = fold.get("lineage_refs")
        if isinstance(lineage_refs, list):
            ref_ids = [ref.get("ref_id") for ref in lineage_refs if isinstance(ref, dict)]
            if len(ref_ids) != len(set(ref_ids)):
                errors.append(f"{path}: {fold_id} lineage_refs ref_id values must be unique")

    return errors


def _validate_json_file(path: Path, validator: Draft7Validator) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        return None, [f"{path}: invalid JSON: {exc}"]
    errors = [
        f"{path}: {_format_schema_error(schema_error)}"
        for schema_error in sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
    ]
    return payload, errors


def validate_walkforward_fold_manifests(
    manifests_dir: Path = DEFAULT_MANIFESTS_DIR,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
    explicit_paths: list[Path] | None = None,
) -> list[str]:
    schema = load_json(schema_path)
    validator = Draft7Validator(schema)
    paths = explicit_paths
    if paths is None:
        paths = sorted(manifests_dir.glob("*.walkforward_fold_manifest.json")) if manifests_dir.exists() else []

    errors: list[str] = []
    for path in paths:
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None or file_errors:
            continue
        errors.extend(_validate_forbidden_authority_keys(path, payload))
        errors.extend(_validate_non_authority(path, payload))
        errors.extend(_validate_fold_semantics(path, payload))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Optional manifest file paths to validate")
    parser.add_argument("--manifests-dir", type=Path, default=DEFAULT_MANIFESTS_DIR)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    args = parser.parse_args()

    explicit_paths = args.paths or None
    errors = validate_walkforward_fold_manifests(
        manifests_dir=args.manifests_dir,
        schema_path=args.schema,
        explicit_paths=explicit_paths,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if explicit_paths is None and not args.manifests_dir.exists():
        print(f"OK: {args.manifests_dir} does not exist; nothing to validate")
    else:
        target = ", ".join(str(path) for path in explicit_paths) if explicit_paths else str(args.manifests_dir)
        print(f"OK: walk-forward fold manifests validate: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
