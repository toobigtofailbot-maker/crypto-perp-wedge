"""Validate JSON overlay_shadow_log artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OVERLAY_SHADOW_LOGS_DIR = REPO_ROOT / "research" / "overlay_shadow_logs"
DEFAULT_BUCKET_MAPPINGS_DIR = REPO_ROOT / "research" / "bucket_mappings"
DEFAULT_AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "agent_outputs"
DEFAULT_PRE_GATE_ADVISORY_SNAPSHOTS_DIR = REPO_ROOT / "research" / "pre_gate_advisory_snapshots"
OVERLAY_SHADOW_LOG_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "overlay_shadow_log.schema.json"
LOCKED_BUCKET_TO_MULTIPLIER = {"ALLOW": 1.0, "ALLOW_REDUCED": 0.5, "BLOCK": 0.0}


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


def _source_bucket_mapping_path(bucket_mappings_dir: Path, source_bucket_mapping_id: Any) -> Path | None:
    if not isinstance(source_bucket_mapping_id, str) or not source_bucket_mapping_id:
        return None
    return bucket_mappings_dir / f"{source_bucket_mapping_id}.bucket_mapping.json"


def _source_agent_output_path(agent_outputs_dir: Path, source_agent_output_id: Any) -> Path | None:
    if not isinstance(source_agent_output_id, str) or not source_agent_output_id:
        return None
    return agent_outputs_dir / f"{source_agent_output_id}.agent_output.json"


def _source_pre_gate_advisory_snapshot_path(
    pre_gate_advisory_snapshots_dir: Path,
    source_pre_gate_advisory_snapshot_id: Any,
) -> Path | None:
    if (
        not isinstance(source_pre_gate_advisory_snapshot_id, str)
        or not source_pre_gate_advisory_snapshot_id
    ):
        return None
    return (
        pre_gate_advisory_snapshots_dir
        / f"{source_pre_gate_advisory_snapshot_id}.pre_gate_advisory_snapshot.json"
    )


def _expected_comparison(observed_overlay_bucket: Any, mapped_bucket: Any) -> str | None:
    if not isinstance(observed_overlay_bucket, str) or not isinstance(mapped_bucket, str):
        return None
    return "MATCH" if observed_overlay_bucket == mapped_bucket else "MISMATCH"


def _normalized_advisory_source(payload: dict[str, Any]) -> str | None:
    advisory_source = payload.get("advisory_source")
    if advisory_source is None:
        return "BMAP"
    if not isinstance(advisory_source, str):
        return None
    return advisory_source


def _expected_size_multiplier_for_bucket(bucket: Any) -> float | None:
    if not isinstance(bucket, str):
        return None
    return LOCKED_BUCKET_TO_MULTIPLIER.get(bucket)


def validate_overlay_shadow_logs(
    overlay_shadow_logs_dir: Path = DEFAULT_OVERLAY_SHADOW_LOGS_DIR,
    bucket_mappings_dir: Path = DEFAULT_BUCKET_MAPPINGS_DIR,
    agent_outputs_dir: Path = DEFAULT_AGENT_OUTPUTS_DIR,
    pre_gate_advisory_snapshots_dir: Path = DEFAULT_PRE_GATE_ADVISORY_SNAPSHOTS_DIR,
    schema_path: Path = OVERLAY_SHADOW_LOG_SCHEMA_PATH,
) -> list[str]:
    """Return validation errors for overlay_shadow_log artifacts, or an empty list when valid."""

    if not overlay_shadow_logs_dir.exists():
        return []

    shadow_log_files = sorted(overlay_shadow_logs_dir.rglob("*.overlay_shadow_log.json"))
    if not shadow_log_files:
        return []

    errors: list[str] = []
    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    known_shadow_log_ids: set[str] = set()
    shadow_log_id_paths: dict[str, Path] = {}

    for path in shadow_log_files:
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None:
            continue

        shadow_log_id = payload.get("overlay_shadow_log_id")
        if isinstance(shadow_log_id, str):
            expected_name = f"{shadow_log_id}.overlay_shadow_log.json"
            if path.name != expected_name:
                errors.append(f"{path}: filename must be {expected_name}")
            if shadow_log_id in known_shadow_log_ids:
                errors.append(
                    f"{path}: duplicate overlay_shadow_log_id {shadow_log_id}; "
                    f"first seen at {shadow_log_id_paths[shadow_log_id]}"
                )
            known_shadow_log_ids.add(shadow_log_id)
            shadow_log_id_paths.setdefault(shadow_log_id, path)

        if payload.get("override_applied") is not False:
            errors.append(f"{path}: override_applied must be false")
        if payload.get("fail_open_preserved") is not True:
            errors.append(f"{path}: fail_open_preserved must be true")
        if payload.get("advisory_only") is not True:
            errors.append(f"{path}: advisory_only must be true")

        expected_comparison = _expected_comparison(
            payload.get("observed_overlay_bucket"),
            payload.get("mapped_bucket"),
        )
        if expected_comparison is not None and payload.get("comparison_result") != expected_comparison:
            errors.append(
                f"{path}: comparison_result should be {expected_comparison}, "
                f"got {payload.get('comparison_result')}"
            )

        observation_source = payload.get("observation_source")
        if isinstance(observation_source, dict):
            if payload.get("observed_at") != observation_source.get("evaluation_time_utc"):
                errors.append(
                    f"{path}: observed_at must match observation_source.evaluation_time_utc"
                )

        advisory_source = _normalized_advisory_source(payload)
        bucket_mapping_path = _source_bucket_mapping_path(
            bucket_mappings_dir,
            payload.get("source_bucket_mapping_id"),
        )
        if bucket_mapping_path is None:
            errors.append(f"{path}: invalid source_bucket_mapping_id: {payload.get('source_bucket_mapping_id')}")
            continue
        if not bucket_mapping_path.exists():
            errors.append(f"{path}: source bucket mapping file does not exist: {bucket_mapping_path}")
            continue

        try:
            bucket_mapping = load_json(bucket_mapping_path)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: source bucket mapping invalid JSON: {bucket_mapping_path}: {exc}")
            continue

        source_checks = {
            "source_agent_output_id": bucket_mapping.get("source_agent_output_id"),
        }
        if advisory_source != "PGAS":
            source_checks.update(
                {
                    "mapped_bucket": bucket_mapping.get("mapped_bucket"),
                    "size_multiplier": bucket_mapping.get("size_multiplier"),
                }
            )
        for field_name, expected_value in source_checks.items():
            actual_value = payload.get(field_name)
            if actual_value != expected_value:
                errors.append(
                    f"{path}: {field_name} mismatch with source {bucket_mapping_path.name}: "
                    f"expected {expected_value}, got {actual_value}"
                )

        agent_output_path = _source_agent_output_path(agent_outputs_dir, payload.get("source_agent_output_id"))
        if agent_output_path is None:
            errors.append(f"{path}: invalid source_agent_output_id: {payload.get('source_agent_output_id')}")
            continue
        if not agent_output_path.exists():
            errors.append(f"{path}: source agent output file does not exist: {agent_output_path}")
            continue

        try:
            agent_output = load_json(agent_output_path)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: source agent output invalid JSON: {agent_output_path}: {exc}")
            continue

        if payload.get("source_agent_output_id") != agent_output.get("agent_output_id"):
            errors.append(
                f"{path}: source_agent_output_id mismatch with source {agent_output_path.name}: "
                f"expected {agent_output.get('agent_output_id')}, got {payload.get('source_agent_output_id')}"
            )

        if advisory_source == "PGAS":
            pre_gate_path = _source_pre_gate_advisory_snapshot_path(
                pre_gate_advisory_snapshots_dir,
                payload.get("source_pre_gate_advisory_snapshot_id"),
            )
            if pre_gate_path is None:
                errors.append(
                    f"{path}: PGAS advisory_source requires source_pre_gate_advisory_snapshot_id"
                )
                continue
            if not pre_gate_path.exists():
                errors.append(
                    f"{path}: source pre-gate advisory snapshot file does not exist: {pre_gate_path}"
                )
                continue

            try:
                pre_gate_advisory_snapshot = load_json(pre_gate_path)
            except json.JSONDecodeError as exc:
                errors.append(
                    f"{path}: source pre-gate advisory snapshot invalid JSON: {pre_gate_path}: {exc}"
                )
                continue

            pre_gate_source_checks = {
                "source_pre_gate_advisory_snapshot_id": pre_gate_advisory_snapshot.get(
                    "pre_gate_advisory_snapshot_id"
                ),
                "source_bucket_mapping_id": pre_gate_advisory_snapshot.get("source_bucket_mapping_id"),
                "source_agent_output_id": pre_gate_advisory_snapshot.get("source_agent_output_id"),
                "mapped_bucket": pre_gate_advisory_snapshot.get("combined_bucket"),
            }
            for field_name, expected_value in pre_gate_source_checks.items():
                actual_value = payload.get(field_name)
                if actual_value != expected_value:
                    errors.append(
                        f"{path}: {field_name} mismatch with source {pre_gate_path.name}: "
                        f"expected {expected_value}, got {actual_value}"
                    )

            expected_size_multiplier = _expected_size_multiplier_for_bucket(
                pre_gate_advisory_snapshot.get("combined_bucket")
            )
            if expected_size_multiplier is None:
                errors.append(
                    f"{path}: source {pre_gate_path.name} must expose a locked-domain combined_bucket"
                )
            elif payload.get("size_multiplier") != expected_size_multiplier:
                errors.append(
                    f"{path}: size_multiplier mismatch with source {pre_gate_path.name}: "
                    f"expected {expected_size_multiplier}, got {payload.get('size_multiplier')}"
                )
        elif payload.get("source_pre_gate_advisory_snapshot_id") is not None:
            errors.append(
                f"{path}: source_pre_gate_advisory_snapshot_id is only valid for advisory_source=PGAS"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overlay-shadow-logs-dir", type=Path, default=DEFAULT_OVERLAY_SHADOW_LOGS_DIR)
    parser.add_argument("--bucket-mappings-dir", type=Path, default=DEFAULT_BUCKET_MAPPINGS_DIR)
    parser.add_argument("--agent-outputs-dir", type=Path, default=DEFAULT_AGENT_OUTPUTS_DIR)
    parser.add_argument(
        "--pre-gate-advisory-snapshots-dir",
        type=Path,
        default=DEFAULT_PRE_GATE_ADVISORY_SNAPSHOTS_DIR,
    )
    parser.add_argument("--schema", type=Path, default=OVERLAY_SHADOW_LOG_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_overlay_shadow_logs(
        overlay_shadow_logs_dir=args.overlay_shadow_logs_dir,
        bucket_mappings_dir=args.bucket_mappings_dir,
        agent_outputs_dir=args.agent_outputs_dir,
        pre_gate_advisory_snapshots_dir=args.pre_gate_advisory_snapshots_dir,
        schema_path=args.schema,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.overlay_shadow_logs_dir.exists():
        print(f"OK: {args.overlay_shadow_logs_dir} does not exist; nothing to validate")
    else:
        print(f"OK: overlay_shadow_log artifacts under {args.overlay_shadow_logs_dir} validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
