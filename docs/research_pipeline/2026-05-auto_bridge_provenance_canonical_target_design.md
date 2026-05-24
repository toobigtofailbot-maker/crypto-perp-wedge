# AUTO Bridge Provenance + Canonical Target Design

## A. Scope

WP-12cu / WP-S2c-53 is docs-only.

This package covers Capsules 3+2 only: provenance / source traceability plus canonical target posture.

This package creates an AUTO bridge provenance/source-traceability and canonical-target design document only.

It is design-only and does not implement anything.

It does not reactivate AUTO in capability terms.

It does not make AUTO local outputs canonical.

It does not transform any existing AUTO output.

It does not make pre-bridge AUTO outputs eligible for canonical transformation.

It does not create REP, OL, REC, EXP, lifecycle, registry, or other canonical artifacts.

It does not define schema/validator/query-layer authority.

It does not bind the bridge to any candidate or evidence track.

It does not reopen A2C-001.

It does not authorize Path B.

It does not modify schemas, validators, central query-layer views, canonical corpus artifacts, configs, dependencies, data, runtime, or protected paths.

It does not create policy/scoring/ranking/recommendation, approval/readiness/lifecycle, or downstream authority.

Committed file scope is only:

- `docs/research_pipeline/2026-05-auto_bridge_provenance_canonical_target_design.md`
- `docs/project_status.md`

## B. Verified Repo-Truth Inputs

Repo-file evidence verified before edits:

- PR #243 / WP-12ct is merged to `main` at merge commit `52f3f8c5751b52b292e6bb382e52e4a501d9be67`.
- Local `main` and `origin/main` both resolved to `52f3f8c5751b52b292e6bb382e52e4a501d9be67` before the WP-12cu branch was created.
- No open GitHub PRs were found during package preflight.
- No existing local branch or PR named `codex/wp-12cu-auto-bridge-provenance-canonical-target` was found before branch creation.
- `docs/research_pipeline/2026-05-auto_bridge_provenance_canonical_target_design.md` did not exist before this package.
- No schema, validator, central query-layer, canonical-corpus, implementation, helper, config, dependency, data, runtime, or protected-path change is required for this package.

Current project-status branch-state for WP-12ct:

- `docs/project_status.md` records WP-12ct / WP-S2c-52 as the latest branch-state after WP-12cs.
- It records WP-12ct as docs-only, creating `docs/research_pipeline/2026-05-auto_bridge_retroactivity_posture.md` and updating `docs/project_status.md` only.
- It records Capsule 6 for the AUTO bridge design tranche.
- It locks existing pre-bridge AUTO outputs as permanently non-canonical under the current design-tranche posture.
- It locks existing pre-bridge AUTO outputs as not eligible for retroactive canonical transformation under this design tranche.
- It preserves the candidate-agnostic bridge posture from WP-12cs.
- It does not implement the bridge, reactivate AUTO, make AUTO local outputs canonical, transform existing AUTO outputs, bind the bridge to A2C-001 or any candidate/evidence track, reopen A2C-001, authorize Path B, modify schemas/validators/central query-layer/canonical corpus/configs/dependencies/data/runtime/protected paths, or create approval/readiness/lifecycle/downstream authority.
- It permits Side to continue to the next already-authorized capsule WP only within Main's 10-capsule design framework after refreshed-main preflight.

Capsule authority:

- WP-12cs records Direction A as continuing the AUTO bridge architecture-design tranche, documentation-only/design-only, within Main's 10-capsule framework.
- WP-12ct records Capsule 6 and identifies Capsules 3+2 as able to focus on provenance/source-traceability and canonical target for future post-bridge outputs, not retroactive conversion.
- Design-tranche interpretation for this package: Capsules 3+2 are the next logical already-authorized bundled package after WP-12ct because source provenance and target posture constrain each other.

AUTO sketch state from `docs/research_pipeline/2026-05-auto_bridge_architecture_design_sketch.md`:

- WP-12cr recorded the first AUTO bridge architecture-design sketch.
- The sketch is conceptual only and does not implement intake, transformation, artifact writer, validator, query view, consumer, or review surface.
- It preserves local-only AUTO boundaries, creates no bridge capability, keeps A2C-001 stopped/deferred, keeps Path B unauthorized, and requires separate explicit authorization for any future implementation.
- It notes that canonical evidence has stricter requirements: committed artifact families, schema/version posture, validators, integrity views, REC/OL semantics, and repo-truth provenance.

AUTO design-continuation / candidate-binding posture from `docs/research_pipeline/2026-05-auto_bridge_design_continuation_candidate_binding.md`:

- WP-12cs locks that the AUTO bridge design tranche continues after WP-12cr as docs-only and design-only.
- It records the current bridge design posture as candidate-agnostic.
- It defers candidate-bound bridge design unless separately authorized.
- It does not decide which canonical artifact family the bridge targets.
- It does not decide schema/validator/query-layer authority or implementation-tranche scope.

AUTO retroactivity posture from `docs/research_pipeline/2026-05-auto_bridge_retroactivity_posture.md`:

- WP-12ct locks that existing pre-bridge AUTO outputs remain permanently non-canonical under the current design-tranche posture.
- Existing pre-bridge AUTO outputs are not eligible for retroactive canonical transformation under this design tranche.
- Future canonical consideration, if any, applies only to future post-bridge-implementation outputs and requires separate explicit authorization.
- Existing AUTO material may inform future design questions descriptively but must not be copied into canonical artifacts, summarized as candidate evidence, or used to satisfy OL, REC, REP, EXP, lifecycle, approval, readiness, ranking, recommendation, or policy requirements.

AUTO checkpoint state from `docs/research_pipeline/2026-04-local_sweep_usability_runway_checkpoint.md`:

- WP-12t through WP-12aa established local JSON sweep-spec materialization design, local JSON loading, local sweep helper delegation, bounded deterministic local sweeps, local-only structural summaries, and sidecar organization over already-completed local results.
- All generated material remains caller-local and uncommitted.
- Runway material remains local-only, research-only, structural, non-authoritative, and no-committed-evidence.
- No schema, central validator, query-layer visibility, canonical `research/` placement, or evidence bridge is established.

AUTO pause state from `docs/research_pipeline/2026-04-post_auto_usability_direction_decision.md`:

- AUTO usability is paused at the WP-12aa-checkpointed state.
- No WP-12ac or AUTO successor package was authorized by WP-12ab.
- AUTO can be reopened later only by a separate chat-level decision and new capsule.
- Local sweep outputs, JSON specs, and sidecars remain local research material only and non-canonical.

Canonical evidence constraints from inspected Phase 9 / OL / REC / schema / query documents:

- `docs/research_pipeline/2026-04-phase9_decision_record.md` records research-pipeline architecture decisions only and has no runtime, policy, deployment, OMS, reconciliation, risk, overlay, safe-mode, or live-trading authority.
- OL v1 supports `research_oos` only; outcome-ledger entries require derivation disclosure and pipeline version.
- OL consumers must use the locked insufficient-evidence floor of at least three evaluation windows per candidate / outcome kind / pipeline version before cross-window inference.
- REC v1 reconciles committed OL v1 `research_oos` entries against committed expectation sources only.
- REC v1 requires one committed expectation source per REC artifact and preserves `REC-5` floor discipline by candidate / outcome kind / pipeline version / expectation-source type.
- REC verdicts and REC consumers are descriptive; they do not create policy, ranking, recommendation, promotion, demotion, paper/live, runtime, or deployment authority.
- Schema-version discipline requires explicit schema-version posture, explicit scoped packages for additive changes, validator impact review, query-layer impact review, and no smuggled schema evolution inside artifact-production packages.
- The schema-family inventory records EXP and REP as legacy research evidence families without explicit `schema_version`; OL v1 and REC v1 are explicitly versioned.
- The query layer is read-only, in-memory, and registers views over existing committed repo files; it must not write to research artifacts or create new research evidence.

