# Manual / On-Demand Shadow-Run Helper

## Purpose

`tools/shadow/shadow_run_helper.py` is a manual helper for building one
candidate `overlay_shadow_log` artifact from explicit committed advisory
evidence plus explicit canonical overlay-input references. It exists to let a
human operator produce and validate a candidate shadow-log payload without
changing any protected runtime path.

## What The Helper Does

- Accepts an explicit advisory source: `BMAP` or `PGAS`.
- Accepts an explicit source artifact id for that advisory source.
- Accepts explicit canonical `--snapshot` and `--config` paths.
- Accepts an explicit UTC `--timestamp`; there is no clock-now behavior.
- Computes the next available `OSH-NNNN` id deterministically from the
  committed `research/overlay_shadow_logs/` directory when `--out` is omitted.
- Builds a candidate payload using the existing external observation method.
- Validates the candidate against the committed shadow corpus before any write.

## Manual / On-Demand Only

This helper is invoked manually. It is not attached to any scheduler, trigger,
watcher, polling loop, or runtime bridge. A human decides when to run it and
which committed evidence references to provide.

## Dry-Run Default

Dry-run is the default mode. Without `--write`, the helper:

- prints the candidate JSON to stdout
- prints the proposed `OSH` output path and id
- runs corpus-aware validation
- writes nothing to the repo

Write mode is explicit. `--write` must be present before the helper can create
an `overlay_shadow_log` file.

## Deterministic Inputs

The helper requires:

- `--advisory-source {BMAP,PGAS}`
- `--advisory-artifact-id`
- `--snapshot`
- `--config`
- `--timestamp`

`--timestamp` must be UTC and is used for both `observed_at` and
`observation_source.evaluation_time_utc`. Identical arguments, including the
same timestamp, produce byte-identical payload output.

`--snapshot` and `--config` are explicit but intentionally restricted to the
current committed canonical paths:

- `tests/fixtures/context_snapshot_sample.json`
- `configs/fmp_macro_flags.json`

That restriction keeps helper output compatible with the existing
`overlay_shadow_log` schema and validator behavior.

## Supported Advisory Sources

### `BMAP`

The helper loads the committed bucket mapping and its linked source agent
output, then builds a BMAP-style candidate payload that preserves the
historical omission of `advisory_source`.

### `PGAS`

The helper loads the committed pre-gate advisory snapshot, its linked bucket
mapping, and its linked agent output. It consumes the committed
`combined_bucket` directly and emits a PGAS-style candidate payload with
`advisory_source = PGAS` plus `source_pre_gate_advisory_snapshot_id`.

The helper does not recompute PGAS combination logic.

## Validation Before Write

Before any write, the helper creates a temporary validation directory
containing:

- the current committed `overlay_shadow_log` corpus
- the candidate payload under its proposed filename

It then runs the existing
`tools/registry/validate_overlay_shadow_logs.py` validator against that
temporary corpus. The helper only writes after validation succeeds.

The helper also refuses to overwrite an existing target file.

## What This Is Not

- scheduler
- cron
- event trigger
- watcher
- polling loop
- runtime bridge
- execution authority
- OMS authority
- risk authority
- policy change

## Boundary Notes

WP-7k adds only the runner. It does not:

- create a committed OSH entry by itself
- modify `OSH-0001` or `OSH-0002`
- modify `PGAS-0002`
- modify schemas or validators
- modify `lib/`, `src/`, or `configs/`
- create runtime influence

The helper is research-side, deterministic, validation-gated, and advisory
only.
