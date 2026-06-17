# WP-ONLINE-OHLCV-VARIANT-BINDING-01

## Package class

Bundled additive research-compiler / schema / validator infrastructure.

## Branch / worktree / base

- Branch: `impl/online-ohlcv-variant-binding-01`
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-ONLINE-OHLCV-VARIANT-BINDING-01`
- Base: `origin/main` at `ad607fd`

## Changed files

- `research/schemas/strategy_spec.schema.json`
- `tools/research_runner/spec_signal_compiler.py`
- `tools/registry/validate_strategy_specs.py`
- `tools/registry/validate_variant_sweep_artifacts.py`
- `tests/test_spec_signal_compiler.py`
- `tests/test_validate_strategy_specs.py`
- `tests/test_validate_variant_sweep_artifacts.py`
- `docs/research_pipeline/2026-06-online_ohlcv_variant_binding_01.md`
- `docs/status_entries/WP-ONLINE-OHLCV-VARIANT-BINDING-01.md`

## Binding result

Bindable fields:

- candle shape upper/lower wick and body percentage values
- opening-range breakout ATR tolerance multiple
- opening-range retest min/max window bars and ATR tolerance multiple
- max trades per session
- ATR stop multiplier
- fixed-R target multiple

Unsupported/deferred fields:

- `time_exit.session_end`, no numeric field in merged grammar
- `opening_range_opposite_side`, no numeric tolerance/offset field in merged grammar
- opening-range start/length and min-bars-between-entries controls
- all strategy/evidence/runtime/protected-path surfaces

## Boundary summary

This package changes offline research schema, validator, compiler, tests, and docs only. It creates no Strategy Spec, Variant Manifest, Sweep Plan, Result Population, probe, canonical trial, candidate row, walk-forward/OOS artifact, runtime behavior, paper/live path, OMS/risk/reconciliation path, broker/exchange path, capital path, or trading authority.

## Non-executability confirmation

No eval, lambda, expression string, formula-as-code, arbitrary Python hook, user-provided code path, runtime hook, broker/exchange hook, paper/live hook, or protected-path hook was added.

`{"parameter_ref": "name"}` is the only new value-reference form. It resolves only from the variant assignment parameter map and is validated against declared free-parameter enumeration plus target-field literal constraints.

The Variant Manifest / Sweep validator requires each value-bound parent Strategy Spec parameter to be present as a VM parameter axis before sweep planning.

## Existing-strategy regression result

Existing lookback binding remains unchanged. Existing literal primitive thresholds remain valid. Committed Strategy Specs `0004`, `0005`, and `0006` validate unchanged under the additive schema and validator.

`RP-6236` byte-for-byte regression passed. A dry-run over `STRAT-SPEC-0006` / `VM-0006` / `SWEEP-PLAN-0006` with the documented local 4h CSV reproduced `RP-6236`, denominator `8`, `8` successful rows, `wrote=false`, and generated canonical JSON bytes equal to committed `research/result_populations/RP-6236.result_population.json`.

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
- `python -m pytest tests/test_spec_signal_compiler.py -q`: PASS, `195 passed`
- `python -m pytest tests/test_validate_strategy_specs.py -q`: PASS, `102 passed`
- `python -m pytest tests/test_validate_variant_sweep_artifacts.py -q`: PASS, `42 passed`
- Combined focused suite for the three changed test files after VM cross-check addition: PASS, `339 passed`
- `python -m pytest tests/test_offline_research_runner.py -q`: PASS, `94 passed`, warnings only
- `python -m pytest tests/test_research_query.py -q`: command exceeded local timeout at 180s and 420s with no pytest failure output; substituted chunked execution by query group.
- Chunked `tests/test_research_query.py`: PASS, all `64` collected tests passed across chunks.
- `python tools/dev/diff_scope_summary.py --check-forbidden --authorized-package WP-ONLINE-OHLCV-VARIANT-BINDING-01 --authorized-scope strategy-spec-schema --authorized-path research/schemas/strategy_spec.schema.json`: PASS
- Brief-specified multi-scope `diff_scope_summary.py` form: FAIL under current helper syntax because only one `--authorized-scope` is accepted per invocation; it applied `strategy-spec-prereg` to `research/schemas/strategy_spec.schema.json`.
- `python tools/dev/verify.py --integrity-views --integrity-max-workers 4 --timeout-seconds 300 --max-output-chars 6000 --json`: FAIL only because its internal generic `diff_scope_summary.py --check-forbidden` flags the package-authorized schema path; all integrity views shown were clean.
- `python tools/dev/verify.py --full-pytest-sharded --pytest-shards 4 --pytest-shard-workers 4 --timeout-seconds 300 --full-pytest-timeout-seconds 1800 --max-output-chars 6000 --json`: FAIL only because its internal generic `diff_scope_summary.py --check-forbidden` flags the package-authorized schema path; all pytest shards passed: `1329 passed`, `1 skipped`, warnings only.
- `RP-6236` dry-run CLI summary: PASS, `ok=true`, `dry_run=true`, `wrote=false`, denominator `8`, successful `8`.
- `RP-6236` API byte comparison with `max_workers=1`: PASS, generated canonical bytes equal committed canonical bytes.

The required plain verify wrappers are not claimed as passing; their observed failure is the known generic diff-scope false positive on this package-authorized schema edit.

## Deferred scope

No Strategy Spec, Variant Manifest, Sweep Plan, Result Population, probe, canonical run, trial, candidate row, walk-forward/OOS, paper/live/runtime/capital path, OMS/risk/reconciliation path, broker/exchange path, data materialization, higher-timeframe binding, intrabar semantics, runner mode, or strategy surface was created.
