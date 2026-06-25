"""Deterministic read-only data model for the unified operator surface index.

The index is a pure *composition* of the already-merged read-only surfaces:

- the coordinator state model (``tools/lab_state``) — the single source of state
  truth and batch membership;
- the results dashboard (``tools/lab_dashboard``) — denominator summary;
- the operator brief / weekly report (``tools/lab_reporting``);
- the approval / gate queue (``tools/lab_approval_queue``) — the source of the
  honest "nothing candidate-ready unless evidence says otherwise" state;
- the inert default-off scheduler shell (``tools/lab_scheduler_shell``).

It re-uses each surface's own honest summary verbatim. It therefore:

- never re-derives or re-ranks **state** — every state value comes from the
  surface that owns it, which takes it from ``tools.lab_state``;
- introduces **no new state vocabulary** and no new status names;
- holds **no execution authority** — it is an index of where to look, not a
  control panel; it has no run / approve / reject / promote / retry / scheduler
  control, fetches no live data, and never auto-refreshes.

Determinism: the model reads no clock, no git, and no network. The scheduler
shell reads a committed static fixture. Two builds over the same checkout
produce byte-identical output.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.lab_approval_queue.queue_model import build_queue_data
from tools.lab_dashboard.data_model import build_dashboard_data
from tools.lab_reporting.report_model import build_report_data
from tools.lab_scheduler_shell.run import DEFAULT_FIXTURE
from tools.lab_scheduler_shell.shell import SchedulerShell
from tools.lab_state import model
from tools.lab_state.resolver import REPO_ROOT

SCHEMA_VERSION = "lab_operator_surface_integration_v1"

# Read-only integration index. Inherits the coordinator state model's
# non-authority declaration and adds the explicit "this is an index, not a
# control panel" guarantees required by the package (§6 forbidden behavior).
INTEGRATION_NON_AUTHORITY: dict[str, bool] = {
    **model.NON_AUTHORITY_DECLARATION,
    "is_an_integration_index_only": True,
    "renders_executable_control": False,
    "has_run_button": False,
    "has_approve_button": False,
    "has_reject_button": False,
    "has_promote_button": False,
    "has_retry_button": False,
    "has_scheduler_toggle": False,
    "fetches_live_data": False,
    "auto_refreshes": False,
    "ranks_or_recommends": False,
    "introduces_new_state_vocabulary": False,
    "enables_autonomous_behavior": False,
}


def _doc_ref(repo_root: Path, role: str, rel_path: str) -> dict[str, Any]:
    """A pointer to a committed doc / artifact path with a present flag."""
    return {
        "role": role,
        "path": rel_path,
        "present": (repo_root / rel_path).exists(),
    }


def _state_tile(dashboard: dict[str, Any]) -> dict[str, Any]:
    summary = dashboard["denominator_summary"]
    return {
        "key": "coordinator_state",
        "title": "Coordinator state snapshot",
        "package": "WP-LAB-COORDINATOR-STATE-MODEL-01",
        "module": "tools/lab_state",
        "cli": "python -m tools.lab_state.run --snapshot",
        "doc": "docs/research/LAB_COORDINATOR_STATE_MODEL.md",
        "summary": {
            "subject_count": summary["subject_count"],
            "by_overall_state": dict(summary["by_overall_state"]),
        },
    }


def _dashboard_tile(dashboard: dict[str, Any]) -> dict[str, Any]:
    summary = dashboard["denominator_summary"]
    return {
        "key": "results_dashboard",
        "title": "Results dashboard",
        "package": "WP-LAB-RESULTS-DASHBOARD-01",
        "module": "tools/lab_dashboard",
        "cli": "python -m tools.lab_dashboard.run --markdown",
        "doc": "docs/research/LAB_RESULTS_DASHBOARD_SURFACE.md",
        "summary": {
            "completed_experiment_run_count": summary[
                "completed_experiment_run_count"
            ],
            "no_go_count": summary["no_go_count"],
            "blocked_count": summary["blocked_count"],
            "candidate_ready_count": summary["candidate_ready_count"],
            "operator_gate_pending_count": summary["operator_gate_pending_count"],
            "distinct_result_population_sets": summary[
                "distinct_result_population_sets"
            ],
        },
    }


def _brief_tile(report: dict[str, Any]) -> dict[str, Any]:
    counts = report["counts"]
    return {
        "key": "daily_brief",
        "title": "Latest daily brief",
        "package": "WP-LAB-OPERATOR-BRIEF-REPORT-01",
        "module": "tools/lab_reporting",
        "cli": "python -m tools.lab_reporting.run --daily-brief --as-of <label>",
        "doc": "docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md",
        "summary": {
            "as_of": report["as_of"],
            "completed_runs": counts["completed_runs"],
            "blocked_runs": counts["blocked_runs"],
            "no_gos": counts["no_gos"],
            "open_decision_surfaces": counts["open_decision_surfaces"],
        },
    }


def _report_tile(report: dict[str, Any]) -> dict[str, Any]:
    counts = report["counts"]
    return {
        "key": "weekly_report",
        "title": "Latest weekly report",
        "package": "WP-LAB-OPERATOR-BRIEF-REPORT-01",
        "module": "tools/lab_reporting",
        "cli": "python -m tools.lab_reporting.run --weekly-report --period <label>",
        "doc": "docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md",
        "summary": {
            "period": report["period"],
            "subjects": counts["subjects"],
            "candidate_review_evidence": counts["candidate_review_evidence"],
            "withheld_statistics": list(report["withheld_statistics"]),
        },
    }


def _queue_tile(queue: dict[str, Any]) -> dict[str, Any]:
    summary = queue["queue_summary"]
    return {
        "key": "approval_queue",
        "title": "Approval / gate queue",
        "package": "WP-LAB-APPROVAL-QUEUE-SURFACE-01",
        "module": "tools/lab_approval_queue",
        "cli": "python -m tools.lab_approval_queue.run --markdown",
        "doc": "docs/research/LAB_APPROVAL_QUEUE_SURFACE.md",
        "summary": {
            "by_queue_status": dict(summary["by_queue_status"]),
            "operator_gate_pending_count": summary["operator_gate_pending_count"],
            "blocked_validation_count": summary["blocked_validation_count"],
            "no_go_count": summary["no_go_count"],
            "candidate_review_packet_created_count": summary[
                "candidate_review_packet_created_count"
            ],
            "nothing_candidate_ready": summary["nothing_candidate_ready"],
            "honest_state_note": summary["honest_state_note"],
        },
    }


def _scheduler_tile(scheduler: dict[str, Any]) -> dict[str, Any]:
    validation = scheduler["config_validation"]
    dry_run = scheduler["dry_run"]
    queue_status = scheduler["queue_status"]
    return {
        "key": "scheduler_shell",
        "title": "Scheduler shell (inert, default-off)",
        "package": "WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01",
        "module": "tools/lab_scheduler_shell",
        "cli": "python -m tools.lab_scheduler_shell.run --snapshot",
        "doc": "docs/research/LAB_SCHEDULER_SHELL_DEFAULT_OFF.md",
        "summary": {
            "all_default_off": validation["all_default_off"],
            "enabled_flags": list(validation["enabled_flags"]),
            "queue_entry_count": queue_status["entry_count"],
            "dry_run_all_actions_noop": dry_run["all_actions_noop"],
            "dry_run_executed_any_action": dry_run["executed_any_action"],
            "dry_run_noop_reason_code": dry_run["noop_reason_code"],
        },
    }


def _batch_boundary(dashboard: dict[str, Any]) -> dict[str, Any]:
    """Batch boundary summary — full population, never winners only."""
    summary = dashboard["denominator_summary"]
    return {
        "subject_count": summary["subject_count"],
        "by_overall_state": dict(summary["by_overall_state"]),
        "completed_experiment_run_count": summary[
            "completed_experiment_run_count"
        ],
        "no_go_count": summary["no_go_count"],
        "blocked_count": summary["blocked_count"],
        "candidate_ready_count": summary["candidate_ready_count"],
        "operator_gate_pending_count": summary["operator_gate_pending_count"],
        "distinct_result_population_sets": summary[
            "distinct_result_population_sets"
        ],
        "trial_denominator_over_distinct_sets": dict(
            summary["trial_denominator_over_distinct_sets"]
        ),
    }


def _honest_state(queue: dict[str, Any]) -> dict[str, Any]:
    """The honest current state, taken verbatim from the approval queue.

    The queue owns the "nothing candidate-ready unless committed evidence
    records it" truth. This surface re-states it; it never invents readiness.
    """
    summary = queue["queue_summary"]
    return {
        "nothing_candidate_ready": summary["nothing_candidate_ready"],
        "candidate_ready_count": summary[
            "candidate_review_packet_created_count"
        ],
        "operator_gate_pending_count": summary["operator_gate_pending_count"],
        "note": summary["honest_state_note"],
    }


def _global_caveats() -> list[str]:
    return [
        "This is a read-only index of where to look; it is not a control panel "
        "and holds no execution authority.",
        "Every state value is taken verbatim from the surface that owns it "
        "(ultimately the coordinator state model); this index re-ranks nothing "
        "and adds no new state vocabulary.",
        "The denominator is the full population (every run and state), shown by "
        "the dashboard and brief/report — not winners only.",
        "Honest current state: no candidate is ready for human review unless the "
        "approval queue's committed evidence records it.",
        "The scheduler shell is inert and default-off; its dry-run actions are "
        "all no-ops and it has no executor.",
        "Any real transition, approval, promotion, or run requires separate "
        "human action through the human-gated candidate lifecycle engine; this "
        "index cannot grant it.",
    ]


def build_index_data(
    *,
    as_of: str | None = None,
    period: str | None = None,
    repo_root: Path = REPO_ROOT,
    scheduler_fixture: Path | None = None,
) -> dict[str, Any]:
    """Build the unified read-only operator-surface index (deterministic).

    ``as_of`` / ``period`` are passed through to the brief / report surface as
    descriptive labels only (no clock is read). The scheduler shell reads a
    committed static fixture (``scheduler_fixture`` defaults to the merged
    default fixture). All underlying builders project subjects in sorted order,
    so the output is byte-stable.
    """
    dashboard = build_dashboard_data(repo_root=repo_root)
    report = build_report_data(as_of=as_of, period=period, repo_root=repo_root)
    queue = build_queue_data(repo_root=repo_root)

    fixture = scheduler_fixture or DEFAULT_FIXTURE
    scheduler = SchedulerShell.from_fixture(fixture).snapshot()

    surfaces = [
        _state_tile(dashboard),
        _dashboard_tile(dashboard),
        _brief_tile(report),
        _report_tile(report),
        _queue_tile(queue),
        _scheduler_tile(scheduler),
    ]

    related_docs = [
        _doc_ref(repo_root, "integration", "docs/research/LAB_OPERATOR_SURFACE_INTEGRATION.md"),
        _doc_ref(repo_root, "state_model", "docs/research/LAB_COORDINATOR_STATE_MODEL.md"),
        _doc_ref(repo_root, "dashboard", "docs/research/LAB_RESULTS_DASHBOARD_SURFACE.md"),
        _doc_ref(repo_root, "brief_report", "docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md"),
        _doc_ref(repo_root, "approval_queue", "docs/research/LAB_APPROVAL_QUEUE_SURFACE.md"),
        _doc_ref(repo_root, "scheduler_shell", "docs/research/LAB_SCHEDULER_SHELL_DEFAULT_OFF.md"),
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "surface_kind": "read_only_operator_surface_index",
        "non_authority_declaration": dict(INTEGRATION_NON_AUTHORITY),
        "edge_search_hold": model.EDGE_SEARCH_HOLD_NOTE,
        "as_of": report["as_of"],
        "period": report["period"],
        "batch_boundary": _batch_boundary(dashboard),
        "honest_state": _honest_state(queue),
        "surfaces": surfaces,
        "related_docs": related_docs,
        "caveats": _global_caveats(),
    }
