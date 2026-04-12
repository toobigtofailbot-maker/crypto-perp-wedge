# Data Catalog

## Dataset template

* Source (endpoint / public dump):
* Symbol/Contract:
* Timeframe:
* Range (start/end):
* Created (UTC):
* SHA256:
* Storage path:
  



\## Dataset: BTCUSDT 1h sample (Binance USDT-M Perp)

\- Source: Binance Futures API `/fapi/v1/klines`

\- Symbol/Contract: BTCUSDT (USDT-M Perpetual)

\- Timeframe: 1h

\- Range (start/end): 2026-02-06 / 2026-02-27

\- Created (UTC): 2026-02-27T0627Z

\- SHA256: 1af10c9a808bdce6d0744f44b0962b351dafb043995c1e9867f68b5b489377a4

\- Storage path: data/processed/binance\_um\_perp\_BTCUSDT\_1h\_2026-02-06\_2026-02-27\_2026-02-27T0627Z.csv


## Dataset: BTCUSDT 1h range (Binance USDT-M Perp) – Parquet
- Source: Binance Futures API `/fapi/v1/klines`
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Timeframe: 1h
- Range (start/end): 2026-01-01 / 2026-02-27
- Created (UTC): 2026-02-27T0721Z
- SHA256: 7ee8deba11fd616d127c0f7a879199868c0634105c30831388c3521293375ed6
- Storage path: data/processed/binance_um_perp_BTCUSDT_1h_2026-01-01_2026-02-27_2026-02-27T0721Z.parquet

## Dataset: BTCUSDT 4h range (Binance USDT-M Perp) – Parquet
- Source: Binance Futures API `/fapi/v1/klines`
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Timeframe: 4h
- Range (start/end): 2026-01-01 / 2026-02-27
- Created (UTC): 2026-02-27T0721Z
- SHA256: 2e4613306880068fc7fa75baf50e3735d7d9f917d072da257191090c726a6344
- Storage path: data/processed/binance_um_perp_BTCUSDT_4h_2026-01-01_2026-02-27_2026-02-27T0721Z.parquet

## Dataset: BTCUSDT funding rates (Binance USDT-M Perp) – Parquet
- Source: Binance Futures API `/fapi/v1/fundingRate`
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Timeframe: 8h funding events
- Range (start/end): 2026-01-01 / 2026-02-27
- Created (UTC): 2026-02-27T0739Z
- SHA256: 47b662918ebfe9a4610959cbd6963002f4a1a7e26a1465b3fcb045299ba4d5e3
- Storage path: data/processed/binance_um_perp_BTCUSDT_funding_8h_2026-01-01_2026-02-27_2026-02-27T0739Z.parquet

## Dataset: BTCUSDT premium index snapshots (Binance USDT-M Perp) – Parquet
- Source: Binance Futures API `/fapi/v1/premiumIndex`
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Timeframe: snapshot polling (1s configured)
- Range (start/end): 2026-03-11 / 2026-03-11
- Created (UTC): 2026-03-11T0104Z
- SHA256: 26c78fd2ddea0fc63d09ad117d54c5e797608c18830ad36eeb2ac986b5ccb144
- Storage path: data/processed/binance_um_perp_BTCUSDT_premium_index_snapshots_2026-03-11_2026-03-11_2026-03-11T0104Z.parquet

## Dataset: BTCUSDT book ticker snapshots (Binance USDT-M Perp, 10s deterministic buckets) – Parquet
- Source: Binance Futures API `/fapi/v1/ticker/bookTicker`
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Timeframe: deterministic bucketed snapshots (10s)
- Range (start/end): 2026-03-11 / 2026-03-11
- Created (UTC): 2026-03-11T0104Z
- SHA256: feacd9e1a30f898d09925006518064fb4526c42d8b0ec3dec447f4e4bf82d30b
- Storage path: data/processed/binance_um_perp_BTCUSDT_book_ticker_10s_2026-03-11_2026-03-11_2026-03-11T0104Z.parquet

## Dataset: BTCUSDT funding schedule metadata (Binance USDT-M Perp) – Parquet
- Source: Binance Futures API `/fapi/v1/fundingInfo` + `/fapi/v1/premiumIndex`
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Timeframe: snapshot polling (1s configured)
- Range (start/end): 2026-03-11 / 2026-03-11
- Created (UTC): 2026-03-11T0104Z
- SHA256: 6ec3ca2f7302a65413ed3f05beeb4e1d8f97cd3ae975c37af8e499c120dffb21
- Storage path: data/processed/binance_um_perp_BTCUSDT_funding_schedule_metadata_2026-03-11_2026-03-11_2026-03-11T0104Z.parquet

## Dataset: BTCUSDT 15m full history (Binance USDT-M Perp) – Parquet
- Source: data.binance.vision bulk archives + Binance Futures API
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Timeframe: 15m
- Range (start/end): 2020-01-01 / 2026-04-11
- Created (UTC): 2026-04-12T1655Z
- SHA256: 3fd05b841210962147a92bd77167ccefce57f6eb812cb55565d6f6cbb5154c31
- Storage path: data/processed/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet

## Dataset: BTCUSDT 30m full history (Binance USDT-M Perp) – Parquet
- Source: data.binance.vision bulk archives + Binance Futures API
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Timeframe: 30m
- Range (start/end): 2020-01-01 / 2026-04-11
- Created (UTC): 2026-04-12T1655Z
- SHA256: 059cb1ab3e5194578a39823e787ab29f41f6ce061309371cd414e0936aa9625b
- Storage path: data/processed/binance_um_perp_BTCUSDT_30m_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet

## Dataset: BTCUSDT 1h full history (Binance USDT-M Perp) – Parquet
- Source: data.binance.vision bulk archives + Binance Futures API
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Timeframe: 1h
- Range (start/end): 2020-01-01 / 2026-04-11
- Created (UTC): 2026-04-12T1655Z
- SHA256: 9f77e67628e2ece56d114af1af45d732c840df569a5f51fda3ac2a923349da54
- Storage path: data/processed/binance_um_perp_BTCUSDT_1h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet

## Dataset: BTCUSDT 4h full history (Binance USDT-M Perp) – Parquet
- Source: data.binance.vision bulk archives + Binance Futures API
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Timeframe: 4h
- Range (start/end): 2020-01-01 / 2026-04-11
- Created (UTC): 2026-04-12T1655Z
- SHA256: 4aed22360d52e01ea724637f82593c4f91ca2bcdad1581a92f434d4077669e50
- Storage path: data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet

## Dataset: BTCUSDT 1d full history (Binance USDT-M Perp) – Parquet
- Source: data.binance.vision bulk archives + Binance Futures API
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Timeframe: 1d
- Range (start/end): 2020-01-01 / 2026-04-11
- Created (UTC): 2026-04-12T1655Z
- SHA256: c6e2e7ce030db6a710d95e48325fc77b27efbbdd441199b3d7458d4394795802
- Storage path: data/processed/binance_um_perp_BTCUSDT_1d_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet

## Dataset: BTCUSDT funding rates full history (Binance USDT-M Perp) – Parquet
- Source: Binance Futures API `/fapi/v1/fundingRate`
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Timeframe: 8h funding events
- Range (start/end): 2019-09-10 / 2026-04-12
- Created (UTC): 2026-04-12T1655Z
- SHA256: 5f0da7478ccf3514af41dff9958b579cd2f797a2716001b0fa10a11059912798
- Storage path: data/processed/binance_um_perp_BTCUSDT_funding_8h_2019-09-10_2026-04-12_2026-04-12T1655Z.parquet
