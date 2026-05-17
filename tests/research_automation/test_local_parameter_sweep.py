import json
from pathlib import Path
from types import SimpleNamespace

from tools.research_automation.local_parameter_sweep import (
    CHECKED_BOUNDARIES,
    DEFAULT_MAX_POINT_COUNT,
    SWEEP_SUMMARY_FILE_NAME,
    LocalParameterSweepResult,
    LocalParameterSweepSummary,
    ParameterSweepPoint,
    ParameterSweepPointResult,
    ParameterSweepSpec,
    run_local_parameter_sweep,
)


def _spec(**overrides) -> ParameterSweepSpec:
    values = {
        "sweep_id": "SWEEP-WP12Q-0001",
        "candidate_id": "H-004",
        "evaluation_purpose": "AUTO-16 local parameter sweep fixture",
        "data_refs": ("local_fixture:wp12q:auto16:sample",),
        "timeframe": "1d",
        "evaluation_window": {
            "start": "2026-04-01T00:00:00Z",
            "end": "2026-04-02T00:00:00Z",
        },
        "base_parameters": {"mode": "local_parameter_sweep", "max_rows": 1},
        "sweep_parameters": {"threshold": (1, 2, 3)},
        "pipeline_version": "wp_12q_auto_16_fixture_v1",
        "static_metadata": {"source_package": "WP-12q / AUTO-16"},
    }
    values.update(overrides)
    return ParameterSweepSpec(**values)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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
            batch_id="BM-FAKE",
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
        records=(SimpleNamespace(registry_record_id="LRR-FAKE"),),
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


def _run_success(tmp_path):
    output_root = tmp_path / "batch"
    registry_root = tmp_path / "registry"
    output_root.mkdir(parents=True)
    registry_root.mkdir(parents=True)
    return output_root, registry_root, run_local_parameter_sweep(_spec(), output_root, registry_root)


def test_successful_one_axis_small_sweep_writes_batch_registry_and_summary(tmp_path):
    output_root, registry_root, result = _run_success(tmp_path)

    assert result.summary is not None
    assert result.summary.point_count == 3
    assert result.summary.success_point_count == 3
    assert result.summary.failed_point_count == 0
    assert result.summary.blocked_point_count == 0
    assert result.summary.skipped_point_count == 0
    assert (output_root / "batch_manifest.json").exists()
    assert (output_root / "local_batch_run_summary.json").exists()
    assert (output_root / "local_batch_run_summary_validation.json").exists()
    assert (registry_root / "local_run_registry.json").exists()
    assert (output_root / SWEEP_SUMMARY_FILE_NAME).exists()
    assert result.registry_result.registry_validation_report is not None
    assert result.registry_result.registry_validation_report.passed is True
    summary = _load(output_root / SWEEP_SUMMARY_FILE_NAME)
    assert summary["point_count"] == 3
    assert summary["registry_record_ids"] == [
        record.registry_record_id for record in result.registry_result.records
    ]


def test_deterministic_enumeration_across_clean_roots(tmp_path):
    first_output, first_registry, first = _run_success(tmp_path / "first")
    second_output, second_registry, second = _run_success(tmp_path / "second")

    assert [point.point_id for point in first.points] == [point.point_id for point in second.points]
    assert [point.point_index for point in first.points] == [1, 2, 3]
    assert [dict(point.parameter_values) for point in first.points] == [
        {"threshold": 1},
        {"threshold": 2},
        {"threshold": 3},
    ]
    assert [result.point_id for result in first.summary.point_results] == [
        result.point_id for result in second.summary.point_results
    ]
    assert [result.status for result in first.summary.point_results] == [
        result.status for result in second.summary.point_results
    ]
    assert first.summary.point_count == second.summary.point_count
    assert first.summary.success_point_count == second.summary.success_point_count
    assert (first_output / SWEEP_SUMMARY_FILE_NAME).exists()
    assert (second_output / SWEEP_SUMMARY_FILE_NAME).exists()
    assert (first_registry / "local_run_registry.json").exists()
    assert (second_registry / "local_run_registry.json").exists()


