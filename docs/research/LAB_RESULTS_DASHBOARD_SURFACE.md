# Lab Results Dashboard Surface

## Status and Authority

This document defines the **read-only** research results dashboard surface. It
is an operator visibility surface over completed research runs and lab states.
It contains **no executable controls**.

The surface is descriptive only. It does not execute a transition, run or
generate a strategy, resume edge-search, write canonical or candidate-lifecycle
evidence, execute canonical crossing, rank or recommend, declare readiness or
promotion, or touch runtime, paper/live, OMS, risk, reconciliation, capital,
broker, exchange, provider/API, or funding accounting paths.

It is implemented by `tools/lab_dashboard/` and exercised by
`tests/test_lab_dashboard.py`.

## Relationship to the coordinator state model

The dashboard is a pure projection of the merged **lab coordinator state model**
(`docs/research/LAB_COORDINATOR_STATE_MODEL.md`, `tools/lab_state/`). It does
**not** invent or re-derive state and introduces **no new state vocabulary**:

- per-stage and overall **state** is taken verbatim from
  `tools.lab_state.resolver.build_snapshot`;
- **display facts** (denominator breakdown, Result Population identities,
  withheld statistics, evidence class, NO-GO caveats) are read from the same
  committed artifacts the resolver already consults.

It is a separate module from the F-series `tools/dashboard` surface, which owns
a different contract (`dashboard_data.v1`: data slices, gates, operator review)
and is intentionally non-deterministic (`generated_at_utc`, git subprocess). See
`scratch/WP-LAB-RESULTS-DASHBOARD-01/repo_truth_discovery.md` for the rationale.

## What the surface shows

For the whole population:

- **Denominator summary** — subject count, completed-experiment-run count, and
  the **full** `by_overall_state` map listing *every* overall state with its
  count (including zero buckets), so failed / blocked / NO-GO buckets are always
  visible. This is the full denominator, **not winners only**.
- **Trial denominator** — planned / complete / failed / invalid / blocked /
  pruned aggregated over *distinct* Result Population sets (a shared conclusion
  artifact is never double-counted).
- **Caveats** — non-canonical evidence class, dry-run-only OOS is not a pass,
  withheld statistics shown explicitly, ordering is display-only (no ranking),
  and any real transition/approval requires separate human action.

For each subject (completed run / lab state):

- overall state and **evidence class** (canonical vs non-canonical);
- **denominator** breakdown with `preserved` flag;
- **Result Populations** (id, exit mode, rows, sha256) for drill-down;
- **replay** normalization status (state + reason code);
- **OOS gate** status (state + reason code) and the underlying OOS evidence
  status (e.g. `completed_dry_run_only`);
- **robustness** status with the explicit list of **withheld statistics**;
- **candidate-review reach** reason status (`NO_GO_*` / `BLOCKED_*` / ready);
- **reporting** and **operator-gate** status;
- **NO-GO caveats** derived from the conclusion's primary failure and
  interpretation caveats;
- **artifact drill-down** — de-duplicated repo-relative paths with a `present`
  flag.

## Non-authority boundary

The data model carries a `non_authority_declaration` that extends the
coordinator state model's declaration with explicit dashboard guarantees:

```
renders_executable_control: false
has_run_button: false
has_approve_button: false
has_promote_button: false
has_retry_button: false
has_scheduler_toggle: false
fetches_live_data: false
auto_refreshes_from_network: false
ranks_as_authority: false
shows_recommendation_labels: false
```

The static HTML renderer emits tables and text only: no `<script>`, `<button>`,
`<form>`, `<input>`, `onclick`, or `<meta http-equiv="refresh">`. There is no
network fetch and no auto-refresh. Every snapshot also carries the
`edge_search_hold` note — the dashboard authorizes no new edge-search.

## Determinism

The model carries no clock, no git, and no network. JSON is emitted with sorted
keys; HTML and markdown are deterministic functions of the model. Two renders
over the same checkout are byte-identical (verified by
`tests/test_lab_dashboard.py::test_render_is_deterministic_across_two_builds`).

## CLI

```
python -m tools.lab_dashboard.run --data-json            # data model JSON
python -m tools.lab_dashboard.run --html                 # static HTML
python -m tools.lab_dashboard.run --markdown             # static markdown
python -m tools.lab_dashboard.run --out-dir <dir>        # write all three
```

Committed read-only fixtures live under
`scratch/WP-LAB-RESULTS-DASHBOARD-01/` (`dashboard_data_fixture.json`,
`dashboard_render_fixture.html`, `dashboard_render_fixture.md`).
