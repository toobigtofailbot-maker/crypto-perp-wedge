# CPW-NAUTILUS-N2-HISTORY-ROUTE-01 — PARTIAL / NATIVE_V2_ROUTE_FAILED

## Continuation: CPW-NAUTILUS-N2-CURRENT-ARCHIVE-03

Owner authorization, verbatim: "I approve everything so please proceed and always include my full authorization"

One bounded native current-cache plus exact archived-frame diagnostic, on
existing draft #747 at `bf94917ae55be99fd323cbe720fb8f1a6e048da7`, base
`a1d83b9157ee9e9892cd7fc92fe6471b5d8349c2`. The four existing allowed fixture/status
paths are the only continuation changes; Cargo manifest/lock remain immutable.
Prior HISTORY-ROUTE-01 and BOOTSTRAP-REPLAY-02 failures remain historical below.

Frozen contract: native current-cache load and index rebuild, then native
BLAKE3-checked restoration of one exact index-zero archived reversal frame;
round trip has no archive. No tail replay. Prefix phase probes and complete
restores each use fresh native Redis/redb clones and close/drain the native
writer before external measurement. Cross-process prefix comparisons are
distinct from same-process phase instrumentation. This observes a measured
sealed/drained checkpoint pairing, not cross-store atomicity or general crash
recovery. Native frame-index overwrite limitations remain excluded.

**Verdict: `SEALED_CHECKPOINT_FEASIBILITY_ONLY`.** One frozen native build,
290.296-second matrix, controller exit 0; quick gate passed before the remaining
producers. Two fresh restores per producer matched every recorded native
account/current-position/order/fill/trade, archived identity and frame byte.

| Producer | Native producer/restored PnL | Equity | Full restores |
| --- | --- | --- | --- |
| reversal / healthy | 29.836 USDT | 10029.836 USDT | 2/2 exact |
| round trip / healthy | 9.916 USDT | 10009.916 USDT | 2/2 exact |
| round trip / post-seal SIGKILL | 9.916 USDT | 10009.916 USDT | 2/2 exact |
| reversal / post-seal SIGKILL | 29.836 USDT | 10029.836 USDT | 2/2 exact |

Eight prefix probes and eight full restores had zero raw/semantic Redis deltas;
authoritative native records, sealed redb and checkpoints remained unchanged.
All twelve negative controls refused, including native snapshot missing/hash
failures, without semantic mutation. Two native duplicate sequences refused at
unchanged watermark 7. Two genuine captured duplicate fills refused at the
order layer before position application, preserving economics and Redis. This
does not prove associated duplicate-position/economic safety: current receipts
omit the captured fill association; prior verified captures had null position
IDs. These controls and negative cases also had zero raw clone deltas.

Locked offline native check/build, controller syntax, 211 active Linux registry
package archive/source checksums, 15 exact-commit native crate identities,
independent receipt audit and four-path scope checks passed. Audit assumptions
about registry checksum files, inactive lock targets and duplicate application
were corrected offline; original errors are retained, with no physical rerun.
Thirty-five distinct producer/native-receipt PIDs bind the evidence. Native bus
taps measured no traffic/endpoints in ordinary restores; source inspection
confirms no recovery execution client. No syscall-level venue audit or client
counter is claimed. The owned network-none container and all Redis are stopped.

