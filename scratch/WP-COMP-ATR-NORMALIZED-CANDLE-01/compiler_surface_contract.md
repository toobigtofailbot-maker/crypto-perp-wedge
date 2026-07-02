# Compiler Surface Contract

## Fact

`atr_normalized_candle_ratio_v1` is a closed `composed_operand` surface with exactly two ratio outputs:

- `candle_range_atr_ratio`: `(high - low) / ATR(lookback)`
- `candle_body_atr_ratio`: `abs(close - open) / ATR(lookback)`

ATR lookback uses the existing compiler lookback forms: literal `{"bars": n}` or parameter-bound `{"bars_parameter_ref": "name"}`.

## Decision

The surface is implemented as a Strategy Spec composed operand, not as a free-form formula, data provider, or new executable catalog entry.

## Boundary

The surface creates no Strategy Spec instance, no sweep, no result population, no candidate admission, no crossing, no readiness or promotion authority, and no paper/live/runtime authority.
