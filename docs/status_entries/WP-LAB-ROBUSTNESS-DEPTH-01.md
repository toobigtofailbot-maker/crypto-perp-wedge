# WP-LAB-ROBUSTNESS-DEPTH-01 - Advisory Robustness Depth

## Branch / PR

- Branch: `lab/robustness-depth-01`
- Base: `origin/main` at `4da388a`
- PR: not opened in this local execution

## Package Class

Advisory robustness / stress diagnostics. Scratch-only, non-canonical, and
boundary-preserving.

## Scope Summary

This package adds `tools/robustness/robustness_depth.py`, a deterministic
advisory CLI that reads existing Result Population-style rows or fixtures and
emits scratch-only stress diagnostics for cost, funding, slippage, regime, and
per-trade resampling posture.

Cost, funding, and slippage stress use only existing aggregate row metrics and
do not alter canonical metrics. Regime stress is exercised only when real
regime labels are present. Per-trade resampling is exercised only when real
trade rows are supplied; committed Result Populations lacking per-trade rows are
reported as unavailable, with no fabricated trades.

## Changed Files

- `tools/robustness/robustness_depth.py`
- `tests/test_robustness_depth.py`
- `tests/fixtures/robustness_depth/valid_result_population_rows.json`
- `tests/fixtures/robustness_depth/missing_per_trade_rows.json`
- `scratch/WP-LAB-ROBUSTNESS-DEPTH-01/README.md`
- `scratch/WP-LAB-ROBUSTNESS-DEPTH-01/robustness_depth_report.json`
- `scratch/WP-LAB-ROBUSTNESS-DEPTH-01/robustness_depth_report.md`
- `scratch/WP-LAB-ROBUSTNESS-DEPTH-01/provenance.json`
- `docs/status_entries/WP-LAB-ROBUSTNESS-DEPTH-01.md`

## Report Facts

- Default input: `research/result_populations/RP-2592.result_population.json`
- Seed: `1729`
- Stress dimensions exercised on the default input: cost, funding, slippage
- Missing default-input surfaces: real regime labels, per-trade rows
- Per-trade resampling status on the default input:
  `unavailable_missing_per_trade_rows`
- Canonical artifact mutation: `false`
- Gate/readiness authority created: `false`

## Boundary Summary

- Canonical Result Populations: read-only, not mutated.
- Strategy Specs / Variant Manifests / Sweep Plans: not mutated.
- Runner / backtester / `lib/`: not touched.
- Runtime / paper / live paths: not touched.
- OMS / risk / reconciliation / safe-mode / kill-switch / broker / exchange /
  order / capital paths: not touched.
- Dependency files: not touched.
- Trial log: not touched.
- `docs/project_status.md`: not touched.
- Authority posture: advisory only, scratch only, non-canonical, not a
  screen gate, not promotion, not readiness, not candidate evidence, not
  paper/live.

## Validation Summary

- `python -m pytest tests/test_robustness_depth.py tests/test_seeded_advisory_mc.py -q`:
  PASS, 27 passed.
- `python -m tools.robustness.robustness_depth --output-dir scratch/WP-LAB-ROBUSTNESS-DEPTH-01 --seed 1729`:
  PASS, wrote required scratch outputs. Default RP-2592 report checksum:
  `sha256:2a062e32df42e9566a187ee7415b66b52c6ca31d75b0b5f1ff775daaf4857d16`.
- `python tools/dev/diff_scope_summary.py`: PASS, forbidden-path matches:
  none.
- `git diff --check`: PASS.
- `python -m pytest tests/test_lab_run_registry.py tests/test_generate_static_dashboard.py -q`:
  PASS, 38 passed.
- `python -m tools.research_query.run --list-views`: PASS.
- `python -m pytest -q` with the default interpreter: collection failed in
  7.24 seconds because the interpreter lacks `binance`, `pandas`, and
  `numpy`; no package-specific failure surfaced before collection stopped.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`:
  timed out after 30 minutes with no visible pytest output; no package-specific
  failure surfaced before timeout.
