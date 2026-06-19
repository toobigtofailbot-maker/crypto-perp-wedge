# EXT-INTEG-VECTORBT-TRIAGE-SIDECAR-01 Vectorbt Triage Report

- NON-CANONICAL VECTORBT TRIAGE SIDECAR OUTPUT
- NOT A RESULT POPULATION
- NOT CANONICAL EVIDENCE
- NOT CANDIDATE EVIDENCE
- NOT RANKING / SCREEN-GATE / READINESS AUTHORITY
- NOT STRATEGY / VM / SWEEP AUTHORITY
- NOT RUNNER / BACKTESTER AUTHORITY
- NOT PAPER / LIVE / RUNTIME AUTHORITY
- CANONICAL RUNNER CONFIRMATION REQUIRED FOR EVERY FINALIST

Execution status: `COMPLETED_NON_CANONICAL_TRIAGE`
Decision label: `ADOPT_AS_NON_CANONICAL_TRIAGE_SIDECAR`
Output checksum: `sha256:add979d96a6d95380380e4fd84e13f72847a66135a3af706dac3cca9566a0fd4`
Vectorbt: `available` / `1.0.0`

## Fixture

- Strategy Spec: `STRAT-SPEC-0004`
- Variant Manifest: `VM-0004`
- Sweep Plan: `SWEEP-PLAN-0004`
- Data slice: `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- Selected variants: `8`
- Processed variants: `8`
- Bound: `8` (hard maximum `10000`)

## Triage Metrics

| variant | trades | return | drawdown | sharpe |
|---|---:|---:|---:|---:|
| VAR-000001 | 1274 | -0.42965351678663827 | 0.7122088596486857 | -0.01998278548061986 |
| VAR-000002 | 1301 | 0.1698060761526125 | 0.6287567514053404 | 0.2666668993889724 |
| VAR-000003 | 819 | 0.48346440355468984 | 0.6923569649839074 | 0.3581293390955653 |
| VAR-000004 | 801 | 0.6440049269638471 | 0.5653069539695565 | 0.39784871668079086 |
| VAR-000005 | 1026 | 0.8107913450250606 | 0.6572388928223688 | 0.43545109189135633 |
| VAR-000006 | 1043 | 0.954179924080049 | 0.6142091869570009 | 0.4644132881102334 |
| VAR-000007 | 602 | -0.17920199069795653 | 0.675603886968185 | 0.13423647627272225 |
| VAR-000008 | 578 | -0.05650815332907623 | 0.5701754175739372 | 0.17976192303881272 |

## Limitations and Boundary

- vectorized fills and portfolio accounting are not canonical runner semantics
- funding cashflows are not modeled
- repo-equivalent liquidation and zero-equity behavior are not modeled
- metrics are triage diagnostics only and are not finalist confirmation
- Rows are ordered by variant id, not by a readiness or promotion score.
- Every finalist requires later confirmation through the repo-owned canonical runner/evidence path.
- This sidecar writes no canonical Result Population, Strategy Spec, Variant Manifest, or Sweep Plan.
