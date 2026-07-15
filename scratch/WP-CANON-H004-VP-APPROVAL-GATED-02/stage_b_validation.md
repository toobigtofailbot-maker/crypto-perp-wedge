# WP-CANON-H004-VP-APPROVAL-GATED-02 Stage-B validation

## Crossing and replay

- Stage-B pre-crossing refresh: `HEAD` and `origin/main` both `79329306f1fc84ed06a47822e04e2c5427f19c6e`; no open PR owned the scope at crossing time.
- Authorization match: PASS for ID, target, whole-file hash, contract-core hash, and complete VM/search-family/ordered-axes/population contract.
- Proposal preservation before writer call: PASS, exactly 3,695 LF-only bytes and `sha256:13b40df10af9290d65c971e1e57397e5193cc76fa5852a04b6084ec41c8a275a`.
- Protected writer invocation: PASS on the single invocation; no retry occurred.
- Authoritative bytes equal authorized proposal bytes: PASS.
- Authoritative whole-file hash: PASS, `sha256:13b40df10af9290d65c971e1e57397e5193cc76fa5852a04b6084ec41c8a275a`.
- Contract-core recomputation: PASS, `sha256:4b8e126870c918e88ac42336427c3ba495bcacb6433bd3741b0a01c712bf99f0`.
- Audit shape: PASS, exactly one canonical JSON record plus one LF and no CR.
- Complete historical approval/audit replay and one-to-one alignment: PASS, one approval and one audit record.
- Canonical Strategy Spec, Gate-C line, and bound hashes: unchanged.

## Validators and focused regressions

- Strategy Spec registry validator: PASS.
- Variant Manifest / Sweep Plan validator: PASS; all six existing canonical VM/Sweep pairs preserved.
- Result Population validator: PASS.
- Gate C-VP / external VM / queue control-plane / queue admission suite: `221 passed, 5 skipped`; the skips are the existing Windows symlink-privilege cases.
- Research-query suite: `65 passed`.
- All 58 discovered `v_integrity_*` views ran. Fifty-seven are empty. The sole nonempty row is the unchanged merged-base `STRAT-SPEC-0007` hash-readiness row; this package does not mutate that Spec or query behavior.

## Deterministic full regression

- Two global collections: identical, 2,955 unique nodes each; normalized inventory SHA-256 `d6351e29a8b77d70ca0714e32567be5d4b29f63ee99c3c8815d0746d4655cc38`.
- Tracked 8-shard run: all eight shards PASS; 143 files / 2,696 nodes; 2,689 passed, 7 skipped, 0 failed, 0 errors, 0 internal errors, 0 timeouts.
- Disjoint `tests/research_automation` supplement: 259 passed.
- Combined exact inventory: 2,955 nodes executed once; 2,948 passed, 7 skipped, 0 failed/errors/internal errors/timeouts.
- Exact authorized skip set: missing gitignored normalized D4A CSV; missing gitignored benign-window parquet; five Windows symlink-privilege cases. A direct seven-node run confirmed exactly seven skips.

The standard verifier's aggregate status is non-green only because `diff_scope_summary.py --check-forbidden` has no Gate C-VP authorized-scope class and mechanically flags the two package-explicit `research/` writes. Direct changed-file inspection confirms those paths are exactly the authorized approval and audit outputs. Every validator, focused suite, query suite, integrity view evaluation, and pytest shard completed successfully.

## Superseded non-acceptance attempts

- A combined focused command reached a 10-minute command ceiling with no failure output; it is not counted as passing evidence.
- A parallel split attempt reached a 20-minute ceiling under cross-package CPU contention; an orphaned query process from that attempt was identified and only the owned process tree was terminated. Successful dedicated reruns supersede it.
- The first two-collection reporting command completed collection but its PowerShell hash helper collided with the built-in `h` alias. The corrected rerun produced two identical 2,955-node collections and is the acceptance evidence.

## Boundary and preservation

- New authoritative paths are exactly the one approved file and one audit file.
- Package evidence is confined to `scratch/WP-CANON-H004-VP-APPROVAL-GATED-02/` plus this compact status entry.
- No schema, writer, validator, query-layer, Strategy Spec, Gate-C approval/audit, VM, Sweep, dataset, Gate Q, queue, dispatch, execution, result, candidate, ranking, recommendation, runtime, paper/live, OMS, risk, reconciliation, config, or dependency mutation occurred.
- `VM-0007` and `SWEEP-PLAN-0007` remain absent.
