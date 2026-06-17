# Online OHLCV Surface Integration 01

Package: `WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01`

## 1. Authority boundary

This package drafts online OHLCV strategy surfaces and runs scratch-only integration probes. It does not freeze Strategy Specs, create canonical Variant Manifests, create canonical Sweep Plans, write Result Populations, run canonical trials, register candidates, authorize walk-forward/OOS, paper/live execution, runtime behavior, OMS/risk changes, broker/exchange connectivity, capital movement, or autonomous agent action.

Scratch artifacts were generated under `scratch/WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01/` and are intentionally not committed. Validator-compatible scratch statuses and hash fields were used only because the current offline runner requires validated parent Strategy Spec / Variant Manifest / Sweep Plan inputs before dry-run execution.

## 2. Source docs/code/data inspected

Docs inspected:

- `docs/project_status.md`
- `CLAUDE_START_HERE.md`
- `docs/runbook.md`
- `docs/research_pipeline/2026-06-online_ohlcv_hypothesis_param_lock.md`
- `docs/research_pipeline/2026-06-online_ohlcv_primitive_impl_01.md`
- `docs/research_pipeline/2026-06-online_ohlcv_exit_primitive_impl_01.md`
- `docs/research_pipeline/2026-06-online_ohlcv_variant_binding_01.md`
- `docs/research_pipeline/2026-06-probe_methodology_canonical_regrounding.md`
- `docs/architecture/online_ohlcv_primitive_design.md`

Code/schema/artifacts inspected:

- `research/schemas/strategy_spec.schema.json`
- `research/schemas/variant_manifest.schema.json`
- `research/schemas/result_population.schema.json`
- `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json`
- `tools/research_runner/spec_signal_compiler.py`
- `tools/research_runner/run_offline_sweep.py`
- `tools/registry/validate_strategy_specs.py`
- `tools/registry/validate_variant_sweep_artifacts.py`
- `tests/test_spec_signal_compiler.py`
- `tests/test_offline_research_runner.py`
- `tests/test_research_query.py`
- `research/data_slices/binance_usdtm_btcusdt_15m/`
- `research/data_slices/binance_usdtm_btcusdt_4h/`
- Existing `STRAT-SPEC-0006` / `VM-0006` / `SWEEP-PLAN-0006` / `RP-6236` 4h command and report lineage.

Repo-truth discovery:

- 15m data identity: `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`.
- 15m local data path used: `C:\GitHub\crypto-perp-wedge\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`.
- 15m catalog ref: `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`.
- 4h data identity: `binance_usdtm_btcusdt_ohlcv_4h:sha256:4379d2f0fad5e79bfd5576b308d01fb6134b0f5acf04013e73e00ce33ca96b30`.
- 4h local data path used: `C:\GitHub\crypto-perp-wedge\data\processed\d4h\binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_d4h_resampled.csv`.
- 4h parent lineage: deterministic 15m-to-4h UTC-boundary resample from the 15m D4A slice above; parent normalized SHA `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`.
- Indicator catalog has `sma`, `ema`, `atr`, and `stddev` compiler-owned builtins.
- Current value-binding syntax is `{"parameter_ref": "parameter_name"}` for primitive thresholds and selected exits; indicator lookback binding uses `{"bars_parameter_ref": "parameter_name"}`.
- Current primitive refs use `{"operand_type": "primitive_ref", "ref": "...", "field": "long|short|value", "timeframe": null, "lookback": null}` with `is_true`.
- Current runner command shape is `python -m tools.research_runner.run_offline_sweep --strategy-spec ... --variant-manifest ... --sweep-plan ... --canonical-15m|--canonical-4h --ohlcv-input ...` without `--write-result-population`.
- Scratch Strategy Spec / VM / Sweep artifacts can exist under `scratch/` and validate/run without repository registration or canonical writes.

## 3. Surface A: no-wick 4h EMA-retest draft

