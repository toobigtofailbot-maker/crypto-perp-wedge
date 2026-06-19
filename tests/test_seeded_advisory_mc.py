import json
import math
import re
from pathlib import Path

import pytest

from tools.robustness import seeded_advisory_mc as mc


def _fixture_result_population() -> dict:
    return {
        "result_population_id": "RP-9002",
        "lineage": {
            "strategy_spec_id": "STRAT-SPEC-9002",
            "variant_manifest_id": "VM-9002",
            "sweep_plan_id": "SWEEP-PLAN-9002",
        },
        "data_coverage_summary": {
            "data_slice_identity": "fixture:sha256:def",
            "timeframe": "15m",
        },
        "committed_denominator_snapshot": {
            "committed_denominator": 3,
            "result_row_count": 3,
        },
        "variant_result_rows": [
            {
                "variant_id": "VAR-000001",
                "row_id": "RP-9002-ROW-000001",
                "attempted": True,
                "outcome_category": "successful",
                "parameter_values": {"fast": 5, "slow": 20},
                "metrics": {
                    "return_pct": 0.10,
                    "pnl": 100.0,
                    "drawdown": 0.02,
                    "sharpe": 1.0,
                    "trade_count": 10,
                    "win_rate": 0.6,
                    "fees": 1.0,
                    "funding": 0.0,
                    "slippage": 0.2,
                    "exposure": 1.0,
                },
            },
            {
                "variant_id": "VAR-000002",
                "row_id": "RP-9002-ROW-000002",
                "attempted": True,
                "outcome_category": "successful",
                "parameter_values": {"fast": 10, "slow": 20},
                "metrics": {
                    "return_pct": -0.05,
                    "pnl": -50.0,
                    "drawdown": 0.04,
                    "sharpe": -0.2,
                    "trade_count": 20,
                    "win_rate": 0.4,
                    "fees": 2.0,
                    "funding": 0.0,
                    "slippage": 0.3,
                    "exposure": 1.0,
                },
            },
            {
                "variant_id": "VAR-000003",
                "row_id": "RP-9002-ROW-000003",
                "attempted": False,
                "outcome_category": "not_attempted",
                "metrics": {},
            },
        ],
    }


def _write_fixture(path: Path, payload: dict | None = None) -> Path:
    path.write_text(json.dumps(payload or _fixture_result_population(), indent=2), encoding="utf-8")
    return path


def test_advisory_labels_are_complete() -> None:
    assert mc.ADVISORY_LABELS == [
        "ADVISORY ROBUSTNESS / SEEDED MONTE CARLO OUTPUT",
        "NON-CANONICAL REPORT",
        "NOT A RESULT POPULATION",
        "NOT SCREEN-GATE AUTHORITY",
        "NOT STRATEGY / VM / SWEEP AUTHORITY",
        "NOT CANDIDATE EVIDENCE AUTHORITY",
        "NOT PROMOTION / READINESS AUTHORITY",
        "NOT PAPER / LIVE / RUNTIME AUTHORITY",
        "PER-TRADE MONTE CARLO USES ONLY REAL PER-TRADE DATA IF AVAILABLE",
        "MISSING PER-TRADE DATA MUST BE REPORTED, NOT FABRICATED",
    ]


def test_same_seed_produces_identical_report_and_samples(tmp_path: Path) -> None:
    fixture = _write_fixture(tmp_path / "RP-9002.result_population.json")

    first_report, first_samples = mc.build_report(
        result_population_path=fixture,
        seed=123,
        bootstrap_samples=25,
    )
    second_report, second_samples = mc.build_report(
        result_population_path=fixture,
        seed=123,
        bootstrap_samples=25,
    )

    assert first_report == second_report
    assert first_samples == second_samples
    assert first_report["bootstrap_samples_checksum"] == mc._sha256_payload(first_samples)
    assert first_report["output_checksum"].startswith("sha256:")


