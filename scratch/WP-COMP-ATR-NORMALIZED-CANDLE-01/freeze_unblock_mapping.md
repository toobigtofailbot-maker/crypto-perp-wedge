# Freeze Unblock Mapping

## Fact

- `LAB-RT-HYP-002R.range_atr_min` requires the current candle high-low range normalized by ATR.
- `LAB-RT-HYP-004R.body_atr_min` requires the current candle body normalized by ATR.

## Mapping

- `LAB-RT-HYP-002R.range_atr_min` maps to `candle_range_atr_ratio >= threshold`.
- `LAB-RT-HYP-004R.body_atr_min` maps to `candle_body_atr_ratio >= threshold`.

## Boundary

This package does not execute the real-traffic batch and does not modify the signed frozen set.
