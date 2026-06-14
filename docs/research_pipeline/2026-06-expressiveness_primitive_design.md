# Expressiveness Primitive Design

## Status / authority boundary

`WP-EXPRESS-DESIGN-01` is docs-only design. It does not implement primitives,
change schema, change validators, change compiler behavior, change runner or
backtester behavior, add catalog entries, author Strategy Specs, author variant
manifests, author sweep plans, write result populations, register candidates,
rank variants or strategies, mark readiness, promote a strategy, authorize data
acquisition, authorize paper/live execution, alter runtime behavior, change
OMS/risk/reconciliation behavior, touch broker/exchange connectivity, move
collateral, or create autonomous behavior.

This design preserves the closed Strategy Spec posture:

- closed enumerated forms only;
- bounded composition, with composed operands and predicates preferably at
  depth `<= 3`;
- no expression language, `eval`, `exec`, lambda, callback, script, dynamic
  import, formula parser, user-defined formula, or unrestricted boolean DSL;
- catalog entries remain interface declarations only;
- compiler-owned reviewed computation only;
- Strategy Specs remain declarative and non-executing;
- unsupported forms fail closed;
- no lookahead;
- no paper/live/runtime or protected-path authority.

The current project objective is not to execute many strategy-search WPs now or
to find the final profitable strategy in this phase. The objective is to build
the lab, vocabulary, validation structure, and future automation surfaces that
will later allow systematic testing of many strategy ideas and variants under
anti-overfit and robustness controls.

## Why this design now

The compiler runway now supports a materially richer closed surface than the
earlier compiler-extension plan: parameter-bound indicator lookbacks,
`crosses_above` / `crosses_below`, plus/minus parameter scaling, and locked
both-direction long/short semantics. The first both-direction SMA-band family
has also been exercised through canonical result-population evidence.

The next expressiveness question is therefore not whether the lab can express a
simple symmetric band. It is which closed, non-executable primitives should be
designed next so future BTCUSDT perpetual research can express more plausible
families before any larger strategy-search campaign is considered.

## RP-7520 cost-drag finding and expressiveness implications

`RP-7520` is canonical dynamic-sizing evidence for `STRAT-SPEC-0002` /
`VM-0002` / `SWEEP-PLAN-0002`.

The `RP-7520` population shows the tested symmetric SMA-band strategy is
cost-dragged under the dynamic-equity-target-leverage measurement model.

This is evidence-level interpretation only. It creates no candidate lifecycle
verdict, no ranking, no promotion, no paper/live authority, and no trading
authority.

The tested strategy lacked volatility normalization, trend/regime filtering,
and trade-frequency controls. The next expressiveness tranche should
prioritize primitives that make those families representable before scaling
large strategy search.

Design inference from the evidence: high trade counts and materially negative
returns under dynamic 1x sizing make raw fixed-percentage SMA bands a weak
shape by themselves. Future families need ways to normalize distance by recent
volatility, avoid hostile trend/regime states, and reduce churn.

## Current closed compiler/spec surface

Current repo-truth surface, inspected from schema, validator, compiler, tests,
and status fragments:

| Surface | Current state |
|---|---|
| Directions | `long`, `short`, and closed `both` with explicit side-labeled long/short root entry groups. |
| Both-direction semantics | Single mutually exclusive long/short/flat signal stream; no mirroring; simultaneous long/short entry while flat stays flat; side-specific exits; no silent opposite-side flips. |
| Operators | `gt`, `gte`, `lt`, `lte`, `eq`, `neq`, `crosses_above`, `crosses_below` are supported. `in_set`, `is_true`, and `is_false` remain fail-closed. |
| Operands | `data_ref`, `indicator_ref`, `parameter_ref`, `constant`, and closed `composed_operand`. |
| Composed operands | `scale_by_one_minus_parameter` and `scale_by_one_plus_parameter`; base restricted to `data_ref` / `indicator_ref`; parameter restricted to `parameter_ref`; parameter value in `(0, 1)`; no nesting. |
| Indicator lookbacks | Literal bars or `bars_parameter_ref` for allowed `indicator_ref.lookback` contexts. |
| Catalog/builtins | `sma`, `ema`, `atr`, and `stddev` with compiler-owned builtins. |
| Data refs | Primary OHLCV `open`, `high`, `low`, `close`, `volume`. |
| Timeframe handling | Non-empty operand timeframe values remain unsupported; no multi-timeframe alignment is implemented. |
| Runner/backtester | Offline runner consumes compiled position-intent signals; stop metadata, intrabar stop consumption, and Strategy Spec-to-runtime paths are not authorized by this design. |

