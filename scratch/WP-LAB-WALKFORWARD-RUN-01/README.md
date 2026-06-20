# WP-LAB-WALKFORWARD-RUN-01 scratch evidence

This directory contains a deterministic, non-canonical STRAT-SPEC-0004 walk-forward demonstration.

- `walkforward_fold_manifest.input.json` is a scratch-only instance of the merged fold-manifest contract. It creates no canonical manifest or evidence authority.
- `walkforward_run_report.json` contains per-fold and per-variant IS/OOS metrics plus descriptive degradation comparisons.
- `walkforward_dashboard_fragment.json` is a display-only summary shape for a later dashboard package.

The run carries all eight frozen `VM-0004` variants through two explicit folds against the validated D4 15m slice. It uses the existing offline runner/backtester path with dynamic-equity target leverage at `1.0` and the runner's current D4 zero-funding posture. It writes no Result Population, trial log, Strategy Spec, Variant Manifest, Sweep Plan, canonical fold manifest, candidate record, or runtime/paper/live artifact.

Reproduction requires the locally materialized D4 CSV whose SHA-256 is locked by the committed catalog slice:

```powershell
& "C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe" -m tools.walkforward.run_walkforward_scratch `
  --walkforward-manifest scratch/WP-LAB-WALKFORWARD-RUN-01/walkforward_fold_manifest.input.json `
  --ohlcv-input "C:\GitHub\crypto-perp-wedge\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv" `
  --created-at-utc 2026-06-20T12:00:00Z
```

Non-authority posture: not canonical evidence; not promotion evidence; not ranking authority; not readiness authority; not paper/live authority; not candidate registration.
