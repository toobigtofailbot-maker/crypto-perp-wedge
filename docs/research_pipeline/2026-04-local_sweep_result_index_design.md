# Local Sweep Result Index / Organization Design

## Package Metadata

- Package label: WP-12v / AUTO-21.
- Package title: Local Sweep Result Index / Organization Design.
- Package class: Tier 1 documentation-only design package.
- Effective base: refreshed `main` after merged WP-12u / AUTO-20.
- Created design document: this file only.
- Modified status surface: `docs/project_status.md` only.
- No implementation files.
- No test files.
- No generated output files.
- No JSON instance files.

WP-12v creates no result index file, implementation, tests, JSON spec
instances, schema, validator, query-layer exposure, CLI, config, dependency,
data change, committed output, evidence bridge, dashboard, agent, scheduler,
Monte Carlo, runtime, paper/live, OMS, risk, safe-mode, exchange, broker,
order, protected-path behavior, or downstream authority.

## Purpose

WP-12v designs how local parameter sweep outputs should be organized and
indexed structurally before any implementation package.

The design is local-only, research-only, structural, and non-authoritative. It
does not implement an index, change existing helpers, or create artifact,
schema, validator, query, evidence, or runtime authority.

## Repo-Truth Foundation

Current merged repo truth establishes the following facts:

- WP-12p / AUTO-15 selected conservative local deterministic sweep semantics:
  finite, human-initiated, local-only sweeps with static batch-compatible
  fan-out and structural aggregation only.
- WP-12q / AUTO-16 introduced the in-memory `ParameterSweepSpec`, deterministic
  point enumeration, local batch fan-out, local registry integration, and
  `local_parameter_sweep_summary.json` after batch and registry success.
- WP-12r / AUTO-17 exercised a two-axis scalar sweep without helper changes.
- WP-12s / AUTO-18 checkpointed the first parameter sweep tranche.
- WP-12t / AUTO-19 designed local JSON sweep-spec materialization.
- WP-12u / AUTO-20 implemented the local JSON sweep-spec loader and
  JSON-driven wrapper.
- Current local sweep outputs are produced under caller-provided local roots and
  are not committed.
- Current local registry integration records actual returned registry record
  IDs and does not fabricate per-point registry IDs.

The current sweep summary file is `local_parameter_sweep_summary.json`. Its
structural fields include sweep identity, implementation/package identity,
point counts, point results, batch ID, batch summary references, registry file
reference, actual registry record IDs, checked boundaries, local-only and
research-only markers, non-authoritative status, no-committed-evidence status,
and protected-boundary status.

Current local batch output names include `batch_manifest.json`,
`batch_validation_report.json`, `local_batch_run_summary.json`, and
`local_batch_run_summary_validation.json`. Current local registry output is
`local_run_registry.json`.

The current sweep helper calls `build_local_run_registry((output_root,),
registry_output_root)`, so registry integration is rooted at the local batch
output root. Current repo truth does not provide fabricated per-point registry
records for sweep points.

`run_local_json_parameter_sweep(...)` first loads one caller-provided local JSON
file through `load_local_json_sweep_spec(...)`. On successful load, it delegates
to the existing `run_local_parameter_sweep(...)` helper. It adds no output
behavior and does not interpret sweep outcomes.

No result organization or result indexing helper is currently implemented for
sweep outputs. No schema, `tools.registry` validator, query-layer exposure,
CLI, config, dependency, data, evidence bridge, runtime authority, or protected
path behavior exists for sweep result organization.

## Problem Statement

JSON-driven and in-memory sweeps can now produce repeatable local output sets.
Those outputs currently depend on caller-provided roots, local batch summaries,
local registry records, and sweep summary files.

Without a design for grouping, linking, and retrieval posture, modest repeated
sweeps become hard to inspect across JSON spec source, sweep summary, batch
summary, registry file, point IDs, and output subpaths.

The problem is structural organization only. It is not interpretation,
ranking, scoring, evidence promotion, lifecycle state, or runtime decisioning.

## Design Goals

- Keep result organization local-only and structural.
- Deterministically group one sweep run and its related local files.
- Link JSON spec file path or in-memory spec identity to the local sweep
  summary, local batch output root, local batch summary, local registry file,
  actual returned registry record IDs, sweep point IDs, and output subpaths.
- Stay compatible with existing `local_parameter_sweep.py`.
- Stay compatible with existing `local_json_sweep_spec_loader.py`.
- Avoid changes to the existing local registry shape unless a later package
  explicitly authorizes them.
- Avoid query-layer exposure.
- Avoid evidence bridge behavior.
- Avoid scoring, ranking, recommendation, approval, promotion, readiness,
  lifecycle, policy, or runtime-action semantics.

## Non-Goals

WP-12v does not:

- implement result indexing;
- change `local_parameter_sweep.py`;
- change `local_json_sweep_spec_loader.py`;
- change `local_batch_runner.py`;
- change `local_run_registry.py`;
- change `local_run_registry_validation.py`;
- create schema authority;
- create `tools.registry` validator authority;
- create query-layer exposure;
- create CLI, config, dependency, or data changes;
- create committed outputs;
- create JSON spec instances;
- create result-store or evidence bridge behavior;
- create dashboard, agent, scheduler, queue, watcher, or trigger behavior;
- create Monte Carlo or robustness execution;
- touch runtime, paper/live, OMS, risk, safe-mode, exchange, broker, or order
  behavior;
