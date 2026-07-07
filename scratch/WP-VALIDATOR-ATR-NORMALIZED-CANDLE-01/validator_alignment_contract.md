# Validator Alignment Contract

## Decision

The Strategy Spec validator accepts `atr_normalized_candle_ratio_v1` only in the same closed shape already present in the Strategy Spec schema and compiler.

## Accepted Shape

- `operand_type`: `composed_operand`
- `composition_type`: `atr_normalized_candle_ratio_v1`
- `ratio_type`: `candle_range_atr_ratio` or `candle_body_atr_ratio`
- `atr_lookback`: literal `bars` integer >= 1, or `bars_parameter_ref` validated through existing integer lookback parameter rules
- `zero_atr_policy`: `null_output`

## Rejected Shape

- Unknown `ratio_type`
- Missing or extra operand keys
- Unknown composed-operand types
- Arbitrary expression, formula, code, script, eval, or similar executable-looking payload keys
- Nested or otherwise unauthorized composed operands

## Boundary

This contract does not authorize research execution, Strategy Spec creation, variant or sweep creation, result population writes, candidate admission, crossing, promotion/readiness, paper/live, runtime, OMS, risk, broker, exchange, data, config, dependency, runner, or compiler changes.

