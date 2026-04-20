"""Validate JSON bucket_mapping artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUCKET_MAPPINGS_DIR = REPO_ROOT / "research" / "bucket_mappings"
DEFAULT_AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "agent_outputs"
BUCKET_MAPPING_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "bucket_mapping.schema.json"
CONFIDENCE_FLOOR = 0.60
VALID_BUCKET_MULTIPLIERS = {
    "ALLOW": 1.0,
    "ALLOW_REDUCED": 0.5,
    "BLOCK": 0.0,
}


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


def _source_agent_output_path(agent_outputs_dir: Path, source_agent_output_id: Any) -> Path | None:
    if not isinstance(source_agent_output_id, str) or not source_agent_output_id:
        return None
    return agent_outputs_dir / f"{source_agent_output_id}.agent_output.json"


def _expected_mapping(setup_score: float, confidence: float) -> tuple[str, float, bool]:
    if confidence < CONFIDENCE_FLOOR:
        return "BLOCK", 0.0, True
    if setup_score >= 80.0:
        return "ALLOW", 1.0, False
    if setup_score >= 60.0:
        return "ALLOW_REDUCED", 0.5, False
    return "BLOCK", 0.0, False


def validate_bucket_mappings(
    bucket_mappings_dir: Path = DEFAULT_BUCKET_MAPPINGS_DIR,
    agent_outputs_dir: Path = DEFAULT_AGENT_OUTPUTS_DIR,
    schema_path: Path = BUCKET_MAPPING_SCHEMA_PATH,
) -> list[str]:
    """Return validation errors for bucket_mapping artifacts, or an empty list when valid."""

    if not bucket_mappings_dir.exists():
        return []

    bucket_mapping_files = sorted(bucket_mappings_dir.rglob("*.bucket_mapping.json"))
    if not bucket_mapping_files:
        return []

    errors: list[str] = []
    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    known_bucket_mapping_ids: set[str] = set()
    bucket_mapping_id_paths: dict[str, Path] = {}

    for path in bucket_mapping_files:
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None:
            continue

        bucket_mapping_id = payload.get("bucket_mapping_id")
        if isinstance(bucket_mapping_id, str):
            expected_name = f"{bucket_mapping_id}.bucket_mapping.json"
            if path.name != expected_name:
                errors.append(f"{path}: filename must be {expected_name}")
            if bucket_mapping_id in known_bucket_mapping_ids:
                errors.append(
                    f"{path}: duplicate bucket_mapping_id {bucket_mapping_id}; "
                    f"first seen at {bucket_mapping_id_paths[bucket_mapping_id]}"
                )
            known_bucket_mapping_ids.add(bucket_mapping_id)
            bucket_mapping_id_paths.setdefault(bucket_mapping_id, path)

        mapped_bucket = payload.get("mapped_bucket")
        size_multiplier = payload.get("size_multiplier")
        if mapped_bucket in VALID_BUCKET_MULTIPLIERS:
            expected_multiplier = VALID_BUCKET_MULTIPLIERS[mapped_bucket]
            if size_multiplier != expected_multiplier:
                errors.append(
                    f"{path}: mapped_bucket {mapped_bucket} requires size_multiplier "
                    f"{expected_multiplier}, got {size_multiplier}"
                )

        source_path = _source_agent_output_path(agent_outputs_dir, payload.get("source_agent_output_id"))
        if source_path is None:
            errors.append(f"{path}: invalid source_agent_output_id: {payload.get('source_agent_output_id')}")
            continue
        if not source_path.exists():
            errors.append(f"{path}: source agent output file does not exist: {source_path}")
            continue

        try:
            source_payload = load_json(source_path)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: source agent output invalid JSON: {source_path}: {exc}")
            continue

        source_checks = {
            "source_agent_output_id": source_payload.get("agent_output_id"),
            "agent_type": source_payload.get("agent_type"),
            "generated_at": source_payload.get("generated_at"),
            "as_of_timestamp": source_payload.get("as_of_timestamp"),
            "source_setup_score": source_payload.get("setup_score"),
            "source_confidence": source_payload.get("confidence"),
        }
        for field_name, expected_value in source_checks.items():
            actual_value = payload.get(field_name)
            if actual_value != expected_value:
                errors.append(
                    f"{path}: {field_name} mismatch with source {source_path.name}: "
                    f"expected {expected_value}, got {actual_value}"
                )

        source_setup_score = payload.get("source_setup_score")
        source_confidence = payload.get("source_confidence")
        if isinstance(source_setup_score, (int, float)) and isinstance(source_confidence, (int, float)):
            expected_bucket, expected_multiplier, expected_floor_triggered = _expected_mapping(
                setup_score=float(source_setup_score),
                confidence=float(source_confidence),
            )
            if mapped_bucket != expected_bucket:
                errors.append(f"{path}: mapped_bucket should be {expected_bucket}, got {mapped_bucket}")
            if size_multiplier != expected_multiplier:
                errors.append(
                    f"{path}: size_multiplier should be {expected_multiplier}, got {size_multiplier}"
                )
            if payload.get("confidence_floor_triggered") != expected_floor_triggered:
                errors.append(
                    f"{path}: confidence_floor_triggered should be {expected_floor_triggered}, "
                    f"got {payload.get('confidence_floor_triggered')}"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bucket-mappings-dir", type=Path, default=DEFAULT_BUCKET_MAPPINGS_DIR)
    parser.add_argument("--agent-outputs-dir", type=Path, default=DEFAULT_AGENT_OUTPUTS_DIR)
    parser.add_argument("--schema", type=Path, default=BUCKET_MAPPING_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_bucket_mappings(
        bucket_mappings_dir=args.bucket_mappings_dir,
        agent_outputs_dir=args.agent_outputs_dir,
        schema_path=args.schema,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.bucket_mappings_dir.exists():
        print(f"OK: {args.bucket_mappings_dir} does not exist; nothing to validate")
    else:
        print(f"OK: bucket_mapping artifacts under {args.bucket_mappings_dir} validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
