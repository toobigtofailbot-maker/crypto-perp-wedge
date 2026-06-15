# Phase-B v1 Failure Decomposition

## Status / authority boundary

Status: read-only diagnostic evidence for `WP-PHASEB-V1-DIAG-01`.

This document decomposes the committed Phase-B v1 result population
`RP-7134` against the comparable dynamic-sizing baseline `RP-7520`. It does
not mutate v1, does not replace any canonical result population, does not
write canonical evidence, does not authorize v2, does not authorize
walk-forward, and does not authorize candidate registration, ranking,
promotion, paper/live, runtime, OMS/risk/reconciliation, broker/exchange, or
trading behavior.

Any future v2 requires a separate pre-registration. Any stop-loss primitive,
including a possible ATR-stop capability, requires a separate compiler/schema
package if it is not currently expressible.

## Evidence inputs

Fact:

- `RP-7134` is committed canonical evidence for `STRAT-SPEC-0003` /
  `VM-0003` / `SWEEP-PLAN-0003`.
- `RP-7134` preserves denominator `8`, result row count `8`, outcome count
  sum `8`, and `8` successful runner completions.
- `RP-7520` is committed canonical dynamic-sizing evidence for
  `STRAT-SPEC-0002` / `VM-0002` / `SWEEP-PLAN-0002`.
- Both result populations use `dynamic_equity_target_leverage`,
  `target_leverage=1.0`, `initial_equity=10000`, taker-entry / taker-exit
  fees, fixed-bps slippage, zero funding in the canonical 15m runner input,
  zero-equity liquidation mode, and the same BTCUSDT 15m D4/D4A data-slice
  identity `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`.
- The metric fields used here are `variant_result_rows[].metrics`.

The gross-return calculation below is an approximation:

```text
total_explicit_cost = metrics.fees + metrics.slippage + metrics.funding
cost_to_initial_equity = total_explicit_cost / 10000
gross_return_approx = metrics.return_pct + cost_to_initial_equity
```

The unit compatibility is confirmed by the runner and result-population
assumption surface: `metrics.return_pct` is `(final_equity - initial_equity) /
initial_equity`; costs are stored in the same monetary unit as
`initial_equity`; and the committed assumption text records
`initial_equity=10000`. The approximation does not reconstruct intratrade
path, liquidation mechanics, or per-trade distribution.

## RP-7134 decomposition

| variant_id | center | vol | trend | return_pct | drawdown | win_rate | sharpe | trade_count | fees | slippage | funding | total_cost | cost/equity | gross_return_approx |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| VAR-000001 | 50 | 30 | 100 | -0.997720 | 0.997858 | 0.699604 | -2.127242 | 3532 | 3846.19 | 961.55 | 0.00 | 4807.74 | 0.480774 | -0.516946 |
| VAR-000002 | 50 | 30 | 200 | -0.993909 | 0.994177 | 0.703572 | -1.726841 | 3667 | 5228.48 | 1307.12 | 0.00 | 6535.60 | 0.653560 | -0.340349 |
| VAR-000003 | 50 | 50 | 100 | -0.995174 | 0.995508 | 0.679329 | -1.957253 | 2922 | 3339.72 | 834.93 | 0.00 | 4174.66 | 0.417466 | -0.577709 |
| VAR-000004 | 50 | 50 | 200 | -0.991644 | 0.992135 | 0.686287 | -1.657983 | 3143 | 4612.82 | 1153.21 | 0.00 | 5766.03 | 0.576603 | -0.415041 |
| VAR-000005 | 100 | 30 | 100 | -0.993416 | 0.993639 | 0.742075 | -1.721283 | 2082 | 1925.70 | 481.43 | 0.00 | 2407.13 | 0.240713 | -0.752703 |
| VAR-000006 | 100 | 30 | 200 | -0.989630 | 0.990066 | 0.735925 | -1.381610 | 2469 | 2908.38 | 727.10 | 0.00 | 3635.48 | 0.363548 | -0.626082 |
| VAR-000007 | 100 | 50 | 100 | -0.991992 | 0.992488 | 0.721983 | -1.682052 | 1856 | 1749.67 | 437.42 | 0.00 | 2187.09 | 0.218709 | -0.773283 |
| VAR-000008 | 100 | 50 | 200 | -0.986042 | 0.986650 | 0.722070 | -1.311212 | 2184 | 2785.63 | 696.41 | 0.00 | 3482.03 | 0.348203 | -0.637839 |

Population facts:

