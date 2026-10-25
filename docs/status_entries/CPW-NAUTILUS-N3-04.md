# CPW-NAUTILUS-N3-04 — offline native execution-engine reconciliation proof

Karl's full authorization: “I approve everything so please proceed and always include my full authorization”

T2, synthetic offline evidence only. Lane B branch
`claude/cpw-nautilus-n3-04-native-engine-apply-01` starts at refreshed main
`fb1de82a964c345baa7602c76f5c5ed877790a85` (contains #756 N3-03). Only open PR
was Lane A #757 (Hermes files only); no shared file or interface.

Changed: two new files (harness, focused tests), this fragment, and a narrow
compatibility edit to the N3-03 harness: `safety_boundary(allow=...)` admits
exactly `LiveExecutionEngine` (no subclass; default still refuses it), the
native run can hand back its raw `ExecutionMassStatus`/instrument/account
objects, and engine reconciliation methods were added to the trace set. N3-03's
semantic receipt is byte-identical (`5c38389f…`). No dependency, lock, CI,
protected src/lib/configs/OMS/risk/reconciliation/safe-mode path or
project_status change; no public export or production consumer.

## Physical behavior

Pinned image as N3-03 (CPython 3.12.10, NautilusTrader 1.231.0, PyArrow
25.0.1). `live/execution_engine.py` SHA-256 `7482c888…a81d` is checked at
runtime. A real `LiveExecutionEngine` (default `LiveExecEngineConfig`:
reconciliation on, external orders kept, `generate_missing_orders` on) is built
with a disposable `Cache`/`Portfolio`/`MessageBus`/`TestClock`, the native
instrument and account state. No TradingNode, Trader, strategy, RiskEngine,
client or command. Reports go in through the engine-bound
`ExecEngine.reconcile_execution_mass_status` endpoint, as the native client
sends them; upstream call counts prove each send ran the engine method.

- **Gate first.** A proof-only admission check on the N3-03 witness admits only
  complete snapshots whose anomalies are venue drift (`clean_flat`, `active`,
  `reconnect_gap`, `external_order`). The other 14 scenarios are refused with
  their own reason codes. Each refused report is offered to the populated
  `active` engine through the same gate and leaves its state identical. A
  per-route venue-time watermark refuses `REPORT_OLDER_THAN_APPLIED_STATE`.
- **Ordinary.** `active`: 101 FILLED (501 0.004 MAKER 0.048, 502 0.006 TAKER
  0.180 USDT), 202 ACCEPTED, LONG 0.010 @ 60000, realized −0.228 USDT, venue
  index maps 101/202 to their client ids. A fresh identical native report adds
  zero events.
- **Reconnect.** Startup partial (501), then the transport reconnect report adds
  502 once and cancels 202; the second reconnect and a fresh native replay add
  nothing. Replay's older startup report is refused by the watermark.
- **External order.** In a cold cache the engine marks every venue order
  `EXTERNAL`/`VENUE`, held or not, and caches 303 as ACCEPTED. CPW still reports
  `UNKNOWN_EXTERNAL_OPEN_ORDER`; cache presence is never adoptable.
- **Hazard probes** (separate disposable state, `NON_AUTHORITATIVE_HAZARD_OBSERVATION`):
  `missing_fill` → inferred fill plus a partial-window synthetic BUY plus a
  position-diff SELL (three zero-fee `NO_LIQUIDITY_SIDE` fills, realized −0.048
  vs venue −0.228); swallowed-429 `rate_limited` → one inferred 0.010 zero-fee
  fill; `duplicate_trade` → synthetic fills; `filter_unclaimed_external_orders`
  drops held orders too and books one synthetic 0.010 fill; re-delivering an
  older report after newer state fabricates a SELL 0.006 and leaves the engine
  at 0.004 against a venue 0.010.
- Every result keeps `RECONCILIATION_REQUIRED / NO_NEW_ORDERS / NO_RESUME /
  NOT_PAPER_OR_LIVE_READY`. The public entry returns `None`; nothing here is a
  CPW clearance.

## Validation and limits

Focused N3-04 + N3-03: 35 passed. Two fresh CLI processes under the Linux
seccomp socket filter produce byte-identical `semantic.json`; engine-made random
ids are tokenised, raw values in provenance. Adjacent N3-01 + N3-02: 95 passed;
N2-04 + N2-05: 44 passed. N2 sandbox/restart: environment-blocked (image lacks
`colorama`), unchanged and not importing changed code. Full pytest/release:
NOT RUN — scoped T2.

Not proved: credentialed demo/testnet contact; engine behaviour with a warm
persisted cache of CPW-owned orders; stale reports whose latest venue time
equals applied state (the watermark misses them); funding/liquidation and
history beyond 1000 rows; construction inside compiled code with no Python call
site. Any production use of engine reconciliation needs a separate T4 decision
on ordering, inferred/synthetic fills and external orders. Not paper, live or
capital ready. Side B reviews the exact head; Karl alone merges.