def test_batch_compatible_fan_out_uses_point_source_ids_and_combined_parameters(tmp_path, monkeypatch):
    output_root = tmp_path / "batch"
    registry_root = tmp_path / "registry"
    output_root.mkdir()
    registry_root.mkdir()
    calls = []

    def fake_run_local_batch(items, output_root_arg, resource_limits, static_metadata=None):
        item_tuple = tuple(items)
        calls.append((item_tuple, output_root_arg, resource_limits, static_metadata))
        return _fake_batch_result(item_tuple)

    monkeypatch.setattr(
        "tools.research_automation.local_parameter_sweep.run_local_batch",
        fake_run_local_batch,
    )
    monkeypatch.setattr(
        "tools.research_automation.local_parameter_sweep.build_local_run_registry",
        lambda source_roots, registry_root_arg: _fake_registry_result(registry_root_arg),
    )

    result = run_local_parameter_sweep(_spec(), output_root, registry_root)

    assert result.summary is not None
    assert len(calls) == 1
    items, output_root_arg, resource_limits, static_metadata = calls[0]
    assert output_root_arg == output_root
    assert resource_limits.max_item_count == DEFAULT_MAX_POINT_COUNT
    assert resource_limits.max_local_jobs == 1
    assert resource_limits.max_concurrency == 1
    assert resource_limits.failure_threshold == 0
    assert static_metadata == {
        "source_package": "WP-12q / AUTO-16",
        "sweep_id": "SWEEP-WP12Q-0001",
        "implementation_id": "wp_12q_auto_16_local_parameter_sweep_v1",
    }
    assert len(items) == len(result.points)
    assert [item.source_id for item in items] == [point.point_id for point in result.points]
    assert [item.output_path for item in items] == [
        "sweep-point-0001",
        "sweep-point-0002",
        "sweep-point-0003",
    ]
    assert all(not Path(item.output_path).is_absolute() for item in items)
    assert items[0].parameters == {"mode": "local_parameter_sweep", "max_rows": 1, "threshold": 1}
    assert items[2].parameters == {"mode": "local_parameter_sweep", "max_rows": 1, "threshold": 3}


def test_local_registry_integration_returns_actual_record_ids(tmp_path):
    _, registry_root, result = _run_success(tmp_path)

    assert result.registry_result.registry_file == registry_root / "local_run_registry.json"
    assert result.registry_result.registry_validation_report.passed is True
    assert len(result.registry_result.records) == 1
    assert result.registry_result.records[0].source_kind == "local_batch_run"
    assert result.summary.registry_record_ids == tuple(
        record.registry_record_id for record in result.registry_result.records
    )


def test_invalid_missing_output_root_fails_before_calls_and_writes(tmp_path, monkeypatch):
    missing_output_root = tmp_path / "missing" / "batch"
    registry_root = tmp_path / "registry"
    registry_root.mkdir()
    calls = []
    monkeypatch.setattr(
        "tools.research_automation.local_parameter_sweep.run_local_batch",
        lambda *args, **kwargs: calls.append(("batch", args, kwargs)),
    )
    monkeypatch.setattr(
        "tools.research_automation.local_parameter_sweep.build_local_run_registry",
        lambda *args, **kwargs: calls.append(("registry", args, kwargs)),
    )

    result = run_local_parameter_sweep(_spec(), missing_output_root, registry_root)

    assert calls == []
    assert result.summary is None
    assert result.summary_file is None
    assert result.written_files == {}
    assert "output_root must be an existing directory" in result.failure_reasons
    assert not missing_output_root.exists()
    assert not (tmp_path / "missing").exists()
    assert list(registry_root.iterdir()) == []


def test_invalid_missing_registry_output_root_fails_before_calls_and_writes(tmp_path, monkeypatch):
    output_root = tmp_path / "batch"
    missing_registry_root = tmp_path / "missing" / "registry"
    output_root.mkdir()
    calls = []
    monkeypatch.setattr(
        "tools.research_automation.local_parameter_sweep.run_local_batch",
        lambda *args, **kwargs: calls.append(("batch", args, kwargs)),
    )
    monkeypatch.setattr(
        "tools.research_automation.local_parameter_sweep.build_local_run_registry",
        lambda *args, **kwargs: calls.append(("registry", args, kwargs)),
    )

    result = run_local_parameter_sweep(_spec(), output_root, missing_registry_root)

    assert calls == []
    assert result.written_files == {}
    assert "registry_output_root must be an existing directory" in result.failure_reasons
    assert not missing_registry_root.exists()
    assert not (tmp_path / "missing").exists()
    assert list(output_root.iterdir()) == []


def test_empty_grid_fails_before_execution(tmp_path, monkeypatch):
    output_root = tmp_path / "batch"
    registry_root = tmp_path / "registry"
    output_root.mkdir()
    registry_root.mkdir()
    calls = []
    monkeypatch.setattr(
        "tools.research_automation.local_parameter_sweep.run_local_batch",
        lambda *args, **kwargs: calls.append(("batch", args, kwargs)),
    )
    result = run_local_parameter_sweep(
        _spec(sweep_parameters={}),
        output_root,
        registry_root,
    )

    assert calls == []
    assert "sweep_parameters must contain at least one axis" in result.failure_reasons
    assert list(output_root.iterdir()) == []
    assert list(registry_root.iterdir()) == []


def test_excessive_point_count_fails_before_execution(tmp_path, monkeypatch):
    output_root = tmp_path / "batch"
    registry_root = tmp_path / "registry"
    output_root.mkdir()
    registry_root.mkdir()
    calls = []
    monkeypatch.setattr(
        "tools.research_automation.local_parameter_sweep.run_local_batch",
        lambda *args, **kwargs: calls.append(("batch", args, kwargs)),
    )

    result = run_local_parameter_sweep(
        _spec(sweep_parameters={"threshold": (1, 2, 3)}),
        output_root,
        registry_root,
        max_point_count=2,
    )

    assert calls == []
    assert result.failure_reasons == ("sweep point count exceeds max_point_count",)
    assert list(output_root.iterdir()) == []
    assert list(registry_root.iterdir()) == []


