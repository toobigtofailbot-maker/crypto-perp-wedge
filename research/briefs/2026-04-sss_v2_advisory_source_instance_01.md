# SSS v2 Advisory-Source Instance 01 Production Record

**Date:** 2026-04-24
**Package:** WP-8a
**Scope:** First committed SSS v2 instance as an advisory-source-only single-axis summary over the committed overlay-shadow corpus.
**Does not introduce:** Consumer analysis, schema changes, validator changes, helper changes, query-layer changes, new shadow rows, fixture changes, advisory-artifact changes, or runtime contact.
**Does not encode:** Policy inference, cadence, overlay influence, OMS influence, risk influence, runtime authority, or execution authority.

## 1. Purpose

This record documents the first committed SSS v2 instance.

The instance is intentionally narrow: it produces an advisory-source-only single-axis summary over the already committed overlay-shadow corpus so the v2 schema family is exercised as a real artifact rather than only as a schema and validator contract.

This file is an artifact-production record only. It is not a diagnostic consumer brief and should not be interpreted as source ranking, policy guidance, or runtime evidence.

## 2. Inputs

The instance was derived from the committed overlay-shadow corpus window:

- `OSH-0001` through `OSH-0010`
- `2026-04-19T17:00:00Z` through `2026-04-22T08:00:00Z`

Schema and validator inputs used:

- `research/schemas/shadow_signal_summary_v2.schema.json`
- `tools/registry/validate_shadow_signal_summary_v2.py`

The corpus window matches the committed `SSS-0001` window exactly, so the v1/v2 comparison remains anchored to the same underlying shadow-log family.

## 3. Derivation

The v2 payload uses:

- `schema_version: "v2"`
- `shadow_signal_summary_id: "SSS-0002"`
- `segmentation_axes: ["advisory_source"]`
- locked `derivation_method: "shadow_signal_summary_option_a_floor_10_v1"`

Aggregation is source-only over committed overlay-shadow logs with the existing repo-truth normalization:

- advisory source = `payload.get("advisory_source") or "BMAP"`
- `MATCH` contributes to `match_count`
- `MISMATCH` contributes to `mismatch_count`
- any other comparison value contributes to `abstention_count`

Locked count and rate rules:

- `observation_count = match_count + mismatch_count + abstention_count`
- `rate_denominator = match_count + mismatch_count`
- floor = `10` observations per segment
- if below floor, then `insufficient_evidence = true`, `signal_outcome = INSUFFICIENT_EVIDENCE`, and both usable rates remain `null`

## 4. Segment Coverage

The source-only v2 instance realizes exactly two advisory-source segments in deterministic lexical order:

| Advisory source | Match | Mismatch | Abstention | Observations | Rate denominator | Floor status | Signal outcome |
|---|---|---|---|---|---|---|---|
| `BMAP` | 2 | 3 | 0 | 5 | 5 | Below floor | `INSUFFICIENT_EVIDENCE` |
| `PGAS` | 2 | 3 | 0 | 5 | 5 | Below floor | `INSUFFICIENT_EVIDENCE` |

Both realized source segments remain below the locked floor of 10 observations. No sufficient agreement, disagreement, or mixed classification is claimed.

## 5. Validation

Validation performed for this package:

- v2 validator pass for `research/shadow_signal_summaries_v2/SSS-0002.shadow_signal_summary.json`
- v1 validator pass for the unchanged committed v1 family
- overlay-shadow validator pass for the unchanged committed OSH family
- explicit v1 schema rejection for the new v2 payload in a one-off schema check because `schema_version: "v2"` is outside the v1 contract

The package also preserves the unchanged v1 schema, v1 validator, v2 schema, v2 validator, committed v1 instance corpus, committed OSH corpus, fixtures, and advisory artifacts.

## 6. Non-Claims

This package does not claim:

- that a diagnostic consumer has been produced
- that any policy or override action is justified
- that any runtime or query-layer behavior should change
- that any cadence or automation mechanism is established
- that any schema or validator patch was required

The instance is descriptive and additive only.

## 7. Forward Reference

WP-8b may consume `SSS-0002` later as the first bounded downstream brief over a committed v2 instance.

WP-8a itself does not perform that consumer analysis.
