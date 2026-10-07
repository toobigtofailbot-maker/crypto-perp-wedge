import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import optuna
import pandas as pd
import pytest

from tools.research_memory.fingerprint import fingerprint
from tools.research_runner.spec_signal_compiler import compile_signal
from tools.research_search.contract import (
    ConditionalParameterRule,
    ForbiddenRegion,
    ObjectiveSpec,
    ParameterSpec,
    ProposerSpec,
    RelationalConstraint,
    SearchContract,
    SearchPolicies,
    SplitProtocol,
)
from tools.research_search.governor import (
    BudgetExhausted,
    ContractMutationDenied,
    HoldoutAccessDenied,
    SearchGovernor,
    TrialStateError,
)
from tools.research_search.optuna_adapter import (
    AdapterBypassDenied,
    AdapterProposal,
    OptunaProposalAdapter,
    ProposalSurface,
    supported_backends,
)


def make_contract(
    *,
    backend="tpe",
    max_proposals=50,
    max_trials=6,
    wave_size=2,
    duplicate_policy="reject_and_charge",
):
    definition = {
        "strategy_family": "test family",
        "mechanism": "bounded parameter test",
        "primary_timeframe": "15m",
        "required_data_features": ["ohlcv"],
        "free_parameter_count": 4,
    }
    proposer_config = (("multivariate", True), ("group", True), ("n_startup_trials", 1))
    if backend != "tpe":
        proposer_config = ()
    return SearchContract(
        envelope_id="ENVELOPE-TEST-FIXTURE",
        envelope_version=1,
        envelope_content_sha256="sha256:" + "c" * 64,
        contamination_domain_id="DOMAIN-TEST-FIXTURE",
        authority_lineage_version=0,
        authority_lineage_sha256="sha256:" + "0" * 64,
        campaign_id="CAMPAIGN-TEST-001",
        search_id="SEARCH-TEST-001",
        parent_search_id=None,
        reason_for_change=None,
        hypothesis_id="H-TEST-001",
        family_id="FAMILY-TEST",
        hypothesis_fingerprint=fingerprint(definition),
        data_identity="synthetic-development-data",
        data_version="v1",
        repo_sha="a" * 40,
        strategy_spec_id="STRAT-SPEC-0004",
        strategy_spec_hash="sha256:" + "b" * 64,
        parameter_space=(
            ParameterSpec("fast", "int", low=2, high=40),
            ParameterSpec("slow", "int", low=41, high=80),
            ParameterSpec("mode", "categorical", choices=("off", "on")),
            ParameterSpec("threshold", "float", low=0.1, high=0.3, step=0.1, required=False),
        ),
        conditional_rules=(ConditionalParameterRule("threshold", "mode", ("on",)),),
        relational_constraints=(RelationalConstraint("fast", "lt", "slow", "fast_lt_slow"),),
        forbidden_regions=(
            ForbiddenRegion("known_invalid_pair", (("fast", 4), ("slow", 41)), "structural"),
        ),
        objective=ObjectiveSpec("score", "maximize", "deterministic test score"),
        scientific_constraints=("finite objective",),
        max_proposals=max_proposals,
        max_scientific_trials=max_trials,
        wave_size=wave_size,
        concurrency=1,
        split_protocol=SplitProtocol(
            "SPLIT-TEST-001",
            "development-ref",
            "bars[0:80)",
            "FINAL-HOLDOUT-SECRET-REF",
        ),
        proposer=ProposerSpec(backend, optuna.__version__, proposer_config),
        seed=1729,
        policies=SearchPolicies(
            duplicate_policy=duplicate_policy,
            invalid_trial_policy="reject_before_scientific_execution",
            failed_software_trial_policy="retry_same_scientific_trial_id",
            performance_failure_classification="scientific_result",
            pruning_policy="off",
            retry_limit=1,
            stop_rule="proposal_or_trial_budget_exhausted",
        ),
        campaign_proposals_before_search=0,
        campaign_scientific_trials_before_search=0,
    )


class ScriptedAdapter:
    def __init__(self, rows):
        self.rows = iter(rows)
        self.told = []

    def ask(self, _capability):
        number, params = next(self.rows)
        return AdapterProposal(f"scripted:{number}", number, params)

    def tell(self, _capability, handle, *, state, value=None):
        self.told.append((handle, state, value))


def finish_wave(governor, proposals, *, offset=0.0):
    for index, proposal in enumerate(reversed(proposals)):
        governor.submit_result(
            proposal.proposal_id,
            state="performance_result",
            objective_value=offset + index,
            performance_constraints_passed=False,
            detail="bad performance remains a scientific result",
        )
    return governor.finalize_wave()


