# Lifecycle Change Artifact (LCH)

## Purpose

Lifecycle Change artifacts record Phase 9 lifecycle state transitions.

The artifact is JSON-first. Future instance files should use a stable
`LCH-NNNN` identifier and validate against:

```text
research/schemas/lifecycle_change.schema.json
```

WP-9a defines the schema and documentation only. It creates no LCH instances and
adds no validator.

## Relationship To DCH And REL

LCH is distinct from Decision Change and Release Notes artifacts.

- DCH records a human approval-gate decision in the existing candidate
  pipeline-stage vocabulary.
- REL records release and monitoring details for a human-approved stage
  transition.
- LCH records Phase 9 lifecycle state movement.

The vocabularies are intentionally adjacent. WP-9a does not rewrite DCH, REL,
the candidate registry, or their schemas.

## Required Fields

- `lifecycle_change_id`: stable `LCH-NNNN` artifact identifier.
- `schema_version`: Phase 9 schema marker, fixed to `v1`.
- `candidate_id`: `H-NNN` candidate identifier.
- `from_state`: lifecycle state before the transition.
- `to_state`: lifecycle state after the transition.
- `transition_edge`: permitted transition edge string.
- `decided_by`: human reviewer or package that recorded the lifecycle change.
- `decided_at`: timezone-qualified ISO datetime.
- `evidence_summary`: concise summary of evidence considered.
- `risk_acknowledgment`: explicit risk acknowledgment.
- `evidence_artifact_refs`: evidence artifact identifiers or paths.
- `supersedes_lch_id`: prior `LCH-NNNN` superseded by this artifact, or `null`.

## Optional / Forward-Compatible Fields

- `notes`: optional human context.
- `linked_advisory_artifacts`: optional one-way links to advisory artifacts.
- `retrospective_flag`: marks a retrospective lifecycle record.
- `retrospective_disclosure`: required when `retrospective_flag` is true.
- `fast_track_flag`: marks a structurally fast-track lifecycle decision.
- `strong_candidate_criteria_refs`: required when `fast_track_flag` is true.

These fields create structural accommodation only. They do not enforce exact
promotion policy thresholds, capital caps, monitoring cadence, halt mechanics,
or deployment mechanics in WP-9a.

## Human Approval Semantics

Approval semantics are embedded in LCH. Approval is human-only. Helpers,
validators, query-layer views, advisory artifacts, and agents do not approve
lifecycle movement.

## Retrospective Support

LCH supports retrospective disclosure through `retrospective_flag` and
`retrospective_disclosure`. WP-9a creates no retrospective instances. H-001
through H-010 lifecycle backfill belongs to a later scoped package.

## Advisory-Linking Support

LCH may include optional one-way links to advisory artifacts such as PGAS, SSS,
AOUT, MOUT, and BMAP. Those links do not modify advisory schemas and do not
grant advisory artifacts execution or approval authority.

## Fast-Track Support

LCH v1 includes `fast_track_flag` and `strong_candidate_criteria_refs` so a
later package can record exceptional fast-track lifecycle decisions. The exact
operational policy is deferred.

## Validation

WP-9a did not add an LCH validator. WP-9b adds the first validator at:

```text
tools/registry/validate_lifecycle_changes.py
```

The validator treats a missing or empty `research/lifecycle_changes/` directory
as a healthy empty state. It validates schema shape, filename/ID consistency,
duplicate IDs, candidate references, supersession references, tractable
known-pattern artifact references, approval-field completeness,
retrospective-disclosure structure, and fast-track structure.

The schema validates local shape and local transition-edge consistency only.

Repository reference checks, candidate existence checks, supersession
resolution, artifact-reference resolution, prior-state history, and historical
`halted -> previous_non_halted_state` validation are outside the schema.
WP-9b covers the tractable reference and local-shape checks through the
validator and query-layer integrity views. Historical proof that halted recovery
returns to the immediately preceding non-halted state remains deferred until a
later package locks ordering policy.

## Query-Layer Support

WP-9b adds central read-only query-layer support through the relation:

```text
lifecycle_changes
```

The relation is registered from:

```text
research/lifecycle_changes/*.lifecycle_change.json
```

When the directory is missing or empty, the query layer registers a typed empty
relation so the healthy committed state remains queryable without requiring an
LCH instance.

WP-9b adds these overview and aggregate views:

- `v_lifecycle_change_overview`
- `v_lifecycle_state_transitions`

WP-9b adds these expected-empty integrity views:

- `v_integrity_lifecycle_change_refs`
- `v_integrity_lifecycle_transition_graph`
- `v_integrity_lifecycle_approval_completeness`
- `v_integrity_lifecycle_fast_track_completeness`

These views add validation and observability only. WP-9b commits no LCH
instances and adds no runtime, policy, deployment, OMS, reconciliation, risk,
overlay, safe-mode, live-trading, promotion, demotion, or execution authority.

## Non-Claims

LCH does not:

- execute lifecycle changes by itself before validator/query-layer packages
- authorize runtime deployment
- touch OMS, risk, overlay, safe-mode, reconciliation, or runtime behavior
- create paper execution
- create live execution
- automate promotion or demotion
