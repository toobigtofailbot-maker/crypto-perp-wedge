# Intraday Data Assessment

## Purpose

Document the current repo-local readiness of 1h, 30m, and 15m data for upcoming Phase 2 hypothesis execution. This assessment uses existing catalogued data only and does not fetch, derive, or persist any new data.

## Summary

| Timeframe | OHLCV file present | Coverage | Continuity | Data-readiness implication |
|---|---|---|---|---|
| 1h | Yes | 2020-01-01 to 2026-04-11 | Continuous OHLCV | H-005 is executable from an OHLCV data perspective |
| 30m | Yes | 2020-01-01 to 2026-04-11 | Continuous OHLCV | H-006 is executable from an OHLCV data perspective |
| 15m | Yes | 2020-01-01 to 2026-04-11 | Continuous OHLCV | Future OHLCV-only 15m hypotheses are data-ready |

## OHLCV Availability

| Timeframe | Path | Rows | Start | End | Obvious blocker |
|---|---|---:|---|---|---|
| 1h | `data/processed/binance_um_perp_BTCUSDT_1h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet` | 55032 | 2020-01-01 00:59:59.999 UTC | 2026-04-11 23:59:59.999 UTC | None for H-005 OHLCV requirements |
| 30m | `data/processed/binance_um_perp_BTCUSDT_30m_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet` | 110064 | 2020-01-01 00:29:59.999 UTC | 2026-04-11 23:59:59.999 UTC | None for H-006 OHLCV requirements |
| 15m | `data/processed/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet` | 220128 | 2020-01-01 00:14:59.999 UTC | 2026-04-11 23:59:59.999 UTC | None for future OHLCV-only 15m hypotheses |

## Related Intraday Streams

Mark price, index price, and premium index parquet files also exist for 1h, 30m, and 15m. They are not required by H-005 or H-006 as currently pre-registered, but they are available for future hypotheses if explicitly registered.

| Stream | 1h status | 30m status | 15m status |
|---|---|---|---|
| Mark price klines | Present; no known irreparable gaps | Present; no known irreparable gaps | Present; 2 known irreparable bars |
| Index price klines | Present; no known irreparable gaps | Present; no known irreparable gaps | Present; 2 known irreparable bars |
| Premium index klines | Present; 1 known irreparable bar | Present; 3 known irreparable bars | Present; 8 known irreparable bars |

Known irreparable gaps are governed by `docs/irreparable_gaps_policy.md` and recorded in `data/irreparable_gaps.json`. Downstream research must skip or explicitly handle affected bars; silent interpolation is forbidden.

## H-005 / H-006 Implication

- H-005 requires 1h OHLCV only. Current repo-local data is sufficient for baseline execution.
- H-006 requires 30m OHLCV only. Current repo-local data is sufficient for baseline execution.
- Future 15m OHLCV-only hypotheses are data-ready. Future 15m hypotheses that require mark, index, or premium index streams must account for the documented D2-003A irreparable gaps.
