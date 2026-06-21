# WP-COMPILER-MTF-NOLOOKAHEAD-DESIGN-01 Branch State

## WP Id / Title

- WP id: `WP-COMPILER-MTF-NOLOOKAHEAD-DESIGN-01`
- Title: Design no-lookahead multi-timeframe alignment.

## Branch / PR

- Branch: `docs/compiler-mtf-nolookahead-design-01`
- Base: `main` at `a9edc67`
- Worktree: `C:\GitHub\crypto-perp-wedge-worktrees\docs-compiler-mtf-nolookahead-design-01`
- PR: Not opened in this package run.

## Package Class

Docs/design only.

This package implements no source code, schema, validator, compiler, runner, backtester, data ingestion, dependency, canonical artifact, query-layer, dashboard, runtime, paper/live, OMS, risk, reconciliation, safe-mode, kill-switch, broker, exchange, order, promotion, readiness, ranking, or recommendation change.

## Scope Summary

Created a repo-owned multi-timeframe alignment design before any MTF implementation. The design locks vocabulary, no-lookahead alignment rules, allowed/invalid fixture-style 15m/1h examples, borrowed external patterns as references only, future implementation surfaces, and future stop conditions.

Current compiler behavior is preserved: non-empty `data_ref.timeframe` and `indicator_ref.timeframe` values fail closed in `tools/research_runner/spec_signal_compiler.py`; no MTF alignment implementation exists.

## Repo-Truth Discovery

Current paths used:

- `docs/project_status.md`
- `CLAUDE_START_HERE.md`
- `docs/runbook.md`
- `research/schemas/strategy_spec.schema.json`
- `tools/research_runner/spec_signal_compiler.py`
- `tests/test_spec_signal_compiler.py`
- `docs/status_entries/WP-EXPRESS-A1.md`
- `docs/status_entries/WP-EXPRESS-A2.md`
- `docs/status_entries/WP-EXPRESS-A3.md`
- `docs/research_pipeline/2026-06-compiler_extension_tranche_plan.md`
- `docs/research_pipeline/2026-06-compiler_indicator_first_block_options.md`
- `docs/research_pipeline/2026-06-computation_binding_tranche_checkpoint.md`

Already-existing surfaces preserved:

- WP-EXPRESS-A1 z-score / volatility-normalized distance support remains compiler-owned as a closed composed operand.
- WP-EXPRESS-A2 `trend` and existing `regime` entry-gate group roles remain unchanged.
- WP-EXPRESS-A3 `entry_logic.entry_controls.min_bars_between_entries` remains unchanged.
- Computation-binding architecture remains unchanged: catalog declares interface only, compiler owns reviewed computation, and Strategy Specs remain declarative and non-executable.

Repo-truth adjustments:

- `docs/status_entries/WP-COMPILER-FEATURES-REGIME-SESSION-01.md` is not present on current `main`.
- `docs/architecture/README.md` is not present, so no architecture index update was required.
- Current repo truth already contains later compiler features beyond older checkpoint docs. The design relies on inspected current files rather than stale capability summaries.

Existing MTF implementation search result:

- No merged MTF alignment implementation was found.
- Search confirmed current fail-closed compiler behavior for non-empty operand timeframes:
  - `tools/research_runner/spec_signal_compiler.py`: `data_ref timeframe resampling is not supported`
  - `tools/research_runner/spec_signal_compiler.py`: `indicator_ref timeframe resampling is not supported`

## Changed Files

- `docs/architecture/2026-06-compiler_mtf_nolookahead_design.md`
- `docs/status_entries/WP-COMPILER-MTF-NOLOOKAHEAD-DESIGN-01.md`

## Validation Summary

- `git status --short --untracked-files=all`: PASS; only the two package docs are untracked.
- `python tools/dev/diff_scope_summary.py`: PASS; changed files limited to docs; no forbidden-path matches.
- `git diff --check`: PASS for tracked diff state.
- `git diff --no-index --check -- NUL <new-doc>`: PASS for both new untracked docs files.
- `python -m tools.registry.validate_indicator_catalogs`: PASS.
- `python -m tools.registry.validate_strategy_specs`: PASS.
- `python -m tools.registry.validate_result_populations`: PASS.
- `python -m tools.research_query.run --list-views`: PASS.
- `python -m pytest -q` with system Python 3.14: FAIL during collection because local system Python lacks required dependencies including `pandas`, `numpy`, and `binance`.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`: FAIL, 1803 passed, 1 skipped, 1 failed, 6 warnings in 1938.25 seconds. The failing test is `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage`, where `fixture["normalized_data_local_exists"]` was `False` but the test expected `True`. No package-changed files are involved.

## Boundary Summary

- Dependency files: not touched.
- External code copied: none.
- External library output canonical: no.
- Canonical artifacts: not touched.
- Strategy Specs / Variant Manifests / Sweep Plans / Result Populations / trial log: not touched.
- Schema / validator / compiler / runner / backtester / query-layer behavior: not touched.
- `lib/backtest.py` / `lib/evaluation.py`: not touched.
- Runtime / paper / live: not touched.
- OMS / risk / reconciliation / safe-mode / kill-switch / broker / exchange / order / capital paths: not touched.
- Private endpoints / credentials: not used.
- Promotion / readiness / ranking / recommendation authority: not created.
- `docs/project_status.md`: not touched, per package prohibition.

## Merge Status

Branch has local docs-only changes and is ready for review after PR creation with the full-pytest local data-fixture caveat disclosed above.

## Next Dependency / Runway Note

Future implementation still requires explicit Main/Karl authorization. Expected future package surfaces are schema fields, compiler resolver, tests, fixtures, validator updates, data alignment helper, and provenance/status capture. Implementation must stop on ambiguous timestamps, non-monotonic or duplicate indexes, incomplete informative candles, lower-than-base informative timeframes, missing close timestamps, future-candle exposure, or any need to touch protected runtime paths.
