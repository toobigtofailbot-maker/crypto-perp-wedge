"""Validate JSON experiment plan and report artifacts."""

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


DEFAULT_EXPERIMENTS_DIR = REPO_ROOT / "research" / "experiments"
PLAN_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "experiment_plan.schema.json"
REPORT_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "experiment_report.schema.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_candidate_ids(registry_path: Path = DEFAULT_REGISTRY_PATH) -> set[str]:
    return {
        row["candidate_id"]
        for _, row in load_registry_rows(registry_path)
        if isinstance(row.get("candidate_id"), str)
    }


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


def validate_experiment_artifacts(
    experiments_dir: Path = DEFAULT_EXPERIMENTS_DIR,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    plan_schema_path: Path = PLAN_SCHEMA_PATH,
    report_schema_path: Path = REPORT_SCHEMA_PATH,
) -> list[str]:
    """Return validation errors for experiment artifacts, or an empty list when valid."""

    if not experiments_dir.exists():
        return []

    errors: list[str] = []
    candidate_ids = load_candidate_ids(registry_path)

    plan_schema = load_json(plan_schema_path)
    report_schema = load_json(report_schema_path)
    Draft7Validator.check_schema(plan_schema)
    Draft7Validator.check_schema(report_schema)
    plan_validator = Draft7Validator(plan_schema)
    report_validator = Draft7Validator(report_schema)

    known_plan_ids: set[str] = set()
    plan_files = sorted(experiments_dir.rglob("*.plan.json"))
    report_files = sorted(experiments_dir.rglob("*.report.json"))
    yaml_files = sorted(experiments_dir.rglob("*.plan.yaml")) + sorted(
        experiments_dir.rglob("*.report.yaml")
    )

    for path in yaml_files:
        errors.append(
            f"{path}: YAML experiment artifacts are unsupported in WP-6a; "
            "use *.plan.json or *.report.json instead"
        )

    for path in plan_files:
        payload, file_errors = _validate_json_file(path, plan_validator)
        errors.extend(file_errors)
        if payload is None:
            continue
        candidate_id = payload.get("candidate_id")
        if candidate_id not in candidate_ids:
            errors.append(f"{path}: candidate_id not found in registry: {candidate_id}")
        plan_id = payload.get("plan_id")
        if isinstance(plan_id, str):
            known_plan_ids.add(plan_id)

    for path in report_files:
        payload, file_errors = _validate_json_file(path, report_validator)
        errors.extend(file_errors)
        if payload is None:
            continue
        candidate_id = payload.get("candidate_id")
        if candidate_id not in candidate_ids:
            errors.append(f"{path}: candidate_id not found in registry: {candidate_id}")
        plan_id = payload.get("plan_id")
        if plan_id not in known_plan_ids:
            errors.append(f"{path}: plan_id not found in discovered plans: {plan_id}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiments-dir", type=Path, default=DEFAULT_EXPERIMENTS_DIR)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    args = parser.parse_args()

    errors = validate_experiment_artifacts(
        experiments_dir=args.experiments_dir,
        registry_path=args.registry,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.experiments_dir.exists():
        print(f"OK: {args.experiments_dir} does not exist; nothing to validate")
    else:
        print(f"OK: JSON experiment artifacts under {args.experiments_dir} validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
