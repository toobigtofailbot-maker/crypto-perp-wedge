# Pre-Gate Advisory Snapshot Artifacts

## Purpose

`pre_gate_advisory_snapshot` artifacts record a single current advisory picture
for review by bundling already-committed advisory evidence from the Regime /
Scoring lane, the bucket-mapping lane, and the Macro / Narrative lane.

WP-7g introduces this family as a bundle-only research artifact. It preserves
source evidence together without deciding how those advisory lanes should be
combined for policy, gating, overlay behavior, or execution.

The artifact is JSON-first and validates against:

```text
research/schemas/pre_gate_advisory_snapshot.schema.json
```

## Directory / Naming Convention

Instances live under:

```text
research/pre_gate_advisory_snapshots/
```

Future instances use:

```text
PGAS-NNNN.pre_gate_advisory_snapshot.json
```

WP-7g creates exactly one instance:

```text
research/pre_gate_advisory_snapshots/PGAS-0001.pre_gate_advisory_snapshot.json
```

## Schema Summary

The schema records:

- `pre_gate_advisory_snapshot_id`: stable `PGAS-NNNN` identifier.
- `generated_at`: latest source `generated_at` timestamp across the bundled inputs.
- `as_of_timestamp`: latest source `as_of_timestamp` across the bundled inputs.
- `source_agent_output_id`: source `AOUT-NNNN` identifier.
- `source_bucket_mapping_id`: source `BMAP-NNNN` identifier.
- `source_macro_window_agent_output_id`: source `MOUT-NNNN` identifier.
- `setup_score` and `confidence`: copied Regime / Scoring values.
- `mapped_bucket` and `size_multiplier`: copied bucket-mapping values.
- `macro_window_flag`: copied macro-window flag.
- `deterministic`: required to be true.
- `advisory_only`: required to be true.
- `combination_rule_applied`: fixed explicit no-op value `NONE_BUNDLE_ONLY`.
- `notes`: boundary notes.

## Validator Command

```powershell
.venv\Scripts\python.exe -m tools.registry.validate_pre_gate_advisory_snapshots
```

The validator exits successfully when `research/pre_gate_advisory_snapshots/` is
missing or empty. When files exist, it validates schema shape, duplicate IDs,
filename conventions, source-artifact existence, copied source fields, derived
timestamp consistency, and explicit bundle-only semantics.

## Bundle-Only Statement

The snapshot bundles existing advisory outputs for read-only inspection. It does
not derive a fused bucket, precedence rule, or final decision from the bundled
lanes.

## Advisory-Only Statement

Pre-gate advisory snapshots are research artifacts only. They do not alter
overlay rules, risk caps, OMS state, order routing, paper runtime behavior,
position sizing, kill-switch behavior, candidate status, or promotion state.

## Out Of Scope In WP-7g

- No changes to existing advisory source artifacts.
- No new combination rule between macro and regime lanes.
- No mapper semantics change.
- No overlay, OMS, risk, runtime, or execution wiring.
- No candidate-specific logic.
- No LLM, network, live external input, or external service call.
