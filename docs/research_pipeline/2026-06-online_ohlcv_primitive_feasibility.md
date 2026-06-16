# Online OHLCV Primitive Feasibility

Package label: `WP-ONLINE-OHLCV-PRIMITIVE-FEASIBILITY-01`

## 1. Authority boundary

This document is a feasibility assessment only. It does not implement primitives, create Strategy Specs, create Variant Manifests, create Sweep Plans, write Result Populations, run probes, register candidates, authorize walk-forward/OOS, paper/live execution, runtime behavior, OMS/risk changes, broker/exchange connectivity, capital movement, or autonomous agent action.

This assessment has no signal-definition authority, ranking authority, readiness authority, policy authority, promotion authority, or runtime authority. Future implementation, if any, requires a separately scoped package with explicit changed-file boundaries and validation.

## 2. Source docs/code inspected

Source documents inspected:

- `docs/research_pipeline/2026-06-online_ohlcv_hypothesis_param_lock.md`
- `docs/research_pipeline/2026-06-probe_methodology_canonical_regrounding.md`
- `docs/research_pipeline/2026-06-momentum_4h_probe_canonical_reconcile.md`
- `docs/architecture/future_strategy_capability_matrix.md`
- `docs/architecture/BTC_PERP_FUTURE_CAPABILITY_BACKLOG.md`
- `docs/data/intraday_data_assessment.md`
- `docs/data/2026-06-binance_usdtm_15m_catalog_and_slice_identity.md`
- `docs/data/2026-06-binance_usdtm_4h_resampled_catalog_and_slice_identity.md`
- `docs/data_catalog.md`

Schemas, catalogs, artifacts, code, and tests inspected:

- `research/schemas/strategy_spec.schema.json`
- `research/schemas/indicator_catalog.schema.json`
- `research/schemas/result_population.schema.json`
- `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json`
- `research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json`
- `research/strategy_specs/STRAT-SPEC-0006.strategy_spec.json`
- `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json`
- `research/data_slices/binance_usdtm_btcusdt_4h/binance_usdtm_btcusdt_4h_20200101_20260411.catalog_slice.json`
- `tools/research_runner/spec_signal_compiler.py`
- `tools/research_runner/run_offline_sweep.py`
- `tools/registry/validate_strategy_specs.py`
- `tools/registry/validate_variant_sweep_artifacts.py`
- `tools/registry/validate_indicator_catalogs.py`
- `tools/registry/validate_result_populations.py`
- `tests/test_spec_signal_compiler.py`
- `tests/test_offline_research_runner.py`
- `tests/test_validate_strategy_specs.py`
- `tests/test_validate_variant_sweep_artifacts.py`
- `tests/test_validate_indicator_catalogs.py`
- `tests/test_validate_result_populations.py`
- `tests/test_research_query.py`

Repo-truth facts:

- The current Strategy Spec grammar is closed and non-executable.
- The active indicator catalog exposes only `sma`, `ema`, `atr`, and `stddev` as compiler-owned builtins.
- `spec_signal_compiler.py` supports deterministic bar-close condition evaluation, side-specific entry/exit groups, shared filters, simple comparison and crossover operators, z-score and one-plus/one-minus parameter compositions, fixed `entry_controls.min_bars_between_entries`, `exit_logic.max_holding_period`, and fixed literal `exit_logic.atr_stop`.
- `spec_signal_compiler.py` does not support non-null `data_ref.timeframe` or `indicator_ref.timeframe`; cross-timeframe references fail closed as unsupported.
- Current canonical runner modes are explicit for 15m and 4h, not generic 30m or 1h canonical result-population production.
- Result-population validation enforces complete committed-denominator retention, row-count equality, and successful-only / winner-only denominator rejection.

## 3. Preserved hypotheses reviewed

Reviewed preserved hypotheses from `2026-06-online_ohlcv_hypothesis_param_lock.md`:

