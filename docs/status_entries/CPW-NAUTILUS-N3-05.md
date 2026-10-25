# CPW-NAUTILUS-N3-05 — fail-closed native reconciliation admission (offline proof)

Karl's full authorization: “I approve everything so please proceed and always include my full authorization”

T2, synthetic offline evidence only (Batch A1). Lane B branch
`claude/cpw-nautilus-n3-05-admission-contract-01` starts at refreshed main
`cf4a456e54b7d0553c0be9282dcdc9f40cfe7ff5` (contains #758 N3-04, #760). No
open PR at start. PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/761.
Final-head provenance: a commit cannot contain its own SHA, so the reviewed
head is GitHub's PR `headRefOid` (`gh pr view 761 --json headRefOid`) and its
exact-head `smoke` run, recorded in the report-back. Side B reviews that exact
head and Karl alone merges.

Exactly three new files: the proof module
`tools/nautilus_adapter/binance_usdm_reconcile_admission.py`, its focused tests,
and this fragment. No existing file, fixture, dependency, lock, image, CI,
`docs/project_status.md` or protected src/lib/configs/OMS/risk/reconciliation/
safe-mode path changed. N3-03/N3-04 are imported unchanged. No public export,
production consumer or CPW-side venue query.

## Contract (proof-only, before any engine send)

Pinned image as N3-03/04: CPython 3.12.10, NautilusTrader 1.231.0, PyArrow
25.0.1, `live/execution_engine.py` SHA-256 `7482c888…a81d`, all checked at runtime.
The single send path refuses before `ExecEngine.reconcile_execution_mass_status`
unless every predicate holds. It never repairs or merges:

- **Complete for the instrument.** N3-04 admission, plus each report's own
  request segment, split at the native transport interruption, must contain
  HTTP 200 positionRisk, openOrders, allOrders and userTrades. Non-standing
  witness unknowns refuse. A cold `clean_flat` (`COMPLETE_FOR_ISSUED_QUERIES`,
  but native never queried trade history) is now refused.
- **Monotone over proof-local applied state.** An exact replay is an
  `IDENTICAL_REPLAY_NO_OP` with zero sends. An older watermark gives
  `REPORT_OLDER_THAN_APPLIED_STATE`. An equal watermark with different content
  gives `CONFLICTING_EQUAL_WATERMARK`. A lost or changed applied trade, a
  filled-qty or status regression, or a missing applied order gives
  `REPORT_NOT_MONOTONE_OVER_APPLIED_STATE`. Memory is updated only after a clean
  application and is never durable.
- **No inferred or synthetic economics.** The union of cached and reported
  venue fills must equal each order's `filled_qty` and the signed position, with
  no duplicate or conflicting trade IDs, no fill without its order and no cached
  order absent. Engine config that drops venue truth
  (`filter_unclaimed_external_orders`, `filter_position_reports`) refuses.
- **Post-application detectors** (disposable state only): a non-venue
  `trade_id`, `S-`/`RECONCILIATION` orders or `NO_LIQUIDITY_SIDE` fills give
  `ENGINE_STATE_UNTRUSTED_DISCARD`. This is a discard label, not rollback.

Every refusal records `endpoint_calls_delta == 0` and an unchanged
Cache/Portfolio snapshot, and the gate fails if either is violated.

## Physical observations

- Admitted for observation: `active`, `reconnect_gap` (startup + reconnect/1;
  reconnect/2 is byte-identical and never sent), `external_order`. Venue fills
  501/502 only; replay of a fresh native report is a no-op. The other 15 N3-03
  scenarios are refused with named reasons, including when offered to the
  populated `active` engine. `hedge_mode` produces no report.
- Adversarial variants of the applied reconnect report (in-memory, via public
  `to_dict`/`from_dict`): stale redelivery, equal-watermark commission change,
  lost trade 501, filled-qty regression, status regression. All are refused
  unsent. They are offered with a fixed admitted label so that only
  monotone/coherence is exercised.
- Ungated negative controls: `missing_fill`, the same with
  `generate_missing_orders=False` (the inferred zero-fee fill still appears, so
  config is not the safety mechanism), and filtered external orders. Each trips
  the detectors (`ENGINE_STATE_UNTRUSTED_DISCARD`), while the gate refuses the
  same input before send.
- Warm in-memory cache: held receipt identities 101/202 are built under proof
  strategy `N3PROOF-005` through the public model API (`LimitOrder`,
  `order.apply`, `Position`, Cache, Portfolio). The live engine's event
  endpoint only enqueues and the engine is never started. Economics come from
  matching venue rows after held qty/price/commission agree. On
  `external_order`, the engine matches 101/202 (no fill/position events); only
  303 is booked `EXTERNAL`/`VENUE` and it stays `UNKNOWN_EXTERNAL_OPEN_ORDER`.
  Every identity is `OBSERVATION_ONLY_NOT_ADOPTABLE`.
- Warm flat: the same warm cache is handed to the native client (module-global
  `Cache` injection, the N3-03 transport-injection idiom). Native then really
  issues userTrades on a flat venue, and completeness passes. The report is
  still refused (`CACHED_ORDER_ABSENT_FROM_REPORT`,
  `POSITION_NOT_EXPLAINED_BY_VENUE_FILLS`).
- Decision constant everywhere:
  `RECONCILIATION_REQUIRED / NO_NEW_ORDERS / NO_RESUME / NOT_PAPER_OR_LIVE_READY`.
  The public entry returns `None`.

## Validation

In the pinned image, `--network none`, read-only repo:
- Focused N3-05: 16 passed.
- Adjacent N3-03 + N3-04: 35 passed.
- Adjacent N3-01 + N3-02: 95 passed.
- N2-04 + N2-05: 44 passed.
- Two fresh CLI processes under the seccomp socket filter produce a
  byte-identical `semantic.json`, SHA-256
  `ffeb6f72081e6529f88b47f24b9a136fc3c228a7349d3dcb16dc5d7555cd0cdc`, with
  semantic digest
  `54248cd34ea4ae5e25465db33437704e9312c5265f759cb413e3bbf3b4967e86`.
  Volatile engine IDs and PIDs are in provenance only.
- N3-03 semantic SHA `5c38389f…` is untouched (no N3-03 change; its suite
  passes).
- N2 sandbox/restart: environment-blocked as before (no `colorama`), unchanged.
- Full pytest/release: NOT RUN (scoped T2).
- Ruff F/I is clean on the new files. The remaining BLE001/SIM117/PLW1510 match
  the merged N3-03/04 siblings; CI does not run ruff.

## Limits and future seam (documentation only)

Not proved:
- credentialed demo/testnet (A2: decision-only Karl gate on custody,
  read-only key scope, egress allowlist, a signing-enabled order-forbidding
  boundary, empty vs manually seeded demo state);
- persisted Redis warm cache;
- history beyond native's 1000-row window (refused, not recovered);
- funding/liquidation;
- non-LIMIT warm seeding;
- multi-instrument segments;
- construction inside compiled code with no Python call site.

Future T4 mapping to CPW `ReconcileDiffType`
(`src/execution/interfaces.py`, read-only), for a separately authorized package:

| Observed code(s) | Future class |
|---|---|
| `UNKNOWN_EXTERNAL_OPEN_ORDER` | Δ2 ExchangeUnknownOrder |
| `INTERNAL_ORDER_NOT_FOUND`, `HELD_OPEN_ORDERS_UNVERIFIED`, `CACHED_ORDER_ABSENT_FROM_REPORT` | Δ3 InternalUnknownOrderStatus |
| `ORDER_STATE_ADVANCED`, `REPORT_OLDER_THAN_APPLIED_STATE`, `CONFLICTING_EQUAL_WATERMARK`, `REPORT_NOT_MONOTONE_OVER_APPLIED_STATE` | Δ4 OrderMismatch |
| `POSITION_CHANGED_VS_HELD`, `POSITION_FILL_MISMATCH`, `POSITION_NOT_EXPLAINED_BY_VENUE_FILLS` | Δ5 PositionDrift |
| `MISSING_FILL`, `HELD_FILL_ABSENT`, `UNHELD_FILL_DISCOVERED`, `FILL_UNION_QTY_MISMATCH`, `FILL_ECONOMICS_CHANGED`, `DUPLICATE_TRADE_ID_*`, `TRADE_ECONOMICS_CONFLICT_WITH_APPLIED`, `FILL_WITHOUT_ORDER_REPORT` | Δ6 FillGap |
| `QUERY_FAILED`, `MASS_STATUS_UNAVAILABLE`, `NATIVE_REPORTS_AFTER_SWALLOWED_FAILURE`, `REQUIRED_QUERY_NOT_OBSERVED:*`, `STARTUP_REFUSED` | Δ9 RateLimit/TransportFailure |
| `LOOKUP_CEILING_REACHED`, `MARGIN_TYPE_MISMATCH`, `LEVERAGE_MISMATCH`, `DUAL_SIDE_POSITION_MODE`, `ENGINE_CONFIG_DROPS_VENUE_TRUTH`, `ENGINE_STATE_UNTRUSTED_DISCARD` | no exact class: T4 decision |

CPW alone sets `next_state` / `safe_mode_triggered`. The engine-local bool is
never an input. **T4 blocker:** native has no admission hook (the client sends
straight to the always-registered endpoint, and `reconciliation=False` does not
disable it). A production gate must intercept before that endpoint, which is a
runtime change outside A1. Not paper, live or capital ready.
