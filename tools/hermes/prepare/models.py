"""Strict contracts for inert Hermes H2.5 prepared payloads."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from tools.hermes.proposals.models import (
    AuthorityClass,
    EvidenceAnchor,
    EvidenceRef,
    FactClaim,
    ProposalType,
    RepoSha,
    Sha256,
    ShortText,
    Text,
)

PreparedId = Annotated[
    str,
    Field(pattern=r"^HERMES-PREP-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{16}$"),
]
SourceProposalId = Annotated[
    str,
    Field(pattern=r"^HERMES-PROP-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{16}$"),
]


class StrictPreparedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class PreparedPayloadType(str, Enum):
    STRATEGY_LAB = "StrategyLabPreparedPayload"
    SEARCH_GOVERNOR_CAMPAIGN = "SearchGovernorCampaignPreparedPayload"
    CODEX_WORK_PACKAGE = "CodexWorkPackagePreparedPayload"
    PREFECT_WORKFLOW = "PrefectWorkflowPreparedPayload"
    BOUNDED_DIAGNOSTIC = "BoundedDiagnosticPreparedPayload"
    DATA_HYDRATION = "DataHydrationPreparedPayload"
    DEPENDENCY_MAINTENANCE = "DependencyMaintenancePreparedPayload"


class FutureActionType(str, Enum):
    STRATEGY_LAB_DRAFT = "future_strategy_lab_experiment_or_spec_draft"
    SEARCH_CAMPAIGN_DRAFT = "future_search_governor_campaign_draft"
    CODEX_WORK_PACKAGE_DRAFT = "future_codex_work_package_draft"
    PREFECT_WORKFLOW_DRAFT = "future_prefect_workflow_definition_draft"
    BOUNDED_DIAGNOSTIC_DRAFT = "future_read_only_bounded_diagnostic_draft"
    DATA_HYDRATION_DRAFT = "future_data_hydration_plan_draft"
    DEPENDENCY_MAINTENANCE_DRAFT = "future_dependency_maintenance_plan_draft"


class ExactBound(StrictPreparedModel):
    amount: Annotated[int, Field(ge=0, le=10**12)]
    unit: Annotated[str, Field(min_length=1, max_length=80)]
    hard_limit: Literal[True]


class TimeoutBound(StrictPreparedModel):
    seconds: Annotated[int, Field(ge=1, le=31_536_000)]
    hard_limit: Literal[True]


class StrategyLabBody(StrictPreparedModel):
    future_lab_only_experiment_or_spec_draft: Text
    parameters_or_search_space_draft: Annotated[tuple[Text, ...], Field(min_length=1)]
    data_or_evidence_inputs: Annotated[tuple[EvidenceRef, ...], Field(min_length=1)]
    falsification_criteria: Annotated[tuple[Text, ...], Field(min_length=1)]
    candidate_or_promotion_authority: Literal[False]
    go_authority: Literal[False]


class SearchGovernorCampaignBody(StrictPreparedModel):
    intended_future_campaign_purpose: Text
    intended_surface: Literal["tools/research_search"]
    legal_search_intent: Text
    seed: Annotated[int, Field(ge=0, le=2**63 - 1)]
    objective: Text
    constraints: Annotated[tuple[Text, ...], Field(min_length=1)]
    holdout_access: Literal[False]
    governor_call: Literal[False]
    winner_semantics: Literal[False]


class CodexWorkPackageBody(StrictPreparedModel):
    objective: Text
    why_now: Text
    allowed_scope: Annotated[tuple[Text, ...], Field(min_length=1)]
    forbidden_scope: Annotated[tuple[Text, ...], Field(min_length=1)]
    expected_files_or_targets: Annotated[tuple[ShortText, ...], Field(min_length=1)]
    dependencies: tuple[ShortText, ...]
    model_recommendation: ShortText
    reasoning_recommendation: Literal["LOW", "MEDIUM", "HIGH", "XHIGH"]
    explicitly_non_protected_research_tooling: bool
    task_creation: Literal[False]
    branch_creation: Literal[False]
    pull_request_creation: Literal[False]


class PrefectTaskDraft(StrictPreparedModel):
    task_name: ShortText
    future_behavior: Text
    inputs: tuple[ShortText, ...]
    outputs: tuple[ShortText, ...]


class PrefectWorkflowBody(StrictPreparedModel):
    future_workflow_definition: Text
    tasks: Annotated[tuple[PrefectTaskDraft, ...], Field(min_length=1)]
    workflow_inputs: tuple[ShortText, ...]
    workflow_outputs: Annotated[tuple[ShortText, ...], Field(min_length=1)]
    retry_expectations: Text
    timeout_expectations: Text
    idempotency_expectations: Text
    evidence_or_output_contract: Text
    prefect_call: Literal[False]
    deployment_creation: Literal[False]
    workflow_run: Literal[False]


class BoundedDiagnosticBody(StrictPreparedModel):
    diagnostic_question: Text
    read_only_targets: Annotated[tuple[ShortText, ...], Field(min_length=1)]
    allowed_diagnostic_concept: Text
    diagnostic_outputs: Annotated[tuple[ShortText, ...], Field(min_length=1)]
    execution: Literal[False]


class DataHydrationBody(StrictPreparedModel):
    source: Text
    dataset: Text
    exact_range: Text
    storage_estimate: ShortText
    network_estimate: ShortText
    provenance_rules: Annotated[tuple[Text, ...], Field(min_length=1)]
    checksum_rules: Annotated[tuple[Text, ...], Field(min_length=1)]
    causality_rules: Annotated[tuple[Text, ...], Field(min_length=1)]
    availability_rules: Annotated[tuple[Text, ...], Field(min_length=1)]
    network_access: Literal[False]
    hydration: Literal[False]


class DependencyMaintenanceBody(StrictPreparedModel):
    repo_evidenced_current_dependency: ShortText
    proposed_target_or_unknown: ShortText
    compatibility_plan: Annotated[tuple[Text, ...], Field(min_length=1)]
    lock_update_plan: Annotated[tuple[Text, ...], Field(min_length=1)]
    rollback_plan: Annotated[tuple[Text, ...], Field(min_length=1)]
    watch_advisory_context: tuple[Text, ...]
    install_or_update: Literal[False]
    transient_watch_fact: Literal[False]


_FORBIDDEN_PARAMETER_KEYS = frozenset(
    {
        "approval_token",
        "approval_token_id",
        "broker_endpoint",
        "broker_url",
        "dispatch_target",
        "automatic_dispatch_target",
        "already_approved",
        "authorized",
        "execute_now",
    }
)


def _validate_parameter_value(value: Any, *, depth: int = 0) -> None:
    if depth > 20:
        raise ValueError("parameter nesting exceeds 20 levels")
    if isinstance(value, float):
        raise TypeError("floating-point parameters are forbidden; use an exact string")
    if value is None or isinstance(value, (str, int, bool)):
        return
    if isinstance(value, dict):
        if len(value) > 200:
            raise ValueError("parameter object exceeds 200 keys")
        for key, child in value.items():
            if not isinstance(key, str):
                raise TypeError("parameter keys must be strings")
            if key.casefold().replace("-", "_") in _FORBIDDEN_PARAMETER_KEYS:
                raise ValueError(f"authority-bearing parameter is forbidden: {key}")
            _validate_parameter_value(child, depth=depth + 1)
        return
    if isinstance(value, (list, tuple)):
        if len(value) > 500:
            raise ValueError("parameter sequence exceeds 500 items")
        for child in value:
            _validate_parameter_value(child, depth=depth + 1)
        return
    raise ValueError(f"unsupported parameter value: {type(value).__name__}")


class PreparedPayloadBase(StrictPreparedModel):
    schema_version: Literal["hermes_prepared_payload_v1"]
    prepared_payload_type: PreparedPayloadType
    repo_sha: RepoSha
    source_session_id: Annotated[
        str,
        Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"),
    ]
    source_proposal_id: SourceProposalId
    source_proposal_type: ProposalType
    source_proposal_content_sha256: Sha256
    source_proposal_repo_sha: RepoSha
    source_authority_class: AuthorityClass
    evidence_refs: Annotated[tuple[EvidenceRef, ...], Field(min_length=1, max_length=50)]
    evidence_anchors: Annotated[tuple[EvidenceAnchor, ...], Field(min_length=1, max_length=50)]
    facts: Annotated[tuple[FactClaim, ...], Field(min_length=1, max_length=100)]
    inferences: tuple[Text, ...]
    open_questions: tuple[Text, ...]
    future_action_type: FutureActionType
    target: Text
    scope: Text
    parameters: dict[str, Any]
    count_or_quantity_bound: ExactBound | None
    budget_bound: ExactBound
    timeout: TimeoutBound
    expected_outputs: Annotated[tuple[Text, ...], Field(min_length=1, max_length=100)]
    validation_plan: Annotated[tuple[Text, ...], Field(min_length=1, max_length=100)]
    rollback_or_stop_conditions: Annotated[tuple[Text, ...], Field(min_length=1, max_length=100)]
    authority_class: AuthorityClass
    human_review_required: Literal[True]
    not_authority: Literal[True]
    automatic_consumers: tuple[()] = ()
    self_approval: Literal[False]
    direct_execution: Literal[False]
    standing_authority: Literal[False]
    approval_token_eligible: Literal[False]
    broker_eligible: Literal[False]
    dispatch_eligible: Literal[False]
    permanent_non_executable: Literal[True] | None = None
    protected_human_gate_only: Literal[True] | None = None

    @model_validator(mode="after")
    def validate_base_contract(self) -> PreparedPayloadBase:
        if self.authority_class is not self.source_authority_class:
            raise ValueError("authority_class must exactly preserve source_authority_class")
        if self.authority_class is AuthorityClass.A0:
            if self.permanent_non_executable is not True:
                raise ValueError("A0 requires permanent_non_executable=true")
            if self.protected_human_gate_only is not True:
                raise ValueError("A0 requires protected_human_gate_only=true")
        elif (
            self.permanent_non_executable is not None or self.protected_human_gate_only is not None
        ):
            raise ValueError("A0-only permanence fields must be absent for A1/A2")

        refs = tuple(self.evidence_refs)
        anchor_refs = tuple(anchor.ref for anchor in self.evidence_anchors)
        if len(refs) != len(set(refs)) or len(anchor_refs) != len(set(anchor_refs)):
            raise ValueError("evidence references must be unique")
        if refs != anchor_refs:
            raise ValueError("evidence_refs must exactly match evidence_anchors in order")
        if any(anchor.repo_sha != self.repo_sha for anchor in self.evidence_anchors):
            raise ValueError("every prepared evidence anchor must bind the prepared repo SHA")
        known_refs = set(refs)
        for fact in self.facts:
            if not set(fact.evidence_refs).issubset(known_refs):
                raise ValueError("every FACT must cite an anchored evidence reference")
        _validate_parameter_value(self.parameters)
        return self


class StrategyLabPreparedPayload(PreparedPayloadBase):
    prepared_payload_type: Literal[PreparedPayloadType.STRATEGY_LAB]
    future_action_type: Literal[FutureActionType.STRATEGY_LAB_DRAFT]
    count_or_quantity_bound: ExactBound
    body: StrategyLabBody


class SearchGovernorCampaignPreparedPayload(PreparedPayloadBase):
    prepared_payload_type: Literal[PreparedPayloadType.SEARCH_GOVERNOR_CAMPAIGN]
    future_action_type: Literal[FutureActionType.SEARCH_CAMPAIGN_DRAFT]
    count_or_quantity_bound: ExactBound
    body: SearchGovernorCampaignBody


class CodexWorkPackagePreparedPayload(PreparedPayloadBase):
    prepared_payload_type: Literal[PreparedPayloadType.CODEX_WORK_PACKAGE]
    future_action_type: Literal[FutureActionType.CODEX_WORK_PACKAGE_DRAFT]
    body: CodexWorkPackageBody


class PrefectWorkflowPreparedPayload(PreparedPayloadBase):
    prepared_payload_type: Literal[PreparedPayloadType.PREFECT_WORKFLOW]
    future_action_type: Literal[FutureActionType.PREFECT_WORKFLOW_DRAFT]
    body: PrefectWorkflowBody


class BoundedDiagnosticPreparedPayload(PreparedPayloadBase):
    prepared_payload_type: Literal[PreparedPayloadType.BOUNDED_DIAGNOSTIC]
    future_action_type: Literal[FutureActionType.BOUNDED_DIAGNOSTIC_DRAFT]
    body: BoundedDiagnosticBody


class DataHydrationPreparedPayload(PreparedPayloadBase):
    prepared_payload_type: Literal[PreparedPayloadType.DATA_HYDRATION]
    future_action_type: Literal[FutureActionType.DATA_HYDRATION_DRAFT]
    count_or_quantity_bound: ExactBound
    body: DataHydrationBody


class DependencyMaintenancePreparedPayload(PreparedPayloadBase):
    prepared_payload_type: Literal[PreparedPayloadType.DEPENDENCY_MAINTENANCE]
    future_action_type: Literal[FutureActionType.DEPENDENCY_MAINTENANCE_DRAFT]
    body: DependencyMaintenanceBody


PreparedPayload = Annotated[
    StrategyLabPreparedPayload
    | SearchGovernorCampaignPreparedPayload
    | CodexWorkPackagePreparedPayload
    | PrefectWorkflowPreparedPayload
    | BoundedDiagnosticPreparedPayload
    | DataHydrationPreparedPayload
    | DependencyMaintenancePreparedPayload,
    Field(discriminator="prepared_payload_type"),
]

PREPARED_PAYLOAD_TYPES = {
    PreparedPayloadType.STRATEGY_LAB: StrategyLabPreparedPayload,
    PreparedPayloadType.SEARCH_GOVERNOR_CAMPAIGN: SearchGovernorCampaignPreparedPayload,
    PreparedPayloadType.CODEX_WORK_PACKAGE: CodexWorkPackagePreparedPayload,
    PreparedPayloadType.PREFECT_WORKFLOW: PrefectWorkflowPreparedPayload,
    PreparedPayloadType.BOUNDED_DIAGNOSTIC: BoundedDiagnosticPreparedPayload,
    PreparedPayloadType.DATA_HYDRATION: DataHydrationPreparedPayload,
    PreparedPayloadType.DEPENDENCY_MAINTENANCE: DependencyMaintenancePreparedPayload,
}