Draft ID used in scratch: `STRAT-SPEC-9001`.

Surface:

- BTCUSDT 4h primary timeframe.
- Both-direction entries.
- Side-specific no-wick impulse through `candle_shape` with VM-bound `wick_threshold` and `body_threshold`.
- EMA50 trend/retest proxy through existing data/indicator comparison grammar:
  - long: candle-shape long, `close > EMA50`, and `low <= EMA50`;
  - short: candle-shape short, `close < EMA50`, and `high >= EMA50`.
- ATR-stop exit with VM-bound `atr_stop_multiple`.
- Free parameter count: 3.
- Denominator: 8 variants from `wick_threshold {0.05, 0.10}` x `body_threshold {0.60, 0.70}` x `atr_stop_multiple {1.5, 2.0}`.

Decision:

- EMA-retest was expressed as a closed-bar EMA touch-and-close-confirmation proxy using existing comparison grammar. No midpoint-pullback primitive or new primitive was implemented.

## 4. Surface A: scratch integration command(s)

Scratch validation:

```powershell
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_strategy_specs --strategy-specs-dir scratch\WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01\nowick_4h
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_variant_sweep_artifacts --strategy-specs-dir scratch\WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01\nowick_4h --variant-manifests-dir scratch\WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01\nowick_4h --sweep-plans-dir scratch\WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01\nowick_4h
```

Scratch runner:

```powershell
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_runner.run_offline_sweep --strategy-spec scratch\WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01\nowick_4h\STRAT-SPEC-9001.strategy_spec.json --variant-manifest scratch\WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01\nowick_4h\VM-9001.variant_manifest.json --sweep-plan scratch\WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01\nowick_4h\SWEEP-PLAN-9001.sweep_plan.json --canonical-4h --ohlcv-input C:\GitHub\crypto-perp-wedge\data\processed\d4h\binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_d4h_resampled.csv --run-label WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01-nowick --sizing-mode dynamic_equity_target_leverage --target-leverage 1.0 --max-workers 1
```

## 5. Surface A: scratch integration result / blocker

Result: PASS.

- Strategy Spec validation: PASS.
- VM/Sweep validation: PASS.
- Compiler accepted `candle_shape` parameter refs, EMA comparisons, both-direction side groups, and ATR-stop parameter ref.
- Runner completed end to end on the existing 4h derived slice.
- Dry run: `true`.
- Wrote result population: `false`.
- Result population ID in dry-run memory: `RP-4307`.
- Denominator preserved: 8.
- Outcome counts: 8 successful, 0 failed/errored/aborted/data_unavailable/not_attempted.
- Nondegenerate: PASS; per-variant trade counts were `[14, 2, 14, 2, 8, 8, 8, 8]`.
- Core metrics were computable. First two scratch rows produced trade counts 14 and 2, fees/slippage/funding fields, drawdown, return, and Sharpe.

No blocker remains for this surface at scratch integration level.

## 6. Surface B: ORB 15m break-retest draft

Draft ID used in scratch: `STRAT-SPEC-9002`.

Surface:

- BTCUSDT 15m primary timeframe.
- UTC 00:00 daily session.
- Opening range length: first 2 bars.
- Close-confirmed opening-range breakout with VM-bound `breakout_tolerance_atr`.
- Close-confirmed opening-range retest with VM-bound `retest_window_bars`.
- `entry_controls.max_trades_per_session.max_trades = 1`.
- Exits:
  - `time_exit.session_end`;
  - `opening_range_opposite_side`;
  - `fixed_R_target` with VM-bound `fixed_R_target`.
- Both-direction entries.
- Free parameter count: 3.
- Denominator: 8 variants from `retest_window_bars {2, 4}` x `breakout_tolerance_atr {0.0, 0.1}` x `fixed_R_target {1.0, 2.0}`.

## 7. Surface B: scratch integration command(s)

Scratch validation:

