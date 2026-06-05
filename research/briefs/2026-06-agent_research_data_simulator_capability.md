# Agent Research Data / Simulator Capability Brief

## 1. Status / Authority

This brief is non-authoritative research input.

It does not authorize implementation. It does not rank strategies by expected profit. It does not commit to vendors. It does not create canonical evidence. It does not modify Strategy Spec, compiler, catalog, runner, backtester, schemas, validators, result populations, or runtime. It has no paper/live/runtime/protected-path effect.

## 2. Source Scope

This brief preserves findings from three Agent Mode research tracks:

1. Advanced crypto / Binance data-source map.
2. Mature open-source trading/research repo architecture review.
3. Simulator + advanced strategy capability synthesis.

These tracks are research inputs for future planning. They are not repo truth, implementation authority, strategy-selection authority, or vendor-selection authority.

## 3. Core Findings

- External sources should primarily provide raw data and exchange facts.
- The repo should compute indicators, features, signals, validation, result populations, and robustness internally.
- Binance-native data should be the first raw data source where suitable.
- FMP is supplementary only, not the primary source for Binance perp research.
- Paid external data should be considered only when a strategy class requires data the project cannot reconstruct well, especially historical L2/order-book data, liquidation history, and possibly CME BTC futures/calendar data.
- Mature open-source repos are useful for architecture patterns, not direct authority or shortcuts.
- Simulator capability should expand in layers; advanced strategies should not be forced into an insufficient candle-level simulator.

## 4. Build Internally Vs Source Externally

Preferred posture: build indicators/features/signals internally; source raw observations externally.

| Component | Build internally | Source externally | Notes |
|---|---:|---:|---|
| SMA / EMA / ATR / StdDev | Yes | No | Current closed catalog / compiler path owns reviewed computation internally. |
| VWAP / RVOL | Yes | No | Future catalog or composition expansion candidate; do not rely on vendor-computed values as authority. |
| z_score | Yes | No | Future composition review needed; avoid treating it as a promissory single indicator. |
| Donchian channels | Yes | No | Candidate for later indicator expansion using internal OHLCV computation. |
| OBI feature computation | Yes | No | Compute internally only after raw order-book data and simulator support exist. |
| liquidation-cluster features | Yes | No | Compute internally from sourced liquidation/event history if later acquired. |
| funding / OI derived features | Yes | No | Source raw funding/OI observations; derive features internally. |
| session labels | Yes | No | Internal calendar/session labeling should be deterministic and reviewed. |
| regime labels | Yes | No | Internal research labels only unless later governed by explicit schema/validator scope. |
| raw OHLCV candles | No | Yes | Binance-first where available and sufficient. |
| funding records | No | Yes | Binance-native funding records remain the first source for Binance perp research. |
| open interest | No | Yes | Source exchange-native raw observations where available; derive features internally. |
| trade data | No | Yes | Source raw trades if later strategy/simulator scope requires them. |
| L2/order book data | No | Yes | Likely requires later vendor investigation for historical depth. |
| liquidation event history | No | Yes | Likely requires later vendor/source investigation. |
| CME BTC futures/calendar data | No | Yes | Later cost/licensing review needed before use. |

## 5. Data-Source Posture

- Binance-first for exchange-native raw data where available and sufficient.
- FMP supplementary only.
- Historical L2/order book likely needs later vendor investigation.
- Liquidation history likely needs later vendor/source investigation.
- CME BTC futures/calendar data likely needs later cost/licensing review.
- No vendor commitment is made in this brief.

## 6. Mature Repo Lessons

Patterns worth preserving as research input:

- vectorbt: vectorized sweeps / indicator-factory concepts.
- Backtrader / QuantConnect LEAN: event and fill-model concepts.
- NautilusTrader: deterministic, fail-fast, high-assurance architecture.
- Hummingbot: connector and execution lessons later only.
- Freqtrade / Jesse: useful practical workflow / robustness ideas, but avoid shortcuts that bypass repo governance.

Guardrails:

- Do not copy flexible strategy-code shortcuts into canonical Strategy Specs.
- Do not use vendor-computed indicators as authority.
- Do not preserve winner-only optimization output.

## 7. Strategy Capability Sequencing

Readiness categories only; this is not profit ranking, recommendation, approval, or execution sequencing authority.

### Near-Term After Compiler / First Canonical Path

- Dynamic Volatility Mean Reversion.
- Donchian / trend breakout.
- Simple candle/statistical strategies.
- Simple funding/OI-aware candle strategies, if data and schema support are later added.

### Mid-Term After Data / Session / Indicator Expansion

- VWAP/RVOL reversal.
- Q-ORB / opening-range strategies.
- US/opening-bell expansion.
- Multi-timeframe/session strategies.
- More serious funding/OI strategies.

### Later After Advanced Simulator / Data Work

- Liquidation cluster hunting.
- Order book imbalance.
- Dynamic grid / execution-heavy strategies.
- CME gap / weekend momentum.
- Regime router.
- Multi-strategy portfolio allocator.

## 8. Simulator Layer Map

| Simulator layer | Supports | Required data | Status |
|---|---|---|---|
| candle / next-open signal simulator | Candle/statistical and first constrained Strategy Spec paths | OHLCV, funding where applicable | Current bounded research path exists; compiler path is build-and-test-only pending canonical use authorization. |
| multi-timeframe / session simulator | Session, opening-range, multi-timeframe filters | OHLCV across approved timeframes, deterministic session calendar | Future expansion. |
| derivatives-event simulator | Funding/OI/liquidation-aware strategies | Raw funding, open interest, liquidation/event history | Partial raw inputs exist for funding; broader derivatives event layer is future work. |
| order-book / microstructure simulator | OBI, queue-sensitive, depth-sensitive strategies | Historical L2/order book, trades, spread/depth assumptions | Future work; likely vendor investigation needed. |
| limit-order / execution simulator | Grid, maker/taker, partial-fill, execution-heavy strategies | Order book/trades, order constraints, latency/queue assumptions | Future work; no paper/live authority. |
| portfolio / risk allocator simulator | Regime router, multi-strategy allocator | Strategy result populations, correlation/exposure/risk assumptions | Later work after individual strategy evidence matures. |

Do not force order-book, grid, liquidation, or execution-heavy strategies into a candle-only simulator if that would create misleading evidence.

## 9. Roadmap Implications

Research-input roadmap, not implementation authorization:

1. Finish/checkpoint catalog + compiler binding.
2. Run first constrained canonical candle strategy.
3. Add robustness / item 6.
4. Expand indicator catalog: VWAP, RVOL, Donchian, RSI, z_score composition.
5. Add session + multi-timeframe support.
6. Add funding / OI / derivatives-event layer.
7. Investigate paid L2 / liquidation vendors.
8. Add order-book / microstructure simulator.
9. Add limit-order / grid simulator.
10. Later: regime router + portfolio allocator.

## 10. Known Limitations / Caution

Agent research may contain citation or source-quality weaknesses. Before turning findings into design locks or implementation WPs, verify primary sources and current repo truth. This brief should inform future decisions, not override repo truth or Main/Karl decisions.

## 11. Future Decision Questions

- Which advanced strategy family should drive first post-candle data expansion?
- Should first canonical sweep use the current constrained compiler or wait for compiler extensions?
- When should lookback parameter-binding, both direction, crosses_* operators, and z_score composition be reviewed?
- How much paid data cost is acceptable for historical L2/order-book or liquidation history?
- Should session/multi-timeframe work come before derivatives-event work?
- Should order-book/grid strategies remain deferred until paid historical L2 data is available?
