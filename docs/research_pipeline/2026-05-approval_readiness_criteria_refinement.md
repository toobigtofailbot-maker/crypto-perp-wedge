# Approval/Readiness Criteria Focused Refinement

## 1. Scope

WP-S2c-99-refine / WP-12ef is a Tier 1 documentation-only focused refinement
package.

It addresses the five known deferred decisions surfaced by the WP-12ee
approval/readiness criteria consolidation.

This package creates only this document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-narrow.

No criteria are locked by this package.

## 2. Repo-truth basis

WP-12ee / WP-S2c-99-pre is merged.

WP-S2c-94 through WP-S2c-98 documents exist.

WP-S2c-99-pre consolidation exists at
`docs/research_pipeline/2026-05-approval_readiness_criteria_consolidation.md`.

Criteria remain proposed lock candidates only, not locked criteria.

Criteria locking requires later separate Karl approval.

Main directed this focused refinement package before criteria locking.

Permanent human gates remain absolute.

D2-006, D2-007, REC-5, Phase 9 Decision 9, Phase 9 Decision 6, and permanent
human gates remain locked and unmodified.

Path B, A2C-003, Phase 3 transition, Phase 3 implementation, AUTO bridge
further work, approval/readiness/lifecycle, policy/scoring/ranking/
recommendation, runtime, paper/live, exchange/broker/order contact, and
downstream authority remain unauthorized.

## 3. Refinement method

Each deferred item is refined into proposed lock-candidate wording where
current source material supports it.

Each refined candidate includes:

- deferred item ID;
- source basis;
- proposed refined lock-candidate wording;
- preservation note;
- unresolved note if still not lockable.

Refinement clarifies deferred content but does not lock criteria, change
D2-006, D2-007, REC-5, or Phase 9 semantics, or modify human gates.

If source material cannot support lock-candidate wording, the item is
explicitly deferred rather than invented.

## 4. Deferred item 1 - D2-006 relationship for research-to-shadow

Deferred item ID: R2S-D1.

Source basis: D2-006 in `docs/onboarding/PHASE2_BASELINE.md`, WP-S2c-95
research-to-shadow readiness criteria sketch, WP-S2c-97 permanent human gate
preservation sketch, and WP-S2c-99-pre consolidation item R2S-1.

Proposed refined lock-candidate wording: Research-to-shadow eligibility
requires direct evidence that the candidate passed all D2-006 promotion gates.
D2-006 remains the locked source of truth for the gates, thresholds, and
semantics. Research-to-shadow criteria should reference D2-006 as the locked
source of truth and require a D2-006 pass evidence reference or attestation,
rather than restating or locally rewriting the D2-006 gate text. Research-to-
shadow criteria may add review-context requirements needed to preserve REC-5
exact-segment discipline and permanent human approval, but may not add local
tightening or weakening of D2-006 gate thresholds. No D2-006 gate is locally
tightened by this refinement.

Preservation note: D2-006 is locked. This refinement applies and references
D2-006; it does not modify D2-006 thresholds or semantics. D2-006 pass
evidence cannot create automatic shadow promotion.

Unresolved note: Ready for Karl review as a proposed lock candidate. Final
criteria locking still requires later separate Karl approval.

## 5. Deferred item 2 - research-to-shadow human approval record

Deferred item ID: R2S-D2.

Source basis: WP-S2c-95 research-to-shadow readiness criteria sketch,
WP-S2c-97 permanent human gate preservation sketch, and WP-S2c-99-pre
consolidation item R2S-5.

Proposed refined lock-candidate wording: Before any research-to-shadow
transition, a human approval record must exist and must document, at minimum,
the candidate identity; strategy or candidate family where repo truth supports
that wording; evidence snapshot references; D2-006 gate pass evidence
reference or attestation; REC-5 exact-segment evidence list or reference;
explicit statement that no cross-segment inference is used below the REC-5
floor; approver identity; approval timestamp/date; decision outcome; explicit
confirmation that permanent human gates, D2-006, D2-007, REC-5, and Phase 9
semantics remain preserved; and explicit statement that the record is required
before transition but does not itself implement transition machinery.

