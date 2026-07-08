"""Closed vocabulary for the read-only lab readiness display."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SCHEMA_VERSION = "lab_data_sim_readiness_v1"

READINESS_STATUSES: tuple[str, ...] = (
    "testable_now_with_current_public_history",
    "testable_now_with_current_caveats",
    "needs_local_full_history_materialization",
    "needs_vendor_or_captured_history",
    "needs_runner_or_compiler_support",
    "needs_simulator_realism_upgrade",
    "go_gated_or_paper_phase_only",
    "protected_or_out_of_scope",
    "unknown_needs_review",
)

NON_AUTHORITY_FLAGS: tuple[str, ...] = (
    "read_only_display_only",
    "not_data_acquisition_authority",
    "not_vendor_or_api_authority",
    "not_runner_or_compiler_change_authority",
    "not_simulator_change_authority",
    "not_strategy_execution_authority",
    "not_candidate_authority",
    "not_crossing_or_promotion_authority",
    "not_paper_live_runtime_authority",
    "not_provider_api_or_credential_authority",
    "not_scheduler_or_autonomy_authority",
)


@dataclass(frozen=True)
class ReadinessItem:
    """One deterministic operator-facing readiness row."""

    subject_id: str
    label: str
    feature_or_family: str
    status: str
    reason_code: str
    required_source_evidence: list[str]
    current_repo_support: list[str]
    blocker_detail: str
    next_prerequisite_category: str
    non_authority_flags: list[str] = field(
        default_factory=lambda: list(NON_AUTHORITY_FLAGS)
    )

    def to_dict(self) -> dict[str, Any]:
        if self.status not in READINESS_STATUSES:
            raise ValueError(f"unknown readiness status: {self.status}")
        return {
            "subject_id": self.subject_id,
            "label": self.label,
            "feature_or_family": self.feature_or_family,
            "status": self.status,
            "reason_code": self.reason_code,
            "required_source_evidence": list(self.required_source_evidence),
            "current_repo_support": list(self.current_repo_support),
            "blocker_detail": self.blocker_detail,
            "next_prerequisite_category": self.next_prerequisite_category,
            "non_authority_flags": list(self.non_authority_flags),
        }


NON_AUTHORITY_DECLARATION = {
    "read_only_display_only": True,
    "writes_only_with_out_dir": True,
    "runs_strategy": False,
    "acquires_data": False,
    "contacts_network_or_provider_api": False,
    "uses_credentials": False,
    "changes_runner_or_compiler": False,
    "changes_simulator": False,
    "creates_candidate_or_result_population": False,
    "authorizes_crossing_promotion_or_readiness": False,
    "authorizes_paper_live_runtime": False,
    "authorizes_scheduler_or_autonomy": False,
}