1. ORB break-and-retest on 30m bars with UTC 00:00 opening range, close-confirmed breakout, retest window, ATR tolerance, opposite-range-side stop, fixed R target, session-end exit, and one trade per session.
2. No-wick trend pullback on 1h bars with close-vs-EMA50 trend filter, wick/body predicates, midpoint pullback, next-open entry, signal-candle or ATR stop, fixed R target, and one active position.
3. Deterministic ORB-derived bias variant on 30m bars with 30m opening range, 4h close-vs-SMA50 bias, close-confirmed breakout, opposite-range-side stop, fixed R target, session-end exit, and one trade per session.

Decision:

- Treat all three as preserved hypotheses only.
- Do not treat any of them as candidates, frozen specs, or profitability claims.
- A shared primitive route is feasible as a later design package, but not testable now without adding closed primitives.

## 4. Primitive feasibility table

| Primitive candidate | Current repo support | Classification | Feasibility note |
|---|---|---|---|
| Deterministic session/opening-range primitive | No closed session primitive exists. The schema has `session` as a group role label, but the compiler does not implement calendar/session anchoring or opening-range state. | Medium addition | Feasible as a bounded closed primitive if designed as deterministic UTC bar-session state, with no free-form calendar code and no runner/runtime contact. It likely needs schema/catalog/compiler/test work later. |
| Close-confirmed breakout primitive | Simple `close > operand` comparisons exist, but rolling/session range high/low and ATR-offset breakout levels are not currently expressible as a stateful opening-range reference. | Medium addition | Feasible if built on the session/opening-range primitive plus a closed breakout condition. Close-confirmed evaluation aligns with current bar-close compiler posture. |
| Retest-window and retest-tolerance primitive | No current state machine records breakout, waits N bars, and tests tolerance around a prior range boundary. | Medium addition | Feasible, but it is the highest-complexity shared primitive because it needs bounded state, explicit timeout semantics, side rules, denominator treatment for no-retest sessions, and ambiguity handling. |
| One-trade-per-session guard | Current `min_bars_between_entries` gives fixed bar throttling only, not session reset logic. | Small bounded addition | Feasible if tied to the same deterministic session primitive. It should be a closed entry-control extension, not arbitrary runner hooks. |
| Candle-shape/wick predicate | Current compiler can compare raw OHLCV fields and simple indicators, but cannot compute upper/lower wick share or body/range ratio as a named predicate. | Small bounded addition | Feasible as closed candle-shape predicates over current bar OHLC fields, with zero-range policy and no arbitrary formulas. |
| Body-ratio predicate | Same as wick predicate: raw fields exist, but closed ratio predicate does not. | Small bounded addition | Feasible as a closed predicate family alongside wick predicates. Needs explicit zero-range and equality-bound semantics. |
| Higher-timeframe deterministic trend-bias reference | SMA exists, and 4h data lineage exists, but compiler operands reject non-null timeframe refs and runner modes do not currently bind 30m primary bars to 4h confirmation series. | Medium addition | Feasible as a later bounded multi-timeframe binding design. It must define causal alignment, no-lookahead use of completed 4h bars, parent lineage, and result identity. |

Overall primitive feasibility:

- One bounded shared primitive package is feasible in design terms.
- It should be a design package first, not an implementation package, because session state, retest state, R-target semantics, and cross-timeframe binding need exact closed grammar before code changes.
- None of these primitives requires touching paper/live/runtime/OMS/risk/broker/exchange paths.

## 5. Strategy feasibility table

| Hypothesis | Classification | Reason |
|---|---|---|
| ORB break-and-retest | Near-term after bounded primitive package | Data is available for 30m OHLCV, and close-confirmed breakout plus next-bar entry can fit current bar-close posture. It needs new closed session/opening-range, breakout, retest, one-trade-per-session, opposite-range-side stop, fixed R target, and session-exit semantics before a Strategy Spec can honestly express it. |
| No-wick trend pullback | Near-term after bounded primitive package | Data is available for 1h OHLCV and EMA exists. It needs closed candle-shape/body-ratio predicates and deterministic pullback-to-midpoint semantics. If stop and target are fixed R/path-dependent, a simulator-realism design may also be needed before canonical evidence. |
| Deterministic ORB-derived bias variant | Requires larger compiler upgrade | It shares the ORB/session/breakout/one-trade primitives, but also requires higher-timeframe 4h trend-bias binding while the current compiler rejects cross-timeframe refs. It remains feasible, but should wait until multi-timeframe binding is explicitly designed. |

