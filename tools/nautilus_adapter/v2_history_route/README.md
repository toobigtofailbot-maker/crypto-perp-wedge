# Private rc7 native history/bootstrap fixture

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
