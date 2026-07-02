# WP-COMP-ATR-NORMALIZED-CANDLE-01 Branch State

## Fact

- Package: WP-COMP-ATR-NORMALIZED-CANDLE-01 - Add closed compiler support for ATR-normalized candle range/body predicates.
- Branch: `comp/atr-normalized-candle-01`.
- Base: `45f86a8c713b8ee7def2c05edeba2476ef942c7b`, the PR #602 merge state on `origin/main`.
- PR #602 status: merged.
- Blocker source: `scratch/WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01/blocked_reason.json`.

## Implementation

- Added closed `atr_normalized_candle_ratio_v1` composed operand support to `tools/research_runner/spec_signal_compiler.py`.
- Supported `ratio_type` values are exactly `candle_range_atr_ratio` and `candle_body_atr_ratio`.
- `candle_range_atr_ratio` computes `(high - low) / ATR(lookback)`.
- `candle_body_atr_ratio` computes `abs(close - open) / ATR(lookback)`.
- ATR uses the existing closed `atr_v1` compiler convention and existing literal or parameter-bound lookback resolution.
- `zero_atr_policy` is fixed to `null_output`; warmup, null, and zero-ATR outputs remain false under the existing condition null policy.
- Updated `research/schemas/strategy_spec.schema.json` only to admit the new closed composed operand shape.
- Left `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json` unchanged because this is a composed compiler operand over existing ATR/OHLCV fields, not a new catalog indicator.

## Boundary

- No research execution was performed.
- The signed revised frozen set was inspected only and not modified.
- No Strategy Spec, Variant Manifest, Sweep Plan, Result Population, candidate registry, crossing, readiness, promotion, paper/live, runtime, OMS, risk, reconciliation, broker, exchange, config, data, dependency, or protected path was changed.
- The new surface is compiler/schema-only and creates no candidate lifecycle or execution authority.

## Validation

- JSON validation: PASS for `compiler_surface_contract.json`, `freeze_unblock_mapping.json`, and `non_authority_assertions.json`.
- Research query view discovery: PASS.
- Result Population validator: PASS.
- Candidate registry validator: PASS.
- Indicator catalog validator: PASS.
- Strategy Spec validator: PASS.
- Direct Strategy Spec schema sanity check for `atr_normalized_candle_ratio_v1`: PASS.
- Focused compiler tests: PASS, `252 passed`.
- Diff-scope summary: PASS / advisory `research/` match only for package-allowed `research/schemas/strategy_spec.schema.json`.
- `git diff --check`: PASS.
- Full pytest: not run; package changed only the focused compiler/schema surface and focused compiler tests plus direct schema/catalog validators passed.
