# Momentum V2 Preregistration 0005

Status: freeze-candidate preregistration surface for
`WP-MOMENTUM-V2-PREREG-01`.

This document surfaces `STRAT-SPEC-0005`, `VM-0005`, and
`SWEEP-PLAN-0005` plus the proposed single-slice screen for momentum v2 with
the A6 ATR-stop primitive. Merge/finalize remains `HOLD` pending Karl gate.
It is not canonical evidence, not a candidate lifecycle decision, not a
ranking/readiness/promotion decision, and not paper/live/runtime authority.

## Design

- Strategy Spec: `STRAT-SPEC-0005`, both-direction BTCUSDT 15m SMA crossover
  trend continuation.
- Parent comparison: reuses `STRAT-SPEC-0004` fast/slow/trend entry and
  opposite-crossover exit logic.
- Added exit: fixed A6 `exit_logic.atr_stop`.
- Fixed throttle: `entry_logic.entry_controls.min_bars_between_entries = 16`.
- ATR literals: `atr_lookback = 14`, `atr_multiplier = 3.0`.
- ATR rationale: conventional volatility-stop constants selected before any
  0005 result exists; not selected from post-hoc 0005 performance optimization.
- ATR semantics: entry reference is next-bar open before fee/slippage,
  evaluation price is close, evaluation timing is bar close, ATR is frozen from
  the entry signal bar, long stop is `entry_ref - 3.0 * ATR(14)`, and short
  stop is `entry_ref + 3.0 * ATR(14)`.
- Excluded primitives: z-score, regime gate, fixed stop-loss, trailing stop,
  target distance, max holding period, slope primitive, rolling breakout
  channel, intrabar stop touches, fill realism, and ATR parameter sweeps.

## Axes And Denominator

- fast_lookback_bars: `[20, 50]`
- slow_lookback_bars: `[100, 200]`
- trend_lookback_bars: `[300, 400]`
- Free-parameter count: `3`
- Fixed non-swept parameters: `atr_lookback=14`, `atr_multiplier=3.0`,
  `min_bars_between_entries=16`
- Committed denominator: `8`
- Invalid/excluded cells: `0`
- Validity rule: every Cartesian row satisfies `fast < slow < trend`.

`SWEEP-PLAN-0005` selects all eight `VM-0005` variants, records
`executed=0`, `successful=0`, `not_attempted=8`, maps no result population,
and creates no canonical write authority.

## RP-2592 Cost Classification

Committed `RP-2592` fields available:

- denominator, result row count, outcome counts, sizing metadata, data lineage;
- row-level `drawdown`, `exposure`, `fees`, `funding`, `pnl`, `return_pct`,
  `sharpe`, `slippage`, `trade_count`, and `win_rate`.

Committed fields missing:

- gross profit, gross loss, absolute gross trade PnL, average equity, equity
  curve, per-trade PnL distribution, turnover, and notional.

Scratch diagnostic used: `YES`.

Scratch scope:

- local in-memory diagnostic only;
- no result population, canonical artifact, trial log, or repo file written;
- D4A local CSV read from the existing documented local path;
- `VAR-000006` and `VAR-000004` rerun through `compile_signal` and
  `run_backtest` to expose `trades_df` and `equity_curve`;
- attempted full eight-row scratch diagnostic timed out after 300 seconds
  before output and was not used as evidence.

Scratch facts:

| Variant | return_pct | drawdown | trades | cost/initial | cost/gross_pnl | cost/avg_equity | cost/abs gross trade PnL |
|---|---:|---:|---:|---:|---:|---:|---:|
| VAR-000006 | 0.954728 | 0.614364 | 1042 | 2.097051 | 0.687157 | 1.046094 | 0.053211 |
| VAR-000004 | 0.644372 | 0.565444 | 800 | 1.716236 | 0.727031 | 0.800885 | 0.050202 |

Classification: `mixed`.

Fact:

- The committed fixed-initial-equity cost screen is distorted for dynamic 1x
  compounding winners because cost-to-initial-equity is much larger than
  cost-to-average-equity on rerun rows.
- Cost remains economically material: rerun cost-to-gross-PnL is about
  `0.69` to `0.73` for two positive-return rows, so ATR-stop alone must not be
  treated as a cost fix.
- Cost-to-absolute-gross-trade-PnL is low on those rows, which suggests gross
  churn notional is large and the gross edge is thin after fees/slippage.

Decision:

- v2 must use a compounding-aware cost metric, preferably cost-to-gross-PnL
  when gross PnL is positive.
- If a future canonical 0005 result population cannot expose
  cost-to-gross-PnL or an equivalent compounding-aware metric, the v2 screen
  must stop rather than freeze an undecidable cost verdict.
- If v2 still fails cost-to-gross-PnL, the next lever is cost/churn reduction,
  not claiming the ATR stop solved cost.

## Proposed Single-Slice Screen

All criteria below are proposed for the future canonical single-slice result
population if Karl approves this freeze candidate and a later package
separately authorizes execution. They are not promotion, readiness, candidate
approval, walk-forward, or paper/live authority.

1. Denominator completeness: PASS only if result rows equal denominator `8`,
   outcome count sum equals `8`, and all non-success rows remain retained with
   explicit outcome accounting.
2. No degenerate denominator: PASS only if all eight rows are attempted or
   every non-attempted row has a predeclared retained non-success reason.
3. Runner completion: PASS only if all rows complete successfully, unless a
   predeclared failure-accounting rule explicitly retains the failure in the
   denominator.
4. Net performance: PASS only if population median `return_pct > 0.0`, at
   least `5/8` rows have `return_pct > 0.0`, and at least `5/8` rows have
   `sharpe > 0.0`.
5. Drawdown primary gate: PASS only if population median drawdown `<= 0.45`,
   maximum drawdown `< 0.60`, and every row that otherwise satisfies net and
   churn sanity has drawdown `<= 0.50`. Automatic `NO-GO` if any row has
   drawdown `>= 0.75`.
6. Cost: PASS only if a compounding-aware metric is available. Preferred rule:
   median `cost_to_gross_pnl <= 0.55` over positive-gross-PnL rows and every
   otherwise core-sanity row `<= 0.75`. If gross PnL is unavailable or
   non-positive for most rows, use a repo-supported equivalent such as
   cost-to-average-equity or cost-to-absolute-gross-PnL; otherwise STOP.
7. Churn: PASS only if median `trade_count` is between `50` and `1400`, maximum
   `trade_count <= 1800`, and no otherwise core-sanity row is carried by a
   single very low-trade outcome.
8. Sensitivity: PASS only if positive-return rows span more than one bucket on
   at least two of the fast, slow, and trend axes. Single-row or best-row-only
   success is forbidden.
9. DSR / PSR / MinTRL: compute only if required inputs exist. If not wired,
   mark not-evaluable and do not fabricate numeric confidence.
10. Retention and authority: non-success, failed, errored, data-unavailable,
    filtered, invalid, excluded, and not-attempted rows remain in denominator
    accounting. Passing this screen creates no candidate, promotion,
    walk-forward, paper/live, or runtime authority.

Core-sanity row means a row with retained successful runner completion,
`trade_count` in `[50, 1800]`, `return_pct > 0.0`, `sharpe > 0.0`, drawdown
`<= 0.50`, and a decidable compounding-aware cost value.

## Boundary

No canonical sweep, canonical result population, trial-log entry, candidate
registry entry, promotion, walk-forward, paper/live/runtime path,
OMS/risk/reconciliation path, broker/exchange path, schema, validator,
compiler, runner, `lib/`, `src/`, data catalog, or data-content change is
authorized by this artifact.

Do not mutate `RP-2592`, `STRAT-SPEC-0004`, `VM-0004`, or
`SWEEP-PLAN-0004`. Future canonical trial execution remains separately
unauthorized and requires a later explicit package.
