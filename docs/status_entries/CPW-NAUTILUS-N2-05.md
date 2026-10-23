# CPW-NAUTILUS-N2-05 — private native multi-cycle and open-position continuity

Karl's full authorization, verbatim: "I approve everything so please proceed and always include my full authorization"

## Scope and exact provenance

T2 private isolated fixture, based on `f3a5ece7b27286063de55f069ef2966646b02f8d`
(#749 merged; its five N2-04 files are in ancestry). Branch
`claude/cpw-nautilus-n2-05-native-continuity-01`, executed in a new dedicated
Claude Code worktree from refreshed origin/main. PR: PENDING_PUBLICATION.
Only open #748 was inspected; its six Lane A files are disjoint. Side B owns
independent exact-head review; Karl alone decides merge.

Exactly five allowed files: modified fixture `src/main.rs`, `run_proof.py` and
`README.md`; added `tests/test_nautilus_n2_05_continuity.py` and this fragment.
Cargo manifest/lock, the N2-04 test and every CPW production path are unchanged.
Native source remains rc7 `55c0e82053142bce3a5cba4de4221d3929c2d3bc`, crates
0.66.0; all 15 native crates match their lock checksums and VCS commit. The
installed Python Nautilus 1.231.0 is not touched or integrated.

## Behavior and measured outcomes

**N2_05_NATIVE_CONTINUITY_PASSED.** One counted frozen-binary matrix (binary
`50ab33d576051bf51105a1d5a1ee12581f854d5e537e819793dba92e757718e1`):
**36 cases from 8 genuine native producers, 38 distinct restore PIDs,
558.24 seconds**, controller exit 0, network-none owned container.

- **Two-cycle history, restored twice in one clone:** both native frames
  (indices 0/1, anchored natively at seq 13 and 21; durable watermark 32) and
  the current closed position were restored. Restored cycles are 9.916 + 19.92,
  current 29.916, total realized 59.752 USDT, and equity 10059.752 USDT. All
  account/order/fill/trade/position identities, frame bytes/hashes, commissions
  and quantities equal the producer's.
- **OPEN position, restored twice:** qty 1.000 BTC, same position and account
  IDs, unrealized 10, exposure 110, realized -0.04, and equity 9999.96 USDT.
  Maintenance margin is 5.00, locked 5.00 and free 9994.96. The producer quote
  (110.00, ts 1800000002000000000) is restored exactly. Before that quote was
  applied, the same restore measured unrealized PnL as unpriced (`None`).
  Decision `OPEN_EXPOSURE_RECONSTRUCTED_NO_RESUME`, `NO_NEW_ORDERS / NO_RESUME`,
  venue reconciliation required.
- Native Portfolio initialization attempted the account `RPUSHX`; the clone's
  read-only ACL user denied it (retained `ACL LOG`). Every case has zero raw and
  semantic DUMP deltas and unchanged redb hashes. All 8 producers' stores,
  record bytes and checkpoints are byte-identical after the matrix. No bus
  publishes/sends/responses/endpoints, no tail replay, no execution engine/client.
- Associated duplicates on multi-cycle, open and reversal: two identical replays
  and one same-trade-ID quantity conflict each rejected natively. Economics and
  persistent state are unchanged.
- **28 refusals before any persistent change.** Re-signed defective receipts:
  missing, corrupt, stale, cross-paired and reordered prior anchors. Redis
  frame 0 overwritten (as raw pair mismatch and re-signed) and deleted
  (re-signed). Truncated redb. Missing, altered-byte, stale, wrong-instrument
  and cross-paired quotes. A consistent divergent mark (120) reached native
  economics and refused `RECOVERY_NOT_QUALIFIED`. Also: contradictory order,
  writable connection, both valid-producer cross pairs, and a torn receipt.
- N2-04 regressions on the same binary: sealed one-cycle and zero-cycle restores,
  torn pair, absent/wrong-run/stale-watermark/invalid-marker receipts, and the
  before-seal/after-seal/after-drain crash windows refused. The acknowledged
  window restored exactly.

The anchor list is captured by a pass-through `EventStore` tap on the native
`RedbBackend` the default opener uses. The tap retains each native anchor after
native acceptance; the producer refuses if its last entry differs from the
native latest anchor. The fixture witnesses (59.752, 10059.752, 10, 110, 9999.96)
are controller assertions only. They never feed restoration.

## Validation and evidence limits

- Locked offline cargo check/build: PASS; cargo test: 8 passed (4 new chain/quote).
- Python: N2-05 focused 27 + N2-04 17 = 44 passed. Adjacent native-cache guards
  and paper-state, paper ledger and paper broker suites: 24 passed. Paper-state
  validator: PASS; py_compile: PASS; `git diff --check`: clean.
- One prior diagnostic matrix (`diagnostic-01`, same binary, 36 cases, 552.23 s)
  also passed. It is retained but not counted. Afterwards only the controller's
  ACL-log retention line changed; the counted run used the frozen hashes.
  README/status text changed after the run; the binary and controller did not.
- Hosted smoke is publication evidence only, not native proof. Full pytest/full
  release: NOT RUN under scoped T2 policy.
- Limits: one deterministic BTCUSDT-PERP fixture, single position, linear
  perpetual, no funding. The read-only ACL is fixture isolation, not a production
  overlay. Settle/purge index reuse (the upstream overwrite limitation) is
  detected and refused, not repaired. The quote is producer-retained context,
  not a venue mark or a reconciliation substitute.

Evidence is outside Git at `C:/Users/dersu/Downloads/CPW-N2-05-evidence-20261023`:
counted `physical-n2-05/` (raw DUMPs, receipts, ACL logs, PIDs), `diagnostic-01/`,
frozen hashes and binary, cargo logs, source pins, upstream source and the
cleanup/container receipts. The Side B ZIP digest is in the A–I handoff.

## Boundaries and next dependency

Protected runtime, OMS, reconciliation, risk, overlays, safe mode, kill switch,
configs, schema, validators, query layer, credentials, live/order/capital paths,
Lane A, CI and docs/project_status.md are unchanged. No dependency, engine
upgrade, upstream patch, custom fill replay, synthetic position, direct Redis
economic write or alternative ledger is introduced. The anchor list is
producer-retained provenance of native anchors only. The quote is the producer's
own native observation, applied only to a disposable in-memory cache.

This closes two measured N2 recovery gaps in an offline fixture only. It is not
full N2 or production ownership. Funding, liquidation and margin-call parity,
installed-version integration, venue reconciliation, N3 exchange mechanics and
human-gated paper/live/capital remain separately scoped. Manual owner
engineering steps: none.