def test_different_seed_changes_samples_without_changing_schema(tmp_path: Path) -> None:
    fixture = _write_fixture(tmp_path / "RP-9002.result_population.json")

    first_report, first_samples = mc.build_report(
        result_population_path=fixture,
        seed=123,
        bootstrap_samples=25,
    )
    second_report, second_samples = mc.build_report(
        result_population_path=fixture,
        seed=456,
        bootstrap_samples=25,
    )

    assert first_samples != second_samples
    assert set(first_report) == set(second_report)
    assert set(first_report["bootstrap_ci"]) == set(second_report["bootstrap_ci"])


def test_bootstrap_uses_finite_numeric_values_and_reports_skips(tmp_path: Path) -> None:
    payload = _fixture_result_population()
    payload["variant_result_rows"][1]["metrics"]["sharpe"] = float("nan")
    fixture = _write_fixture(tmp_path / "RP-9002.result_population.json", payload)

    report, _samples = mc.build_report(
        result_population_path=fixture,
        seed=123,
        bootstrap_samples=10,
    )

    assert report["bootstrap_ci"]["sharpe"]["row_count"] == 1
    skipped = {row["metric"]: row for row in report["metrics_skipped"]}
    assert skipped["sharpe"]["reason"] == "some_rows_missing_or_non_finite"
    assert "RP-9002-ROW-000002" in skipped["sharpe"]["skipped_rows"]


def test_per_trade_monte_carlo_is_queued_not_fabricated(tmp_path: Path) -> None:
    fixture = _write_fixture(tmp_path / "RP-9002.result_population.json")

    report, _samples = mc.build_report(
        result_population_path=fixture,
        seed=123,
        bootstrap_samples=10,
    )

    per_trade = report["per_trade_monte_carlo"]
    assert per_trade["status"] == "QUEUE_PER_TRADE_INSTRUMENTATION"
    assert per_trade["performed"] is False
    assert per_trade["finding"] == "PER_TRADE_DATA_MISSING"
    assert per_trade["fabricated_per_trade_data"] is False


def test_parameter_sensitivity_uses_row_parameter_values_when_available(tmp_path: Path) -> None:
    fixture = _write_fixture(tmp_path / "RP-9002.result_population.json")

    report, _samples = mc.build_report(
        result_population_path=fixture,
        seed=123,
        bootstrap_samples=10,
    )

    sensitivity = report["parameter_sensitivity"]
    assert sensitivity["status"] == "performed"
    assert sensitivity["source_type"] == "variant_result_rows"
    assert sensitivity["source_path"] is None
    assert sensitivity["parameter_count"] == 2


def test_default_rp_2592_has_manifest_parameter_sensitivity() -> None:
    report, _samples = mc.build_report(bootstrap_samples=10)

    assert report["fixture"]["result_population_id"] == "RP-2592"
    assert report["fixture"]["path"] == "research/result_populations/RP-2592.result_population.json"
    assert report["fixture"]["variant_manifest_id"] == "VM-0004"
    assert report["fixture_validation"]["status"] == "passed"
    assert report["parameter_sensitivity"]["status"] == "performed"
    assert report["parameter_sensitivity"]["source_type"] == "variant_manifest"
    assert (
        report["parameter_sensitivity"]["source_path"]
        == "research/variant_manifests/VM-0004.variant_manifest.json"
    )
    assert report["parameter_sensitivity"]["parameter_count"] == 3
    assert report["per_trade_monte_carlo"]["status"] == "QUEUE_PER_TRADE_INSTRUMENTATION"
    assert "return_pct" in report["metrics_used"]


def test_run_writes_expected_scratch_outputs(tmp_path: Path) -> None:
    fixture = _write_fixture(tmp_path / "RP-9002.result_population.json")
    output_dir = tmp_path / "scratch"

    report = mc.run(
        result_population_path=fixture,
        output_dir=output_dir,
        seed=123,
        bootstrap_samples=10,
    )

    assert {path.name for path in output_dir.iterdir()} == {
        "bootstrap_samples.sha256",
        "seeded_advisory_mc_report.json",
        "seeded_advisory_mc_report.md",
    }
    on_disk = json.loads((output_dir / "seeded_advisory_mc_report.json").read_text(encoding="utf-8"))
    assert on_disk["output_checksum"] == report["output_checksum"]
    assert (output_dir / "bootstrap_samples.sha256").read_text(encoding="utf-8").strip() == report[
        "bootstrap_samples_checksum"
    ]
    markdown = (output_dir / "seeded_advisory_mc_report.md").read_text(encoding="utf-8")
    assert "ADVISORY ROBUSTNESS / SEEDED MONTE CARLO OUTPUT" in markdown
    assert "NOT SCREEN-GATE AUTHORITY" in markdown


