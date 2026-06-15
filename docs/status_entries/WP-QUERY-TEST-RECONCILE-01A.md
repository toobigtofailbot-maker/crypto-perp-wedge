# WP-QUERY-TEST-RECONCILE-01A - composed operand query-view fix

## Branch / Worktree

- Branch: `tests/query-reconcile-rp7134`
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-QUERY-TEST-RECONCILE-01`
- Base: current `origin/main` after fast-forward to `386a0f2`.

## Scope Summary

This follow-up resolves the blocked `WP-QUERY-TEST-RECONCILE-01` state by
making `v_strategy_spec_condition_groups` tolerate valid composed operands in
the current Strategy Spec corpus, then reconciling stale query-test expectations
for `STRAT-SPEC-0003`, `VM-0003`, `SWEEP-PLAN-0003`, and `RP-7134`.

## Root Cause

The previous `v_strategy_spec_condition_groups` implementation carried the full
nested `condition_group` struct through a `UNION ALL` across entry, exit, and
filter groups. With `STRAT-SPEC-0003`, that forced DuckDB to reconcile
heterogeneous nested operand structs, including composed `z_score` operands and
simple scalar operands. Current valid repo data then raised DuckDB
`ConversionException` failures such as malformed JSON input `z_score` or
`value` during normal view reads.

## Changes Made

- `tools/research_query/views.sql`: `v_strategy_spec_condition_groups` now
  projects scalar top-level group metadata inside each union branch instead of
  unioning the nested `condition_group` struct.
- `tests/test_research_query.py`: current-corpus expectations now include
  `STRAT-SPEC-0003`, `VM-0003`, `SWEEP-PLAN-0003`, and `RP-7134`.
- `tests/test_research_query.py`: added focused regression coverage that
  confirms the current `STRAT-SPEC-0003` entry conditions contain composed
  `z_score` operands and that `v_strategy_spec_condition_groups` returns their
  top-level groups without conversion errors while preserving scalar/simple
  operand specs.

No result populations, Strategy Specs, Variant Manifests, Sweep Plans, schemas,
validators, compiler, runner, data, runtime, paper/live, OMS, risk,
reconciliation, broker, or exchange paths were changed.

## Validation

- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_research_query.py -x -vv --tb=short` before fix: reproduced
  `test_named_views_present` failure with DuckDB `ConversionException`:
  malformed JSON input `z_score`.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_research_query.py -q` before fix:
  8 failed, 55 passed.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_research_query.py -q` after fix:
  64 passed.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest`:
  1449 passed, 1 skipped, 6 warnings.
- `git diff --check`: pass.
- `git diff --cached --check`: pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_strategy_specs`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_variant_sweep_artifacts`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_indicator_catalogs`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_result_populations`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/verify.py --help`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py --check-forbidden`:
  pass; no forbidden-path matches.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/verify.py --integrity-views --integrity-max-workers 4 --timeout-seconds 300 --max-output-chars 6000`:
  pass; all discovered integrity views clean.

## Boundaries

- Result populations changed: no.
- Strategy Specs changed: no.
- Variant Manifests changed: no.
- Sweep Plans changed: no.
- Compiler/schema/catalog/lib/runner changed: no.
- Runtime, paper/live, OMS/risk/reconciliation, broker/exchange paths changed:
  no.
- Candidate authority, ranking, readiness, promotion, recommendation, policy, or
  runtime authority created: no.
- Query behavior broadened beyond composed operand handling: no.

## Standing Rule Handling

The `WP-QUERY-TEST-RECONCILE-01` blocked status fragment remains present as
diagnostic history. No active canonical-write checklist/template target was
found in this follow-up, so the standing rule remains recorded in the status
fragments only: any package adding or changing a canonical result population
must run `tests/test_research_query.py` and full pytest, or explicitly report
why full pytest could not be run.

## Current State

Ready for PR review.
