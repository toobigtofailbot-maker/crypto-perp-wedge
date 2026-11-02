# CPW-NAUTILUS-N4-02 — bounded durable native non-capital recovery

Karl's full authorization, verbatim: “I approve everything so please proceed and always include my full authorization”.

Karl's bundle authorization, verbatim: “I authorize this bundle execution plan, start now!”

## Identity, scope and environment

T2 isolated, manual proof; no production consumer. Dedicated Lane B branch
`codex/cpw-nautilus-n4-02-durable-native-recovery-01` starts at refreshed main
`77a5a840128fae6cb46d085862a15fd5e204d61f` (merged #766).
The only competing open PR at startup and prepublication was #765, with eight
disjoint Hermes/research files. Root checkout and other lanes were not edited.
PR: [#767](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/767),
non-draft for independent bounded-proof review; no merge. Exact final head
and hosted smoke receipt are recorded in the external A–I report.

Exactly four additions: `tools/nautilus_adapter/noncapital_persistent_session.py`,
`tools/nautilus_adapter/noncapital_persistent_proof.py`,
`tests/test_nautilus_noncapital_persistent_session.py`, and this entry.
N4-01/N2/N3 helpers, dependencies, workflows, protected code and project status
are unchanged. The controller reuses native N2 observation/record/provenance
helpers and N4-01 public transport, filters, quote validation and feed latch.
It does not instantiate N4-01's in-memory economic engine.

ENV-01's explicit amendment authorized a new disposable image derived from
unchanged `cpw-n3-02-proof:pinned`, base ID
`79e7aeab9e8761d75dc6c492126bd846af86cecb3735d0cfb1f264a195aa95aa`.
New `cpw-n4-02-env01:exact-pins` image ID:
`561f46170f6697a683bdb6c3a00ca8f8045144d5126a82a8bdb85bdb3a681c65`.
Exact CPython 3.12.10, NautilusTrader 1.231.0, PyArrow 25.0.1 and all 20
committed lock versions pass the original environment/native RECORD gates.
Only `colorama==0.4.6` and separate historical client `redis==8.1.0` were added,
from exact PyPI wheels verified against published SHA-256, installed offline
with `--no-deps`. Their installed RECORD checks also pass. Recipe, URLs,
hashes, failed setup attempt and image acceptance are external evidence.
No source image, host package, dependency lock or native wheel/source changed.

## Native capability and physical result

The final frozen-source physical matrix (`frozen-physical-03`) passed:

| Case | Actual outcome | Native balance / equity / fees, USDT |
| --- | --- | --- |
| Clean OPEN | Native single-exposure recovery, two fresh readers | 9999.96900436 / 9999.96890436 / .03099564 |
| Clean FLAT | Native completed-cycle recovery, two fresh readers | 9999.93803532 / 9999.93803532 / .06206468 |
| Acknowledged OPEN SIGKILL | Durable checkpoint, exit 137, two fresh equivalent readers | 9999.96896 / 9999.96886 / .03104000 |
| Before-ack OPEN SIGKILL | Exit 137; both fresh readers refuse missing seal | No admitted recovery |

Fresh unsigned Binance exchangeInfo/bookTicker/mark-price data reaches the
same persistent TradingNode's native `N4SIM` sandbox execution client.
Fixed .001 BTC, at most 250 USDT, 1x, 10000 USDT disposable initial balance
and 4 bps fixture fee remain unchanged. The fee is not Binance account data.
Account/order/fill/trade/position identities, quantity, entry, commissions,
cost/position linkage, realized/unrealized, balances, margin and equity are
checked against actual native observations. A closed single cycle has no
prior NETTING snapshots; both its closed position and snapshot collection
are explicitly checked.

Native Redis 7.4.2 owns economic persistence, with `appendfsync always` and
account-event persistence. Controller-labelled isolated containers bind
Redis only to loopback; no host port is published. A task-owner marker and
server run ID guard the fixed backend. Event-ID read-back, stable native
record hashes and successful AOF status precede the fsynced acknowledgment.
The kill controller independently checks digest, native records, AOF and
the producer's `/proc` identity, retains a fsynced checkpoint, then SIGKILLs
only its owned producer. PID namespace plus PID identifies a process.

Readers use real `TradingNode`/`exec_engine.load_cache`, construct no execution
client and register/submit nothing. Only the original producer quote is added
through the native in-memory quote/portfolio APIs for valuation. Network
interfaces are disconnected before recovery; native Redis permissions are
read-only. Native command/event counters remain zero, raw native records
and complete semantic projections stay equal, and ACL logs contain no
prohibited reader command. No journal is replayed into economic state.

Fifteen physical controls refuse missing/torn acknowledgments, untrusted
digest, expired checkpoint, source/version/trader/run mismatch, altered
economics, stale quote, filter/mark mismatch, and missing/corrupt/out-of-order
native records in disposable genuine-byte clones. Original source records
remain intact and an additional original reload succeeds. All 33 final
controller-owned containers, including transient producers/readers/Redis
fixtures, are removed; the separately owned debugging resource is removed too.

## Validation, history and limits

Final focused suite: **33 passed**, including native open/flat economics,
actual duplicate and conflicting native fill delivery without monetary effect,
economic/identity refusals, process-namespace regression and freshness wait.
Adjacent core: **252 passed**; original N2-02 native/cache/restart: **29 passed**;
developer smoke: **109 passed**. Compile, applicable Ruff and scope/diff checks
pass. The required exact-head hosted smoke receipt is in the external report.
Full release is not run: isolated T2, no production consumer/protected change.

N2-02 runs use an external test-only adapter for the new loopback Redis
transport and its legacy runpy launcher, without changing helper files or
native economic behavior. Its known negative is **REPRODUCED**, with retained
raw receipts: reversal producer realized 29.836 USDT and one historical
snapshot; native reload realized 19.92 USDT and no snapshot. A separate
source-matched repetition passes its negative assertions. The new capability
refuses this shape as `MULTICYCLE_NATIVE_HISTORY_UNSUPPORTED_PINNED`.

Earlier failed physical runs remain failed external evidence: ACL result
parsing, cross-namespace PID collision and startup quote freshness were
corrected within scope; only the final source-matched run is counted.
Ponytail FULL ran first; mandatory installed skills were read/applied, their
locator scripts executed where supplied, and final actual-diff financial,
authority, security, lean and verification reviews were performed. Locators
are not safety certificates.

`RECONCILIATION_REQUIRED / NO_NEW_ORDERS / NO_RESUME / NOT_PAPER_OR_LIVE_READY`.
This proves only one unfunded exposure and one completed native cycle. It
does not prove power-loss/in-flight atomicity, funded restore, funding
settlement, liquidation, multi-cycle parity, private venue reconciliation or
active resume. No credentials, exchange account action, signed/private/order
transport, strategy/scheduler, paper/demo/LIVE, capital or self-merge.
Side B reviews the exact PR/evidence; Karl alone decides merge. A future
non-capital supervisor seam requires its own authority.
