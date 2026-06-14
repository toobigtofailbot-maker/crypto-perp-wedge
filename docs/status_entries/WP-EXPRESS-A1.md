# WP-EXPRESS-A1 Branch State

- Package: WP-EXPRESS-A1 - closed z-score / volatility-normalized distance compiler support.
- Branch: `express/a1-zscore-volnorm-distance`.
- Base: refreshed `main` after PR #458 was confirmed merged.

## Scope Summary

This package adds a closed `composed_operand` form for `composition_type: "z_score"` with fixed fields:

- `value_operand`
- `center_operand`
- `scale_operand`
- `zero_scale_policy: "null_output"`

The compiler-owned computation is `(value - center) / scale`. A null scale, null operand, or zero scale produces null output, preserving the existing condition policy that null operands never make entries true.

## Boundary Summary

- No `lib/` changes.
- No runner/backtester behavior changes.
- No Strategy Spec, variant manifest, sweep plan, result-population, candidate lifecycle, ranking, readiness, promotion, data-lineage, runtime, paper/live, OMS/risk, broker/exchange, or collateral authority changes.
- The Strategy Spec schema change is additive: the existing plus/minus parameter-scaling composed operands remain accepted unchanged, and `z_score` is added as a separate fixed-arity branch.
- No indicator catalog entry is added because z-score is a compiler-owned composed operand rather than a catalog-declared indicator builtin.

## Implementation Summary

- `research/schemas/strategy_spec.schema.json` now accepts the fixed `z_score` composed operand shape.
- `tools/registry/validate_strategy_specs.py` validates `z_score` as a separate closed composed-operand shape, rejects nested composition, rejects non-`data_ref` / `indicator_ref` value-center-scale operands, and requires `zero_scale_policy: "null_output"`.
- `tools/research_runner/spec_signal_compiler.py` resolves `z_score` through reviewed compiler code only and masks zero-scale outputs to null.
- Focused tests cover manual pandas equivalence, warmup/null behavior, zero-scale behavior, no-lookahead mutation behavior, fail-closed invalid forms, forbidden-key posture, and both-direction compatibility.

## Validation Status

Validation completed on the package branch:

- `git diff --check`: PASS
- `git diff --cached --check`: PASS
- `python tools/dev/diff_scope_summary.py --check-forbidden`: expected nonzero advisory output because the authorized schema file matches the tool's broad `research/` forbidden prefix.
- `python -m tools.registry.validate_indicator_catalogs`: PASS
- `python -m tools.registry.validate_strategy_specs`: PASS
- `python -m tools.registry.validate_result_populations`: PASS
- `python -m tools.research_query.run --list-views`: PASS
- `python -m pytest tests/test_spec_signal_compiler.py tests/test_validate_strategy_specs.py -q`: PASS
- `python -m pytest tests/test_validate_indicator_catalogs.py -q`: PASS
- `python -m pytest tests/research_automation -q`: PASS
- Per-file top-level pytest isolation: PASS for all top-level `tests/test_*.py` files when long-running query files were given enough time.
- `python -m pytest -q`: PASS, 1398 passed, 6 warnings in 1296.36 seconds.
