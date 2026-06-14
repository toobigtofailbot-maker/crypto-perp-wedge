# WP-EXPRESS-A2 Branch State

- Package: WP-EXPRESS-A2 - closed trend / regime filter entry-gating support.
- Branch: `express/a2-trend-regime-entry-gates`.
- Base: refreshed `origin/main` after PR #461 / WP-EXPRESS-A1 was confirmed merged.
- Dedicated worktree: `C:\GitHub\crypto-perp-wedge-WP-EXPRESS-A2`.

## Scope Summary

This package adds `trend` as a closed Strategy Spec condition-group role and compiler-supported entry-gate group role. Existing `regime` filter groups remain supported as entry gates. Trend/regime gates reuse the existing closed condition-group semantics:

- gate groups are evaluated only as entry filters;
- when all gate conditions are true, normal entry conditions may operate;
- when a gate condition is false or null, entry is blocked;
- warmup/null indicator values remain false through existing condition evaluation;
- exit logic is not altered.

## Boundary Summary

- No `lib/` changes.
- No runner/backtester changes.
- No Strategy Spec, variant manifest, sweep plan, result-population, candidate lifecycle, ranking, readiness, promotion, data-lineage, runtime, paper/live, OMS/risk, broker/exchange, or collateral authority changes.
- The Strategy Spec schema change is additive: existing group roles remain accepted, and `trend` is added as a closed enum value.
- No trade-frequency, cooldown, re-entry, minimum-hold, or other A3 stateful timing semantics are introduced.

## Implementation Summary

- `research/schemas/strategy_spec.schema.json` now accepts `group_role: "trend"`.
- `tools/research_runner/spec_signal_compiler.py` now treats `trend` groups like existing `regime` groups in the entry-gate allow-list.
- Focused compiler tests cover trend gates allowing/blocking entries, regime warmup/null blocking, no-lookahead future mutation, both-direction compatibility through the shared filter path, unknown/malformed gate failure, unsupported operands, forbidden executable keys, and existing z-score / plus-minus regressions.
- Focused validator tests cover accepted `trend` / `regime` filter entry gates, unknown gate-type rejection, and forbidden executable-key posture.

## Validation Status

Validation completed or pending on the package branch:

- `git diff --check`: PASS
- `git diff --cached --check`: PASS
- `git diff --name-only`: PASS; changed files are limited to the schema enum, compiler allow-list, focused tests, and this status fragment.
- `python tools/dev/diff_scope_summary.py --check-forbidden`: expected advisory nonzero because the authorized schema file matches the tool's broad `research/` forbidden prefix.
- `python -m pytest tests/test_spec_signal_compiler.py tests/test_validate_strategy_specs.py -q`: PASS using `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe`
- `python -m tools.registry.validate_strategy_specs`: PASS using `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe`
- `python -m tools.registry.validate_indicator_catalogs`: PASS using `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe`
- `python -m tools.registry.validate_result_populations`: PASS using `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe`
- `python -m tools.research_query.run --list-views`: PASS using `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe`
- `python -m pytest -q`: PASS, 1409 passed, 1 skipped, 6 warnings in 1183.05 seconds using `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe`
