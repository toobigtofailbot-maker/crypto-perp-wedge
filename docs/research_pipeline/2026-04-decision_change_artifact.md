# Decision Change Artifacts

## Purpose

`decision_change` artifacts record the structured outcome of the Diagram 2
Human Approval Gate. They preserve who made the decision, what candidate and
reports were reviewed, which pipeline transition was considered, and what risk
acknowledgment accompanied the decision.

The artifact is JSON-first. Although the diagram may describe the concept as
`decision_change.md`, future instance files use `*.decision_change.json` and
validate against `research/schemas/decision_change.schema.json`.

## When Required

A `decision_change` artifact is required before a candidate can be moved by a
human approval decision toward shadow, paper, live, revision, rejection, or
approval reversal.

It is not required for offline schema work, diagnostic briefs, or retrospective
query outputs that do not make a promotion, demotion, or release decision.

## Relationship To Human Approval Gate

The Human Approval Gate reviews schema-validated evidence and records a human
decision. The artifact documents that decision; it does not grant execution
authority, bypass risk controls, or automate approval.

Approvals to shadow, paper, or live require at least one referenced Experiment
Report. Revision requests require explicit conditions. Reversals require the
prior `decision_change_id` being superseded.

## Field Definitions

- `decision_change_id`: stable `DCH-NNNN` artifact identifier.
- `candidate_id`: `H-NNN` candidate registry identifier.
- `report_ids`: `REP-NNNN` Experiment Report identifiers reviewed as evidence.
- `decision`: human approval gate outcome.
- `stage_transition`: `from_stage` and `to_stage` values from the candidate
  registry `pipeline_stage` enum.
- `decided_by`: human reviewer or package that recorded the decision.
- `decided_at`: timezone-qualified ISO datetime.
- `rationale`: why the decision was made.
- `evidence_summary`: short summary of the evidence reviewed.
- `risk_acknowledgment`: explicit human acknowledgment of risk and rollback
  implications.
- `supersedes_decision_id`: prior `DCH-NNNN` decision superseded by this one,
  or `null`.
- `conditions`: follow-up conditions, required for revision requests.
- `notes`: optional context that does not change the decision.

## Naming Convention

Future instances use:

```text
*.decision_change.json
```

The artifact ID uses `DCH-NNNN` to avoid collision with existing human-readable
decision records named `DEC-NNNN`.

## Instance Location

Future instances live under:

```text
research/decision_changes/
```

WP-6f defines the schema and validator only. It does not create this directory
and does not author any instance.

## Cross-Reference Behavior

Schema validation checks local shape and local conditional rules. The validator
checks repository references:

- `candidate_id` resolves in `research/candidate_registry.jsonl`.
- Every `report_id` resolves under `research/experiments/`.
- Non-null `supersedes_decision_id` resolves to another discovered
  `decision_change` artifact.

## Validation Command

```powershell
.venv\Scripts\python.exe -m tools.registry.validate_decision_changes
```

The validator exits successfully when `research/decision_changes/` is missing or
empty.

## Retrospective Instances

Retrospective `decision_change` artifacts should only be authored by a future
scoped package when a prior human approval decision must be represented in the
JSON grammar. They must not invent a decision that did not happen.

## Out Of Scope In WP-6f

- No `decision_change` instance is authored.
- No candidate is promoted, rejected, revised, or reverted.
- No policy decision is made.
- No execution-core, OMS, overlay, risk, or kill-switch behavior changes.
- No agent or LLM approval logic is introduced.

## Human Approval Gate Is Not Automated Approval

The artifact makes a human decision auditable. It does not automate approval,
perform ranking, place orders, alter runtime behavior, or authorize any action
outside the explicitly scoped package that creates a future instance.
