# JSON Sweep-Spec Loader Vertical Slice

## Package Metadata

- Package: WP-12u / AUTO-20
- Class: Tier 3 local automation implementation slice
- Implementation: `tools/research_automation/local_json_sweep_spec_loader.py`
- Tests: `tests/research_automation/test_local_json_sweep_spec_loader.py`
- Dependency: merged WP-12t / AUTO-19 JSON sweep-spec materialization design

## Purpose

WP-12u implements the first local JSON sweep-spec loader/materialization slice. It lets a caller provide one local JSON file in the WP-12t single-spec wrapper shape and converts the contained `parameter_sweep_spec` into the existing in-memory `ParameterSweepSpec`.

The JSON material is local-only, research-only, additive to the in-memory parameter sweep API, non-canonical, and non-authoritative.

## Implementation Summary

The loader reads exactly one caller-provided JSON path, detects duplicate JSON object keys before object materialization, validates the local wrapper posture, and converts valid JSON arrays into the tuple fields expected by `ParameterSweepSpec`.

The loader accepts the WP-12t wrapper fields:

- `spec_version`
- `materialization_kind`
- `locality`
- `boundary_markers`
- `parameter_sweep_spec`

It supports only `spec_version="wp12t-design-v1"` and `materialization_kind="local_parameter_sweep_spec"`.

## Loader Behavior

`load_local_json_sweep_spec(...)` performs no writes, creates no directories, and performs no sweep execution. Invalid input returns `spec=None`, failure reasons, and `protected_boundary_preserved=False`.

Successful loads preserve:

- `local_only=True`
- `research_only=True`
- `non_authoritative=True`
- `creates_committed_evidence=False`
- `protected_boundary_preserved=True`

The loader rejects malformed or ambiguous material including missing files, directories, invalid JSON, duplicate object keys, non-object top-level JSON, missing or extra top-level fields, unsupported version or kind, invalid locality, missing boundary markers, invalid `ParameterSweepSpec` fields, bare-string `data_refs`, invalid evaluation-window fields, invalid parameter names, base/sweep overlap, non-array or empty sweep axes, duplicate sweep axis values, and non-string `static_metadata` values.

## JSON-Driven Wrapper Behavior

`run_local_json_parameter_sweep(...)` first calls the loader. If loading fails, it does not call downstream sweep execution.

On successful load, it delegates exactly once to the existing `run_local_parameter_sweep(...)` helper with the loaded `ParameterSweepSpec`, caller-provided output roots, and caller-provided `max_point_count`. It does not add output behavior and does not interpret sweep outcomes.

## Tests Added

The WP-12u test file covers valid materialization, tuple conversion, ordered axis preservation, wrapper delegation, invalid JSON, non-object top-level JSON, missing and extra fields, unsupported version and kind, invalid locality and boundary markers, invalid `data_refs`, missing evaluation window fields, invalid sweep axes, duplicate axis values, invalid parameter names, base/sweep overlap, duplicate JSON key detection, invalid `static_metadata`, boundary flags, and absence of authority fields.

All JSON spec files used by tests are temporary files under `tmp_path`.

## Known Limitations And Deferred Items

- JSON spec files remain local caller-provided inputs.
- No JSON spec files are committed.
- No schema is created.
- No `tools.registry` validator is created.
- No query-layer exposure is created.
- No CLI is created.
- No configs, dependencies, or data are changed.
- No result organization or indexing is implemented.
- No evidence bridge is created.
- No dashboard, agent, scheduler, or Monte Carlo behavior is created.

## Boundary And Non-Authority Posture

WP-12u touches no runtime, paper-live, OMS, risk, safe-mode, exchange, broker, order, protected-path, or live-trading behavior.

It creates no policy, scoring, ranking, recommendation, approval, promotion, demotion, readiness, lifecycle, runtime action, or downstream authority.

Any next package requires separate authorization.
