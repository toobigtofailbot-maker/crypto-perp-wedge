# Pre-Execution Freeze Fidelity Check

Decision: execute `LAB-RT-HYP-002R` only.

- Previous-bar route: exact `previous_bar_high / previous_bar_low` primitive_ref route with `lag_bars=1`.
- Denominator axes: `rvol_lookback_bars x rvol_min x range_atr_min` = 8 rows.
- Substitution: none; no Donchian, ORB/session anchor, retuning, or parameter expansion.
- Signed frozen set modified: false.
