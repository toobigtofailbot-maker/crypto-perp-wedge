"""Bounded Prefect P1/P2/P3 acceptance flows with no production authority."""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from prefect import flow, task
from prefect.flow_runs import pause_flow_run
from prefect.input import RunInput
from prefect.runtime import flow_run, task_run

from tools.research_domain.contracts import TRIAL_STATUSES
from tools.research_domain.preregistration import validate_prereg_approval
from tools.research_domain.scientific_accounting import validate_trial_denominator


class ApprovalTransport(RunInput):
    """Transport an arbitrary mapping; CPW validates all semantic meaning."""

    payload: dict[str, Any]


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _wait_until(predicate: Any, *, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while not predicate():
        if time.monotonic() >= deadline:
            raise TimeoutError("proof coordination timed out")
        time.sleep(0.01)


@task(cache_policy=None, persist_result=False)
def _p1_trial(
    trial: Mapping[str, Any], coordination_dir: str, completion_rank: int, total: int
) -> dict[str, Any]:
    root = Path(coordination_dir)
    trial_id = str(trial["trial_id"])
    (root / f"started-{trial_id}").write_text(str(task_run.id), encoding="utf-8")
    _wait_until(lambda: len(list(root.glob("started-*"))) == total)
    if completion_rank:
        _wait_until(lambda: (root / f"completed-{completion_rank - 1}").exists())
    (root / f"completed-{completion_rank}").write_text(trial_id, encoding="utf-8")
    return {
        "trial_id": trial_id,
        "trial_status": TRIAL_STATUSES[0],
        "params": dict(trial["params"]),
        "noncanonical": True,
        "task_run_id": str(task_run.id),
    }


@flow(name="cpw-prefect-p1-acceptance", persist_result=False)
def p1_deterministic_sweep(
    declared_trials: Sequence[Mapping[str, Any]], coordination_dir: str
) -> dict[str, Any]:
    root = Path(coordination_dir)
    root.mkdir(parents=True, exist_ok=True)
    declared_ids = [str(row["trial_id"]) for row in declared_trials]
    operational_ids = list(reversed(declared_ids))
    ranks = {trial_id: rank for rank, trial_id in enumerate(operational_ids)}
    futures = [
        _p1_trial.submit(row, coordination_dir, ranks[str(row["trial_id"])], len(declared_ids))
        for row in declared_trials
    ]
    by_id = {row["trial_id"]: row for row in (future.result() for future in futures)}
    ledger = [by_id[trial_id] for trial_id in declared_ids]
    validate_trial_denominator(ledger, declared_ids)
    observed = [
        (root / f"completed-{rank}").read_text(encoding="utf-8")
        for rank in range(len(declared_ids))
    ]
    return {
        "flow_run_id": str(flow_run.id),
        "declared_order": declared_ids,
        "operational_completion_order": observed,
        "ledger": ledger,
        "denominator": len(ledger),
    }


@task(cache_policy=None, persist_result=False)
def _p2_continuation(effect_path: str) -> dict[str, Any]:
    path = Path(effect_path)
    payload = {"effect": "noncanonical_proof_continuation", "noncanonical": True}
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, sort_keys=True, separators=(",", ":"))
        handle.write("\n")
    return payload


@flow(name="cpw-prefect-p2-acceptance", persist_result=False)
def p2_human_gate(
    packet: Mapping[str, Any], requirement: Mapping[str, Any], coordination_path: str, effect_path: str
) -> dict[str, Any]:
    Path(coordination_path).write_text(str(flow_run.id), encoding="utf-8")
    transported = pause_flow_run(
        wait_for_input=ApprovalTransport,
        timeout=60,
        poll_interval=0.1,
        key="cpw-prefect-01-human-gate",
    )
    errors = validate_prereg_approval(transported.payload, packet, requirement=requirement)
    if errors:
        raise ValueError("CPW preregistration approval rejected: " + ", ".join(errors))
    continuation = _p2_continuation(effect_path)
    return {"flow_run_id": str(flow_run.id), "continuation": continuation}


@task(retries=1, retry_delay_seconds=0, cache_policy=None, persist_result=False)
def _p3_retry(scientific_trial_id: str, attempts_dir: str) -> dict[str, Any]:
    run_count = int(task_run.run_count)
    Path(attempts_dir, f"attempt-{run_count}").write_text(
        f"{task_run.id}\n", encoding="utf-8"
    )
    if run_count == 1:
        raise RuntimeError("deliberate first-attempt operational failure")
    return {
        "scientific_trial_id": scientific_trial_id,
        "task_run_id": str(task_run.id),
        "run_count": run_count,
    }


@flow(name="cpw-prefect-p3a-acceptance", persist_result=False)
def p3_retry_once(scientific_trial_id: str, attempts_dir: str) -> dict[str, Any]:
    Path(attempts_dir).mkdir(parents=True, exist_ok=True)
    operational = _p3_retry(scientific_trial_id, attempts_dir)
    ledger = [{"trial_id": scientific_trial_id, "trial_status": TRIAL_STATUSES[0]}]
    validate_trial_denominator(ledger, [scientific_trial_id])
    return {
        "flow_run_id": str(flow_run.id),
        "operational": operational,
        "ledger": ledger,
        "denominator": len(ledger),
    }


def _create_or_reuse_effect(effect_path: Path, effect: Mapping[str, Any]) -> dict[str, Any]:
    expected = _canonical_bytes(effect)
    try:
        descriptor = os.open(effect_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError:
        actual = effect_path.read_bytes()
        if actual != expected:
            raise ValueError("existing proof effect conflicts with frozen identity/content")
        return {"disposition": "reused", "sha256": _sha256(actual), "bytes": len(actual)}
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(expected)
        handle.flush()
        os.fsync(handle.fileno())
    return {"disposition": "created", "sha256": _sha256(expected), "bytes": len(expected)}


@flow(name="cpw-prefect-p3b-acceptance", persist_result=False)
def p3_recover_effect(
    scientific_trial_id: str,
    frozen_payload: Mapping[str, Any],
    effect_path: str,
    fail_after_effect: bool,
) -> dict[str, Any]:
    effect = {
        "scientific_trial_id": scientific_trial_id,
        "payload": dict(frozen_payload),
        "noncanonical": True,
        "authoritative": False,
    }
    result = _create_or_reuse_effect(Path(effect_path), effect)
    if fail_after_effect:
        raise RuntimeError("deliberate crash after non-authoritative proof effect")
    ledger = [{"trial_id": scientific_trial_id, "trial_status": TRIAL_STATUSES[0]}]
    validate_trial_denominator(ledger, [scientific_trial_id])
    return {
        "flow_run_id": str(flow_run.id),
        "effect": result,
        "ledger": ledger,
        "denominator": len(ledger),
    }
