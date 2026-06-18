# EXT-CCXT-DATA-INGESTION-PILOT-01 Validation Report

- NON-CANONICAL EXTERNAL PUBLIC-DATA PILOT OUTPUT
- NOT A RESULT POPULATION
- NOT STRATEGY / VM / SWEEP AUTHORITY
- NOT BACKTEST COST-MODEL AUTHORITY
- NOT PAPER / LIVE / RUNTIME AUTHORITY
- FUNDING-INTO-BACKTEST REQUIRES A SEPARATE GATED WP

Status: `PASS`
Public method: `ccxt.binanceusdm.fapiPublicGetFundingRate`
Credentials used: `False`

## Coverage

- Target start UTC: `2020-01-01T00:00:00Z`
- Target end UTC: `2026-04-11T23:45:00Z`
- Observed start UTC: `2020-01-01T00:00:00Z`
- Observed end UTC: `2026-04-11T16:00:00Z`
- Expected events: `6879`
- Observed events: `6879`
- Missing events: `0`
- Duplicate groups: `0`

## Boundary

- No Result Population, Strategy Spec, Variant Manifest, Sweep Plan, backtester, runner, runtime, paper, live, OMS, risk, or execution path is changed.
- Funding integration into backtests remains a separate gated work package.
