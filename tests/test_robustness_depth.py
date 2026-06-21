import json
import re
from pathlib import Path

import pytest

from tools.robustness import robustness_depth as depth


FIXTURE_DIR = Path("tests/fixtures/robustness_depth")


def test_non_authority_flags_match_package_boundary() -> None:
    assert depth.NON_AUTHORITY_FLAGS == [
        "advisory_only",
        "scratch_only",
        "non_canonical",
        "not_screen_gate",
        "not_promotion",
        "not_readiness",
        "not_candidate_evidence",
        "not_paper_live",
        "missing_inputs_not_fabricated",
    ]


def test_fixture_with_trade_rows_exercises_all_available_depth_surfaces() -> None:
    report = depth.build_report(
        result_population_path=FIXTURE_DIR / "valid_result_population_rows.json",
        seed=1729,
    )

    assert report["schema_version"] == "robustness_depth.v1"
    assert report["cost_stress_results"]["status"] == "exercised"
    assert report["funding_stress_results"]["status"] == "exercised"
    assert report["slippage_stress_results"]["status"] == "exercised"
    assert report["regime_stress_results"]["status"] == "exercised"
    assert report["per_trade_resampling_status"]["status"] == "available_and_exercised"
    assert report["per_trade_resampling_status"]["fabricated_per_trade_data"] is False
    assert report["canonical_artifact_mutation"] is False
    assert report["gate_or_readiness_authority_created"] is False
    assert set(report["dimensions_exercised"]) == {
        "cost",
        "funding",
        "slippage",
        "regime",
        "per_trade_resampling",
    }


def test_missing_per_trade_rows_are_reported_not_fabricated() -> None:
    report = depth.build_report(
        result_population_path=FIXTURE_DIR / "missing_per_trade_rows.json",
        seed=1729,
    )

    per_trade = report["per_trade_resampling_status"]
    assert per_trade["status"] == "unavailable_missing_per_trade_rows"
    assert per_trade["performed"] is False
    assert per_trade["reason"] == "per-trade resampling not exercised"
    assert per_trade["no_fabricated_trade_rows"] is True
    assert "per_trade_rows" in report["missing_inputs"]


def test_default_result_population_does_not_fabricate_regime_or_trade_inputs() -> None:
    report = depth.build_report(seed=1729)

    assert report["input_refs"][0]["result_population_id"] == "RP-2592"
    assert report["cost_stress_results"]["status"] == "exercised"
    assert report["funding_stress_results"]["status"] == "exercised"
    assert report["slippage_stress_results"]["status"] == "exercised"
    assert report["regime_stress_results"]["status"] == "blocked_input_gap"
    assert report["per_trade_resampling_status"]["status"] == "unavailable_missing_per_trade_rows"
    assert "variant_result_rows[].regime_label_or_equivalent" in report["missing_inputs"]
    assert "per_trade_rows" in report["missing_inputs"]
    assert report["funding_stress_results"]["warnings"][0]["reason"] == "all_metrics.funding_values_are_zero"


def test_same_seed_and_input_are_deterministic() -> None:
    path = FIXTURE_DIR / "valid_result_population_rows.json"

    first = depth.build_report(result_population_path=path, seed=1729)
    second = depth.build_report(result_population_path=path, seed=1729)

    assert first == second
    assert first["output_checksum"] == depth._sha256_payload({key: value for key, value in first.items() if key != "output_checksum"})


def test_different_seed_changes_per_trade_resampling_checksum() -> None:
    path = FIXTURE_DIR / "valid_result_population_rows.json"

    first = depth.build_report(result_population_path=path, seed=1729)
    second = depth.build_report(result_population_path=path, seed=1730)

    assert first["per_trade_resampling_status"] != second["per_trade_resampling_status"]
    assert first["output_checksum"] != second["output_checksum"]


def test_run_writes_required_scratch_outputs(tmp_path: Path) -> None:
    report = depth.run(
        result_population_path=FIXTURE_DIR / "missing_per_trade_rows.json",
        output_dir=tmp_path,
        seed=1729,
    )

    assert {path.name for path in tmp_path.iterdir()} == {
        "README.md",
        "provenance.json",
        "robustness_depth_report.json",
        "robustness_depth_report.md",
    }
    on_disk = json.loads((tmp_path / "robustness_depth_report.json").read_text(encoding="utf-8"))
    assert on_disk["output_checksum"] == report["output_checksum"]
    markdown = (tmp_path / "robustness_depth_report.md").read_text(encoding="utf-8")
    assert "No screen-gate, promotion, readiness" in markdown
    provenance = json.loads((tmp_path / "provenance.json").read_text(encoding="utf-8"))
    assert provenance["canonical_artifact_mutation"] is False
    assert provenance["runner_backtester_touched"] is False


def test_cli_writes_report_and_prints_summary(tmp_path: Path, capsys) -> None:
    exit_code = depth.main(
        [
            "--result-population",
            str(FIXTURE_DIR / "missing_per_trade_rows.json"),
            "--output-dir",
            str(tmp_path),
            "--seed",
            "1729",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    printed = json.loads(captured.out)
    assert printed["package_id"] == depth.PACKAGE_ID
    assert printed["per_trade_resampling_status"] == "unavailable_missing_per_trade_rows"
    assert (tmp_path / "robustness_depth_report.json").exists()


def test_invalid_input_fails_cleanly(tmp_path: Path, capsys) -> None:
    exit_code = depth.main(["--result-population", str(tmp_path / "missing.json")])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "ERROR:" in captured.err
    assert "input file does not exist" in captured.err


def test_invalid_required_structure_fails_cleanly(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text('{"result_population_id": "RP-BAD"}\n', encoding="utf-8")

    with pytest.raises(depth.RobustnessDepthError, match="missing required Result Population fields"):
        depth.build_report(result_population_path=invalid)


def test_source_does_not_use_network_canonical_writes_or_runtime_paths() -> None:
    source = (depth.REPO_ROOT / "tools/robustness/robustness_depth.py").read_text(encoding="utf-8")

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
    assert depth.DEFAULT_OUTPUT_DIR.parts[-2:] == ("scratch", depth.PACKAGE_ID)


def test_default_run_outputs_do_not_embed_local_absolute_paths(tmp_path: Path) -> None:
    depth.run(output_dir=tmp_path, seed=1729)

    root = depth.REPO_ROOT.resolve()
    bad_tokens = {str(root), str(root).replace("\\", "/"), "C:/", "C:\\"}
    for path in (tmp_path / "robustness_depth_report.json", tmp_path / "robustness_depth_report.md", tmp_path / "provenance.json"):
        text = path.read_text(encoding="utf-8")
        assert not any(token and token in text for token in bad_tokens)
        assert not re.search(r"\b[A-Za-z]:[\\/]", text)
