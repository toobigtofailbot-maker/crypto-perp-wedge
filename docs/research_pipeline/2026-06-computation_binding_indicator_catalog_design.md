# Computation-Binding / Indicator-Catalog Design

## 1. Scope And Non-Authority

WP-12hp / WP-S2c-196 is a Tier 1 documentation-only design opening for the computation-binding tranche.

This package creates no schema, validator, catalog instance, compiler implementation, runner integration, backtester change, evaluation change, Strategy Spec instance, variant manifest, sweep plan, result population, canonical sweep, EXP, REP, trial-log entry, OL, REC, DEC, runtime change, paper/live change, protected-path change, recommendation, ranking, readiness, transition, gate, approval, or human-gate execution authority.

The design is offline research-only. Any future package that requires modifying `lib.backtest.run_backtest(...)`, `lib/evaluation.py`, runtime, paper/live, OMS, reconciliation, risk, safe mode, kill-switch, configs, dependencies, or protected paths must halt unless separately authorized.

## 2. Problem Statement

Current blocker:

```text
Strategy Spec artifacts can describe conditions, but current repo truth does not bind those conditions to computed signals for backtesting.
```

Repo-truth basis:

- `research/schemas/strategy_spec.schema.json` defines declarative operands and closed operators.
- `tools/registry/validate_strategy_specs.py` validates shape, closed operators, depth, free-parameter limits, forbidden executable keys, non-authority flags, and host-data-reference safety.
- `tools/research_runner/run_offline_sweep.py` validates parent artifacts but currently builds synthetic OHLCV, funding, and signal inputs.
- `lib.backtest.run_backtest(...)` consumes a precomputed `signal`, `ohlcv`, and `funding`; it does not consume Strategy Spec JSON directly and does not compute indicators.
- No committed indicator catalog schema, catalog instance, or Strategy Spec-to-signal compiler exists.

Decision:

- The next tranche must define a reviewed computation binding before canonical Strategy Spec-derived sweeps can produce real evidence.

## 3. Indicator Catalog Concept

The indicator catalog should be a closed, schema-validated artifact family in a later package. It should provide deterministic, reviewed name-to-computation contracts for indicators that Strategy Specs may reference through `indicator_ref`.

Required concept boundaries:

- closed catalog entries only;
- no arbitrary Python, callbacks, scripts, eval, lambdas, SQL, shell, URLs, or host-language snippets;
- no arbitrary arithmetic expressions embedded in Strategy Specs;
- no hidden computation inside notes;
- no code keyed off arbitrary unreviewed indicator names;
- no runtime authority;
- offline research-only consumer posture.

Terminology:

| Term | Meaning |
|---|---|
| catalog definition | Reviewed computation contract for one named indicator, including inputs, parameters, output fields, warmup posture, and invalid-data posture. |
| `indicator_ref` | Strategy Spec operand reference to one locked catalog entry and one of its declared output fields. |
| compiler | Future allowed consumer that resolves Strategy Spec data refs, indicator refs, and variant-assigned parameter values into deterministic signal series for the existing backtester. |

Only this path should be eligible for computation:

```text
locked catalog entry
+ closed Strategy Spec operator
+ declared parameter assignment
+ supplied data frame
= deterministic signal
```

## 4. First Catalog Set

The first closed catalog set should be exactly:

```text
SMA
EMA
ATR
StdDev
```

These entries are suitable for the first implementation slice because they are deterministic OHLCV-derived primitives, are broadly understood, and support the currently selected Dynamic Volatility Mean Reversion design without introducing composed indicator authority.

