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
    LocalRunRegistryRecord,
    LocalRunRegistryResult,
    build_local_run_registry,
)


def _intent() -> ResearchIntentFixture:
    return ResearchIntentFixture(
        intent_id="INTENT-WP12M-0001",
        candidate_id="H-004",
        evaluation_purpose="AUTO-12 local run registry fixture",
        data_refs=("local_fixture:wp12m:auto12:sample",),
        timeframe="1d",
        evaluation_window={
            "start": "2026-04-01T00:00:00Z",
            "end": "2026-04-02T00:00:00Z",
        },
        parameters={"mode": "local_run_registry", "max_rows": 1},
        pipeline_version="wp_12m_auto_12_fixture_v1",
        static_metadata={"source_package": "WP-12m / AUTO-12"},
    )


def _batch_item(source_id: str, output_path: str) -> BatchManifestItem:
    return BatchManifestItem(
        source_id=source_id,
        candidate_id="H-004",
        evaluation_purpose="AUTO-12 local batch registry fixture",
        data_refs=("local_fixture:wp12m:auto12:batch",),
        timeframe="1d",
        evaluation_window={
            "start": "2026-04-01T00:00:00Z",
            "end": "2026-04-02T00:00:00Z",
        },
        parameters={"mode": "local_batch_registry", "max_rows": 1},
        pipeline_version="wp_12m_auto_12_fixture_v1",
        output_path=output_path,
    )


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_valid_local_dry_run_output_root_is_indexed(tmp_path):
    dry_root = tmp_path / "dry"
    registry_root = tmp_path / "registry"
    dry_root.mkdir()
    registry_root.mkdir()
    dry_result = run_local_dry_run(_intent(), dry_root)

    result = build_local_run_registry((dry_root,), registry_root)

    assert result.failure_reasons == ()
    assert len(result.records) == 1
    record = result.records[0]
    assert record.source_kind == "local_dry_run"
    assert record.run_id == dry_result.run_request.run_id
    assert record.candidate_id == "H-004"
    assert record.evaluation_purpose == "AUTO-12 local run registry fixture"
    assert record.validation_passed is True


def test_valid_local_batch_run_output_root_is_indexed(tmp_path):
    batch_root = tmp_path / "batch"
    registry_root = tmp_path / "registry"
    batch_root.mkdir()
    registry_root.mkdir()
    run_local_batch(
        (_batch_item("INTENT-WP12M-0001", "item-0001"),),
        batch_root,
        BatchResourceLimits(max_item_count=1),
        static_metadata={"source_package": "WP-12m / AUTO-12"},
    )

    result = build_local_run_registry((batch_root,), registry_root)

    assert result.failure_reasons == ()
    assert len(result.records) == 1
    record = result.records[0]
    assert record.source_kind == "local_batch_run"
    assert record.batch_id.startswith("BM-")
    assert record.validation_passed is True


def test_mixed_dry_run_and_batch_roots_produce_two_records(tmp_path):
    dry_root = tmp_path / "dry"
    batch_root = tmp_path / "batch"
    registry_root = tmp_path / "registry"
    dry_root.mkdir()
    batch_root.mkdir()
    registry_root.mkdir()
    run_local_dry_run(_intent(), dry_root)
    run_local_batch(
        (_batch_item("INTENT-WP12M-0001", "item-0001"),),
        batch_root,
        BatchResourceLimits(max_item_count=1),
    )

    result = build_local_run_registry((batch_root, dry_root), registry_root)

    assert result.failure_reasons == ()
    assert [record.source_kind for record in result.records] == [
        "local_batch_run",
        "local_dry_run",
    ]


