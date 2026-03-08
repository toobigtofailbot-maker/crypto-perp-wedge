# OMS State Machine (Architecture Spec)



## Scope / Boundary

- Venue: Single-venue, single-account (Binance USD-M Futures) â€” OMS bleibt venue-agnostisch im Interface, aber Spec ist fÃ¼r 1 Venue ausgelegt.

- Input: Strategy liefert ausschlieÃŸlich `DesiredPosition` (target exposure).

- Output: Execution erzeugt/verwaltet Orders, Cancels, Safe/Flatten.

- No implementation details (kein Code, keine API calls).



## Core Entities (conceptual)

- DesiredPosition: Zielposition je Symbol (z.B. BTCUSDT), inkl. timestamp + decision_id.

- WorkingOrders: Menge aktueller OMS-Orders (intents + exchange identifiers).

- Fills: AusfÃ¼hrungen (Execution reports).

- PositionSnapshot: Exchange-seitige Position (authoritative after reconcile).

- ReconciledPosition: OMS-interner Zustand nach Abgleich (Position + Orders konsistent).



## States

S0 INIT

S1 IDLE

S2 PLANNING

S3 SUBMITTING

S4 WORKING

S5 RECONCILING

S6 SAFE_FLATTENING

S7 FROZEN

S8 ERROR_TERMINAL (optional; nur wenn Recovery nicht mÃ¶glich/gewollt)



## Events (canonical)

E1 START

E2 DESIRED_UPDATE (new DesiredPosition)

E3 TIMER_TICK (periodic reconcile tick)

E4 MARKET_DATA (best bid/ask / spread snapshot; optional input)

E5 ORDER_ACK (accepted/working)

E6 ORDER_REJECT

E7 CANCEL_ACK

E8 CANCEL_REJECT

E9 FILL

E10 RECONCILE_DONE_OK

E11 RECONCILE_DONE_FAIL

E12 SAFE_MODE_TRIGGER (manual or automatic)

E13 SAFE_MODE_CLEARED (operator clears)

E14 RESET (operator resets frozen/safe after checks)

E15 SHUTDOWN



## Actions (canonical)

A1 Load/Init state (load persisted snapshot, set run_id)

A2 Compute ExecutionDecision from DesiredPosition + reconciled snapshot

A3 Emit OrderIntents (place/cancel list) â€” decision_id assigned

A4 Submit place/cancel to exchange (side-effects in execution layer)

A5 Update local OMS store with acks/rejects

A6 Trigger reconcile cycle (pull open orders + positions + fills since last)

A7 Enter Safe Mode (freeze new intents, begin flatten)

A8 Perform Safe Flatten step (cancel-all, then flatten position, then post-check)

A9 Freeze (FROZEN; require operator RESET)

A10 Log event / state transition (event log contract)

A11 Ignore (NOOP) but log unexpected event

A12 Shutdown cleanly (stop timers, persist, no new actions)



## Invariants (must hold)

I1 No secret leakage: logs/events never contain API keys, headers, or raw signed payloads.

I2 Single source of truth after reconcile: `PositionSnapshot` + `OpenOrders` from exchange override local uncertainty.

I3 No orphan activity: Any exchange open order that is not represented in OMS store must be explicitly handled (cancel or adopt) during reconcile.

I4 Idempotency: cancel-all and cancel by id/clientOrderId must be safe to retry.

I5 Safe mode dominance: In SAFE_FLATTENING/FROZEN no new risk-increasing orders are allowed.

I6 Post-flatten guarantee: end of SAFE_FLATTENING implies `open_orders == 0` AND `position == 0` (per symbol scope).

I7 Decision traceability: every order intent and resulting exchange order is linked to `decision_id`.



## State Ã— Event â†’ Action / NextState (Decision Table)

Rule format: (State, Event) -> Actions; NextState



### S0 INIT

- (S0, E1 START) -> A1, A10; S1 IDLE

- (S0, E15 SHUTDOWN) -> A12, A10; S8 ERROR_TERMINAL

- (S0, E12 SAFE_MODE_TRIGGER) -> A7, A10; S6 SAFE_FLATTENING

- (S0, ELSE) -> A11, A10; S0 INIT



### S1 IDLE

- (S1, E2 DESIRED_UPDATE) -> A2, A3, A10; S3 SUBMITTING

