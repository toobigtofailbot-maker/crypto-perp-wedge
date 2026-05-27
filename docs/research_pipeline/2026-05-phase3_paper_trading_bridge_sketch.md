# Phase 3 Paper-Trading Bridge Architecture Sketch

## 1. Scope

WP-S2c-91 is the paper-trading bridge surface inside bundled WP-12dy /
WP-S2c-91+92.

This is a Tier 1 documentation-only architecture sketch package. It uses CS12
T1-doc-narrow validation.

This document sketches paper-trading bridge architecture only. It does not
authorize Phase 3 transition, Phase 3 implementation, paper-trading bridge
implementation, runtime modification, paper/live contact, exchange/broker/order
contact, or downstream authority.

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
  `docs/research_pipeline/2026-05-phase3_live_trading_boundary_sketch.md` did
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
- `docs/onboarding/PHASE2_BASELINE.md` locks D2-006 promotion gates, D2-007
  shadow discipline, D2-008 overlay bounds, the Phase 1 paper runtime
  baseline, and protected execution-core boundaries.
- `src/signal/provider.py` defines the current `SignalProvider` protocol.
- `src/runtime/paper_trader.py` and `src/paper/ledger_state.py` record the
  current Phase 1 paper-runtime and paper-ledger behavior for reference only.
- `docs/architecture/event_log_schema.md`,
  `docs/architecture/oms_state_machine.md`,
  `docs/architecture/reconciliation_loop.md`, and
  `docs/architecture/safe_mode_flatten.md` record event-log, OMS,
  reconciliation, and safe-mode truth surfaces.
- `docs/decisions.md` records D-0001 hard risk caps and D2-008 overlay
  semantics.
- Path B, A2C-003, Phase 3 transition, Phase 3 implementation, AUTO bridge
  canonical-write-path work, approval/readiness/lifecycle,
  policy/scoring/ranking/recommendation, runtime, paper/live,
  exchange/broker/order contact, and downstream authority remain unauthorized.

## 3. Locked Paper Runtime Discipline

The Phase 1 paper runtime remains the protected live/shadow execution path.
Phase 2 research uses the lightweight research backtester as the primary
research engine, and D2-007 preserves shadow mode as the sole bridge from the
research backtester to the paper runtime.

Paper runtime, paper ledger accounting, overlay evaluation, OMS truth,
reconciliation truth, kill-switch semantics, safe-mode semantics, D-0001 hard
caps, D2-008 overlay bounds, event-log discipline, and `SignalProvider`
protocol behavior remain locked.

This sketch does not convert paper runtime into a research replay engine, does
not modify the scheduler, does not invoke the paper trader, and does not write
paper ledger, event-log, bridge-output, or canonical evidence files.

## 4. Bridge Architecture Surface

At architecture level only, a future paper-trading bridge surface could connect
a separately promoted candidate from research evidence toward the protected
Phase 1 paper runtime by preserving this flow:

1. Research backtester produces candidate evidence under committed research
   artifacts and locked D2-006 gate discipline.
2. A separate human-gated promotion decision, if later authorized, determines
   whether the candidate is eligible for shadow work.
3. D2-007 shadow deployment represents the candidate through the existing
   `SignalProvider` boundary and logs shadow behavior without acting on it.
4. D2-007 parity observation compares shadow-window behavior to research
   backtester behavior using the locked PnL and trade-count deviation
   thresholds.
5. Only a later separately authorized package could define whether and how
   paper-runtime participation proceeds.

This package selects no implementation shape. It defines no bridge adapter,
no file format, no write path, no invocation path, no candidate-specific
mapping, and no readiness criteria.

## 5. SignalProvider Boundary

Candidate strategy output must be shaped as `SignalProvider`-compatible input
before it can be considered for a future protected paper-runtime path.

The current `SignalProvider` protocol exposes
`compute_desired_position(evaluation_time_utc, inputs)` returning a
`DesiredPosition`. This package does not modify that protocol, does not modify
`build_signal_provider`, does not add a provider, and does not change any
runtime code path.

At architecture level only, a future implementation decision may need to define
how a candidate's research signal, timing, symbol, target quantity or notional,
decision metadata, and source timeframe are normalized before reaching the
locked protocol boundary. That decision remains future work and must preserve
bar-close determinism, no-agent execution boundaries, and protected runtime
semantics.

