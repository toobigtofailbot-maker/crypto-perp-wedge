# AUTO Bridge Architecture Design Sketch

## A. Scope

WP-12cr / WP-S2c-50 is docs-only.

This package creates an AUTO bridge architecture design sketch only.

It is design-only and does not implement anything.

It does not reactivate AUTO in capability terms.

It does not make AUTO local outputs canonical.

It does not modify schemas, validators, central query-layer views, canonical
corpus artifacts, configs, dependencies, data, runtime, or protected paths.

It does not reopen A2C-001.

It does not authorize Path B.

It does not create policy/scoring/ranking/recommendation,
approval/readiness/lifecycle, or downstream authority.

Committed file scope is only:

- `docs/research_pipeline/2026-05-auto_bridge_architecture_design_sketch.md`
- `docs/project_status.md`

## B. Verified Repo-Truth Inputs

Repo-file and branch-state evidence verified during package preflight:

- WP-12cq / PR #240 is merged to `main`; refreshed `main` is at merge commit
  `b7bfc3fe4965489001dd73f9b98e69d138a147e9`.
- This package branch starts from refreshed `main` at
  `b7bfc3fe4965489001dd73f9b98e69d138a147e9`.
- `docs/project_status.md` records WP-12cq / WP-S2c-49 as the latest
  branch-state.
- `docs/project_status.md` records WP-12cq as docs-only, creating
  `docs/research_pipeline/2026-05-post_a2c_lessons_decision_review.md` and
  updating `docs/project_status.md` only.
- `docs/project_status.md` records that WP-12cq preserved the A2C-001
  stop/defer hold, did not reopen A2C-001, did not approve A2C-001, did not
  claim A2C-001 completion or cohort-phase closure, did not authorize Path B,
  and did not select a next substantive execution track.
- Track selection authority for this package is chat-level and package-local:
  Main selected the AUTO bridge architecture-design tranche, design-only, and
  the user requested Codex execution from that selected track.
- No open PR was found touching `docs/project_status.md` during package
  preflight.
- No WP-12cr / WP-S2c-50 branch or PR existed before this package branch was
  created.
- The expected design-sketch file did not exist before this package created it.
- No current merged repo document was found that implements, authorizes, or
  claims an AUTO-to-canonical-evidence bridge.
- No current merged repo document was found that authorizes AUTO bridge
  implementation.
- No schema, validator, central query-layer, canonical-corpus, implementation,
  helper, config, dependency, data, runtime, or protected-path change is
  required.

AUTO checkpoint state:

- `docs/research_pipeline/2026-04-local_sweep_usability_runway_checkpoint.md`
  records that WP-12t through WP-12aa established only local capabilities:
  local JSON sweep-spec materialization design, one caller-provided local JSON
  spec loader into `ParameterSweepSpec`, JSON-driven delegation to the local
  sweep helper, bounded deterministic local sweeps, local-only structural
  summaries, and a sidecar writer over already-completed local sweep results.
- The same checkpoint records that all generated material remains
  caller-local and uncommitted, and that all runway material remains
  local-only, research-only, structural, non-authoritative, and
  no-committed-evidence.
- It also records that no schema, central validator, query-layer visibility,
  canonical `research/` placement, or evidence bridge is established.

AUTO pause state:

- `docs/research_pipeline/2026-04-post_auto_usability_direction_decision.md`
  locks AUTO usability paused at the WP-12aa-checkpointed state.
- It records no WP-12ac or AUTO successor package authorized by WP-12ab.
- It records that AUTO can be reopened later only by a separate chat-level
  decision and new capsule.
- It records that local sweep outputs, JSON specs, and sidecars remain local
  research material only and non-canonical.

Post-A2C gate and lessons state:

- `docs/research_pipeline/2026-05-post_a2c_active_track_selection_gate.md`
  records no active post-A2C project track selected by that package, A2C-001
  stopped/deferred, and future substantive work requiring explicit
  Main/Karl/user authorization.
- `docs/research_pipeline/2026-05-post_a2c_lessons_decision_review.md`
  records lessons and decision-review observations only, not
  policy/scoring/ranking/recommendation, readiness criteria, approval
  criteria, or future-track selection.
- The WP-12cq lessons document also records that AUTO bridge
  architecture-design remained a separate possible design-only track, not
  selected by that package, and that AUTO-to-canonical-evidence bridge
  implementation was not authorized.

Constraint sources used for REC, OL, schema-versioning, integrity-view,
validator, central-query, and canonical evidence boundaries:

