# Closed Plus-Parameter Composition Design

## Scope And Non-Authority

WP-COMP-PLUSCOMP-01a is docs-only.

It locks design semantics only.

It does not implement schema, validator, compiler, catalog, Strategy Specs, variants, sweeps, result populations, dashboard, runtime, paper/live, data acquisition, simulator, OMS/risk, broker/exchange, or protected-path changes.

This document creates no implementation authority. Later packages must stay inside their own explicit scope and current merged repo truth.

## Repo-Truth Basis

Current merged repo truth wins over older summaries, stale handoffs, and prior planning language.

Files inspected for this lock:

- `AGENTS.md`
- `docs/project_status.md`
- `CLAUDE_START_HERE.md`
- `docs/runbook.md`
- `docs/ai/codex/WP_DRAFTING_STANDARD.md`
- `docs/ai/codex/COMPACT_WP_TEMPLATE.md`
- `docs/ai/codex/WP_EXECUTION_REPORT.md`
- `docs/status_entries/README.md`
- `docs/research_pipeline/README.md`
- `docs/research_pipeline/2026-05-stage2c_workflow_efficiency_operating_model_lock.md`
- `docs/research_pipeline/2026-06-compiler_indicator_first_block_options.md`
- `docs/status_entries/WP-COMP-XOVER-01.md`
- `research/schemas/strategy_spec.schema.json`
- `tools/registry/validate_strategy_specs.py`
- `tools/research_runner/spec_signal_compiler.py`
- `tests/test_validate_strategy_specs.py`
- `tests/test_spec_signal_compiler.py`

Current minus-form posture:

- `research/schemas/strategy_spec.schema.json` defines `composed_operand.composition_type` as the closed const `scale_by_one_minus_parameter`.
- `tools/registry/validate_strategy_specs.py` validates composed operands against `scale_by_one_minus_parameter`, base operands restricted to `data_ref` / `indicator_ref`, parameter operands restricted to `parameter_ref`, no nested composition, and bound parameter values in `(0, 1)`.
- `tools/research_runner/spec_signal_compiler.py` supports `scale_by_one_minus_parameter` only and computes `base * (1 - p)`.
- `tests/test_validate_strategy_specs.py` and `tests/test_spec_signal_compiler.py` currently reject `scale_by_one_plus_parameter` as an unsupported or unclosed composition type.

Current plus-form absence:

- `scale_by_one_plus_parameter` is mentioned in prior planning surfaces as future work.
- No existing design document locks `scale_by_one_plus_parameter` with complete semantics and package sequencing.
- No existing `WP-COMP-PLUSCOMP-01a` status fragment exists at the start of this package.

Current `crosses_*` completion state:

- `docs/status_entries/WP-COMP-XOVER-01.md` records PR #429 for `crosses_above` and `crosses_below`.
- Current `origin/main` includes merge commit `7a3f993` for PR #429.
- The compiler now supports `crosses_above` / `crosses_below`; that completion does not alter the closed minus-only composed-operand posture.

## Locked Form

```text
composition_type: scale_by_one_plus_parameter
formula: base * (1 + p)
base_operand: data_ref or indicator_ref only
parameter_operand: parameter_ref only
parameter bound: 0 < p < 1
nesting: forbidden
depth: no additional condition depth
grammar: closed form only
```

The plus form is a closed sibling of the existing minus form. It is not an expression language and does not permit arbitrary arithmetic.

## Symmetry With Minus Form

The intended symmetry is:

```text
scale_by_one_minus_parameter: base * (1 - p)
scale_by_one_plus_parameter:  base * (1 + p)
```

This design must not widen:

- base operand types;
- parameter operand type;
- parameter bound;
- nesting;
- arithmetic grammar;
- expression grammar.

The plus form exists only to express the upper-side closed threshold that is symmetric with the existing lower-side threshold. It preserves the current bounded composed-operand shape.

## Required Later Package Sequence

```text
01b: schema + validator + tests only
01c: compiler + tests only
report back to Main 5 after 01c validates
```

This document records the conditional runway only. It does not authorize executing 01b or 01c before their dependency conditions are met.

## Stop And Rejection Rules For Later Implementation

Later implementation packages must stop if plus-form support:

- needs expression language;
- needs nested `composed_operand`;
- needs new operand type;
- needs new data stream;
- needs condition depth >3;
- changes minus-form behavior;
- touches runtime/protected paths.

Any such need means the closed symmetric design no longer matches this lock and requires a new decision surface instead of implementation drift.

## Boundary Statement

This design creates no Strategy Specs, variants, sweeps, result populations, backtests, ranking, recommendation, readiness, promotion, canonical-use, runtime, paper/live, OMS/risk, broker/exchange, data acquisition, simulator, or protected-path authority.

It does not authorize schema, validator, compiler, catalog, query, runner, backtester, dashboard, data, dependency, configuration, or test changes. Those remain deferred to separately scoped packages only.
