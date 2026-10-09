"""Closed, frozen inputs. Scientific policy is always explicit."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identity = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")]
Text = Annotated[str, Field(min_length=1, max_length=8192)]
Sha = Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]
RepoSha = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
Positive = Annotated[int, Field(gt=0)]
Count = Annotated[int, Field(ge=0)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, allow_inf_nan=False)


class NoAuthority(StrictModel):
    candidate_promotion: Literal[False]
    canonical_result_population: Literal[False]
    protected_runtime: Literal[False]
    risk_changes: Literal[False]
    paper_live: Literal[False]
    exchange_order: Literal[False]
    capital: Literal[False]


class ParameterDomain(StrictModel):
    name: Text
    kind: Literal["int", "float", "categorical"]
    low: int | float | None
    high: int | float | None
    step: int | float | None
    choices: tuple[str | int | float | bool, ...]
    required: bool

    @model_validator(mode="after")
    def consistent(self):
        if self.kind == "categorical":
            if not self.choices or any(x is not None for x in (self.low, self.high, self.step)):
                raise ValueError("categorical domain needs choices only")
        else:
            if self.choices or self.low is None or self.high is None or self.low > self.high:
                raise ValueError("invalid numeric domain")
            if isinstance(self.low, bool) or isinstance(self.high, bool):
                raise ValueError("boolean numeric bounds")
            if self.kind == "int" and any(type(x) is not int for x in (self.low, self.high)):
                raise ValueError("integer bounds required")
            if self.step is not None and (isinstance(self.step, bool) or self.step <= 0):
                raise ValueError("positive step required")
            if self.kind == "int" and self.step is not None and type(self.step) is not int:
                raise ValueError("integer step required")
        return self


class ResearchSurface(StrictModel):
    instruments: tuple[Text, ...]
    venues: tuple[Text, ...]
    market_types: tuple[Text, ...]
    timeframes: tuple[Literal["15m", "30m", "1h", "4h", "1d"], ...]
    strategy_families: tuple[Text, ...]
    mechanisms: tuple[Text, ...]
    data_source_classes: tuple[Text, ...]
    feature_families: tuple[Text, ...]
    strategy_spec_ids: tuple[Text, ...]
    dsl_versions: tuple[Text, ...]

    @model_validator(mode="after")
    def nonempty_unique(self):
        for name in type(self).model_fields:
            values = getattr(self, name)
            if not values or len(values) != len(set(values)):
                raise ValueError(f"{name} must be nonempty and unique")
        return self


class ProposerConfig(StrictModel):
    backend: Literal["tpe", "random", "qmc", "gp"]
    version: Literal["4.9.0"]
    # Exact approved key/value pairs, rather than an open configuration object.
    config: tuple[tuple[Text, str | int | float | bool], ...]

    @model_validator(mode="after")
    def unique_keys(self):
        keys = [key for key, _ in self.config]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate proposer config key")
        return self


class Policies(StrictModel):
    duplicate_policy: Literal["reject_and_charge", "reuse_prior_result"]
    invalid_trial_policy: Literal["reject_before_scientific_execution"]
    failed_software_trial_policy: Literal["retry_same_scientific_trial_id"]
    performance_failure_classification: Literal["scientific_result"]
    pruning_policy: Literal["off"]
    retry_limit: Count
    stop_rule: Literal["proposal_or_trial_budget_exhausted"]


class SearchPolicy(StrictModel):
    parameter_domains: tuple[ParameterDomain, ...]
    proposers: tuple[ProposerConfig, ...]
    wave_size_limit: Positive
    concurrency_limit: Positive
    policies: Policies
    objectives: tuple[Objective, ...]
    conditional_rules: tuple[ConditionalRule, ...]
    relational_constraints: tuple[Relation, ...]
    forbidden_regions: tuple[Exclusion, ...]
    data_bindings: tuple[DataSelection, ...]
    split_protocols: tuple[Split, ...]

    @model_validator(mode="after")
    def unique_domains(self):
        names = [p.name for p in self.parameter_domains]
        if not names or len(names) != len(set(names)) or not self.proposers:
            raise ValueError("unique nonempty domains and proposers required")
        return self


class Budgets(StrictModel):
    job_proposals: Positive
    job_trials: Positive
    hypothesis_proposals: Positive
    hypothesis_trials: Positive
    campaign_proposals: Positive
    campaign_trials: Positive
    campaign_searches: Positive
    compute_seconds: Positive
    runtime_seconds: Positive
    concurrency: Positive
    retries: Count
    recoveries: Count


class ScientificProtocol(StrictModel):
    development_construction: Text
    wfo_oos_requirements: tuple[Text, ...]
    purge_bars: Count
    embargo_bars: Count
    leakage_policy: Text
    robustness_requirements: tuple[Text, ...]
    multiple_testing_dsr: Text
    final_holdout_policy: Literal["prohibited_to_adaptive_search_consumed_on_informative_escape"]
    scientific_constraints: tuple[Text, ...]


class EvidencePolicy(StrictModel):
    provenance_requirements: tuple[Text, ...]
    memory_indexing: Literal["index_not_truth"]
    memory_dedup: Literal["hypothesis-v1"]
    dispositions: tuple[Literal["research_completed", "research_completed_no_edge", "research_failed", "research_terminated", "research_duplicate", "research_insufficient_evidence", "research_blocked"], ...]
    stop_conditions: tuple[Text, ...]
    escalation_conditions: tuple[Text, ...]


class BoundedResearchEnvelope(StrictModel):
    schema_version: Literal["cpw_bounded_research_envelope_v1"]
    envelope_id: Identity
    envelope_version: Positive
    repo_sha: RepoSha
    content_sha256: Sha
    approved_by: Literal["Karl"]
    approved_at: Text
    contamination_domain_id: Identity
    surface: ResearchSurface
    search_policy: SearchPolicy
    budgets: Budgets
    scientific_protocol: ScientificProtocol
    evidence_policy: EvidencePolicy
    authority: NoAuthority

    @model_validator(mode="after")
    def utc_approval(self):
        if datetime.fromisoformat(self.approved_at.replace("Z", "+00:00")).utcoffset() is None:
            raise ValueError("approval must have timezone")
        return self


class EnvelopeSuccessor(StrictModel):
    envelope_id: Identity
    envelope_version: Positive
    content_sha256: Sha


class EnvelopeControlAction(StrictModel):
    schema_version: Literal["cpw_bounded_research_envelope_control_v1"]
    control_action_id: Identity
    envelope_id: Identity
    envelope_version: Positive
    envelope_content_sha256: Sha
    repo_sha: RepoSha
    action: Literal["revoke", "replace"]
    approved_by: Literal["Karl"]
    approved_at: Text
    reason: Text
    successor: EnvelopeSuccessor | None
    authority: NoAuthority

    @model_validator(mode="after")
    def consistent(self):
        if (self.action == "replace") != (self.successor is not None):
            raise ValueError("replacement alone requires successor")
        if datetime.fromisoformat(self.approved_at.replace("Z", "+00:00")).utcoffset() is None:
            raise ValueError("approval must have timezone")
        if self.successor and (self.successor.envelope_id, self.successor.envelope_version) == (self.envelope_id, self.envelope_version):
            raise ValueError("replacement requires distinct envelope identity")
        return self


class EvidenceBinding(StrictModel):
    resource_uri: Text
    repo_path: Text
    artifact_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    repo_sha: RepoSha


class DataSelection(StrictModel):
    data_identity: Text
    data_version: Text
    evidence: EvidenceBinding


class Objective(StrictModel):
    name: Text
    direction: Literal["maximize", "minimize"]
    definition: Text


class Split(StrictModel):
    protocol_id: Text
    development_data_ref: Text
    development_window: Text
    final_holdout_ref: Identity
    final_holdout_access: Literal["prohibited"]


class ConditionalRule(StrictModel):
    parameter: Text
    when_parameter: Text
    when_values: tuple[str | int | float | bool, ...]


class Relation(StrictModel):
    left_parameter: Text
    operator: Literal["lt", "lte", "gt", "gte", "eq", "neq"]
    right_parameter: Text
    constraint_id: Text


class Exclusion(StrictModel):
    region_id: Text
    equal_values: tuple[tuple[Text, str | int | float | bool], ...]
    reason: Text


class BoundedSearchRequest(StrictModel):
    campaign_id: Identity
    search_id: Identity
    parent_search_id: Identity | None
    reason_for_change: Text | None
    intent_sha256: Sha
    hypothesis_id: Text
    family_id: Text
    strategy_spec_id: Text
    strategy_spec_evidence: EvidenceBinding
    data_identity: Text
    data_version: Text
    data_evidence: EvidenceBinding
    instrument: Text
    venue: Text
    market_type: Text
    data_source_class: Text
    dsl_version: Text
    parameter_space: tuple[ParameterDomain, ...]
    conditional_rules: tuple[ConditionalRule, ...]
    relational_constraints: tuple[Relation, ...]
    forbidden_regions: tuple[Exclusion, ...]
    objective: Objective
    scientific_protocol: ScientificProtocol
    max_proposals: Positive
    max_scientific_trials: Positive
    compute_seconds: Positive
    runtime_seconds: Positive
    recovery_limit: Count
    wave_size: Positive
    concurrency: Positive
    split_protocol: Split
    proposer: ProposerConfig
    seed: int
    policies: Policies

    @model_validator(mode="after")
    def parent_reason(self):
        if (self.parent_search_id is None) != (self.reason_for_change is None):
            raise ValueError("parent and reason must appear together")
        return self


class BudgetState(StrictModel):
    proposals_used: Count
    scientific_trials_used: Count
    reserved_proposals: Count
    reserved_trials: Count
    proposal_ceiling: Positive
    trial_ceiling: Positive
    search_ceiling: Positive
    search_count: Count


class HoldoutState(StrictModel):
    contamination_domain_id: Identity
    holdout_id: Identity
    state: Literal["unexposed", "attempted_isolated", "consumed"]
    contaminated: bool


class DurableLineageSnapshot(StrictModel):
    campaign_id: Identity
    envelope_id: Identity
    envelope_version: Positive
    envelope_content_sha256: Sha
    contamination_domain_id: Identity
    lineage_version: Count
    lineage_sha256: Sha
    budget: BudgetState
    holdout: HoldoutState


class ContractAuthority(StrictModel):
    mode: Literal["noncanonical"]
    canonical_authority: Literal[False]
    winner_authority: Literal[False]
    promotion_authority: Literal[False]
    go_authority: Literal[False]


class FrozenContractPayload(StrictModel):
    campaign_id: Identity
    search_id: Identity
    parent_search_id: Identity | None
    reason_for_change: Text | None
    hypothesis_id: Text
    family_id: Text
    hypothesis_fingerprint: Text
    data_identity: Text
    data_version: Text
    repo_sha: RepoSha
    strategy_spec_id: Text
    strategy_spec_hash: Sha
    parameter_space: tuple[ParameterDomain, ...]
    conditional_rules: tuple[ConditionalRule, ...]
    relational_constraints: tuple[Relation, ...]
    forbidden_regions: tuple[Exclusion, ...]
    objective: Objective
    scientific_constraints: tuple[Text, ...]
    max_proposals: Positive
    max_scientific_trials: Positive
    wave_size: Positive
    concurrency: Positive
    split_protocol: Split
    proposer: ProposerConfig
    seed: int
    policies: Policies
    campaign_proposals_before_search: Count
    campaign_scientific_trials_before_search: Count
    envelope_id: Identity
    envelope_version: Positive
    envelope_content_sha256: Sha
    contamination_domain_id: Identity
    authority_lineage_version: Count
    authority_lineage_sha256: Sha
    authority: ContractAuthority


class WaveProposal(StrictModel):
    proposal_id: Identity
    proposal_sequence: Count
    wave_id: Identity
    backend_trial_number: Count
    adapter_handle: Text
    params: dict[Text, str | int | float | bool]
    params_fingerprint: Sha
    status: Literal["ACCEPTED_FOR_SCIENTIFIC_EXECUTION", "REJECTED_INVALID", "DUPLICATE_NOT_NEW_OBSERVATION"]
    rejection_reasons: tuple[Text, ...]
    scientific_trial_id: Text | None
    campaign_id: Identity
    search_id: Identity
    parent_search_id: Identity | None
    hypothesis_id: Text
    family_id: Text
    hypothesis_fingerprint: Text
    contract_hash: Sha
    data_identity: Text
    data_version: Text
    repo_sha: RepoSha
    proposer_backend: Literal["tpe", "random", "qmc", "gp"]
    proposer_version: Literal["4.9.0"]
    seed: int
    campaign_proposals_before_search: Count
    campaign_scientific_trials_before_search: Count
    noncanonical: Literal[True]
    canonical_authority: Literal[False]
    winner_authority: Literal[False]
    promotion_authority: Literal[False]
    go_authority: Literal[False]


class SoftwareAttempt(StrictModel):
    scientific_trial_id: Text
    proposal_id: Identity
    attempt_number: Positive
    state: Literal["SOFTWARE_FAILED"]
    objective_value: None
    performance_constraints_passed: None
    detail: None
    counts_as_independent_scientific_observation: bool


class AskOperation(StrictModel):
    op: Literal["ask"]
    handle: Text
    backend_trial_number: Count
    params: dict[Text, str | int | float | bool]


class TellOperation(StrictModel):
    op: Literal["tell"]
    handle: Text
    state: Literal["invalid", "duplicate", "software_failed"]
    value: None


class ProposerSurface(StrictModel):
    search_id: Identity
    contract_hash: Sha
    parameter_space: tuple[ParameterDomain, ...]
    conditional_rules: tuple[ConditionalRule, ...]
    proposer: ProposerConfig
    seed: int
    objective_direction: Literal["maximize", "minimize"]


class AdapterSnapshot(StrictModel):
    snapshot_version: Literal["optuna-proposal-replay-v1"]
    optuna_version: Literal["4.9.0"]
    surface: ProposerSurface
    operations: tuple[AskOperation | TellOperation, ...]
    restore_method: Literal["seeded_exact_operation_replay_with_proposal_verification"]
    contains_final_holdout: Literal[False]
    snapshot_hash: Sha


class GovernorSnapshot(StrictModel):
    snapshot_version: Literal["search-governor-state-v1"]
    contract_hash: Sha
    proposal_records: tuple[WaveProposal, ...]
    trial_attempts: tuple[SoftwareAttempt, ...]
    accepted_by_fingerprint: dict[Sha, Identity]
    objective_by_fingerprint: Annotated[dict[Sha, float], Field(max_length=0)]
    proposal_attempt_number: dict[Identity, Count]
    wave_number: Count
    scientific_denominator: Count
    adapter_snapshot: AdapterSnapshot
    snapshot_hash: Sha


class ProposalWaveHandoff(StrictModel):
    schema_version: Literal["cpw_proposal_wave_handoff_v1"]
    repo_sha: RepoSha
    intent_sha256: Sha
    envelope_id: Identity
    envelope_version: Positive
    envelope_content_sha256: Sha
    campaign_id: Identity
    search_id: Identity
    parent_search_id: Identity | None
    authority_lineage_version: Count
    authority_lineage_sha256: Sha
    frozen_contract: FrozenContractPayload
    contract_hash: Sha
    pre_wave_snapshot: GovernorSnapshot
    requested_wave_count: Positive
    proposal_records: tuple[WaveProposal, ...]
    resulting_denominator: Count
    content_sha256: Sha
    noncanonical: Literal[True]
    runner_authority: Literal[False]
    approval_authority: Literal[False]
    authority: NoAuthority