- `docs/research_pipeline/2026-04-phase9_decision_record.md`
- `docs/research_pipeline/2026-04-outcome_ledger_artifact.md`
- `docs/research_pipeline/2026-04-outcome_ledger_v1_stability.md`
- `docs/research_pipeline/2026-04-reconciliation_artifact.md`
- `docs/research_pipeline/2026-04-rec_v1_stability.md`
- `docs/research_pipeline/2026-04-schema_versioning_discipline.md`
- `docs/research_pipeline/2026-04-schema_family_inventory.md`
- `docs/research_pipeline/2026-04-query_layer.md`
- `docs/research_pipeline/2026-05-a2c001_stop_defer_hold_lock.md`

Explicit repo-truth note: AUTO local material remains local-only,
research-only, non-authoritative, and non-canonical.

## C. Design Problem

AUTO/local sweep material can produce local research outputs and structural
summaries.

Canonical evidence has stricter requirements: committed artifact families,
schema/version posture, validators, integrity views, REC/OL semantics, and
repo-truth provenance.

No current bridge exists that safely converts or stages AUTO-local material
into canonical evidence.

Any future bridge would need explicit design and implementation authorization
before it can create canonical artifacts or expose bridge outputs.

This document sketches the architecture surface only.

## D. Design Goals

Design goals only:

- preserve canonical evidence integrity;
- preserve local-only AUTO boundaries until implementation is authorized;
- separate local source material from canonical artifact creation;
- require explicit provenance and transformation boundaries;
- preserve REC and OL semantics;
- avoid silent schema, validator, or query-layer expansion;
- make future implementation tranche requirements visible;
- make stop conditions and authorization gates explicit.

These goals are not implemented capabilities.

## E. Non-Goals

Non-goals:

- no implementation;
- no helper/tool/script creation;
- no schema or validator changes;
- no central query-layer exposure;
- no new artifact-family creation;
- no AUTO output canonicalization;
- no retroactive canonical status for existing local AUTO outputs;
- no A2C-001 reopening;
- no Path B;
- no runtime/paper-live;
- no OMS/risk/safe mode;
- no policy/scoring/ranking/recommendation;
- no approval/readiness/lifecycle authority;
- no downstream authority.

## F. Conceptual Bridge Architecture

This architecture is conceptual only. It does not implement an intake,
transformation, artifact writer, validator, query view, consumer, or review
surface.

### 1. Local AUTO source layer

The local source layer would consist of existing local JSON sweep spec
material, the local sweep helper, the local sidecar writer, local run-registry
references, and local structural summary material.

This layer remains local-only and non-canonical. Local JSON specs, generated
sweep outputs, local registry outputs, sidecar outputs, and structural
summaries do not become repo evidence merely because this design sketch exists.

### 2. Bridge intake boundary

A future bridge intake boundary would need to validate that an authorized
implementation can identify the source material, source provenance,
configuration, code state, data/run context, local output root, and boundary
markers.

This package defines no intake format and implements no intake behavior.

### 3. Transformation / normalization boundary

A future transformation boundary would need to define how local material maps
into canonical candidate evidence inputs without inventing missing facts,
combining forbidden dimensions, bypassing REP/OL/REC semantics, or weakening
source disclosure.

This package defines no transformation contract and implements no
normalization behavior.

### 4. Canonical artifact boundary

The canonical artifact boundary would only be crossed by a future explicitly
authorized implementation tranche.

Any such tranche would need to honor schema-versioning posture, validators,
REC/OL semantics, integrity views, committed artifact-family rules, and
repo-truth provenance. This design sketch does not create or modify any
canonical artifact.

### 5. Validation / integrity boundary

A future bridge would require validators, tests, and integrity views only if a
separate authorized package grants that scope.

This package creates no validator, test, integrity view, query-layer exposure,
or validation authority.

### 6. Consumer / review boundary

A future consumer or review boundary would present bridge outputs only after
canonical evidence authority exists.

This package creates no consumer artifact, dashboard, report bundle, review
queue, scheduler, agent, or query exposure.

## G. Canonical Lock Matrix

