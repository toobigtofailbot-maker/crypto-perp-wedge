# Canonical Dynamic-Sizing Result Population

## Status / authority boundary

This canonical result population is evidence only. It does not rank variants, register candidates, mark readiness, promote a strategy, authorize paper/live/runtime behavior, or create trading authority.

`WP-REALISM-SIZING-03a` commits append-only canonical result-population evidence for `STRAT-SPEC-0002` / `VM-0002` / `SWEEP-PLAN-0002` using `dynamic_equity_target_leverage` at `target_leverage=1.0`. It creates `RP-7520` and does not mutate any prior result population.

## Input lineage

- Strategy Spec: `STRAT-SPEC-0002`
- Variant Manifest: `VM-0002`
- Sweep Plan: `SWEEP-PLAN-0002`
- Market/data: BTCUSDT Binance USDT-M perpetual 15m real D4 slice
- Data catalog ref: `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
- D4 slice identity: `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- D3 validation-report SHA256: `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`
- Normalized CSV path consumed locally by the runner: `data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`
- Normalized CSV SHA256: `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`
- Row count: `220128`
- Time range: `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`
- Gap count / missing bars: `0` / `0`
- Duplicate group / duplicate row count: `0` / `0`

## Prior scratch-run evidence

`WP-REALISM-SIZING-02f` proved that the canonical runner path emits top-level `sizing_metadata`, includes it in both identity-hash scopes, and produces `RP-7520` in scratch output with the expected hashes and per-variant rows.

`WP-REALISM-SIZING-02g` materialized the documented D4A normalized CSV locally from existing local source, reran the same dynamic 1x runner path against that file, and confirmed exact identity-hash and per-variant agreement with 02f.

`WP-DATA-LINEAGE-DIAG-01` diagnosed the validation-report SHA mismatch as line-ending byte drift. `WP-DATA-LINEAGE-FIX-01` restored the validation-report bytes to the catalog-attested SHA `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c` while preserving the D4 slice identity.

## Result population identity

- Result population: `RP-7520`
- Path: `research/result_populations/RP-7520.result_population.json`
- Provenance class: `canonical_real_data`
- Runner path: `tools.research_runner.run_offline_sweep`
- Runner temp output: `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_03a\result_populations\RP-7520.result_population.json`
- Staged/committed artifact SHA256 after repo LF normalization: `1df066eeb15957bb0a0825b180bcded8ee971a6e9834a30fe93ac7b70810bd36`
- Input identity hash: `sha256:761f4af20320a244b0ff966eca17f3cc3a47bc79a5672cf2b40ee183ab9c05de`
- Result population identity hash: `sha256:698f02c6239a5d2221ababeab62850403f71d9cf6f36279b3b8dcdc05fa7403c`
- `input_identity_hash.hash_scope` includes `sizing_metadata`: yes
- `result_population_identity_hash.hash_scope` includes `sizing_metadata`: yes

## Sizing metadata

```json
{
  "entry_reference_price_basis": "next_bar_open_pre_fee_slippage",
  "sizing_equity_basis": "realized_available_equity_at_entry",
  "sizing_mode": "dynamic_equity_target_leverage",
  "target_leverage": 1.0
}
```

## Per-variant population

Rows are in the pre-registered variant order. `max_drawdown` maps to artifact field `metrics.drawdown`.

| variant_id | sma_lookback_bars | band_threshold | return_pct | max_drawdown | win_rate | sharpe | trade_count |
|---|---:|---:|---:|---:|---:|---:|---:|
| VAR-000001 | 20 | 0.0025 | -0.999998194341 | 0.999998256543 | 0.689014041043 | -3.169618686010 | 12962 |
| VAR-000002 | 20 | 0.005 | -0.999714064365 | 0.999732147789 | 0.656729449919 | -1.975828408143 | 8017 |
| VAR-000003 | 20 | 0.01 | -0.975631111181 | 0.977582598332 | 0.616122343183 | -0.906815289570 | 3858 |
| VAR-000004 | 20 | 0.015 | -0.827978227395 | 0.904671311111 | 0.595734816875 | -0.389424616606 | 2157 |
| VAR-000005 | 20 | 0.02 | -0.616500646241 | 0.726300398546 | 0.592409240924 | -0.174432132340 | 1212 |
| VAR-000006 | 50 | 0.0025 | -0.999946644325 | 0.999948376898 | 0.740572967679 | -2.168159878161 | 8168 |
| VAR-000007 | 50 | 0.005 | -0.999062500791 | 0.999127085015 | 0.698291530353 | -1.506881096294 | 5502 |
| VAR-000008 | 50 | 0.01 | -0.987385030964 | 0.988748687069 | 0.653882725832 | -0.938321185895 | 3155 |
| VAR-000009 | 50 | 0.015 | -0.913642819333 | 0.919707612242 | 0.623857623858 | -0.471047573412 | 2079 |
| VAR-000010 | 50 | 0.02 | -0.802027795512 | 0.839137615219 | 0.611350574713 | -0.281987774993 | 1392 |

Comparison to 02f/02g scratch references: all ten rows match within absolute tolerance `<= 1e-9` for floating metrics and exact equality for `trade_count`.

## Non-degeneracy check

- `return_pct == -1.0` count: `0`
- `max_drawdown == 1.0` count: `0`
- Liquidation / zero-equity terminal flag count: `0`
- Uniform liquidation artifact reproduced: NO

This is non-degeneracy evidence only. It is not edge, profitability, ranking, readiness, promotion, candidate-registration, or trading evidence.

## Validation

- `python -m tools.registry.validate_result_populations`: pass.
- `python -m tools.research_query.run --list-views`: pass, `118` views listed.
- All discovered `v_integrity_*` views: pass, `55` views returned zero rows.
- Focused identity/content checks: pass for `RP-7520` existence, result-population ID, denominator, row count, outcome counts, both required identity hashes, sizing metadata scope inclusion, D4 slice identity, D3 validation-report SHA, per-variant tolerance, and non-degeneracy counts.

Final diff-scope, whitespace, no-forbidden-mutation, rebase, and PR mergeability checks are recorded in `docs/status_entries/WP-REALISM-SIZING-03a.md`.

## Boundary / append-only proof

`RP-7520` is a new result-population artifact. `RP-2134`, `RP-4492`, and `RP-6688` are unchanged.

This package changes no prior result population, D4 catalog object, validation-report file, data content, Strategy Spec, variant manifest, sweep plan, schema, validator, runner, code, test, candidate registry, dashboard implementation, generated dashboard output, runtime, paper/live, OMS/risk, broker/exchange, or protected path.

## Interpretation boundary

This result records the honest dynamic-sizing population for the specific `STRAT-SPEC-0002` / `VM-0002` / `SWEEP-PLAN-0002` dynamic 1x interpretation over the cleaned BTCUSDT 15m D4 lineage.

It supersedes the misleading fixed-size liquidation artifact for this specific dynamic-sizing interpretation. It does not mutate or delete `RP-6688`. It does not prove profitability. It does not generalize to mean-reversion broadly.

## Next authority

No next work package is automatically authorized by this canonical write. Candidate lifecycle, dashboard refresh, post-canonical checkpoint, paper/live/runtime, and trading behavior remain separate future authority surfaces.
