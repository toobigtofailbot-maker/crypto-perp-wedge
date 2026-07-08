# Legacy Byte-Regression Plan

## Purpose

A future implementation must prove every legacy bridge path remains unchanged after adding product mode.

## Legacy Fixtures / Examples

Use existing bridge tests and fixtures as the starting corpus:

- `tests/test_agent_formalizer_runner_bridge.py::_setup_source`
- `tests/test_agent_formalizer_runner_bridge.py::_write_ohlcv_fixture`
- `tests/test_agent_formalizer_runner_bridge.py::test_approved_bridge_runs_real_runner_and_reconciles`
- funding path coverage from `test_funding_bridge_emits_valid_18_row_halves_and_compiles`
- blocking paths from missing approval, funding-on, constrained data, and denominator suppression tests

If additional scratch fixture material is needed, it must be produced under the future implementation package scratch root and recorded with hashes.

## Before / After Invocation

1. On pre-implementation base, run direct legacy bridge invocation using deterministic inputs and fixed clock.
2. Capture output tree, audit records, returned dict, and file hashes.
3. After implementation, run the same direct legacy bridge invocation with the same deterministic inputs.
4. Compare outputs.

## Byte-For-Byte Comparisons Required Where Deterministic

- derived Strategy Spec JSON;
- derived Variant Manifest JSON;
- derived Sweep Plan JSON;
- denominator ledger JSON;
- human review packet JSON;
- returned `artifact_paths` payload where path roots are deterministic;
- audit records where deterministic;
- runner artifacts where deterministic under repo truth.

## Hash Comparisons

Record SHA256 for:

- source formalizer output;
- approval marker;
- draft Strategy Spec;
- derived Strategy Spec;
- derived Variant Manifest;
- derived Sweep Plan;
- denominator ledger;
- human review packet;
- runner result artifact if produced.

## Normalization Rule

Do not silently normalize timestamps, absolute paths, UUIDs, ordering, or hashes. Use normalized comparison only if repo truth already provides deterministic volatile-field handling. If byte comparison is impossible because a volatile field is not deterministic, stop and ask Karl whether a normalized comparison rule is acceptable.

## Required Behavior Tests

- Legacy ToolContext WP allowlist unchanged.
- Legacy rejected WP IDs still rejected.
- Legacy approval shape unchanged.
- Legacy Karl/product approval still rejected unless separately authorized.
- Legacy source-prefix validation unchanged.
- Legacy output root unchanged.
- Legacy draft validation unchanged.
- Legacy derived input validation unchanged.
- Legacy runner invocation behavior unchanged in legacy mode.
- Legacy denominator suppression still blocked.
- Legacy data availability bypass still blocked.
- Legacy adversarial/protected actions still blocked.

## Failure Classification

- Byte mismatch in deterministic legacy outputs: implementation blocker.
- Missing legacy artifact: implementation blocker.
- Changed runner invocation count or target: implementation blocker.
- Legacy approval shape broadened: implementation blocker.
- Legacy source-prefix broadened in legacy mode: implementation blocker.
- Legacy output root moved: implementation blocker.
- ToolContext or protected-path permissiveness increased: implementation blocker.
- Volatile-field mismatch with no approved normalization rule: Karl escalation.

## Plan Status

`legacy_byte_regression_plan_status`: `specified_for_future_implementation_not_executed_here`
