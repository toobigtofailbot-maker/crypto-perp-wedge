# AUTO Bridge Transformation / Normalization Implementation

## A. Scope

WP-12dc / WP-S2c-62+63 is a bundled Tier 3 implementation + tests package for
the AUTO bridge transformation/normalization layer only.

The package creates local-only bridge normalization primitives and tests. It
does not implement validation/integrity, candidate-artifact production,
consumer surfaces, central query views, registry validators, canonical artifact
commitment, or candidate binding.

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
  records the WP-12db intake/source-layer implementation and states that the
  next package surface is likely transformation/normalization.

The active WP-12dc / WP-S2c-62+63 brief provides the explicit implementation
authority for this narrow transformation/normalization surface after merged
WP-12db.

## C. Implementation Summary

Created or updated files:

- `tools/research_automation/bridge/__init__.py`
- `tools/research_automation/bridge/transform.py`
- `tests/research_automation/test_bridge_transform.py`

The new module defines:

- `BridgeTransformError`
- `BridgeNormalizedRecord`
- `normalize_bridge_payload`
- `sha256_json_payload`

`normalize_bridge_payload` consumes a validated WP-12db `BridgeIntakeRecord`
and a caller-provided in-memory mapping payload. It normalizes JSON-like
mapping content through stable JSON serialization, preserves intake
provenance, records the `normalized` bridge stage, marks the result as
local-only and non-canonical, and records that no canonical artifact or
committed evidence is created.

## D. Eligibility And Rejection Behavior

The transformation layer is post-bridge-only and fail-closed.

It rejects:

- non-`BridgeIntakeRecord` intake input;
- intake records that do not preserve local-only/non-canonical state;
- intake records that claim canonical artifact creation or committed evidence;
- unsupported or empty payload mappings;
- payload or metadata that claims canonical status;
- payload or metadata that claims artifact commitment or trial-log append
  behavior;
- payload or metadata containing candidate-binding keys such as
  `candidate_id`, `symbol`, `cohort`, `path_b`, or nested candidate-binding
  fields;
- payload or metadata containing pre-bridge or retroactive-transformation
  claims.

The module does not scan real AUTO output directories, crawl files, read source
paths, write files, emit REP/OL/REC/EXP/lifecycle/registry/query artifacts, or
append trial-log rows.

## E. Tests

`tests/research_automation/test_bridge_transform.py` proves:

- valid WP-12db intake plus in-memory mapping payload succeeds;
- returned normalized records are local-only and non-canonical;
- intake provenance is preserved;
- normalized payload values and payload digests are deterministic;
- non-`BridgeIntakeRecord` input is rejected;
- non-local/canonical intake records are rejected;
- canonical-status metadata is rejected;
- artifact-commitment metadata is rejected;
- candidate-binding metadata is rejected in payloads and nested metadata;
- pre-bridge and retroactive-transformation claims are rejected;
- unsupported payload types are rejected;
- normalization does not write files or create canonical artifacts.

Existing intake tests remain part of the package validation.

## F. What Is Locked

This package locks only that the AUTO bridge transformation/normalization
implementation and tests exist under local-only, candidate-agnostic,
post-bridge-only, fail-closed, deterministic, non-canonical boundaries.

The normalized bridge record is a local in-memory representation only. It is
not a canonical artifact, committed evidence, registry row, query-layer row, or
candidate-bound evidence object.

## G. What Is Not Authorized

This package does not authorize:

- validation/integrity layer implementation;
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

The next package surface is likely the bridge validation/integrity-check layer.
Codex/Side must wait until this PR is merged and refreshed-main preflight
passes before continuing under Main's authorized tranche, unless a stop trigger
fires.
