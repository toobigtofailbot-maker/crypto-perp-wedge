import json
import types
from pathlib import Path

import pandas as pd
import pytest

from tools.external_pilots import vectorbt_sweep_comparator as pilot


class _FakeTrades:
    def count(self):
        return 1


class _FakePortfolio:
    trades = _FakeTrades()

    def value(self):
        index = pd.date_range("2026-01-01", periods=3, freq="15min", tz="UTC")
        return pd.Series([10_000.0, 10_100.0, 10_050.0], index=index)


class _FakePortfolioFactory:
    calls = []

    @classmethod
    def from_signals(cls, **kwargs):
        cls.calls.append(kwargs)
        return _FakePortfolio()


def _fake_vbt():
    _FakePortfolioFactory.calls = []
    return types.SimpleNamespace(__version__="fake-vectorbt", Portfolio=_FakePortfolioFactory)


def test_non_canonical_labels_are_complete():
    assert pilot.NON_CANONICAL_LABELS == [
        "NON-CANONICAL EXTERNAL SIDECAR OUTPUT",
        "NOT A RESULT POPULATION",
        "NOT STRATEGY AUTHORITY",
        "NOT VM/SWEEP AUTHORITY",
        "NOT CANDIDATE EVIDENCE",
        "NOT PAPER/LIVE/RUNTIME AUTHORITY",
    ]


def test_execution_signals_shift_repo_desired_position_to_fill_bar():
    index = pd.date_range("2026-01-01", periods=5, freq="15min", tz="UTC")
    signal = pd.Series([0.0, 1.0, 1.0, -1.0, 0.0], index=index)

    long_entries, long_exits, short_entries, short_exits = pilot._execution_signals(signal)

    assert long_entries.tolist() == [False, False, True, False, False]
    assert long_exits.tolist() == [False, False, False, False, True]
    assert short_entries.tolist() == [False, False, False, False, True]
    assert short_exits.tolist() == [False, False, False, False, False]


def test_vectorbt_run_uses_repo_compiler_signal_and_noncanonical_semantics(monkeypatch):
    index = pd.date_range("2026-01-01", periods=4, freq="15min", tz="UTC")
    ohlcv = pd.DataFrame(
        {
            "open": [100.0, 101.0, 102.0, 103.0],
            "high": [101.0, 102.0, 103.0, 104.0],
            "low": [99.0, 100.0, 101.0, 102.0],
            "close": [100.5, 101.5, 102.5, 103.5],
            "volume": [1000.0] * 4,
        },
        index=index,
    )
    signal = pd.Series([0.0, 1.0, 1.0, 0.0], index=index)

    def fake_compile_signal(strategy_spec, variant, frame):
        assert strategy_spec["strategy_spec_id"] == "STRAT-SPEC-TEST"
        assert variant["variant_id"] == "VAR-000001"
        assert frame is ohlcv
        return signal

    monkeypatch.setattr(pilot, "compile_signal", fake_compile_signal)

    payload = pilot._run_vectorbt_once(
        vbt=_fake_vbt(),
        strategy_spec={"strategy_spec_id": "STRAT-SPEC-TEST"},
        variants=[{"variant_id": "VAR-000001", "parameter_values": {}}],
        ohlcv=ohlcv,
        funding=pd.DataFrame(index=index),
        timeframe="15m",
    )

    assert payload["labels"] == pilot.NON_CANONICAL_LABELS
    assert payload["vectorbt_version"] == "fake-vectorbt"
    assert payload["variant_rows"][0]["variant_id"] == "VAR-000001"
    assert payload["semantics"]["sizing"].startswith("vectorbt size_type=percent")
    call = _FakePortfolioFactory.calls[0]
    assert call["price"].equals(ohlcv["open"])
    assert call["size"] == 1.0
    assert call["size_type"] == "percent"
    assert call["fees"] == 0.0004
    assert call["slippage"] == 0.0001


def test_comparison_marks_deterministic_vectorbt_differences_explained():
    repo_row = {
        "variant_id": "VAR-000001",
        "metrics": {
            "trade_count": 2,
            "return_pct": 0.1,
            "drawdown": 0.2,
            "sharpe": 1.0,
        },
    }
    vectorbt_row = {
        "variant_id": "VAR-000001",
        "metrics": {
            "trade_count": 1,
            "return_pct": 0.05,
            "drawdown": 0.1,
            "sharpe": 0.5,
        },
    }

    report = pilot._comparison(
        vectorbt_run_1={
            "variant_rows": [vectorbt_row],
            "determinism_hash": "sha256:" + "1" * 64,
            "wall_clock_seconds": 1.0,
        },
        vectorbt_run_2={
            "variant_rows": [vectorbt_row],
            "determinism_hash": "sha256:" + "1" * 64,
            "wall_clock_seconds": 1.0,
        },
        repo_baseline={"variant_rows": [repo_row], "wall_clock_seconds": 2.0},
        rp_comparator={
            "lineage": {
                "strategy_spec_id": "STRAT-SPEC-0004",
                "variant_manifest_id": "VM-0004",
                "sweep_plan_id": "SWEEP-PLAN-0004",
            },
            "result_population_id": "RP-2592",
            "data_coverage_summary": {"data_slice_identity": "slice"},
        },
    )

    assert report["recommendation"] == "EXPLORATION_ONLY"
    assert report["determinism_match"] is True
    assert report["matched_variants"] == []
    assert report["explained_difference_variants"] == ["VAR-000001"]
    assert report["unexplained_difference_variants"] == []


