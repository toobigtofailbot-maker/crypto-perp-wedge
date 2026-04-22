# Overlay Shadow Log Artifacts

## Purpose

`overlay_shadow_log` artifacts record zero-override comparison evidence between
an externally observable overlay-side bucket and an advisory bucket source.
WP-7c introduced the first BMAP-sourced instance so the repo could compare
mapper output against the locked overlay bucket domain without changing overlay
behavior. WP-7i extends the same family additively so the hook can also consume
the committed PGAS combined advisory bucket.

## Directory / Naming Convention

Instances live under:

```text
research/overlay_shadow_logs/
```

Future instances use:

```text
OSH-NNNN.overlay_shadow_log.json
```

WP-7c creates the first historical instance:

```text
research/overlay_shadow_logs/OSH-0001.overlay_shadow_log.json
```

WP-7i adds the first PGAS-sourced instance:

```text
research/overlay_shadow_logs/OSH-0002.overlay_shadow_log.json
```

## Schema Summary

The schema records:

- `overlay_shadow_log_id`: stable `OSH-NNNN` identifier.
- `advisory_source`: additive source discriminator. Missing means historical
  `BMAP` semantics so `OSH-0001` remains unchanged.
- `source_bucket_mapping_id`: source `BMAP-NNNN` artifact.
- `source_pre_gate_advisory_snapshot_id`: source `PGAS-NNNN` artifact for
  PGAS-sourced entries only.
- `source_agent_output_id`: source `AOUT-NNNN` copied from the mapping chain.
- `observed_overlay_bucket`: externally observed locked-domain overlay bucket.
- `observed_overlay_size_multiplier`: locked multiplier for the observed bucket.
- `mapped_bucket` and `size_multiplier`: compared advisory bucket state. For
  historical `BMAP` entries they copy the source bucket mapping. For `PGAS`
  entries they copy the referenced PGAS `combined_bucket` and its implied
  multiplier.
- `comparison_result`: `MATCH` or `MISMATCH`.
- `override_applied`: required to be `false`.
- `fail_open_preserved`: required to be `true`.
- `advisory_only`: required to be `true`.
- `observed_at` and `observation_source`: deterministic external observation
  metadata.
- `notes`: boundary statement.

## Validator Command

```powershell
.venv\Scripts\python.exe -m tools.registry.validate_overlay_shadow_logs
```

The validator exits successfully when `research/overlay_shadow_logs/` is missing
or empty. When files exist, it validates schema shape, filename conventions,
duplicate IDs, source bucket mapping / PGAS / agent output references,
historical copied-field consistency, PGAS combined-bucket consistency,
comparison result consistency, and the zero-override booleans.

`OSH-0001` remains the unchanged historical BMAP-path instance. `OSH-0002` is
the first PGAS-sourced entry and remains advisory-only.

## Zero-Override Statement

Overlay shadow logs are research evidence only. They never override the
overlay-side bucket, position sizing, risk, OMS, kill-switch, order routing, or
paper/live runtime behavior.

## No `lib/` Statement

WP-7c does not modify `lib/` and the shadow hook does not import from `lib/`.
The hook consumes committed repo-local artifacts and writes only the explicit
research-side shadow log output when invoked.

## Out Of Scope In WP-7c

- No overlay logic changes.
- No mapper or agent schema changes.
- No OMS, reconciliation, risk cap, kill-switch, or safe-mode changes.
- No runtime log writes.
- No candidate registry, EXP/REP, DCH/REL, trial-log, hypothesis, decision,
  timeframe, brief, audit, `src/`, `configs/`, `.claude/`, or data changes.
- No LLM call, network access, live external input, or execution authority.
