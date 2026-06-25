"""Default-off research-lab scheduler / run-queue *shell* (inert control plane).

This package defines the control-plane structure a future always-on research lab
would need — a run-queue data model, a run-status model, an artifact-link model,
retry/block-state visibility, a default-off configuration, and a dry-run/no-op
planner — **without enabling any autonomous execution**.

It is a shell only. It does not create runs, generate strategies, resume
edge-search, fire notifications, write candidate-lifecycle records, or contact
any runtime / paper / live path. Every default-off guarantee defaults to
``False`` and the only "action" it can produce is a planned *no-op*.

State and subject truth come verbatim from the merged coordinator state model
(``tools/lab_state``); no new lab state vocabulary is invented here.
"""

from __future__ import annotations

from tools.lab_scheduler_shell.config import (
    DEFAULT_OFF_FLAGS,
    SchedulerShellConfig,
    default_config,
    validate_default_off,
)
from tools.lab_scheduler_shell.model import (
    SCHEMA_VERSION,
    RUN_STATUSES,
    RETRY_STATES,
    QueueEntry,
    RunQueue,
)
from tools.lab_scheduler_shell.shell import (
    SchedulerShell,
    plan_dry_run,
)

__all__ = [
    "DEFAULT_OFF_FLAGS",
    "SchedulerShellConfig",
    "default_config",
    "validate_default_off",
    "SCHEMA_VERSION",
    "RUN_STATUSES",
    "RETRY_STATES",
    "QueueEntry",
    "RunQueue",
    "SchedulerShell",
    "plan_dry_run",
]
