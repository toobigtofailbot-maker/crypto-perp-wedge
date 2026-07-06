# WP-VALIDATOR-ATR-NORMALIZED-CANDLE-01

## Decision

Complete.

## Repo Truth

- Base: `origin/main` at `f4f78cb4fd1fb2e4adcc46584e1415a896ee9bd2`, merge commit for PR #604.
- Blocker source: `scratch/WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01/blocked_reason.json`.
- Schema/compiler truth: `research/schemas/strategy_spec.schema.json` and `tools/research_runner/spec_signal_compiler.py` already define `atr_normalized_candle_ratio_v1`.
- Validator truth before this package: `tools/registry/validate_strategy_specs.py` did not include `atr_normalized_candle_ratio_v1` in its closed composed-operand validation.

## Implementation

- Added closed validator support for `composition_type: atr_normalized_candle_ratio_v1`.
- Accepted ratio types remain limited to `candle_range_atr_ratio` and `candle_body_atr_ratio`.
- Required operand shape is exactly `operand_type`, `composition_type`, `ratio_type`, `atr_lookback`, and `zero_atr_policy`.
- `atr_lookback` accepts only literal `bars` or `bars_parameter_ref` using existing integer lookback parameter validation.
- `zero_atr_policy` remains fixed to `null_output`.

## Boundary

- No research execution was performed.
- No signed frozen set was modified.
- No Strategy Spec, Variant Manifest, Sweep Plan, Result Population, candidate, crossing, promotion/readiness, paper/live, runtime, OMS, risk, broker, exchange, config, data, dependency, runner, compiler, or protected-path authority was created or modified.

## Validation

- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests\test_validate_strategy_specs.py -q` passed.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests\test_spec_signal_compiler.py -q` passed.
- Package JSON artifacts passed `python -m json.tool`.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_strategy_specs` passed.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views` passed.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_result_populations` passed.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_candidate_registry` passed.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools\dev\diff_scope_summary.py` passed with no forbidden-path matches.
- `git diff --check` passed.
- Full pytest was not run because the package changed only the narrow Strategy Spec validator/test surface and the focused validator/compiler suites passed.
