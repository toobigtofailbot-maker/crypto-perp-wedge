from __future__ import annotations

from pathlib import Path

from tools.lab_pipeline.queue_status import (
    STATUS_STATES,
    build_queue_status,
    render_markdown,
)
from tools.lab_pipeline.state import write_json


def _state(
    root: Path,
    run_id: str,
    *,
    pipeline_status: str,
    current_stage: str,
    blocked_reasons: list[str] | None = None,
    stage_statuses: list[dict] | None = None,
) -> Path:
    run_dir = root / run_id
    payload = {
        "schema_version": "lab_pipeline_state_v1",
        "pipeline_run_id": run_id,
        "request_id": f"REQ-{run_id[-4:]}",
        "current_stage": current_stage,
        "pipeline_status": pipeline_status,
        "source_idea": f"Fixture idea for {run_id}",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "requested_by": "Karl",
        "approval_requirements": {
            "preregistration_packet_sha256": "sha256:" + "1" * 64,
            "required_fields": {
                "approval_scope": "noncanonical_offline_research_execution_only"
            },
        },
        "blocked_reasons": blocked_reasons or [],
        "stage_statuses": stage_statuses or [],
        "non_authority_flags": {
            "fires_notifications": False,
            "uses_scheduler_or_autonomy": False,
            "contacts_paper_live_runtime": False,
        },
    }
    write_json(run_dir / "pipeline_state.json", payload)
    return run_dir


def _runner(root: Path, pipeline_run_id: str, *, status: str = "completed") -> None:
    write_json(
        root / "LRUN-fixture" / "runner_adapter_result.json",
        {
            "schema_version": "product_runner_adapter_result_v1",
            "runner_adapter_run_id": f"LRUN-{pipeline_run_id}",
            "adapter_status": status,
            "source_bindings": {
                "product_pipeline_run_id": pipeline_run_id,
                "execute_approval_path": "scratch/fixture/execute_approval.json",
                "execute_approval_sha256": "sha256:" + "2" * 64,
            },
            "denominator_counts": {
                "completed": 1,
                "failed": 0,
                "invalid": 0,
                "blocked": 0,
                "pruned": 0,
            },
            "non_authority_assertions": {
                "notification_firing": False,
                "scheduler_autonomous_dispatch": False,
            },
        },
    )


def _advisory(root: Path, pipeline_run_id: str, *, status: str = "completed") -> None:
    write_json(
        root / "LGATE-fixture" / "advisory_review_packet.json",
        {
            "schema_version": "product_pipeline_advisory_review_packet_v1",
            "gates_adapter_run_id": f"LGATE-{pipeline_run_id}",
            "adapter_status": status,
            "runner_result_reference": {
                "product_pipeline_run_id": pipeline_run_id,
                "runner_adapter_run_id": f"LRUN-{pipeline_run_id}",
            },
            "candidate_surface_routing": {"surface_status": "needs_more_evidence"},
            "denominator_counts": {
                "completed": 1,
                "failed": 0,
                "invalid": 0,
                "blocked": 0,
                "pruned": 0,
            },
            "withheld_statistics": {"fabricated": False},
            "non_authority_assertions": {
                "notification_firing": False,
                "scheduler_autonomous_dispatch": False,
            },
        },
    )


def _build(tmp_path: Path) -> dict:
    return build_queue_status(
        repo_root=tmp_path,
        pipeline_runs_root="pipeline_runs",
        runner_results_root="runner_outputs",
        gates_results_root="gates_outputs",
    )


def test_committed_pipeline_fixtures_project_current_statuses() -> None:
    data = build_queue_status()
    statuses = {run["status"] for run in data["runs"]}
    assert "awaiting_prereg_approval" in statuses
    assert "awaiting_execute_approval" in statuses
    assert "blocked" in statuses
    assert data["non_authority_declaration"]["notification_firing"] is False
    assert data["non_authority_declaration"]["scheduler_activation"] is False
    assert data["non_authority_declaration"]["job_execution_controls"] is False


def test_status_vocabulary_lists_every_allowed_state(tmp_path: Path) -> None:
    _state(tmp_path / "pipeline_runs", "LPIPE-queued", pipeline_status="queued", current_stage="request_loaded")
    data = _build(tmp_path)
    assert tuple(data["allowed_status_states"]) == STATUS_STATES
    assert set(data["summary"]["by_status"]) == set(STATUS_STATES)