Strategy-surface decision:

- Do not proceed directly to Strategy Specs.
- Do not run probes or backtests from ad hoc custom logic.
- Use the next package to design the closed primitive surface and decide whether the multi-timeframe bias belongs in the first implementation tranche or a later tranche.

## 6. Data feasibility

Current data assets support the basic OHLCV needs:

- 30m bars: Supported by `docs/data/intraday_data_assessment.md` and `docs/data_catalog.md`; cataloged full-history OHLCV exists from 2020-01-01 through 2026-04-11 with 110,064 rows and continuous OHLCV for the earlier H-006 data perspective.
- 1h bars: Supported by `docs/data/intraday_data_assessment.md` and `docs/data_catalog.md`; cataloged full-history OHLCV exists from 2020-01-01 through 2026-04-11 with 55,032 rows and continuous OHLCV for the earlier H-005 data perspective.
- 4h trend reference: Supported as a derived, validated, UTC-boundary 4h slice from parent 15m D4A lineage, with 13,758 rows, no gaps, no duplicates, and slice identity `binance_usdtm_btcusdt_ohlcv_4h:sha256:4379d2f0fad5e79bfd5576b308d01fb6134b0f5acf04013e73e00ce33ca96b30`.
- UTC session anchoring: The committed 15m and 4h data-slice docs use UTC timestamps and UTC-boundary validation. A future 30m/1h session primitive should still explicitly validate bar spacing, daily UTC anchors, no partial sessions, and exchange calendar assumptions.
- Preserving no-trade days: Data availability is not the blocker. Future result artifacts must retain no-trade days/sessions in the tested denominator and report zero-trade outcomes honestly.
- Parent lineage from existing 15m/4h slices: Strong for the 15m parent and derived 4h. A future 30m/1h canonical package should decide whether to consume existing cataloged native 30m/1h parquet, derive 30m/1h from D4A 15m, or create committed slice metadata similar to D4H before canonical result production.

Data feasibility decision:

- No new data acquisition is needed for the three preserved OHLCV hypotheses at feasibility level.
- A future canonical evidence package should not rely only on legacy `docs/data_catalog.md` rows for 30m/1h if result-population identity needs committed data-slice lineage equivalent to current 15m/4h lineage.

## 7. Simulator realism feasibility

Current semantics that can be safely represented:

- Close-confirmed breakout: Feasible if entry signals are generated only after the bar close. This matches current compiler condition timing.
- Next-bar entries: Feasible under current backtest/runner posture, which records next-bar-open pre-fee/slippage entry reference for ATR-stop and uses bar-based signals.
- One active position: Current signal compilation is position-stateful and avoids simultaneous long/short exposure in `direction=both`.
- Max holding period / time exit in bars: Current `exit_logic.max_holding_period` supports a fixed bar count, but it is not the same as a session-end exit unless session boundaries are encoded.

Current semantics requiring closed additions:

- Retest windows: Require a bounded state machine after breakout. This is not supported by current declarative conditions.
- Opposite-range-side stops: Require opening-range boundary memory and side-specific stop level binding. Current ATR stop is a fixed ATR-distance close-evaluated stop only.
- Fixed R targets: Require target-distance binding to stop distance and an exit condition. Current schema has `risk_model.target_distance` as recording text/value but no compiler target implementation.
- Session-end exits: Require session boundary awareness, not just a fixed max-holding bar count, unless the first-test design reduces session-end exits to an explicitly precomputed bar count with no partial-session ambiguity.

Realism constraints:

- Current ATR stop is evaluated on close at bar close, not intrabar high/low stop touch.
- Fixed R targets and opposite-range-side stops can suffer same-bar stop/target ambiguity if both are reachable inside one OHLCV bar.
- Same-bar entry/exit assumptions remain forbidden by the parameter-lock doc.

