"""Run the bounded, non-canonical Search Governor / Optuna proposal pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import optuna
import pandas as pd

from tools.research_memory.fingerprint import fingerprint
from tools.research_runner.spec_signal_compiler import compile_signal
from tools.research_search.contract import (
    ForbiddenRegion,
    ObjectiveSpec,
    ParameterSpec,
    ProposerSpec,
    RelationalConstraint,
    SearchContract,
    SearchPolicies,
    SplitProtocol,
    canonical_json,
    sha256_payload,
)
from tools.research_search.governor import SearchGovernor
from tools.research_search.optuna_adapter import supported_backends

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ID = "WP-SEARCH-GOVERNOR-OPTUNA-PROPOSAL-PILOT-01"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / PACKAGE_ID
STRATEGY_SPEC_PATH = (
    REPO_ROOT / "research" / "strategy_specs" / "STRAT-SPEC-0007.strategy_spec.json"
)
DEFAULT_SEED = 1729
DEVELOPMENT_BARS = 900
ANNUALIZATION_1D = math.sqrt(365.0)


class GovernedPilotError(RuntimeError):
    """Raised when the non-canonical pilot cannot preserve its boundaries."""


def _source_commit(repo_root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown-noncanonical-pilot-source"
    return completed.stdout.strip()


def _file_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_scratch_output(output_dir: Path, repo_root: Path) -> Path:
    resolved = output_dir.resolve()
    scratch = (repo_root / "scratch").resolve()
    if resolved != scratch and scratch not in resolved.parents:
        raise GovernedPilotError(f"pilot output must remain under {scratch}: {resolved}")
    return resolved


def build_pilot_contract(
    *, repo_root: Path = REPO_ROOT, seed: int = DEFAULT_SEED
) -> SearchContract:
    strategy_path = repo_root / STRATEGY_SPEC_PATH.relative_to(REPO_ROOT)
    strategy = json.loads(strategy_path.read_text(encoding="utf-8"))
    parameter_names = {parameter["name"] for parameter in strategy["free_parameters"]["parameters"]}
    expected_names = {
        "pullback_ema_bars",
        "trend_fast_ema_bars",
        "atr_multiplier",
        "max_holding_bars",
    }
    if parameter_names != expected_names:
        raise GovernedPilotError(
            "STRAT-SPEC-0007 parameter surface changed; pilot contract is stale"
        )
    definition = {
        "strategy_family": "ema pullback continuation",
        "mechanism": "both-direction EMA pullback continuation with ATR and time exits",
        "primary_timeframe": "1d",
        "required_data_features": ["ohlcv", "ema", "atr"],
        "free_parameter_count": 4,
    }
    return SearchContract(
        campaign_id="CAMPAIGN-EMA-PULLBACK-GOVERNED-PILOT-001",
        search_id="SEARCH-EMA-PULLBACK-OPTUNA-TPE-001",
        parent_search_id=None,
        reason_for_change=None,
        hypothesis_id="STRAT-SPEC-0007-NONCANONICAL-PILOT",
        family_id="H-004-R2-EMA-PULLBACK-CONTINUATION",
        hypothesis_fingerprint=fingerprint(definition),
        data_identity="NONCANONICAL-SYNTHETIC-OHLCV-DEVELOPMENT-001",
        data_version="deterministic-wave-score-v1",
        repo_sha=_source_commit(repo_root),
        strategy_spec_id="STRAT-SPEC-0007",
        strategy_spec_hash=_file_sha256(strategy_path),
        parameter_space=(
            ParameterSpec("pullback_ema_bars", "int", low=10, high=30, step=10),
            ParameterSpec("trend_fast_ema_bars", "int", low=40, high=60, step=10),
            ParameterSpec("atr_multiplier", "float", low=2.0, high=3.0, step=0.5),
            ParameterSpec("max_holding_bars", "int", low=30, high=60, step=15),
        ),
        conditional_rules=(),
        relational_constraints=(
            RelationalConstraint(
                "pullback_ema_bars",
                "lt",
                "trend_fast_ema_bars",
                "pullback_lt_trend",
            ),
        ),
        forbidden_regions=(
            ForbiddenRegion(
                "exclude_shortest_horizon_tightest_stop_corner",
                (
                    ("pullback_ema_bars", 30),
                    ("trend_fast_ema_bars", 40),
                    ("atr_multiplier", 2.0),
                    ("max_holding_bars", 30),
                ),
                "Frozen structural exclusion: shortest trend gap, tightest stop, shortest hold.",
            ),
        ),
        objective=ObjectiveSpec(
            "development_signal_score_v1",
            "maximize",
            (
                "Daily-annualized mean/std of next-bar synthetic development returns multiplied by "
                "the existing compiler signal; non-canonical and not a project winner metric."
            ),
        ),
        scientific_constraints=(
            "compiled signal contains only {-1, 0, 1}",
            "objective is finite",
            "at least one position transition is observed",
        ),
        max_proposals=20,
        max_scientific_trials=4,
        wave_size=2,
        concurrency=2,
        split_protocol=SplitProtocol(
            "SPLIT-NONCANONICAL-SYNTHETIC-001",
            "NONCANONICAL-SYNTHETIC-OHLCV-DEVELOPMENT-001",
            "synthetic daily bars [0,900); proposer/evaluator accessible",
            "FINAL-HOLDOUT-NONCANONICAL-SYNTHETIC-OPAQUE-001",
        ),
        proposer=ProposerSpec(
            "tpe",
            optuna.__version__,
            (("multivariate", True), ("group", True), ("n_startup_trials", 2)),
        ),
        seed=seed,
        policies=SearchPolicies(
            duplicate_policy="reject_and_charge",
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


def _development_ohlcv(seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    bar = np.arange(DEVELOPMENT_BARS, dtype=float)
    cycle = 240.0 * np.sin(bar / 19.0) + 120.0 * np.sin(bar / 53.0)
    drift = 1.7 * bar
    noise = rng.normal(0.0, 18.0, DEVELOPMENT_BARS).cumsum() * 0.15
    close = 30_000.0 + drift + cycle + noise
    open_ = np.concatenate(([close[0] - 2.0], close[:-1]))
    high = np.maximum(open_, close) + 8.0
    low = np.minimum(open_, close) - 8.0
    volume = 100.0 + 10.0 * (1.0 + np.sin(bar / 11.0))
    index = pd.date_range("2020-01-01", periods=DEVELOPMENT_BARS, freq="1D", tz="UTC")
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=index,
    )


def _evaluate(
    strategy: dict[str, Any],
    ohlcv: pd.DataFrame,
    params: dict[str, Any],
) -> tuple[float, bool, str]:
    signal = compile_signal(strategy, {"parameter_values": params}, ohlcv)
    if not set(signal.unique()) <= {-1.0, 0.0, 1.0}:
        raise GovernedPilotError("compiler returned a signal outside {-1,0,1}")
    returns = ohlcv["close"].pct_change().shift(-1)
    strategy_returns = (signal * returns).dropna()
    standard_deviation = float(strategy_returns.std(ddof=0))
    score = (
        float(strategy_returns.mean()) / standard_deviation * ANNUALIZATION_1D
        if standard_deviation > 0.0
        else -1_000_000.0
    )
    transitions = int(signal.diff().fillna(signal).ne(0.0).sum())
    finite = math.isfinite(score)
    constraints_passed = finite and transitions > 0
    detail = f"finite={finite};position_transitions={transitions}"
    return round(score, 12), constraints_passed, detail


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(canonical_json(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def _contradiction_map(contract: SearchContract) -> dict[str, Any]:
    return {
        "pilot_source_repo_sha": contract.repo_sha,
        "equivalent_governor_found": False,
        "prior_optuna_surface": (
            "tools/sidecars/optuna_search_pilot is scratch-only prior art without Governor "
            "legality, budget, holdout, anti-laundering, or retry authority"
        ),
        "legal_parameter_representation": (
            "STRAT-SPEC-0007 declared numeric ranges/allowed values; no grammar mutation"
        ),
        "conditional_rules": "Governor contract supports them; pilot family declares none",
        "forbidden_regions": "Governor-owned exact structural exclusions",
        "budget_representation": "separate frozen proposal and scientific-trial budgets",
        "holdout_location": (
            "opaque final_holdout_ref retained only in Governor contract; proposer surface omits it"
        ),
        "trial_state_mapping": (
            "performance_result, software_failed, rejected_invalid, duplicate; pruning off"
        ),
        "lineage_identities": (
            "campaign/search/parent/hypothesis/family/data/repo/proposer/seed on proposals"
        ),
        "runner_overlap": (
            "existing offline runner forbids adaptive search and remains unchanged; pilot uses "
            "the existing compiler only and writes scratch output"
        ),
        "research_memory_use": (
            "deterministic hypothesis fingerprint only; no historical performance prior"
        ),
        "stop_condition_triggered": False,
    }


def run_pilot(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    repo_root: Path = REPO_ROOT,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    output_dir = _assert_scratch_output(output_dir, repo_root)
    contract = build_pilot_contract(repo_root=repo_root, seed=seed)
    strategy_path = repo_root / STRATEGY_SPEC_PATH.relative_to(REPO_ROOT)
    strategy = json.loads(strategy_path.read_text(encoding="utf-8"))
    ohlcv = _development_ohlcv(seed)

    governor = SearchGovernor(contract)
    if contract.split_protocol.final_holdout_ref in canonical_json(governor.adapter_surface):
        raise GovernedPilotError("final holdout leaked into proposer surface")
    first_wave = governor.propose_wave()
    for proposal in reversed(first_wave):
        score, constraints_passed, detail = _evaluate(strategy, ohlcv, proposal.params)
        governor.submit_result(
            proposal.proposal_id,
            state="performance_result",
            objective_value=score,
            performance_constraints_passed=constraints_passed,
            detail=detail,
        )
    governor.finalize_wave()
    wave_one_snapshot = json.loads(json.dumps(governor.snapshot()))

    continuation_a = SearchGovernor.restore(contract, wave_one_snapshot)
    continuation_b = SearchGovernor.restore(contract, wave_one_snapshot)
    second_a = continuation_a.propose_wave()
    second_b = continuation_b.propose_wave()
    continuation_reproduced = [row.params for row in second_a] == [row.params for row in second_b]
    if not continuation_reproduced:
        raise GovernedPilotError("exact adaptive continuation replay diverged")
    for proposal in reversed(second_a):
        score, constraints_passed, detail = _evaluate(strategy, ohlcv, proposal.params)
        continuation_a.submit_result(
            proposal.proposal_id,
            state="performance_result",
            objective_value=score,
            performance_constraints_passed=constraints_passed,
            detail=detail,
        )
    continuation_a.finalize_wave()
    final_state = continuation_a.snapshot()
    accounting = continuation_a.accounting_summary()
    summary = {
        "package_id": PACKAGE_ID,
        "execution_status": "COMPLETED_NONCANONICAL_GOVERNED_OPTUNA_PILOT",
        "pilot_family": "STRAT-SPEC-0007 H-004-R2 EMA Pullback Continuation",
        "contract_hash": contract.contract_hash,
        "optuna_version": optuna.__version__,
        "proposer_backend": contract.proposer.backend,
        "proposer_config": dict(contract.proposer.config),
        "supported_proposer_set": {
            **supported_backends(),
            "gp_posture": "adapter-capable experimental challenger; not exercised by this pilot",
        },
        "proposal_count": len(continuation_a.proposal_records),
        "accepted_scientific_trials": continuation_a.scientific_denominator,
        "trial_attempt_count": len(continuation_a.trial_attempts),
        "proposal_budget": contract.max_proposals,
        "scientific_trial_budget": contract.max_scientific_trials,
        "ordered_tell_independent_of_completion_order": True,
        "seeded_sequential_reproducibility": True,
        "snapshot_restore_exact_continuation": continuation_reproduced,
        "snapshot_restore_method": (
            "seeded exact operation replay with proposal verification; no claim that study "
            "history alone reproduces continuation"
        ),
        "legal_parameter_space_frozen_before_proposal": True,
        "invalid_proposals_execute_scientifically": False,
        "final_holdout_exposed_to_proposer": False,
        "hidden_performance_prior_used": False,
        "performance_pruning": False,
        "canonical_result_population_write": False,
        "canonical_trial_log_write": False,
        "winner_or_best_trial_authority": False,
        "go_or_promotion_authority": False,
        "noncanonical": True,
        "accounting": accounting,
    }
    summary["summary_hash"] = sha256_payload(summary)

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "contradiction_map.json", _contradiction_map(contract))
    _write_json(output_dir / "search_contract.json", contract.to_dict())
    _write_json(
        output_dir / "proposer_state_after_wave_1.json", wave_one_snapshot["adapter_snapshot"]
    )
    _write_json(output_dir / "governor_final_state.json", final_state)
    _write_jsonl(
        output_dir / "proposal_records.jsonl",
        [record.to_dict() for record in continuation_a.proposal_records],
    )
    _write_jsonl(
        output_dir / "trial_attempts.jsonl",
        [attempt.to_dict() for attempt in continuation_a.trial_attempts],
    )
    _write_json(output_dir / "pilot_summary.json", summary)
    (output_dir / "README.md").write_text(
        "# Governed Optuna proposal pilot\n\n"
        "NON-CANONICAL scratch proof only. Optuna proposed parameters behind the "
        "project-owned Search Governor. No winner, GO, promotion, canonical evidence, "
        "paper/live, runtime, or execution authority is created.\n",
        encoding="utf-8",
    )
    return summary


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        summary = run_pilot(output_dir=args.output_dir, seed=args.seed)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
