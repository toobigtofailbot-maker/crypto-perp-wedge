# Online OHLCV Primitive Design

This document is a docs-only primitive design. It does not implement primitives, edit schemas, edit validators, edit compiler logic, edit runner logic, create Strategy Specs, create Variant Manifests, create Sweep Plans, write Result Populations, run probes, register candidates, authorize walk-forward/OOS, paper/live execution, runtime behavior, OMS/risk changes, broker/exchange connectivity, capital movement, or autonomous agent action.

## 1. Authority boundary

Fact:

- The three online OHLCV shapes remain preserved hypotheses only: ORB break-and-retest, no-wick trend pullback, and deterministic ORB-derived bias.
- Current Strategy Spec artifacts are closed, non-executing human-review surfaces.
- Current indicator catalog entries are compiler-owned builtins only: `sma`, `ema`, `atr`, and `stddev`.
- Current compiler support does not include session/opening-range state, retest state, candle-shape predicates, fixed-R target exits, opposite-opening-range stops, session-end exits, 30m canonical runner mode, 1h canonical runner mode, or non-null timeframe references.

Decision:

- Treat this design as the grammar and semantics target for later implementation packages only.
- Preserve closed-catalog and non-executability posture. Do not introduce formulas-as-code, eval, lambdas, user Python hooks, runner hooks, or arbitrary expression execution.
- Keep future implementation entirely in offline research surfaces unless separately authorized.

## 2. Source docs/code inspected

Source documents inspected:

- `docs/research_pipeline/2026-06-online_ohlcv_hypothesis_param_lock.md`
- `docs/research_pipeline/2026-06-online_ohlcv_primitive_feasibility.md`
- `docs/research_pipeline/2026-06-probe_methodology_canonical_regrounding.md`
- `docs/research_pipeline/2026-06-momentum_4h_probe_canonical_reconcile.md`
- `docs/architecture/future_strategy_capability_matrix.md`
- `docs/architecture/BTC_PERP_FUTURE_CAPABILITY_BACKLOG.md`
- `docs/research_pipeline/README.md`

Schemas, artifacts, code, and tests inspected:

- `research/schemas/strategy_spec.schema.json`
- `research/schemas/indicator_catalog.schema.json`
- `research/schemas/result_population.schema.json`
- `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json`
- `research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json`
- `research/strategy_specs/STRAT-SPEC-0006.strategy_spec.json`
- `tools/research_runner/spec_signal_compiler.py`
- `tools/research_runner/run_offline_sweep.py`
- `tests/test_spec_signal_compiler.py`
- `tests/test_offline_research_runner.py`
- `tests/test_validate_strategy_specs.py`
- `tests/test_validate_variant_sweep_artifacts.py`
- `tests/test_validate_indicator_catalogs.py`
- `tests/test_validate_result_populations.py`
- `tests/test_research_query.py`

## 3. Design objective

Design a closed Strategy Spec / compiler / runner surface that can later express the preserved online OHLCV hypotheses without custom strategy scripts or hidden denominator loss.

The target surface must support:

- deterministic UTC sessions and opening ranges;
- close-confirmed opening-range breakouts;
- bounded retest windows and tolerances;
- session-scoped entry guards;
- candle-shape predicates over OHLC fields;
- explicit conservative realism for stop, target, and session exits;
- full variant and no-trade-session denominator retention.

## 4. First-tranche decision

Decision:

- Split first implementation into two bounded packages rather than one combined package.
- Put session/ORB state into `WP-ONLINE-OHLCV-SESSION-ORB-IMPL-01`.
- Put candle-shape predicates into `WP-ONLINE-OHLCV-CANDLE-SHAPE-IMPL-01`.

First session/ORB tranche should include:

- `session_window`;
- `opening_range`;
- `opening_range_breakout`;
- `opening_range_retest`;
- `entry_controls.max_trades_per_session`;
- optional close-only `time_exit.session_end` if it can be implemented without intrabar ambiguity;
- close-only `stop_logic.opening_range_opposite_side` as a conservative research exit, not as stop-order realism.

First candle-shape tranche should include:

- `candle_shape.upper_wick_pct`;
- `candle_shape.lower_wick_pct`;
- `candle_shape.body_pct`;
- side-specific no-wick/impulse predicates;
- zero-range and missing-field fail-closed behavior.

