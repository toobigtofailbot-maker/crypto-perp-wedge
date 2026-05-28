# Approval/Readiness Criteria Design Opening

## 1. Scope

WP-S2c-94 / WP-12ea is a Tier 1 documentation-only opening package.

This package opens the approval/readiness criteria design surface. It creates
only this document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-narrow.

Criteria are sketched in this tranche, not locked. Criteria locking requires a
later separate Karl approval.

## 2. Repo-truth basis

WP-12dz / WP-S2c-93 is merged.

The Phase 3 architecture sketch tranche checkpoint exists at
`docs/research_pipeline/2026-05-phase3_architecture_sketch_tranche_checkpoint.md`.

WP-S2c-88 through WP-S2c-92 are closed as complete-as-built
documentation-only sketches:

- WP-S2c-88 / WP-12dw: Phase 3 architecture design opening.
- WP-S2c-89 / WP-12dx: shadow deployment architecture sketch.
- WP-S2c-90 / WP-12dx: monitoring and dashboard architecture sketch.
- WP-S2c-91 / WP-12dy: paper-trading bridge architecture sketch.
- WP-S2c-92 / WP-12dy: live-trading boundary sketch.

The WP-S2c-93 checkpoint requires Main/Karl/user re-engagement before
post-tranche drafting.

Main selected the approval/readiness criteria definition tranche after
WP-S2c-93.

Path B, A2C-003, Phase 3 transition, Phase 3 implementation, AUTO bridge
further work, approval/readiness/lifecycle, policy/scoring/ranking/
recommendation, runtime, paper/live, exchange/broker/order contact, and
downstream authority remain unauthorized.

## 3. Why this tranche is next

Approval/readiness criteria design is upstream of implementation. The project
should not implement transition machinery before the approval/readiness
criteria surface is sketched.

Implementation planning should not precede criteria design because criteria
define the later questions that implementation would need to respect. This
package opens that design surface only and does not approve criteria,
implement criteria, or authorize transition work.

## 4. Locked inputs

This tranche references, without modifying, the following locked or protected
inputs:

- D2-006 promotion gates.
- D2-007 shadow discipline and parity thresholds.
- REC-5 exact-segment floor discipline.
- Phase 9 Decision 9 - Tiered Promotion Evidence Policy.
- Phase 9 Decision 6 - Human Approval Semantics.
- `docs/architecture/LONG_TERM_SCOPE.md` permanent human gates.
- Phase 1 paper runtime protection.
- Phase 3 architecture sketch tranche outputs from WP-S2c-88 through
  WP-S2c-93.
- Broad-floor-crossing sufficiency Yes as a gating-input decision only.

These inputs remain repo-truth constraints. This opening package does not
modify any of them.

## 5. Available evidence base

The available evidence base is repo-truth context only. Prior sufficiency and
checkpoint documents record the selected closed-runway floor-crossed breadth:
12 floor-crossed exact segments across six candidates, with the wider
structural inventory preserved as 14 all-repo floor-crossed exact segments and
two separate H-004 post-WP-5b Track F / historical rows.

This package does not reinterpret performance, rank candidates, infer
candidate readiness, or create cross-segment inference under the REC-5 floor.

The broad-floor-crossing sufficiency Yes remains a gating-input decision only.
It does not approve Phase 3 transition, criteria locking, implementation,
candidate readiness, or downstream authority.

## 6. Criteria-design questions to be sketched later

Later WP-S2c-95 through WP-S2c-97 packages may sketch unresolved questions
such as:

- What research-to-shadow readiness criteria should require beyond or
  alongside D2-006 and REC-5 evidence?
- How does per-segment REC-5 relate to candidate-level readiness without
  illegal cross-segment inference?
- What shadow-to-paper readiness criteria should require from D2-007
  shadow/parity evidence?
- How do criteria inform, but not replace, permanent human gates?
- What remains to be locked later by Karl approval?

WP-S2c-94 does not answer or lock those questions.

## 7. Tranche sequence

Expected tranche sequence:

- WP-S2c-94: opening.
- WP-S2c-95+96: likely E10 bundle if refreshed repo truth remains clean;
  research-to-shadow plus shadow-to-paper readiness criteria sketches.
- WP-S2c-97: standalone permanent human gate preservation sketch.
- WP-S2c-98: tranche checkpoint, CS12 T1-doc-major-decision, full pytest, and
  mandatory Main/Karl/user re-engagement.

Each later package must still start from refreshed `main`, verify repo truth,
check for conflicting `docs/project_status.md` PRs, and stop if a stop trigger
fires.

## 8. Boundary discipline

Criteria are sketched, not locked.

Criteria locking requires later separate Karl approval.

Permanent human gates remain absolute.

This package creates no candidate-specific readiness determination.

This package creates no transition authorization.

This package creates no implementation authorization.

This package creates no runtime or protected-path work.

All Tier 4 boundaries remain absolute.

## 9. What is not authorized

This package does not authorize:

- criteria locking;
- candidate readiness determination;
- research-to-shadow transition;
- shadow-to-paper transition;
- paper-to-live or live transition;
- Phase 3 implementation;
- runtime, paper-live, OMS, reconciliation, risk, safe-mode, kill-switch,
  event-log schema, `SignalProvider`, config, dependency, data, or
  protected-path changes;
- D2-006, D2-007, REC-5, Phase 9 Decision 9, tiered-promotion, or
  permanent-human-gate modification;
- cross-segment inference under the REC-5 floor;
- performance ranking or scoring;
- AUTO bridge further work;
- A2C-003 or Path B work except as deferred context;
- downstream authority.

It also creates no policy, recommendation, approval, lifecycle, promotion,
demotion, archive, bridge-code, bridge-output, paper/live, exchange, broker,
order, live API, schema, validator, central query-layer, test, canonical
artifact, trial-log, config, dependency, data, runtime, or protected-path
authority.

## 10. Validation / checkpoint posture

WP-S2c-94 uses CS12 T1-doc-narrow.

WP-S2c-95+96 and WP-S2c-97 are expected T1-doc-narrow unless repo truth or stop
triggers require escalation.

WP-S2c-98 uses CS12 T1-doc-major-decision with full pytest.

Mandatory Main/Karl/user re-engagement occurs at the WP-S2c-98 checkpoint.