Full v1/whole-repo pytest or release: NOT RUN - scoped T2 private fixture policy;
not used as N2 economic or merge evidence. Exact final-head hosted smoke is
publication evidence in the external A–I report/ZIP, not recovery acceptance.
Publication remains [draft PR #747](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/747).

Next: Side B independent exact-head review; Karl's merge decision remains
separate. Cross-store atomicity, in-flight/power-loss recovery, same-namespace
recovery, frame-index overwrite/multi-cycle continuity, funding/margin and real
venue reconciliation remain unproven. No production N2 remediation, N2
acceptance, N3, resume, deployment, paper/live/capital or merge authority follows.

## Continuation: CPW-NAUTILUS-N2-BOOTSTRAP-REPLAY-02

**NATIVE_V2_BOOTSTRAP_ROUTE_FAILED. Production N2 remediation draftable: NO.**
This distinct continuation WP keeps draft PR #747 and its six-file scope. Old
reviewed head: `fc053f97600f3311f72ce9ae15b1d207613b628c`; refreshed base remains
`a1d83b9157ee9e9892cd7fc92fe6471b5d8349c2`. No merge, PR-state change, engine
upgrade, Lane A change, resume, N2 completion or trading authority follows.

The original HISTORY-ROUTE-01 evidence remains immutable: ZIP SHA-256
`88205135df66802eab22132e5cc512d289feef70c7784df3b2e77abd8fb4c30a`, all
190 indexed payloads reverified. Its failed verdict below is historical evidence,
not overwritten by this continuation. The original N2-02 ZIP and four file blobs
plus v1 lock are also preserved. Only Rust source, controller, README and this
status entry change; Cargo manifest/lock and upstream sources are unchanged.

### Source-grounded native bootstrap contract

Exact rc7 source/crates remain commit
`55c0e82053142bce3a5cba4de4221d3929c2d3bc` / Rust crates 0.66.0.

| Entity | Native owner | Bootstrap rule |
| --- | --- | --- |
| Current accounts/orders/positions | Redis cache adapter / `cache_all` | Do not preload mutable state before replay |
| Archived-cycle blob | `Cache.snapshot_position_encoded` / general Redis state | Native loader fetches via `load_snapshot_blob` / `cache_general` |
| Anchor/range | Event-store reader | Latest anchor watermark + 1 through durable high-watermark; otherwise seq 1 |
| Reference data | `cache_currencies`, `cache_instruments` | Native reference-only bootstrap |
| Archived frames | `restore_snapshot_blob` | Native BLAKE3 validation and restoration, no fabricated cycles |
| Tail | `restore_cache_from_sealed_run` | Upstream state-only replay, no custom prefix replay or duplicate suppression |
| Portfolio PnL | Native `Portfolio` | Derived from native recovered cache, never injected |
| Reconstruction writes | Native cache backing adapter | Directly measured in isolated native Redis clones |

The fixture now proves zero mutable orders/positions/accounts/archived frames
in memory before replay. It records the native anchor, exact range, payload
counts, source run/instance IDs and a separately PID-bound process-run ID.
An inspection reader is dropped before reopening through the official loader,
as redb rejects simultaneous handles even when read-only.

### Physical result

One corrective clean matrix, **221.27 seconds**, controller **exit 2**. All native
loader calls in the eight ordinary recoveries return successfully, but the
fixture rejects their economic results with `RECOVERY_NOT_QUALIFIED`.

| Scenario / stop | Producer PnL / equity (USDT) | Two recovered PnLs | Position count | Order/fill counts producer → restore | Native range |
| --- | --- | --- | --- | --- | --- |
| Round trip / healthy | 9.916 / 10009.916 | 0 / 0 | 1 → 0 | 2/2 → 2/2 | 1–16, no anchor |
| Round trip / post-seal SIGKILL | 9.916 / 10009.916 | 0 / 0 | 1 → 0 | 2/2 → 2/2 | 1–16, no anchor |
| Reversal / healthy | 29.836 / 10029.836 | 0 / 0 | 1 → 0 | 3/3 → 1/1 | 14–24, anchor 13 |
| Reversal / post-seal SIGKILL | 29.836 / 10029.836 | 0 / 0 | 1 → 0 | 3/3 → 1/1 | 14–24, anchor 13 |

Recovered equity matches all four producers. Reversal restores the original
archived frame identity and **9.916** PnL, but not the current **19.92** cycle.
With no current position the portfolio total is still zero. No complete history,
order/fill/trade identity conservation or idempotent recovery acceptance follows.
Round-trip order/fill identities match; reversal omits the pre-anchor orders/fills.

Captured native order fills have `position_id=null`. Exact source
`replay.rs::apply_fill_to_position` returns without creating a position for that
case; the following position events require a position already in cache. The
archived-cycle anchor is not a complete cache snapshot. This explains this
fixture's mismatch; it is not a proof that every upstream configuration fails.
No synthetic binding, hand-written prefix replay or upstream patch was tried.

### Effects, negative controls and limits

- Each attempt uses native Redis DUMP/RESTORE inputs and a copied sealed redb in
  a new empty, disposable loopback instance. Exact source DUMP bytes are retained.
  Native RESTORE may re-encode unordered sets, so raw clone-byte equality is
  reported separately from verified native type/content equality. Each clone
  has its own before/after raw and content baseline. This test isolation is not
  a CPW persistence overlay, production promotion protocol or rollback repair.
- All eight ordinary failed economic recoveries mutate their clone: three
  keys for round trip, two for reversal. Account event lists grow **8→11** and
  **13→16** respectively, appending three already-existing event IDs; no new
  event identities. Order lists are rewritten at length three, not extra fills.
  Recovered equity does not grow twice; the persistent repeated account-state
  events are a real write/atomicity gap, not proven duplicate monetary profit.
- Measured bus publishes/sends/responses and registered endpoints are empty in
  all ordinary receipts. Sealed source file hashes stay unchanged (no append).
  No execution engine/client is constructed in restore. There is no exposed
  runtime client-registry measurement; absence is also checked by source/control
  flow, not a literal `execution_clients=0` receipt. No syscall-level venue audit
  or complete zero-effect claim is made.
- Two genuine native duplicate-sequence controls first append captured entries
  1–7, then reapply captured seq 7 to a separate native backend. Both reject
  out-of-order seq with high-watermark **7→7**, no authoritative/economic state
  mutation. Exact `OrderFilled` reapplication remains **unproven**: neither
  scenario has a qualified ordinary recovery, so that control is gated/masked.
- Twelve negative cases cover wrong source/binary/lock/run/instance, missing/
  corrupt/truncated snapshot, missing/corrupt/truncated anchor-source file, and
  resume refusal. All return failure; snapshot faults reach native missing/hash
  errors. No negative clone has a native record-content delta. Anchor tests
  damage the source file, not an independently edited anchor record.
- Every authoritative producer checkpoint, native Redis record and sealed
  source file remains unchanged, including after fault injection. This proves
  preservation through disposable native clones, **not same-namespace recovery
  failure atomicity**. Ordinary reconstruction writes before economic refusal
  remain unsafe for a direct authoritative target.
- The initial diagnostic was segregated: an open inspection reader caused
  native lock errors. A premature rebuild while that diagnostic was active also
  invalidated a later producer's executable reread. Those partial results are
  retained and excluded. One source correction released the reader; the single
  corrective matrix used a frozen binary. No further physical iteration occurred.
- Both crashes are post-seal, database-drained SIGKILL checkpoints. In-flight
  logs, Redis/power-loss restart, open exposure, funding, margin/liquidation,
  reconciliation and real venues remain outside this proof.

Locked offline `cargo check`/`cargo build`, controller syntax and native clone
preflight passed (an earlier raw-clone equality assumption failed and is retained).
No v1/full-release rerun. T2 scope/source/evidence checks and final exact-head
hosted smoke are retained in the new owner A–I report/ZIP. Smoke is publication
evidence only. The owned continuation container has no external network or
published ports; all its Redis processes and the container are stopped.

**Next action:** Side B independent exact-head review of the failed route and
producer association/anchor contract evidence before any further WP. Production
remediation remains **NO**. No speculative continuation is authorized here.

## Preserved HISTORY-ROUTE-01 result (historical)

The tested native bootstrap/replay composition fails. **Complete native recovery
is not proven; production N2 remediation is not yet draftable from this evidence.**
This result is not an upstream-wide impossibility claim or N2 acceptance.
No migration, version promotion, resume, paper/live/capital, or merge is authorized.

Publication: [draft PR #747 — partial native route failure evidence](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/747).
This is a partial-evidence draft, not a merge-ready engineering delivery.
Final exact-head GitHub smoke/mergeability and the verified local evidence ZIP
are recorded in the owner A–I report; smoke cannot qualify the native route.

## Facts and method

- Dedicated Lane B branch: `codex/cpw-nautilus-n2-history-route-01`, based on
  refreshed `origin/main` at `a1d83b9157ee9e9892cd7fc92fe6471b5d8349c2`.
  PR #746 is merged; initial root checkout was clean and left unchanged. No
  competing open PR or equivalent history-route branch was found at preflight.
- Exact upstream: `v2.0.0rc7`, commit
  `55c0e82053142bce3a5cba4de4221d3929c2d3bc`. Published Rust crates `0.66.0`
  carry that commit in `.cargo_vcs_info.json`; the fixture pins them and commits
  the isolated Cargo lock. Downloaded source blobs are verified against the
  exact upstream Git tree, with SHA-256 receipts in owner evidence.
- Windows Python 3.14.3 rc7 wheel import succeeds. Wheel SHA-256:
  `079a8f195e024274d86f380993f492e071c386ddb089c0e8905c71690a27429d`.
  Required durable cache restore methods and event-store replay are not bound.
  A separate Rust 1.99.0 installation succeeded, but Windows linking failed
  because `link.exe` is absent. Neither condition is an upstream economic failure.
- A separately owned Linux Docker container provided a viable Rust fallback.
  Image digest:
  `sha256:114c7a4425406451c2866b6aafe69fe29b1b298832db1277d411ac73c82d04d6`.
  Rust 1.99.0, Redis 7.0.15 and Debian bookworm package versions are preserved.
  This is a Debian container proof, not Windows or Ubuntu platform certification.
- Upstream `BacktestEngine` produced actual native orders/fills/positions/account
  state and portfolio PnL. Native `RedisCacheDatabaseAdapter` owned persistence;
  `EventStoreLifecycle` owned capture, redb, snapshot encoding and anchors.
  Fresh restore processes called `Cache.cache_all`, then
  `restore_cache_from_sealed_run`. No CPW snapshot serializer, ledger, PnL policy,
  replay algorithm, or production engine integration was implemented.

## Physical observations and limits

The corrective physical matrix took **105.77 seconds**. All four producers
matched the N2-02 oracle exactly, closed their current positions and preserved
their checkpoint bytes. Native values, before restart:

| Scenario | Healthy/crash PnL (USDT) | Equity (USDT) | Archived cycles |
| --- | ---: | ---: | ---: |
| Round trip | 9.91600000 | 10009.91600000 | 0 |
| NETTING reversal | 29.83600000 | 10029.83600000 | 1 |

Each producer was followed by two fresh restore attempts: **8/8 returned exit 1**.
Round trip failed at replay sequence 4; reversal failed at sequence 18, both
`OrderInitialized`: its `client_order_id` was already in the native orders map.
The controller returned **exit 2 / NATIVE_V2_ROUTE_FAILED**. Native Redis record
hashes changed before rejection in all four cases. No recovered-state PnL/equity,
complete restored history, successful restore PID/instance receipt, zero duplicate
economic effects, or read-only/idempotent recovery claim is established.

**Inference:** preloading current order state and then replaying captured
initialization events is incompatible in this fixture. Inspection of the exact
upstream loader confirms the rejecting `cache.add_order` path. This does not
establish that an upstream-supported bootstrap using a different native initial
cache population would fail. No alternate bootstrap was tried after the limit.

The initial diagnostic run had a fixture shutdown defect: a retained snapshot
callback prevented native writer sealing. The correction releases the callback
before `EventStoreLifecycle.seal`, following the upstream kernel. The diagnostic
run and all raw errors are retained separately. The single clean corrective
physical rerun is consumed; no source patch or additional physical rerun followed.
Initial Rust compilation signature errors were corrected before physical work.

Both owned crash producers were killed with SIGKILL after native event-store
sealing and native Redis writer close/drain, while held alive at the checkpoint.
This is **post-seal checkpoint hard termination**, not an in-flight/unsealed-log,
Redis restart, host-power-loss or open-exposure crash proof. Producer PIDs,
instance/run identities, snapshot SHA-256 and checkpoint hashes are in receipts.
Failed restores exit before success PID/instance receipts; those identities are
not retrospectively invented.

## Validation and negative controls

- Exact-tag source checks, wheel hash/import/export probe, Rust buildability,
  isolated locked native build, controller syntax, source scope and preserved
  N2-02 identities were checked. `cargo fmt` was unavailable in the minimal
  container toolchain; no formatter pass is claimed.
- Genuine negative refusals: wrong source, binary and dependency identity;
  missing/corrupt/truncated native snapshot; missing/corrupt/truncated native
  anchor source; wrong replay instance identity; and no venue reconciliation.
  Raw errors distinguish native hash/open failures from source guards.
- The replay identity control checks source-instance binding, not a deliberately
  duplicated event-store sequence. The duplicate-fill control **did not reach**
  its native duplicate application because normal replay failed first. Full
  replay-collision/duplicate-effect coverage therefore remains unverified.
- The container was owner-labelled, Redis was empty at each physical entry,
  no host Redis port was published, and its external Docker network was
  disconnected before simulated trades. Only its own loopback was available.
  Restore code constructs no execution client; failure prevents successful
  zero-new-effect receipts. Owned Redis and the container were stopped afterward.
- No v1 physical test was rerun. Four N2-02 Git blobs and the existing v1 lock
  were preserved. Original N2-02 ZIP SHA-256 was reverified as
  `08d6fee2203b34df44ce082a3b2dd0be33fba41d19f3f505f4dddf1b341bcec2`.
  No unrelated full release suite was run under this disjoint T2 package.

## Traceability and decision

| WP requirement | Section | Evidence | Disposition |
| --- | --- | --- | --- |
| Refreshed base, #746, no collision, isolation | 3 | owner preflight receipts | satisfied |
| Exact-tag API/buildability/provenance | 3 | source audit, wheel probe, Rust logs/lock | satisfied with Windows limits |
| Actual native economics | 5 | four native producer checkpoints | satisfied |
| Complete healthy/crash restore and idempotency | 5 | eight errors and Redis hash comparisons | failed |
| Corruption and source guards | 5 | eleven refusal logs | observed; narrower collision control disclosed |
| Duplicate fill and recovered zero-effects | 5 | duplicate control log, failed normal restores | unverified / masked |
| Exact scope and original identities | 6 | six-file inventory, diff check, native-source and original-blob audit | satisfied |
| Owner ZIP/report and exact-head publication | 6–7 | final owner A–I report and PR receipts | partial-evidence publication; never N2 proof |

Installed skills applied: pre-draft inspector, readiness preflight, minimum-test
plan, one-shot WP review, CPW migration parity, canonical evidence audit, runtime
authority review, PR/evidence reconcile, Ponytail, Ponytail review, systematic
debugging and verification before completion. All eight locator runs returned
`SOURCE_LOCATED` under Python isolated mode; an earlier non-isolated locator
failed from its `inspect.py` shadowing the standard library. No locator is a
readiness or acceptance certificate. No subagents or other chats were operated.

**Decision:** retain one partial-evidence PR; no merge or N2 acceptance.
**Single next action:** a new bounded WP to qualify the exact upstream native
cache-bootstrap/snapshot-tail contract without preloading incompatible current
orders, including duplicate-effect and failure-atomicity evidence. No custom
replay or ledger, runtime cutover, or engine-version decision is implied.
