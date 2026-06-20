from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from tools.research_runner import run_offline_sweep as runner
from tools.walkforward import run_walkforward_scratch as subject


REPO_ROOT = Path(__file__).resolve().parents[1]


def _fold(fold_id: str, order: int, start: str) -> dict:
    start_ts = pd.Timestamp(start)
    selection_end = start_ts + pd.Timedelta(hours=6)
    evaluation_end = selection_end + pd.Timedelta(hours=6)
    return {
        "fold_id": fold_id,
        "fold_order": order,
        "selection_window_start_utc": start_ts.isoformat().replace("+00:00", "Z"),
        "selection_window_end_utc": selection_end.isoformat().replace("+00:00", "Z"),
        "evaluation_window_start_utc": selection_end.isoformat().replace("+00:00", "Z"),
        "evaluation_window_end_utc": evaluation_end.isoformat().replace("+00:00", "Z"),
        "warmup_window_start_utc": None,
        "warmup_window_end_utc": None,
        "purge": {"mode": "none", "bars": None, "duration": None},
        "embargo": {"mode": "none", "bars": None, "duration": None},
        "result_population_ref": None,
        "planned_result_population_ref": f"scratch:not-created:{fold_id}",
        "declared_variant_count": 8,
        "successful_count": None,
        "failed_count": None,
        "errored_count": None,
        "invalid_count": None,
        "data_unavailable_count": None,
        "not_attempted_count": None,
        "gap_posture": {
            "missing_data_policy": "mark_data_unavailable",
            "irreparable_gap_policy": "consult_irreparable_gaps_manifest",
            "silent_interpolation_forbidden": True,
        },
        "lineage_refs": [
            {"ref_id": "spec", "ref_type": "strategy_spec", "ref": "research/strategy_specs/STRAT-SPEC-0004.strategy_spec.json"},
            {"ref_id": "vm", "ref_type": "variant_manifest", "ref": "research/variant_manifests/VM-0004.variant_manifest.json"},
            {"ref_id": "sweep", "ref_type": "sweep_plan", "ref": "research/sweep_plans/SWEEP-PLAN-0004.sweep_plan.json"},
        ],
    }


def _manifest() -> dict:
    return {
        "schema_version": "v1",
        "manifest_id": "WFM-9001",
        "created_at_utc": "2026-06-20T12:00:00Z",
        "source_commit": "fcb8a8f",
        "non_authority_declaration": {
            "not_executable": True,
            "not_runner_authority": True,
            "not_result_population_write_authority": True,
            "not_canonical_result_population": True,
            "not_candidate_approval": True,
            "not_ranking_authority": True,
            "not_recommendation_authority": True,
            "not_readiness_authority": True,
            "not_promotion_authority": True,
            "not_gate_authority": True,
            "not_runtime_authority": True,
            "not_paper_live_authority": True,
            "not_broker_exchange_order_authority": True,
        },
        "strategy_spec_id": "STRAT-SPEC-0004",
        "variant_manifest_id": "VM-0004",
        "sweep_plan_id": "SWEEP-PLAN-0004",
        "data_slice_id": "TEST-SLICE",
        "timeframe": "15m",
        "timezone": "UTC",
        "boundary_semantics": "start_inclusive_end_exclusive",
        "window_policy": {
            "policy_id": "test",
            "window_type": "custom_explicit",
            "fold_construction": "explicit_manifest_boundaries",
            "overlap_policy": "selection_evaluation_overlap_forbidden",
            "declared_before_evaluation": True,
        },
        "selection_rule": {
            "rule_id": "carry_full_population",
            "rule_type": "carry_full_population",
            "description": "Carry all included variants.",
            "declared_before_evaluation": True,
            "winner_only_selection_forbidden": True,
            "denominator_preservation": "all_declared_variants_remain_visible",
        },
        "folds": [_fold("FOLD-001", 1, "2026-01-01T00:00:00Z"), _fold("FOLD-002", 2, "2026-01-01T12:00:00Z")],
    }


def _execution_input() -> runner._ExecutionInput:  # noqa: SLF001
    index = pd.date_range("2026-01-01T00:00:00Z", periods=96, freq="15min")
    ohlcv = pd.DataFrame(
        {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1.0},
        index=index,
    )
    funding = pd.DataFrame({"funding_rate": 0.0}, index=pd.date_range(index[0], periods=3, freq="8h"))
    return runner._ExecutionInput(  # noqa: SLF001
        mode="test",
        execution_provenance_class="test",
        ohlcv=ohlcv,
        funding=funding,
        timeframe="15m",
        data_catalog_ref="TEST-CATALOG",
        data_slice_identity="TEST-SLICE",
        environment_summary=[],
        data_coverage_notes=[],
    )


