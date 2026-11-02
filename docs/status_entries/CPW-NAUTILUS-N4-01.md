# CPW-NAUTILUS-N4-01 — integrated native non-capital session

Karl's full authorization: “I approve everything so please proceed and always include my full authorization”.

## Scope and identity

T2 isolated manual proof, default OFF. Branch
`codex/cpw-nautilus-n4-01-noncapital-integrated-01`, dedicated worktree off
refreshed `origin/main` `c144c821d1decc48253b60901bf44377811954b0` (#764).
The only other open PR at preflight and publication check was #765, draft,
with eight disjoint Hermes/research files. No edits to that PR or its worktree.
PR provenance and exact final head/check are recorded in the external report.

Exactly three additions: `tools/nautilus_adapter/noncapital_integrated_session.py`,
`tests/test_nautilus_noncapital_integrated_session.py`, and this entry. No
optional helper edits. Reuses N2 pin/wheel integrity, canonical serialization
and monetary helpers; N3-02 observation projection, monotone observation
collection, instrument projection, fixed public endpoints and lifecycle observer.
The native N2 construction idiom is composed with the accepted public instrument,
without modifying the existing closed N2 scenarios or N3 reconnect orchestrator.

Ponytail full was applied before coding. Installed WP inspection/readiness,
one-shot review, test-plan, financial-invariant, authority-boundary, security,
Ponytail review, verification, PR evidence and handoff skills were read/applied.
Locator scripts ran read-only with `python -I -B`; isolated mode corrects the
Python 3.14 `inspect.py` module-shadowing launcher failure. No skill edits.

## Actual physical observation

`N4_01_INTEGRATED_NONCAPITAL_PASSED`. Final source-matched physical session:
2026-11-02 04:43:23.314–04:43:37.364 UTC (14.05 seconds; November 1 locally).
Existing image `cpw-02j-native-validation:20261101`, CPython 3.12.10,
NautilusTrader 1.231.0, PyArrow 25.0.1; all 20 lock versions and native/sandbox
wheel RECORD hashes checked. No install, pin, upstream or image modification.

Native `BinanceFuturesDataClient` public bookTicker/markPrice observations reach
the same process's native `SandboxExecutionClient` / `SimulatedExchange`,
`ExecutionEngine`, `MessageBus`, `Cache`, `Portfolio`, `OrderFactory`, `TestClock`.
Only `N4SIM` is registered for execution. The local native instrument copies
accepted Binance filters/units; its ID is explicitly derived. A fresh public
filter re-query must match before the evidence seal is acknowledged.

| Observation | Measured value |
| --- | --- |
| Source | `BTCUSDT-PERP.BINANCE`, native `QuoteTick` |
| BUY quote event time | `1793594612744000000` ns |
| SELL quote event time | `1793594613643000064` ns |
| Public bid / ask, both steps | 78469.30 / 78469.40 USDT |
| Local simulated orders | BUY .001 @78469.40, SELL .001 @78469.30 |
| Native commissions | .03138776 + .03138772 = .06277548 USDT |
| Maximum gross open notional | 78.46940 USDT, below 250; fixture leverage 1x |
| Native final state | FLAT; 2 FILLED orders; 2 native trade IDs |
| Native final balance / equity | 9999.93712452 USDT |
| Native realized net / unrealized | -.06287548 / 0 USDT |

Disposable initial balance is 10000 USDT. The 4 bps fee is a local fixture
assumption, not Binance fee evidence. Native account, position, commission and
portfolio observations agree with independent read-only Decimal assertions.
Market orders on this pin do not emit OrderAccepted; no acceptance is fabricated.
Public mark/index/funding observations are retained, never settled or applied.

## Persistence, interruption and refusal

Every observation appends, flushes, fsyncs and closes a hash-linked journal
record. A closed/fsynced manifest binds its full bytes, tail, run, native IDs,
environment and final native observation. Recovery requires a caller-retained
expected manifest digest. Two fresh OS inspectors, with native/CPW execution
imports blocked and network disabled, return identical read-only results and
zero extra orders/fills; source hashes remain unchanged.

The physical SIGKILL test retains the producer PID, original journal and a
durable .001 BTC open-position boundary. Two independent processes refuse its
missing seal without changing its bytes. Identical/conflicting duplicate event,
trade and venue-order IDs, wrong position-order linkage, removed/truncated
events, bad source/hash/time/account/instrument/run/version, altered accounting
and manifest all refuse, including semantically corrupted cases with recomputed
outer hashes. Missing/stale/disconnected feed latches a stop. Valid later native
input remains observable but cannot resume the interrupted native order sequence.

This is durable observed state, **not native cache rehydration**. Existing N2-02
already documents incomplete native NETTING-history/PnL restoration on this pin.
No custom restore engine or active-cache claim is introduced.

## Validation and reproduction

37 focused tests and 324 adjacent tests pass, zero skips. Adjacent coverage:
N2 sandbox/restart; N3-01/02 public reports/feed; N3-03/04/05 offline execution
and admission; paper broker/ledger interface/accounting contracts; developer-tool
smoke. Changed Python compile checks, exact three-file scope and diff checks
pass. Hosted `smoke` must be bound to the final PR head in the external report.
Full pytest/full-release: NOT RUN — isolated T2, no production consumer or
protected changes. Paper-state validator: inapplicable; no CPW paper records
are created/consumed. The unchanged N3-02 physical 65-second reconnect proof and
Rust N2-06 matrices are not rerun; no transport/callback implementation changed.

In the existing approved pinned Linux environment, from the repository root:

```sh
python -B -m tools.nautilus_adapter.noncapital_integrated_session run --public-noncapital-proof --output /tmp/owner-created-empty-n4
python -B -m tools.nautilus_adapter.noncapital_integrated_session verify --output /tmp/owner-created-empty-n4 --expected-manifest-sha256 CALLER_RETAINED_DIGEST
python -B -m pytest tests/test_nautilus_noncapital_integrated_session.py -q -p no:cacheprovider
```

The output directory must already exist, be empty and outside the repository.
The report contains the exact Docker commands, trusted digest and evidence ZIP
identity. Source module SHA-256:
`3c9634ca28a09b96ca3a2969c8fee1df26d87754ee6912a2ff990d389d8ab62f`.
Focused test SHA-256:
`d59dc246ce8c3524152d221641c792528ac78e231428d0b4fe593b6f038839e8`.
Final public manifest SHA-256:
`741a04d7f352531b784d6adc570afbb0d53d42a205b80d8940aabb839e25f7f8`.
Earlier failed compatibility/test/public attempts are retained externally, not
relabeled passes. The first image lacked colorama; an existing full-pin image
resolved that prerequisite. Quote precision, native timestamp provenance and a
dictionary iteration error were corrected within scope. The first public run
submitted no orders; the second passed; the third revalidated final reviewed code.

## Boundaries

`RECONCILIATION_REQUIRED / NO_NEW_ORDERS / NO_RESUME / NOT_PAPER_OR_LIVE_READY`.
No Binance execution client/order sender, signed/private request, credential
read, exchange account access, paper/live activation, scheduling or strategy.
Only unsigned public exchangeInfo GET and fixed public WebSocket subscriptions;
negative tests prove submit/cancel/account/listenKey/signing requests refuse.
N3-05 offline private-report admission is unchanged and receives no invented
authenticated account facts. No `src/`, `lib/`, config, dependency, workflow,
OMS/risk/reconciliation/safe-mode/overlay, project-status, historical evidence,
Lane A, Rust history route or canonical artifact edits. Only proof-owned
containers/processes are removed; other resources remain untouched.

This proves no funded recovery, active-position rehydration, funding settlement,
margin/liquidation parity, private Binance synchronization, CPW protected OMS
integration, paper/demo or live readiness. Side B reviews the actual final
diff/head; Karl alone decides merge. No self-merge.
