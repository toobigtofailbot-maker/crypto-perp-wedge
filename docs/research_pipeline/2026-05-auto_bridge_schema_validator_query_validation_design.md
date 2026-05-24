# AUTO Bridge Schema / Validator / Query Authority + Validation Expectations

## A. Scope

WP-12cv / WP-S2c-54 is docs-only.

This package covers Capsules 4+8 only. It creates an AUTO bridge schema/validator/query authority and validation-expectations design document only. It is design-only and does not implement anything.

This package does not reactivate AUTO in capability terms. It does not make AUTO local outputs canonical. It does not transform any existing AUTO output. It does not make pre-bridge AUTO outputs eligible for canonical transformation.

This package does not create REP, OL, REC, EXP, lifecycle, registry, query, or other canonical artifacts. It does not create or modify schemas. It does not create or modify validators. It does not create or modify central query-layer views or integrity views. It does not define active schema/validator/query-layer authority.

This package does not bind the bridge to any candidate or evidence track. It does not reopen A2C-001. It does not authorize Path B. It does not modify configs, dependencies, data, runtime, or protected paths. It does not create policy/scoring/ranking/recommendation, approval/readiness/lifecycle, or downstream authority.

Committed file scope is only:

- `docs/research_pipeline/2026-05-auto_bridge_schema_validator_query_validation_design.md`
- `docs/project_status.md`

## B. Verified Repo-Truth Inputs

WP-12cu / PR #244 is merged. Refreshed `main` is at merge commit `8faa66b0cf9e23c14ed82b4a1e55a469098910bc`, which includes WP-12cu commit `ca53d3b46d6584be1a7fca6deedc551278bd079c`.

`docs/project_status.md` records WP-12cu / WP-S2c-53 as the latest branch-state before this package. It records WP-12cu as docs-only, creating `docs/research_pipeline/2026-05-auto_bridge_provenance_canonical_target_design.md` and updating `docs/project_status.md` only. It records bundled Capsules 3+2 for the AUTO bridge design tranche, preserves the WP-12ct retroactivity posture, preserves the candidate-agnostic bridge posture from WP-12cs, records canonical target posture as design-only and not artifact-emission authority, and does not implement the bridge or authorize schemas/validators/query/canonical-corpus/runtime/protected-path changes.

Capsule authority: WP-12cu records that Side may continue to the next already-authorized capsule WP only within Main's 10-capsule design framework after refreshed-main preflight. WP-12cu identifies Capsules 4+8 as the next logical already-authorized bundled package: schema/validator/query authority plus validation expectations.

AUTO sketch, candidate-binding, retroactivity, provenance/canonical-target, checkpoint, and pause states from direct file inspection:

- `docs/research_pipeline/2026-05-auto_bridge_architecture_design_sketch.md` records a conceptual bridge sketch only. It creates no intake, transformation, artifact writer, validator, query view, consumer, review queue, scheduler, agent, or query exposure.
- `docs/research_pipeline/2026-05-auto_bridge_design_continuation_candidate_binding.md` records the current bridge design posture as candidate-agnostic and defers candidate-bound bridge design unless separately authorized.
- `docs/research_pipeline/2026-05-auto_bridge_retroactivity_posture.md` locks existing pre-bridge AUTO outputs as permanently non-canonical under the current design-tranche posture and not eligible for retroactive canonical transformation.
- `docs/research_pipeline/2026-05-auto_bridge_provenance_canonical_target_design.md` locks a future-output-only provenance minimum bar and records canonical target posture as design-only, candidate-agnostic, future-output-only, and not artifact-emission authority.
- `docs/research_pipeline/2026-04-local_sweep_usability_runway_checkpoint.md` records the AUTO local sweep runway as local-only, research-only, structural, non-authoritative, and non-canonical, with no schema, central validator, query-layer visibility, canonical `research/` placement, or evidence bridge.
- `docs/research_pipeline/2026-04-post_auto_usability_direction_decision.md` pauses AUTO usability at the WP-12aa-checkpointed state. No WP-12ac or AUTO successor package is authorized by that decision, and AUTO local material remains non-canonical.

Canonical evidence constraints from direct file inspection:

