import json
import re
from pathlib import Path

import pytest

from tools.external_pilots import simulator_pilot as pilot


def test_non_canonical_labels_are_complete():
    assert pilot.NON_CANONICAL_LABELS == [
        "NON-CANONICAL EXTERNAL SIMULATOR PILOT OUTPUT",
        "NOT A RESULT POPULATION",
        "NOT STRATEGY / VM / SWEEP AUTHORITY",
        "NOT CANONICAL RUNNER AUTHORITY",
        "NOT BACKTEST REPLACEMENT AUTHORITY",
        "NOT PAPER / LIVE / RUNTIME AUTHORITY",
        "NOT OMS / RISK / RECONCILIATION AUTHORITY",
        (
            "CANONICAL-EVIDENCE USE REQUIRES SEPARATE MAPPING, VALIDATION, "
            "DETERMINISM, AUDITABILITY, PROVENANCE, AND MAIN/KARL APPROVAL"
        ),
    ]


def test_default_fixture_mapping_uses_rp_2592_lineage():
    report = pilot.build_report()

    fixture = report["fixture"]
    assert fixture["result_population_id"] == "RP-2592"
    assert fixture["result_population_path"] == (
        "research/result_populations/RP-2592.result_population.json"
    )
    assert fixture["strategy_spec_id"] == "STRAT-SPEC-0004"
    assert fixture["variant_manifest_id"] == "VM-0004"
    assert fixture["sweep_plan_id"] == "SWEEP-PLAN-0004"
    assert fixture["selected_variant_count"] == 8
    assert fixture["rp_successful_row_count"] == 8
    assert fixture["normalized_data_local_exists"] is True
    assert fixture["data_slice_identity"].startswith("binance_usdtm_btcusdt_ohlcv_15m:sha256:")


def test_blocked_nautilus_probe_marks_no_reconciliation(monkeypatch):
    def fake_probe(*, isolated_environment_used, isolated_install_command):
        return {
            "candidate": "NautilusTrader",
            "metadata_available": True,
            "version": "fixture-version",
            "python_version": "3.x",
            "platform": "fixture-platform",
            "isolated_environment_used": isolated_environment_used,
            "isolated_install_command": isolated_install_command,
            "dependency_files_changed": False,
            "backtest_api_importable": False,
            "backtest_api_import_error": "ImportError: blocked",
            "source_inspection": {"status": "performed"},
            "offline_backtest_executed": False,
            "offline_backtest_blocked_reason": "blocked",
        }

    monkeypatch.setattr(pilot, "_nautilus_probe", fake_probe)

    report = pilot.build_report(
        isolated_environment_used=True,
        isolated_install_command="python -m pip install nautilus_trader",
    )

    assert report["decision_recommendation"] == "BLOCKED"
    assert report["broader_adoption_taxonomy"] == "blocked"
    assert report["simulator_candidate"]["version"] == "fixture-version"
    assert report["simulator_candidate"]["isolated_environment_used"] is True
    assert report["reconciliation"]["variants_attempted"] == 0
    assert report["reconciliation"]["variants_expressible"] == 0
    assert report["determinism"]["result"] == "not_established"


def test_importable_nautilus_probe_without_execution_still_blocks(monkeypatch):
    def fake_probe(*, isolated_environment_used, isolated_install_command):
        return {
            "candidate": "NautilusTrader",
            "metadata_available": True,
            "version": "fixture-version",
            "python_version": "3.x",
            "platform": "fixture-platform",
            "isolated_environment_used": isolated_environment_used,
            "isolated_install_command": isolated_install_command,
            "dependency_files_changed": False,
            "backtest_api_importable": True,
            "backtest_api_import_error": None,
            "source_inspection": {"status": "performed"},
            "offline_backtest_executed": False,
            "offline_backtest_blocked_reason": None,
        }

    monkeypatch.setattr(pilot, "_nautilus_probe", fake_probe)

    report = pilot.build_report()

    assert report["decision_recommendation"] == "BLOCKED"
    assert report["boundary_statement"]["canonical_result_population_write"] is False
    assert report["boundary_statement"]["runner_backtester_changed"] is False
    assert report["boundary_statement"]["runtime_paper_live_touched"] is False
    assert report["reconciliation"]["variants_attempted"] == 0


def test_run_pilot_writes_expected_outputs_without_absolute_paths(tmp_path, monkeypatch):
    def fake_probe(*, isolated_environment_used, isolated_install_command):
        return {
            "candidate": "NautilusTrader",
            "metadata_available": True,
            "version": "fixture-version",
            "python_version": "3.x",
            "platform": "fixture-platform",
            "isolated_environment_used": isolated_environment_used,
            "isolated_install_command": isolated_install_command,
            "dependency_files_changed": False,
            "backtest_api_importable": False,
            "backtest_api_import_error": "ImportError: blocked",
            "source_inspection": {"status": "performed"},
            "offline_backtest_executed": False,
            "offline_backtest_blocked_reason": "blocked",
        }

    monkeypatch.setattr(pilot, "_nautilus_probe", fake_probe)

    report = pilot.run_pilot(
        output_dir=tmp_path,
        isolated_environment_used=True,
        isolated_install_command="python -m pip install nautilus_trader",
    )

    assert {path.name for path in tmp_path.iterdir()} == {
        "simulator_pilot_report.json",
        "simulator_pilot_report.md",
        "simulator_pilot_report.sha256",
    }
    on_disk = json.loads((tmp_path / "simulator_pilot_report.json").read_text(encoding="utf-8"))
    assert on_disk["output_checksum"] == report["output_checksum"]
    assert (tmp_path / "simulator_pilot_report.sha256").read_text(encoding="utf-8").strip() == (
        report["output_checksum"]
    )

    root = pilot.REPO_ROOT.resolve()
    bad_tokens = {str(root), str(root).replace("\\", "/"), "C:/", "C:\\"}
    for path in tmp_path.iterdir():
        text = path.read_text(encoding="utf-8")
        assert not any(token and token in text for token in bad_tokens)
        assert not re.search(r"\b[A-Za-z]:[\\/]", text)


def test_offline_source_guard_has_no_active_forbidden_calls():
    guard = pilot._source_guard()

    assert guard["checked"] is True
    assert guard["source_path"] == "tools/external_pilots/simulator_pilot.py"
    assert guard["active_forbidden_pattern_hits"] == []
    assert guard["no_network_or_exchange_adapter_calls"] is True


def test_committed_report_checksums_match_status_entry():
    report_json = (
        pilot.REPO_ROOT
        / "scratch"
        / pilot.PACKAGE_ID
        / "simulator_pilot_report.json"
    )
    status_entry = pilot.REPO_ROOT / "docs" / "status_entries" / f"{pilot.PACKAGE_ID}.md"

    if not report_json.exists() or not status_entry.exists():
        pytest.skip("committed simulator pilot artifacts not generated yet")

    payload = json.loads(report_json.read_text(encoding="utf-8"))
    checksum = payload["output_checksum"]

    assert checksum in (pilot.REPO_ROOT / "scratch" / pilot.PACKAGE_ID / "simulator_pilot_report.md").read_text(
        encoding="utf-8"
    )
    assert checksum in status_entry.read_text(encoding="utf-8")
