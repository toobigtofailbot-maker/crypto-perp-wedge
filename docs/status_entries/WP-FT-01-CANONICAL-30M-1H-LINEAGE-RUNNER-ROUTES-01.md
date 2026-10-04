# WP-FT-01 Canonical 30m/1h Lineage and Runner Routes

## Repository and publication state

- Package: `WP-FT-01-CANONICAL-30M-1H-LINEAGE-RUNNER-ROUTES-01`
- Branch: `codex/wp-ft-01-canonical-30m-1h-lineage-runner-routes-01`
- Locked base and `origin/main`: `c6ae5c1d81b095c128579b0633da0d0908c3f385`
- Validated semantic implementation head:
  `c46feb28f4fa9497a403972bcc8c98b390c835ab`
- Publication-evidence commit: the status-only descendant containing this
  record on PR #725; no implementation or lineage bytes changed after the
  validated semantic head
- Pull request: #725
  (`https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/725`)
- Self-merge: no

The final committed comparison is restricted to the 13 paths listed below.
No `docs/project_status.md`, FT-02, protected runtime, paper/live, OMS,
reconciliation, risk, capital, configuration, dependency, acquisition, or
network surface is in scope.

## Exact 13-file scope

Modified:

1. `docs/decisions.md`
2. `tools/research_runner/run_offline_sweep.py`
3. `tests/test_offline_research_runner.py`

Created:

4. `tools/data/resample_binance_usdtm_15m_to_30m_1h.py`
5. `tests/test_resample_binance_usdtm_15m_to_30m_1h.py`
6. `research/data_slices/binance_usdtm_btcusdt_30m/binance_usdtm_btcusdt_30m_20200101_20260411.validation_report.json`
7. `research/data_slices/binance_usdtm_btcusdt_30m/binance_usdtm_btcusdt_30m_20200101_20260411.derivation_report.json`
8. `research/data_slices/binance_usdtm_btcusdt_30m/binance_usdtm_btcusdt_30m_20200101_20260411.catalog_slice.json`
9. `research/data_slices/binance_usdtm_btcusdt_1h/binance_usdtm_btcusdt_1h_20200101_20260411.validation_report.json`
10. `research/data_slices/binance_usdtm_btcusdt_1h/binance_usdtm_btcusdt_1h_20200101_20260411.derivation_report.json`
11. `research/data_slices/binance_usdtm_btcusdt_1h/binance_usdtm_btcusdt_1h_20200101_20260411.catalog_slice.json`
12. `docs/data/2026-10-binance_usdtm_30m_1h_derived_catalog_and_slice_identity.md`
13. `docs/status_entries/WP-FT-01-CANONICAL-30M-1H-LINEAGE-RUNNER-ROUTES-01.md`

## Decision and lineage

D2-021, **Five-Timeframe Canonical Base and Feature Parent Identity**, records
Model B. Canonical 30m and 1h derive deterministically from the exact canonical
D4 15m base. Direct 30m/1h Parquets are diagnostic only and do not create dual
authority. No tolerance, repair, splicing, averaging, or source switching is
authorized. The existing canonical 15m, D4-derived 4h, and direct 1d bases stay
unchanged. D2-021 creates no FT-02, autonomy, promotion, runtime, paper/live,
risk, capital, or economic authority.

The exact parent normalized SHA-256 is
`c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`.

- 30m: 110064 rows, `2020-01-01T00:00:00Z` through
  `2026-04-11T23:30:00Z`, CSV SHA-256
  `05c5857d668d2d12bcc743a13ad92a34590bc1c37ff8ea1f5f54d5d1fbf379ba`,
  identity
  `binance_usdtm_btcusdt_ohlcv_30m:sha256:090f4fac75bedf64fd19dbbeec141169bd7eaeaaaef187038878a6242022b94e`.
