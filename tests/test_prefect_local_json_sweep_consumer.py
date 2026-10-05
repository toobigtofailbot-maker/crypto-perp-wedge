from __future__ import annotations

import ast
import asyncio
import hashlib
import json
import os
import shutil
from pathlib import Path
from types import SimpleNamespace

import prefect
import pytest
from prefect.flows import Flow
from prefect.testing.utilities import prefect_test_harness

import tools.prefect_integration.local_json_sweep_consumer as consumer_module
from tools.prefect_integration.local_json_sweep_consumer import (
    DEPLOYMENT_NAME,
    FLOW_NAME,
    RUN_NAMESPACE,
    WORK_POOL_NAME,
    LocalJsonSweepConsumerError,
    local_json_sweep_consumer,
    register_local_json_sweep_deployment,
)
from tools.research_automation.local_json_sweep_spec_loader import (
    run_local_json_parameter_sweep,
)
from tools.research_automation.local_parameter_sweep import DEFAULT_MAX_POINT_COUNT


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "tools/prefect_integration/local_json_sweep_consumer.py"


@pytest.fixture(scope="module", autouse=True)
def local_prefect_backend():
    with prefect_test_harness(server_startup_timeout=60):
        yield


def _payload() -> dict:
    return {
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
            "sweep_id": "SWEEP-CPW-PREFECT-02-PARITY-0001",
            "candidate_id": "H-004",
            "evaluation_purpose": "CPW-PREFECT-02 direct-vs-Prefect parity proof",
            "data_refs": ["local_fixture:cpw-prefect-02:parity"],
            "timeframe": "1d",
            "evaluation_window": {
                "start": "2026-04-01T00:00:00Z",
                "end": "2026-04-02T00:00:00Z",
            },
            "base_parameters": {"mode": "prefect_parity"},
            "sweep_parameters": {"alpha": [1, 2], "zeta": ["low", "high"]},
            "pipeline_version": "cpw_prefect_02_parity_v1",
            "static_metadata": {"source_package": "CPW-PREFECT-02"},
        },
    }