| lock / rule family | current authority source | bridge design implication | forbidden in this package |
|---|---|---|---|
| OL-1 | `docs/research_pipeline/2026-04-phase9_decision_record.md`; `docs/research_pipeline/2026-04-outcome_ledger_artifact.md` | Outcome-ledger v1 supports `research_oos` only. Any future bridge target would need to stay within authorized outcome kinds or obtain versioned scope. | Paper/live OL semantics or any OL artifact creation. |
| OL-2 | `docs/research_pipeline/2026-04-phase9_decision_record.md`; `docs/research_pipeline/2026-04-outcome_ledger_artifact.md` | Retrospective REP backfill was accepted only after schema and validator support; bridge-derived backfill would need separate explicit authorization. | Retrospective AUTO-to-OL conversion. |
| OL-3 | `docs/research_pipeline/2026-04-phase9_decision_record.md`; `docs/research_pipeline/2026-04-outcome_ledger_artifact.md` | Future bridge design must preserve `derivation_record`, `pipeline_version`, committed source artifacts, and disclosed pipeline semantics. | Creating derivation records or assigning pipeline versions for AUTO outputs. |
| OL-4 | `docs/research_pipeline/2026-04-phase9_decision_record.md`; `docs/research_pipeline/2026-04-outcome_ledger_v1_stability.md` | Future consumers must preserve the floor of at least 3 evaluation windows per candidate / outcome_kind / pipeline_version before cross-window inference. | Cross-window inference or floor lowering. |
| OL-5 | `docs/research_pipeline/2026-04-phase9_decision_record.md`; `docs/research_pipeline/2026-04-outcome_ledger_artifact.md` | Future bridge scope must respect OL v1 exclusions: no paper/live, no per-trade granularity, and no evidence-quality scoring. | Paper/live, per-trade, or evidence-scoring fields. |
| OL-6 | `docs/research_pipeline/2026-04-phase9_decision_record.md`; `docs/research_pipeline/2026-04-outcome_ledger_artifact.md` | Outcome-ingestion helper sequencing shows helpers need their own later scope and validation. | Helper/tool/script creation. |
| REC-1 | `docs/research_pipeline/2026-04-phase9_decision_record.md`; `docs/research_pipeline/2026-04-reconciliation_artifact.md` | REC v1 reconciles `research_oos` OL entries only. A bridge cannot imply paper/live reconciliation. | REC artifact creation or paper/live reconciliation. |
| REC-2 | `docs/research_pipeline/2026-04-phase9_decision_record.md`; `docs/research_pipeline/2026-04-reconciliation_artifact.md` | REC v1 supports only `exp_success_criteria` and `d2_006_gates` expectation sources. | New expectation-source authority. |
| REC-3 | `docs/research_pipeline/2026-04-phase9_decision_record.md`; `docs/research_pipeline/2026-04-reconciliation_artifact.md` | Future bridge design must not collapse per-metric comparisons or derived verdict semantics. | Comparison logic, verdict logic, or REC emission. |
| REC-4 | `docs/research_pipeline/2026-04-phase9_decision_record.md`; `docs/research_pipeline/2026-04-reconciliation_artifact.md` | Retrospective REC backfill requires scoped derivation mechanics and validator support. | Retrospective REC generation from AUTO material. |
| REC-5 | `docs/research_pipeline/2026-04-phase9_decision_record.md`; `docs/research_pipeline/2026-04-rec_v1_stability.md` | Future bridge work must preserve the floor of at least 3 reconciliations per candidate_id / outcome_kind / pipeline_version / expectation_source_type. | REC-5 satisfaction, dimension combining, or cross-segment inference. |
| REC-6 | `docs/research_pipeline/2026-04-phase9_decision_record.md`; `docs/research_pipeline/2026-04-reconciliation_artifact.md` | REC v1 excludes paper/live, evidence-quality scoring, policy fields, promotion/demotion flags, and runtime authority. | Any excluded REC semantics or authority. |
| Schema-versioning posture | `docs/research_pipeline/2026-04-schema_versioning_discipline.md`; `docs/research_pipeline/2026-04-schema_family_inventory.md` | New Phase 9 schemas require top-level `schema_version`; schema changes require explicit scope and validation. | Schema creation, retrofit, or semantic schema change. |
| Validator authority | `docs/research_pipeline/2026-04-schema_family_inventory.md`; artifact-family docs | Existing validators own committed artifact-family checks. A future bridge cannot bypass them. | Validator changes or new validator authority. |
| Integrity-view discipline | `docs/research_pipeline/2026-04-query_layer.md`; REC/OL stability locks | Integrity views must remain clean and are authoritative health checks for exposed families. | Integrity-view creation or weakening. |
| Central query-layer exposure | `docs/research_pipeline/2026-04-query_layer.md`; `docs/research_pipeline/2026-04-schema_family_inventory.md` | Query exposure is read-only, in-memory, and scoped to committed repo files. Future bridge outputs need explicit query-layer authority. | New relation, view, or query exposure. |
| Canonical corpus immutability | OL/REC stability locks and artifact docs | Committed OL/REC artifacts append by ID and are not retroactively mutated without scoped rationale. | Canonical corpus modification. |
| Provenance / source traceability | OL-3; REC docs; schema inventory | Future bridge material would need explicit source, derivation, run, and pipeline provenance. | Treating local AUTO files as provenance-sufficient by design alone. |
| A2C-001 stop/defer hold | `docs/research_pipeline/2026-05-a2c001_stop_defer_hold_lock.md` | Bridge design cannot reopen A2C-001 or create A2C-001 approval/readiness authority. | A2C-001 reopen, approval, completion, or readiness. |
| AUTO pause / local-only status | `docs/research_pipeline/2026-04-post_auto_usability_direction_decision.md`; AUTO checkpoint | AUTO remains paused, local-only, non-authoritative, and non-canonical unless later reopened. | AUTO reactivation or canonicalization. |
| Path B unauthorized status | A2C-001 hold/gate/lessons docs | Bridge design cannot select or authorize Path B. | Path B authority. |
| Runtime/protected-path boundary | `AGENTS.md`; `CLAUDE_START_HERE.md`; `docs/project_status.md`; `docs/runbook.md` | Future bridge design must remain non-runtime unless separately authorized. | Runtime, paper/live, OMS, risk, safe-mode, configs, data, or protected paths. |

