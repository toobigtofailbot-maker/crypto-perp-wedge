# WP-LAB-BASELINE-PAYLOAD-DEFINE-01 Repo Truth Discovery

## Fact

- Base commit: `b060059fcd09de790344e8c3336ef27711527162`.
- Refreshed `main` by fast-forward from `788f46c` to `b060059`.
- Required PR #582 artifacts are present:
  - `docs/status_entries/WP-RESEARCH-FUNDING-FADE-RISKMANAGED-CONCLUDE-01.md`
  - `docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md`
  - `scratch/WP-RESEARCH-FUNDING-FADE-RISKMANAGED-CONCLUDE-01/conclusion_summary.json`
  - `scratch/WP-RESEARCH-FUNDING-FADE-RISKMANAGED-CONCLUDE-01/operator_visibility_binding.json`
  - `tools/lab_state/run.py`
- No existing `WP-LAB-BASELINE-PAYLOAD-DEFINE-01` package was found by repo search.
- No local or remote branch named `lab/baseline-payload-define-01` existed before this package branch was created.
- Pre-existing untracked local path observed before package work: `build/`. It was not inspected, modified, staged, or used.

## Fact: Supported Primitive And Artifact Surface

- Current Strategy Spec grammar supports closed condition groups over `data_ref`, `indicator_ref`, `parameter_ref`, `constant`, `primitive_ref`, and limited `composed_operand` forms.
- Current simple supported price-only primitives include `sma` and `stddev`, as evidenced by:
  - `research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json`
  - `research/strategy_specs/STRAT-SPEC-0004.strategy_spec.json`
  - `research/variant_manifests/VM-0003.variant_manifest.json`
  - `research/sweep_plans/SWEEP-PLAN-0003.sweep_plan.json`
  - `tools/research_runner/spec_signal_compiler.py`
  - `tools/registry/validate_strategy_specs.py`
  - `tools/registry/validate_variant_sweep_artifacts.py`
- Current schema and validator surfaces already treat Strategy Specs, Variant Manifests, and Sweep Plans as non-execution planning artifacts.

## Fact: Existing Construction / Non-Promotable Idiom

- Search found no schema-level fields named exactly:
  - `construction_payload`
  - `non_promotable`
  - `candidate_eligible`
  - `promotion_eligible`
  - `paper_live_eligible`
  - `edge_claim_allowed`
  - `canonical_crossing_allowed`
- Current schemas use strict `additionalProperties: false`.
- The exact required permanent provenance fields cannot be inserted into Strategy Spec, Variant Manifest, or Sweep Plan JSON without schema changes.

## Inference

- The repo can describe baseline payloads using existing SMA / StdDev / closed-condition vocabulary.
- The repo cannot yet express the required permanent construction-only and non-promotable fields inside schema-validated Strategy Spec / Variant Manifest / Sweep Plan artifacts.
- Scratch Strategy Spec / Variant Manifest / Sweep Plan drafts would therefore either omit required hard provenance semantics or require schema changes. Both outcomes are outside this package intent.

## Decision

- Use a contract-only route for this package.
- Define three construction payloads in `baseline_payload_catalog.*` and `baseline_ground_truth_contract.*`.
- Do not create scratch Strategy Spec, Variant Manifest, or Sweep Plan drafts in this package.
- Record schema-level provenance support as a deferred requirement.

## Chosen Artifact Locations

- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/repo_truth_discovery.md`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_payload_catalog.json`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_payload_catalog.md`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_ground_truth_contract.json`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_ground_truth_contract.md`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/non_promotable_provenance_contract.md`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/later_consumer_map.md`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/blocked_or_deferred_requirements.json`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/validation_summary.txt`
- `docs/status_entries/WP-LAB-BASELINE-PAYLOAD-DEFINE-01.md`

## Boundary Statement

No execution is authorized here. This package does not run a strategy, run a backtest, write a canonical Result Population, write candidate lifecycle records, create a candidate-review packet, cross any candidate, promote any candidate, touch paper/live/runtime paths, touch OMS/risk/reconciliation/order/exchange paths, acquire data, or change code/schema/validator behavior.
