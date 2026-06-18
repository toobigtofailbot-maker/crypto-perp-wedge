# EXT-CCXT-DATA-INGESTION-PILOT-01 - CCXT Public Funding Ingestion Pilot

## Branch / PR

- Branch: `ext/ccxt-data-ingestion-pilot-01`
- PR: `https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/510`

## Package Class

External-repo adoption pilot / public data ingestion / non-runtime data lineage.

## Scope Summary

This package adds an isolated CCXT public REST funding-rate ingestion pilot for
BTCUSDT Binance USDT-M perpetual funding history over the current BTCUSDT 15m
D4 data window. The pilot fetches public funding rows once, freezes raw and
normalized JSONL snapshots, writes checksum/provenance/validation/catalog-lineage
scratch artifacts, and records a non-canonical catalog pointer.

The pilot does not wire funding into the backtester, cost model, runner,
compiler, Strategy Specs, Variant Manifests, Sweep Plans, Result Populations,
runtime, paper, live, OMS, risk, broker, exchange execution, safe mode, or kill
switch paths.

## Changed Files

- `tools/external_pilots/ccxt_public_funding_ingest.py`
- `tests/test_ccxt_public_funding_ingest.py`
- `docs/status_entries/EXT-CCXT-DATA-INGESTION-PILOT-01.md`
- `docs/data_catalog.md`
- `scratch/EXT-CCXT-DATA-INGESTION-PILOT-01/funding_snapshot.normalized.jsonl`
- `scratch/EXT-CCXT-DATA-INGESTION-PILOT-01/funding_snapshot.raw.jsonl`
- `scratch/EXT-CCXT-DATA-INGESTION-PILOT-01/funding_snapshot.sha256`
- `scratch/EXT-CCXT-DATA-INGESTION-PILOT-01/validation_report.json`
- `scratch/EXT-CCXT-DATA-INGESTION-PILOT-01/validation_report.md`
- `scratch/EXT-CCXT-DATA-INGESTION-PILOT-01/provenance.json`
- `scratch/EXT-CCXT-DATA-INGESTION-PILOT-01/catalog_lineage.json`

## Dependency / Adoption Mode

No repo dependency file is changed. Current repo truth has one broad dependency
surface, `requirements.txt` plus `requirements.lock.txt`, and no isolated
non-runtime external-pilot dependency group.

The adapter uses an optional `ccxt` import and fails closed with setup guidance
if `ccxt` is absent. For the live pilot run, `ccxt==4.5.59` was installed only
into the local ignored `.venv`; that local install is not a committed dependency
or runtime requirement.

Recommendation: `ADOPT_AS_PUBLIC_DATA_ADAPTER`, conditional on a future package
creating an explicit non-runtime external-pilot dependency group or otherwise
approving dependency isolation.

## Data Window

- Target OHLCV window: `2020-01-01T00:00:00Z` through
  `2026-04-11T23:45:00Z`
- Funding observed start: `2020-01-01T00:00:00Z`
- Funding observed end: `2026-04-11T16:00:00Z`
- Expected 8h funding events: `6879`
- Observed funding rows: `6879`
- Normalized snapshot checksum:
  `sha256:58cab557e1a35d7832dc8d23424a5c3969706d516de9a9d3c2ed786b224c4666`

The raw Binance/CCXT `fundingTime` often carries a small positive millisecond
offset from the nominal 8h boundary. The normalized snapshot preserves the exact
raw value in `exchange_funding_time_*` and stores the nominal 8h event boundary
in `funding_time_*`. Validation observed maximum absolute offset `47ms`, within
the pilot tolerance of `1000ms`.

## Validation Summary

- `.\.venv\Scripts\python.exe -m pytest tests\test_ccxt_public_funding_ingest.py -q`:
  `PASS`, 9 passed.
- `.\.venv\Scripts\python.exe -m tools.external_pilots.ccxt_public_funding_ingest`:
  `PASS`; wrote raw snapshot, normalized snapshot, checksum, validation,
  provenance, and catalog-lineage files under
  `scratch/EXT-CCXT-DATA-INGESTION-PILOT-01/`.
- `.\.venv\Scripts\python.exe -m pytest tests\test_research_query.py -q`:
  `PASS`, 64 passed.
- `.\.venv\Scripts\python.exe -m pytest tests\test_offline_research_runner.py -q`:
  `PASS`, 94 passed, 2 existing timestamp parsing warnings.
- `.\.venv\Scripts\python.exe tools\dev\verify.py --integrity-views --full-pytest-sharded --pytest-shards 4 --pytest-shard-workers 4 --full-pytest-timeout-seconds 900`:
  `PASS`; diff checks, forbidden-scope check, result-population validator,
  query view listing, 4 pytest shards over 72 test files, and all discovered
  integrity views passed/clean.

Validation report:

- Public-only method: `ccxt.binanceusdm.fapiPublicGetFundingRate`.
- Credentials used: `NO`.
- Coverage: `6879 / 6879` expected events.
- Gaps: `0`.
- Duplicate timestamps: `0`.
- Outside-window rows: `0`.
- UTC 8h alignment: `PASS` on nominal `funding_time_ms`.
- Funding numeric parse: `PASS`.
- Provenance complete: `PASS`.

## Boundary Summary

- Canonical Result Population write: `NO`.
- Canonical Strategy Spec / VM / Sweep Plan mutation: `NO`.
- Existing OHLCV slice mutation: `NO`.
- Backtester / cost-model integration: `NO`.
- Runner / compiler behavior change: `NO`.
- Runtime / paper / live / OMS / risk / broker / exchange execution /
  credential paths touched: `NO`.
- CCXT output authority: non-canonical external public-data pilot only.

## Recommendation

`ADOPT_AS_PUBLIC_DATA_ADAPTER`.

Rationale: CCXT public REST fetched the full target funding-event coverage
without credentials, the frozen snapshot validates cleanly, raw and normalized
provenance are preserved, dependency mutation was avoided, and no protected or
canonical evidence paths changed.

## Merge Status

Ready PR #510 opened. GitHub connector reported `mergeable=false` immediately
after creation; this may be transient, but this fragment does not call the PR
merge-ready while GitHub reports that state.

## Next Dependency / Runway Note

Next gated step: design or approve a non-runtime external-pilot dependency
surface for CCXT, then run a separate funding-into-backtest integration design
package. Funding cost-model integration remains explicitly out of scope here.
