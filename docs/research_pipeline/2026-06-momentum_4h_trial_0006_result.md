# Momentum 4h Trial 0006 Result

Package label: `WP-MOMENTUM-4H-TRIAL-01`

Date: 2026-06-16

Status: canonical result-population evidence plus frozen single-slice screen
verdict.

## Authority Boundary

This package used explicit user authorization to write the canonical 0006
Result Population. It does not create a candidate, walk-forward, paper/live,
runtime, OMS/risk/reconciliation, broker/exchange, capital, ranking,
recommendation, readiness, or transition authority.

The unfavorable result is retained with the complete denominator. No grid,
threshold, Strategy Spec, Variant Manifest, or Sweep Plan was changed after
seeing results.

## Source Artifacts

- Strategy Spec: `STRAT-SPEC-0006`
- Variant Manifest: `VM-0006`
- Sweep Plan: `SWEEP-PLAN-0006`
- Result Population: `RP-6236`
- Result Population path:
  `research/result_populations/RP-6236.result_population.json`
- Result Population file SHA256:
  `1b8f4ed5199067629e55fea3fcaf5d544168b03fa99af824d98b22582b1772b9`
- Runner scratch output SHA256 before repository line-ending normalization:
  `9ad2b0f0d3134ae0f29f428deb668e8174ed78f502f6a69c88a08cacf678510b`
- Input identity hash:
  `sha256:47e5b6f90586159bc8da63e181ad8912c889e1bd637fc63dd68d2d1b08065a95`
- Result population identity hash:
  `sha256:60ac2a69f7551983b4d6ac3f061ff76c3ba7d0caea00fe407212f63a8b55c35a`
- 4h data identity:
  `binance_usdtm_btcusdt_ohlcv_4h:sha256:4379d2f0fad5e79bfd5576b308d01fb6134b0f5acf04013e73e00ce33ca96b30`
- Parent 15m data identity:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- 4h CSV SHA256:
  `828ad4a975c157c7ac4d3c873a39a8b6bbfec3cb306e25eb74209c8a01da6ca1`

## Command

Dry-run, no write:

```powershell
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_runner.run_offline_sweep `
  --strategy-spec research\strategy_specs\STRAT-SPEC-0006.strategy_spec.json `
  --variant-manifest research\variant_manifests\VM-0006.variant_manifest.json `
  --sweep-plan research\sweep_plans\SWEEP-PLAN-0006.sweep_plan.json `
  --canonical-4h `
  --ohlcv-input C:\GitHub\crypto-perp-wedge\data\processed\d4h\binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_d4h_resampled.csv `
  --sizing-mode dynamic_equity_target_leverage `
  --target-leverage 1.0 `
  --max-workers 4
```

Canonical write:

```powershell
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_runner.run_offline_sweep `
  --strategy-spec research\strategy_specs\STRAT-SPEC-0006.strategy_spec.json `
  --variant-manifest research\variant_manifests\VM-0006.variant_manifest.json `
  --sweep-plan research\sweep_plans\SWEEP-PLAN-0006.sweep_plan.json `
  --output-dir scratch\WP-MOMENTUM-4H-TRIAL-01\canonical_0006 `
  --write-result-population `
  --canonical-4h `
  --ohlcv-input C:\GitHub\crypto-perp-wedge\data\processed\d4h\binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_d4h_resampled.csv `
  --sizing-mode dynamic_equity_target_leverage `
  --target-leverage 1.0 `
  --max-workers 4
```

The 4h CSV was read from the exact-SHA local base checkout so the trial
worktree did not create or modify `data/`.

## Population Summary

- Committed denominator: `8`
- Result row count: `8`
- Outcome count sum: `8`
- Outcome counts: `successful=8`; `failed=0`; `invalid=0`; `excluded=0`;
  `errored=0`; `aborted=0`; `filtered=0`; `data_unavailable=0`;
  `not_attempted=0`
- Denominator reconciliation: `PASS`

Successful means the runner completed the row. It does not mean profitable,
approved, promoted, ready, or recommended.

## Cost Computability

`cost_to_gross_pnl` was computed from committed fields:

- `total_cost = fees + slippage + funding`
- `gross_pnl = pnl + total_cost`
- `cost_to_gross_pnl = total_cost / gross_pnl` where `gross_pnl > 0`

