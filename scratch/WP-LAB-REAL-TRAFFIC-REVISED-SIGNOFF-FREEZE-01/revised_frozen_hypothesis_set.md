# Revised Frozen Hypothesis Set - WP-LAB-REAL-TRAFFIC-REVISED-SIGNOFF-FREEZE-01

- Frozen set ID: `LAB-RT-REVISED-FROZEN-SET-001`
- Main authorization present: `true`
- Karl signoff present: `true`
- Main decision: `authorized_as_is`
- Hypothesis count: `4`
- Non-promotion posture: preserved
- Stop-and-surface rule: if any hypothesis screens GO later, execution must stop and surface to Karl as a real candidate decision before admission, crossing, readiness, paper/live, or runtime action.

## Freeze Conditions

- `LAB-RT-HYP-004R`: session filter must be load-bearing; `session_hours_utc` remains an explicit denominator axis or equivalent load-bearing gate; `weekend_allowed=false` remains fixed; formalization must not reduce to EMA/SMA momentum with a cosmetic session wrapper.
- `LAB-RT-HYP-003R`: `pass_with_caution` context must carry into future result records; interpretation must read against `RP-7134 / STRAT-SPEC-0003`; mechanics remain rolling-VWAP anchor + ATR distance + RSI exhaustion/neutrality, not SMA/stddev z-score.
- `LAB-RT-HYP-004R`: `pass_with_caution` context must carry into future result records; interpretation must read against `RP-2592 / RP-3731 / RP-6236`; mechanics remain EMA-side body/ATR impulse + RVOL + UTC session filter, not fast/slow SMA crossover momentum.

## LAB-RT-HYP-001 - BTCUSDT 4h no-wick EMA retest continuation

- Supported family route: `price_only_ohlcv.no_wick_ema_retest_4h`
- Distinctness result: `retained_by_main_decision_not_rechecked_in_this_packet`
- Distinctness source: `scratch/WP-LAB-REAL-TRAFFIC-DISTINCTNESS-CHECKS-01/revised_set_after_distinctness.json`
- Denominator: All 8 predeclared variants from wick_threshold x body_threshold x atr_stop_multiple are retained, including completed, failed, invalid, blocked, data-unavailable, withheld, no-trade, and NO-GO rows.
- Non-promotion posture: `True`

## LAB-RT-HYP-002R - BTCUSDT 15m RVOL-gated range-expansion breakout

- Supported family route: `price_only_ohlcv.rvol_range_expansion_breakout_15m`
- Distinctness result: `pass`
- Distinctness source: `scratch/WP-LAB-REAL-TRAFFIC-DISTINCTNESS-CHECKS-01/hyp_002r_donchian_distinctness_check.json`
- Denominator: All 8 predeclared variants from rvol_lookback_bars x rvol_min x range_atr_min are retained, including completed, failed, invalid, blocked, data-unavailable, withheld, no-trade, and NO-GO rows.
- Non-promotion posture: `True`

## LAB-RT-HYP-003R - BTCUSDT 15m rolling VWAP distance reversion

- Supported family route: `price_only_ohlcv.rolling_vwap_distance_reversion_15m`
- Distinctness result: `pass_with_caution`
- Distinctness source: `scratch/WP-LAB-REAL-TRAFFIC-DISTINCTNESS-CHECKS-01/hyp_003r_rp7134_distinctness_check.json`
- Denominator: All 8 predeclared variants from rolling_vwap_lookback_bars x distance_atr_entry x rsi_extreme are retained, including completed, failed, invalid, blocked, data-unavailable, withheld, no-trade, and NO-GO rows.
- Non-promotion posture: `True`
- Result context flags: `pass_with_caution`, `future result records must carry pass_with_caution context`, `interpret future result records against RP-7134 / STRAT-SPEC-0003 context`

## LAB-RT-HYP-004R - BTCUSDT 15m session-filtered EMA impulse continuation

- Supported family route: `price_only_ohlcv.session_ema_impulse_continuation_15m`
- Distinctness result: `pass_with_caution`
- Distinctness source: `scratch/WP-LAB-REAL-TRAFFIC-DISTINCTNESS-CHECKS-01/hyp_004r_momentum_distinctness_check.json`
- Denominator: All 8 predeclared variants from ema_lookback_bars x body_atr_min x session_hours_utc with fixed rvol_min and weekend filter are retained, including completed, failed, invalid, blocked, data-unavailable, withheld, no-trade, and NO-GO rows.
- Non-promotion posture: `True`
- Result context flags: `pass_with_caution`, `future result records must carry pass_with_caution context`, `interpret future result records against RP-2592 / RP-3731 / RP-6236 context`, `load-bearing session filter required`
