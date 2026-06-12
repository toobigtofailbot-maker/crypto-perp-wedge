# WP-SPEC-BOTHDIR-01b - Author both-direction preregistration instances

- Package class: T2/T3 canonical research-artifact authoring / frozen pre-registration instances.
- Branch: `research/spec-bothdir-01b-prereg`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/438
- Karl gate: Karl-gated frozen canonical instance package. Mandatory frozen-instance report-back to Karl is required before merge. WP-SPEC-BOTHDIR-01c remains separately Karl-gated and is not authorized by this package.
- Scope summary: Creates the frozen Strategy Spec, Variant Manifest, and Sweep Plan instances for the accepted first both-direction BTCUSDT 15m OHLCV symmetric SMA-band mean-reversion design.
- Authorization basis: Main 5 accepted WP-SPEC-BOTHDIR-01a as the design basis; this package is authorized for WP-SPEC-BOTHDIR-01b only.
- Created artifacts:
  - `research/strategy_specs/STRAT-SPEC-0002.strategy_spec.json`
  - `research/variant_manifests/VM-0002.variant_manifest.json`
  - `research/sweep_plans/SWEEP-PLAN-0002.sweep_plan.json`
- Modified files:
  - `docs/status_entries/WP-SPEC-BOTHDIR-01b.md`
  - `docs/project_status.md`
  - `tests/test_research_query.py`
- Design basis: `docs/research_pipeline/2026-06-both_direction_sma_band_spec_design.md` and locked both-direction semantics from `docs/research_pipeline/2026-06-both_direction_semantics_lock.md`.
- Denominator: committed denominator 10; the manifest includes all 10 grid cells for `sma_lookback_bars in {20, 50}` crossed with `band_threshold in {0.0025, 0.005, 0.01, 0.015, 0.02}`. The sweep plan selects all 10 variants, records 0 executed variants, and keeps 10 not-attempted variants in denominator accounting.
- Hash chain:
  - Strategy Spec full parent hash: `sha256:aa2d05134e788b6b34e2ff03af8d111563dece743e943e134c0b8e46bee429e3`
  - Variant Manifest hash: `sha256:27d89f01b3ec5a7cbb87ad224481f6328727737aa292b7fa332d3474b6bda5bc`
  - `VM-0002` pins `STRAT-SPEC-0002`; `SWEEP-PLAN-0002` pins `VM-0002`.
- Backtest-realism assumptions: Existing locked declaration surface only: `taker_entry_taker_exit`, `fixed_bps`, `complete`, `entry_price`, `zero_equity`, `close`, and `next_open_close_mark`. No new realism assumption or realism-surface change is included.
- Data references: Existing BTCUSDT 15m OHLCV references only, including D4A catalog ref `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b` and slice identity `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`.
- Validation summary:
  - `python -m tools.registry.validate_strategy_specs`: pass.
  - `python -m tools.registry.validate_variant_sweep_artifacts`: pass.
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - `python -m pytest tests/test_research_query.py -q`: pass, 63 passed.
  - `python tools/dev/diff_scope_summary.py`: pass, with expected package-scope research artifact matches.
  - `python -m pytest -q`: environment-only failure, 1312 passed / 1 failed / 6 warnings. The failure is `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window`, which requires gitignored local file `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet` that is absent from the isolated worktree.
- Boundary summary: No sweep run, result population, candidate registry change, schema change, validator change, compiler change, catalog change, data acquisition, dashboard implementation, generated dashboard output, runtime, paper/live, OMS/risk, broker/exchange, or protected-path change is included.
- Active-WP requirement traceability:

| Requirement | Evidence | Status |
|---|---|---|
| next available Strategy Spec ID used | directory preflight + `STRAT-SPEC-0002.strategy_spec.json` | satisfied |
| next available VM ID used | directory preflight + `VM-0002.variant_manifest.json` | satisfied |
| next available sweep plan ID used | directory preflight + `SWEEP-PLAN-0002.sweep_plan.json` | satisfied |
| Strategy Spec uses accepted 01a design | `STRAT-SPEC-0002` plus 01a design doc | satisfied |
| side-labeled long/short entries included | `STRAT-SPEC-0002.entry_logic.groups` | satisfied |
| side-labeled long/short exits included | `STRAT-SPEC-0002.exit_logic.groups` | satisfied |
| plus/minus band operands used | `scale_by_one_minus_parameter` and `scale_by_one_plus_parameter` in `STRAT-SPEC-0002` | satisfied |
| bars_parameter_ref for SMA lookback used | `bars_parameter_ref: sma_lookback_bars` in SMA operands | satisfied |
| band_threshold parameter reused symmetrically | `STRAT-SPEC-0002` and `VM-0002` | satisfied |
| 10-cell grid complete | `VM-0002.variant_assignments` and `SWEEP-PLAN-0002.test_selection` | satisfied |
| committed denominator = 10 | `VM-0002.population_governance` and `SWEEP-PLAN-0002.trial_accounting` | satisfied |
| parent hash chain valid | focused artifact validators | satisfied |
| existing data refs used | `STRAT-SPEC-0002` provenance/data assumptions and this fragment | satisfied |
| existing realism assumptions only | `STRAT-SPEC-0002.backtest_realism_assumptions` and `SWEEP-PLAN-0002.realism_assumptions` | satisfied |
| no sweep run | changed-file list and sweep plan non-execution declarations | satisfied |
| no result population | changed-file list | satisfied |
| no candidate registry change | changed-file list | satisfied |
| validation passed | validators, integrity views, focused query test, and environment-only full-suite classification | satisfied |
| full pytest run | `python -m pytest -q` completed with one environment-only missing gitignored data-file failure | satisfied |
| Karl report-back before merge noted | this fragment | satisfied |
| no forbidden files touched | changed-file list and diff scope | satisfied |

- Merge status: Not merge-ready; Karl report-back is required before merge.
- Next authority: Review the frozen instances, prepare report-back to Karl, and wait for Karl explicit clearance before merge. WP-SPEC-BOTHDIR-01c remains separately Karl-gated.
