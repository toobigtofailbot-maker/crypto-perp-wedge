# WP-VERIFY-01 - Standard verification entry point and env-only test pollution containment

## Branch / PR

- Branch: `tools/verify-01-standard-validation-entrypoint`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/458

## Package Class

- T3 tooling/test-support.

## Scope Summary

- Adds a standard repo-local verification entry point under `tools/dev/verify.py`.
- Contains the recurring missing-local-parquet test pollution by skipping only `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window` when its gitignored local parquet fixture is absent.
- Does not change runtime, runner, backtester, schema, query-layer behavior, result populations, canonical data lineage, or protected execution paths.

## Changed Files

- `tools/dev/verify.py`
- `tests/test_verify.py`
- `tests/test_backtest_liquidation.py`
- `docs/status_entries/WP-VERIFY-01.md`

## Validation Summary

- Branch refresh: PR #457 confirmed merged, branch rebased onto `origin/main` at merge commit `bd14800`, no conflicts.
- `git diff --check`: pass.
- `git diff --cached --check`: pass.
- `git diff --name-only`: pass; no unstaged tracked files after commit/rebase.
- `python tools/dev/diff_scope_summary.py --check-forbidden`: pass; no forbidden-path matches.
- `python -m tools.registry.validate_result_populations`: pass.
- `python -m tools.research_query.run --list-views`: pass.
- `python -m pytest tests/test_verify.py -q`: pass, 7 passed.
- `python -m pytest tests/test_validation_summary.py -q`: pass, 14 passed.
- `python -m pytest tests/test_backtest_liquidation.py -q`: pass, 14 passed / 1 skipped for absent gitignored local parquet fixture.
- `python tools/dev/verify.py --help`: pass.
- `python tools/dev/verify.py --pytest tests/test_verify.py`: pass.
- `python tools/dev/verify.py --json --pytest tests/test_verify.py`: pass.
- `python tools/dev/verify.py --integrity-views --json --max-output-chars 1200`: pass; all discovered `v_integrity_*` views returned zero rows.
- `python -m pytest -q`: pass, 1382 passed / 1 skipped / 6 warnings.

## Boundary Summary

- Forbidden paths touched: no.
- Production behavior changed: no.
- Schema/compiler/runner/lib/result-population/data-lineage changed: no.
- Candidate/paper/live/runtime/OMS-risk authority created: no.
- Verification helper preserves raw command strings, exit codes, timeout status, and material output; helper output remains advisory and does not replace raw command accountability.

## Merge Status

- Ready for review.

## Next Dependency / Runway Note

- No further WP-VERIFY dependency is known after PR #457 corrected the stale `RP-7520` corpus-count expectations on `main`.
