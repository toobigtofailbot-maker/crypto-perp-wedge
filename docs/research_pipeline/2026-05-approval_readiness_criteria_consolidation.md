# Approval/Readiness Criteria Consolidation

## 1. Scope

WP-S2c-99-pre / WP-12ee is a Tier 1 documentation-only consolidation package.

This package consolidates the WP-S2c-94 through WP-S2c-97 approval/readiness
criteria sketches into proposed lock-candidate wording for Main/Karl review.

This package creates only this document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-narrow.

No criteria are locked by this package.

## 2. Repo-truth basis

WP-12ed / WP-S2c-98 is merged.

WP-S2c-94 through WP-S2c-97 documents exist:

- `docs/research_pipeline/2026-05-approval_readiness_criteria_design_opening.md`
- `docs/research_pipeline/2026-05-research_to_shadow_readiness_criteria_sketch.md`
- `docs/research_pipeline/2026-05-shadow_to_paper_readiness_criteria_sketch.md`
- `docs/research_pipeline/2026-05-permanent_human_gate_preservation_sketch.md`

WP-S2c-98 closed the approval/readiness criteria definition tranche as
documentation-only, sketch-only work. Criteria remain sketched, not locked.
Criteria locking requires later separate Karl approval.

Main directed this consolidation package before criteria locking because the
sketched criteria were distributed across multiple documents and were not yet
written as proposed lock text.

Permanent human gates remain absolute.

Path B, A2C-003, Phase 3 transition, Phase 3 implementation, AUTO bridge
further work, approval/readiness/lifecycle, policy/scoring/ranking/
recommendation, runtime, paper/live, exchange/broker/order contact, and
downstream authority remain unauthorized.

## 3. Consolidation method

Each lock candidate is traced to the originating sketch document.

Consolidation rewords only for lock-candidate clarity and does not change
criterion intent.

Each candidate includes:

- ID;
- proposed lock-candidate wording;
- source sketch;
- preservation note;
- unresolved decision note if applicable.

If the source sketch does not provide enough substance for lock-candidate
wording, the item is flagged as a gap rather than invented.

## 4. Global lock-candidate criteria

### G-1

Proposed lock-candidate wording: Approval/readiness criteria become governing
gates only after explicit Karl approval; until then they remain sketches.

Source sketch: WP-S2c-94 design opening and WP-S2c-98 tranche checkpoint.

Preservation note: Preserves the sketch-only status and later separate Karl
approval requirement.

### G-2

Proposed lock-candidate wording: Locked approval/readiness criteria may inform
human review, but may not replace, bypass, automate, weaken, or reinterpret
human approval.

Source sketch: WP-S2c-97 permanent human gate preservation sketch.

Preservation note: Preserves permanent human gates as absolute and
human-controlled.

### G-3

Proposed lock-candidate wording: No approval/readiness criterion may create
automatic transition, promotion, demotion, lifecycle, paper, live, risk-change,
or kill authority.

Source sketch: WP-S2c-95 research-to-shadow sketch, WP-S2c-96
shadow-to-paper sketch, and WP-S2c-97 permanent human gate preservation sketch.

Preservation note: Preserves the non-automation boundary and prevents criteria
from becoming self-executing authority.

### G-4

Proposed lock-candidate wording: Criteria locking itself does not make any
candidate ready and does not determine candidate readiness.

Source sketch: WP-S2c-94 design opening and WP-S2c-98 tranche checkpoint.

Preservation note: Preserves the difference between criteria text and a later
candidate-specific human readiness decision.

### G-5

Proposed lock-candidate wording: Criteria locking does not authorize Phase 3
implementation, runtime, paper/live, exchange/broker/order, or Tier 4 contact.

Source sketch: WP-S2c-94 design opening, WP-S2c-96 shadow-to-paper sketch, and
WP-S2c-98 tranche checkpoint.

Preservation note: Preserves protected runtime and Tier 4 boundaries.

## 5. Research-to-shadow lock-candidate criteria

### R2S-1

Proposed lock-candidate wording: Research-to-shadow readiness review must
reference D2-006 promotion gates.

Source sketch: WP-S2c-95 research-to-shadow readiness criteria sketch.

Preservation note: Preserves D2-006 as the locked source of truth and does not
modify D2-006 thresholds or semantics.

Unresolved decision note: Karl/Main must resolve whether locked wording
requires direct D2-006 pass evidence, explicit gate-by-gate documentation, or
a narrower reference to the existing D2-006 source of truth.

### R2S-2

Proposed lock-candidate wording: REC-5 evidence used for readiness review must
remain exact-segment evidence under `candidate_id / outcome_kind /
pipeline_version / expectation_source_type`; no pooled candidate evidence or
cross-segment aggregation may be used.

Source sketch: WP-S2c-95 research-to-shadow readiness criteria sketch.

Preservation note: Preserves REC-5 exact-segment discipline and rejects pooled
candidate-level inference.

### R2S-3

Proposed lock-candidate wording: Segment-level REC inference requires at
least 3 reconciliations per exact segment before drawing segment-level
inference.

