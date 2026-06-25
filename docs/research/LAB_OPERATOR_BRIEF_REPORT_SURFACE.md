# Lab Operator Brief / Weekly Report Surface

## Status and Authority

This document defines the **read-only** operator daily brief and weekly
research-lab report surface. It generates operator-readable artifacts that
summarize completed runs, blocked runs, NO-GOs, open decision surfaces,
validation status, artifact links, withheld statistics and caveats, and
candidate-review readiness (only when evidence exists).

The surface is **descriptive only**. It does not recommend, rank as authority,
apply promotion or decision labels, declare a readiness verdict, execute a
transition, run or generate a strategy, resume edge-search, write canonical or
candidate-lifecycle evidence, execute canonical crossing, auto-send, fire
notifications, integrate a scheduler, or touch runtime, paper/live, OMS, risk,
reconciliation, capital, broker, exchange, provider/API, or funding accounting
paths.

It is implemented by `tools/lab_reporting/` and exercised by
`tests/test_lab_reporting.py`.

## Relationship to the coordinator state model and dashboard

The brief/report is a pure shaping of the merged **lab results dashboard**
projection (`tools/lab_dashboard/`), which is itself a deterministic projection
of the merged **lab coordinator state model** (`tools/lab_state/`,
`docs/research/LAB_COORDINATOR_STATE_MODEL.md`). This surface:

- **never re-derives or re-ranks state** — per-subject and overall state are
  taken verbatim from the dashboard projection, which takes them verbatim from
  `tools.lab_state.resolver.build_snapshot`;
- introduces **no new state vocabulary**;
- reuses the dashboard's display facts (denominator, evidence class, withheld
  statistics, NO-GO caveats, OOS/replay/robustness status, artifact drill-down).

Consuming the dashboard model keeps a single projection of repo truth: there is
no second state derivation and no second artifact read path.

## What the surface shows

For the whole population (counts):

- subject count, completed-run count, blocked-run count, NO-GO count, open
  decision-surface count, candidate-review-evidence count, and the **full**
  `by_overall_state` map (every overall state with its count, including zero
  buckets) — the full denominator, not winners only.

Sectioned, descriptively:

- **Completed runs** — subjects that reached at least an experiment-complete
  legibility bucket.
- **Blocked runs** — subjects whose overall state is `blocked` or that carry any
  blocked stage. (A NO-GO is a *conclusion*, not a block, and is listed
  separately.)
- **NO-GOs** — subjects concluded NO-GO, with their NO-GO caveats carried
  verbatim from the conclusion.
- **Open decision surfaces** — subjects in `candidate_ready_for_human_review` or
  `operator_gate_pending` (a human decision is pending; the surface never makes
  it).
- **Validation status** — replay normalization state, OOS gate state + reason
  code + underlying OOS evidence status, robustness state, and withheld
  statistics. This is legibility, never a pass/fail verdict the surface issues.
- **Candidate-review readiness** — surfaced **only when packet evidence exists**
  (state `candidate_ready_for_human_review`); otherwise each subject is recorded
  descriptively as having no candidate-review evidence and why. This is never a
  registration, ranking, readiness verdict, or promotion.
- **Artifact links** — de-duplicated repo-relative artifact paths with a
  `present` flag.
- **Withheld statistics and caveats** — withheld statistics (e.g. PSR / DSR /
  MinTRL) shown explicitly rather than fabricated, plus the inherited global
  caveats.

## Non-authority boundary

The data model carries a `non_authority_declaration` that extends the
dashboard's declaration (which extends the coordinator state model's) with the
explicit reporting guarantees:

```
descriptive_only: true
emits_recommendations: false
ranks_as_authority: false
applies_promotion_labels: false
applies_decision_labels: false
declares_readiness_verdict: false
auto_sends: false
fires_notifications: false
integrates_scheduler: false
suggests_edge_search: false
```

Every output carries the `edge_search_hold` note — the surface authorizes no new
edge-search. The static HTML renderer emits tables and text only: no `<script>`,
`<button>`, `<form>`, `<input>`, `onclick`, or `<meta http-equiv="refresh">`.
There is no network fetch, no auto-refresh, no send, and no notification.

## Determinism

The model reads **no clock, no git, and no network**. The brief / report
`as_of` and `period` are explicit descriptive labels supplied by the caller
(default `unspecified`). JSON is emitted with sorted keys; the markdown and HTML
renderers are deterministic functions of the model. Two builds over the same
checkout and the same labels are byte-identical (verified by
`tests/test_lab_reporting.py::test_render_is_deterministic_across_two_builds` and
by repeated CLI runs producing identical sha256). Output strings are ASCII to
avoid platform encoding drift.

## Charting

The weekly report is **table-based static output only**. No safe,
dependency-light static-chart path is adopted, so per the package scope charting
is recorded as **deferred** (`charting.enabled = false`) rather than adding a
dependency. Counts are shown as text tables.

## CLI

```
python -m tools.lab_reporting.run --report-data                       # data model JSON
python -m tools.lab_reporting.run --daily-brief --as-of 2026-06-25    # daily brief markdown
python -m tools.lab_reporting.run --weekly-report --period 2026-W26   # weekly report markdown
python -m tools.lab_reporting.run --weekly-report-html --period 2026-W26  # weekly report HTML
python -m tools.lab_reporting.run --out-dir <dir> --as-of D --period W     # write all four
```

Committed read-only fixtures live under
`scratch/WP-LAB-OPERATOR-BRIEF-REPORT-01/` (`report_data_fixture.json`,
`daily_brief_fixture.md`, `weekly_report_fixture.md`,
`weekly_report_fixture.html`).
