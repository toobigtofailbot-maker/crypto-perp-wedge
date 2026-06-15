# WP-RUNNER-PARALLEL-01 Branch State

- Package: `WP-RUNNER-PARALLEL-01`.
- Branch: `tools/runner-parallel-01`.
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-RUNNER-PARALLEL-01`.
- Base: `origin/main` at `1da7489`, merge of PR #475; PR #474 is present at `e9d0017`.
- Package class: tooling/performance, deterministic build-test.

## Scope Summary

This package adds opt-in process-level parallel orchestration to
`tools/research_runner/run_offline_sweep.py` for independent variant rows and
walk-forward window/variant rows.

Sequential execution remains the default through `max_workers=1` and the new
CLI flag `--max-workers` defaults to `1`. Worker count is not written into
result-population payloads, identity scopes, or row hashes.

## Implementation Summary

- Adds API parameter `max_workers: int = 1`.
- Adds CLI flag `--max-workers`, positive integer only.
- Keeps the existing sequential row loop as the `max_workers == 1` path.
- Uses `ProcessPoolExecutor` only for `max_workers > 1`.
- Uses top-level worker functions so Windows process spawning can pickle them.
- Workers return metrics/error metadata only; the parent process assembles
  result rows and walk-forward rows in deterministic input order.
- Preserves abort handling by classifying variants in sorted order before task
  submission and not submitting variants after an infrastructure abort point.
- Preserves walk-forward window order and variant order by building deterministic
  task indexes and assembling rows by that index.

## Repo Truth Checked

- PR #474 equivalent query-layer fix is merged on base.
- PR #475 equivalent momentum prereg artifacts are merged on base.
- `run_offline_sweep.py` still owns offline runner orchestration.
- `lib/backtest.py` was not changed.
- `STRAT-SPEC-0003`, `VM-0003`, `SWEEP-PLAN-0003`, `RP-7134`,
  `STRAT-SPEC-0004`, `VM-0004`, and `SWEEP-PLAN-0004` are present on base.
- D4/D4A catalog/import references for BTCUSDT 15m are present under
  `research/data_slices/binance_usdtm_btcusdt_15m/`.

## Validation

- Package-local `.venv` path check: `.\.venv\Scripts\python.exe` is absent in
  this dedicated worktree; validation used the existing repo venv at
  `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe` from this worktree.
- `git diff --check`: PASS.
- `git diff --cached --check`: PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_offline_research_runner.py -q`:
  PASS, 84 passed, 2 warnings.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_research_query.py -q`:
  PASS, 64 passed in 548.04 seconds after one earlier 3-minute timeout.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest`:
  PASS, 1456 passed, 1 skipped, 6 warnings in 1381.79 seconds.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_strategy_specs`:
  PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_variant_sweep_artifacts`:
  PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_indicator_catalogs`:
  PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_result_populations`:
  PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`:
  PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/verify.py --help`:
  PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py --check-forbidden`:
  PASS, no forbidden-path matches.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/verify.py --integrity-views --integrity-max-workers 4 --timeout-seconds 300 --max-output-chars 6000`:
  PASS, all discovered integrity views clean.

## Identity / Performance Evidence

- Synthetic STRAT-SPEC-0004 / VM-0004 / SWEEP-PLAN-0004 scratch writes were
  run with `--max-workers 1` and `--max-workers 2`.
- Task count: 8 variants.
- Sequential elapsed: 1.814 seconds.
- Parallel elapsed: 2.835 seconds.
- Speedup ratio on tiny synthetic run: 0.64x; process overhead dominates at
  this scale.
- Scratch outputs were byte-identical:
  `ED67CEA5F3D7ED0F6BDDF287701FB9ED6BEE2F306C3AD531E25FC754372B0C3E`.
- Focused tests additionally prove sequential-vs-parallel identity for mixed
  non-success synthetic rows, abort/not-attempted semantics, canonical 15m
  fixture output, and walk-forward dry-run rows.
- Full D4 RP-7134 and STRAT-SPEC-0004 real-data comparisons were not run
  because the D4A normalized CSV referenced by the committed catalog is not
  present under `data/processed/d4a/` in this worktree or the root checkout.
  This remains a merge-hold proof item, not claimed as complete here.

## Boundaries

- `lib/backtest.py` touched: no.
- Compiler/schema/catalog touched: no.
- Strategy Specs changed: no.
- Variant Manifests changed: no.
- Sweep Plans changed: no.
- Result Populations changed: no.
- `tools/research_query` changed: no.
- Runtime, paper/live, OMS/risk/reconciliation, broker/exchange paths changed:
  no.
- Candidate, promotion, ranking, readiness, recommendation, policy, or runtime
  authority created: no.
