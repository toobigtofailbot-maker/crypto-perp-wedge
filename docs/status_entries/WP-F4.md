# WP-F4 / Dashboard Track - Static Dashboard Polish Pass

## WP Id / Title

WP-F4 / Dashboard Track - Static dashboard polish pass.

## Branch / PR

- Branch: `codex/dashboard-f4-static-polish-pass`
- PR: pending

## Package Class

T3 dashboard UI polish.

## Scope Summary

Polishes the existing F3 static dashboard presentation while preserving the
three-page MVP, renderer-only consumption of validated `dashboard_data.v1`, and
display-only operator posture. The pass improves the dark visual system,
Overview card hierarchy, status-count treatment, Data / Provenance table
readability, Gates table readability, empty/warning states, local table
filtering, and responsive behavior.

## Changed Files

- `tools/dashboard/templates/index.html`
- `tools/dashboard/static/dashboard.css`
- `tools/dashboard/static/dashboard.js`
- `tools/dashboard/renderer.py`
- `tests/test_generate_static_dashboard.py`
- `docs/dashboard/README.md`
- `docs/status_entries/WP-F4.md`

## Validation Summary

- `git diff --check`: pass.
- `python -m pytest tests/test_validate_dashboard_data.py -q`: pass, 15 tests.
- `python -m pytest tests/test_generate_static_dashboard.py -q`: pass, 11 tests.
- `python -m tools.dashboard.generate_static_dashboard --output-dir dashboard_build --data-dir dashboard_data`: pass.
- `python -m tools.dashboard.validate_dashboard_data dashboard_data/dashboard_data.json`: pass.
- `python -m tools.registry.validate_result_populations`: pass.
- `python -m tools.research_query.run --list-views`: pass.
- `v_integrity_*`: clean, 55 views.
- `python tools/dev/diff_scope_summary.py`: pass; no forbidden-path matches.
- `python -m pytest -q`: environment-only failure after 1,216 passed tests because
  the isolated worktree lacks gitignored local fixture
  `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`
  required by
  `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window`.
  No data file is committed or pulled into scope.
- In-app browser visual check: direct `file://` navigation to generated
  `dashboard_build/index.html` was blocked by Browser URL policy. No local
  server workaround was used because F4 remains static-file only.

## Boundary Summary

Presentation-only. No collector logic, schema, validator, dashboard-data
contract, data/result artifact, runner/compiler/backtester/lib, query-layer,
runtime, paper/live, broker/exchange/order, credentials, CDN, network fetch,
server, JavaScript build pipeline, dependency, ranking, recommendation,
readiness, promotion, transition, approval, or execution authority is added.

The local search inputs are inert browser filters over rendered table rows.
They do not mutate artifacts, call a runtime, call a server, rank strategy
quality, satisfy gates, or alter source facts.

## Merge Status

Pending PR at package execution time.

## Next Dependency / Runway Note

F5 waits for D5 result population. F6 waits for separately authorized paper
runtime plus read-only paper-state snapshots.
