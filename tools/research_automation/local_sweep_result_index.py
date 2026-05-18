"""Local structural sweep result index sidecar for WP-12w / AUTO-22.

This module indexes an already-completed local parameter sweep result. It does
not execute sweeps, build registries, expose query surfaces, or create
authoritative evidence.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping


IMPLEMENTATION_ID = "wp_12w_auto_22_local_sweep_result_index_v1"
PACKAGE_LABEL = "WP-12w / AUTO-22"
RESULT_INDEX_FILE_NAME = "local_sweep_result_index.json"
INDEX_VERSION = "wp12w-local-sweep-result-index-v1"
INDEX_KIND = "local_sweep_result_index"
CHECKED_BOUNDARIES = (
    "local_only",
    "research_only",
    "non_authoritative",
    "no_committed_evidence_artifact",
    "structural_index_only",
    "actual_registry_record_ids_only",
    "no_fabricated_per_point_registry_ids",
    "no_query_layer_exposure",
    "no_tools_registry_validator",
    "no_evidence_bridge",
    "no_runtime_or_downstream_authority",
    "no_ranking_scoring_recommendation_authority",
)


@dataclass(frozen=True)
class LocalSweepPointIndexRef:
    point_id: str
    point_index: int
    output_path: str
    batch_item_id: str
    dry_run_run_id: str
    status: str


@dataclass(frozen=True)
class LocalSweepResultIndex:
    index_version: str
    index_kind: str
    implementation_id: str
    package_label: str
    sweep_id: str
    spec_source: str
    loader_source: str
    sweep_summary_file: str
    batch_output_root: str
    batch_summary_file: str
    batch_summary_validation_file: str
    registry_file: str
    registry_record_ids: tuple[str, ...]
    point_count: int
    point_refs: tuple[LocalSweepPointIndexRef, ...]
    checked_boundaries: tuple[str, ...]
    local_only: bool
    research_only: bool
    non_authoritative: bool
    creates_committed_evidence: bool
    protected_boundary_preserved: bool


@dataclass(frozen=True)
class LocalSweepResultIndexWriteResult:
    index: LocalSweepResultIndex | None
    index_file: Path | None
    written_files: Mapping[str, Path]
    failure_reasons: tuple[str, ...]
    local_only: bool
    research_only: bool
    non_authoritative: bool
    creates_committed_evidence: bool
    protected_boundary_preserved: bool


def _as_path(value: str | Path) -> Path:
    return value if isinstance(value, Path) else Path(value)


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _failure_result(failure_reasons: tuple[str, ...]) -> LocalSweepResultIndexWriteResult:
    return LocalSweepResultIndexWriteResult(
        index=None,
        index_file=None,
        written_files={},
        failure_reasons=failure_reasons,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=False,
    )


def _is_sequence(value: Any) -> bool:
    return isinstance(value, (tuple, list)) and not isinstance(value, (str, bytes, bytearray))


def _boundary_failures(sweep_result: Any) -> tuple[str, ...]:
    failures: list[str] = []
    expected = {
        "protected_boundary_preserved": True,
        "local_only": True,
        "research_only": True,
        "non_authoritative": True,
        "creates_committed_evidence": False,
    }
    for field_name, expected_value in expected.items():
        if getattr(sweep_result, field_name, None) is not expected_value:
            failures.append(f"sweep_result.{field_name} must be {expected_value}")
    return tuple(failures)


def _summary_failures(summary: Any) -> tuple[str, ...]:
    failures: list[str] = []
    if summary is None:
        return ("sweep_result.summary is required",)
    if not isinstance(getattr(summary, "sweep_id", None), str) or not getattr(summary, "sweep_id", "").strip():
        failures.append("sweep_result.summary.sweep_id must be a non-empty string")
    if not _is_sequence(getattr(summary, "point_results", None)):
        failures.append("sweep_result.summary.point_results must be a sequence")
    if not _is_sequence(getattr(summary, "registry_record_ids", None)):
        failures.append("sweep_result.summary.registry_record_ids must be a sequence")
    return tuple(failures)


def _point_index(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _point_ref(point_result: Any) -> LocalSweepPointIndexRef:
    return LocalSweepPointIndexRef(
        point_id=str(getattr(point_result, "point_id", "")),
        point_index=_point_index(getattr(point_result, "point_index", 0)),
        output_path=str(getattr(point_result, "output_path", "")),
        batch_item_id=str(getattr(point_result, "batch_item_id", "")),
        dry_run_run_id=str(getattr(point_result, "dry_run_run_id", "")),
        status=str(getattr(point_result, "status", "")),
    )


def _build_index(
    sweep_result: Any,
    output_root: Path,
    *,
    spec_source: str,
    loader_source: str,
) -> LocalSweepResultIndex:
    summary = getattr(sweep_result, "summary")
    registry_record_ids = tuple(str(record_id) for record_id in getattr(summary, "registry_record_ids", ()))
    point_refs = tuple(_point_ref(point_result) for point_result in getattr(summary, "point_results", ()))
    return LocalSweepResultIndex(
        index_version=INDEX_VERSION,
        index_kind=INDEX_KIND,
        implementation_id=IMPLEMENTATION_ID,
        package_label=PACKAGE_LABEL,
        sweep_id=str(getattr(summary, "sweep_id")),
        spec_source=str(spec_source),
        loader_source=str(loader_source),
        sweep_summary_file=str(getattr(sweep_result, "summary_file")),
        batch_output_root=str(output_root),
        batch_summary_file=str(getattr(summary, "batch_summary_file", "")),
        batch_summary_validation_file=str(getattr(summary, "batch_summary_validation_file", "")),
        registry_file=str(getattr(summary, "registry_file", "")),
        registry_record_ids=registry_record_ids,
        point_count=int(getattr(summary, "point_count", len(point_refs))),
        point_refs=point_refs,
        checked_boundaries=CHECKED_BOUNDARIES,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=True,
    )


def write_local_sweep_result_index(
    sweep_result: Any,
    output_root: str | Path,
    *,
    spec_source: str = "",
    loader_source: str = "",
) -> LocalSweepResultIndexWriteResult:
    """Write one local structural result-index sidecar for a completed sweep."""

    output_root_path = _as_path(output_root)
    if not output_root_path.exists() or not output_root_path.is_dir():
        return _failure_result(("output_root must be an existing directory",))

    boundary_failures = _boundary_failures(sweep_result)
    if boundary_failures:
        return _failure_result(boundary_failures)

    summary = getattr(sweep_result, "summary", None)
    summary_failures = _summary_failures(summary)
    if summary_failures:
        return _failure_result(summary_failures)

    summary_file = getattr(sweep_result, "summary_file", None)
    if summary_file is None:
        return _failure_result(("sweep_result.summary_file is required",))
    summary_file_path = _as_path(summary_file)
    if not summary_file_path.exists() or not summary_file_path.is_file():
        return _failure_result(("sweep_result.summary_file must exist",))

    index = _build_index(
        sweep_result,
        output_root_path,
        spec_source=spec_source,
        loader_source=loader_source,
    )
    index_file = output_root_path / RESULT_INDEX_FILE_NAME
    _write_json(index_file, asdict(index))
    return LocalSweepResultIndexWriteResult(
        index=index,
        index_file=index_file,
        written_files={"local_sweep_result_index": index_file},
        failure_reasons=(),
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=True,
    )