A2C stop/defer and post-A2C gate/lessons state:

- A2C-001 remains stopped/deferred.
- There is no active next A2C-001 execution track from the inspected post-A2C gate documents.
- A2C-001 is not approved, not ready, and not lifecycle-complete.
- No selected A2C-001 candidate is approved.
- Path B remains unauthorized.
- Post-A2C lessons documents record observations only and do not create policy/scoring/ranking/recommendation, readiness, approval, or future-track selection authority.

Candidate registry posture from direct inspection of `research/candidate_registry.jsonl`:

- H-001 through H-010 are `CONCLUDED` with `NO-GO` verdicts.
- H-011 is `DRAFT`, `PENDING`, and `reserved`.
- This package does not modify the registry, register H-012+, bind to H-011, or change candidate/cohort state.

Explicit repo-truth notes:

- AUTO remains paused, local-only, research-only, non-authoritative, and non-canonical.
- The current bridge posture remains candidate-agnostic.
- Existing pre-bridge AUTO outputs remain permanently non-canonical and are not eligible for retroactive canonical transformation.

## C. Design Problem

A future AUTO bridge could only be safe if future post-bridge outputs are traceable from local source material through transformation and artifact-emission boundaries.

A future bridge also needs a target canonical evidence path, but target posture must be constrained before any schema, validator, query, or implementation authority is considered.

Existing pre-bridge AUTO outputs cannot be used as a shortcut because WP-12ct locks them as permanently non-canonical and not eligible for retroactive canonical transformation.

This package defines design-level provenance requirements and target posture only.

## D. Provenance Design Requirements

These are future-output-only design requirements that a later implementation would need to satisfy before canonical transformation could be considered. They are not implemented here.

1. Source identity
   - source file or object identity;
   - source format/version;
   - source checksum or stable content identity if later authorized;
   - source path classification as local/non-canonical before bridge intake.

2. Run context
   - command or invocation source;
   - timestamp or run identifier;
   - caller-provided parameters;
   - environment/runtime identity sufficient for reproducibility discussion;
   - explicit note that no runtime/paper-live execution is involved.

3. Code/config identity
   - helper or tool identity;
   - code version or commit identity;
   - configuration identity, if any;
   - explicit note that this package does not authorize config changes.

4. Transformation trace
   - input-to-output mapping;
   - normalization decisions;
   - derived-field explanation;
   - loss/rounding/filtering disclosure;
   - failure and exclusion reasons.

5. Artifact-emission trace
   - target artifact family selected by a future authorized implementation;
   - emission boundary;
   - schema/version binding;
   - validator binding;
   - query/integrity visibility only if separately authorized.

6. Review trace
   - human review surface;
   - report-back expectations;
   - stop conditions;
   - evidence/non-evidence distinction.

## E. Provenance Minimum Bar

Future bridge consideration requires at least:

- no anonymous source material;
- no unversioned transformation path;
- no artifact emission without schema/version authority;
- no validator bypass;
- no central query exposure without explicit authority;
- no canonical claim without committed artifact provenance;
- no backfill from pre-bridge AUTO outputs;
- no candidate evidence use without separately authorized candidate/evidence track;
- no approval/readiness/lifecycle/policy/scoring/ranking/recommendation use.

This minimum bar is design-only. It does not implement provenance capture, source hashing, transformation tooling, schema changes, validators, or query exposure.

## F. Canonical Target Posture

The design target remains candidate-agnostic.

The design target is future-output-only.

The bridge should conceptually target a staged candidate-evidence input path before any REP/OL/REC/lifecycle authority is considered.

