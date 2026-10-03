# Approval/Readiness Criteria Locking Decision

## V2 prospective supersession

`D2-020` prospectively supersedes HG-1, HG-4, HG-5, and generic go/no-go
wording only where they would prohibit autonomous legal in-envelope research
lifecycle work after Stage 5B is implemented, validated, explicitly activated,
and a valid Karl-approved envelope exists. Until then, the current restrictions
remain operational.

HG-1/HG-4/HG-5 remain controlling for candidate approval, promotion,
readiness, transition, paper/live, and economic human gates. An automated
non-candidate research disposition is not rejection, promotion, readiness, or
a lifecycle transition. The controlling detail is
`docs/architecture/2026-10-bounded_autonomous_research_v2_architecture.md`.

## 1. Scope

WP-S2c-100 / WP-12eg is a Tier 1 documentation-only major-decision package.

It locks approval/readiness criteria in repo truth.

This package creates only this document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-major-decision. Full pytest is required.

This package does not authorize transition, implementation, runtime/protected-path work, or candidate readiness determination.

## 2. Repo-truth basis

WP-12ef / WP-S2c-99-refine is merged.

WP-S2c-94 through WP-S2c-99-refine documents exist.

WP-S2c-99-pre consolidated proposed lock-candidate wording.

WP-S2c-99-refine resolved the five deferred criteria decisions as proposed lock-candidate wording.

Main/Karl resolved all five refined items as LOCK as-written.

Main/Karl resolved all remaining G/R2S/S2P/HG/DR items as LOCK as-written.

Deferred packaging points do not block the locking package and remain outside WP-S2c-100.

Permanent human gates remain absolute.

D2-006, D2-007, REC-5, Phase 9 Decision 9, Phase 9 Decision 6, tiered-promotion, human-approval semantics, and permanent human gates remain locked and unmodified.

Path B, A2C-003, Phase 3 transition, Phase 3 implementation, AUTO bridge further work, approval/readiness/lifecycle, policy/scoring/ranking/recommendation, runtime, paper/live, exchange/broker/order contact, and downstream authority remain unauthorized.

## 3. Decision authority and resolution source

Main/Karl explicitly resolved:

- all global criteria G-1 through G-5: LOCK as-written;
- all R2S criteria R2S-1 through R2S-6, including refined R2S items: LOCK as-written;
- all S2P criteria S2P-1 through S2P-7, including refined S2P items: LOCK as-written;
- all HG criteria HG-1 through HG-6: LOCK as-written;
- all DR criteria DR-1 through DR-9: LOCK as-written;
- refined candidate-level readiness item: LOCK as-written.

No MODIFY, DEFER, or REJECT resolution exists for criteria content.

Deferred packaging points are explicitly deferred outside WP-S2c-100 and do not block criteria locking.

## 4. Locked global criteria

G-1: Approval/readiness criteria become governing gates only after explicit Karl approval; until then they remain sketches.

Preservation note: Preserves the requirement that criteria become governing only through explicit Main/Karl locking authority.

G-2: Locked approval/readiness criteria may inform human review, but may not replace, bypass, automate, weaken, or reinterpret human approval.

Preservation note: Preserves permanent human gates as absolute and human-controlled.

G-3: No approval/readiness criterion may create automatic transition, promotion, demotion, lifecycle, paper, live, risk-change, or kill authority.

Preservation note: Preserves the non-automation boundary and prevents criteria from becoming self-executing authority.

G-4: Criteria locking itself does not make any candidate ready and does not determine candidate readiness.

Preservation note: Preserves the difference between locked review criteria and a later candidate-specific human readiness decision.

G-5: Criteria locking does not authorize Phase 3 implementation, runtime, paper/live, exchange/broker/order, or Tier 4 contact.

Preservation note: Preserves protected runtime, paper/live, exchange/broker/order, and Tier 4 boundaries.

## 5. Locked research-to-shadow criteria

R2S-1: Research-to-shadow eligibility requires direct evidence that the candidate passed all D2-006 promotion gates. D2-006 remains the locked source of truth for the gates, thresholds, and semantics. Research-to-shadow criteria should reference D2-006 as the locked source of truth and require a D2-006 pass evidence reference or attestation, rather than restating or locally rewriting the D2-006 gate text. Research-to-shadow criteria may add review-context requirements needed to preserve REC-5 exact-segment discipline and permanent human approval, but may not add local tightening or weakening of D2-006 gate thresholds. No D2-006 gate is locally tightened.

