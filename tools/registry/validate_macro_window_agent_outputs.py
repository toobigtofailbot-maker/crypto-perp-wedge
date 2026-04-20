"""Validate JSON macro_window_agent_output artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MACRO_WINDOW_AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "macro_window_agent_outputs"
MACRO_WINDOW_AGENT_OUTPUT_SCHEMA_PATH = (
    REPO_ROOT / "research" / "schemas" / "macro_window_agent_output.schema.json"
)


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


def validate_macro_window_agent_outputs(
    macro_window_agent_outputs_dir: Path = DEFAULT_MACRO_WINDOW_AGENT_OUTPUTS_DIR,
    schema_path: Path = MACRO_WINDOW_AGENT_OUTPUT_SCHEMA_PATH,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    """Return validation errors for macro_window_agent_output artifacts, or [] when valid."""

    if not macro_window_agent_outputs_dir.exists():
        return []

    macro_window_agent_output_files = sorted(
        macro_window_agent_outputs_dir.rglob("*.macro_window_agent_output.json")
    )
    if not macro_window_agent_output_files:
        return []

    errors: list[str] = []
    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    known_output_ids: set[str] = set()
    output_id_paths: dict[str, Path] = {}

    for path in macro_window_agent_output_files:
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None:
            continue

        output_id = payload.get("macro_window_agent_output_id")
        if isinstance(output_id, str):
            expected_name = f"{output_id}.macro_window_agent_output.json"
            if path.name != expected_name:
                errors.append(f"{path}: filename must be {expected_name}")
            if output_id in known_output_ids:
                errors.append(
                    f"{path}: duplicate macro_window_agent_output_id {output_id}; "
                    f"first seen at {output_id_paths[output_id]}"
                )
            known_output_ids.add(output_id)
            output_id_paths.setdefault(output_id, path)

        fixture_path_value = payload.get("source_fixture_path")
        fixture_path = _resolve_repo_ref(repo_root, fixture_path_value)
        if fixture_path is None:
            errors.append(f"{path}: invalid repo-relative source_fixture_path: {fixture_path_value}")
            continue
        if not fixture_path.exists():
            errors.append(f"{path}: source_fixture_path does not exist: {fixture_path_value}")
            continue

        expected_sha256 = payload.get("source_fixture_sha256")
        actual_sha256 = _sha256_file(fixture_path)
        if expected_sha256 != actual_sha256:
            errors.append(
                f"{path}: source_fixture_sha256 mismatch for {fixture_path_value}: "
                f"expected {expected_sha256}, got {actual_sha256}"
            )

        try:
            fixture = load_json(fixture_path)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: source fixture invalid JSON: {fixture_path_value}: {exc}")
            continue

        expected_flag = bool(fixture.get("macro_event_window_active"))
        if payload.get("macro_window_flag") != expected_flag:
            errors.append(
                f"{path}: macro_window_flag should be {expected_flag}, "
                f"got {payload.get('macro_window_flag')}"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--macro-window-agent-outputs-dir",
        type=Path,
        default=DEFAULT_MACRO_WINDOW_AGENT_OUTPUTS_DIR,
    )
    parser.add_argument("--schema", type=Path, default=MACRO_WINDOW_AGENT_OUTPUT_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_macro_window_agent_outputs(
        macro_window_agent_outputs_dir=args.macro_window_agent_outputs_dir,
        schema_path=args.schema,
        repo_root=REPO_ROOT,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.macro_window_agent_outputs_dir.exists():
        print(f"OK: {args.macro_window_agent_outputs_dir} does not exist; nothing to validate")
    else:
        print(
            "OK: macro_window_agent_output artifacts under "
            f"{args.macro_window_agent_outputs_dir} validate"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
