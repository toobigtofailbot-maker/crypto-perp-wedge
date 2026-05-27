# Phase 3 Live-Trading Boundary Sketch

## 1. Scope

WP-S2c-92 is the live-trading boundary surface inside bundled WP-12dy /
WP-S2c-91+92.

This is a Tier 1 documentation-only architecture sketch package. It uses CS12
T1-doc-narrow validation.

This document sketches the live-trading boundary only. It does not authorize
Phase 3 transition, Phase 3 implementation, live-trading implementation,
real-capital trading, exchange/broker/order contact, runtime modification,
paper/live contact, or downstream authority.

## 2. Repo-Truth Basis

Reference block:

- Refreshed `main` is at `6e62e97`, the PR #273 / WP-12dx merge commit.
- PR #273 / WP-12dx is merged.
- `docs/project_status.md` records WP-12dx / WP-S2c-89+90 as the latest
  branch-state before this package.
- No open PR was found touching `docs/project_status.md` or relevant
  `docs/research_pipeline` architecture files before this package branch was
  created.
- No WP-12dy / WP-S2c-91 / WP-S2c-92 branch or PR was found before this
  package branch was created.
- This document and
  `docs/research_pipeline/2026-05-phase3_paper_trading_bridge_sketch.md` did
  not exist before this package.
- `docs/research_pipeline/2026-05-phase3_architecture_design_opening.md`
  exists and opens the Phase 3 architecture sketch tranche without
  implementation authority.
- `docs/research_pipeline/2026-05-phase3_shadow_deployment_sketch.md` and
  `docs/research_pipeline/2026-05-phase3_monitoring_dashboard_sketch.md` exist
  as the WP-S2c-89 and WP-S2c-90 surfaces.
- `docs/research_pipeline/2026-05-broad_floor_crossing_sufficiency_decision.md`
  exists and records Karl/user's Yes sufficiency decision for Phase 3
  transition gating consideration only.
- `docs/architecture/LONG_TERM_SCOPE.md` records the staged roadmap:
  production execution comes only after shadow evidence, human approval, and
  protected runtime integration; no agent or automation deploys directly to
  live execution.
- `docs/onboarding/PHASE2_BASELINE.md` and `docs/decisions.md` lock D2-006,
  D2-007, D2-008, D-0001, Phase 1 paper runtime boundaries, event-log
  protection, and no-agent execution boundaries.
- `docs/architecture/event_log_schema.md`,
  `docs/architecture/oms_state_machine.md`,
  `docs/architecture/reconciliation_loop.md`, and
  `docs/architecture/safe_mode_flatten.md` record event-log, OMS,
  reconciliation, and safe-mode truth surfaces.
- Path B, A2C-003, Phase 3 transition, Phase 3 implementation, AUTO bridge
  canonical-write-path work, approval/readiness/lifecycle,
  policy/scoring/ranking/recommendation, runtime, paper/live,
  exchange/broker/order contact, live trading with real capital, and
  downstream authority remain unauthorized.

## 3. Phase 3 / Phase 4 Boundary

Phase 3 stops at staged paper-live architecture and paper-runtime architecture.
It does not authorize real-capital live trading.

Live trading with real capital remains Phase 4+ under the locked
`docs/architecture/LONG_TERM_SCOPE.md` staged direction unless later explicitly
changed by Karl/user/Main decision and locked into repo truth.

This sketch does not pre-commit the Phase 4 implementation direction. It only
records the boundary that Phase 3 architecture sketches must not cross.

## 4. Locked Human Gates

Permanent human gates remain locked:

- hypothesis approval;
- decision records and go/no-go decisions;
- shadow promotion;
- live promotion;
- risk parameter changes;
- kill decisions;
- novel strategy-family introduction.

Automation may prepare evidence for these gates only when separately
authorized. It may not approve them. No agent, automation, dashboard, bridge,
monitor, query view, report, or sketch output deploys directly to live
execution or becomes live-promotion authority.

## 5. Live-Trading Prohibitions

For the Phase 3 architecture sketch tranche, the live-trading boundary is:

- no real-capital live trading;
- no exchange, broker, order, live API, or execution contact;
- no autonomous live deployment;
- no candidate-specific live-trading framing;
- no live readiness claim;
- no live promotion criteria;
- no live risk-parameter change;
- no kill-switch, safe-mode, OMS, reconciliation, event-log, overlay, or risk
  cap modification;
- no Tier 4 contact.

Any future live-trading work must be a separately authorized Phase 4+ package
or later explicitly changed staging decision. This document does not authorize
that work.

