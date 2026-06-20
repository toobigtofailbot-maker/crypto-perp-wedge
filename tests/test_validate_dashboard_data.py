import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator

from tools.dashboard.validate_dashboard_data import (
    DEFAULT_SCHEMA_PATH,
    _validate_operator_review,
    _validate_results_page,
    main,
    validate_dashboard_data_file,
)


FIXTURE_DIR = Path("tests/fixtures/dashboard")
VALID_FIXTURE = FIXTURE_DIR / "valid_dashboard_data_minimal.json"


def _load_valid() -> dict:
    return json.loads(VALID_FIXTURE.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _validate_payload(tmp_path: Path, payload: dict) -> list[str]:
    path = tmp_path / "dashboard_data.json"
    _write_json(path, payload)
    return validate_dashboard_data_file(path)


def test_dashboard_data_schema_meta_valid():
    Draft7Validator.check_schema(json.loads(DEFAULT_SCHEMA_PATH.read_text(encoding="utf-8")))


def test_valid_minimal_dashboard_data_passes():
    assert validate_dashboard_data_file(VALID_FIXTURE) == []


def test_missing_required_top_level_field_fails(tmp_path):
    payload = _load_valid()
    del payload["system_posture"]

    errors = _validate_payload(tmp_path, payload)

    assert any("system_posture" in error for error in errors)


def test_unknown_status_vocabulary_fails(tmp_path):
    payload = _load_valid()
    payload["pages"]["overview"]["status"] = "OK"

    errors = _validate_payload(tmp_path, payload)

    assert any("pages.overview.status" in error for error in errors)


def test_authority_like_field_fails():
    path = FIXTURE_DIR / "invalid_dashboard_data_authority_field.json"

    errors = validate_dashboard_data_file(path)

    assert any("ready_for_live" in error for error in errors)


def test_authority_like_value_fails(tmp_path):
    payload = _load_valid()
    payload["warnings"][0]["message"] = "promote_to_paper"

    errors = _validate_payload(tmp_path, payload)

    assert any("forbidden authority/execution value" in error for error in errors)


def test_missing_status_fixture_fails():
    path = FIXTURE_DIR / "invalid_dashboard_data_missing_status.json"

    errors = validate_dashboard_data_file(path)

    assert any("status" in error for error in errors)


def test_gate_execution_action_field_fails():
    path = FIXTURE_DIR / "invalid_dashboard_data_bad_gate_action.json"

    errors = validate_dashboard_data_file(path)

    assert any("execute" in error or "required_human_action" in error for error in errors)


def test_staleness_field_vocabulary_enforced(tmp_path):
    payload = _load_valid()
    payload["pages"]["data_provenance"]["freshness"]["staleness_status"] = "CURRENT"

    errors = _validate_payload(tmp_path, payload)

    assert any("staleness_status" in error for error in errors)


def test_source_ref_resolution_enforced(tmp_path):
    payload = _load_valid()
    payload["pages"]["overview"]["source_refs"] = ["missing-ref"]

    errors = _validate_payload(tmp_path, payload)

    assert any("unknown ref_id" in error for error in errors)


def test_d4a_provenance_shape_accepted():
    payload = _load_valid()
    d4 = payload["pages"]["data_provenance"]["d4_slice"]

    assert d4["catalog_ref"].startswith("binance_usdtm_btcusdt_ohlcv_15m.")
    assert d4["data_slice_identity"].startswith("binance_usdtm_btcusdt_ohlcv_15m:sha256:")
    assert d4["row_count"] == d4["expected_row_count"] == 220128
    assert validate_dashboard_data_file(VALID_FIXTURE) == []


def test_cli_exits_zero_for_valid_fixture(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["validate_dashboard_data", str(VALID_FIXTURE)])

    assert main() == 0
    assert "OK:" in capsys.readouterr().out


def test_cli_exits_nonzero_for_invalid_fixture(monkeypatch, capsys):
    path = FIXTURE_DIR / "invalid_dashboard_data_bad_gate_action.json"
    monkeypatch.setattr(sys, "argv", ["validate_dashboard_data", str(path)])

    assert main() == 1
    assert "ERROR:" in capsys.readouterr().out


def test_validator_does_not_import_runtime_or_backtester_modules():
    protected_modules = {
        "src.runtime.paper_trader",
        "tools.research_runner.run_offline_sweep",
        "lib.backtest",
        "lib.evaluation",
    }
    before = {name for name in protected_modules if name in sys.modules}

    assert validate_dashboard_data_file(VALID_FIXTURE) == []

    after = {name for name in protected_modules if name in sys.modules}
    assert after == before


def test_fixture_mutation_copy_does_not_affect_source():
    payload = _load_valid()
    copied = copy.deepcopy(payload)
    copied["pages"]["overview"]["status"] = "FAIL"

    assert payload["pages"]["overview"]["status"] == "WARN"


RESULTS_FIXTURE = FIXTURE_DIR / "valid_dashboard_data_with_results.json"


def _load_results() -> dict:
    return json.loads(RESULTS_FIXTURE.read_text(encoding="utf-8"))


def test_valid_results_fixture_passes():
    assert validate_dashboard_data_file(RESULTS_FIXTURE) == []


def test_results_denominator_mismatch_fails(tmp_path):
    payload = _load_results()
    payload["pages"]["results"]["complete_population"]["committed_denominator"] = 5

    errors = _validate_payload(tmp_path, payload)

    assert any("denominator" in error.lower() for error in errors)


def test_results_out_of_order_variant_rows_fail():
    path = FIXTURE_DIR / "invalid_dashboard_data_results_ordering.json"

    errors = validate_dashboard_data_file(path)

    assert any("ascending" in error.lower() or "order" in error.lower() for error in errors)


def test_results_authority_field_or_value_fails():
    path = FIXTURE_DIR / "invalid_dashboard_data_results_authority.json"

    errors = validate_dashboard_data_file(path)

    assert any("forbidden" in error.lower() or "best_variant" in error.lower() for error in errors)


def test_results_specific_forbidden_key_fails():
    payload = _load_results()
    payload["pages"]["results"]["variant_table"]["leaderboard"] = "display_only_note"

    errors = _validate_results_page(Path("test_doc.json"), payload)

    assert any(
        "leaderboard" in error.lower() and "forbidden" in error.lower()
        for error in errors
    )


def test_cli_validates_results_fixture(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["validate_dashboard_data", str(RESULTS_FIXTURE)])

    assert main() == 0
    assert "OK:" in capsys.readouterr().out


OPERATOR_FIXTURE = FIXTURE_DIR / "valid_dashboard_data_operator_review.json"


def test_valid_operator_review_fixture_passes():
    assert validate_dashboard_data_file(OPERATOR_FIXTURE) == []


def test_operator_review_authority_fixture_fails():
    path = FIXTURE_DIR / "invalid_dashboard_data_operator_authority.json"

    errors = validate_dashboard_data_file(path)

    assert any("execution_control" in error or "deploy_now" in error for error in errors)


def test_operator_review_outcome_counts_must_reconcile():
    payload = json.loads(OPERATOR_FIXTURE.read_text(encoding="utf-8"))
    payload["pages"]["operator_review"]["population_summary"]["outcome_counts"]["failed"] = 1

    errors = _validate_operator_review(Path("operator_review.json"), payload)

    assert any("outcome counts" in error for error in errors)


def test_operator_review_deterministic_job_order_enforced():
    payload = json.loads(OPERATOR_FIXTURE.read_text(encoding="utf-8"))
    jobs = payload["pages"]["operator_review"]["active_and_recent_jobs"]
    second = copy.deepcopy(jobs["jobs"][0])
    second["run_id"] = "RP-FIXTURE-0002"
    jobs["jobs"].insert(0, second)
    jobs["recent_job_count"] = 2

    errors = _validate_operator_review(Path("operator_review.json"), payload)

    assert any("deterministic order" in error for error in errors)