- (S1, E3 TIMER_TICK) -> A6, A10; S5 RECONCILING

- (S1, E12 SAFE_MODE_TRIGGER) -> A7, A10; S6 SAFE_FLATTENING

- (S1, E15 SHUTDOWN) -> A12, A10; S8 ERROR_TERMINAL

- (S1, ELSE) -> A11, A10; S1 IDLE



### S2 PLANNING (optional; wenn getrennt von IDLE genutzt)

- (S2, E2 DESIRED_UPDATE) -> A2, A3, A10; S3 SUBMITTING

- (S2, E12 SAFE_MODE_TRIGGER) -> A7, A10; S6 SAFE_FLATTENING

- (S2, E15 SHUTDOWN) -> A12, A10; S8 ERROR_TERMINAL

- (S2, ELSE) -> A11, A10; S2 PLANNING



### S3 SUBMITTING

- (S3, E5 ORDER_ACK) -> A5, A10; S4 WORKING

- (S3, E6 ORDER_REJECT) -> A5, A6, A10; S5 RECONCILING

- (S3, E7 CANCEL_ACK) -> A5, A10; S3 SUBMITTING

- (S3, E8 CANCEL_REJECT) -> A5, A6, A10; S5 RECONCILING

- (S3, E9 FILL) -> A5, A10; S3 SUBMITTING

- (S3, E3 TIMER_TICK) -> A6, A10; S5 RECONCILING

- (S3, E12 SAFE_MODE_TRIGGER) -> A7, A10; S6 SAFE_FLATTENING

- (S3, E15 SHUTDOWN) -> A12, A10; S8 ERROR_TERMINAL

- (S3, ELSE) -> A11, A10; S3 SUBMITTING



### S4 WORKING

- (S4, E9 FILL) -> A5, A10; S4 WORKING

- (S4, E2 DESIRED_UPDATE) -> A2, A3, A10; S3 SUBMITTING

- (S4, E3 TIMER_TICK) -> A6, A10; S5 RECONCILING

- (S4, E6 ORDER_REJECT) -> A5, A6, A10; S5 RECONCILING

- (S4, E8 CANCEL_REJECT) -> A5, A6, A10; S5 RECONCILING

- (S4, E12 SAFE_MODE_TRIGGER) -> A7, A10; S6 SAFE_FLATTENING

- (S4, E15 SHUTDOWN) -> A12, A10; S8 ERROR_TERMINAL

- (S4, ELSE) -> A11, A10; S4 WORKING



### S5 RECONCILING

- (S5, E10 RECONCILE_DONE_OK) -> A10; NextState determined by post-state:

   - If open_orders_count == 0 AND desired_position == 0 -> S1 IDLE

   - Else -> S4 WORKING

- (S5, E11 RECONCILE_DONE_FAIL) -> A9, A10; S7 FROZEN

- (S5, E12 SAFE_MODE_TRIGGER) -> A7, A10; S6 SAFE_FLATTENING

- (S5, E15 SHUTDOWN) -> A12, A10; S8 ERROR_TERMINAL

- (S5, ELSE) -> A11, A10; S5 RECONCILING



### S6 SAFE_FLATTENING

- (S6, E3 TIMER_TICK) -> A8, A10; S6 SAFE_FLATTENING

- (S6, E9 FILL) -> A5, A10; S6 SAFE_FLATTENING

- (S6, E13 SAFE_MODE_CLEARED) -> A9, A10; S7 FROZEN

- (S6, E14 RESET) -> A6, A10; S5 RECONCILING

- (S6, E15 SHUTDOWN) -> A12, A10; S8 ERROR_TERMINAL

- (S6, ELSE) -> A11, A10; S6 SAFE_FLATTENING



### S7 FROZEN

- (S7, E14 RESET) -> A6, A10; S5 RECONCILING

- (S7, E12 SAFE_MODE_TRIGGER) -> A7, A10; S6 SAFE_FLATTENING

- (S7, E15 SHUTDOWN) -> A12, A10; S8 ERROR_TERMINAL

- (S7, ELSE) -> A11, A10; S7 FROZEN



### S8 ERROR_TERMINAL

- (S8, ANY_EVENT) -> A11, A10; S8 ERROR_TERMINAL