Do not include in either first tranche:

- higher-timeframe deterministic trend-bias binding;
- intrabar stop/target ordering;
- fill/queue/order-book realism;
- fixed-R target implementation unless it is close-only and explicitly marked conservative;
- canonical evidence production.

Inference:

- Session/ORB state is medium complexity because it needs day/session state, opening-range memory, breakout memory, retest timeout, side-specific logic, session reset, and denominator/session counters.
- Candle-shape predicates are smaller and can be validated independently over synthetic OHLC arrays.
- Multi-timeframe binding is a separate design problem because current compiler operands reject non-null `timeframe` references and runner identity has only explicit 15m/4h canonical modes.

## 5. Deferred scope

Deferred to separate packages:

- deterministic multi-timeframe binding for 30m primary bars using completed 4h reference bars;
- 30m and 1h canonical runner/data identity packages if canonical result populations require committed data-slice lineage equivalent to current 15m/4h lineage;
- intrabar stop/target ordering and any path-dependent fill realism;
- fixed-R target semantics if target/stop interaction cannot be represented honestly with close-only bar-close exits;
- research-query extensions for session-count reporting if the result-population schema is extended;
- Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, candidates, probes, and walk-forward/OOS evidence.

## 6. Proposed closed grammar surface

The examples below are design sketches only. They are deterministic JSON-like shapes, not current valid schema.

### Session window

```json
{
  "session_window": {
    "session_id": "UTC_DAILY_0000",
    "timezone": "UTC",
    "anchor_time": "00:00",
    "duration": { "value": 1, "units": "day" },
    "bar_alignment": "bar_open_must_equal_session_anchor_or_member_grid",
    "partial_session_policy": "no_trade_count_in_denominator",
    "missing_bar_policy": "no_trade_count_in_denominator",
    "zero_length_session_policy": "invalid"
  }
}
```

Closed operators and units:

- `timezone`: `UTC` only for first tranche.
- `anchor_time`: `HH:MM` UTC.
- `duration.units`: `day` only for first tranche.
- Partial or missing sessions fail closed to no trade and still count in session denominator.

### Opening range

```json
{
  "opening_range": {
    "range_id": "OR-SESSION-FIRST-BAR",
    "session_ref": "UTC_DAILY_0000",
    "start_offset": { "value": 0, "units": "bars" },
    "length": { "value": 1, "units": "bars" },
    "high_source": "high",
    "low_source": "low",
    "close_after_range_required": true,
    "zero_range_policy": "no_trade_count_in_denominator",
    "incomplete_range_policy": "no_trade_count_in_denominator"
  }
}
```

Side-specific reference levels:

- Long breakout/retest uses `opening_range.high`.
- Short breakout/retest uses `opening_range.low`.
- Opposite-side stop uses `opening_range.low` for long and `opening_range.high` for short.

### Opening-range breakout

```json
{
  "opening_range_breakout": {
    "breakout_id": "ORB-CLOSE-CONFIRMED",
    "range_ref": "OR-SESSION-FIRST-BAR",
    "confirmation_price": "close",
    "confirmation_timing": "bar_close",
    "entry_timing": "next_bar_open",
    "long_operator": "close_gt_range_high_plus_tolerance",
    "short_operator": "close_lt_range_low_minus_tolerance",
    "tolerance": {
      "mode": "atr_multiple",
      "atr_lookback_bars": 14,
      "multiple": 0.1,
      "units": "ATR"
    },
    "breakout_before_range_complete_policy": "false",
    "simultaneous_long_short_policy": "no_trade"
  }
}
```

Closed tolerance modes for first session/ORB tranche:

- `atr_multiple`;
- optionally `percent_of_range`, if range zero is already fail-closed.

No arbitrary arithmetic strings are allowed.

### Opening-range retest