def test_registry_writes_exact_file_under_registry_output_root(tmp_path):
    dry_root = tmp_path / "dry"
    registry_root = tmp_path / "registry"
    dry_root.mkdir()
    registry_root.mkdir()
    run_local_dry_run(_intent(), dry_root)

    result = build_local_run_registry((dry_root,), registry_root)

    assert result.registry_file == registry_root / LOCAL_RUN_REGISTRY_FILE_NAME
    assert result.written_files == {"local_run_registry": registry_root / LOCAL_RUN_REGISTRY_FILE_NAME}
    assert (registry_root / LOCAL_RUN_REGISTRY_FILE_NAME).exists()
    assert sorted(path.name for path in registry_root.iterdir()) == [LOCAL_RUN_REGISTRY_FILE_NAME]
    assert LOCAL_RUN_REGISTRY_FILE_NAME not in [path.name for path in dry_root.iterdir()]


def test_registry_output_contains_boundary_markers(tmp_path):
    dry_root = tmp_path / "dry"
    registry_root = tmp_path / "registry"
    dry_root.mkdir()
    registry_root.mkdir()
    run_local_dry_run(_intent(), dry_root)

    build_local_run_registry((dry_root,), registry_root)

    payload = _load(registry_root / LOCAL_RUN_REGISTRY_FILE_NAME)
    assert payload["local_only"] is True
    assert payload["research_only"] is True
    assert payload["non_authoritative"] is True
    assert payload["creates_committed_evidence"] is False
    assert payload["records"][0]["local_only"] is True
    assert payload["records"][0]["research_only"] is True
    assert payload["records"][0]["non_authoritative"] is True
    assert payload["records"][0]["creates_committed_evidence"] is False


def test_registry_records_include_source_file_hashes(tmp_path):
    dry_root = tmp_path / "dry"
    registry_root = tmp_path / "registry"
    dry_root.mkdir()
    registry_root.mkdir()
    run_local_dry_run(_intent(), dry_root)

    result = build_local_run_registry((dry_root,), registry_root)

    hashes = result.records[0].source_file_hashes
    assert set(hashes) == {"manifest", "output_bundle", "run_request", "validation_report"}
    assert all(len(value) == 64 for value in hashes.values())


def test_registry_output_is_deterministic_for_identical_source_roots(tmp_path):
    dry_root = tmp_path / "dry"
    first_registry_root = tmp_path / "registry-1"
    second_registry_root = tmp_path / "registry-2"
    dry_root.mkdir()
    first_registry_root.mkdir()
    second_registry_root.mkdir()
    run_local_dry_run(_intent(), dry_root)

    build_local_run_registry((dry_root,), first_registry_root)
    build_local_run_registry((dry_root,), second_registry_root)

    assert (first_registry_root / LOCAL_RUN_REGISTRY_FILE_NAME).read_text(
        encoding="utf-8"
    ) == (second_registry_root / LOCAL_RUN_REGISTRY_FILE_NAME).read_text(
        encoding="utf-8"
    )


def test_invalid_registry_output_root_writes_nothing(tmp_path):
    dry_root = tmp_path / "dry"
    missing_registry_root = tmp_path / "missing" / "registry"
    dry_root.mkdir()
    run_local_dry_run(_intent(), dry_root)

    result = build_local_run_registry((dry_root,), missing_registry_root)

    assert result.records == ()
    assert result.written_files == {}
    assert "registry_output_root must be an existing directory" in result.failure_reasons
    assert not missing_registry_root.exists()


def test_missing_source_root_writes_nothing(tmp_path):
    registry_root = tmp_path / "registry"
    missing_source_root = tmp_path / "missing" / "source"
    registry_root.mkdir()

    result = build_local_run_registry((missing_source_root,), registry_root)

    assert result.records == ()
    assert result.written_files == {}
    assert any("source root must be an existing directory" in reason for reason in result.failure_reasons)
    assert list(registry_root.iterdir()) == []


def test_unrecognized_source_root_writes_nothing(tmp_path):
    source_root = tmp_path / "source"
    registry_root = tmp_path / "registry"
    source_root.mkdir()
    registry_root.mkdir()
    (source_root / "unrelated.json").write_text("{}", encoding="utf-8")

    result = build_local_run_registry((source_root,), registry_root)

    assert result.records == ()
    assert result.written_files == {}
    assert any("no recognized local run signature" in reason for reason in result.failure_reasons)
    assert list(registry_root.iterdir()) == []


