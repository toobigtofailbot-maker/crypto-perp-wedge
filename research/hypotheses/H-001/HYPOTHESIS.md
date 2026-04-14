# Hypothesis: Funding-Informed Short Baseline

## Hypothesis ID

H-001

## Economic Rationale

BTCUSDT perpetual futures exhibit persistent positive funding rates during
bull regimes, meaning long holders pay shorts. A true hedged funding carry
trade would short the perpetual and hold an offsetting long exposure elsewhere,
such as spot or another venue, to isolate the funding leg.

This hypothesis is not a fully hedged carry strategy. It is a simplified
single-instrument directional proxy: use elevated positive funding as evidence
of crowded long positioning and express that signal through short exposure in
the BTCUSDT USDT-M perpetual itself.

The edge being tested is the combination of speculative long imbalance,
adverse carry for longs, and possible mean-reversion in overheated long regimes.

## Testable Prediction

A single-instrument strategy that sizes short exposure proportionally to
trailing positive funding above a threshold will produce positive
risk-adjusted returns net of realistic costs on BTCUSDT USDT-M perpetual at
the 4h timeframe.

## Primary Timeframe

4h

**Justification:** Funding events occur every 8h. A 4h bar cadence allows
the strategy to observe one funding event per two bars, capturing funding
state without excessive noise. Finer timeframes (1h, 30m, 15m) would
introduce signal fragmentation without additional information. Coarser
timeframes (1d) would miss intra-day funding regime shifts.

## Confirmation Timeframes

None

## Success Criteria

* OOS Sharpe ≥ 1.0 net of modeled costs (Gate 1)
* DSR probability P(true Sharpe > 1.0) > 0.95 after multiple-testing correction using the registered trial count (Gate 2)
* Max drawdown ≤ 20% in any walk-forward fold (Gate 3)
* Parameter sensitivity: ±25% shift keeps Sharpe within 70% of baseline (Gate 4)
* Cost drag ≤ 50% of gross PnL (Gate 5)
* No 90-day window > 60% of total PnL (Gate 6)
* ≤ 5 free parameters (Gate 7)
* Walk-forward efficiency > 0.5 (Gate 8)

## Kill Criteria

* OOS Sharpe < 0.5 after full walk-forward evaluation
* Max drawdown > 30% in any fold
* More than 80% of PnL concentrated in a single 90-day window
* Parameter sensitivity shows Sharpe collapses (< 30% of baseline) at ±25% shift

## Free Parameters

1. `funding_threshold` — minimum funding rate (bps) to trigger short signal
2. `lookback_periods` — number of 4h bars for trailing funding average
3. `position_scale` — multiplier mapping funding magnitude to position size
4. `exit_threshold` — funding rate below which position is closed

## Expected Trial Count

Grid: 4 values × 4 values × 3 values × 3 values = 144 combinations
Walk-forward folds: 5
Total trials: ~720

Rationale: This covers a reasonable parameter space without excessive
multiple-testing burden. DSR will use this registered trial count when testing
whether P(true Sharpe > 1.0) exceeds 0.95.

## Notes

This hypothesis intentionally uses a simple funding-informed short baseline to
validate the research pipeline before testing more complex strategies. It is
not a full hedge-based carry implementation.
