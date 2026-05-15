import json
from dataclasses import asdict
from pathlib import Path

from tools.research_automation.batch_manifest import BatchManifestItem, BatchResourceLimits
from tools.research_automation.local_batch_runner import (
    SUMMARY_FILE_NAME,
    LocalBatchItemResult,
    LocalBatchRunResult,
    LocalBatchRunSummary,
    run_local_batch,
)
from tools.research_automation.local_dry_run_runner import OUTPUT_FILE_NAMES as DRY_RUN_OUTPUT_FILE_NAMES


def _item(source_id: str, output_path: str) -> BatchManifestItem:
    return BatchManifestItem(
        source_id=source_id,
        candidate_id="H-004",
        evaluation_purpose="AUTO-07 local batch runner vertical slice fixture",
        data_refs=("local_fixture:wp12h:auto07:sample",),
        timeframe="1d",
        evaluation_window={
            "start": "2026-04-01T00:00:00Z",
            "end": "2026-04-02T00:00:00Z",
        },
        parameters={"mode": "local_batch", "max_rows": 1},
        pipeline_version="wp_12h_auto_07_fixture_v1",
        output_path=output_path,
    )


def _items() -> tuple[BatchManifestItem, BatchManifestItem]:
    return (
        _item("INTENT-WP12H-0001", "item-0001"),
        _item("INTENT-WP12H-0002", "nested/item-0002"),
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
        "source_package": "WP-12h / AUTO-07",
    }


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_ready(payload: dict) -> dict:
    return json.loads(json.dumps(payload, sort_keys=True))


def test_two_item_success_writes_manifest_summary_and_item_outputs(tmp_path):
    result = run_local_batch(_items(), tmp_path, _limits(), static_metadata=_metadata())

    assert result.summary.item_count == 2
    assert result.summary.success_item_count == 2
    assert result.summary.failed_item_count == 0
    assert result.summary.skipped_item_count == 0
    assert result.summary.blocked_item_count == 0
    assert (tmp_path / "batch_manifest.json").exists()
    assert (tmp_path / "batch_validation_report.json").exists()
    assert (tmp_path / SUMMARY_FILE_NAME).exists()
    for item_dir in (tmp_path / "item-0001", tmp_path / "nested" / "item-0002"):
        assert item_dir.is_dir()
        for file_name in DRY_RUN_OUTPUT_FILE_NAMES.values():
            assert (item_dir / file_name).exists()


def test_local_dry_run_called_once_per_item_with_item_derived_intent(tmp_path, monkeypatch):
    calls = []

    def fake_run_local_dry_run(intent, output_dir):
        calls.append((intent, output_dir))
        return type(
            "FakeDryRunResult",
            (),
            {
                "run_request": type("FakeRunRequest", (), {"run_id": f"RUN-{intent.intent_id}"})(),
                "validation_report": type(
                    "FakeValidationReport",
                    (),
                    {"passed": True, "failure_reasons": ()},
                )(),
                "written_files": {},
            },
        )()

    monkeypatch.setattr(
        "tools.research_automation.local_batch_runner.run_local_dry_run",
        fake_run_local_dry_run,
    )

    result = run_local_batch(_items(), tmp_path, _limits(), static_metadata=_metadata())

    assert result.summary.success_item_count == 2
    assert len(calls) == 2
    assert calls[0][0].intent_id == "INTENT-WP12H-0001"
    assert calls[0][0].candidate_id == "H-004"
    assert calls[0][0].data_refs == ("local_fixture:wp12h:auto07:sample",)
    assert calls[0][1] == tmp_path / "item-0001"
    assert calls[1][0].intent_id == "INTENT-WP12H-0002"
    assert calls[1][1] == tmp_path / "nested" / "item-0002"


def test_local_batch_is_deterministic_for_identical_input_and_clean_roots(tmp_path):
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()

    first = run_local_batch(_items(), first_root, _limits(), static_metadata=_metadata())
    second = run_local_batch(_items(), second_root, _limits(), static_metadata=_metadata())

    assert first.summary == second.summary
    assert (first_root / "batch_manifest.json").read_text(encoding="utf-8") == (
        second_root / "batch_manifest.json"
    ).read_text(encoding="utf-8")
    assert (first_root / SUMMARY_FILE_NAME).read_text(encoding="utf-8") == (
        second_root / SUMMARY_FILE_NAME
    ).read_text(encoding="utf-8")


def test_missing_output_root_fails_with_no_writes_and_no_parent_creation(tmp_path):
    missing_root = tmp_path / "missing" / "batch-output"

    result = run_local_batch(_items(), missing_root, _limits(), static_metadata=_metadata())

    assert result.summary.success_item_count == 0
    assert result.summary.failed_item_count == 0
    assert result.summary.protected_boundary_preserved is False
    assert result.written_files == {}
    assert result.manifest_result.written_files == {}
    assert result.summary.failure_reasons == ("output_root must be an existing directory",)
    assert not missing_root.exists()
    assert not (tmp_path / "missing").exists()


