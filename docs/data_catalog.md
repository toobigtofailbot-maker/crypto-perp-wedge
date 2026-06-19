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

## Dataset: BTCUSDT mark price klines full history (Binance USDT-M Perp) - Parquet (15m)
- Source: data.binance.vision monthly archives + historical daily overlay + Binance Futures REST repair
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Stream: markPriceKlines
- Timeframe: 15m
- Range (start/end): 2019-12-23 / 2026-04-11
- Created (UTC): 2026-04-12T2316Z
- SHA256: 80a14b519817c653a8fa17f4e144b01612dd8fe32c11acfa93dad6e217aad6e0
- Storage path: data/processed/binance_um_perp_BTCUSDT_mark_price_15m_2019-12-23_2026-04-11_2026-04-12T2316Z.parquet
- Known irreparable gaps: 2 bar(s), largest window 1 bar(s); see data/irreparable_gaps.json

## Dataset: BTCUSDT mark price klines full history (Binance USDT-M Perp) - Parquet (30m)
- Source: data.binance.vision monthly archives + historical daily overlay + Binance Futures REST repair
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Stream: markPriceKlines
- Timeframe: 30m
- Range (start/end): 2019-12-23 / 2026-04-11
- Created (UTC): 2026-04-12T2327Z
- SHA256: 2706cf22c20e05acfb69808fe7544c4746c9d17e268f5868c319d22ced1c1c4a
- Storage path: data/processed/binance_um_perp_BTCUSDT_mark_price_30m_2019-12-23_2026-04-11_2026-04-12T2327Z.parquet
- Known irreparable gaps: 0 bar(s), largest window 0 bar(s); see data/irreparable_gaps.json

## Dataset: BTCUSDT mark price klines full history (Binance USDT-M Perp) - Parquet (1h)
- Source: data.binance.vision monthly archives + historical daily overlay + Binance Futures REST repair
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Stream: markPriceKlines
- Timeframe: 1h
- Range (start/end): 2019-12-23 / 2026-04-11
- Created (UTC): 2026-04-12T2338Z
- SHA256: ba3bb5d632ef479fe56959907763ee7709f0d5fa684b91d78f6c7577fd7a512b
- Storage path: data/processed/binance_um_perp_BTCUSDT_mark_price_1h_2019-12-23_2026-04-11_2026-04-12T2338Z.parquet
- Known irreparable gaps: 0 bar(s), largest window 0 bar(s); see data/irreparable_gaps.json

## Dataset: BTCUSDT mark price klines full history (Binance USDT-M Perp) - Parquet (4h)
- Source: data.binance.vision monthly archives + historical daily overlay + Binance Futures REST repair
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Stream: markPriceKlines
- Timeframe: 4h
- Range (start/end): 2019-12-23 / 2026-04-11
- Created (UTC): 2026-04-12T2349Z
- SHA256: 4faaaaa5db911732914bbe6117a32f116e5d593a03d51f20a69a304f4866dedd
- Storage path: data/processed/binance_um_perp_BTCUSDT_mark_price_4h_2019-12-23_2026-04-11_2026-04-12T2349Z.parquet
- Known irreparable gaps: 0 bar(s), largest window 0 bar(s); see data/irreparable_gaps.json

## Dataset: BTCUSDT mark price klines full history (Binance USDT-M Perp) - Parquet (1d)
- Source: data.binance.vision monthly archives + historical daily overlay + Binance Futures REST repair
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Stream: markPriceKlines
- Timeframe: 1d
- Range (start/end): 2019-12-23 / 2026-04-11
- Created (UTC): 2026-04-12T2359Z
- SHA256: 9ffbdcbc55316f7c6c89ef7431b18aaa953bb4add0991c0af0338dfc406d0f77
- Storage path: data/processed/binance_um_perp_BTCUSDT_mark_price_1d_2019-12-23_2026-04-11_2026-04-12T2359Z.parquet
- Known irreparable gaps: 0 bar(s), largest window 0 bar(s); see data/irreparable_gaps.json

## Dataset: BTCUSDT index price klines full history (Binance USDT-M Perp) - Parquet (15m)
- Source: data.binance.vision monthly archives + historical daily overlay + Binance Futures REST repair
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Stream: indexPriceKlines
- Timeframe: 15m
- Range (start/end): 2019-12-23 / 2026-04-11
- Created (UTC): 2026-04-13T0010Z
- SHA256: 2cc256a77c62c61dbe6a7a73c9d076d25f8d972d9cf1474b27076ec2c72290c1
- Storage path: data/processed/binance_um_perp_BTCUSDT_index_price_15m_2019-12-23_2026-04-11_2026-04-13T0010Z.parquet
- Known irreparable gaps: 2 bar(s), largest window 1 bar(s); see data/irreparable_gaps.json

