# Hypothesis H-002: Donchian Channel Trend-Following (4h)

## Hypothesis ID
H-002

## Metadata
- Created: 2026-04-14
- Status: CONCLUDED
- Owner: WP-2b-combined

## Economic Rationale

Bitcoin exhibits persistent momentum at medium timeframes due to several reinforcing mechanisms:

1. **Reflexive dynamics:** Price increases attract attention (media, social), which brings new buyers, which drives further price increases. The reverse applies to downtrends.
2. **Institutional flow patterns:** Large buyers and sellers cannot execute their full desired position instantly without moving the market. Their gradual accumulation or distribution creates predictable directional pressure over hours to days.
3. **Leverage and liquidation cascades:** The perpetual futures market is highly leveraged. When price moves against crowded positions, liquidations trigger market orders that amplify the move in a self-reinforcing cascade.
4. **Information diffusion:** Fundamental news (regulatory, adoption, macro) takes time to be fully incorporated into price as market participants learn about and react to developments at different speeds.

The Donchian channel (N-bar high/low breakout) is one of the oldest and most robust trend-following systems, dating to Richard Donchian's work in the 1960s. It captures trends by entering when price breaks to new highs or lows over a lookback window.

Academic research confirms that Donchian-style trend-following can work on BTC when combined with sensible cost control and medium-term horizons.

This hypothesis tests whether a simple Donchian breakout on 4h bars generates positive risk-adjusted returns after realistic transaction costs.

## Testable Prediction

A Donchian channel breakout strategy on BTCUSDT perpetual 4h bars will:
1. Generate OOS Sharpe >= 1.0 net of fees (4bps taker, 2bps slippage)
2. Capture both bullish and bearish trend regimes
3. Exhibit positive skewness (let winners run, cut losers)
4. Survive walk-forward validation with efficiency > 0.5

## Primary Timeframe
4h

**Justification:** The 4h timeframe balances signal quality with cost efficiency:
- **Signal quality:** enough bars to detect meaningful trends
- **Cost efficiency:** lower trade frequency than 1h or shorter timeframes
- **Research fit:** aligns with the current Phase 2 dataset and expected signal horizon

## Confirmation Timeframes
1d (optional enhancement, not in baseline)

**Justification:** A 1d regime filter could reduce whipsaws during ranging / choppy markets. Per D2-015, confirmation timeframes must be coarser than primary. This would be tested as H-002b if baseline H-002 shows promise.

## Required Data
- Instrument: BTCUSDT Binance USDT-M Perpetual
- Required streams: 4h OHLCV
- Optional: 1d OHLCV (for confirmation variant)
- Evaluation range: Full history (2020-01-01 to present, per data_catalog.md)

## Signal Logic

INPUTS:
- `ohlcv_4h`: 4h OHLCV bars with columns `[open, high, low, close, volume]`

PARAMETERS:
- `lookback`: 20 (number of 4h bars = 80 hours ~= 3.3 days)

PREPROCESSING:
1. Compute `upper_band[t] = max(high[t-lookback : t-1])` - highest high over lookback, excluding current bar
2. Compute `lower_band[t] = min(low[t-lookback : t-1])` - lowest low over lookback, excluding current bar

SIGNAL GENERATION (at each bar close):
1. If `close[t] > upper_band[t]`: signal = +1 (LONG)
2. Else if `close[t] < lower_band[t]`: signal = -1 (SHORT)
3. Else: signal = `signal[t-1]` (HOLD current position)

INITIALIZATION:
- `signal[0 : lookback] = 0` (flat during warmup period)

POSITION LOGIC:
- Position changes only on signal change
- No partial positions
- Position size: 1x notional (no volatility scaling in baseline)

EXIT LOGIC:
- Exit long on short signal (reverse)
- Exit short on long signal (reverse)
- No stop-loss in baseline

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
- No profitable year in the OOS window -> archive hypothesis
- Win rate < 30% AND average win < 2x average loss -> archive hypothesis

## Free Parameters
1. **lookback** (default: 20) - number of 4h bars for channel calculation

**Count: 1** (well under 5-parameter cap per D2-006)

## Expected Trial Count
- Baseline (lookback=20): 1 trial
- Lookback sensitivity sweep (10, 15, 20, 25, 30, 40): 6 trials
- With 1d confirmation filter (if baseline promising): +6 trials
- **Conservative estimate: 7-13 trials**

## Artefacts
- Notebook: `research/hypotheses/H-002/experiment.ipynb` (to be created in execution package)
- Decision record: `research/decisions/DEC-0002.md` (to be created after evaluation)

## Decision Record
- Outcome: NO-GO
- Record: `research/decisions/DEC-0002.md`

## Notes
- Donchian channel is chosen over moving average crossover for simplicity: 1 parameter vs 2.
- This is a pure price-based strategy - funding costs are incurred but not used as a signal.
