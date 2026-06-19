import json
import math
import re
from pathlib import Path

import pandas as pd
import pytest

from tools.analytics import advisory_metrics as metrics
from tools.analytics import advisory_metrics_report as reporting


def _result_population() -> dict:
    return {
        "result_population_id": "RP-9003",
        "lineage": {
            "strategy_spec_id": "STRAT-SPEC-9003",
            "variant_manifest_id": "VM-9003",
            "sweep_plan_id": "SWEEP-PLAN-9003",
        },
        "data_coverage_summary": {
            "data_slice_identity": "fixture:sha256:ghi",
            "timeframe": "15m",
        },
        "variant_result_rows": [
            {
                "variant_id": "VAR-000001",
                "row_id": "RP-9003-ROW-000001",
                "attempted": True,
                "outcome_category": "successful",
                "metrics": {"return_pct": 0.10, "drawdown": 0.05},
            },
            {
                "variant_id": "VAR-000002",
                "row_id": "RP-9003-ROW-000002",
                "attempted": True,
                "outcome_category": "successful",
                "metrics": {"return_pct": -0.20, "drawdown": 0.25},
            },
        ],
    }


def _write_fixture(path: Path, payload: dict | None = None) -> Path:
    path.write_text(json.dumps(payload or _result_population(), indent=2), encoding="utf-8")
    return path


def test_required_advisory_labels_are_exact() -> None:
    assert reporting.ADVISORY_LABELS == [
        "ADVISORY ANALYTICS OUTPUT",
        "NOT A SCREEN GATE",
        "NOT CANDIDATE READINESS",
        "NOT PROMOTION AUTHORITY",
        "NOT RUNTIME/PAPER/LIVE AUTHORITY",
    ]


def test_return_normalization_preserves_chronology_and_compounds() -> None:
    returns = pd.Series([0.10, -0.20, 0.05], index=["p1", "p2", "p3"])
    normalized = metrics.normalize_inputs(returns=returns)

    assert normalized["returns"].index.tolist() == ["p1", "p2", "p3"]
    assert normalized["equity"].index.tolist() == ["__initial__", "p1", "p2", "p3"]
    assert normalized["equity"].tolist() == pytest.approx([1.0, 1.1, 0.88, 0.924])


def test_equity_normalization_derives_only_observed_returns() -> None:
    equity = pd.Series([100.0, 110.0, 88.0, 121.0], index=[1, 2, 3, 4])
    normalized = metrics.normalize_inputs(equity=equity)

    assert normalized["returns"].tolist() == pytest.approx([0.10, -0.20, 0.375])


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({}, "exactly one"),
        ({"equity": [1.0], "returns": [0.0]}, "exactly one"),
        ({"equity": [1.0, 0.0]}, "greater than zero"),
        ({"returns": [0.1, -1.0]}, "greater than -1.0"),
    ],
)
def test_input_normalization_fails_closed(kwargs, message) -> None:
    with pytest.raises(metrics.AdvisoryMetricsError, match=message):
        metrics.normalize_inputs(**kwargs)


def test_unsorted_input_is_not_silently_reordered() -> None:
    series = pd.Series([0.1, 0.2], index=[2, 1])
    with pytest.raises(metrics.AdvisoryMetricsError, match="chronological"):
        metrics.normalize_inputs(returns=series)


def test_drawdown_decomposition_and_underwater_curve() -> None:
    equity = pd.Series([100.0, 120.0, 90.0, 100.0, 125.0, 100.0], index=list("abcdef"))

    underwater = metrics.underwater_curve(equity)
    episodes = metrics.drawdown_episodes(equity)
    maximum = metrics.max_drawdown(equity)

    assert underwater.tolist() == pytest.approx([0.0, 0.0, -0.25, -1 / 6, 0.0, -0.20])
    assert [{key: value for key, value in row.items() if key != "depth"} for row in episodes] == [
        {
            "peak": "b",
            "start": "c",
            "trough": "c",
            "recovery": "e",
            "duration_observations": 3,
            "time_to_trough_observations": 1,
            "recovered": True,
        },
        {
            "peak": "e",
            "start": "f",
            "trough": "f",
            "recovery": None,
            "duration_observations": 1,
            "time_to_trough_observations": 1,
            "recovered": False,
        },
    ]
    assert [row["depth"] for row in episodes] == pytest.approx([0.25, 0.20])
    assert maximum["value"] == pytest.approx(0.25)
    assert maximum["episode"] == episodes[0]


def test_rolling_metrics_known_values() -> None:
    returns = pd.Series([0.10, -0.10, 0.20], index=["p1", "p2", "p3"])
    rows = metrics.rolling_metrics(returns, window=2, periods_per_year=4)

    assert len(rows) == 2
    assert rows[0]["compounded_return"] == pytest.approx(-0.01)
    assert rows[0]["max_drawdown"] == pytest.approx(0.10)
    assert rows[0]["annualized_volatility"] == pytest.approx(
        pd.Series([0.10, -0.10]).std(ddof=1) * 2
    )


