# Online OHLCV Runner Perf 01

Package: `WP-ONLINE-OHLCV-RUNNER-PERF-01`

## 1. Authority boundary

This package optimizes offline research signal-generation performance only. It does not create Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, probes as canonical evidence, canonical trials, candidate registration, walk-forward/OOS, paper/live execution, runtime behavior, OMS/risk changes, broker/exchange connectivity, capital movement, or autonomous agent action.

Scratch artifacts were generated under `scratch/WP-ONLINE-OHLCV-RUNNER-PERF-01/` for validation only and are not committed.

## 2. Problem statement

`WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01` validated the 15m ORB scratch Strategy Spec / Variant Manifest / Sweep Plan surface, but the full-slice 15m runner did not complete within local timeout windows. The blocker was performance in online OHLCV primitive signal generation, not a schema or data availability failure.

## 3. Source docs/code inspected

- `docs/research_pipeline/2026-06-online_ohlcv_surface_integration_01.md`
- `docs/status_entries/WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01.md`
- `docs/research_pipeline/2026-06-online_ohlcv_primitive_impl_01.md`
- `docs/research_pipeline/2026-06-online_ohlcv_exit_primitive_impl_01.md`
- `docs/research_pipeline/2026-06-online_ohlcv_variant_binding_01.md`
- `tools/research_runner/spec_signal_compiler.py`
- `tools/research_runner/run_offline_sweep.py`
- `tests/test_spec_signal_compiler.py`
- `tests/test_offline_research_runner.py`
- `tests/test_research_query.py`
- `research/result_populations/RP-6236.result_population.json`

Scratch command references were taken from the surface-integration note. The prior uncommitted scratch payloads were not available in the refreshed worktree, so this package recreated validator-compatible scratch inputs under `scratch/WP-ONLINE-OHLCV-RUNNER-PERF-01/`.

## 4. Profile result / slow path

Profiled command shape: full 15m ORB compiler path over `C:\GitHub\crypto-perp-wedge\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`, one representative variant.

Baseline profile before optimization:

- rows: 220,128
- elapsed: 571.067 seconds for one variant
- top slow paths: repeated entry/group/condition resolution around cached primitive refs; pandas label writes inside opening-range/session state; repeated bar-delta/session-end checks.

Post-optimization profile:

- rows: 220,128
- elapsed: 47.501 seconds for the same one-variant compile
- signal summary unchanged from the profiled baseline: `nonzero=12816`, `sum=-918.0`

## 5. Optimization summary

The implementation changes only `tools/research_runner/spec_signal_compiler.py`.

- Adds compiler-context caches for primitive config lookup, condition boolean series, group boolean series, and inferred bar spacing.
- Precomputes both-direction entry eligibility series before the per-bar position state loop.
- Keeps the existing position state machine but writes both-direction output through a positional float array.
- Builds session membership, opening-range, breakout, retest, and session-end helper outputs using positional arrays rather than repeated pandas label assignment.
- Leaves `lib/backtest.py`, runner result semantics, Strategy Specs, Variant Manifests, Sweep Plans, and Result Populations unchanged.

## 6. Byte-identical proof

Bounded-window ORB 15m runner proof:

- bounded input: first 90 days of the local 15m D4A CSV, 8,640 rows, scratch-only CSV under `scratch/WP-ONLINE-OHLCV-RUNNER-PERF-01/`
- pre-optimization runner: main worktree, scratch ORB artifacts, `max_workers=1`
- post-optimization runner: package worktree, same scratch ORB artifacts/input, `max_workers=1`
- result population ID: `RP-9298` in both runs
- trade counts: `[34, 34, 32, 32, 45, 45, 41, 41]` in both runs
- canonical JSON bytes: equal when using identical scratch `run_label`
- note: with different scratch run labels, the only payload difference was `audit_envelope.operator_notes[0]`; that field is administrative and excluded from identity scopes.

Additional compiler signal-array proof:

- compared old `HEAD` compiler to optimized compiler on the same 90-day ORB input for `VAR-000001` and `VAR-000008`
- both signal series matched exactly

## 7. Full-slice 15m ORB completion result

Full-slice command shape:

```powershell
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_runner.run_offline_sweep --strategy-spec scratch\WP-ONLINE-OHLCV-RUNNER-PERF-01\orb_15m\STRAT-SPEC-9102.strategy_spec.json --variant-manifest scratch\WP-ONLINE-OHLCV-RUNNER-PERF-01\orb_15m\VM-9102.variant_manifest.json --sweep-plan scratch\WP-ONLINE-OHLCV-RUNNER-PERF-01\orb_15m\SWEEP-PLAN-9102.sweep_plan.json --canonical-15m --ohlcv-input C:\GitHub\crypto-perp-wedge\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv --d4-catalog-slice research\data_slices\binance_usdtm_btcusdt_15m\binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json --d2-import-report research\data_slices\binance_usdtm_btcusdt_15m\binance_usdtm_btcusdt_15m_20200101_20260411.import_report.json --run-label WP-ONLINE-OHLCV-RUNNER-PERF-01-orb --sizing-mode dynamic_equity_target_leverage --target-leverage 1.0 --max-workers 4
```

Result:

- completed: YES
- wall-clock: 131.623 seconds
- dry run: `true`
- wrote result population: `false`
- result population ID in memory: `RP-5416`
- denominator: 8
- outcome counts: 8 successful, 0 failed/errored/aborted/data_unavailable/not_attempted
- full-slice trade counts from single-worker API extraction: `[999, 999, 901, 901, 1298, 1298, 1216, 1216]`
- single-worker API extraction wall-clock: 496.729 seconds

## 8. No-wick 4h reproduction result

Scratch no-wick 4h dry-run:

- completed: YES
- dry run: `true`
- wrote result population: `false`
- denominator: 8
- outcome counts: 8 successful, 0 failed/errored/aborted/data_unavailable/not_attempted
- result population ID in memory: `RP-5270`
- trade counts: `[14, 2, 14, 2, 8, 8, 8, 8]`

The original no-wick scratch payload was not available in the refreshed worktree because prior scratch artifacts were intentionally uncommitted. This package therefore proves the documented trade-count reproduction rather than a prior-payload byte match for no-wick.

## 9. RP-6236 regression result

Read-only dry-run over committed `STRAT-SPEC-0006` / `VM-0006` / `SWEEP-PLAN-0006` with local 4h CSV:

- result population ID: `RP-6236`
- denominator: 8
- wrote result population: `false`
- canonical JSON bytes equal committed `research/result_populations/RP-6236.result_population.json`
- trade counts: `[562, 558, 468, 454, 554, 556, 448, 432]`

## 10. Validation summary

Focused validation run before broad validators:

- `pytest tests/test_spec_signal_compiler.py -q`: PASS, `196 passed`
- bounded ORB pre/post canonical payload byte comparison: PASS
- full-slice ORB 15m dry-run completion: PASS
- no-wick 4h documented trade-count reproduction: PASS
- RP-6236 canonical JSON byte regression: PASS

## 11. Deferred scope

Deferred:

- Strategy Spec freeze
- canonical Variant Manifest or Sweep Plan creation
- canonical Result Population write
- candidate registration
- walk-forward/OOS
- signal-definition changes
- ATR implementation performance work beyond this package's required target
- runner multiprocessing API ergonomics on Windows stdin/script contexts
- paper/live/runtime/capital paths

## 12. Forbidden scope

Forbidden scope check:

- signal values changed: NO
- `lib/backtest.py` changed: NO
- `run_offline_sweep.py` changed: NO
- Strategy Spec / Variant Manifest / Sweep Plan / Result Population artifacts created in committed corpus: NO
- canonical write: NO
- candidate / walk-forward / paper / live / runtime / capital path: NO
- protected runtime, OMS, risk, reconciliation, broker, exchange, credentials, or capital path touched: NO
