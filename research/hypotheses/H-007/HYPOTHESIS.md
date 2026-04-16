# Hypothesis H-007: Funding + Momentum Composite

## Hypothesis ID
H-007

## Metadata
- Created: 2026-04-16
- Status: DRAFT
- Owner: WP-4a

## Economic Rationale

Funding rates can identify derivative-market positioning pressure, but H-001 showed that funding-directional logic alone was not promotable under current assumptions. A funding signal can remain wrong for long periods when crowded positioning persists with trend pressure.

This hypothesis tests whether funding information becomes more useful when it is paired with independent price confirmation:

1. **Funding favorability identifies carry/positioning context:** Positive funding favors shorts from a cashflow perspective; negative funding favors longs.
2. **Momentum confirmation avoids fading persistent trends too early:** The strategy only trades the funding-favorable direction when 4h price momentum confirms that direction.
3. **Composite logic is materially different from H-001:** Funding is not sufficient by itself; it must align with price movement.
4. **4h remains economically aligned with funding cadence:** Binance funding settles every 8 hours, and 4h bars sample twice per funding period without moving to a high-turnover intraday layer.

This is a new pre-registered hypothesis, not a tuning pass on H-001.

## Testable Prediction

A 4h funding + momentum composite strategy on BTCUSDT perpetuals will:

1. Generate OOS Sharpe >= 1.0 net of modeled costs
2. Improve on naive funding-directional logic by requiring price confirmation
3. Keep turnover controlled enough that cost drag remains within D2-006 limits
4. Survive walk-forward validation with efficiency > 0.5

## Primary Timeframe
4h

**Justification:** Funding settles every 8 hours on Binance USDT-M perpetuals. A 4h primary timeframe is close enough to react to funding-context changes while avoiding the turnover pressure observed in the failed 1h and 30m baselines. Although 4h is in Cold Storage after H-001/H-002, this hypothesis has a materially different economic rationale from both failed 4h baselines.

## Confirmation Timeframes
None

## Required Data
- Instrument: BTCUSDT Binance USDT-M Perpetual
- Required streams: 4h OHLCV, 8h funding rates
- Extra data required: None
- Evaluation range: Full history available in `docs/data_catalog.md`

## Signal Logic

INPUTS:
- `ohlcv_4h`: 4h OHLCV bars with columns `[open, high, low, close, volume]`
- `funding`: 8h funding-rate events with `funding_rate`

INDICATORS:
- `rolling_funding[t]` = rolling mean of funding rates aligned to 4h bars
- `momentum[t]` = close-to-close return over `momentum_lookback` 4h bars

PARAMETERS:
- `funding_lookback`: 6
- `funding_threshold`: 0.0001
- `momentum_lookback`: 12
- `momentum_threshold`: 0.0

PREPROCESSING:
1. Align funding events to the 4h OHLCV index using forward-fill.
2. Each funding rate applies after its funding event until the next funding event.
3. Compute rolling funding and 4h price momentum using only information available at the bar close.

SIGNAL GENERATION (at each 4h bar close):
1. If `rolling_funding[t] < -funding_threshold` and `momentum[t] > momentum_threshold`: signal = +1 (LONG)
2. If `rolling_funding[t] > funding_threshold` and `momentum[t] < -momentum_threshold`: signal = -1 (SHORT)
3. Else: signal = 0 (FLAT)

POSITION LOGIC:
- Position changes only on signal change
- No partial positions
- Position size: 1x baseline notional

EXIT LOGIC:
- Exit to flat when funding favorability and momentum confirmation no longer both support the current direction
- Reverse only when the opposite composite condition is met

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
- Composite confirmation does not materially improve on the H-001 failure mode -> archive hypothesis
- Both long leg and short leg unprofitable when analyzed separately -> archive hypothesis

## Free Parameters
1. **funding_lookback** (default: 6; sensitivity range: 3-12) - number of 4h bars for rolling funding context
2. **funding_threshold** (default: 0.0001; sensitivity range: 0.00005-0.0002) - minimum funding magnitude for carry context
3. **momentum_lookback** (default: 12; sensitivity range: 6-24) - 4h bars for price confirmation
4. **momentum_threshold** (default: 0.0; sensitivity range: 0.0-0.005) - minimum price momentum required to confirm direction

**Count: 4** (under the D2-006 parameter cap)

## Expected Trial Count
- Baseline (default parameters): 1 trial
- One-at-a-time parameter sensitivity: 8-12 trials
- Combined grid only if baseline is promising: up to 24 trials
- **Conservative estimate: 9-13 trials**

## Artefacts
- Notebook: `research/hypotheses/H-007/experiment.ipynb` (to be created by execution package)
- Decision record: `research/decisions/DEC-0007.md` (to be created after evaluation)

## Decision Record
- Outcome: TBD

## Notes
- This hypothesis reopens 4h planning only because it is materially different from H-001 and H-002.
- The baseline must not be interpreted as proof that funding strategies broadly work; it is a specific composite test.
