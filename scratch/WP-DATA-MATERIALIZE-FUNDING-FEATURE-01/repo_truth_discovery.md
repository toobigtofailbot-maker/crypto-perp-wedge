# WP-DATA-MATERIALIZE-FUNDING-FEATURE-01 Repo-Truth Discovery

## Facts

- PR #559 / `WP-RUNNER-DATA-PATH-NONOHLCV-01` is merged at base commit `c34e4c4`.
- Local ignored full-history funding data exists at `C:\GitHub\crypto-perp-wedge\data\processed\binance_um_perp_BTCUSDT_funding_8h_2019-09-10_2026-04-12_2026-04-12T1655Z.parquet`. It has 7,220 rows and SHA256 `5f0da7478ccf3514af41dff9958b579cd2f797a2716001b0fa10a11059912798`.
- The target D4A parent is `C:\GitHub\crypto-perp-wedge\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`, with 220,128 rows and SHA256 `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`.
- The D4A range is `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`; funding contains 6,879 events in that window and covers the first bar close.
- Compiler-visible funding fields are `funding_rate` and `funding_mark_price`. This WP materializes only `funding_rate`.
- `funding_rate` is labeled `FULL_HISTORY_PUBLIC_ARCHIVE` with source class `PUBLIC_FUNDING_ARCHIVE`; its condition is that aligned funding records cover the claimed evidence window.
- The PR #559 runner accepts declared non-OHLCV columns from `data_ref` / `host_data_refs`, preserves them in its input frame, emits an identity-bearing `data_availability_claim`, and fails closed on absent or ineligible declared columns.
- Funding feature materialization and funding P&L are distinct. `lib/backtest.py` has a default-off `funding_cost_mode`; this WP does not change or enable it.
- Canonical OHLCV Result Populations `RP-2592`, `RP-3731`, and `RP-7134` exist, but no committed command deterministically reconstructs those exact artifacts from their committed parents and local data.

## Decision Applied by Package Contract

- Use bar-close as-of alignment: a bar receives the latest funding event timestamp at or before that bar's close. Carry forward only from an already observed event.
- Store the 15.45 MB full materialized CSV under ignored `data/processed/d4a/`; commit only code, tests, lineage/checksum reports, and status artifacts.

## Repo-Truth Adjustments

- The package is not blocked: adequate local ignored full-history funding and D4A data exist in the root checkout, although a fresh worktree contains only tracked `.gitkeep` files by default.
- Exchange funding timestamps contain millisecond-scale jitter. Gap reporting uses an 8-hour plus 1-minute tolerance and reports zero gaps over that threshold; no timestamps are rounded for alignment.
- Exact RP byte replay remains blocked because repo-native replay commands are absent. No general replay framework is added.

## Open Question

- Whether a later authorized package supplies an exact canonical RP replay contract and expected normalization rules.
