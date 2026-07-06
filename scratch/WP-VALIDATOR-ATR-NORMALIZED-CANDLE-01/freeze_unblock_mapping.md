# Freeze Unblock Mapping

## Fact

`scratch/WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01/blocked_reason.json` identifies validator non-alignment as the pre-execution blocker for exact ATR-normalized candle formalizations.

## Mapping

- `LAB-RT-HYP-002R.range_atr_min` maps to `atr_normalized_candle_ratio_v1.candle_range_atr_ratio >= threshold` and is validator accepted.
- `LAB-RT-HYP-004R.body_atr_min` maps to `atr_normalized_candle_ratio_v1.candle_body_atr_ratio >= threshold` and is validator accepted.

## Boundary

This artifact maps validator acceptance only. It does not create or modify a signed frozen set, Strategy Spec, Variant Manifest, Sweep Plan, Result Population, candidate record, crossing artifact, promotion/readiness artifact, or execution output.

