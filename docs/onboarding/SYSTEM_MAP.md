# System Map (current)

## Runtime flow (paper)

1. Scheduler computes bar_close_time_utc (UTC, deterministic)
2. Data freshness gate
3. Signal provider -> DesiredPosition (currently flat scaffold; Phase 2 will implement real candidates)
4. Context overlay -> {ALLOW/REDUCE/BLOCK} + size_multiplier {1.0/0.5/0.0}
5. Paper broker simulates fills (deterministic) using price_ref provider
6. Ledger updates (fees/slippage, realized/unrealized)
7. Persistence writes atomic state; idempotency guard prevents duplicate bar processing
8. Structured JSONL events append-only

## Key modules (repo)

* src/runtime/ : paper_trader, scheduler
* src/signal/ : signal interface + current flat provider
* src/overlay/ : overlay evaluator v1 (bounded, deterministic, fail-open)
* src/marketdata/ : price_ref provider (parquet-based + deterministic fallback)
* src/paper/ : paper broker + position state + ledger + state store
* configs/ : runtime config(s)
* docs/architecture/ : OMS/Reconcile spec pack (locked)
* docs/decisions.md : binding decisions

## Execution-critical boundaries (do not let AI change)

* OMS state machine semantics (spec)
* Reconciliation truth rules (spec)
* Kill-switch semantics
* Hard risk caps (D-0001)
* Overlay bounds + fail-open rule
