# WP-LAB-DATA-EXPANSION-01 - Public Perp-Native Data Expansion Coverage

## WP Id / Title

- WP id: `WP-LAB-DATA-EXPANSION-01`
- Title: Add public perp-native data expansion coverage

## Branch / PR

- Branch: `lab/data-expansion-public-perp-01`
- PR: pending

## Package Class

Data ingestion/catalog/provenance, public-only.

## Scope Summary

This package adds an offline repo-owned coverage and sample-parsing adapter for
public perp-native data streams needed by later Side 12 strategy-family work.
It does not fetch live data by default. It records endpoint/source coverage,
history-depth class, public/private posture, pagination/rate-limit notes,
lineage keys, and feature-family runway, then parses committed fixture responses
into normalized sample records for validation and lineage checks.

Existing repo-truth surfaces are preserved, not reimplemented:

- `tools/data_ingestion/ccxt_public_funding_adapter.py` remains the funding
  history adapter.
- `docs/data_catalog.md` already records funding plus full-history mark, index,
  and premium kline datasets.

## Endpoint Coverage

Coverage matrix entries are written to
`scratch/WP-LAB-DATA-EXPANSION-01/coverage_matrix.json` and
`scratch/WP-LAB-DATA-EXPANSION-01/coverage_matrix.md`.

Adopted or preserved public sources:

- Existing CCXT/Binance public funding history adapter: preserved,
  `backfillable`.
- Existing Binance mark/index/premium kline catalog surfaces: preserved,
  `backfillable`.
- Binance public REST mark-price snapshot: adopted, `recent_only`.
- Binance public REST current open interest: adopted, `recent_only`.
- Binance public REST open-interest statistics: adopted, `recent_only`, latest
  one month per primary docs.
- Binance public REST top trader long/short position ratio: adopted,
  `recent_only`, latest 30 days per primary docs.
- Binance public REST top trader long/short account ratio: adopted,
  `recent_only`, latest 30 days per primary docs.
- Binance public REST global long/short account ratio: adopted, `recent_only`,
  latest 30 days per primary docs.
- Binance public REST taker buy/sell volume ratio: adopted, `recent_only`,
  latest 30 days per primary docs.
- Binance public REST aggregate trades and recent trades: adopted,
  `recent_only`; aggregate-trades REST history is limited to not older than
  24 hours per primary docs.
- `data.binance.vision` public futures UM aggregate-trade and trade archives:
  adopted as public archive coverage, `backfillable`, with per-file availability
  verification required before any canonical use.
- Binance public REST exchange metadata: adopted, `recent_only`.

Primary docs checked on `2026-06-21`:

- Binance USD-M Futures market-data REST pages for funding rate, mark price,
  mark/index/premium klines, open interest, open interest statistics, top trader
  ratios, global long/short ratio, taker buy/sell volume, aggregate trades,
  recent trades, and exchange information.
- `data.binance.vision` public futures UM archive listings for historical
  aggregate-trade and trade files.

## Changed Files

- `tools/data_ingestion/perp_public_data_adapter.py`
- `tests/test_perp_public_data_adapter.py`
- `tests/fixtures/data_ingestion/perp_public_data/*`
- `scratch/WP-LAB-DATA-EXPANSION-01/coverage_matrix.json`
- `scratch/WP-LAB-DATA-EXPANSION-01/coverage_matrix.md`
- `scratch/WP-LAB-DATA-EXPANSION-01/sample_catalog_lineage.json`
- `scratch/WP-LAB-DATA-EXPANSION-01/provenance.json`
- `scratch/WP-LAB-DATA-EXPANSION-01/validation_report.json`
- `scratch/WP-LAB-DATA-EXPANSION-01/validation_report.md`
- `docs/status_entries/WP-LAB-DATA-EXPANSION-01.md`

`docs/data_catalog.md` was intentionally left unchanged because this package
records noncanonical sample lineage in scratch artifacts and existing catalog
entries already cover the preserved funding/mark/index/premium surfaces.

## Validation Summary

- `python -m pytest tests/test_perp_public_data_adapter.py -q`: PASS,
  16 passed.
- `python -m tools.data_ingestion.perp_public_data_adapter --coverage-only --output-dir scratch/WP-LAB-DATA-EXPANSION-01`: PASS; wrote coverage,
  sample lineage, provenance, and validation artifacts.
- `python -m pytest tests/test_perp_public_data_adapter.py tests/test_ccxt_public_funding_adapter.py tests/test_ccxt_public_funding_ingest.py -q`: PASS,
  36 passed.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_perp_public_data_adapter.py tests/test_ccxt_public_funding_adapter.py tests/test_ccxt_public_funding_ingest.py -q`: PASS,
  36 passed.
- `python -m tools.registry.validate_indicator_catalogs`: PASS.
- `python -m tools.registry.validate_strategy_specs`: PASS.
- `python -m tools.registry.validate_result_populations`: PASS.
- `python -m tools.research_query.run --list-views`: PASS.
- `python tools/dev/diff_scope_summary.py`: PASS; expected package files only,
  no forbidden-path matches.
- `git diff --check`: PASS.
- `python -m pytest -q`: BLOCKED in ambient Python 3.14 because that
  interpreter lacks repo dependencies (`binance`, `pandas`, `numpy`).
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`:
  TIMED OUT after 1204 seconds without a failure summary.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/verify.py --integrity-views --full-pytest-sharded --pytest-shards 4 --pytest-shard-workers 4 --full-pytest-timeout-seconds 1500 --json --max-output-chars 4000`:
  initially found the known isolated-worktree local-data limitation in
  `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage`
  because the gitignored local normalized D4A CSV was absent. After copying
  `data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`
  from the root checkout into this worktree for validation only, the failing
  shard command passed: 395 passed, 4 warnings. The other three verifier shards
  had already passed: 256 passed; 425 passed with 2 warnings; and shard 3
  passed in the verifier output.

Generated validation report:

- Endpoint definitions: `16`.
- Sample endpoints parsed: `16`.
- Sample records parsed: `17`.
- Aggregate normalized sample checksum:
  `sha256:273b7fd8d1a51dd89993a1d1a67e3f4905c62818594b622048a03b107d268fdd`.
- Network calls performed: `false`.
- Credentials used: `false`.
- Canonical write: `false`.
- Runtime / paper / live contact: `false`.

## Boundary Summary

- Dependency files changed: NO.
- External code copied: NO.
- External library output made canonical: NO.
- Existing frozen data slices mutated: NO.
- Canonical evidence, Strategy Specs, Variant Manifests, Sweep Plans, Result
  Populations, candidate lifecycle, promotion/readiness, trial log, schema,
  validator, query-layer, compiler, runner, or backtester behavior changed: NO.
- Runtime, paper, live, OMS, risk, reconciliation, safe-mode, kill-switch,
  broker, exchange execution, account, order, or credential paths touched: NO.
- Private/authenticated endpoints used: NO.

## Merge Status

- PR state: pending.
- Push status: pending.
