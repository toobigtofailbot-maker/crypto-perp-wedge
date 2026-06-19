# EXT-SIMULATOR-PILOT-01 Scratch Simulator Pilot Report

- NON-CANONICAL EXTERNAL SIMULATOR PILOT OUTPUT
- NOT A RESULT POPULATION
- NOT STRATEGY / VM / SWEEP AUTHORITY
- NOT CANONICAL RUNNER AUTHORITY
- NOT BACKTEST REPLACEMENT AUTHORITY
- NOT PAPER / LIVE / RUNTIME AUTHORITY
- NOT OMS / RISK / RECONCILIATION AUTHORITY
- CANONICAL-EVIDENCE USE REQUIRES SEPARATE MAPPING, VALIDATION, DETERMINISM, AUDITABILITY, PROVENANCE, AND MAIN/KARL APPROVAL

Recommendation: `BLOCKED`
Broader taxonomy: `blocked`
Output checksum: `sha256:6f3eff7bfb26ca57c792813a56e4847b3011b3161b371836be300c8f15c3b4e0`

## Fixture

- Result Population: `RP-2592`
- Strategy Spec: `STRAT-SPEC-0004`
- Variant Manifest: `VM-0004`
- Sweep Plan: `SWEEP-PLAN-0004`
- Data slice: `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- Variants: `8`

## NautilusTrader Probe

- Metadata available: `True`
- Version: `1.228.0`
- Isolated environment used: `True`
- Install command: `python -m pip install nautilus_trader`
- Backtest API importable: `True`
- Import error: `None`
- Source inspection: `performed`
- Offline backtest executed: `False`

## Reconciliation

- Variants attempted: `0`
- Variants expressible: `0`
- Trade count comparison: `not_performed`
- Final equity / return comparison: `not_performed`
- Integration burden: `unmeasured_until_safe_offline_backtest_mapping_is_implemented`

## Determinism

- Repeated runs: `False`
- Byte-identical: `False`
- Normalized-identical: `False`
- Result: `not_established`

## Boundary

- candidate_evidence_authority_created: `False`
- canonical_result_population_write: `False`
- external_dependency_added_to_repo: `False`
- machine_local_absolute_paths_in_outputs: `False`
- oms_risk_reconciliation_changed: `False`
- promotion_readiness_authority_created: `False`
- runner_backtester_changed: `False`
- runtime_paper_live_touched: `False`
- screen_gate_authority_created: `False`
- strategy_spec_mutation: `False`
- sweep_plan_mutation: `False`
- variant_manifest_mutation: `False`

## Rationale

NautilusTrader installed in isolation and source inspection found relevant simulator concepts, but no offline backtest produced simulator metrics in this package, so offline-only execution, reconciliation, and determinism are not established.
