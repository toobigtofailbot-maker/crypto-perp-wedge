# Repo Truth Discovery

## Fact

- `tools/registry/validate_strategy_specs.py` had closed composed-operand validation for parameter scaling, `z_score`, and `rolling_empirical_percentile_v1`.
- `tools/registry/validate_strategy_specs.py` omitted `atr_normalized_candle_ratio_v1` from `COMPOSITION_TYPES` before this package.
- `research/schemas/strategy_spec.schema.json` already included `atr_normalized_candle_ratio_composed_operand`.
- `tools/research_runner/spec_signal_compiler.py` already included `COMPOSITION_TYPE_ATR_NORMALIZED_CANDLE_RATIO` and closed compiler handling for the same operand shape.
- `tests/test_spec_signal_compiler.py` already covered ATR-normalized candle ratio values, thresholds, warmup/null/zero ATR, no-lookahead, parameter-bound lookback, and arbitrary ratio-expression rejection.
- `scratch/WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01/blocked_reason.json` records PR #604's pre-execution blocker as validator non-alignment.
- `scratch/WP-COMP-ATR-NORMALIZED-CANDLE-01/freeze_unblock_mapping.json` maps `LAB-RT-HYP-002R.range_atr_min` and `LAB-RT-HYP-004R.body_atr_min` to the compiler operand.
- `scratch/WP-COMP-ATR-NORMALIZED-CANDLE-01/compiler_surface_contract.json` defines the allowed ratio types, ATR lookback forms, zero-ATR policy, no-expression constraints, and no-authority boundaries.

## Inference

- The schema and compiler surface were already merged and closed.
- The narrow unblock was validator alignment, not schema/compiler redesign.

## Decision

- Edit only validator/test code and package artifacts.
- Do not modify `research/schemas/strategy_spec.schema.json`.
- Do not modify compiler, runner, live/runtime, data, configs, signed frozen set, or result/candidate artifacts.

## Open Question

- None for this package.

## Future Option

- A later explicitly authorized execution package may formalize Strategy Specs using this now-validator-accepted operand. This package does not do that.

