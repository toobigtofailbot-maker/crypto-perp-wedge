# Dynamic Equity-Relative Sizing Design

## Status / authority boundary

This is a docs-only, read-only design and protected-path scope-surfacing package. It does not edit `lib/backtest.py`, `lib/evaluation.py`, runner code, schema, validators, tests, Strategy Specs, variant manifests, sweep plans, result populations, data, candidate registry, dashboard implementation, runtime, paper/live, OMS/risk, broker/exchange, or protected paths. It does not authorize implementation, canonical reruns, candidate registration, ranking, readiness, promotion, or trading.

`WP-REALISM-SIZING-02a` records a design for Main/Karl review only. Any future code package that touches `lib/backtest.py` or `lib/evaluation.py` requires explicit future authorization after this surfaced scope is reviewed.

## Source runway and motivation

Fact:

- `WP-RP6688-SIZING-DIAG-01` classified `RP-6688` as primarily affected by fixed-unit sizing and leverage drift.
- `WP-REALISM-SIZING-01a` designed the equity-relative sizing runway and kept lib-core dynamic sizing as a later Main/Karl-reviewed path.
- `WP-REALISM-SIZING-01b` mapped runner/spec-side fixed sizing as the smallest first implementation path and classified `lib/backtest.py` and `lib/evaluation.py` as not required for that first slice.
- `WP-REALISM-SIZING-01c` is merged in PR #444 and implements runner-side fixed order-size resolution from target leverage, starting equity, and first in-sample open.

Inference:

- The 01c runner fix improves starting exposure but does not resize future entries after price or equity changes.
- Long slices can still drift because a fixed quantity calibrated at the first bar is reused for later entries.

Decision recorded for this design:

- Define an additive, opt-in dynamic sizing mode for future review.
- Surface the exact protected-path regions a later code package would likely touch.
- Do not implement the mode in this package.

## Current fixed-sizing limitation

Current backtest-core behavior accepts a fixed `order_size` and uses it for every fill in the run. In the 01c runner path, that fixed size is resolved once:

```text
resolved_order_size = target_leverage * initial_equity / first_in_sample_open
```

That caps notional exposure at the reference price only. If BTCUSDT rises materially after the first in-sample open, a fixed quantity can represent a larger notional fraction of equity on later entries. If equity falls, the same fixed quantity can also represent a larger fraction of remaining equity.

This limitation is a sizing-methodology limitation, not evidence that any result population should be reinterpreted.

## Design goals

- Preserve current `order_size` behavior by default.
- Add a future opt-in `sizing_mode` surface.
- Define deterministic per-entry dynamic sizing semantics.
- Keep sizing no-lookahead under the current signal-at-bar-t, fill-at-next-open model.
- Keep fee, slippage, funding, liquidation, and PnL mechanics unchanged unless a later package explicitly scopes changes.
- Make sizing mode and basis identity-bearing for future dynamic result populations.
- Preserve prior result-population reproducibility.
- Define validation expectations for a future implementation package.

## Non-goals

- No code change.
- No schema, validator, test, runner, query, dashboard, data, or artifact change.
- No canonical result-population write or rerun.
- No migration or reinterpretation of `RP-2134`, `RP-4492`, or `RP-6688`.
- No Strategy Spec, variant manifest, or sweep-plan mutation.
- No runtime, paper/live, OMS/risk, broker/exchange, safe-mode, or execution-path authority.
- No ranking, readiness, promotion, candidate registration, or trading authority.

## Proposed additive sizing modes

Future `sizing_mode` values should include at least:

```text
fixed_order_size
dynamic_equity_target_leverage
```

`fixed_order_size`:

- Existing behavior.
- Default behavior.
- Uses the fixed `order_size` argument.
- Preserves all prior result populations under their recorded assumptions.
- Does not reinterpret `RP-2134`, `RP-4492`, or `RP-6688`.

`dynamic_equity_target_leverage`:

- Opt-in only.
- Computes quantity at each new entry.
- Uses current sizing equity available at the time of entry.
- Uses an entry reference price available at or before the execution decision.
- Computes quantity dynamically:

```text
quantity = target_leverage * sizing_equity / entry_reference_price
```

## Default-preservation contract

A future implementation must preserve `fixed_order_size` as the default.
Existing callers without an explicit sizing mode must produce identical results to current behavior, except for intentionally versioned outputs where the mode is explicitly changed.
Prior result populations remain reproducible and must not be silently reinterpreted.

Required future regression evidence:

- Before/after default-preservation test for callers that omit `sizing_mode`.
- Deterministic fixture equality when `sizing_mode=fixed_order_size`.
- Existing `order_size` validation and run parameters preserved for fixed mode.
- Existing result-population validation unchanged.
- No schema-required changes unless separately authorized.

## Dynamic sizing semantics

Definitions for future review:

- `target_leverage`: finite positive sizing target. It expresses desired pre-cost notional exposure relative to `sizing_equity` for a new entry.
- `sizing_equity`: chosen design basis for Main/Karl review is current realized available equity at the entry fill point, after any required close and exit costs on the same bar, after funding cashflows already due through that bar, and before new entry fee/slippage costs.
- `entry_reference_price`: chosen design basis for Main/Karl review is the next-bar open fill price used by the current execution model, before fee/slippage costs.
- `quantity`: absolute contract/unit size for the new position. Direction remains represented separately as `+1` long or `-1` short.

Formula:

```text
quantity = target_leverage * sizing_equity / entry_reference_price
```

Rounding posture:

- Future v1 should not add rounding by default because current `order_size` behavior is float-based and optional exchange constraints are disclosure-only.
- If lot-size rounding or min-notional enforcement is desired later, it should be a separate explicitly authorized package because it can change fills, rejection behavior, and identity.

Max/min quantity behavior:

- No implicit min quantity in the core v1 design.
- Optional max leverage cap may fail closed before entry when target leverage exceeds the cap.
- Existing `liquidity_cap_fraction` capacity behavior should continue to apply to the computed quantity if that cap is provided.
- Non-finite, zero, or negative computed quantity is invalid.

Invalid/non-finite handling:

- `target_leverage`, `sizing_equity`, and `entry_reference_price` must be finite.
- `target_leverage` and `entry_reference_price` must be positive.
- If `sizing_equity <= 0`, the future implementation must not open a new position. Under current zero-equity semantics, this should align with terminal zero-equity handling rather than creating a zero or negative quantity.
- Any ambiguous state where a nonpositive equity basis is reached without liquidation should fail closed and be reviewed.

Long and short symmetry:

- The quantity formula is identical for long and short entries.
- Direction changes only the sign of PnL, funding cashflow, and position state.
- No side-specific leverage multiplier is part of this design.

No lookahead:

- Sizing may use only state and prices available through the entry fill event.
- Sizing must not use the bar close after the entry fill, later highs/lows, later funding events, or final equity.

## Equity basis

Evaluated bases:

| Basis | Benefit | Risk / limitation |
|---|---|---|
| Starting equity only | Simple and stable | Recreates fixed-size drift after price/equity changes |
| Current realized equity before trade | Deterministic, available at entry, avoids using still-open unrealized PnL for a new position | Does not compound unrealized PnL until a position is closed |
| Current marked equity including unrealized PnL | Tracks account value more continuously | Can blur timing when sizing a flip and may require careful no-lookahead treatment |
| Current cash/equity after fees | Conservative after costs | Circular if entry fee depends on the quantity being computed |

Chosen design basis for Main/Karl review:

```text
sizing_equity = current realized available equity at entry, after any required close and exit costs on the same fill bar, after funding due through that bar, and before new entry fee/slippage costs
```

Rationale:

- Deterministic under the current bar loop.
- Uses only state available at the entry event.
- Lets closed-trade gains and losses resize the next entry.
- Avoids circular dependency between entry fees and quantity.
- Avoids using an unrealized mark after the entry fill as the basis for that same entry.

Behavior after zero-equity/liquidation:

- Once current liquidation logic floors equity at zero and terminates the run, dynamic sizing has no further entries to size.
- If a future implementation observes `sizing_equity <= 0` before a new entry outside that existing terminal path, it must fail closed or route into the existing liquidation/zero-equity behavior rather than place a trade.

## Entry reference price basis

Evaluated bases:

| Basis | Benefit | Risk / limitation |
|---|---|---|
| Signal bar close | Known at signal time | Not the current execution fill basis and can drift across the next-open gap |
| Next bar open | Matches current `next_bar_open` fill timing | Requires sizing inside the fill branch, not runner pre-resolution |
| Execution fill price after slippage | Could represent effective cost if slippage becomes price-based | Current slippage is modeled as a separate bps cost, not a fill-price adjustment |
| Pre-slippage entry price | Matches current PnL/funding/cost notional basis | Entry fees/slippage reduce equity after sizing, so realized post-cost leverage may differ slightly |

Chosen design basis for Main/Karl review:

```text
entry_reference_price = next bar open fill price before fee/slippage costs
```

Rationale:

- It matches the current execution model: signal at bar `t`, fill at open of bar `t+1`.
- It avoids signal-close lookahead or stale-reference drift.
- It uses the same price currently used for PnL entry price, fee notional, slippage notional, and entry notional.
- It preserves the current fee/slippage model as costs rather than modifying fill price.

## Leverage-cap behavior

Future dynamic mode should enforce:

- `target_leverage` must be finite and positive.
- Optional `max_leverage_cap`, if introduced, must be finite and positive.
- If both are supplied, `target_leverage <= max_leverage_cap`; otherwise fail closed.
- Silent leverage clipping is not part of the v1 design because it can hide the scientific identity of a run.

For simple `dynamic_equity_target_leverage`, a separate max cap is partly redundant because the target itself sets pre-cost notional. It still may be useful as a fail-closed guard when target leverage comes from layered configuration in a later runner or artifact surface.

The mode prevents long-run fixed-size drift by recomputing quantity at each new entry from current available equity and current entry reference price. Large price gaps between signal bar close and next open are handled by using the next open as the sizing reference, not the prior close.

Entry fees and slippage occur after the quantity is computed under this design, so realized post-entry leverage can differ slightly from the pre-cost target. That is a cost-model disclosure issue, not a reason to change cost mechanics inside 02a.

## Cost model interaction

Dynamic sizing changes the quantity input to existing cost calculations; it does not change the cost model.

- Taker/maker fees remain bps of `price * quantity` for the costed side.
- Slippage remains bps of `price * quantity`.
- Funding notional mode remains one of the existing assumptions:
  - `entry_price`: funding notional is based on entry fill price times quantity.
  - `mark_price`: funding notional is based on current close/mark price times quantity.
- Cost-to-equity reporting should identify whether ratios use starting equity, average equity, or current equity. This design does not add those fields.
- Zero-equity outcomes remain governed by existing liquidation logic.

Future validation should prove that changing quantity dynamically scales fees, slippage, and funding notional deterministically without changing bps formulas.

## Liquidation / margin interaction

Dynamic sizing must not change liquidation logic in the future core sizing package unless that package explicitly scopes liquidation changes.

Existing interactions:

- `liquidation_mode="zero_equity"` floors equity at zero when marked equity is nonpositive and terminates the run.
- `liquidation_mode="maintenance_margin"` compares marked equity with `abs(mark_price * order_size) * maintenance_margin_rate` today.
- Drawdown and return calculations consume the resulting equity curve.

Future dynamic mode impact:

- The maintenance-margin notional should use the current open position quantity, not a stale fixed `order_size`.
- Zero-equity behavior remains a terminal outcome.
- Drawdown and return calculations should continue to consume the equity curve without knowing the sizing mode.

If dynamic sizing exposes a need for richer liquidation/margin semantics, that should be a separate future package. This design does not authorize it.

## Determinism and no-lookahead requirements

Future implementation must preserve:

- Same input artifacts plus same parameters produce identical quantities, trades, costs, and equity curve.
- Quantity is calculated only inside deterministic entry events.
- No use of later bar close/high/low, future funding events, final equity, or result metrics in sizing.
- Irreparable-gap behavior remains deterministic and carries trade state forward as current code defines.
- Same default fixed mode produces byte-for-byte or numerically identical fixture outputs where current tests require it.

## Exact protected-path scope surfaced from lib/backtest.py

Read-only inspection of current `lib/backtest.py` surfaces these likely future 02b regions:

| file | function / region | current role | future change type | risk | why needed | default-preservation requirement | test coverage needed |
|---|---|---|---|---|---|---|---|
| `lib/backtest.py` | `BacktestResult` dataclass | Carries equity curve, trades, costs, params, and liquidation flags | Probably unchanged for core v1; may need optional params/trade metadata only if scoped | Result contract drift | Dynamic mode can likely reuse existing fields if trade row `size` varies | Fixed mode dataclass shape and field meanings unchanged | Result shape regression |
| `lib/backtest.py` | `_bps_cost(price, size, bps)` | Computes fee/slippage cost from price and size | Use computed entry quantity instead of fixed `order_size` at call sites | Cost scaling regression | Dynamic sizing changes size, not bps formula | Fixed mode calls still pass fixed `order_size` | Fee/slippage interaction tests |
| `lib/backtest.py` | `_funding_notional(..., order_size)` | Computes funding notional from entry or mark price and fixed size | Rename/generalize size argument or pass current position quantity | Funding notional regression | Funding must reflect dynamic position quantity | Fixed mode funding totals identical | Funding mode tests |
| `lib/backtest.py` | `_validate_fill_size_assumptions(...)` | Validates positive fixed `order_size`, fill mode, liquidity cap, slippage model | Add `sizing_mode` validation and dynamic-mode parameter validation while retaining fixed validation | Backward compatibility | Future mode needs fail-closed target leverage/reference/equity handling | Omitted `sizing_mode` follows fixed validation exactly | Invalid sizing mode/leverage tests |
| `lib/backtest.py` | `_check_liquidity_capacity(...)` | Fails if fixed `order_size` exceeds volume capacity | Check computed quantity per attempted fill | Fill rejection semantics | Dynamic quantity can differ per entry | Fixed mode capacity behavior unchanged | Dynamic capacity tests if cap is in scope |
| `lib/backtest.py` | `run_backtest(...)` signature/docstring | Accepts fixed `order_size=1.0` and assumptions | Add optional `sizing_mode`, `target_leverage`, maybe `max_leverage_cap`; keep defaults fixed | Public API drift | Entry quantity must be computed inside core for dynamic mode | Existing callers with no new args produce identical results | Default-preservation tests |
| `lib/backtest.py` | bar loop state variables (`equity`, `position`, `entry_fill_price`) | Tracks realized equity/cash-like state, direction, and entry fill | Add current position quantity state separate from direction | High semantic risk | Fixed `order_size` is currently global; dynamic mode needs per-position quantity | Fixed mode initializes quantity to `order_size` and behaves identically | Long/short and flip tests |
| `lib/backtest.py` | funding cashflow block | Applies funding to open positions using fixed `order_size` | Use current open quantity | Funding/cashflow risk | Dynamic positions must fund on actual notional | Fixed mode unchanged | Funding notional tests |
| `lib/backtest.py` | close-position branch | Computes realized PnL, exit fees/slippage, trade row notional using fixed `order_size` | Use current open quantity for close calculations | PnL/trade-row risk | Exit must close the quantity opened at entry | Fixed mode row values identical | Round-trip PnL tests |
| `lib/backtest.py` | open-position branch | Charges entry costs and sets position using fixed `order_size` | Compute dynamic quantity from chosen equity and reference price before entry cost | Core sizing risk | This is the main dynamic sizing insertion point | Fixed mode continues using fixed `order_size` | Formula, no-lookahead, invalid basis tests |
| `lib/backtest.py` | unrealized PnL recomputation | Marks open PnL as direction times price change times fixed `order_size` | Use current open quantity | Equity curve risk | Dynamic quantity affects marked equity until exit | Fixed mode equity curve identical | Equity curve deterministic tests |
| `lib/backtest.py` | liquidation / maintenance-margin block | Checks marked equity and maintenance margin using fixed `order_size` | Use current open quantity for notional and liquidation price math | Liquidation regression risk | Dynamic position notional must drive margin approximation | Fixed mode liquidation behavior identical | Zero-equity and maintenance-margin tests |
| `lib/backtest.py` | final unrealized block | Computes final unrealized PnL with fixed `order_size` | Use current open quantity | Terminal metric risk | Open dynamic position at end must be marked correctly | Fixed mode unchanged | Open-at-end tests |
| `lib/backtest.py` | `trades_df` rows and empty columns | Records `size`, entry/exit notional, gross/net PnL | Continue recording actual per-trade quantity in `size` | Reporting compatibility | Evaluation already consumes notional columns | Fixed mode rows identical | Trade-row schema tests |
| `lib/backtest.py` | `params_snapshot` | Records run assumptions including `order_size` | Add dynamic sizing params only if 02b scopes result params; otherwise preserve fixed params | Identity/reporting risk | Future outputs need visible sizing context | Fixed mode params unchanged | Params snapshot regression |

## Evaluation/reporting interaction

Read-only inspection of `lib/evaluation.py` indicates future 02b core dynamic sizing likely does not require evaluation-code changes if `BacktestResult` keeps the existing equity curve, cost totals, and trade-row notional fields:

- `turnover()` consumes `trades_df["notional"]` when present, then entry/exit notional fallback, then a legacy one-contract fallback.
- `cost_drag()` consumes aggregate fees, slippage, funding, realized PnL, and unrealized PnL.
- Sharpe, drawdown, return-window, and gate calculations consume the equity curve and per-bar PnL.

