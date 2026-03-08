# Reconciliation Loop (Architecture Spec)



## Goal

Stellt sicher, dass OMS-interner Zustand (orders, fills, position) mit Exchange-RealitÃ¤t konsistent ist.

Reconcile ist der einzige Pfad, der Unsicherheiten (unknown status, missing orders, drift) deterministisch auflÃ¶st.



## Inputs (conceptual)

- Internal snapshot: last reconciled state (orders, known fills, desired position, decision history)

- Exchange snapshot (authoritative):

   - Open orders (per symbol)

   - Position snapshot (per symbol)

   - Fills since last cursor (if available)

- Market snapshot (optional): best bid/ask, spread, tick/step/minNotional filters



## Outputs

- ReconcileSnapshot: normalized merged snapshot (internal + exchange)

- Diff classes (Î”): categorized differences

- Action plan: ordered list of actions (cancel/place/flatten/freeze/noop)

- ReconcileResult: OK/FAIL + reasons + next state recommendation



## Reconcile Phases (deterministic)

P0 Start: Emit RECONCILE_START event (decision_id can be "D-RECONCILE-XXXX")

P1 Acquire: Pull exchange open_orders + position + (fills since cursor if applicable)

P2 Normalize: Map exchange entities to canonical types (ids, clientOrderId, status)

P3 Join: Match internal orders â†” exchange orders (by orderId preferred, else clientOrderId)

P4 Diff: Compute diffs (below)

P5 Decide: Produce action plan from diffs (ordered)

P6 Apply: Execute actions (side effects live in execution layer; spec only defines ordering)

P7 Verify: Re-pull minimal post state if actions were taken (open_orders / position)

P8 Emit: RECONCILE_DONE_OK or RECONCILE_DONE_FAIL with error_summary



## Diff Classes (complete)

Î”1 DesiredDiff

- Definition: DesiredPosition changed since last reconcile OR desired not yet reflected in current working plan.

- Action: trigger execution decision (place/cancel set) -> move toward target.



Î”2 ExchangeUnknownOrder

- Definition: Exchange open order exists but OMS has no corresponding internal record (no orderId/clientOrderId match).

- Action options (must be explicit):

   A) CancelUnknown: cancel the order (default safe choice)

   B) AdoptUnknown: create internal record and continue managing (ONLY if policy explicitly allows)

- This spec default: CancelUnknown.



Î”3 InternalUnknownOrderStatus

- Definition: OMS has an order record, but exchange cannot find it by orderId/clientOrderId, and it is not definitively terminal.

- Mandatory handling:

   - Try query-by-id (if API supports) once.

   - If still unknown: treat as terminal-unknown and proceed by:

     - If risk-increasing: enter SAFE_MODE_TRIGGER OR Freeze (policy decides).

     - Else: mark as closed + continue.

- This spec default: if it could be live and risk-bearing â†’ SAFE_MODE_TRIGGER.



Î”4 OrderMismatch

- Definition: Matched order differs in critical fields (price/qty/side/type) vs OMS record.

- Action: prefer cancel+replace to restore invariants (amend is optional, only if explicitly supported later).



Î”5 PositionDrift

- Definition: Exchange position_amt != OMS expected position after considering known fills.

- Action:

   - If within tolerance and explainable by fills lag: reconcile by updating internal.

   - If unexplained or beyond tolerance: SAFE_MODE_TRIGGER (default) or FROZEN.



Î”6 FillGap

- Definition: New fills observed on exchange not present internally (or missing fill details).

- Action: ingest fills, update internal position calc, update order statuses, then re-run diffs if needed.



Î”7 FiltersChanged

- Definition: Exchange filters snapshot (tick/step/minNotional/precision) differs from what order planner assumed.

- Action: re-plan orders using current filters; do not submit invalid orders.



Î”8 CancelFailure

- Definition: cancel rejected repeatedly or returns unknown status.

- Action: escalate:

   - retry with backoff (bounded)

   - if still failing: SAFE_MODE_TRIGGER (default) or FROZEN.



Î”9 RateLimit/TransportFailure

- Definition: acquire/apply phases fail due to network/rate limit.

- Action: bounded retry; if exceeded -> RECONCILE_DONE_FAIL -> FROZEN.



## Unknown Order Status (explicit policy)

Unknown statuses are never ignored.

Resolution order (must be followed):

1\) Identify: match by orderId first; fallback to clientOrderId.

2\) Query: if still unknown, attempt direct query once.

3\) Decide:

    - If exchange says not found AND OMS thinks it might still be live -> SAFE_MODE_TRIGGER.

    - If exchange confirms terminal -> update internal terminal status.

4\) Verify: after any cancel/flatten, re-check open_orders and position.



## Action Ordering (complete, deterministic)

When multiple actions exist, apply in this order:

1\) Cancel actions (risk reduction first)

2\) Flatten actions (if safe mode triggered)

3\) Place/replace actions (only if not in safe/frozen)

4\) Post-check (open_orders/position)

5\) Persist state + emit events



## ReconcileResult statuses

- OK: all invariants hold; unknowns resolved; post-check ok.

- FAIL: cannot guarantee invariants (unknown live risk, persistent errors, drift).

FAIL implies next state recommendation: FROZEN (default) or SAFE_FLATTENING if risk requires.




