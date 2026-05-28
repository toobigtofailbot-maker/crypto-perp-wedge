# Shadow-to-Paper Readiness Criteria Sketch

## 1. Scope

WP-S2c-96 is one surface inside bundled WP-12eb / WP-S2c-95+96.

This is a Tier 1 documentation-only surface. It sketches shadow-to-paper
readiness criteria only.

Criteria are sketched, not locked. Criteria locking requires later separate
Karl approval.

This document creates no shadow-to-paper transition, implementation, paper
runtime contact, approval/readiness, lifecycle, runtime, paper/live, or
downstream authority.

## 2. Repo-truth basis

WP-12ea / WP-S2c-94 is merged and opened the approval/readiness criteria
design surface.

WP-S2c-95 in this bundle sketches research-to-shadow readiness criteria.

D2-007 shadow discipline remains locked.

Phase 1 paper runtime remains protected.

No shadow-to-paper transition, implementation, paper runtime contact,
approval/readiness/lifecycle, runtime, paper/live, or downstream authority
exists.

## 3. Locked inputs

This sketch references, without modifying, these locked or protected inputs:

- D2-007 minimum shadow window of at least 14 calendar days.
- D2-007 parity thresholds requiring PnL deviation no more than 10% and trade
  count deviation no more than 5% during the shadow window.
- The `SignalProvider` boundary as read-only reference context.
- Phase 1 paper runtime protection.
- Permanent human gates from `docs/architecture/LONG_TERM_SCOPE.md`.
- D-0001 hard caps.
- D2-008 overlay bounds.
- OMS, reconciliation, and safe-mode truth surfaces as boundary context only.

These inputs constrain later criteria design. This sketch does not restate
them as final governing criteria and does not alter their semantics.

## 4. Shadow-to-paper readiness criteria surface

Later criteria-locking work may need to decide how shadow-window completion is
represented for readiness review, including whether the locked criterion
requires completed calendar coverage, clean lineage to shadow evidence, and
explicit disclosure of any interruption or invalid shadow observation.

Later criteria-locking work may need to decide how D2-007 parity results
inform readiness review. Parity pass evidence may be decision-support evidence
only; this sketch does not make it automatic transition authority.

Mismatch diagnostics may be useful as decision-support evidence. They cannot
become ranking, scoring, recommendation, or automated paper-transition logic
inside this package.

Any shadow-to-paper transition would require human approval before paper
transition. This sketch does not define, select, or approve that decision
record.

Paper-runtime protection is a non-negotiable implementation boundary. Later
criteria may need to say what evidence is reviewed before any separately
authorized paper-runtime package, but this sketch does not authorize that
package.

A later criteria-locking package may be required before any criteria become
governing gates.

## 5. D2-007 parity and shadow-window boundary

D2-007 thresholds are not modified.

Parity results may inform later human review but cannot automatically
authorize paper transition.

No parity tooling is implemented or authorized by this package.

## 6. Paper runtime protection boundary

This document does not touch paper runtime, paper/live, OMS, reconciliation,
ledger, overlay, risk, safe-mode, kill-switch, event-log schema,
`SignalProvider`, configs, dependencies, data, or protected paths.

No paper bridge implementation or invocation is authorized.

## 7. Human-gate boundary

Readiness criteria may inform human review but cannot replace human approval.

No automated transition or promotion authority is created.

Permanent human gates remain human-controlled, including hypothesis approval,
decision records and go/no-go decisions, shadow promotion, live promotion, risk
parameter changes, kill decisions, and novel strategy-family introduction.

## 8. Open criteria-locking questions

- How should shadow-window completion be represented in locked criteria?
- What evidence should be required when parity passes?
- What evidence or mismatch should block paper-readiness consideration?
- What human approval record must exist before paper transition?
- What must Karl lock later before criteria become governing gates?

## 9. What is not authorized

This sketch does not authorize:

- criteria locking;
- candidate readiness determination;
- shadow-to-paper transition;
- paper-to-live or live transition;
- parity tooling implementation;
- monitoring or dashboard implementation;
- paper bridge implementation;
- runtime, paper/live, or protected-path changes;
- D2-007 modification;
- `SignalProvider` or event-log schema modification;
- policy, scoring, ranking, or recommendation;
- AUTO bridge further work;
- A2C-003 or Path B work;
- lifecycle action;
- downstream authority.

## 10. Validation / next surface

Validation profile: CS12 T1-doc-narrow.

WP-S2c-97 remains the later standalone permanent human gate preservation
sketch.

Criteria locking remains deferred to a later Karl-approved decision package.
