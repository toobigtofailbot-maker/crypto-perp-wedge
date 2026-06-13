# Canonical Dynamic Sizing Runner Readiness

## Status / authority boundary

This is build-test/scratch runner-readiness evidence. It is not a canonical result population, does not rank variants, does not register candidates, does not mark readiness, does not promote strategies, and does not authorize paper/live/runtime behavior.

`WP-REALISM-SIZING-02f` makes the offline runner emit top-level dynamic sizing metadata directly, includes that metadata in both runner-produced identity-hash scopes, and records a full STRAT-SPEC-0002 dynamic 1x scratch run through the canonical runner path. The package writes no canonical result population and mutates no prior result population.

## Source runway

- `WP-REALISM-SIZING-02b`: opt-in `dynamic_equity_target_leverage` support in `lib/backtest.py`.
- `WP-REALISM-SIZING-02c`: offline runner `sizing_mode` / `target_leverage` exposure.
- `WP-REALISM-SIZING-02d`: result-population schema/validator support for optional `sizing_metadata`.
- `WP-REALISM-SIZING-02e`: scratch/read-only dynamic 1x pre-rerun audit showing non-degenerate full-D4 scratch metrics and the limitation that the runner did not emit top-level `sizing_metadata` directly.

## Runner sizing_metadata emission

For `sizing_mode=dynamic_equity_target_leverage` and `target_leverage=1.0`, the runner-generated scratch artifact contains top-level:

```json
{
  "entry_reference_price_basis": "next_bar_open_pre_fee_slippage",
  "sizing_equity_basis": "realized_available_equity_at_entry",
  "sizing_mode": "dynamic_equity_target_leverage",
  "target_leverage": 1.0
}
```

No `max_leverage_cap` is present in this slice.

Default and explicit fixed-mode runner outputs do not emit top-level `sizing_metadata` and do not include `sizing_metadata` in either identity-hash scope.

## Full-D4 dry-run configuration

- Strategy Spec: `STRAT-SPEC-0002`
- Variant Manifest: `VM-0002`
- Sweep Plan: `SWEEP-PLAN-0002`
- Sizing mode: `dynamic_equity_target_leverage`
- Target leverage: `1.0`
- Deterministic seed: `190`
- Runner path: `tools.research_runner.run_offline_sweep`
- Scratch output directory: `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02f\result_populations`
- Scratch result artifact: `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02f\result_populations\RP-7520.result_population.json`
- Canonical result-population directory: not used for output.

The catalog-referenced normalized CSV path from the D4 catalog, `data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`, was not present in the root checkout or the isolated worktree. The run used the existing local 02e full-D4 scratch CSV fallback at `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02e\btc_usdt_15m_full_d4_lineage_scratch.csv`, with SHA256 `ec69b3a5ba3a00b0f2937c9c7b3aba04c4aaecd88762b699092c5b26656cc014`. The CSV has 220,128 rows, no duplicate timestamps, exact 15-minute spacing, and the D4 range `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`. The runner was invoked with the committed D4 catalog slice and D2 import report so the generated artifact records the RP-6688 D4 catalog ref and slice identity.

## Runtime characterization

- Elapsed runtime: `01:22:51.1896865`
- Runner exit status: success
- Output count: one scratch result-population JSON outside the repo
- Runner stdout summary: `ok=true`, `aborted=false`, `wrote=true`, `output_path=C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02f\result_populations\RP-7520.result_population.json`
- Runner stderr: empty

The scratch write is a temp-directory write used for validation. It is not a canonical result-population write.

## Data provenance

- Data catalog ref: `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
- Data slice identity: `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- Row count: `220128`
- Time range: `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`
- D3 validation report SHA256: `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`
- Execution provenance class: `canonical_real_data`
- Denominator: `10`
- Actual variant rows: `10`
- Outcome count sum: `10`
- Outcome category counts: `10 successful / 0 failed / 0 errored / 0 invalid / 0 excluded / 0 filtered / 0 data_unavailable / 0 not_attempted / 0 aborted`

The data catalog ref and data slice identity match `RP-6688` lineage.

## Sizing metadata

The runner-generated scratch artifact contains top-level `sizing_metadata` with:

- `sizing_mode=dynamic_equity_target_leverage`
- `target_leverage=1.0`
- `sizing_equity_basis=realized_available_equity_at_entry`
- `entry_reference_price_basis=next_bar_open_pre_fee_slippage`

## Identity-hash chain

