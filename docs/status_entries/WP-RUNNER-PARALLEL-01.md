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
- WP-RUNNER-PARALLEL-01A follow-up found the real D4A normalized CSV at
  `C:\GitHub\crypto-perp-wedge-d4a\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`.
- The selected CSV matches the committed catalog/import SHA:
  `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`.
- D4A row count and range: 220,128 rows from `2020-01-01T00:00:00Z` through
  `2026-04-11T23:45:00Z`, matching the catalog slice range.
- Full-D4 STRAT-SPEC-0004 / VM-0004 / SWEEP-PLAN-0004 scratch writes were run
  from this PR branch with `--canonical-15m`, the committed D4 catalog/import
  files, `--sizing-mode dynamic_equity_target_leverage`, `--target-leverage 1.0`,
  `--write-result-population`, and `--deterministic-seed 190`.
- Sequential proof command used `--max-workers 1`, run label
  `WP-RUNNER-PARALLEL-01A-SEQ`, and output directory
  `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_runner_parallel_01a\seq\result_populations`.
- Parallel proof command used `--max-workers 4`, run label
  `WP-RUNNER-PARALLEL-01A-PAR`, and output directory
  `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_runner_parallel_01a\par\result_populations`.
- Sequential full-D4 elapsed time: 2084.585 seconds.
- Parallel full-D4 elapsed time: 614.727 seconds.
- Real-D4 speedup ratio: 3.39x.
- Both runs wrote scratch `RP-2592.result_population.json`; no canonical result
  population path was written.
- Full-file byte identity: false, because the administrative `audit_envelope`
  run label differs (`WP-RUNNER-PARALLEL-01A-SEQ` versus
  `WP-RUNNER-PARALLEL-01A-PAR`).
- Sequential file SHA256:
  `424ef120719df9774cb03f304f40132459391b3aca122ac87b87319a48649a2b`.
- Parallel file SHA256:
  `62f8d511f603c6526c904128f36a380bd60af806002ab19cfc90b2541129245a`.
- Scientific/canonical identity: PASS. `result_population_id`,
  `input_identity_hash`, `result_population_identity_hash`,
  `committed_denominator_snapshot`, `outcome_category_counts`,
  `variant_result_rows`, `sizing_metadata`, `data_coverage_summary`, and
  `backtest_assumption_summary` were identical.
- Input identity hash for both runs:
  `sha256:d6df0801bdff4cd3b63e747677c0bd458ec65c7fbd9ce45dcf363bddcb739080`.
- Result population identity hash for both runs:
  `sha256:c146d7880687f363ab2fa258a3b205b63f6ce45ba88c7641d63636186656a0e7`.
- Row count/order/hash identity: PASS, 8 rows in identical variant order with
  identical `row_identity_hash` values.
- Denominator identity: PASS, committed denominator 8, row count 8, outcome
  counts sum 8.
- Outcome counts identity: PASS, 8 successful, zero aborted/data_unavailable/
  errored/excluded/failed/filtered/invalid/not_attempted.
- No nondeterminism or memory/process concern was observed during the real-D4
  proof run.

## WP-RUNNER-PARALLEL-01A Validation

- `git diff --check`: PASS.
- `git diff --cached --check`: PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_offline_research_runner.py -q`:
  PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_research_query.py -q`:
  PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest`:
  PASS.
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
  PASS.

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