Preservation note: D2-006 remains locked and unmodified; D2-006 pass evidence is prerequisite evidence, not automatic shadow promotion.

R2S-2: REC-5 evidence used for readiness review must remain exact-segment evidence under `candidate_id / outcome_kind / pipeline_version / expectation_source_type`; no pooled candidate evidence or cross-segment aggregation may be used.

Preservation note: Preserves REC-5 exact-segment discipline and rejects pooled candidate-level inference.

R2S-3: Segment-level REC inference requires at least 3 reconciliations per exact segment before drawing segment-level inference.

Preservation note: Preserves the REC-5 floor and does not create cross-segment inference below that floor.

R2S-4: Broad-floor-crossing evidence may be descriptive input to human readiness review, but it is not automatic approval, candidate-specific readiness, or a substitute for a later human decision.

Preservation note: Preserves broad-floor-crossing sufficiency as descriptive gating input only.

R2S-5 base: Any research-to-shadow transition requires a human approval decision before transition.

Preservation note: Preserves shadow promotion as a permanent human gate.

R2S-5 refined approval record: Before any research-to-shadow transition, a human approval record must exist and must document, at minimum, the candidate identity; strategy or candidate family where repo truth supports that wording; evidence snapshot references; D2-006 gate pass evidence reference or attestation; REC-5 exact-segment evidence list or reference; explicit statement that no cross-segment inference is used below the REC-5 floor; approver identity; approval timestamp/date; decision outcome; explicit confirmation that permanent human gates, D2-006, D2-007, REC-5, and Phase 9 semantics remain preserved; and explicit statement that the record is required before transition but does not itself implement transition machinery.

Preservation note: The record documents a human decision; it does not automate approval or implement transition machinery.

R2S-6 base: Candidate-level readiness remains unresolved unless and until Karl locks how exact-segment evidence, D2-006 evidence, qualitative review, and human approval combine without violating REC-5 floor discipline.

Preservation note: Preserves the prior boundary that per-segment evidence cannot silently become candidate-level readiness approval.

Candidate-level readiness refined: Candidate-level readiness review may use exact-segment REC-5 evidence only as bounded evidence input under `candidate_id / outcome_kind / pipeline_version / expectation_source_type`. It may not use cross-segment inference below the REC-5 floor and may not convert broad-floor-crossing sufficiency into candidate-specific readiness. For research-to-shadow review, candidate-level readiness requires D2-006 pass evidence as a prerequisite and human approval before any transition. For shadow-to-paper review, where applicable, candidate-level readiness requires D2-007 shadow-window and parity evidence as review input and human approval before any transition. This criterion does not declare any candidate ready.

Preservation note: Candidate readiness cannot bypass permanent human gates or arise automatically from exact-segment evidence, D2-006 pass, D2-007 parity pass, or broad-floor-crossing sufficiency.

## 6. Locked shadow-to-paper criteria

S2P-1: Shadow-to-paper readiness review must preserve the D2-007 minimum shadow window of at least 14 calendar days.

Preservation note: Preserves D2-007 shadow-window discipline without changing the threshold.

S2P-2: D2-007 parity thresholds remain PnL deviation no more than 10% and trade count deviation no more than 5% during the shadow window.

Preservation note: Preserves D2-007 parity thresholds without modification.

S2P-3 refined shadow-window evidence: Shadow-to-paper review requires shadow-window completion evidence showing the D2-007 minimum shadow window of at least 14 calendar days; D2-007 parity thresholds of PnL deviation no more than 10% and trade count deviation no more than 5%; clean lineage to the shadow observation/evidence used in review; disclosure of interruptions, invalid observations, missing data, or observation resets; parity result evidence or attestation; and evidence retention/reference sufficient for human review. Mismatch diagnostics may support human review only as decision support and cannot become ranking, scoring, recommendation, or transition logic.

Preservation note: D2-007 remains locked; shadow-window and parity evidence support human review only and do not authorize paper transition.

S2P-4: Passing parity may support human review but cannot automatically authorize paper transition.

