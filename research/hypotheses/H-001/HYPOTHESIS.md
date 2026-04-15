# Hypothesis H-001: Funding-Directional Strategy (4h)

## Hypothesis ID
H-001

## Metadata
- Created: 2026-04-14
- Status: CONCLUDED
- Owner: WP-2b-combined
- Supersedes: Original H-001 "funding-informed short baseline" was replaced before any trials were logged. The original framing was short-only; this version is symmetric (long and short). See git history for original content.

## Economic Rationale

Perpetual futures funding rates reflect the balance between long and short positioning in the derivatives market:

- **Positive funding:** Longs pay shorts - indicates crowded long positioning, perp trading at premium to spot
- **Negative funding:** Shorts pay longs - indicates crowded short positioning, perp trading at discount to spot

Both extremes represent positioning imbalances that tend to mean-revert as:
1. The cost of holding the crowded position accumulates via funding payments
2. Crowded positions become vulnerable to liquidation cascades on adverse moves
3. Arbitrageurs enter to collect the funding spread

This strategy exploits these dynamics by:
1. **Shorting when funding is highly positive** - fade crowded longs, collect funding carry
2. **Longing when funding is highly negative** - fade crowded shorts, collect funding carry
3. **Staying flat when funding is near zero** - no edge, avoid transaction costs

The strategy is symmetric: it treats positive and negative funding extremes as equivalent opportunities in opposite directions.

## Testable Prediction

A symmetric funding-directional strategy on BTCUSDT perpetual 4h bars will:
1. Generate OOS Sharpe >= 1.0 net of fees (4bps taker, 2bps slippage)
2. Capture both crowded-long and crowded-short regimes
3. Outperform a passive long-BTC benchmark on risk-adjusted basis
4. Survive walk-forward validation with efficiency > 0.5

## Primary Timeframe
4h

**Justification:** Funding on Binance USDT-M perpetuals settles every 8 hours. A 4h bar strategy samples twice per funding period, providing sufficient resolution to react to funding changes while maintaining low trade frequency (cost efficiency). Coarser timeframes (1d) would miss intra-day funding swings; finer timeframes (1h, 15m) would increase costs without proportional signal improvement.

## Confirmation Timeframes
None

## Required Data
- Instrument: BTCUSDT Binance USDT-M Perpetual
- Required streams: 4h OHLCV, 8h funding rates
- Evaluation range: Full history (2020-01-01 to present, per data_catalog.md)

## Signal Logic

INPUTS:
- funding_rate: 8h funding rate series from Binance (`fundingRate` field from `/fapi/v1/fundingRate`)
- ohlcv_4h: 4h OHLCV bars

PARAMETERS:
- lookback: 6 (number of 4h bars = 24 hours = 3 funding settlement periods)
- threshold: 0.0001 (+/-0.01% per 8h settlement, equivalent to ~10% annualized)

PREPROCESSING:
1. Align `funding_rate` to 4h bar timestamps using forward-fill
2. Each 8h funding rate applies to the 4h bars that follow its settlement until the next settlement
3. Settlement times on Binance: 00:00, 08:00, 16:00 UTC

SIGNAL GENERATION:
1. Compute `rolling_mean_funding` = rolling mean of aligned funding rate over `lookback` 4h bars
2. Generate signal at each 4h bar close:
   - If `rolling_mean_funding > +threshold`: signal = -1 (SHORT)
   - If `rolling_mean_funding < -threshold`: signal = +1 (LONG)
   - Else: signal = 0 (FLAT)

POSITION LOGIC:
- Position changes only on signal change
- No intra-bar position changes
- Position size: 1x notional (no leverage scaling in baseline)

EXECUTION ASSUMPTION:
- Entry / exit at next bar open after signal generation
- Taker fees: 4 bps
- Slippage: 2 bps

## Success Criteria (aligned with D2-006)
1. OOS Sharpe >= 1.0 net of modeled costs
2. DSR > 1.0 at 95% CI, implemented as P(SR > 1.0) > 0.95 after multiple-testing correction using the registered trial count
3. Max drawdown <= 20% in any walk-forward fold
4. Parameter sensitivity: +/-25% parameter shift keeps Sharpe within 70% of baseline
5. Cost drag <= 50% of gross PnL
6. No single 90-day window contributes > 60% of total PnL
7. Walk-forward efficiency (OOS/IS Sharpe) > 0.5

## Kill Criteria
- OOS Sharpe < 0.3 after baseline test -> archive hypothesis
- Max drawdown > 35% in any walk-forward fold -> archive hypothesis
- Both long leg and short leg unprofitable when analyzed separately -> archive hypothesis
- Funding rate predictability degrades to no better than random -> archive hypothesis

## Free Parameters
1. **lookback** (default: 6) - number of 4h bars for rolling mean
2. **threshold** (default: 0.0001) - funding rate threshold for signal generation

**Count: 2** (well under 5-parameter cap per D2-006)

## Expected Trial Count
- Baseline (default parameters): 1 trial
- Lookback sensitivity sweep (3, 6, 9, 12): 4 trials
- Threshold sensitivity sweep (0.00005, 0.0001, 0.00015, 0.0002): 4 trials
- Combined grid (if baseline promising): up to 16 trials
- **Conservative estimate: 5-10 trials**

## Artefacts
- Notebook: `research/hypotheses/H-001/experiment.ipynb` (to be created in execution package)
- Decision record: `research/decisions/DEC-0001.md` (to be created after evaluation)

## Decision Record
- Outcome: NO-GO
- Record: `research/decisions/DEC-0001.md`

## Notes
- Current market context (April 2026): Funding is deeply negative (~-0.011), meaning this strategy would currently be LONG, not short. This is a useful OOS stress test - the strategy should handle regime variety.
- The symmetric design differs from simple "short the perp, long the spot" carry arbitrage - this is a directional strategy informed by funding, not a hedged carry trade.
- Academic support: Funding rates are predictable (Inan 2025), and funding arbitrage shows favorable risk-adjusted returns (ScienceDirect 2025).