| metric | min | median | max | mean |
|---|---:|---:|---:|---:|
| trade_count | 1856 | 2695.5 | 3667 | 2731.875 |
| return_pct | -0.997720 | -0.992704 | -0.986042 | -0.992441 |
| drawdown | 0.986650 | 0.993063 | 0.997858 | 0.992815 |
| win_rate | 0.679329 | 0.712778 | 0.742075 | 0.711356 |
| sharpe | -2.127242 | -1.701668 | -1.311212 | -1.695685 |
| total_cost | 2187.09 | 3905.07 | 6535.60 | 4124.47 |
| cost/equity | 0.218709 | 0.390507 | 0.653560 | 0.412447 |
| gross_return_approx | -0.773283 | -0.601895 | -0.340349 | -0.579994 |

Fact:

- Net return is nearly constant and near terminal loss across the population:
  range `-0.997720` to `-0.986042`.
- Explicit cost varies materially: cost/equity range `0.218709` to
  `0.653560`.
- Every row has `return_pct <= -0.95` and `drawdown >= 0.95`.
- Every row has negative Sharpe.
- Every row has high win rate, from `0.679329` to `0.742075`.
- Every row has negative gross-return approximation, from `-0.773283` to
  `-0.340349`.
- The lowest-cost row, `VAR-000007`, has cost/equity `0.218709`,
  net return `-0.991992`, drawdown `0.992488`, and gross-return approximation
  `-0.773283`.

Cost relationship:

- Pearson correlation between cost/equity and net return is `-0.280886`.
- Spearman rank correlation between cost/equity and net return is
  `-0.357143`.
- Pearson correlation between cost/equity and gross-return approximation is
  `0.999748`; Spearman is `1.0`. This is mechanically expected because
  `gross_return_approx` adds the cost term back to an almost constant net-loss
  surface.

Inference:

- Costs do not explain the failure on their own. If cost were dominant, lower
  explicit cost should rescue at least part of the population or at least move
  low-cost rows close to flat. It does not.
- The aggregate evidence points to materially negative pre-cost economics
  across all eight Phase-B v1 variants.

## RP-7520 comparison

`RP-7520` comparison facts:

| metric | min | median | max | mean |
|---|---:|---:|---:|---:|
| trade_count | 1212 | 3506.5 | 12962 | 4850.2 |
| return_pct | -0.999998 | -0.981508 | -0.616501 | -0.912189 |
| drawdown | 0.726300 | 0.983166 | 0.999998 | 0.935495 |
| win_rate | 0.592409 | 0.638870 | 0.740573 | 0.647797 |
| sharpe | -3.169619 | -0.922568 | -0.174432 | -1.198252 |
| total_cost | 7141.39 | 8073.02 | 16751.36 | 9052.83 |
| cost/equity | 0.714139 | 0.807302 | 1.675136 | 0.905283 |
| gross_return_approx | -0.284924 | -0.100578 | 0.847158 | -0.006905 |

Comparison:

- Churn improved versus RP-7520: RP-7134 median trade count `2695.5` is below
  RP-7520 median `3506.5`, and RP-7134 mean `2731.875` is below RP-7520 mean
  `4850.2`.
- Cost burden improved versus RP-7520: RP-7134 median cost/equity `0.390507`
  is below RP-7520 median `0.807302`.
- Net outcome did not improve materially: RP-7134 median return
  `-0.992704` is worse than RP-7520 median `-0.981508`, and RP-7134 best
  return `-0.986042` is much worse than RP-7520 best `-0.616501`.
- Drawdown did not improve materially: RP-7134 median drawdown `0.993063` is
  slightly worse than RP-7520 median `0.983166`, and all eight RP-7134 rows
  have drawdown at or above `0.986650`.
- Win rate rose in RP-7134: median `0.712778` versus RP-7520 median
  `0.638870`. This did not translate to positive Sharpe or survivable
  drawdown.

Decision:

- Z-score normalization, the shared trend gate, and fixed throttle reduced
  churn and explicit cost versus RP-7520.
- They did not improve the net outcome, drawdown behavior, or single-slice
  research viability.
- RP-7134 is worse than RP-7520 on best-row and median net outcome, despite
  lower churn and lower explicit cost.

## Gross-vs-net assessment

Fact:

- RP-7134 has `0/8` positive net-return rows.
- RP-7134 has `0/8` positive gross-return-approximation rows.
- RP-7134 median net return is `-0.992704`.
- RP-7134 median gross-return approximation is `-0.601895`.
- RP-7134 best gross-return approximation is still negative at `-0.340349`.
- RP-7134 lowest-cost rows remain heavily gross-negative by approximation.

Inference:

- The committed aggregate fields reject a cost-driven-only diagnosis.
- Lower frequency and stronger churn control alone are unlikely to salvage the
  frozen v1 family unless they also change the underlying adverse gross return
  profile.