- `docs/research_pipeline/2026-04-phase9_decision_record.md` records explicit schema-versioning discipline, human approval semantics, retrospective backfill discipline, OL/REC locks, OL-4 floor discipline, REC-5 floor discipline, and non-claims against automated promotion, deployment authority, and policy authority.
- `docs/research_pipeline/2026-04-outcome_ledger_artifact.md` records outcome-ledger v1 schema posture, validator/query sequencing, derivation and pipeline disclosure, and non-claims against promotion, policy, REC authority, runtime, OMS, risk, deployment, validator, or query-layer behavior beyond explicitly merged packages.
- `docs/research_pipeline/2026-04-outcome_ledger_v1_stability.md` locks the current OL schema, validator, query-layer, artifact, helper, and consumer state as descriptive research only. New OL artifacts append by ID and must pass validator and integrity checks.
- `docs/research_pipeline/2026-04-reconciliation_artifact.md` records REC v1 as evidence only, with explicit expectation-source limits, validator/query-layer support, and exclusions for paper/live, evidence-quality scoring, policy fields, promotion/demotion flags, and runtime authority.
- `docs/research_pipeline/2026-04-rec_v1_stability.md` locks the REC schema, validator, query-layer, artifact, and consumer state as descriptive research only, preserving REC-5 floor discipline and unsupported claims.
- `docs/research_pipeline/2026-04-schema_versioning_discipline.md` and `docs/research_pipeline/2026-04-schema_family_inventory.md` record schema/version posture and current schema-family authority boundaries. Future schema-family changes require explicit scoped work, validator impact, query-layer impact, and migration/backfill posture.
- `docs/research_pipeline/2026-04-query_layer.md` records the central research query layer as read-only, in-memory, and loaded from existing repo files. Query exposure is an inspection surface and does not write artifacts or create runtime/policy/override/OMS/risk/execution behavior.

A2C stop/defer and post-A2C gate/lessons state from direct file inspection:

- `docs/research_pipeline/2026-05-a2c001_deferral_no_approval_decision_lock.md`, `docs/research_pipeline/2026-05-a2c001_post_deferral_closeout_index.md`, and `docs/research_pipeline/2026-05-a2c001_stop_defer_hold_lock.md` preserve A2C-001 as not approved, not ready, not lifecycle-complete, and in stop/defer hold.
- `docs/research_pipeline/2026-05-post_a2c_active_track_selection_gate.md` records no active post-A2C substantive execution track and no A2C-001 reopen.
- `docs/research_pipeline/2026-05-post_a2c_lessons_decision_review.md` records lessons and decision-review observations only, not policy/scoring/ranking/recommendation, readiness criteria, approval criteria, or future-track selection.
- `docs/research_pipeline/2026-05-r1_r2_h006_approval_use_lock.md` authorizes R1/R2 use for H-006 onward when eligible, but does not authorize schema/validator/query-layer changes, A2C-001 completion, Path B, runtime, approval/readiness/lifecycle, or downstream authority.

Candidate registry posture from direct inspection: `research/candidate_registry.jsonl` contains H-001 through H-010 as `CONCLUDED` / `NO-GO` and H-011 as a reserved `DRAFT` / `PENDING` slot. This package does not modify the registry and does not create H-011 first-time inclusion or H-012+ registration.

Explicit repo-truth notes:

- AUTO remains paused, local-only, research-only, non-authoritative, and non-canonical.
- The current bridge posture remains candidate-agnostic.
- Existing pre-bridge AUTO outputs remain permanently non-canonical and are not eligible for retroactive canonical transformation.
- WP-12cu's provenance minimum bar and target posture remain design-only and not implementation authority.

## C. Design Problem

A future AUTO bridge cannot safely create canonical artifacts unless schema, validator, query, and validation responsibilities are explicitly defined.

Existing repo truth already has canonical schema/versioning, validator, REC/OL, and read-only query-layer disciplines that cannot be bypassed.

A future bridge may need new schema, validator, query, or integrity behavior, but this package cannot grant that authority. This package records the authority posture and validation expectations only.

## D. Schema Authority Posture

No schema changes are authorized by this package. No schema-version assignment for bridge outputs is authorized by this package. No new artifact family is created by this package.

