# Local Parameter Sweep Vertical Slice (WP-12q / AUTO-16)

## Package Metadata

- Package label: WP-12q / AUTO-16.
- Package title: Parameter Sweep Vertical Slice.
- Package class: Tier 3 local automation vertical slice.
- Effective base: refreshed `main` after merged WP-12p / AUTO-15.
- Implementation module: `tools/research_automation/local_parameter_sweep.py`.
- Test module: `tests/research_automation/test_local_parameter_sweep.py`.

WP-12q is the first Tier 3 local automation vertical slice after WP-12p.

## Purpose

WP-12q implements a minimal local parameter sweep helper. It accepts one
explicit caller-provided in-memory sweep specification object, deterministically
enumerates a small finite grid, fans sweep points into existing local
batch-run-compatible work, builds the existing local run registry, and writes
one structural local sweep summary only after batch and registry success.

The slice exercises the WP-12d through WP-12o local automation foundation
without creating downstream authority.

## Scope

The package creates one helper module, one focused test module, and this
vertical-slice document. It updates `docs/project_status.md` with a narrow
branch-state entry.

The helper uses caller-provided existing output roots only. Generated outputs
are local-only and must not be committed.

## Non-Goals

WP-12q does not create a CLI, platform, scheduler, daemon, queue, watcher,
trigger, dashboard, agent, evidence bridge, Monte Carlo behavior, formal
schema, tools.registry validator, central query-layer exposure, config,
dependency, data file, committed output, or committed evidence artifact.

WP-12q creates no optimizer framing, best/winner selection, ranking, scoring,
recommendation, approval, promotion, demotion, readiness, lifecycle, policy,
runtime, paper/live, OMS, risk, safe-mode, exchange, broker, order,
protected-path, or downstream authority.

## Dependency Foundation

WP-12d writes local dry-run material. WP-12f writes local batch manifest
material. WP-12h runs local batch items. WP-12j validates local batch-run
summary material. WP-12k integrates that validation before summary persistence.
WP-12m builds a local run registry. WP-12n validates local registry material.
WP-12o integrates registry validation before `local_run_registry.json`
persistence.

WP-12q uses existing local batch and local registry helpers instead of creating
a parallel runner.

## WP-12p Design Alignment

WP-12p selected finite deterministic, human-initiated, local-only parameter
sweeps with static batch-compatible fan-out and structural aggregation only.

WP-12q implements only the first local representation and vertical slice of
that direction. It does not parse, write, validate, or commit a JSON sweep
specification file. JSON file loading/writing, exact file naming, exact file
shape, and any separate sweep-spec validation remain deferred.

## Implemented Vertical Slice

The implemented flow is:

```text
explicit in-memory ParameterSweepSpec
-> deterministic sweep points
-> BatchManifestItem fan-out
-> run_local_batch(...)
-> build_local_run_registry(...)
-> local_parameter_sweep_summary.json
```

The summary is written only after the local batch run and local registry build
both succeed and preserve protected boundaries.

## Sweep Specification Shape

`ParameterSweepSpec` is an in-memory dataclass and the first local
representation of the future local JSON sweep specification shape selected by
WP-12p.

It contains sweep identity, candidate context, evaluation purpose, local data
references, timeframe, evaluation window, base parameters, sweep parameter
axes, pipeline version, and static metadata. It is not a schema and not a
committed artifact contract.

## Deterministic Enumeration Behavior

The helper validates the spec before execution. It rejects missing output
roots, invalid point limits, empty grids, empty axes, ambiguous parameter
names, base/sweep parameter overlap, duplicate axis values, excessive point
counts, and non-JSON-serializable parameter values.

Sweep axes are enumerated by lexicographic parameter name. Values preserve the
caller-provided sequence order within each axis. Point indexes are 1-based.
Stable point IDs are derived from deterministic hashes over package identity,
sweep identity, point index, point parameter values, and combined parameters.

No timestamps, random UUIDs, filesystem-wide discovery, or nondeterministic
ordering are used.

## Fan-Out To Local Batch Behavior

Each sweep point becomes one `BatchManifestItem`. The sweep point ID is used as
the batch item `source_id`, and the item receives combined base plus sweep
parameters.

