# WP-STRAT-CAP-01 — Strategy-lab capability delta map

- Package class: T1 docs/design/roadmap
- Branch: `docs/strat-cap-01-capability-delta-map`
- PR: not opened at initial draft; final PR URL will replace this line before ready-for-review
- Scope summary: Created a design-only strategy-lab capability delta map and
  Main 4 runway closeout inventory. The map reconciles Main 4 post-F5
  authorization against current repo truth, classifies F5D, inventories current
  capabilities and gaps, dispositions the named tracks, and prepares a concise
  Main 5 activation decision menu.
- Main 4 authorization basis: Main 4 authorized F5B -> F5C -> F5D if needed,
  then a report-back checkpoint, and set `WP-STRAT-CAP-01` as the first
  post-F5 design-only lane before choosing FLOW / indicator / OI / simulator
  ordering.
- Changed files:
  - `docs/research_pipeline/2026-06-strategy_lab_capability_delta_map.md`
  - `docs/status_entries/WP-STRAT-CAP-01.md`
  - `docs/project_status.md`
- F5 runway closeout: F5A, GUIDE-EFF-05, F5B, F5C, and
  GUIDE-CLAUDE-ALIGN-01 are classified complete / merged. F5D is classified
  conditional-not-needed because no F5C blocker, generated-output drift, or
  authority drift was found in current repo truth.
- Capability-map summary: Current repo truth includes Strategy Spec, indicator
  catalog, variant manifest, sweep plan, offline runner, result population,
  D4A/D5 real-data provenance, robustness-report, static Results dashboard, data
  ingestion/validation/catalog, operator-surface design, and paper-sandbox
  design surfaces. Missing or incomplete surfaces include expanded
  compiler/catalog capability, WFO protocol, FLOW/OI/trade/L2 feasibility,
  simulator realism, and protected paper/live implementation.
- Track-disposition summary: STRAT-CAP is delivered by this package;
  DASHBOARD-REVIEW is partially built through F5 and E2; INDICATOR/CATALOG is
  partially built; STRAT-BRIEF is partially absorbed by lab/D6 docs but still a
  Main 5 decision candidate; PERP-FEATURES, CALENDAR, WFO, FLOW-FEAS, OI-DATA,
  TRADE/L2-DATA, SIMULATOR, and PROTECTED-PAPER/LIVE remain design-only,
  not-started, Main-decision-required, Karl-gated, or forbidden as classified in
  the map.
- Validation summary: Not yet final at initial draft; final command results
  will replace this line before ready-for-review.
- Boundary summary: Docs/design only. No Strategy Spec, candidate, variant
  manifest, sweep plan, result population, data artifact, schema, validator,
  tool, code, test, dashboard implementation, generated output, runtime,
  paper/live, OMS, risk, broker/exchange, order path, protected path, ranking,
  recommendation, readiness, promotion, or execution authority is changed.
- Merge status: Not yet final at initial draft.
- Main 5 activation note: Main 5 should treat this map as a decision surface:
  F5 is closed through F5C, F5D is conditional-not-needed, current repo truth is
  materially beyond the older F5-only onboarding, and the next choice is which
  narrow design or implementation package to authorize next while keeping data
  acquisition, simulator implementation, and protected paper/live work gated.

## Active-WP Requirement Traceability

| Requirement | Evidence | Status |
|---|---|---|
| STRAT-CAP doc created | `docs/research_pipeline/2026-06-strategy_lab_capability_delta_map.md` | satisfied |
| Status fragment created | `docs/status_entries/WP-STRAT-CAP-01.md` | satisfied |
| Project-status pointer added | `docs/project_status.md` | satisfied |
| F5 runway closeout included | STRAT-CAP doc section `F5 Runway Closeout` | satisfied |
| F5D classified | STRAT-CAP doc section `F5 Runway Closeout` | satisfied |
| Main 4 tracks dispositioned | STRAT-CAP doc section `Main 4 Adopted Track Disposition` | satisfied |
| Current capability inventory included | STRAT-CAP doc section `Current Capability Inventory` | satisfied |
| Karl-gated surfaces preserved | STRAT-CAP doc track table and non-authority sections | satisfied |
| Strategy research remains planning input only | STRAT-CAP doc section `Strategy-Research Input Status` | satisfied |
| Main 5 activation note included | STRAT-CAP doc section `Main 5 Activation Note`; this status fragment | satisfied |
| Required validation run | Validation summary in this status fragment | not final at initial draft |
| PR body/status finality clean | Final PR readiness gate | not final at initial draft |
| No forbidden paths touched | Diff scope validation | not final at initial draft |
