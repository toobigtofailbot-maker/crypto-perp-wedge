import json
from dataclasses import asdict
from pathlib import Path

from tools.research_automation.batch_manifest import BatchManifestItem, BatchResourceLimits
from tools.research_automation.batch_run_summary_validation import (
    validate_local_batch_run_summary,
    validate_local_batch_run_summary_file,
)
from tools.research_automation.local_batch_runner import SUMMARY_FILE_NAME, run_local_batch


def _item_result(status: str = "succeeded") -> dict:
    return {
        "item_id": "BMI-0001",
        "source_id": "INTENT-WP12J-0001",
        "status": status,
        "output_path": "item-0001",
        "dry_run_run_id": "LDR-0001" if status == "succeeded" else "",
        "dry_run_written_files": {
            "run_request": "item-0001/run_request.json",
            "manifest": "item-0001/manifest.json",
        }
        if status == "succeeded"
        else {},
        "failure_reasons": () if status == "succeeded" else ("local fixture failure",),
        "local_only": True,
        "research_only": True,
        "non_authoritative": True,
        "creates_committed_evidence": False,
        "protected_boundary_preserved": status == "succeeded",
    }


def _summary(item_results: list[dict] | None = None) -> dict:
    items = item_results if item_results is not None else [_item_result()]
    return {
        "batch_id": "BM-0001",
        "implementation_id": "wp_12h_auto_07_local_batch_runner_v1",
        "package_label": "WP-12h / AUTO-07",
        "item_count": len(items),
        "success_item_count": sum(item["status"] == "succeeded" for item in items),
        "failed_item_count": sum(item["status"] == "failed" for item in items),
        "skipped_item_count": sum(item["status"] == "skipped" for item in items),
        "blocked_item_count": sum(item["status"] == "blocked" for item in items),
        "failure_reasons": (),
        "item_results": items,
        "manifest_files": {
            "batch_manifest": "batch_manifest.json",
            "batch_validation_report": "batch_validation_report.json",
        },
        "summary_file": "local_batch_run_summary.json",
        "checked_boundaries": (
            "local_only",
            "research_only",
            "non_authoritative",
            "no_committed_evidence_artifact",
        ),
        "local_only": True,
        "research_only": True,
        "non_authoritative": True,
        "creates_committed_evidence": False,
        "protected_boundary_preserved": all(
            item["protected_boundary_preserved"] for item in items
        ),
    }


def _batch_item(source_id: str, output_path: str) -> BatchManifestItem:
    return BatchManifestItem(
        source_id=source_id,
        candidate_id="H-004",
        evaluation_purpose="AUTO-09 batch summary validation fixture",
        data_refs=("local_fixture:wp12j:auto09:sample",),
        timeframe="1d",
        evaluation_window={
            "start": "2026-04-01T00:00:00Z",
            "end": "2026-04-02T00:00:00Z",
        },
        parameters={"mode": "summary_validation", "max_rows": 1},
        pipeline_version="wp_12j_auto_09_fixture_v1",
        output_path=output_path,
    )


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_valid_minimal_successful_summary_passes():
    report = validate_local_batch_run_summary(_summary())

    assert report.passed is True
    assert report.failure_reasons == ()
    assert report.local_only is True
    assert report.research_only is True
    assert report.non_authoritative is True
    assert report.creates_committed_evidence is False


def test_valid_failed_item_summary_passes_shape_validation_and_preserves_markers():
    report = validate_local_batch_run_summary(_summary([_item_result("failed")]))

    assert report.passed is True
    assert report.non_authoritative is True
    assert report.creates_committed_evidence is False


def test_valid_blocked_item_summary_passes_when_counts_match():
    report = validate_local_batch_run_summary(_summary([_item_result("blocked")]))

    assert report.passed is True


def test_missing_batch_field_fails():
    payload = _summary()
    del payload["batch_id"]

    report = validate_local_batch_run_summary(payload)

    assert report.passed is False
    assert "summary missing required field: batch_id" in report.failure_reasons


def test_missing_item_field_fails():
    payload = _summary()
    del payload["item_results"][0]["source_id"]

    report = validate_local_batch_run_summary(payload)

    assert report.passed is False
    assert "summary.item_results[0] missing required field: source_id" in report.failure_reasons


def test_count_mismatch_fails():
    payload = _summary()
    payload["success_item_count"] = 0

    report = validate_local_batch_run_summary(payload)

    assert report.passed is False
    assert "success_item_count must be 1" in report.failure_reasons


def test_unknown_item_status_fails():
    payload = _summary([_item_result("mystery")])

    report = validate_local_batch_run_summary(payload)

    assert report.passed is False
    assert any(".status must be one of" in reason for reason in report.failure_reasons)


def test_absolute_path_reference_fails():
    payload = _summary()
    payload["summary_file"] = "/tmp/local_batch_run_summary.json"

    report = validate_local_batch_run_summary(payload)

    assert report.passed is False
    assert "summary.summary_file must be a non-empty local relative path without traversal" in (
        report.failure_reasons
    )


def test_path_traversal_reference_fails():
    payload = _summary()
    payload["item_results"][0]["dry_run_written_files"]["manifest"] = "../manifest.json"

    report = validate_local_batch_run_summary(payload)

    assert report.passed is False
    assert "summary.item_results[0].dry_run_written_files.manifest must be a non-empty local relative path without traversal" in (
        report.failure_reasons
    )


def test_authority_marker_drift_fails():
    payload = _summary()
    payload["non_authoritative"] = False
    payload["item_results"][0]["creates_committed_evidence"] = True

    report = validate_local_batch_run_summary(payload)

    assert report.passed is False
    assert "summary.non_authoritative must be True" in report.failure_reasons
    assert "summary.item_results[0].creates_committed_evidence must be False" in (
        report.failure_reasons
    )


def test_invalid_json_file_fails_through_file_helper(tmp_path):
    path = tmp_path / "local_batch_run_summary.json"
    path.write_text("{not-json", encoding="utf-8")

    report = validate_local_batch_run_summary_file(path)

    assert report.passed is False
    assert any("invalid JSON" in reason for reason in report.failure_reasons)


def test_non_object_json_file_fails_through_file_helper(tmp_path):
    path = tmp_path / "local_batch_run_summary.json"
    path.write_text("[]", encoding="utf-8")

    report = validate_local_batch_run_summary_file(path)

    assert report.passed is False
    assert report.failure_reasons == ("summary file JSON must be an object",)


def test_valid_summary_file_passes_through_file_helper(tmp_path):
    path = tmp_path / "local_batch_run_summary.json"
    _write_json(path, _summary())

    report = validate_local_batch_run_summary_file(path)

    assert report.passed is True


def test_wp12h_generated_local_batch_summary_validates_under_tmp_path(tmp_path):
    result = run_local_batch(
        (_batch_item("INTENT-WP12J-0001", "item-0001"),),
        tmp_path,
        BatchResourceLimits(max_item_count=1),
        static_metadata={"source_package": "WP-12j / AUTO-09"},
    )

    report = validate_local_batch_run_summary(asdict(result.summary))
    file_report = validate_local_batch_run_summary_file(tmp_path / SUMMARY_FILE_NAME)

    assert report.passed is True
    assert file_report.passed is True
