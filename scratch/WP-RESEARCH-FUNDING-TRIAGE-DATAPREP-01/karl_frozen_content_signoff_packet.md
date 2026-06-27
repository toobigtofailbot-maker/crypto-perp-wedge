# Karl Frozen Content Sign-Off Packet
## Package: WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01
## Date: 2026-06-27

**IMPORTANT: This packet is created for Karl's review. Creating this packet is not sign-off. Stage-1 execution remains blocked until Karl reviews and approves the content below.**

---

## 1. Hypothesis

**H-FUNDING-FADE-RISKMANAGED-01**

Prior funding positioning-fade signal, unchanged from concluded H-FUNDING-RATE-POSITIONING-FADE-01, with an a-priori offline risk layer (ATR stop) added to test whether bounded risk management changes the extreme-drawdown failure mode.

This is test traffic for the generic Side 12 lab. It is not a funding-specific lab pivot.

---

## 2. Evaluation Window

```
evaluation_start: 2024-01-01T00:00:00Z  (inclusive)
evaluation_end:   2025-01-01T00:00:00Z  (exclusive)
warmup_start_no_later_than: 2023-07-05T00:00:00Z
```

**Why this window:**

Calendar year 2024 is a completed mixed BTC market year in the available full-history era. It contains strong directional movement, mid-year range/chop, and renewed late-year trend conditions. It is not the most recent year by default and was not selected from any H-FUNDING-FADE-RISKMANAGED-01 performance result.

**Explicit statement that the window was not selected from strategy outcomes:**

The window was selected from calendar and non-strategy market-regime coverage only. No strategy return, Sharpe, drawdown, variant PnL, or winner cell was used to select this window.

**Warmup prefix requirement:**

The 180-day (17280 bar) funding percentile lookback requires 180 days of history before 2024-01-01. The warmup prefix must begin no later than 2023-07-05T00:00:00Z. The materialized runner-consumable CSV covers from 2020-01-01T00:00:00Z, which satisfies this requirement.

---

## 3. Signal Family — Frozen Identical to Prior Concluded Run

The prior concluded family `H-FUNDING-RATE-POSITIONING-FADE-01` preserved all 36 rows and failed primarily through extreme drawdown (80–100% drawdown range, all rows). The signal parameters are unchanged:

| Signal Parameter | Value |
|---|---|
| Symbol | BTCUSDT |
| Timeframe | 15m |
| Direction | Contrarian: positive funding extreme → short; negative funding extreme → long |
| Funding lookback bars | 2880 (30d), 8640 (90d), 17280 (180d) |
| Entry tail pairs | 0.10/0.90 and 0.05/0.95 |
| Exit modes | fixed_max_hold_only and midline_reversion_or_max_hold |
| Max hold bars | 16, 32, 96 |
| Funding payments/accounting | OFF — price-P&L only |
| Sizing mode | dynamic_equity_target_leverage |
| Target leverage | 1.0 (fixed, not swept) |

**No signal parameter was changed from the prior family.**

---

## 4. A-Priori ATR Risk-Control Ranges

The only variable axis added for this hypothesis is an ATR stop. The three risk-control states are:

| State | ATR Stop | ATR Lookback | ATR Multiplier | Entry Reference | Eval Price | Eval Timing | Rows |
|---|---|---|---|---|---|---|---|
| no_atr (control) | Disabled | — | — | — | — | — | 36 |
| atr_20 | Enabled | 14 bars | **2.0** | next_bar_open_pre_fee_slippage | close | bar_close | 36 |
| atr_30 | Enabled | 14 bars | **3.0** | next_bar_open_pre_fee_slippage | close | bar_close | 36 |

**Why these ATR ranges:**

- ATR lookback 14 is a standard volatility lookback; supported by the current compiler
- Multipliers 2.0 and 3.0 are narrow, standard volatility-stop distances that test tighter vs. looser risk control without a broad optimizer grid
- The no_atr control is required to verify that drawdown improvement is real, not an artifact of a prior full-history run
- No additional ATR multipliers were added

