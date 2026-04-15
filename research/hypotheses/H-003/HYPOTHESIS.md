# Hypothesis H-003: Daily Bollinger Band Mean Reversion (Long-Only)

## Hypothesis ID
H-003

## Metadata
- Created: 2026-04-15
- Status: DRAFT
- Owner: WP-3a1

## Economic Rationale

Daily BTCUSDT downside deviations below a Bollinger Band may represent oversold conditions that revert toward the recent mean. This is a research-informed candidate, not a repo-proven edge.

The long-only framing is intentional:

1. **Extreme deviations can mean-revert:** A close below the lower band marks a price move that is large relative to recent realized volatility.
2. **BTC has long-run directional asymmetry:** A long-only baseline avoids assuming that downside and upside reversions are equally tradeable.
3. **Daily bars reduce noise:** The 1d timeframe filters lower-timeframe chop and should reduce turnover.
4. **Low trade frequency reduces cost drag:** Fewer entries and exits should make the strategy less sensitive to taker fees and slippage.

External literature and practitioner strategy discussions suggest this is a plausible candidate family, but profitability must be validated in this repo's stack.

## Testable Prediction

A daily long-only Bollinger Band mean-reversion strategy on BTCUSDT perpetuals will:

1. Generate OOS Sharpe >= 1.0 net of modeled costs
2. Capture oversold daily reversion without relying on short exposure
3. Keep turnover low enough that cost drag remains within D2-006 limits
4. Survive walk-forward validation with efficiency > 0.5

## Primary Timeframe
1d

**Justification:** Daily bars provide the slower / lower-turnover layer in a broader multi-timeframe research portfolio. The 1d timeframe is expected to reduce lower-timeframe noise and cost drag while preserving enough BTCUSDT history for baseline evaluation.

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
- Bollinger Bands using a 20-period SMA and 2 standard deviations
- `middle_band[t] = SMA(close, bb_period)`
- `lower_band[t] = middle_band[t] - bb_std_dev * rolling_std(close, bb_period)`

PARAMETERS:
- `bb_period`: 20
- `bb_std_dev`: 2.0

SIGNAL GENERATION (at each daily bar close):
1. If `close[t] < lower_band[t]`: signal = +1 (LONG)
2. Else if current position is LONG and `close[t] >= middle_band[t]`: signal = 0 (FLAT)
3. Else: hold current position

POSITION LOGIC:
- Long-only; no short position
- Position changes only on signal change
- Base sizing: full baseline position on entry
- Optional later enhancement: deeper lower-band deviation could imply larger size, but the baseline keeps sizing simple

EXIT LOGIC:
- Exit long when daily close is at or above the middle band
- No hard stop in the baseline pure mean-reversion version
- A stop variant can be tested later as a separate sensitivity direction if the baseline shows promise

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
- Cost drag > 50% of gross PnL after baseline test -> archive hypothesis
- Entries cluster into too few historical regimes to satisfy the 90-day contribution gate -> archive hypothesis

## Free Parameters
1. **bb_period** (default: 20; sensitivity range: 15-30) - lookback window for middle band and rolling standard deviation
2. **bb_std_dev** (default: 2.0; sensitivity range: 1.5-2.5) - lower-band distance from the middle band

**Count: 2** (well under 5-parameter cap per D2-006)

## Expected Trial Count
- Baseline (bb_period=20, bb_std_dev=2.0): 1 trial
- BB period sensitivity (15, 20, 30): 3 trials
- BB standard deviation sensitivity (1.5, 2.0, 2.5): 3 trials
- Combined grid only if baseline is promising: up to 9 trials
- **Conservative estimate: 5-9 trials**

## Artefacts
- Notebook / report: to be created in a later execution package
- Decision record: to be created after evaluation if baseline execution occurs

## Decision Record
- Outcome: PENDING

## Notes
- Research support wording is intentionally cautious: external literature suggests plausibility, not proof of profitability in this repo.
- This candidate respects the H-001/H-002 lesson that simple 4h baselines did not survive gates while keeping 1d as one layer of a broader multi-strategy, multi-timeframe research map.
