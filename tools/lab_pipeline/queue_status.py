"""Read-only operator queue/status projection for product lab pipeline runs.

The surface joins existing product pipeline artifacts:

- ``pipeline_state.json`` from the lab pipeline spine;
- ``runner_adapter_result.json`` from the product runner adapter when present;
- ``advisory_review_packet.json`` from the product gates adapter when present.

It never starts a run, records an approval, fires a notification, activates a
scheduler, or writes canonical/candidate/runtime state. Optional notification
fields are dry-run preview metadata only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final, Mapping

from tools.lab_state.resolver import REPO_ROOT


SCHEMA_VERSION: Final = "lab_product_queue_status_v1"
PIPELINE_RUNS_ROOT: Final = "scratch/WP-LABPROD-COCKPIT-PIPELINE-STATE-02/pipeline_runs"
RUNNER_RESULTS_ROOT: Final = "scratch/WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04/outputs"
GATES_RESULTS_ROOT: Final = "scratch/WP-LABPROD-PIPELINE-GATES-ADAPTERS-05/outputs"
EXECUTE_APPROVAL_SCOPE: Final = "noncanonical_product_runner_execution_only"
EXECUTE_APPROVAL_STATEMENT: Final = (
    "Authorizes only non-canonical product runner execution for the exact "
    "bridge-prepared Strategy Spec, Variant Manifest, and Sweep Plan artifacts."
)
STATUS_STATES: Final[tuple[str, ...]] = (
    "queued",
    "running",
    "awaiting_prereg_approval",
    "awaiting_execute_approval",
    "blocked",
    "complete",
    "failed",
    "advisory_packet_ready",
)

NON_AUTHORITY_DECLARATION: Final[dict[str, bool]] = {
    "status_visibility_only": True,
    "read_only": True,
    "notification_firing": False,
    "autonomous_dispatch": False,
    "scheduler_activation": False,
    "job_execution_controls": False,
    "canonical_evidence_written": False,
    "candidate_lifecycle_written": False,
    "crossing": False,
    "promotion_or_readiness": False,
    "paper_live_runtime_contact": False,
    "provider_api_credential_use": False,
    "dependency_config_data_acquisition": False,
    "protected_path_touch": False,
    "has_approve_button": False,
    "has_execute_button": False,
    "has_retry_button": False,
    "has_scheduler_toggle": False,
}


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _root_path(repo_root: Path, root: Path | str) -> Path:
    candidate = Path(root)
    if candidate.is_absolute():
        return candidate
    return repo_root / candidate


def _index_runner_results(root: Path, repo_root: Path) -> dict[str, dict[str, Any]]:
    if not root.is_dir():
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("runner_adapter_result.json")):
        payload = _read_json(path)
        if not payload:
            continue
        bindings = payload.get("source_bindings")
        if not isinstance(bindings, Mapping):
            continue
        pipeline_run_id = bindings.get("product_pipeline_run_id")
        if not isinstance(pipeline_run_id, str) or not pipeline_run_id:
            continue
        indexed[pipeline_run_id] = {
            "path": _repo_relative(path, repo_root),
            "runner_adapter_run_id": payload.get("runner_adapter_run_id"),
            "adapter_status": payload.get("adapter_status"),
            "denominator_counts": payload.get("denominator_counts") or {},
            "execute_approval_path": bindings.get("execute_approval_path"),
            "execute_approval_sha256": bindings.get("execute_approval_sha256"),
            "non_authority_assertions": payload.get("non_authority_assertions") or {},
        }
    return indexed


def _index_advisory_packets(root: Path, repo_root: Path) -> dict[str, dict[str, Any]]:
    if not root.is_dir():
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("advisory_review_packet.json")):
        payload = _read_json(path)
        if not payload:
            continue
        runner_ref = payload.get("runner_result_reference")
        if not isinstance(runner_ref, Mapping):
            continue
        pipeline_run_id = runner_ref.get("product_pipeline_run_id")
        if not isinstance(pipeline_run_id, str) or not pipeline_run_id:
            continue
        indexed[pipeline_run_id] = {
            "path": _repo_relative(path, repo_root),
            "gates_adapter_run_id": payload.get("gates_adapter_run_id"),
            "adapter_status": payload.get("adapter_status"),
            "candidate_surface_status": (
                payload.get("candidate_surface_routing") or {}
            ).get("surface_status"),
            "denominator_counts": payload.get("denominator_counts") or {},
            "withheld_statistics": payload.get("withheld_statistics") or {},
            "non_authority_assertions": payload.get("non_authority_assertions") or {},
        }
    return indexed


def _stage_statuses(state: Mapping[str, Any]) -> dict[str, str]:
    stages = {}
    for item in state.get("stage_statuses") or []:
        if isinstance(item, Mapping):
            stage = item.get("stage")
            status = item.get("status")
            if isinstance(stage, str) and isinstance(status, str):
                stages[stage] = status
    return stages


def _notification_preview(status: str, approval_needed: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "dry_run_only": True,
        "would_notify_operator": status
        in {"awaiting_prereg_approval", "awaiting_execute_approval", "blocked", "failed", "advisory_packet_ready"},
        "channels": [],
        "notification_fired": False,
        "dispatch_enqueued": False,
        "preview_reason": (
            approval_needed["kind"]
            if approval_needed
            else "status_visibility_preview_no_delivery"
        ),
    }


def _status_for(
    state: Mapping[str, Any],
    runner_result: Mapping[str, Any] | None,
    advisory_packet: Mapping[str, Any] | None,
) -> tuple[str, dict[str, Any] | None, list[str]]:
    raw_status = state.get("pipeline_status")
    current_stage = state.get("current_stage")
    blocked_reasons = [str(item) for item in state.get("blocked_reasons") or []]
    stages = _stage_statuses(state)

    if raw_status == "blocked" or blocked_reasons:
        if raw_status == "awaiting_prereg_approval":
            approval = state.get("approval_requirements") or {}
            return (
                "awaiting_prereg_approval",
                {
                    "kind": "prereg_approval",
                    "needed": True,
                    "approval_scope": (approval.get("required_fields") or {}).get("approval_scope"),
                    "packet_sha256": approval.get("preregistration_packet_sha256"),
                },
                blocked_reasons,
            )
        return "blocked", None, blocked_reasons

    if raw_status == "awaiting_prereg_approval" or current_stage == "awaiting_prereg_approval":
        approval = state.get("approval_requirements") or {}
        return (
            "awaiting_prereg_approval",
            {
                "kind": "prereg_approval",
                "needed": True,
                "approval_scope": (approval.get("required_fields") or {}).get("approval_scope"),
                "packet_sha256": approval.get("preregistration_packet_sha256"),
            },
            [],
        )

    if advisory_packet:
        if advisory_packet.get("adapter_status") == "completed":
            return "advisory_packet_ready", None, []
        if advisory_packet.get("adapter_status") in {"failed", "adapter_failed"}:
            return "failed", None, []

    if runner_result:
        if runner_result.get("adapter_status") in {"failed", "adapter_failed"}:
            return "failed", None, []
        if runner_result.get("adapter_status") == "completed":
            return "complete", None, []
        return "running", None, []

    if current_stage == "noncanonical_execution_running" or stages.get("noncanonical_execution_running") == "running":
        return "running", None, []

    if raw_status == "complete":
        return (
            "awaiting_execute_approval",
            {
                "kind": "execute_approval",
                "needed": True,
                "approval_scope": EXECUTE_APPROVAL_SCOPE,
                "approval_statement": EXECUTE_APPROVAL_STATEMENT,
            },
            [],
        )

    if raw_status in {"queued", "not_started"} or current_stage in {"queued", "request_loaded"}:
        return "queued", None, []

    return "running", None, []


def _pipeline_entry(
    run_dir: Path,
    runs_root: str,
    repo_root: Path,
    runner_results: Mapping[str, dict[str, Any]],
    advisory_packets: Mapping[str, dict[str, Any]],
) -> dict[str, Any]:
    state_path = run_dir / "pipeline_state.json"
    state = _read_json(state_path)
    if not state:
        return {
            "pipeline_run_id": run_dir.name,
            "status": "blocked",
            "status_detail": "pipeline_state_json_missing_or_malformed",
            "approval_needed": None,
            "blocked_reasons": ["pipeline_state_json_missing_or_malformed"],
            "artifact_refs": [{"role": "pipeline_state", "path": f"{runs_root}/{run_dir.name}/pipeline_state.json", "present": state_path.exists()}],
            "notification_preview": _notification_preview("blocked", None),
        }

    pipeline_run_id = str(state.get("pipeline_run_id") or run_dir.name)
    runner_result = runner_results.get(pipeline_run_id)
    advisory_packet = advisory_packets.get(pipeline_run_id)
    status, approval_needed, blocked_reasons = _status_for(state, runner_result, advisory_packet)
    artifacts = [
        {
            "role": "pipeline_state",
            "path": _repo_relative(state_path, repo_root),
            "present": True,
        }
    ]
    if runner_result:
        artifacts.append({"role": "runner_adapter_result", "path": runner_result["path"], "present": True})
    if advisory_packet:
        artifacts.append({"role": "advisory_review_packet", "path": advisory_packet["path"], "present": True})

    return {
        "pipeline_run_id": pipeline_run_id,
        "request_id": state.get("request_id"),
        "source_idea": state.get("source_idea"),
        "symbol": state.get("symbol"),
        "timeframe": state.get("timeframe"),
        "requested_by": state.get("requested_by"),
        "status": status,
        "status_detail": {
            "raw_pipeline_status": state.get("pipeline_status"),
            "current_stage": state.get("current_stage"),
            "runner_adapter_status": (runner_result or {}).get("adapter_status"),
            "advisory_packet_status": (advisory_packet or {}).get("adapter_status"),
        },
        "approval_needed": approval_needed,
        "blocked_reasons": blocked_reasons,
        "runner": runner_result,
        "advisory_packet": advisory_packet,
        "artifact_refs": artifacts,
        "notification_preview": _notification_preview(status, approval_needed),
    }


def _summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {status: 0 for status in STATUS_STATES}
    for entry in entries:
        counts[entry["status"]] = counts.get(entry["status"], 0) + 1
    return {
        "run_count": len(entries),
        "by_status": counts,
        "approval_needed_count": sum(1 for entry in entries if entry["approval_needed"]),
        "blocked_count": counts["blocked"],
        "failed_count": counts["failed"],
        "advisory_packet_ready_count": counts["advisory_packet_ready"],
    }


def build_queue_status(
    *,
    repo_root: Path = REPO_ROOT,
    pipeline_runs_root: Path | str = PIPELINE_RUNS_ROOT,
    runner_results_root: Path | str = RUNNER_RESULTS_ROOT,
    gates_results_root: Path | str = GATES_RESULTS_ROOT,
) -> dict[str, Any]:
    """Build a deterministic read-only product pipeline queue/status surface."""

    runs_dir = _root_path(repo_root, pipeline_runs_root)
    runner_results = _index_runner_results(_root_path(repo_root, runner_results_root), repo_root)
    advisory_packets = _index_advisory_packets(_root_path(repo_root, gates_results_root), repo_root)
    run_dirs = []
    if runs_dir.is_dir():
        run_dirs = sorted(
            (path for path in runs_dir.iterdir() if path.is_dir()),
            key=lambda path: path.name,
        )
    runs_root_rel = _repo_relative(runs_dir, repo_root)
    entries = [
        _pipeline_entry(path, runs_root_rel, repo_root, runner_results, advisory_packets)
        for path in run_dirs
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "surface_kind": "read_only_product_lab_queue_status",
        "allowed_status_states": list(STATUS_STATES),
        "summary": _summary(entries),
        "non_authority_declaration": dict(NON_AUTHORITY_DECLARATION),
        "artifact_roots": {
            "pipeline_runs_root": runs_root_rel,
            "runner_results_root": _repo_relative(_root_path(repo_root, runner_results_root), repo_root),
            "gates_results_root": _repo_relative(_root_path(repo_root, gates_results_root), repo_root),
        },
        "runs": entries,
    }


def render_markdown(data: Mapping[str, Any]) -> str:
    """Render a static operator-facing Markdown view with no controls."""

    lines = [
        "# Product Lab Queue / Status",
        "",
        f"- schema: `{data['schema_version']}`",
        f"- surface: `{data['surface_kind']}`",
        "- posture: read-only visibility; no approvals, dispatch, scheduler, or notifications",
        "",
        "## Summary",
        "",
    ]
    summary = data["summary"]
    lines.append(f"- runs: {summary['run_count']}")
    lines.append(f"- approvals needed: {summary['approval_needed_count']}")
    lines.append(f"- advisory packets ready: {summary['advisory_packet_ready_count']}")
    lines.append("")
    lines.append("| status | count |")
    lines.append("| --- | ---: |")
    for status, count in summary["by_status"].items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Runs", ""])
    for run in data["runs"]:
        approval = run["approval_needed"]
        lines.append(f"### {run['pipeline_run_id']} - `{run['status']}`")
        lines.append("")
        lines.append(f"- request: `{run.get('request_id')}`")
        lines.append(f"- symbol/timeframe: `{run.get('symbol')}` / `{run.get('timeframe')}`")
        if approval:
            lines.append(f"- Karl approval needed: `{approval['kind']}`")
        if run["blocked_reasons"]:
            lines.append("- blocked reasons: " + "; ".join(run["blocked_reasons"]))
        if run.get("advisory_packet"):
            lines.append(f"- advisory packet: `{run['advisory_packet']['path']}`")
        lines.append(
            "- notification preview: dry-run only, fired="
            f"{str(run['notification_preview']['notification_fired']).lower()}"
        )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
