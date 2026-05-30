# Path B Reassessment Design Opening

## 1. Scope

WP-S2c-120 / WP-12ez is a Tier 1 documentation-only opening package.

It opens the Path B reassessment design tranche. It creates only this opening
document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-narrow.

This package creates no Path B execution authorization, candidate registration,
hypothesis pre-registration, research artifact creation, tools changes, tests,
schema changes, validator changes, query-layer changes, runtime or
protected-path work, readiness determination, transition authorization, or
human-gate execution.

## 2. Repo-truth basis

WP-S2c-119 is merged and closed the second cross-candidate diagnostic brief
tranche. The second diagnostic brief exists at
`research/briefs/2026-05-cross_candidate_diagnostic_brief.md`.

The diagnostic brief is diagnostic only. It does not recommend, rank, score,
select, approve, transition, or determine readiness.

Current Scope 6 surface is complete at schema, validator, and query-layer level:

- WP-S2c-113 locked Scope 6 artifact families.
- WP-S2c-114 introduced the Scope 6 schemas.
- WP-S2c-115 introduced Scope 6 validators.
- WP-S2c-117 introduced Scope 6 query-layer views.

Related locked repo-truth anchors remain in force:

- WP-S2c-100 locked refined approval/readiness criteria.
- WP-S2c-104 locked the implementation authorization decision.
- WP-S2c-105 through WP-S2c-110 completed the bounded shadow adapter plus
  parity tooling tranche.

Existing canonical artifacts and existing briefs remain historical records and
must not be modified by this tranche.

## 3. Why Path B reassessment now

The repo has stronger infrastructure surfaces than it had during the first
cross-candidate diagnostic brief. The research pipeline is not actively
producing a candidate.

The current diagnostic state shows a concluded NO-GO population, one reserved
draft row, and no Scope 6 approval/evidence instances.

Path B reassessment is the design-only way to evaluate evidence-kind expansion
without pre-authorizing execution. This tranche produces durable design
substance for Main/Karl review.

Path B execution requires a later Karl-gated decision and is not authorized
here.

## 4. Current research pipeline state

The WP-S2c-119 diagnostic brief records:

- ten concluded baseline-tested candidates;
- one reserved draft row;
- no active research candidate flowing through R2S/S2P approval surfaces;
- Scope 6 base views returning zero rows;
- Scope 6 inventory and link views operating cleanly under zero-instance state;
- Q08 full integrity sweep and Q11 Scope 6 integrity subset returning `[]`.

This state does not imply readiness, recommendation, ranking, approval,
transition eligibility, or candidate selection.

## 5. Diagnostic brief anchors

WP-S2c-121 should use these WP-S2c-119 brief sections and outputs as primary
substance input:

- candidate inventory and status distribution;
- search-space coverage by strategy family and timeframe;
- information-input coverage;
- Scope 6 zero-instance exercise;
- data-integrity and read-only checks.

WP-S2c-121 should anchor on the diagnostic brief instead of restating coverage
from scratch. Diagnostic evidence may inform design options, but it cannot
select options or authorize execution.

## 6. Path B reassessment question

Central design question:

Given the current diagnostic state and locked boundaries, what evidence-kind
expansion options could re-prime the research pipeline without weakening locked
gates, human approval boundaries, runtime protection, Tier 4 limits,
information-input discipline, or timeframe discipline?

This opening does not answer that question. WP-S2c-121 produces options, and
WP-S2c-122 consolidates them.

## 7. Locked boundaries

The design tranche must preserve:

- Permanent human gates remain absolute.
- D2-006 remains unchanged.
- D2-007 remains unchanged.
- REC-5 exact-segment discipline remains unchanged.
- Phase 9 Decision 9 tiered-promotion discipline remains unchanged.
- WP-S2c-100 locked criteria remain unchanged.
- WP-S2c-104 implementation authorization remains unchanged.
- WP-S2c-113 Scope 6 lock remains unchanged.
- WP-S2c-114 schemas remain unchanged.
- WP-S2c-115 validators remain unchanged.
- WP-S2c-117 query views remain unchanged.
- Phase 1 paper runtime protection remains unchanged.
- SignalProvider Protocol remains unchanged.
- Locked information-inputs taxonomy remains unchanged where confirmed by repo
  truth.
