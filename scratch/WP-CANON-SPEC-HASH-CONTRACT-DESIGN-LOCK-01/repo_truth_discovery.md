# Repo-truth discovery

- Package-start validation base: `origin/main` at `1c22edf602f748ed03d9304c66b4b40cd6f0d601`.
- Same-PR refresh preflight: old head `9f64707afef85dbd6cf2de801d69b0ee2972beed`, old merge base `1c22edf602f748ed03d9304c66b4b40cd6f0d601`, and old ahead/behind `3/3` relative to refreshed `origin/main`.
- Refreshed final validation base: `origin/main` at `64f3757c6ee0ae5249dce52babd6a5811347d719`. The rebase completed without conflict at rebased pre-follow-up head `50e776007212e54fea42166e9714fb4c957d98b9`; final merge base equals refreshed `origin/main`, refreshed `main` is an ancestor, and post-rebase ahead/behind is `3/0` before the follow-up commit.
- PR #666 was the only open PR at refresh preflight. Merged PR #665 accounts for the intervening 30-file dispatch package; its paths are distinct from this package's 24 PR paths, the exact intersection is empty, and no PR #665 file is edited here.
- No merged external Strategy Spec content-readiness fact, schema, validator, query view, or equivalent H-C design lock existed.
- The prior `codex/wp-canon-spec0007-hash-readiness-integrity-01` branch had no committed or uncommitted implementation beyond merged base. Its controlling blocked result is the active package's finding that no known algorithm reproduces every historical internal `canonical_spec_hash`.
- `tools/registry/validate_variant_sweep_artifacts.py::canonical_json_bytes` reproducibly hashes all seven complete Strategy Specs and every result equals the corresponding VM parent `strategy_spec_hash`.
- `tools/canon_intake/queue_admission.py::repo_canonical_json_v1` uses the same sorted/compact/UTF-8/Unicode byte rules for float-free queue records but rejects in-memory floats. The Strategy Spec content contract therefore anchors to the existing VM lineage helper and does not weaken the queue helper.
- STRAT-SPEC-0007 remains 19,880 bytes with raw SHA-256 `sha256:b23ebc1093df51b7fab5e39c46fd2b96b5e71d35300134eb319a5cbc32d0857c`, full canonical SHA-256 `sha256:8b6f7dd7a3e12b934c1038ae113aa25aa79f0b3cc6a336b25bd58164f5cc92db`, Git blob `ac5a493cb5b7d1a5de3647df07bd3151a8e4a440`, and embedded status `not_computed`.
- VM-0007 and SWEEP-PLAN-0007 remain present and unchanged; all Strategy Specs, VMs, and Sweeps are recorded in `preservation_manifest.json`.
- All 58 merged-base `v_integrity_*` views ran. The sole nonempty result is the existing STRAT-SPEC-0007 `not_computed` row in `v_integrity_strategy_spec_hash_readiness`.
- No production external readiness directory or fact exists. H-004 remains not dispatch-ready.
- H-C production scope is closed to Strategy Specs explicitly bound by the H-004 prerequisite chain. `STRAT-SPEC-0007` is currently the only authorized production spec; the scratch-only `STRAT-SPEC-9000` fixture is not in scope and grants no production authority.