- Input identity hash: `sha256:761f4af20320a244b0ff966eca17f3cc3a47bc79a5672cf2b40ee183ab9c05de`
- Result population identity hash: `sha256:698f02c6239a5d2221ababeab62850403f71d9cf6f36279b3b8dcdc05fa7403c`
- `input_identity_hash.hash_scope` includes `sizing_metadata`: yes
- `result_population_identity_hash.hash_scope` includes `sizing_metadata`: yes

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
sizing_metadata
committed_denominator_snapshot
variant_result_rows
outcome_category_counts
append_only_ledger.creation_event_ref
validation_summary.validator_identity
```

Focused tests also prove that changing dynamic `target_leverage` changes both identity hash values, and repeated identical dynamic runs keep identical identity hashes and rows.

## Per-variant canonical-path population

`max_drawdown` maps to the artifact field `metrics.drawdown`. The liquidation / zero-equity flag is `return_pct == -1.0` or `metrics.drawdown == 1.0`.

| variant_id | sma_lookback_bars | band_threshold | return_pct | max_drawdown | win_rate | sharpe | trade_count | liquidation / zero-equity flag | comparison_to_02e_within_tolerance |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| VAR-000001 | 20 | 0.0025 | -0.999998194 | 0.999998257 | 0.689014041 | -3.169618686 | 12962 | false | true |
| VAR-000002 | 20 | 0.005 | -0.999714064 | 0.999732148 | 0.656729450 | -1.975828408 | 8017 | false | true |
| VAR-000003 | 20 | 0.01 | -0.975631111 | 0.977582598 | 0.616122343 | -0.906815290 | 3858 | false | true |
| VAR-000004 | 20 | 0.015 | -0.827978227 | 0.904671311 | 0.595734817 | -0.389424617 | 2157 | false | true |
| VAR-000005 | 20 | 0.02 | -0.616500646 | 0.726300399 | 0.592409241 | -0.174432132 | 1212 | false | true |
| VAR-000006 | 50 | 0.0025 | -0.999946644 | 0.999948377 | 0.740572968 | -2.168159878 | 8168 | false | true |
| VAR-000007 | 50 | 0.005 | -0.999062501 | 0.999127085 | 0.698291530 | -1.506881096 | 5502 | false | true |
| VAR-000008 | 50 | 0.01 | -0.987385031 | 0.988748687 | 0.653882726 | -0.938321186 | 3155 | false | true |
| VAR-000009 | 50 | 0.015 | -0.913642819 | 0.919707612 | 0.623857624 | -0.471047573 | 2079 | false | true |
| VAR-000010 | 50 | 0.02 | -0.802027796 | 0.839137615 | 0.611350575 | -0.281987775 | 1392 | false | true |

## Comparison to 02e scratch

Tolerance: absolute tolerance `<= 1e-9` for floating metrics and exact equality for `trade_count`.

All 10 variants match the 02e scratch reference rows within tolerance. There are no mismatch rows.

## Non-degeneracy check

- Count variants with `return_pct == -1.0`: `0`
- Count variants with `max_drawdown == 1.0`: `0`
- Count variants with liquidation / zero-equity terminal flag: `0`
- Whether all 10 are uniformly -100% / full liquidation: no

Uniform liquidation artifact reproduced: NO

This is non-degeneracy evidence only. It is not edge, profitability, ranking, readiness, promotion, candidate-registration, or trading evidence.

## Validation

- `python -m pytest tests/test_offline_research_runner.py -q`: pass, `73 passed`, 2 existing timestamp parsing warnings.
- Scratch artifact validation: pass with `python -m tools.registry.validate_result_populations --result-populations-dir C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02f\result_populations --strategy-specs-dir research\strategy_specs --variant-manifests-dir research\variant_manifests --sweep-plans-dir research\sweep_plans`.

Additional final validation is summarized in `docs/status_entries/WP-REALISM-SIZING-02f.md`.

## No-canonical-write proof

The runner wrote only to `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02f\result_populations`. The canonical `research/result_populations` path is not used as an output directory.

Final git checks for `research/result_populations` are recorded in the status fragment and PR body.

## Limitations

- The catalog-referenced normalized CSV path recorded by D4 was not locally present in the root checkout or isolated worktree.
- The run used the existing local 02e full-D4 scratch CSV as a fallback input while passing the committed D4 catalog slice and D2 import report to the runner. The generated artifact records the same D4 catalog ref and slice identity as `RP-6688`.
- The scratch artifact is local temp evidence and is not committed.
- This package prepares the runner path only; it does not create or authorize a canonical dynamic-sizing result population.

## What this package does not authorize

This package does not authorize a canonical dynamic-sizing result-population write, result-population mutation, lib edit, schema/validator edit, Strategy Spec mutation, variant manifest mutation, sweep plan mutation, data acquisition, candidate registration, ranking, readiness, promotion, paper/live/runtime behavior, OMS/risk behavior, broker/exchange behavior, or protected-path behavior.

## Next authority

This package does not authorize a canonical dynamic-sizing result population. Main review and Karl gate are required before any canonical write.
