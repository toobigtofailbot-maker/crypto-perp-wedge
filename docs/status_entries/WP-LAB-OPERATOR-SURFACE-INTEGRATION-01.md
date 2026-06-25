# WP-LAB-OPERATOR-SURFACE-INTEGRATION-01 — Unified read-only operator entry point

## Package

- Package: `WP-LAB-OPERATOR-SURFACE-INTEGRATION-01`
- Decision: `COMPLETE`
- Package class: research-lab operator experience / read-only integration surface.
- Execution mode: repo-first, fresh isolated worktree, read-only integration,
  no writes, no edge-search, no autonomous behavior.

## Objective

Unify the merged research-lab operator surfaces into one coherent read-only
entry point so the operator has one top-level place to see and open the
coordinator state snapshot, results dashboard, latest daily brief, latest weekly
report, approval / gate queue, scheduler-shell status, and related docs. **This
WP integrates existing surfaces. It creates no new lab state logic and executes
nothing.**

## Dependencies — all merged

| PR | Package | Provides |
| --- | --- | --- |
| #568 | WP-LAB-COORDINATOR-STATE-MODEL-01 | `tools/lab_state/` |
| #569 | WP-LAB-RESULTS-DASHBOARD-01 | `tools/lab_dashboard/` |
| #570 | WP-LAB-OPERATOR-BRIEF-REPORT-01 | `tools/lab_reporting/` |
| #571 | WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01 | `tools/lab_scheduler_shell/` |
| #572 | WP-LAB-APPROVAL-QUEUE-SURFACE-01 | `tools/lab_approval_queue/` |

All present on the current base (`git log` commits `5107b86`, `335eaac`,
`5ba9efa`, `9e8ed40`, `4a3d734`). **Not blocked.**

## Repo-Truth Discovery

Recorded in
`scratch/WP-LAB-OPERATOR-SURFACE-INTEGRATION-01/repo_truth_discovery.md`. Key
findings: every surface exposes a deterministic read-only data-model builder
(`build_dashboard_data`, `build_report_data`, `build_queue_data`,
`SchedulerShell.from_fixture(...).snapshot()`) sharing one state source
(`tools/lab_state`), the `NON_AUTHORITY_DECLARATION`, and the
`EDGE_SEARCH_HOLD_NOTE`. No aggregator existed. The correct low-risk choice is a
new focused `tools/lab_operator_surface` module that mirrors the merged surface
modules and **composes** the five existing builders — adding no new state
vocabulary and rendering no executable control.

## Delivered

- `docs/research/LAB_OPERATOR_SURFACE_INTEGRATION.md` — surface contract.
- `docs/status_entries/WP-LAB-OPERATOR-SURFACE-INTEGRATION-01.md` — this entry.
- `tools/lab_operator_surface/__init__.py`.
- `tools/lab_operator_surface/index_model.py` — deterministic composition of the
  five surface data models into one index.
- `tools/lab_operator_surface/render.py` — static HTML / markdown landing-page
  renderers (tables / links / text only; no scripts/controls).
- `tools/lab_operator_surface/run.py` — CLI (`--data-json` / `--markdown` /
  `--html` / `--out-dir`, with descriptive `--as-of` / `--period`).
- `tests/test_lab_operator_surface.py` — 11 tests.
- `scratch/WP-LAB-OPERATOR-SURFACE-INTEGRATION-01/repo_truth_discovery.md`
- `scratch/WP-LAB-OPERATOR-SURFACE-INTEGRATION-01/operator_surface_index_data.json`
- `scratch/WP-LAB-OPERATOR-SURFACE-INTEGRATION-01/operator_surface_index.md`
- `scratch/WP-LAB-OPERATOR-SURFACE-INTEGRATION-01/operator_surface_index.html`
- `scratch/WP-LAB-OPERATOR-SURFACE-INTEGRATION-01/validation_summary.txt`
- `scratch/WP-LAB-OPERATOR-SURFACE-INTEGRATION-01/main_report_back_guardrail.txt`

## What the index exposes

- current lab state summary (subjects + full `by_overall_state`);
- per-surface tiles (package, module path, read-only CLI, research doc, honest
  summary) for state / dashboard / daily brief / weekly report / approval queue /
  scheduler shell;
- batch boundary summary (full population, not winners only);
- honest current state taken verbatim from the approval queue;
- related artifacts and docs with present/missing flags;
- caveats, edge-search hold, and the non-authority declaration.

## Honest current state

Both committed subjects conclude NO-GO / blocked and no committed evidence
records a created candidate-review packet, so the index re-states
`nothing_candidate_ready = true`, `candidate_ready_count = 0`,
`operator_gate_pending_count = 0`. No fake candidate-ready entries were created;
this is asserted by a test.

## Boundary Summary

- No new lab state logic, no new state vocabulary, no new status names; state is
  taken verbatim from the merged surfaces.
- No execution authority: no run / approve / reject / promote / retry / scheduler
  control, no live fetch, no auto-refresh, no hidden ranking or recommendation.
- No approval write, candidate-lifecycle write, notification firing, canonical
  crossing, promotion, or readiness declaration.
- No strategy run/generation, no edge-search, no backtest/sweep (reads committed
  JSON/markdown + one committed scheduler fixture only).
- No Strategy Spec, Variant Manifest, Sweep Plan, canonical Result Population,
  trial log, candidate registry, or candidate lifecycle write.
- No autonomous scheduler/scout/coordinator behavior enabled.
- No runtime, paper/live, OMS, risk, reconciliation, capital, broker, exchange,
  provider/API/network, or funding-accounting path; no large tracked data.

## Determinism

No clock, no git, no network; the scheduler shell reads a committed static
fixture. JSON emitted with sorted keys; HTML/markdown are pure functions of the
model. Two `--data-json` builds over the same checkout and labels are
byte-identical. The committed (LF) index data artifact for labels as-of
`2026-06-25` / period `2026-W26` is sha256
`d4d2ff3059a4ecda7344f03559dbba951ccbc1fc513e692d2155af086342af4d`.

## Edge-Search Hold

No further edge-search is authorized by this surface. Strategy
generation/search remains held until separate operator authorization.

## Validation

Recorded in
`scratch/WP-LAB-OPERATOR-SURFACE-INTEGRATION-01/validation_summary.txt`. Scoped
pytest (`tests/test_lab_operator_surface.py`, 11 passed), full dependent-surface
suite (`tests/test_lab_state*.py tests/test_lab_dashboard*.py
tests/test_lab_reporting*.py tests/test_lab_approval_queue*.py
tests/test_lab_scheduler_shell*.py`, 73 passed), research query `--list-views`
(unchanged), diff scope summary (no forbidden-path matches), `git diff --check`
(clean), HTML control scan (no `<script>` / `<button>` / `<form>` / `<input>` /
`onclick` / meta refresh), and deterministic two-build output. Full repo pytest
was not run to completion and is not claimed as passed; the new code is
stdlib-only and its scoped suites pass.

## Merge Status

Ready for review after push.
