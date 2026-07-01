# Revised Real-Traffic Acceptance-Batch Proposal

Package: `WP-LAB-REAL-TRAFFIC-FRESH-REPLACEMENTS-01`

Status: review packet only. This is not a frozen set, not Karl sign-off, not Main verification, not execution authority, and not candidate/crossing/promotion/paper-live authority.

## Set

| ID | Name | Action | Supported route | Denominator |
| --- | --- | --- | --- | ---: |
| `LAB-RT-HYP-001` | BTCUSDT 4h no-wick EMA retest continuation | retained unchanged | `price_only_ohlcv.no_wick_ema_retest_4h` | 8 |
| `LAB-RT-HYP-002R` | BTCUSDT 15m RVOL-gated range-expansion breakout | replacement | `price_only_ohlcv.rvol_range_expansion_breakout_15m` | 8 |
| `LAB-RT-HYP-003R` | BTCUSDT 15m rolling VWAP distance reversion | replacement | `price_only_ohlcv.rolling_vwap_distance_reversion_15m` | 8 |
| `LAB-RT-HYP-004R` | BTCUSDT 15m session-filtered EMA impulse continuation | replacement | `price_only_ohlcv.session_ema_impulse_continuation_15m` | 8 |

Replaced: `LAB-RT-HYP-002`, `LAB-RT-HYP-003`, `LAB-RT-HYP-004`.

Reduced batch: no. Three replacements passed the proposal-stage freshness screen.

## Replacement Summaries

### `LAB-RT-HYP-002R`

RVOL-gated range-expansion breakout tests abnormal participation plus ATR-normalized candle expansion. It is not Donchian, not ORB, not Bollinger squeeze, not SMA crossover, and not funding/premium/basis based.

Freshness result: `pass`.

### `LAB-RT-HYP-003R`

Rolling VWAP distance reversion tests reversion to a volume-weighted OHLCV fair-value proxy using ATR distance and RSI exhaustion. It is not SMA/stddev z-score, not SMA-band, not Bollinger, and not basis/premium.

Freshness result: `pass_with_caution`, because it remains a broad reversion family but is structurally distinct from concluded fade families.

### `LAB-RT-HYP-004R`

Session-filtered EMA impulse continuation tests high-liquidity UTC session impulse follow-through using EMA side, ATR body, RVOL, and timestamp-derived filters. It is not SMA crossover, not ORB, not Donchian, not MTF alignment, and not the retained 4h no-wick EMA retest.

Freshness result: `pass_with_caution`, because it mentions EMA like retained HYP-001 but differs in timeframe, trigger, and session conditioning.

## Required Next Human Steps

- Main verification remains required.
- Karl sign-off remains required.
- No signed frozen-set artifacts were created by this package.

## Boundary

No research execution, Strategy Spec, Variant Manifest, Sweep Plan, Result Population, candidate admission, canonical crossing, promotion/readiness, paper/live/runtime contact, private provider/API use, notification sending, autonomous scheduler activation, dependency change, or protected-path change occurred.
