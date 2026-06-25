# WP-LAB-OPERATOR-BRIEF-REPORT-01 — Read-only operator brief / weekly report surface

## Package

- Package: `WP-LAB-OPERATOR-BRIEF-REPORT-01`
- Decision: `COMPLETE`
- Package class: research-lab reporting surface.
- Execution mode: repo-first, fresh isolated worktree, read-only static
  reporting, no edge-search.

## Branch / Base

- Branch: `lab/operator-brief-report-01`.
- Base: `origin/main` after the `WP-LAB-COORDINATOR-STATE-MODEL-01` merge
  (PR #568) and the `WP-LAB-RESULTS-DASHBOARD-01` merge (PR #569), which provide
  the required state model (`tools/lab_state/`) and the dashboard projection
  (`tools/lab_dashboard/`) this surface consumes.

## Objective

Build an operator-readable daily brief and weekly research-lab report generator
from the coordinator state model. Outputs summarize completed runs, blocked
runs, NO-GOs, open decision surfaces, validation status, artifact links,
withheld statistics and caveats, and candidate-review readiness (only when
evidence exists). The output is **descriptive, not directive**.

## Dependency

`WP-LAB-COORDINATOR-STATE-MODEL-01` is **merged** (PR #568, 2026-06-25). Not
blocked. The surface also consumes the merged results dashboard (PR #569).

## Repo-Truth Discovery

Recorded in `scratch/WP-LAB-OPERATOR-BRIEF-REPORT-01/repo_truth_discovery.md`.
Key finding: the read-only results dashboard (`tools/lab_dashboard`) is a
deterministic projection over the coordinator state model that already exposes
exactly the categories a brief/report needs. The reporting surface consumes the
dashboard data model rather than re-reading artifacts, so there is one
projection of repo truth and no second state derivation. The F-series
`tools/dashboard` surface (intentionally non-deterministic, registry-built) is
the wrong base and was not used.

## Delivered

- `docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md` — surface contract.
- `docs/status_entries/WP-LAB-OPERATOR-BRIEF-REPORT-01.md` — this entry.
- `tools/lab_reporting/report_model.py` — deterministic read-only shaping of the
  dashboard projection into brief/report data.
- `tools/lab_reporting/render.py` — daily brief markdown, weekly report markdown,
  and weekly report static HTML renderers (tables and text only; no
  scripts/controls/recommendations).
- `tools/lab_reporting/run.py` — CLI (`--report-data` / `--daily-brief` /
  `--weekly-report` / `--weekly-report-html` / `--out-dir`, with descriptive
  `--as-of` / `--period` labels).
- `tools/lab_reporting/__init__.py`.
- `tests/test_lab_reporting.py` — 15 tests.
- `scratch/WP-LAB-OPERATOR-BRIEF-REPORT-01/repo_truth_discovery.md`
- `scratch/WP-LAB-OPERATOR-BRIEF-REPORT-01/daily_brief_fixture.md`
- `scratch/WP-LAB-OPERATOR-BRIEF-REPORT-01/weekly_report_fixture.md`
- `scratch/WP-LAB-OPERATOR-BRIEF-REPORT-01/weekly_report_fixture.html`
- `scratch/WP-LAB-OPERATOR-BRIEF-REPORT-01/report_data_fixture.json`
- `scratch/WP-LAB-OPERATOR-BRIEF-REPORT-01/validation_summary.txt`
- `scratch/WP-LAB-OPERATOR-BRIEF-REPORT-01/main_report_back_guardrail.txt`

## Reporting Principles Honored

- **Descriptive, not directive** — no recommendation, ranking-as-authority,
  promotion label, decision label, or readiness verdict.
- State taken **verbatim** from the dashboard projection / coordinator state
  model; **no new state vocabulary**.
- Surfaces completed / blocked / NO-GO runs and open decision surfaces; a NO-GO
  is reported as a conclusion, not a block.
- Validation status (replay + OOS gate + reason codes + OOS evidence status +
  robustness) shown as legibility, never a verdict the surface issues.
- **Withheld statistics** (PSR / DSR / MinTRL) shown explicitly, never
  fabricated; NO-GO caveats carried verbatim.
- **Candidate-review readiness surfaced only when packet evidence exists**;
  otherwise recorded descriptively as no evidence.
- Charting **deferred**; weekly report is table-based static output only.

## Boundary Summary

- No transition executed; descriptive read-only projection only.
- No strategy run/generation, no edge-search, no backtest (reads committed
  JSON/markdown only via the dashboard projection).
- No Strategy Spec, Variant Manifest, Sweep Plan, canonical Result Population,
  trial log, candidate registry, or candidate lifecycle write.
- No canonical crossing, approval, or promotion.
- No runtime, paper/live, OMS, risk, reconciliation, capital, broker, exchange,
  provider/API/network, or funding accounting.
- No auto-send, email/slack/apprise, notification firing, or scheduler
  integration; no executable control in rendered output; no large tracked data.

## Determinism

The model reads no clock, no git, and no network; `as_of` / `period` are
descriptive labels (default `unspecified`). JSON uses sorted keys; markdown and
HTML are deterministic functions of the model, and output strings are ASCII to
avoid platform encoding drift. Two builds over the same checkout and labels are
byte-identical (verified by a test and by repeated CLI runs producing identical
sha256).

## Edge-Search Hold

No further edge-search is authorized by this surface. Strategy
generation/search remains held until separate operator authorization. The
`edge_search_hold` note is carried on every output.

## Validation

Recorded in `scratch/WP-LAB-OPERATOR-BRIEF-REPORT-01/validation_summary.txt`.
Package-required checks: scoped pytest (`tests/test_lab_reporting.py`, 15
passed; with `tests/test_lab_state*.py`, 35 passed; with the dashboard suite,
44 passed), research query `--list-views` (exit 0), diff scope summary (no
forbidden matches), and `git diff --check` (clean). Full repo pytest was not run
to completion and is not claimed as passed; the new code is stdlib-only and its
targeted suites pass.

## Merge Status

Ready for review after push.
