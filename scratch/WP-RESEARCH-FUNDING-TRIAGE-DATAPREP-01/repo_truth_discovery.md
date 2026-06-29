# Repo Truth Discovery
## Package: WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01

### Source Frozen Packet

`WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-PREGATE-01` (merged via PR #577 base chain)

Primary artifacts consumed:
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-PREGATE-01/selected_hypothesis.json`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-PREGATE-01/triage_window_selection.json`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-PREGATE-01/frozen_risk_control_ranges.json`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-PREGATE-01/triage_denominator_plan.json`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-PREGATE-01/stop_go_criteria.json`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-PREGATE-01/karl_signoff_packet.md`
- `docs/research/H_FUNDING_FADE_RISKMANAGED_TRIAGE_PREGATE.md`

### Source Blocked Run

`WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-RUN-01` (merged via PR #578)

Primary artifacts consumed:
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-RUN-01/blocked_reason.json`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-RUN-01/stage1_verdict.json`

Blocked for three reasons:
1. Runner had no evaluation-window support for warmup-prefix + 2024-only-scoring
2. exit_logic.atr_stop is parent-spec-level, requiring multiple scratch specs
3. Runner-consumable funding-feature CSV missing

### Source Unblock Package

`WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-UNBLOCK-01` (merged via PR #579)

Primary artifacts consumed:
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-UNBLOCK-01/funding_feature_data_preflight.json`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-UNBLOCK-01/stage1_retry_readiness.json`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-UNBLOCK-01/evaluation_window_semantics.md`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-UNBLOCK-01/atr_parent_spec_route_plan.md`

Unblock resolved:
- Primary blocker (evaluation window): RESOLVED — `run_offline_sweep` now accepts `--evaluation-start` and `--evaluation-end` with warmup-prefix semantics
- Secondary blocker 1 (ATR parent spec): RESOLVED — `tools/research_runner/atr_denominator_bundler.py` implemented; route plan documented
- Secondary blocker 2 (funding CSV): DEFERRED to this package

---

### Frozen Hypothesis ID

`H-FUNDING-FADE-RISKMANAGED-01`

---

### Frozen 2024 Evaluation Window

```
evaluation_start: 2024-01-01T00:00:00Z  (inclusive)
evaluation_end:   2025-01-01T00:00:00Z  (exclusive)
```

---

### Required Warmup Prefix

Warmup must begin no later than `2023-07-05T00:00:00Z`.

Rationale: the 180-day (17280 bar) funding percentile lookback requires 180 days of history before the evaluation window start (2024-01-01). 2023-07-05 is 180 days before 2024-01-01, ensuring the full-window lookback is available at the first evaluation bar.

---

### Frozen Signal Axes

These signal parameters are frozen-identical across all three parent specs (no_atr, atr_20, atr_30):

| Parameter | Values |
|---|---|
| symbol | BTCUSDT |
| timeframe | 15m |
| direction | contrarian funding-positioning fade |
| funding_lookback_bars | 2880, 8640, 17280 |
| entry tail pairs | 0.10/0.90 and 0.05/0.95 |
| exit modes | fixed_max_hold_only and midline_reversion_or_max_hold |
| max_hold_bars | 16, 32, 96 |
| funding payments / accounting | off |
| sizing_mode | dynamic_equity_target_leverage |
| target_leverage | 1.0 |

---

### Frozen Risk-Control States

Three parent-spec risk-control states (only axis allowed to differ across specs):

| State | atr_stop_enabled | atr_lookback | atr_multiplier | entry_reference_price | evaluation_price | evaluation_timing | Rows |
|---|---|---|---|---|---|---|---|
| no_atr | false | — | — | — | — | — | 36 |
| atr_20 | true | 14 | 2.0 | next_bar_open_pre_fee_slippage | close | bar_close | 36 |
| atr_30 | true | 14 | 3.0 | next_bar_open_pre_fee_slippage | close | bar_close | 36 |

---

### Data Materialization Command Source

From `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-UNBLOCK-01/funding_feature_data_preflight.json`:

```
python -m tools.data.materialize_funding_feature
  --ohlcv-path "data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv"
  --funding-path "data/processed/binance_um_perp_BTCUSDT_funding_8h_2019-09-10_2026-04-12_2026-04-12T1655Z.parquet"
  --availability-catalog-path "research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json"
  --output-path "data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized_with_funding_rate.csv"
  --manifest-path "data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized_with_funding_rate_manifest.json"
```

Local files only. No network/API/credentials required. Output is git-ignored.

---

### Validation / Input-Generation Route

From `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-UNBLOCK-01/atr_parent_spec_route_plan.md`:

1. Three scratch parent Strategy Specs (no_atr, atr_20, atr_30) — created by this package
2. 36-variant Manifest and Sweep Plan per spec — created by this package
3. At execution: each spec runs through `run_offline_sweep --canonical-15m --evaluation-start ... --evaluation-end ...`
4. At execution: three 36-row result populations bundled via `bundle_atr_denominator()`

Note: this package performs steps 1-2 only (data/spec preparation). Steps 3-4 require the next authorized execution package after Karl sign-off.

---

### Explicit Non-Execution Statement

**Stage-1 execution is not authorized in this package.**

This package is classified as `data/spec preparation only / no strategy execution / no canonical writes`. No backtest, sweep, strategy run, sidecar triage, result population write, candidate lifecycle write, or Stage-2 authorization occurs here.

Stage-1 execution remains blocked until:
1. This data-prep package confirms the three specs are signal-frozen and risk-axis-only
2. The frozen packet contents are surfaced for Karl
3. Karl signs off on the surfaced frozen content
