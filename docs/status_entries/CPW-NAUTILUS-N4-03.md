# CPW-NAUTILUS-N4-03 — non-capital recovery-to-supervisor HOLD contract

Karl's full authorization: “I approve everything so please proceed and always include my full authorization”.

PR: [#768](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/768).
T2 isolated manual proof tooling, with no production consumer or trading authority.
Initial refreshed base was merged N4-02 `fff1aeee85d89374fbd9e917fb4f7957fe0a7d3c`;
the dedicated branch was refreshed onto `2ec2f9e5c6834f1dc356dcfe7850f6e3f2b5e575`
after file-disjoint #765 merged. No competing open file overlap remained.

Exactly three additions: `tools/nautilus_adapter/noncapital_supervisor_hold.py`,
`tests/test_nautilus_noncapital_supervisor_hold.py`, and this entry. No existing
helper, economic owner, protected path, dependency, config or workflow changed.
The optional controller hook was unnecessary: the unchanged `Controller.scenario`
already returns its complete case/readers and writes the original raw receipts.

## Actual integration and result

Explicit `run --public-noncapital-proof --output <empty-external-directory>`
calls the existing N4-02 producer/readers, original fault controls and cleanup.
Fresh unsigned Binance public data reaches the existing local N4SIM native
sandbox, Redis/AOF persistence, and genuine independent native restoration.
The bridge then validates source/ACK/process/receipt/publication/economic
bindings and seals a denial-only record with copied, checksum-indexed receipts.
It does not construct a second ledger or reconstruct native state itself.

Final frozen-source `physical-05` passed clean OPEN, single-cycle FLAT,
acknowledged OPEN SIGKILL (exit 137), and pre-ack OPEN SIGKILL refusal (exit 137).
Each positive has two fresh source-equal native readers; clean OPEN also has a
third integrity reload after the fifteen original refusal controls. Recovery
creates zero orders, fills, clients, native commands or events. Reader mounts and
Redis ACL are read-only; native record hashes and empty ACL logs bind no-write
evidence. All 33 owned containers and the owned network were removed.

Final HOLD SHA-256:
`13816a049fe632fc0d3f70aeecdddccdc0c0082d3ee010629aeedf1de874beb7`.
`VERIFIED_HOLD` means valid bounded evidence with continued denial. Invalid,
incomplete, stale-at-seal, torn, forged or conflicting proof returns nonzero
`BLOCKED`; it cannot become a successfully verified HOLD.

Two fresh offline exact-CLI verifiers, additional guarded no-engine probes and
bytewise before/after inventories prove repeatable artifact inspection after
Redis cleanup. This inspection is not fresh native recovery or current-market
freshness. A genuine supervisor-process SIGKILL between fsynced HOLD and ACK
leaves no valid acknowledged proof. Caller-supplied trust digest is mandatory;
self-rehashed files cannot supply their own trusted origin.

## Minimal future handoff, without a consumer

| Field | Meaning for a separately authorized future consumer |
|---|---|
| `schema`, `owner`, `sealed_ns`, `bridge_sha256` | Exact version/owner/source and original seal identity; no release authority |
| `binding` | Original controller/image/source identity, native run/trader, namespace/PIDs, manifest/records/projection hashes and economics |
| `files`, `hold-ack.json`, external trusted HOLD digest | Relative-path/size/SHA-256 identity of original and copied receipts, final acknowledged seal |
| `disposition` | Exactly `HOLD` |
| `authority` | `RECONCILIATION_REQUIRED / NO_NEW_ORDERS / NO_RESUME / NOT_PAPER_OR_LIVE_READY` |
| `cpw_production_supervisor_connected`, `authenticated_venue_reconciled`, `execution_permit_issued` | All exactly `false` |
| `blockers` | Fixed unresolved reasons below; success never removes them |

Fixed blockers: `AUTHENTICATED_VENUE_STATE_ABSENT`,
`PRODUCTION_SUPERVISOR_NOT_CONNECTED`, `ACTIVE_TRADING_RESUME_NOT_AUTHORIZED`,
`MULTICYCLE_HISTORY_NOT_PROVEN`, `FUNDED_STATE_AND_LIQUIDATION_UNPROVEN`.
No N3-05 synthetic observation-only report can become authenticated venue truth.
No consumer, subscription, human reset action, daemon or execution route is added.

## Validation, evidence and limits

Final focused profile: **69 passed, zero skips**, using the exact pinned image
and checksum-identical local hydration of new physical-05 receipts; original
external evidence remained bytewise unchanged. N4-02 focused **33 passed**;
adjacent core **252 passed**; original N2-02 native/cache/restart **29 passed**;
developer smoke **109 passed**. Separate original reversal repetition preserves
the known multi-cycle history-loss negative; it is not a positive capability.
The verified external N2 test-only transport adapter changes no economic owner.
Compile, applicable Ruff and exact three-file diff/scope checks pass. Final
exact-head hosted smoke and GitHub state are recorded in the external A–I report.
Full release: **NOT RUN — T2 bounded proof; not merge evidence**.

Native image remains `cpw-n4-02-env01:exact-pins`, immutable ID
`561f46170f6697a683bdb6c3a00ca8f8045144d5126a82a8bdb85bdb3a681c65`:
CPython 3.12.10, NautilusTrader 1.231.0, PyArrow 25.0.1, all 20 lock entries,
Redis client 8.1.0/server 7.4.2. Full installed RECORD verification passed.
No image repair, native patch, version substitution or host install was needed.

Failed/superseded attempts are retained externally: initial receipt-shape error,
source-change refusal, and the 68-pass/one-failure quote-shape profile corrected
by an early validation guard. Final native/focused evidence was repeated after
the correction. Minimal native-image developer smoke lacked Git; an existing
host environment lacked pytest; the canonical existing host environment then
passed all 109 developer tests without installation or source changes.

Only one unfunded exposure and one completed native cycle are proven. Fixed
.001 BTC, 4bps fee and 1x are local fixture assumptions, not Binance account
economics. Multi-cycle, funded/funding/liquidation, power-loss and in-flight
atomicity, private venue reconciliation and active resume remain unproven.
Authenticated venue status, an actual CPW policy adapter, human recovery
authority, risk/OMS integration and protected lifecycle validation require
separately authorized protected work. No paper/demo/LIVE or capital decision
follows. Side B reviews exact head/evidence; Karl alone decides merge. No self-merge.
