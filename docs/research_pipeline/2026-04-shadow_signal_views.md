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
`OSH-0001` instance. It does not create a new schema, validator, hook, or
shadow-log entry.

## New Views

`v_overlay_shadow_agreement_summary` groups committed shadow logs by
`comparison_result`. It reports entry count, match count, mismatch count,
override-true count, and the first and last observed timestamps for each
comparison class.

`v_overlay_shadow_override_audit` is a strict zero-override audit surface. It
returns rows only when a shadow log records `override_applied=true`,
`fail_open_preserved=false`, or `advisory_only=false`.

## Interpreting MATCH And MISMATCH

`MATCH` means the observed overlay bucket and the advisory mapped bucket agreed
for a committed shadow-log observation. `MISMATCH` means they differed. A
mismatch is diagnostic evidence only: it can motivate review, but it does not
recommend a policy change and does not authorize overlay behavior changes.

The current single committed entry is useful for proving the evidence path, but
one observation is not enough evidence for promotion, demotion, or policy
change. Shadow-log evidence should be reviewed over time alongside the
entry-level logs, source references, and existing integrity views.

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
