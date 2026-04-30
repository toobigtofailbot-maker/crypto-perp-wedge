# Lifecycle Stability Lock (WP-9j)

## Purpose

This document is the retrospective disclosure and stability-lock record for the
currently committed lifecycle/LCH family and the completed Phase 9 lifecycle
consumer tranche.

RETROSPECTIVE DISCLOSURE: this document records the now-completed-as-consumed
LCH v1 / lifecycle baseline after Phase 9 decisions, LCH schema introduction,
validator/query-layer introduction, H-001 through H-010 retrospective LCH
backfill, three bounded lifecycle consumers, and the lifecycle consumer set
synthesis.

It does not create a new LCH artifact, does not redesign the lifecycle model,
and does not authorize runtime, policy, promotion, outcome-learning,
REC/reconciliation, paper/live, fast-track, OMS, risk, deployment, or execution
behavior.

## Retrospective Disclosure

The current LCH corpus is retrospective for H-001 through H-010. All committed
current LCH rows have `retrospective_flag = true`.

The current corpus has no forward-flow examples, no paper/live behavior, no
fast-track examples, and no halted/recovery examples.

Timing fields in the current LCH corpus are retrospective artifact
commit-introduction timestamps. They are not operational lifecycle duration
measurements.

## Committed LCH v1 Schema / Artifact Shape

The committed LCH family has an explicit top-level version marker:

- `schema_version: "v1"`

The committed artifact shape records:

- LCH ID and filename convention through `LCH-NNNN`
- candidate ID reference
- `from_state`
- `to_state`
- `transition_edge`
- `decided_by`
- `decided_at`
- `retrospective_flag`
- `fast_track_flag`
- evidence refs
- linked advisory refs
- strong candidate criteria refs
- approval fields through `evidence_summary` and `risk_acknowledgment`
- `supersedes_lch_id`
- local transition-edge consistency

The committed validator and integrity views enforce the current artifact shape
and tractable references. The schema validates local shape and local
transition-edge consistency; repo-level references and integrity semantics are
covered by the validator and query layer.

This stability lock records the current v1 posture. It does not claim LCH v1 is
final forever.

## Committed Lifecycle State / Transition Baseline

The current consumed baseline observes these lifecycle states:

- `proposed`
- `in_research`
- `research_concluded`
- `archived`

The current consumed baseline observes these transition edges:

- `proposed->in_research`: 10 rows
- `in_research->research_concluded`: 10 rows
- `research_concluded->archived`: 10 rows

The current uniform retrospective path is:

```text
proposed -> in_research -> research_concluded -> archived
```

The schema and transition graph may define additional states or edges. This
stability lock records the consumed current baseline, not every theoretically
allowed future edge.

The absence of paper/live, fast-track, halted, and recovery behavior in the
current corpus is a fact about current committed artifacts. It is not a
prohibition on future explicitly scoped artifacts.

## Committed LCH Corpus Coverage

The committed current corpus covers:

- `LCH-0001` through `LCH-0030`
- candidates H-001 through H-010
- 30 LCH rows
- 10 candidates
- 3 transitions per candidate
- all rows currently retrospective
- no current fast-track rows
- no current linked advisory refs
- no current strong candidate criteria refs

H-005 is the only current cross-family DCH/REL archival evidence exception.
`LCH-0015` cites:

- `research/decisions/DEC-0005.md`
- `DCH-0001`
- `REL-0001`

The exception is descriptive only. It does not change H-005 status, historical
decision meaning, evidence quality, candidate quality, policy posture, or
runtime behavior.

## Consumer / Synthesis Coverage

The completed lifecycle consumer set is:

- WP-9f: per-candidate lifecycle path consumer
- WP-9g: per-transition-edge consumer
- WP-9h: per-evidence-artifact-type consumer
- WP-9i: lifecycle consumer set synthesis

The completed consumer set demonstrates descriptive consumption of the LCH
corpus through the central query layer without changing LCH artifacts, schemas,
validators, query-layer files, runtime, policy, or protected paths.

## Observed Descriptive State

WP-9i records the current descriptive lifecycle state as:

- 10 candidates
- 30 LCH rows
- 3 transition edges
- 32 evidence refs
- 5 known evidence artifact types
- 0 unknown evidence refs
- one uniform retrospective path
- 10 negative archival artifact timestamp gaps
- 0 fast-track rows
- 0 non-retrospective rows
- 0 linked advisory refs
- 0 strong candidate criteria refs
- all lifecycle integrity views empty
- all discovered integrity views empty at synthesis time

Artifact timestamp gaps are not operational lifecycle duration. Negative
archival-edge gaps are artifact timestamp ordering effects, not lifecycle
contradictions.

## Stability Statement

The lifecycle/LCH v1 retrospective baseline is locked as the consumed lifecycle
baseline for the current repo state.

Future lifecycle evolution must occur through explicit later work, not silent
retroactive mutation. Future schema-breaking evolution must use a later
explicit version, for example LCH v2+.

Future additive artifacts may conform to the locked v1 contract only if they do
not reinterpret, mutate, or invalidate the consumed retrospective baseline.

Future outcome-learning, REC/reconciliation, paper/live lifecycle, fast-track,
halted/recovery, promotion policy, evidence scoring, or runtime/deployment work
must treat this lock as a dependency boundary.

## Explicit Boundaries

Later packages must not retroactively mutate:

- LCH v1 schema
- LCH validator
- LCH query-layer relation, views, or integrity semantics
- committed LCH artifacts `LCH-0001` through `LCH-0030`
- WP-9f consumer outputs or conclusions
- WP-9g consumer outputs or conclusions
- WP-9h consumer outputs or conclusions
- WP-9i synthesis outputs or conclusions
- retrospective timing interpretation
- H-005 exception interpretation

Later packages may add new explicitly scoped artifacts or versions, but they
must not silently rewrite the current baseline.

## Non-Claims

This stability lock does not claim:

- LCH v1 is final forever
- future candidates will follow the same path
- paper/live behavior is defined
- fast-track behavior is defined
- halted/recovery behavior is defined
- outcome-learning linkage exists
- REC/reconciliation linkage exists
- promotion/demotion thresholds are defined
- evidence quality is ranked or scored
- H-005 is better, worse, or more important because of extra refs
- timing gaps measure operational lifecycle duration
- any runtime, deployment, OMS, risk, or execution authority is granted

The record is descriptive, not prescriptive.

## Future Evolution Posture

Likely next architecture choices now require an explicit decision before
implementation:

- outcome-learning architecture/scaffold
- REC/reconciliation architecture
- forward-flow lifecycle artifacts for future candidates
- paper/live lifecycle extension
- fast-track semantics
- halted/recovery semantics
- promotion/demotion policy architecture
- evidence-quality scoring

WP-9j does not choose among these options and does not start any of them.

## Version Marker

LCH currently has explicit top-level `schema_version: "v1"`.

WP-9j applies no schema patch, validator patch, query-layer patch, or
committed-artifact patch. This lock records the current version posture only.
