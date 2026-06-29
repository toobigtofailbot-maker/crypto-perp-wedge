# WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01

**Status:** complete (data/spec preparation — Stage-1 execution pending Karl sign-off)
**Date:** 2026-06-27
**Base commit:** 0965851 (origin/main after PR #579 merge)
**Branch:** research/funding-triage-dataprep-01

---

## Package Identity

```
Package label: WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01
Package class: data/spec preparation only / no strategy execution / no canonical writes
Hypothesis: H-FUNDING-FADE-RISKMANAGED-01
```

---

## Source Merged PRs / Packets Used

| Source | PR / Status | Key Artifacts |
|---|---|---|
| WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-PREGATE-01 | PR #577 merged | Frozen hypothesis, evaluation window, risk-control ranges, denominator plan, stop/go criteria |
| WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-RUN-01 | PR #578 merged | Blocked run verdict, three blockers documented |
| WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-UNBLOCK-01 | PR #579 merged | Evaluation-window runner patch, ATR bundler, data preflight |

---

## Data Materialization Result

**Status: READY**

| Field | Value |
|---|---|
| Output path | `data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized_with_funding_rate.csv` |
| Materialization command | `python -m tools.data.materialize_funding_feature` (local files only) |
| Private API / fetch used | NO |
| SHA-256 | `70cbe2040c8fb5987b2971a13c8bd4f66e91152331d5b641d684673364be3931` |
| Row count | 220,128 |
| Coverage | 2020-01-01T00:00:00Z to 2026-04-11T23:45:00Z |
| Covers warmup requirement (≥ 2023-07-05) | YES |
| Covers evaluation window (through 2025-01-01) | YES |
| Columns present | timestamp, open, high, low, close, volume, funding_rate |
| Git tracking | local_ignored_data (.gitignore:14:/data/processed/**) |
| Data committed | NO |
| Manifest recorded | `funding_feature_materialization_report.json` |
| Materialization tests | 5 passed (test_funding_feature_materialization.py) |

---

## Spec / VM / Sweep Generation Result

**Status: COMPLETE — 3 parent specs, 3 × 36-row VMs, 3 sweep plans**

| Risk State | Spec ID | VM ID | SP ID | Rows | Spec Validates |
|---|---|---|---|---|---|
| no_atr | STRAT-SPEC-9601 | VM-9601 | SWEEP-PLAN-9601 | 36 | YES |
| atr_20 | STRAT-SPEC-9602 | VM-9602 | SWEEP-PLAN-9602 | 36 | YES |
| atr_30 | STRAT-SPEC-9603 | VM-9603 | SWEEP-PLAN-9603 | 36 | YES |

Denominator manifest: 108 rows total (`denominator_manifest.json`)

Composite ID convention: `{risk_state}:{signal_variant_id}`

Example: `no_atr:fl2880_tail10_90_exitfixed_hold16`

All specs are marked `non_canonical: true`, `execution_authorized: false`, `stage: stage_1_triage_input_prep_only`.

Exit mode is encoded as a free parameter (`exit_mode: enum`) in each parent spec for planning purposes. At execution time, the next authorized package must decompose to two runner invocations per risk state (one per exit mode), producing 6 × 18-row sub-runs that bundle into 3 × 36-row result populations, then into the 108-row denominator via `atr_denominator_bundler`.

---

## Frozen Fidelity Result

**Status: PASS**

- `signal_frozen_identical: true` — all 10 signal axes identical across no_atr / atr_20 / atr_30
- `risk_axis_only_difference: true` — only ATR-stop settings differ between parent specs
- `forbidden_changes_detected: []` — no forbidden changes
- `combined_rows: 108` — denominator count correct

Check artifact: `scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/frozen_fidelity_check.json`

---

## Karl Sign-Off Packet Path

`scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/karl_frozen_content_signoff_packet.md`

The packet surfaces:
- 2024 window rationale and regime-coverage statement
- Explicit no-outcome-peeking statement
- 108-row grid and three 36-row risk-control slices
- A-priori ATR ranges
- Signal-frozen identity check summary
- Frozen stop/go criteria
- Data materialization status
- Statement that Stage-1 execution remains blocked pending Karl sign-off

---

## Readiness State

| Gate | Status |
|---|---|
| Funding-feature CSV materialized | YES |
| Data not committed | YES |
| Three scratch parent specs created | YES |
| Three 36-row VMs and sweep plans created | YES |
| 108-row denominator manifest exists | YES |
| Frozen fidelity check passes | YES |
| Karl sign-off packet created | YES |
| Karl sign-off obtained | **NO** |
| Stage-1 execution authorized here | **NO** |
| Ready for Stage-1 after Karl sign-off | **YES** |

---

## Remaining Blockers

1. **Karl sign-off on frozen content not yet obtained.** Required before Stage-1 execution. Review `karl_frozen_content_signoff_packet.md`.

---

## Validation Summary

| Validator | Result |
|---|---|
| `tools.registry.validate_strategy_specs` (no_atr) | OK |
| `tools.registry.validate_strategy_specs` (atr_20) | OK |
| `tools.registry.validate_strategy_specs` (atr_30) | OK |
| Variant manifest validators | No repo validator; schema/consistency checks performed in-package |
| Sweep plan validators | No repo validator; schema/consistency checks performed in-package |
| `test_funding_feature_materialization.py` | 5 passed |
| `tools.research_query.run --list-views` | OK |
| `tools.registry.validate_result_populations` | OK |
| `tools.registry.validate_candidate_registry` | OK |
| `tools/dev/diff_scope_summary.py` | No forbidden-path matches |
| `git diff --check` | No whitespace errors |
| Full pytest | Not required (no code changes) |

---

## Boundary Statement

- Stage-1 triage run executed: **NO**
- Stage-2 authorized: **NO**
- Canonical Result Population written: **NO**
- Candidate lifecycle write: **NO**
- Paper/live/runtime paths touched: **NO**
- OMS/risk/reconciliation/order/exchange: **NO**
- Funding P&L/accounting changed: **NO**
- Private provider/API access: **NO**
- Data committed: **NO**
- Code changes: **NO** (all changes are scratch artifacts and docs/status only)

---

## Next Package

- **If Karl signs off:** `WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01` (Stage-1 execution)
- **If blocked:** N/A (not currently blocked beyond Karl sign-off)

---

## PR

[PR #580](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/580) — open, ready for review, not draft.
