# Private native rc7 history-route fixture

CPW-NAUTILUS-N2-HISTORY-ROUTE-01 only. This executable has no production import
or entry point. It does not upgrade CPW's Python 3.12 / Nautilus 1.231.0 environment.
It grants no resume, paper/live/capital, migration, or N2 acceptance authority.

**Observed result: NATIVE_V2_ROUTE_FAILED for this tested composition.**
`cache_all` preloads current orders, and subsequent native event-store replay
rejects an already-cached `OrderInitialized`. All eight corrective-run restores
fail; native Redis record hashes also change before rejection. The duplicate-fill
control is masked by this earlier error. This fixture is retained as failed
diagnostic evidence. It does not disprove other upstream bootstrap/replay
compositions. The one clean corrective physical rerun is consumed; another
attempt requires a new bounded WP. See the status entry for the full limitations.

## Native ownership

The exact upstream tag is `v2.0.0rc7`, commit
`55c0e82053142bce3a5cba4de4221d3929c2d3bc`. Its published Rust crates are
`0.66.0`; every Nautilus dependency is pinned to that version. `Cargo.lock`
pins the dependency tree and registry checksums. Verify the downloaded
Nautilus crates' `.cargo_vcs_info.json` against this commit before running.

The Python rc7 Windows wheel imports successfully but does not bind
`Cache.snapshot_position_encoded`, `load_snapshot_blob`, or
`restore_snapshot_blob`, and exposes no event-store replay module. The fixture
therefore uses the public Rust APIs:

- `BacktestEngine`, a three-quote scripted strategy, and the native simulated
  venue generate orders, fills, positions, account balances and portfolio PnL.
- `RedisCacheConfig.create` and `Cache.set_database` provide upstream-owned
  persistence. The execution engine calls `snapshot_position_encoded` through
  the callback from `EventStoreLifecycle.snapshot_anchorer`.
- `EventStoreLifecycle.open` captures the native bus traffic into its own redb
  store. Release the execution engine's snapshot callback before `seal`, as the
  upstream kernel does. `Cache.dispose` closes the native database and drains
  queued writes. CPW implements no snapshot serializer or economic replay.
- A fresh process uses `Cache.cache_all` and
  `restore_cache_from_sealed_run`; native code loads/verifies/restores the
  anchored snapshot and replays the tail. `Portfolio.initialize_positions`
  computes the native result. No execution engine or venue client is built in
  restore mode.

The source identity checks and JSON receipts are evidence guards, not an
accounting ledger. Redis `DUMP` hashes measure whether restores changed native
records. The duplicate-fill control applies a genuine captured fill a second
time through `apply_cache_replay_entry` and requires native rejection or no
change to observed state. Resume always fails with `RECONCILIATION_UNVERIFIED`.

## Isolated reproduction

Use a dedicated Linux x86_64 container, Rust **1.99.0**, Redis and Python 3.
The execution used official image
`rust@sha256:114c7a4425406451c2866b6aafe69fe29b1b298832db1277d411ac73c82d04d6`.
Mount an empty owner-only evidence directory at `/evidence` and copy this
directory to `/proof`. Label the container with this WP identity; do not mount
CPW runtime directories, credentials, Lane A, or the N2-02 environment.

During setup only, install Redis and the Linux linker, then build:

```sh
apt-get update
apt-get install -y --no-install-recommends redis-server lld
CARGO_TARGET_DIR=/evidence/build_gate/target cargo build --locked -j 4 --manifest-path /proof/Cargo.toml
mkdir -p /evidence/native-redis
redis-server --bind 127.0.0.1 --port 6397 --appendonly yes --appendfsync always \
  --daemonize yes --dir /evidence/native-redis --save ""
redis-cli -p 6397 DBSIZE
```

Record the image digest, package versions, crate provenance, exact build command,
binary hash and lock hash. Disconnect the container's external Docker network
before running any simulated trades. The only remaining connection is the
container's own loopback Redis. The controller checks for no external route
and an empty Redis before creating its physical directory.

```sh
python3 -B /proof/run_proof.py
```

Preserve stdout/stderr, all files under `/evidence/native-physical`, Redis AOF
files, binary and source hashes. The controller exits 2 when comparisons fail;
its JSON result preserves mismatches. An assertion/timeout is a diagnostic
failure, not proof of an upstream economic defect. Do not rerun into existing
state. Preserve a diagnostic run and use at most the WP's one clean corrective
physical rerun with a fresh owned Redis directory. Stop the owned Redis and
container after collecting evidence. No Redis port is published to the host.

## Limits of the proof

Initial equity is 10000 USDT, fees 4 bps, quantity one, and quotes have no spread.
Round trip quotes are 100/105/110; reversal quotes are 100/110/90. Expected net
PnL is 9.916/29.836 USDT. Synthetic timestamps are fixture times, not evidence
collection timestamps. Producer instances, event-store run IDs and fill IDs are
native identities and need not repeat between runs.

The hard termination occurs **after the native event store is sealed and the
cache database is closed and drained**, while the owned producer is held alive.
It proves recovery from this acknowledged closed checkpoint only. It does not
prove recovery during an in-flight write, an unsealed log, a Redis restart,
host-power loss, open exposure, funding, liquidation or margin stress, or venue
reconciliation. These limitations must remain visible even if every bounded
comparison passes. See the package status entry for observed results.
