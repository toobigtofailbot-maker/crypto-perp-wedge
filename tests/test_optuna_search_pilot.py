import json
import types
from pathlib import Path

import pytest

from tools.sidecars.optuna_search_pilot import run_optuna_search_pilot as pilot


def test_non_authority_flags_include_package_required_flags():
    assert pilot.NON_AUTHORITY_FLAGS == [
        "scratch_only",
        "non_canonical",
        "not_full_population_evidence",
        "not_oos_evidence",
        "not_robustness_evidence",
        "not_candidate_evidence",
        "not_promotion",
        "not_readiness",
        "not_paper_live",
        "requires_repo_owned_rescreen",
    ]
    assert "Optuna suggestions are not winners." in pilot.GUARDRAIL_STATEMENTS
    assert "No winner-only reporting is allowed." in pilot.GUARDRAIL_STATEMENTS


def test_mock_sampler_exports_all_trial_states_when_optuna_unavailable(monkeypatch):
    monkeypatch.setattr(
        pilot,
        "_load_optuna_optional",
        lambda: (None, "ModuleNotFoundError: No module named 'optuna'"),
    )

    payloads = pilot.build_payloads(trials=20, seed=1729)
    rows = payloads["trial_rows"]
    summary = payloads["summary"]

    assert len(rows) == 20
    assert summary["total_trials"] == 20
    assert summary["complete_count"] == 16
    assert summary["pruned_count"] == 2
    assert summary["fail_count"] == 2
    assert summary["real_optuna_exercised"] is False
    assert summary["execution_status"] == "PARTIAL_BLOCKED_OPTIONAL_DEPENDENCY_UNAVAILABLE"
    assert summary["blocked_reason_or_null"] == "Optuna is not importable in the execution environment."
    assert summary["recommendation"] == "preserve"
    assert {row["state"] for row in rows} == {"COMPLETE", "PRUNED", "FAIL"}
    assert all(row["canonical_authority"] is False for row in rows)
    assert all(row["suggested_by"] == "deterministic_mock_sampler" for row in rows)
    assert all(row["study_id"] == rows[0]["study_id"] for row in rows)


def test_mock_sampler_is_deterministic(monkeypatch):
    monkeypatch.setattr(pilot, "_load_optuna_optional", lambda: (None, "missing"))

    first = pilot.build_payloads(trials=20, seed=1729)
    second = pilot.build_payloads(trials=20, seed=1729)

    assert first["trial_rows"] == second["trial_rows"]
    assert first["summary"] == second["summary"]


class _FakeTrialPruned(Exception):
    pass


class _FakeSampler:
    def __init__(self, seed):
        self.seed = seed


class _FakeState:
    def __init__(self, name):
        self.name = name


class _FakeFrozenTrial:
    def __init__(self, trial, state, value=None):
        self.number = trial.number
        self.params = dict(trial.params)
        self.state = _FakeState(state)
        self.value = value
        self.user_attrs = dict(trial.user_attrs)


class _FakeTrial:
    def __init__(self, number):
        self.number = number
        self.params = {}
        self.user_attrs = {}

    def suggest_int(self, name, low, high):
        value = low + ((self.number * 3) % (high - low + 1))
        self.params[name] = value
        return value

    def suggest_float(self, name, low, high):
        value = low + (self.number % 10) * ((high - low) / 10.0)
        self.params[name] = value
        return value

    def suggest_categorical(self, name, choices):
        value = choices[self.number % len(choices)]
        self.params[name] = value
        return value

    def set_user_attr(self, name, value):
        self.user_attrs[name] = value


class _FakeStudy:
    def __init__(self):
        self.trials = []

    def optimize(self, objective, n_trials, catch):
        for number in range(n_trials):
            trial = _FakeTrial(number)
            try:
                value = objective(trial)
            except _FakeTrialPruned:
                self.trials.append(_FakeFrozenTrial(trial, "PRUNED"))
            except catch:
                self.trials.append(_FakeFrozenTrial(trial, "FAIL"))
            else:
                self.trials.append(_FakeFrozenTrial(trial, "COMPLETE", value))


def _fake_optuna():
    return types.SimpleNamespace(
        __version__="fake-optuna",
        samplers=types.SimpleNamespace(TPESampler=_FakeSampler),
        exceptions=types.SimpleNamespace(TrialPruned=_FakeTrialPruned),
        create_study=lambda **kwargs: _FakeStudy(),
    )


def test_available_optuna_path_exports_full_lineage(monkeypatch):
    monkeypatch.setattr(pilot, "_load_optuna_optional", lambda: (_fake_optuna(), None))

    payloads = pilot.build_payloads(trials=20, seed=1729)
    rows = payloads["trial_rows"]
    summary = payloads["summary"]

    assert summary["real_optuna_exercised"] is True
    assert summary["execution_status"] == "COMPLETED_REAL_OPTUNA_SIDECAR_PILOT"
    assert summary["blocked_reason_or_null"] is None
    assert summary["recommendation"] == "sidecar"
    assert summary["complete_count"] == 16
    assert summary["pruned_count"] == 2
    assert summary["fail_count"] == 2
    assert all(row["suggested_by"] == "optuna_tpe_sampler" for row in rows)
    assert rows[3]["state"] == "PRUNED"
    assert rows[5]["state"] == "FAIL"


def test_run_writes_required_scratch_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(pilot, "_load_optuna_optional", lambda: (None, "missing"))
    monkeypatch.setattr(pilot, "REPO_ROOT", tmp_path)
    output_dir = tmp_path / "scratch" / pilot.PACKAGE_ID

    summary = pilot.run_pilot(output_dir=output_dir, trials=20, seed=1729)

    assert summary["total_trials"] == 20
    assert {path.name for path in output_dir.iterdir()} == {
        "README.md",
        "dependency_probe.json",
        "provenance.json",
        "recommendation_report.md",
        "requirements.poc.txt",
        "search_space.json",
        "trial_population.jsonl",
        "trial_summary.json",
    }
    rows = [
        json.loads(line)
        for line in (output_dir / "trial_population.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(rows) == 20
    assert json.loads((output_dir / "trial_summary.json").read_text(encoding="utf-8")) == summary


def test_output_dir_must_remain_under_scratch(tmp_path):
    with pytest.raises(pilot.OptunaSearchPilotError, match="output-dir must remain under"):
        pilot.run_pilot(output_dir=tmp_path, trials=1, seed=1)


def test_summary_checksum_covers_payload(monkeypatch):
    monkeypatch.setattr(pilot, "_load_optuna_optional", lambda: (None, "missing"))

    summary = pilot.build_payloads(trials=20, seed=1729)["summary"]
    payload = dict(summary)
    checksum = payload.pop("output_checksum")

    assert checksum == pilot._sha256_payload(payload)


def test_source_does_not_invoke_canonical_runner_or_write_canonical_artifacts():
    source = (
        pilot.REPO_ROOT
        / "tools/sidecars/optuna_search_pilot/run_optuna_search_pilot.py"
    ).read_text(encoding="utf-8")

    forbidden_terms = [
        "tools.research_runner",
        "run_offline_sweep",
        "lib.backtest",
        "append_trial",
        "write_result_population",
        "research/result_populations",
        "BINANCE_API",
    ]
    assert not any(term in source for term in forbidden_terms)
