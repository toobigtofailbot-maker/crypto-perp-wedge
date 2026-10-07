"""Frozen scientific contract models owned by the Search Governor."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from dataclasses import asdict, dataclass, replace
from typing import Any, Literal

ParameterKind = Literal["int", "float", "categorical"]
DuplicatePolicy = Literal["reject_and_charge", "reuse_prior_result"]


class SearchContractError(ValueError):
    """Raised when a governed search contract is incomplete or inconsistent."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_payload(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ParameterSpec:
    name: str
    kind: ParameterKind
    low: int | float | None = None
    high: int | float | None = None
    step: int | float | None = None
    choices: tuple[Any, ...] = ()
    required: bool = True

    def __post_init__(self) -> None:
        if not self.name:
            raise SearchContractError("parameter name must not be empty")
        if self.kind == "categorical":
            if not self.choices:
                raise SearchContractError(f"categorical parameter {self.name} needs choices")
            if self.low is not None or self.high is not None or self.step is not None:
                raise SearchContractError(f"categorical parameter {self.name} cannot have bounds")
            return
        if self.low is None or self.high is None or self.low > self.high:
            raise SearchContractError(f"numeric parameter {self.name} has invalid bounds")
        if self.kind == "int" and (
            isinstance(self.low, bool)
            or isinstance(self.high, bool)
            or not isinstance(self.low, int)
            or not isinstance(self.high, int)
        ):
            raise SearchContractError(f"integer parameter {self.name} needs integer bounds")
        if self.step is not None and (
            isinstance(self.step, bool) or not isinstance(self.step, (int, float)) or self.step <= 0
        ):
            raise SearchContractError(f"numeric parameter {self.name} has invalid step")

    def contains(self, value: Any) -> bool:
        if self.kind == "categorical":
            return value in self.choices
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        if self.kind == "int" and not isinstance(value, int):
            return False
        numeric = float(value)
        if not math.isfinite(numeric) or numeric < float(self.low) or numeric > float(self.high):
            return False
        if self.step is None:
            return True
        steps = (numeric - float(self.low)) / float(self.step)
        return math.isclose(steps, round(steps), rel_tol=0.0, abs_tol=1e-9)


@dataclass(frozen=True)
class ConditionalParameterRule:
    parameter: str
    when_parameter: str
    when_values: tuple[Any, ...]


@dataclass(frozen=True)
class RelationalConstraint:
    left_parameter: str
    operator: Literal["lt", "lte", "gt", "gte", "eq", "neq"]
    right_parameter: str
    constraint_id: str

    def satisfied(self, params: Mapping[str, Any]) -> bool:
        left = params[self.left_parameter]
        right = params[self.right_parameter]
        return {
            "lt": left < right,
            "lte": left <= right,
            "gt": left > right,
            "gte": left >= right,
            "eq": left == right,
            "neq": left != right,
        }[self.operator]


@dataclass(frozen=True)
class ForbiddenRegion:
    region_id: str
    equal_values: tuple[tuple[str, Any], ...]
    reason: str

    def matches(self, params: Mapping[str, Any]) -> bool:
        return all(params.get(name) == value for name, value in self.equal_values)


@dataclass(frozen=True)
class ObjectiveSpec:
    name: str
    direction: Literal["maximize", "minimize"]
    definition: str


@dataclass(frozen=True)
class SplitProtocol:
    protocol_id: str
    development_data_ref: str
    development_window: str
    final_holdout_ref: str
    final_holdout_access: Literal["prohibited"] = "prohibited"


@dataclass(frozen=True)
class ProposerSpec:
    backend: Literal["tpe", "random", "qmc", "gp"]
    version: str
    config: tuple[tuple[str, Any], ...]


@dataclass(frozen=True)
class SearchPolicies:
    duplicate_policy: DuplicatePolicy
    invalid_trial_policy: Literal["reject_before_scientific_execution"]
    failed_software_trial_policy: Literal["retry_same_scientific_trial_id"]
    performance_failure_classification: Literal["scientific_result"]
    pruning_policy: Literal["off"]
    retry_limit: int
    stop_rule: Literal["proposal_or_trial_budget_exhausted"]

    def __post_init__(self) -> None:
        if self.retry_limit < 0:
            raise SearchContractError("retry_limit must be non-negative")


@dataclass(frozen=True)
class AuthoritySemantics:
    mode: Literal["noncanonical"] = "noncanonical"
    canonical_authority: bool = False
    winner_authority: bool = False
    promotion_authority: bool = False
    go_authority: bool = False


