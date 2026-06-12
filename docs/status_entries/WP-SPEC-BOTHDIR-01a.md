# WP-SPEC-BOTHDIR-01a - Design both-direction SMA-band spec

- Package class: T1 docs-only design / lock-candidate Strategy Spec design.
- Branch: `docs/spec-bothdir-01a-design`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/437
- Scope summary: Creates a docs-only design surface for the first symmetric
  both-direction SMA-band Strategy Spec candidate and records a non-committed
  compile probe.
- Authorization basis: Main 5 accepted the completed BOTHDIR runway and
  selected Direction A: first both-direction Strategy Spec design.
- Changed files:
  - `docs/research_pipeline/2026-06-both_direction_sma_band_spec_design.md`
  - `docs/status_entries/WP-SPEC-BOTHDIR-01a.md`
  - `docs/research_pipeline/README.md`
  - `docs/project_status.md`
- Design summary: BTCUSDT Binance USDT-M 15m OHLCV symmetric SMA-band
  mean-reversion research candidate, `direction: "both"`, explicit
  side-labeled long and short entry groups, side-specific centerline exits, no
  compiler mirroring, and locked both-direction conflict semantics.
- Proposed parameter grid: 2 free parameters; `sma_lookback_bars in {20, 50}`
  and `band_threshold in {0.0025, 0.005, 0.01, 0.015, 0.02}`; finite 10-cell
  grid if later frozen unchanged.
- Compile probe: PASS. A temporary full Strategy Spec-shaped payload under
  `.local_tmp/wp-spec-bothdir-01a-probe/` validated through
  `validate_strategy_specs` and compiled through `compile_signal` against
  synthetic 15m OHLCV, producing deterministic signal values
  `[-1.0, 0.0, 1.0]`. Scratch files were removed and not committed.
- Validation summary:
  - Non-committed compile probe: pass.
  - `git diff --check`: pass.
  - `python -m tools.registry.validate_strategy_specs`: pass.
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - `python tools/dev/diff_scope_summary.py`: pass; changed-file scope is the
    expected docs/status set and no forbidden-path matches were reported.
  - Final rebase onto `origin/main`: branch already up to date.
  - Final GitHub PR check: non-draft and `mergeable=MERGEABLE`.
- Boundary summary: No committed Strategy Spec, variant manifest, sweep plan,
  result population, schema, validator, compiler, test, catalog, dashboard,
  data acquisition, simulator, runtime, paper/live, OMS/risk, broker/exchange,
  or protected-path change is included.
- Active-WP requirement traceability:

| Requirement | Evidence | Status |
|---|---|---|
| design doc created | `docs/research_pipeline/2026-06-both_direction_sma_band_spec_design.md` | satisfied |
| both-direction SMA-band family described | design doc sections 3-5 | satisfied |
| long entry lower-band rule included | design doc section 4 | satisfied |
| short entry upper-band rule included | design doc section 4 | satisfied |
| side-specific centerline exits included | design doc section 5 | satisfied |
| explicit side-labeled groups included | design doc sections 4-5 | satisfied |
| finite parameter grid proposed | design doc section 7 | satisfied |
| free-parameter count <= 3 target / <= 5 hard cap addressed | design doc section 7 | satisfied |
| BTCUSDT 15m data references included | design doc section 8 | satisfied |
| backtest-realism assumptions referenced | design doc section 9 | satisfied |
| non-committed compile probe run and recorded | design doc section 10 and this status fragment | satisfied |
| downstream Karl gates stated | design doc section 12 | satisfied |
| status fragment created | this file | satisfied |
| README index entry added | `docs/research_pipeline/README.md` | satisfied |
| project-status pointer added | `docs/project_status.md` | satisfied |
| no committed Strategy Spec / variant / sweep / result files | changed-file list | satisfied |
| no implementation files changed | changed-file list | satisfied |
| validation run | validation summary | satisfied |
| PR body/status finality clean | final PR readiness gate | satisfied |
| no forbidden paths touched | diff scope | satisfied |

- Merge status: PR #437 is open, non-draft, and GitHub reports
  `mergeable=MERGEABLE`.
- Next authority: `WP-SPEC-BOTHDIR-01b` frozen instance authoring and
  `WP-SPEC-BOTHDIR-01c` canonical sweep/result-population work remain
  Karl-gated and unauthorized by this package.
