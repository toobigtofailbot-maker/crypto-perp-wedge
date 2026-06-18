import json
import math
import types
from pathlib import Path

import pandas as pd
import pytest

from tools.external_pilots import analytics_metrics_pilot as pilot


def _fixture_result_population() -> dict:
    return {
        "result_population_id": "RP-9001",
        "lineage": {
            "strategy_spec_id": "STRAT-SPEC-9001",
            "variant_manifest_id": "VM-9001",
            "sweep_plan_id": "SWEEP-PLAN-9001",
        },
        "data_coverage_summary": {
            "data_slice_identity": "fixture:sha256:abc",
            "timeframe": "15m",
        },
        "variant_result_rows": [
            {
                "variant_id": "VAR-000002",
                "row_id": "RP-9001-ROW-000002",
                "attempted": True,
                "outcome_category": "successful",
                "metrics": {
                    "return_pct": -0.02,
                    "drawdown": 0.03,
                    "sharpe": -0.4,
                    "trade_count": 2,
                    "win_rate": 0.5,
                    "fees": 2.0,
                    "funding": 0.0,
                    "slippage": 0.5,
                },
            },
            {
                "variant_id": "VAR-000001",
                "row_id": "RP-9001-ROW-000001",
                "attempted": True,
                "outcome_category": "successful",
                "metrics": {
                    "return_pct": 0.10,
                    "drawdown": 0.01,
                    "sharpe": 1.0,
                    "trade_count": 1,
                    "win_rate": 1.0,
                    "fees": 1.0,
                    "funding": 0.0,
                    "slippage": 0.25,
                },
            },
        ],
    }


def _write_fixture(path: Path) -> Path:
    path.write_text(json.dumps(_fixture_result_population(), indent=2), encoding="utf-8")
    return path


def _fake_empyrical():
    def cum_returns_final(returns):
        return float((1.0 + returns.astype(float)).prod() - 1.0)

    def max_drawdown(returns):
        equity = pd.Series([1.0, *((1.0 + returns.astype(float)).cumprod().tolist())])
        drawdown = (equity - equity.cummax()) / equity.cummax()
        return float(drawdown.min())

    def tail_ratio(returns):
        lower = float(returns.quantile(0.05))
        upper = float(returns.quantile(0.95))
        return abs(upper / lower)

    return types.SimpleNamespace(
        __version__="fake-empyrical",
        cum_returns_final=cum_returns_final,
        max_drawdown=max_drawdown,
        tail_ratio=tail_ratio,
    )


def test_non_canonical_labels_are_complete():
    assert pilot.NON_CANONICAL_LABELS == [
        "NON-CANONICAL EXTERNAL ANALYTICS PILOT OUTPUT",
        "NOT A RESULT POPULATION",
        "NOT SCREEN-GATE AUTHORITY",
        "NOT STRATEGY / VM / SWEEP AUTHORITY",
        "NOT CANDIDATE EVIDENCE",
        "NOT PAPER / LIVE / RUNTIME AUTHORITY",
    ]


def test_fake_empyrical_matches_formula_metrics(tmp_path):
    report = pilot.build_report(
        rp_fixture_path=_write_fixture(tmp_path / "RP-9001.result_population.json"),
        empyrical_module=_fake_empyrical(),
        load_external=False,
    )

    assert report["external_engine"]["available"] is True
    assert report["external_engine"]["version"] == "fake-empyrical"
    statuses = {row["metric_name"]: row["status"] for row in report["metric_comparison"]}
    assert statuses["cumulative_return"] == "matched"
    assert statuses["max_drawdown"] == "matched"
    assert statuses["tail_ratio"] == "matched"
    assert statuses["annualized_sharpe"] == "unsupported"
    assert report["recommendation"] == "FORMULA_ADAPT_ONLY"


def test_formula_only_report_is_deterministic_and_explicit(tmp_path):
    fixture = _write_fixture(tmp_path / "RP-9001.result_population.json")

    first = pilot.build_report(rp_fixture_path=fixture, load_external=False)
    second = pilot.build_report(rp_fixture_path=fixture, load_external=False)

    assert first == second
    assert first["dependency_mode"] == "formula_adapter_only_no_repo_dependency_change"
    assert first["external_engine"]["available"] is False
    assert first["network_required"] is False
    assert first["canonical_write"] is False
    assert first["recommendation"] == "FORMULA_ADAPT_ONLY"
    assert first["fixture"]["source_fields_used"] == [
        "variant_result_rows[].variant_id",
        "variant_result_rows[].metrics.return_pct",
        "variant_result_rows[].metrics.drawdown",
        "variant_result_rows[].metrics.sharpe",
        "variant_result_rows[].metrics.trade_count",
        "variant_result_rows[].metrics.win_rate",
        "variant_result_rows[].metrics.fees",
        "variant_result_rows[].metrics.funding",
        "variant_result_rows[].metrics.slippage",
    ]


def test_run_pilot_writes_only_requested_scratch_outputs(tmp_path):
    fixture = _write_fixture(tmp_path / "RP-9001.result_population.json")
    output_dir = tmp_path / "scratch"

    report = pilot.run_pilot(
        rp_fixture_path=fixture,
        output_dir=output_dir,
        empyrical_module=_fake_empyrical(),
        load_external=False,
    )

    assert {path.name for path in output_dir.iterdir()} == {
        "analytics_report.json",
        "analytics_report.md",
        "metric_comparison.csv",
    }
    on_disk = json.loads((output_dir / "analytics_report.json").read_text(encoding="utf-8"))
    assert on_disk["determinism_hash"] == report["determinism_hash"]
    markdown = (output_dir / "analytics_report.md").read_text(encoding="utf-8")
    assert "NOT A RESULT POPULATION" in markdown
    assert "NOT PAPER / LIVE / RUNTIME AUTHORITY" in markdown
    assert "metric_name,fixture_formula_value,external_value,delta,tolerance,status,notes" in (
        output_dir / "metric_comparison.csv"
    ).read_text(encoding="utf-8")


def test_formula_parity_for_simple_fixture(tmp_path):
    fixture = _write_fixture(tmp_path / "RP-9001.result_population.json")
    report = pilot.build_report(rp_fixture_path=fixture, load_external=False)

    expected_return = (1.0 + 0.10) * (1.0 - 0.02) - 1.0
    assert math.isclose(report["formula_metrics"]["cumulative_return"], expected_return)
    assert math.isclose(report["formula_metrics"]["max_drawdown"], 0.02)


def test_failure_is_clear_when_required_return_field_is_missing(tmp_path):
    payload = _fixture_result_population()
    del payload["variant_result_rows"][0]["metrics"]["return_pct"]
    fixture = tmp_path / "bad.result_population.json"
    fixture.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(pilot.AnalyticsPilotError, match="metrics.return_pct"):
        pilot.build_report(rp_fixture_path=fixture, load_external=False)


def test_adapter_source_does_not_use_network_or_canonical_result_population_write():
    source = (pilot.REPO_ROOT / "tools/external_pilots/analytics_metrics_pilot.py").read_text(
        encoding="utf-8"
    )

    forbidden_terms = [
        "requests",
        "urllib",
        "http://",
        "https://",
        "socket",
        "write_result_population",
    ]
    assert not any(term in source for term in forbidden_terms)
    assert pilot.DEFAULT_OUTPUT_DIR.parts[-2:] == ("scratch", "EXT-ANALYTICS-PILOT-01")