Classification for 02b:

```text
lib/evaluation.py impact: not required for the core dynamic sizing implementation if existing BacktestResult and trade notional fields remain semantically valid.
```

Future evaluation/reporting work may be needed in a separate package if Main/Karl want new sizing-specific metrics such as average leverage, max leverage, exposure-to-equity, or structured sizing identity display. This is not required to compute dynamic quantities in the backtest core.

## Result-population identity and pipeline-versioning posture

Future dynamic-sizing outputs must carry explicit sizing identity. At minimum, identity-bearing context should include:

- `sizing_mode`;
- `target_leverage`;
- chosen equity basis;
- chosen entry reference price basis;
- max leverage cap if provided;
- any future rounding or quantity constraint behavior if later authorized.

Old result-population schema currently supports assumption-string disclosure through `backtest_assumption_summary.order_size_assumption`, and identity hash scope includes `backtest_assumption_summary`. Structured fields require a separate schema/validator package.

Required language:

```text
RP-2134, RP-4492, and RP-6688 remain valid under their recorded fixed-sizing model. They are not migrated or reinterpreted. Any future dynamic-sizing run must produce a new result population with explicit sizing model identity.
```

Canonical reruns remain Karl-gated. This design does not authorize a rerun.

## Backward compatibility / prior RP reproducibility

Existing fixed-order-size result populations remain reproducible under their recorded assumptions. A future implementation must not make old callers opt into dynamic behavior implicitly.

Compatibility requirements:

- `fixed_order_size` remains default.
- `order_size=1.0` default remains current behavior unless a caller explicitly changes it.
- Prior fixed-size assumption strings are not rewritten.
- Old identity hashes remain historical facts.
- Future dynamic output uses new artifacts and new identity hashes.

## Validation plan for future implementation

Future 02b validation should include:

- Unit tests for fixed default preservation.
- Unit tests for dynamic quantity formula.
- Long and short symmetry tests.
- Invalid target leverage tests.
- Invalid equity/reference price tests.
- No-lookahead tests.
- Fee/slippage/funding interaction tests.
- Zero-equity/liquidation interaction tests.
- Determinism tests.
- Focused backtest tests.
- Runner integration tests if runner exposes the mode.
- `python -m tools.registry.validate_result_populations`.
- `python -m tools.research_query.run --list-views`.
- All discovered `v_integrity_*` views clean / zero rows.
- Full pytest for code-touching packages.
- No RP mutation proof.

Default-preservation evidence must compare current fixed-mode results before and after the change.

## Proposed code-package split for review

This split is proposed for Main/Karl review only. It is not authorization.

Future `WP-REALISM-SIZING-02b` - core dynamic sizing implementation:

- Possible scope: `lib/backtest.py` and focused backtest-core sizing tests.
- No runner integration unless explicitly authorized.
- No canonical result population.

Future `WP-REALISM-SIZING-02c` - runner exposure / integration:

- Possible scope: runner option/config and tests.
- No canonical result population.

Future `WP-REALISM-SIZING-02d` - sizing metadata schema / validator:

- Possible scope: result-population schema, validator, query/reporting tests.
- No canonical result population unless separately authorized.

Future canonical rerun package:

- Possible scope: new result population under dynamic sizing.
- Karl-gated.
- No candidate registration, ranking, readiness, promotion, or trading authority.

## Stop conditions for 02b

Stop a future 02b package if:

- Fixed default preservation cannot be proven.
- Dynamic sizing requires schema, validator, runner, or result-population changes not scoped in 02b.
- `lib/evaluation.py` changes become materially required but are not authorized.
- Sizing equity basis conflicts with current liquidation or cash/equity accounting.
- Entry reference price cannot be defined without lookahead.
- Zero-equity or maintenance-margin behavior becomes ambiguous.
- Prior result-population reproducibility would be broken.
- Any implementation would require runtime, paper/live, OMS/risk, broker/exchange, or protected execution-path changes.

## What this package does not authorize

This package does not authorize:

- `WP-REALISM-SIZING-02b` implementation.
- Any `lib/backtest.py` edit.
- Any `lib/evaluation.py` edit.
- Runner exposure.
- Schema, validator, query, dashboard, or test changes.
- Strategy Spec, variant manifest, sweep-plan, data, or result-population mutation.
- Canonical reruns.
- Candidate registration.
- Ranking, readiness, promotion, or trading.
- Paper/live/runtime, OMS/risk, broker/exchange, safe-mode, or protected-path behavior.