def test_awaiting_prereg_and_execute_approvals_are_distinct(tmp_path: Path) -> None:
    _state(
        tmp_path / "pipeline_runs",
        "LPIPE-prereg",
        pipeline_status="awaiting_prereg_approval",
        current_stage="awaiting_prereg_approval",
        blocked_reasons=["prereg_approval_blocked:missing_prereg_approval"],
    )
    _state(
        tmp_path / "pipeline_runs",
        "LPIPE-exec",
        pipeline_status="complete",
        current_stage="complete",
    )

    entries = {entry["pipeline_run_id"]: entry for entry in _build(tmp_path)["runs"]}

    assert entries["LPIPE-prereg"]["status"] == "awaiting_prereg_approval"
    assert entries["LPIPE-prereg"]["approval_needed"]["kind"] == "prereg_approval"
    assert entries["LPIPE-exec"]["status"] == "awaiting_execute_approval"
    assert entries["LPIPE-exec"]["approval_needed"]["kind"] == "execute_approval"


def test_blocked_running_complete_failed_and_advisory_ready(tmp_path: Path) -> None:
    _state(
        tmp_path / "pipeline_runs",
        "LPIPE-blocked",
        pipeline_status="blocked",
        current_stage="blocked",
        blocked_reasons=["availability_blocked:unsupported_timeframe"],
    )
    _state(
        tmp_path / "pipeline_runs",
        "LPIPE-running",
        pipeline_status="in_progress",
        current_stage="noncanonical_execution_running",
        stage_statuses=[
            {
                "stage": "noncanonical_execution_running",
                "status": "running",
            }
        ],
    )
    _state(
        tmp_path / "pipeline_runs",
        "LPIPE-complete",
        pipeline_status="complete",
        current_stage="complete",
    )
    _runner(tmp_path / "runner_outputs", "LPIPE-complete")
    _state(
        tmp_path / "pipeline_runs",
        "LPIPE-failed",
        pipeline_status="complete",
        current_stage="complete",
    )
    _runner(tmp_path / "runner_outputs" / "failed", "LPIPE-failed", status="failed")
    _state(
        tmp_path / "pipeline_runs",
        "LPIPE-advisory",
        pipeline_status="complete",
        current_stage="complete",
    )
    _runner(tmp_path / "runner_outputs" / "advisory", "LPIPE-advisory")
    _advisory(tmp_path / "gates_outputs", "LPIPE-advisory")

    entries = {entry["pipeline_run_id"]: entry for entry in _build(tmp_path)["runs"]}

    assert entries["LPIPE-blocked"]["status"] == "blocked"
    assert entries["LPIPE-running"]["status"] == "running"
    assert entries["LPIPE-complete"]["status"] == "complete"
    assert entries["LPIPE-failed"]["status"] == "failed"
    assert entries["LPIPE-advisory"]["status"] == "advisory_packet_ready"
    assert entries["LPIPE-advisory"]["advisory_packet"]["path"].endswith(
        "advisory_review_packet.json"
    )


def test_notification_fields_are_dry_run_only(tmp_path: Path) -> None:
    _state(
        tmp_path / "pipeline_runs",
        "LPIPE-prereg",
        pipeline_status="awaiting_prereg_approval",
        current_stage="awaiting_prereg_approval",
    )
    run = _build(tmp_path)["runs"][0]
    preview = run["notification_preview"]
    assert preview["dry_run_only"] is True
    assert preview["would_notify_operator"] is True
    assert preview["channels"] == []
    assert preview["notification_fired"] is False
    assert preview["dispatch_enqueued"] is False


def test_markdown_surface_has_no_executable_controls(tmp_path: Path) -> None:
    _state(tmp_path / "pipeline_runs", "LPIPE-queued", pipeline_status="queued", current_stage="request_loaded")
    rendered = render_markdown(_build(tmp_path)).lower()
    assert "read-only visibility" in rendered
    for forbidden in ("<button", "<form", "<script", "approve button", "retry button"):
        assert forbidden not in rendered
