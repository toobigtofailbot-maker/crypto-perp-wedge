"""Validate Scope 6 packaging artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


DEFAULT_R2S_APPROVAL_RECORDS_DIR = REPO_ROOT / "research" / "r2s_approval_records"
DEFAULT_SHADOW_EVIDENCE_RETENTION_DIR = REPO_ROOT / "research" / "shadow_evidence_retention"
DEFAULT_S2P_APPROVAL_RECORDS_DIR = REPO_ROOT / "research" / "s2p_approval_records"
R2S_APPROVAL_RECORD_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "r2s_approval_record.schema.json"
SHADOW_EVIDENCE_RETENTION_SCHEMA_PATH = (
    REPO_ROOT / "research" / "schemas" / "shadow_evidence_retention.schema.json"
)
S2P_APPROVAL_RECORD_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "s2p_approval_record.schema.json"


@dataclass(frozen=True)
class ArtifactFamily:
    label: str
    directory: Path
    schema_path: Path
    glob_pattern: str
    id_field: str
    filename_suffix: str


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _format_schema_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    if location:
        return f"{location}: {error.message}"
    return error.message


def _validate_json_file(
    path: Path,
    validator: Draft7Validator,
) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        return None, [f"{path}: invalid JSON: {exc}"]

    errors = [
        f"{path}: {_format_schema_error(schema_error)}"
        for schema_error in sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
    ]
    return payload, errors


def _matching_files(directory: Path, pattern: str) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(directory.rglob(pattern))


def _validate_family_files(
    family: ArtifactFamily,
    validator: Draft7Validator,
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    errors: list[str] = []
    payloads_by_id: dict[str, dict[str, Any]] = {}
    first_path_by_id: dict[str, Path] = {}

    for path in _matching_files(family.directory, family.glob_pattern):
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None:
            continue

        artifact_id = payload.get(family.id_field)
        if isinstance(artifact_id, str):
            expected_name = f"{artifact_id}{family.filename_suffix}"
            if path.name != expected_name:
                errors.append(f"{path}: filename must be {expected_name}")
            if artifact_id in first_path_by_id:
                errors.append(
                    f"{path}: duplicate {family.id_field} {artifact_id}; "
                    f"first seen at {first_path_by_id[artifact_id]}"
                )
            first_path_by_id.setdefault(artifact_id, path)
            payloads_by_id.setdefault(artifact_id, payload)
        else:
            errors.append(f"{path}: missing valid {family.id_field}")

    return errors, payloads_by_id


def _validate_r2s_candidate_consistency(
    r2s_dir: Path,
    r2s_validator: Draft7Validator,
) -> list[str]:
    errors: list[str] = []
    for path in _matching_files(r2s_dir, "*.r2s_approval_record.json"):
        payload, _ = _validate_json_file(path, r2s_validator)
        if payload is None:
            continue
        top_level_candidate_id = payload.get("candidate_id")
        rec5_evidence = payload.get("rec5_exact_segment_evidence")
        nested_candidate_id = rec5_evidence.get("candidate_id") if isinstance(rec5_evidence, dict) else None
        if (
            isinstance(top_level_candidate_id, str)
            and isinstance(nested_candidate_id, str)
            and nested_candidate_id != top_level_candidate_id
        ):
            errors.append(
                f"{path}: rec5_exact_segment_evidence.candidate_id must match "
                f"candidate_id {top_level_candidate_id}"
            )
    return errors


def _validate_s2p_shadow_evidence_consistency(
    s2p_dir: Path,
    s2p_validator: Draft7Validator,
    shadow_evidence_by_id: dict[str, dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    for path in _matching_files(s2p_dir, "*.s2p_approval_record.json"):
        payload, _ = _validate_json_file(path, s2p_validator)
        if payload is None:
            continue
        reference = payload.get("shadow_window_evidence_reference")
        if not isinstance(reference, dict):
            continue
        shadow_evidence_id = reference.get("shadow_evidence_id")
        if not isinstance(shadow_evidence_id, str):
            continue

        referenced_payload = shadow_evidence_by_id.get(shadow_evidence_id)
        if referenced_payload is None:
            continue

        s2p_candidate_id = payload.get("candidate_id")
        shadow_candidate_id = referenced_payload.get("candidate_id")
        if (
            isinstance(s2p_candidate_id, str)
            and isinstance(shadow_candidate_id, str)
            and shadow_candidate_id != s2p_candidate_id
        ):
            errors.append(
                f"{path}: shadow_window_evidence_reference {shadow_evidence_id} candidate_id "
                f"{shadow_candidate_id} does not match S2P candidate_id {s2p_candidate_id}"
            )
    return errors


def _load_schema_validator(schema_path: Path) -> Draft7Validator:
    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema)


def validate_scope6_packaging(
    *,
    r2s_approval_records_dir: Path = DEFAULT_R2S_APPROVAL_RECORDS_DIR,
    shadow_evidence_retention_dir: Path = DEFAULT_SHADOW_EVIDENCE_RETENTION_DIR,
    s2p_approval_records_dir: Path = DEFAULT_S2P_APPROVAL_RECORDS_DIR,
    r2s_approval_record_schema: Path = R2S_APPROVAL_RECORD_SCHEMA_PATH,
    shadow_evidence_retention_schema: Path = SHADOW_EVIDENCE_RETENTION_SCHEMA_PATH,
    s2p_approval_record_schema: Path = S2P_APPROVAL_RECORD_SCHEMA_PATH,
) -> list[str]:
    """Return validation errors for Scope 6 artifacts, or [] when valid."""

    r2s_validator = _load_schema_validator(r2s_approval_record_schema)
    shadow_evidence_validator = _load_schema_validator(shadow_evidence_retention_schema)
    s2p_validator = _load_schema_validator(s2p_approval_record_schema)

    r2s_family = ArtifactFamily(
        label="R2S approval records",
        directory=r2s_approval_records_dir,
        schema_path=r2s_approval_record_schema,
        glob_pattern="*.r2s_approval_record.json",
        id_field="approval_record_id",
        filename_suffix=".r2s_approval_record.json",
    )
    shadow_evidence_family = ArtifactFamily(
        label="shadow-evidence retention records",
        directory=shadow_evidence_retention_dir,
        schema_path=shadow_evidence_retention_schema,
        glob_pattern="*.shadow_evidence_retention.json",
        id_field="shadow_evidence_id",
        filename_suffix=".shadow_evidence_retention.json",
    )
    s2p_family = ArtifactFamily(
        label="S2P approval records",
        directory=s2p_approval_records_dir,
        schema_path=s2p_approval_record_schema,
        glob_pattern="*.s2p_approval_record.json",
        id_field="approval_record_id",
        filename_suffix=".s2p_approval_record.json",
    )

    errors: list[str] = []
    family_results: dict[str, dict[str, dict[str, Any]]] = {}
    for family, validator in (
        (r2s_family, r2s_validator),
        (shadow_evidence_family, shadow_evidence_validator),
        (s2p_family, s2p_validator),
    ):
        family_errors, payloads_by_id = _validate_family_files(family, validator)
        errors.extend(family_errors)
        family_results[family.label] = payloads_by_id

    errors.extend(_validate_r2s_candidate_consistency(r2s_approval_records_dir, r2s_validator))
    errors.extend(
        _validate_s2p_shadow_evidence_consistency(
            s2p_approval_records_dir,
            s2p_validator,
            family_results[shadow_evidence_family.label],
        )
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r2s-approval-records-dir", type=Path, default=DEFAULT_R2S_APPROVAL_RECORDS_DIR)
    parser.add_argument(
        "--shadow-evidence-retention-dir",
        type=Path,
        default=DEFAULT_SHADOW_EVIDENCE_RETENTION_DIR,
    )
    parser.add_argument("--s2p-approval-records-dir", type=Path, default=DEFAULT_S2P_APPROVAL_RECORDS_DIR)
    parser.add_argument("--r2s-approval-record-schema", type=Path, default=R2S_APPROVAL_RECORD_SCHEMA_PATH)
    parser.add_argument(
        "--shadow-evidence-retention-schema",
        type=Path,
        default=SHADOW_EVIDENCE_RETENTION_SCHEMA_PATH,
    )
    parser.add_argument("--s2p-approval-record-schema", type=Path, default=S2P_APPROVAL_RECORD_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_scope6_packaging(
        r2s_approval_records_dir=args.r2s_approval_records_dir,
        shadow_evidence_retention_dir=args.shadow_evidence_retention_dir,
        s2p_approval_records_dir=args.s2p_approval_records_dir,
        r2s_approval_record_schema=args.r2s_approval_record_schema,
        shadow_evidence_retention_schema=args.shadow_evidence_retention_schema,
        s2p_approval_record_schema=args.s2p_approval_record_schema,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("OK: Scope 6 packaging artifacts validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
