# RP-6688 Both-Direction SMA-Band Descriptive Checkpoint

## Status / authority boundary

This checkpoint is descriptive evidence only. It does not rank variants for
deployment, select a winner, approve a strategy, register a candidate, claim
profitability, authorize paper/live trading, or modify runtime behavior.

It consumes the committed result population `RP-6688` read-only and records
population-level facts from that artifact. It creates no Strategy Spec, Variant
Manifest, Sweep Plan, result population, derived robustness report, dashboard
data, candidate registry entry, paper/live path, runtime path, OMS/risk path, or
protected-path behavior.

## Source artifact

- Result population: `RP-6688`
- Path:
  `research/result_populations/RP-6688.result_population.json`
- Schema version: `v1`
- Status: `generated`
- Creation event: `RP-6688-EVENT-001`
- Runner recorded in artifact: `tools.research_runner.run_offline_sweep`
- Execution mode recorded in artifact: `offline_research`
- Execution provenance class recorded in artifact:
  `canonical_real_data`

## Parent artifacts and strategy design

Parent lineage recorded in `RP-6688`:

- Strategy Spec: `STRAT-SPEC-0002`
- Variant Manifest: `VM-0002`
- Sweep Plan: `SWEEP-PLAN-0002`

The parent design is the frozen both-direction BTCUSDT 15m OHLCV symmetric
SMA-band mean-reversion population. The manifest commits ten variants from the
manual grid:

- `sma_lookback_bars in {20, 50}`
- `band_threshold in {0.0025, 0.005, 0.01, 0.015, 0.02}`

The Strategy Spec uses explicit side-labeled long and short entry groups,
explicit side-labeled long and short exit groups, parameter-bound SMA lookback,
and symmetric plus/minus band operands. This checkpoint does not modify those
parents or infer any execution status from them.

## Denominator and outcome accounting

`RP-6688` records complete-population denominator accounting:

- committed denominator = `10`
- result rows = `10`
- outcome counts sum = `10`
- all variants retained
- no successful-only denominator
- no executed-only denominator
- no winner-only retention

Outcome category counts recorded in the source artifact:

| outcome_category | count |
|---|---:|
| successful | 10 |
| failed | 0 |
| errored | 0 |
| invalid | 0 |
| excluded | 0 |
| filtered | 0 |
| data_unavailable | 0 |
| not_attempted | 0 |
| aborted | 0 |

## Important clarification: "successful" does not mean profitable

`successful = 10` means all 10 variants ran to completion and produced result
rows. It does not mean all 10 variants were profitable, validated, ready, or
good.

In this population, each of the ten completed rows records
`return_pct = -1.0` and `pnl = -10000.0` under the recorded offline model.
Completion status is therefore separate from outcome quality, strategy
validity, or any future decision.

## Data provenance

`RP-6688` records BTCUSDT 15m OHLCV D4 catalog/slice provenance:

