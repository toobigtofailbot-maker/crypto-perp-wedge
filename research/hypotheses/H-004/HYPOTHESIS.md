# Hypothesis H-004: Daily Dual Moving Average with Volatility Regime Filter

## Hypothesis ID
H-004

## Metadata
- Created: 2026-04-15
- Status: DRAFT
- Owner: WP-3a1

## Economic Rationale

BTCUSDT can trend over multi-week and multi-month horizons, making slower daily trend-following a plausible candidate family. A plain crossover can be fragile, so this hypothesis adds a volatility regime filter to avoid low-quality crossover environments where whipsaws may dominate.

The candidate rationale is:

1. **BTC trends can persist:** Slower moving averages may capture medium-term directional regimes.
2. **Low-volatility/ranging periods weaken crossover quality:** Crossover signals can churn when price lacks directional expansion.
3. **Volatility regime filtering is a common enhancement pattern:** A realized-volatility filter may improve robustness by requiring a more active market state.
4. **Daily timeframe keeps turnover low:** A 1d primary timeframe should reduce cost drag versus shorter bars.

This is a research-informed candidate to be validated in our stack, not a proven repo strategy.

## Testable Prediction

A daily 50/200 SMA crossover strategy with a realized-volatility regime filter on BTCUSDT perpetuals will:

1. Generate OOS Sharpe >= 1.0 net of modeled costs
2. Capture both bullish and bearish daily trend regimes when volatility is supportive
3. Reduce low-quality crossover exposure by staying flat in LOW volatility regimes
4. Survive walk-forward validation with efficiency > 0.5

## Primary Timeframe
1d

**Justification:** Daily bars match the slow trend-following concept and reduce turnover. The 1d timeframe is the current primary research pivot after H-001 and H-002 failed on 4h.

## Confirmation Timeframes
None

## Required Data
- Instrument: BTCUSDT Binance USDT-M Perpetual
- Required streams: 1d OHLCV
- Extra data required: None
- Evaluation range: Full history (2020-01-01 to present, per data_catalog.md)

## Signal Logic

INPUTS:
- `ohlcv_1d`: 1d OHLCV bars with columns `[open, high, low, close, volume]`

INDICATORS:
- 50-period SMA
- 200-period SMA
- 30-day realized volatility from daily close-to-close returns
- Volatility regime = HIGH if 30-day realized volatility is greater than the 50th percentile of its trailing 252-day history

PARAMETERS:
- `fast_ma`: 50
- `slow_ma`: 200
- `rv_lookback`: 30
- `rv_percentile`: 50

PREPROCESSING:
1. Compute `fast_sma[t] = SMA(close, fast_ma)`
2. Compute `slow_sma[t] = SMA(close, slow_ma)`
3. Compute `rv_30[t]` from rolling close-to-close daily returns over `rv_lookback`
4. Compute trailing `rv_percentile` threshold over the prior 252 daily bars
5. Set `volatility_regime[t] = HIGH` when `rv_30[t] > threshold[t]`, else LOW

SIGNAL GENERATION (at each daily bar close):
1. If `fast_sma[t] > slow_sma[t]` and `volatility_regime[t] = HIGH`: signal = +1 (LONG)
2. If `fast_sma[t] < slow_sma[t]` and `volatility_regime[t] = HIGH`: signal = -1 (SHORT)
3. If `volatility_regime[t] = LOW`: signal = 0 (FLAT)

POSITION LOGIC:
- Position changes only on signal change
- No partial positions
- Position size: 1x baseline notional

EXIT LOGIC:
- Exit on opposite crossover
- Exit when volatility regime drops to LOW
- A 2x ATR(20) stop concept may be evaluated later, but it is not part of the baseline complexity

EXECUTION ASSUMPTION:
- Entry / exit at next bar open after signal generation
- Taker fees: 4 bps
- Slippage: 2 bps

## Success Criteria (aligned with D2-006)
1. OOS Sharpe >= 1.0 net of modeled costs
2. Gate 2 passes under current evaluator semantics: `dsr_val > 0.95` versus the expected maximum-SR benchmark from the registered trial count
3. Max drawdown <= 20% in any walk-forward fold
4. Parameter sensitivity: +/-25% parameter shift keeps Sharpe within 70% of baseline
5. Cost drag <= 50% of gross PnL
6. No single 90-day window contributes > 60% of total PnL
7. Free parameters <= 5
8. Walk-forward efficiency (OOS/IS Sharpe) > 0.5

Baseline execution status: pending; no backtest has been run in this package.

## Kill Criteria
- OOS Sharpe < 0.3 after baseline test -> archive hypothesis
- Max drawdown > 35% in any walk-forward fold -> archive hypothesis
- Both long leg and short leg unprofitable when analyzed separately -> archive hypothesis
- Volatility regime filter fails to reduce low-quality crossover exposure or materially worsens gate performance -> archive hypothesis

## Free Parameters
1. **fast_ma** (default: 50; sensitivity range: 30-70) - fast trend moving average
2. **slow_ma** (default: 200; sensitivity range: 150-250) - slow trend moving average
3. **rv_lookback** (default: 30; sensitivity range: 20-60) - realized-volatility lookback
4. **rv_percentile** (default: 50; sensitivity range: 30-70) - trailing 252-day volatility percentile threshold

**Count: 4** (under 5-parameter cap per D2-006)

## Expected Trial Count
- Baseline (50/200 SMA, 30-day RV, 50th percentile): 1 trial
- One-at-a-time parameter sensitivity: 8-12 trials
- Combined grid only if baseline is promising: up to 16 trials
- **Conservative estimate: 9-17 trials**

## Artefacts
- Notebook / report: to be created in a later execution package
- Decision record: to be created after evaluation if baseline execution occurs

## Decision Record
- Outcome: PENDING

## Notes
- Trend-following is a plausible BTC candidate family, and volatility regime filtering is a common enhancement pattern.
- This candidate remains to be validated in the repo's backtest, evaluation, and trial-log process.
