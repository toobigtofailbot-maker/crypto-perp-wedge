# Online OHLCV Primitive Implementation 01

Package label: `WP-ONLINE-OHLCV-PRIMITIVE-IMPL-01`

## Authority boundary

This package implements additive offline research compiler primitives only. It does not create Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, probes, canonical trials, candidate registration, walk-forward/OOS, paper/live execution, runtime behavior, OMS/risk changes, broker/exchange connectivity, capital movement, or autonomous agent action.

The implementation is non-canonical infrastructure. It adds closed Strategy Spec grammar, validator checks, compiler recognition, and tests only.

## Implemented primitives

- `session_window`
- `opening_range`
- `opening_range_breakout`
- `opening_range_retest`
- `entry_controls.max_trades_per_session`
- `candle_shape.upper_wick_pct`
- `candle_shape.lower_wick_pct`
- `candle_shape.body_pct`

## Primitive-by-primitive grammar summary

`session_window` declares `session_id`, `timezone=UTC`, `anchor_time=HH:MM`, and `duration={value:1, units:day}`.

`opening_range` declares a `range_id`, `session_ref`, bar-count `start_offset`, bar-count `length`, fixed `high_source=high`, fixed `low_source=low`, `close_after_range_required=true`, and fail-closed zero/incomplete range policies.

`opening_range_breakout` declares a `breakout_id`, `range_ref`, close/bar-close confirmation, `entry_timing=next_bar_open`, fixed long/short threshold operator labels, ATR-multiple tolerance, false-before-range-complete policy, and simultaneous-side no-trade policy.

`opening_range_retest` declares a `retest_id`, `breakout_ref`, bounded min/max bar window, close-only touch source, next-open-after-confirmation timing, fixed OR high/low retest levels, ATR-multiple tolerance, timeout false policy, and opposite-breakout cancel policy.

`entry_controls.max_trades_per_session` declares `enabled=true`, `count_basis=entries_filled`, positive integer `max_trades`, `session_ref`, and `reset=session_start`.

`candle_shape` declares a `predicate_id`, `range_source=high_low`, fail-closed zero/missing policies, optional closed ratio predicates for upper wick, lower wick, and body, plus `side_mode` of `neutral` or `side_specific`.

Primitive conditions are consumed through closed `primitive_ref` operands and `is_true` / `is_false` operators. No expression strings or user code are accepted.

## Primitive-by-primitive causal semantics

`session_window` uses UTC-aware primary OHLCV timestamps only. Bars must align to the inferred primary bar grid inside the UTC daily session. Misaligned or irregular bars fail closed.

`opening_range` remains unavailable until all configured opening-range bars have closed. Missing range bars, zero range, nulls, and non-finite high/low values produce false/no-trade behavior.

`opening_range_breakout` evaluates only close-confirmed thresholds after the opening range is complete. Long requires `close > OR high + ATR tolerance`; short requires `close < OR low - ATR tolerance`.

`opening_range_retest` starts only after a confirmed breakout. It evaluates close-only retests inside the bounded window, expires deterministically, and cancels the session signal if the opposite breakout occurs first.

`max_trades_per_session` counts compiler entry signals as filled entries for this offline compiler surface, blocks additional entries after the cap, and resets at the declared UTC session boundary.

`candle_shape` computes ratios from the completed candle only. Range <= 0, missing OHLC, non-finite OHLC, doji side-specific impulse, and wrong candle direction all fail closed.

## Non-executability confirmation

The package adds no eval, lambda, expression string, formula-as-code, arbitrary Python hook, runtime hook, broker/exchange hook, paper/live hook, or user-provided code path.

Operators and units remain closed enums or const values. Unknown primitive refs, unknown primitive fields, invalid tolerance modes, invalid candle-shape operators, and unsupported keys fail validation or compiler construction.

Composition depth remains bounded by the existing Strategy Spec schema and validator at `max_condition_group_depth=3`.

## No-lookahead confirmation

All primitive outputs are derived from current or prior completed OHLCV bars. Opening range output is not emitted until the range bars are closed. Breakout and retest are close-confirmed. Candle-shape predicates use only the current completed candle. Session trade counters use past/current compiler entry events only.

