# AUTO Bridge Retroactivity Posture

## A. Scope

WP-12ct / WP-S2c-52 is docs-only.

This package covers Capsule 6 only.

It creates an AUTO bridge retroactivity posture document only.

It is design-only and does not implement anything.

It does not reactivate AUTO in capability terms.

It does not make AUTO local outputs canonical.

It does not transform any existing AUTO output.

It does not make pre-bridge AUTO outputs eligible for canonical
transformation.

It does not define a full provenance standard, canonical artifact target,
schema/validator/query authority, validation plan, or implementation tranche.

It does not bind the bridge to any candidate or evidence track.

It does not reopen A2C-001.

It does not authorize Path B.

It does not modify schemas, validators, central query-layer views, canonical
corpus artifacts, configs, dependencies, data, runtime, or protected paths.

It does not create policy/scoring/ranking/recommendation,
approval/readiness/lifecycle, or downstream authority.

Committed file scope is only:

- `docs/research_pipeline/2026-05-auto_bridge_retroactivity_posture.md`
- `docs/project_status.md`

## B. Verified Repo-Truth Inputs

Repo-file, branch-state, and direct inspection evidence verified during package
preflight:

- WP-12cs / PR #242 is merged to `main`; refreshed `main` is at merge commit
  `f9c5e182cc73e079c7363b7530490f10dfe48021`.
- This package branch starts from refreshed `main` containing the WP-12cs
  merge commit.
- `docs/project_status.md` records WP-12cs / WP-S2c-51 as the latest
  branch-state.
- `docs/project_status.md` records WP-12cs as docs-only, creating
  `docs/research_pipeline/2026-05-auto_bridge_design_continuation_candidate_binding.md`
  and updating `docs/project_status.md` only.
- `docs/project_status.md` records that WP-12cs bundled Capsules 1+7, locks
  that the AUTO bridge design tranche continues after WP-12cr as
  documentation-only/design-only, records the current bridge design posture as
  candidate-agnostic, defers candidate-bound bridge design unless separately
  authorized, does not implement the bridge, does not reactivate AUTO, does not
  make AUTO local outputs canonical, does not bind the bridge to A2C-001 or
  any candidate/evidence track, does not reopen A2C-001, does not authorize
  Path B, does not modify schemas/validators/central query-layer/canonical
  corpus/configs/dependencies/data/runtime/protected paths, does not create
  approval/readiness/lifecycle/downstream authority, and permits Side to
  continue to the next already-authorized capsule WP only within Main's
  10-capsule design framework after refreshed-main preflight.
- Capsule authority: Capsule 6 retroactivity posture is the next logical
  already-authorized capsule after WP-12cs under Main's 10-capsule AUTO bridge
  design framework.
- No open PR was found touching `docs/project_status.md` during package
  preflight.
- No WP-12ct / WP-S2c-52 branch or PR existed before this package branch was
  created.
- The expected retroactivity-posture file did not exist before this package
  created it.
- No current merged repo document was found that implements, authorizes, or
  claims an AUTO-to-canonical-evidence bridge.
- No current merged repo document was found that authorizes AUTO bridge
  implementation.
- No current merged repo document was found that authorizes retroactive
  canonicalization of AUTO outputs.
- No current merged repo document was found that binds AUTO bridge design to a
  specific candidate or evidence track.
- No schema, validator, central query-layer, canonical-corpus, implementation,
  helper, config, dependency, data, runtime, or protected-path change is
  required.

AUTO sketch state from
`docs/research_pipeline/2026-05-auto_bridge_architecture_design_sketch.md`:

- WP-12cr recorded the first AUTO bridge architecture-design sketch.
- The sketch is conceptual only and does not implement an intake,
  transformation, artifact writer, validator, query view, consumer, or review
  surface.
- It preserves local-only AUTO boundaries, creates no bridge capability, keeps
  A2C-001 stopped/deferred, keeps Path B unauthorized, and requires separate
  explicit authorization for any future implementation.

AUTO design-continuation and candidate-binding posture from
`docs/research_pipeline/2026-05-auto_bridge_design_continuation_candidate_binding.md`:

- WP-12cs locks that the AUTO bridge design tranche continues after WP-12cr.
- The tranche remains docs-only and design-only.
- Capsules 1+7 were resolved by WP-12cs.
- The current tranche posture is candidate-agnostic.
- Candidate-bound bridge design is deferred unless separately authorized.
- Future bridge implementation requires separate explicit authorization.