## Dataset: BTCUSDT index price klines full history (Binance USDT-M Perp) - Parquet (30m)
- Source: data.binance.vision monthly archives + historical daily overlay + Binance Futures REST repair
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Stream: indexPriceKlines
- Timeframe: 30m
- Range (start/end): 2019-12-23 / 2026-04-11
- Created (UTC): 2026-04-13T0021Z
- SHA256: 73c82d0dd3fa33e288e132f2d2936f947abc713b62d10231da7847970e2ee156
- Storage path: data/processed/binance_um_perp_BTCUSDT_index_price_30m_2019-12-23_2026-04-11_2026-04-13T0021Z.parquet
- Known irreparable gaps: 0 bar(s), largest window 0 bar(s); see data/irreparable_gaps.json

## Dataset: BTCUSDT index price klines full history (Binance USDT-M Perp) - Parquet (1h)
- Source: data.binance.vision monthly archives + historical daily overlay + Binance Futures REST repair
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Stream: indexPriceKlines
- Timeframe: 1h
- Range (start/end): 2019-12-23 / 2026-04-11
- Created (UTC): 2026-04-13T0032Z
- SHA256: 31f53f22855195bed051c65b303b28cab8d7e4a5b7abc67f761bd598224614bc
- Storage path: data/processed/binance_um_perp_BTCUSDT_index_price_1h_2019-12-23_2026-04-11_2026-04-13T0032Z.parquet
- Known irreparable gaps: 0 bar(s), largest window 0 bar(s); see data/irreparable_gaps.json

## Dataset: BTCUSDT index price klines full history (Binance USDT-M Perp) - Parquet (4h)
- Source: data.binance.vision monthly archives + historical daily overlay + Binance Futures REST repair
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Stream: indexPriceKlines
- Timeframe: 4h
- Range (start/end): 2019-12-23 / 2026-04-11
- Created (UTC): 2026-04-13T0043Z
- SHA256: 48136899fdb805d462b1f726419e66e011a379d1b7cf4fadbf9b50ab6e881e31
- Storage path: data/processed/binance_um_perp_BTCUSDT_index_price_4h_2019-12-23_2026-04-11_2026-04-13T0043Z.parquet
- Known irreparable gaps: 0 bar(s), largest window 0 bar(s); see data/irreparable_gaps.json

## Dataset: BTCUSDT index price klines full history (Binance USDT-M Perp) - Parquet (1d)
- Source: data.binance.vision monthly archives + historical daily overlay + Binance Futures REST repair
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Stream: indexPriceKlines
- Timeframe: 1d
- Range (start/end): 2019-12-23 / 2026-04-11
- Created (UTC): 2026-04-13T0054Z
- SHA256: 0f9333680e60293f78079ba1e2590c4808642d5eacacac801ce24b1522d9c2a0
- Storage path: data/processed/binance_um_perp_BTCUSDT_index_price_1d_2019-12-23_2026-04-11_2026-04-13T0054Z.parquet
- Known irreparable gaps: 0 bar(s), largest window 0 bar(s); see data/irreparable_gaps.json

## Dataset: BTCUSDT premium index klines full history (Binance USDT-M Perp) - Parquet (15m)
- Source: data.binance.vision monthly archives + historical daily overlay + Binance Futures REST repair
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Stream: premiumIndexKlines
- Timeframe: 15m
- Range (start/end): 2019-12-24 / 2026-04-11
- Created (UTC): 2026-04-13T0107Z
- SHA256: 61f1a714c3bfe8a868569b879ce34b307d8c4fc421b8ba112db767cfd5ec53b6
- Storage path: data/processed/binance_um_perp_BTCUSDT_premium_index_15m_2019-12-24_2026-04-11_2026-04-13T0107Z.parquet
- Known irreparable gaps: 8 bar(s), largest window 5 bar(s); see data/irreparable_gaps.json

## Dataset: BTCUSDT premium index klines full history (Binance USDT-M Perp) - Parquet (30m)
- Source: data.binance.vision monthly archives + historical daily overlay + Binance Futures REST repair
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Stream: premiumIndexKlines
- Timeframe: 30m
- Range (start/end): 2019-12-24 / 2026-04-11
- Created (UTC): 2026-04-13T0120Z
- SHA256: 06c937cd2ee47e93c998f34b2f59d446383bd7b85331e6b48bc68478723a5d8d
- Storage path: data/processed/binance_um_perp_BTCUSDT_premium_index_30m_2019-12-24_2026-04-11_2026-04-13T0120Z.parquet
- Known irreparable gaps: 3 bar(s), largest window 2 bar(s); see data/irreparable_gaps.json

## Dataset: BTCUSDT premium index klines full history (Binance USDT-M Perp) - Parquet (1h)
- Source: data.binance.vision monthly archives + historical daily overlay + Binance Futures REST repair
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Stream: premiumIndexKlines
- Timeframe: 1h
- Range (start/end): 2019-12-24 / 2026-04-11
- Created (UTC): 2026-04-13T0136Z
- SHA256: a0ba3d2fca7ed6638020579ce339705f7162849ce8fd8de70f4ff0f6a43532a9
- Storage path: data/processed/binance_um_perp_BTCUSDT_premium_index_1h_2019-12-24_2026-04-11_2026-04-13T0136Z.parquet
- Known irreparable gaps: 1 bar(s), largest window 1 bar(s); see data/irreparable_gaps.json

