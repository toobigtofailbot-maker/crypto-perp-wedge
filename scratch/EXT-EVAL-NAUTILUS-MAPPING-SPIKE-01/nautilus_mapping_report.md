# EXT-EVAL-NAUTILUS-MAPPING-SPIKE-01 Nautilus Mapping Report

- NON-CANONICAL NAUTILUS MAPPING SPIKE
- NOT CANONICAL EVIDENCE
- NOT RUNNER REPLACEMENT
- NOT PAPER/LIVE/RUNTIME AUTHORITY
- CANONICAL USE REQUIRES SEPARATE MAPPING, VALIDATION, DETERMINISM, AUDITABILITY, PROVENANCE, AND MAIN APPROVAL

Decision label: `VIABLE_CANONICAL_GRADE_SIMULATOR_CANDIDATE`
Report checksum: `4c3d84f639c4da9e20c064cc5e6b6f15cbe4110693d23aa6e48f11c1739772a5`

## Fixture

- RP: `RP-2592`
- Strategy / VM / sweep: `STRAT-SPEC-0004` / `VM-0004` / `SWEEP-PLAN-0004`
- Data slice: `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- Rows: `220128`
- Variants attempted / expressible: `8` / `8`

## Determinism

- Repeated runs: `True`
- Normalized identical: `True`
- Run 1 checksum: `d5a42698d41d45b6f138a29b348321805636f09b4016bd9801525426b00c6ce5`
- Run 2 checksum: `d5a42698d41d45b6f138a29b348321805636f09b4016bd9801525426b00c6ce5`

## Reconciliation

| Variant | RP trades | Nautilus trades | Return delta |
|---|---:|---:|---:|
| VAR-000001 | 1273 | 1273 | -0.001876287713 |
| VAR-000002 | 1300 | 1300 | -0.004382623128 |
| VAR-000003 | 818 | 818 | -0.000959972147 |
| VAR-000004 | 800 | 800 | -0.000740587548 |
| VAR-000005 | 1025 | 1025 | -0.000798940748 |
| VAR-000006 | 1042 | 1042 | -0.001072210892 |
| VAR-000007 | 601 | 601 | 0.000100475525 |
| VAR-000008 | 577 | 577 | 0.000172206121 |

## Unsupported Semantics

- Nautilus 1.221.0 does not expose the RP zero-equity liquidation rule through this low-level bounded mapping; no RP-2592 variant liquidated.
- Continuous canonical quantities are rounded to 8 decimal places by the synthetic offline instrument.

## Boundary

- canonical_artifacts_mutated: `False`
- dependency_files_mutated: `False`
- external_dependency_isolated: `True`
- private_apis_credentials_orders_used: `False`
- promotion_readiness_screen_gate_authority_created: `False`
- runner_backtester_mutated: `False`
- runtime_paper_live_touched: `False`