def _write_spec(repo_root: Path, *, valid: bool = True) -> Path:
    path = repo_root / ".cpw/active/specs/input/sweep.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(_payload(), indent=2, sort_keys=True) if valid else "{not-json"
    path.write_text(text + "\n", encoding="utf-8")
    return path


def _run_root(repo_root: Path, run_id: str) -> Path:
    return repo_root / ".cpw/active" / RUN_NAMESPACE / run_id


def _fake_success(sweep_output: Path, registry_output: Path) -> SimpleNamespace:
    manifest = sweep_output / "batch_manifest.json"
    manifest_validation = sweep_output / "batch_validation_report.json"
    batch_summary = sweep_output / "local_batch_run_summary.json"
    batch_validation = sweep_output / "local_batch_run_summary_validation.json"
    sweep_summary = sweep_output / "local_parameter_sweep_summary.json"
    dry_run = sweep_output / "sweep-point-0001/run_request.json"
    registry = registry_output / "local_run_registry.json"
    for path in (
        manifest,
        manifest_validation,
        batch_summary,
        batch_validation,
        sweep_summary,
        dry_run,
        registry,
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8")
    item = SimpleNamespace(
        dry_run_written_files={"run_request": "sweep-point-0001/run_request.json"}
    )
    batch = SimpleNamespace(
        manifest_result=SimpleNamespace(
            written_files={
                "batch_manifest": manifest,
                "batch_validation_report": manifest_validation,
            }
        ),
        written_files={
            "local_batch_run_summary": batch_summary.name,
            "local_batch_run_summary_validation": batch_validation.name,
        },
        summary=SimpleNamespace(item_results=(item,)),
    )
    registry_result = SimpleNamespace(
        registry_file=registry,
        written_files={"local_run_registry": registry},
    )
    summary = SimpleNamespace(
        sweep_id="SWEEP-FAKE",
        point_count=1,
        success_point_count=1,
        failed_point_count=0,
        blocked_point_count=0,
        skipped_point_count=0,
    )
    sweep_result = SimpleNamespace(
        summary=summary,
        summary_file=sweep_summary,
        batch_result=batch,
        registry_result=registry_result,
    )
    return SimpleNamespace(
        sweep_result=sweep_result,
        failure_reasons=(),
        protected_boundary_preserved=True,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
    )


def _tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_static_contract_and_dependency_posture() -> None:
    assert prefect.__version__ == "3.8.6"
    assert FLOW_NAME == "cpw-local-json-sweep"
    assert DEPLOYMENT_NAME == "cpw-local-json-sweep-v1"
    assert WORK_POOL_NAME == "cpw-research-local-process"
    assert local_json_sweep_consumer.name == FLOW_NAME
    assert local_json_sweep_consumer.retries == 0
    assert local_json_sweep_consumer.persist_result is False

    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "task" not in calls
    assert "PREFECT_API_KEY" not in source
    assert "subprocess" not in source
    assert "cron=" not in source
    assert "interval=" not in source
    assert "rrule=" not in source


def test_registration_binds_explicit_source_names_version_and_no_schedule(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module_root = tmp_path.resolve()
    monkeypatch.setattr(consumer_module, "_repo_root", lambda: module_root)
    captured: dict[str, object] = {}

    class SourcedFlow:
        def deploy(self, **kwargs):
            captured["deploy"] = kwargs
            return "deployment-id"

    def fake_from_source(*, source, entrypoint):
        captured["source"] = source
        captured["entrypoint"] = entrypoint
        return SourcedFlow()

    monkeypatch.setattr(Flow, "from_source", staticmethod(fake_from_source))
    version = "a" * 40
    result = register_local_json_sweep_deployment(repo_root=module_root, version=version)

    assert result == "deployment-id"
    assert captured["source"].destination == module_root
    assert captured["entrypoint"].endswith(":local_json_sweep_consumer")
    deploy = captured["deploy"]
    assert deploy["name"] == DEPLOYMENT_NAME
    assert deploy["work_pool_name"] == WORK_POOL_NAME
    assert deploy["version"] == version
    assert deploy["schedules"] == []
    assert deploy["triggers"] == []
    assert deploy["build"] is False
    assert deploy["push"] is False


@pytest.mark.parametrize(
    "namespace,artifact,run_id",
    [
        ("/absolute", "sweep.json", "run-1"),
        (r"C:\qualified", "sweep.json", "run-1"),
        ("../escape", "sweep.json", "run-1"),
        ("specs", "../../escape.json", "run-1"),
        ("specs", "input/sweep.json", "nested/run"),
        ("specs", "input/sweep.json", r"nested\run"),
        ("specs", "input/sweep.json", "C:drive"),
        ("specs", "input/sweep.json", ".."),
        ("specs", "input/sweep.json", "unsafe."),
    ],
)
def test_unsafe_paths_fail_before_consumer_invocation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    namespace: str,
    artifact: str,
    run_id: str,
) -> None:
    _write_spec(tmp_path)
    calls: list[object] = []
    monkeypatch.setattr(consumer_module, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(
        consumer_module,
        "run_local_json_parameter_sweep",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    with pytest.raises((ValueError, LocalJsonSweepConsumerError)):
        local_json_sweep_consumer.fn(namespace, artifact, run_id)
    assert calls == []
    assert not (tmp_path / "research").exists()
    assert not (tmp_path / "src").exists()


def test_symlink_escape_is_rejected_where_supported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    class_root = tmp_path / ".cpw/active"
    class_root.mkdir(parents=True)
    try:
        os.symlink(outside, class_root / "escape", target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")
    monkeypatch.setattr(consumer_module, "_repo_root", lambda: tmp_path)
    with pytest.raises(ValueError, match="escapes"):
        local_json_sweep_consumer.fn("escape", "sweep.json", "run-1")


def test_exact_delegation_and_success_mapping(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = _write_spec(tmp_path)
    calls: list[tuple[object, ...]] = []
    monkeypatch.setattr(consumer_module, "_repo_root", lambda: tmp_path)

    def fake_consumer(spec_path, output_root, registry_root, *, max_point_count):
        calls.append((spec_path, output_root, registry_root, max_point_count))
        return _fake_success(output_root, registry_root)

    monkeypatch.setattr(consumer_module, "run_local_json_parameter_sweep", fake_consumer)
    result = local_json_sweep_consumer.fn("specs", "input/sweep.json", "run-1", 4)

    run_root = _run_root(tmp_path, "run-1")
    assert calls == [(spec.resolve(), run_root / "sweep-output", run_root / "registry-output", 4)]
    assert result == {
        "consumer_run_id": "run-1",
        "sweep_id": "SWEEP-FAKE",
        "point_count": 1,
        "success_point_count": 1,
        "failed_point_count": 0,
        "blocked_point_count": 0,
        "skipped_point_count": 0,
        "sweep_summary_path": (
            ".cpw/active/prefect/local-json-sweep/run-1/"
            "sweep-output/local_parameter_sweep_summary.json"
        ),
        "registry_path": (
            ".cpw/active/prefect/local-json-sweep/run-1/"
            "registry-output/local_run_registry.json"
        ),
        "local_only": True,
        "research_only": True,
        "non_authoritative": True,
        "creates_committed_evidence": False,
    }
    assert not (run_root / "prefect_result.json").exists()


def test_existing_nonempty_or_file_run_namespace_fails_without_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_spec(tmp_path)
    monkeypatch.setattr(consumer_module, "_repo_root", lambda: tmp_path)
    calls: list[object] = []
    monkeypatch.setattr(
        consumer_module,
        "run_local_json_parameter_sweep",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    nonempty = _run_root(tmp_path, "nonempty")
    nonempty.mkdir(parents=True)
    prior = nonempty / "prior.txt"
    prior.write_bytes(b"unchanged")
    with pytest.raises(LocalJsonSweepConsumerError, match="not empty"):
        local_json_sweep_consumer.fn("specs", "input/sweep.json", "nonempty")
    assert prior.read_bytes() == b"unchanged"

    file_root = _run_root(tmp_path, "file-root")
    file_root.parent.mkdir(parents=True, exist_ok=True)
    file_root.write_bytes(b"unchanged-file")
    with pytest.raises(LocalJsonSweepConsumerError, match="not a directory"):
        local_json_sweep_consumer.fn("specs", "input/sweep.json", "file-root")
    assert file_root.read_bytes() == b"unchanged-file"
    assert calls == []


def test_existing_empty_namespace_is_allowed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_spec(tmp_path)
    empty = _run_root(tmp_path, "empty")
    empty.mkdir(parents=True)
    monkeypatch.setattr(consumer_module, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(
        consumer_module,
        "run_local_json_parameter_sweep",
        lambda _spec, output, registry, **_kwargs: _fake_success(output, registry),
    )
    assert local_json_sweep_consumer.fn("specs", "input/sweep.json", "empty")[
        "consumer_run_id"
    ] == "empty"


@pytest.mark.parametrize(
    "mutate,match",
    [
        (
            lambda result: setattr(result, "failure_reasons", ("downstream failed",)),
            "downstream failed",
        ),
        (
            lambda result: setattr(result, "protected_boundary_preserved", False),
            "protected boundary",
        ),
        (lambda result: setattr(result, "sweep_result", None), "no sweep_result"),
        (lambda result: setattr(result.sweep_result, "summary", None), "no final sweep summary"),
    ],
)
def test_incomplete_or_failed_downstream_result_fails_flow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutate, match: str
) -> None:
    _write_spec(tmp_path)
    monkeypatch.setattr(consumer_module, "_repo_root", lambda: tmp_path)

    def fake_consumer(_spec, output, registry, **_kwargs):
        result = _fake_success(output, registry)
        mutate(result)
        return result

    monkeypatch.setattr(consumer_module, "run_local_json_parameter_sweep", fake_consumer)
    state = local_json_sweep_consumer(
        "specs", "input/sweep.json", f"failed-{match.replace(' ', '-')}", return_state=True
    )
    assert state.is_failed()
    assert match in state.message


def test_invalid_json_and_underlying_exception_are_failed_states(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_spec(tmp_path, valid=False)
    monkeypatch.setattr(consumer_module, "_repo_root", lambda: tmp_path)
    invalid = local_json_sweep_consumer(
        "specs", "input/sweep.json", "invalid-json", return_state=True
    )
    assert invalid.is_failed()
    invalid_summary = (
        _run_root(tmp_path, "invalid-json")
        / "sweep-output/local_parameter_sweep_summary.json"
    )
    assert not invalid_summary.exists()

    _write_spec(tmp_path, valid=True)
    monkeypatch.setattr(
        consumer_module,
        "run_local_json_parameter_sweep",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("underlying boom")),
    )
    raised = local_json_sweep_consumer(
        "specs", "input/sweep.json", "underlying-raise", return_state=True
    )
    assert raised.is_failed()
    assert "underlying boom" in raised.message


def test_interruption_creates_no_success_and_namespace_cannot_be_reused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_spec(tmp_path)
    monkeypatch.setattr(consumer_module, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(
        consumer_module,
        "run_local_json_parameter_sweep",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(asyncio.CancelledError()),
    )
    with pytest.raises(asyncio.CancelledError):
        local_json_sweep_consumer.fn("specs", "input/sweep.json", "interrupted")
    root = _run_root(tmp_path, "interrupted")
    assert not (root / "sweep-output/local_parameter_sweep_summary.json").exists()
    assert not (tmp_path / "research").exists()
    with pytest.raises(LocalJsonSweepConsumerError, match="not empty"):
        local_json_sweep_consumer.fn("specs", "input/sweep.json", "interrupted")


def test_real_four_point_sweep_preserves_identity_and_direct_prefect_artifact_parity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = _write_spec(tmp_path)
    monkeypatch.setattr(consumer_module, "_repo_root", lambda: tmp_path)
    run_root = _run_root(tmp_path, "parity")
    direct_sweep = run_root / "sweep-output"
    direct_registry = run_root / "registry-output"
    direct_sweep.mkdir(parents=True)
    direct_registry.mkdir()
    direct = run_local_json_parameter_sweep(
        spec, direct_sweep, direct_registry, max_point_count=4
    )
    assert direct.failure_reasons == ()
    direct_hashes = _tree_hashes(run_root)
    direct_ids = (
        direct.sweep_result.summary.sweep_id,
        tuple(point.point_id for point in direct.sweep_result.points),
        direct.sweep_result.summary.batch_id,
        direct.sweep_result.summary.registry_record_ids,
    )

    shutil.rmtree(run_root)
    result = local_json_sweep_consumer(
        "specs", "input/sweep.json", "parity", 4
    )
    prefect_hashes = _tree_hashes(run_root)
    summary_payload = json.loads(
        (run_root / "sweep-output/local_parameter_sweep_summary.json").read_text(encoding="utf-8")
    )
    prefect_ids = (
        summary_payload["sweep_id"],
        tuple(item["point_id"] for item in summary_payload["point_results"]),
        summary_payload["batch_id"],
        tuple(summary_payload["registry_record_ids"]),
    )

    assert result["point_count"] == 4
    assert result["success_point_count"] == 4
    assert direct_hashes == prefect_hashes
    assert direct_ids == prefect_ids
    assert not any("prefect" in key.casefold() for key in summary_payload if key.endswith("_id"))
    assert sorted(direct_hashes) == sorted(prefect_hashes)
