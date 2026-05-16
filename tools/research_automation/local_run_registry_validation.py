"""Local run registry validation helper for AUTO-13.

This module validates caller-supplied WP-12m local registry material only. It
does not call registry builders, runners, create output, expose query surfaces,
or define a formal schema.
"""

from __future__ import annotations

import json
import string
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from tools.research_automation.local_run_registry import IMPLEMENTATION_ID, PACKAGE_LABEL


TOP_LEVEL_REQUIRED_FIELDS = (
    "implementation_id",
    "package_label",
    "record_count",
    "records",
    "failure_reasons",
    "local_only",
    "research_only",
    "non_authoritative",
    "creates_committed_evidence",
    "protected_boundary_preserved",
    "checked_boundaries",
)

RECORD_REQUIRED_FIELDS = (
    "registry_record_id",
    "source_kind",
    "package_label",
    "implementation_id",
    "output_root",
    "relative_paths",
    "run_id",
    "batch_id",
    "candidate_id",
    "evaluation_purpose",
    "validation_passed",
    "failure_reasons",
    "local_only",
    "research_only",
    "non_authoritative",
    "creates_committed_evidence",
    "protected_boundary_preserved",
    "source_file_hashes",
    "notes",
)

ALLOWED_SOURCE_KINDS = frozenset(("local_dry_run", "local_batch_run"))
HEX_DIGITS = frozenset(string.hexdigits)


@dataclass(frozen=True)
class LocalRunRegistryValidationReport:
    passed: bool
    failure_reasons: tuple[str, ...]
    record_count: int
    local_only: bool
    research_only: bool
    non_authoritative: bool
    creates_committed_evidence: bool
    protected_boundary_preserved: bool


def _report(
    passed: bool,
    failure_reasons: list[str],
    record_count: int,
    protected_boundary_preserved: bool,
) -> LocalRunRegistryValidationReport:
    return LocalRunRegistryValidationReport(
        passed=passed,
        failure_reasons=tuple(failure_reasons),
        record_count=record_count,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=protected_boundary_preserved if passed else False,
    )


def _failure_report(failure_reasons: list[str], record_count: int = 0) -> LocalRunRegistryValidationReport:
    return _report(False, failure_reasons, record_count, False)


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