def test_illegal_forbidden_and_conditional_parameters_are_rejected():
    contract = make_contract()
    assert "parameter outside frozen legal space: fast" in contract.validate_parameters(
        {"fast": 99, "slow": 60, "mode": "off"}
    )
    assert "forbidden region: known_invalid_pair" in contract.validate_parameters(
        {"fast": 4, "slow": 41, "mode": "off"}
    )
    assert "conditional parameter required: threshold" in contract.validate_parameters(
        {"fast": 2, "slow": 60, "mode": "on"}
    )
    assert "conditional parameter must be absent: threshold" in contract.validate_parameters(
        {"fast": 2, "slow": 60, "mode": "off", "threshold": 0.2}
    )


def test_governor_rejects_illegal_proposal_before_scientific_execution():
    governor = SearchGovernor(make_contract(wave_size=1))
    scripted = ScriptedAdapter(
        [
            (0, {"fast": 99, "slow": 60, "mode": "off"}),
            (1, {"fast": 2, "slow": 60, "mode": "off"}),
        ]
    )
    governor._adapter = scripted
    accepted = governor.propose_wave()
    assert len(accepted) == 1
    assert governor.proposal_records[0].status == "REJECTED_INVALID"
    assert governor.proposal_records[0].scientific_trial_id is None
    assert governor.scientific_denominator == 1
    assert scripted.told == [("scripted:0", "invalid", None)]


def test_proposal_and_posthoc_budget_expansion_are_denied():
    governor = SearchGovernor(make_contract(max_proposals=1, max_trials=2, wave_size=1))
    governor._adapter = ScriptedAdapter([(0, {"fast": 2, "slow": 60, "mode": "off"})])
    proposals = governor.propose_wave()
    finish_wave(governor, proposals)
    with pytest.raises(BudgetExhausted):
        governor.propose_wave()
    with pytest.raises(ContractMutationDenied, match="parent-linked new search_id"):
        governor.assert_frozen_contract(replace(governor.contract, max_proposals=2))


def test_final_holdout_access_is_denied_and_not_exposed_to_adapter():
    governor = SearchGovernor(make_contract())
    assert governor.data_reference("development") == "development-ref"
    with pytest.raises(HoldoutAccessDenied):
        governor.data_reference("final_holdout")
    assert "FINAL-HOLDOUT-SECRET-REF" not in json.dumps(governor.adapter_surface)


def test_direct_adapter_construction_without_governor_is_denied():
    contract = make_contract()
    surface = ProposalSurface(
        contract.search_id,
        contract.contract_hash,
        contract.parameter_space,
        contract.conditional_rules,
        contract.proposer,
        contract.seed,
        contract.objective.direction,
    )
    with pytest.raises(AdapterBypassDenied):
        OptunaProposalAdapter(surface)


def test_duplicate_is_visible_and_does_not_increment_denominator():
    governor = SearchGovernor(make_contract(max_proposals=4, max_trials=2, wave_size=1))
    governor._adapter = ScriptedAdapter(
        [
            (0, {"fast": 2, "slow": 60, "mode": "off"}),
            (1, {"fast": 2, "slow": 60, "mode": "off"}),
            (2, {"fast": 3, "slow": 70, "mode": "off"}),
        ]
    )
    first = governor.propose_wave()
    finish_wave(governor, first, offset=1.0)
    second = governor.propose_wave()
    assert second[0].params["fast"] == 3
    assert governor.scientific_denominator == 2
    duplicate = [row for row in governor.proposal_records if row.status.startswith("DUPLICATE")]
    assert len(duplicate) == 1
    assert duplicate[0].scientific_trial_id is None


def test_retry_keeps_one_scientific_identity_and_denominator_slot():
    governor = SearchGovernor(make_contract(wave_size=1))
    proposals = governor.propose_wave()
    proposal = proposals[0]
    first = governor.submit_result(proposal.proposal_id, state="software_failed", detail="boom")
    retry = governor.authorize_retry(proposal.proposal_id)
    assert retry["scientific_trial_id"] == first.scientific_trial_id
    assert retry["counts_as_independent_scientific_observation"] is False
    second = governor.submit_result(
        proposal.proposal_id,
        state="performance_result",
        objective_value=-2.0,
        performance_constraints_passed=False,
    )
    governor.finalize_wave()
    assert governor.scientific_denominator == 1
    assert second.attempt_number == 2
    assert second.counts_as_independent_scientific_observation is False