## Existing-strategy regression result

Existing `STRAT-SPEC-0004`, `STRAT-SPEC-0005`, and `STRAT-SPEC-0006` continue to validate under the additive schema and validator.

The compiler change is additive for existing specs: prior operands, indicator builtins, composed operands, crossover behavior, ATR stop behavior, both-direction handling, and `min_bars_between_entries` behavior remain covered by existing and updated compiler tests.

Representative byte-for-byte result-population regression passed for the unchanged 0006 4h canonical path. A read-only dry-run over `STRAT-SPEC-0006` / `VM-0006` / `SWEEP-PLAN-0006` with the documented local 4h CSV produced `RP-6236`, denominator `8`, `8` successful rows, and a generated payload equal to committed `research/result_populations/RP-6236.result_population.json` under canonical JSON bytes. No result-population artifact was written.

## Tests/validation summary

Focused tests added or updated:

- Strategy Spec schema/validator tests for valid primitive declarations and closed-form rejections.
- Compiler tests for range completion, breakout confirmation, retest expiry/cancel, session max-trade reset, grid alignment, zero/missing range fail-closed behavior, candle-shape ratio/side handling, and a depth-three composed example.

Validation:

- `python -m pytest tests/test_validate_strategy_specs.py -q`: PASS
- `python -m pytest tests/test_spec_signal_compiler.py -q`: PASS
- `python -m pytest tests/test_validate_indicator_catalogs.py -q`: PASS
- `python -m pytest tests/test_offline_research_runner.py -q`: PASS
- `python -m pytest tests/test_research_query.py -q`: PASS on rerun with longer timeout
- `python -m tools.registry.validate_strategy_specs`: PASS
- `python -m tools.registry.validate_indicator_catalogs`: PASS
- `python -m tools.registry.validate_variant_sweep_artifacts`: PASS
- `python -m tools.registry.validate_result_populations`: PASS
- `python -m tools.registry.validate_candidate_registry`: PASS
- `python -m tools.registry.validate_paper_state`: PASS
- `python -m tools.research_query.run --list-views`: PASS
- `git diff --check`: PASS
- `git diff --cached --check`: PASS
- `python tools/dev/diff_scope_summary.py --check-forbidden`: FAIL because the generic forbidden-prefix helper flags the authorized package touch to `research/schemas/strategy_spec.schema.json`.
- `python tools/dev/diff_scope_summary.py --check-forbidden --authorized-package WP-ONLINE-OHLCV-PRIMITIVE-IMPL-01 --authorized-scope strategy-spec-schema --authorized-path research/schemas/strategy_spec.schema.json`: PASS
- `python tools/dev/verify.py --integrity-views ... --json`: FAIL only because it internally invokes the generic forbidden-scope check above; integrity rows shown before failure were clean.
- `python tools/dev/verify.py --full-pytest-sharded --pytest-shards 4 --pytest-shard-workers 4 --timeout-seconds 300 --full-pytest-timeout-seconds 1800 --max-output-chars 6000 --json`: FAIL only because it internally invokes the same generic forbidden-scope check. All pytest shards passed: `1296 passed`, `1 skipped`, warnings only.
- Read-only RP-6236 dry-run regression: PASS; generated payload equals committed `RP-6236` canonical JSON bytes.

## Deferred scope

Deferred:

- Strategy Specs for online ideas
- Variant Manifests
- Sweep Plans
- Result Populations
- canonical runs
- probes or trials
- candidate registration
- walk-forward/OOS
- paper/live/runtime/capital paths
- OMS/risk/reconciliation
- higher-timeframe deterministic trend-bias binding
- intrabar stop/target ordering
- simulator realism changes
- fixed-R targets
- session-end exits
- opening-range opposite-side stop
- 30m/1h canonical runner modes
- data materialization

## Next possible package

If Main later directs it, the next package can create a review-surface Strategy Spec using these primitives, or can design the deferred higher-timeframe binding. This package itself creates no strategy artifact and provides no trial authority.