def _is_local_relative_reference(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    if "\\" in value or (len(value) >= 2 and value[1] == ":"):
        return False
    path = PurePosixPath(value)
    if path.is_absolute():
        return False
    return ".." not in path.parts


def _is_sha256_hex(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in HEX_DIGITS for char in value)


def _validate_required_fields(
    payload: Mapping[str, Any],
    required_fields: tuple[str, ...],
    label: str,
    failures: list[str],
) -> None:
    for field_name in required_fields:
        if field_name not in payload:
            failures.append(f"{label} missing required field: {field_name}")


def _validate_marker(
    payload: Mapping[str, Any],
    field_name: str,
    expected: bool,
    label: str,
    failures: list[str],
) -> None:
    if payload.get(field_name) is not expected:
        failures.append(f"{label}.{field_name} must be {expected}")


def _validate_boundary_markers(payload: Mapping[str, Any], label: str, failures: list[str]) -> None:
    _validate_marker(payload, "local_only", True, label, failures)
    _validate_marker(payload, "research_only", True, label, failures)
    _validate_marker(payload, "non_authoritative", True, label, failures)
    _validate_marker(payload, "creates_committed_evidence", False, label, failures)


def _validate_sequence(value: Any, label: str, failures: list[str], *, non_empty: bool = False) -> bool:
    if not _is_sequence(value):
        failures.append(f"{label} must be a sequence")
        return False
    if non_empty and len(value) == 0:
        failures.append(f"{label} must be a non-empty sequence")
        return False
    return True


def _validate_relative_paths(value: Any, label: str, failures: list[str]) -> set[str]:
    if not isinstance(value, Mapping):
        failures.append(f"{label} must be a non-empty mapping")
        return set()
    if not value:
        failures.append(f"{label} must be a non-empty mapping")
        return set()

    keys: set[str] = set()
    for key, path_value in value.items():
        if not isinstance(key, str) or not key.strip():
            failures.append(f"{label} keys must be non-empty strings")
            continue
        keys.add(key)
        if not _is_local_relative_reference(path_value):
            failures.append(f"{label}.{key} must be a non-empty local relative path without traversal")
    return keys


def _validate_source_file_hashes(value: Any, expected_keys: set[str], label: str, failures: list[str]) -> None:
    if not isinstance(value, Mapping):
        failures.append(f"{label} must be a non-empty mapping")
        return
    if not value:
        failures.append(f"{label} must be a non-empty mapping")
        return

    hash_keys: set[str] = set()
    for key, hash_value in value.items():
        if not isinstance(key, str) or not key.strip():
            failures.append(f"{label} keys must be non-empty strings")
            continue
        hash_keys.add(key)
        if not _is_sha256_hex(hash_value):
            failures.append(f"{label}.{key} must be a 64-character hex SHA-256 string")

    if hash_keys != expected_keys:
        failures.append(f"{label} keys must match relative_paths keys exactly")


def _validate_record(record: Mapping[str, Any], index: int, failures: list[str]) -> bool:
    label = f"records[{index}]"
    _validate_required_fields(record, RECORD_REQUIRED_FIELDS, label, failures)
    if any(field_name not in record for field_name in RECORD_REQUIRED_FIELDS):
        return False

    registry_record_id = record.get("registry_record_id")
    if not isinstance(registry_record_id, str) or not registry_record_id.startswith("LRR-"):
        failures.append(f"{label}.registry_record_id must be a non-empty string beginning with LRR-")

    source_kind = record.get("source_kind")
    if source_kind not in ALLOWED_SOURCE_KINDS:
        failures.append(f"{label}.source_kind must be one of {sorted(ALLOWED_SOURCE_KINDS)}")

    if record.get("package_label") != PACKAGE_LABEL:
        failures.append(f"{label}.package_label must equal {PACKAGE_LABEL}")
    if record.get("implementation_id") != IMPLEMENTATION_ID:
        failures.append(f"{label}.implementation_id must equal {IMPLEMENTATION_ID}")

    output_root = record.get("output_root")
    if not isinstance(output_root, str) or not output_root.strip():
        failures.append(f"{label}.output_root must be a non-empty string")

    relative_path_keys = _validate_relative_paths(record.get("relative_paths"), f"{label}.relative_paths", failures)
    _validate_source_file_hashes(
        record.get("source_file_hashes"),
        relative_path_keys,
        f"{label}.source_file_hashes",
        failures,
    )

    validation_passed = record.get("validation_passed")
    if not isinstance(validation_passed, bool):
        failures.append(f"{label}.validation_passed must be a bool")

    protected_boundary_preserved = record.get("protected_boundary_preserved")
    if not isinstance(protected_boundary_preserved, bool):
        failures.append(f"{label}.protected_boundary_preserved must be a bool")

    _validate_sequence(record.get("failure_reasons"), f"{label}.failure_reasons", failures)
    _validate_sequence(record.get("notes"), f"{label}.notes", failures)
    _validate_boundary_markers(record, label, failures)

    run_id = record.get("run_id")
    batch_id = record.get("batch_id")
    if source_kind == "local_dry_run":
        if not isinstance(run_id, str) or not run_id.strip():
            failures.append(f"{label}.run_id must be non-empty for local_dry_run")
        if batch_id != "":
            failures.append(f"{label}.batch_id must be empty for local_dry_run")
        if validation_passed is False and protected_boundary_preserved is not False:
            failures.append(f"{label}.protected_boundary_preserved must be False for failed local_dry_run")
        if validation_passed is True and protected_boundary_preserved is not True:
            failures.append(f"{label}.protected_boundary_preserved must be True for passed local_dry_run")
    elif source_kind == "local_batch_run":
        if not isinstance(batch_id, str) or not batch_id.strip():
            failures.append(f"{label}.batch_id must be non-empty for local_batch_run")
        if run_id != "":
            failures.append(f"{label}.run_id must be empty for local_batch_run")
        if validation_passed is not True:
            failures.append(f"{label}.validation_passed must be True for local_batch_run")

    return isinstance(protected_boundary_preserved, bool) and protected_boundary_preserved


def validate_local_run_registry(registry: Mapping[str, Any]) -> LocalRunRegistryValidationReport:
    """Validate one caller-provided WP-12m local registry mapping."""

    if not isinstance(registry, Mapping):
        return _failure_report(["registry must be a mapping"])

    failures: list[str] = []
    _validate_required_fields(registry, TOP_LEVEL_REQUIRED_FIELDS, "registry", failures)
    if failures:
        return _failure_report(failures)

    if registry.get("implementation_id") != IMPLEMENTATION_ID:
        failures.append(f"registry.implementation_id must equal {IMPLEMENTATION_ID}")
    if registry.get("package_label") != PACKAGE_LABEL:
        failures.append(f"registry.package_label must equal {PACKAGE_LABEL}")

    _validate_boundary_markers(registry, "registry", failures)

    record_count_value = registry.get("record_count")
    if not isinstance(record_count_value, int):
        failures.append("registry.record_count must be an int")
        record_count = 0
    else:
        record_count = record_count_value

    records_value = registry.get("records")
    records: list[Mapping[str, Any]] = []
    if not _validate_sequence(records_value, "registry.records", failures):
        records = []
    else:
        for index, record in enumerate(records_value):
            if not isinstance(record, Mapping):
                failures.append(f"records[{index}] must be a mapping")
                continue
            records.append(record)

    if isinstance(record_count_value, int) and record_count_value != len(records):
        failures.append("registry.record_count must equal len(records)")

    _validate_sequence(registry.get("failure_reasons"), "registry.failure_reasons", failures)
    _validate_sequence(registry.get("checked_boundaries"), "registry.checked_boundaries", failures, non_empty=True)

    top_level_protected = registry.get("protected_boundary_preserved")
    if not isinstance(top_level_protected, bool):
        failures.append("registry.protected_boundary_preserved must be a bool")

    record_boundary_values = [
        _validate_record(record, index, failures)
        for index, record in enumerate(records)
    ]
    if records and isinstance(top_level_protected, bool):
        expected_boundary = all(record_boundary_values)
        if top_level_protected is not expected_boundary:
            failures.append("registry.protected_boundary_preserved must equal all record protected_boundary_preserved values")

    if failures:
        return _failure_report(failures, record_count=record_count)
    return _report(True, [], record_count, bool(top_level_protected))


def validate_local_run_registry_file(path: str | Path) -> LocalRunRegistryValidationReport:
    """Read one JSON file and validate it as WP-12m local registry material."""

    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        return _failure_report([f"registry file could not be read: {exc}"])
    except json.JSONDecodeError as exc:
        return _failure_report([f"registry file contains invalid JSON: {exc.msg}"])

    if not isinstance(payload, Mapping):
        return _failure_report(["registry file JSON must be an object"])
    return validate_local_run_registry(payload)
