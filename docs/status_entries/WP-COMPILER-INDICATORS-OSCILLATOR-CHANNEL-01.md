# WP-COMPILER-INDICATORS-OSCILLATOR-CHANNEL-01 Branch State

- Package: WP-COMPILER-INDICATORS-OSCILLATOR-CHANNEL-01 - Add RSI, Donchian, and MA-distance catalog/compiler support.
- Recovery branch: `compiler/indicators-oscillator-channel-01-recovery`.
- Base: recovered from the dirty root `main` snapshot at `a9edc67`; `origin/main` was at `7c46d91` when recovery began.

## Scope Summary

This package additively extends the closed indicator catalog and build-test-only Strategy Spec signal compiler with:

- `rsi_v1`
- `donchian_v1`
- `ma_distance_v1`

The Strategy Spec schema remains unchanged because existing `indicator_ref` operands can reference the new closed catalog IDs and explicit output fields. Existing A1 `z_score` composed operands, A2 `trend` / `regime` gates, A3 `entry_logic.entry_controls.min_bars_between_entries`, and plus/minus composed-band semantics remain preserved.

## Semantic Summary

- RSI uses Wilder-style smoothing over close-to-close deltas. First output appears after `lookback_bars` completed deltas. Missing close data resets the sequence. Zero movement policy is locked as gain-positive/loss-zero -> 100, gain-zero/loss-positive -> 0, both zero -> 50.
- Donchian `upper`, `lower`, `mid`, and `width` include the current bar and require a full non-null lookback. Lagged `upper_lag1`, `lower_lag1`, `mid_lag1`, and `width_lag1` expose previous-channel values for breakout-safe comparisons.
- MA-distance v1 uses the repo's current close-source/SMA idiom. It outputs `distance_abs`, `distance_ratio`, and `distance_pct`; zero or null MA masks ratio/pct to null. Existing plus/minus composed operands remain the repo-owned MA-band idiom.

## Boundary Summary

- No `lib/` changes.
- No runner/backtester changes.
- No runtime, paper/live, OMS/risk/reconciliation, safe-mode, broker/exchange, dependency-file, canonical Strategy Spec, Variant Manifest, Sweep Plan, Result Population, data, trial-log, candidate lifecycle, ranking, readiness, promotion, or dashboard authority changes.
- The indicator catalog remains an interface declaration only; computations are owned by `tools/research_runner/spec_signal_compiler.py`.
- No external indicator library code or output is canonicalized.

## Implementation Summary

- `research/schemas/indicator_catalog.schema.json` now permits the seven-entry closed catalog and declares the new input, parameter, and output contracts.
- `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json` adds RSI, Donchian, and SMA-distance entries with non-execution declarations.
- `tools/registry/validate_indicator_catalogs.py` validates the expanded closed builtin set and checks RSI zero-movement policy, Donchian output fields, and SMA-only MA-distance convention.
- `tools/research_runner/spec_signal_compiler.py` implements repo-owned deterministic calculations and multi-output indicator field resolution.
- Focused tests cover warmup/null behavior, no-lookahead future mutation, RSI zero edge cases, Donchian lagged breakout-safe fields, MA-distance zero-MA handling, both-direction compatibility, existing indicator regressions, existing z-score and composed-band regressions, and validator forbidden-key posture.

## Validation Status

Validation completed with `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe` where Python dependencies were required:

- `python -m pytest tests/test_validate_indicator_catalogs.py tests/test_validate_strategy_specs.py tests/test_spec_signal_compiler.py -q`: PASS, 325 passed
- `python -m tools.registry.validate_indicator_catalogs`: PASS
- `python -m tools.registry.validate_strategy_specs`: PASS
- `python -m pytest -q`: PASS, 1816 passed, 6 warnings

Broader package validation is recorded in the final Codex report-back.
