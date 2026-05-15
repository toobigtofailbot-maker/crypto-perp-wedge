import json
from pathlib import Path

from tools.research_automation.local_dry_run_runner import (
    OUTPUT_FILE_NAMES,
    ResearchIntentFixture,
    run_local_dry_run,
)


def _intent() -> ResearchIntentFixture:
    return ResearchIntentFixture(
        intent_id="INTENT-WP12D-0001",
        candidate_id="H-004",
        evaluation_purpose="AUTO-03 local dry-run vertical slice fixture",
        data_refs=("local_fixture:wp12d:auto03:sample",),
        timeframe="1d",
        evaluation_window={
            "start": "2026-04-01T00:00:00Z",
            "end": "2026-04-02T00:00:00Z",
        },
        parameters={"mode": "vertical_slice", "max_rows": 1},
        pipeline_version="wp_12d_auto_03_fixture_v1",
        static_metadata={
            "repo_version_ref": "static-test-ref",
            "source_package": "WP-12d / AUTO-03",
        },
    )


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_local_dry_run_writes_expected_bundle_files_under_tmp_path(tmp_path):
    result = run_local_dry_run(_intent(), tmp_path)

    assert result.validation_report.passed is True
    assert set(result.written_files) == set(OUTPUT_FILE_NAMES)
    for file_name in OUTPUT_FILE_NAMES.values():
        path = tmp_path / file_name
        assert path.exists()
        assert path.parent == tmp_path


def test_missing_output_dir_returns_failure_and_writes_no_files(tmp_path):
    missing_dir = tmp_path / "missing" / "runner-output"

    result = run_local_dry_run(_intent(), missing_dir)

    assert result.run_request is None
    assert result.manifest is None
    assert result.output_bundle is None
    assert result.written_files == {}
    assert result.validation_report.passed is False
    assert result.validation_report.failure_reasons == ("output_dir must be a directory",)
    assert not missing_dir.exists()
    assert list(tmp_path.iterdir()) == []


def test_file_path_as_output_dir_returns_failure_and_writes_no_files(tmp_path):
    output_file = tmp_path / "not-a-directory"
    output_file.write_text("existing file\n", encoding="utf-8")

    result = run_local_dry_run(_intent(), output_file)

    assert result.run_request is None
    assert result.manifest is None
    assert result.output_bundle is None
    assert result.written_files == {}
    assert result.validation_report.passed is False
    assert result.validation_report.failure_reasons == ("output_dir must be a directory",)
    assert output_file.read_text(encoding="utf-8") == "existing file\n"
    assert [path.name for path in tmp_path.iterdir()] == ["not-a-directory"]


def test_runner_does_not_create_parent_directories(tmp_path):
    missing_dir = tmp_path / "parent" / "child"

    result = run_local_dry_run(_intent(), missing_dir)

    assert result.validation_report.passed is False
    assert result.written_files == {}
    assert not (tmp_path / "parent").exists()


def test_local_dry_run_converts_intent_to_run_request(tmp_path):
    result = run_local_dry_run(_intent(), tmp_path)

    assert result.run_request is not None
    assert result.run_request.intent_id == "INTENT-WP12D-0001"
    assert result.run_request.candidate_id == "H-004"
    assert result.run_request.data_refs == ("local_fixture:wp12d:auto03:sample",)
    assert result.run_request.local_only is True
    assert result.run_request.deterministic is True
    assert result.run_request.non_authoritative is True


def test_manifest_output_and_validation_boundaries_are_non_authoritative(tmp_path):
    result = run_local_dry_run(_intent(), tmp_path)

    assert result.manifest is not None
    assert result.output_bundle is not None
    assert result.manifest.research_only is True
    assert result.manifest.non_authoritative is True
    assert result.manifest.protected_boundary_preserved is True
    assert result.output_bundle.creates_committed_evidence is False
    assert result.output_bundle.non_authoritative is True
    assert result.validation_report.checked_boundaries == (
        "local_only",
        "research_only",
        "non_authoritative",
        "no_committed_evidence_artifact",
        "no_runtime_paper_live_oms_risk_safe_mode_contact",
        "no_exchange_broker_order_scheduler_daemon_queue_contact",
        "no_config_dependency_schema_validator_query_layer_contact",
    )


def test_local_dry_run_is_deterministic_for_identical_intent(tmp_path):
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_dir.mkdir()
    second_dir.mkdir()

    first = run_local_dry_run(_intent(), first_dir)
    second = run_local_dry_run(_intent(), second_dir)

    assert first.run_request == second.run_request
    assert first.manifest == second.manifest
    assert first.output_bundle == second.output_bundle
    assert first.validation_report == second.validation_report
    for file_name in OUTPUT_FILE_NAMES.values():
        assert (first_dir / file_name).read_text(encoding="utf-8") == (
            second_dir / file_name
        ).read_text(encoding="utf-8")


def test_invalid_intent_records_failure_accounting_without_run_outputs(tmp_path):
    invalid_intent = ResearchIntentFixture(
        intent_id="",
        candidate_id="H-004",
        evaluation_purpose="AUTO-03 invalid fixture",
        data_refs=(),
        timeframe="1d",
        evaluation_window={"start": "", "end": "2026-04-02T00:00:00Z"},
        parameters={},
        pipeline_version="wp_12d_auto_03_fixture_v1",
    )

    result = run_local_dry_run(invalid_intent, tmp_path)

    assert result.run_request is None
    assert result.manifest is None
    assert result.output_bundle is None
    assert result.validation_report.passed is False
    assert "intent_id must be a non-empty string" in result.validation_report.failure_reasons
    assert "data_refs must contain at least one non-empty local reference" in (
        result.validation_report.failure_reasons
    )
    assert (tmp_path / OUTPUT_FILE_NAMES["validation_report"]).exists()
    assert not (tmp_path / OUTPUT_FILE_NAMES["run_request"]).exists()
    assert not (tmp_path / OUTPUT_FILE_NAMES["manifest"]).exists()
    assert not (tmp_path / OUTPUT_FILE_NAMES["output_bundle"]).exists()


def test_bundle_file_content_matches_returned_structures(tmp_path):
    result = run_local_dry_run(_intent(), tmp_path)

    run_request = _load(tmp_path / OUTPUT_FILE_NAMES["run_request"])
    manifest = _load(tmp_path / OUTPUT_FILE_NAMES["manifest"])
    output_bundle = _load(tmp_path / OUTPUT_FILE_NAMES["output_bundle"])
    validation_report = _load(tmp_path / OUTPUT_FILE_NAMES["validation_report"])

    assert result.run_request is not None
    assert result.manifest is not None
    assert result.output_bundle is not None
    assert run_request["run_id"] == result.run_request.run_id
    assert manifest["manifest_id"] == result.manifest.manifest_id
    assert output_bundle["output_bundle_id"] == result.output_bundle.output_bundle_id
    assert validation_report["validation_report_id"] == result.validation_report.validation_report_id
    assert validation_report["passed"] is True
