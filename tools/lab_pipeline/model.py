"""Deterministic state vocabulary for the non-canonical lab pipeline.

This model is local to ``tools.lab_pipeline``. It does not change the canonical
read-only coordinator vocabulary in ``tools.lab_state``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final


SCHEMA_VERSION: Final = "lab_pipeline_state_v1"
REQUEST_SCHEMA_VERSION: Final = "lab_pipeline_request_v1"
APPROVAL_SCHEMA_VERSION: Final = "lab_pipeline_prereg_approval_v1"

PIPELINE_STAGES: Final[tuple[str, ...]] = (
    "request_loaded",
    "idea_formalized",
    "availability_checked",
    "prereg_packet_prepared",
    "awaiting_prereg_approval",
    "approved_for_noncanonical_execution",
    "noncanonical_execution_running",
    "noncanonical_execution_complete",
    "gate_review_complete",
    "robustness_review_complete",
    "candidate_review_packet_prepared",
    "complete",
    "blocked",
)

STAGE_STATUSES: Final[tuple[str, ...]] = (
    "not_started",
    "complete",
    "awaiting_approval",
    "blocked",
)

LOCKED_TIMEFRAMES: Final[tuple[str, ...]] = ("15m", "30m", "1h", "4h", "1d")

APPROVAL_SCOPE: Final = "noncanonical_offline_research_execution_only"
APPROVAL_STATEMENT: Final = (
    "Authorizes only non-canonical offline research execution for the exact "
    "frozen preregistration packet content."
)

NON_AUTHORITY_FLAGS: Final[dict[str, bool]] = {
    "noncanonical_only": True,
    "scratch_only": True,
    "offline_only": True,
    "writes_canonical_evidence": False,
    "writes_candidate_lifecycle": False,
    "executes_canonical_crossing": False,
    "authorizes_promotion_or_readiness": False,
    "contacts_paper_live_runtime": False,
    "uses_scheduler_or_autonomy": False,
    "fires_notifications": False,
    "uses_provider_api_or_credentials": False,
    "human_review_required_for_prereg": True,
    "separate_authorization_required_for_canonical_or_runtime": True,
}

FORBIDDEN_AUTHORITY_CODES: Final[tuple[str, ...]] = (
    "canonical_result_population_write",
    "candidate_admission_or_lifecycle_write",
    "canonical_crossing",
    "promotion_or_readiness",
    "paper_live_runtime_contact",
    "scheduler_or_autonomous_dispatch",
    "notification_firing",
    "provider_api_or_credential_use",
)


def is_valid_stage(stage: str) -> bool:
    return stage in PIPELINE_STAGES


def is_valid_status(status: str) -> bool:
    return status in STAGE_STATUSES


@dataclass(frozen=True)
class StageRecord:
    stage: str
    status: str = "not_started"
    detail: str = ""
    artifact_refs: tuple[str, ...] = ()
    blocked_reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not is_valid_stage(self.stage):
            raise ValueError(f"unknown pipeline stage: {self.stage}")
        if not is_valid_status(self.status):
            raise ValueError(f"unknown pipeline stage status: {self.status}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "status": self.status,
            "detail": self.detail,
            "artifact_refs": list(self.artifact_refs),
            "blocked_reasons": list(self.blocked_reasons),
        }


@dataclass(frozen=True)
class PipelineTraceEvent:
    stage: str
    status: str
    detail: str = ""

    def to_dict(self) -> dict[str, str]:
        return {"stage": self.stage, "status": self.status, "detail": self.detail}


@dataclass(frozen=True)
class PipelineState:
    pipeline_run_id: str
    request_id: str
    current_stage: str
    pipeline_status: str
    source_idea: str
    symbol: str
    timeframe: str
    requested_by: str
    created_at_policy: str
    deterministic_timestamp_utc: str
    stage_statuses: tuple[StageRecord, ...]
    artifact_refs: tuple[str, ...] = ()
    approval_requirements: dict[str, Any] = field(default_factory=dict)
    blocked_reasons: tuple[str, ...] = ()
    non_authority_flags: dict[str, bool] = field(default_factory=lambda: dict(NON_AUTHORITY_FLAGS))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "pipeline_run_id": self.pipeline_run_id,
            "request_id": self.request_id,
            "current_stage": self.current_stage,
            "pipeline_status": self.pipeline_status,
            "source_idea": self.source_idea,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "requested_by": self.requested_by,
            "created_at_policy": self.created_at_policy,
            "deterministic_timestamp_utc": self.deterministic_timestamp_utc,
            "stage_statuses": [stage.to_dict() for stage in self.stage_statuses],
            "artifact_refs": list(self.artifact_refs),
            "approval_requirements": self.approval_requirements,
            "blocked_reasons": list(self.blocked_reasons),
            "non_authority_flags": self.non_authority_flags,
        }
