# Indicator Catalog Schema

## 1. Scope And Non-Authority

WP-12hq / WP-S2c-197 creates the first Indicator Catalog JSON Schema at `research/schemas/indicator_catalog.schema.json`.

This package creates no indicator catalog instance, validator, compiler, Strategy Spec instance, variant manifest, sweep plan, result population, canonical sweep, runner change, backtester change, evaluation change, runtime change, paper/live change, protected-path change, approval, readiness, recommendation, ranking, transition, gate, order, broker, exchange, or human-gate execution authority.

## 2. Purpose

The schema defines a closed, non-executable catalog interface for the first Strategy Spec computation-binding slice. Future catalog artifacts can declare which indicator interfaces exist, what inputs and parameters they accept, what output field they expose, and what warmup/null posture applies.

The catalog does not define computation. It only declares reviewed interfaces that a future compiler may dispatch to through a closed built-in set after that compiler is separately reviewed and implemented.

## 3. Option A Architecture

The schema follows Main's approved Option A:

- catalog declares interface only;
- compiler owns reviewed implementations;
- compiler dispatches only on known built-ins;
- catalog data cannot encode computation, formulas, scripts, callbacks, runtime actions, or arbitrary expressions.

Every entry requires `implementation_binding.binding_type = "compiler_builtin_closed_set"`, `implementation_owner = "spec_signal_compiler"`, `computation_defined_in_catalog = false`, and `arbitrary_expression_allowed = false`.

## 4. First Closed Set

The schema requires exactly four future catalog entries:

- SMA as `indicator_id = "sma"` with `builtin_key = "sma_v1"`;
- EMA as `indicator_id = "ema"` with `builtin_key = "ema_v1"`;
- ATR as `indicator_id = "atr"` with `builtin_key = "atr_v1"`;
- StdDev as `indicator_id = "stddev"` with `builtin_key = "stddev_v1"`.

No additional catalog entries are valid in the v1 schema.

## 5. Reinforcement Checks

Reinforcement 1: the schema enforces 1:1 `indicator_id` to `builtin_key` pairing through Draft-07 `oneOf` branches. Independent enum selection is not sufficient and is not used as the only control.

Reinforcement 2: the schema rejects forbidden executable and authority key names on every schema-defined object with `propertyNames`, and all schema-defined object shapes are closed with `additionalProperties: false`. WP-S2c-198 must still add a validator that recursively walks future catalog payloads and hard-fails forbidden keys anywhere as the second enforcement layer.

Reinforcement 3: EMA and ATR convention keys are closed enum declarations, not free strings. EMA closes `smoothing_convention` to `standard_ema_alpha_2_over_n_plus_1` and `initialization_convention` to `sma_seed_after_full_lookback`. ATR closes `true_range_convention` to `wilder_true_range` and `smoothing_convention` to `wilder_rma`. StdDev closes `ddof` to `[0, 1]`.

## 6. Contracts

SMA, EMA, and StdDev use one OHLCV numeric source input with allowed fields `open`, `high`, `low`, `close`, and `volume`, defaulting to `close`.

ATR uses fixed OHLCV inputs `high`, `low`, and `close`.

All four indicators expose only `field = "value"`, `type = "numeric_series"`, and `index_alignment = "primary_ohlcv_index"`.

All four indicators require `no_lookahead = true`, `warmup_output = "null_until_ready"`, and `signal_generation_policy = "null_operand_never_true"`.

## 7. Deferred Packages

WP-S2c-198 is expected to add the first catalog entries plus the validator that recursively enforces forbidden keys, filename/ID consistency, and catalog-specific integrity checks.

WP-S2c-199 is expected to add a build-and-test-only Strategy Spec to signal compiler. That future compiler remains separate from this schema and must not be inferred from it.
