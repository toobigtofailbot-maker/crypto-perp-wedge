import json
from dataclasses import asdict
from pathlib import Path

from tools.research_automation.batch_manifest import (
    OUTPUT_FILE_NAMES,
    BatchManifestItem,
    BatchResourceLimits,
    build_batch_manifest,
)


def _item(source_id: str, output_path: str) -> BatchManifestItem:
    return BatchManifestItem(
        source_id=source_id,
        candidate_id="H-004",
        evaluation_purpose="AUTO-05 batch manifest vertical slice fixture",
        data_refs=("local_fixture:wp12f:auto05:sample",),
        timeframe="1d",
        evaluation_window={
            "start": "2026-04-01T00:00:00Z",
            "end": "2026-04-02T00:00:00Z",
        },
        parameters={"mode": "manifest_only", "max_rows": 1},
        pipeline_version="wp_12f_auto_05_fixture_v1",
        output_path=output_path,
    )


def _items() -> tuple[BatchManifestItem, BatchManifestItem]:
    return (
        _item("INTENT-WP12F-0001", "item-0001"),
        _item("INTENT-WP12F-0002", "nested/item-0002"),
    )


def _limits(max_item_count: int = 2) -> BatchResourceLimits:
    return BatchResourceLimits(
        max_item_count=max_item_count,
        max_local_jobs=1,
        max_concurrency=1,
        failure_threshold=0,
    )


def _metadata() -> dict[str, str]:
    return {
        "repo_version_ref": "static-test-ref",
        "source_package": "WP-12f / AUTO-05",
    }


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_ready(payload: dict) -> dict:
    return json.loads(json.dumps(payload, sort_keys=True))


def test_build_batch_manifest_writes_expected_files_for_two_items(tmp_path):
    result = build_batch_manifest(_items(), tmp_path, _limits(), static_metadata=_metadata())

    assert result.manifest is not None
    assert result.validation_report.passed is True
    assert result.manifest.item_count == 2
    assert set(result.written_files) == set(OUTPUT_FILE_NAMES)
    for file_name in OUTPUT_FILE_NAMES.values():
        path = tmp_path / file_name
        assert path.exists()
        assert path.parent == tmp_path
    assert sorted(path.name for path in tmp_path.iterdir()) == sorted(OUTPUT_FILE_NAMES.values())


def test_build_batch_manifest_is_deterministic_for_identical_input(tmp_path):
    first = build_batch_manifest(_items(), tmp_path, _limits(), static_metadata=_metadata())

    for file_name in OUTPUT_FILE_NAMES.values():
        (tmp_path / file_name).unlink()
    second = build_batch_manifest(_items(), tmp_path, _limits(), static_metadata=_metadata())

    assert first.manifest == second.manifest
    assert first.validation_report == second.validation_report
    for file_name in OUTPUT_FILE_NAMES.values():
        assert (tmp_path / file_name).exists()


def test_empty_item_list_fails_validation_and_writes_no_files(tmp_path):
    result = build_batch_manifest((), tmp_path, _limits(), static_metadata=_metadata())

    assert result.manifest is None
    assert result.written_files == {}
    assert result.validation_report.passed is False
    assert "items must contain at least one batch item" in result.validation_report.failure_reasons
    assert list(tmp_path.iterdir()) == []


def test_missing_and_invalid_item_fields_fail_validation_and_write_no_files(tmp_path):
    invalid_item = BatchManifestItem(
        source_id="",
        candidate_id="H-004",
        evaluation_purpose="",
        data_refs=(),
        timeframe="1d",
        evaluation_window={"start": "", "end": "2026-04-02T00:00:00Z"},
        parameters={},
        pipeline_version="wp_12f_auto_05_fixture_v1",
        output_path="invalid-item-output",
    )

    result = build_batch_manifest((invalid_item,), tmp_path, _limits(), static_metadata=_metadata())

    assert result.manifest is None
    assert result.written_files == {}
    assert result.validation_report.passed is False
    assert "items[0].source_id must be a non-empty string" in result.validation_report.failure_reasons
    assert "items[0].evaluation_purpose must be a non-empty string" in (
        result.validation_report.failure_reasons
    )
    assert "items[0].data_refs must contain at least one non-empty local reference" in (
        result.validation_report.failure_reasons
    )
    assert "items[0].evaluation_window.start must be a non-empty string" in (
        result.validation_report.failure_reasons
    )
    assert list(tmp_path.iterdir()) == []


