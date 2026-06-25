# WP-LAB-RESULTS-DASHBOARD-01 — Read-only research results dashboard surface

## Package

- Package: `WP-LAB-RESULTS-DASHBOARD-01`
- Decision: `COMPLETE`
- Package class: research-lab operator surface.
- Execution mode: repo-first, fresh isolated worktree, read-only dashboard,
  no edge-search.

## Branch / Base

- Branch: `lab/results-dashboard-01`.
- Base: `origin/main` after PR #568 merge (`5107b86`), which provides the
  required `WP-LAB-COORDINATOR-STATE-MODEL-01` dependency (`tools/lab_state/`,
  `docs/research/LAB_COORDINATOR_STATE_MODEL.md`). The worktree was rebased onto
  the post-merge `origin/main` before work began.

## Objective

Build a read-only operator dashboard surface over completed research runs and
lab states: completed runs, NO-GO / blocked / candidate-ready states, Result
Populations, replay status, OOS gate status, robustness status, candidate-review
reason status, denominator counts and caveats, and artifact drill-down paths. It
is an operator visibility surface with **no executable controls**.

## Dependency

`WP-LAB-COORDINATOR-STATE-MODEL-01` is **merged** (PR #568, 2026-06-25). Not
blocked.

## Repo-Truth Discovery

Recorded in `scratch/WP-LAB-RESULTS-DASHBOARD-01/repo_truth_discovery.md`. Key
finding: an F-series dashboard already exists at `tools/dashboard` but owns a
different, intentionally non-deterministic contract (`dashboard_data.v1`: data
slices, gates, operator review built from `tools/lab_registry`) and does not
consume the new coordinator state model. A new focused `tools/lab_dashboard`
module is the correct, lower-risk choice (package §5 allows it): it reuses
`tools/lab_state` as its single source of state truth, introduces no new state
vocabulary, and is deterministic.

## Delivered

- `docs/research/LAB_RESULTS_DASHBOARD_SURFACE.md` — surface contract.
- `docs/status_entries/WP-LAB-RESULTS-DASHBOARD-01.md` — this entry.
- `tools/lab_dashboard/data_model.py` — deterministic read-only projection of
  coordinator-state snapshots + committed display facts.
- `tools/lab_dashboard/render.py` — static HTML and markdown renderers (tables
  and text only; no scripts/controls).
- `tools/lab_dashboard/run.py` — CLI (`--data-json` / `--html` / `--markdown` /
  `--out-dir`).
- `tools/lab_dashboard/__init__.py`.
- `tests/test_lab_dashboard.py` — 9 tests.
- `scratch/WP-LAB-RESULTS-DASHBOARD-01/repo_truth_discovery.md`
- `scratch/WP-LAB-RESULTS-DASHBOARD-01/dashboard_data_fixture.json`
- `scratch/WP-LAB-RESULTS-DASHBOARD-01/dashboard_render_fixture.html`
- `scratch/WP-LAB-RESULTS-DASHBOARD-01/dashboard_render_fixture.md`
- `scratch/WP-LAB-RESULTS-DASHBOARD-01/validation_summary.txt`
- `scratch/WP-LAB-RESULTS-DASHBOARD-01/main_report_back_guardrail.txt`

## Dashboard Principles Honored

- Shows the **full denominator** (every overall state with its count, including
  zero buckets), not winners only.
- Shows failed / invalid / blocked counts (trial denominator over distinct
  Result Population sets).
- Shows canonical vs **non-canonical** evidence class per subject.
- Shows **NO-GO caveats** derived from the conclusion's primary failure.
- Shows **withheld statistics** (PSR / DSR / MinTRL) explicitly.
- Shows OOS gate status + reason codes and the underlying OOS evidence status.
- Shows replay normalization status and robustness / candidate-review reach
  status.
- No ranking-as-authority, no recommendation labels, no promotion controls, no
  execution buttons.

## Boundary Summary

- No transition executed; descriptive read-only projection only.
- No strategy run/generation, no edge-search, no backtest (reads committed
  JSON/markdown only).
- No Strategy Spec, Variant Manifest, Sweep Plan, canonical Result Population,
  trial log, candidate registry, or candidate lifecycle write.
- No canonical crossing, approval, or promotion.
- No runtime, paper/live, OMS, risk, reconciliation, capital, broker, exchange,
  provider/API/network, funding accounting, or scheduler autonomy.
- No dashboard execution control (no run/approve/promote/retry button, no
  scheduler toggle, no live fetch, no auto-refresh) and no large tracked data.

## Determinism

The data model carries no clock, no git, and no network. JSON is emitted with
sorted keys; HTML and markdown are deterministic functions of the model. Two
builds over the same checkout are byte-identical (verified by a test and by two
CLI runs producing identical sha256).

## Edge-Search Hold

No further edge-search is authorized by this surface. Strategy
generation/search remains held until separate operator authorization.

## Validation

Recorded in `scratch/WP-LAB-RESULTS-DASHBOARD-01/validation_summary.txt`.
Package-required checks: scoped pytest (`tests/test_lab_dashboard*.py`, 9
passed; with `tests/test_lab_state*.py`, 29 passed), research query
`--list-views`, diff scope summary, and `git diff --check`. Full repo pytest was
not run to completion and is not claimed as passed; the new code is stdlib-only
and its targeted suite passes.

## Merge Status

Ready for review after push.
