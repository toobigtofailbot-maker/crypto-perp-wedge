# Dynamic Sizing Pre-Rerun Readiness Audit

## Status / authority boundary

This is scratch/read-only audit evidence. It is not a canonical result population, does not rank variants, does not register candidates, does not mark readiness, does not promote strategies, and does not authorize paper/live/runtime behavior.

`WP-REALISM-SIZING-02e` surfaces the STRAT-SPEC-0002 dynamic 1x scratch population before any Karl-gated canonical dynamic-sizing result-population write. It changes no runner, lib, schema, validator, test, Strategy Spec, variant manifest, sweep plan, data, result population, candidate registry, dashboard, runtime, paper/live, OMS/risk, broker/exchange, or protected path.

## Source stack

- Package: `WP-REALISM-SIZING-02e`
- Branch: `audit/realism-sizing-02e-pre-rerun`
- Parent Strategy Spec: `STRAT-SPEC-0002`
- Parent Variant Manifest: `VM-0002`
- Parent Sweep Plan: `SWEEP-PLAN-0002`
- Reference result population lineage: `RP-6688`
- Dynamic sizing core: `docs/research_pipeline/2026-06-dynamic_equity_sizing_impl_note.md`
- Runner exposure: `docs/research_pipeline/2026-06-dynamic_sizing_runner_exposure_impl_note.md`
- Sizing metadata schema/validator: `docs/research_pipeline/2026-06-sizing_metadata_schema_note.md`

## Scratch run configuration

- Sizing mode: `dynamic_equity_target_leverage`
- Target leverage: `1.0`
- Determinism seed: `190`
- Execution provenance class: `canonical_real_data`
- Scratch result population id: `RP-0469`
- Scratch CSV input: `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02e\btc_usdt_15m_full_d4_lineage_scratch.csv`
- Scratch result artifact: `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02e\result_populations\RP-0469.result_population.json`
- Dry run: `true`
- Wrote canonical output: `false`
- Output path: `null`

CLI-equivalent runner configuration:

```powershell
python -m tools.research_runner.run_offline_sweep --strategy-spec research/strategy_specs/STRAT-SPEC-0002.strategy_spec.json --variant-manifest research/variant_manifests/VM-0002.variant_manifest.json --sweep-plan research/sweep_plans/SWEEP-PLAN-0002.sweep_plan.json --canonical-15m --ohlcv-input C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02e\btc_usdt_15m_full_d4_lineage_scratch.csv --d4-catalog-slice research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json --d2-import-report research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.import_report.json --sizing-mode dynamic_equity_target_leverage --target-leverage 1.0
```

The repo runner's sequential row loop did not finish within a 60-minute local timeout. The completed scratch artifact uses the same repo runner/backtest internals and D4 execution input, with per-variant scratch rows run in parallel outside the repo and assembled into one non-committed scratch result population. No repo code was changed.

## Data provenance

- Data catalog ref: `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
- Data slice identity: `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- Row count: `220128`
- Expected row count: `220128`
- Time range: `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`
- D3 validation report SHA256: `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`
- D2 import report SHA256: `543c944f727b2b9a7ad06742946ecefc91aa8b94723f46509e4041f622ef57ad`
- D4 catalog artifact SHA256: `f7b98c4d7759b6ba0c9bf8559bcea5e3311d3abe877930da254aeca96f53105a`
- Gap count: `0`
- Missing bar count: `0`
- Duplicate group count: `0`
- Duplicate row count: `0`
- Raw source SHA256: `343b639e35ce79824d26bddf6d70af2641c9d76003301e303f83cdf61d4feab4`
- Normalized SHA256: `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`
- Committed denominator: `10`
- Actual variant rows: `10`
- Outcome count sum: `10`
- Outcome counts: `10 successful / 0 failed / 0 errored / 0 invalid / 0 excluded / 0 filtered / 0 data_unavailable / 0 not_attempted / 0 aborted`

The data catalog ref and slice identity match `RP-6688`.

## Sizing metadata

The scratch artifact contains this top-level `sizing_metadata` block:

```json
{
  "entry_reference_price_basis": "next_bar_open_pre_fee_slippage",
  "sizing_equity_basis": "realized_available_equity_at_entry",
  "sizing_mode": "dynamic_equity_target_leverage",
  "target_leverage": 1.0
}
```

No `max_leverage_cap` is present.

Current repo truth: `run_offline_sweep.py` exposes `sizing_mode` and `target_leverage`, and the schema/validator support top-level `sizing_metadata`, but the runner does not currently emit top-level `sizing_metadata` by itself. For this scratch audit only, the block above was populated into the non-committed scratch artifact from the runner sizing context, then both identity hashes were recomputed and validated against current validator behavior.

## Identity-hash chain

- Input identity hash: `sha256:15438f68d38c925a80b6ed001be34b0d75707f17c1111aff62c0fcd90933ab3b`
- Result population identity hash: `sha256:bc57f752fc969a4fc3f5e7b5c79ece8b682ea19257c64dbdeaac4bff2d03cf82`
- `input_identity_hash.hash_scope` includes `sizing_metadata`: yes
- `result_population_identity_hash.hash_scope` includes `sizing_metadata`: yes
- Determinism proof: two repeated identity reconstructions from the same scratch artifact produced the same input and result hashes above.

Input hash scope:

```text
parent_strategy_spec.strategy_spec_hash
parent_variant_manifest.manifest_hash
parent_sweep_plan.sweep_plan_identity_hash
parent_variant_manifest.committed_population_count
parent_sweep_plan.committed_population_count
execution_context.runner_code_ref
execution_context.repo_commit
data_coverage_summary.data_catalog_ref
data_coverage_summary.data_slice_identity
backtest_assumption_summary
sizing_metadata
```

Result hash scope:

```text
parent_strategy_spec.strategy_spec_hash
parent_variant_manifest.manifest_hash
parent_sweep_plan.sweep_plan_identity_hash
parent_variant_manifest.committed_population_count
parent_sweep_plan.committed_population_count
execution_context.runner_code_ref
execution_context.repo_commit
data_coverage_summary.data_catalog_ref
data_coverage_summary.data_slice_identity
backtest_assumption_summary
committed_denominator_snapshot
variant_result_rows
outcome_category_counts
append_only_ledger.creation_event_ref
validation_summary.validator_identity
sizing_metadata
```

## Per-variant scratch population

`max_drawdown` below maps to the scratch artifact field `metrics.drawdown`. The liquidation / zero-equity flag is the exact terminal-equivalent check used for this audit: `return_pct == -1.0` or `metrics.drawdown == 1.0`.

| variant_id | sma_lookback_bars | band_threshold | return_pct | max_drawdown | win_rate | sharpe | trade_count | liquidation / zero-equity flag |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| VAR-000001 | 20 | 0.0025 | -0.999998194 | 0.999998257 | 0.689014041 | -3.169618686 | 12962 | false |
| VAR-000002 | 20 | 0.005 | -0.999714064 | 0.999732148 | 0.656729450 | -1.975828408 | 8017 | false |
| VAR-000003 | 20 | 0.01 | -0.975631111 | 0.977582598 | 0.616122343 | -0.906815290 | 3858 | false |
| VAR-000004 | 20 | 0.015 | -0.827978227 | 0.904671311 | 0.595734817 | -0.389424617 | 2157 | false |
| VAR-000005 | 20 | 0.02 | -0.616500646 | 0.726300399 | 0.592409241 | -0.174432132 | 1212 | false |
| VAR-000006 | 50 | 0.0025 | -0.999946644 | 0.999948377 | 0.740572968 | -2.168159878 | 8168 | false |
| VAR-000007 | 50 | 0.005 | -0.999062501 | 0.999127085 | 0.698291530 | -1.506881096 | 5502 | false |
| VAR-000008 | 50 | 0.01 | -0.987385031 | 0.988748687 | 0.653882726 | -0.938321186 | 3155 | false |
| VAR-000009 | 50 | 0.015 | -0.913642819 | 0.919707612 | 0.623857624 | -0.471047573 | 2079 | false |
| VAR-000010 | 50 | 0.02 | -0.802027796 | 0.839137615 | 0.611350575 | -0.281987775 | 1392 | false |

## Non-degeneracy check

- Count variants with `return_pct == -1.0`: `0`
- Count variants with `max_drawdown == 1.0`: `0`
- Count variants with liquidation / zero-equity terminal flag: `0`
- Uniform liquidation artifact reproduced: NO

This is non-degeneracy evidence only. It is not edge, profitability, ranking, readiness, promotion, candidate-registration, or trading evidence.

## Validation

- Scratch artifact path: `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02e\result_populations\RP-0469.result_population.json`
- Scratch validator result: pass, `0` errors from `tools.registry.validate_result_populations.validate_result_populations(...)` against the non-committed scratch directory.
- `sizing_metadata` accepted: yes
- Both identity hash scopes include `sizing_metadata`: yes
- Identity reconstruction deterministic: yes

Package-level validation commands are recorded in `docs/status_entries/WP-REALISM-SIZING-02e.md`.

## No-canonical-write proof

These checks returned no output before docs edits:

```powershell
git status --short research/result_populations
git diff -- research/result_populations
git status --short lib tools/research_runner/run_offline_sweep.py research/schemas tools/registry tests
git diff -- lib tools/research_runner/run_offline_sweep.py research/schemas tools/registry tests
```

The scratch JSON and scratch CSV live outside the repo under `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02e\` and are not committed.

## Limitations

- The repo runner's sequential full-D4 dry-run did not complete within a 60-minute local timeout.
- The completed scratch artifact parallelized per-variant row generation outside the repo while using existing runner/backtest internals and the same D4 execution input.
- The current runner does not emit top-level `sizing_metadata` by itself. This audit populated the schema-supported block only in scratch output to validate the metadata/hash chain without editing code or writing a canonical artifact.
- The scratch CSV was generated outside the repo from the local full 15m parquet because the catalog-referenced normalized CSV was not present locally. The scratch run records the committed D4 catalog/import provenance matching `RP-6688`; the scratch CSV is not committed.

## What this package does not authorize

This package does not authorize a canonical dynamic-sizing result-population write, result-population mutation, runner edit, lib edit, schema/validator edit, test edit, Strategy Spec mutation, variant manifest mutation, sweep plan mutation, data acquisition, candidate registration, ranking, readiness, promotion, paper/live/runtime behavior, OMS/risk behavior, broker/exchange behavior, or protected-path behavior.

## Next authority

This package does not authorize a canonical dynamic-sizing result population. Main/Karl review is required before any canonical write.
