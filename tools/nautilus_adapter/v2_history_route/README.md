# Private rc7 native history/bootstrap fixture

## N2-04 restart admission (2026-10-23)

Karl's full authorization, verbatim: "I approve everything so please proceed and always include my full authorization"

This is a private T2 engineering fixture. `restore DIRECTORY` returns
`RECOVERY_ADMITTED_SEALED` only for its qualified native sealed checkpoint;
all failures return `RECONCILIATION_REQUIRED`. Neither disposition permits
orders or resume. The earlier partial-diagnostic CLI modes are refused; only
`restore` and the isolated `duplicate` probe enter the recovery function.
Historical sections and previous evidence below remain unchanged.

The owning controller supplies `CPW_EXPECTED_CHECKPOINT_SHA256` from the
original producer, outside the recovered stores. That digest is required and
is never recomputed from a faulted clone. This fixture trust root is an integrity
and pairing reference, not a signature, globally atomic checkpoint protocol,
production interface, or human recovery authorization.

Before native restore, Rust validates the acknowledged lifecycle, source,
binary/lock/run/instance/PID identity, all Redis record types and contents,
exact event-store file hashes, native ended manifest, durable watermark and
latest anchor. The source and Redis must belong to the same recorded producer.
Redis set ordering is normalized only for native-content comparison; exact
DUMPs are retained and each clone's raw before/after bytes must be unchanged.
Missing, truncated, changed, unacknowledged or differently paired state refuses.

Native `cache_all()`/`build_index()`, `restore_cache_snapshot_blob()` and
`Portfolio` reconstruct and compare the producer's actual identities, frame
bytes/hashes, exact decimal PnL, quantities, commissions and account equity.
No expected numerical answer supplies the recovery state. Approximate native
floating-point price/return metrics are retained in a separate producer witness:
the locked default JSON float parser changes some values by one ULP. Exact
position events, decimal quantities/fees/PnL and source record bytes remain
required. No dependencies or serialization policy are changed.

The duplicate probe selects a genuine cached-order fill whose native position
and trade exist. Nautilus itself assigned that position ID. The native
MessagePack encoder correlates its pre-association capture bytes and encodes
the associated fill for native replay. Two identical repeats and one changed
quantity with the same trade ID must leave all economics and persistent data
unchanged. No position ID, fill identity, fee repair or ledger is invented.

Crash producers are separate owned processes, killed at PID-bound hooks:
before seal; after seal but before Redis close/drain; after drain but before
acknowledgment; and after acknowledgment. The first three must refuse. The
last must reconstruct exactly. No post-seal kill is called an in-flight seal.
A truncated checkpoint write is untrusted and refuses.

Multi-cycle production uses two genuine closed NETTING cycles and current
state. This fixture refuses `ARCHIVE_CONTINUITY_BLOCKED` when earlier frames
have no retained native anchor: the pinned reader exposes the latest anchor,
not a complete earlier-anchor map. It does not manufacture anchors or accept
partial realized PnL. An authentic OPEN-position producer retains its native
account, orders, unrealized PnL and exposure; restart deliberately refuses
`OPEN_EXPOSURE_REQUIRES_RECONCILIATION`. No quote/exposure reconstruction,
venue reconnect, flatten or order resume is claimed.

Reproduce in a new owned network-none Linux container from the verified cached
setup, with a fresh empty `/evidence` mount and the fixture at `/continuation`:

```sh
CARGO_TARGET_DIR=/tmp/cpw-target cargo check --locked --offline -j 4 --manifest-path /continuation/Cargo.toml
CARGO_TARGET_DIR=/tmp/cpw-target cargo test --locked --offline -j 4 --manifest-path /continuation/Cargo.toml
CARGO_TARGET_DIR=/tmp/cpw-target cargo build --locked --offline -j 4 --manifest-path /continuation/Cargo.toml
python3 -m py_compile /continuation/run_proof.py
python3 -B /continuation/run_proof.py
```

The controller owns fresh loopback-only Redis at 6397/6398, performs Stage B
before Stage C, retains raw process errors and DUMPs, and stops owned Redis in
`finally` blocks. Stop the owned container after the run. It refuses an existing
`/evidence/physical-final` directory. See [CPW-NAUTILUS-N2-04](../../../docs/status_entries/CPW-NAUTILUS-N2-04.md) for measured
results and final identity/evidence references. All earlier #747 feasibility
and failure histories below are historical, not N2-04 acceptance evidence.

Full N2 acceptance, funding/margin/liquidation, installed-engine integration,
exchange reconciliation, N3, paper/live activation, capital and merge remain
separate gates. No CPW production path consumes this fixture.


## CURRENT-ARCHIVE-03 continuation (2026-10-23)

Owner authorization, verbatim: "I approve everything so please proceed and always include my full authorization"

