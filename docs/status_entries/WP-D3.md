# WP-D3 / Data Block 1 - Data Validation And Gap Policy

## WP Id / Title

WP-D3 / Data Block 1 - Data Validation And Gap Policy.

## Branch / PR

- Branch: `codex/data-block-1-d3-validation-gap-policy`
- PR: pending

## Package Class

T3 data validation / policy tooling.

## Scope Summary

Adds offline validation/gap-policy support for D2-normalized Binance USDT-M
BTCUSDT 15m OHLCV CSV data. The validator checks exact D2 normalized column
shape, UTC `open_time` semantics, `open_time_ms` / `open_time` consistency,
15m UTC alignment, strict increasing order, expected row count over the
observed range, gap facts, duplicate timestamp facts, OHLC consistency,
nonnegative volume, and deterministic validation report output.

The validator may optionally write a caller-supplied validated-output CSV only
after PASS, and that output is an exact-byte copy of the already-normalized
input rather than a transformed replacement.

## Changed Files

- `tools/data/validate_binance_usdtm_15m.py`
- `tests/test_validate_binance_usdtm_15m.py`
- `docs/data/2026-06-binance_usdtm_15m_gap_policy.md`
- `docs/status_entries/WP-D3.md`
- `docs/project_status.md`

## Validation Summary

Package validation is expected to include:

- `git diff --check`
- `python -m pytest tests/test_validate_binance_usdtm_15m.py -q`
- `python -m pytest tests/test_import_binance_usdtm_15m.py -q`
- `python -m tools.registry.validate_result_populations`
- `python -m tools.research_query.run --list-views`
- all discovered `v_integrity_*` views clean / zero rows
- `python tools/dev/diff_scope_summary.py`
- `python -m pytest -q` when the gitignored local 4h parquet fixture is
  available in the isolated worktree; otherwise classify the known missing
  fixture failure as environment-only and do not commit the data file
- `git diff --cached --check`
- `git diff --cached --name-only`

## Invalid-Data Output Posture

Invalid data may write validation/provenance reports only. Invalid input,
including report-only invalid validation, does not write a downstream-consumable
validated output. The validator does not fill, interpolate, deduplicate, or
synthesize candles to pass validation.

## Boundary Summary

Offline local-file validation only. No live API, credentials, production data
commit, data catalog mutation, result population, real-data sweep, Strategy
Spec, variant manifest, sweep plan, query, schema, runner, backtester, lib,
compiler, runtime, paper, live, or protected-path change is included.

## Merge Status

Pending PR at package execution time.

## Next Dependency / Runway Note

D4 catalog/slice identity may follow if D3 lands clean. D3 does not promote any
validated file into the data catalog and does not authorize D5 real-data
canonical sweep output.
