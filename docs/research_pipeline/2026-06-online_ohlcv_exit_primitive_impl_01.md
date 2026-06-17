# Online OHLCV Exit Primitive Implementation 01

Package label: `WP-ONLINE-OHLCV-EXIT-PRIMITIVE-IMPL-01`

## Authority boundary

This package implements additive offline research compiler exit primitives only. It does not create Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, probes, canonical trials, candidate registration, walk-forward/OOS, paper/live execution, runtime behavior, OMS/risk changes, broker/exchange connectivity, capital movement, or autonomous agent action.

The implementation is non-canonical infrastructure. It adds closed Strategy Spec grammar, validator checks, compiler recognition, and tests only.

## Implemented exit primitives

- `time_exit.session_end`
- `fixed_R_target`
- `opening_range_opposite_side`

## Primitive-by-primitive grammar summary

`time_exit.session_end` declares `enabled=true`, a declared `session_ref`, `exit_signal_timing=last_bar_close_before_session_end`, `fill_timing=next_bar_open`, and `partial_session_policy=no_exit`.

`opening_range_opposite_side` declares `enabled=true`, a declared `range_ref`, `entry_reference_price=next_bar_open_pre_fee_slippage`, `evaluation_price=close`, `evaluation_timing=bar_close`, fixed long/short stop levels of `opening_range.low` and `opening_range.high`, and `same_bar_entry_stop_policy=not_evaluated_until_after_entry_bar`.

`fixed_R_target` declares `enabled=true`, positive finite `r_multiple`, `entry_reference_price=next_bar_open_pre_fee_slippage`, `stop_ref=opening_range_opposite_side`, `evaluation_price=close`, `evaluation_timing=bar_close`, and `same_bar_stop_target_policy=defer_intrabar_realism`.

## Primitive-by-primitive causal semantics

`time_exit.session_end` exits only on the deterministic final bar close of a declared UTC daily session. It uses the inferred primary bar grid and fails closed for incomplete sessions where the terminal bar is absent.

`opening_range_opposite_side` captures the opening-range levels known at the entry signal bar, captures the entry reference price from the next bar open, and exits long positions only when a later close is `<= opening_range.low` or short positions only when a later close is `>= opening_range.high`.

`fixed_R_target` uses the same captured entry reference and opposite-side stop level to derive R. Long targets require `entry_reference_price - opening_range.low > 0`; short targets require `opening_range.high - entry_reference_price > 0`. If the R base is missing, non-finite, or non-positive, the target fails closed. Target exits trigger only on close-confirmed R reach.

## Non-executability confirmation

The package adds no eval, lambda, expression string, formula-as-code, arbitrary Python hook, runtime hook, broker/exchange hook, paper/live hook, or user-provided code path.

Operators, timing labels, reference labels, units, and policies remain closed constants. Unknown exit keys, invalid refs, invalid timings, non-finite R multiples, executable-looking keys, and malformed controls fail validation or compiler construction.

Composition depth remains bounded by the existing Strategy Spec schema and validator at `max_condition_group_depth=3`.

## No-lookahead confirmation

All exit decisions use completed bars only. Session-end detection uses the deterministic declared UTC session schedule and current timestamp. Opening-range opposite-side and fixed-R target exits use opening-range levels available at the entry signal bar, the next-open entry reference, and current/later close prices only. No future bar is used to decide the current bar.

## Realism note

Close-only target exits are conservative and safe for the current OHLCV research compiler surface.

Close-only stops retain the known intrabar-touch limitation: an intrabar breach that recovers by close will not exit. This limitation must resurface before walk-forward, paper, or live work.

Intrabar stop/target ordering remains deferred. The implementation does not infer same-bar target/stop order from OHLCV bars and blocks same-bar re-entry after close-only exit triggers in single-direction mode.

## Regression result

Existing `STRAT-SPEC-0004`, `STRAT-SPEC-0005`, and `STRAT-SPEC-0006` validate under the additive schema and validator. Existing compiler behavior for ATR stops, entry primitives, both-direction state, max holding period, and entry controls remains covered by focused regression tests.

Representative byte-for-byte result-population regression passed for the unchanged 0006 4h canonical path. A read-only dry-run over `STRAT-SPEC-0006` / `VM-0006` / `SWEEP-PLAN-0006` with the documented local 4h CSV reproduced `RP-6236`, denominator `8`, `8` successful rows, and canonical JSON bytes equal to committed `research/result_populations/RP-6236.result_population.json`. No result-population artifact was written.

## Validation summary

Validation:

- `git diff --check`: PASS
- `git diff --cached --check`: PASS
- `python -m tools.registry.validate_strategy_specs`: PASS
- `python -m tools.registry.validate_variant_sweep_artifacts`: PASS
- `python -m tools.registry.validate_indicator_catalogs`: PASS
- `python -m tools.registry.validate_result_populations`: PASS
- `python -m tools.registry.validate_candidate_registry`: PASS
- `python -m tools.registry.validate_paper_state`: PASS
- `python -m tools.research_query.run --list-views`: PASS
- `python -m pytest tests/test_spec_signal_compiler.py -q`: PASS, `186 passed`
- `python -m pytest tests/test_validate_strategy_specs.py -q`: PASS, `100 passed`
- `python -m pytest tests/test_offline_research_runner.py -q`: PASS, `94 passed`, warnings only
- `python -m pytest tests/test_research_query.py -q`: PASS on longer rerun, `64 passed`
- `python tools/dev/diff_scope_summary.py --check-forbidden --authorized-package WP-ONLINE-OHLCV-EXIT-PRIMITIVE-IMPL-01 --authorized-scope strategy-spec-schema --authorized-path research/schemas/strategy_spec.schema.json`: PASS
- `python tools/dev/verify.py --integrity-views ... --json`: FAIL only because its internal generic `diff_scope_summary.py --check-forbidden` flags the package-authorized schema path `research/schemas/strategy_spec.schema.json`; all integrity views shown were clean.
- `python tools/dev/verify.py --full-pytest-sharded ... --json`: FAIL only because its internal generic `diff_scope_summary.py --check-forbidden` flags the package-authorized schema path; all pytest shards passed: `1309 passed`, `1 skipped`, warnings only.
- Read-only `RP-6236` dry-run byte regression: PASS; generated canonical JSON bytes equal committed `RP-6236`, denominator `8`, `8` successful rows, wrote `false`.

The required plain verify wrappers are not claimed as passing; their observed failure is the known generic diff-scope false positive on this package-authorized schema edit.

## Deferred scope

Deferred:

- Strategy Specs
- Variant Manifests
- Sweep Plans
- Result Populations
- canonical runs
- probes or trials
- candidate registration
- walk-forward/OOS
- paper/live/runtime/capital paths
- OMS/risk/reconciliation
- broker/exchange connectivity
- higher-timeframe trend-bias binding
- intrabar stop/target ordering
- high/low touch stops or targets
- same-bar entry/exit resolution changes
- 30m/1h canonical runner modes
- data materialization