- create protected-path behavior;
- create policy, scoring, ranking, recommendation, approval, promotion,
  demotion, readiness, lifecycle, downstream, or runtime authority.

## Alternatives Evaluated

### Alternative 1: No New Index; Rely On Current Output Roots And Summaries

Pros:

- zero new surface area;
- no additional local file to manage;
- current helper behavior remains sufficient for isolated one-off inspection.

Cons:

- poor repeated-sweep ergonomics;
- weak grouping across JSON spec source, sweep summary, batch summary, and
  registry file;
- caller must reconstruct relationships from several local files manually.

### Alternative 2: Sidecar Local Sweep Result Index File

This option uses one structural local sidecar file per sweep output root, such
as a future `local_sweep_result_index.json`. It records file links, IDs, point
counts, paths, and boundary markers only.

Pros:

- narrow and local;
- compatible with the existing registry;
- avoids central query-layer exposure;
- can group in-memory and JSON-driven sweeps without making JSON specs
  canonical artifacts.

Cons:

- one more local file;
- future validation questions remain deferred;
- future implementation must preserve no-write-before-success behavior.

### Alternative 3: Extend Existing Local Run Registry

This option adds sweep result grouping directly into local run registry records.

Pros:

- one local registry surface;
- fewer local output files for callers to inspect.

Cons:

- risks breaking WP-12m through WP-12o registry semantics;
- couples sweep result organization to registry shape before repo truth shows
  that need;
- may imply per-point registry behavior before it is authorized.

### Alternative 4: Central Query-Layer Exposure

Pros:

- easier lookup across runs.

Cons:

- forbidden now;
- widens into canonical/query authority;
- risks evidence posture and downstream authority drift.

### Selected Conservative V1 Direction

The conservative v1 direction is Alternative 2: a future local sidecar result
index. This remains design guidance only. It is not schema authority, not a
canonical artifact contract, and not a `tools.registry` validated artifact
family.

## Proposed Conservative V1 Result-Index Shape

A future implementation slice may write one local sidecar file named:

```text
local_sweep_result_index.json
```

The proposed design-level shape is structural only and may include fields such
as:

```text
index_version
index_kind
sweep_id
spec_source
loader_source
sweep_summary_file
batch_output_root
batch_summary_file
batch_summary_validation_file
registry_file
registry_record_ids
point_count
point_refs
checked_boundaries
local_only
research_only
non_authoritative
creates_committed_evidence
```

`point_refs` may include only structural fields such as:

```text
point_id
point_index
output_path
batch_item_id
dry_run_run_id
status
```

The proposed shape must explicitly forbid authority fields such as:

```text
best_parameter
winner
rank
score
recommendation
approval
promotion
readiness
lifecycle
policy_action
runtime_action
paper_live_readiness
```

This proposed shape is:

- not implemented in WP-12v;
- not a schema;
- not a canonical artifact contract;
- not a `tools.registry` validated artifact family;
- not query-layer exposed;
- not evidence bridge material.

## Relationship To Current Local Registry

The current local registry remains valid and unchanged. WP-12v does not
authorize registry-shape changes.

A future local result index should record registry IDs actually returned by the
current helpers. It must not fabricate per-point registry IDs. Per-point
registry indexing remains deferred unless repo truth later supports it without
scope expansion.

If a future implementation requires changing existing registry semantics, that
is a stop condition for that implementation slice.

## Relationship To JSON Loader

WP-12u JSON loader behavior remains valid and unchanged.

Local result indexing should be compatible with both in-memory and JSON-driven
sweeps. If a JSON spec path is recorded, it remains a local caller-provided
path/reference only. The index must not treat JSON specs as canonical artifacts
or evidence.

For in-memory sweeps, `spec_source` should remain structural identity material,
not a new artifact requirement. For JSON-driven sweeps, `loader_source` may
record the local loader wrapper context as structural provenance only.

## Future Implementation Expectations

A future WP-12w implementation slice may, if separately authorized:

- write one structural sidecar index after successful local sweep summary
  creation;
- write under caller-provided local output roots only;
- use existing local sweep result fields and existing registry IDs;
- avoid running sweeps by itself;
- avoid altering existing helper semantics unless explicitly scoped;
- avoid writing committed outputs;
- add focused tests for no writes before success, boundary flags, forbidden
  authority fields, and exact file scope.

This section does not implement code and does not authorize WP-12w.

## Open / Deferred Items

- Result index implementation.
- Any index validation helper.
- Any formal schema.
- Any `tools.registry` validator.
- Any query-layer exposure.
- Any local path convention beyond the proposed v1 sidecar.
- Per-point registry indexing.
- Richer result retrieval tools.
- Dashboard, agent, and scheduler behavior.
- Monte Carlo and robustness execution.
- Evidence bridge.
- Runtime, paper, and live integration.

## Non-Claims

WP-12v does not create implementation, tests, result index files, JSON spec
instances, schemas, validators, query-layer exposure, CLI, config, dependency,
data changes, committed outputs, generated outputs, evidence artifacts,
evidence bridge, dashboard, agent, scheduler, daemon, queue, watcher, trigger,
Monte Carlo, runtime, paper/live, OMS, risk, safe-mode, exchange, broker, order
behavior, protected-path behavior, or downstream authority.

WP-12v does not create optimizer authority, best-parameter authority, ranking
authority, scoring authority, recommendation authority, approval authority,
promotion authority, demotion authority, readiness authority, lifecycle
authority, policy authority, runtime authority, paper/live authority, evidence
authority, query authority, schema authority, or validator authority.
