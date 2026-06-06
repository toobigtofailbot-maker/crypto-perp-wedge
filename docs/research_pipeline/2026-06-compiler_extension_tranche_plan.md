# Compiler-Extension Tranche Plan

## Status And Scope

WP-12ii / WP-S2c-213 is planning-only. It does not implement a schema change, validator change, indicator catalog change, compiler change, runner/backtester change, Strategy Spec instance change, variant manifest change, sweep plan change, result-population change, robustness artifact change, ranking, recommendation, readiness, transition, promotion, paper/live/runtime authority, or protected-path authority.

This plan orders future compiler-extension work by dependency, risk, and utility after the first canonical result-population path proved the pipeline with `RP-2134`.

## Current Compiler Surface

Repo-truth current surface:

| Surface | Current state |
|---|---|
| Supported directions | `long`, `short` compile to `+1.0` and `-1.0`; `both` is schema-valid but fails closed in the compiler. |
| Supported operators | `gt`, `gte`, `lt`, `lte`, `eq`, `neq`. |
| Unsupported closed operators | `crosses_above`, `crosses_below`, `in_set`, `is_true`, `is_false` are schema-valid but fail closed in the compiler. |
| Supported operands | `data_ref`, `indicator_ref`, `parameter_ref`, `constant`, `composed_operand`. |
| Supported composed form | `scale_by_one_minus_parameter` only. |
| Composed operand constraints | base operand `data_ref` or `indicator_ref`; parameter operand `parameter_ref`; no nested composition; numeric parameter value in `(0, 1)`. |
| Supported indicators / builtins | Catalog IDs `sma`, `ema`, `atr`, `stddev`; compiler-owned builtins `sma_v1`, `ema_v1`, `atr_v1`, `stddev_v1`. |
| Lookback posture | Indicator lookback must be a literal `operand.lookback.bars`; parameter-bound lookbacks fail closed. |
| Data refs | `open`, `high`, `low`, `close`, `volume` on the supplied primary OHLCV frame. |
| Timeframe posture | Non-empty operand `timeframe` values fail closed; no resampling or multi-timeframe handling exists. |
| Runner/backtester posture | The offline runner consumes compiled signals for the explicit canonical 15m path; `lib.backtest.run_backtest(...)` still consumes a precomputed signal and does not consume Strategy Spec JSON or stop metadata. |

Boundary facts:

- Catalog data is interface-only; computation remains compiler-owned.
- Strategy Specs remain declarative and non-executing.
- There is no expression language, formula parser, `eval`, `exec`, lambda, dynamic import, catalog-data-interpreted computation, or notes-as-computation path.
- `RP-2134` is fixture/input pipeline evidence only, not production-history strategy-quality evidence and not ranking, recommendation, readiness, promotion, paper/live, or runtime authority.

## Extension Inventory

