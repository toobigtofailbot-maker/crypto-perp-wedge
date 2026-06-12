# Dynamic Equity-Relative Sizing Implementation Note

## Status / authority boundary

`WP-REALISM-SIZING-02b` implements an opt-in dynamic equity-relative sizing
mode in `lib/backtest.py` under protected-path discipline.

This implementation is opt-in and default-preserving. It does not expose runner integration, change schemas or validators, write canonical result populations, mutate prior RPs, register candidates, rank variants, mark readiness, promote strategies, or authorize paper/live/runtime behavior.

## Source design

Source design:

- `docs/research_pipeline/2026-06-dynamic_equity_sizing_design.md`
- `docs/status_entries/WP-REALISM-SIZING-02a.md`

The source design locked the additive `dynamic_equity_target_leverage` mode,
the `fixed_order_size` default, the current realized-equity basis, and the
next-bar-open entry reference price basis.

## Implemented modes

Implemented backtest-core sizing modes:

- `fixed_order_size`: default mode; uses the existing `order_size` argument.
- `dynamic_equity_target_leverage`: opt-in mode; computes each new entry
  quantity from current realized equity and the entry reference price.

No runner integration is exposed in this package.

## Fixed default preservation

Callers that omit `sizing_mode` continue to run under `fixed_order_size`.
Explicit `sizing_mode="fixed_order_size"` uses the same `order_size` quantity
path as the implicit default.

The implementation keeps existing result fields and trade-row meanings intact.
It adds sizing identity fields to the existing params snapshot without changing
the `BacktestResult` dataclass shape.

## Dynamic sizing formula

For a new dynamic-mode entry:

```text
quantity = target_leverage * sizing_equity / entry_reference_price
```

`target_leverage` is validated as finite and positive for dynamic mode. This
slice adds no leverage cap, rounding, lot-size, or min-notional enforcement.

## Equity basis

The dynamic sizing equity basis is:

```text
realized_available_equity_at_entry
```

It is the current realized account equity in the bar loop after funding due
through the entry bar and after any same-bar close, exit fee, and exit slippage
costs, before new entry fee and slippage costs.

## Entry reference price basis

The dynamic entry reference price basis is:

```text
next_bar_open_pre_fee_slippage
```

It is the existing next-bar-open fill price before separate fee/slippage cost
application. It does not use later close, high, low, final equity, or result
metrics.

## Edge cases

Dynamic mode fails fast when `target_leverage` is missing, non-finite, zero, or
negative.

Dynamic entry attempts fail closed and stay flat when:

- sizing equity is non-finite, zero, or negative;
- entry reference price is missing, non-finite, zero, or negative;
- the computed quantity is non-finite, zero, or negative.

Fail-closed entries do not charge entry fee or slippage and do not create a
trade row. Existing liquidation handling still runs after the failed entry
attempt for the current bar.

## Cost / funding / liquidation interaction

The implementation changes quantity selection only. It does not change the
fee, slippage, funding, PnL, or liquidation models.

In dynamic mode, the current open position quantity is used for:

- entry fees and slippage;
- exit realized PnL, fees, and slippage;
- funding notional under both existing funding-notional modes;
- marked unrealized PnL;
- maintenance-margin notional;
- liquidation price math;
- trade-row `size`, `entry_notional`, `exit_notional`, and `notional`.

Fixed mode initializes the current open position quantity from `order_size`, so
the existing fixed-size path remains behaviorally unchanged.

## Params snapshot

The existing `BacktestResult.params` dictionary now records:

- `sizing_mode`
- `target_leverage`
- `sizing_equity_basis`
- `entry_reference_price_basis`
- `order_size`

For fixed mode, the equity and reference basis fields record
`not_applicable_fixed_order_size`. For dynamic mode, they record the locked
dynamic basis strings.

## Tests and validation

Focused backtest tests cover:

- implicit fixed default versus explicit fixed-mode preservation;
- dynamic formula math;
- realized-equity scaling across separate entries;
- long/short quantity symmetry;
- non-positive sizing equity fail-closed handling;
- invalid reference price fail-closed handling;
- invalid target leverage rejection;
- no-lookahead entry quantity behavior;
- determinism;
- dynamic fee, slippage, funding, and maintenance-margin interactions;
- benign 1x dynamic maintenance-margin behavior.

Final validation evidence is recorded in
`docs/status_entries/WP-REALISM-SIZING-02b.md`.

## What this package does not authorize

This package does not authorize runner exposure, schema or validator changes,
result-population schema changes, canonical reruns, candidate registration,
ranking, readiness, promotion, paper/live/runtime behavior, OMS/risk behavior,
broker/exchange behavior, or any `lib/evaluation.py` change.

It does not mutate `RP-2134`, `RP-4492`, or `RP-6688`.

## Next authority

No follow-on package is automatically authorized by this implementation.
Main/Karl review is required after merge before any runner exposure, sizing
metadata schema/validator work, canonical dynamic-sizing rerun, candidate
registration, or paper/live/runtime work.