## 6. Ledger / Overlay / OMS / Reconciliation Boundary

Paper ledger remains accounting truth for the paper runtime. This sketch does
not write ledger entries, does not modify `src/paper/ledger_state.py`, and does
not change paper-ledger math.

D2-008 overlay semantics remain locked. The overlay evaluator remains
protected: BLOCK gates only new entries and risk-increasing deltas,
ALLOW_REDUCED remains `0.5`, reductions remain allowed at full size, and
fail-open behavior is preserved. This sketch authorizes no overlay code change
and no overlay-bound change.

OMS truth remains protected by the locked OMS state machine. Reconciliation
truth remains the deterministic resolution path for exchange/internal
uncertainty. This sketch authorizes no OMS or reconciliation code change, no
state-machine change, no reconcile policy change, and no event-log schema
change.

## 7. Shadow-to-Paper Flow Boundary

The only repo-truth bridge from research backtester toward paper runtime is
D2-007 shadow mode. A future flow must preserve the distinction between:

- research evidence, which remains committed repo evidence only;
- shadow observations, which are non-executing observations unless a later
  package explicitly defines their artifact posture;
- protected paper-runtime behavior, which remains execution-core truth only
  under separately authorized scope;
- human promotion decisions, which remain required before lifecycle or runtime
  transitions.

No sketch output, dashboard output, AUTO bridge output, query view, report, or
agent output can become paper-runtime authority, promotion authority, risk
truth, OMS truth, reconciliation truth, or downstream authority.

## 8. Protected Runtime Boundaries

The paper-trading bridge sketch preserves:

- Phase 1 paper runtime baseline;
- existing `SignalProvider` protocol;
- paper ledger accounting truth;
- D-0001 hard risk caps;
- D2-006 promotion gates;
- D2-007 shadow discipline;
- D2-008 overlay bounds;
- existing event-log schema;
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

## 9. Open Questions

Future implementation decisions may need to answer:

- what minimal adapter shape can transform a candidate's research signal into
  `SignalProvider`-compatible behavior without changing the protocol;
- how to preserve bar timing, funding, fee, slippage, and fill-assumption
  traceability across research, shadow, and paper-runtime-compatible surfaces;
- whether bridge observations need a separately authorized non-canonical or
  canonical artifact family, and what validation would apply;
- how to diagnose paper-runtime mismatch without creating policy, scoring,
  ranking, recommendation, approval, readiness, lifecycle, or promotion
  authority;
- what human review package consumes shadow and paper-bridge observations after
  a separately authorized implementation exists.

No option is selected by this document.

## 10. What Is Not Authorized

This package does not authorize:

- Phase 3 transition;
- Phase 3 implementation;
- paper-trading bridge implementation;
- bridge adapter implementation;
- bridge invocation;
- bridge code changes;
- bridge output files;
- canonical artifacts, trial-log rows, tests, or committed data;
- runtime, paper/live, OMS, reconciliation, risk, safe-mode, kill-switch,
  config, dependency, data, schema, validator, central query-layer,
  event-log schema, `SignalProvider`, or protected-path changes;
- paper ledger writes or paper-ledger code changes;
- overlay evaluator code changes or D2-008 modification;
- exchange, broker, order, live, or Tier 4 contact;
- D2-006 promotion-gate modification;
- D2-007 shadow-mode modification;
- D-0001 risk-cap modification;
- approval/readiness criteria;
- lifecycle, promotion, demotion, or archive action;
- policy, scoring, ranking, recommendation, or evidence-quality scoring;
- Path B;
- A2C-003;
- AUTO bridge canonical-write-path or further bridge work;
- autonomous deployment or downstream authority.

## 11. Next Surface

The paired surface in this bundled package is WP-S2c-92, the Phase 3
live-trading boundary sketch.

After merge, Side may continue to WP-S2c-93, the Phase 3 architecture sketch
tranche checkpoint, from refreshed `main` unless a stop trigger fires.
WP-S2c-93 is T1-doc-major-decision and requires full pytest plus Main
re-engagement after report-back.

## 12. Validation

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