def test_item_output_path_escape_fails_validation_and_writes_no_files(tmp_path):
    result = build_batch_manifest(
        (_item("INTENT-WP12F-0001", "../outside-root"),),
        tmp_path,
        _limits(),
        static_metadata=_metadata(),
    )

    assert result.manifest is None
    assert result.written_files == {}
    assert result.validation_report.passed is False
    assert "items[0].output_path must be contained under output_root" in (
        result.validation_report.failure_reasons
    )
    assert result.validation_report.output_location_failure_count == 1
    assert list(tmp_path.iterdir()) == []


def test_missing_output_root_fails_with_no_writes_and_no_parent_creation(tmp_path):
    missing_root = tmp_path / "missing" / "batch-output"

    result = build_batch_manifest(_items(), missing_root, _limits(), static_metadata=_metadata())

    assert result.manifest is None
    assert result.written_files == {}
    assert result.validation_report.passed is False
    assert result.validation_report.failure_reasons == ("output_root must be an existing directory",)
    assert not missing_root.exists()
    assert not (tmp_path / "missing").exists()


def test_file_path_output_root_fails_and_preserves_file(tmp_path):
    output_file = tmp_path / "not-a-directory"
    output_file.write_text("existing file\n", encoding="utf-8")

    result = build_batch_manifest(_items(), output_file, _limits(), static_metadata=_metadata())

    assert result.manifest is None
    assert result.written_files == {}
    assert result.validation_report.passed is False
    assert result.validation_report.failure_reasons == ("output_root must be an existing directory",)
    assert output_file.read_text(encoding="utf-8") == "existing file\n"
    assert [path.name for path in tmp_path.iterdir()] == ["not-a-directory"]


def test_resource_limit_failure_when_item_count_exceeds_maximum(tmp_path):
    result = build_batch_manifest(_items(), tmp_path, _limits(max_item_count=1), static_metadata=_metadata())

    assert result.manifest is None
    assert result.written_files == {}
    assert result.validation_report.passed is False
    assert "item count exceeds resource_limits.max_item_count" in result.validation_report.failure_reasons
    assert result.validation_report.resource_limit_failure_count == 1
    assert list(tmp_path.iterdir()) == []


def test_manifest_and_validation_json_match_returned_structures(tmp_path):
    result = build_batch_manifest(_items(), tmp_path, _limits(), static_metadata=_metadata())

    assert result.manifest is not None
    manifest = _load(tmp_path / OUTPUT_FILE_NAMES["batch_manifest"])
    validation_report = _load(tmp_path / OUTPUT_FILE_NAMES["batch_validation_report"])

    assert manifest == _json_ready(asdict(result.manifest))
    assert validation_report == _json_ready(asdict(result.validation_report))


def test_outputs_mark_local_research_only_non_authoritative_no_execution_no_evidence(tmp_path):
    result = build_batch_manifest(_items(), tmp_path, _limits(), static_metadata=_metadata())

    assert result.manifest is not None
    assert result.manifest.local_only is True
    assert result.manifest.research_only is True
    assert result.manifest.non_authoritative is True
    assert result.manifest.execution_occurred is False
    assert result.manifest.creates_committed_evidence is False
    assert result.validation_report.local_only is True
    assert result.validation_report.research_only is True
    assert result.validation_report.non_authoritative is True
    assert result.validation_report.execution_occurred is False
    assert result.validation_report.creates_committed_evidence is False
    for item in result.manifest.items:
        assert item.local_only is True
        assert item.research_only is True
        assert item.non_authoritative is True
        assert item.execution_occurred is False
        assert item.creates_committed_evidence is False
