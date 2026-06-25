# WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01 — Repo-Truth Discovery

## Purpose

Establish the control-plane *shell* for a future always-on research lab without
enabling any autonomous behavior. This document records what already exists in
the repo so the shell reuses state truth, avoids duplicating runtime/automation
code, and stays strictly inert (default-off, dry-run/no-op only).

## Dependencies (package §3)

- `WP-LAB-COORDINATOR-STATE-MODEL-01` — **MERGED** (PR #568, `5107b86`,
  2026-06-25). Provides `tools/lab_state/` (`model.py`, `resolver.py`,
  `run.py`) and `docs/research/LAB_COORDINATOR_STATE_MODEL.md`. This is the
  single source of lab *state* truth. **Present → not blocked.**
- `WP-LAB-RESULTS-DASHBOARD-01` — **MERGED** (PR #569, `335eaac`, 2026-06-25).
  Provides `tools/lab_dashboard/` read-only surface. Useful as a convention
  template; not a hard dependency for the shell.
- `WP-LAB-OPERATOR-BRIEF-REPORT-01` — not present in the tree. Explicitly **not
  needed**: the scheduler shell does not generate operator briefs.
- `WP-LAB-APPROVAL-QUEUE-SURFACE-01` — not present in the tree. Explicitly **not
  needed**: the shell models a *run queue*, not an approval queue, and performs
  no approval/candidate-lifecycle writes.

Conclusion: the required state-model dependency is present, so this package is
**not blocked**.

## State-model truth reused (no new vocabulary invented)

`tools/lab_state/model.py`:

- `SCHEMA_VERSION = "lab_coordinator_state_model_v1"`.
- `STAGES` — the ordered pipeline stages (`idea_intake` … `operator_gate`).
- `STATES` / `OVERALL_STATES` — the canonical lab state vocabulary.
- `NON_AUTHORITY_DECLARATION` — read-only / no-transition / no-crossing /
  no-candidate-write / no-edge-search / no-paper-live flags. The shell extends
  this with scheduler-specific default-off flags.
- `EDGE_SEARCH_HOLD_NOTE` — required edge-search hold string.

`tools/lab_state/run.py` exposes `SUBJECTS` — the committed read-only subject
bindings. The scheduler-shell run-queue fixture references these `subject_id`s
(`H-FUNDING-RATE-POSITIONING-FADE-01`, `OOS-GATE-FIXTURE-RP-2592`) so a queue
entry's planned (no-op) target is a real, already-concluded subject and nothing
new is generated.

`tools/lab_state/resolver.py` exposes the `ArtifactRef` shape
(`role`/`path`/`present`/`note`) reused by the shell's artifact-link model.

## Existing automation / runtime code to AVOID

These are real, write/execute-capable modules. The shell must **not** import,
invoke, extend, or duplicate their execution behavior:

- `tools/research_automation/local_batch_runner.py` — executes local batch runs.
- `tools/research_automation/local_dry_run_runner.py` — a runner (executes).
- `tools/research_automation/local_parameter_sweep.py` — runs sweeps.
- `tools/research_automation/local_run_registry.py` — writes a run registry.
- `tools/research_runner/*` — offline sweep / robustness report execution.
- `tools/research_agents/formalizer_runner_bridge.py` — agent→runner bridge.
- `tools/shadow/shadow_run_helper.py` — shadow runtime helper.
- any paper/live runtime, OMS, risk, reconciliation, broker/order paths.

The shell is a distinct, inert module (`tools/lab_scheduler_shell/`) that only
*describes* a queue and *plans* no-op actions. It never reaches any of the above.

## Discovery search

```
Select-String -Path docs\**\*.md,tools\**\*.py,tests\**\*.py,configs\**\*,scratch\**\*.json `
  -Pattern "scheduler|queue|run queue|retry|blocked|dry-run|default-off|scout|coordinator|autonomous|approval"
```

Relevant hits: `tools/research_automation/*` (runtime — avoid), `tools/lab_state/*`
and `tools/lab_dashboard/*` (read-only surfaces — reuse), architecture docs
describing future automation operating model (background context only).

No pre-existing scheduler *service*, cron trigger, GitHub Action workflow, or
background daemon for the research lab exists. This package deliberately does
**not** add one — it adds only the control-plane data/contract shell.

## Decision

Build `tools/lab_scheduler_shell/` as an inert, default-off, read-only shell:
queue schema + run-status model + artifact-link model + retry/block visibility +
default-off config validation + a dry-run planner that returns no-op actions
only. Reuse `tools/lab_state` for all state and subject truth. Introduce no new
lab state vocabulary and no execution path.
