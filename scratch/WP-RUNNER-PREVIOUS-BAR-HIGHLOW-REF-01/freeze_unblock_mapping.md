# Freeze Unblock Mapping

Frozen item: `LAB-RT-HYP-002R.previous_bar_high_low`

Mapping:

- `previous_bar_high` maps to a declared `previous_bar_refs` primitive with
  `primitive_ref.field="high"`.
- `previous_bar_low` maps to the same closed primitive with
  `primitive_ref.field="low"`.
- Both references use `lag_bars=1`, `source="ohlcv"`, and
  `missing_prior_policy="null_output"`.

Status: supported.

This package does not execute HYP-002R and does not modify the signed frozen
set.