- Locked timeframe-status discipline remains unchanged where confirmed by repo
  truth.
- Tier 4 and protected-path boundaries remain absolute.
- Monitoring/dashboard remains deferred.
- Paper bridge remains unauthorized.
- AUTO bridge remains frozen, and A2C-003 remains unauthorized.
- Path B execution remains unauthorized.

## 8. Evidence-kind expansion frame

WP-S2c-121 may examine evidence-kind expansion dimensions without selecting or
locking any option. Opening-level dimensions include:

- strategy-family expansion;
- timeframe expansion within locked timeframe-status discipline;
- information-input combinations within locked taxonomy;
- candidate-instance dimensions;
- data/evidence-type expansion that remains inside approved non-runtime
  research boundaries;
- narrower versus broader Path B variants;
- do-nothing / hold alternative.

Each dimension must be evaluated later against locked boundaries and must
include preservation notes.

## 9. Tranche sequence

- WP-S2c-120: opening/framing.
- WP-S2c-121: substantive reassessment design options.
- WP-S2c-122: consolidation into lock-candidate wording.

After WP-S2c-122, Side must stop and surface consolidated content to Main/Karl.

A later Karl-gated locking decision package is not pre-authorized. Path B
execution is not authorized by this tranche.

## 10. WP-S2c-121 expected output

WP-S2c-121 should produce:

- evidence-kind expansion options;
- trace from each option to the diagnostic brief's coverage/search-space
  findings;
- locked-boundary analysis for each option;
- estimated downstream package shape and cost;
- schema, validator, and query-layer implication assessment without modifying
  those surfaces;
- alternatives including do-nothing, narrower Path B, broader Path B, and mixed
  approach;
- preservation note for each option.

WP-S2c-121 must not select among options.

## 11. WP-S2c-122 expected output

WP-S2c-122 should consume WP-S2c-121 substance, consolidate options into
lock-candidate wording, include preservation notes, and prepare a Main/Karl
resolution surface where each option can be marked LOCK / MODIFY / DEFER /
REJECT.

WP-S2c-122 must not add new options, materially change option intent, lock any
option, authorize execution, or select among options.

## 12. Explicit non-authorizations

This opening does not authorize:

- Path B execution;
- locking any Path B option;
- selecting among options;
- candidate registration;
- hypothesis pre-registration;
- backtest execution;
- research artifact creation;
- schema, validator, or query-layer changes;
- tools or tests changes;
- canonical artifact modification;
- transition authorization;
- candidate readiness determination;
- candidate recommendation, ranking, or scoring;
- human-gate execution;
- Tier 4 contact;
- runtime or protected-path work;
- monitoring/dashboard;
- paper bridge;
- AUTO bridge;
- A2C-003.

## 13. Stop conditions for the design tranche

Stop the design tranche if any of the following appears:

- tension with locked criteria or locked decisions;
- any option or framing that would weaken, automate, bypass, replace,
  reinterpret, or execute permanent human gates;
- any need to modify locked schemas, validators, query views, canonical
  artifacts, timeframe discipline, or information-input taxonomy;
- any need for protected-path, Tier 4, runtime, paper, or live contact;
- any need for candidate registration, hypothesis pre-registration, backtest
  execution, readiness determination, transition authorization, recommendation,
  ranking, or scoring;
- incoherence in Path B framing that requires Karl resolution before proceeding;
- Karl override.

## 14. Validation / next-package posture

WP-S2c-120 uses CS12 T1-doc-narrow.

After merge, Side may draft WP-S2c-121 after refreshed-main preflight and no
stop trigger. WP-S2c-121 is T1-doc-narrow and design-substance only.

WP-S2c-122 is T1-doc-narrow and consolidation-only.

After WP-S2c-122 merges, Side must stop and report back to Main 4.0 with
consolidated lock-candidate content. No locking package may be drafted until
Main/Karl resolves each option.
