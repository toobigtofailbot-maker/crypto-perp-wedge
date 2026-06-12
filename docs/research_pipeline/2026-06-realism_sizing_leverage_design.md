# Equity-Relative Sizing / Leverage-Cap Realism Design

## Status / authority boundary

This is a docs-only design package. It does not implement sizing logic, rerun a
backtest, mutate any result population, change `lib/backtest.py`, change
`lib/evaluation.py`, change runner behavior, register a candidate, rank
variants, claim readiness, promote a strategy, or authorize paper/live/runtime
behavior.

The design consumes the `RP-6688` sizing/leverage diagnostic as the motivating
case. It defines a future sizing-realism surface for planning only.

## Source diagnostic

Source diagnostic:

- `docs/research_pipeline/2026-06-rp6688_sizing_leverage_diagnostic.md`
- `docs/status_entries/WP-RP6688-SIZING-DIAG-01.md`
- `research/result_populations/RP-6688.result_population.json`

Repo-truth facts from the diagnostic:

- Primary classification: `(b) sizing / leverage artifact`.
- The canonical 15m runner called `run_backtest()` with
  `initial_equity=10000` and `order_size=1.0`.
- `lib/backtest.py` treats `order_size` as a fixed contract/unit quantity.
- PnL is price change times fixed `order_size`.
- Fees and slippage are charged on trade notional through bps of
  `price * order_size`.
- Funding was zero in `RP-6688` because the OHLCV-only canonical 15m path
  supplied zero funding events.
- `zero_equity` liquidation semantics can floor marked equity at zero.
- All ten `RP-6688` rows record `return_pct=-1.0`, `pnl=-10000.0`, and
  `drawdown=1.0`.

## Problem Statement

The current canonical 15m sweep path can measure fixed one-BTC exposure against
a USD 10,000 starting account. That means notional exposure varies mechanically
with BTCUSDT price and is not bounded as a fraction of equity. Direct costs are
then also charged on that fixed one-BTC notional, so cost pressure can dominate
terminal equity.

A future sizing-realism surface should solve this measurement problem:

- express intended initial exposure relative to equity;
- disclose target leverage and any leverage cap;
- keep cost accounting tied to the resulting notional;
- preserve complete-population denominator accounting;
- preserve old result populations under their recorded model;
- make future result populations visibly versioned by sizing model;
- avoid silently reinterpreting fixed-size results as equity-relative results.

## Backward Compatibility

Existing result populations remain valid under their recorded model. They must
not be silently reinterpreted under a new sizing model.

`RP-6688` is not invalidated. It remains evidence that fixed one-BTC sizing can
dominate outcomes for this population. Any future regenerated population must
be a new artifact with a new identity hash, new result-population ID, and an
explicit sizing/pipeline version marker.

Comparable views should keep the sizing model visible. Old fixed-order-size
populations can remain queryable beside later equity-aware populations only
when the model context is visible enough to prevent cross-model confusion.

## Versioning Requirements

A new sizing realism model requires an explicit marker in future result
population metadata. The exact schema surface is not implemented here, but the
future output contract should include fields equivalent to:

- `sizing_model_id` or `sizing_pipeline_version`;
- `initial_equity`;
- `target_leverage`;
- `max_leverage_cap`, if any;
- `reference_price` or `sizing_price_basis`;
- `resolved_order_size`;
- average notional exposure, if available;
- max notional exposure, if available;
- `cost_to_equity_ratio`;
- `fee_to_equity_ratio`;
- `slippage_to_equity_ratio`;
- `funding_to_equity_ratio`;
- liquidation or zero-equity flag/status, if available.

Fields not currently supported by the result-population schema or runner should
be treated as future implementation requirements, not current facts.

## Option 1 - Runner-Side Fixed-But-Equity-Aware Sizing

Definition for future implementation planning:

```text
resolved_order_size = target_leverage * initial_equity / reference_price
```

This option keeps the current fixed-size backtester contract. The runner would
resolve a fixed `order_size` before calling `run_backtest()`, then record the
target leverage, sizing basis, reference price, and resolved size in the future
result population.

Reference-price choices:

- First valid close: simple and deterministic, but not necessarily executable.
- First executable bar price: closest to the first fill model because current
  execution uses next-bar open fills, but must define behavior when no trade is
  taken immediately.
- Configured reference price from data slice: most explicit and reproducible,
  but requires a catalog/spec surface to carry that value.

Planning preference inside Option 1: use the first executable bar price when a
runner can derive it deterministically, with first valid close as the explicit
fallback for no-trade or pre-trade sizing contexts. A configured reference price
can be considered later if data-slice contracts add that field.

What Option 1 preserves:

- no `lib/backtest.py` change;
- no `lib/evaluation.py` change;
- fixed-size backtester behavior;
- current PnL and cost mechanics after `order_size` is resolved;
- existing result populations under their recorded fixed-order-size model.

What Option 1 improves:

- initial notional is capped relative to starting equity;
- cost scale is bounded by the resolved initial exposure;
- future canonical runs can disclose the sizing model without changing
  backtest-core semantics.

Limitations:

- no dynamic compounding as equity changes;
- no de-risking after drawdown;
- no leverage recalculation at each entry;
- notional exposure still changes with price after the reference point;
- sizing remains a runner-side convention unless recorded in future artifacts
  and validated by a later implementation package.

