"""Closed adapter contract for the lab pipeline adapter-backed flow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final


ADAPTER_CONTRACT_VERSION: Final = "lab_pipeline_adapter_contract_v1"
RUNNER_ADAPTER_PACKAGE_ID: Final = "WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04"

ADAPTER_STAGE_STATUSES: Final[tuple[str, ...]] = (
    "adapter_complete",
    "adapter_blocked",
    "adapter_skipped",
    "adapter_failed",
    "awaiting_prereg_approval",
    "blocked_unsafe_to_adapt",
)

ADAPTER_RUN_STATUSES: Final[tuple[str, ...]] = (
    "awaiting_prereg_approval",
    "complete_with_gaps",
    "complete_without_gaps",
    "adapter_failed",
)

ADAPTER_IMPLEMENTATION_STATUSES: Final[tuple[str, ...]] = (
    "implemented",
    "blocked",
    "deferred",
)

NON_AUTHORITY_ASSERTIONS: Final[dict[str, bool]] = {
    "canonical_evidence_written": False,
    "candidate_lifecycle_written": False,
    "candidate_admission": False,
    "crossing": False,
    "promotion_or_readiness": False,
    "paper_live_runtime_contact": False,
    "scheduler_autonomous_dispatch": False,
    "notification_firing": False,
    "provider_api_credential_use": False,
    "dependency_config_data_acquisition": False,
    "protected_path_touch": False,
}


@dataclass(frozen=True)
class AdapterAuthorityFlags:
    """Authority posture for one adapter record."""

    noncanonical_offline_research: bool
    scratch_only: bool
    read_only: bool
    writes_canonical_evidence: bool = False
    writes_candidate_lifecycle: bool = False
    admits_candidate: bool = False
    executes_crossing: bool = False
    authorizes_promotion_or_readiness: bool = False
    contacts_paper_live_runtime: bool = False
    uses_scheduler_or_autonomy: bool = False
    fires_notifications: bool = False
    uses_provider_api_or_credentials: bool = False
    mutates_dependencies_configs_or_data: bool = False
    touches_protected_paths: bool = False

    def to_dict(self) -> dict[str, bool]:
        return {
            "noncanonical_offline_research": self.noncanonical_offline_research,
            "scratch_only": self.scratch_only,
            "read_only": self.read_only,
            "writes_canonical_evidence": self.writes_canonical_evidence,
            "writes_candidate_lifecycle": self.writes_candidate_lifecycle,
            "admits_candidate": self.admits_candidate,
            "executes_crossing": self.executes_crossing,
            "authorizes_promotion_or_readiness": self.authorizes_promotion_or_readiness,
            "contacts_paper_live_runtime": self.contacts_paper_live_runtime,
            "uses_scheduler_or_autonomy": self.uses_scheduler_or_autonomy,
            "fires_notifications": self.fires_notifications,
            "uses_provider_api_or_credentials": self.uses_provider_api_or_credentials,
            "mutates_dependencies_configs_or_data": self.mutates_dependencies_configs_or_data,
            "touches_protected_paths": self.touches_protected_paths,
        }


@dataclass(frozen=True)
class AdapterRecord:
    adapter_id: str
    stage: str
    source_module: str
    source_callable: str
    cli_path: str | None
    input_artifact_contract: str
    output_artifact_contract: str
    scratch_output_root: str
    authority_flags: AdapterAuthorityFlags
    implementation_status: str
    blocker_reason: str | None = None

    def __post_init__(self) -> None:
        if self.implementation_status not in ADAPTER_IMPLEMENTATION_STATUSES:
            raise ValueError(f"unknown adapter implementation status: {self.implementation_status}")
        flags = self.authority_flags.to_dict()
        forbidden_true = [
            key
            for key, value in flags.items()
            if value is True
            and key
            not in {"noncanonical_offline_research", "scratch_only", "read_only"}
        ]
        if forbidden_true:
            raise ValueError(f"adapter grants forbidden authority: {forbidden_true}")
        if self.implementation_status in {"blocked", "deferred"} and not self.blocker_reason:
            raise ValueError("blocked/deferred adapter records require a blocker reason")

    def to_dict(self) -> dict[str, Any]:
        return {
            "adapter_id": self.adapter_id,
            "stage": self.stage,
            "source_module": self.source_module,
            "source_callable": self.source_callable,
            "cli_path": self.cli_path,
            "input_artifact_contract": self.input_artifact_contract,
            "output_artifact_contract": self.output_artifact_contract,
            "scratch_output_root": self.scratch_output_root,
            "authority_flags": self.authority_flags.to_dict(),
            "implementation_status": self.implementation_status,
            "blocker_reason": self.blocker_reason,
        }


def build_adapter_registry(package_id: str) -> tuple[AdapterRecord, ...]:
    """Return the deterministic closed registry for pipeline adapter stages."""

    scratch = f"scratch/{package_id}"
    runner_adapter_implemented = package_id == RUNNER_ADAPTER_PACKAGE_ID
    return (
        AdapterRecord(
            adapter_id="adapter.idea_formalizer.fake_offline.v1",
            stage="idea_formalization",
            source_module="tools.research_agents.idea_formalizer_agent",
            source_callable="IdeaFormalizerAgent.run",
            cli_path="python -m tools.research_agents.idea_formalizer_agent",
            input_artifact_contract="lab_pipeline_request_v1.source_idea/symbol/timeframe",
            output_artifact_contract="agent_formalized_idea_v1 under package scratch",
            scratch_output_root=f"{scratch}/outputs",
            authority_flags=AdapterAuthorityFlags(
                noncanonical_offline_research=True,
                scratch_only=True,
                read_only=False,
            ),
            implementation_status="implemented",
        ),
        AdapterRecord(
            adapter_id="adapter.lab_readiness.projection.v1",
            stage="availability_readiness_classification",
            source_module="tools.lab_readiness.readiness",
            source_callable="build_readiness_projection",
            cli_path="python -m tools.lab_readiness.run --json",
            input_artifact_contract="current committed repo metadata only",
            output_artifact_contract="lab_data_sim_readiness_v1 snapshot under adapter packet",
            scratch_output_root=f"{scratch}/outputs",
            authority_flags=AdapterAuthorityFlags(
                noncanonical_offline_research=True,
                scratch_only=True,
                read_only=True,
            ),
            implementation_status="implemented",
        ),
        AdapterRecord(
            adapter_id="adapter.formalizer_runner_bridge.v1",
            stage="bridge_spec_variant_sweep_preparation",
            source_module="tools.research_agents.formalizer_runner_bridge",
            source_callable="FormalizerRunnerBridge.run",
            cli_path=None,
            input_artifact_contract=(
                "accepted formalizer output plus separate "
                "noncanonical_scratch_runner_bridge_only approval marker"
            ),
            output_artifact_contract="formalizer_runner_bridge_human_review_packet_v1",
            scratch_output_root=f"{scratch}/outputs",
            authority_flags=AdapterAuthorityFlags(
                noncanonical_offline_research=True,
                scratch_only=True,
                read_only=False,
            ),
            implementation_status="blocked",
            blocker_reason=(
                "Existing bridge cannot be safely invoked from the lab pipeline package: "
                "it hard-codes a different ToolContext WP allowlist, source formalizer "
                "scratch prefixes, bridge output root, and legacy operator approval shape. "
                "Changing those contracts is outside this package; pipeline prereg or "
                "new bridge approval cannot be substituted safely."
            ),
        ),
        AdapterRecord(
            adapter_id="adapter.offline_runner.noncanonical.v1",
            stage="noncanonical_offline_runner_execution",
            source_module="tools.research_runner.run_offline_sweep",
            source_callable="run_offline_sweep",
            cli_path="python -m tools.research_runner.run_offline_sweep",
            input_artifact_contract="validated Strategy Spec, Variant Manifest, Sweep Plan, and data path",
            output_artifact_contract="in-memory or scratch Result Population-shaped payload",
            scratch_output_root=f"{scratch}/outputs",
            authority_flags=AdapterAuthorityFlags(
                noncanonical_offline_research=True,
                scratch_only=True,
                read_only=False,
            ),
            implementation_status="implemented" if runner_adapter_implemented else "blocked",
            blocker_reason=(
                None
                if runner_adapter_implemented
                else (
                    "No safe bridge-produced validated Strategy Spec / Variant Manifest / "
                    "Sweep Plan input set is available without the separate bridge approval."
                )
            ),
        ),
        AdapterRecord(
            adapter_id="adapter.wfo_oos_gate.v1",
            stage="wfo_oos_gate_review",
            source_module="tools.oos_gate.evaluate",
            source_callable="validate_oos_gate_artifact / evaluate_candidate_review_gate",
            cli_path="python -m tools.oos_gate.evaluate",
            input_artifact_contract="existing OOS gate artifact plus candidate-review input",
            output_artifact_contract="oos_candidate_gate_evaluation.v1",
            scratch_output_root=f"{scratch}/outputs",
            authority_flags=AdapterAuthorityFlags(
                noncanonical_offline_research=True,
                scratch_only=True,
                read_only=True,
            ),
            implementation_status="blocked",
            blocker_reason=(
                "No safe upstream walk-forward/OOS gate artifact exists in this "
                "adapter packet; fabricating a gate pass is forbidden."
            ),
        ),
        AdapterRecord(
            adapter_id="adapter.robustness_diagnostician.v1",
            stage="robustness_diagnostics",
            source_module="tools.research_agents.robustness_diagnostician_agent",
            source_callable="RobustnessDiagnosticianAgent.run",
            cli_path=None,
            input_artifact_contract=(
                "bridge review packet, bridge Result Population artifact, denominator "
                "ledger, and separate robustness approval marker"
            ),
            output_artifact_contract="robustness_diagnostician_review_packet_v1",
            scratch_output_root=f"{scratch}/outputs",
            authority_flags=AdapterAuthorityFlags(
                noncanonical_offline_research=True,
                scratch_only=True,
                read_only=False,
            ),
            implementation_status="blocked",
            blocker_reason=(
                "Requires bridge outputs and a separate robustness approval marker; "
                "neither can be safely fabricated or replaced by pipeline prereg approval."
            ),
        ),
        AdapterRecord(
            adapter_id="adapter.candidate_review_packet.v1",
            stage="candidate_review_packet_preparation",
            source_module="tools.research_agents.candidate_review_packet_agent",
            source_callable="CandidateReviewPacketAgent.run",
            cli_path=None,
            input_artifact_contract=(
                "formalizer, bridge, denominator, robustness, and separate candidate-review "
                "approval marker"
            ),
            output_artifact_contract="candidate_review_packet_v1 / markdown",
            scratch_output_root=f"{scratch}/outputs",
            authority_flags=AdapterAuthorityFlags(
                noncanonical_offline_research=True,
                scratch_only=True,
                read_only=False,
            ),
            implementation_status="blocked",
            blocker_reason=(
                "Requires complete bridge and robustness packets plus its own "
                "candidate-review approval marker; a human-review packet cannot be "
                "safely synthesized from missing upstream evidence."
            ),
        ),
    )
