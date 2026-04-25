# SSS v1 Stability Lock (WP-7y)

## Purpose

This document is the retrospective disclosure and stability-lock record for the
currently committed shadow-signal-summary v1 family.

RETROSPECTIVE DISCLOSURE: the document records the now-completed-as-consumed
state of SSS v1 after the committed three-consumer set and the committed
synthesis brief. It does not create a new SSS instance, does not redesign the
family, and does not authorize runtime, policy, override, OMS, risk, or
execution behavior.

SSS v1 is complete-as-consumed for the current repo state. That means later
packages should not silently mutate the v1 contract after downstream consumers
have already relied on it. It does not mean v1 is final forever or that future
schema work is prohibited.

## Committed v1 Schema Shape

The committed v1 derivation method is
`shadow_signal_summary_option_a_floor_10_v1`.

The committed segment key remains the explicit four-axis combination of:

- `advisory_source`
- `source_bucket_mapping_id`
- `source_pre_gate_advisory_snapshot_id`
- `fixture_identity`

The committed v1 derivation path remains deterministic over the committed
`overlay_shadow_logs` relation. The locked floor remains `10` observations per
segment, and the locked Option A semantics remain:

- if `observation_count < 10`, then
  `insufficient_evidence=true` and
  `signal_outcome=INSUFFICIENT_EVIDENCE`
- if `observation_count >= 10`, then majority semantics produce
  `AGREEMENT_SIGNAL`, `DISAGREEMENT_SIGNAL`, or `MIXED_SIGNAL`

No retroactive change to those v1 semantics is recorded here.

## Consumer Coverage

The current committed v1 consumer coverage is complete for the intended
single-axis consumer set:

- WP-7u: overlay-fixture slice consumer over `canonical` versus `_02`
- WP-7v: advisory-lineage slice consumer over the realized lineages
- WP-7w: advisory-source readout over existing committed `SSS-0001` content
- WP-7x: synthesis brief over the completed three-consumer set

Those packages demonstrate that the committed v1 summary family is consumable as
a descriptive downstream surface without re-deriving signal meaning from raw
overlay-shadow rows and without changing helper, runtime, schema, validator, or
query-layer behavior.

## Observed Evidence State

Repo truth currently contains one committed SSS instance only:

- `research/shadow_signal_summaries/SSS-0001.shadow_signal_summary.json`

`SSS-0001` covers committed `OSH-0001` through `OSH-0010` and realizes 8
segments over the locked four-axis key. All currently realized partitions remain
below the locked floor of `10` observations.

The current floor-limited evidence state observed by the completed consumer set
is therefore:

- fixture slice: 2 realized readout rows, both insufficient
- lineage slice: 4 realized readout rows, all insufficient
- advisory-source readout: 2 realized readout rows, both insufficient

The current state records structural partition shapes and raw counts honestly.
It does not yet record any sufficient agreement, disagreement, or mixed signal
classification above floor.

## Explicit WP-7w Boundary

The WP-7w advisory-source consumer remains bounded as a readout over existing
committed `SSS-0001` rows.

That means `advisory_source` is consumable from existing v1 content, but not as
a first-class advisory-source-only SSS instance under the current v1 contract.
This stability lock preserves that constraint explicitly. The existence of the
WP-7w readout must not be used later to imply that v1 already supports a
different summary shape than the committed four-axis segment family.

## Stability Statement

SSS v1 is locked as the consumed baseline for the current repo state.

Future schema evolution must occur as SSS v2 or later through an additive,
explicitly versioned path rather than through retroactive mutation of the v1
schema contract or committed v1 instances.

This lock applies to both of the following:

- the descriptive v1 schema/derivation contract as already consumed
- the committed v1 instance corpus as already consumed

This document does not start SSS v2 design. It records only the architectural
precondition that future evolution belongs in a later versioned family, not in
silent v1 drift.

## Non-Claims

This stability lock does not claim:

- that v1 is correct for all future contexts
- that current evidence is sufficient for stronger signal claims
- that any runtime or policy action is authorized
- that any override behavior is implied
- that any execution authority is granted

The record is descriptive, not prescriptive.

## Version Marker

WP-7y applies no schema patch, validator patch, or committed-instance patch.

For this package, the existing top-level `derivation_method`
`shadow_signal_summary_option_a_floor_10_v1` is treated as the equivalent
explicit version marker for SSS v1. That marker is already present in:

- `research/schemas/shadow_signal_summary.schema.json`
- `tools/registry/validate_shadow_signal_summaries.py`
- `research/shadow_signal_summaries/SSS-0001.shadow_signal_summary.json`

Because that v1 marker is already encoded at the committed top level, WP-7y
does not add a dedicated `schema_version` field and does not modify any
committed SSS payload to encode one retroactively.
