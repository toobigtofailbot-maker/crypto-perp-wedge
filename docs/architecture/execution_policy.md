# Execution Policy (Architecture Spec)



## Boundary: Strategy vs Execution

- Strategy responsibility:

   - Produce `DesiredPosition` only (target exposure per symbol).

   - No direct order logic, no exchange awareness required.

- Execution responsibility:

   - Transform `DesiredPosition` + reconciled snapshot into `OrderIntents`.

   - Enforce filters (tick/step/minNotional), risk constraints, and safe-mode rules.

   - Own the interaction with OMS state machine + reconcile loop.



## Inputs to ExecutionDecision (conceptual)

- DesiredPosition (target_qty or target_notional, decision_id, timestamp_utc)

- Current reconciled position (position_amt)

- Current working orders (open orders snapshot)

- Filters snapshot (tick, step, minNotional, precision)

- Market snapshot (optional): best bid/ask + spread



## Output of Execution: OrderIntents

- PlaceIntent: order parameters (side/type/qty/price) + clientOrderId + decision_id

- CancelIntent: reference to existing orderId/clientOrderId + decision_id



## Default Execution Policy (non-emergency)

P-DEF-1: Validity gating

- Never submit an order that violates filters snapshot.

- If filters missing/invalid: refuse to trade -> trigger reconcile or freeze (policy decides; default: reconcile then freeze if unresolved).



P-DEF-2: Risk gating

- No new risk-increasing orders in SAFE_FLATTENING or FROZEN.

- If desired requires increasing exposure, but risk gates fail -> no-op + log decision.



P-DEF-3: Market data precondition (Phase-1 Paper)

- For quote-aware execution (spread gating / passive limit placement), a best-bid/ask snapshot (e.g., bookTicker feed) is required.

- If market snapshot is unavailable:

   - Default behavior: do not place new orders; rely on reconcile + wait.

   - This is a deliberate precondition (see OPEN POINT OP-08 for allowing a price-only fallback).

P-DEF-4: Cancellation rules

- Cancel orders that are opposite-side to new desired delta.

- Cancel orders with mismatched price/qty beyond tolerance (replace).



## Emergency Policy (invoked by Safe Mode Trigger)

P-EM-1: Enter SAFE_FLATTENING

- Cancel-all then flatten to zero (see safe_mode_flatten.md).

- After SAFE_MODE_DONE -> FROZEN until operator RESET.



## Paper/Live-taugliche Constraints

- All decisions must be traceable via decision_id.

- Event log must allow post-mortem: why an order was placed/canceled.

- No reliance on strategy for exchange correctness; execution enforces filters and safety.



## Out of scope

- Alpha/strategy definition, portfolio allocation

- Multi-venue routing

- Monitoring stack expansion (nur log contracts)


