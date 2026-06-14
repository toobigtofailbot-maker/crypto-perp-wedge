# WP-PHASEB-PREREG-PREP-01 Branch State

- Package: `WP-PHASEB-PREREG-PREP-01`.
- Title: Pre-registration prep: real-data gate behavior and operational screen
  criteria.
- Branch: `docs/phaseb-prereg-prep-01`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/468
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-PHASEB-PREREG-PREP-01`.
- Base: `origin/main` at `1b4955a`, after PR #466 and PR #467 were present.
- Package class: docs plus read-only real-data probe.
- Merge status: PR open for review.

## Scope Summary

This package creates
`docs/research_pipeline/2026-06-phaseb_prereg_prep.md`, adds a research
pipeline README pointer, records this status fragment, and adds a compact
branch-state pointer to `docs/project_status.md`.

The prep doc resolves two pre-freeze blockers:

- Real-data gate behavior: the fixed regime candidate
  `STDDEV(close, vol_lookback_bars) > 1.0` is inert on the BTCUSDT 15m D4
  slice, with a 100.000000% true-rate for both `vol_lookback_bars` values.
- Operational criteria: the future single-slice Phase-B trial gets a proposed
  denominator-preserving, net-of-cost, not-winner-only GO-to-walk-forward screen
  tied to RP-7520 comparison metrics.

## Probe Summary

The read-only probe used the locally available D4 normalized CSV at
`C:\GitHub\crypto-perp-wedge-d4a\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`.
The file's SHA256 matched the committed catalog normalized SHA256
`c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`.

Data slice:

- catalog ref:
  `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
- data slice identity:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- row count: `220128`
- date range: `2020-01-01T00:00:00+00:00` through
  `2026-04-11T23:45:00+00:00`

Gate results:

- `STDDEV(close, 30) > 1.0`: true-rate `100.000000%`, degenerate.
- `STDDEV(close, 50) > 1.0`: true-rate `100.000000%`, degenerate.
- `close > SMA(close, 100)`: true-rate `52.270383%`, non-degenerate.
- `close > SMA(close, 200)`: true-rate `52.664269%`, non-degenerate.

Closed scale-meaningful alternative found:

- `STDDEV(close, vol_lookback_bars) > STDDEV(close, trend_lookback_bars)`.
- Observed true-rates ranged from `6.827658%` to `22.227979%` over the proposed
  parameter grid, non-degenerate under the package's `<=1%` / `>=99%`
  threshold.

## Changed Files

- `docs/research_pipeline/2026-06-phaseb_prereg_prep.md`
- `docs/research_pipeline/README.md`
- `docs/status_entries/WP-PHASEB-PREREG-PREP-01.md`
- `docs/project_status.md`

## Validation Summary

- Read-only gate-behavior probe: PASS. The probe found a hash-matched local
  D4 normalized CSV, loaded `220128` rows, confirmed the current fixed regime
  gate is `100.000000%` true for both proposed volatility lookbacks, and found
  non-degenerate closed volatility-expansion alternatives.
- RP-7520 comparison snippet: PASS. Read `RP-7520` read-only and extracted
  trade count, return, Sharpe, drawdown, and cost-burden population summaries.
- `git diff --check`: PASS.
- `git diff --cached --check`: PASS.
- `git diff --name-only`: PASS; tracked diffs were
  `docs/project_status.md` and `docs/research_pipeline/README.md`.
- `git status --short`: PASS; complete intended change set included the two
  tracked pointer edits plus untracked
  `docs/research_pipeline/2026-06-phaseb_prereg_prep.md` and
  `docs/status_entries/WP-PHASEB-PREREG-PREP-01.md`.
- `python tools/dev/diff_scope_summary.py --check-forbidden`: PASS; no
  forbidden-path matches.
- `python -m tools.registry.validate_strategy_specs`: PASS.
- `python -m tools.registry.validate_indicator_catalogs`: PASS.
- `python -m tools.registry.validate_result_populations`: PASS.
- `python -m tools.research_query.run --list-views`: PASS.
- `python tools/dev/verify.py --help`: PASS.
- `python tools/dev/verify.py --timeout-seconds 300 --max-output-chars 6000`:
  PASS; overall status `pass`.
- `python tools/dev/verify.py --integrity-views --timeout-seconds 300
  --max-output-chars 6000`: TIMED OUT at the outer command wrapper after the
  helper's integrity sweep exceeded the available command window; not used as
  merge evidence.
- Focused result-population integrity SQL over all
  `v_integrity_result_population_*` views: PASS; all checked views returned
  `0` rows.
- Full pytest: Not run; not required for docs plus read-only probe because no
  code, test, schema, validator, runner, lib, or artifact behavior changed.

## Boundary Summary

- Freeze created: NO.
- Strategy Spec / Variant Manifest / Sweep Plan created or changed: NO.
- Canonical result population changed: NO.
- Trial log changed: NO.
- Compiler/schema/catalog changed: NO.
- `lib/` or runner behavior changed: NO.
- Candidate lifecycle, ranking, promotion, readiness, paper/live/runtime
  authority created: NO.
- Data acquisition or data transformation performed: NO.
- Temp/scratch artifacts committed: NO.

## Next Dependency / Runway Note

Main review should decide whether the Phase-B v1 freeze package replaces the
inert fixed-minimum regime gate with the closed volatility-expansion gate,
drops regime from v1, or routes richer regime semantics back to a future
compiler/schema track. This package does not authorize the freeze or the trial.
