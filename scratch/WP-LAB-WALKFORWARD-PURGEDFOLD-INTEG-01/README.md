# WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01 Scratch Evidence

This directory contains non-canonical scratch evidence for repo-native
purged/embargoed walk-forward folds over the current `STRAT-SPEC-0004` /
`VM-0004` / `SWEEP-PLAN-0004` lineage.

## Contents

- `purged_fold_manifest.json`: schema-compatible scratch fold manifest using
  explicit purge/embargo fields under the existing canonical contract.
- `purged_fold_comparison_report.json`: naive-vs-purged boundary comparison.
- `purged_walkforward_run_report.json`: validated scratch walk-forward run
  report copied from the runner's default `walkforward_run_report.json` output.
- `walkforward_run_report.json`: runner default output filename, same content as
  `purged_walkforward_run_report.json`.
- `walkforward_dashboard_fragment.json`: display-only fragment emitted by the
  existing scratch runner.
- `provenance.json`: generation and validation provenance.

## Fold Parameters

- Timeframe: `15m`
- Fold count: `2`
- Selection window: `35040` bars
- Evaluation window: `8640` bars
- Purge: `96` bars before each evaluation window
- Embargo: `32` bars after each evaluation window where it affects later
  selection windows
- Boundary semantics: `start_inclusive_end_exclusive`

## Observed Boundary Difference

The comparison report shows a material difference versus naive adjacent folds:

- Total naive selection bars: `70080`
- Total purged/embargoed selection bars: `69856`
- Total removed selection bars: `224`
- Fold 1 removes `96` bars by purge.
- Fold 2 removes `128` bars: `96` by purge and `32` by prior-evaluation embargo.

## Regeneration

The manifest, comparison report, and provenance were generated with:

```powershell
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.walkforward.purged_folds `
  --output scratch\WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01\purged_fold_manifest.json
```

The scratch walk-forward run used the existing runner against the local
gitignored D4A CSV:

```powershell
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.walkforward.run_walkforward_scratch `
  --walkforward-manifest scratch\WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01\purged_fold_manifest.json `
  --ohlcv-input data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv `
  --output-dir scratch\WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01 `
  --created-at-utc 2026-06-20T12:00:00Z
```

`purged_walkforward_run_report.json` is a same-content copy of the runner's
default `walkforward_run_report.json` output, preserved under the package's
requested filename.

## Non-Authority

These artifacts are scratch-only and non-canonical. They grant no runner,
backtester, result-population write, ranking, readiness, promotion, paper/live,
runtime, broker, exchange, order, or candidate approval authority.
