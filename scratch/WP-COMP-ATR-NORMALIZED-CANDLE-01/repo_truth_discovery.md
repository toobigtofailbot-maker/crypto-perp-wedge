# WP-COMP-ATR-NORMALIZED-CANDLE-01 Repo Truth Discovery

## Fact

- Base commit: `45f86a8c713b8ee7def2c05edeba2476ef942c7b`.
- PR #602 is merged: `https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/602`.
- Current blocker file exists at `scratch/WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01/blocked_reason.json`.
- Signed revised frozen set exists at `scratch/WP-LAB-REAL-TRAFFIC-REVISED-SIGNOFF-FREEZE-01/revised_frozen_hypothesis_set.json`.
- Required compiler file inspected: `tools/research_runner/spec_signal_compiler.py`.
- Required compiler tests inspected: `tests/test_spec_signal_compiler.py`.
- Required catalog inspected: `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json`.
- Required catalog schema inspected: `research/schemas/indicator_catalog.schema.json`.
- Required Strategy Spec schema inspected: `research/schemas/strategy_spec.schema.json`.
- Required status entries inspected:
  - `docs/status_entries/WP-COMPILER-INDICATORS-VOLUME-01.md`
  - `docs/status_entries/WP-COMPILER-FEATURES-DATA-DERIVED-01.md`

## Inference

- Existing ATR support is already a closed compiler builtin through `atr_v1`.
- Existing candle-shape support normalizes wick/body percentages by candle high-low range, not by ATR.
- Existing composed operands are the narrowest repo-native surface for closed derived numeric operands used in Strategy Spec conditions.
- The indicator catalog does not need a new entry because the new behavior composes existing OHLCV fields with existing ATR rather than declaring a standalone catalog indicator.

## Decision

- Implement `candle_range_atr_ratio` and `candle_body_atr_ratio` as closed `atr_normalized_candle_ratio_v1` composed operands.
- Update the Strategy Spec schema to admit only that closed composed operand shape.
- Do not modify the indicator catalog.
- Do not execute the real-traffic revised batch.

## Open Question

- None for this package.

## Future Option

- A later authorized execution package may use this surface to formalize the already-frozen `LAB-RT-HYP-002R.range_atr_min` and `LAB-RT-HYP-004R.body_atr_min` axes without changing this package's non-execution posture.