def test_file_path_output_root_fails_and_preserves_file(tmp_path):
    output_file = tmp_path / "not-a-directory"
    output_file.write_text("existing file\n", encoding="utf-8")

    result = run_local_batch(_items(), output_file, _limits(), static_metadata=_metadata())

    assert result.written_files == {}
    assert result.summary.failure_reasons == ("output_root must be an existing directory",)
    assert output_file.read_text(encoding="utf-8") == "existing file\n"
    assert [path.name for path in tmp_path.iterdir()] == ["not-a-directory"]


def test_invalid_batch_item_fails_without_calling_dry_run(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "tools.research_automation.local_batch_runner.run_local_dry_run",
        lambda intent, output_dir: calls.append((intent, output_dir)),
    )
    invalid_item = BatchManifestItem(
        source_id="",
        candidate_id="H-004",
        evaluation_purpose="AUTO-07 invalid fixture",
        data_refs=(),
        timeframe="1d",
        evaluation_window={"start": "", "end": "2026-04-02T00:00:00Z"},
        parameters={},
        pipeline_version="wp_12h_auto_07_fixture_v1",
        output_path="invalid-item-output",
    )

    result = run_local_batch((invalid_item,), tmp_path, _limits(), static_metadata=_metadata())

    assert calls == []
    assert result.manifest_result.manifest is None
    assert result.written_files == {}
    assert "items[0].source_id must be a non-empty string" in result.summary.failure_reasons
    assert not (tmp_path / SUMMARY_FILE_NAME).exists()
    assert list(tmp_path.iterdir()) == []


def test_output_path_escape_fails_without_writes_outside_tmp_path(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "tools.research_automation.local_batch_runner.run_local_dry_run",
        lambda intent, output_dir: calls.append((intent, output_dir)),
    )

    result = run_local_batch(
        (_item("INTENT-WP12H-0001", "../outside-root"),),
        tmp_path,
        _limits(),
        static_metadata=_metadata(),
    )

    assert calls == []
    assert result.written_files == {}
    assert result.summary.failure_reasons == ("items[0].output_path must be contained under output_root",)
    assert not (tmp_path.parent / "outside-root").exists()
    assert list(tmp_path.iterdir()) == []


def test_max_item_count_resource_limit_failure_blocks_execution(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "tools.research_automation.local_batch_runner.run_local_dry_run",
        lambda intent, output_dir: calls.append((intent, output_dir)),
    )

    result = run_local_batch(_items(), tmp_path, _limits(max_item_count=1), static_metadata=_metadata())

    assert calls == []
    assert result.manifest_result.manifest is None
    assert result.written_files == {}
    assert "item count exceeds resource_limits.max_item_count" in result.summary.failure_reasons
    assert list(tmp_path.iterdir()) == []


def test_summary_json_matches_returned_dataclass(tmp_path):
    result = run_local_batch(_items(), tmp_path, _limits(), static_metadata=_metadata())

    summary = _load(tmp_path / SUMMARY_FILE_NAME)

    assert summary == _json_ready(asdict(result.summary))
    assert summary["manifest_files"] == {
        "batch_manifest": "batch_manifest.json",
        "batch_validation_report": "batch_validation_report.json",
    }


def test_outputs_mark_local_research_non_authoritative_no_evidence(tmp_path):
    result = run_local_batch(_items(), tmp_path, _limits(), static_metadata=_metadata())

    assert result.local_only is True
    assert result.research_only is True
    assert result.non_authoritative is True
    assert result.creates_committed_evidence is False
    assert result.summary.local_only is True
    assert result.summary.research_only is True
    assert result.summary.non_authoritative is True
    assert result.summary.creates_committed_evidence is False
    for item_result in result.summary.item_results:
        assert item_result.local_only is True
        assert item_result.research_only is True
        assert item_result.non_authoritative is True
        assert item_result.creates_committed_evidence is False


def test_boundaries_record_no_runtime_or_trigger_behavior(tmp_path):
    result = run_local_batch(_items(), tmp_path, _limits(), static_metadata=_metadata())

    assert "no_runtime_paper_live_oms_risk_safe_mode_contact" in result.summary.checked_boundaries
    assert "no_exchange_broker_order_scheduler_daemon_queue_watcher_trigger_contact" in (
        result.summary.checked_boundaries
    )
    assert not any(
        marker in result.summary.checked_boundaries
        for marker in ("scheduler", "daemon", "queue", "watcher", "trigger")
    )
    assert result.summary.protected_boundary_preserved is True


def test_local_batch_dataclass_names_are_available():
    assert LocalBatchItemResult.__name__ == "LocalBatchItemResult"
    assert LocalBatchRunSummary.__name__ == "LocalBatchRunSummary"
    assert LocalBatchRunResult.__name__ == "LocalBatchRunResult"