Source sketch: WP-S2c-95 research-to-shadow readiness criteria sketch.

Preservation note: Preserves the REC-5 floor and does not create
cross-segment inference below that floor.

### R2S-4

Proposed lock-candidate wording: Broad-floor-crossing evidence may be
descriptive input to human readiness review, but it is not automatic approval,
candidate-specific readiness, or a substitute for a later human decision.

Source sketch: WP-S2c-95 research-to-shadow readiness criteria sketch and
WP-S2c-87 broad-floor-crossing sufficiency decision.

Preservation note: Preserves broad-floor-crossing sufficiency as a gating
input only.

### R2S-5

Proposed lock-candidate wording: Any research-to-shadow transition requires a
human approval decision before transition.

Source sketch: WP-S2c-95 research-to-shadow readiness criteria sketch and
WP-S2c-97 permanent human gate preservation sketch.

Preservation note: Preserves shadow promotion as a permanent human gate.

Unresolved decision note: Exact approval-record wording remains unresolved for
Karl/Main.

### R2S-6

Proposed lock-candidate wording: Candidate-level readiness remains unresolved
unless and until Karl locks how exact-segment evidence, D2-006 evidence,
qualitative review, and human approval combine without violating REC-5 floor
discipline.

Source sketch: WP-S2c-95 research-to-shadow readiness criteria sketch.

Preservation note: Preserves the boundary that per-segment evidence cannot be
silently transformed into candidate-level readiness approval.

Unresolved decision note: Candidate-level readiness design remains unresolved.

## 6. Shadow-to-paper lock-candidate criteria

### S2P-1

Proposed lock-candidate wording: Shadow-to-paper readiness review must
preserve the D2-007 minimum shadow window of at least 14 calendar days.

Source sketch: WP-S2c-96 shadow-to-paper readiness criteria sketch.

Preservation note: Preserves D2-007 shadow-window discipline without changing
the threshold.

### S2P-2

Proposed lock-candidate wording: D2-007 parity thresholds remain PnL deviation
no more than 10% and trade count deviation no more than 5% during the shadow
window.

Source sketch: WP-S2c-96 shadow-to-paper readiness criteria sketch.

Preservation note: Preserves D2-007 parity thresholds without modification.

### S2P-3

Proposed lock-candidate wording: Shadow-window completion evidence may require
completed calendar coverage, clean lineage to shadow evidence, and disclosure
of interruptions or invalid shadow observations.

Source sketch: WP-S2c-96 shadow-to-paper readiness criteria sketch.

Preservation note: Preserves the shadow-evidence design surface without
inventing final evidence wording.

Unresolved decision note: Exact required evidence wording remains unresolved
for Karl/Main.

### S2P-4

Proposed lock-candidate wording: Passing parity may support human review but
cannot automatically authorize paper transition.

Source sketch: WP-S2c-96 shadow-to-paper readiness criteria sketch.

Preservation note: Preserves parity as decision-support evidence only.

### S2P-5

Proposed lock-candidate wording: Mismatch diagnostics may be decision-support
evidence only; they cannot become ranking, scoring, recommendation, or
automated paper-transition logic.

Source sketch: WP-S2c-96 shadow-to-paper readiness criteria sketch.

Preservation note: Preserves the prohibition on policy, scoring, ranking, and
recommendation authority.

### S2P-6

Proposed lock-candidate wording: Any shadow-to-paper transition requires a
human approval decision before paper transition.

Source sketch: WP-S2c-96 shadow-to-paper readiness criteria sketch and
WP-S2c-97 permanent human gate preservation sketch.

Preservation note: Preserves transition authority as human-controlled.

Unresolved decision note: Exact approval-record wording remains unresolved for
Karl/Main.

### S2P-7

Proposed lock-candidate wording: Paper runtime protection remains
non-negotiable; criteria locking does not authorize paper-runtime
implementation, paper bridge implementation, paper bridge invocation, or
paper/live contact.

Source sketch: WP-S2c-96 shadow-to-paper readiness criteria sketch.

Preservation note: Preserves Phase 1 paper runtime protection and protected
paper/live boundaries.

## 7. Human-gate preservation lock-candidate criteria

### HG-1

Proposed lock-candidate wording: Permanent human gates remain
human-controlled for hypothesis approval, decision records/go-no-go, shadow
promotion, live promotion, risk parameter changes, kill decisions, and novel
strategy-family introduction.

Source sketch: WP-S2c-97 permanent human gate preservation sketch and
`docs/architecture/LONG_TERM_SCOPE.md`.

Preservation note: Explicitly confirms all permanent human gates listed in the
source sketch.

### HG-2

Proposed lock-candidate wording: Approval/readiness criteria may inform human
review but cannot replace human approval.

Source sketch: WP-S2c-97 permanent human gate preservation sketch.

Preservation note: Confirms human approval remains required wherever human
gates apply.

### HG-3

Proposed lock-candidate wording: Approval/readiness criteria cannot create
automatic transition authority.

Source sketch: WP-S2c-97 permanent human gate preservation sketch.