AUTO checkpoint state from
`docs/research_pipeline/2026-04-local_sweep_usability_runway_checkpoint.md`:

- WP-12t through WP-12aa established only local capabilities: local JSON
  sweep-spec materialization design, one caller-provided local JSON spec loader
  into `ParameterSweepSpec`, JSON-driven delegation to the local sweep helper,
  bounded deterministic local sweeps, local-only structural summaries, and a
  sidecar writer over already-completed local sweep results.
- All generated material remains caller-local and uncommitted.
- All runway material remains local-only, research-only, structural,
  non-authoritative, and no-committed-evidence.
- No schema, central validator, query-layer visibility, canonical `research/`
  placement, or evidence bridge is established.

AUTO pause state from
`docs/research_pipeline/2026-04-post_auto_usability_direction_decision.md`:

- AUTO usability is paused at the WP-12aa-checkpointed state.
- No WP-12ac or AUTO successor package is authorized by WP-12ab.
- AUTO can be reopened later only by a separate chat-level decision and new
  capsule.
- Local sweep outputs, JSON specs, and sidecars remain local research material
  only and non-canonical.

Canonical evidence constraints from inspected Phase 9 / OL / REC / schema /
query documents:

- `docs/research_pipeline/2026-04-phase9_decision_record.md` records OL and
  REC v1 as research evidence contracts only, with no runtime, policy,
  deployment, automated-promotion, OMS, risk, overlay, safe-mode, or
  live-trading authority.
- Outcome-ledger v1 supports `research_oos` only, requires derivation and
  pipeline disclosure, excludes paper/live, per-trade granularity, and
  evidence-quality scoring, and keeps consumer inference behind the OL-4
  floor.
- REC v1 reconciles committed `research_oos` outcome-ledger entries only,
  supports only `exp_success_criteria` and `d2_006_gates` expectation sources,
  preserves per-metric comparison, excludes paper/live, evidence-quality
  scoring, policy fields, promotion/demotion flags, and runtime authority, and
  keeps consumer inference behind the REC-5 floor.
- `docs/research_pipeline/2026-04-outcome_ledger_v1_stability.md` and
  `docs/research_pipeline/2026-04-rec_v1_stability.md` lock the consumed OL
  and REC baselines as descriptive research surfaces, require explicit scoped
  packages for retroactive mutation or semantic evolution, and preserve
  canonical corpus boundaries.
- `docs/research_pipeline/2026-04-schema_versioning_discipline.md` and
  `docs/research_pipeline/2026-04-schema_family_inventory.md` require explicit
  schema-versioned scope for new or changed Phase 9 schemas and do not
  authorize retrofits by documentation alone.
- `docs/research_pipeline/2026-04-query_layer.md` defines the central research
  query layer as read-only, in-memory, and scoped to committed repo files; it
  creates no evidence, runtime, policy, OMS, risk, or execution behavior.

A2C stop/defer and post-A2C gate/lessons state from
`docs/research_pipeline/2026-05-a2c001_stop_defer_hold_lock.md`,
`docs/research_pipeline/2026-05-a2c001_post_deferral_closeout_index.md`,
`docs/research_pipeline/2026-05-a2c001_deferral_no_approval_decision_lock.md`,
`docs/research_pipeline/2026-05-post_a2c_active_track_selection_gate.md`, and
`docs/research_pipeline/2026-05-post_a2c_lessons_decision_review.md`:

- A2C-001 remains stopped/deferred.
- There is no active next A2C-001 execution track.
- A2C-001 is not approved, not ready, and not lifecycle-complete.
- No selected A2C-001 candidate is approved.
- Path B remains unauthorized.
- Future substantive work requires explicit Main/Karl/user authorization.
- WP-12cq records lessons and decision-review observations only, not
  policy/scoring/ranking/recommendation, readiness criteria, approval criteria,
  or future-track selection.

Candidate registry posture from direct inspection of
`research/candidate_registry.jsonl`:

- H-001 remains `CONCLUDED` / `NO-GO` / `baseline_tested`.
- H-005 remains `CONCLUDED` / `NO-GO` / `baseline_tested`.
- H-006 remains `CONCLUDED` / `NO-GO` / `baseline_tested`.
- H-011 remains `DRAFT` / `PENDING` / `reserved`; no H-012+ entry exists.

