import json
from pathlib import Path

from tools.research_automation.batch_manifest import BatchManifestItem, BatchResourceLimits
from tools.research_automation.local_batch_runner import run_local_batch
from tools.research_automation.local_dry_run_runner import (
    ResearchIntentFixture,
    run_local_dry_run,
)
from tools.research_automation.local_run_registry import (
    LOCAL_RUN_REGISTRY_FILE_NAME,
    build_local_run_registry,
)
from tools.research_automation.local_run_registry_validation import (
    validate_local_run_registry,
    validate_local_run_registry_file,
)


def _intent() -> ResearchIntentFixture:
    return ResearchIntentFixture(
        intent_id="INTENT-WP12N-0001",
        candidate_id="H-004",
        evaluation_purpose="AUTO-13 local registry validation fixture",
        data_refs=("local_fixture:wp12n:auto13:sample",),
        timeframe="1d",
        evaluation_window={
            "start": "2026-04-01T00:00:00Z",
            "end": "2026-04-02T00:00:00Z",
        },
        parameters={"mode": "local_run_registry_validation", "max_rows": 1},
        pipeline_version="wp_12n_auto_13_fixture_v1",
        static_metadata={"source_package": "WP-12n / AUTO-13"},
    )


def _invalid_intent() -> ResearchIntentFixture:
    return ResearchIntentFixture(
        intent_id="",
        candidate_id="H-004",
        evaluation_purpose="AUTO-13 failed dry-run validation fixture",
        data_refs=(),
        timeframe="1d",
        evaluation_window={"start": "", "end": "2026-04-02T00:00:00Z"},
        parameters={},
        pipeline_version="wp_12n_auto_13_fixture_v1",
    )


def _batch_item(source_id: str, output_path: str) -> BatchManifestItem:
    return BatchManifestItem(
        source_id=source_id,
        candidate_id="H-004",
        evaluation_purpose="AUTO-13 local batch registry validation fixture",
        data_refs=("local_fixture:wp12n:auto13:batch",),
        timeframe="1d",
        evaluation_window={
            "start": "2026-04-01T00:00:00Z",
            "end": "2026-04-02T00:00:00Z",
        },
        parameters={"mode": "local_batch_registry_validation", "max_rows": 1},
        pipeline_version="wp_12n_auto_13_fixture_v1",
        output_path=output_path,
    )


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _valid_registry(tmp_path: Path) -> dict:
    dry_root = tmp_path / "dry"
    registry_root = tmp_path / "registry"
    dry_root.mkdir(parents=True)
    registry_root.mkdir(parents=True)
    run_local_dry_run(_intent(), dry_root)
    build_local_run_registry((dry_root,), registry_root)
    return _load(registry_root / LOCAL_RUN_REGISTRY_FILE_NAME)


def test_valid_registry_output_from_builder_passes_validation(tmp_path):
    payload = _valid_registry(tmp_path)

    report = validate_local_run_registry(payload)

    assert report.passed is True
    assert report.failure_reasons == ()
    assert report.record_count == 1
    assert report.local_only is True
    assert report.research_only is True
    assert report.non_authoritative is True
    assert report.creates_committed_evidence is False


def test_valid_registry_file_passes_through_file_helper(tmp_path):
    dry_root = tmp_path / "dry"
    registry_root = tmp_path / "registry"
    dry_root.mkdir()
    registry_root.mkdir()
    run_local_dry_run(_intent(), dry_root)
    build_local_run_registry((dry_root,), registry_root)

    report = validate_local_run_registry_file(registry_root / LOCAL_RUN_REGISTRY_FILE_NAME)

    assert report.passed is True
    assert report.record_count == 1


def test_failed_dry_run_record_passes_shape_validation_with_preserved_markers(tmp_path):
    dry_root = tmp_path / "dry"
    registry_root = tmp_path / "registry"
    dry_root.mkdir()
    registry_root.mkdir()
    run_local_dry_run(_invalid_intent(), dry_root)
    build_local_run_registry((dry_root,), registry_root)

    payload = _load(registry_root / LOCAL_RUN_REGISTRY_FILE_NAME)
    report = validate_local_run_registry(payload)

    assert report.passed is True
    assert report.protected_boundary_preserved is False
    assert payload["records"][0]["validation_passed"] is False
    assert payload["records"][0]["protected_boundary_preserved"] is False


def test_missing_top_level_required_field_fails(tmp_path):
    payload = _valid_registry(tmp_path)
    del payload["implementation_id"]

    report = validate_local_run_registry(payload)

    assert report.passed is False
    assert "registry missing required field: implementation_id" in report.failure_reasons


def test_missing_record_required_field_fails(tmp_path):
    payload = _valid_registry(tmp_path)
    del payload["records"][0]["registry_record_id"]

    report = validate_local_run_registry(payload)

    assert report.passed is False
    assert "records[0] missing required field: registry_record_id" in report.failure_reasons


def test_record_count_mismatch_fails(tmp_path):
    payload = _valid_registry(tmp_path)
    payload["record_count"] = 2

    report = validate_local_run_registry(payload)

    assert report.passed is False
    assert "registry.record_count must equal len(records)" in report.failure_reasons


def test_unknown_source_kind_fails(tmp_path):
    payload = _valid_registry(tmp_path)
    payload["records"][0]["source_kind"] = "mystery"

    report = validate_local_run_registry(payload)

    assert report.passed is False
    assert any(".source_kind must be one of" in reason for reason in report.failure_reasons)


