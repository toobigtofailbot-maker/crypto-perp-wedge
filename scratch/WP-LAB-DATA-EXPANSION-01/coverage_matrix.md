# WP-LAB-DATA-EXPANSION-01 Coverage Matrix

- REPO-OWNED PUBLIC PERP-DATA COVERAGE OUTPUT
- NOT CANONICAL DATA AUTHORITY WITHOUT SEPARATE PROMOTION
- NOT A RESULT POPULATION
- NOT STRATEGY / VM / SWEEP AUTHORITY
- NOT BACKTEST COST-MODEL AUTHORITY
- NOT PAPER / LIVE / RUNTIME AUTHORITY
- PUBLIC-ONLY SAMPLE PARSING; NO NETWORK CALLS IN DEFAULT MODE

| Source | Endpoint / method | History depth | Status | Known limit |
|---|---|---|---|---|
| ccxt_public_funding_adapter | `ccxt.binanceusdm.fapiPublicGetFundingRate -> /fapi/v1/fundingRate` | `backfillable` | `preserved` | Existing repo adapter validated target D4 window; endpoint returns startTime + limit when larger than limit |
| binance_usds_m_public_rest | `GET /fapi/v1/markPriceKlines` | `backfillable` | `preserved` | Repo catalog already records full history via data.binance.vision + REST repair |
| binance_usds_m_public_rest | `GET /fapi/v1/indexPriceKlines` | `backfillable` | `preserved` | Repo catalog already records full history via data.binance.vision + REST repair |
| binance_usds_m_public_rest | `GET /fapi/v1/premiumIndexKlines` | `backfillable` | `preserved` | Repo catalog already records full history via data.binance.vision + REST repair |
| binance_usds_m_public_rest | `GET /fapi/v1/premiumIndex` | `recent_only` | `adopted` | current snapshot only via REST |
| binance_usds_m_public_rest | `GET /fapi/v1/openInterest` | `recent_only` | `adopted` | current open interest only |
| binance_usds_m_public_rest | `GET /futures/data/openInterestHist` | `recent_only` | `adopted` | latest 1 month per Binance docs |
| binance_usds_m_public_rest | `GET /futures/data/topLongShortPositionRatio` | `recent_only` | `adopted` | latest 30 days per Binance docs |
| binance_usds_m_public_rest | `GET /futures/data/topLongShortAccountRatio` | `recent_only` | `adopted` | latest 30 days per Binance docs |
| binance_usds_m_public_rest | `GET /futures/data/globalLongShortAccountRatio` | `recent_only` | `adopted` | latest 30 days per Binance docs |
| binance_usds_m_public_rest | `GET /futures/data/takerlongshortRatio` | `recent_only` | `adopted` | latest 30 days per Binance docs |
| binance_usds_m_public_rest | `GET /fapi/v1/aggTrades` | `recent_only` | `adopted` | REST query futures trade histories not older than 24 hours per Binance docs |
| binance_usds_m_public_rest | `GET /fapi/v1/trades` | `recent_only` | `adopted` | recent market trades only |
| data.binance.vision_public_archive | `https://data.binance.vision/data/futures/um/{daily,monthly}/aggTrades/{symbol}/` | `backfillable` | `adopted` | public archive availability must be verified per requested file before canonical use |
| data.binance.vision_public_archive | `https://data.binance.vision/data/futures/um/{daily,monthly}/trades/{symbol}/` | `backfillable` | `adopted` | public archive availability must be verified per requested file before canonical use |
| binance_usds_m_public_rest | `GET /fapi/v1/exchangeInfo` | `recent_only` | `adopted` | current exchange rules only |

## Boundary

- Coverage and samples are public-only and non-authoritative.
- Existing funding, mark, index, and premium catalog surfaces are preserved.
- No network, dependency, runtime, runner, compiler, query, or canonical evidence path is changed.
