# WP-DIAG-4H-PROBE-CANONICAL-RECONCILE-01

Status: branch-state read-only diagnostic package.

## Scope

Package class: read-only evidence diagnostic / methodology audit.

Branch: `diag/4h-probe-canonical-reconcile-01`

Worktree:
`C:\GitHub\crypto-perp-wedge-WP-DIAG-4H-PROBE-CANONICAL-RECONCILE-01`

Base: `origin/main` at `1354b81` after post-branch refresh/rebase.

Authorization: user-authorized diagnostic after 0006 canonical `NO-GO` and
probe/canonical metric divergence.

## Changed Files

- `docs/research_pipeline/2026-06-momentum_4h_probe_canonical_reconcile.md`
- `docs/status_entries/WP-DIAG-4H-PROBE-CANONICAL-RECONCILE-01.md`

## Source Artifacts Inspected

- `research/result_populations/RP-6236.result_population.json`
- `research/strategy_specs/STRAT-SPEC-0006.strategy_spec.json`
- `research/variant_manifests/VM-0006.variant_manifest.json`
- `research/sweep_plans/SWEEP-PLAN-0006.sweep_plan.json`
- `docs/research_pipeline/2026-06-momentum_4h_trial_0006_result.md`
- `docs/research_pipeline/2026-06-momentum_4h_prereg_0006.md`
- `docs/status_entries/WP-MOMENTUM-4H-TRIAL-01.md`
- `docs/status_entries/WP-RUNNER-4H-CAPABILITY-01.md`
- `docs/status_entries/WP-MOMENTUM-4H-PREREG-01.md`
- `tools/research_runner/run_offline_sweep.py`
- `tools/research_runner/spec_signal_compiler.py`
- `tests/test_offline_research_runner.py`
- `tests/test_spec_signal_compiler.py`

## Scratch Commands Run

Canonical dry-run, no write:

```powershell
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_runner.run_offline_sweep --strategy-spec research\strategy_specs\STRAT-SPEC-0006.strategy_spec.json --variant-manifest research\variant_manifests\VM-0006.variant_manifest.json --sweep-plan research\sweep_plans\SWEEP-PLAN-0006.sweep_plan.json --canonical-4h --ohlcv-input C:\GitHub\crypto-perp-wedge\data\processed\d4h\binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_d4h_resampled.csv --sizing-mode dynamic_equity_target_leverage --target-leverage 1.0 --max-workers 4
```

Result: `PASS`; dry-run reproduced `RP-6236` with denominator `8`,
`successful=8`, and no canonical write.

Additional in-memory diagnostics:

- exact 0006 direct `compile_signal` plus `run_backtest` over the exact 4h CSV;
- exact 0006 with confirming trend conditions removed in memory;
- probe-like 0005 bar-count grid directly on 4h bars, using the 0006 shape and
  direct `compile_signal` plus `run_backtest`;
- representative first-entry timestamp comparison for `VAR-000001`.

These diagnostics wrote no committed artifacts and did not mutate data or
canonical evidence.

## Classification Result

- Canonical runner: sound for this diagnostic.
- Trend gate: `CANONICAL_GATE_APPLIED_AS_INTENDED`.
- Probe logic: `PROBE_USED_NONCANONICAL_OR_UNRELIABLE_LOGIC` for use as an
  exact canonical-population premise gate.
- Probe methodology:
  `PROBE_METHODOLOGY_NEEDS_CANONICAL_REGROUNDING`.
- `RP-6236`: interpretable as valid canonical evidence for the exact frozen
  0006 population.

## Root Cause Summary

The probe and canonical result did not test the same population. The probe used
the 0005 bar-count grid directly on 4h bars (`20/50`, `100/200`, `300/400`),
while canonical `RP-6236` used the frozen 0006 horizon-rescaled 4h grid
(`2/3`, `6/12`, `19/25`). The shorter canonical lookbacks create many more SMA
crossovers and therefore much higher churn and cost exposure.

The trend-confirmation gate is applied. Removing it in memory changed thousands
of signal bars, changed trade counts for six variants, and caused two variants
to fail closed before ATR availability.

## Validation Summary

Completed from this worktree:

- `git status --short`: expected two untracked docs files only
- `git diff --check`: `PASS`
- `git diff --cached --check`: `PASS`
- `python -m tools.registry.validate_strategy_specs`: `PASS`
- `python -m tools.registry.validate_variant_sweep_artifacts`: `PASS`
- `python -m tools.registry.validate_indicator_catalogs`: `PASS`
- `python -m tools.registry.validate_result_populations`: `PASS`
- `python -m tools.registry.validate_candidate_registry`: `PASS`
- `python -m tools.registry.validate_paper_state`: `PASS`
- `python -m tools.research_query.run --list-views`: `PASS`
- `python tools/dev/diff_scope_summary.py --check-forbidden`: `PASS`
- `python tools/dev/verify.py --integrity-views --integrity-max-workers 4
  --timeout-seconds 300 --max-output-chars 6000 --json`: `PASS`
- `python -m pytest tests/test_offline_research_runner.py -q`: `PASS`
  (`94 passed`, 2 warnings)

Full sharded pytest: `NOT RUN` - docs-only diagnostic; no code, schema,
validator, query-layer, runner, or protected-path behavior changed.

## Boundary Summary

- RP mutation: `NO`
- Runner/compiler/lib changes: `NO`
- Strategy Spec/VM/Sweep changes: `NO`
- Canonical write: `NO`
- Candidate/walk-forward/paper/live/runtime/capital authority: `NO`
- Protected paths touched: `NO`
- Data artifact creation or mutation: `NO`

The exact 4h CSV was read from the base checkout at
`C:\GitHub\crypto-perp-wedge\data\processed\d4h\binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_d4h_resampled.csv`
with SHA256 `828ad4a975c157c7ac4d3c873a39a8b6bbfec3cb306e25eb74209c8a01da6ca1`.

## Next Package

Recommended next package: a probe-methodology correction / canonical-regrounding
package that documents when premise probes must use the exact Strategy Spec,
exact grid, canonical runner path, and data lineage before their metrics can be
used as a gate for canonical expectations.

No `RP-6236` correction, replacement, or fresh 0006 rerun is indicated by this
diagnostic.