## 6. Risk / Kill-Switch / Cap Boundaries

D-0001 hard caps remain locked, including risk per trade, daily and weekly
loss limits, peak-to-trough drawdown, turnover, leverage, margin reserve, and
related execution policy caps.

Kill-switch semantics remain protected. Safe-mode semantics remain protected:
safe mode freezes new risk-increasing intents, cancels open orders, flattens
position to zero, verifies open orders and position, and requires operator
reset.

D2-008 overlay bounds remain locked: BLOCK gates only new entries and
risk-increasing deltas, ALLOW_REDUCED remains `0.5`, reductions remain allowed
at full size, and fail-open behavior is preserved.

This sketch defines no risk parameter, no cap value, no kill threshold, no
safe-mode procedure, and no overlay change.

## 7. Protected Runtime Boundaries

The live-trading boundary sketch preserves:

- Phase 1 paper runtime baseline;
- D-0001 hard risk caps;
- D2-006 promotion gates;
- D2-007 shadow discipline;
- D2-008 overlay bounds;
- existing `SignalProvider` protocol;
- existing event-log schema;
- paper ledger accounting truth;
- OMS state-machine truth;
- reconciliation truth;
- kill-switch and safe-mode semantics;
- Tier 4 boundary: no real-capital live trading, no exchange/broker/order
  contact, and no autonomous deployment.

If future safe implementation appears to require runtime, paper/live, OMS,
reconciliation, risk, safe-mode, kill-switch, event-log schema,
`SignalProvider`, config, dependency, data, schema, validator, query-layer,
bridge-code, bridge-output, or protected-path modification, that future package
must stop and return to Main/Karl/user for separate authority.

## 8. Open Questions

Future implementation or Phase 4 boundary decisions may need to answer:

- what additional evidence is required before any Phase 4+ live-trading
  architecture package can be considered;
- what paper-runtime and shadow evidence must be reviewed by humans before any
  live-promotion discussion;
- what operational controls, venue permissions, safe-mode evidence,
  reconciliation evidence, and kill-switch checks would be required for a later
  live package;
- how to represent live-readiness review without creating automated readiness,
  lifecycle, policy, scoring, ranking, recommendation, or downstream authority;
- whether the Phase 4+ staging direction should remain as currently locked or
  be changed by a later explicit Karl/user/Main decision.

No option is selected by this document.

## 9. What Is Not Authorized

This package does not authorize:

- Phase 3 transition;
- Phase 3 implementation;
- Phase 4 implementation;
- live-trading implementation;
- real-capital trading;
- exchange, broker, order, live API, execution, or Tier 4 contact;
- candidate-specific live-trading framing;
- live readiness claims;
- live promotion criteria;
- autonomous live deployment;
- runtime, paper/live, OMS, reconciliation, risk, safe-mode, kill-switch,
  config, dependency, data, schema, validator, central query-layer,
  event-log schema, `SignalProvider`, or protected-path changes;
- paper ledger writes or paper-ledger code changes;
- overlay evaluator code changes or D2-008 modification;
- D2-006 promotion-gate modification;
- D2-007 shadow-mode modification;
- D-0001 risk-cap modification;
- canonical artifacts, trial-log rows, tests, or committed data;
- Path B;
- A2C-003;
- approval/readiness criteria;
- lifecycle, promotion, demotion, or archive action;
- policy, scoring, ranking, recommendation, or evidence-quality scoring;
- AUTO bridge canonical-write-path or further bridge work;
- downstream authority.

## 10. Next Surface

The paired surface in this bundled package is WP-S2c-91, the Phase 3
paper-trading bridge architecture sketch.

After merge, Side may continue to WP-S2c-93, the Phase 3 architecture sketch
tranche checkpoint, from refreshed `main` unless a stop trigger fires.
WP-S2c-93 is T1-doc-major-decision and requires full pytest plus Main
re-engagement after report-back.

## 11. Validation

This package uses CS12 T1-doc-narrow validation because it modifies only
`docs/research_pipeline/` and `docs/project_status.md`, creates architecture
sketch records, and does not create a major decision-boundary checkpoint.

Required validation is execution validation only:

- exact changed-file scope;
- diff/scope summary against the three allowed files;
- research query view listing;
- all discovered `v_integrity_*` views with JSON output returning `[]`;
- registry validators;
- targeted research-query tests for outcome-ledger and reconciliation views.

No full pytest is required unless a stop trigger or validation-profile
ambiguity fires.
