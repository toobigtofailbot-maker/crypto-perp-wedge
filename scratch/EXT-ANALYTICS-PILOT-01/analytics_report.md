# EXT-ANALYTICS-PILOT-01 Scratch Analytics Report

- NON-CANONICAL EXTERNAL ANALYTICS PILOT OUTPUT
- NOT A RESULT POPULATION
- NOT SCREEN-GATE AUTHORITY
- NOT STRATEGY / VM / SWEEP AUTHORITY
- NOT CANDIDATE EVIDENCE
- NOT PAPER / LIVE / RUNTIME AUTHORITY

Recommendation: `FORMULA_ADAPT_ONLY`
Dependency mode: `formula_adapter_only_no_repo_dependency_change`
External engine available: `False`

## Fixture

- Result Population: `RP-7134`
- Strategy: `STRAT-SPEC-0003`
- VM: `VM-0003`
- Sweep: `SWEEP-PLAN-0003`
- Data slice: `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- Rows used: `8`

## Metric Comparison

| metric | formula value | external value | delta | status |
|---|---:|---:|---:|---|
| cumulative_return | -1.0 | None | None | external_unavailable |
| max_drawdown | 1.0 | None | None | external_unavailable |
| tail_ratio | 0.9904383695637042 | None | None | external_unavailable |
| annualized_sharpe | None | None | None | unsupported |
| sortino | None | None | None | unsupported |
| calmar | None | None | None | unsupported |

## Unsupported Metrics

- Annualized Sharpe, Sortino, and Calmar are not claimed for this fixture.
- The committed RP fixture exposes per-variant result rows, not a chronological return series.
- No canonical Result Population, Strategy Spec, Variant Manifest, Sweep Plan, or runtime artifact is written.
