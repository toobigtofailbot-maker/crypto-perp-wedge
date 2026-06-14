import hashlib
import json
from pathlib import Path

from tools.research_runner.generate_robustness_report import (
    build_diagnostic,
    build_diagnostic_with_trial_log,
    generate_report,
    main,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
RP_2134_PATH = REPO_ROOT / "research" / "result_populations" / "RP-2134.result_population.json"
RP_7520_PATH = REPO_ROOT / "research" / "result_populations" / "RP-7520.result_population.json"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_rp_2134() -> dict:
    return json.loads(RP_2134_PATH.read_text(encoding="utf-8"))


def _load_rp_7520() -> dict:
    return json.loads(RP_7520_PATH.read_text(encoding="utf-8"))


def test_report_reads_rp_2134_and_preserves_input_file() -> None:
    before = _sha256_file(RP_2134_PATH)
    report = generate_report(_load_rp_2134(), RP_2134_PATH)
    after = _sha256_file(RP_2134_PATH)

    assert before == after
    assert "input_result_population_id: RP-2134" in report
    assert "committed_denominator: 7" in report
    assert "counts_sum: 7" in report
    assert "successful: 7" in report
    assert "fixture-based pipeline evidence, not strategy-quality evidence" in report


def test_report_reads_rp_7520_and_preserves_input_file() -> None:
    before = _sha256_file(RP_7520_PATH)
    report = generate_report(_load_rp_7520(), RP_7520_PATH)
    after = _sha256_file(RP_7520_PATH)

    assert before == after
    assert "input_result_population_id: RP-7520" in report
    assert "committed_denominator: 10" in report
    assert "counts_sum: 10" in report
    assert "successful: 10" in report
    assert "data_posture: committed_offline_result_population_data_posture" in report
    assert "does not claim strategy edge" in report
    assert "sharpe" in report
    assert "VAR-000010" in report


def test_report_withholds_numeric_robustness_metrics_and_lists_missing_inputs() -> None:
    report = generate_report(_load_rp_2134(), RP_2134_PATH)

    assert "psr_status: withheld_missing_inputs" in report
    assert "dsr_status: withheld_missing_inputs" in report
    assert "min_trl_status: withheld_missing_inputs" in report
    assert "No fabricated PSR, DSR, or MinTRL numeric values are emitted." in report
    assert "per-bar or per-period return series: absent" in report
    assert "number of observations / effective sample length: absent" in report
    assert "skewness: absent" in report
    assert "kurtosis: absent" in report
    assert "benchmark Sharpe: absent" in report
    assert "annualization convention: absent" in report
    assert "selection rule: absent" in report
    assert "effective number of independent trials: absent" in report


def test_report_contains_denominator_policy_and_non_authority_declaration() -> None:
    report = generate_report(_load_rp_2134(), RP_2134_PATH)

    assert "DSR and multiple-testing-aware metrics must use the committed denominator" in report
    assert "No winner-only denominator." in report
    assert "No executed-only denominator." in report
    assert "derived report only" in report
    assert "not ranking authority" in report
    assert "not readiness authority" in report
    assert "not recommendation authority" in report
    assert "not promotion authority" in report
    assert "not transition authority" in report
    assert "not paper/live/runtime authority" in report


def test_report_includes_committed_trial_accounting_without_mutation() -> None:
    trial_log_path = REPO_ROOT / "research" / "trial_log.jsonl"
    before = _sha256_file(trial_log_path)
    diagnostic = build_diagnostic(_load_rp_7520(), RP_7520_PATH)
    after = _sha256_file(trial_log_path)

    assert before == after
    assert diagnostic["trial_accounting"]["state"] == "present"
    assert diagnostic["trial_accounting"]["trial_count_source"] == (
        "valid_rows_in_committed_trial_log_jsonl"
    )
    assert diagnostic["trial_accounting"]["countable_trial_denominator"] > 0
    assert diagnostic["trial_accounting"]["invalid_trial_rows"] == 0
    assert diagnostic["trial_accounting"]["hypothesis_counts"]
    assert diagnostic["robustness_readiness_assessment"]["multiple_testing_inputs_present"][
        "trial_log_denominator"
    ] is True


def test_report_handles_missing_trial_log_as_missing_input(tmp_path: Path) -> None:
    missing_trial_log = tmp_path / "missing_trial_log.jsonl"

    diagnostic = build_diagnostic_with_trial_log(
        _load_rp_2134(), RP_2134_PATH, missing_trial_log
    )

    assert diagnostic["trial_accounting"]["state"] == "missing"
    assert diagnostic["trial_accounting"]["trial_count_source"] == "missing_trial_log_file"
    assert diagnostic["trial_accounting"]["countable_trial_denominator"] is None
    assert diagnostic["robustness_readiness_assessment"]["multiple_testing_inputs_present"][
        "trial_log_denominator"
    ] is False
    assert diagnostic["robustness_readiness_assessment"]["numeric_values_emitted"] is False


def test_report_counts_fixture_trial_log_denominator(tmp_path: Path) -> None:
    trial_log = tmp_path / "trial_log.jsonl"
    rows = [
        {
            "trial_id": "trial-001",
            "utc": "2026-06-01T00:00:00+00:00",
            "hypothesis_id": "H-FIXTURE",
            "config_sha256": "a" * 64,
            "dataset_sha256": "b" * 64,
            "params": {"x": 1},
            "in_sample_sharpe": 0.1,
            "oos_sharpe": 0.2,
            "max_drawdown": 0.3,
            "n_obs": 10,
        },
        {
            "trial_id": "trial-002",
            "utc": "2026-06-02T00:00:00+00:00",
            "hypothesis_id": "H-FIXTURE",
            "config_sha256": "c" * 64,
            "dataset_sha256": "d" * 64,
            "params": {"x": 2},
            "in_sample_sharpe": 0.3,
            "oos_sharpe": 0.4,
            "max_drawdown": 0.5,
            "n_obs": 20,
        },
    ]
    trial_log.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    diagnostic = build_diagnostic_with_trial_log(_load_rp_2134(), RP_2134_PATH, trial_log)

    assert diagnostic["trial_accounting"]["countable_trial_denominator"] == 2
    assert diagnostic["trial_accounting"]["hypothesis_counts"] == {"H-FIXTURE": 2}
    assert diagnostic["trial_accounting"]["n_obs_min"] == 10
    assert diagnostic["trial_accounting"]["n_obs_max"] == 20


def test_report_contains_definition_only_anti_overfit_thresholds() -> None:
    report = generate_report(_load_rp_2134(), RP_2134_PATH)

    assert "## Anti-Overfit Threshold Definitions" in report
    assert "committed_population_denominator: Definition only" in report
    assert "trial_log_denominator: Definition only" in report
    assert "effective_independent_trials: Definition only" in report
    assert "benchmark_sharpe: Definition only" in report
    assert "minimum_track_record_length: Definition only" in report


def test_diagnostic_json_structure_for_rp_7520() -> None:
    diagnostic = build_diagnostic(_load_rp_7520(), RP_7520_PATH)

    assert diagnostic["report_identity"]["input_result_population_id"] == "RP-7520"
    assert diagnostic["committed_denominator_snapshot"]["committed_denominator"] == 10
    assert diagnostic["outcome_distribution"]["counts_sum"] == 10
    assert len(diagnostic["observed_summary"]) == 10
    assert diagnostic["robustness_readiness_assessment"]["numeric_values_emitted"] is False
    assert diagnostic["missing_input_warnings"]["benchmark Sharpe"] == "absent"
    assert "trial_accounting" in diagnostic
    assert "anti_overfit_threshold_definitions" in diagnostic


def test_cli_writes_report(tmp_path: Path) -> None:
    output = tmp_path / "RP-2134.item6_robustness_report.md"

    exit_code = main(
        [
            "--result-population",
            str(RP_2134_PATH),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    report = output.read_text(encoding="utf-8")
    assert "# Item 6 Robustness Report - RP-2134" in report
    assert "committed_denominator: 7" in report


def test_cli_writes_json_report(tmp_path: Path) -> None:
    output = tmp_path / "RP-7520.item6_robustness_diagnostic.json"

    exit_code = main(
        [
            "--result-population",
            str(RP_7520_PATH),
            "--format",
            "json",
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    diagnostic = json.loads(output.read_text(encoding="utf-8"))
    assert diagnostic["report_identity"]["input_result_population_id"] == "RP-7520"
    assert diagnostic["committed_denominator_snapshot"]["committed_denominator"] == 10
    assert diagnostic["robustness_readiness_assessment"]["numeric_values_emitted"] is False
    assert diagnostic["trial_accounting"]["countable_trial_denominator"] > 0


def test_cli_accepts_explicit_trial_log_fixture(tmp_path: Path) -> None:
    trial_log = tmp_path / "trial_log.jsonl"
    trial_log.write_text(
        json.dumps(
            {
                "trial_id": "trial-001",
                "utc": "2026-06-01T00:00:00+00:00",
                "hypothesis_id": "H-FIXTURE",
                "config_sha256": "a" * 64,
                "dataset_sha256": "b" * 64,
                "params": {"x": 1},
                "in_sample_sharpe": 0.1,
                "oos_sharpe": 0.2,
                "max_drawdown": 0.3,
                "n_obs": 10,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "RP-7520.item6_robustness_diagnostic.json"

    exit_code = main(
        [
            "--result-population",
            str(RP_7520_PATH),
            "--trial-log",
            str(trial_log),
            "--format",
            "json",
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    diagnostic = json.loads(output.read_text(encoding="utf-8"))
    assert diagnostic["trial_accounting"]["countable_trial_denominator"] == 1
    assert diagnostic["trial_accounting"]["hypothesis_counts"] == {"H-FIXTURE": 1}


def test_missing_input_fails_cleanly(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "missing.result_population.json"

    exit_code = main(["--result-population", str(missing)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "ERROR:" in captured.err
    assert "does not exist" in captured.err


def test_invalid_required_structure_fails_cleanly(tmp_path: Path, capsys) -> None:
    invalid = tmp_path / "invalid.result_population.json"
    invalid.write_text('{"result_population_id": "RP-9999"}\n', encoding="utf-8")

    exit_code = main(["--result-population", str(invalid)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "ERROR:" in captured.err
    assert "missing required result_population fields" in captured.err
