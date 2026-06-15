# Momentum V2 Design After RP-2592

## Status And Boundary

Status: docs-only read-only research design for
`WP-MOMENTUM-V2-DESIGN-01`.

This document analyzes committed evidence after the valid `RP-2592` `NO-GO`
and designs the next evidence-based momentum v2 direction. It does not create
or freeze a Strategy Spec, Variant Manifest, Sweep Plan, or Result Population.
It does not mutate `RP-2592`, `STRAT-SPEC-0004`, `VM-0004`,
`SWEEP-PLAN-0004`, or the frozen 0004 operational screen.

No compiler, schema, catalog, query-layer, runner, `lib/`, data acquisition,
candidate lifecycle, walk-forward, paper/live/runtime, OMS, risk,
reconciliation, broker/exchange, safe-mode, or trading authority is created.

## Evidence Inputs

Fact:

- `RP-2592` is committed canonical evidence for `STRAT-SPEC-0004` /
  `VM-0004` / `SWEEP-PLAN-0004`.
- `RP-2592` preserves denominator `8`, result row count `8`, outcome count sum
  `8`, and `8` successful runner completions.
- `RP-2592` remains `NO-GO` under the frozen 0004 operational screen.
- `RP-7134` is committed canonical evidence for the Phase-B v1 fade family and
  is classified in repo truth as valid evidence for fundamental
  gross-negative expectancy.
- `RP-7520` is committed dynamic-equity-target-leverage evidence for the prior
  SMA-band fade family and is retained as a comparable realism surface.
- `STRAT-SPEC-0004` uses both-direction 15m SMA crossover momentum with
  side-specific trend confirmation, fixed `min_bars_between_entries=16`, and
  opposite-crossover exits only.
- `STRAT-SPEC-0004` explicitly excludes ATR-stop, fixed stop-loss, trailing
  stop, target distance, and max holding period.

## A. Evidence Summary

Fact:

| Population | Family | Denominator | Positive return rows | Positive Sharpe rows | Median return_pct | Median drawdown | Median trade_count | Median cost/initial equity | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `RP-7520` | 15m SMA-band fade | 10 | 0/10 | 0/10 | -0.981508 | 0.983166 | 3506.5 | 0.807302 | evidence-level no-edge/cost-drag finding |
| `RP-7134` | 15m z-score fade v1 | 8 | 0/8 | 0/8 | -0.992704 | 0.993063 | 2695.5 | 0.390507 | valid NO-GO |
| `RP-2592` | 15m SMA crossover momentum | 8 | 5/8 | 7/8 | 0.326808 | 0.643156 | 921.5 | 1.664382 | valid NO-GO |

Inference:

- Momentum is materially more encouraging than the fade families because
  `RP-2592` shows positive median net return, broad positive Sharpe, and lower
  churn than `RP-7134` and `RP-7520`.
- Momentum is still not viable under repo rules because `RP-2592` fails the
  frozen 0004 cost and drawdown screen.
- The contrast with fade evidence matters: the fade line failed even after
  churn and explicit cost improvements, while the momentum line failed after
  producing a positive net distribution.

Decision:

- Momentum v2 is justified as a future research-design direction, not as an
  immediate pre-registration freeze.
- The v2 premise must target risk-path and measurement weaknesses surfaced by
  `RP-2592`; it should not be a threshold-only or winner-only retest of 0004.

## B. Cost Decomposition

The committed result-population rows expose aggregate metrics only:
`drawdown`, `exposure`, `fees`, `funding`, `pnl`, `return_pct`, `sharpe`,
`slippage`, `trade_count`, and `win_rate`.

Computed from committed fields:

```text
total_cost = fees + slippage + funding
cost_to_initial_equity = total_cost / 10000
per_trade_average_cost = total_cost / trade_count
gross_return_approx = return_pct + cost_to_initial_equity
```

`gross_return_approx` is a compatible-units aggregate approximation only. It
does not reconstruct intratrade path, gross profit, gross loss, turnover, or
equity-curve exposure.

