"""Validate JSON pre_gate_advisory_snapshot artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PRE_GATE_ADVISORY_SNAPSHOTS_DIR = REPO_ROOT / "research" / "pre_gate_advisory_snapshots"
DEFAULT_AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "agent_outputs"
DEFAULT_BUCKET_MAPPINGS_DIR = REPO_ROOT / "research" / "bucket_mappings"
DEFAULT_MACRO_WINDOW_AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "macro_window_agent_outputs"
PRE_GATE_ADVISORY_SNAPSHOT_SCHEMA_PATH = (
    REPO_ROOT / "research" / "schemas" / "pre_gate_advisory_snapshot.schema.json"
)
COMBINATION_RULE = "NONE_BUNDLE_ONLY"


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


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _latest_timestamp(*values: str) -> str:
    latest = max((_parse_timestamp(value) for value in values), key=lambda item: item.timestamp())
    return latest.strftime("%Y-%m-%dT%H:%M:%SZ")


def _source_path(directory: Path, artifact_id: Any, suffix: str) -> Path | None:
    if not isinstance(artifact_id, str) or not artifact_id:
        return None
    return directory / f"{artifact_id}{suffix}"


def validate_pre_gate_advisory_snapshots(
    pre_gate_advisory_snapshots_dir: Path = DEFAULT_PRE_GATE_ADVISORY_SNAPSHOTS_DIR,
    agent_outputs_dir: Path = DEFAULT_AGENT_OUTPUTS_DIR,
    bucket_mappings_dir: Path = DEFAULT_BUCKET_MAPPINGS_DIR,
    macro_window_agent_outputs_dir: Path = DEFAULT_MACRO_WINDOW_AGENT_OUTPUTS_DIR,
    schema_path: Path = PRE_GATE_ADVISORY_SNAPSHOT_SCHEMA_PATH,
) -> list[str]:
    """Return validation errors for pre_gate_advisory_snapshot artifacts, or [] when valid."""

    if not pre_gate_advisory_snapshots_dir.exists():
        return []

    snapshot_files = sorted(
        pre_gate_advisory_snapshots_dir.rglob("*.pre_gate_advisory_snapshot.json")
    )
    if not snapshot_files:
        return []

    errors: list[str] = []
    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    known_ids: set[str] = set()
    id_paths: dict[str, Path] = {}

    for path in snapshot_files:
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None:
            continue

        snapshot_id = payload.get("pre_gate_advisory_snapshot_id")
        if isinstance(snapshot_id, str):
            expected_name = f"{snapshot_id}.pre_gate_advisory_snapshot.json"
            if path.name != expected_name:
                errors.append(f"{path}: filename must be {expected_name}")
            if snapshot_id in known_ids:
                errors.append(
                    f"{path}: duplicate pre_gate_advisory_snapshot_id {snapshot_id}; "
                    f"first seen at {id_paths[snapshot_id]}"
                )
            known_ids.add(snapshot_id)
            id_paths.setdefault(snapshot_id, path)

        agent_output_path = _source_path(
            agent_outputs_dir,
            payload.get("source_agent_output_id"),
            ".agent_output.json",
        )
        bucket_mapping_path = _source_path(
            bucket_mappings_dir,
            payload.get("source_bucket_mapping_id"),
            ".bucket_mapping.json",
        )
        macro_window_agent_output_path = _source_path(
            macro_window_agent_outputs_dir,
            payload.get("source_macro_window_agent_output_id"),
            ".macro_window_agent_output.json",
        )

        if agent_output_path is None:
            errors.append(f"{path}: invalid source_agent_output_id: {payload.get('source_agent_output_id')}")
            continue
        if bucket_mapping_path is None:
            errors.append(
                f"{path}: invalid source_bucket_mapping_id: {payload.get('source_bucket_mapping_id')}"
            )
            continue
        if macro_window_agent_output_path is None:
            errors.append(
                f"{path}: invalid source_macro_window_agent_output_id: "
                f"{payload.get('source_macro_window_agent_output_id')}"
            )
            continue

        missing_source = False
        for label, source_path in {
            "agent output": agent_output_path,
            "bucket mapping": bucket_mapping_path,
            "macro-window agent output": macro_window_agent_output_path,
        }.items():
            if not source_path.exists():
                errors.append(f"{path}: source {label} file does not exist: {source_path}")
                missing_source = True
        if missing_source:
            continue

        try:
            agent_output = load_json(agent_output_path)
            bucket_mapping = load_json(bucket_mapping_path)
            macro_window_agent_output = load_json(macro_window_agent_output_path)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: source artifact invalid JSON: {exc}")
            continue

        source_checks = {
            "source_agent_output_id": agent_output.get("agent_output_id"),
            "source_bucket_mapping_id": bucket_mapping.get("bucket_mapping_id"),
            "source_macro_window_agent_output_id": macro_window_agent_output.get("macro_window_agent_output_id"),
            "setup_score": agent_output.get("setup_score"),
            "confidence": agent_output.get("confidence"),
            "mapped_bucket": bucket_mapping.get("mapped_bucket"),
            "size_multiplier": bucket_mapping.get("size_multiplier"),
            "macro_window_flag": macro_window_agent_output.get("macro_window_flag"),
        }
        for field_name, expected_value in source_checks.items():
            actual_value = payload.get(field_name)
            if actual_value != expected_value:
                errors.append(
                    f"{path}: {field_name} mismatch with source artifacts: "
                    f"expected {expected_value}, got {actual_value}"
                )

        if bucket_mapping.get("source_agent_output_id") != payload.get("source_agent_output_id"):
            errors.append(
                f"{path}: source_agent_output_id mismatch with bucket mapping "
                f"{bucket_mapping_path.name}: expected {bucket_mapping.get('source_agent_output_id')}, "
                f"got {payload.get('source_agent_output_id')}"
            )

        expected_generated_at = _latest_timestamp(
            agent_output["generated_at"],
            bucket_mapping["generated_at"],
            macro_window_agent_output["generated_at"],
        )
        if payload.get("generated_at") != expected_generated_at:
            errors.append(
                f"{path}: generated_at should be {expected_generated_at}, "
                f"got {payload.get('generated_at')}"
            )

        expected_as_of_timestamp = _latest_timestamp(
            agent_output["as_of_timestamp"],
            bucket_mapping["as_of_timestamp"],
            macro_window_agent_output["as_of_timestamp"],
        )
        if payload.get("as_of_timestamp") != expected_as_of_timestamp:
            errors.append(
                f"{path}: as_of_timestamp should be {expected_as_of_timestamp}, "
                f"got {payload.get('as_of_timestamp')}"
            )

        if payload.get("combination_rule_applied") != COMBINATION_RULE:
            errors.append(
                f"{path}: combination_rule_applied should be {COMBINATION_RULE}, "
                f"got {payload.get('combination_rule_applied')}"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pre-gate-advisory-snapshots-dir",
        type=Path,
        default=DEFAULT_PRE_GATE_ADVISORY_SNAPSHOTS_DIR,
    )
    parser.add_argument("--agent-outputs-dir", type=Path, default=DEFAULT_AGENT_OUTPUTS_DIR)
    parser.add_argument("--bucket-mappings-dir", type=Path, default=DEFAULT_BUCKET_MAPPINGS_DIR)
    parser.add_argument(
        "--macro-window-agent-outputs-dir",
        type=Path,
        default=DEFAULT_MACRO_WINDOW_AGENT_OUTPUTS_DIR,
    )
    parser.add_argument("--schema", type=Path, default=PRE_GATE_ADVISORY_SNAPSHOT_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_pre_gate_advisory_snapshots(
        pre_gate_advisory_snapshots_dir=args.pre_gate_advisory_snapshots_dir,
        agent_outputs_dir=args.agent_outputs_dir,
        bucket_mappings_dir=args.bucket_mappings_dir,
        macro_window_agent_outputs_dir=args.macro_window_agent_outputs_dir,
        schema_path=args.schema,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.pre_gate_advisory_snapshots_dir.exists():
        print(f"OK: {args.pre_gate_advisory_snapshots_dir} does not exist; nothing to validate")
    else:
        print(
            "OK: pre_gate_advisory_snapshot artifacts under "
            f"{args.pre_gate_advisory_snapshots_dir} validate"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
