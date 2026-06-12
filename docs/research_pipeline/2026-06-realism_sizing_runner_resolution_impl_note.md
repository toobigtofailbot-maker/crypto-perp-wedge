# Runner-Side Sizing Resolution Implementation Note

## Status / authority boundary

`WP-REALISM-SIZING-01c` implements runner-side fixed order-size resolution for
offline sweeps as a build-and-test-only package. It does not write a canonical
result population, mutate `RP-6688`, change `lib/backtest.py`, change
`lib/evaluation.py`, change schemas or validators, register a candidate, rank
variants, claim readiness, promote a strategy, or create paper/live/runtime
authority.

## Source design and impact map

Source design:

- `docs/research_pipeline/2026-06-realism_sizing_leverage_design.md`
- `docs/status_entries/WP-REALISM-SIZING-01a.md`

Source impact map:

- `docs/research_pipeline/2026-06-realism_sizing_implementation_impact_map.md`
- `docs/status_entries/WP-REALISM-SIZING-01b.md`

The impact map classified `lib/backtest.py` and `lib/evaluation.py` as not
required for the first Option 1 runner/spec-side implementation slice.

## Implemented behavior

The offline sweep runner now accepts a target leverage input, defaulting to
`1.0`. Before calling the existing backtester, the runner resolves a fixed
`order_size` from target leverage, starting equity, and the first in-sample
open price of the actual OHLCV frame used by that run.

The existing backtester still receives a fixed `order_size`. No dynamic
compounding or per-entry resizing is implemented.

## Sizing formula

```text
resolved_order_size = target_leverage * initial_equity / reference_price
```

For this package:

- `target_leverage` is a runner parameter.
- `initial_equity` remains `10000.0`.
- `reference_price` is the first in-sample bar open.
- `resolved_order_size` is passed to `run_backtest(order_size=...)`.

Invalid target leverage values fail closed when they are non-numeric, zero,
negative, NaN, or infinite.

## Reference-price basis

Reference-price basis:

```text
first_in_sample_open
```

The reference price comes from the same OHLCV frame the runner passes to the
backtester. It is deterministic and uses no later bar. Missing, zero, negative,
NaN, or infinite first-open values fail closed.

## Provenance / assumption recording

The result-population schema does not currently permit new structured sizing
fields. This package records sizing provenance in the existing
`backtest_assumption_summary.order_size_assumption` string, which is already in
the result-population identity hash scope.

Recorded facts include:

- `sizing_model=runner_resolved_fixed_order_size`
- `target_leverage`
- `initial_equity`
- `reference_price_basis=first_in_sample_open`
- exact `reference_price` and `resolved_order_size` for canonical 15m input
- per-variant reference/resolution disclosure for synthetic fixtures
- the drift caveat

## Drift limitation

Runner-side fixed order-size resolution caps leverage at the reference price
only. Effective leverage can drift as price changes over long real-data
slices. This package measures that drift in tests but does not solve it
dynamically.

## Tests

Focused runner tests cover:

- target leverage resolution from `target_leverage * initial_equity / first_open`;
- default target leverage of `1.0x`;
- API and CLI rejection of invalid target leverage;
- fail-closed invalid first-open reference prices;
- no-lookahead behavior when later prices change;
- deterministic sizing metadata for repeated inputs;
- dry-run behavior with no canonical result-population write;
- short real-like fixture sub-window sizing;
- start-vs-end effective-leverage drift measurement.

## What this does not authorize

This implementation does not authorize a canonical re-run, new result
population, sizing metadata schema package, Strategy Spec or sweep-plan sizing
declaration, query/dashboard surfacing, dynamic lib-core sizing, candidate
registration, ranking, readiness, promotion, paper/live/runtime work, or
execution authority.

## Next decision fork

Main/Karl review is required after merge to choose the next fork:

- Fixed-good-enough: authorize a Karl-gated canonical re-run under
  leverage-aware fixed sizing.
- Dynamic required: authorize protected lib-core dynamic sizing runway, with
  Main two-stage review and Karl methodology sign-off.
