# WP-COMPILER-FUNDING-PERCENTILE-SEMANTICS-01 Branch State

## Scope Summary

Add closed rolling empirical-percentile semantics over a declared `data_ref` and variant-bindable `max_holding_period.bars`. This is compiler/research-lab infrastructure only; no funding research run is included.

## Main / Operator Direction

PR #561 recorded the funding positioning-fade family as blocked before execution. This package implements only the bounded semantics unblock and fixture validation.

## Repo-Truth Discovery

PR #561 is merged at base `a713a39`. Direct `funding_rate` data and runner preservation existed. Rolling data-ref percentile semantics and max-hold parameter binding did not. The existing closed composition catalog and bounded parameter-binding patterns support both additions without runner loading or backtester changes.

## Protected Compiler Boundary

Changes are limited to the Strategy Spec schema, build-and-test compiler, Strategy Spec and VM/Sweep validators, focused tests, and package documentation. No arbitrary formula surface, dynamic evaluation, runner data-path change, backtester semantic change, or runtime path is introduced.

## Rolling Percentile Semantics

`rolling_empirical_percentile_v1` is a closed composed operand over one declared `data_ref`. At bar `t`, it emits `count(window_value <= current_value) / window_count` over the trailing full window including `t`. Ties use weak rank. Warmup or any missing window observation yields null. Literal and approved `bars_parameter_ref` lookbacks are supported. Future rows, whole-sample fitting, expanding windows, and expressions are absent.

## Max-Hold Variant Binding

`exit_logic.max_holding_period.bars` now accepts the existing closed `{ "parameter_ref": "..." }` shape. Strategy declaration, bounded integer values, VM/Sweep axis presence, and compiler assignment are fail-closed. Existing literal behavior remains unchanged.

## Funding-Family Fixture Status

Fixture-only tests validate `funding_rate`, 15m equivalents of 30/90/180-day lookbacks (`2880/8640/17280`), `0.90/0.95` entry thresholds, symmetric lower-tail semantics, `0.50` exit representability, `16/32/96` max holds, and positive-extreme short / negative-extreme long direction. No canonical artifact or real research population was created.

## No-Lookahead Tests

Tests cover current/trailing-only windows, future-mutation prefix invariance, exact window boundary, weak-rank ties, full-window warmup, null windows, missing columns, undeclared transform sources, bounded parameter binding, and contrarian fixture compilation. Existing runner availability tests cover recent-only fail-closed behavior.

## Regression Status

Focused compiler/schema/validator tests passed. Offline runner tests passed. Result-population, availability, and candidate-registry tests passed. All four deterministic full-pytest shards over 107 test files passed after a catalog-hash-verified validation-only copy of the ignored D4A CSV; the copy was removed afterward. The initial serial suite timed out and is not recorded as a pass.

## Validation Status

Strategy Spec, VM/Sweep, candidate, result-population, and data-availability validators passed. Query view listing passed; all discovered integrity views were clean. Authorized diff-scope and `git diff --check` passed. No repo-native exact RP replay command exists, so no exact replay is claimed.

## Boundary Summary

No funding research run, canonical artifact write, crossing, lifecycle write, funding P&L change, fill/accounting/backtester change, runtime, paper/live, OMS, risk, reconciliation, capital, credential, provider/API/network, adoption PoC, dashboard, scheduler, notification, or large-data commit occurred.

## Non-Authority Statement

The implementation and scratch fixtures grant no execution, canonical evidence, candidate, promotion, readiness, paper/live, or runtime authority.

## Research-Lab Completion Note

The Side 12 / operator research-lab target state remains incomplete. This package adds the missing bounded compiler semantics and makes the funding-rate positioning-fade family expressible as a validated fixture. It does not execute the hypothesis or add downstream evidence, robustness, candidate-review, replay, scheduling, reporting, or trading authority.

## Open Decision Surfaces

- Whether a later separately authorized package materializes non-canonical VM/Sweep fixtures and runs the pre-registered funding family.
- Whether a later package adds a reusable exact result-population replay and normalization contract.
- Whether downstream formalizer, bridge, robustness, or candidate-review surfaces are extended after executable funding evidence exists.
