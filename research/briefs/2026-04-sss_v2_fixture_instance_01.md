# SSS v2 Fixture Instance 01 Production Record

**Date:** 2026-04-25
**Package:** WP-8f
**Scope:** Third committed SSS v2 instance as a fixture-only segment-form summary over the committed overlay-shadow corpus.
**Does not introduce:** Consumer analysis, schema changes, validator changes, helper changes, query-layer changes, new shadow rows, fixture/config changes, advisory-artifact changes, or runtime contact.
**Does not encode:** Policy recommendation, cadence, overlay influence, OMS influence, risk influence, runtime authority, override authority, or execution authority.

## 1. Objective

This artifact-production record documents `SSS-0004`, the third committed SSS v2 instance.

The instance uses the fixture-only segment form encoded by exactly this field:

- `fixture_identity`

No literal `overlay_input_fixture`, `fixture_pair`, `snapshot_config_pair`, or `overlay_input_identity` schema field is introduced.

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

- `shadow_signal_summary_id: "SSS-0004"`
- `schema_version: "v2"`
- `derivation_method: "shadow_signal_summary_option_a_floor_10_v1"`
- `segmentation_axes: ["fixture_identity"]`
- `fixture_identity_rule: "committed_overlay_input_pair_v1"`
- `rate_denominator_rule: "match_plus_mismatch"`

Aggregation is over committed overlay-shadow logs using the repo-truth fixture identity mapping:

- `tests/fixtures/context_snapshot_sample.json` + `configs/fmp_macro_flags.json` -> `canonical`
- `tests/fixtures/context_snapshot_sample_02.json` + `configs/fmp_macro_flags_02.json` -> `_02`

Counting semantics:

- `MATCH` contributes to `match_count`
- `MISMATCH` contributes to `mismatch_count`
- absent, null, or other comparison values contribute to `abstention_count`

## 4. Segment Coverage

Produced artifact path:

- `research/shadow_signal_summaries_v2/SSS-0004.shadow_signal_summary.json`

Derived segment count: `2`

Realized fixture identities:

- `_02`
- `canonical`

| Fixture identity | Match | Mismatch | Abstention | Observations | Rate denominator | Floor status | Signal outcome |
|---|---:|---:|---:|---:|---:|---|---|
| `_02` | 2 | 2 | 0 | 4 | 4 | Below floor | `INSUFFICIENT_EVIDENCE` |
| `canonical` | 2 | 4 | 0 | 6 | 6 | Below floor | `INSUFFICIENT_EVIDENCE` |

Floor-crossing summary:

- above-floor segments: `0`
- below-floor segments: `2`

The fixture variety is limited but non-degenerate: two fixture identities are realized, and both remain below the locked floor of 10 observations.

No sufficient agreement, disagreement, or mixed classification is claimed.

## 5. Query-Layer Result

Central query-layer visibility after artifact creation:

- `v_shadow_signal_summaries_v2_overview` surfaces `SSS-0004`.
- `v_integrity_shadow_signal_summary_v2_derivation` remains empty after `SSS-0004`.

Integrity result:

```json
[]
```

## 6. Disclosures

This package creates the third committed SSS v2 instance and a factual artifact-production record only.

It creates no consumer brief, makes no policy recommendation, and does not interpret evidence beyond factual floor status.

It is descriptive only and has no runtime, override, OMS, risk, policy, or execution authority.
