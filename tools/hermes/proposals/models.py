"""Strict machine-validatable contracts for inert Hermes H2 proposals."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Text = Annotated[str, Field(min_length=1, max_length=10_000)]
ShortText = Annotated[str, Field(min_length=1, max_length=500)]
RepoSha = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
EvidenceRef = Annotated[
    str,
    Field(pattern=r"^(project://|evidence://|query://)[A-Za-z0-9._:/-]{1,280}$"),
]


class StrictModel(BaseModel):
    """Reject extra or mutable state in every proposal component."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class ProposalType(str, Enum):
    STRATEGY = "StrategyProposal"
    STRATEGY_ADJUSTMENT = "StrategyAdjustmentProposal"
    BUG_FIX = "BugFixProposal"
    LAB_IMPROVEMENT = "LabImprovementProposal"
    DATA_ACQUISITION = "DataAcquisitionProposal"
    DEPENDENCY_UPGRADE = "DependencyUpgradeProposal"
    INVESTIGATION = "InvestigationProposal"


class AuthorityClass(str, Enum):
    A0 = "A0"
    A1 = "A1"
    A2 = "A2"


class AffectedDomain(str, Enum):
    # Permanently protected/proposal-only domains.
    CANONICAL_EVIDENCE_WRITE = "canonical_evidence_write"
    RESULT_POPULATION_MUTATION = "result_population_mutation"
    STRATEGY_SPEC_AUTHORITY_MUTATION = "strategy_spec_authority_mutation"
    PROMOTION_OR_GO = "promotion_or_go"
    DISPATCH_OR_KDAUTH = "dispatch_or_kdauth"
    OMS = "oms"
    RECONCILIATION = "reconciliation"
    HARD_RISK = "hard_risk"
    SAFE_MODE_OR_KILL_SWITCH = "safe_mode_or_kill_switch"
    LIVE_STRATEGY_PARAMETER_CHANGE = "live_strategy_parameter_change"
    PAPER_OR_LIVE_RUNTIME_MUTATION = "paper_or_live_runtime_mutation"
    EXCHANGE_ORDER_OR_CAPITAL_ACCESS = "exchange_order_or_capital_access"
    PRIVATE_CREDENTIALS = "private_credentials"
    SEARCH_GOVERNOR_BYPASS = "search_governor_legality_holdout_or_budget_bypass"
    AMBIGUOUS_PROTECTED_SCOPE = "ambiguous_protected_scope"

    # Proposal-only research/project domains with no H2 execution authority.
    STRATEGY_RESEARCH = "strategy_research"
    STRATEGY_ADJUSTMENT_RESEARCH = "strategy_adjustment_research"
    BUG_FIX = "bug_fix"
    LAB_PROCESS = "lab_process"
    DATA_ACQUISITION = "data_acquisition"
    DEPENDENCY_MAINTENANCE = "dependency_maintenance"
    BOUNDED_INVESTIGATION = "bounded_investigation"
    DOCUMENTATION = "documentation"
    TEST_ONLY_TOOLING = "test_only_tooling"


A0_DOMAINS = frozenset(
    {
        AffectedDomain.CANONICAL_EVIDENCE_WRITE,
        AffectedDomain.RESULT_POPULATION_MUTATION,
        AffectedDomain.STRATEGY_SPEC_AUTHORITY_MUTATION,
        AffectedDomain.PROMOTION_OR_GO,
        AffectedDomain.DISPATCH_OR_KDAUTH,
        AffectedDomain.OMS,
        AffectedDomain.RECONCILIATION,
        AffectedDomain.HARD_RISK,
        AffectedDomain.SAFE_MODE_OR_KILL_SWITCH,
        AffectedDomain.LIVE_STRATEGY_PARAMETER_CHANGE,
        AffectedDomain.PAPER_OR_LIVE_RUNTIME_MUTATION,
        AffectedDomain.EXCHANGE_ORDER_OR_CAPITAL_ACCESS,
        AffectedDomain.PRIVATE_CREDENTIALS,
        AffectedDomain.SEARCH_GOVERNOR_BYPASS,
        AffectedDomain.AMBIGUOUS_PROTECTED_SCOPE,
    }
)

A2_DOMAINS = frozenset(
    {
        AffectedDomain.LAB_PROCESS,
        AffectedDomain.BOUNDED_INVESTIGATION,
        AffectedDomain.DOCUMENTATION,
        AffectedDomain.TEST_ONLY_TOOLING,
    }
)


