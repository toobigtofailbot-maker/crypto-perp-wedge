# WP-RUNNER-FUNDING-PROVENANCE-CONTRACT-01 - Bind validated funding provenance

- Package class: Tier 3 funding-data provenance contract and exact local-data
  binding.
- Approved base/head: `1c22edf602f748ed03d9304c66b4b40cd6f0d601` on
  `codex/wp-runner-funding-provenance-contract-01`.
- Karl gate: exact-content Stage-B approval received for the schema,
  provenance artifact, contract, validator, tests, raw-data identity, boundary
  rule, producer-history caveat, and nine-path allowlist frozen in
  `scratch/WP-RUNNER-FUNDING-PROVENANCE-CONTRACT-01/stage_a_packet.md`.
- Authoritative scope: adds the canonical funding provenance contract, closed
  Draft 7 schema, one exact BTCUSDT Binance USDT-M funding provenance artifact,
  an offline read-only validator, and focused regression tests. The three
  Stage-A evidence files are retained unchanged.
- Bound data: gitignored Parquet SHA-256
  `5f0da7478ccf3514af41dff9958b579cd2f797a2716001b0fa10a11059912798`,
  `126987` bytes, `7220` rows, coverage `2019-09-10T08:00:00Z` through
  `2026-04-12T16:00:00Z`, zero duplicate timestamps, and zero missing nominal
  8-hour slots.
- Semantics: actual exchange timestamps only; boundary
  `(previous_bar_timestamp,current_bar_timestamp]`; same-timestamp new entries
  excluded; no timestamp repair, interpolation, forward fill, backfill, or zero
  substitution. The producer's keep-first deduplication is recorded while the
  pre-dedup input and removed-row counts remain unevidenced; the exact bound
  Parquet has zero duplicate timestamps.
- Validation: all five promoted production hashes match Karl-approved bytes;
  Draft 7 meta-validation and exact production-data validation pass; all 1115
  JSON files and 12 JSONL files parse; all 25 registry validators pass; all 58
  integrity views reproduce the Stage-A baseline (57 empty and one preserved
  `STRAT-SPEC-0007 hash_status=not_computed` row); focused funding tests report
  `25 passed, 1 skipped`; all 145 tracked test files pass across the complete
  deterministic 16-shard full-pytest partition, with the new funding test also
  executed explicitly. The skip is the documented Windows symlink-fixture
  limitation.
- Non-authority: no runner integration, `canonical_1d`, H-004 execution or
  dispatch, Result Population work, data acquisition or mutation, backtest or
  funding-math change, Option-C schema change, scheduler/autonomy, runtime,
  paper/live, OMS, risk, or reconciliation work is authorized or performed.