- Data catalog ref:
  `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
- Data slice identity:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- Data stream: `ohlcv`
- Timeframe: `15m`
- Row count / expected row count: `220128 / 220128`
- Time range: `2020-01-01T00:00:00Z` through
  `2026-04-11T23:45:00Z`
- Gap facts: `gap_count=0`, `missing_bar_count=0`, `gaps=[]`
- Duplicate facts: `duplicate_group_count=0`, `duplicate_row_count=0`,
  `duplicates=[]`
- D3 validation report SHA256:
  `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`
- D2 import report SHA256:
  `543c944f727b2b9a7ad06742946ecefc91aa8b94723f46509e4041f622ef57ad`
- D4 catalog artifact SHA256:
  `f7b98c4d7759b6ba0c9bf8559bcea5e3311d3abe877930da254aeca96f53105a`
- Raw source SHA256:
  `343b639e35ce79824d26bddf6d70af2641c9d76003301e303f83cdf61d4feab4`
- Normalized SHA256:
  `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`

The artifact records offline-only execution context with no broker, exchange,
paper/live, runtime, or protected-path contact.

## Identity hashes

Identity hashes recorded in `RP-6688`:

| identity field | hash |
|---|---|
| `input_identity_hash` | `sha256:ea9ea760ef7a5d30956a4573fc4ca0c39b43a533803667370219f5e3f7ffe386` |
| `result_population_identity_hash` | `sha256:7ee08cc1f30e26c318b39d571b90d25406072329ce4a67bd7c94ec35f98fcdbc` |
| `strategy_spec_hash` | `sha256:aa2d05134e788b6b34e2ff03af8d111563dece743e943e134c0b8e46bee429e3` |
| `variant_manifest_hash` | `sha256:27d89f01b3ec5a7cbb87ad224481f6328727737aa292b7fa332d3474b6bda5bc` |
| `sweep_plan_identity_hash` | `sha256:93ed973044e52e530ca66935744fbe7fc455fcb1473ef770983d7e4107306ed6` |

The source artifact states that administrative audit metadata is excluded from
the scientific input and result-population identity hashes.

## Backtest-realism assumptions

`RP-6688.backtest_assumption_summary` records these assumption values:

| assumption field | recorded value |
|---|---|
| `fee_side_assumption` | `taker_entry_taker_exit` |
| `slippage_model` | `fixed_bps` |
| `fill_mode` | `complete` |
| `funding_notional` | `entry_price` |
| `liquidation_mode` | `zero_equity` |
| `mark_price_source` | `close` |
| `bar_path_assumption` | `next_open_close_mark` |
| `exchange_constraint_disclosure` | `True` |
| `order_size_assumption` | `future offline runner assumption only; no execution here` |
| `liquidity_capacity_assumption` | `null` |
| `maintenance_margin_assumption` | `null` |

These are recorded assumptions only. They do not represent paper/live
execution readiness, liquidity realism, market-impact analysis, or an execution
model upgrade.

## Population-level outcome description

The table below includes all 10 rows in pre-registered variant ID order. It is
not sorted by performance. No row is emphasized, selected, or described as a
preferred parameter set.

| variant_id | sma_lookback_bars | band_threshold | outcome_category | return_pct | pnl | drawdown | sharpe | trade_count | win_rate | fees | slippage | funding |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| VAR-000001 | 20 | 0.0025 | successful | -1.0000 | -10000.00 | 1.0000 | -3.3185 | 747 | 0.7068 | 4712.34 | 1178.08 | 0.00 |
| VAR-000002 | 20 | 0.0050 | successful | -1.0000 | -10000.00 | 1.0000 | -0.0941 | 1037 | 0.6683 | 7695.88 | 1923.97 | 0.00 |
| VAR-000003 | 20 | 0.0100 | successful | -1.0000 | -10000.00 | 1.0000 | 0.7334 | 854 | 0.6230 | 12895.14 | 3223.78 | 0.00 |
| VAR-000004 | 20 | 0.0150 | successful | -1.0000 | -10000.00 | 1.0000 | 0.8303 | 1466 | 0.6132 | 37332.33 | 9333.08 | 0.00 |
| VAR-000005 | 20 | 0.0200 | successful | -1.0000 | -10000.00 | 1.0000 | -0.1537 | 555 | 0.6216 | 13633.02 | 3408.25 | 0.00 |
| VAR-000006 | 50 | 0.0025 | successful | -1.0000 | -10000.00 | 1.0000 | 0.5901 | 1096 | 0.7600 | 8173.68 | 2043.42 | 0.00 |
| VAR-000007 | 50 | 0.0050 | successful | -1.0000 | -10000.00 | 1.0000 | -1.0654 | 794 | 0.7179 | 6355.36 | 1588.84 | 0.00 |
| VAR-000008 | 50 | 0.0100 | successful | -1.0000 | -10000.00 | 1.0000 | 0.6157 | 543 | 0.6814 | 5619.58 | 1404.89 | 0.00 |
| VAR-000009 | 50 | 0.0150 | successful | -1.0000 | -10000.00 | 1.0000 | 0.0346 | 360 | 0.6611 | 3897.31 | 974.33 | 0.00 |
| VAR-000010 | 50 | 0.0200 | successful | -1.0000 | -10000.00 | 1.0000 | 0.9972 | 308 | 0.6494 | 4697.42 | 1174.35 | 0.00 |

Raw population-level observations:

- Return and PnL: all 10 rows record `return_pct = -1.0` and
  `pnl = -10000.0` under the recorded offline model.
- Outcome completion: all 10 rows record `outcome_category=successful`, meaning
  completion with a result row.
- Drawdown: all 10 rows record `drawdown = 1.0`.
- Trade count: row values range from `308` to `1466`, with median `770.5`.
- Fees: row values range from `3897.31` to `37332.33`, with median `7025.62`.
- Slippage: row values range from `974.33` to `9333.08`, with median
  `1756.41`.
- Funding: all 10 rows record `funding = 0.0`.
- Sharpe: row values range from `-3.3185` to `0.9972`, with median `0.3124`;
  six rows are positive and four rows are negative.
- Win rate: row values range from `0.6132` to `0.7600`, with median `0.6647`.
- Exposure: all 10 rows record `exposure = 1.0`.

## Cost / drawdown / trade-count / Sharpe characteristics

Cost and activity levels vary across the grid under the fixed-bps slippage and
taker-entry/taker-exit fee assumptions. The largest recorded trade-count row
also records the largest fee and slippage values, while lower trade-count rows
generally record lower direct cost values. This is a raw artifact observation,
not a parameter recommendation.

All rows record full drawdown and `return_pct = -1.0`, so the population does
not contain a profitable row under the recorded model. Sharpe values still vary
across rows, ranging from negative to positive values, because Sharpe is a
return-series statistic and is not the same field as terminal return or PnL.

## Limitations

- One design point: symmetric SMA-band mean reversion.
- One market/timeframe/slice: BTCUSDT 15m over the committed D4A slice.
- No walk-forward/OOS split is computed in this checkpoint.
- No DSR/PSR/MinTRL is computed here.
- No robustness analysis is performed here.
- No cost-model upgrade is performed here.
- No paper/live/runtime inference is made here.
- No candidate lifecycle decision is made here.
- This checkpoint is not enough by itself to claim an edge.
- The runner records `funding=0.0` for all rows; this checkpoint does not add a
  funding-model analysis.
- The runner records `exposure=1.0` for all rows; this checkpoint does not add
  a position-state or sizing analysis.

## What this checkpoint does not decide

This checkpoint does not decide:

- whether any variant should be used;
- whether any parameter value is preferred;
- whether the strategy has an edge;
- whether the strategy should enter any candidate registry process;
- whether paper/live trading should occur;
- whether runtime, OMS, reconciliation, risk, broker, exchange, safe-mode, or
  protected paths should change;
- whether any future robustness, DSR/PSR/MinTRL, OOS, walk-forward, dashboard,
  candidate lifecycle, or registration package should be drafted.

## Possible later work, not authorized here

Possible later work, only if separately authorized, could include:

- robustness / PSR / DSR / MinTRL over `RP-6688`;
- additional descriptive comparison surfaces that preserve denominator
  accounting and non-authority language;
- a separately scoped candidate lifecycle or registration decision;
- a separately scoped return to expressiveness primitives.

Those are future options only. This checkpoint authorizes none of them.
