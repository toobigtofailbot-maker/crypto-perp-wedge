# CPW-NAUTILUS-N2-04 — private native restart safety admission

Karl's full authorization, verbatim: "I approve everything so please proceed and always include my full authorization"

## Scope and exact provenance

T2 private isolated fixture, based on `617a2d645800d3a44e2bfcf133384903bea35dd0`
(#747 merged). Dedicated branch `codex/cpw-nautilus-n2-04-restart-safety-01`;
worktree `C:/GitHub/crypto-perp-wedge-worktrees/cpw-nautilus-n2-04-restart-safety-01`.
PR: [#749](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/749),
open non-draft for independent Side B review. No merge.
Only open #748 was inspected: its six Lane A files are disjoint. Side B owns
independent review; Karl alone decides merge. Historical references to a Main
role do not create a current additional approval step for this authorized WP.

Exactly five allowed files: modified fixture `src/main.rs`, `run_proof.py` and
`README.md`; added `tests/test_nautilus_n2_04_recovery.py` and this fragment.
Cargo manifest/lock and all CPW production paths remain unchanged. The fixture
has no production consumer. Native source remains rc7 commit
`55c0e82053142bce3a5cba4de4221d3929c2d3bc`, crates 0.66.0; the separately installed
Python Nautilus 1.231.0 is not upgraded, patched or integrated here.

## Behavior and measured outcomes

**N2_04_SAFETY_GATE_PASSED**, with conservative archive/open refusals.
Rust admission checks the original externally supplied checkpoint digest,
acknowledged lifecycle, source/binary/lock/run/instance/PID, all native Redis
types/contents, event-store file hashes, ended manifest, watermark and anchor.
Only qualified sealed native current-cache plus archived-frame reconstruction
returns `RECOVERY_ADMITTED_SEALED`; failures return `RECONCILIATION_REQUIRED`.
Recovery constructs no execution engine/client and invokes no tail replay,
venue reconnect, flatten or resume. Neither result grants order authority.

One complete frozen-binary matrix: **16 cases, 7 authentic native producers,
250.147 seconds**. Two ordinary sealed restores and the associated duplicate
probe admitted exact state; **13 invalid/unsupported checkpoints refused**.
Every recovery/probe had zero raw/semantic Redis deltas and unchanged redb bytes.
Healthy reversal reconstructed 29.83600000 USDT realized PnL, .16400000 total
fill commissions, and 10029.83600000 USDT equity, with native identity/frame
bytes and hashes conserved.

The genuine cached-order fill carries its engine-assigned non-null position ID
and a trade present in that cache position. Native MessagePack encoding matches
its original pre-association event-store capture. Two identical replays and one
conflicting quantity with the same trade ID were rejected by native order
handling, preserving quantities, native PnL, commissions, fills, account, bus
traffic and persisted data. This closes the prior null-association limitation
for this bounded route; it proves neither arbitrary venue replay nor funding.

Separate owned producer PIDs were killed before seal, after seal/before Redis
close, after drain/before acknowledgment, and after acknowledgment. The first
three refused; the last reconstructed exactly. Both valid-producer cross-pair
controls, a torn account record, and five invalid authority receipts refused.
Post-seal termination is not described as an in-flight seal or power-loss test.

Multi-cycle production retained genuine frames at indices 0 and 1 and native
59.75200000 realized PnL / 10059.75200000 equity. The native reader retains only
the latest anchor (/1); this fixture refuses `ARCHIVE_CONTINUITY_BLOCKED`
without manufacturing an earlier anchor or accepting incomplete PnL. This is
conservative route refusal, not an upstream-wide impossibility claim.
The authentic open position had 1.000 BTC quantity, 10.00000000 unrealized PnL,
110.00000000 exposure and 9999.96000000 account balance; restart refused
`OPEN_EXPOSURE_REQUIRES_RECONCILIATION`. No automatic exit was attempted.

## Validation and evidence limits

- Focused Python: 17 passed; adjacent native-cache guards and paper-state,
  paper broker/ledger: 24 passed; paper-state validator: PASS; py_compile: PASS.
- Final locked offline native cargo check/build: PASS; cargo test: 4 passed.
  All 211 active cached packages and 15 native crate pins were verified.
- Two pre-matrix fixture diagnostics are retained: JSON float-parser ULP drift,
  then an incorrect JSON assumption for native MessagePack. No native invariant
  failure was hidden. Decimal economics and exact native events remain required;
  approximate position metrics are retained separately as producer witnesses.
- Final review disabled obsolete diagnostic CLI entrypoints, which otherwise
  could have received an admission label. The producer/recovery bodies and
  controller are byte-identical to the matrix source; only two dispatcher lines
  differ. Exact-source reuse evidence is retained. Final rebuilt binary separately
  passed one fresh sealed producer/restore and four CLI refusals. The complete
  matrix was not repeated or misattributed to that final binary.
- Final-head hosted smoke is recorded in the external A-I report and actual
  PR checks; it is publication evidence only, not native recovery proof.
- Full pytest/full-release: NOT RUN - scoped T2 private fixture policy; not used
  as N2 or merge evidence. No earlier v1 physical matrix is counted as this proof.

Evidence is outside Git at
`C:/Users/dersu/Downloads/CPW-N2-04-evidence-20261023`, including full A–I report,
source snapshots, raw DUMPs, exact hashes, process receipts, immutable native
inputs/outputs and final publication evidence. The Side B ZIP and its digest
are recorded in the final A–I handoff; previous #747 bundles remain untouched.

## Boundaries and next dependency

Protected runtime, OMS, reconciliation, risk, overlays, safe mode, kill switch,
configs, schema, validators, query layer, credentials, live/order/capital paths,
Lane A, CI and docs/project_status.md are unchanged. Recovery remains read-only
against native economics. No dependencies, engine upgrade, upstream patch,
custom fill repair, alternative ledger or execution activation is introduced.
All owned Redis processes and the network-none proof container are stopped
before delivery; the final report contains the cleanup receipt.

This bounded safety verdict is not full N2/production ownership. Archive and
open-exposure reconstruction remain unproven. Applicable funding, margin,
liquidation, version integration and exchange reconciliation need separately
scoped proofs before N2 completion, then N3 and human-gated paper/live/capital
activation. Side B reviews the exact final head; Karl's merge decision remains
separate. Manual owner engineering steps: none.