| Indicator | Required input fields | Required parameters | Deterministic expectation | Output fields | Warmup / insufficient history | NaN/null posture | Timeframe/source posture | First-slice safety |
|---|---|---|---|---|---|---|---|---|
| SMA | One numeric series, typically `close` | `lookback_bars` integer greater than 0 | Rolling arithmetic mean over the declared lookback using only current and prior bars | `value` | Output null until full lookback exists | Null input inside window yields null output unless later schema locks stricter blocking | Resolved from supplied OHLCV frame at the Strategy Spec operand timeframe | Safe |
| EMA | One numeric series, typically `close` | `lookback_bars` integer greater than 0; smoothing convention must be locked later | Exponential moving average with one reviewed smoothing convention and no lookahead | `value` | Output null until the locked initialization posture is satisfied | Null input propagates or blocks per later catalog schema; no silent fill | Resolved from supplied OHLCV frame at the Strategy Spec operand timeframe | Safe if initialization is explicit |
| ATR | `high`, `low`, `close` | `lookback_bars` integer greater than 0; true-range convention must be locked later | Average true range over reviewed true-range and smoothing conventions using prior close where required | `value` | Output null until prior close and full lookback requirements are satisfied | Null OHLC input yields null output or compile failure per later schema | Resolved from supplied OHLCV frame at the Strategy Spec operand timeframe | Safe if true-range and smoothing conventions are explicit |
| StdDev | One numeric series, typically `close` | `lookback_bars` integer greater than 1; population/sample convention must be locked later | Rolling standard deviation over the declared lookback with one reviewed degrees-of-freedom convention | `value` | Output null until full lookback exists | Null input inside window yields null output unless later schema locks stricter blocking | Resolved from supplied OHLCV frame at the Strategy Spec operand timeframe | Safe if degrees-of-freedom convention is explicit |

The first catalog set must not include `z_score` as a single named promissory indicator.

## 5. Raw OHLCV `data_ref` Operands

Raw OHLCV operands in the first binding slice should be:

```text
open
high
low
close
volume
```

Strategy Spec `data_ref` operands should refer to these fields through the existing operand shape, with `operand_type = "data_ref"`, a closed or validated ref to the OHLCV stream, an explicit `field`, and an explicit `timeframe` compatible with the supplied OHLCV frame.

The compiler should resolve raw OHLCV operands from the supplied OHLCV DataFrame columns:

- `open`;
- `high`;
- `low`;
- `close`;
- `volume`.

`lib.backtest.run_backtest(...)` requires `open`, `high`, `low`, `close`, and `volume` in the OHLCV frame. It uses the precomputed signal for position intent, fills signal changes at next-bar open, uses close for marking, and can use volume for opt-in liquidity-cap checks.

Raw OHLCV alone is not sufficient to validate the catalog mechanism because it does not exercise `indicator_ref` resolution, parameterized indicator computation, warmup handling, or Strategy Spec condition compilation from named catalog entries.

## 6. Strategy Spec Condition Support

The first supported condition subset should stay inside the existing closed Strategy Spec grammar.

Supported left operands:

- `data_ref`;
- `indicator_ref`.

Supported right operands:

- `constant`;
- `parameter_ref`;
- `data_ref` only when both sides resolve to aligned series;
- `indicator_ref` only when both sides resolve to aligned catalog outputs.

First-slice operators should prefer stateless comparisons:

- `gt`;
- `gte`;
- `lt`;
- `lte`;
- `eq`;
- `neq`.

No new operators are designed here.

`crosses_above` and `crosses_below` remain valid existing grammar, but first implementation should defer them unless the compiler design explicitly locks prior-bar state handling, warmup around the prior bar, and behavior when either current or prior operand value is null.

`in_set`, `is_true`, and `is_false` remain existing grammar but are not needed for the first OHLCV indicator-binding slice.

## 7. Variant Assignment Binding

The binding model should be:

```text
Strategy Spec free parameter declaration
+ variant manifest assignment
= concrete parameter values for one compiled variant signal
```

The compiler should require every `parameter_ref` used in compiled conditions or indicator parameters to resolve to exactly one concrete value from the variant assignment or a declared fixed default that is not part of the free-parameter grid.

Preserved constraints:

- max 5 free parameters;
- finite bounded variant population;
- committed denominator from the pre-registered manifest and sweep plan;
- no adaptive search;
- no post-hoc expansion;
- no result-conditioned variant mutation;
- failed, invalid, skipped, and not-attempted variants remain denominator-visible in later result populations.

## 8. Compiler Concept

Future compiler surface:

```text
compile_signal(spec, variant_assignment, ohlcv, funding, catalog) -> signal series
```

Conceptual requirements:

- deterministic output for fixed inputs;
- UTC DatetimeIndex output aligned to the supplied primary OHLCV bar index;
- output values use the existing backtester representation: `+1` long, `-1` short, `0` flat;
- no lookahead: signal at bar `t` represents intent available after bar `t` and fills through `run_backtest(...)` at open of bar `t+1`;
- warmup bars with insufficient data produce flat `0` unless a later schema locks per-variant failure for specific insufficient-data cases;
- null/NaN operands cannot silently become trading signals;
- compile failures are per-variant where possible and should map to later result-population rows such as `errored`, `invalid`, or `data_unavailable` according to the existing closed outcome enum;
- infrastructure-level compile aborts should preserve not-attempted rows for remaining variants;
- no canonical writes in the first compiler implementation;
- WP-S2c-199 should be build-and-test-only with fixture/synthetic inputs, no canonical Strategy Spec use, and no canonical result-population writes.

Role interpretation:

- entry groups define when the compiler may move from flat to long or short, subject to declared direction support;
- exit groups define when the compiler moves an open position to flat;
- filter/blocking/no-trade groups can suppress new entries and, only if explicitly designed later, may force flattening;
- risk groups such as ATR stop posture require separate precise design before executable use, because current `run_backtest(...)` accepts only a position-intent signal and does not model arbitrary intrabar stop orders.

The compiler adapts Strategy Spec output into the existing precomputed signal input expected by `lib.backtest.run_backtest(...)`.

## 9. Non-Executable-Spec Boundary

Explicitly forbidden:

- arbitrary expressions;
- formulas inside Strategy Spec artifacts;
- Python/eval/lambda/script/code fields;
- SQL/shell/URL/file-path computation hooks;
- code keyed off arbitrary indicator names;
- computation hidden in notes;
- Strategy Spec as runtime authority;
- Strategy Spec as paper/live authority;
- Strategy Spec as order, broker, exchange, OMS, reconciliation, risk, safe-mode, or kill-switch authority.

Strategy Spec remains declarative. The compiler may only consume closed Strategy Spec operators, declared operands, locked catalog entries, declared parameter assignments, and supplied data frames.

## 10. Backtester Interface Preservation

`lib.backtest.run_backtest(...)` remains unchanged.

`lib/evaluation.py` remains unchanged.

The compiler concept must adapt Strategy Spec-derived logic into the existing precomputed `signal` Series. Any design requiring modification to `lib/backtest.py` or `lib/evaluation.py` is out of scope for this package and must halt.

## 11. First-Slice Package Sequence

Authorized sequence:

```text
WP-S2c-196 - design opening
WP-S2c-197 - indicator catalog schema
WP-S2c-198 - indicator catalog instance for SMA/EMA/ATR/StdDev + validator
WP-S2c-199 - build-and-test-only spec->signal compiler
WP-S2c-200 - computation-binding tranche checkpoint
```

Required report-backs:

- after WP-S2c-196: Main reviews catalog schema shape and compiler surface before WP-S2c-197;
- after WP-S2c-199: Main reviews compiler computation surface before canonical use;
- after WP-S2c-200: Main re-engages for revised first canonical spec path.

## 12. `z_score` Posture

`z_score` remains deferred.

It should not be treated as a single named promissory indicator. It becomes eligible only after the indicator-catalog and composition discipline is reviewed. The initial catalog primitives SMA, EMA, ATR, and StdDev support future composition work but do not authorize composed indicators by themselves.

## 13. Karl Future-Lab Requirement

Karl wants the lab eventually to test:

- candle/statistical strategies;
- session/multi-timeframe strategies;
- derivatives-data strategies;
- microstructure/order-book strategies;
- execution-simulation-heavy strategies;
- calendar/time-anchor strategies;
- regime-routing strategies.

This design is foundational because all those families require explicit data, indicator, simulator, and signal binding. They must not rely on hidden computation in notes, arbitrary indicator names, unreviewed runner assumptions, or executable Strategy Spec text.

## 14. Open Decisions For Main

Before WP-S2c-197, Main should decide:

1. approve or adjust the catalog schema shape;
2. approve or adjust the first catalog entries;
3. approve or adjust the compiler surface;
4. decide whether WP-S2c-197 may auto-draft;
5. identify any required simplification before schema work.