The helper calls `run_local_batch(...)` exactly once with all sweep-point
items, conservative local resource limits, and static package metadata. Point
output paths are top-level local paths such as `sweep-point-0001`.

## Local Registry Integration Behavior

After batch success, the helper calls
`build_local_run_registry((output_root,), registry_output_root)`.

Registry record IDs in the sweep summary are the actual IDs returned by the
existing registry helper. WP-12q does not fabricate per-point registry IDs. If
the current registry produces one batch-level record for the sweep batch output
root, that is acceptable for WP-12q.

## Structural Summary Behavior

On success, the helper writes exactly
`local_parameter_sweep_summary.json` under the caller-provided batch output
root.

The summary records sweep ID, point count, per-point parameter values,
per-point output references, local batch status, local batch summary and
validation references, local registry file reference, actual registry record
IDs, non-interpretive counts, failure reasons, and local boundary markers.

Aggregation is structural only and non-authoritative.

## Failure Behavior

Pre-execution validation failures call no downstream helper, write no files,
and create no directories.

Batch or registry failures do not delete downstream local files already written
by existing helpers. They also do not write
`local_parameter_sweep_summary.json`.

## Test Coverage Summary

Tests cover successful one-axis sweep execution, deterministic enumeration,
batch-compatible fan-out, local registry integration, missing output roots,
missing registry roots, empty grids, excessive point count, duplicate
parameter values, base/sweep overlap, non-serializable values, downstream batch
failure, downstream registry failure, boundary marker preservation, and absence
of positive interpretive authority fields in the summary JSON.

Generated test outputs are created only under `tmp_path`.

## Local-Only / Non-Authoritative Boundary

All result structures preserve:

- `local_only=True`;
- `research_only=True`;
- `non_authoritative=True`;
- `creates_committed_evidence=False`.

The helper is human-initiated and local-only. It produces local output material
only and creates no committed evidence.

## No Schema / Validator / Query-Layer Boundary

WP-12q creates no formal schema, no separate sweep-spec validator, no
tools.registry validator, and no central query-layer exposure.

Internal helper checks are local guard behavior only. They are not a canonical
artifact contract.

## No CLI / Scheduler / Platform Boundary

WP-12q exposes only an in-process helper. It creates no CLI, platform,
scheduler, daemon, queue, watcher, trigger, service loop, or autonomous
execution surface.

## No Monte Carlo / Dashboard / Agent / Evidence Bridge Boundary

WP-12q creates no Monte Carlo behavior, dashboard surface, agent behavior, or
evidence bridge.

Sweep outputs do not become EXP, REP, OL, REC, LCH, registry, advisory, shadow,
summary, canonical evidence, or committed evidence artifacts.

## Protected Runtime / Paper / Live Boundary

WP-12q does not contact or authorize runtime, paper/live, OMS, risk, safe-mode,
exchange, broker, order, execution, deployment, live-trading, or protected-path
behavior.

## Known Limitations

- The sweep specification is in-memory only.
- There is no JSON sweep-spec file loading or writing.
- There is no separate sweep-spec validation artifact.
- The default point-count limit is intentionally small.
- Current registry behavior indexes the sweep batch output root as one
  batch-level local registry record.
- Per-point registry indexing is not implemented unless a later package
  separately authorizes it.

## Open / Deferred Items

Deferred items include JSON sweep-spec file loading/writing, exact sweep-spec
file naming, exact file shape, separate sweep-spec validation, larger point
limits, richer parameter value support, parallelism, and any per-point registry
indexing if current repo truth does not already provide it.

## Likely WP-12r Direction, Non-Binding

WP-12r may exercise a second local parameter sweep shape if separately drafted
and accepted. WP-12q does not authorize WP-12r.

## Non-Claims

WP-12q creates no schema, tools.registry validator, central query-layer
exposure, CLI, config, dependency, data, committed output, result-store
implementation, dashboard, agent, scheduler, daemon, queue, watcher, trigger,
Monte Carlo behavior, evidence bridge, runtime, paper/live, OMS, risk,
safe-mode, exchange/broker/order, protected-path behavior, optimizer/scoring/
ranking/recommendation, approval, promotion, demotion, readiness, lifecycle,
policy, or downstream authority.
