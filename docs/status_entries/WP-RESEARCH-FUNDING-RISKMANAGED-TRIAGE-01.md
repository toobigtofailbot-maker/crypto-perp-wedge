# WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01 Status Entry

## Package Status

Complete: Stage-1 triage executed. Verdict: `no_go`.

## Base Commit

`ca3916a5b5d68e8239ec5753d2a27bd4bcea3632`

## Prerequisite PRs Consumed

PR #577, PR #578, PR #579, and PR #580 artifacts were present on refreshed `main` before branch work.

## Karl Authorization / Sign-off Consumed

Operator authorization in the attached execution package authorized this WP after the frozen content sign-off packet was surfaced. Stage-1 execution only was consumed; Stage-2 execution remains unauthorized.

## Data Preflight Result

Funding-feature CSV ready: `True`. Manifest ready: `True`. Path: `data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized_with_funding_rate.csv`. Checksum: `70cbe2040c8fb5987b2971a13c8bd4f66e91152331d5b641d684673364be3931`. Row count: `220128`. Coverage: `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`. Local files only: true. Private API/fetch used: false. Data committed: false.

## Execution Route Used

Six exit-mode-decomposed runner invocations:

- `no_atr / fixed_max_hold_only`
- `no_atr / midline_reversion_or_max_hold`
- `atr_20 / fixed_max_hold_only`
- `atr_20 / midline_reversion_or_max_hold`
- `atr_30 / fixed_max_hold_only`
- `atr_30 / midline_reversion_or_max_hold`

Repo-truth adjustments were required only for scratch runner compatibility: closed-schema copies stripped non-schema planning wrapper fields, mapped frozen descriptive variant IDs to `VAR-000001`-style runner IDs, normalized metadata enum values, and kept each sub-run at a 36-row committed denominator with the non-selected exit-mode rows explicitly excluded. Signal parameters, risk settings, sizing, data path, and evaluation window were unchanged.

## Row Accounting Summary

Planned denominator rows: 108. Final denominator rows: 108. Executed rows: 108. Blocked rows: 0. Errored rows: 0. Invalid rows: 0. Data-unavailable rows: 0.

Full 108-row denominator status: complete, no winner-only reporting.

## Slice Summaries

| Slice | Rows | Median DD | Worst DD | Median Net Return | Positive Rows |
|---|---:|---:|---:|---:|---:|
| no_atr | 36 | 0.497721 | 0.737582 | -0.459715 | 0 |
| atr_20 | 36 | 0.481411 | 0.729638 | -0.440943 | 0 |
| atr_30 | 36 | 0.507059 | 0.716278 | -0.464067 | 0 |

## Stop/Go Result

NO-GO. Reason: all ATR slices have median drawdown > 35% or worst-row drawdown >= 50%; drawdown improves only with non-positive median net return for every ATR slice.

## Stage-1 Verdict

`no_go`. Next package if continue: ``.

## Remaining Blockers

None for Stage-1 record completion. Stage-2 execution is not authorized.

## Validation Summary

- Strategy Spec validators: PASS using repo-native --strategy-specs-dir for no_atr, atr_20, atr_30; package-suggested positional path syntax is not supported by repo truth
- Runner/data tests: PASS: tests/test_evaluation_window.py 20 passed; tests/test_offline_research_runner.py 101 passed, 2 warnings; tests/test_funding_feature_materialization.py 5 passed
- Research query: PASS: python -m tools.research_query.run --list-views
- Result-population validator: PASS: python -m tools.registry.validate_result_populations
- Candidate-registry validator: PASS: python -m tools.registry.validate_candidate_registry
- Diff scope: PASS: python tools/dev/diff_scope_summary.py; no tracked changes at time of run, no forbidden-path matches; unrelated pre-existing build/ remains untracked
- `git diff --check`: PASS
- Full pytest: not run; package has no code changes and full pytest is not required

## Boundary Statement

Stage-2 execution authorized: no.
Canonical Result Population written: no.
Candidate lifecycle write: no.
Paper/live/runtime touched: no.
OMS/risk/reconciliation/order/exchange touched: no.
Funding P&L/accounting changed: no.
Private provider/API used: no.
Data committed: no.
Code changed: no.

## PR URL

https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/581
