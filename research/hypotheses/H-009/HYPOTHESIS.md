# Hypothesis H-009: Multi-Timeframe Trend Alignment

## Hypothesis ID
H-009

## Metadata
- Created: 2026-04-16
- Status: CONCLUDED
- Owner: WP-4a

## Economic Rationale

H-005 and H-006 both showed that intraday signals can be overwhelmed by cost drag, drawdown, and noise. This hypothesis tests whether a 30m trigger becomes more selective when it is allowed only during aligned 1h and 4h trend states.

The candidate rationale is:

1. **Intraday triggers need stronger context:** Single-timeframe 1h and 30m baselines did not survive gates.
2. **Coarser trend alignment may reduce chop:** Requiring 1h and 4h agreement can filter countertrend and range-bound entries.
3. **The design follows D2-015:** confirmation timeframes are coarser than the 30m primary timeframe.
4. **This is materially distinct from H-005/H-006:** the core edge thesis is multi-timeframe agreement, not a single indicator or squeeze condition.

## Testable Prediction

A 30m trend-trigger strategy gated by 1h and 4h trend alignment on BTCUSDT perpetuals will:

1. Generate OOS Sharpe >= 1.0 net of modeled costs
2. Reduce false intraday entries relative to single-timeframe intraday baselines
3. Keep turnover controlled enough that cost drag remains within D2-006 limits
4. Survive walk-forward validation with efficiency > 0.5

## Primary Timeframe
30m

**Justification:** The 30m timeframe remains in PLANNING after one failed candidate cycle. It offers enough observations for intraday research, but the failed H-006 baseline argues for strong filtering. Multi-timeframe alignment is the required filter for this candidate.

## Confirmation Timeframes
1h, 4h

**Justification:** Both confirmation timeframes are coarser than the 30m primary timeframe, satisfying D2-015. The 1h state filters near-term trend, and the 4h state filters broader directional regime.

## Required Data
- Instrument: BTCUSDT Binance USDT-M Perpetual
- Required streams: 30m OHLCV, 1h OHLCV, 4h OHLCV, 8h funding rates for cashflow accounting
- Extra data required: None
- Evaluation range: Full history available in `docs/data_catalog.md`

## Signal Logic

INPUTS:
- `ohlcv_30m`: 30m OHLCV bars with columns `[open, high, low, close, volume]`
- `ohlcv_1h`: 1h OHLCV bars for confirmation
- `ohlcv_4h`: 4h OHLCV bars for confirmation
- `funding`: 8h funding-rate events for backtest cashflows

INDICATORS:
- `trigger_high_30m[t]` = highest 30m high over `trigger_lookback_30m`, excluding current bar
- `trigger_low_30m[t]` = lowest 30m low over `trigger_lookback_30m`, excluding current bar
- `trend_1h[t]` = +1 when 1h close is above its trend average, -1 when below
- `trend_4h[t]` = +1 when 4h close is above its trend average, -1 when below
- ATR(14) on 30m bars for risk framing

PARAMETERS:
- `trigger_lookback_30m`: 20
- `trend_lookback_1h`: 48
- `trend_lookback_4h`: 30
- `atr_multiplier`: 2.0
- `time_stop_bars`: 24

PREPROCESSING:
1. Compute 1h and 4h trend states at their own bar closes.
2. Align each coarser trend state to 30m bars using only the latest completed coarser bar.
3. Compute 30m trigger levels excluding the current bar.

SIGNAL GENERATION (at each 30m bar close):
1. If `close_30m[t] > trigger_high_30m[t]` and `trend_1h[t] = +1` and `trend_4h[t] = +1`: signal = +1 (LONG)
2. If `close_30m[t] < trigger_low_30m[t]` and `trend_1h[t] = -1` and `trend_4h[t] = -1`: signal = -1 (SHORT)
3. Else: hold current position unless an exit condition fires

POSITION LOGIC:
- Position changes only on signal change or exit
- No partial positions
- Position size: 1x baseline notional

EXIT LOGIC:
- Exit when 1h or 4h confirmation no longer agrees with the position direction
- Exit on an opposite 30m trigger
- Use `atr_multiplier * ATR(14)` as stop-distance framing
- Use `time_stop_bars` as maximum holding period

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
- Multi-timeframe alignment fails to reduce the intraday noise/cost failure mode from H-005/H-006 -> archive hypothesis
- Trade count is too sparse to support credible baseline evaluation -> archive hypothesis

## Free Parameters
1. **trigger_lookback_30m** (default: 20; sensitivity range: 12-40) - 30m breakout trigger lookback
2. **trend_lookback_1h** (default: 48; sensitivity range: 24-96) - 1h trend-state average
3. **trend_lookback_4h** (default: 30; sensitivity range: 15-60) - 4h trend-state average
4. **atr_multiplier** (default: 2.0; sensitivity range: 1.5-3.0) - ATR stop-distance framing
5. **time_stop_bars** (default: 24; sensitivity range: 12-48) - maximum holding period in 30m bars

**Count: 5** (at the D2-006 parameter cap)

## Expected Trial Count
- Baseline (default parameters): 1 trial
- One-at-a-time parameter sensitivity: 10-15 trials
- Combined grid only if baseline is promising: up to 25 trials
- **Conservative estimate: 11-16 trials**

## Artefacts
- Notebook: `research/hypotheses/H-009/experiment.ipynb` (to be created by execution package)
- Decision record: `research/decisions/DEC-0009.md` (to be created after evaluation)

## Decision Record
- Outcome: NO-GO
- Decision record: `research/decisions/DEC-0009.md`
- Trial ID: `7292282d-abcb-462c-8d4a-c8572ff529d7`
- Sharpe: -0.1638 | Max DD: 925.16% | Trades: 2148 | Gates passed: 2/8

## Notes
- This candidate should not be simplified into a single-timeframe breakout during implementation.
- Confirmation values must use completed 1h and 4h bars only; no lookahead from incomplete coarser bars.