## H. Future Implementation Tranche Surface

A later implementation tranche might need to decide or build the following
categories. Each category requires separate explicit authorization and may
require multiple WPs:

- bridge intake specification;
- source provenance model;
- local-to-canonical transformation contract;
- candidate/evidence binding rules;
- artifact emission rules;
- validator requirements;
- integrity-view requirements;
- query exposure requirements;
- failure/stop behavior;
- review/reporting format.

These categories are not approved by this package.

## I. Authorization Gates

Before any implementation, the project would need:

- Main/Karl/user explicit authorization for an AUTO bridge implementation
  tranche;
- explicit allowed file families;
- explicit schema/validator/query-layer authority, if any;
- explicit canonical artifact authority, if any;
- explicit data/provenance rules;
- explicit validation plan;
- explicit protected-path exclusion or review if ever relevant;
- explicit non-runtime boundary unless runtime is separately authorized later;
- explicit confirmation that no existing AUTO outputs become canonical
  retroactively by design alone.

## J. Open Questions For Main/Karl

Neutral open questions:

- Should the next design-tranche package continue to a fuller bridge design,
  or stop after this sketch?
- What canonical artifact family or evidence path, if any, should the future
  bridge target?
- Should bridge design remain candidate-agnostic, or must it bind to a future
  candidate/evidence track only after separate authorization?
- What schema/validator/query-layer authority, if any, should be considered in
  a later design package?
- What provenance standard would be required before local AUTO material can be
  considered for canonical evidence transformation?
- Should existing AUTO outputs remain permanently non-canonical, or should
  future bridge rules address only new post-bridge outputs?
- Are there efficiency improvements in bot operation or WP execution that Main
  wants to self-authorize as design-package inputs?

## K. What Is Locked

This package locks only:

- The AUTO bridge design sketch was recorded from refreshed repo truth.
- Track C / AUTO bridge architecture-design tranche has begun as
  documentation-only design.
- AUTO remains paused and local-only.
- The design sketch creates no implementation and no bridge capability.
- A2C-001 remains stopped/deferred.
- Path B remains unauthorized.
- Future bridge implementation requires separate explicit authorization.
- Main/Karl/user re-engagement is required before the next package.

## L. What Is Not Authorized

This package does not authorize:

- AUTO bridge implementation;
- AUTO reactivation in capability terms;
- canonical conversion of AUTO outputs;
- retroactive canonical status for any AUTO output;
- schema authority;
- validator authority;
- central query-layer exposure;
- canonical-corpus modification;
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

## M. Validation

Validation results for WP-12cr / WP-S2c-50:

- `git diff --check`: passed.
- Pre-staging changed-file scope:
  - `git diff --name-only`: `docs/project_status.md`.
  - `git status --short`: `M docs/project_status.md` and
    `?? docs/research_pipeline/2026-05-auto_bridge_architecture_design_sketch.md`.
  - `git ls-files --others --exclude-standard`:
    `docs/research_pipeline/2026-05-auto_bridge_architecture_design_sketch.md`.
- Advisory diff/scope helper:
  `.\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py --allowed-file docs/project_status.md --allowed-file docs/research_pipeline/2026-05-auto_bridge_architecture_design_sketch.md --json`
  passed with no allowed-file violations and no forbidden matches.
- Query views listed: 55.
- `v_integrity_*`: clean (24); every discovered integrity view ran with JSON
  output and returned `[]`.
- Registry validators: 14 `tools.registry.validate_*` modules passed.
- Helper tests:
  `.\.venv\Scripts\python.exe -m pytest tests/test_diff_scope_summary.py tests/test_validation_summary.py tests/test_code_index.py tests/test_status_snapshot.py -q`
  passed with 61 passed in 33.65 seconds.
- Scoped regression:
  `.\.venv\Scripts\python.exe -m pytest tests -q -k "registry or research_query or reconciliation or outcome_ledger or lifecycle or experiment or diff_scope_summary or validation_summary or code_index or status_snapshot"`
  passed with 303 passed and 314 deselected in 430.02 seconds.
- Full pytest:
  `.\.venv\Scripts\python.exe -m pytest -q`
  passed with 617 passed and 4 warnings in 292.36 seconds.
