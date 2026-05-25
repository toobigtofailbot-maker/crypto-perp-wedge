# AUTO Bridge Intake / Source-Layer Implementation

## A. Scope

WP-12db / WP-S2c-60+61 is a bundled Tier 3 implementation + tests package for
the AUTO bridge intake/source layer only.

The package creates local-only bridge intake primitives and tests. It does not
implement transformation, normalization, artifact production, validation /
integrity layer, consumer surfaces, central query views, registry validators,
canonical artifact commitment, or candidate binding.

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
  records the future-output-only provenance minimum bar and candidate-agnostic
  future-output-only canonical-target posture.
- `docs/research_pipeline/2026-05-auto_bridge_schema_validator_query_validation_design.md`
  records no schema, validator, or central query-layer authority for AUTO
  bridge work under the design tranche.
- `docs/research_pipeline/2026-05-auto_bridge_implementation_tranche_boundary.md`
  records the future implementation-tranche boundary and stop posture.

The active WP-12db / WP-S2c-60+61 brief provides the explicit implementation
authority for this narrow intake/source-layer surface after WP-12da closure.

## C. Implementation Summary

Created files:

- `tools/research_automation/bridge/__init__.py`
- `tools/research_automation/bridge/intake.py`
- `tests/research_automation/test_bridge_intake.py`

The new module defines:

- `BridgeSourceRef`
- `BridgeRunContext`
- `BridgeIntakeRecord`
- `BridgeIntakeError`
- `create_intake_record`
- `sha256_bytes`

The intake function accepts explicit caller-provided source and run-context
objects only. It validates source identity, source kind, post-bridge
eligibility, local-only/non-canonical state, run identity, run timestamp,
provenance metadata, caller-supplied parameters, and optional content digest.

## D. Eligibility And Rejection Behavior

The intake layer is post-bridge-only and fail-closed.

It rejects:

- pre-bridge source era;
- missing source identity;
- missing source kind;
- missing run identity;
- missing run timestamp;
- missing local-only/non-canonical state marker;
- metadata that claims canonical status;
- metadata that claims artifact commitment or trial-log append behavior;
- candidate-binding metadata such as candidate, symbol, cohort, Path B, or
  nested candidate-binding fields;
- unsupported source eligibility markers.

Returned intake records are local-only and non-canonical. They explicitly
record that they create no canonical artifact and no committed evidence.

The module does not scan real AUTO output directories, crawl files, read source
paths, write files, emit REP/OL/REC/EXP/lifecycle/registry/query artifacts, or
append trial-log rows.

## E. Tests

`tests/research_automation/test_bridge_intake.py` proves:

- valid post-bridge local-only source intake succeeds;
- pre-bridge source era is rejected;
- missing source identity is rejected;
- missing run identity is rejected;
- missing local-only/non-canonical marker is rejected;
- canonical-status metadata is rejected;
- artifact-commitment metadata is rejected;
- candidate-binding metadata is rejected;
- provenance fields are preserved in the returned record;
- caller-supplied byte digests are deterministic;
- intake does not write files or create canonical artifacts.

## F. What Is Locked

This package locks only that the first AUTO bridge intake/source-layer
implementation and tests exist under local-only, candidate-agnostic,
post-bridge-only, fail-closed, non-canonical boundaries.

## G. What Is Not Authorized

This package does not authorize:

- transformation or normalization;
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

The next package is likely bridge transformation/normalization layer
implementation. Codex/Side must wait until this PR is merged and refreshed-main
preflight passes before continuing under Main's authorized tranche, unless a
stop trigger fires.
