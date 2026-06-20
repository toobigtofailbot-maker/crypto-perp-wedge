from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.pilots.purgedcv_pilot import run_purgedcv_pilot as pilot


def test_non_authority_flags_match_package_required_set():
    assert pilot.NON_AUTHORITY_FLAGS == [
        "scratch_only",
        "non_canonical",
        "not_walkforward_contract",
        "not_canonical_evidence",
        "not_runner_change",
        "not_promotion",
        "not_readiness",
        "not_paper_live",
    ]


def test_build_report_compares_naive_against_purged_embargoed(monkeypatch):
    monkeypatch.setattr(pilot, "_source_commit", lambda: "0ca18b9")
    monkeypatch.setattr(
        pilot,
        "_dependency_status",
        lambda: {
            "package": "purgedcv",
            "import_attempted": True,
            "available": False,
            "version": None,
            "used_for_fold_construction": False,
            "probe_result": "unavailable",
            "notes": [],
        },
    )

    report = pilot.build_report()

    assert report["schema_version"] == "v1"
    assert report["pilot_id"] == "WP-PILOT-PURGEDCV-01"
    assert report["tool_candidate"] == "purgedcv"
    assert report["recommendation"] == "borrow"
    assert report["dependency_status"]["used_for_fold_construction"] is False
    assert report["comparison_summary"]["material_difference_observed"] is True
    assert report["comparison_summary"]["folds_with_boundary_gap"] == 4
    assert report["comparison_summary"]["folds_with_embargo_shifted_selection_start"] == 3
    first_naive = report["naive_folds"][0]
    first_purged = report["purged_embargoed_folds"][0]
    assert first_naive["evaluation_window"]["start_utc"] == first_purged["evaluation_window"]["start_utc"]
    assert first_naive["selection_window"]["end_utc_exclusive"] != first_purged["selection_window"]["end_utc_exclusive"]
    assert first_purged["purge"]["bars"] == 12
    assert first_purged["embargo"]["bars"] == 8
    assert report["repo_fit_assessment"]["should_borrow_repo_native"] is True
    assert report["repo_fit_assessment"]["keep_purgedcv_as_dependency_or_sidecar"] is False


def test_run_pilot_writes_expected_scratch_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(pilot, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(pilot, "_source_commit", lambda: "0ca18b9")
    monkeypatch.setattr(
        pilot,
        "_dependency_status",
        lambda: {
            "package": "purgedcv",
            "import_attempted": True,
            "available": False,
            "version": None,
            "used_for_fold_construction": False,
            "probe_result": "unavailable",
            "notes": ["test probe"],
        },
    )
    output_dir = tmp_path / "scratch" / "WP-PILOT-PURGEDCV-01"

    first = pilot.run_pilot(output_dir=output_dir)
    first_bytes = (output_dir / "fold_comparison_report.json").read_bytes()
    second = pilot.run_pilot(output_dir=output_dir)

    assert first == second
    assert (output_dir / "fold_comparison_report.json").read_bytes() == first_bytes
    assert {path.name for path in output_dir.iterdir()} == {
        "README.md",
        "dependency_probe.json",
        "fold_comparison_report.json",
        "fold_comparison_report.md",
        "provenance.json",
        "requirements.poc.txt",
    }
    payload = json.loads((output_dir / "fold_comparison_report.json").read_text(encoding="utf-8"))
    provenance = json.loads((output_dir / "provenance.json").read_text(encoding="utf-8"))
    assert payload["recommendation"] == "borrow"
    assert provenance["canonical_write_paths"] == []
    assert "fold_comparison_report.json" in provenance["generated_files"]


def test_output_outside_scratch_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(pilot, "REPO_ROOT", tmp_path)

    with pytest.raises(pilot.PurgedCvPilotError, match="output must remain"):
        pilot.run_pilot(output_dir=tmp_path / "reports")


def test_dependency_probe_does_not_fake_import_use(monkeypatch):
    real_import = pilot.importlib.import_module

    def blocked_import(name: str):
        if name == "purgedcv":
            raise ModuleNotFoundError(name)
        return real_import(name)

    monkeypatch.setattr(pilot.importlib, "import_module", blocked_import)

    status = pilot._dependency_status()

    assert status["available"] is False
    assert status["used_for_fold_construction"] is False
    assert status["error_type"] == "ModuleNotFoundError"
