import json
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace

from tools.research_automation.local_parameter_sweep import ParameterSweepSpec
from tools.research_automation.local_json_sweep_spec_loader import (
    LocalJsonParameterSweepRunResult,
    LocalJsonSweepSpecLoadResult,
    load_local_json_sweep_spec,
    run_local_json_parameter_sweep,
)


def _payload(**overrides):
    payload = {
        "spec_version": "wp12t-design-v1",
        "materialization_kind": "local_parameter_sweep_spec",
        "locality": {
            "local_only": True,
            "research_only": True,
            "non_authoritative": True,
            "creates_committed_evidence": False,
        },
        "boundary_markers": [
            "additive_to_in_memory_parameter_sweep_spec",
            "not_canonical_research_artifact",
            "not_tools_registry_validated",
            "not_query_layer_exposed",
            "no_runtime_or_downstream_authority",
        ],
        "parameter_sweep_spec": {
            "sweep_id": "SWEEP-WP12U-0001",
            "candidate_id": "H-004",
            "evaluation_purpose": "AUTO-20 JSON loader fixture",
            "data_refs": ["local_fixture:wp12u:auto20:sample"],
            "timeframe": "1d",
            "evaluation_window": {
                "start": "2026-04-04T00:00:00Z",
                "end": "2026-04-05T00:00:00Z",
            },
            "base_parameters": {"mode": "json_sweep_spec_loader", "max_rows": 1},
            "sweep_parameters": {"threshold": [3, 1, 2]},
            "pipeline_version": "wp_12u_auto_20_fixture_v1",
            "static_metadata": {"source_package": "WP-12u / AUTO-20"},
        },
    }
    payload.update(overrides)
    return payload


def _write_json(path: Path, payload):
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _spec_path(tmp_path: Path, payload=None) -> Path:
    return _write_json(tmp_path / "caller_provided_sweep_spec.json", payload or _payload())


def _assert_empty_roots(*roots: Path) -> None:
    for root in roots:
        if root.exists():
            assert list(root.iterdir()) == []