**Chosen without outcome peeking:** the multiplier range was selected from a-priori volatility-stop rationale and current primitive capability, not from any H-FUNDING-FADE-RISKMANAGED-01 backtest result.

---

## 5. Full 108-Row Grid

### 5a. Per-State Grid (identical signal cells across all three states)

For each of the three risk-control states (no_atr, atr_20, atr_30), the 36 signal cells are:

| # | fl_bars | lo_tail | hi_tail | exit_mode | max_hold | Variant ID |
|---|---|---|---|---|---|---|
| 1 | 2880 | 0.10 | 0.90 | fixed_max_hold_only | 16 | fl2880_tail10_90_exitfixed_hold16 |
| 2 | 2880 | 0.10 | 0.90 | fixed_max_hold_only | 32 | fl2880_tail10_90_exitfixed_hold32 |
| 3 | 2880 | 0.10 | 0.90 | fixed_max_hold_only | 96 | fl2880_tail10_90_exitfixed_hold96 |
| 4 | 2880 | 0.10 | 0.90 | midline_reversion_or_max_hold | 16 | fl2880_tail10_90_exitmidline_hold16 |
| 5 | 2880 | 0.10 | 0.90 | midline_reversion_or_max_hold | 32 | fl2880_tail10_90_exitmidline_hold32 |
| 6 | 2880 | 0.10 | 0.90 | midline_reversion_or_max_hold | 96 | fl2880_tail10_90_exitmidline_hold96 |
| 7 | 2880 | 0.05 | 0.95 | fixed_max_hold_only | 16 | fl2880_tail05_95_exitfixed_hold16 |
| 8 | 2880 | 0.05 | 0.95 | fixed_max_hold_only | 32 | fl2880_tail05_95_exitfixed_hold32 |
| 9 | 2880 | 0.05 | 0.95 | fixed_max_hold_only | 96 | fl2880_tail05_95_exitfixed_hold96 |
| 10 | 2880 | 0.05 | 0.95 | midline_reversion_or_max_hold | 16 | fl2880_tail05_95_exitmidline_hold16 |
| 11 | 2880 | 0.05 | 0.95 | midline_reversion_or_max_hold | 32 | fl2880_tail05_95_exitmidline_hold32 |
| 12 | 2880 | 0.05 | 0.95 | midline_reversion_or_max_hold | 96 | fl2880_tail05_95_exitmidline_hold96 |
| 13 | 8640 | 0.10 | 0.90 | fixed_max_hold_only | 16 | fl8640_tail10_90_exitfixed_hold16 |
| 14 | 8640 | 0.10 | 0.90 | fixed_max_hold_only | 32 | fl8640_tail10_90_exitfixed_hold32 |
| 15 | 8640 | 0.10 | 0.90 | fixed_max_hold_only | 96 | fl8640_tail10_90_exitfixed_hold96 |
| 16 | 8640 | 0.10 | 0.90 | midline_reversion_or_max_hold | 16 | fl8640_tail10_90_exitmidline_hold16 |
| 17 | 8640 | 0.10 | 0.90 | midline_reversion_or_max_hold | 32 | fl8640_tail10_90_exitmidline_hold32 |
| 18 | 8640 | 0.10 | 0.90 | midline_reversion_or_max_hold | 96 | fl8640_tail10_90_exitmidline_hold96 |
| 19 | 8640 | 0.05 | 0.95 | fixed_max_hold_only | 16 | fl8640_tail05_95_exitfixed_hold16 |
| 20 | 8640 | 0.05 | 0.95 | fixed_max_hold_only | 32 | fl8640_tail05_95_exitfixed_hold32 |
| 21 | 8640 | 0.05 | 0.95 | fixed_max_hold_only | 96 | fl8640_tail05_95_exitfixed_hold96 |
| 22 | 8640 | 0.05 | 0.95 | midline_reversion_or_max_hold | 16 | fl8640_tail05_95_exitmidline_hold16 |
| 23 | 8640 | 0.05 | 0.95 | midline_reversion_or_max_hold | 32 | fl8640_tail05_95_exitmidline_hold32 |
| 24 | 8640 | 0.05 | 0.95 | midline_reversion_or_max_hold | 96 | fl8640_tail05_95_exitmidline_hold96 |
| 25 | 17280 | 0.10 | 0.90 | fixed_max_hold_only | 16 | fl17280_tail10_90_exitfixed_hold16 |
| 26 | 17280 | 0.10 | 0.90 | fixed_max_hold_only | 32 | fl17280_tail10_90_exitfixed_hold32 |
| 27 | 17280 | 0.10 | 0.90 | fixed_max_hold_only | 96 | fl17280_tail10_90_exitfixed_hold96 |
| 28 | 17280 | 0.10 | 0.90 | midline_reversion_or_max_hold | 16 | fl17280_tail10_90_exitmidline_hold16 |
| 29 | 17280 | 0.10 | 0.90 | midline_reversion_or_max_hold | 32 | fl17280_tail10_90_exitmidline_hold32 |
| 30 | 17280 | 0.10 | 0.90 | midline_reversion_or_max_hold | 96 | fl17280_tail10_90_exitmidline_hold96 |
| 31 | 17280 | 0.05 | 0.95 | fixed_max_hold_only | 16 | fl17280_tail05_95_exitfixed_hold16 |
| 32 | 17280 | 0.05 | 0.95 | fixed_max_hold_only | 32 | fl17280_tail05_95_exitfixed_hold32 |
| 33 | 17280 | 0.05 | 0.95 | fixed_max_hold_only | 96 | fl17280_tail05_95_exitfixed_hold96 |
| 34 | 17280 | 0.05 | 0.95 | midline_reversion_or_max_hold | 16 | fl17280_tail05_95_exitmidline_hold16 |
| 35 | 17280 | 0.05 | 0.95 | midline_reversion_or_max_hold | 32 | fl17280_tail05_95_exitmidline_hold32 |
| 36 | 17280 | 0.05 | 0.95 | midline_reversion_or_max_hold | 96 | fl17280_tail05_95_exitmidline_hold96 |

