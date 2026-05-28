# Phase 3 Shadow Adapter Authorization Scope Sketch

## 1. Scope

WP-S2c-102 is one surface inside bundled WP-12ei / WP-S2c-102+103.

This is a Tier 1 documentation-only authorization-scope sketch.

It sketches shadow adapter and parity tooling authorization scope only. It does not authorize implementation.

Authorization decisions are deferred to WP-S2c-104 after Main/Karl resolution.

## 2. Repo-truth basis

WP-12eh / WP-S2c-101 is merged and opened the Phase 3 implementation authorization decision tranche.

WP-12eg / WP-S2c-100 locked approval/readiness criteria in repo truth.

WP-S2c-89 sketched shadow deployment and shadow adapter/parity boundaries.

D2-007 shadow discipline remains locked. The SignalProvider Protocol boundary remains locked. Phase 1 paper runtime protection remains locked.

Phase 3 implementation, runtime/protected-path work, Tier 4 contact, candidate readiness determination, and transition authorization remain unauthorized.

## 3. Locked criteria basis

This sketch references the WP-S2c-100 locked criteria without modifying them.

S2P-1 preserves the D2-007 minimum shadow window of at least 14 calendar days.

S2P-2 preserves D2-007 parity thresholds: PnL deviation no more than 10% and trade-count deviation no more than 5%.

S2P-3 requires refined shadow-window completion evidence, including window completion, parity evidence, lineage, interruption or invalid-observation disclosure, and retention/reference sufficient for human review.

S2P-4 keeps parity as decision-support only. Passing parity cannot automatically authorize paper transition.

S2P-5 keeps mismatch diagnostics as decision-support only. They cannot become ranking, scoring, recommendation, or automated transition logic.

S2P-7 keeps paper runtime protection non-negotiable and does not authorize paper-runtime implementation, paper bridge implementation, paper bridge invocation, or paper/live contact.

The HG and DR criteria preserve human gates and reject agentic execution, automated transition authority, dashboard/report/score/validator/bridge/automation authority, and any conversion of permanent human gates into advisory-only steps.

## 4. Architecture sketch basis

WP-S2c-89 is the sketch source for shadow deployment, shadow adapter, and parity boundaries.

It sketched observational shadow deployment around the locked SignalProvider protocol, D2-007 shadow discipline, D2-006 promotion gates, D2-007 parity thresholds, Phase 1 paper runtime protection, OMS, reconciliation, risk, safe mode, kill switch, and Tier 4 boundaries.

WP-S2c-89 did not authorize implementation.

## 5. Candidate authorization surfaces

These surfaces are candidates for later authorization review, not authorized work:

- shadow adapter shape needed to observe candidate signals without touching paper/live execution;
- parity observation/checking surface needed to compare shadow behavior under D2-007 discipline;
- evidence/reporting surfaces needed for later human review.

Explicit non-surfaces:

- paper runtime changes;
- live trading;
- Tier 4 contact;
- exchange, broker, order, live API, paper/live, or execution contact;
- runtime/protected-path changes.

## 6. Shadow adapter authorization-scope sketch

A later authorization decision could consider a shadow adapter boundary around SignalProvider-compatible signal observation.

Any such later scope would need to preserve read-only or non-executing shadow behavior. It would need to create no order generation and no broker, exchange, order, live API, paper/live, or Tier 4 contact.

Any later scope would need to preserve no paper/live runtime mutation, no candidate readiness declaration, no automatic promotion, and no transition authority.

Any later implementation package, if separately authorized, would need to preserve D2-007 and the WP-S2c-100 locked criteria.

This package does not select a final design.

## 7. Parity tooling authorization-scope sketch

A later authorization decision could consider tooling that measures D2-007 shadow-window and parity evidence.

The candidate observation surface could include PnL deviation and trade-count deviation observations under locked D2-007 thresholds.

The candidate disclosure surface could support interruption, invalid observation, missing data, or observation reset disclosure.

Mismatch diagnostics may support human review only. They cannot become ranking, scoring, recommendation, policy, readiness, or automated paper-transition authority.

This package does not implement parity tooling and does not select a final design.

## 8. Artifact-family posture

This package does not create canonical artifacts, schema, directories, validators, query-layer changes, or output files.

Possible future artifact families may need separate authorization.

The deferred packaging points from WP-S2c-100 remain deferred outside this package:

- approval-record artifact location/schema for research-to-shadow;
- shadow-evidence retention location/artifact grammar;
- approval-record artifact location/schema for shadow-to-paper.

## 9. Protected runtime and Tier 4 boundaries

This sketch preserves paper runtime, paper/live, OMS, reconciliation, risk, safe-mode, kill-switch, event-log schema, SignalProvider, config, dependency, data, bridge code/output, and Tier 4 boundaries.

It does not authorize runtime/protected-path work, exchange/broker/order contact, live API contact, paper/live contact, real-capital trading, or any protected execution-core modification.

## 10. Open authorization questions for WP-S2c-104

Karl must later resolve:

- Is any shadow adapter implementation scope authorized?
- Is any parity tooling implementation scope authorized?
- What is deferred?
- What remains explicitly unauthorized?
- Which evidence/artifact surfaces require later schema/artifact packages?
- What preservation notes must bind any later implementation package?

## 11. What is not authorized

This package does not authorize:

- shadow adapter implementation;
- parity tooling implementation;
- implementation code;
- canonical artifacts;
- runtime/protected-path work;
- research-to-shadow, shadow-to-paper, paper-to-live, or live transition authorization;
- candidate readiness determination;
- paper/live or Tier 4 contact;
- exchange, broker, order, live API, or execution contact;
- scoring, ranking, recommendation, policy, approval, readiness, lifecycle, or promotion authority;
- AUTO bridge further work;
- A2C-003;
- Path B;
- downstream authority.

## 12. Validation / next surface

Validation profile: CS12 T1-doc-narrow.

This surface is paired with the monitoring/dashboard + paper bridge scope sketch in WP-S2c-103.

After WP-S2c-102+103 merge, Side must report back to Main/Karl/user for WP-S2c-104 authorization-scope resolution.
