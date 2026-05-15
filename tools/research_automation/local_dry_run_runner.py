"""Local in-process dry-run runner vertical slice for AUTO-03.

This module is intentionally small. It accepts explicit caller-provided intent,
derives deterministic local-only representations, and writes only to the
caller-provided output directory.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping


IMPLEMENTATION_ID = "wp_12d_auto_03_local_dry_run_runner_v1"
PACKAGE_LABEL = "WP-12d / AUTO-03"
OUTPUT_FILE_NAMES = {
    "run_request": "run_request.json",
    "manifest": "manifest.json",
    "output_bundle": "output_bundle.json",
    "validation_report": "validation_report.json",
}


@dataclass(frozen=True)
class ResearchIntentFixture:
    """Explicit local research intent supplied by the caller or test."""

    intent_id: str
    candidate_id: str
    evaluation_purpose: str
    data_refs: tuple[str, ...]
    timeframe: str
    evaluation_window: Mapping[str, str]
    parameters: Mapping[str, Any]
    pipeline_version: str
    static_metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RunRequest:
    run_id: str
    intent_id: str
    candidate_id: str
    evaluation_purpose: str
    data_refs: tuple[str, ...]
    timeframe: str
    evaluation_window: Mapping[str, str]
    parameters: Mapping[str, Any]
    pipeline_version: str
    implementation_id: str
    package_label: str
    local_only: bool
    deterministic: bool
    non_authoritative: bool


@dataclass(frozen=True)
class RunManifest:
    manifest_id: str
    run_id: str
    intent_id: str
    implementation_id: str
    package_label: str
    pipeline_version: str
    static_metadata: Mapping[str, str]
    output_files: Mapping[str, str]
    local_only: bool
    research_only: bool
    non_authoritative: bool
    protected_boundary_preserved: bool


@dataclass(frozen=True)
class OutputBundle:
    output_bundle_id: str
    run_id: str
    manifest_id: str
    summary: Mapping[str, Any]
    diagnostics: tuple[str, ...]
    local_only: bool
    research_only: bool
    non_authoritative: bool
    creates_committed_evidence: bool


@dataclass(frozen=True)
class ValidationReport:
    validation_report_id: str
    run_id: str
    passed: bool
    failure_reasons: tuple[str, ...]
    checked_boundaries: tuple[str, ...]
    local_only: bool
    research_only: bool
    non_authoritative: bool


@dataclass(frozen=True)
class LocalDryRunResult:
    run_request: RunRequest | None
    manifest: RunManifest | None
    output_bundle: OutputBundle | None
    validation_report: ValidationReport
    written_files: Mapping[str, Path]


def _stable_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _stable_digest(payload: Any) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _validate_intent(intent: ResearchIntentFixture) -> tuple[str, ...]:
    failures: list[str] = []
    required_strings = {
        "intent_id": intent.intent_id,
        "candidate_id": intent.candidate_id,
        "evaluation_purpose": intent.evaluation_purpose,
        "timeframe": intent.timeframe,
        "pipeline_version": intent.pipeline_version,
    }
    for field_name, value in required_strings.items():
        if not isinstance(value, str) or not value.strip():
            failures.append(f"{field_name} must be a non-empty string")

    if not intent.data_refs or any(not isinstance(item, str) or not item.strip() for item in intent.data_refs):
        failures.append("data_refs must contain at least one non-empty local reference")

    window_start = intent.evaluation_window.get("start")
    window_end = intent.evaluation_window.get("end")
    if not isinstance(window_start, str) or not window_start.strip():
        failures.append("evaluation_window.start must be a non-empty string")
    if not isinstance(window_end, str) or not window_end.strip():
        failures.append("evaluation_window.end must be a non-empty string")

    if not isinstance(intent.parameters, Mapping):
        failures.append("parameters must be a mapping")
    if not isinstance(intent.static_metadata, Mapping):
        failures.append("static_metadata must be a mapping")

    return tuple(failures)


def _build_run_request(intent: ResearchIntentFixture) -> RunRequest:
    run_identity_payload = {
        "intent": asdict(intent),
        "implementation_id": IMPLEMENTATION_ID,
        "package_label": PACKAGE_LABEL,
    }
    run_id = f"LDR-{_stable_digest(run_identity_payload)[:12].upper()}"
    return RunRequest(
        run_id=run_id,
        intent_id=intent.intent_id,
        candidate_id=intent.candidate_id,
        evaluation_purpose=intent.evaluation_purpose,
        data_refs=tuple(intent.data_refs),
        timeframe=intent.timeframe,
        evaluation_window=dict(intent.evaluation_window),
        parameters=dict(intent.parameters),
        pipeline_version=intent.pipeline_version,
        implementation_id=IMPLEMENTATION_ID,
        package_label=PACKAGE_LABEL,
        local_only=True,
        deterministic=True,
        non_authoritative=True,
    )


def _build_manifest(run_request: RunRequest, intent: ResearchIntentFixture) -> RunManifest:
    manifest_payload = {
        "run_id": run_request.run_id,
        "intent_id": run_request.intent_id,
        "implementation_id": IMPLEMENTATION_ID,
        "output_files": OUTPUT_FILE_NAMES,
    }
    manifest_id = f"LDM-{_stable_digest(manifest_payload)[:12].upper()}"
    return RunManifest(
        manifest_id=manifest_id,
        run_id=run_request.run_id,
        intent_id=run_request.intent_id,
        implementation_id=IMPLEMENTATION_ID,
        package_label=PACKAGE_LABEL,
        pipeline_version=run_request.pipeline_version,
        static_metadata=dict(intent.static_metadata),
        output_files=dict(OUTPUT_FILE_NAMES),
        local_only=True,
        research_only=True,
        non_authoritative=True,
        protected_boundary_preserved=True,
    )


def _build_output_bundle(run_request: RunRequest, manifest: RunManifest) -> OutputBundle:
    output_payload = {
        "run_id": run_request.run_id,
        "manifest_id": manifest.manifest_id,
        "parameters": run_request.parameters,
        "evaluation_window": run_request.evaluation_window,
    }
    output_bundle_id = f"LDO-{_stable_digest(output_payload)[:12].upper()}"
    return OutputBundle(
        output_bundle_id=output_bundle_id,
        run_id=run_request.run_id,
        manifest_id=manifest.manifest_id,
        summary={
            "candidate_id": run_request.candidate_id,
            "timeframe": run_request.timeframe,
            "data_ref_count": len(run_request.data_refs),
            "parameter_count": len(run_request.parameters),
            "dry_run_status": "completed",
        },
        diagnostics=(
            "local in-process dry-run only",
            "no committed evidence artifact created",
            "no protected runtime boundary contacted",
        ),
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
    )


def _build_validation_report(run_id: str, failures: tuple[str, ...]) -> ValidationReport:
    report_payload = {
        "run_id": run_id,
        "failures": failures,
        "implementation_id": IMPLEMENTATION_ID,
    }
    return ValidationReport(
        validation_report_id=f"LDV-{_stable_digest(report_payload)[:12].upper()}",
        run_id=run_id,
        passed=not failures,
        failure_reasons=failures,
        checked_boundaries=(
            "local_only",
            "research_only",
            "non_authoritative",
            "no_committed_evidence_artifact",
            "no_runtime_paper_live_oms_risk_safe_mode_contact",
            "no_exchange_broker_order_scheduler_daemon_queue_contact",
            "no_config_dependency_schema_validator_query_layer_contact",
        ),
        local_only=True,
        research_only=True,
        non_authoritative=True,
    )


def run_local_dry_run(intent: ResearchIntentFixture, output_dir: Path) -> LocalDryRunResult:
    """Run one deterministic local dry-run slice from an explicit intent.

    The function derives all run content from its arguments and writes only
    under ``output_dir``.
    """

    if output_dir.exists() and not output_dir.is_dir():
        failure_report = _build_validation_report("LDR-INVALID", ("output_dir must be a directory",))
        return LocalDryRunResult(
            run_request=None,
            manifest=None,
            output_bundle=None,
            validation_report=failure_report,
            written_files={},
        )
    output_dir.mkdir(parents=True, exist_ok=True)

    intent_failures = _validate_intent(intent)
    if intent_failures:
        validation_report = _build_validation_report("LDR-INVALID", intent_failures)
        validation_path = output_dir / OUTPUT_FILE_NAMES["validation_report"]
        _write_json(validation_path, asdict(validation_report))
        return LocalDryRunResult(
            run_request=None,
            manifest=None,
            output_bundle=None,
            validation_report=validation_report,
            written_files={"validation_report": validation_path},
        )

    run_request = _build_run_request(intent)
    manifest = _build_manifest(run_request, intent)
    output_bundle = _build_output_bundle(run_request, manifest)
    validation_report = _build_validation_report(run_request.run_id, ())

    written_files = {
        "run_request": output_dir / OUTPUT_FILE_NAMES["run_request"],
        "manifest": output_dir / OUTPUT_FILE_NAMES["manifest"],
        "output_bundle": output_dir / OUTPUT_FILE_NAMES["output_bundle"],
        "validation_report": output_dir / OUTPUT_FILE_NAMES["validation_report"],
    }
    _write_json(written_files["run_request"], asdict(run_request))
    _write_json(written_files["manifest"], asdict(manifest))
    _write_json(written_files["output_bundle"], asdict(output_bundle))
    _write_json(written_files["validation_report"], asdict(validation_report))

    return LocalDryRunResult(
        run_request=run_request,
        manifest=manifest,
        output_bundle=output_bundle,
        validation_report=validation_report,
        written_files=written_files,
    )
