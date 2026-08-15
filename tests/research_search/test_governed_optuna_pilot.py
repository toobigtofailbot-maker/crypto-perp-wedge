import json
import shutil
from pathlib import Path

import pytest

from tools.research_search import run_governed_optuna_pilot as pilot


def _temp_repo(tmp_path):
    strategy_dir = tmp_path / "research" / "strategy_specs"
    strategy_dir.mkdir(parents=True)
    shutil.copy2(
        pilot.STRATEGY_SPEC_PATH,
        strategy_dir / pilot.STRATEGY_SPEC_PATH.name,
    )
    return tmp_path


def test_pilot_contract_reuses_existing_0007_surface_without_grammar_change():
    contract = pilot.build_pilot_contract()
    assert contract.strategy_spec_id == "STRAT-SPEC-0007"
    assert [parameter.name for parameter in contract.parameter_space] == [
        "pullback_ema_bars",
        "trend_fast_ema_bars",
        "atr_multiplier",
        "max_holding_bars",
    ]
    assert contract.max_proposals == 20
    assert contract.max_scientific_trials == 4
    assert contract.policies.pruning_policy == "off"
    assert contract.authority.mode == "noncanonical"


def test_pilot_writes_noncanonical_proof_and_keeps_holdout_out_of_proposer(tmp_path):
    repo_root = _temp_repo(tmp_path)
    output_dir = repo_root / "scratch" / pilot.PACKAGE_ID
    summary = pilot.run_pilot(output_dir=output_dir, repo_root=repo_root)

    assert summary["execution_status"] == "COMPLETED_NONCANONICAL_GOVERNED_OPTUNA_PILOT"
    assert summary["accepted_scientific_trials"] <= summary["scientific_trial_budget"]
    assert summary["proposal_count"] <= summary["proposal_budget"]
    assert summary["snapshot_restore_exact_continuation"] is True
    assert summary["final_holdout_exposed_to_proposer"] is False
    assert summary["canonical_result_population_write"] is False
    assert summary["winner_or_best_trial_authority"] is False
    assert summary["go_or_promotion_authority"] is False

    snapshot_text = (output_dir / "proposer_state_after_wave_1.json").read_text(encoding="utf-8")
    contract = json.loads((output_dir / "search_contract.json").read_text(encoding="utf-8"))
    holdout_ref = contract["split_protocol"]["final_holdout_ref"]
    assert holdout_ref not in snapshot_text
    assert json.loads(snapshot_text)["contains_final_holdout"] is False

    proposals = [
        json.loads(line)
        for line in (output_dir / "proposal_records.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    accepted = [row for row in proposals if row["scientific_trial_id"] is not None]
    assert len(accepted) == summary["accepted_scientific_trials"]
    assert all(row["noncanonical"] is True for row in proposals)
    assert all(row["canonical_authority"] is False for row in proposals)
    assert all(row["winner_authority"] is False for row in proposals)


def test_pilot_output_is_confined_to_scratch(tmp_path):
    repo_root = _temp_repo(tmp_path)
    with pytest.raises(pilot.GovernedPilotError, match="must remain under"):
        pilot.run_pilot(output_dir=repo_root / "outside", repo_root=repo_root)


def test_pilot_source_does_not_use_project_winner_or_canonical_writer_authority():
    source = Path(pilot.__file__).read_text(encoding="utf-8")
    forbidden = [
        "study.best_trial",
        "run_offline_sweep",
        "append_trial(",
        "write_result_population",
    ]
    assert not any(term in source for term in forbidden)
