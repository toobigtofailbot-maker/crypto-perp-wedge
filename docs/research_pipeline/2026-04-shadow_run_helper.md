# Manual / On-Demand Shadow-Run Helper

## Purpose

`tools/shadow/shadow_run_helper.py` is a manual helper for building one
candidate `overlay_shadow_log` artifact from explicit committed advisory
evidence plus explicit overlay-input references. It exists to let a human
operator produce and validate a candidate shadow-log payload without changing
any protected runtime path.

## What The Helper Does

- Accepts an explicit advisory source: `BMAP` or `PGAS`.
- Accepts an explicit source artifact id for that advisory source.
- Accepts additive explicit overlay-input path pairs through
  `--context-snapshot-path` plus `--macro-flags-path`.
- Preserves legacy canonical-only `--snapshot` and `--config` arguments for
  backward compatibility.
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
- prints whether canonical or explicit overlay-input paths were used
- prints the snapshot/config paths used for the observation
- runs corpus-aware validation when the observation source remains schema-valid
- keeps noncanonical explicit-path dry-runs helper-local and reports that
  corpus validation is skipped under the current schema lock
- writes nothing to the repo

Write mode is explicit. `--write` must be present before the helper can create
an `overlay_shadow_log` file.

## Deterministic Inputs

The helper requires:

- `--advisory-source {BMAP,PGAS}`
- `--advisory-artifact-id`
- `--timestamp`

`--timestamp` must be UTC and is used for both `observed_at` and
`observation_source.evaluation_time_utc`. Identical arguments, including the
same timestamp, produce byte-identical payload output.

Overlay-input path handling is additive and backward-compatible:

- if `--context-snapshot-path` and `--macro-flags-path` are both omitted, the
  helper uses the current canonical defaults:
  - `tests/fixtures/context_snapshot_sample.json`
  - `configs/fmp_macro_flags.json`
- if `--context-snapshot-path` and `--macro-flags-path` are both supplied, the
  helper uses those explicit files for the observation input
- partial explicit mode is forbidden; both new arguments must be supplied
  together or omitted together
- legacy `--snapshot` and `--config` remain accepted, but only as
  backward-compatible canonical-path aliases
- legacy `--snapshot` / `--config` cannot be mixed with the new explicit-path
  pair in one invocation

When the new explicit-path pair is omitted, canonical/default behavior remains
byte-identical to the currently merged helper behavior.

The helper validates explicit overlay-input files locally before payload build:

- the file must exist
- the file must be readable
- the file must parse as JSON

This package does not add schema validation for those explicit files.

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

Noncanonical explicit overlay-input paths are currently dry-run only. Write mode
remains blocked for noncanonical explicit paths because the current
`overlay_shadow_log` schema and validator still lock
`observation_source.snapshot_path` and `observation_source.config_path` to the
canonical fixture paths. Dry-run still succeeds after helper-local path and
JSON checks, but corpus validation is reported as skipped for those
noncanonical explicit inputs. A later package can widen that contract
explicitly if needed.

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

WP-7q-prep does not introduce new fixtures or new shadow entries. It only
widens the helper surface so later WP-7q work can honestly consume additive
overlay-input fixtures through explicit helper arguments.

The helper is research-side, deterministic, validation-gated, and advisory
only.
