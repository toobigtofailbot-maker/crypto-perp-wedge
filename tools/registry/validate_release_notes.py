"""Validate JSON release_notes artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


DEFAULT_DECISION_CHANGES_DIR = REPO_ROOT / "research" / "decision_changes"
DEFAULT_RELEASE_NOTES_DIR = REPO_ROOT / "research" / "release_notes"
RELEASE_NOTES_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "release_notes.schema.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def _parse_iso_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def load_decision_changes(decision_changes_dir: Path = DEFAULT_DECISION_CHANGES_DIR) -> dict[str, dict[str, Any]]:
    decision_changes: dict[str, dict[str, Any]] = {}
    if not decision_changes_dir.exists():
        return decision_changes

    for path in sorted(decision_changes_dir.rglob("*.decision_change.json")):
        try:
            payload = load_json(path)
        except json.JSONDecodeError:
            continue
        decision_change_id = payload.get("decision_change_id")
        if isinstance(decision_change_id, str):
            decision_changes[decision_change_id] = payload
    return decision_changes


def validate_release_notes(
    release_notes_dir: Path = DEFAULT_RELEASE_NOTES_DIR,
    decision_changes_dir: Path = DEFAULT_DECISION_CHANGES_DIR,
    schema_path: Path = RELEASE_NOTES_SCHEMA_PATH,
) -> list[str]:
    """Return validation errors for release_notes artifacts, or an empty list when valid."""

    if not release_notes_dir.exists():
        return []

    release_files = sorted(release_notes_dir.rglob("*.release_notes.json"))
    if not release_files:
        return []

    errors: list[str] = []
    decision_changes = load_decision_changes(decision_changes_dir)

    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    release_notes_ids: set[str] = set()
    release_notes_id_paths: dict[str, Path] = {}

    for path in release_files:
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None:
            continue

        release_notes_id = payload.get("release_notes_id")
        if isinstance(release_notes_id, str):
            if release_notes_id in release_notes_ids:
                errors.append(
                    f"{path}: duplicate release_notes_id {release_notes_id}; "
                    f"first seen at {release_notes_id_paths[release_notes_id]}"
                )
            release_notes_ids.add(release_notes_id)
            release_notes_id_paths.setdefault(release_notes_id, path)

        decision_change_id = payload.get("decision_change_id")
        decision_change = decision_changes.get(decision_change_id)
        if decision_change is None:
            errors.append(f"{path}: decision_change_id not found in discovered decision changes: {decision_change_id}")
            continue

        candidate_id = payload.get("candidate_id")
        expected_candidate_id = decision_change.get("candidate_id")
        if candidate_id != expected_candidate_id:
            errors.append(
                f"{path}: candidate_id {candidate_id} does not match decision_change "
                f"{decision_change_id}: {expected_candidate_id}"
            )

        stage_transition = decision_change.get("stage_transition", {})
        expected_stage = stage_transition.get("to_stage") if isinstance(stage_transition, dict) else None
        effective_stage = payload.get("effective_stage")
        if effective_stage != expected_stage:
            errors.append(
                f"{path}: effective_stage {effective_stage} does not match decision_change "
                f"{decision_change_id} to_stage: {expected_stage}"
            )

        released_at = _parse_iso_datetime(payload.get("released_at"))
        decided_at = _parse_iso_datetime(decision_change.get("decided_at"))
        if released_at is not None and decided_at is not None and released_at < decided_at:
            errors.append(
                f"{path}: released_at {payload.get('released_at')} is before decision_change "
                f"{decision_change_id} decided_at {decision_change.get('decided_at')}"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-notes-dir", type=Path, default=DEFAULT_RELEASE_NOTES_DIR)
    parser.add_argument("--decision-changes-dir", type=Path, default=DEFAULT_DECISION_CHANGES_DIR)
    parser.add_argument("--schema", type=Path, default=RELEASE_NOTES_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_release_notes(
        release_notes_dir=args.release_notes_dir,
        decision_changes_dir=args.decision_changes_dir,
        schema_path=args.schema,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.release_notes_dir.exists():
        print(f"OK: {args.release_notes_dir} does not exist; nothing to validate")
    else:
        print(f"OK: release_notes artifacts under {args.release_notes_dir} validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