## Candidate primitive inventory

| Primitive family | Purpose | Families unlocked | RP-7520 cost-drag relevance | Closed representation sketch | Later touched surfaces | Dependencies | Risk class | Validation requirements | Include / defer / exclude |
|---|---|---|---|---|---|---|---|---|---|
| `z_score` closed composition | Standardize a value versus center and scale. | Volatility-normalized mean reversion, standardized breakout filters, regime filters. | Direct: replaces raw price-distance bands with volatility-scaled distance and may reduce noisy entries. | `composition_type: z_score`, fixed fields `value_operand`, `center_operand`, `scale_operand`, optional closed `zero_scale_policy`. | Schema, validator, compiler, tests; possibly catalog docs if exposed as indicator. | Existing `sma`/`ema` and `stddev` support; exact zero-scale behavior. | Medium-high. | Null/warmup, zero/near-zero denominator, no-lookahead, determinism, fail-closed unknown fields, no nesting expansion. | Include, highest priority design. |
| Volatility-normalized distance / band forms | Express `distance / volatility` without open arithmetic. | Bollinger-like bands, ATR bands, normalized pullback entries. | Direct: raw band thresholds in RP-7520 did not adapt to changing volatility. | Closed forms such as `normalized_distance(value, center, scale)` and threshold predicates using existing operators. | Schema, validator, compiler, tests. | `z_score` or fixed distance form; `stddev` / `atr` semantics. | Medium-high. | Same as z-score plus equivalence tests against manual series. | Include, highest priority. |
| ATR or realized-volatility normalized thresholds | Scale threshold by ATR/stddev/realized volatility. | Volatility breakout, pullback, channel buffer filters. | Direct: can widen/narrow entries and exits by volatility, potentially lowering churn. | Prefer closed composed operand `volatility_band` with base, scale indicator, multiplier parameter. | Schema, validator, compiler, tests; maybe catalog if new realized-vol indicator is added. | Existing `atr`/`stddev`; multiplier parameter bounds. | Medium. | Indicator warmup, null propagation, multiplier bounds, no-lookahead. | Include after z-score shape is locked. |
| Trend/regime filters | Gate entries by trend state. | Trend-following, mean-reversion-in-trend, avoid-countertrend filters. | Direct: can block SMA-band entries during persistent adverse regimes. | Root filter groups using existing operators over `ema`, `sma`, `crosses_*`, or later closed slope/regime primitives. | Mostly Strategy Spec usage if existing indicators suffice; new slope/regime forms need schema/compiler. | Exact closed slope/regime definition if beyond existing indicators. | Medium. | Filter application tests, side interaction under `both`, no-lookahead, determinism. | Include, highest priority. |
| Trade-frequency reduction primitives | Reduce repeated entries in noisy bands. | Lower-turnover mean reversion, breakout retest filters. | Direct: RP-7520 had high trade counts and severe cost drag. | Signal-state controls such as `cooldown_bars_after_exit`, `min_bars_between_entries`, or root entry gate fields. | Schema, validator, compiler state machine, tests; runner unchanged if still signal-only. | Need exact interaction with exits, both-direction state, max holding. | Medium-high. | State-machine tests, simultaneous-side tests, no-lookahead, determinism, edge bars. | Include, highest priority design. |
| Cooldown / re-entry gate | Block re-entry for N bars after an exit. | Churn control, whipsaw reduction. | Direct: targets cost-driven overtrading. | Closed integer field under entry controls, possibly side-specific for `both`. | Schema, validator, compiler tests. | Decide global vs side-specific cooldown. | Medium. | Exit-to-entry sequencing, side-specific behavior, parameter-bound integer checks. | Include within frequency-control design. |
| Minimum-hold / maximum-hold boundary | Preserve or extend holding-period controls. | Avoid instant churn, cap stale positions. | Direct for turnover control; max-hold already exists and should not be widened casually. | Keep `max_holding_period`; design separate `minimum_holding_period` only if exit suppression semantics are locked. | Schema, validator, compiler tests. | Exit ordering and risk semantics; avoid pretending stop/risk control. | Medium-high. | Same-bar exit suppression tests, no forced runtime authority, side-specific both tests. | Design carefully; include max-hold preservation, defer min-hold implementation. |
| Volume / RVOL filter | Gate signals by participation or anomaly. | Breakout confirmation, liquidity filters, churn avoidance. | Indirect: may reduce low-quality entries and cost exposure. | Catalog indicator `rvol` with fixed denominator and zero-volume policy, then normal filter predicates. | Indicator catalog, catalog validator, compiler builtin, tests. | Exact rolling volume average and zero-denominator policy. | Medium. | Formula convention, null/warmup, zero volume, no-lookahead, catalog/builtin hash checks. | Medium priority include. |
| Donchian / channel breakout forms | Express highest-high / lowest-low channels. | Breakout, trend continuation, failed breakout, channel filters. | Indirect: unlocks non-SMA-band families that may trade less or align with regimes. | Catalog indicator with output fields such as `upper`, `lower`, `mid`; current-bar exclusion locked explicitly. | Indicator catalog, validator, compiler builtin, tests. | Current-bar inclusion/exclusion decision; pairs with `crosses_*`. | Medium. | No-lookahead via prior-window tests, output-field validation, null/warmup. | Medium priority include. |
| RSI oscillator | Standard bounded oscillator. | Mean reversion, momentum exhaustion, filter overlays. | Indirect: can filter entries but does not directly solve cost drag alone. | Catalog indicator `rsi` with locked Wilder convention and `value` output. | Indicator catalog, compiler builtin, tests. | Exact RSI convention and warmup. | Medium. | Formula convention, bounded range, null/warmup, no-lookahead. | Medium priority include. |
| `offset_by_parameter` forms | Add/subtract absolute or unit-aware offsets. | Price buffers, oscillator margins, threshold offsets. | Low to medium; useful but unit ambiguity can hide bad comparisons. | Separate closed forms such as `offset_plus_parameter` / `offset_minus_parameter` with parameter unit discipline. | Schema, validator, compiler, tests. | Unit semantics by operand family. | Medium. | Unit checks, no arbitrary arithmetic, null/no-lookahead. | Medium priority, after normalized forms. |
| Rolling VWAP | Volume-weighted centerline. | Intraday mean reversion, participation filters. | Medium: can improve centerline quality but may not reduce churn alone. | Catalog indicator `rolling_vwap` over fixed lookback; no session anchor. | Indicator catalog, compiler builtin, tests. | Decide rolling only; anchored/session VWAP needs time/session model. | Medium-high. | Volume zero policy, rolling window, no-lookahead, warmup. | Design/defer. |
| Session/time UTC-only filters | Closed calendar gates. | Time-of-day effects, weekend filters, liquidity windows. | Medium: can reduce low-liquidity churn if proven later. | Closed predicates over UTC hour/day only; no local timezone or runtime clock. | Schema, validator, compiler tests. | Exact UTC predicate grammar. | High until grammar is locked. | Timezone invariance, deterministic index-only evaluation, no runtime clock. | Design/defer. |
| Multi-timeframe confirmation | Higher-timeframe trend/regime confirmation. | 15m entries gated by 1h/4h state. | Medium-high but unsafe without alignment design. | No representation until data/runner alignment contract exists. | Data layer, runner input contract, compiler alignment, tests, provenance. | Explicit no-lookahead resampling/alignment design. | High. | Higher-timeframe close availability tests, gap handling, provenance, no forward fill. | Defer. |
| ATR-stop consumption | Use volatility stop distances as exits/stops. | Risk exits, trailing exits, volatility stops. | Potentially direct for adverse excursions, but not signal-only. | Do not represent as executable stop until runner/backtester stop-consumption design exists. | Runner/backtester, maybe `lib`, schemas, result assumptions, tests. | Separate stop-consumption design and protected-boundary review. | High / protected-adjacent. | Intrabar semantics, no-lookahead, event ordering, result metadata. | Defer. |
| Cost-aware filter design | Express trade avoidance based on expected cost thresholds. | Cost-aware signal gating, minimum edge filters. | Direct in intent, but dangerous if it becomes optimization or future-aware. | Closed static metadata-derived filter only after cost inputs are declared; no realized future cost reads. | Schema, compiler, runner assumptions, tests. | Exact cost input contract and no-lookahead proof. | High. | No future PnL/cost reads, deterministic static inputs, fail-closed missing assumptions. | Design/defer. |
| Funding/basis feature hooks | Add perp-specific carry or basis context. | Funding mean reversion, basis filters, carry-aware entries. | Medium: can avoid negative carry regimes or exploit basis. | No implementation until data lineage and feature contract are explicit. | Data contract, catalog/feature schema, runner input, compiler, tests. | Committed provenance and alignment contract. | High. | Data lineage, gap handling, no-lookahead, query/provenance validation. | Defer. |
| Open-interest / liquidation hooks | Add leverage/liquidation regime context. | Crowding, squeeze, liquidation cascade filters. | Unknown; could improve perp-specific regimes. | Excluded from current tranche without data contract. | Data acquisition/provenance, schema, compiler, runner, tests. | New data source approval and lineage. | High. | Source provenance, licensing, alignment, no-lookahead. | Defer. |

