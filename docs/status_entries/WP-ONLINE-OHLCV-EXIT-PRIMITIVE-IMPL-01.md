# WP-ONLINE-OHLCV-EXIT-PRIMITIVE-IMPL-01

## Package class

Bundled additive research-compiler exit primitive implementation.

## Branch / worktree / base

- Branch: `impl/online-ohlcv-exit-primitive-impl-01`
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-ONLINE-OHLCV-EXIT-PRIMITIVE-IMPL-01`
- Base: `origin/main` at `e613545`

## Changed files

- `research/schemas/strategy_spec.schema.json`
- `tools/registry/validate_strategy_specs.py`
- `tools/research_runner/spec_signal_compiler.py`
- `tests/test_spec_signal_compiler.py`
- `tests/test_validate_strategy_specs.py`
- `docs/research_pipeline/2026-06-online_ohlcv_exit_primitive_impl_01.md`
- `docs/status_entries/WP-ONLINE-OHLCV-EXIT-PRIMITIVE-IMPL-01.md`

## Implemented primitives

- `time_exit.session_end`: implemented.
- `fixed_R_target`: implemented.
- `opening_range_opposite_side`: implemented.

## Boundary summary

This package changes offline research schema, validator, compiler, tests, and docs only. It creates no Strategy Spec, Variant Manifest, Sweep Plan, Result Population, trial, candidate, walk-forward/OOS artifact, runtime behavior, paper/live path, OMS/risk/reconciliation path, broker/exchange path, capital path, or trading authority.

## Non-executability confirmation

No eval, lambda, expression strings, formula-as-code, arbitrary Python hooks, user-provided code, runtime hooks, broker/exchange hooks, paper/live hooks, or protected-path hooks were added.

Exit declarations are closed JSON schema forms. Unknown refs, invalid fields, invalid timings, invalid policies, non-finite R multiples, executable-looking keys, and malformed controls fail validation or compiler construction.

## Close-only confirmation

`time_exit.session_end` exits only on the deterministic final bar close of a declared UTC daily session.

`opening_range_opposite_side` exits only on close-confirmed opposite-side OR breach.

`fixed_R_target` exits only on close-confirmed R-target reach, using the known entry reference and configured opposite-side stop distance.

The implementation does not add high/low touch semantics, intrabar ordering, or same-bar stop/target inference.

## Existing-strategy regression result

Committed Strategy Specs `0004`, `0005`, and `0006` validate under the additive schema and validator.

Representative byte-for-byte `RP-6236` regression passed for the unchanged 0006 4h canonical path. A read-only dry-run generated `RP-6236` with denominator `8`, `8` successful rows, and canonical JSON bytes equal to committed `research/result_populations/RP-6236.result_population.json`. No result-population artifact was written.

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

No Strategy Spec, Variant Manifest, Sweep Plan, Result Population, probe, canonical run, trial, candidate row, walk-forward/OOS, paper/live/runtime/capital path, OMS/risk/reconciliation path, broker/exchange path, data materialization, higher-timeframe binding, intrabar ordering, high/low touch exit, or 30m/1h canonical mode was created.
