# PGAS Combination Rule v1

## Purpose

WP-7h introduces the first deterministic non-NONE pre-gate advisory combination
rule for the existing PGAS family. It does not create a new artifact family and
does not modify the upstream AOUT, BMAP, or MOUT instances.

## Historical State

`PGAS-0001` is the WP-7g historical bundle-only snapshot. It remains unchanged
with `combination_rule_applied = NONE_BUNDLE_ONLY` and no `combined_bucket`.

## MACRO_AWARE_FLOOR

`MACRO_AWARE_FLOOR` consumes already-committed advisory state from:

- `research/bucket_mappings/BMAP-0001.bucket_mapping.json`
- `research/macro_window_agent_outputs/MOUT-0001.macro_window_agent_output.json`

Exact semantics:

- If `macro_window_flag = true`, combined bucket = the more restrictive of:
  - BMAP bucket
  - `ALLOW_REDUCED`
- If `macro_window_flag = false`, combined bucket = BMAP bucket unchanged.
- Restrictiveness ordering is `BLOCK` > `ALLOW_REDUCED` > `ALLOW`.

The rule does not recompute from raw AOUT score or confidence. AOUT values are
copied into PGAS only as provenance.

## First Rule-Applied Instance

`PGAS-0002` is the first rule-applied PGAS instance. Current committed inputs
are `BMAP-0001.mapped_bucket = ALLOW_REDUCED` and
`MOUT-0001.macro_window_flag = true`, so the deterministic combined bucket is
`ALLOW_REDUCED`.

## Boundaries

The rule is deterministic and advisory-only. It has no overlay contact, no OMS,
no risk authority, no sizing authority, no execution authority, no gate
promotion authority, and no runtime influence.