- 1h: 55032 rows, `2020-01-01T00:00:00Z` through
  `2026-04-11T23:00:00Z`, CSV SHA-256
  `28b750e90ee9957e6fc22811c4ae632355a239f2b958ed65c9b3c56cb2d9e79e`,
  identity
  `binance_usdtm_btcusdt_ohlcv_1h:sha256:9e0faa68eb84b1aa176a5857432840b71a6049765963637236241b91ae807877`.

Both generated CSVs and all six metadata artifacts reproduced byte-identically
from the same parent bytes. Their committed JSON byte policy is UTF-8 LF.

## Diagnostic stop and authorized resumption

The original direct-source zero-mismatch gate stopped the first implementation
pass. The diagnostic-only follow-up changed no tracked file and independently
proved:

- D4 15m to derived 30m: zero mismatches;
- D4 15m to derived 1h: zero mismatches;
- derived 30m to derived 1h: zero mismatches;
- pinned direct 30m/1h sources still disagree with the derived outputs and are
  not mutually consistent in every substantive window.

The accepted classification is `DIAGNOSTIC_SOURCE_DIVERGENCE`. Karl's resume
authorization replaced the original direct-source zero-mismatch criterion with
the independently proven canonical-parent and internal-consistency criteria.
Canonical D4-derived authority remains unchanged. The detailed mismatch counts,
source hashes, and substantive windows are recorded in the companion data doc.

## Runner routes and boundaries

The offline runner adds default-off `--canonical-30m` and `--canonical-1h`
routes. The 15m/30m/1h/4h/1d selectors are mutually exclusive. Each new route
fails closed on lineage, report, CSV, parent, range, cadence, gap, duplicate,
partial-window, or timeframe disagreement and binds the selected data identity
and provenance into the existing scientific/result identity path. Research
feature-table inputs remain restricted to `--canonical-15m`. Real-byte smoke
loads confirmed the 30m and 1h identities and timeframes without writing a
Result Population or lifecycle artifact.

## Validation evidence

Pre-commit evidence:

- baseline: 249 passed, 1 skipped;
- resampler unit suite: 18 passed;
- complete runner test file: 123 passed, 4 warnings;
- focused FT-01 suite: 141 passed, 4 warnings;
- unchanged 4h/1d, dispatch, evaluation, funding, provenance, and backtest
  regressions: 261 passed, 4 skipped, 8 warnings;
- Strategy Spec, Variant/Sweep, Result Population, candidate-registry, and
  paper-state validators: pass;
- all 62 discovered `v_integrity_*` views executed: 60 clean, with only the two
  repo-documented baseline disclosures (`v_integrity_execution_streams` for the
  intentionally absent H-004 local stream and
  `v_integrity_strategy_spec_legacy_hash_scope_reproducibility` for
  `STRAT-SPEC-0007`); FT-01 changes neither surface;
- real-byte 30m and 1h route smoke: pass;
- independent full-corpus parent and 30m-to-1h recomputation: zero mismatches;
- deterministic scratch reproduction: all eight generated outputs
  byte-identical.

Committed exact-scope validation passed at the semantic implementation head:
exactly 13 paths, all six lineage artifacts independently authorized under
`research-data-slice-lineage`, zero rejected authorizations, zero forbidden
matches, and zero allowlist violations.

Mandatory full release passed at exact semantic implementation head
`c46feb28f4fa9497a403972bcc8c98b390c835ab` using
`full-release-balanced-v1`. All 187 tracked test files were uniquely assigned
once across 48 completed shards. Failed shards: 0. Timed-out shards: 0. The
slowest shard was shard 41 at 1202.125 seconds.

## Preservation

The package creates no Strategy Spec, Variant Manifest, Sweep Plan, Result
Population, candidate, lifecycle, or trial-log artifact. It does not change the
existing canonical 15m/4h/1d artifacts or routes. Validation-only ignored input
corpora and generated CSVs were not tracked or staged and were removed from the
dedicated worktree after accepted final validation.
