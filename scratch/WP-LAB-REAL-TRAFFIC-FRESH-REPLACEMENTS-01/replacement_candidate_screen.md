# Replacement Candidate Screen

Package: `WP-LAB-REAL-TRAFFIC-FRESH-REPLACEMENTS-01`

## Accepted

| ID | Name | Supported route | Freshness result |
| --- | --- | --- | --- |
| `LAB-RT-HYP-002R` | BTCUSDT 15m RVOL-gated range-expansion breakout | `price_only_ohlcv.rvol_range_expansion_breakout_15m` | Accepted. Distinct from Donchian, ORB, and Bollinger squeeze because the trigger is abnormal participation plus range expansion. |
| `LAB-RT-HYP-003R` | BTCUSDT 15m rolling VWAP distance reversion | `price_only_ohlcv.rolling_vwap_distance_reversion_15m` | Accepted with caution. It is a reversion family, but the anchor is rolling candle-VWAP plus ATR/RSI context rather than SMA/stddev/Bollinger or basis/premium. |
| `LAB-RT-HYP-004R` | BTCUSDT 15m session-filtered EMA impulse continuation | `price_only_ohlcv.session_ema_impulse_continuation_15m` | Accepted. Distinct from SMA crossover and HYP-001 because it is 15m time-windowed impulse continuation, not crossover or 4h EMA retest. |

## Rejected During Screening

| Rejected idea | Reason |
| --- | --- |
| UTC opening-range breakout retest | Duplicate of PR #598 `LAB-RT-HYP-002` and prior ORB prereg surface. |
| SMA crossover continuation | Duplicate/retune of `RP-2592`, `RP-3731`, and `RP-6236`. |
| Z-score/SMA/stddev fade | Duplicate/retune of `RP-7134` and prior SMA freshness-blocked attempt. |
| Donchian trend continuation | Too close to `H-002` and `H-012`. |
| Funding carry/fade/filter | Too close to `H-001`, `H-007`, `H-012`, and funding scratch families. |

Batch result: three replacements passed freshness, so the batch is not reduced.
