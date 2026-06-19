# EXT-INTEG-ANALYTICS-METRICS-01 - Repo-native Advisory Analytics Metrics

## Branch / PR

- Branch: `ext/integ-analytics-metrics-01`
- PR: `https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/518`
- Base: `origin/main` at `c095c88` when the dedicated worktree was created.
- Prerequisite: PR #513 / `EXT-SIMULATOR-PILOT-01` is merged.

## Package Class

T3 advisory analytics and reporting; repo-owned, additive, deterministic,
non-runtime, non-canonical, and boundary-preserving.

## Scope Summary

This package adds repo-native formulas for normalization of real chronological
equity or simple-return inputs, drawdown episodes, underwater curves, rolling
return/volatility/drawdown, a Calmar-style metric, and downside/tail summaries.
It also adds a fixture-backed advisory reporting surface over committed
`RP-7134` evidence.

`RP-7134` exposes aggregate per-variant metrics rather than a chronological
equity or return series. The report therefore marks all path-dependent metrics
unavailable, provides only a clearly labeled cross-sectional variant summary,
and does not invent a variant ordering, return path, rolling window, period
frequency, or annualization assumption.

Decision label: `FORMULA_ADAPT_REPO_NATIVE`.

## Changed Files

- `tools/analytics/advisory_metrics.py`
- `tools/analytics/advisory_metrics_report.py`
- `tests/test_advisory_analytics_metrics.py`
- `docs/status_entries/EXT-INTEG-ANALYTICS-METRICS-01.md`
- `scratch/EXT-INTEG-ANALYTICS-METRICS-01/advisory_analytics_report.json`
- `scratch/EXT-INTEG-ANALYTICS-METRICS-01/advisory_analytics_report.md`
- `scratch/EXT-INTEG-ANALYTICS-METRICS-01/advisory_analytics_report.sha256`

## Fixture / Output Facts

- Result Population: `RP-7134`
- Input path: `research/result_populations/RP-7134.result_population.json`
- Input checksum:
  `sha256:9813afd65c946ceaac23804fd485b4452d2451bec31a726eb86667926741e524`
- Successful attempted aggregate rows: `8`
- Chronological equity series available: `NO`
- Chronological return series available: `NO`
- Path-dependent metrics reported unavailable: `10`
- Report checksum:
  `sha256:be9fcf133397aeb141178445e713e359da1d37d0945cceeb23faefcb3cee48f7`
- Committed outputs contain no local absolute paths.

## Validation Summary

- `python -m pytest tests/test_advisory_analytics_metrics.py -q`:
  `PASS`, 20 passed.
- `python -m tools.analytics.advisory_metrics_report --result-population
  research/result_populations/RP-7134.result_population.json --output-dir
  scratch/EXT-INTEG-ANALYTICS-METRICS-01`: `PASS`; decision label and report
  checksum match the committed outputs.
- `python -m tools.research_query.run --list-views`: `PASS`.
- `python tools/dev/diff_scope_summary.py`: `PASS`; forbidden-path matches:
  none.
- `python -m pytest tests/test_external_analytics_pilot.py
  tests/test_evaluation.py -q`: `PASS`, 18 passed, 4 warnings.
- `python -m pytest -q`: `PASS`, 1700 passed, 1 skipped, 6 warnings.
- The isolated worktree used a local-only ignored copy of the existing D4A
  normalized CSV from the root checkout so the simulator pilot fixture test
  could evaluate its normal local-data precondition. The file is not committed.
- Ruff: not installed in the repo environment; not used as merge evidence.

## Boundary Summary

- Runtime / paper / live touched: `NO`.
- OMS / risk / reconciliation / safe-mode / kill-switch / broker / exchange /
  order paths touched: `NO`.
- Private APIs / credentials / account / balance / position / order methods:
  `NO`.
- Canonical Result Population mutation: `NO`.
- Canonical Strategy Spec / Variant Manifest / Sweep Plan mutation: `NO`.
- Runner / backtester mutation: `NO`.
- Schema / validator / query-layer mutation: `NO`.
- External dependency change: `NO`.
- Screen-gate / ranking / promotion / readiness / candidate-evidence authority:
  `NO`.
- Fabricated return or equity paths: `NO`.

## Merge Status

PR #518 is open as ready for review. The branch uses the required dedicated
worktree and does not modify `docs/project_status.md`.

## Next Dependency / Runway Note

The repo-native formulas can analyze real chronological equity or return data
when a later authorized advisory input surface supplies it. This package does
not add that input to canonical Result Populations and does not authorize any
schema, runner, evidence, gate, candidate, promotion, or runtime change.
