# Research-to-Shadow Readiness Criteria Sketch

## 1. Scope

WP-S2c-95 is one surface inside bundled WP-12eb / WP-S2c-95+96.

This is a Tier 1 documentation-only surface. It sketches
research-to-shadow readiness criteria only.

Criteria are sketched, not locked. Criteria locking requires later separate
Karl approval.

This document creates no transition, implementation, approval/readiness,
lifecycle, policy, scoring, ranking, recommendation, runtime, paper/live, or
downstream authority.

## 2. Repo-truth basis

WP-12ea / WP-S2c-94 is merged and opened the approval/readiness criteria
design surface.

WP-S2c-93 closed the Phase 3 architecture sketch tranche.

D2-006, D2-007, REC-5, Phase 9 Decision 9 - Tiered Promotion Evidence Policy,
and permanent human gates remain locked. Phase 9 Decision 6 - Human Approval
Semantics remains locked as the human-only approval surface.

No transition, implementation, approval/readiness/lifecycle,
policy/scoring/ranking/recommendation, runtime, paper/live, or downstream
authority exists.

## 3. Locked inputs

This sketch references, without modifying, these locked or protected inputs:

- D2-006 promotion gates.
- D2-007 shadow as the sole bridge from research backtester to paper runtime.
- REC-5 exact-segment floor discipline.
- Phase 9 Decision 9 - Tiered Promotion Evidence Policy.
- Phase 9 Decision 6 - Human Approval Semantics.
- Permanent human gates from `docs/architecture/LONG_TERM_SCOPE.md`.
- Broad-floor-crossing sufficiency Yes as a gating-input decision only.

These inputs constrain later criteria design. This sketch does not restate
them as final governing criteria and does not alter their semantics.

## 4. Research-to-shadow readiness criteria surface

Later criteria-locking work may need to decide how research-to-shadow
readiness should relate to D2-006 gates. Open design questions include
whether locked criteria should require direct D2-006 pass evidence, explicit
documentation of each gate, or a narrower reference to the existing D2-006
source of truth.

Later criteria-locking work may need to decide how REC-5 evidence is presented
for readiness review. The possible surface is exact-segment evidence under
`candidate_id / outcome_kind / pipeline_version / expectation_source_type`,
not pooled candidate evidence and not cross-segment aggregation.

Broad-floor-crossing evidence may be descriptive input to a readiness review.
It is not automatic approval, not candidate-specific readiness, and not a
substitute for a later human decision.

Candidate-level readiness remains unresolved. A later package may need to
define how exact-segment evidence, D2-006 evidence, qualitative review, and
human approval combine without violating REC-5 floor discipline.

Any research-to-shadow transition would require a human approval decision
before transition. This sketch does not define, select, or approve that
decision record.

A later criteria-locking package may be required before any criteria become
governing gates.

## 5. REC-5 and candidate-level readiness boundary

REC-5 is exact-segment discipline. REC consumers must use a floor of at least
3 reconciliations per `candidate_id / outcome_kind / pipeline_version /
expectation_source_type` before drawing segment-level inference.

No cross-segment inference under the REC-5 floor is allowed.

This document cannot transform per-segment evidence into candidate-level
readiness approval.

Candidate-level readiness criteria remain sketch-only until later
Karl-approved locking.

## 6. Human-gate boundary

Readiness criteria may inform human review but cannot replace human approval.

No automated transition or promotion authority is created.

Permanent human gates remain human-controlled, including hypothesis approval,
decision records and go/no-go decisions, shadow promotion, live promotion, risk
parameter changes, kill decisions, and novel strategy-family introduction.

## 7. Open criteria-locking questions

- Which D2-006 gates must be restated versus referenced?
- How should exact-segment REC-5 breadth be represented without illegal
  aggregation?
- What additional qualitative or operational review questions must a human
  decide?
- What evidence is insufficient for research-to-shadow readiness?
- What must Karl lock later before criteria become governing gates?

## 8. What is not authorized

This sketch does not authorize:

- criteria locking;
- candidate readiness determination;
- research-to-shadow transition;
- shadow adapter or parity tooling implementation;
- D2-006, D2-007, REC-5, Phase 9, tiered-promotion, or
  permanent-human-gate modification;
- cross-segment inference under the REC-5 floor;
- performance ranking, scoring, or recommendation;
- runtime, paper/live, or protected-path work;
- AUTO bridge further work;
- A2C-003 or Path B work;
- lifecycle action;
- downstream authority.

## 9. Validation / next surface

Validation profile: CS12 T1-doc-narrow.

This surface is paired with the shadow-to-paper readiness sketch in WP-S2c-96.

WP-S2c-97 remains the later standalone permanent human gate preservation
sketch.
