# WP-SPEC-BOTHDIR-01c - Canonical both-direction result population

- Package class: T3 canonical research-artifact generation / result-population write.
- Branch: `research/spec-bothdir-01c-result-population`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/439
- Karl gate: Karl authorized WP-SPEC-BOTHDIR-01c after WP-SPEC-BOTHDIR-01b merged. This package writes the first canonical both-direction result population only. It does not authorize result interpretation, ranking, readiness, promotion, paper/live, runtime, or any follow-on package.
- Scope summary: Runs the first Karl-authorized canonical both-direction sweep for the merged `STRAT-SPEC-0002` / `VM-0002` / `SWEEP-PLAN-0002` frozen pre-registration set and writes one complete result population.
- Authorization basis: `WP-SPEC-BOTHDIR-01b` merged in PR #438, and Karl explicitly authorized the separately scoped `WP-SPEC-BOTHDIR-01c` downstream gate after that merge. The follow-up authorization allowed a narrow stale corpus expectation update in `tests/test_offline_research_runner.py`, plus `tests/test_research_query.py` only if needed for stale repo-state assertions caused by adding `RP-6688`.
- Parent artifacts:
  - Strategy Spec: `STRAT-SPEC-0002`
  - Variant Manifest: `VM-0002`
  - Sweep Plan: `SWEEP-PLAN-0002`
- Created result population:
  - `research/result_populations/RP-6688.result_population.json`
  - `result_population_id`: `RP-6688`
  - File SHA256: `52197cdca855112653e880946814674400922c5ccd9e63b991c9fb9d73d1b336`
- Data provenance:
  - D4 catalog ref: `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
  - D4 slice identity: `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
  - Execution provenance class: `canonical_real_data`
  - D3 validation identity: `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`
- Denominator: committed denominator 10; result rows 10; outcome counts sum 10; all variants retained in denominator accounting.
- Outcome counts: 10 successful / 0 failed / 0 errored / 0 invalid / 0 excluded / 0 filtered / 0 data_unavailable / 0 not_attempted / 0 aborted.
- Identity hashes:
  - Input identity hash: `sha256:ea9ea760ef7a5d30956a4573fc4ca0c39b43a533803667370219f5e3f7ffe386`
  - Result population identity hash: `sha256:7ee08cc1f30e26c318b39d571b90d25406072329ce4a67bd7c94ec35f98fcdbc`
- Backtest-realism assumptions: existing locked declaration surface only: `taker_entry_taker_exit`, `fixed_bps`, `complete`, `entry_price`, `zero_equity`, `close`, and `next_open_close_mark`.
- Test correction: A stale canonical corpus expectation in `tests/test_offline_research_runner.py` was updated to include `RP-6688`. This did not change runner behavior or query semantics. `tests/test_research_query.py` was also updated only for stale exact result-population corpus assertions caused by adding `RP-6688`.
- Validation summary:
  - `python -m tools.registry.validate_strategy_specs`: pass.
  - `python -m tools.registry.validate_variant_sweep_artifacts`: pass.
  - Scratch result-population validation for `RP-6688`: pass.
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - `python -m pytest tests/test_offline_research_runner.py -q`: pass, 41 tests.
  - `python -m pytest tests/test_spec_signal_compiler.py -q`: pass, 124 tests.
  - `python -m pytest tests/test_research_query.py -q`: pass, 63 tests.
  - `python -m pytest -q`: environment-only failure, 1312 passed / 1 failed / 6 warnings. The failure is `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window`, which requires gitignored local file `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet` absent from the isolated worktree.
- Boundary summary: No Strategy Spec, variant manifest, sweep plan, schema, validator, compiler, runner, catalog, lib, runtime, paper/live, OMS/risk, broker/exchange, candidate registry, dashboard implementation, or protected-path behavior changed. No result interpretation, ranking, recommendation, readiness, promotion, transition, paper/live, runtime, or execution authority is created.
- Active-WP requirement traceability:

| Requirement | Evidence | Status |
|---|---|---|
| 01b merged before start | PR #438 / `origin/main` merge commit `bb7843e` | satisfied |
| `STRAT-SPEC-0002` used unchanged | result lineage and changed-file list | satisfied |
| `VM-0002` used unchanged | result lineage and changed-file list | satisfied |
| `SWEEP-PLAN-0002` used unchanged | result lineage and changed-file list | satisfied |
| existing BTCUSDT 15m D4 data provenance used | result data coverage | satisfied |
| no synthetic fixture fallback | `execution_provenance_class=canonical_real_data` | satisfied |
| committed denominator = 10 | `committed_denominator_snapshot` | satisfied |
| result row count = 10 | `variant_result_rows` length | satisfied |
| outcome counts sum = 10 | `outcome_category_counts.counts_sum` | satisfied |
| all variants retained | `VAR-000001` through `VAR-000010` rows | satisfied |
| parent hash chain valid | validators | satisfied |
| result identity hash valid | validators | satisfied |
| no Strategy Spec / VM / sweep plan changes | changed-file list | satisfied |
| no schema/validator/compiler/lib changes | changed-file list | satisfied |
| no candidate registry change | changed-file list | satisfied |
| no runtime/paper/live/protected changes | changed-file list | satisfied |
| stale offline-runner corpus expectation corrected | `tests/test_offline_research_runner.py` | satisfied |
| stale query corpus expectation corrected | `tests/test_research_query.py` | satisfied |
| validation passed | validators, integrity views, and focused tests | satisfied |
| full pytest run | completed with one environment-only missing gitignored data-file failure | satisfied |
| no ranking/readiness/promotion text | semantic audit found only artifact identity, raw result facts, validation facts, denominator discipline, non-authority declarations, boundary statements, Karl authorization statements, and forbidden-scope statements | satisfied |

- Merge status: PR #439 is open for review.
- Next authority: After this PR merges, result interpretation or checkpoint work remains separately gated by Main/Karl; this package authorizes no follow-on work.
