from __future__ import annotations

import ast
import contextvars
import copy
import json
import time
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable
from uuid import UUID

import prefect
import pytest
from prefect.client.orchestration import get_client
from prefect.flow_runs import resume_flow_run
from prefect.testing.utilities import prefect_test_harness

from tools.prefect_integration.acceptance import (
    p1_deterministic_sweep,
    p2_human_gate,
    p3_recover_effect,
    p3_retry_once,
)
from tools.research_domain.preregistration import (
    build_approval_requirement,
    build_approval_template,
    build_preregistration_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE_PATH = REPO_ROOT / "tools/prefect_integration/acceptance.py"


@pytest.fixture(scope="module", autouse=True)
def local_prefect_backend():
    with prefect_test_harness(server_startup_timeout=60):
        yield


def _declared_trials() -> list[dict[str, Any]]:
    return [
        {"strategy_family": "synthetic", "variant_id": f"V{i}", "trial_id": f"T{i}", "params": {"n": i}}
        for i in range(1, 4)
    ]


def _packet_and_approval() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    request = {"request_id": "REQ-PREFECT-01", "source_idea": "synthetic engineering fixture"}
    packet = build_preregistration_packet(
        pipeline_run_id="LPIPE-PREFECT-01",
        request=request,
        formalized={"request_id": request["request_id"], "synthetic": True},
        availability={"status": "ready", "blocking_reasons": []},
    )
    requirement = build_approval_requirement(packet)
    approval = build_approval_template(packet, approval_timestamp_utc="2026-09-26T00:00:00Z")
    return packet, requirement, approval


def _wait_for(predicate: Callable[[], Any], timeout: float = 20.0) -> Any:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(0.05)
    raise TimeoutError("test condition was not observed")


def _state_type(flow_run_id: UUID) -> str:
    with get_client(sync_client=True) as client:
        run = client.read_flow_run(flow_run_id)
    return run.state.type.value


def _start_gate_flow(
    executor: ThreadPoolExecutor,
    packet: dict[str, Any],
    requirement: dict[str, Any],
    coordination: Path,
    effect: Path,
) -> Future[Any]:
    context = contextvars.copy_context()
    return executor.submit(
        context.run,
        lambda: p2_human_gate(
            packet,
            requirement,
            str(coordination),
            str(effect),
            return_state=True,
        ),
    )


def _run_gate_case(
    root: Path, packet: dict[str, Any], requirement: dict[str, Any], approval: dict[str, Any]
) -> tuple[Any, UUID, Path]:
    coordination = root / "flow-run-id.txt"
    effect = root / "continuation.json"
    root.mkdir()
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = _start_gate_flow(executor, packet, requirement, coordination, effect)
        flow_run_id = UUID(_wait_for(lambda: coordination.read_text() if coordination.exists() else None))
        assert _wait_for(lambda: _state_type(flow_run_id) == "PAUSED")
        assert not effect.exists()
        resume_flow_run(flow_run_id, run_input={"payload": approval})
        state = future.result(timeout=20)
    return state, flow_run_id, effect


def test_dependency_and_harness_are_exact_and_local() -> None:
    assert prefect.__version__ == "3.8.6"
    assert prefect.settings.PREFECT_API_URL.value().startswith("http://127.0.0.1:")
    assert not prefect.settings.PREFECT_API_KEY.value()


def test_p1_concurrency_preserves_frozen_order_denominator_and_repeatability(tmp_path: Path) -> None:
    declared = _declared_trials()
    first = p1_deterministic_sweep(declared, str(tmp_path / "first"))
    second = p1_deterministic_sweep(declared, str(tmp_path / "second"))
    expected = ["T1", "T2", "T3"]
    assert first["declared_order"] == expected
    assert first["operational_completion_order"] == list(reversed(expected))
    assert [row["trial_id"] for row in first["ledger"]] == expected
    assert first["denominator"] == 3
    assert len({row["task_run_id"] for row in first["ledger"]}) == 3
    assert first["flow_run_id"] != second["flow_run_id"]
    normalize = lambda result: [
        {key: value for key, value in row.items() if key != "task_run_id"}
        for row in result["ledger"]
    ]
    assert normalize(first) == normalize(second)
    assert second["operational_completion_order"] == list(reversed(expected))


def test_p2_real_pause_valid_resume_and_duplicate_protection(tmp_path: Path) -> None:
    packet, requirement, approval = _packet_and_approval()
    state, flow_run_id, effect = _run_gate_case(
        tmp_path / "valid", packet, requirement, approval
    )
    assert state.is_completed()
    assert json.loads(effect.read_text(encoding="utf-8"))["noncanonical"] is True
    before = effect.read_bytes()
    with pytest.raises(Exception):
        resume_flow_run(flow_run_id, run_input={"payload": approval})
    assert effect.read_bytes() == before


@pytest.mark.parametrize(
    "case,mutate",
    [
        ("wrong-actor", lambda value: value.update(approved_by="operator")),
        ("wrong-hash", lambda value: value.update(preregistration_packet_sha256="sha256:wrong")),
        ("wrong-scope", lambda value: value.update(approval_scope="other")),
        ("wrong-statement", lambda value: value.update(approval_statement="other")),
        ("missing-timestamp", lambda value: value.pop("approval_timestamp_utc")),
        ("broad-authority", lambda value: value.update(authorizes_canonical_write=True)),
    ],
)
def test_p2_invalid_semantic_input_pauses_then_creates_no_effect(
    tmp_path: Path, case: str, mutate: Callable[[dict[str, Any]], Any]
) -> None:
    packet, requirement, valid = _packet_and_approval()
    invalid = copy.deepcopy(valid)
    mutate(invalid)
    state, _flow_run_id, effect = _run_gate_case(
        tmp_path / case, packet, requirement, invalid
    )
    assert state.is_failed()
    assert not effect.exists()


def test_p3a_prefect_retry_is_one_scientific_observation(tmp_path: Path) -> None:
    result = p3_retry_once("TRIAL-RETRY-1", str(tmp_path / "attempts"))
    operational = result["operational"]
    assert operational["run_count"] == 2
    assert operational["scientific_trial_id"] == "TRIAL-RETRY-1"
    assert sorted(path.name for path in (tmp_path / "attempts").iterdir()) == [
        "attempt-1",
        "attempt-2",
    ]
    assert (tmp_path / "attempts/attempt-1").read_text() == (
        tmp_path / "attempts/attempt-2"
    ).read_text()
    with get_client(sync_client=True) as client:
        task_record = client.read_task_run(UUID(operational["task_run_id"]))
    assert task_record.run_count == 2
    assert task_record.state.is_completed()
    assert result["ledger"] == [{"trial_id": "TRIAL-RETRY-1", "trial_status": "completed"}]
    assert result["denominator"] == 1


def test_p3b_fresh_flow_recovery_reuses_exact_effect_and_conflict_fails(tmp_path: Path) -> None:
    effect = tmp_path / "proof-effect.json"
    first = p3_recover_effect(
        "TRIAL-RECOVERY-1", {"fixture": 7}, str(effect), True, return_state=True
    )
    assert first.is_failed()
    original = effect.read_bytes()
    original_stat = effect.stat()

    second = p3_recover_effect("TRIAL-RECOVERY-1", {"fixture": 7}, str(effect), False)
    assert second["effect"]["disposition"] == "reused"
    assert second["flow_run_id"] != str(first.state_details.flow_run_id)
    assert effect.read_bytes() == original
    assert effect.stat().st_mtime_ns == original_stat.st_mtime_ns
    assert list(tmp_path.glob("*.json")) == [effect]
    assert second["denominator"] == 1

    conflict = p3_recover_effect(
        "TRIAL-RECOVERY-1", {"fixture": 8}, str(effect), False, return_state=True
    )
    assert conflict.is_failed()
    assert effect.read_bytes() == original
    assert effect.stat().st_mtime_ns == original_stat.st_mtime_ns


def test_acceptance_source_preserves_owner_and_non_adoption_boundaries() -> None:
    source = ACCEPTANCE_PATH.read_text(encoding="utf-8")
    assert "Karl" not in source
    assert "noncanonical_offline_research_execution_only" not in source
    assert "Authorizes only non-canonical offline research" not in source
    assert "TRIAL_STATUSES =" not in source
    tree = ast.parse(source)
    imports: list[str] = []
    calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    forbidden_imports = (
        "tools.research_search",
        "tools.research_automation",
        "tools.lab_scheduler_shell",
        "tools.lab_pipeline",
        "tools.canon_intake",
        "tools.hermes",
        "lib.backtest",
        "src.",
    )
    assert not [name for name in imports if name.startswith(forbidden_imports)]
    forbidden_calls = {
        "serve",
        "deploy",
        "Deployment",
        "WorkPool",
        "Worker",
        "create_deployment",
        "create_work_pool",
        "create_work_queue",
    }
    assert forbidden_calls.isdisjoint(calls)
    assert "PREFECT_API_KEY" not in source
