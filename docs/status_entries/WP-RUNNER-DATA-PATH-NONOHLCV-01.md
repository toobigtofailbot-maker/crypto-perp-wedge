# WP-RUNNER-DATA-PATH-NONOHLCV-01 Branch State

## Scope Summary

This branch implements runner-side declared non-OHLCV column preservation for offline research sweeps. It is research-lab infrastructure foundation only.

## Main / Operator Authorization

Main surfaced Path A after PR #558: build runner/data-path support before taker-flow/funding can be tested. Operator selected that path for `WP-RUNNER-DATA-PATH-NONOHLCV-01`.

## Repo-Truth Discovery

The compiler already permits allowed data-derived `data_ref` fields when present in the input frame. The runner CSV loader was the narrowing point because it retained only `open`, `high`, `low`, `close`, and `volume`. The result-population schema and validator already support optional identity-bearing `data_availability_claim`.

## Protected Runner/Data-Path Boundary

The change is additive and runner-scoped. It changes no backtest fill logic, position accounting, cost/funding semantics, compiler operator semantics, canonical evidence rules, runtime, paper/live, OMS, risk, reconciliation, or capital paths.

## Declared Column Contract

OHLCV columns remain required. The runner now collects declared non-OHLCV fields from Strategy Spec `data_ref` operands and `timeframe_and_data.host_data_refs`, retains only those additional CSV columns, drops undeclared extras, and fails closed when declared columns are missing. Recent-only or snapshot-only fields fail closed for this full-history runner claim.

## Implementation Summary

- Added declared non-OHLCV field collection in `tools/research_runner/run_offline_sweep.py`.
- Extended canonical 15m/4h CSV loading to retain declared extra columns while preserving the OHLCV-only default.
- Added optional `data_availability_claim` emission for declared non-OHLCV fields with `FULL_HISTORY_PUBLIC_ARCHIVE` source labels.
- Included `data_availability_claim` in input and result identity hash scopes only when present.
- Added focused runner tests for single/multiple declared columns, missing declared columns, undeclared extras, recent-only fail-closed behavior, OHLCV-only unchanged scope, and runner smoke to backtest.

## Full-History Materialization Status

Blocked. The isolated worktree contains only small taker-flow reconstruction fixtures, not full-history trade or aggTrade archives. No network, provider/API, private endpoint, vendor source, or large data dump was used.

## OHLCV Regression Proof

Behavior-equivalent regression proof was obtained through the runner/compiler/validator tests and unchanged OHLCV-only identity scope. Byte-identical replay for `RP-2592`, `RP-3731`, and `RP-7134` was not claimed because no committed repo-native exact replay command was found.

## Non-OHLCV Smoke Result

Passed through `tests/test_offline_research_runner.py::test_declared_non_ohlcv_runner_smoke_reaches_backtester`. The smoke proves the declared non-OHLCV field reaches the runner backtest path. It does not produce edge, GO/NO-GO, candidate, promotion, paper/live, or canonical evidence.

## Availability Label Preservation

The runner emits `data_availability_claim` for declared non-OHLCV fields and preserves source class plus condition assertions from `research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json`. Recent-only fields are not treated as full-history evidence.

## Validation Status

Passed targeted validation:

- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_offline_research_runner.py -q`
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_spec_signal_compiler.py -q`
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_validate_result_populations.py tests/test_validate_data_feature_availability.py tests/test_validate_candidate_registry.py -q`
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_candidate_registry`
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_result_populations`
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_data_feature_availability`
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py`
- `git diff --check`

Full pytest was not run.

## Boundary Summary

No canonical Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, trial logs, candidate lifecycle entries, canonical crossings, promotion/freeze/register actions, paper/live/runtime files, OMS/risk/reconciliation/capital paths, private endpoints, credentials, provider/API/network code, or large data dumps were written.

## Non-Authority Statement

This branch does not run edge discovery, produce GO/NO-GO evidence, create a candidate, authorize promotion, or authorize paper/live/runtime usage.

## Research-Lab Completion Note

This WP is research-lab infrastructure foundation. It does not complete the Side 12 / operator target-state lab. It does not run edge discovery. It does not produce a candidate. It does not authorize paper/live/runtime. It only addresses one blocking data-path layer required before data-derived families can be tested honestly.

## Open Decision Surfaces

- Whether to provide full-history local taker-flow trade or aggTrade archive inputs for a future materialization package.
- Whether to promote an aligned funding feature materialization path from local ignored funding data in a separately scoped package.
- Whether future runner result populations with declared non-OHLCV fields require additional query surfaces beyond the existing optional `data_availability_claim`.
