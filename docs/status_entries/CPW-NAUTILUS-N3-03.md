# CPW-NAUTILUS-N3-03 — offline native private startup/reconnect reconciliation proof

Karl's full authorization: “I approve everything so please proceed and always include my full authorization”

T2, synthetic offline evidence only. Dedicated Lane B branch
`claude/cpw-nautilus-n3-03-private-reconcile-01` starts at refreshed main
`a75c7e49cebccfab4467d1ff3ad1dfbf244d86cb` (contains #750 N2-05, #753 N3-01,
#754 N3-02, #752). No other PR was open; no shared file or interface.

Exactly four new files: proof CLI, focused tests, a synthetic hash-bound
private-response fixture that references the N3-01 tape for every
order/trade/position row, and this fragment. No existing file, dependency, lock,
protected src/lib/configs/OMS/risk/reconciliation/safe-mode path, CI or
project_status is changed. No public export or production consumer.

## Physical behavior

Pinned Linux image: CPython 3.12.10, NautilusTrader 1.231.0
(`cp312-cp312-manylinux_2_35_x86_64`), PyArrow 25.0.1, uvloop 0.22.1; reused,
not rebuilt or upgraded. Installed upstream sources are unmodified; hashes are
in the external receipt.

The real `BinanceFuturesExecutionClient`, `BinanceFuturesInstrumentProvider`,
`Portfolio`, `Cache`, `MessageBus` and user-data WebSocket client run against
in-process fakes that replace only the pyo3 `HttpClient` object and the
`WebSocketClient` module global. `sign_request` is overridden to call the native
unsigned `send_request`, so no signature is ever computed. Host
`n3-03.offline.invalid`; GET read routes plus `POST listenKey` only; any other
verb, route, signature, body or host refuses. Placeholder non-secret key string.

- Startup is native `_connect`: instruments, account (twice), symbolConfig, hedge
  mode, server time, REST listenKey, user stream. Then native
  `generate_mass_status(lookback_mins=None)`.
- Reconnect: the fake stream invokes the native-registered `post_reconnection`.
  Native resubscribes (new listenKey, new stream) and, before dispatch resumes,
  runs `_reconcile_after_resubscribe` → full mass status → `_send_mass_status_report`.
  The gap's missed fill 502 and 101 PARTIALLY_FILLED → FILLED are discovered; a
  second reconnect is identical (idempotent, no new trade IDs).
- Ordinary active state: 101 FILLED 0.010, 202 ACCEPTED reduce-only, fills
  501/502 (0.004/0.006 @ 60000.00, 0.048/0.180 USDT, MAKER/TAKER), LONG 0.010;
  native MarginAccount 1000/600/400 USDT, initial margin 600, leverage 1.
- 15 adverse/failure/gap scenarios each yield distinct witness anomaly codes.
  Measured native facts: 429/`BinanceError` on userTrades is swallowed into
  `[]` fills inside a non-None mass status (witness refuses it); 5xx positionRisk,
  malformed/partial JSON and timeout give `None`; hedge mode refuses startup;
  missing internal order lookup returns `None` after -2013; allOrders stops at
  1000 rows with no pagination; flat accounts with no active symbol never query
  trade history; native sorts fills by `TradeId` string ("1000" before "999").
- Every scenario keeps `RECONCILIATION_REQUIRED / NO_NEW_ORDERS / NO_RESUME /
  NOT_PAPER_OR_LIVE_READY`. The witness never adopts, cancels, flattens or resumes.

## Validation and limits

Focused: 24 passed, zero skips. Two fresh CLI processes under a Linux seccomp
socket-syscall filter (native negative control EPERM) produce identical
semantic receipts, `semantic_sha256`
`5c38389f5fe3beef54c068c667bf4515c0979a1e3cdb944ff953a0bc06b398e7`, with
distinct PIDs only in provenance. Guards fire before effects: Python socket,
credential env, hmac, writes outside evidence, subprocess, native `_get_sign`,
native `set_leverage`, and Cython `RiskEngine` / Python `LiveExecutionEngine` /
`Trader` construction (a `sys.monitoring` CALL monitor). Static tests forbid
authority calls and imports.

Adjacent N3-01 + N3-02: 95 passed. N2-04 recovery + N2-05 continuity: 44 passed.
N2 sandbox/restart could not run: the proof image lacks `colorama` and the
Windows venv is not CPython 3.12. These files are unchanged and share no code;
nothing was installed or synthesized. Full pytest/release and N1/N2 physical
matrices: NOT RUN — scoped T2.

Not proved: credentialed demo/testnet contact, LiveExecutionEngine-side
application of the mass status, funding/liquidation/multi-cycle accounting,
history beyond native's unpaginated 1000-row window, Windows portability,
native position `ts_last` (init time), and construction inside compiled code
with no Python call site (seccomp covers sockets only in CLI runs). Not paper,
live or capital ready.

External A–I report, evidence manifest and SHA-256 ZIP are outside Git; the
final-head and hosted smoke receipt binds the PR head. Side B reviews the exact
head; Karl alone merges. No self-merge.
