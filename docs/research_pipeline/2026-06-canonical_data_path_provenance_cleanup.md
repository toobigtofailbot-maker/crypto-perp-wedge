# Canonical Data-Path Provenance Cleanup

## Status / authority boundary

This is data-path readiness evidence. It is not a canonical result population, does not rank variants, does not register candidates, does not mark readiness, does not promote strategies, and does not authorize paper/live/runtime behavior.

`WP-REALISM-SIZING-02g` proves that the STRAT-SPEC-0002 dynamic 1x runner path can consume the documented D4A normalized CSV at the catalog-referenced local path. The package writes only a local scratch artifact outside the repo and commits docs/status evidence only.

## Source issue

`WP-REALISM-SIZING-02f` completed the full dynamic 1x canonical-runner-path scratch run, but the catalog-referenced normalized D4 CSV was locally absent. That run used the existing 02e fallback CSV while passing the committed D4 catalog slice and D2 import report to the runner.

02g closes that data-path gap by materializing the documented normalized CSV locally and rerunning the same dynamic 1x runner path over that file.

## Materialization method

- Materialized CSV path: `C:\GitHub\crypto-perp-wedge-realism-sizing-02g\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`
- Existing local source path: `C:\GitHub\crypto-perp-wedge-d4a\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_source_from_repo_catalog_parquet.csv`
- Source SHA256: `343b639e35ce79824d26bddf6d70af2641c9d76003301e303f83cdf61d4feab4`
- Source lineage: D4A-documented D2-compatible source CSV generated offline from the existing repo-cataloged local 15m Parquet `data/processed/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`, whose repo catalog SHA256 is `3fd05b841210962147a92bd77167ccefce57f6eb812cb55565d6f6cbb5154c31`.
- Materialization command:

```powershell
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.data.import_binance_usdtm_15m --input C:\GitHub\crypto-perp-wedge-d4a\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_source_from_repo_catalog_parquet.csv --output C:\GitHub\crypto-perp-wedge-realism-sizing-02g\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv --report C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02g\d2_import_report_from_existing_source.json
```

No external/raw data acquisition occurred.

## Materialized CSV identity

- Raw CSV SHA256: `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`
- D2 normalized data slice identity: `binance_usdtm:BTCUSDT:ohlcv:15m:2020-01-01T00:00:00Z:2026-04-11T23:45:00Z:wp-d2-offline-binance-usdtm-15m-v1:sha256:c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`
- Row count: `220128`
- Expected row count: `220128`
- Timestamp range: `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`
- Duplicate timestamp count: `0`
- Gap count / missing bars: `0` / `0`
- Exact spacing check: one unique delta, `0 days 00:15:00`

The committed D4 catalog slice identity is:

```text
binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664
```

The materialized raw CSV SHA256 is not the D4 slice identity hash. The D4 slice identity is derived from the committed catalog identity-input object, including raw source SHA, normalized SHA, validation status/hash, range, gap facts, duplicate facts, symbol, venue, stream, timeframe, and version fields. Recomputing SHA256 over the committed catalog `slice_identity.identity_inputs` produced `3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`.

## Relationship to 02e/02f fallback CSV

- Fallback path: `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02e\btc_usdt_15m_full_d4_lineage_scratch.csv`
- Fallback SHA256: `ec69b3a5ba3a00b0f2937c9c7b3aba04c4aaecd88762b699092c5b26656cc014`
- Fallback columns: `open_time_ms`, `open`, `high`, `low`, `close`, `volume`
- Relationship: content-equivalent under the runner's timestamp/OHLCV consumption semantics; not identical file bytes.

Comparison normalized both files to timestamp plus `open/high/low/close/volume` over 220,128 rows. The timestamp range matched exactly and all runner-consumed OHLCV values matched exactly.

## Canonical-path dynamic dry-run

- Strategy Spec: `STRAT-SPEC-0002`
- Variant Manifest: `VM-0002`
- Sweep Plan: `SWEEP-PLAN-0002`
- Sizing mode: `dynamic_equity_target_leverage`
- Target leverage: `1.0`
- Deterministic seed: `190`
- Runner path: `tools.research_runner.run_offline_sweep`
- Input CSV: materialized documented D4A normalized CSV path above
- D4 catalog slice: `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json`
- D2 import report: `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.import_report.json`
- Scratch output directory: `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02g\result_populations`
- Scratch artifact: `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02g\result_populations\RP-7520.result_population.json`
- Runtime: `01:23:43.6720158`

The runner wrote only to the temp scratch output directory. It did not use `research/result_populations` as an output directory.

## Data provenance

- Data catalog ref: `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
- Data slice identity: `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- Provenance class: `canonical_real_data`
- Denominator: `10`
- Actual variant rows: `10`
- Outcome count sum: `10`
- Outcome counts: `10 successful / 0 failed / 0 errored / 0 invalid / 0 excluded / 0 filtered / 0 data_unavailable / 0 not_attempted / 0 aborted`

## Identity-hash comparison to 02f