### 5b. Full 108-Row Composite Denominator Summary

| Slice | State | Rows | Composite ID pattern |
|---|---|---|---|
| 1–36 | no_atr | 36 | `no_atr:fl{fl}_tail{lo}_{hi}_exit{mode}_hold{hold}` |
| 37–72 | atr_20 | 36 | `atr_20:fl{fl}_tail{lo}_{hi}_exit{mode}_hold{hold}` |
| 73–108 | atr_30 | 36 | `atr_30:fl{fl}_tail{lo}_{hi}_exit{mode}_hold{hold}` |
| **Total** | | **108** | |

Full row list: `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/denominator_manifest.json`

---

## 6. Signal-Frozen Identity Check Summary

From `frozen_fidelity_check.json`:

- **signal_frozen_identical: true**
- **risk_axis_only_difference: true**
- **no_atr_rows: 36**
- **atr_20_rows: 36**
- **atr_30_rows: 36**
- **combined_rows: 108**
- **unexpected_signal_differences: []**
- **unexpected_risk_differences: []**
- **forbidden_changes_detected: []**
- **status: pass**

All three scratch Strategy Specs pass the schema validator.

---

## 7. Frozen Stop/Go Criteria

From `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-PREGATE-01/stop_go_criteria.json`:

**GO to Stage 2 only if ALL of the following are true:**
- Full 108-row denominator is complete
- At least one ATR-stop multiplier slice has median drawdown ≤ 35%
- Same slice has worst-row drawdown < 50%
- Same slice improves median drawdown by ≥ 20 absolute percentage points vs. the no-ATR control slice
- Same slice has positive median net return
- At least 4 rows in same slice have positive net return
- Effect appears across at least 2 funding lookbacks AND both entry tail pairs
- No single isolated parameter cell is the only evidence
- Real-runner reconciliation does not contradict any sidecar preview
- Funding P&L/accounting changes not required

