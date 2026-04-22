# Overlay Shadow External Hook

## Why This Package Is Next

WP-7a proved the first deterministic advisory agent output. WP-6j proved the
first deterministic advisory score-bucket mapper. WP-7c proved the next narrow
step: comparing the mapper bucket to an externally observable overlay-adjacent
bucket without changing protected overlay behavior. WP-7i extends that exact
hook path so it can also compare the committed PGAS combined advisory bucket
without creating a parallel hook or changing protected runtime behavior.

## Why The Hook Is Outside `lib/`

The package is intentionally outside `lib/` because the goal is observability,
not integration. The hook reads committed research/support artifacts and writes
only a research-side shadow log when explicitly invoked. It does not import
overlay runtime code, mutate runtime paths, or alter execution decisions.

## Observed Source Pair

The historical BMAP-sourced comparison uses:

- mapper source: `research/bucket_mappings/BMAP-0001.bucket_mapping.json`
- source agent output: `research/agent_outputs/AOUT-0001.agent_output.json`
- external overlay-side source: `tests/fixtures/context_snapshot_sample.json`
  plus `configs/fmp_macro_flags.json`

The external source pair is evaluated at `BMAP-0001.as_of_timestamp`,
`2026-04-19T17:00:00Z`. The committed macro context fixture has no active
window at that timestamp, so the observed overlay-side bucket is `ALLOW`.

The additive PGAS-sourced comparison uses:

- pre-gate source: `research/pre_gate_advisory_snapshots/PGAS-0002.pre_gate_advisory_snapshot.json`
- inherited mapping source: `research/bucket_mappings/BMAP-0001.bucket_mapping.json`
- inherited source agent output: `research/agent_outputs/AOUT-0001.agent_output.json`
- external overlay-side source: `tests/fixtures/context_snapshot_sample.json`
  plus `configs/fmp_macro_flags.json`

The PGAS path preserves the same external observation method and simply shifts
the evaluation timestamp to `PGAS-0002.as_of_timestamp`,
`2026-04-19T18:00:00Z`. The committed fixture still has no active window at
that timestamp, so the observed overlay-side bucket remains `ALLOW`.

## Logged Comparison

`BMAP-0001` maps `AOUT-0001` to `ALLOW_REDUCED` with `size_multiplier = 0.5`.
`PGAS-0002` applies `MACRO_AWARE_FLOOR` and currently has
`combined_bucket = ALLOW_REDUCED`, so both current paths compare the same
advisory bucket against the observed overlay bucket.

`OSH-0001` therefore records:

- observed overlay bucket: `ALLOW`
- mapped bucket: `ALLOW_REDUCED`
- comparison result: `MISMATCH`
- override applied: `false`
- fail-open preserved: `true`
- advisory only: `true`

`OSH-0002` records the same comparison outcome, but with
`advisory_source = PGAS` and `source_pre_gate_advisory_snapshot_id = PGAS-0002`.
That identical outcome is informative, not defective: the variable under test is
the advisory-source path, not a new overlay-input scenario.

These mismatches are evidence only. They do not change the authoritative
overlay bucket.

## Why This Remains Zero-Override

The original overlay-side bucket remains authoritative. The mapper bucket is
advisory-only, and the shadow log is append-only research evidence. Missing or
invalid mapper input cannot affect runtime behavior because no runtime path
reads this artifact family.

## Why Deeper Overlay Contact Is Deferred

Any deeper contact with overlay runtime behavior would be a separate,
higher-risk package. WP-7c and WP-7i stop at external observation and
comparison so the project can review the evidence pattern before considering any
future shadow or integration path.