```json
{
  "opening_range_retest": {
    "retest_id": "ORB-RETEST",
    "breakout_ref": "ORB-CLOSE-CONFIRMED",
    "window": { "min_bars_after_breakout": 1, "max_bars_after_breakout": 4 },
    "touch_price_source": "close",
    "entry_timing": "next_bar_open_after_retest_confirmation",
    "long_retest_level": "opening_range.high",
    "short_retest_level": "opening_range.low",
    "tolerance": {
      "mode": "atr_multiple",
      "atr_lookback_bars": 14,
      "multiple": 0.1,
      "units": "ATR"
    },
    "timeout_policy": "no_trade_count_in_denominator",
    "opposite_breakout_before_retest_policy": "cancel_session_signal"
  }
}
```

Decision:

- First implementation should use `touch_price_source=close` to avoid intrabar touch ambiguity.
- High/low retest touch can be designed later only with explicit simulator-realism posture.

### Entry control

```json
{
  "entry_controls": {
    "min_bars_between_entries": 1,
    "max_trades_per_session": {
      "enabled": true,
      "count_basis": "entries_filled",
      "max_trades": 1,
      "session_ref": "UTC_DAILY_0000",
      "reset": "session_start"
    }
  }
}
```

Interaction with existing throttle:

- `min_bars_between_entries` remains a bar-count throttle across the compiled position stream.
- `max_trades_per_session` is an additional session-scoped guard.
- Both must allow a first valid entry without prior-entry state.

### Candle-shape predicates

```json
{
  "candle_shape": {
    "predicate_id": "NO-WICK-IMPULSE",
    "range_source": "high_low",
    "zero_range_policy": "false",
    "missing_ohlc_policy": "false",
    "upper_wick_pct": {
      "operator": "lte",
      "value": 0.10,
      "units": "fraction_of_range"
    },
    "lower_wick_pct": {
      "operator": "lte",
      "value": 0.10,
      "units": "fraction_of_range"
    },
    "body_pct": {
      "operator": "gte",
      "value": 0.60,
      "units": "fraction_of_range"
    },
    "side_mode": "side_specific"
  }
}
```

Definitions:

- `range = high - low`.
- `body = abs(close - open)`.
- `upper_wick = high - max(open, close)`.
- `lower_wick = min(open, close) - low`.
- `*_pct = component / range`.
- If `range <= 0`, any required predicate is false.
- If any required OHLC field is null or non-finite, predicate is false.

Side-specific interpretation:

- Long impulse may require bullish body (`close > open`) plus upper/lower wick bounds.
- Short impulse may require bearish body (`close < open`) plus upper/lower wick bounds.
- Doji (`close == open`) is false for side-specific impulse.

### Optional session-end exit

```json
{
  "time_exit": {
    "session_end": {
      "enabled": true,
      "session_ref": "UTC_DAILY_0000",
      "exit_signal_timing": "last_bar_close_before_session_end",
      "fill_timing": "next_bar_open",
      "partial_session_policy": "exit_at_last_available_bar_close_signal"
    }
  }
}
```

Decision:

- Include only if first implementation can make the last eligible bar causal and deterministic.
- If a position enters on the last bar of a session, same-bar entry/exit is forbidden; the session-end exit must wait for the next causal exit opportunity or block the late entry by rule.

### Optional fixed-R target

```json
{
  "risk_target": {
    "fixed_r": {
      "enabled": true,
      "r_multiple": 2.0,
      "entry_reference_price": "next_bar_open_pre_fee_slippage",
      "stop_ref": "stop_logic.opening_range_opposite_side",
      "evaluation_price": "close",
      "evaluation_timing": "bar_close",
      "same_bar_stop_target_policy": "defer_intrabar_realism"
    }
  }
}
```

Decision:

- Fixed-R target should be deferred unless implemented as close-only bar-close target evaluation with explicit limitation.
- Intrabar high/low target touch is not first-tranche primitive work.

### Optional opening-range opposite-side stop

```json
{
  "stop_logic": {
    "opening_range_opposite_side": {
      "enabled": true,
      "range_ref": "OR-SESSION-FIRST-BAR",
      "entry_reference_price": "next_bar_open_pre_fee_slippage",
      "evaluation_price": "close",
      "evaluation_timing": "bar_close",
      "long_stop_level": "opening_range.low",
      "short_stop_level": "opening_range.high",
      "same_bar_entry_stop_policy": "not_evaluated_until_after_entry_bar"
    }
  }
}
```

Decision:

- This is a conservative research exit, not stop-order or exchange-order semantics.
- Intrabar stop touch remains deferred to simulator realism.

## 7. Compiler semantics

Future compiler semantics must be causal:

- Opening range state is unavailable until all range bars have closed.
- Breakout is confirmed only at breakout bar close.
- Retest is confirmed only at retest bar close under first-tranche close-only semantics.
- Entry signal can be emitted only after confirmation and consumed by the existing next-bar-open backtest posture.
- The compiler must never use future bars to classify current session, breakout, retest, candle shape, stop, target, or exit state.

State reset:

- Session state resets at each UTC session start.
- Opening-range high/low, breakout state, retest state, trade count, and timeout state are session-local.
- Incomplete or partial sessions produce no trade and remain counted.

Long/short handling:

- Long and short ORB state must be side-specific.
- Both-direction mode must remain mutually exclusive and must not reverse on the same bar as an exit.
- Simultaneous long and short entry eligibility while flat must produce no trade unless a later closed tie-breaker is explicitly designed. First tranche should use no trade.

No-trade behavior:

- Bars outside a declared session cannot create opening-range, breakout, retest, or session-end signals.
- Bars before opening range completion cannot create breakout or retest signals.
- No-breakout sessions, breakout-without-retest sessions, zero-range sessions, and incomplete sessions must be no-trade sessions, not deleted sessions.

Interaction with existing position-state logic:

- Existing position state remains single-stream long/short/flat.
- Existing `min_bars_between_entries` remains a separate bar-count throttle.
- `max_trades_per_session` blocks additional entries after its session count is reached, even if `min_bars_between_entries` would allow an entry.
- Existing close-evaluated ATR-stop behavior remains unchanged unless a future package explicitly changes it.

Partial sessions:

- A session with missing opening-range bars is no-trade.
- A session with missing terminal bars cannot silently disappear; it must be retained in session denominator and flagged in future result/session coverage fields.
- Warmup-null ATR, SMA, EMA, or other required references make the dependent primitive false, not interpolated.

## 8. Runner/data/result implications

Future data requirements:

- 30m canonical evidence needs a 30m OHLCV identity surface with UTC spacing, row count, no duplicate timestamps, gap policy, source lineage, and checksum binding.
- 1h canonical evidence needs the same for 1h OHLCV.
- 4h higher-timeframe reference, if later used, must bind to completed 4h bars causally and record its own data-slice identity plus parent lineage.
- UTC session anchoring must be validated against the primary bar index. A session anchor that does not align to the primary timeframe must fail closed.

Runner implications:

- Current runner has explicit canonical modes for 15m and 4h, not generic 30m/1h canonical result-population production. A future 30m/1h package must either add explicit bounded modes or document another approved canonical path.
- Session strategies need runner output fields or result artifacts that distinguish variant denominator from session denominator.
- No-trade sessions must be retained and counted even when trade count is zero.

Future result-population/reporting implications:

- Preserve `committed_denominator_snapshot` and variant row equality to parent manifest/sweep counts.
- Add, if authorized, result/report fields for:
  - `session_count`;
  - `no_trade_session_count`;
  - `zero_range_session_count`;
  - `incomplete_session_count`;
  - `breakout_without_retest_session_count`;
  - `sessions_with_entries`;
  - session denominator basis and UTC anchor.
- Do not rank only sessions with trades.
- Do not drop variants with zero trades, invalid configuration, data-unavailable rows, or no qualifying sessions.

Canonical-equivalent probe binding:

- Any probe expected to set canonical expectations must match exact Strategy Spec, exact Variant Manifest, exact Sweep Plan, canonical runner path, exact data lineage, cost/funding/sizing assumptions, and full denominator.
- Any direct/custom route or altered population remains exploratory and non-gating.

## 9. Simulator realism posture

Conservative accepted posture:

- Close-confirmed breakout: allowed. The close of the breakout bar confirms the event; entry is next bar.
- Close-confirmed retest: allowed for first tranche. High/low touch retest is deferred unless simulator realism is explicitly designed.
- Session-end exit: allowed only if represented as a causal close-time exit signal and next-bar fill under current runner posture.
- Opposite-range-side stop: allowed only as close-evaluated research exit, not intrabar stop touch or exchange stop-order behavior.
- Fixed-R target: defer by default. If implemented early, use close-only bar-close evaluation and disclose that it is not intrabar target realism.

