# Event Log Schema (Architecture Spec)



## Purpose

Minimaler, auditierbarer Event-Log-Contract fÃ¼r OMS/Reconcile/Safe Mode.

Dient Reproduzierbarkeit + Debug + Traceability. Keine Secrets.



## Common Fields (mandatory on every event)

- timestamp_utc (ISO-8601, e.g. 2026-03-08T18:02:00Z)

- run_id (string; constant per process run)

- correlation_id (string; links causal chain across events)

- event_id (string; unique per event)

- event_type (enum)

- decision_id (string; e.g. "D-0001" or "D-RECONCILE-0007")

- symbol (string, e.g. "BTCUSDT"; optional if global event)

- severity (INFO|WARN|ERROR)

- payload (object; event-specific; must follow redaction rules)



## Redaction Rule (must)

- payload MUST NOT contain:

   - API keys/secrets

   - auth headers

   - signed query strings

   - raw request/response bodies that may embed sensitive info

- Allowed:

   - orderId/clientOrderId (non-secret)

   - numeric quantities/prices

   - normalized error codes/messages (sanitized)



## Event Types (minimum set)

1\) STATE_TRANSITION

- payload: { from_state, to_state, trigger_event }



2\) DECISION_MADE

- payload: { decision_id, desired_position, rationale_codes\[] }



3\) ORDER_INTENT_CREATED

- payload: { intent_type: PLACE|CANCEL, clientOrderId?, order_ref?, side?, qty?, price? }



4\) ORDER_SENT

- payload: { clientOrderId, side, type, qty, price }



5\) ORDER_ACK

- payload: { clientOrderId, orderId, status }



6\) ORDER_REJECT

- payload: { clientOrderId, error_code, error_message_sanitized }



7\) CANCEL_SENT

- payload: { orderId?, clientOrderId? }



8\) CANCEL_ACK

- payload: { orderId, status }



9\) CANCEL_REJECT

- payload: { orderId?, clientOrderId?, error_code, error_message_sanitized }



10\) FILL_RECEIVED

- payload: { orderId, fill_id, qty, price, fee?, fee_asset? }



11\) POSITION_SNAPSHOT

- payload: { position_amt, entry_price?, unrealized_pnl? }



12\) RECONCILE_START

- payload: { cursor?, reason: TIMER|EVENT|MANUAL }



13\) RECONCILE_DIFF

- payload: { diffs: \[ { diff_type, details_sanitized } ] }



14\) RECONCILE_ACTION

- payload: { actions: \[ { action_type, target_ref, parameters } ] }



15\) RECONCILE_DONE

- payload: { ok: true|false, error_summary? }



16\) SAFE_MODE_TRIGGERED

- payload: { reason_code, reason_details_sanitized }



17\) SAFE_MODE_STEP

- payload: { step: "CANCEL_ALL"|"FLATTEN"|"POSTCHECK", ok, details_sanitized }



18\) SAFE_MODE_DONE

- payload: { ok: true|false, final_open_orders, final_position_amt }



19\) ERROR

- payload: { error_code?, error_message_sanitized, context }



20\) HEARTBEAT

- payload: { uptime_s, last_reconcile_ts_utc }



## Example Event (reference)

{

   "timestamp_utc": "2026-03-08T18:02:00Z",

   "run_id": "RUN-20260308-180200",

   "correlation_id": "C-9f2a",

   "event_id": "E-000123",

   "event_type": "RECONCILE_DONE",

   "decision_id": "D-RECONCILE-0007",

   "symbol": "BTCUSDT",

   "severity": "INFO",

   "payload": { "ok": true }

}


