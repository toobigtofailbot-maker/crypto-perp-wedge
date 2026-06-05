# Composition Extension Checkpoint

## Status / Authority

This is a checkpoint document only.

It does not authorize first canonical Strategy Spec creation. It does not authorize variant manifest or sweep plan creation. It does not authorize canonical sweeps. It does not authorize canonical writes. It does not authorize compiler/schema/catalog changes. It does not authorize deferred capabilities. It does not create ranking, readiness, recommendation, approval, promotion, or runtime authority.

## Tranche Inventory

WP-S2c-204 created `docs/research_pipeline/2026-06-closed_composition_extension_design.md`. It selected the bounded design direction: a distinct `composed_operand`, initially closed to `scale_by_one_minus_parameter`, with no expression language and no runner/backtester/lib requirement.

WP-S2c-205 updated `research/schemas/strategy_spec.schema.json`, `tools/registry/validate_strategy_specs.py`, `tests/test_validate_strategy_specs.py`, and `docs/project_status.md`. It extended Strategy Spec grammar and validation for composed operands while preserving the non-executing Strategy Spec boundary.

WP-S2c-206 updated `tools/research_runner/spec_signal_compiler.py`, `tests/test_spec_signal_compiler.py`, and `docs/project_status.md`. It implemented build-and-test-only compiler support for the approved composed operand surface, with no canonical Strategy Spec, variant manifest, sweep plan, result population, signal artifact, runner/backtester/lib change, or runtime influence.

## Closed Composition Surface Now Available

The approved surface is:

```text
operand_type: composed_operand
composition_type: scale_by_one_minus_parameter
base_operand: data_ref or indicator_ref only
parameter_operand: parameter_ref only
no nested composed_operand
no composition-of-composed_operand
no multi-parameter composition
parameter value: numeric, finite, non-bool, 0 < value < 1
```

The target expression now supported is:

```text
close < SMA(20) * (1 - entry_distance_threshold)
```

This is a fixed-arity, single-form, compiler-owned computation. It is not an expression language.

## Schema / Validator Confirmation

`research/schemas/strategy_spec.schema.json` includes `composed_operand` as a distinct operand type. `composition_type` is closed to `scale_by_one_minus_parameter`. `base_operand` is restricted to `data_ref` / `indicator_ref`. `parameter_operand` is restricted to `parameter_ref`.

`tools/registry/validate_strategy_specs.py` rejects nested composition and requires the bound parameter declaration to exist exactly once. The bound parameter must be `type: number`, `role: entry`, `is_free_parameter: true`, and `included_in_variant_generation: true`. Its range must have `min > 0` and `max < 1`; any `allowed_values` must be numeric and in `(0,1)`.

The recursive forbidden-key posture is preserved, including rejection of executable, lookahead, forward-fill, backfill, interpolation, future-value, authority, broker, exchange, order, and runtime key names.

## Compiler Confirmation

`tools/research_runner/spec_signal_compiler.py` dispatches `composed_operand` through the existing operand resolver. The composed base operand resolves through the existing resolver. The parameter operand resolves through the existing `parameter_ref` resolver. `scale_by_one_minus_parameter` computes:

```text
base * (1 - parameter)
```

The result feeds the existing closed comparison evaluator. No other computation path was added.

## Null / No-Lookahead / Determinism Confirmation

`tests/test_spec_signal_compiler.py` confirms:

- base null/warmup propagates as null in the composed series;
- null operands produce false conditions through existing comparison logic;
- no fill, forward-fill, backfill, or interpolation is added;
- future OHLCV mutation does not change past signal decisions;
- identical inputs produce identical signals.

## No-Other-Path Confirmation

No `eval`. No `exec`. No lambda. No dynamic import. No string arithmetic parser. No formula parser. No AST evaluator. No operator-precedence evaluator. No user-defined functions. No catalog-data-interpreted computation. No notes-as-computation. No runner/backtester/lib change.

## Revised First-Spec Path Now Available

The revised first canonical Strategy Spec path is surfaced for later Main/Karl decision only:

```text
direction: long-only
instrument: BTCUSDT perpetual
timeframe: 15m
data: OHLCV-only
entry: close < SMA(n) * (1 - entry_distance_threshold)
exit: close >= SMA(n)
SMA lookback n: fixed literal, not swept
entry_distance_threshold: swept parameter, 0 < value < 1
optional max_holding_period.bars: fixed literal only if used
ATR-stop multiplier: deferred metadata only; no active consumer
```

The first sweep can now have a genuine committed population greater than 1 by sweeping `entry_distance_threshold`.

Suggested future design material, not authorization: Side should propose a sensible sub-range at first-spec design, for example `0.005` to `0.05`, and a bounded grid.

## Remaining Deferrals

The following remain deferred and unauthorized here:

- `scale_by_one_plus_parameter`
- `offset_minus_parameter`
- `offset_plus_parameter`
- ATR-stop consumption
- `risk_model.stop_distance` consumer
- lookback parameter binding
- `both` direction
- `crosses_above` / `crosses_below`
- `in_set` / `is_true` / `is_false`
- `z_score` composition
- VWAP / RVOL / Donchian / RSI
- session / multi-timeframe support
- order-book / liquidation / CME features
- runner/backtester/lib modification
- paper/live/runtime/protected paths

## Next Decision For Main/Karl

Report-back questions:

1. Is the composition tranche checkpoint accepted?
2. May Side draft the revised first-spec design package?
3. Should the revised first-spec design use:
   - SMA lookback fixed at 20, or another fixed literal?
   - `entry_distance_threshold` range proposal around `0.005` to `0.05`?
   - `max_holding_period.bars` fixed at 96, or omit it?
4. Should ATR-stop remain excluded entirely from the first spec, or recorded only as deferred metadata?
5. Confirm no first-spec instances until after the next design report-back.
