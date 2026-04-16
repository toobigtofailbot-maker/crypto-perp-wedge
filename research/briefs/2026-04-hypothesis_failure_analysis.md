# Hypothesis Failure Analysis: H-001 through H-006

**Date:** 2026-04-16
**Status:** ADVISORY / RESET BRIEF
**Context:** WP-4a docs-only reset after six baseline NO-GO decisions

## Executive Summary

H-001 through H-006 tested six pre-registered BTCUSDT USDT-M perpetual baseline hypotheses across 4h, 1d, 1h, and 30m. All six completed baselines are `NO-GO` under current repo assumptions, cost model, and D2-006 promotion gates.

The negative evidence is useful but bounded. It rejects the tested baseline implementations under current assumptions: naive symmetric funding-directional logic, simple 4h Donchian breakout, daily price-band mean reversion, daily dual moving-average trend with volatility regime filtering, 1h MACD with price-structure confirmation, and 30m Bollinger Band squeeze breakout. It does not reject all funding, all trend, all momentum, all mean-reversion, or all basis/premium strategies.

## Complete Results Summary

Values below are taken from DEC-0001 through DEC-0006 and cross-checked against `research/trial_log.jsonl`.

| Hypothesis | Timeframe | Strategy family | OOS Sharpe | Max DD | Trades | Cost drag | Gates | Verdict |
|---|---:|---|---:|---:|---:|---:|---:|---|
| H-001 | 4h | Symmetric funding-directional | -0.3898 | 178.1316% | 104 | 251.8278% | 1/8 pass | NO-GO |
| H-002 | 4h | Donchian trend-following | 0.0758 | 120.5047% | 258 | 39.7307% | 5/8 pass | NO-GO |
| H-003 | 1d | Bollinger Band mean reversion, long-only | -0.4064 | 109.5869% | 35 | 24.1338% | 2/8 pass | NO-GO |
| H-004 | 1d | Dual MA trend with volatility regime | 0.7462 | 69.7950% | 41 | 25.7700% | 5/8 pass | NO-GO |
| H-005 | 1h | MACD momentum with price structure | 0.3751 | 212.0803% | 934 | 445.5331% | 3/8 pass | NO-GO |
| H-006 | 30m | Bollinger Band squeeze breakout | -0.3512 | 612.0835% | 926 | -194.2900% | 3/8 pass | NO-GO |

Notes:

- H-006 Gate 5 passed mechanically because gross PnL was negative, making the cost-drag fraction negative. DEC-0006 explicitly warns not to interpret that as healthy cost behavior.
- The current baseline convention records full-period Sharpe in both IS and OOS trial-log fields because no separate IS/OOS split convention exists yet.
- All six hypotheses triggered their decision-record `NO-GO` outcome; none is promotable to shadow mode.

## Common Failure Patterns

1. **Drawdown severity was the clearest shared failure.** Every baseline exceeded the 20% D2-006 max-drawdown gate and the 35% kill-threshold framing used in the decision records. Drawdowns ranged from 69.7950% for H-004 to 612.0835% for H-006.

2. **Risk-adjusted return was insufficient.** No baseline reached OOS Sharpe >= 1.0. H-004 was the strongest Sharpe result at 0.7462, but still failed the promotion threshold and breached drawdown and concentration gates.

3. **Cost drag worsened materially at intraday frequencies.** H-005 recorded 934 trades on 1h and cost drag of 445.5331% of gross PnL. H-006 recorded 926 trades on 30m, negative gross PnL, and a mechanically negative cost-drag fraction that does not represent a healthy cost profile.

4. **Higher trade frequency did not improve signal quality.** H-005 and H-006 produced many more trades than the daily baselines but did not improve promotion evidence. H-005 had a positive Sharpe below threshold but ended with negative final equity, while H-006 had negative Sharpe and severe drawdown.

5. **Several simple baseline families failed in their tested form.** The completed set covers simple indicator momentum, simple breakout, simple price-band mean reversion, simple trend following, and simple funding-directional logic. The evidence supports a reset away from near-variants of these baselines.

## What Has Been Rejected

The following are rejected under current assumptions and are not promotable under the current cost and gate framework:

- Naive symmetric funding-directional logic on 4h bars, as tested by H-001.
- Simple 4h Donchian breakout trend following without additional risk or context design, as tested by H-002.
- Daily long-only price-band Bollinger mean reversion, as tested by H-003.
- Daily 50/200 dual moving-average trend following with a realized-volatility regime filter, as tested by H-004.
- 1h MACD crossover plus price-structure confirmation, as tested by H-005.
- 30m Bollinger Band squeeze breakout with ATR stop, fixed target, and time stop, as tested by H-006.

This evidence does not reject:

- Funding strategies that combine carry/funding information with independent directional confirmation.
- Trend strategies that use multi-timeframe alignment or materially different risk containment.
- Mean-reversion strategies based on mark-index basis or premium structure rather than price-band deviations.
- Intraday candidates that have explicit turnover control and signal-quality rationale before testing.

## What Remains Viable to Explore

Materially different families remain plausible if pre-registered and evaluated under the same gates:

- **Funding + Momentum Composite:** funding or carry favorability is used only when price confirms direction. This differs from H-001 because funding alone does not determine the trade.
- **Premium-Confirmed Momentum Continuation:** derivative-market premium pressure confirms price continuation. This differs from H-005/H-006 because the confirmation stream is not just OHLCV structure.
- **Multi-Timeframe Trend Alignment:** primary intraday triggers are only allowed when coarser trend states agree. This differs from H-002/H-005/H-006 because it treats higher-timeframe agreement as the core filter rather than an optional enhancement.
- **Basis / Premium Mean Reversion:** reversion is defined around mark-index or premium extremes, not price-band oversold/overbought conditions. This differs from H-003 because the economic object is perp dislocation, not spot-price deviation from a moving average.

## Implications for Research Direction

The next batch should not test weak copies of H-001 through H-006. The common failure pattern is not just "bad parameters"; it is that simple standalone signals did not survive current cost, drawdown, Sharpe, and concentration gates.

The next hypotheses should therefore be materially different in at least one of these ways:

- use multiple independent data streams, such as funding or premium plus OHLCV
- require coarser-timeframe agreement before intraday entries
- express structural perp dislocation instead of only price-derived indicators
- document turnover and gap-handling risks before execution

## Recommended Next Hypothesis Families

Priority order for the next pre-registered batch:

1. H-007: Funding + Momentum Composite on 4h.
2. H-008: Premium-Confirmed Momentum Continuation on 1h.
3. H-009: Multi-Timeframe Trend Alignment on 30m with 1h/4h confirmation.
4. H-010: Basis / Premium Mean Reversion on 4h.

The volatility-scaled trend / risk-overlay family should remain documented but not pre-registered in this batch because true fractional sizing is blocked by the current integer signal handling in the research backtester, and this package is docs-only.