| Extension | Purpose / family unlocked | Surfaces touched if implemented | Risk class | Dependency / validation | Closure posture |
|---|---|---|---|---|---|
| Lookback parameter binding | Sweep SMA/EMA/ATR/StdDev lookbacks; basic trend, mean-reversion, volatility families. | Strategy Spec schema, validator, compiler, compiler tests, variant/sweep artifacts only when explicitly scoped. Runner/backtester unchanged if still signal-only. | Medium. Misbinding could distort population accounting or indicator warmup. | Requires exact parameter binding rules, integer range enforcement, missing parameter failures, warmup/no-lookahead tests, determinism tests. | Can be closed/enumerated: `lookback.bars_parameter_ref` or equivalent fixed key, integer-only, bounded by declared parameter. |
| `both` direction | Long and short variants or symmetrical mean-reversion/trend logic inside one Strategy Spec. | Compiler semantics, compiler tests; possibly schema/validator if long/short condition namespaces are needed. Runner/backtester can consume `+1/-1/0` signals. | Medium-high because ambiguous single entry/exit groups can create flip behavior. | Needs design for whether one condition set applies symmetrically or separate long/short groups are required. Must test entry, exit, flip, flat, and no same-bar lookahead behavior. | Closed only if direction semantics are explicit and finite; avoid heuristic inversion. |
| `crosses_above` / `crosses_below` | Crossovers, breakouts, mean-reversion centerline triggers. | Compiler/operator implementation and tests; schema already enumerates operators; validator may need semantic checks. | Medium. Prior-bar state and null handling must be exact. | Needs prior/current operand evaluation, warmup on `t-1`, null-never-true, no lookahead, series/scalar combinations, deterministic tests. | Closed/enumerated as two operators; no open event language. |
| `z_score` composition | Bollinger-style distance, volatility-normalized mean reversion, standardized breakout filters. | Likely schema grammar, validator, compiler, tests. May depend on lookback binding and StdDev/SMA availability. | Medium-high because naive arithmetic can become an expression language. | Should follow a distinct closed form, for example `z_score_from_base_center_scale`, after operand composition rules are accepted. Test zero/near-zero denominator, nulls, no lookahead. | Can be closed if fixed arity: value operand, center operand, scale operand. Do not use formula strings. |
| ATR-stop consumption | Stop-loss or volatility stop families that need stop distance, not just entry/exit signal. | Runner/backtester consumption design, possibly `lib.backtest`, result-population assumption capture, tests, and later artifacts. | High and potentially protected-boundary-adjacent. | Current backtester consumes a position-intent signal only. Needs separate design before any implementation. | Blocked pending runner/backtester design; not a compiler-only extension. |
| `scale_by_one_plus_parameter` | Upper threshold / short-side symmetric distance forms such as `SMA * (1 + threshold)`. | Strategy Spec schema, validator, compiler, tests. | Low-medium if copied from existing minus form. | Requires same parameter `(0,1)` posture unless a later design widens it. Test null/no-lookahead/determinism. | Closed single form; safe near-term after current composition pattern. |
| `offset_by_parameter` forms | Absolute or unit-based offsets from a base series. | Strategy Spec schema, validator, compiler, tests; parameter unit discipline. | Medium. Unit ambiguity can create false semantics across price, ratio, and indicator units. | Needs explicit forms and units, likely `offset_plus_parameter` and `offset_minus_parameter`, with parameter role/unit checks. | Closed if plus/minus forms are separate enums and units are constrained. |
| RSI | Momentum and mean-reversion oscillator families. | Indicator catalog schema/instance/validator, compiler builtin, tests, Strategy Spec host-data refs when artifacts use it. | Medium. Formula convention and warmup must be locked. | Needs exact RSI convention, lookback handling, null/no-lookahead tests, catalog id/builtin pairing tests. | Closed catalog entry plus compiler-owned builtin. |
| VWAP | Volume-weighted price filters and intraday mean-reversion families. | Indicator catalog and compiler; possibly session/data semantics. | Medium-high. Session anchoring and cumulative vs rolling VWAP semantics are unclear. | Needs decision: rolling VWAP over lookback vs anchored session VWAP. Session VWAP depends on session/time handling. | Rolling VWAP can be closed; session VWAP should wait for session model. |
| RVOL | Volume anomaly and participation filters. | Indicator catalog and compiler; possibly lookback binding. | Medium. Baseline convention must be explicit. | Needs exact denominator, rolling average convention, null/zero-volume behavior. | Closed catalog entry if formula is fixed. |
| Donchian | Breakout/channel families. | Indicator catalog and compiler; may benefit from `crosses_*`. | Medium. Highest-high/lowest-low convention and current-bar inclusion must be locked. | Needs no-lookahead convention, likely prior-window high/low excluding current bar for breakout triggers unless deliberately included. | Closed catalog entry with explicit output fields. |
| Session/time filters | Calendar/session gates, time-of-day filters, weekend filters. | Schema grammar, validator, compiler, tests; maybe data/timezone conventions. | High for ambiguity, lower if limited to UTC-only filters. | Needs UTC-only closed filter design, no exchange-calendar inference, no local-time dependency, no runtime clock. | Defer or design separately as closed enumerated UTC filters. |
| Multi-timeframe handling | Higher-timeframe confirmation, MTF trend/regime filters. | Data/query layer, runner input contract, compiler alignment/resampling, tests, possibly artifact provenance. | High. Alignment, resampling, gap handling, and lookahead are critical. | Needs data-layer and runner-input design before compiler implementation. Must prove no future higher-timeframe bar leakage. | Blocked pending data/backtester/runner input design. |

## Dependency Ordering

Recommended dependency-ordered extension sequence:

| Step | Extension | Package shape |
|---|---|---|
| E1 | Lookback parameter binding | Design, then schema/validator implementation, then compiler/tests. Runner/backtester unchanged if still signal-only. Checkpoint before canonical artifact use. |
| E2 | `crosses_above` / `crosses_below` | Compiler/operator implementation and tests; schema may already allow the operators, but validator checks may be added if needed. Checkpoint before canonical use. |
| E3 | `scale_by_one_plus_parameter` | Add one closed composed form mirroring the current minus form. Schema/validator/compiler/tests. |
| E4 | `both` direction | Separate design first. Implementation only after Main accepts explicit long/short semantics. Compiler/tests likely first; schema may need distinct long/short condition structure if current groups are too ambiguous. |
| E5 | `z_score` closed composition | Design first, then grammar/validator/compiler/tests. Should wait until lookback binding and closed composition discipline are stable. |
| E6 | Additional closed indicators: RSI, RVOL, Donchian | Catalog design/update, catalog validator, compiler builtins, compiler tests. Donchian may be more useful after `crosses_*`; RVOL may pair with filters. |
| E7 | Offset forms | Design first because unit semantics matter. Then schema/validator/compiler/tests if accepted. |
| E8 | VWAP | Design first. Rolling VWAP may fit indicator block; anchored/session VWAP waits for session filters. |
| E9 | Session/time filters | Separate design block. Prefer UTC-only closed predicates if pursued. |
| E10 | Multi-timeframe handling | Data/runner/compiler alignment design block before implementation. |
| E11 | ATR-stop consumption | Runner/backtester consumption design block before implementation; not a compiler-only package. |

Each implementation block should separate:

- schema/grammar extension;
- validator extension;
- catalog/operator extension where applicable;
- compiler implementation;
- runner/backtester consumption only when explicitly required;
- result-population/query impact only when output semantics change;
- tests;
- canonical artifact impact only when separately scoped.

## Recommended Near-Term Tranche

Recommended first compiler-extension block after WP-S2c-213:

```text
Compiler Extension Block 1:
1. lookback parameter binding;
2. crosses_above / crosses_below;
3. scale_by_one_plus_parameter.
```

Reasoning:

- Lookback binding has the highest utility-to-risk ratio because it turns fixed-indicator specs into bounded populations without touching runner/backtester semantics.
- `crosses_*` unlocks basic crossover and breakout families while staying inside a closed operator set already present in schema grammar.
- `scale_by_one_plus_parameter` is the smallest symmetric extension to the existing `scale_by_one_minus_parameter` composition and helps upper-threshold / short-side designs.
- This block materially improves strategy usefulness without introducing arbitrary arithmetic, formulas, session handling, multi-timeframe alignment, or stop-order simulation.

Suggested package split:

1. E1 design or schema-shape note if Main wants design first.
2. E1 schema/validator plus tests.
3. E1 compiler plus tests.
4. E2 compiler/operator plus tests, with validator adjustment only if repo truth requires it.
5. E3 schema/validator/compiler plus tests.
6. Tranche checkpoint before any canonical artifact use.

If Main wants a smaller first package, start with lookback parameter binding alone.

## Mid-Term Candidates

Mid-term after Block 1:

- `both` direction after an explicit semantic design. Current groups are not enough to infer whether the same predicates should invert for shorts or whether separate long/short groups are required.
- `z_score` as a closed composition form after the team accepts exact fixed-arity representation and zero-scale handling.
- RSI, RVOL, and Donchian as closed catalog additions with compiler-owned builtins and no catalog-data computation.
- Offset forms only after unit semantics are explicit.

## Deferred / Blocked Surfaces

Deferred:

- VWAP until rolling-vs-anchored semantics are decided.
- Session/time filters until a UTC-only closed filter design exists.
- Open expression languages, arbitrary arithmetic, formula strings, ASTs, dynamic function dispatch, and user-defined formulas.

Blocked pending data/runner/backtester/runtime-adjacent design:

- Multi-timeframe handling, because input alignment, resampling, gap handling, and no-lookahead proof are not compiler-only.
- ATR-stop consumption, because current compiler/runner/backtester path emits and consumes position-intent signals, not stop-order or intrabar risk-stop instructions.
- Any paper/live/runtime semantics or protected-path integration.

## Boundary Rules For All Compiler Extensions

All future compiler-extension work should preserve these rules:

- closed enumerated forms only;
- no expression language;
- no `eval`, `exec`, lambda, callback, script, or dynamic import computation path;
- no arbitrary AST, formula parser, or operator-precedence parser;
- no dynamic dispatch from catalog text;
- catalog entries remain interface declarations; compiler owns reviewed computation;
- Strategy Specs remain non-executing and declarative;
- no runtime, paper/live, OMS, reconciliation, risk, safe-mode, kill-switch, broker, exchange, or order authority;
- fail closed on unsupported forms;
- schema, validator, and compiler tests are required for grammar/compiler packages;
- determinism, null handling, no-lookahead, and no-write behavior must be tested;
- no forward-fill, backfill, interpolation, future-value, or metadata falsification;
- no canonical artifact mutation unless a later package explicitly scopes it;
- result populations preserve committed denominators and non-authority posture.

## Validation Template For Future Extension WPs

Future extension implementation packages should normally run:

```text
schema validation for affected artifact family
validator tests proving unsupported/widened forms reject
compiler unit tests for supported and fail-closed cases
synthetic fixture tests with deterministic OHLCV/funding inputs
determinism tests for repeated compilation
no-lookahead tests that mutate future bars and compare past signals
null/warmup tests
no-write tests for compiler-only code
result-population validator if result artifacts are touched or consumed
query integrity views if query surfaces are touched
full pytest for implementation packages unless an explicit future repo rule changes this
git diff --check
diff scope summary
```

Future documentation-only packages should at minimum run the package-specific validators and integrity checks required by the active brief, plus diff checks and scope checks.

## Recommended Next Work Block After WP-S2c-213

Recommendation for Main/Side:

1. Accept or revise the E1-E11 extension ordering.
2. Authorize Compiler Extension Block 1 if the priority is richer strategy families from the existing OHLCV compiler path.
3. Choose a Data Block first instead if Main wants production-history canonical evidence before expanding expressiveness.
4. Choose an Engineering / E1 sandbox-wall block first only if Main wants stronger local isolation or harnessing before more compiler code.

This plan recommends Compiler Extension Block 1 as the next technical block, with lookback parameter binding first, because it improves bounded population design while staying inside the current offline research path and avoiding runtime/protected surfaces.

## Decision Request

Main/Karl decision requested:

```text
Accept or revise the extension ordering.
Authorize the first compiler-extension block, or choose Data/E1 priority first.
Confirm the hard boundaries: closed forms only, no expression language, no runtime/paper/live authority, no protected-path contact.
```
