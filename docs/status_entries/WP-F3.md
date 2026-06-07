# WP-F3 / Dashboard Track - Static Dashboard MVP Generator

## WP Id / Title

WP-F3 / Dashboard Track - Static dashboard MVP generator.

## Branch / PR

- Branch: `codex/dashboard-f3-static-mvp-generator`
- PR: pending

## Package Class

T3 dashboard implementation.

## Scope Summary

Adds the first local/offline static dashboard generator. The generator collects
current repo facts into `dashboard_data.v1`, validates the generated contract
data with `tools.dashboard.validate_dashboard_data`, then renders only validated
dashboard data into a static three-page dashboard: Overview, Data / Provenance,
and Gates.

Generated `dashboard_data/` and `dashboard_build/` outputs remain gitignored and
are not committed.

## Changed Files

- `tools/dashboard/collector.py`
- `tools/dashboard/renderer.py`
- `tools/dashboard/generate_static_dashboard.py`
- `tools/dashboard/templates/index.html`
- `tools/dashboard/static/dashboard.css`
- `tools/dashboard/static/dashboard.js`
- `docs/dashboard/README.md`
- `tests/test_generate_static_dashboard.py`
- `docs/status_entries/WP-F3.md`

## Validation Summary

- `git diff --check`: pass.
- `python -m pytest tests/test_validate_dashboard_data.py -q`: pass, 15 tests.
- `python -m pytest tests/test_generate_static_dashboard.py -q`: pass, 9 tests.
- `python -m tools.dashboard.generate_static_dashboard --output-dir dashboard_build --data-dir dashboard_data`: pass.
- `python -m tools.dashboard.validate_dashboard_data dashboard_data/dashboard_data.json`: pass.
- `python -m tools.registry.validate_result_populations`: pass.
- `python -m tools.research_query.run --list-views`: pass.
- `v_integrity_*`: clean, 55 views.
- `python tools/dev/diff_scope_summary.py`: pass; no forbidden-path matches.
- `python -m pytest -q`: environment-only failure after 1,214 passed tests because
  the isolated worktree lacks gitignored local fixture
  `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`
  required by
  `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window`.
  No data file is committed or pulled into scope.

The in-app browser rejected direct `file://` navigation to the generated static
HTML under its URL policy. No local server was started because F3 forbids a
server; static HTML rendering is covered by generator/content tests instead.

## Boundary Summary

Local/offline static generation only. No server, daemon, scheduler, watcher,
network fetch, CDN, JavaScript build pipeline, React/Vite, Streamlit/Dash/Panel,
credentials, broker/exchange/live API, runtime/paper/live contact, execution
controls, artifact mutation, result population mutation, runner/compiler/
backtester/lib change, query/schema change, ranking, recommendation, readiness,
promotion, transition, or downstream authority is included.

## Merge Status

Pending PR at package execution time.

## Next Dependency / Runway Note

F4 may polish the static UI after F3. F5 remains gated until D5. F6 remains
gated until paper runtime plus authorized read-only paper-state snapshots exist.
