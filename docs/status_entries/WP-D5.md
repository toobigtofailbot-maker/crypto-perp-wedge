# WP-D5 / Data Block 1 - First Real-Data Canonical Sweep

## WP Id / Title

WP-D5 / Data Block 1 - First real-data canonical sweep.

## Branch / PR

- Branch: `codex/data-block-1-d5-first-real-data-canonical-sweep`
- PR: `#415`

## Package Class

T3 canonical evidence write.

## Scope Summary

Creates exactly one canonical real-data result population for the frozen parent
set `STRAT-SPEC-0001` / `VM-0001` / `SWEEP-PLAN-0001`, using the D4A Binance
USDT-M BTCUSDT 15m real-data slice directly.

D5 creates canonical real-data evidence only. It does not interpret results,
rank variants, recommend a strategy, approve paper/live readiness, promote
anything, contact runtime/paper/live paths, or mutate protected execution
surfaces.

## Changed Files

- `research/result_populations/RP-4492.result_population.json`
- `docs/status_entries/WP-D5.md`
- `docs/project_status.md`
- `tests/test_offline_research_runner.py`
- `tests/test_research_query.py`

The test changes are stale corpus assertion updates for the now two-entry
result-population corpus: `RP-2134` fixture-backed and `RP-4492` canonical
real-data.

## Result Population

- Result population ID: `RP-4492`
- Path: `research/result_populations/RP-4492.result_population.json`
- File SHA256: `22b5976e695c50c86aab9cf62bfa3d4c2b0bbd41b6ad7833ad4a43ab2bc8734e`
- Result population identity hash:
  `sha256:2a9cee1b1ba32d9f98f879aa4c1ef95e2f5b75b7348e1084e66afe80f77bb32c`
- Input identity hash:
  `sha256:8fca9c6f6238f4fd5712420921faa649a1a182866adb22f1d5f3680b850a535c`
- Provenance class: `canonical_real_data`

## D4 Provenance Proof

- D4 catalog ref:
  `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
- D4 slice identity:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- D3 validation identity:
  `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`
- D2 import report current committed file SHA256:
  `543c944f727b2b9a7ad06742946ecefc91aa8b94723f46509e4041f622ef57ad`
- D4 catalog artifact current committed file SHA256:
  `f7b98c4d7759b6ba0c9bf8559bcea5e3311d3abe877930da254aeca96f53105a`

## Row / Range / Gap / Duplicate / Source Facts

- Row count: `220128`
- Expected row count: `220128`
- Timestamp range: `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`
- Gap facts: `gap_count=0`, `missing_bar_count=0`, `gaps=[]`
- Duplicate facts: `duplicate_group_count=0`, `duplicate_row_count=0`, `duplicates=[]`
- Raw source SHA256:
  `343b639e35ce79824d26bddf6d70af2641c9d76003301e303f83cdf61d4feab4`
- Normalized CSV SHA256:
  `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`

## Denominator / Variant Completeness Proof

- Committed denominator: `7`
- Variant result rows: `7`
- Outcome counts sum: `7`
- Represented variants:
  `VAR-000001`, `VAR-000002`, `VAR-000003`, `VAR-000004`, `VAR-000005`,
  `VAR-000006`, `VAR-000007`
- No dropped, executed-only, successful-only, or winner-only denominator is
  encoded.

## Determinism Proof

The D5 run was repeated in scratch output with identical frozen parents, D4A
CSV input, D4 catalog slice input, D2 import report input, and deterministic
seed.

- Same result population ID: `RP-4492`
- Same result population identity hash:
  `sha256:2a9cee1b1ba32d9f98f879aa4c1ef95e2f5b75b7348e1084e66afe80f77bb32c`
- Same input identity hash:
  `sha256:8fca9c6f6238f4fd5712420921faa649a1a182866adb22f1d5f3680b850a535c`
- Same D4 catalog ref and D4 slice identity.
- Same seven result rows.
- Same committed denominator and outcome counts.
- Payloads were identical excluding `audit_envelope`; the only observed
  administrative difference was the scratch rerun `run_label`.

## Validation Summary

- `git diff --check`: pass.
- `python -m tools.registry.validate_result_populations`: pass.
- `python -m tools.research_query.run --list-views`: pass.
- `v_integrity_*`: clean, 55 views / zero nonzero views.
- `python -m pytest tests/test_offline_research_runner.py -q`: pass, 41
  tests.
- `python -m pytest tests/test_validate_result_populations.py -q`: pass, 42
  tests.
- `python -m pytest tests/test_research_query.py -q`: pass, 63 tests.
- `python tools/dev/diff_scope_summary.py`: pass; changed files are the D5
  result-population artifact, status docs, and stale result-population/query
  corpus test assertions.
- `python -m pytest -q`: environment-only failure after 1,227 passed tests
  because the isolated D5 worktree lacks gitignored local fixture
  `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`
  required by
  `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window`.
  No data file is committed or pulled into scope.

## Boundary Summary

No mutation, replacement, deletion, or rename of `RP-2134` is included. No
fixture provenance is encoded in `RP-4492`. No runner, compiler, backtester,
`lib/`, schema, query-layer, runtime, paper/live, dashboard, dependency, config,
D4/D3/D2 data artifact, Strategy Spec, variant manifest, or sweep plan change is
included. No interpretation, ranking, recommendation, readiness, promotion,
transition, policy, or execution authority is created.

## Merge Status

Pending PR at package execution time.

## Next Dependency / Runway Note

After D5 merges, post-D5 interpretation or descriptive checkpoint work remains a
separate package and must not be inferred from this evidence write.
