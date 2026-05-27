# Phase 3 Shadow Deployment Architecture Sketch

## 1. Scope

WP-S2c-89 is the shadow deployment surface inside bundled WP-12dx /
WP-S2c-89+90.

This is a Tier 1 documentation-only architecture sketch package. It uses CS12
T1-doc-narrow validation.

This document sketches shadow deployment architecture only. It does not
authorize Phase 3 transition, Phase 3 implementation, shadow adapter
implementation, parity tooling implementation, runtime modification, paper/live
contact, exchange/broker/order contact, or downstream authority.

## 2. Repo-Truth Basis

Reference block:

- Refreshed `main` is at `95dded6`, the PR #272 / WP-12dw merge commit.
- PR #272 / WP-12dw is merged.
- `docs/project_status.md` records WP-12dw / WP-S2c-88 as the latest
  branch-state before this package.
- No open PR was found touching `docs/project_status.md` or relevant
  `docs/research_pipeline` architecture files before this package branch was
  created.
- No WP-12dx / WP-S2c-89 / WP-S2c-90 branch or PR was found before this
  package branch was created.
- This document and
  `docs/research_pipeline/2026-05-phase3_monitoring_dashboard_sketch.md` did
  not exist before this package.
- `docs/research_pipeline/2026-05-phase3_architecture_design_opening.md`
  exists and opens the Phase 3 architecture sketch tranche without
  implementation authority.
- `docs/research_pipeline/2026-05-broad_floor_crossing_sufficiency_decision.md`
  exists and records Karl/user's Yes sufficiency decision for Phase 3
  transition gating consideration only.
- `docs/onboarding/PHASE2_BASELINE.md` locks D2-006 promotion gates, D2-007
  shadow discipline, D2-008 overlay bounds, the Phase 1 paper runtime
  baseline, and protected execution-core boundaries.
- `src/signal/provider.py` defines the current `SignalProvider` protocol.
- `docs/architecture/event_log_schema.md` records the existing event-log
  discipline.
- `docs/decisions.md` records D-0001 hard risk caps.
- Path B, A2C-003, Phase 3 transition, Phase 3 implementation, AUTO bridge
  canonical-write-path work, approval/readiness/lifecycle,
  policy/scoring/ranking/recommendation, runtime, paper/live,
  exchange/broker/order contact, and downstream authority remain unauthorized.

## 3. Locked Shadow Discipline

D2-007 is the locked shadow discipline: shadow mode is the sole bridge from the
research backtester to the paper runtime.

Repo truth locks the shadow window as at least 14 calendar days. During that
window, a promoted research candidate is represented through the existing
`SignalProvider` boundary and plugged into the Phase 1 paper runtime in shadow
mode, where signals are generated and logged but not acted upon.

The same D2-007 decision locks the parity check boundary: replay the same bars
through the research backtester during the shadow window and require PnL
deviation <= 10% and trade count deviation <= 5%.

This sketch does not change those thresholds, the shadow window, or the
promotion gates.

## 4. Shadow Architecture Surface

The architecture-level shadow deployment surface is:

- consume candidate signals through the locked `SignalProvider` protocol;
- compare research/backtest intent to paper-runtime-compatible behavior;
- preserve the Phase 1 paper runtime as the live/shadow execution path;
- preserve paper ledger accounting, overlay evaluation, OMS truth,
  reconciliation truth, kill-switch and safe-mode semantics, D-0001 hard caps,
  D2-008 overlay bounds, and event-log discipline;
- log or expose observations only through later separately authorized surfaces.

This surface is observational. It does not modify `SignalProvider`, does not
write canonical evidence, does not create REP/OL/REC/EXP/LCH artifacts, does
not append `research/trial_log.jsonl`, and does not contact exchange, broker,
order, paper-live, or live systems.

## 5. Parity Check Boundary

Parity checks remain an architecture boundary, not an implementation in this
package.

The future parity surface may compare:

- research backtester PnL versus shadow-window paper-runtime-compatible PnL;
- research backtester trade count versus shadow-window paper-runtime-compatible
  trade count;
