# Phase-B Momentum Preregistration 0004

Status: finalized pre-registration screen for WP-PHASEB-MOMENTUM-PREREG-01.

This document records the finalized STRAT-SPEC-0004 / VM-0004 /
SWEEP-PLAN-0004 pre-registration surface after Codex-chat finalize
authorization on 2026-06-15. It is not canonical evidence, not a candidate
lifecycle decision, not a ranking/readiness/promotion decision, and not
paper/live/runtime authority.

## Design

- Strategy Spec: STRAT-SPEC-0004, both-direction BTCUSDT 15m SMA crossover trend continuation.
- Variant Manifest: VM-0004, valid-only 8-row grid.
- Sweep Plan: SWEEP-PLAN-0004, all variants selected, executed=0, successful=0, not_attempted=8.
- Fixed throttle: entry_logic.entry_controls.min_bars_between_entries = 16 bars.
- Excluded primitives: z-score, regime gate, ATR-stop, fixed stop-loss, trailing stop, max_holding_period, centerline fade target, volatility regime filter, slope primitive, rolling breakout channel.

## Axes And Denominator

- fast_lookback_bars: [20, 50]
- slow_lookback_bars: [100, 200]
- trend_lookback_bars: [300, 400]
- Free-parameter count: 3
- Committed denominator: 8
- Invalid/excluded cells: 0
- Validity rule: every Cartesian row satisfies fast < slow < trend.

## Operational Success Criteria

All criteria below are frozen for the future canonical single-slice result
population if a later package separately authorizes that run. They are not
promotion, readiness, candidate approval, or paper/live authority.

1. Denominator completeness: PASS only if the future canonical result population preserves committed denominator 8, result rows reconcile to 8, and all non-success rows remain retained with explicit outcome accounting.
2. Churn: PASS only if population median trade_count <= 1200, no row with otherwise-successful net/drawdown characteristics has trade_count > 1500, and no row is degenerate with trade_count < 50.
3. Cost burden: PASS only if median cost_to_initial_equity <= 0.25 and every core-sanity row has cost_to_initial_equity <= 0.35, where cost_to_initial_equity = (fees + slippage + funding) / 10000.
4. Net performance: PASS only if median return_pct > 0.0, at least 4/8 rows have return_pct > 0.0, and at least 3/8 rows have Sharpe > 0.0. Best-row-only success is forbidden.
5. Drawdown: PASS only if population median max_drawdown <= 0.35 and every core-sanity row has max_drawdown <= 0.50. Automatic NO-GO if any row has max_drawdown >= 0.95 or if median max_drawdown >= 0.75.
6. Sensitivity: PASS only if positive net-return rows include both fast-axis values and both slow-axis values, and each trend bucket median return_pct is no worse than -0.10. If an axis cannot be evaluated because no rows pass core sanity, sensitivity fails.
7. C3 / DSR: denominator is 8 for the future family accounting. Numeric PSR/DSR/MinTRL must be withheld unless required inputs exist; do not fabricate unavailable DSR.
8. Retention: non-success, failed, errored, data-unavailable, filtered, invalid, excluded, and not-attempted rows remain in denominator accounting and diagnostic tables.

Core-sanity row means a row with trade_count in [50, 1500], cost_to_initial_equity <= 0.35, max_drawdown <= 0.50, return_pct > 0.0, and Sharpe > 0.0.

## Boundary

No canonical sweep, canonical result population, trial-log entry, candidate
registry entry, promotion, paper/live/runtime path, OMS/risk/reconciliation
path, broker/exchange path, schema, validator, compiler, runner, `lib/`,
`src/`, data catalog, or data-content change is authorized by this artifact.

Future canonical trial execution remains separately unauthorized and requires a
later explicit package.