**NO-GO if ANY of the following:**
- Denominator incomplete or winner-only reporting
- All ATR-stop multiplier slices have median drawdown > 35% or worst-row ≥ 50%
- Drawdown improves only because returns are killed
- Only one isolated row passes
- Effect confined to one funding lookback or one tail pair
- Sidecar and real runner diverge materially without resolution
- Run requires funding accounting, runtime/paper/live, or protected paths

---

## 8. No-Outcome-Peeking Statement

No strategy run, backtest, sweep, sidecar triage, or result inspection has occurred in any prior package up to and including this data-prep package.

The evaluation window was selected from calendar and non-strategy market-regime coverage, not from H-FUNDING-FADE-RISKMANAGED-01 performance results. The signal parameters are frozen from the prior concluded family. The ATR multiplier range (2.0 and 3.0) was selected from a-priori volatility-stop rationale, not from any strategy outcome.

---

## 9. Data Materialization Status

**Runner-consumable CSV: READY**

```
path: data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized_with_funding_rate.csv
sha256: 70cbe2040c8fb5987b2971a13c8bd4f66e91152331d5b641d684673364be3931
row_count: 220128
coverage_start: 2020-01-01T00:00:00Z
coverage_end: 2026-04-11T23:45:00Z
columns: timestamp, open, high, low, close, volume, funding_rate
git_tracking_status: local_ignored_data
private_api_or_fetch_used: false
```

The CSV was materialized from existing local files only:
- Source OHLCV CSV: present in main checkout
- Source funding Parquet: present in main checkout
- No exchange/API/network access required
- Generated data is not committed (git-ignored)

Coverage covers the required warmup prefix (from 2020-01-01, well before 2023-07-05 warmup requirement) and the full evaluation window (through 2026-04-11, past the 2025-01-01 evaluation end).

---

## 10. Stage-1 Execution Remains Blocked Pending Karl Sign-Off

**Stage-1 execution is not authorized until Karl signs off on the content above.**

The next authorized execution package (`WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01`) may proceed only after Karl explicitly approves:
1. The 2024 evaluation window
2. The frozen signal family
3. The three ATR risk-control states (no_atr, atr_20, atr_30)
4. The 108-row denominator
5. The a-priori stop/go criteria

**Karl sign-off obtained: NO** (this packet is prepared for review, not yet signed off)

---

## 11. Scratch Artifacts Created by This Package

| Artifact | Path |
|---|---|
| Repo truth discovery | `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/repo_truth_discovery.md` |
| Materialization report | `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/funding_feature_materialization_report.json` |
| no_atr strategy spec | `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/inputs/no_atr/strategy_spec.json` |
| no_atr variant manifest | `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/inputs/no_atr/variant_manifest.json` |
| no_atr sweep plan | `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/inputs/no_atr/sweep_plan.json` |
| atr_20 strategy spec | `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/inputs/atr_20/strategy_spec.json` |
| atr_20 variant manifest | `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/inputs/atr_20/variant_manifest.json` |
| atr_20 sweep plan | `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/inputs/atr_20/sweep_plan.json` |
| atr_30 strategy spec | `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/inputs/atr_30/strategy_spec.json` |
| atr_30 variant manifest | `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/inputs/atr_30/variant_manifest.json` |
| atr_30 sweep plan | `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/inputs/atr_30/sweep_plan.json` |
| Denominator manifest | `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/denominator_manifest.json` |
| Frozen fidelity check JSON | `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/frozen_fidelity_check.json` |
| Frozen fidelity check MD | `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/frozen_fidelity_check.md` |
| Karl sign-off packet | `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/karl_frozen_content_signoff_packet.md` (this file) |
| Stage-1 readiness | `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/stage1_execution_readiness.json` |
| Status entry | `docs/status_entries/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01.md` |
