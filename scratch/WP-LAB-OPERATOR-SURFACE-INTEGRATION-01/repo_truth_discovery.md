# WP-LAB-OPERATOR-SURFACE-INTEGRATION-01 — Repo-Truth Discovery

Read-only inspection of the merged research-lab operator surfaces before any
edit. This package **integrates** the existing surfaces into one read-only entry
point; it creates no new lab-state logic and executes nothing.

## Dependencies — all merged into the current base

| PR | Package | Provides |
| --- | --- | --- |
| #568 | WP-LAB-COORDINATOR-STATE-MODEL-01 | `tools/lab_state/` (canonical state vocabulary, resolver, snapshot) |
| #569 | WP-LAB-RESULTS-DASHBOARD-01 | `tools/lab_dashboard/` (denominator dashboard) |
| #570 | WP-LAB-OPERATOR-BRIEF-REPORT-01 | `tools/lab_reporting/` (daily brief / weekly report) |
| #571 | WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01 | `tools/lab_scheduler_shell/` (inert default-off scheduler shell) |
| #572 | WP-LAB-APPROVAL-QUEUE-SURFACE-01 | `tools/lab_approval_queue/` (read-only gate queue) |

Confirmed present in `git log` (commits `5107b86`, `335eaac`, `5ba9efa`,
`9e8ed40`, `4a3d734`) and on disk under `tools/`. **Not blocked.**

## Surface module truths

- **`tools/lab_state`** — `model.py` defines `STATES`, `OVERALL_STATES`,
  `STAGES`, `NON_AUTHORITY_DECLARATION`, `EDGE_SEARCH_HOLD_NOTE`. `resolver.py`
  exposes `REPO_ROOT` and `build_snapshot(subject, repo_root)`. `run.py` exposes
  `SUBJECTS` (the committed batch of coordinator subjects) and a CLI
  (`--snapshot` / `--list-states` / `--list-stages` / `--list-subjects`).
- **`tools/lab_dashboard`** — `data_model.build_dashboard_data(repo_root=...)`
  returns `denominator_summary` (full population, `by_overall_state`,
  `candidate_ready_count`, `operator_gate_pending_count`, `no_go_count`,
  `blocked_count`), `caveats`, `subjects`, and a `non_authority_declaration`.
  CLI: `--data-json` / `--html` / `--markdown` / `--out-dir`.
- **`tools/lab_reporting`** — `report_model.build_report_data(as_of=, period=,
  repo_root=)` shapes the dashboard into `counts`, `completed_runs`,
  `blocked_runs`, `no_gos`, `open_decision_surfaces`, `candidate_review_readiness`.
  `as_of`/`period` are descriptive labels only (no clock). CLI: `--report-data`
  / `--daily-brief` / `--weekly-report` / `--weekly-report-html` / `--out-dir`.
- **`tools/lab_approval_queue`** — `queue_model.build_queue_data(repo_root=...)`
  returns `queue_summary` (`by_queue_status`, `operator_gate_pending_count`,
  `candidate_review_packet_created_count`, `nothing_candidate_ready`,
  `honest_state_note`), `entries`, `caveats`. This is the canonical source of
  the "no candidate-ready gate unless evidence says otherwise" honest state.
  CLI: `--data-json` / `--html` / `--markdown` / `--list-statuses` / `--out-dir`.
- **`tools/lab_scheduler_shell`** — `shell.SchedulerShell.from_fixture(path)`
  with `.snapshot()` giving `default_off_config`, `config_validation`
  (`all_default_off`), `queue_status`, `dry_run` (`all_actions_noop`,
  `executed_any_action=False`, `noop_reason_code`). Default fixture:
  `scratch/WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01/run_queue_fixture.json`.
  CLI: `--snapshot` / `--queue-status` / `--dry-run` / `--validate-config`.

## Shared invariants every surface already carries

- State truth comes verbatim from `tools/lab_state`; no surface re-derives or
  re-ranks state, and none introduces new state vocabulary.
- Each surface carries `NON_AUTHORITY_DECLARATION` plus surface-specific
  `*_NON_AUTHORITY` flags (no run/approve/promote/retry/scheduler control).
- Each carries `EDGE_SEARCH_HOLD_NOTE` verbatim.
- All are byte-deterministic: no clock, no git, no network; JSON emitted with
  sorted keys; HTML/markdown are pure functions of the model.
- Honest current state across the committed batch: NO-GO / blocked / advisory
  only, **nothing candidate-ready** (asserted by the approval-queue tests).

## Docs

- `docs/research/LAB_COORDINATOR_STATE_MODEL.md`
- `docs/research/LAB_RESULTS_DASHBOARD_SURFACE.md`
- `docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md`
- `docs/research/LAB_APPROVAL_QUEUE_SURFACE.md`
- `docs/research/LAB_SCHEDULER_SHELL_DEFAULT_OFF.md`

## Integration decision

No existing "operator surface" aggregator exists (only the five separate
surfaces). The correct low-risk choice is a new focused
`tools/lab_operator_surface` module that mirrors the merged surface modules
(`*_model.py` + `render.py` + `run.py`): it **composes** the five existing
data-model builders into one integrated index, links to the existing module /
doc / artifact paths, re-uses each surface's honest summary verbatim, adds no
new state vocabulary, renders no executable control, and preserves the
denominator / caveat / edge-search-hold visibility. It calls only the
already-merged read-only builders; it adds no state logic of its own.

## Render-style conventions to mirror

`tools/lab_dashboard/render.py` and the approval-queue renderer establish the
static-document conventions to follow: tables and text only, a shared `_CSS`
block, `_esc()` HTML-escaping, a read-only banner, the edge-search-hold banner,
and **no** `<script>` / `<button>` / `<form>` / `<input>` / `onclick` /
`meta refresh`. The integration landing page reuses these conventions exactly.
