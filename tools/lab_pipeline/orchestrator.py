"""Deterministic non-canonical lab pipeline orchestrator."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from tools.lab_pipeline import model
from tools.lab_pipeline.state import (
    file_sha256,
    read_json,
    sha256_payload,
    write_json,
    write_text,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
WP_ID = "WP-LABPROD-PIPELINE-ORCHESTRATOR-01"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "scratch" / WP_ID / "outputs"
DEFAULT_SCRATCH_ROOT = REPO_ROOT / "scratch" / WP_ID
DETERMINISTIC_TIMESTAMP_UTC = "2026-07-08T00:00:00Z"
CREATED_AT_POLICY = "deterministic_from_request_content_no_wall_clock"

_FORBIDDEN_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bcanonical\b.*\b(result population|evidence|write)\b", re.I), "canonical_result_population_write"),
    (re.compile(r"\b(result population|evidence)\b.*\bcanonical\b", re.I), "canonical_result_population_write"),
    (re.compile(r"\b(candidate|registry|lifecycle|admission)\b", re.I), "candidate_admission_or_lifecycle_write"),
    (re.compile(r"\bcrossing\b", re.I), "canonical_crossing"),
    (re.compile(r"\b(promot|readiness|ready for paper|ready for live)\b", re.I), "promotion_or_readiness"),
    (re.compile(r"\b(paper|live|runtime|OMS|risk|reconciliation|order|exchange|broker)\b", re.I), "paper_live_runtime_contact"),
    (re.compile(r"\b(scheduler|autonomous|cron|daemon|dispatch)\b", re.I), "scheduler_or_autonomous_dispatch"),
    (re.compile(r"\b(notification|notify|fire alert)\b", re.I), "notification_firing"),
    (re.compile(r"\b(provider api|api key|credential|secret|network call)\b", re.I), "provider_api_or_credential_use"),
)

_SOURCE_FORBIDDEN_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(write|create|commit)\b.*\bcanonical\b.*\b(result population|evidence)\b", re.I), "canonical_result_population_write"),
    (re.compile(r"\b(register|admit|write|update)\b.*\b(candidate|registry|lifecycle)\b", re.I), "candidate_admission_or_lifecycle_write"),
    (re.compile(r"\b(execute|perform|create)\b.*\bcrossing\b", re.I), "canonical_crossing"),
    (re.compile(r"\b(promote|declare readiness|mark ready)\b", re.I), "promotion_or_readiness"),
    (re.compile(r"\b(contact|handoff to|run|touch)\b.*\b(paper|live|runtime)\b", re.I), "paper_live_runtime_contact"),
    (re.compile(r"\b(scheduler|autonomous)\b.*\b(dispatch|run|trigger)\b", re.I), "scheduler_or_autonomous_dispatch"),
    (re.compile(r"\b(fire|send)\b.*\b(notification|alert)\b", re.I), "notification_firing"),
    (re.compile(r"\b(use|call|read)\b.*\b(provider api|api key|credential|secret)\b", re.I), "provider_api_or_credential_use"),
)


class PipelineBlockedError(ValueError):
    """Raised for malformed requests that cannot produce an auditable packet."""


@dataclass(frozen=True)
class PipelineRequest:
    source_idea: str
    symbol: str = "BTCUSDT"
    timeframe: str = "15m"
    requested_by: str = "operator"
    request_id: str | None = None
    deterministic_timestamp_utc: str = DETERMINISTIC_TIMESTAMP_UTC
    requested_authority: tuple[str, ...] = ()
    requested_outputs: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "PipelineRequest":
        idea = str(raw.get("source_idea", "")).strip()
        if not idea:
            raise PipelineBlockedError("source_idea is required")
        requested_authority = tuple(str(item) for item in raw.get("requested_authority", []))
        requested_outputs = tuple(str(item) for item in raw.get("requested_outputs", []))
        return cls(
            source_idea=idea,
            symbol=str(raw.get("symbol", "BTCUSDT")),
            timeframe=str(raw.get("timeframe", "15m")),
            requested_by=str(raw.get("requested_by", "operator")),
            request_id=raw.get("request_id"),
            deterministic_timestamp_utc=str(
                raw.get("deterministic_timestamp_utc", DETERMINISTIC_TIMESTAMP_UTC)
            ),
            requested_authority=requested_authority,
            requested_outputs=requested_outputs,
        )

    def normalized(self) -> dict[str, Any]:
        base = {
            "schema_version": model.REQUEST_SCHEMA_VERSION,
            "source_idea": self.source_idea,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "requested_by": self.requested_by,
            "deterministic_timestamp_utc": self.deterministic_timestamp_utc,
            "requested_authority": list(self.requested_authority),
            "requested_outputs": list(self.requested_outputs),
        }
        request_id = self.request_id
        if not request_id:
            request_id = "REQ-" + sha256_payload(base).split(":", 1)[1][:12]
        base["request_id"] = request_id
        return base


@dataclass(frozen=True)
class PipelineResult:
    pipeline_run_id: str
    pipeline_status: str
    current_stage: str
    output_dir: Path
    artifact_paths: dict[str, str]
    blocked_reasons: tuple[str, ...]


def _pipeline_run_id(request_payload: Mapping[str, Any]) -> str:
    return "LPIPE-" + sha256_payload(
        {"pipeline": "lab_pipeline_v1", "request": request_payload}
    ).split(":", 1)[1][:16]


def _scan_forbidden(request: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    authority_text = "\n".join(
        [
            " ".join(str(item) for item in request.get("requested_authority", [])),
            " ".join(str(item) for item in request.get("requested_outputs", [])),
        ]
    )
    for pattern, code in _FORBIDDEN_PATTERNS:
        if pattern.search(authority_text):
            findings.append(f"requires_separate_authorization:{code}")
    source_text = str(request.get("source_idea", ""))
    for pattern, code in _SOURCE_FORBIDDEN_PATTERNS:
        if pattern.search(source_text):
            findings.append(f"requires_separate_authorization:{code}")
    return sorted(set(findings))


def _base_stage_records() -> dict[str, model.StageRecord]:
    return {stage: model.StageRecord(stage=stage) for stage in model.PIPELINE_STAGES}


def _set_stage(
    stages: dict[str, model.StageRecord],
    stage: str,
    status: str,
    detail: str,
    *,
    artifact_refs: tuple[str, ...] = (),
    blocked_reasons: tuple[str, ...] = (),
) -> None:
    stages[stage] = model.StageRecord(
        stage=stage,
        status=status,
        detail=detail,
        artifact_refs=artifact_refs,
        blocked_reasons=blocked_reasons,
    )


def _availability_check(request: Mapping[str, Any]) -> tuple[str, list[str]]:
    problems: list[str] = []
    if request["symbol"] != "BTCUSDT":
        problems.append("unsupported_symbol")
    if request["timeframe"] not in model.LOCKED_TIMEFRAMES:
        problems.append("unsupported_timeframe")
    if problems:
        return "blocked", problems
    return "ready", []


def _formalized_idea(request: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "lab_pipeline_formalized_idea_v1",
        "request_id": request["request_id"],
        "source_idea": request["source_idea"],
        "symbol": request["symbol"],
        "timeframe": request["timeframe"],
        "formalization_kind": "operator_supplied_idea_preserved",
        "supported_pipeline_posture": "noncanonical_scratch_prereg_packet_only",
        "unresolved_questions": [],
        "non_authority_flags": dict(model.NON_AUTHORITY_FLAGS),
    }


def _prereg_packet(
    *,
    pipeline_run_id: str,
    request: Mapping[str, Any],
    formalized: Mapping[str, Any],
    availability: Mapping[str, Any],
) -> dict[str, Any]:
    packet = {
        "schema_version": "lab_pipeline_preregistration_packet_v1",
        "pipeline_run_id": pipeline_run_id,
        "request_id": request["request_id"],
        "frozen_content": {
            "request": dict(request),
            "formalized_idea": dict(formalized),
            "availability_check": dict(availability),
            "execution_scope": "noncanonical_offline_research_only",
            "canonical_write_allowed": False,
            "candidate_lifecycle_write_allowed": False,
            "paper_live_runtime_contact_allowed": False,
            "scheduler_autonomy_allowed": False,
            "notification_firing_allowed": False,
            "provider_api_network_allowed": False,
            "denominator_policy": "preserve_all_generated_rows_no_winner_only_selection",
        },
        "approval_binding": {
            "required_approval_scope": model.APPROVAL_SCOPE,
            "required_approval_statement": model.APPROVAL_STATEMENT,
            "hash_algorithm": "sha256",
            "hash_scope": "packet_without_packet_sha256",
        },
        "non_authority_flags": dict(model.NON_AUTHORITY_FLAGS),
    }
    packet["packet_sha256"] = sha256_payload(packet)
    return packet


def _approval_requirement(packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "lab_pipeline_approval_requirement_v1",
        "pipeline_run_id": packet["pipeline_run_id"],
        "request_id": packet["request_id"],
        "preregistration_packet_sha256": packet["packet_sha256"],
        "approval_marker_schema": model.APPROVAL_SCHEMA_VERSION,
        "required_fields": {
            "schema_version": model.APPROVAL_SCHEMA_VERSION,
            "approved_by": "Karl",
            "approval_scope": model.APPROVAL_SCOPE,
            "approval_statement": model.APPROVAL_STATEMENT,
            "authorizes_noncanonical_offline_research_execution": True,
            "authorizes_canonical_write": False,
            "authorizes_candidate_lifecycle": False,
            "authorizes_paper_live_runtime": False,
            "authorizes_scheduler_autonomy": False,
            "authorizes_notifications": False,
            "preregistration_packet_sha256": packet["packet_sha256"],
        },
        "non_authority_flags": dict(model.NON_AUTHORITY_FLAGS),
    }


def _validate_approval(
    approval_path: Path | None,
    packet: Mapping[str, Any],
) -> tuple[bool, dict[str, Any], list[str]]:
    if approval_path is None:
        return False, {}, ["missing_prereg_approval"]
    try:
        approval = read_json(approval_path)
    except (OSError, ValueError) as exc:
        return False, {}, [f"malformed_prereg_approval:{exc}"]
    errors: list[str] = []
    required_false = {
        "authorizes_canonical_write": False,
        "authorizes_candidate_lifecycle": False,
        "authorizes_paper_live_runtime": False,
        "authorizes_scheduler_autonomy": False,
        "authorizes_notifications": False,
    }
    if approval.get("schema_version") != model.APPROVAL_SCHEMA_VERSION:
        errors.append("approval_schema_version_mismatch")
    if approval.get("approved_by") != "Karl":
        errors.append("approval_actor_not_karl")
    if approval.get("approval_scope") != model.APPROVAL_SCOPE:
        errors.append("approval_scope_not_noncanonical_offline_only")
    if approval.get("approval_statement") != model.APPROVAL_STATEMENT:
        errors.append("approval_statement_not_exact")
    if approval.get("authorizes_noncanonical_offline_research_execution") is not True:
        errors.append("approval_missing_noncanonical_execution_flag")
    if approval.get("preregistration_packet_sha256") != packet["packet_sha256"]:
        errors.append("approval_hash_mismatch")
    if not isinstance(approval.get("approval_timestamp_utc"), str) or not approval.get(
        "approval_timestamp_utc"
    ):
        errors.append("approval_timestamp_missing")
    for field, expected in required_false.items():
        if approval.get(field) is not expected:
            errors.append(f"approval_too_broad:{field}")
    return not errors, approval, errors


def _noncanonical_execution_packet(
    request: Mapping[str, Any], packet: Mapping[str, Any], approval: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "schema_version": "lab_pipeline_noncanonical_execution_summary_v1",
        "pipeline_run_id": packet["pipeline_run_id"],
        "request_id": request["request_id"],
        "execution_kind": "deterministic_spine_proof",
        "runner_invoked": False,
        "provider_api_network_attempted": False,
        "canonical_files_written": False,
        "approval_marker": {
            "approved_by": approval.get("approved_by"),
            "approval_scope": approval.get("approval_scope"),
            "preregistration_packet_sha256": approval.get("preregistration_packet_sha256"),
        },
        "denominator": {
            "planned_rows": 1,
            "preserved_rows": 1,
            "completed_rows": 1,
            "failed_rows": 0,
            "invalid_rows": 0,
            "blocked_rows": 0,
            "winner_only_selection": False,
        },
        "result": {
            "classification": "noncanonical_pipeline_spine_smoke",
            "candidate_claim_created": False,
            "promotion_or_readiness_created": False,
        },
        "non_authority_flags": dict(model.NON_AUTHORITY_FLAGS),
    }


def _operator_review_markdown(
    state: Mapping[str, Any],
    artifacts: Mapping[str, str],
    *,
    execution_summary: Mapping[str, Any] | None,
) -> str:
    lines = [
        "# Lab Pipeline Operator Review Packet",
        "",
        f"- Pipeline run ID: {state['pipeline_run_id']}",
        f"- Request ID: {state['request_id']}",
        f"- Status: {state['pipeline_status']}",
        f"- Current stage: {state['current_stage']}",
        "- Posture: non-canonical offline lab orchestration only",
        "",
        "## Non-Authority Flags",
    ]
    for key, value in state["non_authority_flags"].items():
        lines.append(f"- {key}: {str(value).lower()}")
    lines.extend(["", "## Blocked Reasons"])
    if state["blocked_reasons"]:
        lines.extend(f"- {reason}" for reason in state["blocked_reasons"])
    else:
        lines.append("- none")
    lines.extend(["", "## Artifacts"])
    for name, path in sorted(artifacts.items()):
        lines.append(f"- {name}: {path}")
    if execution_summary is not None:
        lines.extend(
            [
                "",
                "## Non-Canonical Execution Summary",
                f"- Runner invoked: {str(execution_summary['runner_invoked']).lower()}",
                f"- Provider/API/network attempted: {str(execution_summary['provider_api_network_attempted']).lower()}",
                f"- Canonical files written: {str(execution_summary['canonical_files_written']).lower()}",
                f"- Preserved rows: {execution_summary['denominator']['preserved_rows']}/{execution_summary['denominator']['planned_rows']}",
            ]
        )
    return "\n".join(lines) + "\n"


def run_pipeline(
    *,
    request_path: Path,
    approval_path: Path | None = None,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> PipelineResult:
    _validate_output_root(output_root)
    raw_request = read_json(request_path)
    request_obj = PipelineRequest.from_mapping(raw_request)
    request = request_obj.normalized()
    pipeline_run_id = _pipeline_run_id(request)
    run_dir = output_root / pipeline_run_id
    artifacts: dict[str, str] = {}
    trace: list[model.PipelineTraceEvent] = []
    stages = _base_stage_records()

    def add_trace(stage: str, status: str, detail: str = "") -> None:
        trace.append(model.PipelineTraceEvent(stage=stage, status=status, detail=detail))

    request_out = run_dir / "pipeline_request.json"
    artifacts["pipeline_request"] = write_json(request_out, request)
    _set_stage(stages, "request_loaded", "complete", "Request loaded.", artifact_refs=(artifacts["pipeline_request"],))
    add_trace("request_loaded", "complete", "Request loaded.")

    blocked = _scan_forbidden(request)
    if blocked:
        _set_stage(
            stages,
            "blocked",
            "blocked",
            "Request includes authority outside this package.",
            blocked_reasons=tuple(blocked),
        )
        add_trace("blocked", "blocked", "Forbidden authority requested.")
        return _finalize(
            run_dir=run_dir,
            request=request,
            pipeline_run_id=pipeline_run_id,
            stages=stages,
            artifacts=artifacts,
            trace=trace,
            current_stage="blocked",
            pipeline_status="blocked",
            blocked_reasons=tuple(blocked),
            approval_requirements={},
            execution_summary=None,
        )

    formalized = _formalized_idea(request)
    _set_stage(stages, "idea_formalized", "complete", "Operator idea preserved and formalized.")
    add_trace("idea_formalized", "complete", "Operator idea formalized.")

    availability_status, availability_problems = _availability_check(request)
    availability = {
        "schema_version": "lab_pipeline_availability_check_v1",
        "status": availability_status,
        "symbol_supported": request["symbol"] == "BTCUSDT",
        "timeframe_supported": request["timeframe"] in model.LOCKED_TIMEFRAMES,
        "problems": availability_problems,
        "non_authority_flags": dict(model.NON_AUTHORITY_FLAGS),
    }
    if availability_problems:
        reasons = tuple(f"availability_blocked:{problem}" for problem in availability_problems)
        _set_stage(stages, "availability_checked", "blocked", "Availability check blocked.", blocked_reasons=reasons)
        _set_stage(stages, "blocked", "blocked", "Pipeline blocked by availability.", blocked_reasons=reasons)
        add_trace("availability_checked", "blocked", "Availability check blocked.")
        return _finalize(
            run_dir=run_dir,
            request=request,
            pipeline_run_id=pipeline_run_id,
            stages=stages,
            artifacts=artifacts,
            trace=trace,
            current_stage="blocked",
            pipeline_status="blocked",
            blocked_reasons=reasons,
            approval_requirements={},
            execution_summary=None,
        )
    _set_stage(stages, "availability_checked", "complete", "Availability check passed for prereg packet preparation.")
    add_trace("availability_checked", "complete", "Availability check passed.")

    packet = _prereg_packet(
        pipeline_run_id=pipeline_run_id,
        request=request,
        formalized=formalized,
        availability=availability,
    )
    artifacts["preregistration_packet"] = write_json(
        run_dir / "preregistration_packet.json", packet
    )
    requirement = _approval_requirement(packet)
    artifacts["approval_requirement"] = write_json(run_dir / "approval_requirement.json", requirement)
    _set_stage(
        stages,
        "prereg_packet_prepared",
        "complete",
        "Frozen preregistration packet prepared.",
        artifact_refs=(artifacts["preregistration_packet"], artifacts["approval_requirement"]),
    )
    add_trace("prereg_packet_prepared", "complete", "Frozen packet prepared.")

    approval_ok, approval, approval_errors = _validate_approval(approval_path, packet)
    if not approval_ok:
        reasons = tuple(f"prereg_approval_blocked:{error}" for error in approval_errors)
        _set_stage(
            stages,
            "awaiting_prereg_approval",
            "awaiting_approval",
            "Pipeline halted until exact-content prereg approval is supplied.",
            artifact_refs=(artifacts["approval_requirement"],),
            blocked_reasons=reasons,
        )
        add_trace("awaiting_prereg_approval", "awaiting_approval", "Approval missing or invalid.")
        return _finalize(
            run_dir=run_dir,
            request=request,
            pipeline_run_id=pipeline_run_id,
            stages=stages,
            artifacts=artifacts,
            trace=trace,
            current_stage="awaiting_prereg_approval",
            pipeline_status="awaiting_prereg_approval",
            blocked_reasons=reasons,
            approval_requirements=requirement,
            execution_summary=None,
        )

    _set_stage(
        stages,
        "awaiting_prereg_approval",
        "complete",
        "Exact-content prereg approval marker accepted.",
    )
    _set_stage(
        stages,
        "approved_for_noncanonical_execution",
        "complete",
        "Approval scope permits only non-canonical offline research execution.",
    )
    add_trace("approved_for_noncanonical_execution", "complete", "Approval accepted.")

    _set_stage(stages, "noncanonical_execution_running", "complete", "Deterministic non-canonical spine step entered.")
    execution_summary = _noncanonical_execution_packet(request, packet, approval)
    _set_stage(
        stages,
        "noncanonical_execution_complete",
        "complete",
        "Non-canonical spine step completed with preserved denominator.",
    )
    add_trace("noncanonical_execution_complete", "complete", "Scratch-only execution summary produced.")

    _set_stage(stages, "gate_review_complete", "complete", "Gate review completed as non-authoritative packet check.")
    _set_stage(stages, "robustness_review_complete", "complete", "Robustness review completed as non-authoritative packet check.")
    _set_stage(
        stages,
        "candidate_review_packet_prepared",
        "complete",
        "Operator review packet prepared without candidate lifecycle authority.",
    )
    _set_stage(stages, "complete", "complete", "Pipeline packet complete.")
    add_trace("complete", "complete", "Pipeline complete.")

    return _finalize(
        run_dir=run_dir,
        request=request,
        pipeline_run_id=pipeline_run_id,
        stages=stages,
        artifacts=artifacts,
        trace=trace,
        current_stage="complete",
        pipeline_status="complete",
        blocked_reasons=(),
        approval_requirements=requirement,
        execution_summary=execution_summary,
    )


def _finalize(
    *,
    run_dir: Path,
    request: Mapping[str, Any],
    pipeline_run_id: str,
    stages: Mapping[str, model.StageRecord],
    artifacts: dict[str, str],
    trace: list[model.PipelineTraceEvent],
    current_stage: str,
    pipeline_status: str,
    blocked_reasons: tuple[str, ...],
    approval_requirements: Mapping[str, Any],
    execution_summary: Mapping[str, Any] | None,
) -> PipelineResult:
    state = model.PipelineState(
        pipeline_run_id=pipeline_run_id,
        request_id=str(request["request_id"]),
        current_stage=current_stage,
        pipeline_status=pipeline_status,
        source_idea=str(request["source_idea"]),
        symbol=str(request["symbol"]),
        timeframe=str(request["timeframe"]),
        requested_by=str(request["requested_by"]),
        created_at_policy=CREATED_AT_POLICY,
        deterministic_timestamp_utc=str(request["deterministic_timestamp_utc"]),
        stage_statuses=tuple(stages[stage] for stage in model.PIPELINE_STAGES),
        artifact_refs=tuple(sorted(artifacts.values())),
        approval_requirements=dict(approval_requirements),
        blocked_reasons=blocked_reasons,
    ).to_dict()
    artifacts["pipeline_state"] = write_json(run_dir / "pipeline_state.json", state)
    artifacts["pipeline_trace"] = write_json(
        run_dir / "pipeline_trace.json",
        {
            "schema_version": "lab_pipeline_trace_v1",
            "pipeline_run_id": pipeline_run_id,
            "events": [event.to_dict() for event in trace],
            "non_authority_flags": dict(model.NON_AUTHORITY_FLAGS),
        },
    )
    assertions = {
        "schema_version": "lab_pipeline_non_authority_assertions_v1",
        "pipeline_run_id": pipeline_run_id,
        "protected_paths_touched": False,
        "canonical_files_written": False,
        "candidate_lifecycle_written": False,
        "paper_live_runtime_contacted": False,
        "scheduler_or_autonomy_used": False,
        "notifications_fired": False,
        "provider_api_network_attempted": False,
        "dependency_changes_required": False,
        "non_authority_flags": dict(model.NON_AUTHORITY_FLAGS),
    }
    artifacts["non_authority_assertions"] = write_json(
        run_dir / "non_authority_assertions.json", assertions
    )
    if execution_summary is not None:
        artifacts["noncanonical_execution_summary"] = write_json(
            run_dir / "noncanonical_execution_summary.json", execution_summary
        )
    artifacts["operator_review_packet"] = write_text(
        run_dir / "operator_review_packet.md",
        _operator_review_markdown(state, artifacts, execution_summary=execution_summary),
    )
    index_payload = {
        "schema_version": "lab_pipeline_artifact_index_v1",
        "pipeline_run_id": pipeline_run_id,
        "artifact_count": len(artifacts) + 1,
        "artifacts": {
            name: {
                "path": path,
                "sha256": file_sha256(Path(path)) if Path(path).exists() else None,
            }
            for name, path in sorted(artifacts.items())
        },
        "self_entry_note": "artifact_index self hash omitted to avoid recursive hash mutation",
        "non_authority_flags": dict(model.NON_AUTHORITY_FLAGS),
    }
    artifacts["artifact_index"] = write_json(run_dir / "artifact_index.json", index_payload)
    return PipelineResult(
        pipeline_run_id=pipeline_run_id,
        pipeline_status=pipeline_status,
        current_stage=current_stage,
        output_dir=run_dir,
        artifact_paths=dict(artifacts),
        blocked_reasons=blocked_reasons,
    )


def _validate_output_root(output_root: Path) -> None:
    """Allow repo writes only inside this package's scratch root."""

    resolved = Path(output_root).resolve()
    repo = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo)
    except ValueError:
        return
    allowed = DEFAULT_SCRATCH_ROOT.resolve()
    try:
        resolved.relative_to(allowed)
    except ValueError as exc:
        raise PipelineBlockedError(
            "output_root inside repo must be under "
            f"{allowed.as_posix()}; got {rel.as_posix()}"
        ) from exc


def approval_template_for(preregistration_packet_path: Path) -> dict[str, Any]:
    packet = read_json(preregistration_packet_path)
    packet_hash = packet.get("packet_sha256")
    if not isinstance(packet_hash, str):
        raise PipelineBlockedError("preregistration packet lacks packet_sha256")
    return {
        "schema_version": model.APPROVAL_SCHEMA_VERSION,
        "approved_by": "Karl",
        "approval_scope": model.APPROVAL_SCOPE,
        "approval_statement": model.APPROVAL_STATEMENT,
        "approval_timestamp_utc": DETERMINISTIC_TIMESTAMP_UTC,
        "authorizes_noncanonical_offline_research_execution": True,
        "authorizes_canonical_write": False,
        "authorizes_candidate_lifecycle": False,
        "authorizes_paper_live_runtime": False,
        "authorizes_scheduler_autonomy": False,
        "authorizes_notifications": False,
        "preregistration_packet_sha256": packet_hash,
    }
