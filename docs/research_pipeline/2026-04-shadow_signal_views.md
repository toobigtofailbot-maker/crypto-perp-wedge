# Shadow Signal Views (WP-7d)

## Purpose

The shadow signal views are the first aggregate diagnostic consumption layer over
the existing overlay shadow log family. They make mapper-vs-overlay comparison
evidence readable as a class over time, while preserving the original
entry-level shadow logs as the source of truth.

## Consumed Shadow-Log Family

These views consume `research/overlay_shadow_logs/*.overlay_shadow_log.json` via
the existing read-only `overlay_shadow_logs` relation. WP-7d reuses the WP-7c
schema, validator, external shadow hook, baseline query views, and committed
`OSH-0001` instance. WP-7i extends those exact surfaces additively with
`advisory_source` segmentation and the first PGAS-sourced entry, `OSH-0002`.

## New Views

`v_overlay_shadow_agreement_summary` now groups committed shadow logs by
`advisory_source` plus `comparison_result`. It reports entry count, match count,
mismatch count, override-true count, and the first and last observed timestamps
for each advisory-source comparison class.

`v_overlay_shadow_override_audit` is a strict zero-override audit surface. It
returns rows only when a shadow log records `override_applied=true`,
`fail_open_preserved=false`, or `advisory_only=false`. WP-7i preserves the same
zero-override audit rule while exposing `advisory_source` additively.

## Interpreting MATCH And MISMATCH

`MATCH` means the observed overlay bucket and the advisory mapped bucket agreed
for a committed shadow-log observation. `MISMATCH` means they differed. A
mismatch is diagnostic evidence only: it can motivate review, but it does not
recommend a policy change and does not authorize overlay behavior changes.

The current two committed entries are useful for proving both the historical
BMAP path and the additive PGAS path, but they are still only evidence points.
They are not enough evidence for promotion, demotion, or policy change.
Shadow-log evidence should be reviewed over time alongside the entry-level logs,
source references, and existing integrity views.

## Zero Override Boundary

`override_applied=true` remains out of scope. Shadow logs compare advisory
mapper output with externally observable overlay-side behavior, but they do not
change execution, risk, OMS, or overlay decisions. Fail-open behavior must remain
preserved, and shadow evidence must remain advisory-only.

## Read-Only And Advisory-Only

The query layer loads these views into an in-memory DuckDB connection. The views
only read committed artifacts and do not write research evidence, call external
data sources, or contact runtime paths. They are a structural diagnostic aid for
Phase 2c signal accumulation and review.
