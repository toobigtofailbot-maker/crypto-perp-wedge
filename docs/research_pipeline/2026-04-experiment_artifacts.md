# Experiment Artifacts

## Purpose

Experiment artifacts define the JSON grammar for future research actions in the
Continuous Improvement loop.

- Experiment Plans describe what will be tested before execution.
- Experiment Reports describe what happened after execution.

This package defines schemas only. It does not create any experiment plan or
report instances.

## Experiment Plans

Plan files live under `research/experiments/` and use the suffix
`*.plan.json`.

A plan is required before a future structured experiment such as a baseline,
sensitivity sweep, walk-forward run, paper validation, regime-conditional test,
or candidate comparison.

The schema requires:

- `plan_id`, using `EXP-NNNN`.
- `candidate_id`, referencing `research/candidate_registry.jsonl`.
- `plan_type`.
- `rationale`.
- `hypothesis_to_test`.
- `success_criteria`.
- `evaluation_window`.
- `parameters`.
- `data_requirements`.
- `pre_registration_date`.
- `author`.
- `human_approval_required`.

The current repo has not yet formalized an IS/OOS split convention for all
baseline evidence, so the plan schema allows null evaluation-window boundaries
when a future package explicitly needs to preserve that repo truth.

## Experiment Reports

Report files live under `research/experiments/` and use the suffix
`*.report.json`.

A report records the outcome of an executed plan. It references both the plan
and candidate, links any `trial_ids`, stores metric objects, records gate
results, and provides a next-step recommendation.

The report schema accepts numeric or textual gate threshold / observed values.
This matches current DEC record reality, where some gate entries use evaluator
semantics text rather than plain numbers.

## Human Approval Gate

`human_approval_required` must be `true` for plans that could affect live or
shadow behavior, risk parameters, or first-time promotion. Offline research-only
plans with no policy implications may set it to `false`.

Human approval operates on schema-validated artifacts. The artifacts do not
grant any execution, risk, or promotion authority.

## Naming And Validation

- Plan IDs use `EXP-NNNN`.
- Report IDs use `REP-NNNN`.
- Plan files use `*.plan.json`.
- Report files use `*.report.json`.
- YAML is intentionally unsupported in WP-6a; no PyYAML dependency is added.

Validate future artifacts with:

```powershell
.venv\Scripts\python.exe tools\registry\validate_experiment_artifacts.py
```

The validator exits successfully when `research/experiments/` does not exist,
which is expected for WP-6a.

## Out Of Scope

- No candidate auto-generation.
- No agent in the loop.
- No DuckDB query layer.
- No Monte Carlo infrastructure.
- No gold data procurement.
- No H-011 pre-registration.
- No execution-core changes.
