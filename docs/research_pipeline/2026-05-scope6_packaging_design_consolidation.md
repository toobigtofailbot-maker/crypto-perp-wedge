# Scope 6 Packaging Design Consolidation

## 1. Scope

WP-S2c-112 / WP-12er is a Tier 1 documentation-only consolidation package.

It consolidates WP-S2c-111 sketches into proposed lock-candidate wording for the three deferred Scope 6 packaging items:

- research-to-shadow approval-record artifact location/schema;
- shadow-evidence retention location/artifact grammar;
- shadow-to-paper approval-record artifact location/schema.

It creates only this document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-narrow.

No packaging decision is locked or selected by this consolidation.

WP-S2c-113 remains hard-gated. It cannot be drafted until this consolidated content is surfaced into chat and Main/Karl resolves each item.

## 2. Repo-truth basis

WP-S2c-111 is merged.

WP-S2c-110 checkpointed the bounded shadow adapter + parity tooling implementation tranche.

WP-S2c-100 locked approval/readiness criteria and deferred three packaging points outside criteria locking.

WP-S2c-104 deferred the same Scope 6 packaging/schema/artifact questions outside the authorization decision.

WP-S2c-100 locked refined items 2, 3, and 4 remain the required-content baseline:

- R2S-5 refined approval record;
- S2P-3 refined shadow-window evidence;
- S2P-6 refined approval record.

Permanent human gates, Tier 4 boundaries, D2-006, D2-007, REC-5, Phase 9, WP-S2c-100 locked criteria, SignalProvider Protocol, and Phase 1 paper runtime protection remain unchanged.

## 3. Consolidation source

This document consumes WP-S2c-111 and does not introduce new packaging families beyond the three Scope 6 items.

Wording is consolidated for clarity and lock-candidate review only.

If any tension is identified, it must be surfaced rather than silently resolved.

## 4. Consolidated lock-candidate summary

| Item | Proposed lock-candidate location posture | Schema-shape posture | Validator posture | Authority posture |
|---|---|---|---|---|
| R2S approval-record artifact | PROPOSED / NOT LOCKED: dedicated approval-record artifact family under research artifacts, with R2S as a distinct record type/subfamily. | Documentation-level skeleton derived from R2S-5 refined approval-record content. | Future additive validator checks required fields and non-authority statements only. | Human decision record only; no readiness, approval automation, promotion, transition, or gate execution authority. |
| Shadow-evidence retention artifact | PROPOSED / NOT LOCKED: dedicated shadow-evidence retention family under research artifacts, separate from current local non-canonical tool output. | Documentation-level skeleton derived from S2P-3 refined shadow-window evidence. | Future additive validator checks threshold-field presence, lineage references, disclosure structure, and non-authority statements only. | Human-review evidence only; no readiness, paper-transition, ranking, scoring, recommendation, or gate execution authority. |
| S2P approval-record artifact | PROPOSED / NOT LOCKED: structurally similar approval-record artifact family under research artifacts, with S2P as a distinct record type/subfamily. | Documentation-level skeleton derived from S2P-6 refined approval-record content. | Future additive validator checks required fields and preservation statements only. | Human decision record only; no paper transition, paper runtime invocation, approval automation, or gate execution authority. |

## 5. Lock-candidate 1 — research-to-shadow approval-record artifact

Proposed lock-candidate wording:

The research-to-shadow approval record should be packaged as a dedicated approval-record artifact family under research artifacts, with R2S as a distinct record type or subfamily. This is PROPOSED / NOT LOCKED. If Main/Karl prefers the WP-S2c-111 lifecycle/review-family alternative, WP-S2c-113 must record that modification explicitly before any schema work.

Schema-shape skeleton, documentation level only, derived from R2S-5 refined approval record:

- candidate identity;
- strategy or candidate family where repo truth supports that wording;
- evidence snapshot references;
- D2-006 gate pass evidence reference or attestation;
- REC-5 exact-segment evidence list or reference;
- explicit statement that no cross-segment inference is used below the REC-5 floor;
- approver identity;
- approval timestamp/date;
- decision outcome;
- explicit confirmation that permanent human gates, D2-006, D2-007, REC-5, and Phase 9 semantics remain preserved;
- explicit statement that the record is required before transition but does not itself implement transition machinery.

Retention/lineage posture:

- stable references to exact evidence snapshots;
- immutable-style posture after human decision, if later locked;
- no runtime dependency.

Validator posture:

- validator checks required fields and non-authority statements only;
- validator cannot approve, promote, transition, or execute gates.

Preservation note:

The R2S approval record documents a human decision only. It does not make a candidate ready. It does not authorize or implement transition.

## 6. Lock-candidate 2 — shadow-evidence retention artifact

Proposed lock-candidate wording:

The shadow-evidence retention artifact should be packaged as a dedicated shadow-evidence retention family under research artifacts, separate from current local non-canonical tool output. This is PROPOSED / NOT LOCKED. If Main/Karl prefers the WP-S2c-111 general evidence-retention subfamily alternative, WP-S2c-113 must record that modification explicitly before any schema work.

Schema-shape skeleton, documentation level only, derived from S2P-3 refined shadow-window evidence:

- candidate identity;
- shadow-window start/end;
- D2-007 minimum shadow window of at least 14 calendar days;
- D2-007 parity thresholds of PnL deviation no more than 10% and trade-count deviation no more than 5%;
- actual parity result evidence or attestation;
- clean lineage to shadow observation/evidence used in review;
- disclosure of interruptions, invalid observations, missing data, or observation resets;
- evidence retention/reference sufficient for human review;
- mismatch diagnostics, if present, marked decision-support only and not ranking/scoring/recommendation/transition logic.

