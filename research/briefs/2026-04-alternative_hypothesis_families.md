# Alternative Hypothesis Families: Post Baseline Reset

**Date:** 2026-04-16
**Status:** ADVISORY / PRE-REGISTRATION INPUT
**Context:** WP-4a reset after H-001 through H-006 baseline NO-GO decisions

## Purpose

This brief evaluates candidate families that differ materially from the six failed baselines. It uses current repo data availability and D2-006/D2-014/D2-015 constraints as the filter for next-batch suitability.

## Data Availability Baseline

Current repo truth supports the following relevant data streams:

- OHLCV full history exists for 15m, 30m, 1h, 4h, and 1d from 2020-01-01 through 2026-04-11.
- Funding full history exists as 8h funding events from 2019-09-10 through 2026-04-12.
- Mark price, index price, and premium index kline histories exist for 15m, 30m, 1h, 4h, and 1d.
- Known irreparable gaps are governed by `docs/irreparable_gaps_policy.md` and `data/irreparable_gaps.json`.
- 4h mark, index, and premium streams have no known irreparable gaps. 1h premium has one known irreparable bar. 30m premium has three known irreparable bars. 15m mark, index, and premium have small documented gaps.

## Candidate Family 1: Funding + Momentum Composite

**Concept:** Combine funding or carry favorability with price momentum confirmation. A trade is allowed only when funding conditions are favorable and price action confirms the same direction.

**Why it differs from the failed set:** H-001 let funding direction drive the position by itself. This family requires an independent price-confirmation condition, so funding is a context filter rather than the only signal.

**Economic rationale:** Perp funding can reflect positioning imbalance, but a crowded trade can remain crowded for long periods. Requiring price confirmation seeks to avoid fading strong trends too early and focuses on cases where carry and directional pressure align.

**Rough signal logic sketch:** On 4h bars, compute rolling funding. Longs require negative or improving funding plus positive 4h momentum. Shorts require positive or deteriorating funding plus negative 4h momentum. Otherwise stay flat.

**Data requirements:** 4h OHLCV and 8h funding rates. Both are repo-ready, with no D2-003A skipped bars recorded for the prior 4h OHLCV/funding baselines.

**Likely timeframe(s):** 4h primary, because funding settles every 8h and H-001 already used 4h as the funding-aligned baseline.

**Key risks:** It may still inherit H-001 funding fragility or H-002 trend drawdown if the confirmation is too loose. It can also undertrade if funding and momentum rarely align.

**Next-batch suitability:** Suitable for H-007. It is data-ready, implementable without code changes, and materially different from naive funding-directional logic.

## Candidate Family 2: Volatility-Scaled Trend / Risk Overlay

**Concept:** Keep a trend signal but scale exposure down in high realized-volatility regimes or target a steadier volatility contribution.

**Why it differs from the failed set:** This is not a new alpha family. It tests whether risk structure can improve the durability of an existing directional signal by reducing exposure when volatility is elevated.

**Economic rationale:** H-002, H-004, H-005, and H-006 all suffered severe drawdowns. Volatility-aware exposure could reduce drawdown and concentration if gross signal quality is otherwise adequate.

**Rough signal logic sketch:** Generate a trend signal, compute rolling realized volatility, and scale exposure inversely to volatility or block entries above a volatility threshold.

**Data requirements:** OHLCV only for realized volatility. The OHLCV streams are repo-ready across locked timeframes.

**Likely timeframe(s):** 1h, 4h, or 1d depending on the base signal. It is weaker as a standalone candidate because the economic edge comes from the underlying trend signal, not the scaling itself.

**Key risks:** Current `lib/backtest.py` casts signal values to `int`, so true fractional volatility-scaled exposure is not executable without code changes. A binary volatility filter is implementable, but that would be closer to another regime-filtered trend test and less materially different from H-004.

**Next-batch suitability:** Not suitable for H-008 in this docs-only package. It should remain a documented candidate family for a later package that explicitly authorizes backtester support for fractional exposure or pre-registers a narrower binary risk-filter variant.

## Candidate Family 3: Premium-Confirmed Momentum Continuation

**Concept:** Require price momentum to be confirmed by premium-index pressure. The premium stream acts as a derivative-market participation filter.

**Why it differs from the failed set:** H-005 used MACD and price structure, both derived from OHLCV. H-006 used price-band compression and breakout. This family adds an independent perp-market stream, so confirmation is not another price-only indicator.

