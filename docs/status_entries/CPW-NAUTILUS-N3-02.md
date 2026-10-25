# CPW-NAUTILUS-N3-02 — isolated public-feed reconnect proof

Karl's full authorization: “I approve everything so please proceed and always include my full authorization”.

Dedicated Lane B branch `claude/cpw-nautilus-n3-02-public-feed-reconnect-01`
starts at refreshed main `f4aec58e6f600d1c81169169747abf200ca96f0f` (N3-01/#753).
Lane A/#752 is file-disjoint. The transport-fault continuation supersedes only
the original requirement for a native deliberate-abort API; the pinned native
Binance public data integration remains unmodified.

PR: [#754](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/754),
non-draft for independent Side B review; not merged. Tested implementation
commit `9b928ea4ff5216b54d5bc58e860f99c2860844fb`. This PR-provenance-only
documentation update preserves all three tested module/test/fixture blobs.
The external final-head/check receipt binds the later publication head.

Exactly four new files: bounded proof CLI, native contract/negative tests,
explicitly synthetic invalid-case fixture, and this status fragment. No existing
tracked file, dependency, protected path, CI, or project-status edit.

CPython 3.12.10, NautilusTrader 1.231.0, PyArrow 25.0.1 and all lock-compatible
versions remain pinned; Linux additionally uses uvloop 0.22.1. Public requests
are restricted to unsigned GET `/fapi/v1/exchangeInfo`, native BTCUSDT bookTicker
and markPrice subscriptions. The native provider constructs passive account
HTTP API wrappers but cannot invoke a private/signed request through the proof's
HTTP guard. No execution client, trading node, strategy, key, or account access.

The CLI requires an explicit flag and empty external output directory. Native
instrument/quote/mark/index/funding values, source hashes, timestamps, callback
and re-subscription observations are bounded diagnostic evidence only. An
external supervisor owns fault injection and transport receipts. No callback
is invoked manually; graceful disconnect or process replacement cannot pass.
Missing, malformed, stale, out-of-order, duplicate and unproven reconnect inputs
refuse. All outcomes retain `NO_NEW_ORDERS / NO_RESUME / NOT_PAPER_OR_LIVE_READY`.

Physical native receipt: `N3_02_PUBLIC_FEED_RECONNECT_PASSED`, 85.248 seconds
(86.390 including the external supervisor). The selected loopback `ss -K`
preflight did not terminate its peer; the authorized Docker network fallback
isolated only the proof container for 65 seconds. Both original WS sockets
ceased to be established; two new same-process public WS sockets, real native
callbacks/subscription, and new source timestamps/hashes proved reconnect.
Process 59 and native quote client identity 124940356366416 were unchanged.

Native post-reconnect quote: 80865.90/80866.00 USDT; mark 80865.90000000;
index 80903.53195652; funding fraction 0.00008000, next funding timestamp
1792915200000000000 ns. These are measured observations, not constants or a
trading oracle. Native instrument filters remained tick 0.10, step/minimum
quantity 0.001, minimum notional 50 USDT, status TRADING. Exchange-info native
event time is preserved as supplied, separately from request/receipt time;
this proof does not infer tradable-order validity from that metadata.

37 focused native/control tests and 58 adjacent N3-01 tests pass, zero skips;
compile, offline socket-audit cases, exact scope and diff checks pass. Existing
developer-tool smoke passes locally (109 tests). Required hosted `smoke` is
verified against the published PR head in the external final-head receipt.

Earlier attempts remain UNPROVEN: thread-local callback observer missed the
native worker; initial DNS snapshot wrongly rejected a rotated peer; an overly
tight startup budget stopped before injection; and the pre-fault idle REST pool
timed out on the filter re-query. Each correction/repeat has an evidence-backed
bounded plan under continuation section 3. Final code observes only the two
unchanged native code objects via CPython monitoring and uses a fresh native
public HTTP/provider instance for the single post-fault filter snapshot.
Five public attempts occurred; the first four are retained as failures, not
relabeled PASS. Each run stayed below 180 seconds. All proof resources were
removed; unrelated containers/networks were preserved.

Full pytest/full release and unrelated N1/N2 matrices: NOT RUN — scoped T2.
External A–I evidence retains observations, source/wheel hashes, all attempted
runs and corrections, cleanup, final head/checks and verified ZIP/SHA-256.
This proves neither N2 accounting/funding settlement nor private reconciliation,
full N3 ownership, paper/live or capital readiness. Karl alone may merge after
independent Side B review and the required exact-head smoke. No self-merge.
