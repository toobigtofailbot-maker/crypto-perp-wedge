# Release Notes Artifacts

## Purpose

`release_notes` artifacts record the structured release and monitoring details
for a stage transition that already has a referenced `decision_change` artifact.

The artifact is JSON-first. Although the diagram may describe the concept as
`release_notes.md`, future instance files use `*.release_notes.json` and
validate against `research/schemas/release_notes.schema.json`.

## When Required

A `release_notes` artifact is required when a human-approved stage transition is
made effective and needs monitoring and rollback expectations recorded.

It is not required for schema-only work, diagnostic briefs, or candidate
research that does not release a new stage state.

## Relationship To Decision Change

Each release notes artifact references one `decision_change_id`. The validator
checks that the referenced decision exists, that `candidate_id` matches the
decision, and that `effective_stage` matches the decision's
`stage_transition.to_stage`.

`released_at` must be on or after the referenced decision's `decided_at`.

## Field Definitions

- `release_notes_id`: stable `REL-NNNN` artifact identifier.
- `decision_change_id`: referenced `DCH-NNNN` decision-change artifact.
- `candidate_id`: `H-NNN` candidate registry identifier.
- `released_at`: timezone-qualified ISO datetime when release notes were
  recorded.
- `released_by`: human reviewer or package that recorded the release notes.
- `effective_stage`: candidate registry `pipeline_stage` made effective by the
  decision.
- `monitoring_plan`: structured monitoring expectations.
- `rollback_plan`: human-readable rollback plan.
- `linked_artifacts`: optional related artifact paths or identifiers.
- `notes`: optional context that does not change release state.

## Naming Convention

Future instances use:

```text
*.release_notes.json
```

The artifact ID uses `REL-NNNN`.

## Instance Location

Future instances live under:

```text
research/release_notes/
```

WP-6f defines the schema and validator only. It does not create this directory
and does not author any instance.

## Monitoring-Plan Conventions

The monitoring plan records:

- `metrics_tracked`: metrics or checks monitored after release.
- `review_cadence`: human review cadence.
- `rollback_triggers`: conditions that should trigger rollback review.
- `alert_recipients`: people, roles, or channels expected to receive alerts.

These fields describe monitoring expectations only. They do not create an
automated monitor or external alerting integration.

## Rollback-Plan Expectations

`rollback_plan` should describe how a human reviewer would unwind the released
stage if rollback triggers fire. The field is required because release without a
rollback expectation is not an auditable release state.

## Validation Command

```powershell
.venv\Scripts\python.exe -m tools.registry.validate_release_notes
```

The validator exits successfully when `research/release_notes/` is missing or
empty.

## Out Of Scope In WP-6f

- No `release_notes` instance is authored.
- No release is performed.
- No monitoring system, alert route, dashboard, endpoint, or external data
  source is created.
- No execution-core, OMS, overlay, risk, or kill-switch behavior changes.
- No agent or LLM release logic is introduced.
