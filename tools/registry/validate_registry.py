"""Validate the candidate registry against its JSON Schema and repo references."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY_PATH = REPO_ROOT / "research" / "candidate_registry.jsonl"
DEFAULT_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "candidate_registry.schema.json"
DEFAULT_TRIAL_LOG_PATH = REPO_ROOT / "research" / "trial_log.jsonl"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_trial_ids(trial_log_path: Path) -> set[str]:
    trial_ids: set[str] = set()
    if not trial_log_path.exists():
        return trial_ids

    for line_number, line in enumerate(trial_log_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{trial_log_path}:{line_number}: invalid JSON: {exc}") from exc
        trial_id = row.get("trial_id")
        if isinstance(trial_id, str):
            trial_ids.add(trial_id)
    return trial_ids


def load_registry_rows(registry_path: Path) -> list[tuple[int, dict[str, Any]]]:
    rows: list[tuple[int, dict[str, Any]]] = []
    for line_number, line in enumerate(registry_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            rows.append((line_number, {"__json_error__": str(exc)}))
            continue
        rows.append((line_number, row))
    return rows


def _format_schema_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    if location:
        return f"{location}: {error.message}"
    return error.message


def validate_registry(
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
    trial_log_path: Path = DEFAULT_TRIAL_LOG_PATH,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    """Return validation errors for the registry, or an empty list when valid."""

    errors: list[str] = []
    if not registry_path.exists():
        return [f"registry file not found: {registry_path}"]
    if not schema_path.exists():
        return [f"schema file not found: {schema_path}"]

    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)
    known_trial_ids = load_trial_ids(trial_log_path)

    candidate_ids: set[str] = set()
    for line_number, row in load_registry_rows(registry_path):
        if "__json_error__" in row:
            errors.append(f"{registry_path}:{line_number}: invalid JSON: {row['__json_error__']}")
            continue

        row_label = row.get("candidate_id", f"line {line_number}")
        if isinstance(row_label, str):
            if row_label in candidate_ids:
                errors.append(f"{registry_path}:{line_number}: duplicate candidate_id {row_label}")
            candidate_ids.add(row_label)

        for schema_error in sorted(validator.iter_errors(row), key=lambda err: list(err.path)):
            errors.append(
                f"{registry_path}:{line_number} ({row_label}): {_format_schema_error(schema_error)}"
            )

        for path_field in ("hypothesis_md_path", "decision_record_path"):
            path_value = row.get(path_field)
            if path_value is None:
                continue
            if not isinstance(path_value, str):
                continue
            ref_path = repo_root / path_value
            if not ref_path.exists():
                errors.append(
                    f"{registry_path}:{line_number} ({row_label}): "
                    f"{path_field} does not exist: {path_value}"
                )

        for trial_id in row.get("trial_ids", []):
            if trial_id not in known_trial_ids:
                errors.append(
                    f"{registry_path}:{line_number} ({row_label}): "
                    f"trial_id not found in {trial_log_path}: {trial_id}"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--trial-log", type=Path, default=DEFAULT_TRIAL_LOG_PATH)
    args = parser.parse_args()

    errors = validate_registry(
        registry_path=args.registry,
        schema_path=args.schema,
        trial_log_path=args.trial_log,
        repo_root=REPO_ROOT,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"OK: {args.registry} validates against {args.schema}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