def test_performance_failure_is_not_software_failure_or_pruning():
    governor = SearchGovernor(make_contract(wave_size=1))
    proposal = governor.propose_wave()[0]
    attempt = governor.submit_result(
        proposal.proposal_id,
        state="performance_result",
        objective_value=-100.0,
        performance_constraints_passed=False,
    )
    governor.finalize_wave()
    assert attempt.state == "PERFORMANCE_RESULT"
    assert attempt.performance_constraints_passed is False
    assert governor.accounting_summary()["performance_pruning"] is False
    with pytest.raises(TrialStateError):
        governor.submit_result(proposal.proposal_id, state="invalid")


def test_performance_informed_change_requires_parent_linked_new_search():
    contract = make_contract()
    successor = contract.successor(
        new_search_id="SEARCH-TEST-002",
        reason_for_change="performance-informed bound change",
        parameter_space=(
            replace(contract.parameter_space[0], high=3),
            *contract.parameter_space[1:],
        ),
        observed_proposals=7,
        observed_scientific_trials=3,
    )
    assert successor.campaign_id == contract.campaign_id
    assert successor.parent_search_id == contract.search_id
    assert successor.search_id != contract.search_id
    assert successor.reason_for_change == "performance-informed bound change"
    assert successor.campaign_proposals_before_search == 7
    assert successor.campaign_scientific_trials_before_search == 3


def test_seeded_sequential_proposals_are_reproducible():
    first = SearchGovernor(make_contract())
    second = SearchGovernor(make_contract())
    first_wave = first.propose_wave()
    second_wave = second.propose_wave()
    assert [row.params for row in first_wave] == [row.params for row in second_wave]
    finish_wave(first, first_wave, offset=1.0)
    finish_wave(second, second_wave, offset=1.0)
    assert [row.params for row in first.propose_wave()] == [
        row.params for row in second.propose_wave()
    ]


def test_snapshot_restart_reproduces_exact_adaptive_continuation():
    governor = SearchGovernor(make_contract())
    first_wave = governor.propose_wave()
    finish_wave(governor, first_wave, offset=1.0)
    snapshot = json.loads(json.dumps(governor.snapshot()))
    restored = SearchGovernor.restore(governor.contract, snapshot)
    assert [row.params for row in governor.propose_wave()] == [
        row.params for row in restored.propose_wave()
    ]


def test_proposal_metadata_is_complete_and_has_no_authority():
    governor = SearchGovernor(make_contract(wave_size=1))
    proposal = governor.propose_wave()[0]
    required = {
        "campaign_id",
        "search_id",
        "hypothesis_id",
        "family_id",
        "hypothesis_fingerprint",
        "contract_hash",
        "data_identity",
        "data_version",
        "repo_sha",
        "proposer_backend",
        "proposer_version",
        "seed",
    }
    payload = proposal.to_dict()
    assert all(payload[name] for name in required)
    assert payload["noncanonical"] is True
    assert payload["canonical_authority"] is False
    assert payload["winner_authority"] is False
    assert payload["promotion_authority"] is False
    assert payload["go_authority"] is False


def test_pinned_optuna_exposes_all_initial_adapter_backends():
    assert supported_backends() == {"tpe": True, "random": True, "qmc": True, "gp": True}


@pytest.mark.parametrize("backend", ["random", "qmc", "gp"])
def test_baseline_and_challenger_backends_propose_only_through_governor(backend):
    governor = SearchGovernor(make_contract(backend=backend, wave_size=1))
    proposal = governor.propose_wave()[0]
    assert proposal.proposer_backend == backend
    assert governor.contract.validate_parameters(proposal.params) == ()


def test_existing_strategy_0004_compiles_with_governed_legal_assignment():
    strategy = json.loads(
        Path("research/strategy_specs/STRAT-SPEC-0004.strategy_spec.json").read_text(
            encoding="utf-8"
        )
    )
    index = pd.date_range("2024-01-01", periods=500, freq="15min", tz="UTC")
    close = 30_000 + np.arange(500) * 2 + np.sin(np.arange(500) / 13) * 100
    ohlcv = pd.DataFrame(
        {
            "open": close - 1,
            "high": close + 5,
            "low": close - 5,
            "close": close,
            "volume": np.full(500, 100.0),
        },
        index=index,
    )
    signal = compile_signal(
        strategy,
        {
            "parameter_values": {
                "fast_lookback_bars": 20,
                "slow_lookback_bars": 100,
                "trend_lookback_bars": 300,
            }
        },
        ohlcv,
    )
    assert signal.index.equals(ohlcv.index)
    assert set(signal.unique()) <= {-1.0, 0.0, 1.0}
