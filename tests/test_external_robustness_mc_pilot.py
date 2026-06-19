import json
import math
import re
from pathlib import Path

import pytest

from tools.external_pilots import robustness_mc_pilot as pilot


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
        "variant_result_rows": [
            {
                "variant_id": "VAR-000001",
                "row_id": "RP-9002-ROW-000001",
                "attempted": True,
                "outcome_category": "successful",
                "metrics": {
                    "return_pct": 0.10,
                    "drawdown": 0.02,
                    "sharpe": 1.0,
                    "trade_count": 10,
                    "win_rate": 0.6,
                    "fees": 1.0,
                    "funding": 0.0,
                    "slippage": 0.2,
                },
            },
            {
                "variant_id": "VAR-000002",
                "row_id": "RP-9002-ROW-000002",
                "attempted": True,
                "outcome_category": "successful",
                "metrics": {
                    "return_pct": -0.05,
                    "drawdown": 0.04,
                    "sharpe": -0.2,
                    "trade_count": 20,
                    "win_rate": 0.4,
                    "fees": 2.0,
                    "funding": 0.0,
                    "slippage": 0.3,
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


def test_non_canonical_labels_are_complete():
    assert pilot.NON_CANONICAL_LABELS == [
        "NON-CANONICAL ROBUSTNESS / MONTE CARLO PILOT OUTPUT",
        "NOT A RESULT POPULATION",
        "NOT SCREEN-GATE AUTHORITY",
        "NOT STRATEGY / VM / SWEEP AUTHORITY",
        "NOT CANDIDATE EVIDENCE AUTHORITY",
        "NOT PROMOTION / READINESS AUTHORITY",
        "NOT PAPER / LIVE / RUNTIME AUTHORITY",
        "PER-TRADE MONTE CARLO USES ONLY REAL PER-TRADE DATA IF AVAILABLE",
        "MISSING PER-TRADE DATA MUST BE REPORTED, NOT FABRICATED",
    ]


def test_same_seed_produces_identical_report_and_samples(tmp_path):
    fixture = _write_fixture(tmp_path / "RP-9002.result_population.json")

    first_report, first_samples = pilot.build_report(
        rp_fixture_path=fixture,
        seed=123,
        bootstrap_samples=25,
    )
    second_report, second_samples = pilot.build_report(
        rp_fixture_path=fixture,
        seed=123,
        bootstrap_samples=25,
    )

    assert first_report == second_report
    assert first_samples == second_samples
    assert first_report["bootstrap_samples_checksum"] == pilot._sha256_payload(first_samples)
    assert first_report["output_checksum"].startswith("sha256:")


def test_different_seed_preserves_schema_but_changes_samples(tmp_path):
    fixture = _write_fixture(tmp_path / "RP-9002.result_population.json")

    first_report, first_samples = pilot.build_report(
        rp_fixture_path=fixture,
        seed=123,
        bootstrap_samples=25,
    )
    second_report, second_samples = pilot.build_report(
        rp_fixture_path=fixture,
        seed=456,
        bootstrap_samples=25,
    )

    assert first_samples != second_samples
    assert set(first_report) == set(second_report)
    assert set(first_report["bootstrap_ci"]) == set(second_report["bootstrap_ci"])


def test_bootstrap_uses_finite_numeric_values_and_skips_invalid_rows(tmp_path):
    payload = _fixture_result_population()
    payload["variant_result_rows"][1]["metrics"]["sharpe"] = float("nan")
    fixture = _write_fixture(tmp_path / "RP-9002.result_population.json", payload)

    report, _samples = pilot.build_report(
        rp_fixture_path=fixture,
        seed=123,
        bootstrap_samples=10,
    )

    assert report["bootstrap_ci"]["sharpe"]["row_count"] == 1
    skipped = {row["metric"]: row for row in report["metrics_skipped"]}
    assert skipped["sharpe"]["reason"] == "some_rows_missing_or_non_finite"
    assert "RP-9002-ROW-000002" in skipped["sharpe"]["skipped_rows"]


def test_trade_order_resampling_is_not_fabricated_without_real_trade_rows(tmp_path):
    fixture = _write_fixture(tmp_path / "RP-9002.result_population.json")

    report, _samples = pilot.build_report(
        rp_fixture_path=fixture,
        seed=123,
        bootstrap_samples=10,
    )

    assert report["trade_order_resampling"]["status"] == "PER_TRADE_DATA_MISSING"
    assert report["trade_order_resampling"]["performed"] is False
    assert report["trade_order_resampling"]["fabricated_per_trade_data"] is False


def test_parameter_sensitivity_reports_insufficient_mapping_for_fixture(tmp_path):
    fixture = _write_fixture(tmp_path / "RP-9002.result_population.json")

    report, _samples = pilot.build_report(
        rp_fixture_path=fixture,
        seed=123,
        bootstrap_samples=10,
    )

    assert report["parameter_sensitivity"]["status"] == "insufficient_mapping"
    assert report["parameter_sensitivity"]["reason"] == "variant_manifest_not_found_from_rp_lineage"


def test_default_rp_2592_has_parameter_sensitivity_mapping():
    report, _samples = pilot.build_report(bootstrap_samples=10)

    assert report["fixture"]["result_population_id"] == "RP-2592"
    assert report["fixture"]["path"] == "research/result_populations/RP-2592.result_population.json"
    assert report["fixture"]["variant_manifest_id"] == "VM-0004"
    assert report["parameter_sensitivity"]["status"] == "performed"
    assert (
        report["parameter_sensitivity"]["source_path"]
        == "research/variant_manifests/VM-0004.variant_manifest.json"
    )
    assert report["parameter_sensitivity"]["parameter_count"] == 3
    assert report["trade_order_resampling"]["status"] == "PER_TRADE_DATA_MISSING"
    assert "return_pct" in report["metrics_used"]


def test_run_pilot_writes_expected_scratch_outputs(tmp_path):
    fixture = _write_fixture(tmp_path / "RP-9002.result_population.json")
    output_dir = tmp_path / "scratch"

    report = pilot.run_pilot(
        rp_fixture_path=fixture,
        output_dir=output_dir,
        seed=123,
        bootstrap_samples=10,
    )

    assert {path.name for path in output_dir.iterdir()} == {
        "bootstrap_samples.sha256",
        "robustness_report.json",
        "robustness_report.md",
    }
    on_disk = json.loads((output_dir / "robustness_report.json").read_text(encoding="utf-8"))
    assert on_disk["output_checksum"] == report["output_checksum"]
    assert (output_dir / "bootstrap_samples.sha256").read_text(encoding="utf-8").strip() == report[
        "bootstrap_samples_checksum"
    ]
    markdown = (output_dir / "robustness_report.md").read_text(encoding="utf-8")
    assert "NON-CANONICAL ROBUSTNESS / MONTE CARLO PILOT OUTPUT" in markdown
    assert "NOT SCREEN-GATE AUTHORITY" in markdown


def test_default_run_outputs_do_not_embed_local_repo_paths(tmp_path):
    output_dir = tmp_path / "scratch"

    report = pilot.run_pilot(output_dir=output_dir, bootstrap_samples=10)

    assert report["fixture"]["path"] == "research/result_populations/RP-2592.result_population.json"
    assert (
        report["parameter_sensitivity"]["source_path"]
        == "research/variant_manifests/VM-0004.variant_manifest.json"
    )

    root = pilot.REPO_ROOT.resolve()
    bad_tokens = {str(root), str(root).replace("\\", "/"), "C:/", "C:\\"}
    for path in (output_dir / "robustness_report.json", output_dir / "robustness_report.md"):
        text = path.read_text(encoding="utf-8")
        assert not any(token and token in text for token in bad_tokens)
        assert not re.search(r"\b[A-Za-z]:[\\/]", text)
        assert f"/{root.name}/" not in text


def test_committed_report_checksums_match_status_entry():
    report_json = (
        pilot.REPO_ROOT
        / "scratch"
        / pilot.PACKAGE_ID
        / "robustness_report.json"
    )
    report_md = pilot.REPO_ROOT / "scratch" / pilot.PACKAGE_ID / "robustness_report.md"
    status_entry = pilot.REPO_ROOT / "docs" / "status_entries" / f"{pilot.PACKAGE_ID}.md"

    payload = json.loads(report_json.read_text(encoding="utf-8"))
    checksum = payload["output_checksum"]

    assert checksum in report_md.read_text(encoding="utf-8")
    assert checksum in status_entry.read_text(encoding="utf-8")


def test_source_does_not_use_network_or_canonical_writes():
    source = (pilot.REPO_ROOT / "tools/external_pilots/robustness_mc_pilot.py").read_text(
        encoding="utf-8"
    )

    forbidden_terms = [
        "requests",
        "urllib",
        "http://",
        "https://",
        "socket",
        "write_result_population",
        "append_trial",
    ]
    assert not any(term in source for term in forbidden_terms)
    assert pilot.DEFAULT_OUTPUT_DIR.parts[-2:] == ("scratch", pilot.PACKAGE_ID)


def test_percentile_interpolates_stably():
    assert math.isclose(pilot._percentile([1.0, 2.0, 3.0, 4.0], 0.5), 2.5)


def test_invalid_bootstrap_parameters_fail_cleanly(tmp_path):
    fixture = _write_fixture(tmp_path / "RP-9002.result_population.json")

    with pytest.raises(pilot.RobustnessMCPilotError, match="bootstrap_samples"):
        pilot.build_report(rp_fixture_path=fixture, bootstrap_samples=0)

    with pytest.raises(pilot.RobustnessMCPilotError, match="confidence_level"):
        pilot.build_report(rp_fixture_path=fixture, confidence_level=1.0)