class EvidenceIdentity(StrictModel):
    path: Annotated[str, Field(min_length=1, max_length=500)]
    sha256: Sha256


class EvidenceAnchor(StrictModel):
    ref: EvidenceRef
    repo_sha: RepoSha
    evidence_identities: Annotated[
        tuple[EvidenceIdentity, ...], Field(min_length=1, max_length=200)
    ]
    query_limit: Annotated[int, Field(ge=1, le=200)] | None = None

    @model_validator(mode="after")
    def validate_ref_shape(self) -> EvidenceAnchor:
        is_query = self.ref.startswith("query://")
        if is_query != (self.query_limit is not None):
            raise ValueError("query_limit is required only for query evidence")
        return self


class FactClaim(StrictModel):
    statement: Text
    evidence_refs: Annotated[tuple[EvidenceRef, ...], Field(min_length=1, max_length=20)]


class Estimate(StrictModel):
    cost: ShortText
    compute: ShortText
    time: ShortText


class RequestedAuthority(StrictModel):
    kind: Literal["human_review_for_separate_work_package"]
    description: ShortText
    self_approval: Literal[False]
    direct_execution: Literal[False]
    standing_authority: Literal[False]


class StrategyProposal(StrictModel):
    proposal_type: Literal[ProposalType.STRATEGY]
    hypothesis: Text
    mechanism: Text
    strategy_family: ShortText
    target_market_data_context: Text
    why_it_may_contain_edge: Text
    evidence_basis: Text
    evidence_refs: Annotated[tuple[EvidenceRef, ...], Field(min_length=1)]
    proposed_lab_evaluation_concept: Text
    falsification_criteria: Annotated[tuple[Text, ...], Field(min_length=1)]
    expected_research_cost: ShortText
    claims_promotion_or_readiness: Literal[False]


class StrategyAdjustmentProposal(StrictModel):
    proposal_type: Literal[ProposalType.STRATEGY_ADJUSTMENT]
    target_strategy_or_candidate_identity: ShortText
    observed_evidence_or_performance_issue: Text
    evidence_refs: Annotated[tuple[EvidenceRef, ...], Field(min_length=1)]
    proposed_adjustment: Text
    why_adjustment_might_help: Text
    baseline_vs_adjustment_lab_test_concept: Text
    stop_or_falsification_condition: Text
    application_scope: Literal["future_lab_evaluation_only"]


class BugFixProposal(StrictModel):
    proposal_type: Literal[ProposalType.BUG_FIX]
    observed_defect_or_failure: Text
    evidence_refs: Annotated[tuple[EvidenceRef, ...], Field(min_length=1)]
    suspected_root_cause: Text
    affected_components_or_files: tuple[ShortText, ...]
    protected_boundary_assessment: Text
    proposed_fix_scope: Text
    validation_plan: Annotated[tuple[Text, ...], Field(min_length=1)]
    rollback_notes: Text
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]


class LabImprovementProposal(StrictModel):
    proposal_type: Literal[ProposalType.LAB_IMPROVEMENT]
    observed_bottleneck_waste_or_failure_mode: Text
    evidence_or_metrics: Text
    evidence_refs: Annotated[tuple[EvidenceRef, ...], Field(min_length=1)]
    proposed_lab_or_process_improvement: Text
    expected_throughput_reliability_or_value_effect: Text
    measurement_plan: Annotated[tuple[Text, ...], Field(min_length=1)]
    rollback_or_stop_condition: Text


class DataAcquisitionProposal(StrictModel):
    proposal_type: Literal[ProposalType.DATA_ACQUISITION]
    requested_dataset_or_source: Text
    research_question_enabled: Text
    provenance_or_source_identity: Text
    availability_or_timing_assumptions: Text
    storage_compute_network_cost_impact: Text
    evidence_refs: Annotated[tuple[EvidenceRef, ...], Field(min_length=1)]
    validation_plan: Annotated[tuple[Text, ...], Field(min_length=1)]
    data_quality_risks: Annotated[tuple[Text, ...], Field(min_length=1)]
    silent_repair_or_fabrication_allowed: Literal[False]


class DependencyUpgradeProposal(StrictModel):
    proposal_type: Literal[ProposalType.DEPENDENCY_UPGRADE]
    dependency_and_current_version: ShortText
    proposed_target_or_change: ShortText
    evidence_or_source: Text
    evidence_refs: Annotated[tuple[EvidenceRef, ...], Field(min_length=1)]
    compatibility_concerns: Text
    security_or_reliability_rationale: Text
    validation_plan: Annotated[tuple[Text, ...], Field(min_length=1)]
    rollback_plan: Text
    automatic_install_or_update: Literal[False]


