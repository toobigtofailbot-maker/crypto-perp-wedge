# WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01

## Package class

Bundled strategy-surface draft plus scratch-only canonical-equivalent integration probe.

## Branch / worktree / base

- Branch: `surface/online-ohlcv-bundled-surface-integration-01`
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01`
- Base: refreshed `main` at `93b3b99` (`Merge pull request #504 from toobigtofailbot-maker/impl/online-ohlcv-variant-binding-01`)

## Changed files

- `docs/research_pipeline/2026-06-online_ohlcv_surface_integration_01.md`
- `docs/status_entries/WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01.md`

Scratch artifacts under `scratch/WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01/` were generated for integration only and are not committed.

## No-wick surface draft summary

- Scratch Strategy Spec: `STRAT-SPEC-9001`
- Surface: BTCUSDT 4h no-wick impulse plus EMA50 retest proxy.
- Direction: both.
- VM-bound axes: `wick_threshold {0.05, 0.10}`, `body_threshold {0.60, 0.70}`, `atr_stop_multiple {1.5, 2.0}`.
- Denominator: 8.
- Exit: ATR stop through existing `exit_logic.atr_stop`.

## No-wick integration result

PASS.

- Scratch Strategy Spec validates.
- Scratch VM/Sweep validate.
- Runner dry-run completed on existing 4h derived slice.
- Dry-run wrote: `false`.
- Denominator: 8.
- Outcome counts: 8 successful, 0 failed/errored/aborted/data_unavailable/not_attempted.
- Nondegenerate: YES; per-variant trade counts were `[14, 2, 14, 2, 8, 8, 8, 8]`.

## ORB surface draft summary

- Scratch Strategy Spec: `STRAT-SPEC-9002`
- Surface: BTCUSDT 15m UTC 00:00 opening-range break and retest.
- Direction: both.
- Opening range: first 2 x 15m bars.
- VM-bound axes: `retest_window_bars {2, 4}`, `breakout_tolerance_atr {0.0, 0.1}`, `fixed_R_target {1.0, 2.0}`.
- Denominator: 8.
- Exits: `time_exit.session_end`, `opening_range_opposite_side`, and `fixed_R_target`.

## ORB integration result

BLOCKED at runner completion.

- Scratch Strategy Spec validates.
- Scratch VM/Sweep validate.
- Full-slice real-data runner attempts did not complete within local timeout windows.
- No canonical artifact was written.
- Nondegenerate output was not established.

## Freeze status

Not frozen / Main-Karl-gated.

The scratch no-wick probe can inform a future freeze review. The ORB surface needs follow-up integration instrumentation or performance work before it can claim full-denominator nondegenerate integration success.

## Validation summary

Scratch validation:

- No-wick scratch Strategy Spec: PASS.
- No-wick scratch VM/Sweep: PASS.
- ORB scratch Strategy Spec: PASS.
- ORB scratch VM/Sweep: PASS.
- No-wick scratch runner dry-run: PASS, no write.
- ORB scratch runner dry-run: BLOCKED by timeout, no write.

Package validation:

- `git diff --check`: PASS.
- `git diff --cached --check`: PASS.
- `python -m tools.registry.validate_strategy_specs`: PASS.
- `python -m tools.registry.validate_variant_sweep_artifacts`: PASS.
- `python -m tools.registry.validate_indicator_catalogs`: PASS.
- `python -m tools.registry.validate_result_populations`: PASS.
- `python -m tools.registry.validate_candidate_registry`: PASS.
- `python -m tools.registry.validate_paper_state`: PASS.
- `python -m tools.research_query.run --list-views`: PASS.
- `pytest tests/test_spec_signal_compiler.py -q`: PASS, 195 passed.
- `pytest tests/test_offline_research_runner.py -q`: PASS, 94 passed, 2 warnings.
- `pytest tests/test_research_query.py -q`: PASS, 64 passed.
- `tools/dev/diff_scope_summary.py --check-forbidden`: PASS.
- `tools/dev/verify.py --integrity-views --integrity-max-workers 4 --timeout-seconds 300 --max-output-chars 6000 --json`: PASS.

Full sharded pytest was not run because this package changes only docs/status files and scratch-only probe artifacts were not committed.

## Boundary summary

- Canonical Strategy Spec / VM / Sweep / RP: NO.
- Canonical write: NO.
- Candidate / walk-forward / paper / live / runtime / capital: NO.
- Protected paths touched: NO.
- Scratch artifacts committed: NO.

## Exact next item

Main/Karl review/freeze decision may consider only the no-wick 4h integrated surface. ORB 15m requires a follow-up runner-instrumentation or performance package before freeze review.
