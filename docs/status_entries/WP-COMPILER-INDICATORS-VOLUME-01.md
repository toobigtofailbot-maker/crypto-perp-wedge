# WP-COMPILER-INDICATORS-VOLUME-01 Branch State

- Package: WP-COMPILER-INDICATORS-VOLUME-01 - Add RVOL and rolling VWAP support to the closed indicator catalog/compiler.
- Branch: `compiler/indicators-volume-01`.
- Base: refreshed `origin/main` at `8236f27`, the PR #536 merge commit.
- Dedicated worktree: `C:\GitHub\crypto-perp-wedge-worktrees\compiler-indicators-volume-01`.

## Scope Summary

- Adds `rvol_v1` and `rolling_vwap_v1` to the closed indicator catalog and build-test-only Strategy Spec signal compiler.
- The Strategy Spec schema remains unchanged because existing `indicator_ref` operands already support closed catalog IDs and explicit multi-output fields.
- `rvol_v1` exposes `rvol` and `volume_ma`; `rolling_vwap_v1` exposes only `rolling_vwap`.

## Semantic Summary

- RVOL is `volume_t / rolling_mean(volume, lookback_bars)_t`. It requires a full non-null window and returns null for a zero rolling-volume mean.
- Rolling VWAP uses candle typical price `(high + low + close) / 3` and computes `rolling_sum(typical_price * volume) / rolling_sum(volume)` over a full non-null lookback. A zero rolling-volume denominator returns null.
- Both indicators use only data available through the current bar. Warmup and any missing required input within the window produce null.
- `rolling_vwap_v1` is a candle/rolling approximation based on OHLCV bars. It is not true trade-level VWAP. True VWAP requires the trade-level price-times-volume sequence and remains deferred to future trade-level data work.

## Boundary Summary

- No external indicator libraries or external output were canonicalized, and no external code was copied.
- No dependency, data-ingestion, Strategy Spec schema, Strategy Spec validator, runner/backtester, `lib/`, runtime, paper/live, shadow, OMS/risk/reconciliation, safe-mode, broker/exchange, config, or credential changes.
- No canonical Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, trial logs, candidate lifecycle artifacts, or promotion/readiness surfaces changed.
- The catalog remains an interface declaration only; compiler code owns deterministic computations.

## Validation Status

Validation used `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe`:

- Focused pytest (`test_validate_indicator_catalogs.py`, `test_validate_strategy_specs.py`, `test_spec_signal_compiler.py`): PASS, 334 passed.
- Indicator Catalog validator: PASS.
- Strategy Spec validator: PASS.
- Result Population validator: PASS.
- Query view discovery: PASS.
- Full pytest: environment caveat, 1 unrelated failure; 1,839 passed, 1 skipped, 6 warnings. `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage` expected the gitignored local D4A normalized-data file in this isolated worktree. This known worktree-local fixture failure is independently documented in prior merged status entries and does not involve package-changed files.
- Package-focused rerun: PASS; catalog/compiler tests passed after the full-suite caveat was diagnosed.
