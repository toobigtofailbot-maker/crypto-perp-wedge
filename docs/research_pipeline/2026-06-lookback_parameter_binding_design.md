# Lookback Parameter Binding Design

## Status / Authority

This is a design document only.

It does not implement schema changes. It does not implement validator changes. It does not implement compiler changes. It does not mutate Strategy Specs, variant manifests, sweep plans, result populations, or indicator catalogs. It creates no runner, backtester, lib, data, query-layer, runtime, paper/live, OMS, reconciliation, risk, safe-mode, kill-switch, broker, exchange, order, ranking, recommendation, readiness, transition, promotion, approval, or human-gate execution authority.

R1 is a mandatory closed-form review point before any R2 schema/validator or R3 compiler implementation package.

## Repo-Truth Discovery

Facts from refreshed `main`:

- `docs/research_pipeline/2026-06-compiler_extension_tranche_plan.md` records lookback parameter binding as the first recommended compiler-extension dependency and states that current indicator lookback must be a literal `operand.lookback.bars`; parameter-bound lookbacks fail closed.
- `research/schemas/strategy_spec.schema.json` currently defines `lookback` as an object with exactly `bars`, where `bars` is an integer or null and any integer must be `>= 1`.
- `tools/registry/validate_strategy_specs.py` adds semantic validation for Strategy Specs but has no current semantic path for parameter-bound lookbacks.
- `tools/research_runner/spec_signal_compiler.py` resolves indicator refs only when `operand.lookback` is a mapping and `operand.lookback.bars` is an integer. Non-literal lookbacks raise `UnsupportedSpecSignalCompilerFeature`.
- `tests/test_spec_signal_compiler.py` currently covers literal SMA/EMA/ATR/StdDev lookbacks, null/warmup behavior, determinism, no-lookahead, unsupported operators, forbidden keys, and no-write behavior. It does not cover parameterized indicator lookbacks.
- `research/strategy_specs/STRAT-SPEC-0001.strategy_spec.json` uses literal `{"bars": 20}` for SMA lookbacks and sweeps only `entry_distance_threshold`.
- The prior closed-composition tranche introduced `composed_operand` only for `scale_by_one_minus_parameter`; it explicitly deferred lookback parameter binding.

Inference:

- Lookback binding can be designed as closed parameter substitution inside the existing indicator lookback surface.
- Runner and backtester changes are not required if the compiler still returns a precomputed signal series to existing downstream consumers.
- If implementation later requires runner, backtester, lib, runtime, or protected-path changes, that is a stop condition rather than a reason to broaden scope.

## Current Limitation

Current repo truth is:

```text
indicator lookbacks are literal only;
lookback parameter binding is fail-closed / unsupported;
this constrained earlier first-canonical-spec work before the closed composed_operand extension.
```

The current canonical SMA-distance spec can vary `entry_distance_threshold`, but its SMA lookback is fixed at literal `20`. That keeps first population expressiveness narrow and prevents bounded sweeps over SMA/EMA/ATR/StdDev lookback windows.

## Proposed Closed Grammar

Recommended representation:

```json
{
  "lookback": {
    "bars_parameter_ref": "lookback_n"
  }
}
```

This should be added as an alternative closed lookback shape, not as a string expression and not as an overloaded `bars` value.

The future schema shape should allow exactly one of:

```json
{ "bars": 20 }
```

or:

```json
{ "bars_parameter_ref": "lookback_n" }
```

Allowed locations:

- `indicator_ref.lookback` only;
- base `indicator_ref.lookback` inside the existing approved `composed_operand.base_operand`;
- no `data_ref`, `parameter_ref`, `constant`, or `composed_operand` top-level lookback binding;
- no `max_holding_period.bars` binding in this extension.

Closed grammar requirements:

- `additionalProperties: false`;
- parameter reference must be a non-empty string matching one declared free parameter name exactly;
- no nested objects beyond the one closed lookback object;
- no arithmetic;
- no expression language;
- no formula strings;
- no composed lookback;
- no multi-parameter lookback;
- no dynamic strings or path-like references;
- no catalog-interpreted computation.

Rejected forms:

```json
{ "bars": { "parameter_ref": "lookback_n" } }
```

```json
{ "parameter_ref": "lookback_n", "scale": 2 }
```

```json
{ "expression": "lookback_n * 2" }
```

```json
{ "bars_parameter_ref": ["fast_n", "slow_n"] }
```

## Parameter Declaration Constraints

Lookback-bound parameters should use existing `free_parameters.parameters[]` declarations with extra semantic constraints enforced by the validator.

Required constraints:

```text
type: integer
is_free_parameter: true
included_in_variant_generation: true
range: bounded object
range.min: integer >= 1
range.max: integer and finite
range.step: integer >= 1
allowed_values: if present, all integer, non-bool, >= 1, within range
default: integer, non-bool, >= 1, within range or allowed_values
```

Recommended initial upper bound:

```text
range.max <= 500
```

Reasoning: 500 bars is broad enough for 15m through daily research families while keeping warmup, population design, and accidental unbounded computation under control. Main/Karl may choose a narrower package-specific maximum for the first implementation, but unbounded lookback ranges should remain invalid.

No float lookbacks, negative lookbacks, zero lookbacks, bool lookbacks, null lookbacks for bound parameters, unbounded ranges, open-ended grids, or non-integer grid values should be accepted.

## Validator Behavior

R2 should preserve literal lookbacks unchanged and add semantic checks for approved parameter-bound lookbacks.