def test_default_run_outputs_do_not_embed_local_absolute_paths(tmp_path: Path) -> None:
    output_dir = tmp_path / "scratch"

    report = mc.run(output_dir=output_dir, bootstrap_samples=10)

    assert report["fixture"]["path"] == "research/result_populations/RP-2592.result_population.json"
    assert (
        report["parameter_sensitivity"]["source_path"]
        == "research/variant_manifests/VM-0004.variant_manifest.json"
    )

    root = mc.REPO_ROOT.resolve()
    bad_tokens = {str(root), str(root).replace("\\", "/"), "C:/", "C:\\"}
    for path in (output_dir / "seeded_advisory_mc_report.json", output_dir / "seeded_advisory_mc_report.md"):
        text = path.read_text(encoding="utf-8")
        assert not any(token and token in text for token in bad_tokens)
        assert not re.search(r"\b[A-Za-z]:[\\/]", text)
        assert f"/{root.name}/" not in text


def test_cli_writes_report_and_prints_repo_relative_output_dir(tmp_path: Path, capsys) -> None:
    fixture = _write_fixture(tmp_path / "RP-9002.result_population.json")
    output_dir = tmp_path / "scratch"

    exit_code = mc.main(
        [
            "--result-population",
            str(fixture),
            "--output-dir",
            str(output_dir),
            "--seed",
            "123",
            "--bootstrap-samples",
            "10",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    printed = json.loads(captured.out)
    assert printed["decision_label"] == "ADOPT_AS_ROBUSTNESS_LAYER"
    assert printed["per_trade_monte_carlo"] == "QUEUE_PER_TRADE_INSTRUMENTATION"
    assert printed["output_dir"] == "external:scratch"
    assert (output_dir / "seeded_advisory_mc_report.json").exists()


def test_invalid_input_fails_cleanly(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "missing.result_population.json"

    exit_code = mc.main(["--result-population", str(missing)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "ERROR:" in captured.err
    assert "input file does not exist" in captured.err


def test_invalid_required_structure_fails_cleanly(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.result_population.json"
    invalid.write_text('{"result_population_id": "RP-9999"}\n', encoding="utf-8")

    with pytest.raises(mc.SeededAdvisoryMCError, match="missing required Result Population fields"):
        mc.build_report(result_population_path=invalid)


def test_invalid_bootstrap_parameters_fail_cleanly(tmp_path: Path) -> None:
    fixture = _write_fixture(tmp_path / "RP-9002.result_population.json")

    with pytest.raises(mc.SeededAdvisoryMCError, match="bootstrap_samples"):
        mc.build_report(result_population_path=fixture, bootstrap_samples=0)

    with pytest.raises(mc.SeededAdvisoryMCError, match="confidence_level"):
        mc.build_report(result_population_path=fixture, confidence_level=1.0)


def test_percentile_interpolates_stably() -> None:
    assert math.isclose(mc._percentile([1.0, 2.0, 3.0, 4.0], 0.5), 2.5)


def test_source_does_not_use_network_canonical_writes_or_runtime_paths() -> None:
    source = (mc.REPO_ROOT / "tools/robustness/seeded_advisory_mc.py").read_text(encoding="utf-8")

    forbidden_terms = [
        "requests",
        "urllib",
        "http://",
        "https://",
        "socket",
        "write_result_population",
        "append_trial",
        "src.runtime",
        "src.paper",
        "paper_broker",
        "place_order",
        "submit_order",
        "cancel_order",
        "exchange_client",
    ]
    assert not any(term in source for term in forbidden_terms)
    assert mc.DEFAULT_OUTPUT_DIR.parts[-2:] == ("scratch", mc.PACKAGE_ID)