def _fake_metrics(strategy_spec, variant, execution_input, sizing_mode, target_leverage):
    del strategy_spec, sizing_mode, target_leverage
    value = float(int(variant["variant_id"].split("-")[-1]))
    oos = "evaluation" in execution_input.mode
    sharpe = value / 10.0 - (0.1 if oos else 0.0)
    return {
        "pnl": value - (1.0 if oos else 0.0),
        "return_pct": value / 100.0 - (0.01 if oos else 0.0),
        "drawdown": value / 100.0 + (0.01 if oos else 0.0),
        "trade_count": int(value),
        "win_rate": 0.5,
        "sharpe": sharpe,
        "fees": 1.0,
        "funding": 0.0,
        "slippage": 0.25,
        "exposure": 1.0,
    }


def test_scratch_run_preserves_fold_and_variant_order_without_canonical_writes(tmp_path, monkeypatch):
    monkeypatch.setattr(subject, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(subject, "_source_commit", lambda: "fcb8a8f7fd54c6a12beaa2743e065979ec124d20")
    monkeypatch.setattr(subject, "_load_execution_input", lambda *args: _execution_input())
    monkeypatch.setattr(runner, "_run_window_variant_backtest", _fake_metrics)
    scratch = tmp_path / "scratch" / "WP-LAB-WALKFORWARD-RUN-01"
    scratch.mkdir(parents=True)
    manifest_path = scratch / "walkforward_fold_manifest.input.json"
    manifest_path.write_text(json.dumps(_manifest()), encoding="utf-8")
    canonical_before = sorted((REPO_ROOT / "research" / "result_populations").glob("*.json"))

    kwargs = {
        "walkforward_manifest_path": manifest_path,
        "strategy_spec_path": REPO_ROOT / "research" / "strategy_specs" / "STRAT-SPEC-0004.strategy_spec.json",
        "variant_manifest_path": REPO_ROOT / "research" / "variant_manifests" / "VM-0004.variant_manifest.json",
        "sweep_plan_path": REPO_ROOT / "research" / "sweep_plans" / "SWEEP-PLAN-0004.sweep_plan.json",
        "ohlcv_input_path": tmp_path / "unused.csv",
        "output_dir": scratch,
        "created_at_utc": "2026-06-20T12:00:00Z",
    }
    report_path, fragment_path = subject.run_walkforward_scratch(**kwargs)
    first = report_path.read_bytes()
    subject.run_walkforward_scratch(**kwargs)
    assert report_path.read_bytes() == first
    report = json.loads(report_path.read_text())
    assert [fold["fold_id"] for fold in report["fold_results"]] == ["FOLD-001", "FOLD-002"]
    assert [row["variant_id"] for row in report["fold_results"][0]["variant_results"]] == [
        f"VAR-{index:06d}" for index in range(1, 9)
    ]
    assert report["aggregate_degradation"]["comparable_variant_pairs"] == 16
    assert report["canonical_authority"] is False
    assert fragment_path.exists()
    assert sorted((REPO_ROOT / "research" / "result_populations").glob("*.json")) == canonical_before


def test_output_outside_scratch_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(subject, "REPO_ROOT", tmp_path)
    with pytest.raises(subject.WalkForwardScratchError, match="output must remain"):
        subject._assert_scratch_path(tmp_path / "reports")


def test_invalid_manifest_is_rejected_before_execution(tmp_path, monkeypatch):
    monkeypatch.setattr(subject, "REPO_ROOT", tmp_path)
    scratch = tmp_path / "scratch" / "WP-LAB-WALKFORWARD-RUN-01"
    scratch.mkdir(parents=True)
    manifest = _manifest()
    manifest["canonical_write"] = True
    manifest_path = scratch / "invalid.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(subject.WalkForwardScratchError, match="invalid walk-forward"):
        subject.run_walkforward_scratch(
            walkforward_manifest_path=manifest_path,
            strategy_spec_path=REPO_ROOT / "research" / "strategy_specs" / "STRAT-SPEC-0004.strategy_spec.json",
            variant_manifest_path=REPO_ROOT / "research" / "variant_manifests" / "VM-0004.variant_manifest.json",
            sweep_plan_path=REPO_ROOT / "research" / "sweep_plans" / "SWEEP-PLAN-0004.sweep_plan.json",
            ohlcv_input_path=tmp_path / "unused.csv",
            output_dir=scratch,
            created_at_utc="2026-06-20T12:00:00Z",
        )
