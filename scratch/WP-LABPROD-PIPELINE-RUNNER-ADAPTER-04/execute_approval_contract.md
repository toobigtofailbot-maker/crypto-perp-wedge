# Execute Approval Contract

## Decision

The runner adapter requires a separate Karl exact-content execute approval. A bridge preparation approval or broad lab prereg approval is not accepted for runner execution.

## Schema

- `schema_version`: `product_runner_execute_approval_v1`
- `approved_by`: `Karl`
- `approval_scope`: `noncanonical_product_runner_execution_only`
- `approval_statement`: `Authorizes only non-canonical product runner execution for the exact bridge-prepared Strategy Spec, Variant Manifest, and Sweep Plan artifacts.`
- `approval_timestamp_utc`: required UTC-like ISO-8601 string ending in `Z`; audit syntax only, no wall-clock expiry.
- `prepared_strategy_spec_path` and `prepared_strategy_spec_sha256`
- `prepared_variant_manifest_path` and `prepared_variant_manifest_sha256`
- `prepared_sweep_plan_path` and `prepared_sweep_plan_sha256`
- `bridge_preparation_run_id`
- `product_pipeline_run_id`
- `runner_adapter_stage_identity`: `noncanonical_offline_runner_execution`
- `product_output_root`: package-local output root under `scratch/WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04/outputs`
- `authorizes_runner_execution`: `true`

## Required False Authority Flags

- `authorizes_canonical_write`
- `authorizes_candidate_lifecycle`
- `authorizes_wfo_oos_execution`
- `authorizes_robustness_execution`
- `authorizes_candidate_review_execution`
- `authorizes_paper_live_runtime`
- `authorizes_scheduler_autonomy`
- `authorizes_notification`
- `authorizes_provider_api_credential`
- `authorizes_dependency_config_data_acquisition`
- `authorizes_protected_path_touch`

## Fail-Closed Rejections

The adapter rejects missing, malformed, broad, or mismatched execute approvals, including:

- bridge preparation approval reused as execute approval;
- broad pipeline prereg approval reused as execute approval;
- wrong actor, scope, statement, stage, bridge run, product run, output root, or timestamp syntax;
- prepared Strategy Spec / Variant Manifest / Sweep Plan path or hash mismatch;
- missing `authorizes_runner_execution = true`;
- any protected authority flag not exactly `false`.

## Implementation

- Contract implementation: `tools/lab_pipeline/runner_adapter.py`.
- Template helper: `approval_template()`.
- Runtime validator: `_require_execute_approval()`.
- Focused coverage: `tests/test_lab_pipeline_runner_adapter.py`.