def test_ambiguous_source_root_writes_nothing(tmp_path):
    source_root = tmp_path / "source"
    registry_root = tmp_path / "registry"
    source_root.mkdir()
    registry_root.mkdir()
    run_local_dry_run(_intent(), source_root)
    run_local_batch(
        (_batch_item("INTENT-WP12M-0001", "item-0001"),),
        source_root,
        BatchResourceLimits(max_item_count=1),
    )

    result = build_local_run_registry((source_root,), registry_root)

    assert result.records == ()
    assert result.written_files == {}
    assert any("both dry-run and batch-run signatures" in reason for reason in result.failure_reasons)
    assert list(registry_root.iterdir()) == []


def test_invalid_json_in_required_source_file_writes_nothing(tmp_path):
    dry_root = tmp_path / "dry"
    registry_root = tmp_path / "registry"
    dry_root.mkdir()
    registry_root.mkdir()
    run_local_dry_run(_intent(), dry_root)
    (dry_root / "validation_report.json").write_text("{not-json", encoding="utf-8")

    result = build_local_run_registry((dry_root,), registry_root)

    assert result.records == ()
    assert result.written_files == {}
    assert any("validation_report.json contains invalid JSON" in reason for reason in result.failure_reasons)
    assert list(registry_root.iterdir()) == []


def test_batch_summary_validation_drift_writes_nothing(tmp_path):
    batch_root = tmp_path / "batch"
    registry_root = tmp_path / "registry"
    batch_root.mkdir()
    registry_root.mkdir()
    run_local_batch(
        (_batch_item("INTENT-WP12M-0001", "item-0001"),),
        batch_root,
        BatchResourceLimits(max_item_count=1),
    )
    summary = _load(batch_root / "local_batch_run_summary.json")
    summary["success_item_count"] = 0
    (batch_root / "local_batch_run_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    result = build_local_run_registry((batch_root,), registry_root)

    assert result.records == ()
    assert result.written_files == {}
    assert any("batch summary validation helper" in reason for reason in result.failure_reasons)
    assert list(registry_root.iterdir()) == []


def test_failed_dry_run_validation_can_be_indexed_as_failed_local_record(tmp_path):
    dry_root = tmp_path / "dry"
    registry_root = tmp_path / "registry"
    dry_root.mkdir()
    registry_root.mkdir()
    invalid_intent = ResearchIntentFixture(
        intent_id="",
        candidate_id="H-004",
        evaluation_purpose="AUTO-12 failed dry-run fixture",
        data_refs=(),
        timeframe="1d",
        evaluation_window={"start": "", "end": "2026-04-02T00:00:00Z"},
        parameters={},
        pipeline_version="wp_12m_auto_12_fixture_v1",
    )
    run_local_dry_run(invalid_intent, dry_root)

    result = build_local_run_registry((dry_root,), registry_root)

    assert result.failure_reasons == ()
    assert len(result.records) == 1
    record = result.records[0]
    assert record.source_kind == "local_dry_run"
    assert record.validation_passed is False
    assert record.protected_boundary_preserved is False
    assert record.creates_committed_evidence is False
    assert record.notes == ("failed dry-run output indexed as local non-authoritative record",)


def test_tests_do_not_write_outside_tmp_path(tmp_path):
    dry_root = tmp_path / "dry"
    registry_root = tmp_path / "registry"
    dry_root.mkdir()
    registry_root.mkdir()
    run_local_dry_run(_intent(), dry_root)

    build_local_run_registry((dry_root,), registry_root)

    assert sorted(path.name for path in tmp_path.iterdir()) == ["dry", "registry"]
    assert (registry_root / LOCAL_RUN_REGISTRY_FILE_NAME).exists()


def test_local_registry_dataclass_names_are_available():
    assert LocalRunRegistryRecord.__name__ == "LocalRunRegistryRecord"
    assert LocalRunRegistryResult.__name__ == "LocalRunRegistryResult"
