# AUTO Bridge Validation / Integrity Implementation

## A. Scope

WP-12dd / WP-S2c-64+65 is a bundled Tier 3 implementation + tests package for
the AUTO bridge validation/integrity-check layer only.

The package creates bridge-local validation primitives and tests. It does not
implement candidate-artifact production, consumer surfaces, central query
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
  records the WP-12dc transformation/normalization implementation and states
  that the next package surface is likely validation/integrity.

The active WP-12dd / WP-S2c-64+65 brief provides the explicit implementation
authority for this narrow validation/integrity surface after merged WP-12dc.

## C. Implementation Summary

Created or updated files:

- `tools/research_automation/bridge/__init__.py`
- `tools/research_automation/bridge/validate.py`
- `tests/research_automation/test_bridge_validate.py`

The new module defines:

- `BridgeValidationError`
- `BridgeValidationIssue`
- `BridgeValidationResult`
- `validate_normalized_record`
- `assert_valid_normalized_record`

`validate_normalized_record` consumes a WP-12dc `BridgeNormalizedRecord` and
returns a deterministic in-memory validation result. The result records
validity, issues, the checked stage, local-only/non-canonical posture, and
explicit false canonical-artifact/committed-evidence flags.

## D. Validation / Integrity Behavior

The validation layer is post-bridge-only and fail-closed.

It rejects:

- non-`BridgeNormalizedRecord` input;
- normalized records that do not preserve local-only/non-canonical state;
- normalized records that claim canonical artifact creation or committed
  evidence;
- unsupported bridge stages;
- missing or malformed payload digests;
- empty normalized payloads;
- missing or invalid intake records;
- missing intake source identity or run identity;
- intake records that fail the WP-12db local-only/non-canonical/post-bridge
  boundary;
- normalized payload, metadata, or intake provenance metadata that contains
  canonical-status, artifact-commitment, candidate-binding, pre-bridge, or
  retroactive-transformation claims.

The module does not scan real AUTO output directories, crawl files, read source
paths, write files, emit REP/OL/REC/EXP/lifecycle/registry/query artifacts, or
append trial-log rows.

## E. Tests

`tests/research_automation/test_bridge_validate.py` proves:

- valid WP-12dc normalized bridge records validate successfully;
- `assert_valid_normalized_record` succeeds for valid records and raises
  `BridgeValidationError` for invalid records;
- non-`BridgeNormalizedRecord` input is rejected;
- non-local/canonical normalized records are rejected;
- unsupported bridge stages are rejected;
- missing or malformed payload digests are rejected;
- empty normalized payloads are rejected;
- canonical-status metadata is rejected;
- artifact-commitment metadata is rejected;
- candidate-binding metadata is rejected;
- pre-bridge and retroactive-transformation metadata is rejected;
- invalid or missing intake provenance is rejected;
- validation does not write files or create canonical artifacts.

Existing intake and transform tests remain part of package validation.

## F. What Is Locked

This package locks only that the AUTO bridge validation/integrity-check
implementation and tests exist under local-only, candidate-agnostic,
post-bridge-only, fail-closed, deterministic, non-canonical boundaries.

Validation results are local in-memory representations only. They are not
canonical artifacts, committed evidence, registry rows, query-layer rows, or
candidate-bound evidence objects.

## G. What Is Not Authorized

This package does not authorize:

- candidate-artifact production;
- canonical artifact commitment;
- REP/OL/REC/EXP/lifecycle/registry/query artifact creation;
- schemas, validators, central query-layer changes, or integrity views;
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

The next package surface is likely bridge candidate-artifact production, only
under Main's authorized AUTO bridge implementation tranche and only after this
package merges, refreshed-main preflight passes, and no stop trigger fires.
