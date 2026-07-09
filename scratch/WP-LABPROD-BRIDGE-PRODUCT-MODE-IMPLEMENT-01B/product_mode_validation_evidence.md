# Product Mode Validation Evidence

## Verdict

Product mode is additive, opt-in, product-scratch-local, Karl exact-content-bound, and prepare-only.

## Approval Strictness

Implemented product approval schema:

- `schema_version = product_bridge_preparation_approval_v1`
- `approved_by = Karl`
- `approval_scope = noncanonical_product_bridge_preparation_only`
- exact approval statement
- UTC-like ISO-8601 `approval_timestamp_utc`
- source product packet path/hash
- source formalizer output path/hash
- reproducible approval marker content hash
- source formalizer run id
- product pipeline run id
- bridge stage identity
- product-mode output root
- `authorizes_bridge_preparation = true`
- all protected authority flags false, including runner execution

The approval timestamp is parsed for audit syntax only. No wall-clock comparison is performed.

## Product Scratch / Output

Product mode accepts only `WP-LABPROD-BRIDGE-PRODUCT-MODE-IMPLEMENT-01B` with role `formalizer_runner_bridge`. Source product packet, formalizer output, approval marker, and product output root must remain under that active product scratch tree. Output root must be `scratch/<wp_id>/outputs` or a descendant inside it.

## Bridge-Owned Validation

The product mode reuses bridge-owned:

- formalizer contract validation
- draft Strategy Spec validation through `validate_strategy_specs`
- derived Strategy Spec validation through `validate_strategy_specs`
- Variant Manifest / Sweep Plan validation through `validate_variant_sweep_artifacts`
- denominator integrity assertion

The focused positive product test asserts at least three `run_read_only_validation` audit records.

## Runner Isolation

Product mode does not call `_invoke_runner`, does not call `run_offline_sweep`, and does not request `RUN_NONCANONICAL_OFFLINE_SWEEP`. Product review packets record:

- `runner = null`
- `runner_invoked = false`
- `runner_boundary = not_requested`
- empty `runner_artifact_paths`

## Focused Test Evidence

- `.venv\Scripts\python.exe -m pytest tests/test_agent_formalizer_runner_bridge.py -q`
- Result: `65 passed`

Covered product-mode cases include:

- requires Karl bridge-specific approval
- rejects legacy operator approval
- rejects broad lab prereg approval
- rejects wrong actor/scope/statement
- rejects missing/malformed timestamp
- accepts an old timestamp without wall-clock expiry
- rejects source product packet hash mismatch
- rejects formalizer output hash mismatch
- rejects approval content hash mismatch
- rejects source run/product run/stage/output-root mismatch
- rejects any protected authority flag set true
- rejects source paths outside product scratch
- rejects output root outside product scratch
- writes only product scratch outputs
- validates derived artifacts
- fails closed on invalid draft without runner artifacts, denominator ledger, or review packet
- proves no `_invoke_runner` call with unblocked inputs

Adapter regression:

- `.venv\Scripts\python.exe -m pytest tests/test_lab_pipeline_bridge_adapter.py -q`
- Result: `6 passed`

The old adapter WP remains blocked by default and is not accepted in product mode.
