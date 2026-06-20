"""Validate deterministic scratch-only walk-forward run reports."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORTS_DIR = REPO_ROOT / "scratch" / "WP-LAB-WALKFORWARD-RUN-01"
DEFAULT_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "walkforward_run_report.schema.json"
REQUIRED_NON_AUTHORITY_FLAGS = {
    "not canonical evidence",
    "not promotion evidence",
    "not ranking authority",
    "not readiness authority",
    "not paper/live authority",
    "not candidate registration",
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
    "runner_command",
    "result_population_write",
    "canonical_write",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _format_schema_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    return f"{location}: {error.message}" if location else error.message


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError("timestamp must be UTC")
    return parsed


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


def _semantic_errors(path: Path, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    flags = set(payload.get("non_authority_flags", []))
    if flags != REQUIRED_NON_AUTHORITY_FLAGS:
        errors.append(f"{path}: non_authority_flags must equal the required six-flag set")
    for key_path, key in _walk_keys(payload, []):
        if key.lower() in FORBIDDEN_AUTHORITY_KEYS:
            errors.append(f"{path}: forbidden authority-like key at {key_path}: {key}")

    folds = payload.get("fold_results", [])
    previous_order = 0
    seen_ids: set[str] = set()
    for fold in folds:
        fold_id = fold["fold_id"]
        order = fold["fold_order"]
        if fold_id in seen_ids:
            errors.append(f"{path}: duplicate fold_id {fold_id}")
        seen_ids.add(fold_id)
        if order <= previous_order:
            errors.append(f"{path}: fold_order must be strictly increasing")
        previous_order = order
        try:
            selection_start = _parse_utc(fold["selection_window"]["start_utc"])
            selection_end = _parse_utc(fold["selection_window"]["end_utc"])
            evaluation_start = _parse_utc(fold["evaluation_window"]["start_utc"])
            evaluation_end = _parse_utc(fold["evaluation_window"]["end_utc"])
            if selection_start >= selection_end:
                errors.append(f"{path}: {fold_id} selection start must precede end")
            if evaluation_start >= evaluation_end:
                errors.append(f"{path}: {fold_id} evaluation start must precede end")
            if evaluation_start < selection_end:
                errors.append(f"{path}: {fold_id} selection/evaluation windows overlap")
        except (KeyError, TypeError, ValueError):
            errors.append(f"{path}: {fold_id} windows must contain valid UTC timestamps")

        posture = fold["variant_count_posture"]
        if posture["attempted"] != posture["successful"] + posture["errored"]:
            errors.append(f"{path}: {fold_id} attempted count must equal successful + errored")
        accounted = posture["attempted"] + posture["not_attempted"]
        if accounted != posture["declared"]:
            errors.append(f"{path}: {fold_id} attempted + not_attempted must equal declared")
        if len(fold["variant_results"]) != posture["attempted"]:
            errors.append(f"{path}: {fold_id} variant_results length must equal attempted")
        if posture["denominator_preserved"] is not (accounted == posture["declared"]):
            errors.append(f"{path}: {fold_id} denominator_preserved is inconsistent")

    aggregate = payload.get("aggregate_degradation", {})
    if aggregate.get("fold_count") != len(folds):
        errors.append(f"{path}: aggregate fold_count must equal fold_results length")
    status_total = sum(
        int(aggregate.get(key, 0))
        for key in ("successful_fold_count", "partial_fold_count", "unavailable_or_errored_fold_count")
    )
    if status_total != len(folds):
        errors.append(f"{path}: aggregate fold status counts must equal fold_count")
    pair_count = sum(
        fold["degradation_metrics"]["comparable_variant_count"]
        for fold in folds
        if fold.get("degradation_metrics") is not None
    )
    if aggregate.get("comparable_variant_pairs") != pair_count:
        errors.append(f"{path}: aggregate comparable_variant_pairs is inconsistent")
    return errors


def validate_walkforward_run_reports(
    reports_dir: Path = DEFAULT_REPORTS_DIR,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
    explicit_paths: list[Path] | None = None,
) -> list[str]:
    schema = load_json(schema_path)
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    paths = explicit_paths
    if paths is None:
        default_path = reports_dir / "walkforward_run_report.json"
        paths = [default_path] if default_path.exists() else []
    errors: list[str] = []
    for path in paths:
        try:
            payload = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        schema_errors = [
            f"{path}: {_format_schema_error(error)}"
            for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.path))
        ]
        errors.extend(schema_errors)
        if not schema_errors:
            errors.extend(_semantic_errors(path, payload))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    args = parser.parse_args()
    errors = validate_walkforward_run_reports(
        reports_dir=args.reports_dir,
        schema_path=args.schema,
        explicit_paths=args.paths or None,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: walk-forward run reports validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
