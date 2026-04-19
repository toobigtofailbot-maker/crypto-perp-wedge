# Retrospective Experiment Instances

## Purpose

A retrospective instance is an Experiment Plan or Experiment Report artifact
authored after execution to represent pre-schema research work in the current
experiment artifact grammar.

Retrospective instances exist to make older evidence queryable and
schema-validated. They do not change the original decision, rerun a backtest, or
create new evidence.

## When They Are Appropriate

Retrospective instances are appropriate only for already-completed experiments
whose execution predates the Experiment Plan and Experiment Report schemas.

The current eligible class is the completed H-001 through H-010 baseline tests.
WP-6b backfills only H-005 as EXP-0001 and REP-0001. Any broader backfill is a
separate scoped decision.

## When They Are Not Appropriate

Retrospective instances are not appropriate for:

- Any new experiment.
- Any rerun of an existing candidate.
- Any shadow, paper, or live validation.
- Any change that affects policy, promotion, risk, or execution behavior.

Going forward, a Plan is authored and validated before execution. Execution then
creates or references trial-log evidence, and a Report is authored and validated
after the run.

## Required Disclosure

Every retrospective instance must include a clear `RETROSPECTIVE` marker in a
schema-allowed field.

The WP-6a schemas do not include a generic notes field and reject additional
top-level properties. For EXP-0001, the marker lives in `rationale`. For
REP-0001, it lives in `observations`.

## Going-Forward Flow

Real-time experiment instances should follow this order:

1. Create an Experiment Plan before execution.
2. Validate the Plan against `experiment_plan.schema.json`.
3. Execute the scoped research run.
4. Record trial evidence in `research/trial_log.jsonl` when the run creates a
   trial.
5. Create an Experiment Report after execution.
6. Validate the Report against `experiment_report.schema.json`.
7. Validate artifact linkage through `candidate_id`, `plan_id`, and the
   `research/experiments/` directory.

## Registry Limitation

The WP-6a candidate registry schema does not include Experiment Plan or
Experiment Report reference fields. WP-6b therefore leaves
`research/candidate_registry.jsonl` unchanged and relies on artifact IDs,
candidate IDs, file location, and validator checks for linkage.
