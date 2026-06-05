# Computation-Binding Tranche Checkpoint

## Status / Authority

This is a checkpoint document only.

It does not authorize first canonical Strategy Spec creation. It does not authorize canonical sweeps. It does not authorize compiler extension. It does not authorize result population creation. It does not authorize strategy ranking. It does not authorize paper/live/runtime/protected-path work. It creates no downstream authority.

## Tranche Inventory

WP-S2c-196 created `docs/research_pipeline/2026-06-computation_binding_indicator_catalog_design.md`. It defined the computation-binding / indicator-catalog design and preserved the boundary that Strategy Specs remain declarative and non-executable.

WP-S2c-197 created `research/schemas/indicator_catalog.schema.json` and `docs/research_pipeline/2026-06-indicator_catalog_schema.md`. It locked an interface-only catalog schema for SMA, EMA, ATR, and StdDev and preserved the boundary that catalog data cannot define computation.

WP-S2c-198 created `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json`, `tools/registry/validate_indicator_catalogs.py`, and `tests/test_validate_indicator_catalogs.py`. It instantiated the first closed indicator catalog and validator while preserving the boundary that catalog approval is interface-only and not compiler, runner, sweep, result, runtime, paper/live, recommendation, ranking, readiness, transition, gate, order, broker, or exchange authority.

WP-S2c-199 created `tools/research_runner/spec_signal_compiler.py` and `tests/test_spec_signal_compiler.py`. It added a build-and-test-only Strategy Spec to signal compiler with compiler-owned reviewed builtins and preserved the boundary that no canonical Strategy Spec, variant manifest, sweep plan, result population, canonical signal, runner integration, backtester change, or runtime authority was created.

WP-S2c-199a created `research/briefs/2026-06-agent_research_data_simulator_capability.md` and `research/briefs/README.md`. It preserved Agent research as non-authoritative planning input only and created no implementation authorization, strategy ranking, vendor commitment, canonical evidence, or protected-path authority.

## Current Architecture Checkpoint

Approved Option A is preserved:

```text
Strategy Spec
+ variant assignment
+ OHLCV/funding frames
+ closed indicator catalog
-> catalog lookup
-> exact approved builtin_key
-> compiler-owned reviewed builtin
-> closed operator evaluation
-> deterministic signal series
-> existing run_backtest(...) consumes precomputed signal
```

Catalog declares interface only. Compiler owns reviewed computation. Catalog data is not interpreted as computation. Strategy Spec remains non-executable.

## Current Compiler Capability Surface

Current supported operands:

```text
data_ref
indicator_ref
parameter_ref
constant
```

Current supported operators:

```text
gt
gte
lt
lte
eq
neq
```

Current supported directions:

```text
long
short
```

Current supported builtins:

```text
sma_v1
ema_v1
atr_v1
stddev_v1
```

Current supported indicator refs:

```text
sma
ema
atr
stddev
```

Signal values:

```text
+1.0
0.0
-1.0
```

## Fail-Closed Limitations

`entry_logic.direction = "both"` fails closed. `crosses_above` fails closed. `crosses_below` fails closed. `in_set` fails closed. `is_true` fails closed. `is_false` fails closed.

Indicator lookback parameter-binding fails closed. Indicator lookbacks are literal only through `operand.lookback.bars`.

`z_score` is still deferred. StdDev exists as a primitive only; composition discipline is not yet implemented.

No session/multi-timeframe resampling support exists. Non-empty operand timeframe values fail closed.

No VWAP/RVOL/Donchian/RSI/OBI/liquidation/CME features exist yet.

## No-Other-Path Confirmation

There are no arbitrary expressions. There are no formulas in Strategy Spec. There are no formulas in catalog data. There is no `eval`, `exec`, lambda, script, or dynamic import path. There is no code dispatch on arbitrary unreviewed names. There is no catalog-data-interpreted computation. There is no notes-as-computation. There is no runtime/paper/live authority.

## Agent Research Brief Reference

`research/briefs/2026-06-agent_research_data_simulator_capability.md` is non-authoritative planning input only. It cannot override repo truth, Main/Karl decisions, or approved work packages.

Planning-relevant points preserved there:

- build indicators/features/signals internally;
- source raw observations externally;
- use Binance-first raw data where suitable;
- treat FMP as supplementary only;
- consider paid data only when a strategy class requires it;
- expand simulator capability in layers;
- use mature repos as architecture lessons, not shortcuts.

## Revised First-Canonical-Spec Path Within Current Compiler Limits

A first canonical Strategy Spec using the current compiler must be:

- single-direction: long-only or short-only;
- fixed indicator lookbacks;
- free parameters limited to comparison thresholds/multipliers via `parameter_ref`;
- no more than 5 free parameters;
- operators limited to `gt`, `gte`, `lt`, `lte`, `eq`, `neq`;
- indicator refs limited to `sma`, `ema`, `atr`, `stddev`;
- no `both` direction;
- no `crosses_*`;
- no `z_score`;
- no lookback sweep;
- no multi-timeframe/session support;
- no non-candle simulator dependency.

Candidate shapes, as examples only and not recommendations or authorization:

- long-only SMA/EMA distance threshold with fixed lookbacks and swept threshold;
- long-only ATR-threshold / volatility breakout with fixed ATR lookback and swept multiplier;
- short-only equivalent only if Main/Karl prefers short-only.

No strategy profit claim is made here.

## Decision Options For Main/Karl

Option 1 - constrained first spec now:

```text
Use current compiler limits.
Create a first canonical Strategy Spec with fixed lookbacks and swept threshold/multiplier parameters.
Then run first canonical sweep through the existing pipeline.
```

Pros:

- gets a real first canonical sweep through the pipeline sooner;
- tests the newly built catalog/compiler/result-population path;
- keeps scope narrow.

Risks/limits:

- first spec is intentionally constrained;
- no lookback sweep;
- no both direction;
- no z_score/composed indicators.

Option 2 - compiler extension first:

```text
Before first canonical spec, extend compiler to support lookback parameter binding and/or both direction and/or crosses_*.
```

Pros:

- richer first spec;
- unblocks more future strategy families;
- supports z_score/composition path later.

Risks/limits:

- delays first canonical sweep;
- requires another reviewed compiler-extension tranche;
- must preserve non-executable boundary.

Main previously leaned Option 1, but decision is reserved for WP-S2c-200 report-back.

## Recommended Report-Back Questions

1. Should the next package draft a constrained first canonical Strategy Spec using current compiler limits?
2. Or should Side draft a compiler-extension tranche first?
3. If constrained first spec is chosen, should it be long-only SMA/EMA-distance, long-only ATR-threshold, or another current-compiler-compatible shape?
4. Should lookback parameter binding be the first compiler extension after the first sweep?
5. Should z_score remain deferred until composition + lookback-binding are reviewed?
