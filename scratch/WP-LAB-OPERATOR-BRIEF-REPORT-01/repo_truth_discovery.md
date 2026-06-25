# WP-LAB-OPERATOR-BRIEF-REPORT-01 — Repo-truth discovery

## Question

Where does an operator-readable **daily brief** / **weekly report** belong, and
what existing repo truth must it consume rather than re-derive?

## Search

```
Select-String -Path docs\**\*.md,tools\**\*.py,tests\**\*.py,reports\**\*,scratch\**\*.json \
  -Pattern "daily brief|weekly report|report generator|quarto|markdown report|lab_state|operator report|research report|summary"
```

Plus direct inspection of `tools/lab_state/**`, `tools/lab_dashboard/**`, the
existing research-query views, and the F-series `tools/dashboard` surface.

## Findings

### 1. The coordinator state model is the single source of state truth

`tools/lab_state/` (merged, PR #568) defines the canonical read-only state
vocabulary (`model.py`), a read-only resolver (`resolver.py`,
`build_snapshot`), and a CLI binding two committed subjects
(`run.py::SUBJECTS`). It invents no new state names and executes no transition.
Its `NON_AUTHORITY_DECLARATION` and `EDGE_SEARCH_HOLD_NOTE` are the boundary
constants every downstream surface must inherit.

### 2. The results dashboard is the closest precedent

`tools/lab_dashboard/` (merged, PR #569) is a deterministic read-only
projection over `build_snapshot` plus the same committed display artifacts. It:

- takes per-stage / overall **state verbatim** from the resolver (no
  re-derivation, no new vocabulary);
- projects display facts (denominator breakdown, Result Populations, withheld
  statistics, evidence class, NO-GO caveats, artifact drill-down);
- aggregates a **full-population** denominator summary (`by_overall_state` with
  every state including zero buckets) — never winners only;
- carries an extended `non_authority_declaration` (no run/approve/promote/retry
  buttons, no scheduler toggle, no live fetch, no auto-refresh);
- is **byte-deterministic**: no clock, no git, no network; JSON emitted with
  sorted keys.

`build_dashboard_data()` already exposes exactly the categories a brief/report
needs (completed runs, blocked, NO-GO, candidate-ready, validation/OOS status,
withheld stats, caveats, artifact links). The reporting surface should
**consume the dashboard data model** rather than re-reading artifacts, so there
is one projection of repo truth and no second state derivation.

### 3. The F-series `tools/dashboard` surface is a different contract

`tools/dashboard` (`dashboard_data.v1`) is intentionally **non-deterministic**
(`generated_at_utc`, git subprocess) and is built from `tools/lab_registry`,
not the coordinator state model. It is the wrong base for a deterministic
brief/report. (Same rationale the results dashboard recorded.)

### 4. No existing daily-brief / weekly-report generator

The search found `*_summary.json` research artifacts and synthesis docs, but no
operator brief/report generator. This package creates the first one.

## Decision

Create a new focused module `tools/lab_reporting/` that:

- consumes `tools.lab_dashboard.data_model.build_dashboard_data` (which itself
  consumes `tools.lab_state`), so **state is never re-derived** and **no new
  state vocabulary** is introduced;
- shapes the projection into an operator **daily brief** and **weekly report**
  (completed runs, blocked runs, NO-GOs, open decision surfaces, validation
  status, artifact links, withheld stats + caveats, candidate-review readiness
  only when evidence exists);
- is **descriptive only** — no recommendations, no ranking-as-authority, no
  promotion labels, no auto-send, no notification firing, no scheduler;
- carries an extended `non_authority_declaration` adding the reporting-specific
  guarantees (`emits_recommendations: false`, `auto_sends: false`,
  `fires_notifications: false`, `integrates_scheduler: false`,
  `applies_decision_labels: false`, `suggests_edge_search: false`);
- is **deterministic**: it reads no clock. The brief/report `as_of` and period
  labels are explicit descriptive strings supplied by the caller (default
  `"unspecified"`), so two runs over the same checkout and the same labels are
  byte-identical.

### Charting

The weekly report is **table-based static output only**. The repo has no
committed safe static-chart generation path that is dependency-light for this
surface, so per package §5 charting is recorded as **deferred** rather than
adding a dependency. Counts are shown as text tables.