class InvestigationProposal(StrictModel):
    proposal_type: Literal[ProposalType.INVESTIGATION]
    observed_question_or_anomaly: Text
    evidence_refs: Annotated[tuple[EvidenceRef, ...], Field(min_length=1)]
    why_investigation_is_valuable: Text
    bounded_investigation_scope: Text
    expected_output: Text
    expected_cost_and_time: ShortText
    stop_conditions: Annotated[tuple[Text, ...], Field(min_length=1)]


ProposalBody = Annotated[
    StrategyProposal
    | StrategyAdjustmentProposal
    | BugFixProposal
    | LabImprovementProposal
    | DataAcquisitionProposal
    | DependencyUpgradeProposal
    | InvestigationProposal,
    Field(discriminator="proposal_type"),
]

PROPOSAL_BODY_TYPES = {
    ProposalType.STRATEGY: StrategyProposal,
    ProposalType.STRATEGY_ADJUSTMENT: StrategyAdjustmentProposal,
    ProposalType.BUG_FIX: BugFixProposal,
    ProposalType.LAB_IMPROVEMENT: LabImprovementProposal,
    ProposalType.DATA_ACQUISITION: DataAcquisitionProposal,
    ProposalType.DEPENDENCY_UPGRADE: DependencyUpgradeProposal,
    ProposalType.INVESTIGATION: InvestigationProposal,
}


class TypedProposal(StrictModel):
    schema_version: Literal["hermes_typed_proposal_v1"]
    proposal_type: ProposalType
    title: Annotated[str, Field(min_length=1, max_length=200)]
    repo_sha: RepoSha
    source_session_id: Annotated[
        str,
        Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"),
    ]
    evidence_refs: Annotated[tuple[EvidenceRef, ...], Field(min_length=1, max_length=50)]
    evidence_anchors: Annotated[tuple[EvidenceAnchor, ...], Field(min_length=1, max_length=50)]
    facts: Annotated[tuple[FactClaim, ...], Field(min_length=1, max_length=100)]
    inferences: Annotated[tuple[Text, ...], Field(min_length=1, max_length=100)]
    open_questions: Annotated[tuple[Text, ...], Field(min_length=1, max_length=100)]
    rationale: Text
    expected_benefit: Text
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    affected_scope: Annotated[tuple[ShortText, ...], Field(min_length=1, max_length=100)]
    affected_domains: Annotated[tuple[AffectedDomain, ...], Field(min_length=1, max_length=20)]
    authority_class: AuthorityClass
    estimates: Estimate
    requested_authority: RequestedAuthority
    approval_required: Literal[True]
    validation_plan: Annotated[tuple[Text, ...], Field(min_length=1, max_length=100)]
    rollback_or_stop_conditions: Annotated[tuple[Text, ...], Field(min_length=1, max_length=100)]
    not_authority: Literal[True]
    review_required: Literal[True]
    automatic_consumers: tuple[()] = ()
    body: ProposalBody

    @model_validator(mode="after")
    def validate_closed_contract(self) -> TypedProposal:
        if self.body.proposal_type != self.proposal_type:
            raise ValueError("proposal_type must match the typed body")

        refs = tuple(self.evidence_refs)
        anchor_refs = tuple(anchor.ref for anchor in self.evidence_anchors)
        if len(refs) != len(set(refs)) or len(anchor_refs) != len(set(anchor_refs)):
            raise ValueError("evidence references must be unique")
        if refs != anchor_refs:
            raise ValueError("evidence_refs must exactly match evidence_anchors in order")
        if any(anchor.repo_sha != self.repo_sha for anchor in self.evidence_anchors):
            raise ValueError("every evidence anchor must bind the proposal repo SHA")

        known_refs = set(refs)
        for fact in self.facts:
            if not set(fact.evidence_refs).issubset(known_refs):
                raise ValueError("every FACT must cite an anchored evidence reference")
        if not set(self.body.evidence_refs).issubset(known_refs):
            raise ValueError("typed body evidence must cite anchored evidence references")

        domains = set(self.affected_domains)
        protected = bool(domains & A0_DOMAINS)
        if protected and self.authority_class is not AuthorityClass.A0:
            raise ValueError("protected or ambiguous scope requires authority class A0")
        if self.authority_class is AuthorityClass.A2 and not domains.issubset(A2_DOMAINS):
            raise ValueError("A2 is limited to explicitly low-risk proposal domains")
        return self