Proposed artifact location remains a later decision because current repo truth
does not define a final approval-record location, schema, or directory for
this transition.

Preservation note: Human approval remains mandatory. The record documents a
human decision; it does not automate approval. No research-to-shadow
transition is authorized by this refinement.

Unresolved note: Ready for Karl review as proposed record-content wording.
Artifact location and schema, if any, remain later decisions.

## 6. Deferred item 3 - shadow-window completion evidence

Deferred item ID: S2P-D3.

Source basis: D2-007 in `docs/onboarding/PHASE2_BASELINE.md`, WP-S2c-96
shadow-to-paper readiness criteria sketch, WP-S2c-97 permanent human gate
preservation sketch, and WP-S2c-99-pre consolidation items S2P-1 through
S2P-5.

Proposed refined lock-candidate wording: Shadow-to-paper review requires
shadow-window completion evidence showing the D2-007 minimum shadow window of
at least 14 calendar days; D2-007 parity thresholds of PnL deviation no more
than 10% and trade count deviation no more than 5%; clean lineage to the
shadow observation/evidence used in review; disclosure of interruptions,
invalid observations, missing data, or observation resets; parity result
evidence or attestation; and evidence retention/reference sufficient for
human review. Mismatch diagnostics may support human review only as decision
support and cannot become ranking, scoring, recommendation, or transition
logic.

Preservation note: D2-007 is locked. This refinement does not modify D2-007
thresholds. Passing parity cannot automatically authorize paper transition.

Unresolved note: Ready for Karl review as proposed evidence-content wording.
Final retention location or artifact grammar remains a later decision unless
separately authorized.

## 7. Deferred item 4 - shadow-to-paper human approval record

Deferred item ID: S2P-D4.

Source basis: WP-S2c-96 shadow-to-paper readiness criteria sketch, WP-S2c-97
permanent human gate preservation sketch, and WP-S2c-99-pre consolidation
item S2P-6.

Proposed refined lock-candidate wording: Before any shadow-to-paper
transition, a human approval record must exist and must document, at minimum,
the candidate identity; shadow-window evidence reference; D2-007 parity
result reference or attestation; interruption or invalid-observation
disclosure reference; paper runtime protection confirmation; approver
identity; approval timestamp/date; decision outcome; explicit confirmation
that permanent human gates, D2-007, Phase 1 paper runtime protection, and
Tier 4 boundaries remain preserved; and explicit statement that the record is
required before transition but does not itself implement transition
machinery.

Proposed artifact location remains a later decision because current repo truth
does not define a final approval-record location, schema, or directory for
this transition.

Preservation note: Human approval remains mandatory. The record documents a
human decision; it does not automate approval. No shadow-to-paper transition
is authorized by this refinement.

Unresolved note: Ready for Karl review as proposed record-content wording.
Artifact location and schema, if any, remain later decisions.

## 8. Deferred item 5 - candidate-level readiness lockability

Deferred item ID: R2S-D5.

Source basis: WP-S2c-95 research-to-shadow readiness criteria sketch,
WP-S2c-97 permanent human gate preservation sketch, WP-S2c-99-pre
consolidation item R2S-6, and WP-S2c-87 broad-floor-crossing sufficiency
decision.

Position statement: Candidate-level readiness lock-candidate wording is
producible now from the current sketch/consolidation content, but only as a
bounded human-review criterion that preserves REC-5 exact-segment discipline
and does not decide readiness for any candidate.

Rationale: Current source material is sufficient to define the boundary of
candidate-level readiness review: exact-segment REC-5 evidence may be an input
to human review, D2-006 evidence is required for research-to-shadow
eligibility, D2-007 evidence is required where shadow-to-paper review is at
issue, broad-floor-crossing sufficiency is descriptive gating input only, and
permanent human approval remains mandatory. Current source material is not
authority to declare any candidate ready, compare candidates, score
candidates, or infer candidate readiness automatically from segment evidence.

