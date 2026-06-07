# WP-D5B / Data Block 1 - Runner Input Timestamp Compatibility

## WP Id / Title

WP-D5B / Data Block 1 - Runner input timestamp compatibility for D4A normalized CSV.

## Branch / PR

- Branch: `codex/data-block-1-d5b-runner-d4a-timestamp-compatibility`
- PR: pending

## Package Class

T3 runner input compatibility.

## Scope Summary

Updates the build-and-test-only offline runner's canonical 15m CSV input loader
so it can consume D4A-normalized timestamp columns directly. The runner now
accepts timestamp inputs in deterministic order: `timestamp`, then `open_time`,
then `open_time_ms`. Additional present timestamp columns are parsed and must
agree with the selected column; conflicts fail closed.

No source CSV is rewritten or transformed. The D4A normalized CSV SHA remains
the provenance source for later D5 retry work:
`c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`.

## Changed Files

- `tools/research_runner/run_offline_sweep.py`
- `tests/test_offline_research_runner.py`
- `docs/status_entries/WP-D5B.md`
- `docs/project_status.md`

## Timestamp Compatibility Behavior

- Existing `timestamp` CSV inputs remain supported.
- D4A-style `open_time` inputs are accepted when `timestamp` is absent.
- `open_time_ms` inputs are accepted when both `timestamp` and `open_time` are
  absent, with deterministic UTC epoch-millisecond conversion.
- If supported timestamp columns are absent, the runner fails closed.
- If present supported timestamp columns disagree, the runner fails closed.
- Invalid or non-integer `open_time_ms` values fail closed.

## D4A Column Support

Focused tests cover a tiny synthetic D4A-style CSV shape beginning with
`open_time_ms,open_time,open,high,low,close,volume,...`. The runner consumes the
shape directly through the existing canonical 15m path.

## D4 Provenance Preservation

D4 provenance mode still records the committed D4 catalog ref and D4 slice
identity from the existing D4A artifact chain. Fixture-path provenance remains
the default when D4 provenance paths are not supplied.

## Validation Summary

- `git diff --check`: pass.
- `python -m pytest tests/test_offline_research_runner.py -q`: pass, 35 tests.
- `python -m pytest tests/test_validate_result_populations.py -q`: pass, 42 tests.
- `python -m tools.registry.validate_result_populations`: pass.
- `python -m tools.research_query.run --list-views`: pass.
- `v_integrity_*`: clean, 55 views.
- `python tools/dev/diff_scope_summary.py`: pass; no forbidden-path matches.
- `python -m pytest -q`: environment-only failure after 1,219 passed tests
  because the isolated worktree lacks gitignored local fixture
  `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`
  required by
  `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window`.
  No data file is committed or pulled into scope.

## Boundary Summary

Runner input compatibility only. No canonical result population, sweep output,
local transformed CSV, generated data, D4A CSV mutation, D2/D3/D4 artifact
mutation, Strategy Spec mutation, variant manifest mutation, sweep plan
mutation, compiler, backtester/lib, schema, query-layer, dependency,
runtime/paper/live, broker/exchange/API, credential, ranking, readiness,
recommendation, promotion, transition, or downstream-authority change is
included.

## Merge Status

Pending PR at package execution time.

## Next Dependency / Runway Note

After WP-D5B merges, the existing D5 package can be retried from preflight using
the existing gitignored D4A normalized CSV directly. D5 remains separate and is
not retried in this package.