def _run_with_invalid_payload(tmp_path, monkeypatch, payload):
    calls = []
    output_root = tmp_path / "output"
    registry_root = tmp_path / "registry"
    output_root.mkdir()
    registry_root.mkdir()
    spec_path = _spec_path(tmp_path, payload)
    monkeypatch.setattr(
        "tools.research_automation.local_json_sweep_spec_loader.run_local_parameter_sweep",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    result = run_local_json_parameter_sweep(spec_path, output_root, registry_root)

    assert calls == []
    assert result.sweep_result is None
    assert result.failure_reasons
    _assert_empty_roots(output_root, registry_root)
    return result


def test_valid_wp12t_json_loads_into_parameter_sweep_spec(tmp_path):
    spec_path = _spec_path(tmp_path)

    result = load_local_json_sweep_spec(spec_path)

    assert result.failure_reasons == ()
    assert isinstance(result.spec, ParameterSweepSpec)
    assert result.spec.data_refs == ("local_fixture:wp12u:auto20:sample",)
    assert result.spec.sweep_parameters["threshold"] == (3, 1, 2)
    assert list(result.spec.sweep_parameters["threshold"]) == [3, 1, 2]
    assert result.local_only is True
    assert result.research_only is True
    assert result.non_authoritative is True
    assert result.creates_committed_evidence is False
    assert result.protected_boundary_preserved is True
    assert sorted(path.name for path in tmp_path.iterdir()) == ["caller_provided_sweep_spec.json"]


def test_json_run_wrapper_delegates_after_successful_load(tmp_path, monkeypatch):
    calls = []
    spec_path = _spec_path(tmp_path)
    output_root = tmp_path / "output"
    registry_root = tmp_path / "registry"
    output_root.mkdir()
    registry_root.mkdir()
    fake_sweep_result = SimpleNamespace(
        failure_reasons=(),
        protected_boundary_preserved=True,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
    )

    def fake_run_local_parameter_sweep(spec, output_root_arg, registry_root_arg, *, max_point_count):
        calls.append((spec, output_root_arg, registry_root_arg, max_point_count))
        return fake_sweep_result

    monkeypatch.setattr(
        "tools.research_automation.local_json_sweep_spec_loader.run_local_parameter_sweep",
        fake_run_local_parameter_sweep,
    )

    result = run_local_json_parameter_sweep(
        spec_path,
        output_root,
        registry_root,
        max_point_count=4,
    )

    assert len(calls) == 1
    spec, output_arg, registry_arg, max_point_count = calls[0]
    assert isinstance(spec, ParameterSweepSpec)
    assert output_arg == output_root
    assert registry_arg == registry_root
    assert max_point_count == 4
    assert result.sweep_result is fake_sweep_result
    assert result.failure_reasons == ()
    _assert_empty_roots(output_root, registry_root)


def test_invalid_json_fails_before_downstream_call_and_writes_nothing(tmp_path, monkeypatch):
    calls = []
    output_root = tmp_path / "output"
    registry_root = tmp_path / "registry"
    output_root.mkdir()
    registry_root.mkdir()
    spec_path = tmp_path / "bad.json"
    spec_path.write_text("{not-json", encoding="utf-8")
    monkeypatch.setattr(
        "tools.research_automation.local_json_sweep_spec_loader.run_local_parameter_sweep",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    result = run_local_json_parameter_sweep(spec_path, output_root, registry_root)

    assert calls == []
    assert result.sweep_result is None
    assert result.failure_reasons
    _assert_empty_roots(output_root, registry_root)


def test_non_object_top_level_fails_before_downstream_call_and_writes_nothing(tmp_path, monkeypatch):
    _run_with_invalid_payload(tmp_path, monkeypatch, ["not", "object"])


def test_missing_required_top_level_field_fails_before_downstream_call_and_writes_nothing(tmp_path, monkeypatch):
    payload = _payload()
    payload.pop("spec_version")

    result = _run_with_invalid_payload(tmp_path, monkeypatch, payload)

    assert "top_level.spec_version is required" in result.failure_reasons


def test_unexpected_extra_top_level_field_fails_before_downstream_call_and_writes_nothing(tmp_path, monkeypatch):
    payload = _payload(extra_authority="not allowed")

    result = _run_with_invalid_payload(tmp_path, monkeypatch, payload)

    assert "top_level.extra_authority is not supported" in result.failure_reasons


def test_unsupported_spec_version_fails_before_downstream_call_and_writes_nothing(tmp_path, monkeypatch):
    result = _run_with_invalid_payload(tmp_path, monkeypatch, _payload(spec_version="future"))

    assert "unsupported spec_version" in result.failure_reasons


def test_unsupported_materialization_kind_fails_before_downstream_call_and_writes_nothing(tmp_path, monkeypatch):
    result = _run_with_invalid_payload(tmp_path, monkeypatch, _payload(materialization_kind="other"))

    assert "unsupported materialization_kind" in result.failure_reasons


def test_invalid_locality_marker_fails_before_downstream_call_and_writes_nothing(tmp_path, monkeypatch):
    payload = _payload()
    payload["locality"]["local_only"] = False

    result = _run_with_invalid_payload(tmp_path, monkeypatch, payload)

    assert "locality.local_only must be true" in result.failure_reasons


def test_missing_required_boundary_marker_fails_before_downstream_call_and_writes_nothing(tmp_path, monkeypatch):
    payload = _payload()
    payload["boundary_markers"] = [
        marker
        for marker in payload["boundary_markers"]
        if marker != "not_query_layer_exposed"
    ]

    result = _run_with_invalid_payload(tmp_path, monkeypatch, payload)

    assert "boundary_markers missing not_query_layer_exposed" in result.failure_reasons


def test_bare_string_data_refs_fails_before_downstream_call_and_writes_nothing(tmp_path, monkeypatch):
    payload = _payload()
    payload["parameter_sweep_spec"]["data_refs"] = "local_fixture:bad"

    result = _run_with_invalid_payload(tmp_path, monkeypatch, payload)

    assert "parameter_sweep_spec.data_refs must be an array of non-empty strings" in result.failure_reasons


def test_missing_evaluation_window_end_fails_before_downstream_call_and_writes_nothing(tmp_path, monkeypatch):
    payload = _payload()
    payload["parameter_sweep_spec"]["evaluation_window"].pop("end")

    result = _run_with_invalid_payload(tmp_path, monkeypatch, payload)

    assert "evaluation_window.end must be a non-empty string" in result.failure_reasons


def test_non_array_sweep_axis_values_fail_before_downstream_call_and_write_nothing(tmp_path, monkeypatch):
    payload = _payload()
    payload["parameter_sweep_spec"]["sweep_parameters"]["threshold"] = 1

    result = _run_with_invalid_payload(tmp_path, monkeypatch, payload)

    assert "sweep_parameters.threshold must be an array" in result.failure_reasons


def test_duplicate_sweep_axis_values_fail_before_downstream_call_and_write_nothing(tmp_path, monkeypatch):
    payload = _payload()
    payload["parameter_sweep_spec"]["sweep_parameters"]["threshold"] = [{"x": 1}, {"x": 1}]

    result = _run_with_invalid_payload(tmp_path, monkeypatch, payload)

    assert "sweep_parameters.threshold contains duplicate values" in result.failure_reasons


def test_dotted_sweep_parameter_name_fails_before_downstream_call_and_writes_nothing(tmp_path, monkeypatch):
    payload = _payload()
    payload["parameter_sweep_spec"]["sweep_parameters"] = {"bad.name": [1]}

    result = _run_with_invalid_payload(tmp_path, monkeypatch, payload)

    assert "sweep_parameters keys must be non-empty unambiguous strings" in result.failure_reasons


def test_base_sweep_parameter_overlap_fails_before_downstream_call_and_writes_nothing(tmp_path, monkeypatch):
    payload = _payload()
    payload["parameter_sweep_spec"]["sweep_parameters"] = {"mode": ["fast"]}

    result = _run_with_invalid_payload(tmp_path, monkeypatch, payload)

    assert "sweep_parameters.mode overlaps base_parameters" in result.failure_reasons


def test_duplicate_json_key_detection_fails_before_downstream_call_and_writes_nothing(tmp_path, monkeypatch):
    calls = []
    output_root = tmp_path / "output"
    registry_root = tmp_path / "registry"
    output_root.mkdir()
    registry_root.mkdir()
    spec_path = tmp_path / "duplicate.json"
    spec_path.write_text(
        """
{
  "spec_version": "wp12t-design-v1",
  "materialization_kind": "local_parameter_sweep_spec",
  "locality": {
    "local_only": true,
    "research_only": true,
    "non_authoritative": true,
    "creates_committed_evidence": false
  },
  "boundary_markers": [
    "additive_to_in_memory_parameter_sweep_spec",
    "not_canonical_research_artifact",
    "not_tools_registry_validated",
    "not_query_layer_exposed",
    "no_runtime_or_downstream_authority"
  ],
  "parameter_sweep_spec": {
    "sweep_id": "SWEEP-WP12U-0001",
    "sweep_id": "SWEEP-WP12U-DUPLICATE"
  }
}
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "tools.research_automation.local_json_sweep_spec_loader.run_local_parameter_sweep",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    result = run_local_json_parameter_sweep(spec_path, output_root, registry_root)

    assert calls == []
    assert result.sweep_result is None
    assert result.failure_reasons == ("duplicate JSON object key: sweep_id",)
    _assert_empty_roots(output_root, registry_root)


def test_static_metadata_non_string_value_fails_before_downstream_call_and_writes_nothing(tmp_path, monkeypatch):
    payload = _payload()
    payload["parameter_sweep_spec"]["static_metadata"]["source_package"] = 12

    result = _run_with_invalid_payload(tmp_path, monkeypatch, payload)

    assert "static_metadata.source_package must be a non-empty string" in result.failure_reasons


def test_loader_and_wrapper_results_expose_boundary_flags(tmp_path, monkeypatch):
    spec_path = _spec_path(tmp_path)
    output_root = tmp_path / "output"
    registry_root = tmp_path / "registry"
    output_root.mkdir()
    registry_root.mkdir()
    monkeypatch.setattr(
        "tools.research_automation.local_json_sweep_spec_loader.run_local_parameter_sweep",
        lambda *args, **kwargs: SimpleNamespace(
            failure_reasons=(),
            protected_boundary_preserved=True,
        ),
    )

    load_result = load_local_json_sweep_spec(spec_path)
    run_result = run_local_json_parameter_sweep(spec_path, output_root, registry_root)

    for result in (load_result, run_result):
        assert result.local_only is True
        assert result.research_only is True
        assert result.non_authoritative is True
        assert result.creates_committed_evidence is False
        assert result.protected_boundary_preserved is True


def test_result_dataclasses_do_not_introduce_authority_fields():
    forbidden_names = {
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
    }

    load_fields = {field.name for field in fields(LocalJsonSweepSpecLoadResult)}
    run_fields = {field.name for field in fields(LocalJsonParameterSweepRunResult)}

    assert forbidden_names.isdisjoint(load_fields)
    assert forbidden_names.isdisjoint(run_fields)
