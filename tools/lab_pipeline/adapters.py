"""Adapter-backed lab pipeline flow.

This module consumes a valid lab-pipeline prereg approval marker and writes one
package-local non-canonical adapter packet. It does not create approvals,
canonical evidence, candidates, scheduler actions, notifications, or runtime
contact.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from tools.agent_sandbox import MemoryAuditSink, ToolContext
from tools.lab_pipeline import model
from tools.lab_pipeline.adapter_contract import (
    ADAPTER_CONTRACT_VERSION,
    ADAPTER_RUN_STATUSES,
    ADAPTER_STAGE_STATUSES,
    NON_AUTHORITY_ASSERTIONS,
    AdapterRecord,
    build_adapter_registry,
)
from tools.lab_pipeline.state import file_sha256, read_json, sha256_payload, write_json, write_text
from tools.lab_readiness.readiness import build_readiness_projection
from tools.research_agents.idea_formalizer_agent import (
    IdeaFormalizerAgent,
    IdeaFormalizerConfig,
    make_provider,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
WP_ID = "WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02"
DEFAULT_ADAPTER_OUTPUT_ROOT = REPO_ROOT / "scratch" / WP_ID / "outputs"
DEFAULT_ADAPTER_SCRATCH_ROOT = REPO_ROOT / "scratch" / WP_ID


class AdapterFlowError(ValueError):
    """Raised when an adapter flow cannot produce an auditable packet."""


@dataclass(frozen=True)
class AdapterFlowResult:
    adapter_run_id: str
    adapter_status: str
    output_dir: Path
    artifact_paths: dict[str, str]
    gap_count: int
    invoked_real_modules: tuple[str, ...]


def _fixed_clock() -> datetime:
    return datetime(2026, 7, 8, 0, 0, 0, tzinfo=timezone.utc)


def _adapter_run_id(request: Mapping[str, Any], pipeline_run_id: str) -> str:
    digest = sha256_payload(
        {
            "adapter_contract_version": ADAPTER_CONTRACT_VERSION,
            "pipeline_run_id": pipeline_run_id,
            "request": dict(request),
        }
    ).split(":", 1)[1][:16]
    return f"LADAPT-{digest}"


def _repo_relative(path: Path | str) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        try:
            candidate = candidate.resolve().relative_to(REPO_ROOT.resolve())
        except ValueError:
            return f"external:{candidate.name}"
    normalized = candidate.as_posix()
    if normalized == ".." or normalized.startswith("../"):
        raise AdapterFlowError("adapter artifact path must remain inside repo")
    return normalized


def _validate_adapter_output_root(output_root: Path) -> None:
    resolved = output_root.resolve()
    repo = REPO_ROOT.resolve()
    try:
        resolved.relative_to(repo)
    except ValueError:
        return
    allowed = DEFAULT_ADAPTER_SCRATCH_ROOT.resolve()
    try:
        resolved.relative_to(allowed)
    except ValueError as exc:
        raise AdapterFlowError(
            "adapter output_root inside repo must be under "
            f"{allowed.as_posix()}; got {resolved.as_posix()}"
        ) from exc


def _validate_pipeline_approval(
    *,
    approval_path: Path | None,
    preregistration_packet_path: Path,
) -> tuple[bool, dict[str, Any] | None, tuple[str, ...]]:
    if approval_path is None:
        return False, None, ("missing_prereg_approval",)
    packet = read_json(preregistration_packet_path)
    approval = read_json(approval_path)
    errors: list[str] = []
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
    if approval.get("preregistration_packet_sha256") != packet.get("packet_sha256"):
        errors.append("approval_hash_mismatch")
    for field in (
        "authorizes_canonical_write",
        "authorizes_candidate_lifecycle",
        "authorizes_paper_live_runtime",
        "authorizes_scheduler_autonomy",
        "authorizes_notifications",
    ):
        if approval.get(field) is not False:
            errors.append(f"approval_too_broad:{field}")
    return not errors, approval, tuple(errors)


def _stage_event(
    *,
    adapter: AdapterRecord,
    status: str,
    reason_code: str,
    detail: str,
    input_paths: list[str] | None = None,
    output_paths: list[str] | None = None,
    hashes: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    if status not in ADAPTER_STAGE_STATUSES:
        raise AdapterFlowError(f"unknown adapter stage status: {status}")
    return {
        "adapter_id": adapter.adapter_id,
        "stage": adapter.stage,
        "status": status,
        "reason_code": reason_code,
        "detail": detail,
        "input_paths": input_paths or [],
        "output_paths": output_paths or [],
        "hashes": dict(hashes or {}),
        "non_authority_assertions": dict(NON_AUTHORITY_ASSERTIONS),
    }


def _hash_paths(paths: list[str]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in paths:
        target = REPO_ROOT / path
        if target.exists() and target.is_file():
            hashes[path] = file_sha256(target)
    return hashes


def _formalizer_output_paths(result: Mapping[str, Any]) -> list[str]:
    run_id = str(result.get("run_id"))
    base = Path("scratch") / WP_ID / "outputs" / run_id
    paths = [
        (base / "formalized_idea.json").as_posix(),
        (base / "human_review_packet.json").as_posix(),
    ]
    draft = result.get("draft_strategy_spec")
    if isinstance(draft, Mapping) and isinstance(draft.get("path"), str):
        paths.append(str(draft["path"]))
    metadata = result.get("adapter_metadata")
    declared = metadata.get("strategy_spec_paths") if isinstance(metadata, Mapping) else None
    if isinstance(declared, Mapping):
        paths.extend(str(path) for path in declared.values() if isinstance(path, str))
    return list(dict.fromkeys(paths))


def _run_idea_formalizer(request: Mapping[str, Any]) -> tuple[dict[str, Any], list[str], list[dict[str, Any]]]:
    sink = MemoryAuditSink()
    context = ToolContext(
        wp_id=WP_ID,
        role="idea_formalizer",
        audit_sink=sink,
        clock=_fixed_clock,
    )
    config = IdeaFormalizerConfig(provider_mode="fake_offline", provider_id="fake-rule-v1")
    agent = IdeaFormalizerAgent(
        config=config,
        tool_context=context,
        provider=make_provider(config),
        repo_root=REPO_ROOT,
    )
    result = agent.run(
        idea=str(request["source_idea"]),
        symbol=str(request["symbol"]),
        timeframe=str(request["timeframe"]),
        constraints=[
            "Pipeline adapter invocation: scratch-only, non-canonical, no provider/API call.",
            "Do not request canonical evidence, candidate lifecycle, paper/live/runtime, or scheduler authority.",
        ],
    )
    paths = _formalizer_output_paths(result)
    return result, paths, [record.to_dict() for record in sink.records]


def _review_packet_markdown(
    *,
    state: Mapping[str, Any],
    trace: list[Mapping[str, Any]],
    gaps: list[Mapping[str, Any]],
    artifacts: Mapping[str, str],
) -> str:
    lines = [
        "# Lab Pipeline Adapter Operator Review Packet",
        "",
        f"- Adapter run ID: {state['adapter_run_id']}",
        f"- Pipeline run ID: {state['pipeline_run_id']}",
        f"- Status: {state['adapter_status']}",
        f"- Gap count: {state['gap_count']}",
        "- Posture: package-local, scratch-only, non-canonical offline research adapter packet",
        "",
        "## Stage Trace",
    ]
    for event in trace:
        lines.append(
            f"- {event['stage']}: {event['status']} ({event['reason_code']})"
        )
    lines.extend(["", "## Gap Register"])
    if gaps:
        for gap in gaps:
            lines.append(
                f"- {gap['stage']}: {gap['status']} - {gap['blocker_reason']}"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Non-Authority Assertions"])
    for key, value in state["non_authority_assertions"].items():
        lines.append(f"- {key}: {str(value).lower()}")
    lines.extend(["", "## Artifacts"])
    for name, path in sorted(artifacts.items()):
        lines.append(f"- {name}: {path}")
    return "\n".join(lines) + "\n"


def run_adapter_flow(
    *,
    request: Mapping[str, Any],
    pipeline_run_id: str,
    preregistration_packet_path: Path,
    approval_path: Path | None,
    output_root: Path = DEFAULT_ADAPTER_OUTPUT_ROOT,
) -> AdapterFlowResult:
    """Run the safe adapter-backed portion of one approved lab pipeline packet."""

    _validate_adapter_output_root(output_root)
    adapter_run_id = _adapter_run_id(request, pipeline_run_id)
    run_dir = output_root / adapter_run_id
    registry = build_adapter_registry(WP_ID)
    registry_by_stage = {adapter.stage: adapter for adapter in registry}
    artifacts: dict[str, str] = {}
    trace: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    invoked: list[str] = []

    adapter_request = {
        "schema_version": "lab_pipeline_adapter_request_v1",
        "adapter_contract_version": ADAPTER_CONTRACT_VERSION,
        "adapter_run_id": adapter_run_id,
        "pipeline_run_id": pipeline_run_id,
        "pipeline_request": dict(request),
        "preregistration_packet_path": _repo_relative(preregistration_packet_path),
        "approval_path": None if approval_path is None else _repo_relative(approval_path),
        "requested_posture": "noncanonical_offline_research_adapters_only",
        "non_authority_assertions": dict(NON_AUTHORITY_ASSERTIONS),
    }
    artifacts["pipeline_adapter_request"] = write_json(
        run_dir / "pipeline_adapter_request.json", adapter_request
    )
    artifacts["adapter_registry"] = write_json(
        run_dir / "adapter_registry.json",
        {
            "schema_version": ADAPTER_CONTRACT_VERSION,
            "registry_closed": True,
            "adapter_count": len(registry),
            "adapters": [adapter.to_dict() for adapter in registry],
        },
    )

    approval_ok, approval, approval_errors = _validate_pipeline_approval(
        approval_path=approval_path,
        preregistration_packet_path=preregistration_packet_path,
    )
    if not approval_ok:
        for adapter in registry:
            event = _stage_event(
                adapter=adapter,
                status="awaiting_prereg_approval",
                reason_code="pipeline_prereg_approval_missing_or_invalid",
                detail="Adapter execution halted before invoking real modules.",
            )
            trace.append(event)
        final_status = "awaiting_prereg_approval"
    else:
        formalizer_adapter = registry_by_stage["idea_formalization"]
        try:
            formalizer_result, formalizer_paths, audit_records = _run_idea_formalizer(request)
            artifacts["idea_formalizer_result"] = formalizer_paths[0]
            artifacts["idea_formalizer_human_review_packet"] = formalizer_paths[1]
            if len(formalizer_paths) > 2:
                artifacts["idea_formalizer_draft_strategy_spec"] = formalizer_paths[2]
            artifacts["idea_formalizer_audit_records"] = write_json(
                run_dir / "idea_formalizer_audit_records.json",
                {
                    "schema_version": "lab_pipeline_adapter_toolcontext_audit_v1",
                    "adapter_run_id": adapter_run_id,
                    "records": audit_records,
                    "non_authority_assertions": dict(NON_AUTHORITY_ASSERTIONS),
                },
            )
            invoked.append(
                "tools.research_agents.idea_formalizer_agent.IdeaFormalizerAgent.run"
            )
            status = (
                "adapter_complete"
                if formalizer_result.get("status") in {"accepted", "needs_data"}
                else "adapter_blocked"
            )
            reason = (
                "formalizer_accepted_or_needs_data"
                if status == "adapter_complete"
                else "formalizer_rejected"
            )
            trace.append(
                _stage_event(
                    adapter=formalizer_adapter,
                    status=status,
                    reason_code=reason,
                    detail=f"Formalizer returned status={formalizer_result.get('status')}.",
                    input_paths=[artifacts["pipeline_adapter_request"]],
                    output_paths=formalizer_paths,
                    hashes=_hash_paths(formalizer_paths),
                )
            )
            if status != "adapter_complete":
                gaps.append(
                    {
                        "adapter_id": formalizer_adapter.adapter_id,
                        "stage": formalizer_adapter.stage,
                        "status": status,
                        "blocker_reason": "; ".join(
                            str(item) for item in formalizer_result.get("rejection_reasons", [])
                        )
                        or "formalizer did not accept the operator idea",
                        "future_option": "Operator may revise the source idea under a later invocation.",
                    }
                )
        except Exception as exc:
            trace.append(
                _stage_event(
                    adapter=formalizer_adapter,
                    status="adapter_failed",
                    reason_code=exc.__class__.__name__,
                    detail=str(exc),
                    input_paths=[artifacts["pipeline_adapter_request"]],
                )
            )
            gaps.append(
                {
                    "adapter_id": formalizer_adapter.adapter_id,
                    "stage": formalizer_adapter.stage,
                    "status": "adapter_failed",
                    "blocker_reason": f"{exc.__class__.__name__}: {exc}",
                    "future_option": "Investigate formalizer failure without widening adapter authority.",
                }
            )

        readiness_adapter = registry_by_stage["availability_readiness_classification"]
        try:
            readiness = build_readiness_projection(repo_root=REPO_ROOT)
            readiness_path = write_json(run_dir / "readiness_projection.json", readiness)
            artifacts["readiness_projection"] = readiness_path
            invoked.append("tools.lab_readiness.readiness.build_readiness_projection")
            trace.append(
                _stage_event(
                    adapter=readiness_adapter,
                    status="adapter_complete",
                    reason_code="readiness_projection_built",
                    detail="Read-only lab readiness projection captured under adapter packet.",
                    input_paths=[],
                    output_paths=[readiness_path],
                    hashes=_hash_paths([readiness_path]),
                )
            )
        except Exception as exc:
            trace.append(
                _stage_event(
                    adapter=readiness_adapter,
                    status="adapter_failed",
                    reason_code=exc.__class__.__name__,
                    detail=str(exc),
                )
            )
            gaps.append(
                {
                    "adapter_id": readiness_adapter.adapter_id,
                    "stage": readiness_adapter.stage,
                    "status": "adapter_failed",
                    "blocker_reason": f"{exc.__class__.__name__}: {exc}",
                    "future_option": "Fix readiness projection separately if repo truth changed.",
                }
            )

        for adapter in registry[2:]:
            gap = {
                "adapter_id": adapter.adapter_id,
                "stage": adapter.stage,
                "status": "blocked_unsafe_to_adapt",
                "blocker_reason": str(adapter.blocker_reason),
                "source_module": adapter.source_module,
                "source_callable": adapter.source_callable,
                "input_artifact_contract": adapter.input_artifact_contract,
                "future_option": (
                    "Authorize a later narrow adapter package or gate action that supplies "
                    "the exact missing approval/input contract."
                ),
            }
            gaps.append(gap)
            trace.append(
                _stage_event(
                    adapter=adapter,
                    status="blocked_unsafe_to_adapt",
                    reason_code="missing_safe_input_or_distinct_approval_contract",
                    detail=str(adapter.blocker_reason),
                )
            )

        final_status = "complete_with_gaps" if gaps else "complete_without_gaps"

    if final_status not in ADAPTER_RUN_STATUSES:
        raise AdapterFlowError(f"unknown adapter run status: {final_status}")

    gap_register = {
        "schema_version": "lab_pipeline_adapter_gap_register_v1",
        "adapter_run_id": adapter_run_id,
        "gap_count": len(gaps),
        "gaps": gaps,
        "non_authority_assertions": dict(NON_AUTHORITY_ASSERTIONS),
    }
    artifacts["adapter_gap_register"] = write_json(
        run_dir / "adapter_gap_register.json", gap_register
    )
    state = {
        "schema_version": "lab_pipeline_adapter_state_v1",
        "adapter_contract_version": ADAPTER_CONTRACT_VERSION,
        "adapter_run_id": adapter_run_id,
        "pipeline_run_id": pipeline_run_id,
        "adapter_status": final_status,
        "gap_count": len(gaps),
        "invoked_real_modules": invoked,
        "approval_consumed": approval is not None,
        "approval_errors": list(approval_errors),
        "registry_closed": True,
        "non_authority_assertions": dict(NON_AUTHORITY_ASSERTIONS),
    }
    artifacts["pipeline_adapter_state"] = write_json(
        run_dir / "pipeline_adapter_state.json", state
    )
    artifacts["adapter_trace"] = write_json(
        run_dir / "adapter_trace.json",
        {
            "schema_version": "lab_pipeline_adapter_trace_v1",
            "adapter_run_id": adapter_run_id,
            "events": trace,
            "no_winner_only_or_hidden_failure_status": True,
            "non_authority_assertions": dict(NON_AUTHORITY_ASSERTIONS),
        },
    )
    artifacts["non_authority_assertions"] = write_json(
        run_dir / "non_authority_assertions.json",
        {
            "schema_version": "lab_pipeline_adapter_non_authority_assertions_v1",
            "adapter_run_id": adapter_run_id,
            **NON_AUTHORITY_ASSERTIONS,
        },
    )
    artifacts["operator_review_packet"] = write_text(
        run_dir / "operator_review_packet.md",
        _review_packet_markdown(state=state, trace=trace, gaps=gaps, artifacts=artifacts),
    )
    index_payload = {
        "schema_version": "lab_pipeline_adapter_artifact_index_v1",
        "adapter_run_id": adapter_run_id,
        "artifact_count": len(artifacts) + 1,
        "artifacts": {
            name: {
                "path": path,
                "sha256": file_sha256(REPO_ROOT / path) if (REPO_ROOT / path).exists() else None,
            }
            for name, path in sorted(artifacts.items())
        },
        "self_entry_note": "adapter_artifact_index self hash omitted to avoid recursive hash mutation",
        "non_authority_assertions": dict(NON_AUTHORITY_ASSERTIONS),
    }
    artifacts["adapter_artifact_index"] = write_json(
        run_dir / "adapter_artifact_index.json", index_payload
    )
    return AdapterFlowResult(
        adapter_run_id=adapter_run_id,
        adapter_status=final_status,
        output_dir=run_dir,
        artifact_paths=dict(artifacts),
        gap_count=len(gaps),
        invoked_real_modules=tuple(invoked),
    )
