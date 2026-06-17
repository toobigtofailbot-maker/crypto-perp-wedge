# WP-ONLINE-OHLCV-RUNNER-PERF-01

## Package class

Performance-only offline research runner/compiler optimization.

## Branch / worktree / base

- Branch: `perf/online-ohlcv-runner-perf-01`
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-ONLINE-OHLCV-RUNNER-PERF-01`
- Base: refreshed `main` at `feb4699` (`Merge pull request #505 from toobigtofailbot-maker/surface/online-ohlcv-bundled-surface-integration-01`)

## Changed files

- `tools/research_runner/spec_signal_compiler.py`
- `tests/test_spec_signal_compiler.py`
- `docs/research_pipeline/2026-06-online_ohlcv_runner_perf_01.md`
- `docs/status_entries/WP-ONLINE-OHLCV-RUNNER-PERF-01.md`

Scratch artifacts under `scratch/WP-ONLINE-OHLCV-RUNNER-PERF-01/` were generated for validation only and are not committed.

## Optimization summary

The compiler now caches primitive config lookups, condition/group boolean series, and inferred bar spacing; precomputes both-direction entry eligibility; writes both-direction signals through a positional array; and builds session/opening-range/breakout/retest/session-end helper outputs with positional arrays instead of repeated pandas label writes.

## Performance result

- Pre-optimization full-slice 15m ORB one-variant compile profile: 571.067 seconds.
- Post-optimization same one-variant compile profile: 47.501 seconds.
- Full-slice ORB 15m runner dry-run with `--max-workers 4`: completed in 131.623 seconds.
- Full-slice ORB denominator/outcomes: 8 denominator, 8 successful, no write.
- Full-slice ORB trade counts: `[999, 999, 901, 901, 1298, 1298, 1216, 1216]`.

## Byte / regression proof

- Bounded 90-day ORB runner payload: pre/post canonical JSON bytes match when the scratch run label is identical.
- Bounded 90-day ORB trade counts: `[34, 34, 32, 32, 45, 45, 41, 41]`.
- No-wick 4h documented trade counts reproduced: `[14, 2, 14, 2, 8, 8, 8, 8]`.
- RP-6236 dry-run canonical JSON bytes equal committed `research/result_populations/RP-6236.result_population.json`.

## Boundary summary

- Signal values changed: NO.
- `lib/backtest.py` changed: NO.
- `run_offline_sweep.py` changed: NO.
- Committed Strategy Spec / VM / Sweep / RP artifacts created: NO.
- Canonical write: NO.
- Candidate / walk-forward / paper / live / runtime / capital: NO.
- Protected paths touched: NO.

## Validation status

Focused validations completed:

- `pytest tests/test_spec_signal_compiler.py -q`: PASS, `196 passed`.
- Scratch ORB Strategy Spec validation: PASS.
- Scratch ORB VM/Sweep validation: PASS.
- Scratch no-wick Strategy Spec validation: PASS.
- Scratch no-wick VM/Sweep validation: PASS.
- Full-slice ORB 15m dry-run: PASS.
- No-wick 4h dry-run: PASS.
- RP-6236 dry-run byte regression: PASS.

Broad validations completed:

- `git diff --check`: PASS.
- `git diff --cached --check`: PASS.
- `python -m tools.registry.validate_strategy_specs`: PASS.
- `python -m tools.registry.validate_variant_sweep_artifacts`: PASS.
- `python -m tools.registry.validate_indicator_catalogs`: PASS.
- `python -m tools.registry.validate_result_populations`: PASS.
- `python -m tools.registry.validate_candidate_registry`: PASS.
- `python -m tools.registry.validate_paper_state`: PASS.
- `python -m tools.research_query.run --list-views`: PASS.
- `pytest tests/test_offline_research_runner.py -q`: PASS, `94 passed, 2 warnings`.
- `pytest tests/test_research_query.py -q`: PASS, `64 passed`.
- `tools/dev/diff_scope_summary.py --check-forbidden`: PASS, no forbidden-path matches.
- `tools/dev/verify.py --integrity-views --integrity-max-workers 4 --timeout-seconds 300 --max-output-chars 6000 --json`: PASS.
- `tools/dev/verify.py --full-pytest-sharded --pytest-shards 4 --pytest-shard-workers 4 --timeout-seconds 300 --full-pytest-timeout-seconds 1800 --max-output-chars 6000 --json`: PASS.
