# WP-D4A / Data Block 1 - First Real-Data D4 Catalog Slice Artifact

## WP Id / Title

WP-D4A / Data Block 1 - First real-data D4 catalog slice artifact.

## Branch / PR

- Branch: `codex/data-block-1-d4a-first-real-data-catalog-slice`
- PR: pending

## Package Class

T3 data provenance/catalog artifact.

## Scope Summary

Creates the first lightweight real-data D4 artifact chain for Binance USDT-M
BTCUSDT 15m OHLCV data. The committed artifacts are JSON reports/catalog only:
a D2 import/provenance report, a D3 PASS validation report, and a D4
catalog/slice entry. Bulk OHLCV data remains local and gitignored under
`data/processed/d4a/`.

The local D2-compatible source CSV was generated offline from the existing
repo-cataloged real 15m Parquet at
`data/processed/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`
whose repo catalog SHA256 is
`3fd05b841210962147a92bd77167ccefce57f6eb812cb55565d6f6cbb5154c31`.

## Changed Files

- `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.import_report.json`
- `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.validation_report.json`
- `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json`
- `docs/status_entries/WP-D4A.md`
- `docs/project_status.md`

## Artifact Paths

- D2 import/provenance report: `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.import_report.json`
- D3 validation report: `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.validation_report.json`
- D4 catalog/slice JSON: `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json`

## D2 Import / Provenance Report Identity

- Artifact SHA256: `553c320d6639ceca4422f0f08620550c558e05162eb16aff30854db76a7246d3`
- D2 normalized data slice identity: `binance_usdtm:BTCUSDT:ohlcv:15m:2020-01-01T00:00:00Z:2026-04-11T23:45:00Z:wp-d2-offline-binance-usdtm-15m-v1:sha256:c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`

## D3 Validation Report Identity

- Artifact SHA256: `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`
- Status: `PASS`
- Validator version: `wp-d3-offline-binance-usdtm-15m-validator-v1`

## D4 Catalog Ref / Slice Identity

- D4 catalog ref: `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
- D4 data slice identity: `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- D4 catalog artifact SHA256: `80a080336853ca96c81e2033a381527caec3737c1a817c111fc61d4e8c685327`
- D4 status: `PASS` / usable offline validated slice.

## Row Count / Timestamp Range / Gap Facts / Duplicate Facts

- Row count: `220128`
- Expected row count: `220128`
- Timestamp range: `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`
- Gap facts: `gap_count=0`, `missing_bar_count=0`, `gaps=[]`
- Duplicate facts: `duplicate_group_count=0`, `duplicate_row_count=0`, `duplicates=[]`

## Raw Source Hash / Normalized Hash

- Raw local D2-compatible source CSV SHA256: `343b639e35ce79824d26bddf6d70af2641c9d76003301e303f83cdf61d4feab4`
- Normalized CSV SHA256: `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`
- Source Parquet repo-catalog SHA256: `3fd05b841210962147a92bd77167ccefce57f6eb812cb55565d6f6cbb5154c31`

## Determinism Proof

- D3 validation rerun against the same normalized CSV produced the same report
  SHA256: `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`.
- D4 catalog rerun against the same normalized CSV, import report, and D3 report
  bytes produced the same catalog ref and D4 data slice identity:
  `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
  and
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`.

## Validation Summary

- `git diff --check`: pass.
- `python -m pytest tests/test_import_binance_usdtm_15m.py -q`: pass, 11 tests.
- `python -m pytest tests/test_validate_binance_usdtm_15m.py -q`: pass, 12 tests.
- `python -m pytest tests/test_catalog_binance_usdtm_15m.py -q`: pass, 12 tests.
- D3 determinism rerun: pass, validation report SHA256 repeated as
  `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`.
- D4 determinism rerun: pass, catalog ref and D4 data slice identity stable.
- `python -m tools.registry.validate_result_populations`: pass.
- `python -m tools.research_query.run --list-views`: pass.
- `v_integrity_*`: clean, 55 views.
- `python tools/dev/diff_scope_summary.py`: pass; research/data_slices matches
  the active artifact scope.
- `python -m pytest -q`: environment-only failure after 1,184 passed tests
  because the isolated worktree lacks gitignored local fixture
  `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`
  required by `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window`.
  No data file is committed or pulled into scope.

## Boundary Summary

Offline artifact generation only. No production-scale OHLCV data is committed.
No live API, network download, credentials, result population, sweep, runner,
compiler, backtester, lib, schema, validator, query-layer, Strategy Spec,
variant manifest, sweep plan, runtime, paper, live, OMS, reconciliation, risk,
safe-mode, kill-switch, broker, exchange, order-path, policy, ranking,
readiness, recommendation, promotion, transition, or downstream authority change
is included.

## Runner D4-Provenance Assessment

Repo-truth inspection of `tools/research_runner/run_offline_sweep.py` shows the
current canonical 15m path still assigns
`data_catalog_ref=15m_ohlcv_test_fixture_offline_only` and
`data_slice_identity=csv_fixture:<sha256>` from the caller-supplied CSV. The
runner does not currently accept or record a D4 catalog ref / D4 slice identity
as the honest real-data provenance input for result-population provenance.

## D5A Needed?

Yes. D5A is needed before D5 unless a later merged package changes runner
provenance behavior. D4A does not patch the runner.

## Merge Status

Pending PR at package execution time.

## Next Dependency / Runway Note

D5 remains blocked on runner provenance honesty. The next runway step is D5A if
Main/Karl wants the runner to consume and record this D4 catalog ref and D4
slice identity before any real-data result population package.
