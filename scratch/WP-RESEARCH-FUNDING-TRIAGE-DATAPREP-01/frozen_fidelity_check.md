# Frozen Fidelity Check
## Package: WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01

**Result: PASS**

---

## 1. Signal Axes — Frozen Identical Across All Three Parent Specs

| Signal Axis | no_atr | atr_20 | atr_30 | Identical |
|---|---|---|---|---|
| symbol | BTCUSDT | BTCUSDT | BTCUSDT | YES |
| timeframe | 15m | 15m | 15m | YES |
| direction | both (contrarian) | both (contrarian) | both (contrarian) | YES |
| funding_lookback_bars | 2880, 8640, 17280 | 2880, 8640, 17280 | 2880, 8640, 17280 | YES |
| entry tail pairs | 0.10/0.90, 0.05/0.95 | 0.10/0.90, 0.05/0.95 | 0.10/0.90, 0.05/0.95 | YES |
| exit modes | fixed, midline | fixed, midline | fixed, midline | YES |
| max_hold_bars | 16, 32, 96 | 16, 32, 96 | 16, 32, 96 | YES |
| funding payments | off | off | off | YES |
| sizing_mode | dynamic_equity_target_leverage | dynamic_equity_target_leverage | dynamic_equity_target_leverage | YES |
| target_leverage | 1.0 | 1.0 | 1.0 | YES |

All 10 signal axes are frozen-identical. **Signal-frozen check: PASS.**

---

## 2. Risk-Control Axis — Only Allowed Differences

| Risk Setting | no_atr | atr_20 | atr_30 |
|---|---|---|---|
| atr_stop_enabled | false | **true** | **true** |
| atr_lookback | — | **14** | **14** |
| atr_multiplier | — | **2.0** | **3.0** |
| entry_reference_price | — | next_bar_open_pre_fee_slippage | next_bar_open_pre_fee_slippage |
| evaluation_price | — | close | close |
| evaluation_timing | — | bar_close | bar_close |

Risk-control differences are exactly as declared in `frozen_risk_control_ranges.json`. No other differences exist. **Risk-axis-only-difference check: PASS.**

---

## 3. Row Counts

| State | Rows |
|---|---|
| no_atr | **36** |
| atr_20 | **36** |
| atr_30 | **36** |
| **Combined** | **108** |

Grid formula: 3 funding lookbacks × 2 entry tail pairs × 2 exit modes × 3 max holds = 36 rows per state.

Combined denominator: 108 rows. **Row count check: PASS.**

---

## 4. Variant ID Identity

The 36 variant IDs within each risk state are identical to each other (same signal cells, different risk-control context). The composite ID convention `{risk_state}:{signal_variant_id}` ensures uniqueness across states.

Example first row composite IDs:
- `no_atr:fl2880_tail10_90_exitfixed_hold16`
- `atr_20:fl2880_tail10_90_exitfixed_hold16`
- `atr_30:fl2880_tail10_90_exitfixed_hold16`

**Variant ID identity check: PASS.**

---

## 5. Forbidden Change Checks

| Forbidden Change | Detected |
|---|---|
| funding lookbacks changed | NO |
| tail thresholds changed | NO |
| direction changed | NO |
| timeframe changed | NO |
| symbol changed | NO |
| filters added | NO |
| signal rows dropped | NO |
| new signal parameters added | NO |
| leverage swept | NO |
| funding P&L/accounting changed | NO |
| additional ATR multipliers added | NO |
| take-profit logic added | NO |
| additional stop variants added | NO |
| additional sizing variants added | NO |

**Forbidden changes check: PASS.**

---

## 6. Schema Validation

All three scratch parent Strategy Specs pass the `tools.registry.validate_strategy_specs` validator:
- `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/inputs/no_atr/strategy_spec.json`: **PASS**
- `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/inputs/atr_20/strategy_spec.json`: **PASS**
- `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/inputs/atr_30/strategy_spec.json`: **PASS**

---

## 7. Overall Conclusion

**Frozen fidelity check: PASS**

- Signal axes are frozen-identical across no_atr / atr_20 / atr_30
- Each risk state has the same 36 signal cells
- The only parent-spec differences are ATR-stop risk-control settings and required metadata/IDs
- No signal filters were added
- No signal thresholds changed
- No signal rows were dropped
- No extra risk-control states were added
- No leverage sweep was added
- No funding P&L/accounting change occurred
- Combined denominator is exactly 108 rows

Stage-1 execution remains blocked pending Karl sign-off. This check confirms the inputs are signal-frozen and risk-axis-only as required.