## Prioritization

Priority criteria:

- direct relevance to the `RP-7520` cost-drag finding;
- closed-grammar safety;
- implementation surface size;
- dependency order;
- utility across multiple strategy families;
- risk of hidden lookahead or execution semantics;
- ability to remain signal-only.

Priority order:

| Priority | Primitive family | Reason |
|---|---|---|
| Highest | `z_score` / volatility-normalized distance and band forms | Most directly addresses raw, unnormalized distance bands and generalizes across mean-reversion, breakout, and regime filters while remaining signal-only if closed arity is preserved. |
| Highest | Trend/regime filters | Uses current OHLCV/indicator foundation and can block hostile state participation without requiring runner/backtester changes. |
| Highest | Trade-frequency controls: cooldown / re-entry gate design | Directly targets cost drag from churn and should be designed before broad search expands turnover-heavy families. |
| Medium | RVOL / volume anomaly filters | Useful cross-family filter, but requires catalog/builtin formula closure. |
| Medium | Donchian/channel primitives | Unlocks breakout/channel families and pairs naturally with existing `crosses_*`; current-bar exclusion must be locked. |
| Medium | RSI | Useful bounded oscillator, but less directly cost-drag-specific than normalization and churn controls. |
| Medium | `offset_by_parameter` forms | Useful closed arithmetic sibling, but unit semantics must be explicit. |
| Design/defer | Rolling VWAP | Useful, but anchored/session variants require a separate session model. |
| Design/defer | UTC-only session/time filters | Potentially useful, but needs a closed index-time predicate design. |
| Design/defer | Multi-timeframe confirmation | Requires data/runner/compiler alignment and no-lookahead design before representation. |
| Design/defer | ATR-stop consumption | Requires runner/backtester stop-consumption design and is not a compiler-only primitive. |
| Design/defer | Funding/basis and open-interest/liquidation hooks | Require data lineage, provenance, and alignment contracts before grammar work. |