Rows with `gross_pnl <= 0` are marked `N/A` for the positive-gross-PnL cost
screen denominator. All positive-gross-PnL rows are computable and all fail the
cost threshold.

## Full Variant Table

| Variant | fast/slow/trend | Outcome | Return | Sharpe | Max DD | Trades | Gross PnL | Net PnL | Cost/Gross |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| VAR-000001 | 2/6/19 | successful | -3.20% | 0.117 | 50.38% | 562 | 4,796.64 | -320.26 | 1.067 |
| VAR-000002 | 2/6/25 | successful | -67.51% | -0.538 | 73.38% | 558 | -3,782.84 | -6,751.03 | N/A |
| VAR-000003 | 2/12/19 | successful | -67.83% | -0.388 | 81.44% | 468 | -4,249.85 | -6,782.81 | N/A |
| VAR-000004 | 2/12/25 | successful | -73.52% | -0.504 | 85.91% | 454 | -4,561.03 | -7,352.30 | N/A |
| VAR-000005 | 3/6/19 | successful | -46.54% | -0.248 | 57.02% | 554 | -619.68 | -4,654.08 | N/A |
| VAR-000006 | 3/6/25 | successful | -57.44% | -0.378 | 65.99% | 556 | -2,191.37 | -5,743.73 | N/A |
| VAR-000007 | 3/12/19 | successful | -9.84% | 0.121 | 63.50% | 448 | 3,085.30 | -984.18 | 1.319 |
| VAR-000008 | 3/12/25 | successful | -29.99% | -0.010 | 78.63% | 432 | 1,680.96 | -2,999.15 | 2.784 |

## Frozen Screen Evaluation

Final single-slice verdict: `NO-GO`.

| Criterion | Verdict | Evidence |
|---|---|---|
| Denominator completeness | PASS | 8/8 variants accounted for; outcome count sum 8; no winner-only retention |
| Nondegenerate | PASS | 8 rows have nonzero gross PnL and nonzero trades |
| Net performance | FAIL | median return -51.99%; positive return rows 0/8; positive Sharpe rows 2/8 |
| Drawdown | FAIL | median drawdown 69.68%; max drawdown 85.91%; rows VAR-000003, VAR-000004, and VAR-000008 trigger automatic NO-GO with drawdown >= 75% |
| Cost | FAIL | positive-gross-PnL cost/gross values are 1.067, 1.319, and 2.784; median 1.319 is above 0.20 and every positive-gross row is above 0.35 |
| Churn | FAIL | median trade_count 511.0 is above 250; max trade_count 562 is above 500 |
| Sensitivity | FAIL | positive-return rows 0/8; no positive-return axis span exists; best-row-only success is not present because no row has positive return |
| DSR / PSR / MinTRL | NOT-EVALUABLE | required inputs are absent from available Result Population fields; no DSR, PSR, or MinTRL was fabricated |
| Funding | RECORDED | runner records synthetic zero funding; no live viability claim |
| Intrabar realism | RECORDED | ATR-stop is bar-close evaluated on 4h bars; no intrabar stop-touch or live stop-order realism claim |

## Interpretation

`RP-6236` is valid canonical evidence for the exact frozen 0006 4h
single-slice population. The population does not pass the predeclared screen.

The dominant blockers are not drawdown alone. Net performance, drawdown, cost,
churn, and sensitivity all fail. Therefore this package does not support a
tighter-stop-only follow-up route under the conditional note for drawdown-only
failure with acceptable cost and churn.

## Limitations

- Funding is modeled as synthetic zero funding.
- The ATR stop is bar-close evaluated; intrabar stop-touch and live stop-order
  behavior are not modeled.
- This is one slice only.
- No paper/live readiness is created.
- No candidate approval is created.
- No walk-forward or OOS result is created.
- No Monte Carlo or robustness result is created.

## Possible Next Route

Because the verdict is `NO-GO` for multiple screen families, this exact 0006
population should not advance to walk-forward/OOS. Any next work would require
separate explicit user/Main authorization and should be framed as a new
diagnostic or new pre-registered design package, not as promotion, readiness,
paper/live, or runtime work.
