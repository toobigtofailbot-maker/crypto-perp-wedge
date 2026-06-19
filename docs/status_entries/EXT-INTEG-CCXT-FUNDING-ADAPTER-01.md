# EXT-INTEG-CCXT-FUNDING-ADAPTER-01 - Productionize CCXT Public Funding Adapter

## WP Id / Title

- WP id: `EXT-INTEG-CCXT-FUNDING-ADAPTER-01`
- Title: Productionize CCXT public funding ingestion adapter

## Branch / PR

- Branch: `ext/integ-ccxt-funding-adapter-01`
- PR: `https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/514`

## Package Class

T3 data-ingestion / repo-owned public-data adapter.

## Scope Summary

This package adds a repo-owned CCXT public REST funding-rate ingestion adapter for
BTCUSDT Binance USDT-M perpetual funding history over the repo-truth D4 window:
`2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`.

The adapter fetches public CCXT funding rows, normalizes UTC funding timestamps,
deduplicates by nominal funding time, freezes raw and normalized JSONL snapshots,
writes a checksum, provenance, validation report, and catalog-lineage record, and
records the catalog pointer in `docs/data_catalog.md`.

Decision label: `ADOPT_AS_PUBLIC_DATA_ADAPTER`.

## Changed Files

- `tools/data_ingestion/__init__.py`
- `tools/data_ingestion/ccxt_public_funding_adapter.py`
- `tests/test_ccxt_public_funding_adapter.py`
- `docs/data_catalog.md`
- `docs/status_entries/EXT-INTEG-CCXT-FUNDING-ADAPTER-01.md`
- `scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/funding_snapshot.raw.jsonl`
- `scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/funding_snapshot.normalized.jsonl`
- `scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/funding_snapshot.sha256`
- `scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/provenance.json`
- `scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/validation_report.json`
- `scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/validation_report.md`
- `scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/catalog_lineage.json`

## Validation Summary

- `python -m pytest tests/test_ccxt_public_funding_adapter.py -q`: PASS, 11 passed.
- `python -m pytest tests/test_ccxt_public_funding_ingest.py tests/test_ccxt_public_funding_adapter.py -q`: PASS, 20 passed.
- `python -m tools.data_ingestion.ccxt_public_funding_adapter --help`: PASS.
- `python -m tools.data_ingestion.ccxt_public_funding_adapter --start-utc 2020-01-01T00:00:00Z --end-utc 2026-04-11T23:45:00Z`: PASS; wrote frozen scratch artifacts.
- `python -m tools.research_query.run --list-views`: PASS.
- `python tools/dev/diff_scope_summary.py --json`: PASS; no forbidden matches.
- `python tools/dev/verify.py --integrity-views --json --max-output-chars 6000`: PASS; result-population validator passed and all discovered `v_integrity_*` views were clean.
- `python -m pytest -q`: TIMED OUT after 904 seconds with no failure summary; not used as final full-suite merge evidence.
- `python tools/dev/verify.py --full-pytest-sharded --pytest-shards 4 --pytest-shard-workers 4 --full-pytest-timeout-seconds 1500 --json --max-output-chars 4000`: PASS; 4 shards / 76 test files passed. Shard counts: 446 passed; 383 passed; 280 passed, 1 skipped; 275 passed.

Validation environment note:

- The isolated worktree required local ignored D4A data at `data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv` for existing simulator-pilot tests. The file was copied from the root checkout for validation only and remains gitignored/uncommitted.

Snapshot validation:

- Public method: `ccxt.binanceusdm.fapiPublicGetFundingRate`.
- Credentials used: `false`.
- CCXT version: `4.5.59`.
- Expected 8h events: `6879`.
- Observed events: `6879`.
- Observed window: `2020-01-01T00:00:00Z` through `2026-04-11T16:00:00Z`.
- Missing events: `0`.
- Normalized duplicate groups: `0`.
- Raw duplicate rows removed: `0`.
- Outside-window rows: `0`.
- Required normalized fields: PASS.
- Normalized snapshot checksum: `sha256:58cab557e1a35d7832dc8d23424a5c3969706d516de9a9d3c2ed786b224c4666`.
- Validation report checksum: `sha256:844d1ec304d348f2f7528f2b82c585ac1f74b3fbffb265622056781f1160ae3b`.

## Boundary Summary

- Runtime / paper / live paths changed: NO.
- OMS / risk / reconciliation / safe-mode / kill-switch / broker / exchange execution paths changed: NO.
- Private APIs, credentials, account, balance, position, or order methods used: NO.
- Funding wired into backtester, runner, compiler, cost model, or canonical result populations: NO.
- Existing OHLCV, funding parquet, data slices, Strategy Specs, Variant Manifests, Sweep Plans, and Result Populations mutated: NO.
- External dependency files changed: NO.
- CCXT dependency posture: optional import only; local ignored `.venv` provides `ccxt==4.5.59` for validation.
- Adapter snapshot authority: public-data adapter output only; no canonical data authority without separate promotion.

## Merge Status

- PR state: ready for review.
- Final rebase: `git rebase origin/main` was a no-op; branch was up to date.
- Push status: pushed to `origin/ext/integ-ccxt-funding-adapter-01`.
- GitHub mergeability: `MERGEABLE`.

## Active-WP Requirement Traceability

| Active-WP requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Public-only CCXT funding ingestion | Authorization / Implementation requirements | `tools/data_ingestion/ccxt_public_funding_adapter.py`; `scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/provenance.json` | satisfied |
| Fetch once, checksum, frozen snapshot | Authorization / Implementation requirements | `scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/funding_snapshot.*` | satisfied |
| Catalog lineage and validation report | Authorization / Implementation requirements | `scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/catalog_lineage.json`; `scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/validation_report.json`; `docs/data_catalog.md` | satisfied |
| No funding-into-backtester / OHLCV mutation / private auth endpoint | Authorization / Forbidden scope | Changed-file list and boundary summary | satisfied |
| Optional non-runtime dependency posture | Implementation requirements | No dependency-file diff; optional import error path in adapter tests | satisfied |
| Focused adapter tests | Validation | `tests/test_ccxt_public_funding_adapter.py` | satisfied |

## Next Dependency / Runway Note

Funding integration into backtests, cost-model behavior, canonical data promotion,
and runtime/paper/live consumption remain separate gated packages.