def test_comparison_marks_missing_vectorbt_row_unexplained():
    repo_row = {
        "variant_id": "VAR-000001",
        "metrics": {
            "trade_count": 2,
            "return_pct": 0.1,
            "drawdown": 0.2,
            "sharpe": 1.0,
        },
    }

    report = pilot._comparison(
        vectorbt_run_1={
            "variant_rows": [],
            "determinism_hash": "sha256:" + "1" * 64,
            "wall_clock_seconds": 1.0,
        },
        vectorbt_run_2={
            "variant_rows": [],
            "determinism_hash": "sha256:" + "1" * 64,
            "wall_clock_seconds": 1.0,
        },
        repo_baseline={"variant_rows": [repo_row], "wall_clock_seconds": 2.0},
        rp_comparator={
            "lineage": {
                "strategy_spec_id": "STRAT-SPEC-0004",
                "variant_manifest_id": "VM-0004",
                "sweep_plan_id": "SWEEP-PLAN-0004",
            },
            "result_population_id": "RP-2592",
            "data_coverage_summary": {"data_slice_identity": "slice"},
        },
    )

    assert report["recommendation"] == "BLOCKED"
    assert report["explained_difference_variants"] == []
    assert report["unexplained_difference_variants"] == ["VAR-000001"]
    assert report["variant_comparisons"][0]["unexplained_difference_notes"] == [
        "no vectorbt row produced"
    ]


def test_run_pilot_writes_only_requested_scratch_outputs(tmp_path, monkeypatch):
    report = {
        "recommendation": "EXPLORATION_ONLY",
        "determinism_match": True,
        "matched_variants": [],
        "explained_difference_variants": ["VAR-000001"],
        "unexplained_difference_variants": [],
        "fixture": {
            "strategy_spec_id": "STRAT-SPEC-0004",
            "variant_manifest_id": "VM-0004",
            "sweep_plan_id": "SWEEP-PLAN-0004",
            "rp_comparator_id": "RP-2592",
            "data_slice_identity": "slice",
        },
        "vectorbt_wall_clock_seconds": 1.0,
        "repo_runner_wall_clock_seconds": 2.0,
        "speed_ratio_vectorbt_over_repo": 0.5,
        "variant_comparisons": [],
    }

    monkeypatch.setattr(pilot, "_load_vectorbt", lambda: _fake_vbt())
    monkeypatch.setattr(pilot, "_resolve_ohlcv_path", lambda catalog, explicit: Path("fixture.csv"))
    monkeypatch.setattr(
        pilot,
        "_load_fixture_context",
        lambda **kwargs: {
            "strategy_spec": {"strategy_spec_id": "STRAT-SPEC-0004"},
            "manifest": {"variant_assignments": []},
            "sweep_plan": {"test_selection": {"selected_variant_ids": []}},
            "execution_input": types.SimpleNamespace(
                ohlcv=pd.DataFrame(), funding=pd.DataFrame(), timeframe="15m"
            ),
        },
    )
    monkeypatch.setattr(
        pilot,
        "_load_json",
        lambda path: {
            "lineage": {"strategy_spec_id": "STRAT-SPEC-0004"},
            "result_population_id": "RP-2592",
        },
    )
    monkeypatch.setattr(pilot, "_run_repo_baseline", lambda **kwargs: {"variant_rows": []})
    monkeypatch.setattr(pilot, "_run_vectorbt_once", lambda **kwargs: {"variant_rows": []})
    monkeypatch.setattr(pilot, "_comparison", lambda **kwargs: report)

    result = pilot.run_pilot(output_dir=tmp_path)

    assert result == report
    expected = {
        "vectorbt_run_1.json",
        "vectorbt_run_2.json",
        "runner_baseline.json",
        "comparison_report.json",
        "comparison_report.md",
    }
    assert {path.name for path in tmp_path.iterdir()} == expected
    comparison = json.loads((tmp_path / "comparison_report.json").read_text(encoding="utf-8"))
    assert comparison["recommendation"] == "EXPLORATION_ONLY"


def test_missing_vectorbt_fails_closed(monkeypatch):
    real_import = __import__

    def blocked_import(name, *args, **kwargs):
        if name == "vectorbt":
            raise ModuleNotFoundError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", blocked_import)

    with pytest.raises(pilot.VectorbtPilotError, match="vectorbt is not installed"):
        pilot._load_vectorbt()
