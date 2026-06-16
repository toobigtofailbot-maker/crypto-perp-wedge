# WP-DATA-RESAMPLE-4H-01 - Derived BTCUSDT 4h OHLCV Slice

## Scope

WP-DATA-RESAMPLE-4H-01 adds a user-authorized derived-data lineage slice:
BTCUSDT Binance USDT-M perpetual OHLCV 4h, deterministically resampled from
the validated local D4A 15m normalized CSV.

This package creates data lineage evidence only. It creates no strategy quality
evidence, result population, runtime authority, paper/live authority, capital
authority, or downstream promotion authority.

## Branch / Worktree

- Branch: `data/resample-btcusdt-15m-to-4h`
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-DATA-RESAMPLE-4H-01`
- Base: `origin/main` at `a530270`

## Changed Files

- `tools/data/resample_binance_usdtm_15m_to_4h.py`
- `tests/test_resample_binance_usdtm_15m_to_4h.py`
- `.gitattributes`
- `research/data_slices/binance_usdtm_btcusdt_4h/binance_usdtm_btcusdt_4h_20200101_20260411.validation_report.json`
- `research/data_slices/binance_usdtm_btcusdt_4h/binance_usdtm_btcusdt_4h_20200101_20260411.derivation_report.json`
- `research/data_slices/binance_usdtm_btcusdt_4h/binance_usdtm_btcusdt_4h_20200101_20260411.catalog_slice.json`
- `docs/data/2026-06-binance_usdtm_4h_resampled_catalog_and_slice_identity.md`
- `docs/status_entries/WP-DATA-RESAMPLE-4H-01.md`

The derived 4h CSV is local and gitignored:

```text
data/processed/d4h/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_d4h_resampled.csv
```

## Parent 15m

- Parent catalog slice path:
  `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json`
- Parent normalized path:
  `data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`
- Parent normalized SHA256:
  `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`
- Parent raw source SHA256:
  `343b639e35ce79824d26bddf6d70af2641c9d76003301e303f83cdf61d4feab4`
- Parent validation report SHA256:
  `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`
- Parent data slice identity:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- Parent row count:
  `220128`
- Parent range:
  `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`
- Parent gaps/duplicates:
  `gap_count=0`, `missing_bar_count=0`, `duplicate_row_count=0`

The dedicated worktree parent CSV was populated by exact-byte copy from an
existing local D4A worktree copy with the expected parent SHA256. No external
acquisition, exchange/API contact, or parent data mutation occurred.

## Derived 4h Artifact

- Output CSV path:
  `data/processed/d4h/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_d4h_resampled.csv`
- Output CSV SHA256:
  `828ad4a975c157c7ac4d3c873a39a8b6bbfec3cb306e25eb74209c8a01da6ca1`
- Committed to git:
  NO; `data/processed/**` remains gitignored.
- Row count / expected:
  `13758 / 13758`
- Range:
  `2020-01-01T00:00:00Z` through `2026-04-11T20:00:00Z`
- Aggregation:
  exact 16-row UTC 15m groups; open first, high max, low min, close last,
  volume/quote/trades/taker/ignore sums.
- UTC 4h alignment:
  `PASS`
- Partial windows:
  `0`
- Gaps/duplicates:
  `gap_count=0`, `missing_bar_count=0`, `duplicate_row_count=0`

## Catalog / Validation

- Validation report path:
  `research/data_slices/binance_usdtm_btcusdt_4h/binance_usdtm_btcusdt_4h_20200101_20260411.validation_report.json`
- Validation report SHA256:
  `b995532fe76e5960740ffc86cc4e6bb22e4489c38e0920e611b8a1669814cfd8`
- Validation status:
  `PASS`
- Derivation report path:
  `research/data_slices/binance_usdtm_btcusdt_4h/binance_usdtm_btcusdt_4h_20200101_20260411.derivation_report.json`
- Derivation report SHA256:
  `44288299817bd7b11df91ee4335129987980e0e111e49a6ae5635632d1285933`
- Catalog path:
  `research/data_slices/binance_usdtm_btcusdt_4h/binance_usdtm_btcusdt_4h_20200101_20260411.catalog_slice.json`
- Catalog artifact SHA256:
  `43885198f7d0e53169c3a688fd7b7e0bfd9741ef65da7083e476549674addd57`
- Catalog identity:
  `binance_usdtm_btcusdt_ohlcv_4h:sha256:4379d2f0fad5e79bfd5576b308d01fb6134b0f5acf04013e73e00ce33ca96b30`
- Catalog ref:
  `binance_usdtm_btcusdt_ohlcv_4h.derived_offline_resample.4h.20200101T000000Z.20260411T200000Z.sha256_4379d2f0fad5e79b`

## Validation Summary

- `git status --short`: scoped new files only.
- `git diff --check`: pass.
- `git diff --cached --check`: pass.
- `python -m pytest tests/test_resample_binance_usdtm_15m_to_4h.py -q`:
  pass, 10 tests.
- `python -m tools.registry.validate_strategy_specs`: pass.
- `python -m tools.registry.validate_variant_sweep_artifacts`: pass.
- `python -m tools.registry.validate_indicator_catalogs`: pass.
- `python -m tools.registry.validate_result_populations`: pass.
- `python -m tools.registry.validate_candidate_registry`: pass.
- `python -m tools.registry.validate_paper_state`: pass.
- `python -m tools.research_query.run --list-views`: pass.
- `v_integrity_*`: clean, 55 views.
- `tools/dev/diff_scope_summary.py --check-forbidden`: advisory false-positive
  on the three package-authorized `research/data_slices/binance_usdtm_btcusdt_4h`
  metadata files because the helper treats broad `research/` as forbidden and
  its authorized-path scope support does not include data-slice metadata.
- `tools/dev/verify.py --integrity-views ... --json`: integrity views clean;
  wrapper overall status failed only on the same `research/data_slices` advisory
  false-positive.
- `tools/dev/verify.py --full-pytest-sharded --pytest-shards 4 ... --json`:
  all 4 pytest shards passed; 1267 passed, 1 skipped. Wrapper overall status
  failed only on the same `research/data_slices` advisory false-positive.

## Boundary Check

- External acquisition: NO.
- Exchange/API/credentials: NO.
- Parent 15m mutated: NO.
- Strategy Spec / variant manifest / sweep plan / result population mutated: NO.
- Canonical result population written: NO.
- Compiler / runner / query / lib touched: NO.
- Candidate / walk-forward / paper / live / runtime / capital authority: NO.
- OMS / risk / reconciliation / broker / exchange paths touched: NO.

## Decision

Ready for PR review with the advisory scope-helper false-positive reported
explicitly.
