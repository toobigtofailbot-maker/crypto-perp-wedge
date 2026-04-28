# SSS v2 Stability Lock (WP-8i)

## Purpose

This document is the retrospective disclosure and stability-lock record for the
currently committed shadow-signal-summary v2 family.

RETROSPECTIVE DISCLOSURE: the document records the now-completed-as-consumed
state of SSS v2 after first-class v2 schema and validator introduction, three
committed v2 single-axis instances, three bounded consumers, and the committed
v2 consumer-set synthesis. It does not create a new SSS instance, does not
redesign the family, and does not authorize runtime, policy, override, OMS,
risk, or execution behavior.

SSS v2 is complete-as-consumed for the current repo state. That means later
packages should not silently mutate the v2 contract after downstream consumers
have already relied on it. It does not mean v2 is final forever or that future
schema work is prohibited.

This package changes no SSS schema, validator, committed instance, query-layer
surface, helper, runtime path, policy, or protected-path behavior.

## Committed v2 Schema Shape

The committed v2 family has an explicit top-level version marker:

- `schema_version: "v2"`

That marker is required by the committed v2 schema and enforced by the committed
v2 validator.

The committed derivation method remains
`shadow_signal_summary_option_a_floor_10_v1`.

The committed v2 schema permits the following segment forms:

- four-axis form:
  - `advisory_source`
  - `source_bucket_mapping_id`
  - `source_pre_gate_advisory_snapshot_id`
  - `fixture_identity`
- advisory-source-only form:
  - `advisory_source`
- advisory-lineage form:
  - `advisory_source`
  - `source_bucket_mapping_id`
  - `source_pre_gate_advisory_snapshot_id`
- fixture-only form:
  - `fixture_identity`

The committed v2 derivation path remains deterministic over the committed
`overlay_shadow_logs` relation. The locked floor remains `10` observations per
segment, and the locked Option A semantics remain:

- if `observation_count < 10`, then
  `insufficient_evidence=true` and
  `signal_outcome=INSUFFICIENT_EVIDENCE`
- if `observation_count >= 10`, then majority semantics produce
  `AGREEMENT_SIGNAL`, `DISAGREEMENT_SIGNAL`, or `MIXED_SIGNAL`

The committed validator also preserves deterministic segment ordering,
duplicate-ID rejection, filename-to-ID matching, locked derivation inputs, and
advisory-only / deterministic flags. No retroactive change to those v2
semantics is recorded here.

## Committed v2 Instance Coverage

Repo truth currently contains three committed SSS v2 instances:

- `research/shadow_signal_summaries_v2/SSS-0002.shadow_signal_summary.json`
  - advisory-source-only form
  - `segmentation_axes: ["advisory_source"]`
  - 2 realized segments
- `research/shadow_signal_summaries_v2/SSS-0003.shadow_signal_summary.json`
  - advisory-lineage form
  - `segmentation_axes: ["advisory_source", "source_bucket_mapping_id", "source_pre_gate_advisory_snapshot_id"]`
  - 4 realized segments
- `research/shadow_signal_summaries_v2/SSS-0004.shadow_signal_summary.json`
  - fixture-only form
  - `segmentation_axes: ["fixture_identity"]`
  - 2 realized segments

All three committed v2 instances cover the current committed corpus window from
`OSH-0001` through `OSH-0010`. All three are deterministic and advisory-only.
All currently realized v2 segments remain below the locked floor of `10`
observations and retain `signal_outcome=INSUFFICIENT_EVIDENCE`.

No four-axis v2 instance is committed in the current repo state.

## Consumer Coverage

The current committed v2 consumer coverage is complete for the intended
single-axis consumer set:

- WP-8b: advisory-source-only consumer over `SSS-0002`
- WP-8e: advisory-lineage consumer over `SSS-0003`
- WP-8g: fixture-identity consumer over `SSS-0004`
- WP-8h: synthesis brief over the completed three-consumer set

The central SSS v2 query layer is now the canonical consumption surface for
committed v2 summary content. WP-8e, WP-8g, and WP-8h consume v2 content through
that central surface. WP-8b remains the earlier bounded consumer over
`SSS-0002`, authored before central v2 query-layer support existed.

Those packages demonstrate that the committed v2 summary family is consumable as
a descriptive downstream surface without re-deriving signal meaning from raw
overlay-shadow rows and without changing helper, runtime, schema, validator, or
query-layer behavior.

## Observed Evidence State

The current v2 consumer-set synthesis records the completed single-axis set as:

- consumed v2 single-axis segments: `8`
- above-floor segments: `0`
- below-floor segments: `8`
- null-rate segments: `8`
- `INSUFFICIENT_EVIDENCE` outcomes: `8`

By axis, the current state is:

- advisory-source-only: 2 realized readout rows, both insufficient
- advisory-lineage: 4 realized readout rows, all insufficient
- fixture-identity: 2 realized readout rows, both insufficient

The current state records structural partition shapes and raw counts honestly.
It demonstrates committed v2 structural coverage over the three consumed
single-axis forms. It does not yet record any sufficient agreement,
disagreement, or mixed signal classification above floor.

## Stability Statement

SSS v2 is locked as the consumed single-axis baseline for the current repo
state.

Future schema evolution must occur as SSS v3 or later through an additive,
explicitly versioned path rather than through retroactive mutation of the v2
schema contract, validator behavior, committed v2 instances, integrity
semantics, or completed consumer assumptions.

This lock applies to both of the following:

- the descriptive v2 schema/derivation contract as already consumed
- the committed v2 instance corpus as already consumed

This lock does not prohibit future v2 instances that conform to the locked v2
contract. Such instances must not change the v2 contract, reinterpret completed
consumer assumptions, or silently alter v2 integrity semantics.

This document does not start SSS v3 design. It records only the architectural
precondition that future schema evolution belongs in a later versioned family,
not in silent v2 drift.

## Explicit Boundaries

Later packages must not retroactively mutate:

- the v2 schema
- the v2 validator
- committed v2 instances
- v2 query-layer integrity semantics
- completed v2 consumers
- the completed v2 consumer-set synthesis record

The current floor-limited evidence state must not be used to justify policy,
runtime, ranking, override, OMS, risk, or execution decisions.

This lock does not claim that v2 is final forever. It only locks the consumed
v2 baseline for the current repo state against silent retroactive mutation.

## Non-Claims

This stability lock does not claim:

- that current evidence is sufficient for stronger signal claims
- that v2 is correct for all future contexts
- that corpus growth or cadence is recommended
- that SSS v3 is designed or scoped
- that cross-version synthesis has been performed
- that any runtime or policy action is authorized
- that any override behavior is implied
- that any OMS, risk, or execution authority is granted

The record is descriptive, not prescriptive.

## Version Marker

Unlike SSS v1, SSS v2 already has an explicit top-level
`schema_version: "v2"` marker.

That marker is already present in:

- `research/schemas/shadow_signal_summary_v2.schema.json`
- `tools/registry/validate_shadow_signal_summary_v2.py`
- `research/shadow_signal_summaries_v2/SSS-0002.shadow_signal_summary.json`
- `research/shadow_signal_summaries_v2/SSS-0003.shadow_signal_summary.json`
- `research/shadow_signal_summaries_v2/SSS-0004.shadow_signal_summary.json`

Because the v2 marker is already encoded at the committed top level, WP-8i
applies no schema patch, validator patch, or committed-instance patch. This
package records the SSS v2 stability posture only.