def test_local_batch_run_record_with_failed_validation_fails(tmp_path):
    batch_root = tmp_path / "batch"
    registry_root = tmp_path / "registry"
    batch_root.mkdir()
    registry_root.mkdir()
    run_local_batch(
        (_batch_item("INTENT-WP12N-0001", "item-0001"),),
        batch_root,
        BatchResourceLimits(max_item_count=1),
    )
    build_local_run_registry((batch_root,), registry_root)
    payload = _load(registry_root / LOCAL_RUN_REGISTRY_FILE_NAME)
    payload["records"][0]["validation_passed"] = False

    report = validate_local_run_registry(payload)

    assert report.passed is False
    assert "records[0].validation_passed must be True for local_batch_run" in report.failure_reasons


def test_failed_local_dry_run_record_with_true_protected_boundary_fails(tmp_path):
    dry_root = tmp_path / "dry"
    registry_root = tmp_path / "registry"
    dry_root.mkdir()
    registry_root.mkdir()
    run_local_dry_run(_invalid_intent(), dry_root)
    build_local_run_registry((dry_root,), registry_root)
    payload = _load(registry_root / LOCAL_RUN_REGISTRY_FILE_NAME)
    payload["records"][0]["protected_boundary_preserved"] = True
    payload["protected_boundary_preserved"] = True

    report = validate_local_run_registry(payload)

    assert report.passed is False
    assert "records[0].protected_boundary_preserved must be False for failed local_dry_run" in (
        report.failure_reasons
    )


def test_boundary_marker_drift_fails(tmp_path):
    payload = _valid_registry(tmp_path)
    payload["non_authoritative"] = False
    payload["records"][0]["creates_committed_evidence"] = True

    report = validate_local_run_registry(payload)

    assert report.passed is False
    assert "registry.non_authoritative must be True" in report.failure_reasons
    assert "records[0].creates_committed_evidence must be False" in report.failure_reasons


def test_absolute_path_reference_fails(tmp_path):
    payload = _valid_registry(tmp_path)
    key = next(iter(payload["records"][0]["relative_paths"]))
    payload["records"][0]["relative_paths"][key] = "/tmp/run_request.json"

    report = validate_local_run_registry(payload)

    assert report.passed is False
    assert any("must be a non-empty local relative path without traversal" in reason for reason in report.failure_reasons)


def test_path_traversal_reference_fails(tmp_path):
    payload = _valid_registry(tmp_path)
    key = next(iter(payload["records"][0]["relative_paths"]))
    payload["records"][0]["relative_paths"][key] = "../run_request.json"

    report = validate_local_run_registry(payload)

    assert report.passed is False
    assert any("must be a non-empty local relative path without traversal" in reason for reason in report.failure_reasons)


def test_backslash_or_windows_drive_reference_fails(tmp_path):
    payload = _valid_registry(tmp_path)
    keys = list(payload["records"][0]["relative_paths"])
    payload["records"][0]["relative_paths"][keys[0]] = "nested\\run_request.json"

    report = validate_local_run_registry(payload)

    assert report.passed is False
    assert any("must be a non-empty local relative path without traversal" in reason for reason in report.failure_reasons)

    payload = _valid_registry(tmp_path / "second")
    key = next(iter(payload["records"][0]["relative_paths"]))
    payload["records"][0]["relative_paths"][key] = "C:/run_request.json"

    report = validate_local_run_registry(payload)

    assert report.passed is False
    assert any("must be a non-empty local relative path without traversal" in reason for reason in report.failure_reasons)


def test_source_file_hashes_key_mismatch_fails(tmp_path):
    payload = _valid_registry(tmp_path)
    payload["records"][0]["source_file_hashes"]["unexpected"] = "a" * 64

    report = validate_local_run_registry(payload)

    assert report.passed is False
    assert "records[0].source_file_hashes keys must match relative_paths keys exactly" in report.failure_reasons


def test_invalid_sha256_hash_format_fails(tmp_path):
    payload = _valid_registry(tmp_path)
    key = next(iter(payload["records"][0]["source_file_hashes"]))
    payload["records"][0]["source_file_hashes"][key] = "not-a-sha"

    report = validate_local_run_registry(payload)

    assert report.passed is False
    assert f"records[0].source_file_hashes.{key} must be a 64-character hex SHA-256 string" in (
        report.failure_reasons
    )


def test_invalid_json_file_fails_through_file_helper(tmp_path):
    path = tmp_path / "local_run_registry.json"
    path.write_text("{not-json", encoding="utf-8")

    report = validate_local_run_registry_file(path)

    assert report.passed is False
    assert any("invalid JSON" in reason for reason in report.failure_reasons)


def test_non_object_json_file_fails_through_file_helper(tmp_path):
    path = tmp_path / "local_run_registry.json"
    path.write_text("[]", encoding="utf-8")

    report = validate_local_run_registry_file(path)

    assert report.passed is False
    assert report.failure_reasons == ("registry file JSON must be an object",)


def test_helper_writes_nothing_and_tests_write_only_under_tmp_path(tmp_path):
    payload = _valid_registry(tmp_path)
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    report = validate_local_run_registry(payload)
    file_report = validate_local_run_registry_file(tmp_path / "registry" / LOCAL_RUN_REGISTRY_FILE_NAME)

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert report.passed is True
    assert file_report.passed is True
    assert after == before


def test_test_file_helper_writes_json_only_under_tmp_path(tmp_path):
    payload = _valid_registry(tmp_path)
    path = tmp_path / "copy" / "local_run_registry.json"
    path.parent.mkdir()
    _write_json(path, payload)

    report = validate_local_run_registry_file(path)

    assert report.passed is True
    assert sorted(item.name for item in tmp_path.iterdir()) == ["copy", "dry", "registry"]
