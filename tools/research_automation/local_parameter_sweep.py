"""Local parameter sweep vertical slice for WP-12q / AUTO-16.

This module expands one explicit in-memory sweep spec into local batch-run
compatible work and writes one structural sweep summary only after batch and
registry success.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping

from tools.research_automation.batch_manifest import BatchManifestItem, BatchResourceLimits
from tools.research_automation.local_batch_runner import run_local_batch
from tools.research_automation.local_run_registry import build_local_run_registry


IMPLEMENTATION_ID = "wp_12q_auto_16_local_parameter_sweep_v1"
PACKAGE_LABEL = "WP-12q / AUTO-16"
SWEEP_SUMMARY_FILE_NAME = "local_parameter_sweep_summary.json"
DEFAULT_MAX_POINT_COUNT = 5
CHECKED_BOUNDARIES = (
    "local_only",
    "research_only",
    "non_authoritative",
    "no_committed_evidence_artifact",
    "human_initiated",
    "finite_deterministic_sweep",
    "static_batch_compatible_fan_out",
    "structural_aggregation_only",
    "no_optimizer_ranking_scoring_recommendation_authority",
    "no_evidence_bridge",
    "no_runtime_paper_live_oms_risk_safe_mode_contact",
    "no_exchange_broker_order_scheduler_daemon_queue_watcher_trigger_contact",
    "no_config_dependency_schema_validator_query_layer_contact",
)


@dataclass(frozen=True)
class ParameterSweepSpec:
    sweep_id: str
    candidate_id: str
    evaluation_purpose: str
    data_refs: tuple[str, ...]
    timeframe: str
    evaluation_window: Mapping[str, str]
    base_parameters: Mapping[str, Any]
    sweep_parameters: Mapping[str, tuple[Any, ...]]
    pipeline_version: str
    static_metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ParameterSweepPoint:
    point_id: str
    point_index: int
    parameter_values: Mapping[str, Any]
    combined_parameters: Mapping[str, Any]
    output_path: str
    local_only: bool
    research_only: bool
    non_authoritative: bool
    creates_committed_evidence: bool


@dataclass(frozen=True)
class ParameterSweepPointResult:
    point_id: str
    point_index: int
    parameter_values: Mapping[str, Any]
    batch_item_id: str
    status: str
    output_path: str
    dry_run_run_id: str
    failure_reasons: tuple[str, ...]
    local_only: bool
    research_only: bool
    non_authoritative: bool
    creates_committed_evidence: bool


@dataclass(frozen=True)
class LocalParameterSweepSummary:
    sweep_id: str
    implementation_id: str
    package_label: str
    point_count: int
    success_point_count: int
    failed_point_count: int
    blocked_point_count: int
    skipped_point_count: int
    failure_reasons: tuple[str, ...]
    point_results: tuple[ParameterSweepPointResult, ...]
    batch_id: str
    batch_summary_file: str
    batch_summary_validation_file: str
    registry_file: str
    registry_record_ids: tuple[str, ...]
    summary_file: str
    checked_boundaries: tuple[str, ...]
    local_only: bool
    research_only: bool
    non_authoritative: bool
    creates_committed_evidence: bool
    protected_boundary_preserved: bool


@dataclass(frozen=True)
class LocalParameterSweepResult:
    points: tuple[ParameterSweepPoint, ...]
    batch_result: Any
    registry_result: Any
    summary: LocalParameterSweepSummary | None
    summary_file: Path | None
    written_files: Mapping[str, Path]
    failure_reasons: tuple[str, ...]
    local_only: bool
    research_only: bool
    non_authoritative: bool
    creates_committed_evidence: bool
    protected_boundary_preserved: bool


def _stable_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _stable_digest(payload: Any) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _as_path(value: str | Path) -> Path:
    return value if isinstance(value, Path) else Path(value)


def _failure_result(
    failure_reasons: tuple[str, ...],
    *,
    points: tuple[ParameterSweepPoint, ...] = (),
    batch_result: Any = None,
    registry_result: Any = None,
) -> LocalParameterSweepResult:
    return LocalParameterSweepResult(
        points=points,
        batch_result=batch_result,
        registry_result=registry_result,
        summary=None,
        summary_file=None,
        written_files={},
        failure_reasons=failure_reasons,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=False,
    )


def _is_valid_name(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        return False
    if value in {".", ".."}:
        return False
    if "/" in value or "\\" in value:
        return False
    return True


def _validate_string_mapping(value: Any, label: str, failures: list[str]) -> None:
    if not isinstance(value, Mapping):
        failures.append(f"{label} must be a mapping")
        return
    for key, item in value.items():
        if not _is_valid_name(key):
            failures.append(f"{label} keys must be non-empty unambiguous strings")
        if not isinstance(item, str) or not item.strip():
            failures.append(f"{label}.{key} must be a non-empty string")


def _json_serializable(value: Any) -> bool:
    try:
        _stable_json(value)
    except (TypeError, ValueError):
        return False
    return True


def _validate_spec(spec: ParameterSweepSpec) -> tuple[str, ...]:
    failures: list[str] = []
    if not isinstance(spec, ParameterSweepSpec):
        return ("spec must be a ParameterSweepSpec",)

    required_strings = {
        "sweep_id": spec.sweep_id,
        "candidate_id": spec.candidate_id,
        "evaluation_purpose": spec.evaluation_purpose,
        "timeframe": spec.timeframe,
        "pipeline_version": spec.pipeline_version,
    }
    for field_name, value in required_strings.items():
        if not isinstance(value, str) or not value.strip():
            failures.append(f"{field_name} must be a non-empty string")

    if not spec.data_refs or any(not isinstance(item, str) or not item.strip() for item in spec.data_refs):
        failures.append("data_refs must contain at least one non-empty local reference")

    _validate_string_mapping(spec.evaluation_window, "evaluation_window", failures)
    _validate_string_mapping(spec.static_metadata, "static_metadata", failures)

    if not isinstance(spec.base_parameters, Mapping):
        failures.append("base_parameters must be a mapping")
        base_names: set[str] = set()
    else:
        base_names = set(spec.base_parameters)
        for name, value in spec.base_parameters.items():
            if not _is_valid_name(name):
                failures.append("base_parameters keys must be non-empty unambiguous strings")
            if not _json_serializable(value):
                failures.append(f"base_parameters.{name} must be JSON-serializable")

    if not isinstance(spec.sweep_parameters, Mapping):
        failures.append("sweep_parameters must be a mapping")
        return tuple(failures)
    if not spec.sweep_parameters:
        failures.append("sweep_parameters must contain at least one axis")

    seen_axis_names: set[str] = set()
    for name, values in spec.sweep_parameters.items():
        if not _is_valid_name(name):
            failures.append("sweep_parameters keys must be non-empty unambiguous strings")
        if name in seen_axis_names:
            failures.append(f"sweep_parameters.{name} is duplicated")
        seen_axis_names.add(str(name))
        if name in base_names:
            failures.append(f"sweep_parameters.{name} overlaps base_parameters")
        if not isinstance(values, tuple):
            failures.append(f"sweep_parameters.{name} must be a tuple")
            continue
        if not values:
            failures.append(f"sweep_parameters.{name} must contain at least one value")
            continue
        serialized_values: set[str] = set()
        for value in values:
            if not _json_serializable(value):
                failures.append(f"sweep_parameters.{name} values must be JSON-serializable")
                continue
            serialized = _stable_json(value)
            if serialized in serialized_values:
                failures.append(f"sweep_parameters.{name} contains duplicate values")
            serialized_values.add(serialized)

    return tuple(failures)


def _validate_roots(output_root: Path, registry_output_root: Path) -> tuple[str, ...]:
    failures: list[str] = []
    if not output_root.exists() or not output_root.is_dir():
        failures.append("output_root must be an existing directory")
    if not registry_output_root.exists() or not registry_output_root.is_dir():
        failures.append("registry_output_root must be an existing directory")
    return tuple(failures)


def _validate_max_point_count(max_point_count: int) -> tuple[str, ...]:
    if not isinstance(max_point_count, int) or max_point_count < 1:
        return ("max_point_count must be a positive integer",)
    return ()


def _point_id(
    spec: ParameterSweepSpec,
    point_index: int,
    parameter_values: Mapping[str, Any],
    combined_parameters: Mapping[str, Any],
) -> str:
    payload = {
        "implementation_id": IMPLEMENTATION_ID,
        "package_label": PACKAGE_LABEL,
        "sweep_id": spec.sweep_id,
        "point_index": point_index,
        "parameter_values": dict(parameter_values),
        "combined_parameters": dict(combined_parameters),
    }
    return f"LPSP-{_stable_digest(payload)[:16].upper()}"


def _enumerate_points(
    spec: ParameterSweepSpec,
    max_point_count: int,
) -> tuple[tuple[ParameterSweepPoint, ...], tuple[str, ...]]:
    axis_names = tuple(sorted(spec.sweep_parameters))
    axis_values = tuple(tuple(spec.sweep_parameters[name]) for name in axis_names)
    point_count = 1
    for values in axis_values:
        point_count *= len(values)
    if point_count == 0:
        return (), ("sweep grid must contain at least one point",)
    if point_count > max_point_count:
        return (), ("sweep point count exceeds max_point_count",)

    points: list[ParameterSweepPoint] = []
    seen_combinations: set[str] = set()
    for point_index, values in enumerate(itertools.product(*axis_values), start=1):
        parameter_values = dict(zip(axis_names, values))
        combined_parameters = dict(spec.base_parameters)
        combined_parameters.update(parameter_values)
        serialized_combination = _stable_json(parameter_values)
        if serialized_combination in seen_combinations:
            return (), ("sweep grid contains duplicate parameter combinations",)
        seen_combinations.add(serialized_combination)
        points.append(
            ParameterSweepPoint(
                point_id=_point_id(spec, point_index, parameter_values, combined_parameters),
                point_index=point_index,
                parameter_values=parameter_values,
                combined_parameters=combined_parameters,
                output_path=f"sweep-point-{point_index:04d}",
                local_only=True,
                research_only=True,
                non_authoritative=True,
                creates_committed_evidence=False,
            )
        )
    return tuple(points), ()


def _batch_items(spec: ParameterSweepSpec, points: tuple[ParameterSweepPoint, ...]) -> tuple[BatchManifestItem, ...]:
    return tuple(
        BatchManifestItem(
            source_id=point.point_id,
            candidate_id=spec.candidate_id,
            evaluation_purpose=spec.evaluation_purpose,
            data_refs=tuple(spec.data_refs),
            timeframe=spec.timeframe,
            evaluation_window=dict(spec.evaluation_window),
            parameters=dict(point.combined_parameters),
            pipeline_version=spec.pipeline_version,
            output_path=point.output_path,
            local_only=True,
            research_only=True,
            non_authoritative=True,
            execution_occurred=False,
            creates_committed_evidence=False,
        )
        for point in points
    )


def _point_results(
    points: tuple[ParameterSweepPoint, ...],
    batch_result: Any,
) -> tuple[ParameterSweepPointResult, ...]:
    batch_item_results = {
        getattr(item_result, "source_id", ""): item_result
        for item_result in getattr(getattr(batch_result, "summary", None), "item_results", ())
    }
    results: list[ParameterSweepPointResult] = []
    for point in points:
        item_result = batch_item_results.get(point.point_id)
        results.append(
            ParameterSweepPointResult(
                point_id=point.point_id,
                point_index=point.point_index,
                parameter_values=dict(point.parameter_values),
                batch_item_id=str(getattr(item_result, "item_id", "")) if item_result is not None else "",
                status=str(getattr(item_result, "status", "skipped")) if item_result is not None else "skipped",
                output_path=str(getattr(item_result, "output_path", point.output_path)) if item_result is not None else point.output_path,
                dry_run_run_id=str(getattr(item_result, "dry_run_run_id", "")) if item_result is not None else "",
                failure_reasons=tuple(getattr(item_result, "failure_reasons", ())) if item_result is not None else (),
                local_only=True,
                research_only=True,
                non_authoritative=True,
                creates_committed_evidence=False,
            )
        )
    return tuple(results)


def _written_path(value: Any) -> Path | None:
    return value if isinstance(value, Path) else None


def _build_summary(
    spec: ParameterSweepSpec,
    points: tuple[ParameterSweepPoint, ...],
    batch_result: Any,
    registry_result: Any,
) -> LocalParameterSweepSummary:
    point_results = _point_results(points, batch_result)
    failure_reasons: list[str] = []
    for point_result in point_results:
        failure_reasons.extend(
            f"{point_result.point_id}: {reason}" for reason in point_result.failure_reasons
        )
    failure_reasons.extend(str(reason) for reason in getattr(batch_result, "failure_reasons", ()))
    failure_reasons.extend(str(reason) for reason in getattr(registry_result, "failure_reasons", ()))
    batch_written_files = getattr(batch_result, "written_files", {})
    registry_file = getattr(registry_result, "registry_file", None)
    return LocalParameterSweepSummary(
        sweep_id=spec.sweep_id,
        implementation_id=IMPLEMENTATION_ID,
        package_label=PACKAGE_LABEL,
        point_count=len(points),
        success_point_count=sum(point_result.status == "succeeded" for point_result in point_results),
        failed_point_count=sum(point_result.status == "failed" for point_result in point_results),
        blocked_point_count=sum(point_result.status == "blocked" for point_result in point_results),
        skipped_point_count=sum(point_result.status == "skipped" for point_result in point_results),
        failure_reasons=tuple(failure_reasons),
        point_results=point_results,
        batch_id=str(getattr(getattr(batch_result, "summary", None), "batch_id", "")),
        batch_summary_file=str(batch_written_files.get("local_batch_run_summary", "")),
        batch_summary_validation_file=str(batch_written_files.get("local_batch_run_summary_validation", "")),
        registry_file=str(registry_file) if registry_file is not None else "",
        registry_record_ids=tuple(record.registry_record_id for record in getattr(registry_result, "records", ())),
        summary_file=SWEEP_SUMMARY_FILE_NAME,
        checked_boundaries=CHECKED_BOUNDARIES,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=True,
    )


def _batch_succeeded(batch_result: Any) -> bool:
    summary = getattr(batch_result, "summary", None)
    return (
        bool(getattr(batch_result, "protected_boundary_preserved", False))
        and summary is not None
        and bool(getattr(summary, "protected_boundary_preserved", False))
        and getattr(batch_result, "summary_validation_report", None) is not None
        and bool(getattr(getattr(batch_result, "summary_validation_report", None), "passed", False))
    )


def _registry_succeeded(registry_result: Any) -> bool:
    return (
        bool(getattr(registry_result, "protected_boundary_preserved", False))
        and getattr(registry_result, "registry_file", None) is not None
        and getattr(registry_result, "registry_validation_report", None) is not None
        and bool(getattr(getattr(registry_result, "registry_validation_report", None), "passed", False))
    )


def run_local_parameter_sweep(
    spec: ParameterSweepSpec,
    output_root: str | Path,
    registry_output_root: str | Path,
    *,
    max_point_count: int = DEFAULT_MAX_POINT_COUNT,
) -> LocalParameterSweepResult:
    """Run one deterministic local parameter sweep from an explicit spec."""

    output_root_path = _as_path(output_root)
    registry_output_root_path = _as_path(registry_output_root)
    preflight_failures = (
        _validate_roots(output_root_path, registry_output_root_path)
        + _validate_max_point_count(max_point_count)
        + _validate_spec(spec)
    )
    if preflight_failures:
        return _failure_result(preflight_failures)

    points, point_failures = _enumerate_points(spec, max_point_count)
    if point_failures:
        return _failure_result(point_failures)

    batch_result = run_local_batch(
        _batch_items(spec, points),
        output_root_path,
        BatchResourceLimits(
            max_item_count=max_point_count,
            max_local_jobs=1,
            max_concurrency=1,
            failure_threshold=0,
        ),
        static_metadata={
            "source_package": PACKAGE_LABEL,
            "sweep_id": spec.sweep_id,
            "implementation_id": IMPLEMENTATION_ID,
        },
    )
    if not _batch_succeeded(batch_result):
        reasons = tuple(
            str(reason)
            for reason in getattr(getattr(batch_result, "summary", None), "failure_reasons", ())
        )
        return _failure_result(reasons or ("local batch run failed",), points=points, batch_result=batch_result)

    registry_result = build_local_run_registry((output_root_path,), registry_output_root_path)
    if not _registry_succeeded(registry_result):
        reasons = tuple(str(reason) for reason in getattr(registry_result, "failure_reasons", ()))
        return _failure_result(
            reasons or ("local run registry build failed",),
            points=points,
            batch_result=batch_result,
            registry_result=registry_result,
        )

    summary = _build_summary(spec, points, batch_result, registry_result)
    summary_path = output_root_path / SWEEP_SUMMARY_FILE_NAME
    _write_json(summary_path, asdict(summary))
    written_files: dict[str, Path] = {}
    for key, value in getattr(registry_result, "written_files", {}).items():
        path_value = _written_path(value)
        if path_value is not None:
            written_files[f"registry_{key}"] = path_value
    written_files["local_parameter_sweep_summary"] = summary_path
    return LocalParameterSweepResult(
        points=points,
        batch_result=batch_result,
        registry_result=registry_result,
        summary=summary,
        summary_file=summary_path,
        written_files=written_files,
        failure_reasons=summary.failure_reasons,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=True,
    )
