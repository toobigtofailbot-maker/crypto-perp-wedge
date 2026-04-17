# Hypothesis H-008: Premium-Confirmed Momentum Continuation

## Hypothesis ID
H-008

## Metadata
- Created: 2026-04-16
- Status: DRAFT
- Owner: WP-4a
- Note: Replaces the initially considered volatility-scaling test because current `lib/backtest.py` casts signals to integer positions, so true fractional volatility-scaled sizing is not executable in this docs-only package.

## Economic Rationale

H-005 showed that 1h MACD with price-structure confirmation was not promotable under current assumptions. Its confirmation layer was still entirely price-derived. This hypothesis tests whether an independent derivatives-market stream can improve momentum selectivity.

Premium index pressure can indicate whether perpetual futures are trading rich or cheap relative to the index. Persistent premium aligned with price momentum may identify continuation regimes where derivative-market demand supports the move.

The candidate rationale is:

1. **Momentum alone was insufficient in H-005:** price-only confirmation did not control drawdown or cost drag.
2. **Premium pressure is a different information stream:** it reflects perp-market dislocation rather than another OHLCV transform.
3. **1h remains the cleaner first intraday layer:** it is less exposed to cost drag than 30m or 15m while still offering more observations than 4h/1d.
4. **The strategy is selective by construction:** both price momentum and premium confirmation must agree before entering.

## Testable Prediction

A 1h premium-confirmed momentum continuation strategy on BTCUSDT perpetuals will:

1. Generate OOS Sharpe >= 1.0 net of modeled costs
2. Improve signal selectivity relative to price-only 1h momentum baselines
3. Keep turnover controlled enough that cost drag remains within D2-006 limits
4. Survive walk-forward validation with efficiency > 0.5

## Primary Timeframe
1h

**Justification:** The 1h timeframe remains in PLANNING after one failed candidate cycle. It is the most appropriate first test for premium-confirmed momentum because it balances signal frequency with the cost-drag warnings from H-005/H-006.

## Confirmation Timeframes
None

## Required Data
- Instrument: BTCUSDT Binance USDT-M Perpetual
- Required streams: 1h OHLCV, 1h premium index klines, 8h funding rates for cashflow accounting
- Gap handling: the 1h premium index stream has one known irreparable bar in `data/irreparable_gaps.json`; downstream execution must skip or explicitly handle the affected bar under D2-003A
- Evaluation range: Full history available in `docs/data_catalog.md`

## Signal Logic

INPUTS:
- `ohlcv_1h`: 1h OHLCV bars with columns `[open, high, low, close, volume]`
- `premium_1h`: 1h premium index klines
- `funding`: 8h funding-rate events for backtest cashflows

INDICATORS:
- `price_momentum[t]` = close-to-close return over `momentum_lookback` bars
- `premium_z[t]` = z-score of premium index close over `premium_lookback` bars
- `exit_momentum[t]` = close-to-close return over `exit_lookback` bars

PARAMETERS:
- `premium_lookback`: 168
- `premium_z_threshold`: 1.0
- `momentum_lookback`: 24
- `exit_lookback`: 6

PREPROCESSING:
1. Align 1h premium index data to the 1h OHLCV index.
2. Exclude or explicitly handle D2-003A premium-index gap bars before signal generation.
3. Compute all indicators using only data available at the current 1h bar close.

SIGNAL GENERATION (at each hourly bar close):
1. If `price_momentum[t] > 0` and `premium_z[t] > premium_z_threshold`: signal = +1 (LONG)
2. If `price_momentum[t] < 0` and `premium_z[t] < -premium_z_threshold`: signal = -1 (SHORT)
3. Else: hold current position unless an exit condition fires

POSITION LOGIC:
- Position changes only on signal change or exit
- No partial positions
- Position size: 1x baseline notional

EXIT LOGIC:
- Exit long when `premium_z[t] <= 0` or `exit_momentum[t] < 0`
- Exit short when `premium_z[t] >= 0` or `exit_momentum[t] > 0`
- Reverse only when the opposite entry condition is met

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

## Kill Criteria
- OOS Sharpe < 0.3 after baseline test -> archive hypothesis
- Max drawdown > 35% in any walk-forward fold -> archive hypothesis
- Cost drag > 50% of gross PnL after baseline test -> archive hypothesis
- Premium confirmation fails to reduce price-only momentum fragility -> archive hypothesis
- Results are dominated by too few premium-extreme windows -> archive hypothesis

## Free Parameters
1. **premium_lookback** (default: 168; sensitivity range: 72-336) - 1h bars for premium z-score normalization
2. **premium_z_threshold** (default: 1.0; sensitivity range: 0.75-1.5) - premium pressure threshold
3. **momentum_lookback** (default: 24; sensitivity range: 12-48) - price momentum lookback
4. **exit_lookback** (default: 6; sensitivity range: 3-12) - short momentum lookback for exit confirmation

**Count: 4** (under the D2-006 parameter cap)

## Expected Trial Count
- Baseline (default parameters): 1 trial
- One-at-a-time parameter sensitivity: 8-12 trials
- Combined grid only if baseline is promising: up to 24 trials
- **Conservative estimate: 9-13 trials**

## Artefacts
- Notebook: `research/hypotheses/H-008/experiment.ipynb` (to be created by execution package)
- Decision record: `research/decisions/DEC-0008.md` (to be created after evaluation)

## Decision Record
- Outcome: TBD

## Notes
- This is not a volatility-scaling hypothesis. It replaces that candidate because the current backtester does not support fractional signal exposure without code changes.
- The candidate must not silently interpolate premium-index gaps.
