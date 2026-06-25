# WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01 — Default-off research-lab scheduler/run-queue shell

## Package

- Package: `WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01`
- Decision: `COMPLETE`
- Package class: research-lab control-plane shell.
- Execution mode: repo-first, fresh isolated worktree, inert/default-off shell,
  no autonomous behavior, no edge-search.

## Branch / Base

- Branch: `lab/scheduler-shell-default-off-01`.
- Base: `origin/main` @ `335eaac`, after PR #568
  (`WP-LAB-COORDINATOR-STATE-MODEL-01`) and PR #569
  (`WP-LAB-RESULTS-DASHBOARD-01`) merged.

## Objective

Build the control-plane *structure* for a future always-on research lab — run
queue, run status, artifact links, retry/block visibility, default-off config,
dry-run/no-op behavior — **without enabling autonomous execution**. Shell only:
it must not trigger or generate runs.

## Dependencies

- `WP-LAB-COORDINATOR-STATE-MODEL-01` — **MERGED** (PR #568). Required and
  present (`tools/lab_state/`). Not blocked.
- `WP-LAB-RESULTS-DASHBOARD-01` — **MERGED** (PR #569). Convention template.
- `WP-LAB-OPERATOR-BRIEF-REPORT-01` — not present; **not needed** (this shell
  generates no operator brief).
- `WP-LAB-APPROVAL-QUEUE-SURFACE-01` — not present; **not needed** (this shell
  models a *run* queue, not an approval queue, and writes no approvals).

## Repo-Truth Discovery

Recorded in `scratch/WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01/repo_truth_discovery.md`.
Key findings: `tools/lab_state` is the single source of state/subject truth and
is reused verbatim (no new vocabulary). The write/execute-capable automation
modules (`tools/research_automation/*`, `tools/research_runner/*`,
`tools/shadow/*`) are identified and explicitly avoided. No pre-existing
scheduler service, cron trigger, CI workflow, or daemon exists; this package
deliberately does not add one.

## Delivered

- `docs/research/LAB_SCHEDULER_SHELL_DEFAULT_OFF.md` — shell contract doc.
- `docs/status_entries/WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01.md` — this entry.
- `tools/lab_scheduler_shell/config.py` — frozen default-off config + validation.
- `tools/lab_scheduler_shell/model.py` — run-queue schema, run-status / retry /
  block vocabularies, artifact-link model, fixture parse + validation.
- `tools/lab_scheduler_shell/shell.py` — load queue, validate default-off,
  render status, dry-run no-op planner; no executor.
- `tools/lab_scheduler_shell/run.py` — read-only CLI.
- `tools/lab_scheduler_shell/__init__.py`.
- `tests/test_lab_scheduler_shell.py` — 16 tests.
- `scratch/WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01/repo_truth_discovery.md`
- `scratch/WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01/scheduler_shell_contract.json`
- `scratch/WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01/run_queue_fixture.json`
- `scratch/WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01/dry_run_noop_summary.json`
- `scratch/WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01/validation_summary.txt`
- `scratch/WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01/main_report_back_guardrail.txt`

## Default-off guarantees (all `False` by default)

`autonomous_enabled`, `edge_search_enabled`, `run_triggering_enabled`,
`notification_firing_enabled`, `candidate_lifecycle_writes_enabled`,
`runtime_contact_enabled`, `paper_live_contact_enabled`. The config is frozen and
the shell has no executor, so the only emittable action is a planned no-op.

## No autonomous behavior / no edge-search

No scheduler service, cron/CI trigger, or background daemon; no run creation,
strategy generation, retry execution, notification firing, approval or
candidate-lifecycle write, or runtime/paper/live contact. The coordinator state
model's edge-search hold note is carried verbatim and `edge_search_enabled` is
`False`.

## Validation

- `python -m pytest tests/test_lab_scheduler_shell.py -q` → **16 passed**.
- `python -m tools.research_query.run --list-views` → OK (unchanged; the shell
  registers no view).
- `python tools/dev/diff_scope_summary.py` → `exit reason: ok`,
  `forbidden_matches: []`; changes confined to the allowed scope.
- `git diff --check` → clean (no whitespace errors).
- Full pytest not run as part of this entry; the scoped suite was run and passed.
