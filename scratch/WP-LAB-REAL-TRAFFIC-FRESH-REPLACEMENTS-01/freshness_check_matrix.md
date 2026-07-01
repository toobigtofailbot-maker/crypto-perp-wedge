# Freshness Check Matrix

| Constraint | `LAB-RT-HYP-002R` RVOL breakout | `LAB-RT-HYP-003R` VWAP reversion | `LAB-RT-HYP-004R` session EMA impulse |
| --- | --- | --- | --- |
| `H-002` / `H-012` Donchian | PASS: no Donchian channel | PASS: no Donchian channel | PASS: no Donchian channel |
| ORB / PR #598 `HYP-002` | PASS: not opening-range anchored | PASS: no ORB | PASS: session gate only, no ORB/retest |
| SMA crossover RPs | PASS: no crossover | PASS: no crossover | PASS: EMA side, no crossover |
| Z-score/SMA/stddev fade | PASS: continuation | PASS WITH CAUTION: reversion, but VWAP/RSI/ATR, not SMA/stddev | PASS: continuation |
| SMA-distance/SMA-band RPs | PASS | PASS WITH CAUTION: distance reversion, but volume-weighted anchor | PASS |
| Bollinger H-003/H-006 | PASS: no Bollinger squeeze | PASS WITH CAUTION: reversion, but no Bollinger/stddev | PASS |
| Funding families | PASS: OHLCV-only | PASS: OHLCV-only | PASS: OHLCV-only |
| Premium/basis families | PASS: OHLCV-only | PASS: OHLCV-only rolling VWAP | PASS: OHLCV-only |
| MACD / MTF alignment | PASS | PASS | PASS |
| Retained HYP-001 | PASS | PASS | PASS WITH CAUTION: EMA appears, but structure/timeframe differ |

Overall: all three replacements pass the freshness screen. `LAB-RT-HYP-003R` and `LAB-RT-HYP-004R` carry explicit caution labels because they share broad economic words with prior families, but their actual signal structures differ enough for proposal-stage review.