def test_duplicate_parameter_combinations_fail_before_execution(tmp_path, monkeypatch):
    output_root = tmp_path / "batch"
    registry_root = tmp_path / "registry"
    output_root.mkdir()
    registry_root.mkdir()
    calls = []
    monkeypatch.setattr(
        "tools.research_automation.local_parameter_sweep.run_local_batch",
        lambda *args, **kwargs: calls.append(("batch", args, kwargs)),
    )

    result = run_local_parameter_sweep(
        _spec(sweep_parameters={"threshold": (1, 1)}),
        output_root,
        registry_root,
    )

    assert calls == []
    assert "sweep_parameters.threshold contains duplicate values" in result.failure_reasons
    assert list(output_root.iterdir()) == []
    assert list(registry_root.iterdir()) == []


def test_base_sweep_overlap_fails_before_execution(tmp_path):
    output_root = tmp_path / "batch"
    registry_root = tmp_path / "registry"
    output_root.mkdir()
    registry_root.mkdir()

    result = run_local_parameter_sweep(
        _spec(
            base_parameters={"threshold": 0},
            sweep_parameters={"threshold": (1, 2)},
        ),
        output_root,
        registry_root,
    )

    assert "sweep_parameters.threshold overlaps base_parameters" in result.failure_reasons
    assert list(output_root.iterdir()) == []
    assert list(registry_root.iterdir()) == []


def test_non_serializable_parameter_value_fails_before_execution(tmp_path):
    output_root = tmp_path / "batch"
    registry_root = tmp_path / "registry"
    output_root.mkdir()
    registry_root.mkdir()

    result = run_local_parameter_sweep(
        _spec(sweep_parameters={"threshold": (object(),)}),
        output_root,
        registry_root,
    )

    assert "sweep_parameters.threshold values must be JSON-serializable" in result.failure_reasons
    assert list(output_root.iterdir()) == []
    assert list(registry_root.iterdir()) == []


def test_downstream_batch_failure_writes_no_sweep_summary(tmp_path, monkeypatch):
    output_root = tmp_path / "batch"
    registry_root = tmp_path / "registry"
    output_root.mkdir()
    registry_root.mkdir()
    registry_calls = []

    failed_batch = SimpleNamespace(
        summary=SimpleNamespace(
            item_results=(),
            failure_reasons=("forced local batch failure",),
            protected_boundary_preserved=False,
        ),
        summary_validation_report=None,
        written_files={},
        protected_boundary_preserved=False,
        failure_reasons=("forced local batch failure",),
    )
    monkeypatch.setattr(
        "tools.research_automation.local_parameter_sweep.run_local_batch",
        lambda *args, **kwargs: failed_batch,
    )
    monkeypatch.setattr(
        "tools.research_automation.local_parameter_sweep.build_local_run_registry",
        lambda *args, **kwargs: registry_calls.append((args, kwargs)),
    )

    result = run_local_parameter_sweep(_spec(), output_root, registry_root)

    assert registry_calls == []
    assert result.summary is None
    assert "forced local batch failure" in result.failure_reasons
    assert not (output_root / SWEEP_SUMMARY_FILE_NAME).exists()


def test_downstream_registry_failure_writes_no_sweep_summary(tmp_path, monkeypatch):
    output_root = tmp_path / "batch"
    registry_root = tmp_path / "registry"
    output_root.mkdir()
    registry_root.mkdir()
    failed_registry = SimpleNamespace(
        records=(),
        registry_file=None,
        written_files={},
        failure_reasons=("forced local registry failure",),
        registry_validation_report=SimpleNamespace(passed=False),
        protected_boundary_preserved=False,
    )
    monkeypatch.setattr(
        "tools.research_automation.local_parameter_sweep.build_local_run_registry",
        lambda *args, **kwargs: failed_registry,
    )

    result = run_local_parameter_sweep(_spec(), output_root, registry_root)

    assert result.summary is None
    assert "forced local registry failure" in result.failure_reasons
    assert not (output_root / SWEEP_SUMMARY_FILE_NAME).exists()


def test_boundary_markers_are_preserved(tmp_path):
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


def test_summary_json_has_no_interpretive_authority_fields(tmp_path):
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

    def collect_keys(value):
        if isinstance(value, dict):
            keys = set(value)
            for item in value.values():
                keys.update(collect_keys(item))
            return keys
        if isinstance(value, list):
            keys = set()
            for item in value:
                keys.update(collect_keys(item))
            return keys
        return set()

    assert forbidden_keys.isdisjoint(collect_keys(payload))


def test_local_parameter_sweep_dataclass_names_are_available():
    assert ParameterSweepSpec.__name__ == "ParameterSweepSpec"
    assert ParameterSweepPoint.__name__ == "ParameterSweepPoint"
    assert ParameterSweepPointResult.__name__ == "ParameterSweepPointResult"
    assert LocalParameterSweepSummary.__name__ == "LocalParameterSweepSummary"
    assert LocalParameterSweepResult.__name__ == "LocalParameterSweepResult"