**Economic rationale:** Persistent premium can indicate sustained demand for perp exposure. A momentum signal confirmed by premium pressure may be more selective than price-only intraday momentum.

**Rough signal logic sketch:** On 1h bars, compute a price momentum condition and a premium-index z-score. Longs require positive momentum and positive premium pressure. Shorts require negative momentum and negative premium pressure. Exit when either momentum or premium confirmation decays.

**Data requirements:** 1h OHLCV and 1h premium index klines. Both are repo-ready. The 1h premium stream has one known irreparable bar that must be skipped or explicitly handled under D2-003A.

**Likely timeframe(s):** 1h primary. Faster 30m or 15m variants would be more exposed to cost drag and premium-stream gaps; the 1h layer is the cleaner first test.

**Key risks:** Premium confirmation may still be procyclical and enter late. It may also increase regime concentration if premium extremes cluster in a few historical windows.

**Next-batch suitability:** Suitable as the H-008 replacement for the volatility-scaling concept. It is materially different, data-ready, and executable without code changes.

## Candidate Family 4: Multi-Timeframe Trend Alignment

**Concept:** Trade a primary intraday trigger only when coarser timeframes agree with the same directional state.

**Why it differs from the failed set:** H-002 was single-timeframe 4h breakout. H-005 was single-timeframe 1h MACD/structure. H-006 was single-timeframe 30m squeeze breakout. This family makes higher-timeframe agreement the core condition.

**Economic rationale:** Intraday signals are noisy. Requiring 1h and 4h agreement before taking 30m signals may reduce chop, lower false breakouts, and improve trade quality.

**Rough signal logic sketch:** Generate entries on 30m only when the 30m trigger aligns with 1h and 4h trend states. Longs require all three to be bullish; shorts require all three to be bearish; otherwise stay flat.

**Data requirements:** 30m OHLCV plus 1h and 4h OHLCV. All are repo-ready and continuous per the intraday assessment and data catalog.

**Likely timeframe(s):** 30m primary with 1h and 4h confirmation. This follows D2-015 because confirmation timeframes are coarser than the primary timeframe.

**Key risks:** Alignment may reduce trade count too much or enter after most of the move has already occurred. If the 30m trigger is too sensitive, cost drag can still dominate.

**Next-batch suitability:** Suitable for H-009. It directly addresses intraday noise while preserving the current backtester and data surface.

## Candidate Family 5: Basis / Premium Mean Reversion

**Concept:** Fade extreme deviations between mark price and index price, optionally confirmed by premium-index extremes, expecting the perp dislocation to mean-revert.

**Why it differs from the failed set:** H-003 tested price-band mean reversion around daily close deviations. This family tests structural perp dislocation around mark-index basis or premium, not price oversold/overbought bands.

**Economic rationale:** Perpetual markets include structural mechanisms that connect mark price, index price, premium, and funding. Extreme basis or premium can reflect temporary positioning pressure that may revert as arbitrage and funding mechanics normalize the dislocation.

**Rough signal logic sketch:** On 4h bars, compute basis as `(mark_close - index_close) / index_close` or use premium-index close. Short when basis/premium is extremely positive and starts reverting; long when it is extremely negative and starts reverting; exit near neutral or after a max hold.

**Data requirements:** 4h mark price klines, 4h index price klines, and optionally 4h premium index klines. All are repo-ready with zero known irreparable gaps in the manifest.

**Likely timeframe(s):** 4h primary. This reopens 4h only with materially different economic rationale after H-001/H-002 Cold Storage.

**Key risks:** Basis extremes may persist in strong directional markets. The signal could be sparse, regime-concentrated, or too correlated with funding-directional behavior if not framed carefully.

**Next-batch suitability:** Suitable for H-010. It is data-ready and directly uses the mark/index/premium data family that previous baseline hypotheses did not test.

## Recommended Next Batch

| Hypothesis | Family | Primary timeframe | Required streams | Suitability |
|---|---|---:|---|---|
| H-007 | Funding + Momentum Composite | 4h | OHLCV, funding | Ready |
| H-008 | Premium-Confirmed Momentum Continuation | 1h | OHLCV, premium index | Ready; replaces volatility scaling |
| H-009 | Multi-Timeframe Trend Alignment | 30m | 30m/1h/4h OHLCV | Ready |
| H-010 | Basis / Premium Mean Reversion | 4h | mark, index, premium | Ready |

The next execution package should test these as newly pre-registered baselines, not as parameter tuning of H-001 through H-006.