| Variant | fast | slow | trend | return_pct | trades | total_cost | cost/initial | avg cost/trade | gross_return_approx |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| VAR-000001 | 20 | 100 | 300 | -0.429746 | 1273 | 9943.42 | 0.994342 | 7.8110 | 0.564596 |
| VAR-000002 | 20 | 100 | 400 | 0.169923 | 1300 | 17705.01 | 1.770501 | 13.6192 | 1.940424 |
| VAR-000003 | 20 | 200 | 300 | 0.483694 | 818 | 17567.85 | 1.756785 | 21.4766 | 2.240479 |
| VAR-000004 | 20 | 200 | 400 | 0.644372 | 800 | 17162.36 | 1.716236 | 21.4529 | 2.360608 |
| VAR-000005 | 50 | 100 | 300 | 0.811322 | 1025 | 16125.29 | 1.612529 | 15.7320 | 2.423850 |
| VAR-000006 | 50 | 100 | 400 | 0.954728 | 1042 | 20970.51 | 2.097051 | 20.1253 | 3.051779 |
| VAR-000007 | 50 | 200 | 300 | -0.179286 | 601 | 7005.77 | 0.700577 | 11.6569 | 0.521291 |
| VAR-000008 | 50 | 200 | 400 | -0.056500 | 577 | 7594.35 | 0.759435 | 13.1618 | 0.702935 |

Population facts:

- Median total explicit cost: `16643.82`.
- Median `cost_to_initial_equity`: `1.664382`; range `0.700577` to
  `2.097051`.
- Median average cost per trade: `14.6756`; range `7.8110` to `21.4766`.
- `gross_return_approx` is positive in `8/8` rows; median `2.090452`.
- Pearson correlation between `cost_to_initial_equity` and `return_pct` is
  `0.838960`.
- Pearson correlation between `cost_to_initial_equity` and
  `gross_return_approx` is `0.961196`.
- Pearson correlation between `trade_count` and `cost_to_initial_equity` is
  `0.459619`.

Missing committed fields:

- gross profit;
- gross loss;
- absolute gross PnL;
- average equity;
- equity curve;
- per-trade PnL;
- turnover or notional;
- cost per turnover;
- average, maximum, or time-weighted exposure beyond aggregate exposure.

Inference:

- The frozen `cost_to_initial_equity` screen likely penalizes compounding
  winners because cumulative costs are divided by fixed initial equity while
  dynamic 1x winners can grow equity and therefore notional. The positive
  correlation between cost/equity and net return is consistent with that
  denominator effect.
- The cost failure cannot be dismissed as only a denominator artifact. Median
  explicit cost is more than 1.6x initial equity and committed fields do not
  expose cost relative to gross profit, gross loss, average equity, or
  turnover.
- The available evidence is most consistent with mixed cost diagnosis:
  compounding-denominator artifact is likely present, but explicit trading
  cost remains large enough that v2 must predeclare a better cost screen and
  still prove net-of-cost expectancy.

Decision:

- `STRAT-SPEC-0004` remains `NO-GO` under its frozen screen.
- A future v2 screen should replace `cost_to_initial_equity` as the sole cost
  burden measure with compounding-aware metrics, while preserving the 0004
  verdict unchanged.

Minimal future metric need:

- At least one of cost-to-average-equity, cost-to-gross-profit,
  cost-to-absolute-gross-PnL, or cost-to-turnover/notional should be captured
  before a v2 cost screen is frozen.

## C. Drawdown Decomposition

Fact:

- `RP-2592` median drawdown is `0.643156`.
- Maximum drawdown is `0.712333`.
- Minimum drawdown is `0.565444`.
- Every row has drawdown above the frozen median threshold `0.35` and every
  row exceeds `0.50`.
- Positive-return rows still have unacceptable drawdown:
  `0.628921`, `0.692489`, `0.565444`, `0.657392`, and `0.614364`; median
  `0.628921`.

Axis summaries:

| Axis bucket | n | median return_pct | median drawdown | median cost/initial | median trades |
|---|---:|---:|---:|---:|---:|
| fast=20 | 4 | 0.326808 | 0.660705 | 1.736510 | 1045.5 |
| fast=50 | 4 | 0.377411 | 0.635878 | 1.185982 | 813.0 |
| slow=100 | 4 | 0.490622 | 0.643156 | 1.691515 | 1157.5 |
| slow=200 | 4 | 0.213597 | 0.623031 | 1.237835 | 700.5 |
| trend=300 | 4 | 0.152204 | 0.684124 | 1.303435 | 921.5 |
| trend=400 | 4 | 0.407148 | 0.592333 | 1.743369 | 921.0 |

