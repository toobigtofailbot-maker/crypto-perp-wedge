# Hypothesis H-010: Basis / Premium Mean Reversion

## Hypothesis ID
H-010

## Metadata
- Created: 2026-04-16
- Status: CONCLUDED
- Owner: WP-4a

## Economic Rationale

H-003 rejected daily price-band mean reversion under current assumptions. That result does not reject structural mean reversion in perpetual-market dislocations.

BTCUSDT perpetuals have mark price, index price, premium, and funding mechanics that can pull extreme dislocations back toward neutral. This hypothesis tests mean reversion in the mark-index basis or premium index, not mean reversion in the BTC price itself.

The candidate rationale is:

1. **The signal object is structural basis:** mark-index dislocation is distinct from price deviation around a moving average.
2. **Perp mechanics provide a reversion rationale:** premium and funding mechanisms can pressure extreme dislocations back toward neutral.
3. **4h data are clean for required streams:** current repo truth shows 4h mark, index, and premium histories with no known irreparable gaps.
4. **This is materially different from H-001/H-002/H-003:** it is not naive funding direction, not simple price breakout, and not price-band mean reversion.

## Testable Prediction

A 4h basis / premium mean-reversion strategy on BTCUSDT perpetuals will:

1. Generate OOS Sharpe >= 1.0 net of modeled costs
2. Capture reversion in mark-index or premium extremes without relying on price-band oversold logic
3. Keep turnover controlled enough that cost drag remains within D2-006 limits
4. Survive walk-forward validation with efficiency > 0.5

## Primary Timeframe
4h

**Justification:** The 4h timeframe is reopened from Cold Storage only for this materially different structural-dislocation hypothesis. 4h mark price, index price, and premium index streams are repo-ready with no known irreparable gaps, and 4h frequency is better aligned with funding/premium mechanics than faster intraday bars.

## Confirmation Timeframes
None

## Required Data
- Instrument: BTCUSDT Binance USDT-M Perpetual
- Required streams: 4h mark price klines, 4h index price klines, 4h premium index klines, 8h funding rates for cashflow accounting
- Gap handling: current 4h mark, index, and premium index streams have no known irreparable gaps in `data/irreparable_gaps.json`
- Evaluation range: Full history available in `docs/data_catalog.md`

## Signal Logic

INPUTS:
- `mark_4h`: 4h mark price klines
- `index_4h`: 4h index price klines
- `premium_4h`: 4h premium index klines
- `funding`: 8h funding-rate events for backtest cashflows

INDICATORS:
- `basis[t] = (mark_close[t] - index_close[t]) / index_close[t]`
- `basis_z[t]` = z-score of `basis` over `basis_lookback` bars
- `premium_close[t]` = premium index close, used as a directional consistency check without adding a free parameter

PARAMETERS:
- `basis_lookback`: 90
- `basis_z_threshold`: 2.0
- `exit_z_threshold`: 0.5
- `max_holding_bars`: 18

PREPROCESSING:
1. Align 4h mark, index, and premium streams on completed 4h bar closes.
2. Compute basis and basis z-score using only information available at the current 4h bar close.
3. Exclude any future D2-003A gap bars if the manifest changes before execution.

SIGNAL GENERATION (at each 4h bar close):
1. If `basis_z[t] > basis_z_threshold` and `premium_close[t] > 0`: signal = -1 (SHORT)
2. If `basis_z[t] < -basis_z_threshold` and `premium_close[t] < 0`: signal = +1 (LONG)
3. Else: hold current position unless an exit condition fires

POSITION LOGIC:
- Position changes only on signal change or exit
- No partial positions
- Position size: 1x baseline notional

EXIT LOGIC:
- Exit short when `basis_z[t] <= exit_z_threshold`
- Exit long when `basis_z[t] >= -exit_z_threshold`
- Exit any position after `max_holding_bars` if basis has not reverted
- Reverse only when the opposite extreme condition is met

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
- Basis extremes persist rather than revert under the max-hold framing -> archive hypothesis
- Results are dominated by too few dislocation windows -> archive hypothesis

## Free Parameters
1. **basis_lookback** (default: 90; sensitivity range: 45-180) - 4h bars for basis z-score normalization
2. **basis_z_threshold** (default: 2.0; sensitivity range: 1.5-2.5) - extreme basis entry threshold
3. **exit_z_threshold** (default: 0.5; sensitivity range: 0.25-1.0) - neutral-zone exit threshold
4. **max_holding_bars** (default: 18; sensitivity range: 12-36) - maximum holding period in 4h bars

**Count: 4** (under the D2-006 parameter cap)

## Expected Trial Count
- Baseline (default parameters): 1 trial
- One-at-a-time parameter sensitivity: 8-12 trials
- Combined grid only if baseline is promising: up to 24 trials
- **Conservative estimate: 9-13 trials**

## Artefacts
- Notebook: `research/hypotheses/H-010/experiment.ipynb`
- Decision record: `research/decisions/DEC-0010.md`

## Decision Record
- Outcome: NO-GO
- Decision record: `research/decisions/DEC-0010.md`

## Notes
- This hypothesis must remain basis/premium based. It should not be implemented as price-band mean reversion.
- The 4h timeframe remains historically Cold Storage after H-001/H-002; this candidate documents the explicit economic rationale required by D2-017 to revisit it.