Simulator realism decision:

- Close-confirmed entry logic can stay bar-close conservative.
- Any future implementation of stops/targets should either use close-only conservative semantics and disclose the limitation, or defer target/stop realism to a simulator package before canonical evidence.
- If a future design needs intrabar stop/target ordering, that is a simulator upgrade, not a primitive-only package.

## 8. Denominator/methodology requirements

Future probes/screens must comply with:

- Complete denominator preservation from Variant Manifest through Sweep Plan through Result Population.
- No deletion of no-trade days, no-trade sessions, failed variants, errored variants, invalid variants, filtered variants, or data-unavailable variants.
- No winner-only reporting and no post-hoc cleanup of weak or no-trade rows.
- Exact canonical-equivalent probe requirements from `2026-06-probe_methodology_canonical_regrounding.md` before a probe can set canonical expectations.
- Explicit `premise-only exploratory probe` or `scratch feasibility check` labeling when any direct/custom route, altered population, altered data, altered runner path, or altered cost/funding/sizing assumption is used.

Future report-back for these hypotheses must explicitly state:

```text
Probe class:
Canonical-equivalent: YES/NO
Exact spec/grid/sweep match: YES/NO
Canonical runner path: YES/NO
Exact data lineage: YES/NO
Cost/funding/sizing match: YES/NO
Full denominator retained: YES/NO
Can gate canonical expectations: YES/NO
Reason:
```

Methodology decision:

- The fastest safe path is not an ad hoc probe. The fastest safe path is a closed primitive design, then bounded implementation, then canonical-equivalent evidence only after Strategy Spec / VM / Sweep artifacts exist.

## 9. Recommended next package shape

Recommendation: A. Proceed with one bounded shared primitive design package.

Exact next package:

```text
WP-ONLINE-OHLCV-PRIMITIVE-DESIGN-01
```

Recommended scope for the next package:

- Docs-only design, not implementation.
- Define closed Strategy Spec grammar additions for:
  - UTC session/opening-range primitive;
  - close-confirmed breakout over opening-range boundaries;
  - retest-window and retest-tolerance state;
  - one-trade-per-session entry control;
  - candle wick/body predicates;
  - fixed R target and opposite-range-side stop semantics, or an explicit deferral if simulator realism is not sufficient.
- Define whether higher-timeframe 4h bias is in the first primitive tranche or deferred to a separate multi-timeframe binding design.
- Define validation expectations for schema, compiler, runner, result-population identity, denominator retention, and no runtime contact.

Suggested split if Main wants narrower packages later:

- `WP-ONLINE-OHLCV-SESSION-ORB-DESIGN-01` for session/opening-range/breakout/retest/session guard.
- `WP-ONLINE-OHLCV-CANDLE-SHAPE-DESIGN-01` for wick/body/pullback predicates.
- A later multi-timeframe binding design for deterministic 4h bias if not included in the shared package.

Decision:

- A single design package is feasible because all three hypotheses share OHLCV-only closed primitives and denominator/methodology guardrails.
- The implementation package should not be bundled with the design package.

## 10. Forbidden scope reminder

Forbidden in this package and still forbidden for the next design package unless explicitly authorized:

- Implementing compiler primitives.
- Implementing indicators.
- Editing runner logic.
- Creating Strategy Specs.
- Creating Variant Manifests.
- Creating Sweep Plans.
- Creating Result Populations.
- Running backtests or probes.
- Creating candidates.
- Creating walk-forward/OOS evidence.
- Touching paper/live/runtime/OMS/risk/broker/exchange/capital paths.
- Weakening closed-catalog/non-executability boundaries.
- Introducing eval, lambda, arbitrary Python strategy logic, formulas-as-code, runner hooks, or custom strategy scripts as canonical evidence.

Boundary summary:

- Implementation: NO.
- Strategy Spec / Variant Manifest / Sweep Plan / Result Population: NO.
- Compiler / runner / schema / query / data mutation: NO.
- Candidate / walk-forward / paper / live / runtime / capital authority: NO.
- Protected paths touched: NO.
