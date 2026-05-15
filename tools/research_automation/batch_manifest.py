"""Local in-process batch manifest helper for AUTO-05.

This module builds and validates local research-only batch manifest material.
It does not execute batch items and does not contact the local dry-run runner.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


IMPLEMENTATION_ID = "wp_12f_auto_05_batch_manifest_v1"
PACKAGE_LABEL = "WP-12f / AUTO-05"
OUTPUT_FILE_NAMES = {
    "batch_manifest": "batch_manifest.json",
    "batch_validation_report": "batch_validation_report.json",
}


@dataclass(frozen=True)
class BatchManifestItem:
    """Explicit local research batch item supplied by the caller or test."""

    source_id: str
    candidate_id: str
    evaluation_purpose: str
    data_refs: tuple[str, ...]
    timeframe: str
    evaluation_window: Mapping[str, str]
    parameters: Mapping[str, Any]
    pipeline_version: str
    output_path: str
    item_id: str = ""
    local_only: bool = True
    research_only: bool = True
    non_authoritative: bool = True
    execution_occurred: bool = False
    creates_committed_evidence: bool = False


@dataclass(frozen=True)
class BatchResourceLimits:
    """Caller-provided local resource categories for manifest validation."""

    max_item_count: int
    max_local_jobs: int = 1
    max_concurrency: int = 1
    failure_threshold: int = 0


@dataclass(frozen=True)
class BatchManifest:
    batch_id: str
    implementation_id: str
    package_label: str
    item_count: int
    items: tuple[BatchManifestItem, ...]
    resource_limits: BatchResourceLimits
    static_metadata: Mapping[str, str]
    output_files: Mapping[str, str]
    local_only: bool
    research_only: bool
    non_authoritative: bool
    execution_occurred: bool
    creates_committed_evidence: bool
    protected_boundary_preserved: bool


@dataclass(frozen=True)
class BatchValidationReport:
    validation_report_id: str
    batch_id: str
    passed: bool
    failure_reasons: tuple[str, ...]
    checked_boundaries: tuple[str, ...]
    item_failure_count: int
    resource_limit_failure_count: int
    output_location_failure_count: int
    local_only: bool
    research_only: bool
    non_authoritative: bool
    execution_occurred: bool
    creates_committed_evidence: bool


@dataclass(frozen=True)
class BatchManifestBuildResult:
    manifest: BatchManifest | None
    validation_report: BatchValidationReport
    written_files: Mapping[str, Path]


def _stable_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _stable_digest(payload: Any) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _as_path(value: str | Path) -> Path:
    return value if isinstance(value, Path) else Path(value)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _normalize_output_path(output_root: Path, output_path: str) -> str | None:
    if not isinstance(output_path, str) or not output_path.strip():
        return None
    candidate = Path(output_path)
    resolved = candidate if candidate.is_absolute() else output_root / candidate
    if not _is_relative_to(resolved, output_root):
        return None
    return resolved.resolve().relative_to(output_root.resolve()).as_posix()


def _validate_resource_limits(resource_limits: BatchResourceLimits, item_count: int) -> tuple[str, ...]:
    failures: list[str] = []
    integer_fields = {
        "max_item_count": resource_limits.max_item_count,
        "max_local_jobs": resource_limits.max_local_jobs,
        "max_concurrency": resource_limits.max_concurrency,
        "failure_threshold": resource_limits.failure_threshold,
    }
    for field_name, value in integer_fields.items():
        if not isinstance(value, int):
            failures.append(f"resource_limits.{field_name} must be an integer")

    if isinstance(resource_limits.max_item_count, int) and resource_limits.max_item_count < 1:
        failures.append("resource_limits.max_item_count must be at least 1")
    if isinstance(resource_limits.max_local_jobs, int) and resource_limits.max_local_jobs < 1:
        failures.append("resource_limits.max_local_jobs must be at least 1")
    if isinstance(resource_limits.max_concurrency, int) and resource_limits.max_concurrency < 1:
        failures.append("resource_limits.max_concurrency must be at least 1")
    if isinstance(resource_limits.failure_threshold, int) and resource_limits.failure_threshold < 0:
        failures.append("resource_limits.failure_threshold must be non-negative")

    if (
        isinstance(resource_limits.max_item_count, int)
        and resource_limits.max_item_count >= 1
        and item_count > resource_limits.max_item_count
    ):
        failures.append("item count exceeds resource_limits.max_item_count")

    return tuple(failures)


def _validate_item(item: BatchManifestItem, index: int, output_root: Path) -> tuple[tuple[str, ...], BatchManifestItem | None]:
    failures: list[str] = []
    required_strings = {
        "source_id": item.source_id,
        "candidate_id": item.candidate_id,
        "evaluation_purpose": item.evaluation_purpose,
        "timeframe": item.timeframe,
        "pipeline_version": item.pipeline_version,
    }
    for field_name, value in required_strings.items():
        if not isinstance(value, str) or not value.strip():
            failures.append(f"items[{index}].{field_name} must be a non-empty string")

    if not item.data_refs or any(not isinstance(data_ref, str) or not data_ref.strip() for data_ref in item.data_refs):
        failures.append(f"items[{index}].data_refs must contain at least one non-empty local reference")

    if not isinstance(item.evaluation_window, Mapping):
        failures.append(f"items[{index}].evaluation_window must be a mapping")
    else:
        window_start = item.evaluation_window.get("start")
        window_end = item.evaluation_window.get("end")
        if not isinstance(window_start, str) or not window_start.strip():
            failures.append(f"items[{index}].evaluation_window.start must be a non-empty string")
        if not isinstance(window_end, str) or not window_end.strip():
            failures.append(f"items[{index}].evaluation_window.end must be a non-empty string")

    if not isinstance(item.parameters, Mapping):
        failures.append(f"items[{index}].parameters must be a mapping")

    normalized_output_path = _normalize_output_path(output_root, item.output_path)
    if normalized_output_path is None:
        failures.append(f"items[{index}].output_path must be contained under output_root")

    if failures:
        return tuple(failures), None

    identity_payload = {
        "source_id": item.source_id,
        "candidate_id": item.candidate_id,
        "evaluation_purpose": item.evaluation_purpose,
        "data_refs": tuple(item.data_refs),
        "timeframe": item.timeframe,
        "evaluation_window": dict(item.evaluation_window),
        "parameters": dict(item.parameters),
        "pipeline_version": item.pipeline_version,
        "output_path": normalized_output_path,
        "implementation_id": IMPLEMENTATION_ID,
    }
    item_id = f"BMI-{_stable_digest(identity_payload)[:12].upper()}"
    return (), BatchManifestItem(
        source_id=item.source_id,
        candidate_id=item.candidate_id,
        evaluation_purpose=item.evaluation_purpose,
        data_refs=tuple(item.data_refs),
        timeframe=item.timeframe,
        evaluation_window=dict(item.evaluation_window),
        parameters=dict(item.parameters),
        pipeline_version=item.pipeline_version,
        output_path=normalized_output_path,
        item_id=item_id,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        execution_occurred=False,
        creates_committed_evidence=False,
    )


def _build_manifest(
    items: tuple[BatchManifestItem, ...],
    resource_limits: BatchResourceLimits,
    static_metadata: Mapping[str, str],
) -> BatchManifest:
    identity_payload = {
        "implementation_id": IMPLEMENTATION_ID,
        "package_label": PACKAGE_LABEL,
        "item_ids": tuple(item.item_id for item in items),
        "items": tuple(asdict(item) for item in items),
        "resource_limits": asdict(resource_limits),
        "static_metadata": dict(static_metadata),
    }
    batch_id = f"BM-{_stable_digest(identity_payload)[:12].upper()}"
    return BatchManifest(
        batch_id=batch_id,
        implementation_id=IMPLEMENTATION_ID,
        package_label=PACKAGE_LABEL,
        item_count=len(items),
        items=items,
        resource_limits=resource_limits,
        static_metadata=dict(static_metadata),
        output_files=dict(OUTPUT_FILE_NAMES),
        local_only=True,
        research_only=True,
        non_authoritative=True,
        execution_occurred=False,
        creates_committed_evidence=False,
        protected_boundary_preserved=True,
    )


def _build_validation_report(
    batch_id: str,
    failures: tuple[str, ...],
    item_failure_count: int,
    resource_limit_failure_count: int,
    output_location_failure_count: int,
) -> BatchValidationReport:
    report_payload = {
        "batch_id": batch_id,
        "failures": failures,
        "implementation_id": IMPLEMENTATION_ID,
    }
    return BatchValidationReport(
        validation_report_id=f"BMV-{_stable_digest(report_payload)[:12].upper()}",
        batch_id=batch_id,
        passed=not failures,
        failure_reasons=failures,
        checked_boundaries=(
            "local_only",
            "research_only",
            "non_authoritative",
            "no_execution_occurred",
            "no_committed_evidence_artifact",
            "output_root_must_exist",
            "output_paths_contained_under_output_root",
            "resource_limits_checked",
            "no_runtime_paper_live_oms_risk_safe_mode_contact",
            "no_exchange_broker_order_scheduler_daemon_queue_contact",
            "no_config_dependency_schema_validator_query_layer_contact",
        ),
        item_failure_count=item_failure_count,
        resource_limit_failure_count=resource_limit_failure_count,
        output_location_failure_count=output_location_failure_count,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        execution_occurred=False,
        creates_committed_evidence=False,
    )


def build_batch_manifest(
    items: Iterable[BatchManifestItem],
    output_root: str | Path,
    resource_limits: BatchResourceLimits,
    static_metadata: Mapping[str, str] | None = None,
) -> BatchManifestBuildResult:
    """Build and validate one local research-only batch manifest.

    The helper writes only when validation passes, and then only under
    ``output_root``.
    """

    output_root_path = _as_path(output_root)
    metadata: Mapping[str, str] = {}
    failures: list[str] = []
    item_failures = 0
    resource_limit_failures = 0
    output_location_failures = 0

    if not output_root_path.exists() or not output_root_path.is_dir():
        failures.append("output_root must be an existing directory")
        validation_report = _build_validation_report(
            "BM-INVALID",
            tuple(failures),
            item_failure_count=0,
            resource_limit_failure_count=0,
            output_location_failure_count=1,
        )
        return BatchManifestBuildResult(manifest=None, validation_report=validation_report, written_files={})

    item_tuple = tuple(items)
    if not item_tuple:
        failures.append("items must contain at least one batch item")
        item_failures += 1

    if not isinstance(resource_limits, BatchResourceLimits):
        failures.append("resource_limits must be a BatchResourceLimits instance")
        resource_limit_failures += 1
    else:
        resource_failures = _validate_resource_limits(resource_limits, len(item_tuple))
        failures.extend(resource_failures)
        resource_limit_failures += len(resource_failures)

    if static_metadata is None:
        metadata = {}
    elif isinstance(static_metadata, Mapping):
        metadata = dict(static_metadata)
    else:
        failures.append("static_metadata must be a mapping")

    manifest_items: list[BatchManifestItem] = []
    for index, item in enumerate(item_tuple):
        if not isinstance(item, BatchManifestItem):
            failures.append(f"items[{index}] must be a BatchManifestItem instance")
            item_failures += 1
            continue
        item_failure_reasons, manifest_item = _validate_item(item, index, output_root_path)
        failures.extend(item_failure_reasons)
        if item_failure_reasons:
            item_failures += len(item_failure_reasons)
            output_location_failures += sum("output_path" in reason for reason in item_failure_reasons)
        if manifest_item is not None:
            manifest_items.append(manifest_item)

    if failures:
        validation_report = _build_validation_report(
            "BM-INVALID",
            tuple(failures),
            item_failure_count=item_failures,
            resource_limit_failure_count=resource_limit_failures,
            output_location_failure_count=output_location_failures,
        )
        return BatchManifestBuildResult(manifest=None, validation_report=validation_report, written_files={})

    manifest = _build_manifest(tuple(manifest_items), resource_limits, metadata)
    validation_report = _build_validation_report(
        manifest.batch_id,
        (),
        item_failure_count=0,
        resource_limit_failure_count=0,
        output_location_failure_count=0,
    )
    written_files = {
        "batch_manifest": output_root_path / OUTPUT_FILE_NAMES["batch_manifest"],
        "batch_validation_report": output_root_path / OUTPUT_FILE_NAMES["batch_validation_report"],
    }
    _write_json(written_files["batch_manifest"], asdict(manifest))
    _write_json(written_files["batch_validation_report"], asdict(validation_report))

    return BatchManifestBuildResult(
        manifest=manifest,
        validation_report=validation_report,
        written_files=written_files,
    )
