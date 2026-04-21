# Pre-Gate Advisory Snapshot Artifacts

## Purpose

`pre_gate_advisory_snapshot` artifacts record a single current advisory picture
for review by bundling already-committed advisory evidence from the Regime /
Scoring lane, the bucket-mapping lane, and the Macro / Narrative lane.

WP-7g introduced this family as a bundle-only research artifact. It preserves
source evidence together without deciding how those advisory lanes should be
combined for policy, gating, overlay behavior, or execution.

WP-7h adds the first deterministic non-NONE combination rule,
`MACRO_AWARE_FLOOR`, while preserving `PGAS-0001` as unchanged historical
bundle-only state.

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

WP-7g created the first historical bundle-only instance:

```text
research/pre_gate_advisory_snapshots/PGAS-0001.pre_gate_advisory_snapshot.json
```

WP-7h adds the first rule-applied instance:

```text
research/pre_gate_advisory_snapshots/PGAS-0002.pre_gate_advisory_snapshot.json
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
- `combination_rule_applied`: either historical `NONE_BUNDLE_ONLY` or
  deterministic v1 `MACRO_AWARE_FLOOR`.
- `combined_bucket`: required for non-NONE rules and absent for historical
  bundle-only snapshots.
- `notes`: boundary notes.

## Validator Command

```powershell
.venv\Scripts\python.exe -m tools.registry.validate_pre_gate_advisory_snapshots
```

The validator exits successfully when `research/pre_gate_advisory_snapshots/` is
missing or empty. When files exist, it validates schema shape, duplicate IDs,
filename conventions, source-artifact existence, copied source fields, derived
timestamp consistency, explicit bundle-only semantics, and deterministic
non-NONE rule correctness.

## Combination Rule Semantics

`NONE_BUNDLE_ONLY` means the snapshot bundles existing advisory outputs for
read-only inspection and does not derive a fused bucket, precedence rule, or
final decision from the bundled lanes. `PGAS-0001` remains in this historical
state and is unchanged.

`MACRO_AWARE_FLOOR` means the combined bucket is derived only from the committed
BMAP bucket and committed MOUT macro-window flag:

- If `macro_window_flag = true`, combined bucket = the more restrictive of the
  BMAP bucket and `ALLOW_REDUCED`.
- If `macro_window_flag = false`, combined bucket = BMAP bucket unchanged.
- Restrictiveness ordering is `BLOCK` > `ALLOW_REDUCED` > `ALLOW`.

`PGAS-0002` is the first rule-applied instance. With current committed inputs,
`BMAP-0001.mapped_bucket = ALLOW_REDUCED` and
`MOUT-0001.macro_window_flag = true`, so `PGAS-0002.combined_bucket =
ALLOW_REDUCED`.

## Advisory-Only Statement

Pre-gate advisory snapshots are research artifacts only. They do not alter
overlay rules, risk caps, OMS state, order routing, paper runtime behavior,
position sizing, kill-switch behavior, candidate status, or promotion state.

## Out Of Scope

- No changes to existing advisory source artifacts.
- No mapper semantics change or AOUT score/confidence remapping inside PGAS
  combination.
- No overlay, OMS, risk, runtime, or execution wiring.
- No candidate-specific logic.
- No LLM, network, live external input, or external service call.
