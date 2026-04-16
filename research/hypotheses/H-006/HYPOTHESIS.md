# Hypothesis H-006: 30-Minute Bollinger Band Squeeze Breakout

## Hypothesis ID
H-006

## Metadata
- Created: 2026-04-15
- Status: CONCLUDED
- Owner: WP-3a2

## Economic Rationale

BTCUSDT volatility can cycle between contraction and expansion. A Bollinger Band squeeze may identify compression regimes where a subsequent breakout is more likely to carry directional momentum. This is a research-informed volatility-breakout candidate, not a repo-proven edge.

The candidate rationale is:

1. **Markets cycle between contraction and expansion:** Low realized volatility can precede larger directional moves.
2. **Post-squeeze expansion is a plausible momentum event:** A close outside the bands after compression may indicate that directional pressure is emerging.
3. **The 30m timeframe is an active intraday layer:** It may offer useful signal count for the desired daily opportunity set, but it is more vulnerable to noise and cost drag than 1h or 1d.
4. **Patience is the main edge thesis:** The squeeze filter avoids treating every band breakout as actionable.

This candidate remains to be validated in the repo's backtest, evaluation, and trial-log process.

## Testable Prediction

A 30-minute Bollinger Band squeeze breakout strategy on BTCUSDT perpetuals will:

1. Generate OOS Sharpe >= 1.0 net of modeled costs
2. Capture directional expansion after volatility compression
3. Keep turnover controlled enough that cost drag remains within D2-006 limits
4. Survive walk-forward validation with efficiency > 0.5

## Primary Timeframe
30m

**Justification:** The 30m timeframe is an active intraday candidate layer in the broader multi-timeframe research portfolio. It may provide a usable compromise between trade frequency and noise, but it is more exposed to cost drag than 1h or 1d. The squeeze condition is required to keep this candidate controlled.

## Confirmation Timeframes
None

## Required Data
- Instrument: BTCUSDT Binance USDT-M Perpetual
- Required streams: 30m OHLCV
- Extra data required: None
- Evaluation range: Full history (2020-01-01 to present, per data_catalog.md)

## Signal Logic

INPUTS:
- `ohlcv_30m`: 30m OHLCV bars with columns `[open, high, low, close, volume]`

INDICATORS:
- Bollinger Bands using a 20-period SMA and 2 standard deviations
- `middle_band[t] = SMA(close, bb_period)`
- `upper_band[t] = middle_band[t] + bb_std_dev * rolling_std(close, bb_period)`
- `lower_band[t] = middle_band[t] - bb_std_dev * rolling_std(close, bb_period)`
- `band_width[t] = (upper_band[t] - lower_band[t]) / middle_band[t]`
- `band_width_percentile[t]` over the trailing 20 periods
- Squeeze active when `band_width_percentile[t] < squeeze_percentile`
- ATR(14) for risk framing

PARAMETERS:
- `bb_period`: 20
- `bb_std_dev`: 2.0
- `squeeze_percentile`: 20
- `atr_multiplier`: 1.5
- `risk_reward_ratio`: 2

SIGNAL GENERATION (at each 30-minute bar close):
1. If squeeze is active and `close[t] > upper_band[t]`: signal = +1 (LONG)
2. If squeeze is active and `close[t] < lower_band[t]`: signal = -1 (SHORT)
3. Else: hold current position unless an exit condition fires

POSITION LOGIC:
- Position changes only on signal change or exit
- No partial positions
- Position size: 1x baseline notional

EXIT LOGIC:
- Stop distance = 1.5 * ATR(14)
- Target distance = 2 * stop distance
- Time stop = 20 bars
- Baseline should keep ATR stop, fixed R:R, and time-stop framing interpretable and controlled

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

Baseline execution status: completed in WP-3c; baseline decision is NO-GO.

## Kill Criteria
- OOS Sharpe < 0.3 after baseline test -> archive hypothesis
- Max drawdown > 35% in any walk-forward fold -> archive hypothesis
- Cost drag > 50% of gross PnL after baseline test -> archive hypothesis
- Squeeze filter fails to improve breakout selectivity or materially worsens gate performance -> archive hypothesis
- Time-stop exits dominate results in a way that indicates no durable breakout follow-through -> archive hypothesis

## Free Parameters
1. **bb_period** (default: 20; sensitivity range: 15-30) - Bollinger Band lookback
2. **bb_std_dev** (default: 2.0; sensitivity range: 1.5-2.5) - band distance from the middle band
3. **squeeze_percentile** (default: 20; sensitivity range: 10-30) - squeeze threshold for BandWidth percentile
4. **atr_multiplier** (default: 1.5; sensitivity range: 1.0-2.0) - ATR stop multiplier
5. **risk_reward_ratio** (default: 2; sensitivity range: 1.5-3) - fixed target distance relative to stop distance

**Count: 5** (at the D2-006 parameter cap)

## Expected Trial Count
- Baseline (20-period BB, 2 std dev, squeeze percentile 20, ATR multiplier 1.5, risk-reward ratio 2): 1 trial
- One-at-a-time parameter sensitivity: 10-15 trials
- Combined grid only if baseline is promising: up to 25 trials
- **Conservative estimate: 11-16 trials**

## Artefacts
- Notebook: `research/hypotheses/H-006/experiment.ipynb`
- Decision record: `research/decisions/DEC-0006.md`

## Decision Record
- Outcome: NO-GO
- Record: `research/decisions/DEC-0006.md`

## Notes
- Research support wording is intentionally cautious: BB squeeze logic is a known candidate family, not evidence of profitability in this repo.
- If 30m OHLCV is unavailable to a future executor, report it as a data blocker while preserving this pre-registration.
- This candidate has now been evaluated in the repo's backtest, evaluation, and trial-log process and did not survive baseline gates.
- The result argues for caution before faster 15m breakout expansion because noise, drawdown, and negative risk-adjusted performance dominated this 30m baseline.