Preservation note: Preserves parity as decision-support evidence only.

S2P-5: Mismatch diagnostics may be decision-support evidence only; they cannot become ranking, scoring, recommendation, or automated paper-transition logic.

Preservation note: Preserves the prohibition on policy, scoring, ranking, recommendation, and automated transition authority.

S2P-6 base: Any shadow-to-paper transition requires a human approval decision before paper transition.

Preservation note: Preserves transition authority as human-controlled.

S2P-6 refined approval record: Before any shadow-to-paper transition, a human approval record must exist and must document, at minimum, the candidate identity; shadow-window evidence reference; D2-007 parity result reference or attestation; interruption or invalid-observation disclosure reference; paper runtime protection confirmation; approver identity; approval timestamp/date; decision outcome; explicit confirmation that permanent human gates, D2-007, Phase 1 paper runtime protection, and Tier 4 boundaries remain preserved; and explicit statement that the record is required before transition but does not itself implement transition machinery.

Preservation note: The record documents a human decision; it does not automate approval or implement transition machinery.

S2P-7: Paper runtime protection remains non-negotiable; criteria locking does not authorize paper-runtime implementation, paper bridge implementation, paper bridge invocation, or paper/live contact.

Preservation note: Preserves Phase 1 paper runtime protection and protected paper/live boundaries.

## 7. Locked human-gate preservation criteria

HG-1: Permanent human gates remain human-controlled for hypothesis approval, decision records/go/no-go, shadow promotion, live promotion, risk parameter changes, kill decisions, and novel strategy-family introduction.

Preservation note: Explicitly confirms all permanent human gates listed in repo truth.

HG-2: Approval/readiness criteria may inform human review but cannot replace human approval.

Preservation note: Confirms human approval remains required wherever human gates apply.

HG-3: Approval/readiness criteria cannot create automatic transition authority.

Preservation note: Confirms transition decisions remain human-controlled.

HG-4: Approval/readiness criteria cannot become a self-executing promotion, demotion, or lifecycle mechanism.

Preservation note: Confirms criteria cannot become lifecycle automation.

HG-5: Automation may prepare evidence for human review only when separately authorized; it may not approve gates.

Preservation note: Confirms automation is evidence-preparation only and not approval authority.

HG-6: Future implementation must preserve explicit human approval records wherever human gates apply.

Preservation note: Confirms approval records remain part of the protected human-gate surface.

## 8. Locked drift-rejection criteria

DR-1: Reject criteria wording that implies automatic approval.

Preservation note: Rejects wording drift that would bypass human approval.

DR-2: Reject parity pass interpreted as automatic paper readiness.

Preservation note: Rejects drift from D2-007 parity evidence into paper-transition authority.

DR-3: Reject D2-006 pass interpreted as automatic shadow promotion.

Preservation note: Rejects drift from D2-006 pass evidence into research-to-shadow promotion authority.

DR-4: Reject REC-5 floor crossing interpreted as candidate approval.

Preservation note: Rejects drift from exact-segment evidence into candidate-level approval.

DR-5: Reject dashboard, monitor, or report output treated as authority.

Preservation note: Rejects drift that would let visibility surfaces bypass human gates.

DR-6: Reject score, rank, or recommendation treated as promotion authority.

Preservation note: Rejects drift that would let advisory outputs become promotion authority.

DR-7: Reject any agentic execution of a human gate.

Preservation note: Rejects drift that would let agents execute gates.

DR-8: Reject any risk parameter or kill decision automated without explicit locked authority.

Preservation note: Rejects drift that would automate risk or kill decisions without separate locked authority.

DR-9: Reject any permanent human gate converted into an advisory-only step.

Preservation note: Rejects drift that would weaken permanent human gates.

## 9. Locked refined criteria

The five refined WP-S2c-99-refine items are locked as-written and are recorded above in the relevant criteria sections:

- refined D2-006 relationship locks as-written in R2S-1;
- refined R2S approval-record content locks as-written in R2S-5 refined approval record;
- refined shadow-window evidence locks as-written in S2P-3 refined shadow-window evidence;
- refined S2P approval-record content locks as-written in S2P-6 refined approval record;
- refined candidate-level readiness lockability locks as-written in Candidate-level readiness refined.