Retention/lineage posture:

- current shadow adapter/parity/evidence outputs may inform future canonical evidence, but current outputs remain non-canonical;
- retained evidence must be traceable to observations and parity computations;
- final retention policy and artifact grammar are proposed here only and require WP-S2c-113 locking before schemas.

Validator posture:

- validator checks D2-007 threshold field presence, lineage references, disclosure structure, and non-authority statements;
- validator cannot determine readiness or paper transition.

Preservation note:

Shadow evidence supports human review only. Parity pass and disclosure completeness are not readiness or transition authority.

## 7. Lock-candidate 3 — shadow-to-paper approval-record artifact

Proposed lock-candidate wording:

The shadow-to-paper approval record should use structural similarity with the R2S approval-record artifact where safe, with S2P as a distinct record type or subfamily under the same dedicated approval-record artifact family. This is PROPOSED / NOT LOCKED. If Main/Karl prefers the WP-S2c-111 lifecycle/review-family alternative, WP-S2c-113 must record that modification explicitly before any schema work.

Schema-shape skeleton, documentation level only, derived from S2P-6 refined approval record:

- candidate identity;
- shadow-window evidence reference;
- D2-007 parity result reference or attestation;
- interruption or invalid-observation disclosure reference;
- paper runtime protection confirmation;
- approver identity;
- approval timestamp/date;
- decision outcome;
- explicit confirmation that permanent human gates, D2-007, Phase 1 paper runtime protection, and Tier 4 boundaries remain preserved;
- explicit statement that the record is required before transition but does not itself implement transition machinery.

Retention/lineage posture:

- stable reference to canonical shadow-evidence retention artifact, if later locked;
- immutable-style human decision record posture, if later locked;
- no paper runtime dependency.

Validator posture:

- validator checks required fields and preservation statements only;
- validator cannot invoke paper runtime, approve transition, or execute gates.

Preservation note:

The S2P approval record documents a human decision only. It does not authorize paper transition or paper runtime contact.

## 8. Cross-item consistency

R2S and S2P approval records should be structurally similar where safe.

Shadow-evidence retention should be referenceable from S2P approval records.

All three proposed artifact families should include explicit non-automation/non-transition statements.

All future schema/validator surfaces must preserve human-gate semantics.

Schema naming/location should minimize future duplication while preserving distinct R2S, shadow-evidence, and S2P semantics.

## 9. Validator-surface consolidation

Future validators are additive only.

Validators enforce schema/content only after WP-S2c-114 introduces schemas.

Validators do not create artifacts.

Validators do not grant readiness, approval, transition, promotion, scoring, ranking, recommendation, policy, or human-gate authority.

Validators must preserve locked criteria and human-gate semantics.

## 10. Preservation notes

- Permanent human gates remain absolute.
- Tier 4 remains absolute.
- D2-006 remains unchanged.
- D2-007 remains unchanged.
- REC-5 exact-segment discipline remains unchanged.
- Phase 9 and WP-S2c-100 locked criteria remain unchanged.
- SignalProvider Protocol remains unchanged.
- Phase 1 paper runtime protection remains unchanged.
- Monitoring/dashboard remains deferred.
- Paper bridge remains unauthorized.
- AUTO bridge remains frozen; A2C-003 and Path B remain unauthorized.

## 11. Decision questions for Main/Karl

After merge, Side must surface this section into chat.

For each Scope 6 item, Main/Karl must mark LOCK / MODIFY / DEFER / REJECT.

For the R2S approval-record artifact, Main/Karl must resolve:

- artifact location;
- schema-shape skeleton;
- retention/lineage posture;
- validator surface;
- preservation note.

For the shadow-evidence retention artifact, Main/Karl must resolve:

- artifact location;
- schema-shape skeleton;
- retention/lineage posture;
- validator surface;
- preservation note.

For the S2P approval-record artifact, Main/Karl must resolve:

- artifact location;
- schema-shape skeleton;
- retention/lineage posture;
- validator surface;
- preservation note.

## 12. What this consolidation does not authorize

This consolidation does not authorize:

- locking or selecting packaging decisions;
- schema file creation;
- validator implementation;
- artifact instance creation;
- canonical artifact creation;
- transition authorization;
- candidate readiness determination;
- human-gate execution;
- Tier 4 contact;
- runtime/protected-path changes;
- query-layer changes;
- monitoring/dashboard/paper bridge;
- AUTO bridge, A2C-003, Path B;
- WP-S2c-113 drafting before Main/Karl resolution.

## 13. Required next authority

After WP-S2c-112 merges, Side must stop.

Side must surface the consolidated lock-candidate content from this document into chat.

Main/Karl must resolve each Scope 6 item against verified content.

Side must not draft WP-S2c-113 until the per-item LOCK/MODIFY/DEFER/REJECT resolution exists in chat.

If Main/Karl modifies any item, WP-S2c-113 must use the resolved wording, not the unmodified consolidation wording.

## 14. Validation / next-package posture

WP-S2c-112 uses CS12 T1-doc-narrow.

WP-S2c-113 is T1-doc-major-decision with full pytest, but is hard-gated and not auto-drafted by this package.

WP-S2c-114 and WP-S2c-115 remain downstream and unavailable until WP-S2c-113 merges.