Preservation note: Confirms transition decisions remain human-controlled.

### HG-4

Proposed lock-candidate wording: Approval/readiness criteria cannot become a
self-executing promotion, demotion, or lifecycle mechanism.

Source sketch: WP-S2c-97 permanent human gate preservation sketch.

Preservation note: Confirms criteria cannot become lifecycle automation.

### HG-5

Proposed lock-candidate wording: Automation may prepare evidence for human
review only when separately authorized; it may not approve gates.

Source sketch: WP-S2c-97 permanent human gate preservation sketch and
`docs/architecture/LONG_TERM_SCOPE.md`.

Preservation note: Confirms automation is evidence-preparation only and not
approval authority.

### HG-6

Proposed lock-candidate wording: Future implementation must preserve explicit
human approval records wherever human gates apply.

Source sketch: WP-S2c-97 permanent human gate preservation sketch.

Preservation note: Confirms approval records remain part of the protected
human-gate surface.

## 8. Drift-rejection lock-candidate criteria

### DR-1

Proposed lock-candidate wording: Reject criteria wording that implies
automatic approval.

Source sketch: WP-S2c-97 permanent human gate preservation sketch.

Preservation note: This pattern detects and rejects drift rather than
automating or bypassing approval.

### DR-2

Proposed lock-candidate wording: Reject parity pass interpreted as automatic
paper readiness.

Source sketch: WP-S2c-97 permanent human gate preservation sketch.

Preservation note: This pattern detects and rejects drift rather than
automating or bypassing shadow-to-paper approval.

### DR-3

Proposed lock-candidate wording: Reject D2-006 pass interpreted as automatic
shadow promotion.

Source sketch: WP-S2c-97 permanent human gate preservation sketch.

Preservation note: This pattern detects and rejects drift rather than
automating or bypassing research-to-shadow approval.

### DR-4

Proposed lock-candidate wording: Reject REC-5 floor crossing interpreted as
candidate approval.

Source sketch: WP-S2c-97 permanent human gate preservation sketch.

Preservation note: This pattern detects and rejects drift rather than
automating or bypassing candidate-level human approval.

### DR-5

Proposed lock-candidate wording: Reject dashboard, monitor, or report output
treated as authority.

Source sketch: WP-S2c-97 permanent human gate preservation sketch.

Preservation note: This pattern detects and rejects drift rather than
allowing visibility surfaces to bypass human gates.

### DR-6

Proposed lock-candidate wording: Reject score, rank, or recommendation treated
as promotion authority.

Source sketch: WP-S2c-97 permanent human gate preservation sketch.

Preservation note: This pattern detects and rejects drift rather than
allowing advisory outputs to become promotion authority.

### DR-7

Proposed lock-candidate wording: Reject any agentic execution of a human gate.

Source sketch: WP-S2c-97 permanent human gate preservation sketch.

Preservation note: This pattern detects and rejects drift rather than
allowing agents to execute gates.

### DR-8

Proposed lock-candidate wording: Reject any risk parameter or kill decision
automated without explicit locked authority.

Source sketch: WP-S2c-97 permanent human gate preservation sketch.

Preservation note: This pattern detects and rejects drift rather than
automating risk or kill decisions.

### DR-9

Proposed lock-candidate wording: Reject any permanent human gate converted
into an advisory-only step.

Source sketch: WP-S2c-97 permanent human gate preservation sketch.

Preservation note: This pattern detects and rejects drift rather than
weakening permanent human gates.

## 9. Consolidation gaps / deferred items

The following decisions remain unresolved and are not resolved by this
consolidation:

- Exact D2-006 relationship for research-to-shadow criteria: direct pass
  evidence, gate-by-gate documentation, or narrower reference to D2-006 as
  source of truth.
- Exact research-to-shadow human approval record.
- Exact shadow-window completion evidence for shadow-to-paper criteria.
- Exact shadow-to-paper human approval record.
- Whether candidate-level readiness can be locked now or requires further
  design.
- Source-language ambiguity: WP-S2c-95 and WP-S2c-96 intentionally sketch
  several items as "may need to decide" surfaces, so proposed wording can
  preserve the design surface but cannot lock final evidence form without
  later Karl/Main resolution.

## 10. Non-claims and forbidden authority

This package proposes lock-candidate wording but locks no criteria.

No criteria selection is made.

No readiness determination is made.

No transition is authorized.

No implementation is authorized.

No human gate is modified, automated, weakened, bypassed, replaced, or
reinterpreted.

No runtime/protected path is touched.

No downstream authority is created.

## 11. Required next authority

After merge, Side must surface the consolidated lock-candidate content to
Main/Karl/user.

No criteria-locking WP may be drafted until Main/Karl explicitly resolves
which criteria lock, with what wording/thresholds, and confirms
permanent-human-gate preservation.

The actual criteria-locking decision package, if authorized later, is expected
to be T1-doc-major-decision with full pytest.

## 12. Validation posture

Validation profile: CS12 T1-doc-narrow.

Full pytest is not required unless repo guidance or a stop trigger requires
escalation.
