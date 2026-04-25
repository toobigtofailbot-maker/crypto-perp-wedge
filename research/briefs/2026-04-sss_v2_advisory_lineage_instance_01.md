# SSS v2 Advisory-Lineage Instance 01 Production Record

**Date:** 2026-04-25
**Package:** WP-8d
**Scope:** Second committed SSS v2 instance as an advisory-lineage segment-form summary over the committed overlay-shadow corpus.
**Does not introduce:** Consumer analysis, schema changes, validator changes, helper changes, query-layer changes, new shadow rows, fixture changes, advisory-artifact changes, or runtime contact.
**Does not encode:** Policy recommendation, cadence, overlay influence, OMS influence, risk influence, runtime authority, override authority, or execution authority.

## 1. Objective

This artifact-production record documents `SSS-0003`, the second committed SSS v2 instance.

The instance uses the advisory-lineage segment form encoded by exactly these fields:

- `advisory_source`
- `source_bucket_mapping_id`
- `source_pre_gate_advisory_snapshot_id`

No literal `advisory_artifact_lineage`, `advisory_lineage`, or equivalent schema field is introduced.

## 2. Source Corpus

The source artifact family is `overlay_shadow_logs`.

The instance was derived from the committed overlay-shadow corpus window:

- first source log: `OSH-0001`
- last source log: `OSH-0010`
- first observed timestamp: `2026-04-19T17:00:00Z`
- last observed timestamp: `2026-04-22T08:00:00Z`
- total source observation count: `10`

## 3. Derivation

The v2 payload uses:

- `shadow_signal_summary_id: "SSS-0003"`
- `schema_version: "v2"`
- `derivation_method: "shadow_signal_summary_option_a_floor_10_v1"`
- `segmentation_axes: ["advisory_source", "source_bucket_mapping_id", "source_pre_gate_advisory_snapshot_id"]`
- `rate_denominator_rule: "match_plus_mismatch"`

Aggregation is over committed overlay-shadow logs using the repo-truth advisory-source normalization:

- `advisory_source = COALESCE(advisory_source, "BMAP")`
- `MATCH` contributes to `match_count`
- `MISMATCH` contributes to `mismatch_count`
- absent, null, or other comparison values contribute to `abstention_count`

## 4. Segment Coverage

Produced artifact path:

- `research/shadow_signal_summaries_v2/SSS-0003.shadow_signal_summary.json`

Derived segment count: `4`

| Advisory source | Bucket mapping | Pre-gate snapshot | Match | Mismatch | Abstention | Observations | Floor status | Signal outcome |
|---|---|---|---:|---:|---:|---:|---|---|
| `BMAP` | `BMAP-0001` | `null` | 0 | 3 | 0 | 3 | Below floor | `INSUFFICIENT_EVIDENCE` |
| `BMAP` | `BMAP-0002` | `null` | 2 | 0 | 0 | 2 | Below floor | `INSUFFICIENT_EVIDENCE` |
| `PGAS` | `BMAP-0001` | `PGAS-0002` | 0 | 3 | 0 | 3 | Below floor | `INSUFFICIENT_EVIDENCE` |
| `PGAS` | `BMAP-0002` | `PGAS-0003` | 2 | 0 | 0 | 2 | Below floor | `INSUFFICIENT_EVIDENCE` |

Floor-crossing summary:

- above-floor segments: `0`
- below-floor segments: `4`

No sufficient agreement, disagreement, or mixed classification is claimed.

## 5. Query-Layer Result

Central query-layer visibility after artifact creation:

- `v_shadow_signal_summaries_v2_overview` surfaces `SSS-0003`.
- `v_integrity_shadow_signal_summary_v2_derivation` remains empty after `SSS-0003`.

Integrity result:

```json
[]
```

## 6. Disclosures

This package creates the second committed SSS v2 instance and a factual artifact-production record only.

It creates no consumer brief, makes no policy recommendation, and does not interpret evidence beyond factual floor status.

It is descriptive only and has no runtime, override, OMS, risk, policy, or execution authority.