Any future bridge schema work would require a separate explicit package. A future schema package would need, at minimum:

- target artifact family or non-canonical intake record scope;
- schema-version posture;
- additive versus incompatible-change classification;
- validator impact review;
- query-layer impact review;
- migration/backfill exclusion statement;
- protected-path and canonical-corpus boundary check.

Existing pre-bridge AUTO outputs cannot receive retroactive schema assignment.

## E. Validator Authority Posture

No validator changes are authorized by this package. No validator bypass is allowed for any future bridge output.

Any future bridge validator work would require a separate explicit package. A future validator package would need, at minimum:

- exact artifact or intake-record scope;
- schema/version binding;
- required provenance fields;
- failure conditions;
- strict handling of missing provenance;
- rejection behavior for pre-bridge AUTO outputs;
- registry/integrity/query impact review, if relevant.

Future validation must distinguish local design material from canonical evidence.

## F. Central Query-Layer Authority Posture

No central query-layer exposure is authorized by this package. No new query views or integrity views are authorized by this package.

Query exposure is a consumer surface, not a bridge source target.

Any future bridge query-layer work would require a separate explicit package. A future query-layer package would need, at minimum:

- source artifact family or intake-record definition;
- read-only view semantics;
- integrity-view requirements;
- relationship to validators;
- failure/empty-set behavior;
- explicit no-write guarantee;
- proof that the bridge is not creating evidence through the query layer.

Existing pre-bridge AUTO outputs cannot become query-visible canonical evidence by retroactive exposure.

## G. Validation Expectations For Future Design Packages

Remaining design-tranche packages must remain docs-only unless separately authorized. They must run normal documentation-scope validation, preserve refreshed-main preflight, run diff/scope checks, run query surface listing and integrity views, run registry validators, and run helper/scoped/full pytest unless explicitly reduced by user/Main/Karl authority.

They must keep final staged files limited to allowed docs files. They must not stage `.codex` environment files. They must report exact validation results and distinguish repo-file evidence from query-executed evidence.

## H. Validation Expectations For Future Implementation Tranche

Any future implementation would need a separate explicit validation plan. Possible requirements may include:

- schema validation for any new/changed artifact family;
- validator tests for accepted and rejected bridge inputs;
- negative tests for pre-bridge AUTO output rejection;
- provenance completeness tests;
- transformation determinism tests;
- artifact-emission stop-condition tests;
- no-query-write tests;
- central query-layer/integrity tests only if query exposure is separately authorized;
- diff/scope enforcement;
- full registry validator suite;
- full relevant pytest suite;
- explicit report-back of artifacts created, rejected, and skipped.

These tests are not implemented here.

## I. Authority Matrix

| authority area | current posture | future authorization needed | forbidden in this package |
|---|---|---|---|
| schema family / schema version | No AUTO bridge schema family, schema change, or bridge schema-version assignment exists. | Separate explicit schema package with scope, version posture, validator/query impact, and backfill exclusion. | Creating or modifying schema files; assigning schema versions to bridge or pre-bridge AUTO outputs. |
| validators | Existing validators own current committed artifact-family checks. No bridge validator exists. | Separate explicit validator package bound to schema/version and failure behavior. | Validator changes, validator bypass, or new validator authority. |
| central query views | Query layer is read-only over authorized committed repo files. No bridge exposure exists. | Separate explicit query-layer package with read-only semantics and no-write proof. | New relations, views, central exposure, or query semantic changes. |
| integrity views | Existing integrity views must remain clean. No bridge integrity view exists. | Separate explicit package if query exposure or artifact family requires integrity checks. | Creating, modifying, weakening, or bypassing integrity views. |
| canonical corpus artifact placement | Canonical artifact placement is limited to existing authorized artifact families and package scopes. | Separate explicit artifact-family or intake-record authority. | Canonical-corpus modification or placement of AUTO bridge outputs. |
| non-canonical intake record | Conceptual option only; no path, schema, or writer exists. | Separate explicit implementation scope, location, non-canonical status, and validation plan. | Creating the record, path, helper, schema, validator, or query surface. |
| provenance capture | WP-12cu records a future-output-only minimum bar. No capture tooling exists. | Separate explicit implementation and validation package. | Provenance-capture implementation or source-checksum tooling. |
| artifact emission | WP-12cu records no artifact-emission authority. | Separate explicit artifact-family/schema/validator/query authorization. | Emitting REP, OL, REC, EXP, lifecycle, registry, query, or other canonical artifacts. |
| registry/lifecycle exposure | Registry/lifecycle changes create state authority and remain unauthorized. | Separate explicit lifecycle/registry package with candidate/cohort authority. | Registry mutation, lifecycle artifacts, approval/readiness/promotion/demotion authority. |
| candidate evidence use | Bridge design remains candidate-agnostic. | Separate explicit candidate/evidence-track authorization. | Binding to A2C-001, H-001, H-005, H-006, H-011, H-012+, or any future candidate/evidence track. |
| pre-bridge AUTO output handling | Existing pre-bridge AUTO outputs remain permanently non-canonical and not eligible for retroactive canonical transformation. | Only future post-bridge outputs could be considered after separate implementation authority; this does not affect pre-bridge outputs. | Retroactive schema assignment, validation acceptance, query exposure, or canonical transformation. |