Decision: prioritize closed signal-only primitives first. Do not launch broad
strategy search from this design.

## Primitive specifications

### `z_score` / normalized distance

Purpose: provide a fixed-arity standardized distance form.

Closed sketch:

```text
operand_type: composed_operand
composition_type: z_score
value_operand: data_ref | indicator_ref | composed_operand from allowed non-nested set
center_operand: indicator_ref | data_ref
scale_operand: indicator_ref
zero_scale_policy: null_output
```

Design constraint: if allowing a composed operand inside `value_operand` would
create depth or review complexity, the first implementation should restrict all
three operands to `data_ref` / `indicator_ref` only.

Later surfaces: schema, validator, compiler, compiler tests, Strategy Spec
validator tests, documentation. No runner/backtester change is expected if the
output remains a signal operand.

### Volatility band / normalized threshold

Purpose: express `center +/- multiplier * volatility` as a closed threshold.

Closed sketch:

```text
composition_type: volatility_band
center_operand: indicator_ref
scale_operand: indicator_ref
direction: upper | lower
multiplier_parameter_ref: parameter_ref
```

This can express ATR bands, standard-deviation bands, and realized-volatility
bands without arbitrary arithmetic. It should reuse existing `atr` and
`stddev` before adding new realized-volatility catalog entries.

