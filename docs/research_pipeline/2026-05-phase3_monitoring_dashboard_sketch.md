# Phase 3 Monitoring and Dashboard Architecture Sketch

## 1. Scope

WP-S2c-90 is the monitoring and dashboard surface inside bundled WP-12dx /
WP-S2c-89+90.

This is a Tier 1 documentation-only architecture sketch package. It uses CS12
T1-doc-narrow validation.

This document sketches monitoring and dashboard architecture only. It does not
authorize implementation, dashboard construction, monitoring code, scheduler or
agent activation, runtime integration, Phase 3 transition, Phase 3
implementation, or downstream authority.

## 2. Repo-Truth Basis

Reference block:

- Refreshed `main` is at `95dded6`, the PR #272 / WP-12dw merge commit.
- PR #272 / WP-12dw is merged.
- `docs/project_status.md` records WP-12dw / WP-S2c-88 as the latest
  branch-state before this package.
- `docs/research_pipeline/2026-05-phase3_architecture_design_opening.md`
  exists and opens the Phase 3 architecture sketch tranche without
  implementation authority.
- `docs/research_pipeline/2026-05-broad_floor_crossing_sufficiency_decision.md`
  exists and records Karl/user's Yes sufficiency decision for Phase 3
  transition gating consideration only.
- `docs/architecture/LONG_TERM_SCOPE.md` locks the dashboard / visibility
  direction: visibility derives from repo truth, and dashboards must not create
  separate shadow truth outside the repo.
- `docs/onboarding/PHASE2_BASELINE.md` locks D2-006, D2-007, D2-008, Phase 1
  paper runtime boundaries, event-log protection, D-0001 hard-cap protection,
  and no-agent execution boundaries.
- `docs/architecture/event_log_schema.md` records the current event-log
  contract.
- `docs/architecture/oms_state_machine.md`,
  `docs/architecture/reconciliation_loop.md`, and
  `docs/architecture/safe_mode_flatten.md` record OMS, reconciliation, and
  safe-mode monitoring truth surfaces.
- Path B, A2C-003, Phase 3 transition, Phase 3 implementation, AUTO bridge
  canonical-write-path work, approval/readiness/lifecycle,
  policy/scoring/ranking/recommendation, runtime, paper/live,
  exchange/broker/order contact, and downstream authority remain unauthorized.

## 3. Locked Dashboard Discipline

Dashboard and visibility surfaces derive from repo truth and runtime truth.
They do not become independent truth sources.

`docs/architecture/LONG_TERM_SCOPE.md` states that a later dashboard may read
repo artifacts, JSON outputs, and generated reports, but it must not create a
separate shadow truth outside the repo. If dashboard output disagrees with repo
artifacts, repo artifacts win until the discrepancy is investigated and
corrected.

This sketch preserves that discipline for Phase 3 monitoring. Dashboard output
is observational only. It cannot create approval, promotion, lifecycle, risk,
execution, or downstream authority.

## 4. Monitoring Architecture Surface

The architecture-level monitoring surface may observe:

- D-0001 risk-cap state and breaches;
- kill-switch state and trigger evidence;
- reconciliation truth, including reconcile start, diff, action, done, fail,
  and unresolved-drift visibility;
- OMS state visibility, including state transitions, working-order state, fill
  state, frozen state, and safe-flatten state;
- overlay decision visibility, including ALLOW, ALLOW_REDUCED(0.5), BLOCK,
  fail-open posture, and D2-008 risk-increasing versus risk-reducing deltas;
- shadow parity visibility, including D2-007 PnL deviation, trade count
  deviation, shadow-window coverage, and mismatch diagnostics.

This surface is read-only and observational. It does not prescribe actions,
schedule jobs, create alerting automation, modify thresholds, write event-log
schema changes, or integrate with runtime paths.

## 5. Dashboard Visibility Surface

The architecture-level dashboard surface may summarize:

- current repo artifact status and branch-state context;
- candidate evidence and gate posture from committed repo artifacts;
- shadow-window status and parity observations after a separately authorized
  implementation exists;
- runtime truth snapshots from separately authorized runtime outputs;
- OMS, reconciliation, safe-mode, kill-switch, D-0001, overlay, and shadow
  visibility as derived views;
- discrepancies between dashboard output and repo/runtime truth for human
  investigation.

The dashboard is a reader and presentation layer only. It does not own truth,
does not write canonical evidence, does not promote candidates, does not change
risk or execution behavior, and does not outrank repo artifacts, runtime truth,
OMS truth, reconciliation truth, or human gates.

## 6. Truth-Source Boundaries

Truth-source order for this sketch:

- committed repo artifacts and locked repo docs are repo truth;
- runtime truth remains in the protected runtime, OMS, reconciliation, event
  log, and safe-mode surfaces when separately authorized runtime observation
  exists;
- dashboard output is derived presentation only;
- if dashboard output disagrees with repo artifacts, repo artifacts win;
- if dashboard output disagrees with runtime/reconciliation truth, protected
  runtime/reconciliation truth wins;
- discrepancies are investigation inputs, not autonomous action triggers.

No dashboard or monitor output may become approval authority, readiness
authority, lifecycle authority, risk truth, execution truth, OMS truth,
reconciliation truth, policy/scoring/ranking/recommendation input, or
downstream authority without a later explicit package.

## 7. Protected Runtime Boundaries

The monitoring and dashboard sketch preserves:

- Phase 1 paper runtime baseline;
- D-0001 hard risk caps;
- D2-006 promotion gates;
- D2-007 shadow discipline;
- D2-008 overlay bounds;
- existing event-log schema;
- existing `SignalProvider` protocol;
- OMS state-machine truth;
- reconciliation truth;
- kill-switch and safe-mode semantics;
- Tier 4 boundary: no real-capital live trading, no exchange/broker/order
  contact, and no autonomous deployment.

No scheduler, agent, autonomous action, alerting automation, dashboard
implementation, monitoring implementation, runtime integration, event-log
schema change, or protected-path change is authorized by this document.

## 8. Open Questions

Future implementation decisions may need to answer:

- which read-only repo/query/runtime surfaces are safe for a dashboard to read;
- how to represent dashboard disagreement with repo or runtime truth without
  creating alternate authority;
- which event-log fields are sufficient for monitoring without schema changes;
- how to display D-0001, kill-switch, reconciliation, OMS, overlay, and shadow
  parity status without selecting actions;
- what human review path should consume dashboard-discovered discrepancies;
- whether any future alerting surface is needed, and how it remains
  non-executing and human-gated.

No option is selected by this document.

## 9. What Is Not Authorized

This package does not authorize:

- Phase 3 transition;
- Phase 3 implementation;
- monitoring code implementation;
- dashboard implementation;
- scheduler, daemon, queue, watcher, trigger, agent, or autonomous alerting
  automation;
- runtime integration;
- runtime, OMS, reconciliation, risk, safe-mode, kill-switch, config,
  dependency, data, schema, validator, central query-layer, bridge-code,
  bridge-output, event-log schema, or protected-path changes;
- exchange, broker, order, live, or Tier 4 contact;
- dashboard output as truth over repo artifacts, runtime truth, OMS truth, or
  reconciliation truth;
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
- downstream authority.

## 10. Next Surface

The paired surface in this bundled package is WP-S2c-89, the Phase 3 shadow
deployment architecture sketch.

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