Inference:

- Drawdown is broad, not isolated to one fast/slow/trend bucket.
- The best net-return row, `VAR-000006`, still has drawdown `0.614364`.
- `trend=400` improves median return and drawdown versus `trend=300`, but it
  still fails drawdown and has higher median cost/initial.
- Drawdown is the clearer viability constraint than net performance. The
  population passed net-performance criteria but failed drawdown across every
  row.

ATR-stop assessment:

- ATR as an indicator exists in current repo truth.
- Current docs and compiler surfaces treat ATR-stop consumption as deferred:
  the compiler emits position-intent signals, while stop metadata and intrabar
  stop consumption are not active runner/backtester behavior.
- `RP-2592` makes stop-managed continuation evidence-justified as a future
  design dependency because all positive-return rows still carry
  unacceptable drawdown.
- `RP-2592` does not prove an ATR stop would make the strategy viable. The
  committed aggregate fields do not expose adverse excursion, per-trade loss
  concentration, or equity-path timing.

Decision:

- A stop-loss primitive, likely ATR-based or otherwise volatility-scaled, is
  justified for design and dependency planning before a future momentum v2
  preregistration.
- It is not authorized for implementation in this package.

Limitation:

- No scratch per-trade rerun was used. The package objective can be satisfied
  from committed aggregate evidence, and adding a scratch rerun was not needed
  to avoid the forbidden canonical-write surfaces.

## D. Momentum V2 Design Recommendation

Required v2 elements:

- Preserve the evidence-backed with-move premise: both-direction SMA crossover
  trend continuation or a directly comparable closed trend-continuation shape.
- Add active stop-managed risk control only after a separately authorized
  primitive exists. The preferred first dependency is an ATR-stop or
  volatility-scaled stop that acts as an offline deterministic exit/risk
  control, not as runtime order authority.
- Preserve dynamic equity target leverage at `target_leverage=1.0` unless a
  later package explicitly changes the measurement model.
- Predeclare a compounding-aware cost screen.
- Predeclare strict drawdown criteria that treat drawdown as a primary
  viability constraint, not a secondary annotation.
- Retain full denominator accounting, including non-success rows.
- Keep the design net-of-cost and population-level; best-row-only success is
  forbidden.

Optional v2 elements:

- Keep side-specific trend confirmation, but consider narrowing the trend axis
  or fixing it only if a future preregistration justifies that without using
  winner-only selection.
- Adjust throttle only if cost analysis proves true edge erosion rather than
  only fixed-initial-equity denominator inflation.
- Add maximum holding only if repo truth supports deterministic offline
  semantics and the future package separates it from stop-loss semantics.
- Add volatility-scaled entry filters only after the relevant closed primitive
  exists.

Explicitly rejected elements:

- Do not mutate `STRAT-SPEC-0004`, `VM-0004`, `SWEEP-PLAN-0004`, `RP-2592`, or
  the frozen 0004 screen.
- Do not create `STRAT-SPEC-0005`, a new Variant Manifest, a Sweep Plan, or a
  Result Population in this package.
- Do not claim `RP-2592` proves profitability, deployability, promotion
  readiness, or trading suitability.
- Do not route to walk-forward or candidate promotion from this evidence.
- Do not pursue a throttle-only retest as v2; it would not address the
  all-row drawdown failure.
- Do not add funding, basis, open interest, multi-timeframe confirmation, or
  live-execution concepts without separate data/contract and boundary
  packages.

Future-only elements:

- Per-trade diagnostic rerun to quantify average win, average loss, largest
  loss, adverse excursion, and loss concentration.
- ATR-stop or volatility-stop primitive design and implementation.
- Broader volatility-normalized entry or regime filters after closed grammar
  support exists.
- Multi-timeframe confirmation after no-lookahead alignment and data contract
  design.