@dataclass(frozen=True)
class SearchContract:
    campaign_id: str
    search_id: str
    parent_search_id: str | None
    reason_for_change: str | None
    hypothesis_id: str
    family_id: str
    hypothesis_fingerprint: str
    data_identity: str
    data_version: str
    repo_sha: str
    strategy_spec_id: str
    strategy_spec_hash: str
    parameter_space: tuple[ParameterSpec, ...]
    conditional_rules: tuple[ConditionalParameterRule, ...]
    relational_constraints: tuple[RelationalConstraint, ...]
    forbidden_regions: tuple[ForbiddenRegion, ...]
    objective: ObjectiveSpec
    scientific_constraints: tuple[str, ...]
    max_proposals: int
    max_scientific_trials: int
    wave_size: int
    concurrency: int
    split_protocol: SplitProtocol
    proposer: ProposerSpec
    seed: int
    policies: SearchPolicies
    campaign_proposals_before_search: int
    campaign_scientific_trials_before_search: int
    envelope_id: str
    envelope_version: int
    envelope_content_sha256: str
    contamination_domain_id: str
    authority_lineage_version: int
    authority_lineage_sha256: str
    authority: AuthoritySemantics = AuthoritySemantics()

    def __post_init__(self) -> None:
        required = {
            "campaign_id": self.campaign_id,
            "search_id": self.search_id,
            "hypothesis_id": self.hypothesis_id,
            "family_id": self.family_id,
            "hypothesis_fingerprint": self.hypothesis_fingerprint,
            "data_identity": self.data_identity,
            "data_version": self.data_version,
            "repo_sha": self.repo_sha,
            "strategy_spec_id": self.strategy_spec_id,
            "strategy_spec_hash": self.strategy_spec_hash,
            "envelope_id": self.envelope_id,
            "envelope_content_sha256": self.envelope_content_sha256,
            "contamination_domain_id": self.contamination_domain_id,
            "authority_lineage_sha256": self.authority_lineage_sha256,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise SearchContractError(f"missing contract identities: {', '.join(missing)}")
        if type(self.envelope_version) is not int or self.envelope_version <= 0:
            raise SearchContractError("envelope version must be positive")
        if type(self.authority_lineage_version) is not int or self.authority_lineage_version < 0:
            raise SearchContractError("authority lineage version must be non-negative")
        if self.max_proposals <= 0 or self.max_scientific_trials <= 0:
            raise SearchContractError("proposal and scientific-trial budgets must be positive")
        if (
            self.campaign_proposals_before_search < 0
            or self.campaign_scientific_trials_before_search < 0
        ):
            raise SearchContractError("campaign cumulative accounting must be non-negative")
        if self.wave_size <= 0 or self.wave_size > self.max_scientific_trials:
            raise SearchContractError("wave_size must fit the scientific-trial budget")
        if self.concurrency <= 0 or self.concurrency > self.wave_size:
            raise SearchContractError("concurrency must be positive and no larger than wave_size")
        names = [parameter.name for parameter in self.parameter_space]
        if len(names) != len(set(names)):
            raise SearchContractError("parameter names must be unique")
        known = set(names)
        for rule in self.conditional_rules:
            if rule.parameter not in known or rule.when_parameter not in known:
                raise SearchContractError("conditional rule references an unknown parameter")
        for constraint in self.relational_constraints:
            if constraint.left_parameter not in known or constraint.right_parameter not in known:
                raise SearchContractError("relational constraint references an unknown parameter")
        for region in self.forbidden_regions:
            if any(name not in known for name, _value in region.equal_values):
                raise SearchContractError("forbidden region references an unknown parameter")
        if (self.parent_search_id is None) != (self.reason_for_change is None):
            raise SearchContractError("parent_search_id and reason_for_change must appear together")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def contract_hash(self) -> str:
        return sha256_payload(self.to_dict())

    def validate_parameters(self, params: Mapping[str, Any]) -> tuple[str, ...]:
        errors: list[str] = []
        specs = {parameter.name: parameter for parameter in self.parameter_space}
        unknown = sorted(set(params) - set(specs))
        if unknown:
            errors.append(f"unknown parameters: {', '.join(unknown)}")
        conditional_names = {rule.parameter for rule in self.conditional_rules}
        for name, spec in specs.items():
            if name not in params:
                if spec.required and name not in conditional_names:
                    errors.append(f"missing required parameter: {name}")
                continue
            if not spec.contains(params[name]):
                errors.append(f"parameter outside frozen legal space: {name}")
        for rule in self.conditional_rules:
            active = params.get(rule.when_parameter) in rule.when_values
            present = rule.parameter in params
            if active and not present:
                errors.append(f"conditional parameter required: {rule.parameter}")
            if not active and present:
                errors.append(f"conditional parameter must be absent: {rule.parameter}")
        if errors:
            return tuple(errors)
        for constraint in self.relational_constraints:
            if not constraint.satisfied(params):
                errors.append(f"constraint failed: {constraint.constraint_id}")
        for region in self.forbidden_regions:
            if region.matches(params):
                errors.append(f"forbidden region: {region.region_id}")
        return tuple(errors)

    def successor(
        self,
        *,
        new_search_id: str,
        reason_for_change: str,
        parameter_space: tuple[ParameterSpec, ...] | None = None,
        max_proposals: int | None = None,
        max_scientific_trials: int | None = None,
        observed_proposals: int,
        observed_scientific_trials: int,
    ) -> SearchContract:
        if not new_search_id or new_search_id == self.search_id:
            raise SearchContractError("changed search requires a distinct new_search_id")
        if not reason_for_change:
            raise SearchContractError("changed search requires reason_for_change")
        if observed_proposals < 0 or observed_scientific_trials < 0:
            raise SearchContractError("observed campaign accounting must be non-negative")
        return replace(
            self,
            search_id=new_search_id,
            parent_search_id=self.search_id,
            reason_for_change=reason_for_change,
            parameter_space=parameter_space or self.parameter_space,
            max_proposals=max_proposals or self.max_proposals,
            max_scientific_trials=max_scientific_trials or self.max_scientific_trials,
            campaign_proposals_before_search=(
                self.campaign_proposals_before_search + observed_proposals
            ),
            campaign_scientific_trials_before_search=(
                self.campaign_scientific_trials_before_search + observed_scientific_trials
            ),
        )
