# WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-UNBLOCK-01

**Status:** complete (partial unblock — infrastructure ready, data and specs deferred)
**Date:** 2026-06-26
**Base commit:** efd30d0 (origin/main after PR #578 merge)
**Branch:** research/funding-riskmanaged-triage-unblock-01

---

## Source Blocker (from PR #578)

`WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-RUN-01` was blocked with three blockers:

**Primary:** The offline runner (`tools/research_runner/run_offline_sweep.py`) had no
evaluation-window support. Running on only the 2024 CSV would violate the required
180-day funding-percentile warmup; running on warmup+2024 would score warmup rows.

**Secondary 1:** `exit_logic.atr_stop` is parent-spec-level, requiring multiple scratch
parent specs or a wrapper for the 108-row denominator.

**Secondary 2:** No runner-consumable BTCUSDT 15m funding-feature CSV existed in the
worktree or main checkout processed directory.

---

## Implementation Summary

### 1. Evaluation-window support (primary blocker resolved)

Added to `tools/research_runner/run_offline_sweep.py`:

- `_validate_evaluation_window(evaluation_start, evaluation_end, ohlcv)` — fails closed
  on invalid/outside/too-narrow windows.
- `_mask_signal_before_window(signal, evaluation_start)` — forces signal to 0.0 for all
  bars before `evaluation_start`, preventing pre-window entries.
- `_metrics_from_backtest_windowed(result, freq, evaluation_start, evaluation_end)` —
  restricts equity-curve metrics to `[evaluation_start, evaluation_end)`.
- Modified `_run_canonical_15m_backtest` to accept and apply the evaluation window.
- Threaded `evaluation_start`/`evaluation_end` through `_execute_variant_worker`,
  `_execute_rows`, `_execute_rows_parallel`, `_build_result_population`,
  `run_offline_sweep`.
- Added `--evaluation-start` and `--evaluation-end` CLI arguments.
- Evaluation window notes added to `data_coverage_notes` in result population payload.

### 2. ATR denominator bundler (secondary blocker 1 resolved)

Created `tools/research_runner/atr_denominator_bundler.py`:

- `bundle_atr_denominator(no_atr_rows, atr_20_rows, atr_30_rows)` — combines three
  36-row slices into one 108-row table with `risk_control_state` and `composite_row_id`.
- `validate_bundle_denominator_integrity(bundle)` — verifies 108-row count, 36 per
  state, unique composite IDs.
- Route plan documented in `scratch/.../atr_parent_spec_route_plan.md`.
- Three scratch parent specs NOT created in this package (deferred to Stage-1 retry).

### 3. Funding-feature data preflight (secondary blocker 2 documented)

- `scratch/.../funding_feature_data_preflight.json` documents the materialization command.
- Source files confirmed present in main checkout (base OHLCV CSV + full-history funding
  Parquet).
- Runner-consumable CSV is MISSING; must be created by next package.

---

## Tests Run

| Test suite | Result |
|---|---|
| `tests/test_evaluation_window.py` (15 new tests) | 15 passed |
| `tests/test_offline_research_runner.py` (101 existing tests) | 101 passed, 0 failures |
| `tests/test_funding_feature_materialization.py` | 5 passed |
| `tools.research_query.run --list-views` | OK |
| `tools.registry.validate_result_populations` | OK |
| `tools.registry.validate_candidate_registry` | OK |
| `tools/dev/diff_scope_summary.py` | No forbidden-path matches |
| `git diff --check` | No whitespace errors |

---

## Readiness

| Gate | Status |
|---|---|
| Evaluation-window route ready | YES |
| Pre-window position guard ready | YES |
| ATR parent-spec route ready | YES (bundler implemented; specs deferred) |
| Funding-feature data ready | NO (CSV missing) |
| **Stage-1 retry ready** | **NO** |

---

## Remaining Blockers

1. **Funding-feature CSV missing.** Run `materialize_funding_feature` in the main checkout
   using the command in `funding_feature_data_preflight.json`.

2. **Three scratch parent Strategy Specs not created.** The Stage-1 retry package must
   create `no_atr`, `atr_20`, and `atr_30` scratch specs with 36-variant manifests and
   sweep plans each, then run and bundle.

## Next Required Package

`WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-STAGE1-RETRY-01`

---

## Boundary Statement

- Stage-1 full triage run executed: **NO**
- Stage 2 authorized: **NO**
- Canonical Result Population written: **NO**
- Candidate lifecycle write: **NO**
- Paper/live/runtime paths touched: **NO**
- OMS/risk/reconciliation/order/exchange: **NO**
- Funding P&L/accounting changed: **NO**
- Private provider/API access: **NO**
- Data committed: **NO**

---

## PR

See PR for this branch (research/funding-riskmanaged-triage-unblock-01).
