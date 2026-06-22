# Preauthorized Protected Commit Report

## Karl Preauthorization Conditions

| Condition | Evidence | Result |
|---|---|---|
| Reconcile only existing funding behavior into opt-in mode | One `funding_cost_mode` argument and guard in `lib/backtest.py` | Satisfied |
| Default/omitted funding is off | Omitted and explicit-off regression test; `funding_paid == 0.0` | Satisfied |
| Existing funding behavior is behind explicit on | Existing funding fixtures now select `funding_cost_mode="on"` | Satisfied |
| Default-off is deterministic | Omitted, explicit-off, and empty-funding outputs compare equal | Satisfied |
| Funding-on matches hand calculations | Long cost `5.0`; entry-notional cost `2.0`; mark-notional cost `2.6`; short credits preserved | Satisfied |
| Non-funding outputs / Result Populations remain compatible | Empty-funding/default-off result comparison passes; canonical RP validator passes; canonical RPs untouched | Satisfied |
| No canonical Result Population mutation | No diff under `research/result_populations/` | Satisfied |
| No runtime/paper/live/execution protected-path drift | Direct diff and scope-helper inspection | Satisfied |
| No fee/slippage/fill/sizing change | Funding guard is the only bar-loop semantic change | Satisfied |
| Validation passes subject only to allowed D4A caveat | Focused tests and validators pass; full-suite sole failure is missing gitignored D4A normalized CSV | Satisfied |

## Protected Files Changed

- `lib/backtest.py` is protected research/runtime-support code and is explicitly authorized by this package.
- No other protected path changed.

## Semantic Diff Summary

- Adds `funding_cost_mode="off"|"on"` with default `"off"`.
- Applies the existing funding loop only when mode is `"on"`.
- Preserves funding sign, `(previous_bar_timestamp, current_bar_timestamp]` event alignment, notional modes, and all fee/slippage/fill/sizing behavior.
- Records the selected mode in `BacktestResult.params`.

## Default-Off Evidence

`test_omitted_and_explicit_off_funding_modes_apply_no_funding` compares omitted mode, explicit `"off"`, and an empty-funding baseline. Equity, PnL, trades, costs, liquidation state, and params are equal; `funding_paid` is `0.0`; metadata records `funding_cost_mode="off"` and `funding_notional_mode="entry_price"`.

## Explicit Funding-On Evidence

- Positive funding continues to charge longs and credit shorts.
- The hand-calculated long fixture continues to record `funding_paid=5.0`.
- Entry-price and mark-price fixtures continue to record `2.0` and `2.6` respectively.
- A funding event at the left boundary remains excluded; an event at the current-bar/right boundary remains included.
- Flat positions accrue zero funding with mode explicitly on.

## Existing Test Reconciliation

Existing tests that rely on non-empty funding now enable funding explicitly, directly or through their bounded fixture helper. Funding tests were retained. Unrelated zero-funding tests continue to exercise the omitted/default mode.

## Result Metadata Changes

`BacktestResult.params` now includes `funding_cost_mode` with value `"off"` or `"on"`. Existing `funding_notional_mode` metadata remains unchanged and is recorded in both modes.

## Backward Compatibility Impact

This package intentionally changes calls that supply non-empty funding but omit a mode: they now apply no funding. Callers that require the prior funding behavior must pass `funding_cost_mode="on"`. Calls with empty/zero funding preserve non-funding outputs. Canonical Result Populations, their schemas, validators, query surfaces, and runner artifacts are unchanged and validate successfully.

## Validation Results

- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_backtest.py tests/test_backtest_liquidation.py -q`: pass, `81 passed, 1 skipped`.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_validate_result_populations.py -q`: pass, `61 passed`.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_result_populations`: pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`: pass, `124` views listed.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py`: pass; only expected protected-path match is authorized `lib/backtest.py`.
- `git diff --check`: pass.
- Full `pytest -q`: `1961 passed, 1 skipped, 1 failed`; sole failure is the allowed isolated-worktree D4A caveat described below.

The ambient `python` command lacks repo dependencies and is not evidence. Because PowerShell does not expand the literal `tests/test_backtest*.py` argument for pytest, the focused command used both matching files explicitly through the repo virtual environment.

## Remaining Caveats

The isolated worktree lacks the gitignored D4A normalized CSV expected by `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage`, so `normalized_data_local_exists` is false. This is the package's expressly permitted missing-D4A fixture caveat and is unrelated to the funding reconciliation. The local 4h parquet-dependent test is skipped by current repo convention when its gitignored file is absent.

## Commit Decision

COMMIT. All Karl preauthorization conditions are satisfied. Stage only the five changed package files; do not stage or mutate canonical Result Populations or any forbidden path.
