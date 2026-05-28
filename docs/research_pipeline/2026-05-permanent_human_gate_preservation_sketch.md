# Permanent Human Gate Preservation Sketch

## 1. Scope

WP-S2c-97 / WP-12ec is a Tier 1 documentation-only sketch package.

This package sketches how approval/readiness criteria preserve permanent human
gates. Criteria are sketched, not locked. Criteria locking requires later
separate Karl approval.

This package creates only this document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-narrow.

## 2. Repo-truth basis

WP-12eb / WP-S2c-95+96 is merged and created the research-to-shadow and
shadow-to-paper readiness criteria sketches.

WP-12ea / WP-S2c-94 opened the approval/readiness criteria design surface.

WP-S2c-98 remains the later tranche checkpoint requiring Main/Karl/user
re-engagement.

`docs/architecture/LONG_TERM_SCOPE.md` permanent human gates remain locked.

Phase 9 Decision 6 - Human Approval Semantics and Phase 9 Decision 9 - Tiered
Promotion Evidence Policy remain locked.

No criteria locking, readiness determination, transition authorization, Phase
3 implementation, runtime/protected-path work, or downstream authority exists.

## 3. Locked permanent human gates

This sketch references, without modifying, the locked permanent human gates
from `docs/architecture/LONG_TERM_SCOPE.md`:

- hypothesis approval;
- decision records and go/no-go decisions;
- shadow promotion;
- live promotion;
- risk parameter changes;
- kill decisions;
- novel strategy-family introduction.

These gates remain human-controlled. Automation may prepare evidence for these
gates, but it may not approve them.

## 4. Criteria-as-input boundary

Approval/readiness criteria may inform human review.

Approval/readiness criteria cannot replace human approval.

Approval/readiness criteria cannot create automatic transition authority.

Approval/readiness criteria cannot become a self-executing
promotion/demotion/lifecycle mechanism.

Approval/readiness criteria cannot outrank repo truth, locked decisions, or
human gates.

Readiness criteria remain sketch-only until later Karl-approved locking.

## 5. Non-automation boundary

No bot, agent, dashboard, monitor, validator, bridge, report, score,
recommendation, or automation may execute a permanent human gate.

Automation may only prepare evidence for human review when separately
authorized.

Any future implementation must preserve explicit human approval records where
human gates apply.

No autonomous live, paper, shadow, risk-change, kill, or strategy-family
introduction action is authorized.

## 6. Interaction with research-to-shadow and shadow-to-paper sketches

WP-S2c-95 and WP-S2c-96 readiness sketches are design inputs only.

D2-006, D2-007, REC-5, Phase 9, and permanent human gates remain locked.

Research-to-shadow and shadow-to-paper criteria may define what a human
reviews, not what the system automatically does.

No transition criteria are locked by this tranche.

## 7. Boundary-critical failure modes

Future work must stop on drift patterns including:

- criteria wording that implies automatic approval;
- parity pass interpreted as automatic paper readiness;
- D2-006 pass interpreted as automatic shadow promotion;
- REC-5 floor crossing interpreted as candidate approval;
- dashboard/monitor/report output treated as authority;
- score/rank/recommendation treated as promotion authority;
- any agentic execution of a gate;
- any risk parameter or kill decision automated without explicit locked
  authority;
- any permanent human gate converted into an advisory-only step.

## 8. Open criteria-locking questions

Unresolved questions for later criteria-locking work include:

- What exact human approval record is required before research-to-shadow
  transition?
- What exact human approval record is required before shadow-to-paper
  transition?
- What later Karl-approved criteria-locking package must say to preserve human
  gates?
- How should criteria distinguish evidence sufficiency from decision
  authority?
- What evidence outputs are allowed to inform, but not decide, human gates?

WP-S2c-97 does not answer or lock these questions.

## 9. What is not authorized

This sketch does not authorize:

- criteria locking;
- human-gate modification;
- human-gate automation;
- candidate readiness determination;
- research-to-shadow transition;
- shadow-to-paper transition;
- paper-to-live or live transition;
- Phase 3 implementation;
- shadow adapter, parity tooling, monitoring/dashboard, paper bridge, live
  trading, runtime, paper/live, exchange/broker/order, or Tier 4 contact;
- runtime / paper-live / OMS / reconciliation / risk / safe-mode /
  kill-switch / event-log schema / `SignalProvider` / config / dependency /
  data / protected-path changes;
- D2-006, D2-007, REC-5, Phase 9 Decision 9, Phase 9 Decision 6,
  tiered-promotion, or human-approval semantics modification;
- cross-segment inference under the REC-5 floor;
- performance ranking/scoring/recommendation authority;
- AUTO bridge further work;
- A2C-003 or Path B work except as deferred context;
- downstream authority.

## 10. Validation / checkpoint posture

Validation profile: CS12 T1-doc-narrow.

WP-S2c-98 remains the tranche checkpoint.

WP-S2c-98 requires CS12 T1-doc-major-decision validation with full pytest.

Mandatory Main/Karl/user re-engagement occurs at the WP-S2c-98 checkpoint.

Criteria locking remains deferred to a later Karl-approved decision package.
