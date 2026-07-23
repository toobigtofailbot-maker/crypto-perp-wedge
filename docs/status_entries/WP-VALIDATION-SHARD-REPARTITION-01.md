# WP-VALIDATION-SHARD-REPARTITION-01 - Bounded full-suite shard profile

- Base/branch/worktree:
  `311ee55669a584dfdd6dc9fbb52438f8334345af` on
  `codex/wp-validation-shard-repartition-01` in
  `C:\GitHub\crypto-perp-wedge-wp-validation-shard-repartition-01`.
  `origin/main` was exactly the authorized base and no open PR overlapped at
  package start.
- Blocker evidence: the preserved KDAUTH 16-shard JSON timed out with
  `tests/test_research_query.py` co-scheduled with nine other files at
  1,800.031 seconds and no test failure. The brief records a later 32-shard
  timeout. Reconstructing the current staged KDAUTH Git-index assignment places
  `tests/test_research_query.py` in zero-based shard 17 with four unrelated
  files; no KDAUTH file or index entry was changed.
- Profile: `full-release-balanced-v1`, version 1, 48 shards, 1,800 seconds per
  shard, maximum four parallel workers. Shard 0 contains only
  `tests/test_research_query.py` and runs exclusively. After it passes, all
  remaining sorted tracked `tests/test*.py` files are assigned index-modulo
  across shards 1 through 47 and run with up to four workers. An exclusive
  failure stops before the parallel phase.
- Proof: profile paths, fields, isolated membership, shard representability,
  and sorted tracked discovery fail closed before pytest. The assignment union
  must equal the tracked set exactly, with no missing, duplicate, untracked, or
  empty assignment. The final assignment manifest is
  `sha256:ea1105d98606e338b71307548e4fb3d4d7bea7e8259fc6ccd064f5ecbc476290`:
  152 discovered, 152 assigned, 152 unique, exact coverage true.
- Contention diagnostic: a dedicated-but-concurrent pre-final run passed 47
  shards but timed out shard 0 at 1,800.016 seconds. Running shard 0 alone
  passed in 979.250 seconds. This proved worker contention, so the final profile
  made the dedicated shard resource-exclusive without changing tests, worker
  maximum, or timeout.
- Focused validation: `tests/test_verify_shard_profiles.py` plus
  `tests/test_verify.py`: 46 passed. Coverage includes determinism,
  tracked-file additions/removals, exact union, isolation, invalid/duplicate/
  stale/impossible profiles, CLI conflicts, raw index-modulo compatibility,
  JSON/Markdown proof, completion/failure/timeout reporting, exclusive
  scheduling, fail-fast behavior, and selected-shard determinism.
- Full-profile acceptance: PASS. All 48 shards executed, completed, and passed;
  2,867 tests passed, 10 skipped, 0 xfailed, and 0 xpassed. Shard 0 was slowest
  at 1,028.954 seconds; the fastest shard was 3.218 seconds. No shard timed out
  and no verifier/pytest process remained.
- Adjacent validation: all 25 registry validators passed; the funding
  provenance validator used the existing read-only canonical data root. All
  1,166 tracked JSON files and 12 JSONL files / 27,585 rows parsed. All 41
  `*.schema.json` files passed Draft 7 meta-validation. All 59 integrity views
  executed: 58 were empty/clean and the one non-empty row was the preserved
  `STRAT-SPEC-0007` legacy hash-scope reproducibility disclosure already present
  on the package base.
- Boundaries: no existing test file, test assertion, skip, xfail, marker,
  research/query semantic, schema, validator, runner/backtester, runtime,
  paper/live, OMS, risk, reconciliation, config, dependency, workflow, KDAUTH,
  production artifact, or `docs/project_status.md` path changed. The KDAUTH
  staged tree and its local data remained read-only.
- Evidence:
  `scratch/WP-VALIDATION-SHARD-REPARTITION-01/full_release_balanced_v1.json`,
  `scratch/WP-VALIDATION-SHARD-REPARTITION-01/pre_exclusive_contention_failure.json`,
  and `scratch/WP-VALIDATION-SHARD-REPARTITION-01/integrity_views.json`.
