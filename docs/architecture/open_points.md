# OPEN POINTS (Architecture)



Only real uncertainties / decisions. No new scope.



OP-01: Safe flatten order type policy

- Question: Use MARKET orders in emergency flatten, or only aggressive LIMIT with timeout + fallback?

- Decides by: risk tolerance for slippage vs risk of remaining exposed; exchange constraints; post-check reliability.

- Needed input: preferred emergency policy from Main Chat; any compliance constraints.



OP-02: Reconcile cadence and retry budgets

- Question: TIMER_TICK interval, retry counts, backoff schedule for cancel/reconcile failures.

- Decides by: rate limit thresholds, latency tolerance, operational stability targets.

- Needed input: acceptable max time-to-safety for flatten; acceptable API call budget.



OP-03: AdoptUnknown policy (default vs optional override)

- Default: CancelUnknown for ExchangeUnknownOrder (as defined in reconciliation_loop.md).

- Open decision: Do we ever allow AdoptUnknown (ONLY if external/manual trading on the same account is permitted)?

- Decides by: operational discipline (single controller vs mixed usage), risk tolerance for orphan exposure.

- Needed input: confirm policy "no external trading on same account" (yes/no).



OP-04: Correlation/Decision ID generation standard

- Question: format + uniqueness constraints for correlation_id, decision_id, clientOrderId scheme.

- Decides by: log analysis needs, cross-run traceability, idempotency.

- Needed input: naming conventions already used elsewhere in repo (if any).



OP-05: Persistence layer for OMS state (interface only)

- Question: in-memory only for Phase-0? file-based? sqlite?

- Decides by: restart recovery requirement and audit trail.

- Needed input: Phase-0 vs Phase-1 requirement on restart safety.



OP-06: Data source for fills/positions (polling vs stream)

- Question: rely on REST polling only for now, or plan for user data stream later?

- Decides by: timeliness needs for reconciliation and fill gap handling.

- Needed input: allowed complexity level for Phase-1.



OP-07: Hedge mode support scope

- Question: Must we support hedge mode fully (positionSide) or enforce one-way mode as precondition?

- Decides by: account configuration control + operational simplicity.

- Needed input: team choice: enforce one-way vs support both.



OP-08: Market snapshot requirement vs price-only fallback

- Default: quote-aware execution requires best bid/ask (bookTicker). If unavailable -> no new orders (wait/reconcile).

- Open decision: allow price-only fallback (e.g., last price) for limit placement vs freeze.

- Decides by: operational reliability of market data feed vs risk of trading blind on stale/insufficient data.

- Needed input: Phase-1 paper rule: "bookTicker required" (hard precondition) vs "fallback allowed" (guarded).