Validator should accept:

- existing literal `{"bars": integer >= 1}` lookbacks;
- approved `{"bars_parameter_ref": "name"}` only at indicator-ref lookback locations;
- bound parameter declarations that are integer, bounded, finite, included in variant generation, and free-parameter counted.

Validator should reject:

- unknown parameter refs;
- duplicate parameter declarations for a referenced name;
- non-integer bound parameters;
- bool values masquerading as integers;
- missing, null, zero, negative, float, or string lookback values;
- unbounded or invalid ranges;
- allowed values outside the declared integer range;
- step values that are null, non-integer, <= 0, or bool;
- parameter binding outside approved indicator contexts;
- expression-like fields such as `expression`, `formula`, `code`, `eval`, `function`, `lambda`, `lookahead`, `forward_fill`, `backfill`, `interpolation`, or `future_value`;
- nested or compound lookback specs;
- mixed literal and bound lookback in one object, for example `{"bars": 20, "bars_parameter_ref": "lookback_n"}`.

The validator should keep the existing recursive forbidden-key posture.

## Compiler Behavior

R3 should resolve parameter-bound lookbacks per variant assignment before calling existing approved indicator builtins.

Required compiler behavior:

1. Resolve `indicator_ref.lookback`.
2. If lookback is literal `bars`, preserve current behavior.
3. If lookback is `bars_parameter_ref`, resolve the referenced parameter from `variant_assignment.parameter_values`.
4. Validate the resolved value is an integer, non-bool, finite, and `>= 1`.
5. Use the resolved integer as `lookback_bars`.
6. Call existing compiler-owned builtins: SMA, EMA, ATR, or StdDev.
7. Preserve current cache semantics, including indicator id, resolved lookback integer, and builtin key.
8. Preserve warmup/null behavior.
9. Preserve no-lookahead behavior.
10. Preserve deterministic output for identical inputs and assignments.
11. Fail closed on missing assignment, invalid assignment, unknown indicator, unsupported timeframe, unsupported output field, or unsupported lookback shape.

No catalog data should define computation. The catalog remains interface-only and the compiler remains the reviewed computation owner.

## Tests Needed For R2 / R3

R2 schema/validator tests:

- schema accepts literal lookback unchanged;
- schema accepts `{"bars_parameter_ref": "lookback_n"}` in `indicator_ref.lookback`;
- schema rejects mixed `bars` plus `bars_parameter_ref`;
- schema rejects expression-like, nested, compound, array, and multi-parameter lookbacks;
- validator rejects unknown parameter refs;
- validator rejects duplicate parameter declaration refs;
- validator rejects non-integer, float, bool, null, zero, negative, and unbounded lookback-bound parameters;
- validator rejects invalid range min/max/step and invalid allowed_values;
- validator rejects parameter binding outside approved `indicator_ref` contexts;
- existing Strategy Specs remain valid unchanged.

R3 compiler tests:

- parameterized SMA lookback resolves from variant assignment;
- parameterized EMA lookback resolves from variant assignment;
- parameterized ATR lookback resolves from variant assignment;
- parameterized StdDev lookback resolves from variant assignment, including the existing StdDev minimum requirement;
- missing parameter assignment fails closed;
- float, bool, string, null, zero, and negative assignment values fail closed;
- repeated compilation with identical assignments is deterministic;
- different assignments produce expected distinct warmup and indicator values;
- warmup/null behavior is preserved without fill;
- future OHLCV mutation does not change prior signal decisions;
- unsupported lookback binding contexts fail closed;
- no files are written during compilation.

## Strategy Utility

This unlocks bounded sweeps over:

- SMA lookbacks;
- EMA lookbacks;
- ATR lookbacks;
- StdDev lookbacks;
- threshold-plus-lookback populations;
- future z-score families that need center and scale lookback variation;
- broader mean-reversion, breakout, and trend-following families while remaining inside the current OHLCV compiler path.

The capability improves Strategy Spec population expressiveness without requiring arbitrary arithmetic, multi-timeframe alignment, stop-order simulation, or runtime integration.

## Boundary Rules

This design is:

```text
closed parameter substitution only
```

It is not:

- an expression language;
- arbitrary arithmetic;
- catalog-interpreted computation;
- dynamic eval;
- dynamic dispatch from catalog text;
- notes-as-computation;
- runtime authority;
- paper/live authority;
- promotion, ranking, readiness, recommendation, or transition authority.

Strategy Specs remain declarative and non-executing. Compiler support, if later authorized, remains build-and-test-only until a separate package scopes any canonical artifact or runner use.

## Recommended R2 / R3 Path

Recommendation: split R2 and R3.

R2 should implement only schema/validator/test support for the closed lookback grammar. It should not touch compiler code or Strategy Spec instances.

R3 should implement compiler/test support after R2 merges and after Main/Karl accepts this R1 design. It should not mutate Strategy Specs, variant manifests, sweep plans, result populations, query surfaces, runner/backtester/lib code, or protected paths.

Combined R2/R3 is not recommended. The grammar and parameter-declaration constraints are narrow but boundary-critical enough to deserve a separate schema/validator review before compiler behavior changes.

Decision request:

```text
Accept or revise the closed lookback representation.
Confirm allowed contexts: indicator_ref lookbacks only, including indicator_ref inside composed_operand.base_operand.
Confirm integer parameter constraints and bounded range posture.
Authorize or revise the split R2 schema/validator then R3 compiler path.
```