This reference block avoids duplicating the already-recorded locked criteria text. The same non-authority boundaries apply: no candidate is declared ready, no transition is authorized, and no implementation machinery is created.

## 10. Deferred packaging points

Approval-record artifact location/schema for research-to-shadow is deferred outside WP-S2c-100.

Shadow-evidence retention location/artifact grammar is deferred outside WP-S2c-100.

Approval-record artifact location/schema for shadow-to-paper is deferred outside WP-S2c-100.

These deferrals do not block criteria locking.

Future work on these points requires separate authorization and may require schema/artifact/package planning.

WP-S2c-100 does not create any schema, artifact path, directory, validator, query, bridge, runtime, config, dependency, or data change.

## 11. What this locking decision changes

The listed approval/readiness criteria become locked repo-truth criteria for future human review and future authorized packages.

The criteria define what evidence and boundaries must be preserved before any future human readiness/transition review.

The criteria bind future design and implementation packages to preserve D2-006, D2-007, REC-5, Phase 9 semantics, permanent human gates, and protected runtime/Tier 4 boundaries.

## 12. What this locking decision does not authorize

This locking decision does not authorize:

- candidate readiness determination;
- research-to-shadow transition;
- shadow-to-paper transition;
- paper-to-live or live transition;
- Phase 3 implementation;
- shadow adapter, parity tooling, monitoring/dashboard, paper bridge, live trading, runtime, paper/live, exchange/broker/order, or Tier 4 contact;
- runtime / paper-live / OMS / reconciliation / risk / safe-mode / kill-switch / event-log schema / SignalProvider / config / dependency / data / protected-path changes;
- D2-006, D2-007, REC-5, Phase 9 Decision 9, Phase 9 Decision 6, tiered-promotion, human-approval semantics, or permanent-human-gate modification;
- human-gate automation, bypass, weakening, replacement, or reinterpretation;
- cross-segment inference under REC-5 floor;
- performance ranking/scoring/recommendation authority;
- AUTO bridge further work;
- A2C-003 or Path B work except as deferred context;
- lifecycle, promotion, demotion, archive, or approval/readiness action;
- downstream authority.

## 13. Required next authority

After merge, Side must report back to Main/Karl/user for post-locking direction.

No post-locking package may be auto-drafted until Main/Karl/user selects or explicitly authorizes the next direction.

Possible next directions are strategic only and not selected by this package:

- Phase 3 implementation authorization decision;
- approval-record artifact/schema design;
- shadow-evidence retention/artifact grammar design;
- AUTO bridge canonical-write-path design if separately revived;
- A2C-003;
- Path B;
- hold/defer.

## 14. Validation profile

This package uses CS12 T1-doc-major-decision because it locks approval/readiness criteria and creates a major boundary decision.

Full pytest is required.

## 15. Validation

Pre-edit verification confirmed:

- PR #281 / WP-12ef is merged at `29ffe3c`.
- Refreshed `main` includes the WP-12ef merge.
- `docs/project_status.md` records WP-12ef / WP-S2c-99-refine as the latest branch-state before this package.
- No open PR was reported.
- No remote or local `codex/wp-12eg-approval-readiness-criteria-locking` branch was found before this package branch.
- No WP-12eg / WP-S2c-100 PR was found before drafting.
- Searches for WP-12eg, WP-S2c-100, and approval readiness criteria locking found no started or merged criteria-locking package.
- This locking decision document did not exist before this package.
- WP-S2c-94 through WP-S2c-99-refine source documents exist.
- Main/Karl's resolution is available in handoff context: all criteria groups and five refined items are LOCK as-written, and deferred packaging points do not block WP-S2c-100.
- Path B, A2C-003, Phase 3 transition, Phase 3 implementation, AUTO bridge further work, approval/readiness/lifecycle, policy/scoring/ranking/recommendation, runtime, paper/live, exchange/broker/order contact, and downstream authority remain unauthorized.
- No schema, validator, central query-layer, committed-state test, config, dependency, data, runtime, protected-path, bridge-code, bridge-output, D2-006, D2-007, REC-5, Phase 9, tiered-promotion, human-approval, permanent-human-gate, event-log schema, or SignalProvider modification is required.

Package validation results are recorded in the execution report-back and PR.
