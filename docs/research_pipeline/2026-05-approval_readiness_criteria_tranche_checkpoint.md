# Approval/Readiness Criteria Tranche Checkpoint

## 1. Scope

WP-S2c-98 / WP-12ed is a Tier 1 documentation-only
major-decision-boundary checkpoint package.

This checkpoint closes the approval/readiness criteria definition tranche as
complete-as-built documentation-only criteria sketching.

This package creates only this document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-major-decision. Full pytest is required.

This checkpoint does not lock criteria or authorize transition,
implementation, readiness action, or downstream authority.

## 2. Repo-truth basis

WP-12ec / WP-S2c-97 is merged.

WP-S2c-94 through WP-S2c-97 documents exist:

- `docs/research_pipeline/2026-05-approval_readiness_criteria_design_opening.md`
- `docs/research_pipeline/2026-05-research_to_shadow_readiness_criteria_sketch.md`
- `docs/research_pipeline/2026-05-shadow_to_paper_readiness_criteria_sketch.md`
- `docs/research_pipeline/2026-05-permanent_human_gate_preservation_sketch.md`

WP-S2c-94 opened the approval/readiness criteria design surface.

WP-S2c-95 and WP-S2c-96 sketched research-to-shadow and shadow-to-paper
readiness criteria.

WP-S2c-97 sketched permanent human gate preservation.

Criteria are sketched, not locked.

Criteria locking requires later separate Karl approval.

Permanent human gates remain absolute.

Path B, A2C-003, Phase 3 transition, Phase 3 implementation, AUTO bridge
further work, approval/readiness/lifecycle, policy/scoring/ranking/
recommendation, runtime, paper/live, exchange/broker/order contact, and
downstream authority remain unauthorized.

## 3. Completed tranche surfaces

The completed approval/readiness criteria definition tranche consists of:

- WP-S2c-94 / WP-12ea: approval/readiness criteria design opening.
- WP-S2c-95 / WP-12eb: research-to-shadow readiness criteria sketch.
- WP-S2c-96 / WP-12eb: shadow-to-paper readiness criteria sketch.
- WP-S2c-97 / WP-12ec: permanent human gate preservation sketch.

## 4. Tranche output summary

WP-S2c-94 opened the approval/readiness criteria design surface and defined
the tranche sequence.

WP-S2c-95 sketched research-to-shadow readiness design questions around
D2-006, D2-007, REC-5, candidate-level readiness, and human approval.

WP-S2c-96 sketched shadow-to-paper readiness design questions around D2-007
shadow window/parity, paper runtime protection, and human approval.

WP-S2c-97 sketched how readiness criteria preserve permanent human gates and
cannot replace human approval.

All surfaces remained documentation-only and sketch-only.

## 5. Boundary summary

Criteria are sketched, not locked.

Criteria locking requires later separate Karl approval.

No readiness determination was made.

No transition was authorized.

No implementation was authorized.

No human gate was modified, automated, weakened, or replaced.

No runtime/protected path was touched.

All Tier 4 boundaries remain absolute.

## 6. Unresolved criteria-locking questions

Unresolved questions for Main/Karl/user include:

- Should a later Karl-approved package lock criteria, defer, or require more
  design?
- What exact human approval record is required before research-to-shadow
  transition?
- What exact human approval record is required before shadow-to-paper
  transition?
- How should D2-006 evidence be referenced or restated in locked criteria?
- How should REC-5 exact-segment evidence inform candidate-level review
  without illegal cross-segment inference?
- How should D2-007 parity results inform paper-readiness review without
  becoming automatic transition authority?
- What evidence is insufficient for readiness consideration?
- What wording is needed to keep criteria from becoming automated approval
  gates?

This checkpoint does not answer those questions.

## 7. Descriptive post-tranche options

Post-tranche direction options are descriptive only and unranked:

- Criteria-locking decision package, with explicit Karl approval.
- Additional criteria design package if unresolved design tensions remain.
- Phase 3 implementation authorization decision, only after criteria are
  locked if Main/Karl/user choose.
- Phase 3 implementation planning tranche, only after authorization if
  selected later.
- AUTO bridge canonical-write-path design tranche, if separately revived.
- A2C-003 cohort phase, if more evidence breadth is desired despite prior
  sufficiency Yes.
- Path B architecture design tranche.
- Hold / stop / defer.

No option is selected, ranked, recommended, or authorized by this package.

## 8. What is locked by this checkpoint

This checkpoint locks only documentation/checkpoint facts:

- The approval/readiness criteria definition tranche is complete-as-built as
  documentation-only sketching.
- WP-S2c-94 through WP-S2c-97 documents exist.
- The tranche remained sketch-only.
- Criteria were not locked.
- Criteria locking requires later separate Karl approval.
- Permanent human gates remain absolute.
- No implementation or transition authority was created.
- Main/Karl/user re-engagement is required after merge.

## 9. What is not authorized

This checkpoint does not authorize:

- criteria locking;
- criteria selection;
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
  tiered-promotion, human-approval semantics, or permanent-human-gate
  modification;
- human-gate automation, bypass, weakening, replacement, or reinterpretation;
- cross-segment inference under REC-5 floor;
- performance ranking/scoring/recommendation authority;
- AUTO bridge further work;
- A2C-003 or Path B work except as deferred context;
- lifecycle, promotion, demotion, archive, or approval/readiness action;
- downstream authority.

## 10. Required next authority

After merge, Side must report back to Main/Karl/user for post-tranche
direction.

No post-tranche package may be auto-drafted until Main/Karl/user selects or
explicitly authorizes the next direction.

If criteria locking is selected later, it requires explicit Karl approval.

## 11. Validation profile

This package uses CS12 T1-doc-major-decision because it closes a major
criteria-design tranche and mandates Main/Karl/user re-engagement.

Full pytest is required.

Required validation includes:

- exact changed-file scope;
- diff/scope summary against the two allowed files;
- research query view listing;
- all discovered `v_integrity_*` views with JSON output returning `[]`;
- registry validators;
- targeted research-query tests required by current CS12 convention;
- helper tests required by current CS12 convention;
- bridge tests required by current CS12 convention;
- scoped regression tests required by current CS12 major-decision convention;
- full pytest;
- staged diff/scope checks.

## 12. Validation

Pre-edit verification confirmed:

- PR #278 / WP-12ec is merged at `338ed31`.
- Refreshed `main` includes the WP-12ec merge.
- `docs/project_status.md` records WP-12ec / WP-S2c-97 as the latest
  branch-state before this package.
- No open PR was reported.
- No remote or local `codex/wp-12ed-approval-readiness-checkpoint` branch was
  found before this package branch.
- No WP-12ed / WP-S2c-98 PR was found before drafting.
- This checkpoint document did not exist before this package.
- WP-S2c-94 through WP-S2c-97 tranche documents exist.
- No started approval/readiness criteria tranche checkpoint document was found
  elsewhere in the repo.
- No unresolved decision is required before drafting this checkpoint.
- Path B, A2C-003, Phase 3 transition, Phase 3 implementation, AUTO bridge
  further work, approval/readiness/lifecycle, policy/scoring/ranking/
  recommendation, runtime, paper/live, exchange/broker/order contact, and
  downstream authority remain unauthorized.
- No schema, validator, central query-layer, committed-state test, config,
  dependency, data, runtime, protected-path, bridge-code, bridge-output,
  D2-006, D2-007, REC-5, Phase 9, tiered-promotion, human-approval,
  permanent-human-gate, event-log schema, or `SignalProvider` modification is
  required.

Package validation results are recorded in the execution report-back and PR.