| Hash | 02g runner output | 02f expected | Exact match |
|---|---|---|---|
| Input identity hash | `sha256:761f4af20320a244b0ff966eca17f3cc3a47bc79a5672cf2b40ee183ab9c05de` | `sha256:761f4af20320a244b0ff966eca17f3cc3a47bc79a5672cf2b40ee183ab9c05de` | YES |
| Result population identity hash | `sha256:698f02c6239a5d2221ababeab62850403f71d9cf6f36279b3b8dcdc05fa7403c` | `sha256:698f02c6239a5d2221ababeab62850403f71d9cf6f36279b3b8dcdc05fa7403c` | YES |

The runner-generated scratch artifact contains top-level `sizing_metadata`, and both identity-hash scopes include `sizing_metadata`.

## Per-variant result comparison to 02f

Tolerance: absolute `<= 1e-9` for floating metrics and exact equality for `trade_count`.

| variant_id | return_pct | max_drawdown | win_rate | sharpe | trade_count | within tolerance |
|---|---:|---:|---:|---:|---:|---|
| VAR-000001 | -0.999998194 | 0.999998257 | 0.689014041 | -3.169618686 | 12962 | YES |
| VAR-000002 | -0.999714064 | 0.999732148 | 0.656729450 | -1.975828408 | 8017 | YES |
| VAR-000003 | -0.975631111 | 0.977582598 | 0.616122343 | -0.906815290 | 3858 | YES |
| VAR-000004 | -0.827978227 | 0.904671311 | 0.595734817 | -0.389424617 | 2157 | YES |
| VAR-000005 | -0.616500646 | 0.726300399 | 0.592409241 | -0.174432132 | 1212 | YES |
| VAR-000006 | -0.999946644 | 0.999948377 | 0.740572968 | -2.168159878 | 8168 | YES |
| VAR-000007 | -0.999062501 | 0.999127085 | 0.698291530 | -1.506881096 | 5502 | YES |
| VAR-000008 | -0.987385031 | 0.988748687 | 0.653882726 | -0.938321186 | 3155 | YES |
| VAR-000009 | -0.913642819 | 0.919707612 | 0.623857624 | -0.471047573 | 2079 | YES |
| VAR-000010 | -0.802027796 | 0.839137615 | 0.611350575 | -0.281987775 | 1392 | YES |

No mismatch rows were found.

## Non-degeneracy check

- Count variants with `return_pct == -1.0`: `0`
- Count variants with `max_drawdown == 1.0`: `0`
- Count variants with liquidation / zero-equity terminal flag: `0`
- Whether all 10 are uniformly -100% / full liquidation: no

Uniform liquidation artifact reproduced: NO

This is non-degeneracy evidence only. It is not edge, profitability, ranking, readiness, promotion, candidate-registration, or trading evidence.

## Validation

- D2 materialization command: pass; normalized SHA `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`.
- D3 validation of materialized CSV: pass; row/range/gap/duplicate/spacing facts above.
- Committed catalog identity-input recomputation: pass; hash `3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`.
- Fallback comparison: pass; runner-consumed timestamp/OHLCV content matched exactly.
- Full dynamic 1x canonical-runner-path scratch run: pass; artifact `RP-7520.result_population.json`, runtime `01:23:43.6720158`.
- Scratch artifact validation: pass with `python -m tools.registry.validate_result_populations --result-populations-dir C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02g\result_populations --strategy-specs-dir research\strategy_specs --variant-manifests-dir research\variant_manifests --sweep-plans-dir research\sweep_plans`.

Additional final validation is summarized in `docs/status_entries/WP-REALISM-SIZING-02g.md`.

## No-canonical-write proof

The dynamic runner wrote only to `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02g\result_populations`.

The final package checks include:

```powershell
git status --short research/result_populations
git diff -- research/result_populations
git diff -- lib tools/research_runner/run_offline_sweep.py research/schemas tools/registry tests research/strategy_specs research/variant_manifests research/sweep_plans
git status --short lib tools/research_runner/run_offline_sweep.py research/schemas tools/registry tests research/strategy_specs research/variant_manifests research/sweep_plans
```

These checks returned no result-population, code, schema, validator, test, Strategy Spec, variant manifest, or sweep-plan changes.

## Limitations

- The materialized CSV is local and gitignored; it is not committed.
- The scratch result artifact is local temp evidence and is not committed.
- The current committed D4 catalog entry records validation-report SHA `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`, while the current committed validation-report file bytes hash to `51ceb94dc43c4e63f704bde86585f94bb800c2da21aa516f492d897a5bfc2a46`. The committed catalog identity-input object still recomputes to the recorded D4 slice identity `3daace53...`, and the runner consumes the committed catalog identity/facts rather than regenerating the catalog entry. This package records the mismatch as lineage hygiene debt and does not mutate D4 artifacts.
- This package does not create or authorize a canonical dynamic-sizing result population.

## What this package does not authorize

This package does not authorize a canonical dynamic-sizing result-population write, result-population mutation, external/raw data acquisition, lib edit, runner edit, schema/validator edit, Strategy Spec mutation, variant manifest mutation, sweep plan mutation, candidate registration, ranking, readiness, promotion, paper/live/runtime behavior, OMS/risk behavior, broker/exchange behavior, or protected-path behavior.

## Next authority

This package does not authorize a canonical dynamic-sizing result population. Main review and Karl gate are required before any canonical write.