This separate diagnostic tests native `cache_all()` plus native
`restore_cache_snapshot_blob()` at one sealed, drained checkpoint. Native
`build_index()` rebuilds the loaded cache indexes. It does not invoke the tail
loader; captured entries are inspected and used only in separate duplicate
controls. The earlier failures below remain historical findings.

Claim frozen before physical work: a measured Redis/redb pairing from one
`NATIVE_SEALED_AND_CACHE_DATABASE_CLOSED` producer, with exactly one archived
frame at index zero for reversal and none for round trip. This is not an atomic
cross-store commit, in-flight crash recovery or complete restart scheme. Native
settling/purging can reset indices and overwrite earlier anchor bytes; general
multi-cycle continuity remains excluded.

Phase instrumentation uses independent cache-only and cache-plus-archive
prefix processes on fresh identical native clones, each closed/drained before
Redis measurement, plus two complete restore processes. Phase differences are
cross-process prefix comparisons, not same-process stage timestamps. Every
process retains raw Redis DUMPs, native type/content and native identity
receipts; archived bytes are compared with the exact producer bytes. The
reversal/healthy quick gate runs first and failure stops the remaining matrix.

**Result: `SEALED_CHECKPOINT_FEASIBILITY_ONLY`.** The single frozen-binary
matrix completed in 290.296 seconds, controller exit 0. All eight full restores
matched exact producer account/current-position/order/fill/trade identities,
archived identities and frame bytes. Reversal recovered 29.836 USDT PnL and
10029.836 equity; round trip recovered 9.916 and 10009.916. Both healthy and
post-seal SIGKILL producers passed two fresh restores. All eight prefix probes,
eight full restores and sixteen controls had zero raw or semantic Redis deltas
relative to their own clone baselines. Native clone creation may re-encode
unordered sets; that source-to-clone raw comparison remains separate.

All twelve negative controls refused without semantic mutation. Missing
snapshot reached native blob-not-found; corrupt/truncated snapshot reached
native BLAKE3 mismatch. Wrong source/binary/lock/run/instance, damaged anchor
sources and resume also refused. Two duplicate sequences were rejected by the
native backend at watermark 7, unchanged. Two captured duplicate fills were
rejected at the native order layer before position application, with unchanged
economics. Current receipts omit their captured position association; prior
verified capture had null `position_id`. Neither result proves associated
position/economic duplicate safety.

Locked offline `cargo check`/`cargo build` and controller syntax passed. Cache
provenance verified 211 active Linux registry packages against lock/archive
hashes and extracted bytes, including all 15 native 0.66.0 crates at the pinned
commit. No production/full-release tests ran under scoped T2 policy. The
read-only audit verified 35 distinct producer/native-receipt PIDs, all native
record/source/checkpoint preservation and the four-path continuation scope.
Initial audit assumptions about registry checksum files, inactive target
packages and successful duplicate application are retained with their errors;
only offline audit code was corrected, with no physical rerun or binary change.

