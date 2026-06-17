# WP-ONLINE-OHLCV-PRIMITIVE-IMPL-01

## Package class

Bundled additive research-compiler primitive implementation.

## Branch / worktree / base

- Branch: `impl/online-ohlcv-primitive-impl-01`
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-ONLINE-OHLCV-PRIMITIVE-IMPL-01`
- Base: `origin/main` at `642105a`

## Changed files

- `research/schemas/strategy_spec.schema.json`
- `tools/registry/validate_strategy_specs.py`
- `tools/research_runner/spec_signal_compiler.py`
- `tests/test_spec_signal_compiler.py`
- `tests/test_validate_strategy_specs.py`
- `docs/research_pipeline/2026-06-online_ohlcv_primitive_impl_01.md`
- `docs/status_entries/WP-ONLINE-OHLCV-PRIMITIVE-IMPL-01.md`

## Implemented primitives

- `session_window`: implemented.
- `opening_range`: implemented.
- `opening_range_breakout`: implemented.
- `opening_range_retest`: implemented.
- `entry_controls.max_trades_per_session`: implemented.
- `candle_shape.upper_wick_pct`: implemented.
- `candle_shape.lower_wick_pct`: implemented.
- `candle_shape.body_pct`: implemented.

## Primitive-by-primitive status

`session_window` supports UTC daily sessions with HH:MM anchors and grid-aligned primary bars.

`opening_range` supports bar-offset and bar-length ranges over session-local high/low with fail-closed zero and incomplete range behavior.

`opening_range_breakout` supports close-confirmed long and short breakout thresholds over opening-range boundaries with ATR-multiple tolerance.

`opening_range_retest` supports close-only bounded retest windows, deterministic timeout, and opposite-breakout cancellation.

`max_trades_per_session` supports positive integer session caps over declared sessions and composes with `min_bars_between_entries`.

`candle_shape` supports upper wick, lower wick, and body fraction predicates, including side-specific impulse behavior.

## Non-executability confirmation

No eval, lambda, expression strings, formula-as-code, arbitrary Python hooks, user-provided code, runtime hooks, broker/exchange hooks, paper/live hooks, or protected-path hooks were added.

Primitive declarations are closed JSON schema forms. Unknown refs, invalid fields, invalid operators, invalid units, invalid tolerance modes, executable-looking keys, and malformed controls fail validation or compiler construction.

## No-lookahead confirmation

The compiler uses completed OHLCV bars only. Opening ranges emit only after range completion. Breakouts and retests are close-confirmed. Candle-shape ratios use only the current completed candle. Session counters use prior/current entry events and reset only on session boundaries.

## Existing-strategy regression result

Committed Strategy Specs `0004`, `0005`, and `0006` validate unchanged under the additive schema and validator.

Existing compiler behavior for SMA, EMA, ATR, stddev, composed operands, z-score operands, crossover operators, ATR stops, both-direction state, max holding period, and `min_bars_between_entries` remains covered by the compiler regression suite.

Representative byte-for-byte RP regression passed for the unchanged 0006 4h canonical path. A read-only dry-run generated `RP-6236` with denominator `8`, `8` successful rows, and canonical JSON bytes equal to committed `research/result_populations/RP-6236.result_population.json`. No result-population artifact was written.

## Validation summary

Validation:

- `python -m pytest tests/test_spec_signal_compiler.py -q`: PASS
- `python -m pytest tests/test_validate_strategy_specs.py -q`: PASS
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
- `python tools/dev/diff_scope_summary.py --check-forbidden`: FAIL because the generic forbidden-prefix helper flags the package-authorized schema path `research/schemas/strategy_spec.schema.json`.
- `python tools/dev/diff_scope_summary.py --check-forbidden --authorized-package WP-ONLINE-OHLCV-PRIMITIVE-IMPL-01 --authorized-scope strategy-spec-schema --authorized-path research/schemas/strategy_spec.schema.json`: PASS
- `python tools/dev/verify.py --integrity-views ... --json`: FAIL only because it internally invokes the generic forbidden-scope check above; integrity rows shown before failure were clean.
- `python tools/dev/verify.py --full-pytest-sharded --pytest-shards 4 --pytest-shard-workers 4 --timeout-seconds 300 --full-pytest-timeout-seconds 1800 --max-output-chars 6000 --json`: FAIL only because it internally invokes the same generic forbidden-scope check. All pytest shards passed: `1296 passed`, `1 skipped`, warnings only.
- Read-only RP-6236 dry-run regression: PASS; generated payload equals committed `RP-6236` canonical JSON bytes.

The required plain verify wrappers are not claimed as passing; their observed failure is the known generic diff-scope false positive on this package-authorized schema edit.

## Deferred scope

No Strategy Spec, Variant Manifest, Sweep Plan, Result Population, probe, canonical run, trial, candidate row, walk-forward/OOS, paper/live/runtime/capital path, OMS/risk/reconciliation path, broker/exchange path, data materialization, fixed-R target, session-end exit, opening-range opposite-side stop, intrabar ordering, 30m/1h canonical mode, or higher-timeframe binding was created.

## Boundary summary

This package changes offline research schema, validator, compiler, tests, and docs only. It creates no evidence artifact and no runtime authority.

## Stop/split notes

No primitive was split or stopped during implementation. The active package explicitly authorized bundling the session/ORB and candle-shape primitives even though the prior design doc recommended a narrower implementation split.
