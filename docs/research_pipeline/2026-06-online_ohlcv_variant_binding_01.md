# Online OHLCV Variant Binding 01

Package label: `WP-ONLINE-OHLCV-VARIANT-BINDING-01`

## Authority boundary

This package implements additive closed variant binding for offline research primitives only. It does not create Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, probes, canonical trials, candidate registration, walk-forward/OOS, paper/live execution, runtime behavior, OMS/risk changes, broker/exchange connectivity, capital movement, or autonomous agent action.

The implementation is schema, validator, compiler, test, and documentation infrastructure only. It grants no execution authority and no evidence authority.

## Systemic blocker

The merged online OHLCV primitive grammar could express literal numeric thresholds, but could not bind those thresholds to closed Variant Manifest parameter grids. That blocked honest denominator and sensitivity evidence for future ORB and no-wick style surfaces because characteristic primitive thresholds would have been fixed literals rather than enumerated axes.

## Implemented binding fields

The closed `{"parameter_ref": "parameter_name"}` form is now accepted for:

- `online_ohlcv_primitives.candle_shapes[].upper_wick_pct.value`
- `online_ohlcv_primitives.candle_shapes[].lower_wick_pct.value`
- `online_ohlcv_primitives.candle_shapes[].body_pct.value`
- `online_ohlcv_primitives.opening_range_breakouts[].tolerance.multiple`
- `online_ohlcv_primitives.opening_range_retests[].window.min_bars_after_breakout`
- `online_ohlcv_primitives.opening_range_retests[].window.max_bars_after_breakout`
- `online_ohlcv_primitives.opening_range_retests[].tolerance.multiple`
- `entry_logic.entry_controls.max_trades_per_session.max_trades`
- `exit_logic.atr_stop.atr_multiplier`
- `exit_logic.fixed_R_target.r_multiple`

## Unsupported and deferred fields

The package does not add binding for:

- `time_exit.session_end`, because the merged primitive has no safe numeric threshold field.
- `opening_range_opposite_side`, because the merged primitive has no numeric tolerance or offset field.
- `opening_range.start_offset` or `opening_range.length`.
- `entry_logic.entry_controls.min_bars_between_entries`.
- Any higher-timeframe trend-bias, midpoint-pullback, EMA-retest, intrabar, data, runner-mode, runtime, paper/live, OMS/risk, or broker/exchange field.

## Closed VM enumeration rule

Bound values must resolve from `variant_assignment.parameter_values` using a declared Strategy Spec free parameter. The Strategy Spec validator requires the bound parameter to be declared, included in variant generation, free, type-compatible, and backed by non-empty enumerated `allowed_values`.

The Variant Manifest / Sweep validator also requires each parent Strategy Spec `parameter_ref` used by the value-binding grammar to be present as a VM `parameter_axes[].parameter_name` before sweep planning.

Every enumerated value is checked against the same literal constraints as the target field. The compiler resolves each bound value to a concrete numeric value before signal construction and rejects missing parameters, malformed binding objects, wrong types, non-finite values, and out-of-range values.

Expression strings, formulas, lambda/eval/code-like payloads, arbitrary field paths, runtime hooks, external sources, and implicit fallback values are not supported.

## Determinism and composition depth

Binding occurs inside the same per-variant compile path that already resolves indicator lookback and parameter operands. No compiled signal carries unbound references. Composition depth remains governed by the existing `max_condition_group_depth=3` schema and validator rules; the new value binding form is not an operand-composition mechanism.

## Existing-strategy regression result

Existing literal primitive thresholds still compile through the same paths. Existing parameter-bound lookback behavior remains unchanged.

Committed `STRAT-SPEC-0004`, `STRAT-SPEC-0005`, and `STRAT-SPEC-0006` validate unchanged under the additive schema and validator.

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

## No strategy or evidence authority

No Strategy Spec, Variant Manifest, Sweep Plan, Result Population, probe, canonical trial, candidate registration, walk-forward/OOS artifact, ranking, recommendation, policy change, promotion decision, paper/live path, runtime behavior, capital movement, OMS/risk/reconciliation change, broker/exchange connectivity, or autonomous agent action is created by this package.

The next route remains Main-directed.
