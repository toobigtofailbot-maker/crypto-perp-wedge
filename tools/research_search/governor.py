"""Project-owned legality, budget, holdout, lineage, and trial-accounting governor."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

from tools.research_search.contract import SearchContract, canonical_json, sha256_payload
from tools.research_search.optuna_adapter import (
    OptunaProposalAdapter,
    ProposalSurface,
    _new_governor_capability,
)

GOVERNOR_SNAPSHOT_VERSION = "search-governor-state-v1"


class SearchGovernorError(RuntimeError):
    """Base error for governed-search control violations."""


class BudgetExhausted(SearchGovernorError):
    """Raised when a proposal or scientific-trial budget is exhausted."""


class HoldoutAccessDenied(SearchGovernorError):
    """Raised on every attempted final-holdout access."""


class ContractMutationDenied(SearchGovernorError):
    """Raised when code attempts to mutate a frozen search in place."""


class TrialStateError(SearchGovernorError):
    """Raised for invalid trial-state or retry transitions."""


@dataclass(frozen=True)
class ProposalRecord:
    proposal_id: str
    proposal_sequence: int
    wave_id: str
    backend_trial_number: int
    adapter_handle: str
    params: dict[str, Any]
    params_fingerprint: str
    status: str
    rejection_reasons: tuple[str, ...]
    scientific_trial_id: str | None
    campaign_id: str
    search_id: str
    parent_search_id: str | None
    hypothesis_id: str
    family_id: str
    hypothesis_fingerprint: str
    contract_hash: str
    data_identity: str
    data_version: str
    repo_sha: str
    proposer_backend: str
    proposer_version: str
    seed: int
    campaign_proposals_before_search: int
    campaign_scientific_trials_before_search: int
    noncanonical: bool = True
    canonical_authority: bool = False
    winner_authority: bool = False
    promotion_authority: bool = False
    go_authority: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TrialAttempt:
    scientific_trial_id: str
    proposal_id: str
    attempt_number: int
    state: str
    objective_value: float | None
    performance_constraints_passed: bool | None
    detail: str | None
    counts_as_independent_scientific_observation: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SearchGovernor:
    """The sole owner of search legality and scientific accounting."""

    def __init__(self, contract: SearchContract) -> None:
        self.contract = contract
        self._contract_hash = contract.contract_hash
        self._capability = _new_governor_capability(contract.search_id, self._contract_hash)
        self._surface = ProposalSurface(
            search_id=contract.search_id,
            contract_hash=self._contract_hash,
            parameter_space=contract.parameter_space,
            conditional_rules=contract.conditional_rules,
            proposer=contract.proposer,
            seed=contract.seed,
            objective_direction=contract.objective.direction,
        )
        self._adapter = OptunaProposalAdapter(
            self._surface,
            capability=self._capability,
        )
        self.proposal_records: list[ProposalRecord] = []
        self.trial_attempts: list[TrialAttempt] = []
        self._accepted_by_fingerprint: dict[str, str] = {}
        self._objective_by_fingerprint: dict[str, float] = {}
        self._proposal_attempt_number: dict[str, int] = {}
        self._pending_results: dict[str, TrialAttempt] = {}
        self._active_wave_proposal_ids: list[str] = []
        self._wave_number = 0
        self._scientific_denominator = 0

    @property
    def proposal_count(self) -> int:
        return len(self.proposal_records)

    @property
    def scientific_denominator(self) -> int:
        return self._scientific_denominator

    @property
    def adapter_surface(self) -> dict[str, Any]:
        """Return the sanitized proposer view; it intentionally contains no holdout."""

        return self._surface.to_dict()

    def data_reference(self, role: str) -> str:
        if role == "final_holdout":
            raise HoldoutAccessDenied("FINAL HOLDOUT access is prohibited for governed search")
        if role != "development":
            raise SearchGovernorError(f"unknown data role: {role}")
        return self.contract.split_protocol.development_data_ref

    def assert_frozen_contract(self, candidate: SearchContract) -> None:
        if candidate.contract_hash != self._contract_hash:
            raise ContractMutationDenied(
                "post-hoc contract change denied; create a parent-linked new search_id"
            )

    def _proposal_record(
        self,
        *,
        raw: Any,
        wave_id: str,
        status: str,
        reasons: tuple[str, ...],
        scientific_trial_id: str | None,
    ) -> ProposalRecord:
        sequence = len(self.proposal_records)
        params_fingerprint = sha256_payload(raw.params)
        proposal_id = (
            "PROP-"
            + sha256_payload(
                {
                    "contract_hash": self._contract_hash,
                    "proposal_sequence": sequence,
                    "params": raw.params,
                }
            )
            .split(":", 1)[1][:20]
            .upper()
        )
        return ProposalRecord(
            proposal_id=proposal_id,
            proposal_sequence=sequence,
            wave_id=wave_id,
            backend_trial_number=raw.backend_trial_number,
            adapter_handle=raw.handle,
            params=dict(raw.params),
            params_fingerprint=params_fingerprint,
            status=status,
            rejection_reasons=reasons,
            scientific_trial_id=scientific_trial_id,
            campaign_id=self.contract.campaign_id,
            search_id=self.contract.search_id,
            parent_search_id=self.contract.parent_search_id,
            hypothesis_id=self.contract.hypothesis_id,
            family_id=self.contract.family_id,
            hypothesis_fingerprint=self.contract.hypothesis_fingerprint,
            contract_hash=self._contract_hash,
            data_identity=self.contract.data_identity,
            data_version=self.contract.data_version,
            repo_sha=self.contract.repo_sha,
            proposer_backend=self.contract.proposer.backend,
            proposer_version=self.contract.proposer.version,
            seed=self.contract.seed,
            campaign_proposals_before_search=self.contract.campaign_proposals_before_search,
            campaign_scientific_trials_before_search=(
                self.contract.campaign_scientific_trials_before_search
            ),
        )

    def propose_wave(self, count: int | None = None) -> tuple[ProposalRecord, ...]:
        if self._active_wave_proposal_ids:
            raise SearchGovernorError("the active proposal wave must finish before another begins")
        requested = self.contract.wave_size if count is None else count
        if requested <= 0 or requested > self.contract.wave_size:
            raise SearchGovernorError("requested wave count must fit the frozen wave_size")
        remaining_trials = self.contract.max_scientific_trials - self._scientific_denominator
        if remaining_trials <= 0:
            raise BudgetExhausted("scientific-trial budget exhausted before proposal")
        requested = min(requested, remaining_trials)
        if self.proposal_count >= self.contract.max_proposals:
            raise BudgetExhausted("proposal budget exhausted before proposal")

        self._wave_number += 1
        wave_id = f"WAVE-{self._wave_number:04d}"
        accepted: list[ProposalRecord] = []
        while len(accepted) < requested and self.proposal_count < self.contract.max_proposals:
            raw = self._adapter.ask(self._capability)
            errors = self.contract.validate_parameters(raw.params)
            fingerprint = sha256_payload(raw.params)
            duplicate_of = self._accepted_by_fingerprint.get(fingerprint)
            if errors:
                record = self._proposal_record(
                    raw=raw,
                    wave_id=wave_id,
                    status="REJECTED_INVALID",
                    reasons=errors,
                    scientific_trial_id=None,
                )
                self.proposal_records.append(record)
                self._adapter.tell(self._capability, raw.handle, state="invalid")
                continue
            if duplicate_of is not None:
                record = self._proposal_record(
                    raw=raw,
                    wave_id=wave_id,
                    status="DUPLICATE_NOT_NEW_OBSERVATION",
                    reasons=(f"duplicate_of:{duplicate_of}",),
                    scientific_trial_id=None,
                )
                self.proposal_records.append(record)
                prior = self._objective_by_fingerprint.get(fingerprint)
                if (
                    self.contract.policies.duplicate_policy == "reuse_prior_result"
                    and prior is not None
                ):
                    self._adapter.tell(
                        self._capability,
                        raw.handle,
                        state="complete",
                        value=prior,
                    )
                else:
                    self._adapter.tell(self._capability, raw.handle, state="duplicate")
                continue

            trial_id = f"{self.contract.search_id}:TRIAL-{self._scientific_denominator + 1:04d}"
            record = self._proposal_record(
                raw=raw,
                wave_id=wave_id,
                status="ACCEPTED_FOR_SCIENTIFIC_EXECUTION",
                reasons=(),
                scientific_trial_id=trial_id,
            )
            self.proposal_records.append(record)
            self._accepted_by_fingerprint[fingerprint] = record.proposal_id
            self._proposal_attempt_number[record.proposal_id] = 0
            self._scientific_denominator += 1
            accepted.append(record)

        if not accepted:
            raise BudgetExhausted("proposal budget exhausted without a legal unique proposal")
        self._active_wave_proposal_ids = [record.proposal_id for record in accepted]
        return tuple(accepted)

    def _accepted_record(self, proposal_id: str) -> ProposalRecord:
        for record in self.proposal_records:
            if record.proposal_id == proposal_id:
                if record.scientific_trial_id is None:
                    raise TrialStateError("rejected or duplicate proposal has no scientific trial")
                return record
        raise TrialStateError(f"unknown proposal_id: {proposal_id}")

    def submit_result(
        self,
        proposal_id: str,
        *,
        state: str,
        objective_value: float | None = None,
        performance_constraints_passed: bool | None = None,
        detail: str | None = None,
    ) -> TrialAttempt:
        if proposal_id not in self._active_wave_proposal_ids:
            raise TrialStateError("result must belong to the active frozen wave")
        if proposal_id in self._pending_results:
            raise TrialStateError("proposal already has a pending terminal result")
        record = self._accepted_record(proposal_id)
        if state == "performance_result":
            if objective_value is None:
                raise TrialStateError("performance_result requires objective_value")
            constraint_result = bool(performance_constraints_passed)
        elif state == "software_failed":
            if objective_value is not None or performance_constraints_passed is not None:
                raise TrialStateError("software failure cannot carry scientific performance")
            constraint_result = None
        else:
            raise TrialStateError(
                "trial state must keep performance_result distinct from software_failed"
            )
        attempt_number = self._proposal_attempt_number[proposal_id] + 1
        self._proposal_attempt_number[proposal_id] = attempt_number
        attempt = TrialAttempt(
            scientific_trial_id=str(record.scientific_trial_id),
            proposal_id=proposal_id,
            attempt_number=attempt_number,
            state=state.upper(),
            objective_value=float(objective_value) if objective_value is not None else None,
            performance_constraints_passed=constraint_result,
            detail=detail,
            counts_as_independent_scientific_observation=attempt_number == 1,
        )
        self.trial_attempts.append(attempt)
        self._pending_results[proposal_id] = attempt
        return attempt

    def authorize_retry(self, proposal_id: str) -> dict[str, Any]:
        pending = self._pending_results.get(proposal_id)
        if pending is None or pending.state != "SOFTWARE_FAILED":
            raise TrialStateError("only a pending software failure can be retried")
        if pending.attempt_number > self.contract.policies.retry_limit:
            raise TrialStateError("retry limit exhausted")
        del self._pending_results[proposal_id]
        return {
            "proposal_id": proposal_id,
            "scientific_trial_id": pending.scientific_trial_id,
            "next_attempt_number": pending.attempt_number + 1,
            "counts_as_independent_scientific_observation": False,
        }

    def finalize_wave(self) -> tuple[TrialAttempt, ...]:
        if not self._active_wave_proposal_ids:
            raise TrialStateError("no active wave")
        missing = [
            proposal_id
            for proposal_id in self._active_wave_proposal_ids
            if proposal_id not in self._pending_results
        ]
        if missing:
            raise TrialStateError("every active-wave proposal needs a terminal result")
        by_id = {record.proposal_id: record for record in self.proposal_records}
        ordered_ids = sorted(
            self._active_wave_proposal_ids,
            key=lambda proposal_id: by_id[proposal_id].proposal_sequence,
        )
        terminal: list[TrialAttempt] = []
        for proposal_id in ordered_ids:
            record = by_id[proposal_id]
            attempt = self._pending_results.pop(proposal_id)
            if attempt.state == "PERFORMANCE_RESULT":
                self._adapter.tell(
                    self._capability,
                    record.adapter_handle,
                    state="complete",
                    value=attempt.objective_value,
                )
                assert attempt.objective_value is not None
                self._objective_by_fingerprint[record.params_fingerprint] = attempt.objective_value
            else:
                self._adapter.tell(
                    self._capability,
                    record.adapter_handle,
                    state="software_failed",
                )
            terminal.append(attempt)
        self._active_wave_proposal_ids = []
        return tuple(terminal)

    def snapshot(self) -> dict[str, Any]:
        if self._active_wave_proposal_ids or self._pending_results:
            raise TrialStateError("Governor snapshot requires a finalized wave boundary")
        payload = {
            "snapshot_version": GOVERNOR_SNAPSHOT_VERSION,
            "contract_hash": self._contract_hash,
            "proposal_records": [record.to_dict() for record in self.proposal_records],
            "trial_attempts": [attempt.to_dict() for attempt in self.trial_attempts],
            "accepted_by_fingerprint": dict(self._accepted_by_fingerprint),
            "objective_by_fingerprint": dict(self._objective_by_fingerprint),
            "proposal_attempt_number": dict(self._proposal_attempt_number),
            "wave_number": self._wave_number,
            "scientific_denominator": self._scientific_denominator,
            "adapter_snapshot": self._adapter.snapshot(self._capability),
        }
        payload["snapshot_hash"] = sha256_payload(payload)
        return payload

    @classmethod
    def restore(
        cls,
        contract: SearchContract,
        snapshot: Mapping[str, Any],
    ) -> SearchGovernor:
        payload = dict(snapshot)
        snapshot_hash = payload.pop("snapshot_hash", None)
        if snapshot_hash != sha256_payload(payload):
            raise SearchGovernorError("Governor snapshot hash mismatch")
        if payload.get("snapshot_version") != GOVERNOR_SNAPSHOT_VERSION:
            raise SearchGovernorError("unsupported Governor snapshot version")
        governor = cls.__new__(cls)
        governor.contract = contract
        governor._contract_hash = contract.contract_hash
        if payload.get("contract_hash") != governor._contract_hash:
            raise ContractMutationDenied("snapshot contract requires a new lineaged search")
        governor._capability = _new_governor_capability(
            contract.search_id,
            governor._contract_hash,
        )
        governor._surface = ProposalSurface(
            search_id=contract.search_id,
            contract_hash=governor._contract_hash,
            parameter_space=contract.parameter_space,
            conditional_rules=contract.conditional_rules,
            proposer=contract.proposer,
            seed=contract.seed,
            objective_direction=contract.objective.direction,
        )
        governor._adapter = OptunaProposalAdapter.restore(
            governor._surface,
            payload["adapter_snapshot"],
            capability=governor._capability,
        )
        governor.proposal_records = [
            ProposalRecord(**record) for record in payload["proposal_records"]
        ]
        governor.trial_attempts = [TrialAttempt(**attempt) for attempt in payload["trial_attempts"]]
        governor._accepted_by_fingerprint = dict(payload["accepted_by_fingerprint"])
        governor._objective_by_fingerprint = {
            key: float(value) for key, value in payload["objective_by_fingerprint"].items()
        }
        governor._proposal_attempt_number = {
            key: int(value) for key, value in payload["proposal_attempt_number"].items()
        }
        governor._wave_number = int(payload["wave_number"])
        governor._scientific_denominator = int(payload["scientific_denominator"])
        governor._pending_results = {}
        governor._active_wave_proposal_ids = []
        return governor

    def accounting_summary(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for attempt in self.trial_attempts:
            counts[attempt.state] = counts.get(attempt.state, 0) + 1
        return {
            "campaign_id": self.contract.campaign_id,
            "search_id": self.contract.search_id,
            "contract_hash": self._contract_hash,
            "proposal_budget": self.contract.max_proposals,
            "proposals_used": self.proposal_count,
            "scientific_trial_budget": self.contract.max_scientific_trials,
            "scientific_denominator": self._scientific_denominator,
            "campaign_cumulative_proposals": (
                self.contract.campaign_proposals_before_search + self.proposal_count
            ),
            "campaign_cumulative_scientific_denominator": (
                self.contract.campaign_scientific_trials_before_search
                + self._scientific_denominator
            ),
            "trial_attempt_counts": counts,
            "noncanonical": True,
            "canonical_authority": False,
            "winner_authority": False,
            "promotion_authority": False,
            "go_authority": False,
            "ordered_tell": True,
            "performance_pruning": False,
            "final_holdout_exposed_to_proposer": (
                self.contract.split_protocol.final_holdout_ref
                in canonical_json(self.adapter_surface)
            ),
        }
