# Default-Off Research-Lab Scheduler Shell

Status: **inert shell** (read-only, default-off). Package
`WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01`.

## Purpose

Define the control-plane structure a future always-on research lab will need —
a run queue, a run-status model, an artifact-link model, retry/block-state
visibility, a default-off configuration, and a dry-run/no-op planner — **without
enabling any autonomous execution**.

This is a *shell*. It does not create runs, generate strategies, resume
edge-search, fire notifications, write candidate-lifecycle or approval records,
execute retries, or contact any runtime / paper / live path. It has no executor.
The only "action" it can produce is a planned **no-op**.

## Relationship to existing repo truth

State and subject truth come verbatim from the merged coordinator state model
(`tools/lab_state`, `WP-LAB-COORDINATOR-STATE-MODEL-01`, PR #568). The shell:

- reuses `tools.lab_state.model` stages and the `NON_AUTHORITY_DECLARATION` /
  `EDGE_SEARCH_HOLD_NOTE` constants — it invents **no new lab state vocabulary**;
- binds queue entries to committed read-only subjects exposed by
  `tools.lab_state.run.SUBJECTS`;
- reuses the `ArtifactRef` shape (`role`/`path`/`present`/`note`) for its
  artifact-link model.

It deliberately does **not** import, extend, or invoke the write/execute-capable
automation modules (`tools/research_automation/*`, `tools/research_runner/*`,
`tools/shadow/*`, or any paper/live runtime). See
`scratch/WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01/repo_truth_discovery.md`.

## Modules

| Module | Role |
| --- | --- |
| `tools/lab_scheduler_shell/config.py` | Frozen default-off configuration + validation. |
| `tools/lab_scheduler_shell/model.py` | Run-queue schema, run-status / retry / block vocabularies, artifact-link model, fixture parsing + validation. |
| `tools/lab_scheduler_shell/shell.py` | Loads a queue, validates default-off, renders status, plans no-ops. |
| `tools/lab_scheduler_shell/run.py` | Read-only CLI. |

## Default-off configuration

`SchedulerShellConfig` is a frozen dataclass. Every capability that could lead to
autonomous behavior defaults to `False`:

| Flag | Default | Meaning when (hypothetically) on |
| --- | --- | --- |
| `autonomous_enabled` | `false` | master autonomy switch |
| `edge_search_enabled` | `false` | strategy generation / edge-search |
| `run_triggering_enabled` | `false` | creating runs |
| `notification_firing_enabled` | `false` | firing notifications |
| `candidate_lifecycle_writes_enabled` | `false` | writing approval / candidate-lifecycle |
| `runtime_contact_enabled` | `false` | contacting the runtime |
| `paper_live_contact_enabled` | `false` | contacting paper / live |

`validate_default_off()` reports whether every required flag is present and
`False`; `assert_default_off()` raises `SchedulerConfigError` otherwise. Even a
hand-built "enabled" config does not grant the shell an executor — there is none.

## Run-queue data model

A queue entry describes a *would-be* target, not an execution:

```text
run_id, subject_id, target_stage, priority, status, requested_by,
retry { state, attempts, max_attempts, block_reason_code, block_detail },
artifact_links [ { role, path, present, note } ],
depends_on [ run_id ... ], note
```

Validation enforces: unique `run_id`; `status` in the run-status vocabulary;
`target_stage` is a real `tools/lab_state` stage; `subject_id` binds to a known
committed subject; `retry.state` and `block_reason_code` are in their
vocabularies; `depends_on` resolves within the same queue.

### Run-status model

`queued`, `held_default_off`, `blocked`, `retry_scheduled`, `planned_noop`,
`cancelled`. There is **no** `running` / `succeeded` status — nothing executes.
`blocked` and `cancelled` are terminal for the planner.

### Retry / block visibility

Retry states: `none`, `scheduled`, `exhausted`. Block reason codes are
namespaced `SCHED_*` (e.g. `SCHED_AUTONOMY_DISABLED`,
`SCHED_RUN_TRIGGERING_DISABLED`, `SCHED_NO_EXECUTOR_PRESENT`,
`SCHED_DEPENDENCY_UNRESOLVED`, `SCHED_RETRY_BUDGET_EXHAUSTED`). Retries are
**recorded for visibility only and never executed**.

### Artifact-link model

Each entry carries read-only `ArtifactLink` pointers (`role`/`path`/`present`/
`note`). The model performs no I/O; `present` is a static fixture-supplied flag.

## Dry-run / no-op behavior

`plan_dry_run(queue, config)` walks the queue in deterministic order and, for
each non-terminal entry, records the action a fully-authorized future scheduler
*would* consider — marked `action_kind: "no_op"`, `executed: false`. The summary
asserts `executed_any_action: false` and `all_actions_noop: true`. The no-op
reason is `SCHED_AUTONOMY_DISABLED` under the default config (and
`SCHED_NO_EXECUTOR_PRESENT` even if flags were hypothetically flipped, because
the shell has no executor). The dry-run output is a *description*, not an effect.

Every value the planner can emit for `noop_reason_code` is declared in the
`NOOP_REASON_CODES` contract subset (`SCHED_AUTONOMY_DISABLED`,
`SCHED_RUN_TRIGGERING_DISABLED`, `SCHED_NO_EXECUTOR_PRESENT`), each of which is
also a declared `BLOCK_REASON_CODES` entry, so the tool never emits an
undeclared reason code.

## Non-authority declaration

Every shell snapshot carries the coordinator state model's non-authority
declaration plus scheduler-specific guarantees, all `false`:
`is_a_scheduler_service`, `has_cron_or_ci_trigger`, `has_background_daemon`,
`creates_runs`, `generates_strategies`, `executes_retries`, `fires_notifications`,
`writes_approval_or_candidate_lifecycle`, `contacts_runtime`,
`contacts_paper_or_live`, `has_executor`.

## CLI

```bash
python -m tools.lab_scheduler_shell.run --snapshot          # full inert snapshot
python -m tools.lab_scheduler_shell.run --queue-status --json
python -m tools.lab_scheduler_shell.run --dry-run --json    # no-op plan
python -m tools.lab_scheduler_shell.run --validate-config
python -m tools.lab_scheduler_shell.run --list-statuses
```

The CLI defaults to the committed fixture
`scratch/WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01/run_queue_fixture.json`. It writes
nothing.

## What this shell is NOT

No scheduler service, cron/CI trigger, or background daemon; no run creation,
strategy generation, edge-search, retry execution, notification firing, approval
or candidate-lifecycle write, or runtime/paper/live contact. Any real transition
requires separate explicit operator authorization and machinery this package
does not add.
