# WP-EXPRESS-A3 Branch State

- Package: WP-EXPRESS-A3 - closed trade-frequency / re-entry control support.
- Branch: `express/a3-trade-frequency-controls`.
- Base: refreshed `origin/main` after PR #463 / WP-EXPRESS-A2 was confirmed merged.
- Dedicated worktree: `C:\GitHub\crypto-perp-wedge-WP-EXPRESS-A3`.

## Scope Summary

This package adds an optional closed `entry_logic.entry_controls` object with
one supported field:

- `min_bars_between_entries`

The field is an integer in `[1, 100000]`. When present, the compiler permits a
new entry signal only when more than `N` bars have elapsed since the previous
nonzero entry signal in the final compiled signal stream. The first valid entry
has no prior entry and is allowed.

For both-direction specs, the throttle is shared across long and short entries
in the final mutually exclusive signal stream. It does not create side-specific
cooldowns, does not mirror signals, and preserves existing simultaneous
long/short conflict behavior.

## Boundary Summary

- No `lib/` changes.
- No runner/backtester changes.
- No Strategy Spec, variant manifest, sweep plan, result-population, trial-log,
  candidate lifecycle, ranking, readiness, promotion, data-lineage, runtime,
  paper/live, OMS/risk, broker/exchange, or collateral authority changes.
- The Strategy Spec schema change is additive: existing specs remain valid
  without `entry_controls`; malformed, null, unknown, or executable-key control
  payloads fail closed.
- Exit logic is not suppressed or otherwise altered. Sizing, fills, PnL, costs,
  liquidation, and funding behavior are unchanged.

## Implementation Summary

- `research/schemas/strategy_spec.schema.json` now accepts optional
  `entry_logic.entry_controls.min_bars_between_entries`.
- `tools/research_runner/spec_signal_compiler.py` applies the throttle inside
  the compiler-owned signal loop only when a flat-state entry would otherwise
  be generated.
- Focused tests cover too-frequent re-entry suppression, first-entry behavior,
  exit preservation, null/warmup behavior, both-direction shared-stream
  behavior, no-lookahead mutation behavior, malformed/unknown controls,
  forbidden executable keys, and A1/A2 regression preservation through the
  existing compiler and validator suites.

## Validation Status

Validation completed on the package branch using
`C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe` where Python
dependencies were required:

- `git diff --check`: PASS
- `git diff --cached --check`: PASS
- `git diff --name-only`: PASS; changed files are limited to the authorized
  schema, compiler, focused tests, and this status fragment.
- `python tools/dev/diff_scope_summary.py --check-forbidden`: expected
  advisory nonzero because the authorized schema file matches the tool's broad
  `research/` forbidden prefix.
- `python -m tools.registry.validate_strategy_specs`: PASS
- `python -m tools.registry.validate_indicator_catalogs`: PASS
- `python -m tools.registry.validate_result_populations`: PASS
- `python -m tools.research_query.run --list-views`: PASS
- `python -m pytest tests/test_spec_signal_compiler.py tests/test_validate_strategy_specs.py -q`: PASS, 237 passed
- `python -m pytest -q`: PASS, 1426 passed, 1 skipped, 6 warnings
