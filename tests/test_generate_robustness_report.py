import hashlib
import json
from pathlib import Path

from tools.research_runner.generate_robustness_report import (
    build_diagnostic,
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


def test_diagnostic_json_structure_for_rp_7520() -> None:
    diagnostic = build_diagnostic(_load_rp_7520(), RP_7520_PATH)

    assert diagnostic["report_identity"]["input_result_population_id"] == "RP-7520"
    assert diagnostic["committed_denominator_snapshot"]["committed_denominator"] == 10
    assert diagnostic["outcome_distribution"]["counts_sum"] == 10
    assert len(diagnostic["observed_summary"]) == 10
    assert diagnostic["robustness_readiness_assessment"]["numeric_values_emitted"] is False
    assert diagnostic["missing_input_warnings"]["benchmark Sharpe"] == "absent"


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
