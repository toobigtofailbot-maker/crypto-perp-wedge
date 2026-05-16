"""Local batch-run summary validation helper for AUTO-09.

This module validates caller-supplied local summary material only. It does not
call runners, create output, expose query surfaces, or define a formal schema.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence


BATCH_REQUIRED_FIELDS = (
    "batch_id",
    "implementation_id",
    "package_label",
    "item_count",
    "success_item_count",
    "failed_item_count",
    "skipped_item_count",
    "blocked_item_count",
    "failure_reasons",
    "item_results",
    "manifest_files",
    "summary_file",
    "checked_boundaries",
    "local_only",
    "research_only",
    "non_authoritative",
    "creates_committed_evidence",
    "protected_boundary_preserved",
)

ITEM_REQUIRED_FIELDS = (
    "item_id",
    "source_id",
    "status",
    "output_path",
    "dry_run_run_id",
    "dry_run_written_files",
    "failure_reasons",
    "local_only",
    "research_only",
    "non_authoritative",
    "creates_committed_evidence",
    "protected_boundary_preserved",
)

ALLOWED_STATUSES = frozenset(("succeeded", "failed", "blocked", "skipped"))


@dataclass(frozen=True)
class BatchRunSummaryValidationReport:
    passed: bool
    failure_reasons: tuple[str, ...]
    local_only: bool
    research_only: bool
    non_authoritative: bool
    creates_committed_evidence: bool
    protected_boundary_preserved: bool


def _failure_report(failure_reasons: list[str]) -> BatchRunSummaryValidationReport:
    return BatchRunSummaryValidationReport(
        passed=False,
        failure_reasons=tuple(failure_reasons),
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=False,
    )


def _passed_report() -> BatchRunSummaryValidationReport:
    return BatchRunSummaryValidationReport(
        passed=True,
        failure_reasons=(),
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=True,
    )


def _is_local_relative_reference(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    if "\\" in value or (len(value) >= 2 and value[1] == ":"):
        return False
    path = PurePosixPath(value)
    if path.is_absolute():
        return False
    return ".." not in path.parts


def _validate_marker(
    payload: Mapping[str, Any],
    field_name: str,
    expected: bool,
    label: str,
    failures: list[str],
) -> None:
    if payload.get(field_name) is not expected:
        failures.append(f"{label}.{field_name} must be {expected}")


def _validate_markers(payload: Mapping[str, Any], label: str, failures: list[str]) -> None:
    _validate_marker(payload, "local_only", True, label, failures)
    _validate_marker(payload, "research_only", True, label, failures)
    _validate_marker(payload, "non_authoritative", True, label, failures)
    _validate_marker(payload, "creates_committed_evidence", False, label, failures)


def _validate_required_fields(
    payload: Mapping[str, Any],
    required_fields: tuple[str, ...],
    label: str,
    failures: list[str],
) -> None:
    for field_name in required_fields:
        if field_name not in payload:
            failures.append(f"{label} missing required field: {field_name}")


def _validate_path_reference(value: Any, label: str, failures: list[str]) -> None:
    if not _is_local_relative_reference(value):
        failures.append(f"{label} must be a non-empty local relative path without traversal")


def _validate_path_mapping(value: Any, label: str, failures: list[str]) -> None:
    if not isinstance(value, Mapping):
        failures.append(f"{label} must be a mapping")
        return
    for key, path_value in value.items():
        if not isinstance(key, str) or not key.strip():
            failures.append(f"{label} keys must be non-empty strings")
        _validate_path_reference(path_value, f"{label}.{key}", failures)


def _status_counts(item_results: list[Mapping[str, Any]]) -> dict[str, int]:
    return {
        status: sum(item.get("status") == status for item in item_results)
        for status in ALLOWED_STATUSES
    }


def _validate_counts(summary: Mapping[str, Any], item_results: list[Mapping[str, Any]], failures: list[str]) -> None:
    expected_counts = {
        "item_count": len(item_results),
        "success_item_count": _status_counts(item_results)["succeeded"],
        "failed_item_count": _status_counts(item_results)["failed"],
        "blocked_item_count": _status_counts(item_results)["blocked"],
        "skipped_item_count": _status_counts(item_results)["skipped"],
    }
    for field_name, expected in expected_counts.items():
        if summary.get(field_name) != expected:
            failures.append(f"{field_name} must be {expected}")


def validate_local_batch_run_summary(summary: Mapping[str, Any]) -> BatchRunSummaryValidationReport:
    """Validate one local WP-12h-style batch-run summary mapping."""

    failures: list[str] = []
    if not isinstance(summary, Mapping):
        return _failure_report(["summary must be a mapping"])

    _validate_required_fields(summary, BATCH_REQUIRED_FIELDS, "summary", failures)
    if failures:
        return _failure_report(failures)

    _validate_markers(summary, "summary", failures)
    _validate_path_reference(summary.get("summary_file"), "summary.summary_file", failures)
    _validate_path_mapping(summary.get("manifest_files"), "summary.manifest_files", failures)

    item_results_value = summary.get("item_results")
    if not isinstance(item_results_value, Sequence) or isinstance(item_results_value, (str, bytes)):
        failures.append("summary.item_results must be a sequence")
        item_results: list[Mapping[str, Any]] = []
    else:
        item_results = []
        for index, item in enumerate(item_results_value):
            label = f"summary.item_results[{index}]"
            if not isinstance(item, Mapping):
                failures.append(f"{label} must be a mapping")
                continue
            item_results.append(item)
            _validate_required_fields(item, ITEM_REQUIRED_FIELDS, label, failures)
            if any(field_name not in item for field_name in ITEM_REQUIRED_FIELDS):
                continue
            status = item.get("status")
            if status not in ALLOWED_STATUSES:
                failures.append(f"{label}.status must be one of {sorted(ALLOWED_STATUSES)}")
            _validate_markers(item, label, failures)
            _validate_path_reference(item.get("output_path"), f"{label}.output_path", failures)
            _validate_path_mapping(item.get("dry_run_written_files"), f"{label}.dry_run_written_files", failures)

    _validate_counts(summary, item_results, failures)

    if failures:
        return _failure_report(failures)
    return _passed_report()


def validate_local_batch_run_summary_file(path: str | Path) -> BatchRunSummaryValidationReport:
    """Read one JSON file and validate it as local batch-run summary material."""

    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        return _failure_report([f"summary file could not be read: {exc}"])
    except json.JSONDecodeError as exc:
        return _failure_report([f"summary file contains invalid JSON: {exc.msg}"])

    if not isinstance(payload, Mapping):
        return _failure_report(["summary file JSON must be an object"])
    return validate_local_batch_run_summary(payload)
