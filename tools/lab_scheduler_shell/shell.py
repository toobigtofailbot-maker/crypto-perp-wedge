"""The inert scheduler shell: load a queue, validate default-off, plan no-ops.

This is the control-plane *behavior* allowed by the package:

- parse a static run-queue fixture,
- validate the default-off configuration,
- render queue status (statuses, retry/block visibility, artifact refs),
- produce a dry-run plan whose every action is an explicit **no-op**.

It has no executor. There is no method here that creates a run, generates a
strategy, fires a notification, writes a candidate-lifecycle record, retries
anything, or contacts a runtime/paper/live path. The dry-run planner is the only
"action" entry point and it returns descriptions of actions that were *not*
taken and never will be in this shell.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.lab_scheduler_shell import model
from tools.lab_scheduler_shell.config import (
    SchedulerShellConfig,
    default_config,
    validate_default_off,
)
from tools.lab_state import model as lab_state_model
from tools.lab_state.resolver import REPO_ROOT
from tools.lab_state.run import SUBJECTS


def _known_subject_ids() -> frozenset[str]:
    return frozenset(s.get("subject_id", "") for s in SUBJECTS.values())


# Static, inert non-authority declaration. Extends the coordinator state model's
# declaration with the scheduler-specific "no execution" guarantees (package §5).
SCHEDULER_NON_AUTHORITY: dict[str, bool] = {
    **lab_state_model.NON_AUTHORITY_DECLARATION,
    "is_a_scheduler_service": False,
    "has_cron_or_ci_trigger": False,
    "has_background_daemon": False,
    "creates_runs": False,
    "generates_strategies": False,
    "executes_retries": False,
    "fires_notifications": False,
    "writes_approval_or_candidate_lifecycle": False,
    "contacts_runtime": False,
    "contacts_paper_or_live": False,
    "has_executor": False,
}


@dataclass(frozen=True)
class SchedulerShell:
    """Bundles an inert config and a parsed run queue."""

    config: SchedulerShellConfig
    queue: model.RunQueue

    @classmethod
    def from_fixture(
        cls,
        fixture_path: Path,
        config: SchedulerShellConfig | None = None,
    ) -> "SchedulerShell":
        """Load and validate a run-queue fixture (read-only file I/O only)."""
        config = config or default_config()
        raw = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
        queue = model.build_queue(raw, known_subject_ids=_known_subject_ids())
        return cls(config=config, queue=queue)

    # -- read-only views ----------------------------------------------------
    def config_validation(self) -> dict[str, Any]:
        return validate_default_off(self.config)

    def queue_status(self) -> dict[str, Any]:
        """Render queue status: statuses, retry/block states, artifact refs."""
        by_status = {status: 0 for status in model.RUN_STATUSES}
        rows: list[dict[str, Any]] = []
        for entry in self.queue.ordered():
            by_status[entry.status] = by_status.get(entry.status, 0) + 1
            rows.append(
                {
                    "run_id": entry.run_id,
                    "subject_id": entry.subject_id,
                    "target_stage": entry.target_stage,
                    "priority": entry.priority,
                    "status": entry.status,
                    "retry": entry.retry.to_dict(),
                    "artifact_links": [a.to_dict() for a in entry.artifact_links],
                    "depends_on": list(entry.depends_on),
                }
            )
        return {
            "schema_version": self.queue.schema_version,
            "entry_count": len(self.queue.entries),
            "by_status": by_status,
            "entries": rows,
        }

    def dry_run(self) -> dict[str, Any]:
        """Produce a dry-run plan. Every planned action is a no-op."""
        return plan_dry_run(self.queue, self.config)

    def snapshot(self) -> dict[str, Any]:
        """Full read-only shell snapshot (config + status + dry-run no-op)."""
        return {
            "schema_version": model.SCHEMA_VERSION,
            "surface_kind": "inert_scheduler_shell",
            "non_authority_declaration": dict(SCHEDULER_NON_AUTHORITY),
            "default_off_config": self.config.as_dict(),
            "config_validation": self.config_validation(),
            "queue_status": self.queue_status(),
            "dry_run": self.dry_run(),
            "edge_search_hold": lab_state_model.EDGE_SEARCH_HOLD_NOTE,
        }


def _noop_reason(config: SchedulerShellConfig) -> str:
    """Why a planned action is a no-op, given the (default-off) config."""
    if not config.autonomous_enabled:
        return "SCHED_AUTONOMY_DISABLED"
    if not config.run_triggering_enabled:
        return "SCHED_RUN_TRIGGERING_DISABLED"
    # Even if (hypothetically) those were on, the shell has no executor.
    return "SCHED_NO_EXECUTOR_PRESENT"


def plan_dry_run(
    queue: model.RunQueue, config: SchedulerShellConfig | None = None
) -> dict[str, Any]:
    """Plan a dry run over ``queue``. Returns planned **no-op** actions only.

    For every non-terminal entry the planner records the action a future, fully
    authorized scheduler *would* consider, and marks it ``no_op`` with the reason
    autonomy / run-triggering is disabled. No action is ever performed; the
    return value is a description, not an effect.
    """
    config = config or default_config()
    validation = validate_default_off(config)
    reason = _noop_reason(config)

    planned: list[dict[str, Any]] = []
    for entry in queue.ordered():
        terminal = entry.status in model.TERMINAL_RUN_STATUSES
        planned.append(
            {
                "run_id": entry.run_id,
                "subject_id": entry.subject_id,
                "target_stage": entry.target_stage,
                "would_be_action": "none"
                if terminal
                else f"plan_stage:{entry.target_stage}",
                "executed": False,
                "action_kind": "no_op",
                "noop_reason_code": reason,
                "skipped_terminal": terminal,
            }
        )

    return {
        "dry_run": True,
        "executed_any_action": False,
        "planned_action_count": len(planned),
        "noop_action_count": len(planned),
        "all_actions_noop": True,
        "config_default_off": validation["all_default_off"],
        "noop_reason_code": reason,
        "planned_actions": planned,
        "note": (
            "Dry-run plan only. No run was created, no strategy generated, no "
            "retry executed, no notification fired, no candidate-lifecycle or "
            "approval record written, and no runtime/paper/live path contacted."
        ),
    }