## E. A6 ATR-Stop Dependency

Before v2 can freeze with an ATR stop, repo truth must contain:

- Strategy Spec schema support for the stop primitive or closed stop metadata
  that is explicitly consumed by the offline signal/backtest path.
- Validator support that fails closed on unsupported stop fields, invalid
  parameter bounds, ambiguous units, and missing ATR references.
- Compiler or runner/backtester support that deterministically converts the
  stop definition into offline exits.
- Tests proving no lookahead, deterministic repeated output, null/warmup
  behavior, side-specific both-direction behavior, same-bar ordering, and
  stop-vs-signal-exit precedence.
- Result-population assumption metadata recording stop semantics and whether
  intrabar high/low consumption is used.
- Proof that the stop compiles and changes exits as intended on a synthetic
  fixture before any canonical result population is written.

Bounded semantics required:

- The stop is an offline research exit/risk-control primitive only.
- It is not a runtime order, OMS instruction, exchange order, paper/live
  permission, safe-mode change, or trading recommendation.
- It must not contact `src.runtime`, OMS, reconciliation, broker/exchange, or
  live-trading paths.
- It must use deterministic bar data with a predeclared event-ordering rule.

Open question:

- Whether ATR-stop should be implemented as compiler-emitted signal exits,
  runner/backtester stop consumption, or a two-stage design. Current repo truth
  treats ATR-stop consumption as deferred and protected-adjacent, so this must
  be resolved before v2 freeze.

## F. Future Screen Proposal

A future momentum v2 screen should be predeclared, net-of-cost,
compounding-aware, not winner-only, and not retroactive to `RP-2592`.

Possible criteria:

- Denominator completeness: every predeclared row retained; successful-only
  denominator forbidden.
- Non-success accounting: failed, errored, data-unavailable, invalid,
  excluded, filtered, aborted, and not-attempted rows retained in the
  denominator with explicit reasons.
- Churn: population median and maximum trade-count thresholds, plus a
  degenerate-low-trade floor.
- Cost: at least one compounding-aware cost metric such as
  cost-to-average-equity, cost-to-gross-profit, cost-to-absolute-gross-PnL, or
  cost-to-turnover/notional if available; `cost_to_initial_equity` may remain
  reported as a comparability metric but should not be the only burden test.
- Net performance: median return_pct > 0 after all modeled costs.
- Breadth: positive-return count and positive-Sharpe count across the full
  population.
- Drawdown: strict median and per-row drawdown thresholds; automatic `NO-GO`
  for any terminal or near-terminal drawdown.
- Positive-row sanity: positive-return rows must also satisfy drawdown and
  cost sanity; net-positive/high-drawdown rows cannot carry a `GO`.
- Sensitivity: performance and drawdown must not be concentrated in one
  fast/slow/trend or stop-distance corner.
- DSR/PSR/MinTRL: compute only if required inputs exist; otherwise mark
  not-evaluable and do not fabricate.
- Authority: no candidate, promotion, walk-forward, paper/live, or runtime
  authority from the screen itself.

Decision:

- The v2 screen should be stricter on drawdown than 0004 because `RP-2592`
  already proved positive net rows can still be risk-unacceptable.
- The v2 screen should measure costs differently, but only prospectively.
  `RP-2592` remains `NO-GO` under the frozen 0004 screen.

## G. Stop Conclusion

Fact:

- `RP-2592` is not weak or concentrated in the same way as the fade NO-GOs:
  it has positive median net return, positive Sharpe in `7/8` rows, and
  positive gross-return approximation in `8/8` rows.
- It also has unacceptable drawdown in every row and an unresolved cost
  measurement problem.

Decision:

- Do not stop the momentum line outright.
- Do not freeze momentum v2 now.
- Route the next step to Main/Karl as a dependency decision: either authorize
  an ATR-stop / volatility-stop design runway first, authorize a scratch
  per-trade diagnostic first, or reject v2 and choose a different archetype,
  data, or timeframe direction.

Future option:

- If Main/Karl reject stop-managed momentum as too broad or protected-adjacent,
  the evidence should route back to archetype/timeframe/data selection rather
  than forcing a non-stop v2 that does not address the real failure mode.
