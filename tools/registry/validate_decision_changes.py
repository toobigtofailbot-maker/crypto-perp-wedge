"""Validate JSON decision_change artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.registry.validate_registry import (
    DEFAULT_REGISTRY_PATH,
    load_registry_rows,
)


DEFAULT_DECISION_CHANGES_DIR = REPO_ROOT / "research" / "decision_changes"
DEFAULT_EXPERIMENTS_DIR = REPO_ROOT / "research" / "experiments"
DECISION_CHANGE_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "decision_change.schema.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_candidate_ids(registry_path: Path = DEFAULT_REGISTRY_PATH) -> set[str]:
    return {
        row["candidate_id"]
        for _, row in load_registry_rows(registry_path)
        if isinstance(row.get("candidate_id"), str)
    }


def load_report_ids(experiments_dir: Path = DEFAULT_EXPERIMENTS_DIR) -> set[str]:
    report_ids: set[str] = set()
    if not experiments_dir.exists():
        return report_ids

    for path in sorted(experiments_dir.rglob("*.report.json")):
        try:
            payload = load_json(path)
        except json.JSONDecodeError:
            continue
        report_id = payload.get("report_id")
        if isinstance(report_id, str):
            report_ids.add(report_id)
    return report_ids


def _format_schema_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    if location:
        return f"{location}: {error.message}"
    return error.message


def _validate_json_file(path: Path, validator: Draft7Validator) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        return None, [f"{path}: invalid JSON: {exc}"]

    for schema_error in sorted(validator.iter_errors(payload), key=lambda err: list(err.path)):
        errors.append(f"{path}: {_format_schema_error(schema_error)}")
    return payload, errors


def validate_decision_changes(
    decision_changes_dir: Path = DEFAULT_DECISION_CHANGES_DIR,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    experiments_dir: Path = DEFAULT_EXPERIMENTS_DIR,
    schema_path: Path = DECISION_CHANGE_SCHEMA_PATH,
) -> list[str]:
    """Return validation errors for decision_change artifacts, or an empty list when valid."""

    if not decision_changes_dir.exists():
        return []

    decision_files = sorted(decision_changes_dir.rglob("*.decision_change.json"))
    if not decision_files:
        return []

    errors: list[str] = []
    candidate_ids = load_candidate_ids(registry_path)
    report_ids = load_report_ids(experiments_dir)

    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    payloads: list[tuple[Path, dict[str, Any]]] = []
    decision_id_paths: dict[str, Path] = {}
    known_decision_ids: set[str] = set()

    for path in decision_files:
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None:
            continue
        payloads.append((path, payload))

        decision_change_id = payload.get("decision_change_id")
        if isinstance(decision_change_id, str):
            if decision_change_id in known_decision_ids:
                errors.append(
                    f"{path}: duplicate decision_change_id {decision_change_id}; "
                    f"first seen at {decision_id_paths[decision_change_id]}"
                )
            known_decision_ids.add(decision_change_id)
            decision_id_paths.setdefault(decision_change_id, path)

    for path, payload in payloads:
        candidate_id = payload.get("candidate_id")
        if candidate_id not in candidate_ids:
            errors.append(f"{path}: candidate_id not found in registry: {candidate_id}")

        for report_id in payload.get("report_ids", []):
            if report_id not in report_ids:
                errors.append(f"{path}: report_id not found in discovered reports: {report_id}")

        decision_change_id = payload.get("decision_change_id")
        supersedes_decision_id = payload.get("supersedes_decision_id")
        if supersedes_decision_id is None:
            continue
        if supersedes_decision_id == decision_change_id:
            errors.append(f"{path}: supersedes_decision_id cannot reference itself: {supersedes_decision_id}")
        elif supersedes_decision_id not in known_decision_ids:
            errors.append(
                f"{path}: supersedes_decision_id not found in discovered decision changes: "
                f"{supersedes_decision_id}"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision-changes-dir", type=Path, default=DEFAULT_DECISION_CHANGES_DIR)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--experiments-dir", type=Path, default=DEFAULT_EXPERIMENTS_DIR)
    parser.add_argument("--schema", type=Path, default=DECISION_CHANGE_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_decision_changes(
        decision_changes_dir=args.decision_changes_dir,
        registry_path=args.registry,
        experiments_dir=args.experiments_dir,
        schema_path=args.schema,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.decision_changes_dir.exists():
        print(f"OK: {args.decision_changes_dir} does not exist; nothing to validate")
    else:
        print(f"OK: decision_change artifacts under {args.decision_changes_dir} validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
