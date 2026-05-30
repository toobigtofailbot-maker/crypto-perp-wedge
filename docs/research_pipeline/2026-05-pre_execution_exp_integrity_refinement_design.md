# Pre-execution EXP Integrity Refinement Design

## 1. Scope

WP-S2c-127a / WP-12fg1 is a Tier 1 documentation-only design and lock-candidate package.

This package creates only this design document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-narrow.

This package designs the refinement only. It makes no SQL, code, test, schema, validator, registry, experiment, report, trial-log, decision, outcome-ledger, reconciliation, or other canonical-artifact change.

## 2. Repo-truth basis

WP-S2c-126 / WP-12ff is merged and registered H-012 as the first active Path B candidate under locked Option B.

H-012 is currently registered in `research/candidate_registry.jsonl` as:

- `status`: `DRAFT`
- `overall_verdict`: `PENDING`
- `strategy_family`: `trend_following`
- `timeframe`: `15m`
- `information_inputs`: `["ohlcv_15m", "funding_8h"]`
- `free_parameter_count`: `3`
- `pipeline_stage`: `pre_registered`
- `trial_ids`: `[]`
- `decision_record_path`: `null`

WP-S2c-127 was blocked because a valid pre-execution EXP-0012 plan without a REP triggered `v_integrity_plan_report_pairs` as `plan_without_report`.

Current `v_integrity_plan_report_pairs` flags any EXP without a REP as `plan_without_report`. The current view expects healthy repo state to have no such rows.

The view was created when EXP/REP pairs were effectively retrospective or paired, before the first new forward-flow pre-execution EXP state entered scope.

Phase 9 / D2-011 pre-registration discipline, together with D2-005 and the Path B execution sequence, requires the EXP plan to be committed before backtest execution and REP creation. H-012 is the first Path B candidate requiring a legitimate EXP-before-REP interval.

## 3. Current integrity-view behavior

The existing view logic in `tools/research_query/views.sql` has two branches:

- `plan_without_report`: selects EXP rows from `exp_plans` left-joined to `exp_reports` where no report row exists for the plan.
- `report_without_plan`: selects REP rows from `exp_reports` left-joined to `exp_plans` where no plan row exists for the report's `plan_id`.

The current logic cannot distinguish:

- a valid pre-execution EXP plan awaiting later backtest and REP creation;
- a genuinely broken or abandoned EXP plan with a missing REP.

## 4. Problem statement

The structural check is valid, but its semantics are too coarse for forward-flow pre-registration.

A healthy pre-execution state currently looks identical to an unhealthy orphan-plan state. That creates a false positive that blocks clean pre-registration even when the package is correctly forbidden from creating a REP before backtest execution.

## 5. Main 4.0 Route A authorization

Main 4.0 Route A is authorized for this package sequence:

- WP-S2c-127a designs the integrity semantics refinement.
- WP-S2c-127b implements and validates the refinement after this design merges.

Route B, atomic EXP plus backtest plus REP, is rejected because it sacrifices pre-registration discipline by bundling planning and evidence production solely to satisfy the current view.

Route C alternatives are rejected:

- skip EXP;
- non-canonical EXP staging;
- fake placeholder REP;
- permanent deferral.

WP-S2c-127a and WP-S2c-127b are authorized under standing runway rules. This document does not authorize WP-S2c-127 retry.

## 6. Route rejections

This design explicitly rejects:

- fake placeholder REP creation;
- skipping EXP creation;
- storing EXP outside canonical `research/experiments`;
- bundling EXP creation with backtest and REP solely for view cleanliness;
- weakening, skipping, or bypassing integrity validation.

## 7. Design objective

The refinement objective is to:

- preserve broken-pair detection;
- exclude legitimate pre-execution EXP plans from broken-pair output;
- keep pre-execution state bounded;
- preserve D2-011 / Phase 9 pre-registration discipline, and D2-005 hypothesis pre-registration discipline;
- avoid schema, validator, registry, or canonical artifact changes if a clean signal already exists;
- modify only the bounded plan/report-pair integrity semantics in WP-S2c-127b.

## 8. Candidate signals for distinguishing pre-execution from broken-pair state

### 8.1 Candidate registry state

The candidate registry already records the state needed to identify a legitimate pre-execution candidate:

- candidate exists;
- `status == DRAFT`;
- `overall_verdict == PENDING`;
- `pipeline_stage == pre_registered`;
- `trial_ids == []`;
- `decision_record_path == null`.

This signal is already available to the query layer through the `candidates` relation.

### 8.2 EXP artifact field

The current experiment-plan schema does not contain a dedicated EXP lifecycle status field.

Adding one would require a schema change and likely validator/test changes. That is not preferred for the first refinement because the registry already expresses the needed bounded pre-execution state.

### 8.3 Report/backtest artifact state

Before backtest execution, no REP and no trial-log entry are expected.

Relying only on the absence of a REP is not sufficient because that is the current false-positive path. The absence of REP must be interpreted together with candidate state.

### 8.4 Time-bounded age

Age can be useful as future policy, but it would require current-time logic, date-threshold policy, or a new query-layer convention not currently present in the view.

It is not necessary for the first refinement because the candidate registry provides a stronger available state signal for H-012.

### 8.5 Candidate lifecycle state

Formal lifecycle artifacts may become useful later if the repo adds a richer candidate lifecycle model.

For the first bounded refinement, H-012's current registry state is enough: pre-registered, pending, no trial evidence, and no decision record.

## 9. Recommended signal