The bridge should not directly emit OL or REC artifacts unless a later package explicitly authorizes the required schema, validator, query, expectation-source, and reconciliation semantics.

The bridge should not directly emit lifecycle artifacts.

The bridge should not directly affect candidate registry status.

Any future artifact family target must be selected by separate explicit authorization.

Design preference, not implementation authority: repo truth supports treating the first conceptual target as a staged intake/evidence-input path rather than direct OL, REC, lifecycle, registry, or query emission, because provenance and target semantics need to be proven before canonical artifact-family authority is safe.

## G. Target Options Matrix

No option in this matrix is authorized for implementation by this package. Existing pre-bridge AUTO outputs cannot be used for any option. OL/REC/lifecycle/registry/query paths require separate explicit authority. Runtime and paper/live paths remain forbidden.

| Possible future target | Design fit | Required future authority | Forbidden in this package |
| --- | --- | --- | --- |
| Descriptive bridge intake record | Strong fit as a non-canonical staging concept if future source identity and review rules are authorized. | Explicit implementation scope, allowed file path, provenance fields, validation plan, and non-canonical status. | Creating the record, schema, helper, registry surface, query surface, or canonical claim. |
| Candidate evidence input package | Strong conceptual fit after candidate/evidence-track authorization because it can preserve review before artifact-family emission. | Explicit candidate/evidence track, allowed target family, schema/version posture, validators, and review gates. | Binding to A2C-001, H-001, H-005, H-006, H-011, H-012+, or any future candidate/evidence track. |
| REP-style report surface | Possible later review surface if an authorized package defines source provenance and report semantics. | Explicit REP authority or new report-family authority, schema/validator/query impact review, and candidate binding if applicable. | Emitting REP artifacts or treating AUTO material as candidate evidence. |
| Outcome ledger / OL path | Poor direct first target; OL requires committed derivation, pipeline version, validator, integrity, and floor semantics. | Explicit OL artifact authority, schema/version binding, validator binding, query/integrity authority, and source artifact lineage. | Direct OL emission, OL backfill, OL floor interpretation, or OL consumer claims. |
| Reconciliation / REC path | Poor direct first target; REC depends on committed OL entries and committed expectation sources. | Explicit REC artifact authority, expectation-source semantics, realized-metric binding, validator/query authority, and REC-5 floor handling. | Direct REC emission, expectation-source selection, REC verdict creation, or cross-segment inference. |
| EXP scaffold path | Not a bridge target by default; EXP authoring is a separate planning/evidence scaffold activity. | Explicit EXP scaffold authoring authority, candidate/plan scope, and validation. | EXP scaffold authoring, H-011 first-time inclusion, H-012+ registration, or candidate registration. |
| Lifecycle/registry path | Not a safe target for bridge output; lifecycle and registry changes create state authority. | Explicit lifecycle or registry package, candidate/cohort authority, schema/validator/query authority, and approval semantics if any. | Lifecycle artifacts, registry mutation, candidate status changes, approval/readiness/promotion/demotion. |
| Central query exposure path | Query exposure is a consumer surface, not a source target. | Explicit query-layer authority, registered view semantics, integrity views, and read-only compatibility. | New views, central query exposure, integrity-view changes, or query-layer semantic changes. |

## H. Future Bridge Boundary

Before boundary: AUTO local material remains local-only, research-only, non-authoritative, and non-canonical.

At intake boundary: a future implementation would check provenance/source/run context.

At transformation boundary: a future implementation would map source material to an authorized target structure.

At canonical boundary: a future implementation would emit only if explicit artifact/schema/validator/query authority exists.

At review boundary: a future implementation would expose only authorized review/report surfaces.

If any boundary fails, a future implementation would stop and emit no canonical artifact.

This boundary is not implemented by this package.

## I. What This Package Does Not Decide

This package does not decide:

- final bridge implementation scope;
- whether bridge implementation will ever be authorized;
- final schema changes;
- validator changes;
- central query-layer exposure;
- exact artifact family target;
- REP/OL/REC/EXP/lifecycle/registry creation;
- candidate binding;
- candidate/evidence track selection;
- A2C-001 reopening;
- Path B;
- approval/readiness/lifecycle criteria;
- runtime or paper/live use.

## J. Implications For Downstream Capsules

Capsules 4+8 can use this package's provenance minimum bar and target posture to discuss schema/validator/query authority and validation expectations.

Capsule 5 can size a future implementation tranche using the provenance boundaries and target options from this package.

Capsule 10/checkpoint must report that provenance and target posture remain design-only and that implementation requires separate explicit authorization.

This package does not draft those downstream capsule packages.

## K. Stop Conditions Reinforced By This Posture

Stop if:

- any package attempts to implement provenance capture;
- any package creates or modifies schema, validator, or query-layer files;
- any package emits REP, OL, REC, EXP, lifecycle, registry, or other canonical artifacts;
- any package treats existing pre-bridge AUTO outputs as canonical or candidate evidence;
- any package uses AUTO material for approval/readiness/lifecycle/policy/scoring/ranking/recommendation;
- any package binds the bridge to a candidate/evidence track without separate authorization;
- any package requires configs, dependencies, data changes, runtime contact, protected-path contact, A2C reopening, Path B authorization, candidate registration, cohort modification, or downstream authority.

## L. What Is Locked

- Capsules 3+2 were resolved in this package.
- Future bridge provenance must be explicit, source-traceable, transformation-traceable, and reviewable before canonical transformation can be considered.
- Existing pre-bridge AUTO outputs remain permanently non-canonical and cannot satisfy the provenance bar retroactively.
- Canonical target posture remains candidate-agnostic and future-output-only.
- Direct OL/REC/lifecycle/registry/query emission remains unauthorized.
- Any final artifact family target requires separate explicit authorization.
- AUTO remains paused and local-only.
- Bridge design remains candidate-agnostic.
- A2C-001 remains stopped/deferred.
- Path B remains unauthorized.
- Future bridge implementation requires separate explicit authorization.

## M. What Is Not Authorized

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
- validator authority;
- central query-layer exposure;
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

## N. Validation

Actual validation run for WP-12cu:

- `git diff --check`: passed with no output.
- `git diff --name-only`: returned `docs/project_status.md`; the new design document was still untracked at this pre-staging point.
- `git status --short`: showed only `docs/project_status.md`, `docs/research_pipeline/2026-05-auto_bridge_provenance_canonical_target_design.md`, and pre-existing untracked `.codex/environments/` app material.
- `git ls-files --others --exclude-standard`: showed `docs/research_pipeline/2026-05-auto_bridge_provenance_canonical_target_design.md` and pre-existing untracked `.codex/environments/environment.toml`.
- `tools/dev/diff_scope_summary.py --allowed-file docs/project_status.md --allowed-file docs/research_pipeline/2026-05-auto_bridge_provenance_canonical_target_design.md --json`: exited `ok`; tracked changed files were limited to `docs/project_status.md`; the untracked allowed design document was present; the only allowed-file violation was pre-existing untracked `.codex/environments/environment.toml`; forbidden matches were `[]`.
- `python -m tools.research_query.run --list-views`: listed 55 views.
- Integrity views: all 24 discovered `v_integrity_*` views were executed with `--json`; every view returned `[]`.
- Registry validators: all 14 `tools.registry.validate_*` modules passed.
- Helper tests: `pytest tests/test_diff_scope_summary.py tests/test_validation_summary.py tests/test_code_index.py tests/test_status_snapshot.py -q` passed, `61 passed in 21.74s`.
- Scoped regression: the first 5-minute run timed out before returning a result; rerun with a longer timeout passed, `303 passed, 314 deselected in 319.72s`.
- Full pytest: `pytest -q` passed, `617 passed, 4 warnings in 369.96s`.
