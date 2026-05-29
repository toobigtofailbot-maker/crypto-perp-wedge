# Scope 6 Packaging Design Opening

## 1. Scope

WP-S2c-111 / WP-12eq is a Tier 1 documentation-only design-opening package.

It opens the Scope 6 packaging resolution tranche.

It sketches options for the three deferred packaging questions only:

- research-to-shadow approval-record artifact location/schema;
- shadow-evidence retention location/artifact grammar;
- shadow-to-paper approval-record artifact location/schema.

It creates only this document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-narrow.

No packaging decision is locked or selected by this opening.

## 2. Repo-truth basis

WP-S2c-110 is merged and checkpointed the shadow adapter + parity tooling implementation tranche.

WP-S2c-105 through WP-S2c-109 are complete.

WP-S2c-100 locked approval/readiness criteria and deferred three packaging points outside the criteria-locking decision.

WP-S2c-104 deferred the same Scope 6 packaging/schema/artifact questions outside the authorization decision.

WP-S2c-110 records local shadow evidence as advisory-only, non-canonical, and decision-support-only.

Permanent human gates, Tier 4 boundaries, D2-006, D2-007, REC-5, Phase 9, WP-S2c-100 locked criteria, SignalProvider Protocol, and Phase 1 paper runtime protection remain unchanged.

## 3. Source deferred questions

The Scope 6 items are:

1. approval-record artifact location/schema for research-to-shadow;
2. shadow-evidence retention location/artifact grammar;
3. approval-record artifact location/schema for shadow-to-paper.

These were deferred in WP-S2c-100 and WP-S2c-104. They remain unresolved until the later WP-S2c-113 locking decision.

## 4. Tranche sequence

- WP-S2c-111: opening + per-item sketches.
- WP-S2c-112: consolidation into lock-candidate wording.
- Mandatory stop after WP-S2c-112: Side surfaces consolidated content to Main/Karl.
- WP-S2c-113: Karl-gated Scope 6 packaging locking decision, T1-doc-major-decision, full pytest.
- WP-S2c-114: schema files introduction, T3-implementation, full pytest.
- WP-S2c-115: validator implementation, T3-implementation, full pytest.
- Mandatory Main re-engagement after WP-S2c-115.

## 5. Design principles

- Packaging records and schemas support human review; they do not approve, transition, or promote.
- Approval records document human decisions; they do not automate gates.
- Shadow evidence supports human review only; it is not readiness or transition authority.
- Validators enforce required content only; validators do not approve or execute gates.
- Artifact shapes must preserve exact-segment REC-5 discipline where relevant.
- D2-006 and D2-007 remain source-of-truth criteria and thresholds.
- Tier 4 and protected runtime boundaries remain absolute.
- No candidate-specific readiness is determined in this tranche.

## 6. Sketch 1 — research-to-shadow approval-record artifact

Candidate artifact-family purpose: canonical human approval record required before any future research-to-shadow transition.

Proposed artifact-location options, not locked:

- Option R2S-A: future dedicated approval-record family under research artifacts, with a separate subfamily for research-to-shadow approval records.
- Option R2S-B: future lifecycle/review artifact family under research artifacts, with record type distinguishing research-to-shadow approval records from other human decision records.

Proposed schema-shape skeleton, documentation level only, derived from locked R2S-5 refined approval record:

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

Proposed retention/lineage approach:

- stable reference from any later human review to exact evidence snapshot references;
- immutable-style record posture after human decision, if later locked;
- no runtime dependency.

Proposed validator surface:

- future validator checks required fields and non-authority statements only;
- validator must not approve, promote, or transition.

## 7. Sketch 2 — shadow-evidence retention artifact

Candidate artifact-family purpose: canonical retention/reference for shadow-window completion evidence used in later human shadow-to-paper review.

Proposed artifact-location options, not locked:

- Option SE-A: future dedicated shadow-evidence retention family under research artifacts, separate from current local non-canonical tool output.
- Option SE-B: future evidence-retention subfamily that can be referenced by later shadow-to-paper approval records without becoming a transition authority surface.

Proposed schema-shape skeleton, documentation level only, derived from locked S2P-3 refined shadow-window evidence:

- candidate identity;
- shadow-window start/end;
- D2-007 minimum shadow window of at least 14 calendar days;
- D2-007 parity thresholds of PnL deviation no more than 10% and trade-count deviation no more than 5%;
- actual parity result evidence or attestation;
- clean lineage to shadow observation/evidence used in review;
- disclosure of interruptions, invalid observations, missing data, or observation resets;
- evidence retention/reference sufficient for human review;
- mismatch diagnostics, if present, marked decision-support only and not ranking/scoring/recommendation/transition logic.

Proposed retention/lineage approach:

- local shadow adapter/parity/evidence outputs may inform future canonical evidence, but the current implementation remains non-canonical;
- retained evidence must be traceable to observations and parity computations;
- final retention policy and artifact grammar remain not locked in this package.

Proposed validator surface:

- future validator checks D2-007 threshold field presence, lineage references, disclosure structure, and non-authority statements;
- validator must not determine readiness or paper transition.

## 8. Sketch 3 — shadow-to-paper approval-record artifact

Candidate artifact-family purpose: canonical human approval record required before any future shadow-to-paper transition.

Proposed artifact-location options, not locked:

- Option S2P-A: future dedicated approval-record family under research artifacts, with a separate subfamily for shadow-to-paper approval records.
- Option S2P-B: future lifecycle/review artifact family under research artifacts, with record type distinguishing shadow-to-paper approval records from other human decision records.

Proposed schema-shape skeleton, documentation level only, derived from locked S2P-6 refined approval record:

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

Proposed retention/lineage approach:

- stable reference to canonical shadow-evidence retention artifact, if later locked;
- immutable-style human decision record posture, if later locked;
- no paper runtime dependency.

Proposed validator surface:

- future validator checks required fields and preservation statements only;
- validator must not invoke paper runtime, approve transition, or execute gates.

## 9. Cross-item consistency notes

- R2S and S2P approval records should be structurally similar where safe.
- Shadow-evidence retention should be referenceable from S2P approval records.
- All three artifact families should carry explicit non-automation/non-transition statements.
- All future schema/validator surfaces must preserve human-gate semantics.

## 10. Validator-surface sketch

Future validators are additive only.

WP-S2c-115 will implement validators only after WP-S2c-114 introduces locked schemas.

Validators enforce structure/content only.

Validators do not create artifacts and do not grant readiness or transition authority.

## 11. Boundary preservation

- Permanent human gates remain absolute.
- Tier 4 remains absolute.
- No transition authorization is created.
- No candidate readiness determination is created.
- No runtime/protected-path work is authorized.
- No monitoring/dashboard/paper bridge work is authorized.
- Paper bridge remains unauthorized.
- Scope 6 items remain sketches until WP-S2c-113.

## 12. What this opening does not authorize

This opening does not authorize:

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
- AUTO bridge, A2C-003, or Path B.

## 13. Validation / next-package posture

WP-S2c-111 uses CS12 T1-doc-narrow.

After merge, Side may auto-draft WP-S2c-112 after refreshed-main preflight and no stop trigger.

WP-S2c-112 consolidates sketches into proposed lock-candidate wording.

After WP-S2c-112 merges, Side must surface consolidated content to Main/Karl and must not draft WP-S2c-113 until per-item resolution occurs in chat.