Same-bar ambiguity:

- Same-bar entry and exit is forbidden.
- Same-bar stop and target ordering cannot be inferred from OHLCV bars and must not be assumed.
- If a future primitive requires intrabar high/low ordering, stop and escalate to a simulator-realism package.

## 10. Validation plan for future implementation

Future schema/validator tests:

- new closed grammar validates only enumerated primitive types and operators;
- free-form formula, expression, code, eval, lambda, command, runtime, broker/exchange, paper/live, and authority-like keys remain rejected;
- units are explicit and closed: bars, ATR, R, fraction/percent of range, UTC time;
- required side labels are enforced for both-direction session/ORB predicates;
- `max_trades_per_session` validates integer bounds and session reference consistency;
- fixed-R and opposite-range stops validate conservative close-only timing if included.

Future compiler unit tests:

- opening range forms only after range completion;
- breakout confirmation has no lookahead;
- retest window starts after breakout and expires deterministically;
- session state resets on UTC boundary;
- one-trade-per-session blocks a second entry;
- existing `min_bars_between_entries` still works independently;
- current bar outside session cannot emit session primitives;
- incomplete and partial sessions are no-trade;
- zero-range sessions/predicates fail closed;
- candle-shape predicates compute upper wick, lower wick, and body ratios correctly for long, short, doji, zero-range, null, and non-finite cases;
- repeated runs are deterministic;
- no files are written during compilation.

Future runner/result tests:

- canonical 30m and 1h data identity checks, if added;
- session counts and no-trade-session counts remain retained;
- variant denominator equals manifest/sweep committed population;
- zero-trade and no-trade-session variants are preserved;
- no canonical result write occurs in dry-run modes;
- result-population validators cover any new session-denominator fields if schema changes are authorized;
- research-query views remain read-only if extended.

Forbidden-scope validation:

- diff-scope check must prove no paper/live/runtime/OMS/risk/reconciliation/broker/exchange/capital path contact.
- Implementation packages must not edit protected runtime boundaries unless separately authorized.

## 11. Strategy mapping

| Preserved hypothesis | First-tranche mapping | Classification |
|---|---|---|
| ORB break-and-retest | Requires session window, opening range, close-confirmed breakout, retest window/tolerance, one-trade-per-session, optional close-only opposite-range stop, optional session-end exit. | Feasible after session/ORB implementation. Fixed-R target should be close-only or deferred. |
| No-wick trend pullback | Requires candle-shape upper/lower wick and body predicates. Current EMA trend filter exists on same primary timeframe. Midpoint pullback and fixed-R/stop semantics need either a later closed pullback primitive or constrained close-only design. | Partly feasible after candle-shape implementation; pullback/stop/target may require a later package. |
| Deterministic ORB-derived bias variant | Requires session/ORB primitives plus 4h completed-bar trend-bias binding. Current compiler rejects non-null timeframe refs. | Feasible only after deferred multi-timeframe binding design/implementation. |

No mapping claims profitability, candidate approval, readiness, or promotion.

## 12. Recommended next implementation package

Recommendation: B. Split implementation into session/ORB and candle-shape packages.

Exact next packages:

```text
WP-ONLINE-OHLCV-SESSION-ORB-IMPL-01
WP-ONLINE-OHLCV-CANDLE-SHAPE-IMPL-01
```

Suggested sequencing:

1. Implement and validate session/ORB primitives first if Main wants the ORB break-and-retest path fastest.
2. Implement candle-shape predicates separately for no-wick trend pullback readiness.
3. Defer deterministic ORB-derived 4h bias until a multi-timeframe binding design package.

## 13. Forbidden scope reminder

This design does not authorize:

- compiler, schema, validator, runner, query, data, or library changes;
- Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, probes, backtests, walk-forward/OOS, or candidate registration;
- policy, ranking, readiness, promotion, paper/live execution, runtime behavior, OMS/risk, reconciliation, broker/exchange connectivity, credentials, capital movement, or autonomous agent action;
- weakening closed-catalog, non-execution, denominator-preservation, or canonical-equivalent methodology boundaries.
