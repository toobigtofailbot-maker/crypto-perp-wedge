"""Local in-process batch runner vertical slice for AUTO-07.

This module consumes explicit caller-provided batch items, validates them
through the WP-12f manifest helper, and calls the WP-12d local dry-run runner
only through a direct local function call.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from tools.research_automation.batch_manifest import (
    BatchManifestItem,
    BatchResourceLimits,
    build_batch_manifest,
)
from tools.research_automation.local_dry_run_runner import (
    ResearchIntentFixture,
    run_local_dry_run,
)


IMPLEMENTATION_ID = "wp_12h_auto_07_local_batch_runner_v1"
PACKAGE_LABEL = "WP-12h / AUTO-07"
SUMMARY_FILE_NAME = "local_batch_run_summary.json"
CHECKED_BOUNDARIES = (
    "local_only",
    "research_only",
    "non_authoritative",
    "no_committed_evidence_artifact",
    "no_runtime_paper_live_oms_risk_safe_mode_contact",
    "no_exchange_broker_order_scheduler_daemon_queue_watcher_trigger_contact",
    "no_config_dependency_schema_validator_query_layer_contact",
)


@dataclass(frozen=True)
class LocalBatchItemResult:
    item_id: str
    source_id: str
    status: str
    output_path: str
    dry_run_run_id: str
    dry_run_written_files: Mapping[str, str]
    failure_reasons: tuple[str, ...]
    local_only: bool
    research_only: bool
    non_authoritative: bool
    creates_committed_evidence: bool
    protected_boundary_preserved: bool


@dataclass(frozen=True)
class LocalBatchRunSummary:
    batch_id: str
    implementation_id: str
    package_label: str
    item_count: int
    success_item_count: int
    failed_item_count: int
    skipped_item_count: int
    blocked_item_count: int
    failure_reasons: tuple[str, ...]
    item_results: tuple[LocalBatchItemResult, ...]
    manifest_files: Mapping[str, str]
    summary_file: str
    checked_boundaries: tuple[str, ...]
    local_only: bool
    research_only: bool
    non_authoritative: bool
    creates_committed_evidence: bool
    protected_boundary_preserved: bool


@dataclass(frozen=True)
class LocalBatchRunResult:
    manifest_result: Any
    summary: LocalBatchRunSummary
    written_files: Mapping[str, str]
    local_only: bool
    research_only: bool
    non_authoritative: bool
    creates_committed_evidence: bool
    protected_boundary_preserved: bool


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _as_path(value: str | Path) -> Path:
    return value if isinstance(value, Path) else Path(value)


def _relative_to_output_root(path: Path, output_root: Path) -> str:
    return path.resolve().relative_to(output_root.resolve()).as_posix()


def _manifest_written_files(manifest_written_files: Mapping[str, Path], output_root: Path) -> dict[str, str]:
    return {
        key: _relative_to_output_root(path, output_root)
        for key, path in sorted(manifest_written_files.items())
    }


def _failure_summary(
    manifest_result: Any,
    failure_reasons: tuple[str, ...],
) -> LocalBatchRunSummary:
    return LocalBatchRunSummary(
        batch_id="LB-INVALID",
        implementation_id=IMPLEMENTATION_ID,
        package_label=PACKAGE_LABEL,
        item_count=0,
        success_item_count=0,
        failed_item_count=0,
        skipped_item_count=0,
        blocked_item_count=0,
        failure_reasons=failure_reasons,
        item_results=(),
        manifest_files={},
        summary_file="",
        checked_boundaries=CHECKED_BOUNDARIES,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=False,
    )


def _intent_from_item(item: BatchManifestItem) -> ResearchIntentFixture:
    return ResearchIntentFixture(
        intent_id=item.source_id,
        candidate_id=item.candidate_id,
        evaluation_purpose=item.evaluation_purpose,
        data_refs=tuple(item.data_refs),
        timeframe=item.timeframe,
        evaluation_window=dict(item.evaluation_window),
        parameters=dict(item.parameters),
        pipeline_version=item.pipeline_version,
        static_metadata={
            "batch_item_id": item.item_id,
            "batch_source_id": item.source_id,
            "batch_output_path": item.output_path,
        },
    )


def _dry_run_written_files(dry_run_result: Any, output_root: Path) -> dict[str, str]:
    return {
        key: _relative_to_output_root(path, output_root)
        for key, path in sorted(dry_run_result.written_files.items())
    }


def _item_result_from_dry_run(
    item: BatchManifestItem,
    output_root: Path,
    dry_run_result: Any,
) -> LocalBatchItemResult:
    failure_reasons = tuple(dry_run_result.validation_report.failure_reasons)
    passed = bool(dry_run_result.validation_report.passed)
    run_id = ""
    if dry_run_result.run_request is not None:
        run_id = dry_run_result.run_request.run_id
    return LocalBatchItemResult(
        item_id=item.item_id,
        source_id=item.source_id,
        status="succeeded" if passed else "failed",
        output_path=item.output_path,
        dry_run_run_id=run_id,
        dry_run_written_files=_dry_run_written_files(dry_run_result, output_root),
        failure_reasons=failure_reasons,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=passed,
    )


def run_local_batch(
    items: Iterable[BatchManifestItem],
    output_root: str | Path,
    resource_limits: BatchResourceLimits,
    static_metadata: Mapping[str, str] | None = None,
) -> LocalBatchRunResult:
    """Run one deterministic local batch from explicit caller-provided items."""

    output_root_path = _as_path(output_root)
    manifest_result = build_batch_manifest(
        items,
        output_root_path,
        resource_limits,
        static_metadata=static_metadata,
    )

    if manifest_result.manifest is None or not manifest_result.validation_report.passed:
        failure_summary = _failure_summary(
            manifest_result,
            tuple(manifest_result.validation_report.failure_reasons),
        )
        return LocalBatchRunResult(
            manifest_result=manifest_result,
            summary=failure_summary,
            written_files={},
            local_only=True,
            research_only=True,
            non_authoritative=True,
            creates_committed_evidence=False,
            protected_boundary_preserved=False,
        )

    item_results: list[LocalBatchItemResult] = []
    failure_reasons: list[str] = []
    for item in manifest_result.manifest.items:
        item_output_dir = output_root_path / item.output_path
        item_output_dir.mkdir(parents=True, exist_ok=True)
        dry_run_result = run_local_dry_run(_intent_from_item(item), item_output_dir)
        item_result = _item_result_from_dry_run(item, output_root_path, dry_run_result)
        item_results.append(item_result)
        failure_reasons.extend(
            f"{item.item_id}: {reason}" for reason in item_result.failure_reasons
        )

    success_count = sum(item.status == "succeeded" for item in item_results)
    failed_count = sum(item.status == "failed" for item in item_results)
    summary = LocalBatchRunSummary(
        batch_id=manifest_result.manifest.batch_id,
        implementation_id=IMPLEMENTATION_ID,
        package_label=PACKAGE_LABEL,
        item_count=manifest_result.manifest.item_count,
        success_item_count=success_count,
        failed_item_count=failed_count,
        skipped_item_count=0,
        blocked_item_count=0,
        failure_reasons=tuple(failure_reasons),
        item_results=tuple(item_results),
        manifest_files=_manifest_written_files(manifest_result.written_files, output_root_path),
        summary_file=SUMMARY_FILE_NAME,
        checked_boundaries=CHECKED_BOUNDARIES,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=failed_count == 0,
    )

    summary_path = output_root_path / SUMMARY_FILE_NAME
    _write_json(summary_path, asdict(summary))
    written_files = dict(summary.manifest_files)
    written_files["local_batch_run_summary"] = SUMMARY_FILE_NAME

    return LocalBatchRunResult(
        manifest_result=manifest_result,
        summary=summary,
        written_files=written_files,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=summary.protected_boundary_preserved,
    )
