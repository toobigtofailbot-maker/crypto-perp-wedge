# Repo-Truth Funding Data Contract

- Expected path: `data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_funding_feature_v1.csv`
- Source funding path: `data/processed/binance_um_perp_BTCUSDT_funding_8h_2019-09-10_2026-04-12_2026-04-12T1655Z.parquet`
- Parent OHLCV path: `data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`
- Expected rows: 220128
- Expected range: 2020-01-01T00:00:00Z through 2026-04-11T23:45:00Z
- Expected SHA256: `70cbe2040c8fb5987b2971a13c8bd4f66e91152331d5b641d684673364be3931`
- Expected columns: timestamp, open, high, low, close, volume, funding_rate
- Availability: `FULL_HISTORY_PUBLIC_ARCHIVE` / `PUBLIC_FUNDING_ARCHIVE`
- Runner path: the expected path above, passed through the declared non-OHLCV column path.

These values match the merged PR #560 status entry and materialization manifest.
