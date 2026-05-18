import inspect
import json
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace

from tools.research_automation import local_sweep_result_index
from tools.research_automation.local_sweep_result_index import (
    CHECKED_BOUNDARIES,
    RESULT_INDEX_FILE_NAME,
    LocalSweepPointIndexRef,
    LocalSweepResultIndex,
    LocalSweepResultIndexWriteResult,
    write_local_sweep_result_index,
)


FORBIDDEN_AUTHORITY_FIELDS = {
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


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_summary_file(output_root: Path) -> Path:
    summary_file = output_root / "local_parameter_sweep_summary.json"
    summary_file.write_text('{"local_only": true}\n', encoding="utf-8")
    return summary_file


def _point(point_id: str, index: int, *, status: str = "succeeded"):
    return SimpleNamespace(
        point_id=point_id,
        point_index=index,
        parameter_values={"threshold": index},
        batch_item_id=f"BMI-{index:04d}",
        status=status,
        output_path=f"sweep-point-{index:04d}",
        dry_run_run_id=f"LDR-{index:04d}",
        failure_reasons=(),
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
    )


def _summary(**overrides):
    values = {
        "sweep_id": "SWEEP-WP12W-0001",
        "point_count": 2,
        "point_results": (_point("LPSP-0001", 1), _point("LPSP-0002", 2)),
        "batch_summary_file": "local_batch_run_summary.json",
        "batch_summary_validation_file": "local_batch_run_summary_validation.json",
        "registry_file": "local_run_registry.json",
        "registry_record_ids": ("LRR-ACTUAL-0001",),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _sweep_result(output_root: Path, **overrides):
    summary_file = overrides.pop("summary_file", None)
    if summary_file is None:
        summary_file = _write_summary_file(output_root)
    values = {
        "summary": _summary(),
        "summary_file": summary_file,
        "local_only": True,
        "research_only": True,
        "non_authoritative": True,
        "creates_committed_evidence": False,
        "protected_boundary_preserved": True,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


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


def test_successful_index_write_after_completed_local_sweep_summary(tmp_path):
    result = write_local_sweep_result_index(_sweep_result(tmp_path), tmp_path)

    assert result.failure_reasons == ()
    assert result.index_file == tmp_path / RESULT_INDEX_FILE_NAME
    assert result.written_files == {"local_sweep_result_index": tmp_path / RESULT_INDEX_FILE_NAME}
    assert result.index_file.exists()
    payload = _load(result.index_file)
    assert payload["index_version"] == "wp12w-local-sweep-result-index-v1"
    assert payload["index_kind"] == "local_sweep_result_index"
    assert payload["implementation_id"] == "wp_12w_auto_22_local_sweep_result_index_v1"
    assert payload["package_label"] == "WP-12w / AUTO-22"
    assert payload["sweep_id"] == "SWEEP-WP12W-0001"
    assert payload["sweep_summary_file"].endswith("local_parameter_sweep_summary.json")
    assert payload["batch_summary_file"] == "local_batch_run_summary.json"
    assert payload["batch_summary_validation_file"] == "local_batch_run_summary_validation.json"
    assert payload["registry_file"] == "local_run_registry.json"
    assert payload["registry_record_ids"] == ["LRR-ACTUAL-0001"]
    assert payload["point_count"] == 2
    assert payload["checked_boundaries"] == list(CHECKED_BOUNDARIES)
    assert payload["local_only"] is True
    assert payload["research_only"] is True
    assert payload["non_authoritative"] is True
    assert payload["creates_committed_evidence"] is False
    assert payload["protected_boundary_preserved"] is True
    assert payload["point_refs"] == [
        {
            "batch_item_id": "BMI-0001",
            "dry_run_run_id": "LDR-0001",
            "output_path": "sweep-point-0001",
            "point_id": "LPSP-0001",
            "point_index": 1,
            "status": "succeeded",
        },
        {
            "batch_item_id": "BMI-0002",
            "dry_run_run_id": "LDR-0002",
            "output_path": "sweep-point-0002",
            "point_id": "LPSP-0002",
            "point_index": 2,
            "status": "succeeded",
        },
    ]


def test_failure_when_output_root_is_missing(tmp_path):
    missing = tmp_path / "missing" / "output"
    result = write_local_sweep_result_index(SimpleNamespace(), missing)

    assert result.index is None
    assert result.index_file is None
    assert result.written_files == {}
    assert result.failure_reasons == ("output_root must be an existing directory",)
    assert not missing.exists()
    assert not (tmp_path / "missing").exists()


def test_failure_when_sweep_summary_is_missing(tmp_path):
    sweep_result = _sweep_result(tmp_path, summary=None)

    result = write_local_sweep_result_index(sweep_result, tmp_path)

    assert result.index is None
    assert result.index_file is None
    assert result.written_files == {}
    assert result.failure_reasons == ("sweep_result.summary is required",)
    assert not (tmp_path / RESULT_INDEX_FILE_NAME).exists()


def test_failure_when_summary_file_is_missing_or_does_not_exist(tmp_path):
    missing_summary_file = tmp_path / "local_parameter_sweep_summary.json"
    sweep_result = _sweep_result(tmp_path, summary_file=missing_summary_file)

    result = write_local_sweep_result_index(sweep_result, tmp_path)

    assert result.index is None
    assert result.index_file is None
    assert result.written_files == {}
    assert result.failure_reasons == ("sweep_result.summary_file must exist",)
    assert not (tmp_path / RESULT_INDEX_FILE_NAME).exists()


def test_failure_when_protected_boundary_preserved_is_false(tmp_path):
    result = write_local_sweep_result_index(
        _sweep_result(tmp_path, protected_boundary_preserved=False),
        tmp_path,
    )

    assert result.written_files == {}
    assert result.failure_reasons == ("sweep_result.protected_boundary_preserved must be True",)
    assert not (tmp_path / RESULT_INDEX_FILE_NAME).exists()


def test_failure_when_required_boundary_flags_are_wrong(tmp_path):
    cases = (
        ("local_only", False, "sweep_result.local_only must be True"),
        ("research_only", False, "sweep_result.research_only must be True"),
        ("non_authoritative", False, "sweep_result.non_authoritative must be True"),
        ("creates_committed_evidence", True, "sweep_result.creates_committed_evidence must be False"),
    )
    for field_name, value, expected_reason in cases:
        output_root = tmp_path / field_name
        output_root.mkdir()
        result = write_local_sweep_result_index(
            _sweep_result(output_root, **{field_name: value}),
            output_root,
        )

        assert result.index is None
        assert result.index_file is None
        assert result.written_files == {}
        assert result.failure_reasons == (expected_reason,)
        assert not (output_root / RESULT_INDEX_FILE_NAME).exists()


def test_source_fields_remain_structural_strings_and_do_not_trigger_other_writes(tmp_path):
    spec_source = tmp_path / "caller_spec.json"
    loader_source = "local_json_sweep_spec_loader"

    result = write_local_sweep_result_index(
        _sweep_result(tmp_path),
        tmp_path,
        spec_source=str(spec_source),
        loader_source=loader_source,
    )

    payload = _load(result.index_file)
    assert payload["spec_source"] == str(spec_source)
    assert payload["loader_source"] == loader_source
    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "local_parameter_sweep_summary.json",
        "local_sweep_result_index.json",
    ]
    assert not spec_source.exists()


def test_no_fabricated_per_point_registry_ids(tmp_path):
    summary = _summary(
        point_count=3,
        point_results=(
            _point("LPSP-0001", 1),
            _point("LPSP-0002", 2),
            _point("LPSP-0003", 3),
        ),
        registry_record_ids=("LRR-ACTUAL-ONLY",),
    )
    result = write_local_sweep_result_index(_sweep_result(tmp_path, summary=summary), tmp_path)

    payload = _load(result.index_file)
    assert payload["registry_record_ids"] == ["LRR-ACTUAL-ONLY"]
    assert all("registry_record_id" not in point_ref for point_ref in payload["point_refs"])
    assert all("registry_record_ids" not in point_ref for point_ref in payload["point_refs"])


def test_no_authority_fields_in_written_json(tmp_path):
    result = write_local_sweep_result_index(_sweep_result(tmp_path), tmp_path)

    payload = _load(result.index_file)

    assert FORBIDDEN_AUTHORITY_FIELDS.isdisjoint(_collect_keys(payload))


def test_result_dataclasses_expose_boundary_flags_and_no_authority_fields():
    for dataclass_type in (
        LocalSweepPointIndexRef,
        LocalSweepResultIndex,
        LocalSweepResultIndexWriteResult,
    ):
        field_names = {field.name for field in fields(dataclass_type)}
        assert FORBIDDEN_AUTHORITY_FIELDS.isdisjoint(field_names)

    result_fields = {field.name for field in fields(LocalSweepResultIndexWriteResult)}
    assert {
        "local_only",
        "research_only",
        "non_authoritative",
        "creates_committed_evidence",
        "protected_boundary_preserved",
    }.issubset(result_fields)


def test_writer_does_not_expose_or_import_sweep_execution_helpers():
    public_names = {name for name in dir(local_sweep_result_index) if not name.startswith("_")}
    assert "run_local_parameter_sweep" not in public_names
    assert "run_local_json_parameter_sweep" not in public_names
    assert "build_local_run_registry" not in public_names

    source = inspect.getsource(local_sweep_result_index)
    assert "from tools.research_automation.local_parameter_sweep import" not in source
    assert "from tools.research_automation.local_json_sweep_spec_loader import" not in source
    assert "from tools.research_automation.local_run_registry import" not in source
