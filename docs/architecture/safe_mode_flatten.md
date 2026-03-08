# Safe Mode + Flatten (Architecture Spec)



## Purpose

Ein deterministischer Notfallpfad zur Risikoreduktion:

- Keine neuen risk-increasing orders

- Cancel all

- Flatten position to 0

- Post-check: open_orders=0 AND position=0

- Danach: Freeze/Reset



## Entry Triggers (complete)

T1 Manual trigger (operator)

T2 Reconcile failure (RECONCILE_DONE_FAIL)

T3 Unexplained PositionDrift beyond tolerance

T4 Unknown live order risk (InternalUnknownOrderStatus unresolved)

T5 CancelFailure beyond retry budget

T6 Any safety invariant breach (I3/I5/I6)



## Safe Mode States (within OMS)

- SAFE_FLATTENING: actively cancel/flatten

- FROZEN: no trading; requires operator RESET



## Flatten Procedure (deterministic steps)

Step F0: Emit SAFE_MODE_TRIGGERED event (include reason_code, last decision_id)

Step F1: Freeze new intents

- Action: ignore DESIRED_UPDATE for execution (but still log them) until RESET.

Step F2: Cancel all open orders (symbol scope)

- Action: cancel open orders (by orderId where known; otherwise cancel-all endpoint if available)

- Retry: bounded retries with backoff; if exceeded -> FROZEN

Step F3: Post-check 1

- Condition: open_orders_count == 0

- If not 0: repeat F2 (bounded); else continue.

Step F4: Flatten position to zero

- Action options (policy chooses; must be explicit):

   A) MARKET flatten (fast, higher slippage)

   B) Aggressive LIMIT flatten with timeout + fallback to MARKET

- This spec default for emergency: B with strict timeout then A.

Step F5: Post-check 2

- Condition: position_amt == 0 AND open_orders_count == 0

- If not met: repeat F2/F4 (bounded); else continue.

Step F6: Transition to FROZEN

- Action: emit SAFE_MODE_DONE event; enter FROZEN.

Step F7: RESET workflow (operator)

- Preconditions: operator confirms stable connectivity + permissions + no open orders

- Action: run a fresh reconcile cycle; if OK -> return to WORKING/IDLE.



## PASS / FAIL Criteria for Safe Flatten

PASS:

- open_orders_count == 0

- position_amt == 0

- event log contains SAFE_MODE_TRIGGERED + SAFE_MODE_DONE with correlation_id chain

FAIL:

- unable to cancel all or flatten within retry/timeout budget

- API failures prevent verifying post-checks

FAIL implies: remain FROZEN, require manual intervention.



## Notes (no implementation)

- Exact retry budgets/timeouts are OPEN POINT unless defined elsewhere.

- Safe mode must not leak secrets in logs.