Native bus taps measured no publishes/sends/responses/endpoints in ordinary
restores; source flow constructs no execution engine or client in recovery.
There is no syscall-level venue audit or fabricated client count. All owned
Redis processes and the network-none container are stopped. Full A–I report,
raw logs, exact-head hosted smoke and ZIP digest are in the external owner
evidence/publication record for [draft PR #747](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/747).
Side B independent exact-head review remains separate. No full N2 acceptance,
production remediation, N3, multi-cycle continuity, same-namespace crash
atomicity, in-flight recovery, resume, paper/live/capital or merge is authorized.

## Preserved BOOTSTRAP-REPLAY-02 history

Current continuation: **CPW-NAUTILUS-N2-BOOTSTRAP-REPLAY-02**.
**NATIVE_V2_BOOTSTRAP_ROUTE_FAILED**: fresh-cache replay restores no current
positions and reports zero portfolio PnL. Producer economics pass; recovery does
not. Retain as diagnostic evidence only. Production remediation draftability is
NO; draft PR #747 awaits Side B review. No N2 acceptance, engine upgrade, resume,
paper/live/capital authority or merge follows.

The original HISTORY-ROUTE-01 failure, source at `fc053f9`, and all 190 payloads
remain preserved in owner ZIP SHA-256
`88205135df66802eab22132e5cc512d289feef70c7784df3b2e77abd8fb4c30a`.
The package status entry separates that history from this continuation.

## Native contract

Exact upstream tag `v2.0.0rc7` / commit
`55c0e82053142bce3a5cba4de4221d3929c2d3bc`; published Rust crates 0.66.0.
Cargo manifest/lock are unchanged. Check `.cargo_vcs_info.json` and all lock
checksums before building. CPW's existing Python 3.12 / Nautilus 1.231.0 remains
frozen. The Windows rc7 wheel lacks these durable restore bindings; this fixture
uses native Rust, not a custom Python bridge or rebuilt runtime.

- The native backtest engine, simulated venue and bounded script produce
  orders, fills, accounts and positions. Quotes are 100/105/110 for round trip,
  100/110/90 for reversal, quantity one, 4 bps fees, initial equity 10000 USDT.
  Expected native net PnL: 9.916 / 29.836 USDT.
- Native Redis cache and `EventStoreLifecycle` own persistence, capture and
  archived-cycle snapshots. The execution snapshot callback is released before
  seal; database close drains native writes before checkpoint acknowledgement.
- A fresh native cache loads only currencies and instruments through upstream
  methods. Mutable counts are asserted zero. `cache_all`, mutable preload,
  duplicate suppression and custom prefix replay are forbidden.
- `restore_cache_from_sealed_run` fetches the cache-owned archived blob, checks
  native BLAKE3 identity, restores it and applies native tail events. Latest
  anchor watermark + 1 determines the start; absent anchor means seq 1.
  The archived frame is not a complete order/position/account snapshot.
- Native `Portfolio` derives the result. No numerical answer or synthetic
  position association is injected. Native captured fills have null position
  association; this composition restores no current position. Reversal's
  9.916 archived cycle survives but its 19.92 current cycle does not.

## Reproduction and evidence

Use a **new owner-labelled Linux container with no external network and no
published ports**. Rust 1.99.0, Redis 7.0.15 and Python 3 were reused from the
prior stopped private setup. The original base image was
`rust@sha256:114c7a4425406451c2866b6aafe69fe29b1b298832db1277d411ac73c82d04d6`;
the continuation setup snapshot and package versions are in owner evidence.
Mount a new empty evidence directory at `/evidence`, copy this directory to
`/continuation`. Do not mount old evidence writable or any runtime/Lane A paths.

```sh
CARGO_TARGET_DIR=/tmp/cpw-target cargo check --locked --offline -j 4 --manifest-path /continuation/Cargo.toml
CARGO_TARGET_DIR=/tmp/cpw-target cargo build --locked --offline -j 4 --manifest-path /continuation/Cargo.toml
python3 -m py_compile /continuation/run_proof.py
python3 -B /continuation/run_proof.py
```

Dependencies must be cached during separate pinned setup before going offline.
Freeze the executable before physical work. Do not rebuild while a producer or
controller runs. The controller refuses existing physical evidence or an
external route. It owns a new empty Redis at port 6397 per producer and a new
empty Redis at port 6398 per recovery/fault clone; both bind container loopback.
`CPW_ROUTE_REDIS_PORT` permits only those two private ports.

Native `DUMP` inputs are retained exactly and copied with native `RESTORE`, with
no economic reinterpretation. Unordered Redis sets may re-encode: raw clone
hash equality is recorded separately; native type/content equality is required
at entry. Generic index set sorting is only for content comparison. Each clone
uses its own before/after raw hashes and content snapshot. Authoritative native
records, checkpoint and redb hashes must remain unchanged. This is disposable
test isolation, not a production overlay, rollback or promotion scheme.

Receipts bind real PIDs/process-run UUIDs, original replay source IDs, native
anchor/ranges/payload counts, account/order/fill/trade/frame identity and all
numeric comparisons. Native bus taps measure dispatches; sealed-source hashes
measure event-store appends. No execution engine/client is created during
restore. No literal-zero client/effect receipt is used. A runtime client registry
and syscall-level venue audit are not measured; keep that limitation visible.

Controls apply actual captured seq 7 twice to a separate native backend; the
second append is rejected with unchanged high-watermark. Duplicate-fill
application is gated on qualified economic recovery, so remains unproven in
this result. Source/run/binary/lock, snapshot/source-file corruption and resume
refusal run in independent native clones. Every effect/mutation is retained,
including failed recovery account-event appends and order-list rewrites.

## Observed limits and stop

The clean corrective matrix took 221.27 seconds: four native producers pass,
eight native APIs return without error but economic checks fail with zero PnL
and no current positions. Recovered equity matches. Round trip preserves two
orders/fills; reversal restores only one of three. Account lists grow 8→11 or
13→16 from repeated existing event IDs; order lists remain length three. Do not
equate repeated persisted state events with observed double monetary profit.

Both hard kills occur after native seal/database drain. No in-flight crash,
power-loss, Redis restart, open exposure, funding, margin/liquidation, venue
reconciliation or real-capital proof. Snapshot faults reach native hash checks;
anchor-source faults damage the whole native source file, not only its anchor.
Clone preservation does not prove failure atomicity against an authoritative
same-namespace target. Exact duplicate-fill safety remains unverified.

The initial diagnostic reader-lock defect and premature diagnostic rebuild are
preserved and excluded. The single corrective matrix is consumed; no speculative
rerun or alternate replay implementation is authorized. Stop owned Redis and
container after collecting evidence. Side B reviews the exact updated draft
head before any next WP. See the status entry and owner A–I report/ZIP.