All authority remains future/separate. No implementation is authorized here. Existing pre-bridge AUTO outputs remain non-canonical. No schema/validator/query files may change in this package.

## J. Failure / Stop Behavior Posture

Design-level stop posture:

- If required provenance is missing, future implementation should stop before artifact emission.
- If schema authority is absent, future implementation should stop before artifact emission.
- If validator authority is absent, future implementation should stop before artifact emission.
- If query exposure authority is absent, future implementation should not expose outputs centrally.
- If candidate/evidence-track authority is absent, future implementation should not create candidate evidence.
- If the source is a pre-bridge AUTO output, future implementation should reject canonical transformation.
- If any protected path or runtime surface is required, the package must stop and return to Main/Karl/user.

This stop posture is design-only.

## K. What This Package Does Not Decide

This package does not decide:

- whether bridge implementation will ever be authorized;
- final schema changes;
- validator implementation;
- central query-layer exposure;
- integrity-view design;
- exact artifact family target;
- whether the future target is a non-canonical intake record, candidate evidence input, REP-style surface, OL, REC, EXP, lifecycle, registry, or another family;
- candidate binding;
- candidate/evidence track selection;
- implementation-tranche scope;
- A2C-001 reopening;
- Path B;
- approval/readiness/lifecycle criteria;
- runtime or paper/live use.

## L. Implications For Downstream Capsules

Capsule 5 can use this authority posture to size a future implementation tranche without granting implementation authority.

Capsule 10/checkpoint must report that schema/validator/query authority and validation expectations remain design-only and that implementation requires separate explicit authorization.

Capsule 10/checkpoint should also ask Main for a one-sentence estimate of how many WPs Main thinks it will take to complete the whole project, with the key uncertainty or dependency named.

This package does not draft those downstream capsule packages.

## M. Stop Conditions Reinforced By This Posture

Stop if:

- any package attempts to create or modify schemas;
- any package attempts to create or modify validators;
- any package attempts to create or modify query-layer or integrity-view files;
- any package emits REP, OL, REC, EXP, lifecycle, registry, query, or other canonical artifacts;
- any package implements provenance capture, source-checksum tooling, transformation, or artifact emission;
- any package treats existing pre-bridge AUTO outputs as canonical or candidate evidence;
- any package uses AUTO material for approval/readiness/lifecycle/policy/scoring/ranking/recommendation;
- any package binds the bridge to a candidate/evidence track without separate authorization;
- any package requires configs, dependencies, data changes, runtime contact, protected-path contact, A2C reopening, Path B authorization, candidate registration, cohort modification, or downstream authority.

## N. What Is Locked

