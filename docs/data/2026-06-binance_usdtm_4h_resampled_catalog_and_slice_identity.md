# Binance USDT-M 4h Resampled Catalog And Slice Identity

## Scope

WP-DATA-RESAMPLE-4H-01 adds a derived offline 4h OHLCV slice for Binance
USDT-M BTCUSDT perpetual data.

Package posture:

- User-authorized derived data lineage step.
- Derived from the validated local D4A 15m normalized CSV only.
- UTC 4h boundary resampling only.
- No external acquisition.
- No live API, credentials, exchange, paper/live, runtime, OMS, risk, or
  reconciliation contact.
- No result-population write.
- No Strategy Spec, variant manifest, sweep plan, compiler, runner, query, or
  strategy artifact mutation.

## Parent 15m Facts

The parent slice is:

```text
binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664
```

Parent facts verified before derivation:

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
- Parent row count:
  `220128`
- Parent range:
  `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`
- Parent gaps and duplicates:
  `gap_count=0`, `missing_bar_count=0`, `duplicate_row_count=0`

The dedicated worktree's gitignored parent CSV was populated by exact-byte
copy from an existing local D4A worktree copy with the expected parent SHA256.
No network or exchange source was contacted.

## Resampling Semantics

Each derived 4h candle is built from exactly 16 contiguous 15m rows.

Aggregation:

- `open_time_ms`: first 15m row.
- `open_time`: first 15m row.
- `open`: first 15m row.
- `high`: maximum `high` over the 16 rows.
- `low`: minimum `low` over the 16 rows.
- `close`: last 15m row.
- `volume`: sum over the 16 rows.
- `close_time_ms`: last 15m row `close_time_ms`, validated to equal
  `open_time_ms + 4h - 1ms`.
- `quote_asset_volume`: sum over the 16 rows.
- `num_trades`: sum over the 16 rows.
- `taker_buy_base_vol`: sum over the 16 rows.
- `taker_buy_quote_vol`: sum over the 16 rows.
- `ignore`: numeric sum.

Required invariants:

- Input rows sorted by `open_time`.
- No duplicate 15m `open_time`.
- No missing 15m intervals.
- Parent row count divisible by 16.
- Every output row has exactly 16 parent rows.
- Every group starts on a UTC 4h boundary.
- No partial first or last 4h candle.
- No timezone-local alignment.
- No fill, interpolation, synthetic bar, or deduplication.

## Derived 4h Slice

Derived local CSV:

```text
data/processed/d4h/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_d4h_resampled.csv
```

The CSV remains under gitignored `data/processed/**` and is not committed.

Derived facts:

- CSV SHA256:
  `828ad4a975c157c7ac4d3c873a39a8b6bbfec3cb306e25eb74209c8a01da6ca1`
- Row count:
  `13758`
- Expected row count:
  `13758`
- Range:
  `2020-01-01T00:00:00Z` through `2026-04-11T20:00:00Z`
- UTC 4h alignment:
  `PASS`
- Partial windows:
  `0`
- Gaps and duplicates:
  `gap_count=0`, `missing_bar_count=0`, `duplicate_row_count=0`

## Catalog And Identity

Committed metadata:

- Validation report:
  `research/data_slices/binance_usdtm_btcusdt_4h/binance_usdtm_btcusdt_4h_20200101_20260411.validation_report.json`
- Validation report SHA256:
  `b995532fe76e5960740ffc86cc4e6bb22e4489c38e0920e611b8a1669814cfd8`
- Derivation report:
  `research/data_slices/binance_usdtm_btcusdt_4h/binance_usdtm_btcusdt_4h_20200101_20260411.derivation_report.json`
- Derivation report SHA256:
  `44288299817bd7b11df91ee4335129987980e0e111e49a6ae5635632d1285933`
- Catalog slice:
  `research/data_slices/binance_usdtm_btcusdt_4h/binance_usdtm_btcusdt_4h_20200101_20260411.catalog_slice.json`
- Catalog artifact SHA256:
  `43885198f7d0e53169c3a688fd7b7e0bfd9741ef65da7083e476549674addd57`
- Catalog ref:
  `binance_usdtm_btcusdt_ohlcv_4h.derived_offline_resample.4h.20200101T000000Z.20260411T200000Z.sha256_4379d2f0fad5e79b`
- Derived data slice identity:
  `binance_usdtm_btcusdt_ohlcv_4h:sha256:4379d2f0fad5e79bfd5576b308d01fb6134b0f5acf04013e73e00ce33ca96b30`

Identity inputs include:

- derived dataset id, symbol, venue, market type, stream, and timeframe;
- source type `derived_offline_resample`;
- parent dataset id, parent normalized SHA256, parent validation-report SHA256,
  parent catalog ref, and parent data slice identity;
- derived normalized CSV SHA256;
- derived validation report SHA256 and validation status;
- range, gap, and duplicate summaries;
- resampling method, resampling version, and aggregation map.

The identity hash is SHA256 over canonical JSON with sorted keys, minified
separators, and ASCII encoding.

## Evidence Limit

This package creates derived data and lineage evidence only. It is not strategy
quality evidence by itself, does not write a result population, and creates no
paper/live/runtime/capital authority.
