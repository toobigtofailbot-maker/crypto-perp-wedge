# Research Pipeline Foundation

This directory documents the candidate-agnostic foundation layer for the Phase 2
research machine.

## Documents

- `2026-04-candidate_registry.md` explains `research/candidate_registry.jsonl`,
  the registry schema, and how candidate status links to hypotheses, decision
  records, and the trial log.
- `2026-04-experiment_artifacts.md` explains JSON Experiment Plan and Experiment
  Report artifacts for the Continuous Improvement loop.

## Instances

The first exercise of the experiment artifact grammar is EXP-0001 / REP-0001
for H-005 under `research/experiments/`. See
`2026-04-retrospective_instance_convention.md` for the convention used when an
instance is authored after execution.

The first Stage 6 / Stage 7 retrospective instance pair is DCH-0001 / REL-0001
for the historical H-005 NO-GO archive outcome.

The first Stage 6 / Stage 7 forward-flow instance pair is DCH-0002 / REL-0002
for the H-004 REP-0011 current-evidence NO-GO archive outcome.

## Query Layer

`2026-04-query_layer.md` explains the read-only DuckDB query layer over the
candidate registry, experiment artifacts, and trial log.

## Stages 6-7 Artifacts

`2026-04-decision_change_artifact.md` and
`2026-04-release_notes_artifact.md` explain the JSON artifact conventions for
the Human Approval Gate and Release & Monitor stages.

## Advisory Agent Outputs

`2026-04-agent_output_artifact.md` and
`2026-04-regime_scoring_agent_stub.md` explain the first deterministic bounded
advisory agent output family introduced by WP-7a. The first instance is
fixture-backed, schema-validated, queryable, and advisory-only.

## Advisory Bucket Mappings

`2026-04-bucket_mapping_artifact.md` and `2026-04-score_bucket_mapper.md`
explain the first deterministic advisory score bucket mapper introduced by
WP-6j. The first instance consumes `AOUT-0001` only and maps it into the locked
`ALLOW` / `ALLOW_REDUCED` / `BLOCK` domain without overlay contact.

## Overlay Shadow Logs

`2026-04-overlay_shadow_log_artifact.md` and
`2026-04-overlay_shadow_external_hook.md` explain the first zero-override
overlay shadow log family introduced by WP-7c. The first instance compares
`BMAP-0001` against an externally observable overlay-side source without
changing `lib/` or runtime behavior.

`2026-04-shadow_signal_views.md` explains the first aggregate diagnostic views
over the committed overlay shadow-log family.

## Briefs / Diagnostic Outputs

- `2026-04-cross_candidate_diagnostic.md`: First cross-candidate diagnostic
  brief (WP-6e). See the `queries/` + `outputs/` directory beside it.

## Relationship To Architecture

This package supports the research-pipeline side of the accepted research
machine direction. It creates structured candidate and experiment artifacts so
future work can compare candidates systematically instead of relying on
prose-only status scattered across decision records.

Diagram 2 stages 3 through 6 depend on this grammar:

- Propose: create an Experiment Plan.
- Validate Offline: execute the plan and log trials.
- Validate Paper: report paper or shadow evidence when scoped later.
- Human Approval: review schema-validated artifacts before any promotion.

The decision-pipeline side, including agents, score-bucket mapping, and any
advisory automation, remains later work.

## Validation Commands

Run the registry validator:

```powershell
.venv\Scripts\python.exe tools\registry\validate_registry.py
```

Run the experiment artifact validator:

```powershell
.venv\Scripts\python.exe tools\registry\validate_experiment_artifacts.py
```

Run the regression tests:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_registry_validation.py -q
```

## Out Of Scope

- No candidate auto-generation.
- No agent in the loop.
- No DuckDB query layer.
- No Monte Carlo infrastructure.
- No gold data procurement.
- No H-011 pre-registration.
- No execution-core changes.