## Option 2 - Lib-Core Dynamic Compounding Equity-Relative Sizing

Definition for future implementation planning:

```text
position_size = current_equity * target_leverage / current_or_entry_price
```

This option would compute size inside the backtester from current equity,
target leverage, and current/entry price. It would allow compounding when
equity rises and de-risking when equity falls.

What Option 2 adds:

- dynamic equity-relative sizing throughout a run;
- leverage targeting at each entry;
- natural reduction of position size after losses;
- richer cost and exposure reporting from the source that owns fills.

Costs and risks:

- likely requires `lib/backtest.py` changes;
- may require `lib/evaluation.py` or result metric changes;
- changes backtest semantics rather than only runner inputs;
- needs stronger Main/Karl review because it is backtest-core-adjacent;
- needs broader tests for determinism, no-lookahead behavior, zero-equity
  handling, cost reporting, and backward compatibility;
- must not imply runtime, paper, or live authority.

Option 2 is a stronger long-term model, but it is not the cheapest honest next
step because it changes protected backtest-core-adjacent semantics.

## Option 3 - Hold / No Sizing Change

Doing nothing would preserve the current fixed one-contract/unit behavior for
future canonical result populations. That would leave new populations
vulnerable to the same fixed-notional distortion diagnosed in `RP-6688`.

Under this option, `RP-6688` would remain evidence of the measurement problem,
not clean evidence of strategy edge or strategy failure. This option is not the
selected design path for further planning.

## Selected Design Path For Further Planning

The design selects Option 1, runner-side fixed-but-equity-aware sizing, as the
next planning path.

Reasons:

- It is the cheapest honest option that addresses the `RP-6688` measurement
  problem at initial exposure scale.
- It can be stated without immediate `lib/backtest.py` or `lib/evaluation.py`
  changes.
- It preserves the existing fixed-size backtester contract.
- It supports explicit sizing-model versioning and cost-to-equity reporting for
  future result populations.
- It keeps Option 2 available for a later Main/Karl-reviewed semantic upgrade
  if runner-side sizing proves insufficient.

This selection does not authorize implementation. It is not a strategy
recommendation, trading recommendation, readiness claim, promotion claim, or
paper/live/runtime authorization.

## Future Reporting Requirements

Future result populations using a new sizing-realism model should report:

- sizing model ID or sizing pipeline version;
- starting equity;
- target leverage;
- max leverage cap, if used;
- reference price and sizing-price basis;
- resolved fixed order size for runner-side sizing;
- average notional exposure, if available;
- max notional exposure, if available;
- total direct cost to starting equity ratio;
- fee to starting equity ratio;
- slippage to starting equity ratio;
- funding to starting equity ratio;
- zero-equity/liquidation status, if available;
- whether sizing is fixed after run start or dynamically recomputed;
- whether the result population is comparable only within the same sizing
  model.

For runner-side Option 1, the minimum viable future output should record:

```text
sizing_model_id = fixed_equity_aware_initial_notional_v1
target_leverage
initial_equity
reference_price
sizing_price_basis
resolved_order_size
fee_to_equity_ratio
slippage_to_equity_ratio
funding_to_equity_ratio
cost_to_equity_ratio
zero_equity_or_liquidation_status
```

## Migration Posture

Migration must be append-only:

- old result populations stay unchanged;
- old result populations stay valid under their recorded model;
- new sizing model runs write new result populations;
- old and new populations must not share identity hashes;
- query/comparison surfaces should expose sizing-model context;
- no old row should be relabeled as if it used equity-aware sizing;
- `RP-6688` remains fixed-order-size evidence, not an invalid artifact.

Any future regeneration of `RP-6688` parents under an equity-aware sizing model
must use a new result-population ID and preserve the original `RP-6688`.

## Implementation Split

Proposed future split, not authorized here:

- `WP-REALISM-SIZING-01b`: implementation-readiness and impact map, no code.
  It should map exact runner/spec/schema/reporting surfaces needed for Option
  1, identify whether result-population schema changes are required, define
  validation cases, and confirm no immediate `lib/backtest.py` or
  `lib/evaluation.py` change is required.
- `WP-REALISM-SIZING-01c`: first code implementation slice, not authorized
  here. If Option 1 remains viable, this would likely be runner/spec/output
  plumbing rather than backtest-core behavior. If 01b finds that `lib/` changes
  are required, 01c must return to Main/Karl before authorization.
- Future result regeneration: separately gated. It should create new result
  populations only after the sizing model and reporting fields are validated.

## Validation Evidence Required Before Future Regeneration

Before any future result regeneration under a new sizing model, a separate
implementation package should provide evidence for:

- deterministic resolution of `reference_price`;
- deterministic resolution of `resolved_order_size`;
- fail-closed behavior for missing, zero, negative, or non-finite reference
  prices;
- fail-closed behavior for invalid target leverage or leverage cap;
- stable identity hashing that includes sizing model and resolved sizing facts;
- schema/validator acceptance for new sizing/cost-reporting fields, if schema
  changes are needed;
- unchanged old result-population validation;
- no mutation of existing result populations;
- cost-to-equity, fee-to-equity, slippage-to-equity, and funding-to-equity
  calculations;
- zero-equity/liquidation reporting where supported;
- exact changed-file scope;
- no paper/live/runtime/protected-path contact.

Full strategy-quality interpretation, robustness, ranking, readiness,
promotion, and trading use remain outside this design.
