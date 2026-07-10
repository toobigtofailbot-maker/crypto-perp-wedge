# WP-CANON-INTAKE-ARCHITECTURE-DESIGN-01 Status

## Decision

`READY_FOR_KARL_ARCHITECTURE_REVIEW`

## Summary

Design-only architecture for scratch draft to canonical Strategy Spec to
bounded offline research queue. It proposes two separate Karl exact-content
gates: Gate C for one append-only, hash-bound canonical Strategy Spec write and
Gate Q for a later hash-bound Spec/Variant Manifest/Sweep Plan plus budget and
priority queue admission. `flagged_for_canonicalization` is annotation only.

The proposal is at least as strict as current prereg/freeze repo truth. A UI
action alone can never approve or write canonical or queue artifacts, and
`tools.agent_inbox_intake` can never write canonical artifacts.

## Changed files

- `docs/architecture/scratch_to_canonical_intake_control_plane.md`
- `docs/status_entries/WP-CANON-INTAKE-ARCHITECTURE-DESIGN-01.md`
- `scratch/WP-CANON-INTAKE-ARCHITECTURE-DESIGN-01/repo_truth_discovery.md`
- `scratch/WP-CANON-INTAKE-ARCHITECTURE-DESIGN-01/architecture_decision_record.md`
- `scratch/WP-CANON-INTAKE-ARCHITECTURE-DESIGN-01/failure_modes.md`
- `scratch/WP-CANON-INTAKE-ARCHITECTURE-DESIGN-01/validation_summary.txt`

## Authority and next step

No implementation, code, schema, validator, query, canonical artifact, queue,
Result Population, candidate lifecycle, API, UI, scheduler, paper/live/runtime,
or protected-path change is included. Future capsules C1-C5 are not draftable
until Karl approves this architecture and its decision points.
