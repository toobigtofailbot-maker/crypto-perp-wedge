# Scope 6 Packaging Locking Decision

## 1. Scope

WP-S2c-113 / WP-12es is a Tier 1 documentation-only major-decision package.

It locks the Scope 6 packaging decisions for the three items consolidated in WP-S2c-112:

- research-to-shadow approval-record artifact;
- shadow-evidence retention artifact;
- shadow-to-paper approval-record artifact.

It creates only this document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-major-decision. Full pytest is required.

This package creates no schema files, validators, artifact instances, canonical artifacts, query-layer changes, runtime changes, transition authority, candidate readiness determination, human-gate execution, or Tier 4 contact.

## 2. Repo-truth basis

WP-S2c-112 is merged.

WP-S2c-111 opened the Scope 6 packaging design tranche.

WP-S2c-100 locked approval/readiness criteria and deferred the three packaging points outside criteria locking.

WP-S2c-104 deferred the same Scope 6 packaging/schema/artifact questions outside the authorization decision.

WP-S2c-110 checkpointed the bounded shadow adapter + parity tooling implementation tranche.

WP-S2c-100 locked refined items 2, 3, and 4 remain the required-content baseline:

- R2S-5 refined approval record;
- S2P-3 refined shadow-window evidence;
- S2P-6 refined approval record.

Permanent human gates, Tier 4 boundaries, D2-006, D2-007, REC-5, Phase 9, WP-S2c-100 locked criteria, SignalProvider Protocol, and Phase 1 paper runtime protection remain unchanged.

## 3. Decision authority and resolution source

Side surfaced WP-S2c-112 consolidated content into chat.

Main/Karl reviewed the consolidated content against locked decisions and resolved all three items as LOCK as-written:

- R2S approval-record artifact: LOCK as-written.
- Shadow-evidence retention artifact: LOCK as-written.
- S2P approval-record artifact: LOCK as-written.

There are no MODIFY, DEFER, or REJECT resolutions.

No tension exists between items, locked decisions, or Phase 1 paper runtime protection.

WP-S2c-113 is authorized as a standalone T1-doc-major-decision package with full pytest required.

## 4. Locked decision summary

| Item | Resolution |
|---|---|
| R2S approval-record artifact | LOCK as-written |
| Shadow-evidence retention artifact | LOCK as-written |
| S2P approval-record artifact | LOCK as-written |

## 5. Locked item 1 — research-to-shadow approval-record artifact

The research-to-shadow approval record is packaged as a dedicated approval-record artifact family under research artifacts, with R2S as a distinct record type or subfamily.

Required-content shape is derived from R2S-5 refined approval record and includes:

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
- immutable-style posture after human decision;
- no runtime dependency.

Validator posture:

- future validator checks required fields and non-authority statements only;
- validator cannot approve, promote, transition, or execute gates.

Preservation note:

The R2S approval record documents a human decision only. It does not make a candidate ready. It does not authorize or implement transition.

Main preservation confirmation:

- Required content matches refined item 2.
- G-3, HG-1, HG-3, HG-5, HG-6, DR-1, DR-3, and DR-7 are preserved.

## 6. Locked item 2 — shadow-evidence retention artifact

The shadow-evidence retention artifact is packaged as a dedicated shadow-evidence retention family under research artifacts, separate from current local non-canonical tool output.

Required-content shape is derived from S2P-3 refined shadow-window evidence and includes:

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
- final retention policy and artifact grammar are locked at the artifact-family / required-content level here, with schema-file details landing in WP-S2c-114.

Validator posture:

- future validator checks D2-007 threshold field presence, lineage references, disclosure structure, and non-authority statements;
- validator cannot determine readiness or paper transition.

Preservation note:

Evidence supports human review only. Parity pass and disclosure completeness are not readiness or transition authority.

Main preservation confirmation:

- Required content matches refined item 3.
- S2P-1, S2P-2, S2P-3, S2P-4, S2P-5, DR-2, DR-5, and DR-6 are preserved.

## 7. Locked item 3 — shadow-to-paper approval-record artifact

The shadow-to-paper approval record uses structural similarity with the R2S approval-record artifact where safe, with S2P as a distinct record type or subfamily under the same dedicated approval-record artifact family.

Required-content shape is derived from S2P-6 refined approval record and includes:

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

- stable reference to canonical shadow-evidence retention artifact;
- immutable-style human decision record posture;
- no paper runtime dependency.

Validator posture:

- future validator checks required fields and preservation statements only;
- validator cannot invoke paper runtime, approve transition, or execute gates.

Preservation note:

The S2P approval record documents a human decision only. It does not authorize paper transition or paper runtime contact.

Main preservation confirmation:

- Required content matches refined item 4.
- G-3, HG-1, HG-3, HG-5, HG-6, S2P-6, S2P-7, DR-1, DR-2, and DR-7 are preserved.

## 8. Cross-item consistency

The three locked items form a coherent packaging surface.

Item 1 governs the future R2S human-gate approval record.

