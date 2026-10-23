# CPW-NAUTILUS-N2-HISTORY-ROUTE-01 — PARTIAL / NATIVE_V2_ROUTE_FAILED

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
