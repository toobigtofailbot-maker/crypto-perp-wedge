# WP-D5A / Data Block 1 - Runner D4-Slice Provenance Alignment

## WP Id / Title

WP-D5A / Data Block 1 - Runner D4-slice consumption / provenance alignment.

## Branch / PR

- Branch: `codex/data-block-1-d5a-runner-d4-provenance-alignment`
- PR: pending

## Package Class

T3 runner provenance alignment.

## Scope Summary

Aligns the build-and-test-only offline runner so the canonical 15m path can
consume explicit D4 catalog/slice provenance inputs and record the D4 catalog
ref plus D4 slice identity in result-population metadata. Existing fixture
provenance remains the default for fixture/test paths.

No canonical result population, sweep output, interpretation, ranking,
readiness, recommendation, promotion, paper/live transition, runtime, or
protected-path authority is created.

## Changed Files

- `tools/research_runner/run_offline_sweep.py`
- `tests/test_offline_research_runner.py`
- `docs/status_entries/WP-D5A.md`
- `docs/project_status.md`

## D4A Inputs Consumed

- D4 catalog ref:
  `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
- D4 slice identity:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- D3 validation report identity recorded from the committed D4 catalog:
  `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`
- D2 import report current committed file SHA256:
  `543c944f727b2b9a7ad06742946ecefc91aa8b94723f46509e4041f622ef57ad`
- D4 catalog artifact current committed file SHA256:
  `f7b98c4d7759b6ba0c9bf8559bcea5e3311d3abe877930da254aeca96f53105a`
- Row/range facts:
  `row_count=220128`, `expected_row_count=220128`,
  `start_utc=2020-01-01T00:00:00Z`, `end_utc=2026-04-11T23:45:00Z`
- Gap facts: `gap_count=0`, `missing_bar_count=0`, `gaps=[]`
- Duplicate facts:
  `duplicate_group_count=0`, `duplicate_row_count=0`, `duplicates=[]`
- Raw source SHA256:
  `343b639e35ce79824d26bddf6d70af2641c9d76003301e303f83cdf61d4feab4`
- Normalized CSV SHA256:
  `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`

Repo-truth note: the D2 and D4 artifact byte hashes above are computed from the
current merged files. They differ from the package brief's copied D2/D4 hash
lines, so the runner records current file identities rather than stale copied
values. The D4 catalog ref, D4 slice identity, D3 validation identity, row/range,
gap, duplicate, raw-source, and normalized hashes match the committed D4 catalog
content.

## Runner Behavior Summary

The runner now accepts `--d4-catalog-slice` and `--d2-import-report` with
`--canonical-15m`. Providing either D4 provenance input selects D4 provenance
mode, loads the D4 catalog and D2 import report, validates their required facts,
and records:

- `data_coverage_summary.data_catalog_ref` as the D4 catalog ref;
- `data_coverage_summary.data_slice_identity` as the D4 slice identity;
- per-row `data_coverage.data_catalog_ref` and `data_slice_identity` as the same
  D4 values;
- D3/D2/D4 artifact identities plus row/range/gap/duplicate/source facts in
  deterministic `data_coverage_summary.data_coverage_notes`, because the
  current result-population schema has no dedicated fields for those extra facts.

## Fail-Closed Behavior Summary

D4 provenance mode fails closed if:

- `--canonical-15m` is absent;
- either the D4 catalog path or D2 import report path is absent;
- the D4 catalog ref is missing or malformed;
- the D4 slice identity is missing or malformed;
- the D3 validation report identity or PASS status is missing;
- row/range/gap/duplicate/source facts are missing or malformed;
- D4 catalog facts show row-count mismatch, gaps, or duplicates;
- D2 raw/normalized hashes disagree with the D4 catalog;
- fixture-style catalog ref or `csv_fixture:` slice identity is supplied as D4.

## Fixture-Path Preservation Summary

Existing `--canonical-15m` fixture behavior remains the default when no D4
provenance paths are supplied. The fixture path still emits
`15m_ohlcv_test_fixture_offline_only` and `csv_fixture:sha256:<hash>` and does
not include the D4 provenance mode note.

## Determinism Proof

Focused runner tests rerun the D4 provenance path twice with identical frozen
inputs and distinct run labels. The result population id and identity-scoped
payload excluding the audit envelope are identical. The D4 catalog ref, D4 slice
identity, D3 identity, row/range/gap/duplicate/source facts, and current D2/D4
file identities remain stable in the output metadata.

## Validation Summary

- `python -m pytest tests/test_offline_research_runner.py -q`: pass, 30 tests.
- `python -m pytest tests/test_validate_result_populations.py -q`: pass, 42 tests.
- `python -m tools.registry.validate_result_populations`: pass.
- `python -m tools.research_query.run --list-views`: pass.
- `v_integrity_*`: clean, 55 views.
- `python tools/dev/diff_scope_summary.py`: pass; no forbidden-path matches.
- D4 scratch rerun proof: pass; identical result population id and
  identity-scoped payload excluding the audit envelope across two scratch
  writes with identical frozen inputs.
- `python -m pytest -q`: environment-only failure after 1,190 passed tests
  because the isolated worktree lacks gitignored local fixture
  `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`
  required by
  `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window`.
  No data file is committed or pulled into scope.

## Boundary Summary

Build-and-test runner provenance alignment only. No canonical
`research/result_populations/*` write is committed. No sweep output,
interpretation, ranking, readiness, recommendation, promotion, Strategy Spec,
variant manifest, sweep plan, D4 catalog/slice artifact, D2/D3 data artifact,
compiler, backtester/lib, schema, query-layer, runtime, paper/live, OMS,
reconciliation, risk, kill-switch, safe-mode, broker/exchange/order path,
credential, config, dependency, or production-scale data change is included.

## Merge Status

Pending PR at package execution time.

## Next Dependency / Runway Note

D5 remains Karl-gated after D5A. D5A removes the runner provenance blocker for a
later first real-data canonical sweep package, but it does not authorize or
perform that sweep.
