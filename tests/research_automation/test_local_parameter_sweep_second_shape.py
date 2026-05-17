import json
from pathlib import Path
from types import SimpleNamespace

from tools.research_automation import local_parameter_sweep
from tools.research_automation.local_parameter_sweep import (
    CHECKED_BOUNDARIES,
    SWEEP_SUMMARY_FILE_NAME,
    ParameterSweepSpec,
    run_local_parameter_sweep,
)


EXPECTED_PARAMETER_VALUES = (
    {"alpha": 1, "zeta": "low"},
    {"alpha": 1, "zeta": "high"},
    {"alpha": 2, "zeta": "low"},
    {"alpha": 2, "zeta": "high"},
)


def _spec(**overrides) -> ParameterSweepSpec:
    values = {
        "sweep_id": "SWEEP-WP12R-0001",
        "candidate_id": "H-004",
        "evaluation_purpose": "AUTO-17 local parameter sweep second-shape fixture",
        "data_refs": ("local_fixture:wp12r:auto17:sample",),
        "timeframe": "1h",
        "evaluation_window": {
            "start": "2026-04-03T00:00:00Z",
            "end": "2026-04-03T01:00:00Z",
        },
        "base_parameters": {"mode": "second_shape", "max_rows": 1},
        "sweep_parameters": {
            "zeta": ("low", "high"),
            "alpha": (1, 2),
        },
        "pipeline_version": "wp_12r_auto_17_fixture_v1",
        "static_metadata": {"source_package": "WP-12r / AUTO-17"},
    }
    values.update(overrides)
    return ParameterSweepSpec(**values)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_success(tmp_path):
    output_root = tmp_path / "batch"
    registry_root = tmp_path / "registry"
    output_root.mkdir(parents=True)
    registry_root.mkdir(parents=True)
    result = run_local_parameter_sweep(_spec(), output_root, registry_root, max_point_count=4)
    return output_root, registry_root, result


def _fake_batch_result(items):
    item_results = tuple(
        SimpleNamespace(
            item_id=f"BMI-{index:04d}",
            source_id=item.source_id,
            status="succeeded",
            output_path=item.output_path,
            dry_run_run_id=f"LDR-{index:04d}",
            failure_reasons=(),
        )
        for index, item in enumerate(items, start=1)
    )
    return SimpleNamespace(
        summary=SimpleNamespace(
            batch_id="BM-WP12R-FAKE",
            item_results=item_results,
            failure_reasons=(),
            protected_boundary_preserved=True,
        ),
        summary_validation_report=SimpleNamespace(passed=True),
        written_files={
            "local_batch_run_summary": "local_batch_run_summary.json",
            "local_batch_run_summary_validation": "local_batch_run_summary_validation.json",
        },
        protected_boundary_preserved=True,
        failure_reasons=(),
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
    )


def _fake_registry_result(registry_root: Path):
    registry_file = registry_root / "local_run_registry.json"
    return SimpleNamespace(
        records=(SimpleNamespace(registry_record_id="LRR-WP12R-FAKE"),),
        registry_file=registry_file,
        written_files={"local_run_registry": registry_file},
        failure_reasons=(),
        registry_validation_report=SimpleNamespace(passed=True),
        protected_boundary_preserved=True,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
    )


def _collect_keys(value):
    if isinstance(value, dict):
        keys = set(value)
        for item in value.values():
            keys.update(_collect_keys(item))
        return keys
    if isinstance(value, list):
        keys = set()
        for item in value:
            keys.update(_collect_keys(item))
        return keys
    return set()


def test_two_axis_second_shape_writes_batch_registry_and_summary(tmp_path):
    output_root, registry_root, result = _run_success(tmp_path)

    assert result.summary is not None
    assert result.summary_file == output_root / SWEEP_SUMMARY_FILE_NAME
    assert result.summary.point_count == 4
    assert result.summary.success_point_count == 4
    assert result.summary.failed_point_count == 0
    assert result.summary.blocked_point_count == 0
    assert result.summary.skipped_point_count == 0
    assert (output_root / "batch_manifest.json").exists()
    assert (output_root / "local_batch_run_summary.json").exists()
    assert (output_root / "local_batch_run_summary_validation.json").exists()
    assert (registry_root / "local_run_registry.json").exists()
    assert (output_root / SWEEP_SUMMARY_FILE_NAME).exists()

    summary = _load(output_root / SWEEP_SUMMARY_FILE_NAME)
    assert summary["registry_record_ids"] == [
        record.registry_record_id for record in result.registry_result.records
    ]
    assert result.summary.registry_record_ids == tuple(
        record.registry_record_id for record in result.registry_result.records
    )


def test_two_axis_second_shape_uses_lexicographic_axis_order_and_stable_ids(tmp_path):
    _, _, first = _run_success(tmp_path / "first")
    _, _, second = _run_success(tmp_path / "second")

    assert [point.point_id for point in first.points] == [point.point_id for point in second.points]
    assert [point.point_index for point in first.points] == [1, 2, 3, 4]
    assert [dict(point.parameter_values) for point in first.points] == list(EXPECTED_PARAMETER_VALUES)
    assert [point_result.point_id for point_result in first.summary.point_results] == [
        point.point_id for point in first.points
    ]
    assert [point_result.point_id for point_result in second.summary.point_results] == [
        point.point_id for point in second.points
    ]