Evidence limit:

- `gross_return_approx` is not a trade-level gross PnL reconstruction. It is a
  compatible-units aggregate approximation using committed cost fields and the
  recorded initial equity.

## Tail/no-stop assessment

Fact:

- `STRAT-SPEC-0003` exits only on side-specific SMA centerline returns.
- `STRAT-SPEC-0003` declares no stop distance, no target distance, and no max
  holding period.
- RP-7134 has high win rate in every row but near-total net loss and
  near-total drawdown in every row.
- Committed `RP-7134` rows do not include per-trade PnL distribution, average
  win, average loss, largest loser, adverse excursion, entry/exit sequence, or
  liquidation timestamp fields.
- No scratch per-trade rerun was used for this diagnostic. The existing
  backtester exposes `trades_df` in memory, but the committed D4A normalized
  CSV path referenced by the canonical artifact is not present in the
  dedicated worktree, and this package did not reconstruct or transform data.

Inference:

- No-stop tail behavior is plausible. The pattern of high win rate combined
  with near-total drawdown is consistent with many small or moderate winning
  exits being overwhelmed by adverse holds.
- The committed aggregate evidence does not prove that a few individual
  trades caused most of the loss, because per-trade data are absent.
- A future stop-loss primitive could be a legitimate research dependency only
  if separately scoped, but this diagnostic does not prove that adding a stop
  would make Phase-B v1 salvageable.

Open question:

- A narrow future scratch diagnostic could rerun the frozen v1 inputs against
  the canonical D4A data path and record per-trade PnL distribution outside
  canonical result-population paths. That would answer average-win/loss and
  loss-concentration questions. It would still not authorize v2, walk-forward,
  or trading behavior.

## Failure-mode classification

Decision: `fundamental gross-negative expectancy`.

Confidence: medium-high for the aggregate classification; lower for the exact
tail mechanism.

Rationale:

- Cost burden improved materially versus RP-7520, but net outcome and drawdown
  did not improve.
- Cost variation inside RP-7134 is large, while net return remains nearly
  terminal across all variants.
- Every RP-7134 row remains materially negative after adding explicit costs
  back to initial equity.
- The lowest-cost RP-7134 variants are not close to flat; they are among the
  most negative gross-return-approximation rows.
- Tail/no-stop behavior may worsen the result, but the aggregate evidence
  supports negative pre-cost economics across the frozen family.

Rejected classifications:

- Not `cost-driven`: costs are material but not sufficient to explain the
  failure.
- Not cleanly `no-stop-tail-driven`: the no-stop mechanism is plausible, but
  committed fields do not expose trade-level concentration evidence.
- Not `mixed / inconclusive`: the cost and gross-approximation evidence is
  strong enough to classify the dominant aggregate failure mode.

## Salvage / pivot implication

Fact:

- Churn control and fixed throttling reduced trade count and explicit cost
  relative to RP-7520.
- The frozen v1 family still failed net return, Sharpe, and drawdown across
  every variant.

Decision:

- Stronger churn control / lower frequency alone is not warranted as the next
  single dependency for this frozen fade family.
- A stop-loss primitive is not proven sufficient by committed evidence, but it
  remains a plausible future diagnostic primitive because v1 lacks stop logic
  and has high-win-rate / near-total-drawdown behavior.
- Pivoting away from BTC 15m centerline mean-reversion fading is favored unless
  a separately authorized v2 specifically changes the gross expectancy surface,
  not just the explicit cost surface.

## Forbidden conclusions

This diagnostic does not conclude or authorize any of the following:

- v1 mutation;
- v2 pre-registration;
- walk-forward;
- candidate registry mutation;
- candidate ranking, readiness, promotion, paper/live, or runtime behavior;
- trading recommendation;
- result-population rewrite or replacement;
- compiler/schema/catalog/lib/runner changes;
- OMS, risk, reconciliation, broker/exchange, collateral, safe-mode, or
  live-trading changes.

## Next decision surface

If Main wants another mean-reversion fade package, the next decision should be
one of:

1. Stop the BTC 15m fade line and pivot to a non-fade family such as
   trend/momentum.
2. Authorize a docs-only v2 design surface that explicitly changes the
   expected gross-return mechanism and treats lower churn as secondary.
3. Authorize a separate compiler/schema design for a closed stop-loss
   primitive, likely ATR-stop, before any v2 that depends on stop semantics.
4. Authorize a narrow scratch-only per-trade diagnostic over the frozen v1
   inputs and canonical D4A path to quantify average win, average loss,
   largest losers, and loss concentration.

This document selects no strategy and creates no downstream authority.