```powershell
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_strategy_specs --strategy-specs-dir scratch\WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01\orb_15m
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_variant_sweep_artifacts --strategy-specs-dir scratch\WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01\orb_15m --variant-manifests-dir scratch\WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01\orb_15m --sweep-plans-dir scratch\WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01\orb_15m
```

Scratch runner attempted:

```powershell
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_runner.run_offline_sweep --strategy-spec scratch\WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01\orb_15m\STRAT-SPEC-9002.strategy_spec.json --variant-manifest scratch\WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01\orb_15m\VM-9002.variant_manifest.json --sweep-plan scratch\WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01\orb_15m\SWEEP-PLAN-9002.sweep_plan.json --canonical-15m --ohlcv-input C:\GitHub\crypto-perp-wedge\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv --d4-catalog-slice research\data_slices\binance_usdtm_btcusdt_15m\binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json --d2-import-report research\data_slices\binance_usdtm_btcusdt_15m\binance_usdtm_btcusdt_15m_20200101_20260411.import_report.json --run-label WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01-orb --sizing-mode dynamic_equity_target_leverage --target-leverage 1.0 --max-workers 4
```

## 8. Surface B: scratch integration result / blocker

Result: BLOCKED at runner completion.

- Strategy Spec validation: PASS.
- VM/Sweep validation: PASS.
- Compiler/runner command accepted the artifact set and real-data command shape, but the full-slice 15m dry-run did not complete within local timeout windows.
- Single-worker attempts exceeded 5 minutes and 15 minutes.
- CLI `--max-workers 4` full-slice attempt exceeded the extended local timeout without a runner summary.
- No canonical artifact was written.
- No result population was committed.

Blocker:

- The ORB 15m full-slice integration probe needs a smaller approved integration-instrumentation path or runner performance work before this surface can claim nondegenerate full-denominator scratch output.

Rejected as evidence:

- A Python stdin API attempt with `max_workers=4` produced multiprocessing spawn errors caused by Windows trying to import `<stdin>`. That was instrumentation noise, not ORB strategy evidence, and is not counted as a strategy result.

## 9. Nondegeneracy summary

No-wick 4h:

- Denominator preserved: YES, 8/8.
- At least one variant has trades: YES, all 8 variants had trades.
- Metrics computable: YES.
- Canonical write: NO.

ORB 15m:

- Denominator preserved in scratch artifacts: YES, 8 declared.
- Runner completion: NO.
- Nondegenerate metrics: NOT ESTABLISHED.
- Canonical write: NO.

## 10. Draft screen families

Future freeze review should define exact thresholds before canonical use. Draft screen families only:

- denominator completeness;
- nondegeneracy;
- drawdown-primary;
- cost computable;
- sensitivity across VM-bound axes;
- no winner-only reporting;
- compounding-aware metrics;
- no paper/live/candidate authority.

## 11. Freeze status: not frozen / Main-Karl-gated

Neither surface is frozen.

The no-wick 4h surface is scratch-integration successful only. The ORB 15m surface is blocked before nondegenerate runner output. Any Strategy Spec freeze, canonical VM/Sweep creation, Result Population write, candidate route, walk-forward/OOS route, or paper/live route remains Main/Karl-gated.

## 12. Deferred scope

Deferred:

- canonical Strategy Specs;
- canonical Variant Manifests;
- canonical Sweep Plans;
- canonical Result Populations;
- canonical trials;
- candidate registration;
- walk-forward/OOS;
- profitability claims;
- midpoint-pullback;
- higher-timeframe trend-bias binding;
- new primitives;
- new runner modes;
- ORB runner performance/instrumentation follow-up;
- paper/live/runtime/capital paths.

## 13. Forbidden scope

This package changes no canonical research artifacts, data slices, schemas, validators, compiler, runner, library code, configs/runtime, runtime, paper/live, OMS/risk/reconciliation, broker/exchange, credentials, or capital paths.

Scratch artifacts remain uncommitted and have no execution authority.
