# Blocked Reason

Decision: `blocked`

The package blocked before real research execution.

## Fact

The signed revised frozen set exists on `origin/main` at `scratch/WP-LAB-REAL-TRAFFIC-REVISED-SIGNOFF-FREEZE-01/revised_frozen_hypothesis_set.json`. It contains exactly `LAB-RT-HYP-001`, `LAB-RT-HYP-002R`, `LAB-RT-HYP-003R`, and `LAB-RT-HYP-004R`.

Main verification and Karl signoff are present. The freeze-fidelity audit records pass.

## Blocking Fact

Current `origin/main` includes schema/compiler support for `atr_normalized_candle_ratio_v1`, which maps the previously missing frozen axes:

- `LAB-RT-HYP-002R` `range_atr_min` -> `candle_range_atr_ratio >= threshold`
- `LAB-RT-HYP-004R` `body_atr_min` -> `candle_body_atr_ratio >= threshold`

The Strategy Spec validator has not yet been aligned with that composition type. Its closed `COMPOSITION_TYPES` set omits `atr_normalized_candle_ratio_v1`, while the compiler includes it. The offline runner validates parent Strategy Specs before execution, so an exact formalization would fail runner preflight without a validator/schema/runner change.

## Decision

The batch is blocked before execution. No partial run was performed.

## Boundary

No schema, compiler, runner, result-population, candidate lifecycle, crossing, paper/live/runtime, OMS, risk, reconciliation, broker, exchange, dependency, or data path was changed.

## Future Option

A later explicitly authorized package could align the Strategy Spec validator with the existing ATR-normalized candle schema/compiler route, then retry the frozen batch without retuning.
