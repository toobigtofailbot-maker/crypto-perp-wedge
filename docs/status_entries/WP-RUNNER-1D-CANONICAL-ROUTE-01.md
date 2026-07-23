# WP-RUNNER-1D-CANONICAL-ROUTE-01 - Validated canonical 1d route

- Base/branch: `8371a7ee456610efeb2a854effd0a20a2ffbfff0` on
  `codex/wp-runner-1d-canonical-route-01` in the dedicated package worktree.
  The old blocked branch remains at its prior commit and was not mutated.
- Route decision: Route A. The existing direct public Binance archive snapshot
  rebuilds the committed catalog byte-for-byte; no acquisition, network access,
  regeneration, dependency change, or Karl data gate was required.
- Bound OHLCV identity: dataset
  `binance_usdtm_btcusdt_ohlcv_1d`; catalog SHA-256
  `51fc09918841cd3ac353efe375af91a4732080571f9b1af634f5d1a426217adb`;
  Parquet SHA-256
  `c6e2e7ce030db6a710d95e48325fc77b27efbbdd441199b3d7458d4394795802`;
  200,961 bytes; 2,293 completed UTC-daily rows; coverage
  `2020-01-01T00:00:00Z` through `2026-04-11T23:59:59.999000Z`; canonical
  column order; zero gaps, duplicates, missing bars, boundary violations, or
  partial/open bars.
- Runner surface: `canonical_1d=True` and `--canonical-1d`, explicit and
  default-off. Canonical 15m, 4h, and 1d selectors are mutually exclusive.
  The 1d route accepts no arbitrary OHLCV path and rejects missing, escaped,
  backslashed, linked, stale, mismatched, malformed, gapped, duplicated, or
  partial input. Catalog and source bytes are checked before use and again
  after validation/read. No runner network path exists.
- Funding/scientific identity: the route consumes the merged canonical funding
  input unchanged and requires funding-on for `STRAT-SPEC-0007`. The complete
  1d catalog/source/schema/coverage/validation identity and complete funding
  identity appear in scratch metadata and feed existing deterministic input
  and result identities. A real-byte read-only check bound 6,877 actual funding
  events and compiled `VAR-000001`; no H-004 sweep or Result Population was
  executed.
- Changed files:
  `tools/research_runner/run_offline_sweep.py`,
  `tests/test_offline_runner_canonical_1d.py`,
  `tests/test_register_binance_usdtm_1d_lineage.py`, and this status entry.
- Validation: focused 1d/lineage tests passed; canonical 15m/4h, funding,
  compiler, backtest, and evaluation regressions passed; external-readiness
  writer/contract and focused query checks passed; all 25 registry validators
  passed (the funding validator used the authorized local data root); 1,162
  JSON files and 12 JSONL files / 27,585 rows parsed; all 59 integrity views
  ran, with 58 empty and one preserved STRAT-SPEC-0007 legacy hash-scope
  reproducibility disclosure; the accepted complete 32-shard pytest profile
  passed 2,842 tests with 10 environment-limited skips across all 151 tracked
  test files.
- Preservation/boundary: H-004 Spec/VM/Sweep, readiness, queue/Gate-Q, funding
  provenance, `lib/backtest.py`, and `lib/evaluation.py` are unchanged from
  `origin/main`. No H-004 execution, dispatch/event, Result Population,
  candidate, lifecycle, runtime, paper/live, OMS, risk, reconciliation,
  broker/exchange, credential, order, position, balance, capital, config,
  dependency, workflow, scheduler, schema, validator, query-layer, or
  `docs/project_status.md` change or action occurred.