Explicit repo-truth note: AUTO remains paused, local-only, research-only,
non-authoritative, and non-canonical.

Explicit repo-truth note: the current bridge posture remains
candidate-agnostic.

## C. Retroactivity Decision

Existing pre-bridge AUTO outputs remain permanently non-canonical.

Existing pre-bridge AUTO outputs means local AUTO material and outputs produced
before any separately authorized bridge implementation exists, including
WP-12t through WP-12aa local sweep/spec/sidecar/summary material.

Existing pre-bridge AUTO outputs are not eligible for retroactive canonical
transformation under this design tranche.

Existing pre-bridge AUTO outputs may be read for design understanding only, if
needed, but may not be used as canonical evidence.

Only future post-bridge-implementation outputs may be considered for canonical
transformation, and only if a later explicitly authorized implementation
tranche defines the required provenance, artifact, schema/validator/query,
validation, and stop-condition rules.

This package does not authorize that future implementation tranche.

## D. Rationale

Existing AUTO material was produced under a local-only, research-only,
non-authoritative, non-canonical posture.

Existing AUTO material was not produced under a bridge implementation contract.

Existing AUTO material lacks separately authorized canonical provenance,
artifact-emission, validation, and query/integrity authority.

Retroactive canonicalization would weaken provenance discipline and canonical
corpus boundaries.

Permanent non-canonical treatment for existing outputs avoids backfilling
assumptions into old local material.

Candidate-agnostic design is easier to preserve if old outputs are not
retroactively tied to a candidate/evidence path.

This posture preserves the distinction between design learning and canonical
evidence creation.

## E. Allowed Use Of Existing AUTO Material

Existing AUTO material may be inspected read-only to understand local
capability shape, design constraints, and provenance gaps.

Existing AUTO material may inform future design questions at a descriptive
level.

Existing AUTO material must remain local-only, research-only,
non-authoritative, and non-canonical.

Existing AUTO material must not be copied into canonical artifacts.

Existing AUTO material must not be summarized as candidate evidence.

Existing AUTO material must not satisfy OL, REC, REP, EXP, lifecycle,
approval, readiness, ranking, recommendation, or policy requirements.

## F. Future Post-Bridge Output Eligibility

Future AUTO outputs produced after a separately authorized bridge
implementation may be considered for canonical transformation only if that
implementation defines and validates the necessary rules.

Required future rules may include provenance, source traceability,
code/data/config identity, run context, artifact-emission path,
schema/validator/query authority, integrity checks, failure behavior, and
review surface.

Those rules are not defined or authorized by this package.

No existing output becomes eligible because of this future possibility.

## G. What Retroactivity Posture Does Not Decide

This package does not decide:

- the full provenance standard;
- the canonical artifact family target;
- whether the future bridge targets REP, OL, REC, EXP, lifecycle, or another
  family;
- schema/validator/query authority;
- implementation-tranche scope;
- candidate binding;
- future candidate/evidence track selection;
- validation plan for implementation;
- whether bridge implementation will ever be authorized.

## H. Implications For Downstream Capsules

Capsules 3+2 can focus on provenance/source-traceability and canonical target
for future post-bridge outputs, not retroactive conversion.

Capsules 4+8 can discuss schema/validator/query authority and validation
expectations for future post-bridge outputs only.

Capsule 5 can size a future implementation tranche without including
retroactive backfill of pre-bridge AUTO outputs.

Capsule 10/checkpoint must report that pre-bridge AUTO outputs remain
permanently non-canonical unless Main/Karl/user explicitly changes that posture
in a later package.

## I. Stop Conditions Reinforced By This Posture

Stop if:

- any package attempts to canonicalize existing AUTO outputs;
- any package treats existing AUTO material as candidate evidence;
- any package tries to backfill OL/REC/REP/EXP artifacts from pre-bridge AUTO
  outputs;
- any package proposes retroactive schema/provenance assignment for old local
  outputs;
- any package uses existing AUTO outputs for approval/readiness/lifecycle/
  policy/scoring/ranking/recommendation;
