# AUTO Bridge Candidate-Artifact Draft Implementation

## A. Scope

WP-12de / WP-S2c-66+67 is a bundled Tier 3 implementation + tests package for
the AUTO bridge candidate-artifact draft production layer only.

The package creates bridge-local in-memory candidate-artifact draft primitives
and tests. It does not implement consumer surfaces, file output, central query
views, registry validators, canonical artifact commitment, or candidate
binding.

The implementation is local-only, non-canonical, candidate-agnostic,
post-bridge-only, fail-closed, deterministic, and creates no canonical
artifacts.

## B. Repo-Truth Basis

Reference block:

- `docs/research_pipeline/2026-05-a2c001_cohort_phase_closure_decision.md`
  formally closes A2C-001 as complete-as-built and records that the closure
  does not authorize Path B, A2C-002, artifacts, trial-log rows,
  schema/validator/query changes, runtime, approval/readiness/lifecycle,
  policy/scoring/ranking/recommendation, or downstream authority.
- `docs/research_pipeline/2026-05-auto_bridge_design_tranche_checkpoint.md`
  records the completed bridge design tranche, local-only/non-canonical AUTO
  posture, candidate-agnostic bridge posture, and no retroactive canonical
  status for existing AUTO outputs.
- `docs/research_pipeline/2026-05-auto_bridge_retroactivity_posture.md` locks
  existing pre-bridge AUTO outputs as permanently non-canonical and not
  eligible for retroactive canonical transformation.
- `docs/research_pipeline/2026-05-auto_bridge_provenance_canonical_target_design.md`
  records the future-output-only provenance minimum bar and
  candidate-agnostic future-output-only canonical-target posture.
- `docs/research_pipeline/2026-05-auto_bridge_schema_validator_query_validation_design.md`
  records no schema, validator, or central query-layer authority for AUTO
  bridge work under the design tranche.
- `docs/research_pipeline/2026-05-auto_bridge_implementation_tranche_boundary.md`
  records the future implementation-tranche boundary and stop posture.
- `docs/research_pipeline/2026-05-auto_bridge_intake_source_layer_implementation.md`
  records the WP-12db intake/source-layer implementation.
- `docs/research_pipeline/2026-05-auto_bridge_transformation_normalization_implementation.md`
  records the WP-12dc transformation/normalization implementation.
- `docs/research_pipeline/2026-05-auto_bridge_validation_integrity_implementation.md`
  records the WP-12dd validation/integrity implementation and states that the
  next package surface is likely bridge candidate-artifact production.

The active WP-12de / WP-S2c-66+67 brief provides the explicit implementation
authority for this narrow candidate-artifact draft surface after merged
WP-12dd.

## C. Implementation Summary

Created or updated files:

- `tools/research_automation/bridge/__init__.py`
- `tools/research_automation/bridge/candidate_artifact.py`
- `tests/research_automation/test_bridge_candidate_artifact.py`

The new module defines:

- `BridgeCandidateArtifactError`
- `BridgeCandidateArtifactDraft`
- `create_candidate_artifact_draft`
- `sha256_draft_payload`

`create_candidate_artifact_draft` consumes a WP-12dc
`BridgeNormalizedRecord` only after a WP-12dd `BridgeValidationResult` is
valid, issue-free, stage-matched, local-only, non-canonical, and explicitly
non-committing. If no validation result is supplied, the function internally
calls `assert_valid_normalized_record`.

## D. Candidate-Artifact Draft Behavior

Candidate-artifact drafts are bridge-local, in-memory, and non-canonical.

Each draft records:

- the source normalized bridge record;
- the validation result and issue summary;
- a caller-provided local draft type and target label;
- a caller-provided draft payload mapping;
- a provenance summary preserving intake and transformation lineage;
- `local_only=True`;
- `non_canonical=True`;
- `candidate_bound=False`;
- `creates_canonical_artifact=False`;
- `creates_committed_evidence=False`;
- bridge stage `candidate_artifact_draft`;
- a deterministic draft digest over stable JSON content.

The producer rejects non-normalized input, invalid validation results,
validation results with issues, stage or posture mismatches, unsupported or
empty draft payloads, canonical-status claims, artifact-commitment claims,
pre-bridge/retroactive-transformation claims, candidate-binding metadata,
actual `REP-`, `OL-`, `REC-`, or `EXP-` ID claims, lifecycle/registry/query
claims, trial-log claims, and artifact/output path claims.

The module performs no filesystem reads, no file writes, no real AUTO output
reads, no canonical artifact creation, and no trial-log append.

## E. Tests

`tests/research_automation/test_bridge_candidate_artifact.py` proves:

- valid WP-12dc normalized bridge records plus valid WP-12dd validation
  results create drafts;
- intake and transformation provenance is preserved;
- drafts are local-only, non-canonical, not candidate-bound, and not committed
  evidence;
- draft digests are deterministic and caller mappings are not mutated;
- non-normalized input is rejected;
- invalid validation results and validation results with issues are rejected;
- validation-result stage and posture mismatches are rejected;
- canonical-status metadata is rejected;
- artifact-commitment metadata is rejected;
- candidate-binding metadata is rejected;
- pre-bridge and retroactive-transformation metadata is rejected;
- actual canonical ID, artifact path, output path, trial-log, lifecycle,
  registry, and query-view claims are rejected;
- unsupported or empty draft payloads are rejected;
- draft production does not write files or create canonical artifacts.

Existing intake, transform, and validate tests remain part of package
validation.

## F. What Is Locked

This package locks only that the AUTO bridge candidate-artifact draft
implementation and tests exist under local-only, candidate-agnostic,
post-bridge-only, fail-closed, deterministic, non-canonical boundaries.

Candidate-artifact draft means a bridge-local in-memory draft representation
only. It is not a canonical artifact, committed evidence, registry row,
query-layer row, candidate-bound evidence object, approval input, lifecycle
object, or downstream-authority surface.

## G. What Is Not Authorized

This package does not authorize:

- consumer surfaces;
- file output or artifact writing;
- canonical artifact commitment;
- REP/OL/REC/EXP/lifecycle/registry/query artifact creation;
- schemas, validators, central query-layer changes, or integrity views;
- trial-log rows;
- Path B;
- A2C-002;
- runtime, paper/live, OMS, risk, safe-mode, exchange, broker, order, or
  execution behavior;
- approval, readiness, lifecycle, promotion, demotion, or downstream authority;
- policy, scoring, ranking, recommendation, or evidence-quality scoring;
- candidate binding;
- transformation of existing pre-bridge AUTO outputs;
- use of existing AUTO outputs as canonical evidence.

## H. Next Package Surface

The next package surface is likely bridge end-to-end orchestration, consumer
brief, or implementation-checkpoint work, only under Main's authorized AUTO
bridge implementation tranche and only after this package merges,
refreshed-main preflight passes, and no stop trigger fires.