Use candidate registry state as the initial refinement signal.

An EXP with a missing REP is not a plan/report-pair integrity issue when all of the following are true:

- the EXP `candidate_id` resolves to an existing candidate;
- candidate `status == DRAFT`;
- candidate `overall_verdict == PENDING`;
- candidate `pipeline_stage == pre_registered`;
- candidate `trial_ids` is empty;
- candidate `decision_record_path IS NULL`.

The view should still flag:

- EXP with a missing REP where the candidate is concluded, archived, or promoted;
- EXP with a missing REP where the candidate has any `trial_ids`;
- EXP with a missing REP where the candidate has a decision record;
- EXP with a missing REP where the `candidate_id` is unknown;
- REP with an unknown `plan_id`.

## 10. Lock-candidate refined semantics

Lock-candidate wording:

`v_integrity_plan_report_pairs` continues to detect broken EXP/REP relationships.

A plan without a report is not a broken pair while it is attached to a known candidate in legitimate pre-execution state: DRAFT / PENDING / pre_registered / no `trial_ids` / no `decision_record_path`.

Once a candidate has trial evidence, a decision record, or a non-pre_registered or concluded state, a missing REP for its EXP becomes an integrity issue.

REP without known EXP remains an integrity issue.

Unknown candidate references remain handled by candidate-reference integrity views and should not be hidden by this refinement. An EXP whose candidate is unknown must not be treated as a legitimate pre-execution plan by the plan/report-pair refinement.

This refinement does not make unpaired plans permanently healthy. It recognizes only the valid interval between committed EXP and later backtest/REP.

## 11. Bounded pre-execution state

Pre-execution is valid only while:

- the candidate remains pre_registered and pending;
- no trial has been logged;
- no decision record exists;
- the tranche has a clear next package to execute backtest, trial-log write, and REP creation.

If the project abandons H-012, changes its state, logs a trial, creates a DEC, or moves beyond pre-registration without a REP, the missing report should become visible as broken state.

WP-S2c-127b should encode the strongest feasible version of this bound using available query-layer relations.

## 12. Required WP-S2c-127b implementation shape

WP-S2c-127b should:

- modify `tools/research_query/views.sql` only for `v_integrity_plan_report_pairs`, unless a directly complementary view is cleaner and justified;
- join EXP plans to candidates to inspect candidate registry state;
- exclude only legitimate pre-execution plans from `plan_without_report`;
- preserve the `report_without_plan` branch;
- avoid schema, validator, registry, EXP, report, trial-log, and other canonical-artifact changes;
- update `docs/research_pipeline/2026-04-query_layer.md` additively to document the refined semantics;
- add or update tests only for this bounded semantics.

## 13. Required tests for WP-S2c-127b

WP-S2c-127b must include tests proving:

1. A legitimate pre-execution EXP for H-012 / DRAFT / PENDING / pre_registered / no `trial_ids` / no `decision_record_path` returns no `plan_without_report`.
2. A missing-report EXP for a concluded candidate still returns `plan_without_report`.
3. A missing-report EXP for a candidate with non-empty `trial_ids` still returns `plan_without_report`.
4. A missing-report EXP for a candidate with non-null `decision_record_path` still returns `plan_without_report`.
5. A REP referencing unknown `plan_id` still returns `report_without_plan`.
6. Current repo integrity views return clean rows after EXP-0012 exists in the later retry.
7. Existing query-layer tests for the view continue to pass under refined semantics.

## 14. Documentation update needed in WP-S2c-127b

WP-S2c-127b must update `docs/research_pipeline/2026-04-query_layer.md` additively.

The update should state that `v_integrity_plan_report_pairs` detects broken EXP/REP relationships while allowing bounded pre-execution EXP plans for pending pre-registered candidates.

It should also state that the exception is not permanent and ends once evidence or decision state exists.

## 15. Validation posture

WP-S2c-127a uses CS12 T1-doc-narrow.

WP-S2c-127b should use CS12 T3-implementation with full pytest.

The WP-S2c-127 retry should remain the original T3 EXP creation package after WP-S2c-127b merges.

Full pytest is not required for WP-S2c-127a unless repo-local doc-narrow convention escalates.

## 16. Stop conditions

Stop if:

- the design cannot identify a clean signal distinguishing pre-execution state from broken-pair state;
- the design requires schema, validator, registry, or canonical artifact changes;
- the design would weaken Phase 9 / D2-011 pre-registration discipline;
- the design would weaken broken-pair detection;
- the design would affect other integrity views beyond bounded plan/report-pair semantics;
- the design requires modifying locked criteria or locked decisions;
- the design implies readiness, transition, recommendation, ranking, scoring, promotion, or human-gate execution;
- Karl or the user overrides the route.

## 17. What this design does not authorize

This design does not authorize:

- SQL changes;
- test changes;
- EXP creation;
- REP creation;
- backtests;
- trial-log entries;
- OL/REC;
- DEC;
- schema or validator changes;
- registry changes;
- canonical artifact changes;
- readiness, transition, or promotion;
- fake REP placeholders;
- integrity validation weakening;
- runtime or protected-path work;
- Tier 4 contact.

## 18. Next-package posture

After WP-S2c-127a merges, Side may draft WP-S2c-127b after refreshed-main preflight and no stop trigger.

WP-S2c-127b must implement and validate the refinement.

WP-S2c-127 EXP creation retry must wait until WP-S2c-127b merges.

No retry of EXP-0012 creation is authorized by WP-S2c-127a.