def test_calmar_style_known_values_and_unavailable_states() -> None:
    equity = pd.Series([100.0, 120.0, 90.0, 150.0])
    result = metrics.calmar_style(equity, periods_per_year=3)

    assert result["available"] is True
    assert result["annualized_return"] == pytest.approx(0.5)
    assert result["max_drawdown"] == pytest.approx(0.25)
    assert result["value"] == pytest.approx(2.0)
    assert metrics.calmar_style(equity, periods_per_year=None)["reason"] == (
        "periods_per_year_unavailable"
    )
    assert metrics.calmar_style([1.0, 2.0, 3.0], periods_per_year=2)["reason"] == (
        "zero_max_drawdown"
    )


def test_tail_metrics_known_values() -> None:
    returns = pd.Series([0.10, -0.20, -0.10, 0.30], index=list("abcd"))
    result = metrics.tail_metrics(returns)

    assert result["worst_period"] == {"label": "b", "return": -0.20}
    assert result["downside_count"] == 2
    assert result["downside_frequency"] == pytest.approx(0.5)
    assert result["mean_downside_return"] == pytest.approx(-0.15)
    assert result["downside_deviation"] == pytest.approx(math.sqrt((0.04 + 0.01) / 2))


def test_full_chronological_analysis_is_deterministic() -> None:
    returns = pd.Series([0.10, -0.20, 0.05], index=["p1", "p2", "p3"])
    first = metrics.analyze_chronological_series(
        returns=returns, periods_per_year=3, rolling_window=2
    )
    second = metrics.analyze_chronological_series(
        returns=returns, periods_per_year=3, rolling_window=2
    )

    assert first == second
    assert first["observation_count"] == 3
    assert len(first["rolling_metrics"]) == 2


def test_rp_report_marks_path_metrics_unavailable_without_fabrication(tmp_path: Path) -> None:
    fixture = _write_fixture(tmp_path / "RP-9003.result_population.json")
    report = reporting.build_report(result_population_path=fixture)

    assert report["decision_label"] == "FORMULA_ADAPT_REPO_NATIVE"
    assert all(not item["available"] for item in report["path_metrics"].values())
    assert all(item["value"] is None for item in report["path_metrics"].values())
    assert report["cross_sectional_variant_summary"]["return_pct"]["minimum"] == -0.20
    assert report["cross_sectional_variant_summary"]["return_pct"]["negative_row_count"] == 1
    assert report["report_checksum"].startswith("sha256:")


def test_report_is_deterministic_and_checksum_covers_payload(tmp_path: Path) -> None:
    fixture = _write_fixture(tmp_path / "RP-9003.result_population.json")
    first = reporting.build_report(result_population_path=fixture)
    second = reporting.build_report(result_population_path=fixture)

    assert first == second
    checksum = first.pop("report_checksum")
    assert checksum == reporting._sha256_payload(first)


def test_run_writes_only_advisory_outputs_without_absolute_paths(tmp_path: Path) -> None:
    fixture = _write_fixture(tmp_path / "RP-9003.result_population.json")
    output_dir = tmp_path / "output"
    report = reporting.run(result_population_path=fixture, output_dir=output_dir)

    assert {path.name for path in output_dir.iterdir()} == {
        "advisory_analytics_report.json",
        "advisory_analytics_report.md",
        "advisory_analytics_report.sha256",
    }
    assert (output_dir / "advisory_analytics_report.sha256").read_text().strip() == report[
        "report_checksum"
    ]
    combined = "\n".join(path.read_text() for path in output_dir.iterdir())
    assert not re.search(r"\b[A-Za-z]:[\\/]", combined)
    assert "NOT A SCREEN GATE" in combined
    assert "No return path or annualization assumption is fabricated" in combined


def test_default_fixture_report_uses_committed_rp_without_claiming_path_metrics() -> None:
    report = reporting.build_report()

    assert report["fixture"]["result_population_id"] == "RP-7134"
    assert report["fixture"]["path"] == (
        "research/result_populations/RP-7134.result_population.json"
    )
    assert report["fixture"]["successful_attempted_rows"] == 8
    assert report["input_classification"]["chronological_returns_available"] is False
    assert report["path_metrics"]["calmar_style"]["available"] is False


def test_cli_prints_decision_and_repo_relative_output(tmp_path: Path, capsys) -> None:
    fixture = _write_fixture(tmp_path / "RP-9003.result_population.json")
    output_dir = tmp_path / "output"

    exit_code = reporting.main(
        ["--result-population", str(fixture), "--output-dir", str(output_dir)]
    )

    printed = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert printed["decision_label"] == "FORMULA_ADAPT_REPO_NATIVE"
    assert printed["path_metrics_available"] is False
    assert printed["output_dir"] == "external:output"


def test_invalid_fixture_fails_cleanly(tmp_path: Path, capsys) -> None:
    exit_code = reporting.main(["--result-population", str(tmp_path / "missing.json")])

    assert exit_code == 1
    assert "input file does not exist" in capsys.readouterr().err


def test_modules_do_not_import_network_runtime_or_canonical_writers() -> None:
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            reporting.REPO_ROOT / "tools/analytics/advisory_metrics.py",
            reporting.REPO_ROOT / "tools/analytics/advisory_metrics_report.py",
        )
    )
    forbidden = [
        "import requests",
        "import urllib",
        "import socket",
        "write_result_population",
        "append_trial",
        "from src.runtime",
        "import src.runtime",
        "place_order",
        "submit_order",
        "cancel_order",
    ]
    assert not any(term in sources for term in forbidden)
    assert reporting.DEFAULT_OUTPUT_DIR.parts[-2:] == ("scratch", reporting.PACKAGE_ID)