## Dataset: BTCUSDT premium index klines full history (Binance USDT-M Perp) - Parquet (4h)
- Source: data.binance.vision monthly archives + historical daily overlay + Binance Futures REST repair
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Stream: premiumIndexKlines
- Timeframe: 4h
- Range (start/end): 2019-12-24 / 2026-04-11
- Created (UTC): 2026-04-13T0154Z
- SHA256: af0194829805a080cf700b11d56c819fd673d0af4c39612b324aa61195ff6f07
- Storage path: data/processed/binance_um_perp_BTCUSDT_premium_index_4h_2019-12-24_2026-04-11_2026-04-13T0154Z.parquet
- Known irreparable gaps: 0 bar(s), largest window 0 bar(s); see data/irreparable_gaps.json

## Dataset: BTCUSDT premium index klines full history (Binance USDT-M Perp) - Parquet (1d)
- Source: data.binance.vision monthly archives + historical daily overlay + Binance Futures REST repair
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Stream: premiumIndexKlines
- Timeframe: 1d
- Range (start/end): 2019-12-24 / 2026-04-11
- Created (UTC): 2026-04-13T0226Z
- SHA256: 5cd7f1150ab34ed6b41dbe759165ea7750a0036a900809fefd4b389931079f4b
- Storage path: data/processed/binance_um_perp_BTCUSDT_premium_index_1d_2019-12-24_2026-04-11_2026-04-13T0226Z.parquet
- Known irreparable gaps: 0 bar(s), largest window 0 bar(s); see data/irreparable_gaps.json

## Dataset: BTCUSDT funding rates CCXT public-data pilot (Binance USDT-M Perp) - JSONL
- Source: CCXT `binanceusdm` public REST method `fapiPublicGetFundingRate`
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Data type: funding_rate
- Timeframe: 8h funding events
- Range (target): 2020-01-01T00:00:00Z / 2026-04-11T23:45:00Z
- Range (observed): 2020-01-01T00:00:00Z / 2026-04-11T16:00:00Z
- Created (UTC): 2026-06-18
- SHA256: sha256:58cab557e1a35d7832dc8d23424a5c3969706d516de9a9d3c2ed786b224c4666
- Storage path: scratch/EXT-CCXT-DATA-INGESTION-PILOT-01/funding_snapshot.normalized.jsonl
- Raw snapshot path: scratch/EXT-CCXT-DATA-INGESTION-PILOT-01/funding_snapshot.raw.jsonl
- Provenance path: scratch/EXT-CCXT-DATA-INGESTION-PILOT-01/provenance.json
- Validation path: scratch/EXT-CCXT-DATA-INGESTION-PILOT-01/validation_report.json
- Catalog lineage path: scratch/EXT-CCXT-DATA-INGESTION-PILOT-01/catalog_lineage.json
- Row count: 6879
- Validation summary: PASS; zero missing 8h events, zero duplicate timestamps, zero outside-window rows; exact exchange timestamps are preserved in `exchange_funding_time_*`, while nominal 8h event timestamps are stored in `funding_time_*`.
- Authority: NON-CANONICAL EXTERNAL PUBLIC-DATA PILOT OUTPUT; not a Result Population, Strategy Spec, Variant Manifest, Sweep Plan, backtest cost-model input, paper/live/runtime input, or canonical trading evidence.

## Dataset: BTCUSDT funding rates CCXT public-data adapter (Binance USDT-M Perp) - JSONL
- Source: CCXT `binanceusdm` public REST method `fapiPublicGetFundingRate`
- Symbol/Contract: BTCUSDT (USDT-M Perpetual)
- Data type: funding_rate
- Timeframe: 8h funding events
- Range (target): 2020-01-01T00:00:00Z / 2026-04-11T23:45:00Z
- Range (observed): 2020-01-01T00:00:00Z / 2026-04-11T16:00:00Z
- Created (UTC): 2026-06-19
- SHA256: sha256:58cab557e1a35d7832dc8d23424a5c3969706d516de9a9d3c2ed786b224c4666
- Storage path: scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/funding_snapshot.normalized.jsonl
- Raw snapshot path: scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/funding_snapshot.raw.jsonl
- Checksum path: scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/funding_snapshot.sha256
- Provenance path: scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/provenance.json
- Validation path: scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/validation_report.json
- Catalog lineage path: scratch/EXT-INTEG-CCXT-FUNDING-ADAPTER-01/catalog_lineage.json
- Row count: 6879
- Validation summary: PASS; zero missing 8h events, zero normalized duplicate timestamps, zero raw duplicate rows removed, zero outside-window rows, required fields present, exact exchange timestamps preserved in `exchange_funding_time_*`, and nominal 8h event timestamps stored in `funding_time_*`.
- Decision label: ADOPT_AS_PUBLIC_DATA_ADAPTER
- Authority: REPO-OWNED CCXT PUBLIC-DATA ADAPTER OUTPUT; not canonical data authority without separate promotion, not a Result Population, Strategy Spec, Variant Manifest, Sweep Plan, backtest cost-model input, paper/live/runtime input, or canonical trading evidence.