def test_two_axis_second_shape_fans_out_batch_items_with_combined_parameters(tmp_path, monkeypatch):
    output_root = tmp_path / "batch"
    registry_root = tmp_path / "registry"
    output_root.mkdir()
    registry_root.mkdir()
    batch_calls = []
    registry_calls = []

    def fake_run_local_batch(items, output_root_arg, resource_limits, static_metadata=None):
        item_tuple = tuple(items)
        batch_calls.append((item_tuple, output_root_arg, resource_limits, static_metadata))
        return _fake_batch_result(item_tuple)

    def fake_build_local_run_registry(source_roots, registry_root_arg):
        registry_calls.append((source_roots, registry_root_arg))
        return _fake_registry_result(registry_root_arg)

    monkeypatch.setattr(local_parameter_sweep, "run_local_batch", fake_run_local_batch)
    monkeypatch.setattr(local_parameter_sweep, "build_local_run_registry", fake_build_local_run_registry)

    result = run_local_parameter_sweep(_spec(), output_root, registry_root, max_point_count=4)

    assert result.summary is not None
    assert len(batch_calls) == 1
    assert len(registry_calls) == 1
    items, output_root_arg, resource_limits, static_metadata = batch_calls[0]
    assert output_root_arg == output_root
    assert len(items) == 4
    assert [item.output_path for item in items] == [
        "sweep-point-0001",
        "sweep-point-0002",
        "sweep-point-0003",
        "sweep-point-0004",
    ]
    assert [item.parameters for item in items] == [
        {"mode": "second_shape", "max_rows": 1, "alpha": 1, "zeta": "low"},
        {"mode": "second_shape", "max_rows": 1, "alpha": 1, "zeta": "high"},
        {"mode": "second_shape", "max_rows": 1, "alpha": 2, "zeta": "low"},
        {"mode": "second_shape", "max_rows": 1, "alpha": 2, "zeta": "high"},
    ]
    assert resource_limits.max_item_count == 4
    assert resource_limits.max_local_jobs == 1
    assert resource_limits.max_concurrency == 1
    assert resource_limits.failure_threshold == 0
    assert static_metadata == {
        "source_package": "WP-12q / AUTO-16",
        "sweep_id": "SWEEP-WP12R-0001",
        "implementation_id": "wp_12q_auto_16_local_parameter_sweep_v1",
    }
    assert result.summary.registry_record_ids == ("LRR-WP12R-FAKE",)


def test_two_axis_second_shape_max_point_count_blocks_before_downstream_calls(tmp_path, monkeypatch):
    output_root = tmp_path / "batch"
    registry_root = tmp_path / "registry"
    output_root.mkdir()
    registry_root.mkdir()
    calls = []

    monkeypatch.setattr(local_parameter_sweep, "run_local_batch", lambda *args, **kwargs: calls.append("batch"))
    monkeypatch.setattr(
        local_parameter_sweep,
        "build_local_run_registry",
        lambda *args, **kwargs: calls.append("registry"),
    )

    result = run_local_parameter_sweep(_spec(), output_root, registry_root, max_point_count=3)

    assert calls == []
    assert result.summary is None
    assert result.written_files == {}
    assert result.failure_reasons == ("sweep point count exceeds max_point_count",)
    assert list(output_root.iterdir()) == []
    assert list(registry_root.iterdir()) == []


def test_second_shape_summary_has_no_interpretive_authority_fields(tmp_path):
    output_root, _, _ = _run_success(tmp_path)
    payload = _load(output_root / SWEEP_SUMMARY_FILE_NAME)
    forbidden_keys = {
        "best_parameter",
        "winner",
        "rank",
        "score",
        "recommendation",
        "approval",
        "promotion",
        "readiness",
        "lifecycle",
        "policy_action",
        "runtime_action",
        "paper_live_readiness",
    }

    assert forbidden_keys.isdisjoint(_collect_keys(payload))


def test_second_shape_boundary_markers_are_preserved(tmp_path):
    _, _, result = _run_success(tmp_path)

    assert result.local_only is True
    assert result.research_only is True
    assert result.non_authoritative is True
    assert result.creates_committed_evidence is False
    assert result.protected_boundary_preserved is True
    assert result.summary.local_only is True
    assert result.summary.research_only is True
    assert result.summary.non_authoritative is True
    assert result.summary.creates_committed_evidence is False
    assert result.summary.protected_boundary_preserved is True
    for point in result.points:
        assert point.local_only is True
        assert point.research_only is True
        assert point.non_authoritative is True
        assert point.creates_committed_evidence is False
    for point_result in result.summary.point_results:
        assert point_result.local_only is True
        assert point_result.research_only is True
        assert point_result.non_authoritative is True
        assert point_result.creates_committed_evidence is False
    assert "no_runtime_paper_live_oms_risk_safe_mode_contact" in result.summary.checked_boundaries
    assert "no_exchange_broker_order_scheduler_daemon_queue_watcher_trigger_contact" in (
        result.summary.checked_boundaries
    )
    assert CHECKED_BOUNDARIES == result.summary.checked_boundaries
