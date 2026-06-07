# WP-D4 / Data Block 1 - Data Catalog And Slice Identity

## WP Id / Title

WP-D4 / Data Block 1 - Data Catalog And Slice Identity.

## Branch / PR

- Branch: `codex/data-block-1-d4-data-catalog-slice-identity`
- PR: pending

## Package Class

T3 data catalog / provenance tooling.

## Scope Summary

Adds offline catalog/slice-identity support for D2-normalized and D3-validated
Binance USDT-M BTCUSDT 15m OHLCV CSV data. The catalog tool requires a PASS D3
validation report, verifies the normalized file hash against that report,
requires raw-source hash provenance, and writes deterministic sorted JSON only
for valid slices.

## Changed Files

- `docs/data/2026-06-binance_usdtm_15m_catalog_and_slice_identity.md`
- `tools/data/catalog_binance_usdtm_15m.py`
- `tests/test_catalog_binance_usdtm_15m.py`
- `docs/status_entries/WP-D4.md`
- `docs/project_status.md`

## Validation Summary

Package validation is expected to include:

- `git diff --check`
- `python -m pytest tests/test_catalog_binance_usdtm_15m.py -q`
- `python -m pytest tests/test_validate_binance_usdtm_15m.py -q`
- `python -m pytest tests/test_import_binance_usdtm_15m.py -q`
- `python -m tools.registry.validate_result_populations`
- `python -m tools.research_query.run --list-views`
- all discovered `v_integrity_*` views clean / zero rows
- `python tools/dev/diff_scope_summary.py`
- `python -m pytest -q` when local gitignored data fixtures are available;
  otherwise classify known missing-fixture failures as environment-only
- `git diff --cached --check`
- `git diff --cached --name-only`

## Boundary Summary

Offline local-file catalog/provenance only. No live API, credentials,
production data commit, data download, result population, real-data sweep,
Strategy Spec, variant manifest, sweep plan, query, schema, runner, backtester,
lib, compiler, runtime, paper, live, or protected-path change is included.

## Merge Status

Pending PR at package execution time.

## Next Dependency / Runway Note

D5 remains Karl-gated. A future D5 package must consume a specific validated D4
catalog ref and data slice identity plus PASS D3/D4 status before any real-data
canonical sweep can be considered.