- any package needs implementation, helper/tool/script creation, data
  modification, schema/validator/query/canonical-corpus changes, runtime
  contact, protected-path contact, A2C reopening, Path B authorization,
  candidate registration, cohort modification, or downstream authority.

## J. What Is Locked

This package locks only:

- Capsule 6 was resolved in this package.
- Existing pre-bridge AUTO outputs remain permanently non-canonical under the
  current design-tranche posture.
- Existing pre-bridge AUTO outputs are not eligible for retroactive canonical
  transformation under this design tranche.
- Future canonical consideration, if any, applies only to future
  post-bridge-implementation outputs and requires separate explicit
  authorization.
- AUTO remains paused and local-only.
- Bridge design remains candidate-agnostic.
- A2C-001 remains stopped/deferred.
- Path B remains unauthorized.
- Future bridge implementation requires separate explicit authorization.

## K. What Is Not Authorized

This package does not authorize:

- AUTO bridge implementation;
- AUTO reactivation in capability terms;
- canonical conversion of AUTO outputs;
- retroactive canonical status for any AUTO output;
- retroactive transformation of pre-bridge AUTO outputs;
- use of existing AUTO outputs as canonical evidence;
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
- scheduler/daemon/queue/watcher/trigger/dashboard/agent/Monte Carlo/
  robustness engine;
- policy/scoring/ranking/recommendation;
- evidence-quality scoring;
- approval/promotion/demotion/readiness/lifecycle transition authority;
- downstream authority.

## L. Validation

Validation results for WP-12ct / WP-S2c-52:

- `git diff --check`: passed.
- Pre-staging changed-file scope:
  - `git diff --name-only`: `docs/project_status.md`.
  - `git status --short`: `M docs/project_status.md`,
    `?? .codex/environments/`, and
    `?? docs/research_pipeline/2026-05-auto_bridge_retroactivity_posture.md`.
  - `git ls-files --others --exclude-standard`:
    `.codex/environments/environment.toml` and
    `docs/research_pipeline/2026-05-auto_bridge_retroactivity_posture.md`.
  - `.codex/environments/environment.toml` was pre-existing local Codex app
    material observed before package edits and was not staged.
- Advisory diff/scope helper:
  `.\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py --allowed-file docs/project_status.md --allowed-file docs/research_pipeline/2026-05-auto_bridge_retroactivity_posture.md --json`
  exited `0`, reported no forbidden matches, reported the expected tracked
  change to `docs/project_status.md`, reported the expected untracked package
  document, and reported the pre-existing untracked
  `.codex/environments/environment.toml` as an allowed-file violation.
- Query views listed: 55.
- `v_integrity_*`: clean (24); every discovered integrity view ran with JSON
  output and returned `[]`.
- Registry validators: 14 `tools.registry.validate_*` modules passed.
- Helper tests:
  `.\.venv\Scripts\python.exe -m pytest tests/test_diff_scope_summary.py tests/test_validation_summary.py tests/test_code_index.py tests/test_status_snapshot.py -q`
  passed with 61 passed in 34.55 seconds.
- Scoped regression:
  `.\.venv\Scripts\python.exe -m pytest tests -q -k "registry or research_query or reconciliation or outcome_ledger or lifecycle or experiment or diff_scope_summary or validation_summary or code_index or status_snapshot"`
  passed with 303 passed and 314 deselected in 422.52 seconds.
- Full pytest:
  `.\.venv\Scripts\python.exe -m pytest -q`
  passed with 617 passed and 4 warnings in 255.72 seconds.
- Staged checks:
  - `git diff --cached --check`: passed.
  - `git diff --cached --name-only`:
    `docs/project_status.md` and
    `docs/research_pipeline/2026-05-auto_bridge_retroactivity_posture.md`.
  - `git status --short`: `M  docs/project_status.md`,
    `A  docs/research_pipeline/2026-05-auto_bridge_retroactivity_posture.md`,
    and `?? .codex/environments/`.
  - `git ls-files --others --exclude-standard`:
    `.codex/environments/environment.toml`.
  - Staged diff/scope helper exited `0`, reported no forbidden matches, and
    reported the staged changed-file set exactly as `docs/project_status.md`
    and `docs/research_pipeline/2026-05-auto_bridge_retroactivity_posture.md`.
    It again reported pre-existing untracked
    `.codex/environments/environment.toml` as an allowed-file violation; that
    file remains unstaged.