### Trend/regime filters

Purpose: let specs express participation state using closed filters.

Initial posture: prefer existing `sma`, `ema`, `crosses_*`, and comparison
operators. New primitives should be limited to explicit slope or regime-state
forms only after their exact computation is locked.

Closed sketch:

```text
filter group:
  operator: gt | gte | lt | lte | crosses_above | crosses_below
  operands: existing closed operands
```

Future optional primitive:

```text
indicator_id: trend_slope
output: value
lookback: literal bars | bars_parameter_ref
method: closed enum
```

### Trade-frequency controls

Purpose: reduce repeated churn without adding execution semantics.

Closed sketch:

```text
entry_controls:
  cooldown_bars_after_exit: integer literal or parameter_ref
  cooldown_scope: global | side_specific
```

Rules to lock before implementation:

- measured on completed bars only;
- no entry during cooldown;
- exits still allowed;
- simultaneous both-side entries after cooldown still use the existing
  both-direction conflict rule;
- same input produces identical signal stream.

`minimum_holding_period` should be deferred until exit-suppression semantics are
locked, because suppressing exits can alter risk interpretation.

### RVOL / volume anomaly

Purpose: support participation filters.

Closed sketch:

```text
indicator_id: rvol
inputs: volume
lookback: literal bars | bars_parameter_ref
output: value
zero_denominator_policy: null_output
```

Later surfaces: indicator catalog, catalog validation, compiler builtin, tests.

### Donchian / channel

Purpose: express channel breakouts and channel-state filters.

Closed sketch:

```text
indicator_id: donchian
inputs: high, low
lookback: literal bars | bars_parameter_ref
outputs: upper, lower, mid
window_policy: prior_completed_bars_excluding_current
```

The exclusion policy should be locked before implementation to avoid same-bar
high/low leakage in breakout triggers.

### RSI

Purpose: express bounded oscillator filters without open formulas.

Closed sketch:

```text
indicator_id: rsi
input: close
lookback: literal bars | bars_parameter_ref
method: wilder
output: value
```

### Offset forms

Purpose: support simple unit-aware thresholds.

Closed sketch:

```text
composition_type: offset_plus_parameter | offset_minus_parameter
base_operand: data_ref | indicator_ref
parameter_operand: parameter_ref
parameter_unit: same_as_base | ratio_points | explicit_price_units
```

This should wait until parameter unit discipline is explicit. It must not
become arbitrary addition/subtraction grammar.

## Implementation runway map

Future implementation should use the XOVER / PLUSCOMP / BOTHDIR package shape:
design, then schema/validator support where needed, then compiler support where
needed, then checkpoint before canonical artifact use. Canonical artifacts are
allowed only in separately authorized packages.

Suggested bounded runways:

| Runway | Package shape | Scope notes |
|---|---|---|
| R1: normalized-distance design lock | Docs-only design for `z_score` and volatility-band exact grammar. | No schema/compiler change. Decide arity, nesting, zero-scale policy, and parameter bounds. |
| R2: normalized-distance schema/validator | Add only closed grammar and validation tests. | No compiler support unless explicitly scoped. |
| R3: normalized-distance compiler | Implement compiler-owned computation and tests. | No Strategy Spec or result-population use. |
| R4: frequency-control design lock | Docs-only state-machine design for cooldown/re-entry. | Resolve both-direction interaction and min-hold deferral. |
| R5: frequency-control schema/validator/compiler | Only after R4; may need compiler state-machine tests. | Runner unchanged if still signal-only. |
| R6: indicator design bundle | Docs-only formula locks for RVOL, Donchian, RSI. | Could split by indicator if smaller packages are preferred. |
| R7: catalog-plus-compiler indicator additions | Add catalog entries, compiler builtins, tests. | No Strategy Spec or canonical artifact use. |
| R8: deferred alignment designs | MTF, UTC time filters, rolling VWAP, ATR stops, funding/basis, OI/liquidation. | Design/data-contract work only before implementation. |

Surface separation for later packages:

- catalog-only or catalog-plus-compiler: RVOL, Donchian, RSI, rolling VWAP;
- new closed operators: none required immediately beyond existing `crosses_*`;
- new closed composed operands: `z_score`, volatility bands, offset forms;
- schema/validator changes: required for new composed operands and stateful
  entry controls;
- compiler implementation: required for all new computed operands, indicators,
  and stateful controls;
- runner/backtester consumption: deferred for ATR-stop consumption and any
  non-signal output;
- data-contract dependencies: required for MTF, funding/basis, OI/liquidation,
  and any new non-OHLCV feature stream;
- result-population/query impacts: only if output metadata, assumptions, or
  provenance shape changes in future packages;
- dashboard impacts: deferred and not implied by primitive design.

## Deferred / excluded primitives

Excluded from this tranche:

- arbitrary arithmetic language;
- formula strings;
- expression parser;
- user-defined functions;
- `eval`, lambda, custom scripts, callbacks, dynamic imports;
- unrestricted boolean expression DSL;
- catalog-data-interpreted computation;
- open AST semantics.

Deferred:

- multi-timeframe implementation without explicit alignment and no-lookahead
  design;
- ATR stop consumption without runner/backtester stop-consumption design;
- data-driven features without data lineage and provenance contracts;
- anchored/session VWAP until session semantics are locked;
- UTC time filters until closed index-time predicates are designed;
- funding/basis and open-interest/liquidation hooks until feature contracts and
  source provenance are authorized.

Any primitive that requires protected-path or runtime semantics must stop for a
separate authority surface.

## Validation expectations for later implementation WPs

Future docs-only packages should run package-scoped diff checks, result
population validation, query view listing, discovered integrity views, scope
summary, and text authority audits.

Future schema/validator packages should add:

- JSON schema meta-validation;
- focused validator tests for accepted and rejected forms;
- forbidden-key tests;
- depth-limit tests;
- existing-artifact compatibility validation.

Future compiler packages should add:

- focused compiler tests for supported forms;
- fail-closed tests for unsupported forms;
- null/warmup tests;
- no-lookahead mutation tests;
- deterministic repeated-run tests;
- both-direction interaction tests where applicable;
- no-write validation when no artifacts are scoped;
- full pytest unless a future package explicitly narrows that requirement.

Future data-contract packages should add provenance, gap-handling, alignment,
and integrity checks before any compiler or runner consumption is considered.

## Next decision request

Main decision requested:

```text
Accept or revise this priority ordering.
Choose whether the next bounded package should lock normalized-distance grammar,
frequency-control grammar, or a small indicator formula bundle first.
Confirm that no implementation, canonical artifact use, strategy search, data
acquisition, paper/live, runtime, OMS/risk, broker/exchange, collateral, or
autonomy authority follows from this design.
```