Proposed refined lock-candidate wording: Candidate-level readiness review may
use exact-segment REC-5 evidence only as bounded evidence input under
`candidate_id / outcome_kind / pipeline_version / expectation_source_type`.
It may not use cross-segment inference below the REC-5 floor and may not
convert broad-floor-crossing sufficiency into candidate-specific readiness.
For research-to-shadow review, candidate-level readiness requires D2-006 pass
evidence as a prerequisite and human approval before any transition. For
shadow-to-paper review, where applicable, candidate-level readiness requires
D2-007 shadow-window and parity evidence as review input and human approval
before any transition. This criterion does not declare any candidate ready.

Preservation note: Candidate-level readiness must not be inferred
automatically from segment evidence, D2-006 pass, D2-007 parity pass, or
broad-floor-crossing sufficiency. Candidate-level readiness cannot bypass
permanent human gates.

Unresolved note: Ready for Karl review as bounded lock-candidate wording only.
If Main/Karl want a richer candidate-level decision model, that design remains
outside this refinement and must be separately authorized.

## 9. Refined lock-candidate summary

| Refined item | Proposed refined lock-candidate status | Source basis | Human-gate preservation note |
|---|---|---|---|
| R2S-D1 - D2-006 relationship for research-to-shadow | Ready for Karl review | D2-006, WP-S2c-95, WP-S2c-97, WP-S2c-99-pre | D2-006 pass evidence is prerequisite evidence, not automatic shadow promotion. |
| R2S-D2 - research-to-shadow human approval record | Ready for Karl review; artifact location still deferred | WP-S2c-95, WP-S2c-97, WP-S2c-99-pre | Human record documents the human decision and does not automate transition. |
| S2P-D3 - shadow-window completion evidence | Ready for Karl review; retention/location still deferred | D2-007, WP-S2c-96, WP-S2c-97, WP-S2c-99-pre | Parity and diagnostics inform review only and cannot authorize paper transition. |
| S2P-D4 - shadow-to-paper human approval record | Ready for Karl review; artifact location still deferred | WP-S2c-96, WP-S2c-97, WP-S2c-99-pre | Human record documents the human decision and does not automate transition. |
| R2S-D5 - candidate-level readiness lockability | Ready for Karl review as bounded wording only | WP-S2c-95, WP-S2c-97, WP-S2c-99-pre, WP-S2c-87 | Candidate readiness cannot bypass permanent human gates or arise automatically from evidence. |

## 10. Remaining gaps / deferrals

No boundary conflict is surfaced by this refinement.

The five deferred items are ready for lock-decision review as proposed
lock-candidate wording, subject to later Karl approval.

Artifact location, schema, and directory decisions for research-to-shadow and
shadow-to-paper human approval records remain deferred because current repo
truth does not define them and this package is not authorized to create them.

Evidence retention location or artifact grammar for shadow-window completion
evidence remains deferred unless later authorized.

If Main/Karl want candidate-level readiness to include a richer decision
model than the bounded wording in this document, further focused design is
required before locking that richer model.

## 11. Non-claims and forbidden authority

This package refines proposed lock-candidate wording but locks no criteria.

No criteria selection is made.

No readiness determination is made.

No transition is authorized.

No implementation is authorized.

No human gate is modified, automated, weakened, bypassed, replaced, or
reinterpreted.

No D2-006, D2-007, REC-5, Phase 9, tiered-promotion, human-approval, or
permanent-human-gate semantics are modified.

No runtime/protected path is touched.

No downstream authority is created.

## 12. Required next authority

After merge, Side must surface the refined lock-candidate content to
Main/Karl/user.

No criteria-locking WP may be drafted until Main/Karl explicitly resolves
which criteria lock, with what wording/thresholds, and confirms
permanent-human-gate preservation.

The actual criteria-locking decision package, if authorized later, is expected
to be T1-doc-major-decision with full pytest.

## 13. Validation posture

Validation profile: CS12 T1-doc-narrow.

Full pytest is not required unless repo guidance or a stop trigger requires
escalation.
