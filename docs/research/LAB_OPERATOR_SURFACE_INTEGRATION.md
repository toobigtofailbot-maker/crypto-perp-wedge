# Lab Operator Surface — Unified Integration Index (read-only)

Status: read-only operator surface. **This surface is a unified index of where
to look. It is not a control panel and executes nothing.**

## Purpose

Give a lab operator **one** top-level place to see and open every merged
read-only research-lab surface:

- coordinator state snapshot;
- results dashboard;
- latest daily brief;
- latest weekly report;
- approval / gate queue;
- inert default-off scheduler shell (status / dry-run no-op view);
- related artifacts and docs.

Before this surface, the operator experience was fragmented across separate
artifacts. This integration unifies them **without widening authority**.

## What it is

A pure *composition* of the already-merged read-only surfaces. It re-uses each
surface's own data-model builder and re-states each surface's honest summary
verbatim:

| surface | source module | dependency |
| --- | --- | --- |
| coordinator state snapshot | `tools/lab_state` | WP-LAB-COORDINATOR-STATE-MODEL-01 (PR #568) |
| results dashboard | `tools/lab_dashboard` | WP-LAB-RESULTS-DASHBOARD-01 (PR #569) |
| daily brief / weekly report | `tools/lab_reporting` | WP-LAB-OPERATOR-BRIEF-REPORT-01 (PR #570) |
| scheduler shell | `tools/lab_scheduler_shell` | WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01 (PR #571) |
| approval / gate queue | `tools/lab_approval_queue` | WP-LAB-APPROVAL-QUEUE-SURFACE-01 (PR #572) |

State truth ultimately flows from the coordinator state model
(`tools/lab_state`). This index re-derives no state, re-ranks nothing, and
introduces no new state vocabulary or status names.

## What it is not

It writes no approval, fires no notification, writes no candidate-lifecycle
record, executes no canonical crossing or promotion, declares no readiness, runs
no strategy, generates no strategy, runs no backtest, and contacts no
runtime / paper / live path. It renders **no** executable control — no run /
approve / reject / promote / retry button, no scheduler toggle, no live fetch,
no auto-refresh. Any real operator decision happens separately through the
human-gated candidate lifecycle engine (`tools/candidate_lifecycle`); this index
cannot grant it.

## Module

- `tools/lab_operator_surface/index_model.py` — deterministic read-only
  composition of the five surface data models into one index (per-surface tiles
  with module / CLI / doc pointers + honest summary, batch boundary, honest
  current state, related docs, caveats).
- `tools/lab_operator_surface/render.py` — static HTML and markdown landing-page
  renderers (tables, links, and text only; no scripts, no buttons, no forms, no
  auto-refresh).
- `tools/lab_operator_surface/run.py` — CLI:
  `--data-json` / `--markdown` / `--html` / `--out-dir`, with descriptive
  `--as-of` / `--period` labels passed through to the brief / report surface.

## Index contents

- **current lab state summary** — subject count and full `by_overall_state`
  breakdown, taken verbatim from the dashboard denominator summary.
- **per-surface tiles** — each with its package, module path, the read-only CLI
  to open it, its research doc, and a short honest summary.
- **batch boundary summary** — full population (every run and state), not winners
  only: completed runs, NO-GO, blocked, candidate-ready, operator-gate-pending,
  distinct Result Population sets, and the trial denominator over those sets.
- **honest current state** — taken verbatim from the approval queue: no
  candidate is ready for human review unless committed evidence records it. The
  committed batch is NO-GO / blocked / advisory only, so `nothing_candidate_ready`
  is `true`.
- **related artifacts and docs** — pointers to the five dependency research docs
  (and this one) with present/missing flags.
- **batch boundary + caveats + edge-search hold + non-authority declaration**.

## Honest current state

Both committed subjects conclude NO-GO / blocked, and no committed evidence
records a created candidate-review packet. The index therefore re-states the
approval queue's honest verdict: `nothing_candidate_ready = true`,
`candidate_ready_count = 0`, `operator_gate_pending_count = 0`. The index does
not invent readiness; the honest state is asserted by a test.

## Determinism

No clock, no git, no network. The scheduler shell reads a committed static
fixture. JSON is emitted with sorted keys; HTML / markdown are pure functions of
the model. Two builds over the same checkout and the same descriptive labels are
byte-identical.

## Edge-search hold

No further edge-search is authorized by this surface. Strategy
generation / search remains held until separate operator authorization.

## Boundary

Read-only integration index only. No execution authority, no new state logic, no
new state vocabulary, no autonomous behavior, no runtime / paper / live contact,
and no protected-path writes. It touches no OMS, risk, reconciliation, capital,
broker, exchange, order, or funding-accounting path.
