# WP-MOMENTUM-4H-TRIAL-01

Status: branch-state canonical result-population package.

## Scope

Package class: canonical result-population trial / evidence artifact.

Branch: `trial/momentum-4h-0006-canonical`

Worktree: `C:\GitHub\crypto-perp-wedge-WP-MOMENTUM-4H-TRIAL-01`

Base: `origin/main` at `e8e0e4e` after PR #491 merge.

Authorization: explicit user authorization for the canonical 0006 Result
Population write was present in the active execution package.

## Changed Files

- `research/result_populations/RP-6236.result_population.json`
- `docs/research_pipeline/2026-06-momentum_4h_trial_0006_result.md`
- `docs/status_entries/WP-MOMENTUM-4H-TRIAL-01.md`
- `tests/test_research_query.py`

## Commands

Dry-run:

```powershell
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_runner.run_offline_sweep --strategy-spec research\strategy_specs\STRAT-SPEC-0006.strategy_spec.json --variant-manifest research\variant_manifests\VM-0006.variant_manifest.json --sweep-plan research\sweep_plans\SWEEP-PLAN-0006.sweep_plan.json --canonical-4h --ohlcv-input C:\GitHub\crypto-perp-wedge\data\processed\d4h\binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_d4h_resampled.csv --sizing-mode dynamic_equity_target_leverage --target-leverage 1.0 --max-workers 4
```

Canonical write:

```powershell
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_runner.run_offline_sweep --strategy-spec research\strategy_specs\STRAT-SPEC-0006.strategy_spec.json --variant-manifest research\variant_manifests\VM-0006.variant_manifest.json --sweep-plan research\sweep_plans\SWEEP-PLAN-0006.sweep_plan.json --output-dir scratch\WP-MOMENTUM-4H-TRIAL-01\canonical_0006 --write-result-population --canonical-4h --ohlcv-input C:\GitHub\crypto-perp-wedge\data\processed\d4h\binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_d4h_resampled.csv --sizing-mode dynamic_equity_target_leverage --target-leverage 1.0 --max-workers 4
```

The exact-SHA local CSV was read from the base checkout to avoid creating or
modifying `data/` in the trial worktree.

## Result

- Canonical RP ID/path/hash:
  `RP-6236`;
  `research/result_populations/RP-6236.result_population.json`;
  `sha256:9ad2b0f0d3134ae0f29f428deb668e8174ed78f502f6a69c88a08cacf678510b`
- Input identity hash:
  `sha256:47e5b6f90586159bc8da63e181ad8912c889e1bd637fc63dd68d2d1b08065a95`
- Result population identity hash:
  `sha256:60ac2a69f7551983b4d6ac3f061ff76c3ba7d0caea00fe407212f63a8b55c35a`
- Denominator/outcome counts: denominator `8`; `successful=8`; all other
  outcome categories `0`; counts sum `8`
- Screen verdict: `NO-GO`
- Primary blockers: positive return rows `0/8`; median return `-51.99%`;
  median drawdown `69.68%`; max drawdown `85.91%`; three rows hit automatic
  drawdown NO-GO; positive-gross cost/gross median `1.319`; median trades
  `511.0`; max trades `562`

## Validation

Completed from this worktree:

- `git status --short`: expected four-file package diff
- `git diff --check`: `PASS`
- `git diff --cached --check`: `PASS`
- `python -m tools.registry.validate_strategy_specs`: `PASS`
- `python -m tools.registry.validate_variant_sweep_artifacts`: `PASS`
- `python -m tools.registry.validate_indicator_catalogs`: `PASS`
- `python -m tools.registry.validate_result_populations`: `PASS`
- `python -m tools.registry.validate_candidate_registry`: `PASS`
- `python -m tools.registry.validate_paper_state`: `PASS`
- `python -m tools.research_query.run --list-views`: `PASS`
- `python -m pytest tests/test_offline_research_runner.py -q`: `PASS`
  (`94 passed`, 2 warnings)
- `python -m pytest tests/test_research_query.py -q`: `PASS`
  (`64 passed`)
- `python tools/dev/diff_scope_summary.py --check-forbidden` with explicit
  `WP-MOMENTUM-4H-TRIAL-01` canonical RP authorization for `RP-6236`: `PASS`
- `python tools/dev/verify.py --integrity-views --integrity-max-workers 4
  --timeout-seconds 300 --max-output-chars 6000 --json` with explicit
  `WP-MOMENTUM-4H-TRIAL-01` canonical RP authorization for `RP-6236`: `PASS`
  (all discovered integrity views clean)
- `python tools/dev/verify.py --full-pytest-sharded --pytest-shards 4
  --pytest-shard-workers 4 --timeout-seconds 300
  --full-pytest-timeout-seconds 1800 --max-output-chars 6000 --json` with
  explicit `WP-MOMENTUM-4H-TRIAL-01` canonical RP authorization for `RP-6236`:
  `PASS` (`1287 passed`, 1 skipped; shard warnings only)

Note: running `diff_scope_summary.py --check-forbidden` or `verify.py` without
the package authorization flags fails as designed because the package
intentionally writes one new canonical artifact under `research/result_populations/`.

## Boundary

- Strategy Spec / Variant Manifest / Sweep Plan mutation: `NO`
- Runner / compiler / schema / validator / query logic mutation: `NO`
- Data / catalog mutation: `NO`
- Candidate / walk-forward / paper/live / runtime / capital authority: `NO`
- Protected paths touched: `NO`

Next route depends on verdict and explicit user/Main authorization. Because
the verdict is `NO-GO` across net performance, drawdown, cost, churn, and
sensitivity, this package does not advance the exact 0006 population to
walk-forward/OOS and does not support a drawdown-only tighter-stop follow-up
without a separate authorized package.