Item 2 holds canonical shadow-evidence retention/reference material for later human S2P review.

Item 3 references Item 2 through shadow-window evidence reference.

The three artifact families cover the research-to-shadow-to-paper evidence and approval trail without overlapping with existing canonical artifacts.

The locked packaging creates no execution-adjacent surface.

There is no tension between items, locked criteria, or Phase 1 paper runtime protection.

## 9. Validator and schema posture

No schema files are created in WP-S2c-113.

Schemas land in WP-S2c-114.

No validator implementation is created in WP-S2c-113.

Validators land in WP-S2c-115.

No artifact instances are created in WP-S2c-113, WP-S2c-114, or WP-S2c-115.

Schema-file location and exact format, JSON Schema or equivalent, are resolved in WP-S2c-114 within the locked artifact-family and required-content decisions.

Validator location is resolved in WP-S2c-115 implementation.

Validators enforce required content and non-authority statements only. They do not approve, transition, promote, execute gates, rank, score, recommend, or become policy authority.

## 10. Preservation notes

- Permanent human gates remain absolute.
- Tier 4 boundaries remain absolute.
- D2-006 remains unchanged.
- D2-007 remains unchanged.
- REC-5 exact-segment discipline remains unchanged.
- Phase 9 Decision 9 remains unchanged.
- WP-S2c-100 locked criteria remain unchanged.
- Phase 1 paper runtime protected execution-core remains absolute.
- SignalProvider Protocol remains unchanged.
- Monitoring/dashboard remains deferred.
- Paper bridge remains unauthorized.
- AUTO bridge remains frozen at WP-S2c-68.
- A2C-001/002 are closed.
- A2C-003 and Path B remain unauthorized.

## 11. What this locking decision changes

This locking decision resolves the three deferred Scope 6 packaging questions as LOCK as-written.

It locks the artifact-family and required-content shapes for future R2S approval records, shadow-evidence retention, and S2P approval records.

It permits WP-S2c-114 to introduce schema files matching this locked decision after this package merges and refreshed-main preflight passes.

It permits WP-S2c-115 to implement additive validators after WP-S2c-114 merges.

## 12. What this locking decision does not authorize

This locking decision does not authorize:

- schema file creation in this WP;
- validator implementation in this WP;
- artifact instance creation;
- approval-record creation;
- shadow-evidence file creation;
- canonical artifact instance creation;
- query-layer changes;
- runtime/protected-path changes;
- research-to-shadow transition;
- shadow-to-paper transition;
- paper-to-live or live transition;
- candidate readiness determination;
- candidate approval or promotion;
- human-gate execution;
- Tier 4 contact;
- paper/live contact;
- live trading;
- exchange/broker/order/live API contact;
- monitoring/dashboard implementation;
- paper bridge implementation or invocation;
- AUTO bridge work;
- A2C-003 or Path B work;
- D2-006, D2-007, REC-5, Phase 9, WP-S2c-100, human-gate, Phase 1 paper runtime, or SignalProvider modification;
- ranking/scoring/recommendation/policy authority.

## 13. Downstream package posture

WP-S2c-114 is next after WP-S2c-113 merges, if refreshed-main preflight is clean and no stop trigger fires.

WP-S2c-114 introduces schema files only, no artifact instances.

WP-S2c-114 uses CS12 T3-implementation with full pytest required.

WP-S2c-115 follows WP-S2c-114 and implements additive validators only.

WP-S2c-115 uses CS12 T3-implementation with full pytest required.

Mandatory Main re-engagement occurs after WP-S2c-115 / post-tranche report-back.

## 14. Validation profile

This package uses CS12 T1-doc-major-decision because it records the Scope 6 packaging locking decision.

Full pytest is required.

## 15. Validation

Pre-edit verification confirmed:

- PR #293 / WP-12er is merged at `bc090639c07662bd37b5bcbea3e0b201269bb24e`.
- Refreshed `main` includes the WP-12er merge.
- `docs/project_status.md` records WP-12er / WP-S2c-112 as the latest branch-state before this package.
- No open PR was reported.
- No remote `codex/wp-12es-scope6-packaging-locking-decision` branch was found before this package branch.
- No WP-12es / WP-S2c-113 PR was found before drafting.
- Searches for WP-12es, WP-S2c-113, and Scope 6 packaging locking decision found no started locking-decision package.
- This locking decision document did not exist before this package.
- Required WP-S2c-100 / WP-S2c-104 / WP-S2c-110 / WP-S2c-111 / WP-S2c-112 source documents exist.
- Main/Karl's resolution is available in handoff context: all three Scope 6 items LOCK as-written, with no modifications, deferrals, or rejections.
- No schema file, validator, artifact instance, artifact directory, query-layer, committed-state test, config, dependency, data, runtime, protected-path, bridge-code, bridge-output, canonical artifact instance, D2-006, D2-007, REC-5, Phase 9, WP-S2c-100 locked criteria, Phase 1 paper runtime, permanent-human-gate, or SignalProvider modification is required.

Package validation results are recorded in the execution report-back and PR.
