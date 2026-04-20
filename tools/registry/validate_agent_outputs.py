"""Validate JSON agent_output artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "agent_outputs"
AGENT_OUTPUT_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "agent_output.schema.json"


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


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_repo_ref(repo_root: Path, ref_path: Any) -> Path | None:
    if not isinstance(ref_path, str) or not ref_path:
        return None
    candidate = Path(ref_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (repo_root / candidate).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError:
        return None
    return resolved


def validate_agent_outputs(
    agent_outputs_dir: Path = DEFAULT_AGENT_OUTPUTS_DIR,
    schema_path: Path = AGENT_OUTPUT_SCHEMA_PATH,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    """Return validation errors for agent_output artifacts, or an empty list when valid."""

    if not agent_outputs_dir.exists():
        return []

    agent_output_files = sorted(agent_outputs_dir.rglob("*.agent_output.json"))
    if not agent_output_files:
        return []

    errors: list[str] = []
    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    known_agent_output_ids: set[str] = set()
    agent_output_id_paths: dict[str, Path] = {}

    for path in agent_output_files:
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None:
            continue

        agent_output_id = payload.get("agent_output_id")
        if isinstance(agent_output_id, str):
            expected_name = f"{agent_output_id}.agent_output.json"
            if path.name != expected_name:
                errors.append(f"{path}: filename must be {expected_name}")
            if agent_output_id in known_agent_output_ids:
                errors.append(
                    f"{path}: duplicate agent_output_id {agent_output_id}; "
                    f"first seen at {agent_output_id_paths[agent_output_id]}"
                )
            known_agent_output_ids.add(agent_output_id)
            agent_output_id_paths.setdefault(agent_output_id, path)

        for input_ref in payload.get("input_data_refs", []):
            ref_path_value = input_ref.get("path") if isinstance(input_ref, dict) else None
            ref_path = _resolve_repo_ref(repo_root, ref_path_value)
            if ref_path is None:
                errors.append(f"{path}: invalid repo-relative input_data_refs path: {ref_path_value}")
                continue
            if not ref_path.exists():
                errors.append(f"{path}: input_data_refs path does not exist: {ref_path_value}")
                continue
            expected_sha256 = input_ref.get("sha256")
            actual_sha256 = _sha256_file(ref_path)
            if expected_sha256 != actual_sha256:
                errors.append(
                    f"{path}: input_data_refs sha256 mismatch for {ref_path_value}: "
                    f"expected {expected_sha256}, got {actual_sha256}"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent-outputs-dir", type=Path, default=DEFAULT_AGENT_OUTPUTS_DIR)
    parser.add_argument("--schema", type=Path, default=AGENT_OUTPUT_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_agent_outputs(
        agent_outputs_dir=args.agent_outputs_dir,
        schema_path=args.schema,
        repo_root=REPO_ROOT,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.agent_outputs_dir.exists():
        print(f"OK: {args.agent_outputs_dir} does not exist; nothing to validate")
    else:
        print(f"OK: agent_output artifacts under {args.agent_outputs_dir} validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
