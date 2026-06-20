import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator

from tools.lab_registry.build_lab_run_registry import build_lab_run_registry
from tools.lab_registry.validate_lab_run_registry import (
    DEFAULT_SCHEMA_PATH,
    main,
    validate_lab_run_registry_file,
)


FIXTURE_DIR = Path("tests/fixtures/lab_registry")
VALID_FIXTURE = FIXTURE_DIR / "valid_lab_run_registry.json"


def test_lab_run_registry_schema_meta_valid():
    Draft7Validator.check_schema(json.loads(DEFAULT_SCHEMA_PATH.read_text(encoding="utf-8")))


def test_valid_lab_run_registry_fixture_passes():
    assert validate_lab_run_registry_file(VALID_FIXTURE) == []


def test_builder_indexes_committed_result_populations_read_only():
    registry = build_lab_run_registry(Path("."))
    run_ids = [record["run_id"] for record in registry["records"]]

    assert registry["schema_version"] == "lab_run_registry.v1"
    assert registry["status"] == "PASS"
    assert run_ids == sorted(run_ids)
    assert {"RP-2134", "RP-2592", "RP-3731", "RP-4492", "RP-6236", "RP-6688", "RP-7134", "RP-7520"} <= set(run_ids)
    assert registry["registry_posture"]["display_only"] is True
    assert registry["registry_posture"]["not_execution"] is True


def test_builder_attaches_adopted_reports_without_authority():
    registry = build_lab_run_registry(Path("."))
    by_id = {record["run_id"]: record for record in registry["records"]}

    assert by_id["RP-7134"]["analytics_report_ref"]["path"].endswith("advisory_analytics_report.json")
    assert by_id["RP-2592"]["robustness_report_ref"]["path"].endswith("seeded_advisory_mc_report.json")
    assert by_id["RP-2592"]["triage_sidecar_report_ref"]["path"].endswith("vectorbt_triage_report.json")
    assert by_id["RP-7134"]["analytics_report_ref"]["authority"] == "advisory_display_only_not_gate_not_ranking"


def test_invalid_lab_registry_authority_key_fails():
    path = FIXTURE_DIR / "invalid_lab_run_registry_authority.json"

    errors = validate_lab_run_registry_file(path)

    assert any("leaderboard" in error.lower() or "forbidden" in error.lower() for error in errors)


def test_invalid_lab_registry_variant_order_fails():
    path = FIXTURE_DIR / "invalid_lab_run_registry_ordering.json"

    errors = validate_lab_run_registry_file(path)

    assert any("ascending" in error.lower() for error in errors)


def test_cli_validates_lab_registry_fixture(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["validate_lab_run_registry", str(VALID_FIXTURE)])

    assert main() == 0
    assert "OK:" in capsys.readouterr().out


def test_validator_does_not_import_runtime_or_backtester_modules():
    protected_modules = {
        "src.runtime.paper_trader",
        "tools.research_runner.run_offline_sweep",
        "lib.backtest",
        "lib.evaluation",
    }
    before = {name for name in protected_modules if name in sys.modules}

    assert validate_lab_run_registry_file(VALID_FIXTURE) == []

    after = {name for name in protected_modules if name in sys.modules}
    assert after == before
