# SSS v2 Schema Design (WP-7z)

## Purpose

WP-7z adds an additive SSS v2 schema/validator family so shadow-signal
summaries can support first-class single-axis instances without mutating the
already consumed SSS v1 contract.

SSS v2 remains descriptive, deterministic, advisory-only, and non-runtime. It
does not create a v2 instance, does not define a consumer, and does not encode
cadence, policy, override, OMS, risk, or execution authority.

## Why v2 exists

WP-7w and WP-7x established an explicit boundary in repo truth: advisory-source
consumption is feasible from existing SSS v1 rows, but a first-class
advisory-source-only summary instance is not available under the locked v1
four-axis segment key.

WP-7y then locked SSS v1 as complete-as-consumed. That stability lock means
future schema evolution belongs in a later versioned family, not as silent v1
drift.

## What v2 preserves from v1

The following v1 semantics remain unchanged in v2:

- floor `= 10` observations per segment
- `INSUFFICIENT_EVIDENCE` when `observation_count < 10`
- majority semantics above floor for `AGREEMENT_SIGNAL`,
  `DISAGREEMENT_SIGNAL`, and `MIXED_SIGNAL`
- `rate_denominator = match_count + mismatch_count`
- abstentions remain explicit and excluded from usable-rate denominators
- deterministic derivation contract
- advisory-only / no-runtime character
- no policy, override, or runtime authority

V2 also preserves the existing top-level `derivation_method`
`shadow_signal_summary_option_a_floor_10_v1`. The additive v2 family marker is
the new required top-level `schema_version: "v2"`.

## What v2 adds

V2 adds a distinct schema and validator family with:

- required `schema_version: "v2"`
- a versioned additive path that leaves v1 untouched
- coherent single-axis segment forms
- a preserved four-axis compatibility form for new v2 summaries that still use
  the original v1 segment key

Unused key fields are omitted in v2 segments outside the forms where they are
coherent. V2 does not carry null placeholders for absent axes except where the
lineage-compatible `source_pre_gate_advisory_snapshot_id` field is present and
the existing `BMAP`/`PGAS` null-vs-required rule applies.

## Permitted segment key forms

The permitted `segmentation_axes` forms are:

1. Four-axis compatibility form
   - `["advisory_source", "source_bucket_mapping_id", "source_pre_gate_advisory_snapshot_id", "fixture_identity"]`
   - preserves the committed v1 segment-key shape

2. Advisory-source-only form
   - `["advisory_source"]`
   - supports first-class `BMAP` / `PGAS` source-only summaries

3. Overlay-input-fixture-only form
   - `["fixture_identity"]`
   - supports first-class fixture-identity summaries over `canonical` / `_02`

4. Advisory-lineage form
   - `["advisory_source", "source_bucket_mapping_id", "source_pre_gate_advisory_snapshot_id"]`
   - preserves the exact coherent lineage bundle already surfaced by the v1
     lineage consumer
   - `source_pre_gate_advisory_snapshot_id` remains `null` for `BMAP` lineage
     rows and required for `PGAS` lineage rows

## Disallowed or deferred forms

The following are explicitly disallowed in WP-7z:

- bucket-mapping-only form
- pre-gate-snapshot-only form
- agent-output-only form
- macro-output-only form
- any ad hoc cross-axis or consumer-defined shape not listed above

These forms are disallowed because repo truth does not establish a coherent SSS
segment meaning for them. WP-7z is additive schema work only; it does not
invent new semantic axes beyond the coherent forms already implied by committed
artifacts and bounded consumers.

Query-layer support is also deferred. The current query layer is coupled to the
v1 shape and integrity checks, so any v2 query relation or view update belongs
in a later additive query-layer package rather than in WP-7z.

## Relationship to v1

SSS v1 remains valid, unchanged, and still authoritative for committed v1
content.

WP-7z does not:

- deprecate v1
- require migration of `SSS-0001`
- change the v1 schema
- change the v1 validator
- reinterpret the WP-7w advisory-source readout as if it were already a
  source-only instance

V1 and v2 therefore coexist as distinct explicit families.

## What this package does not do

WP-7z does not:

- create a committed v2 SSS instance
- add a v2 consumer brief
- define summary cadence
- change the query layer
- change helpers, overlay-shadow logs, fixtures, or advisory artifacts
- change runtime, policy, override, OMS, risk, or execution behavior

The package is schema + validator + tests + documentation only.
