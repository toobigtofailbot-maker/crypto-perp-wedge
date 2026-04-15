# Hypothesis H-005: Hourly MACD with Price Structure Confirmation

## Hypothesis ID
H-005

## Metadata
- Created: 2026-04-15
- Status: DRAFT
- Owner: WP-3a2

## Economic Rationale

Hourly BTCUSDT momentum may be tradeable when a momentum signal is confirmed by nearby price structure. This is a research-informed candidate, not a repo-proven edge.

The candidate rationale is:

1. **MACD is a plausible momentum family:** MACD crossovers are a common way to express changes in directional momentum.
2. **Structure confirmation may filter false momentum signals:** Requiring price to break a recent swing high or swing low can avoid taking every indicator crossover in choppy conditions.
3. **The 1h timeframe balances signal count and cost drag:** Hourly bars should provide more observations than 1d while remaining more manageable than very short intraday frames.
4. **Dual confirmation may improve robustness:** Combining momentum and structure keeps the baseline interpretable while avoiding a single-indicator trigger.

This candidate remains to be validated in the repo's backtest, evaluation, and trial-log process.

## Testable Prediction

An hourly MACD crossover strategy with price-structure confirmation on BTCUSDT perpetuals will:

1. Generate OOS Sharpe >= 1.0 net of modeled costs
2. Capture directional momentum only when price confirms through recent structure
3. Reduce false crossover exposure versus a MACD-only baseline
4. Survive walk-forward validation with efficiency > 0.5

## Primary Timeframe
1h

**Justification:** The 1h timeframe is the secondary research tier after the current 1d primary candidates. It offers a balance between trade frequency and cost drag: more signal opportunities than 1d, but less noise and turnover pressure than 30m or 15m.

## Confirmation Timeframes
None

## Required Data
- Instrument: BTCUSDT Binance USDT-M Perpetual
- Required streams: 1h OHLCV
- Extra data required: None
- Evaluation range: Full history (2020-01-01 to present, per data_catalog.md)

## Signal Logic

INPUTS:
- `ohlcv_1h`: 1h OHLCV bars with columns `[open, high, low, close, volume]`

INDICATORS:
- `macd_line[t] = EMA(close, 12)[t] - EMA(close, 26)[t]`
- `signal_line[t] = EMA(macd_line, 9)[t]`
- `swing_high[t] = max(high[t-10 : t-1])`, excluding the current bar
- `swing_low[t] = min(low[t-10 : t-1])`, excluding the current bar

PARAMETERS:
- `macd_fast`: 12
- `macd_slow`: 26
- `macd_signal`: 9
- `swing_lookback`: 10
- `risk_reward_ratio`: 3

SIGNAL GENERATION (at each hourly bar close):
1. If `macd_line[t]` crosses above `signal_line[t]` and `close[t] > swing_high[t]`: signal = +1 (LONG)
2. If `macd_line[t]` crosses below `signal_line[t]` and `close[t] < swing_low[t]`: signal = -1 (SHORT)
3. Else: hold current position unless an exit condition fires

POSITION LOGIC:
- Position changes only on signal change or exit
- No partial positions
- Position size: 1x baseline notional

EXIT LOGIC:
- Exit long on opposite MACD cross or `close[t] < swing_low[t]`
- Exit short on opposite MACD cross or `close[t] > swing_high[t]`
- Risk framing: stop below swing low for longs and above swing high for shorts
- Possible target framing: 3x risk distance or trailing logic; baseline should remain interpretable

EXECUTION ASSUMPTION:
- Entry / exit at next bar open after signal generation
- Taker fees: 4 bps
- Slippage: 2 bps

## Success Criteria
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
- Cost drag > 50% of gross PnL after baseline test -> archive hypothesis
- Structure confirmation fails to reduce false momentum exposure or materially worsens gate performance -> archive hypothesis
- Both long leg and short leg unprofitable when analyzed separately -> archive hypothesis

## Free Parameters
1. **macd_fast** (default: 12; sensitivity range: 8-16) - fast EMA lookback for MACD
2. **macd_slow** (default: 26; sensitivity range: 20-32) - slow EMA lookback for MACD
3. **macd_signal** (default: 9; sensitivity range: 6-12) - signal-line EMA lookback
4. **swing_lookback** (default: 10; sensitivity range: 5-20) - recent structure lookback
5. **risk_reward_ratio** (default: 3; sensitivity range: 2-4) - target framing if fixed R:R is evaluated

**Count: 5** (at the D2-006 parameter cap)

## Expected Trial Count
- Baseline (MACD 12/26/9, swing lookback 10, risk-reward ratio 3): 1 trial
- One-at-a-time parameter sensitivity: 10-15 trials
- Combined grid only if baseline is promising: up to 25 trials
- **Conservative estimate: 11-16 trials**

## Artefacts
- Notebook / report: to be created in a later execution package
- Decision record: to be created after evaluation if baseline execution occurs

## Decision Record
- Outcome: PENDING

## Notes
- Research support wording is intentionally cautious: MACD momentum and structure confirmation are known candidate patterns, not evidence of profitability in this repo.
- If 1h OHLCV is unavailable to a future executor, report it as a data blocker while preserving this pre-registration.