- event timing and signal intent sufficiently to diagnose mismatch sources.

Locked D2-007 thresholds are:

- PnL deviation <= 10%;
- trade count deviation <= 5%.

Parity checks are observational inputs. They are not promotion authority by
themselves and cannot override D2-006, human gates, D-0001, OMS truth,
reconciliation truth, or protected runtime boundaries.

No parity tooling implementation is authorized here.

## 6. Promotion Gate Boundary

D2-006 remains the locked per-candidate research-to-shadow gate set:

- OOS Sharpe >= 1.0 net of modeled costs;
- DSR > 1.0 at 95% confidence given actual trial count;
- max drawdown <= 20% in any walk-forward fold;
- parameter sensitivity at +/-25% keeps Sharpe within 70% of baseline;
- cost drag <= 50% of gross PnL;
- no single 90-day window contributes more than 60% of total PnL;
- <= 5 free parameters;
- walk-forward efficiency greater than 0.5.

Shadow and parity evidence can only support a later separately authorized
human-gated promotion review. They do not define approval/readiness criteria,
do not modify D2-006 thresholds, and do not create lifecycle, promotion,
demotion, archive, or downstream authority.

## 7. Protected Runtime Boundaries

The shadow deployment sketch preserves:

- Phase 1 paper runtime baseline;
- D-0001 hard risk caps;
- D2-008 overlay bounds, including BLOCK gating only new entries and
  risk-increasing deltas while reductions remain allowed at full size;
- existing `SignalProvider` protocol;
- existing event-log schema;
- OMS state-machine truth;
- reconciliation truth;
- kill-switch and safe-mode semantics;
- Tier 4 boundary: no real-capital live trading, no exchange/broker/order
  contact, and no autonomous deployment.

If future safe implementation appears to require runtime, OMS, reconciliation,
risk, safe-mode, event-log schema, `SignalProvider`, config, dependency, data,
schema, validator, query-layer, bridge-code, bridge-output, or protected-path
modification, that future package must stop and return to Main/Karl/user for
separate authority.

## 8. Open Questions

Future implementation decisions may need to answer:

- what minimal shadow adapter shape can consume a candidate through
  `SignalProvider` without changing the protocol;
- what observation format records shadow parity without becoming canonical
  evidence;
- how to align bar timing, funding, slippage, fees, and fill assumptions across
  research and paper-runtime-compatible observation;
- how to diagnose parity failures without creating policy, scoring, ranking,
  recommendation, or promotion authority;
- what human review package consumes shadow and parity observations after a
  separately authorized implementation exists.

No option is selected by this document.

## 9. What Is Not Authorized

This package does not authorize:

- Phase 3 transition;
- Phase 3 implementation;
- shadow adapter implementation;
- parity tooling implementation;
- paper/live runtime modification;
- runtime, OMS, reconciliation, risk, safe-mode, kill-switch, config,
  dependency, data, schema, validator, central query-layer, bridge-code,
  bridge-output, or protected-path changes;
- exchange, broker, order, live, or Tier 4 contact;
- event-log schema modification;
- `SignalProvider` protocol modification;
- D2-006 promotion-gate modification;
- D2-007 shadow-mode modification;
- D-0001 risk-cap modification;
- D2-008 overlay-bound modification;
- canonical artifacts, trial-log rows, tests, or committed data;
- Path B;
- A2C-003;
- approval/readiness criteria;
- lifecycle, promotion, demotion, or archive action;
- policy, scoring, ranking, recommendation, or evidence-quality scoring;
- AUTO bridge canonical-write-path or further bridge work;
- autonomous deployment or downstream authority.

## 10. Next Surface

The paired surface in this bundled package is WP-S2c-90, the Phase 3
monitoring and dashboard architecture sketch.

After merge, Side may continue to WP-S2c-91+92 bundled paper-trading bridge and
live-trading boundary sketches from refreshed `main`, unless a stop trigger
fires.

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
