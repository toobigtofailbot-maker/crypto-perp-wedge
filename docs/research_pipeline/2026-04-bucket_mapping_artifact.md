# Bucket Mapping Artifacts

## Purpose

`bucket_mapping` artifacts record deterministic advisory translations from
Regime/Scoring agent output into the locked bounded bucket domain:

- `ALLOW`
- `ALLOW_REDUCED`
- `BLOCK`

WP-6j introduces the first mapping family to prove the Z2 -> Z3 advisory
contract without changing overlay, OMS, risk, or execution behavior.

## Directory / Naming Convention

Instances live under:

```text
research/bucket_mappings/
```

Future instances use:

```text
BMAP-NNNN.bucket_mapping.json
```

WP-6j creates the first instance:

```text
research/bucket_mappings/BMAP-0001.bucket_mapping.json
```

## Schema Summary

The schema records:

- `bucket_mapping_id`: stable `BMAP-NNNN` identifier.
- `source_agent_output_id`: source `AOUT-NNNN` identifier.
- `agent_type`: bounded advisory family; WP-6j permits only
  `REGIME_SCORING`.
- `generated_at` and `as_of_timestamp`: copied from the source agent output.
- `source_setup_score` and `source_confidence`: copied source values.
- `mapping_method`: fixed deterministic mapper method ID.
- `confidence_floor` and `confidence_floor_triggered`: confidence-floor state.
- `mapped_bucket`: one of `ALLOW`, `ALLOW_REDUCED`, or `BLOCK`.
- `size_multiplier`: one of `1.0`, `0.5`, or `0.0`.
- `deterministic`: required to be true.
- `advisory_only`: required to be true.
- `notes`: boundary notes.

## Validator Command

```powershell
.venv\Scripts\python.exe -m tools.registry.validate_bucket_mappings
```

The validator exits successfully when `research/bucket_mappings/` is missing or
empty. When files exist, it validates schema shape, duplicate IDs, filename
conventions, source agent-output existence, copied source fields, mapping-rule
consistency, and bucket/multiplier pairing.

## Advisory-Only Statement

Bucket mappings are research artifacts only. They do not write overlay inputs,
alter overlay decisions, change hard caps, route orders, change OMS state,
modify risk controls, change paper-runtime behavior, or influence execution.

## Fail-Open Default Contract

WP-6j does not alter the runtime fail-open contract. The mapper output is stored
only as reviewable evidence in the research tree and exposed through the
read-only query layer. No runtime path consumes it.

## Out Of Scope In WP-6j

- No overlay input surface.
- No overlay logic or bucket-semantics change.
- No OMS, risk, kill-switch, reconciliation, or execution change.
- No candidate registration or promotion.
- No agent-output schema change.
- No Regime/Scoring agent-module change.
- No LLM, network, live external input, or external service call.