- Capsules 4+8 were resolved in this package.
- No schema, validator, or central query-layer authority exists for AUTO bridge work under the current design tranche.
- Any future schema, validator, or query-layer work requires separate explicit authorization.
- Future implementation validation would need explicit schema/validator/query/provenance/failure-behavior coverage before canonical transformation can be considered.
- Existing pre-bridge AUTO outputs remain permanently non-canonical and cannot be made eligible by schema/validator/query posture.
- Canonical target posture remains candidate-agnostic and future-output-only.
- Direct OL/REC/lifecycle/registry/query emission remains unauthorized.
- AUTO remains paused and local-only.
- Bridge design remains candidate-agnostic.
- A2C-001 remains stopped/deferred.
- Path B remains unauthorized.
- Future bridge implementation requires separate explicit authorization.

## O. What Is Not Authorized

This package does not authorize:

- AUTO bridge implementation;
- AUTO reactivation in capability terms;
- provenance-capture implementation;
- source-checksum tooling;
- canonical conversion of AUTO outputs;
- retroactive canonical status for any AUTO output;
- retroactive transformation of pre-bridge AUTO outputs;
- use of existing AUTO outputs as canonical evidence;
- REP, OL, REC, EXP, lifecycle, registry, or query artifact creation;
- schema authority;
- schema changes;
- schema-version assignment;
- validator authority;
- validator changes;
- central query-layer exposure;
- query view changes;
- integrity-view changes;
- canonical-corpus modification;
- candidate-bound bridge design;
- candidate-level approval;
- selected-candidate approval;
- cohort-level approval;
- A2C-001 reopen/completion/readiness;
- Path B;
- runtime;
- paper/live;
- OMS;
- risk;
- safe mode;
- exchange/broker/order/execution behavior;
- config/dependency/data changes;
- additional evidence production;
- R1/R2 implementation changes;
- EXP scaffold authoring;
- H-011 first-time inclusion;
- H-012+ registration;
- new cohort definition;
- scheduler/daemon/queue/watcher/trigger/dashboard/agent/Monte Carlo/robustness engine;
- policy/scoring/ranking/recommendation;
- evidence-quality scoring;
- approval/promotion/demotion/readiness/lifecycle transition authority;
- downstream authority.

## P. Validation

Actual validation run for WP-12cv / WP-S2c-54:

- `git diff --check`: passed.
- `git diff --name-only`: returned `docs/project_status.md` before staging; the new design file was untracked at that point.
- `git status --short`: before staging showed `M docs/project_status.md`, `?? docs/research_pipeline/2026-05-auto_bridge_schema_validator_query_validation_design.md`, and pre-existing untracked `.codex/environments/`.
- `git ls-files --others --exclude-standard`: before staging showed `docs/research_pipeline/2026-05-auto_bridge_schema_validator_query_validation_design.md` and pre-existing untracked `.codex/environments/environment.toml`.
- `tools/dev/diff_scope_summary.py --allowed-file docs/project_status.md --allowed-file docs/research_pipeline/2026-05-auto_bridge_schema_validator_query_validation_design.md --json`: exited `ok`; forbidden matches `[]`; tracked changed files were limited to `docs/project_status.md`; untracked files were the allowed new design doc plus pre-existing `.codex/environments/environment.toml`, which the helper reported as an allowed-file violation.
- `python -m tools.research_query.run --list-views`: listed 55 views.
- Integrity views: all 24 discovered `v_integrity_*` views ran with JSON output and returned `[]`.
- Registry validators: all 14 `tools.registry.validate_*` modules passed.
- Helper tests: `61 passed in 24.50s`.
- Scoped regression: `303 passed, 314 deselected in 390.75s`.
- Full pytest: `617 passed, 4 warnings in 310.65s`.
- Staged `git diff --cached --check`: passed.
- Staged `git diff --cached --name-only`: returned exactly `docs/project_status.md` and `docs/research_pipeline/2026-05-auto_bridge_schema_validator_query_validation_design.md`.
- Staged `git status --short`: showed only the two staged docs files plus pre-existing untracked `.codex/environments/`.
- Staged `git ls-files --others --exclude-standard`: showed only pre-existing untracked `.codex/environments/environment.toml`.
- Staged diff-scope summary: exited `ok`; staged changed files were exactly `docs/project_status.md` and `docs/research_pipeline/2026-05-auto_bridge_schema_validator_query_validation_design.md`; forbidden matches `[]`; the only allowed-file violation was pre-existing untracked `.codex/environments/environment.toml`.
