# JSON Sweep-Spec Materialization Design (WP-12t / AUTO-19)

## Package Metadata

- Package label: WP-12t / AUTO-19.
- Package title: JSON Sweep-Spec Materialization Design.
- Package class: Tier 1 documentation-only design package.
- Effective base: refreshed `main` after WP-12s / AUTO-18.
- Created design document: this file only.
- Modified status surface: `docs/project_status.md` only.
- No implementation files.
- No test files.
- No JSON spec instance files.

WP-12t creates no loader, JSON sweep-spec instance, schema, validator,
query-layer exposure, CLI, config, dependency, data change, committed output,
evidence bridge, dashboard, agent, scheduler, Monte Carlo, runtime,
paper/live, OMS, risk, safe-mode, exchange, broker, order, protected-path
behavior, or downstream authority.

## Purpose

WP-12t designs future local JSON sweep-spec materialization so sweep
definitions can become reusable local files instead of only in-memory Python
objects.

WP-12t does not implement a loader. It does not create JSON files, create a
schema, create a validator, expose query-layer views, or create authority
semantics. It does not replace the existing in-memory `ParameterSweepSpec`
API.

## Repo-Truth Foundation

Current merged repo truth establishes the following facts:

- WP-12p / AUTO-15 selected conservative local deterministic sweep semantics:
  finite, human-initiated, local-only parameter sweeps with static
  batch-compatible fan-out and structural aggregation only.
- WP-12q / AUTO-16 introduced the in-memory `ParameterSweepSpec`, deterministic
  point enumeration, local batch fan-out, local registry integration, and
  `local_parameter_sweep_summary.json` after batch and registry success.
- WP-12r / AUTO-17 exercised a second two-axis scalar sweep shape without
  helper changes.
- WP-12s / AUTO-18 checkpointed the tranche and required Main 4.0 approval
  before any next work.
- Main 4.0 approved the next mini-tranche as local parameter sweep usability
  plus result organization and authorized WP-12t as a design-only package for
  JSON sweep-spec materialization.

The current `ParameterSweepSpec` dataclass contains:

- `sweep_id`;
- `candidate_id`;
- `evaluation_purpose`;
- `data_refs`;
- `timeframe`;
- `evaluation_window`;
- `base_parameters`;
- `sweep_parameters`;
- `pipeline_version`;
- `static_metadata`.

The current helper remains local-only and non-authoritative. It accepts
explicit in-memory specs, requires caller-provided existing output roots,
enumerates finite deterministic grids, writes generated outputs only under
local caller-provided roots, and commits no outputs. JSON sweep-spec files are
not implemented. No schema, `tools.registry` validator, central query-layer
view, CLI, config, dependency, or data path exists for sweep specs.

## Design Goals

- Enable local-only reusable sweep definitions.
- Keep JSON materialization additive to the in-memory `ParameterSweepSpec`.
- Make local JSON material human-reviewable.
- Define a deterministic mapping from JSON material to the existing in-memory
  spec.
- Preserve compatibility with a future local loader.
- Preserve no-canonical-evidence posture.
- Avoid schema, validator, and query-layer authority.
- Avoid runtime, execution, paper/live, OMS, risk, safe-mode, exchange, broker,
  order, and downstream authority.

## Non-Goals

WP-12t does not:

- create JSON sweep-spec files;
- implement JSON loading;
- alter `ParameterSweepSpec`;
- deprecate the in-memory API;
- create schema authority;
- create `tools.registry` validator authority;
- create central query-layer exposure;
- create CLI, config, dependency, or data changes;
- create committed outputs;
- create dashboard, agent, scheduler, queue, watcher, trigger, or daemon
  behavior;
- create Monte Carlo or robustness execution;
- create an evidence bridge;
- touch runtime, paper, live, OMS, risk, safe-mode, exchange, broker, or order
  behavior;
- create protected-path behavior;
- create policy, scoring, ranking, recommendation, approval, promotion,
  demotion, readiness, lifecycle, or downstream authority.

## Alternatives Evaluated

### Alternative 1: Direct Dataclass Mirror

This shape would use JSON keys that closely mirror `ParameterSweepSpec`.

Pros:

- low impedance with the current dataclass;
- easy future loader mapping;
- minimal structural overhead.

Cons:

- may overfit to the current Python dataclass;
- leaves little room for file metadata, materialization versioning, and
  explicit locality markers;
- can blur local file posture with the in-memory API surface.

### Alternative 2: Wrapper Object With Explicit Metadata And `spec` Body

This shape uses top-level package/file metadata and locality markers around a
`parameter_sweep_spec` body.

Pros:

- clearer local-only posture;
- explicit loader metadata and versioning;
- boundary markers are visible before reading the spec body;
- future loader can reject unsupported materialization kinds before converting
  to `ParameterSweepSpec`.

Cons:

- more structure than a direct mirror;
- creates more fields for a future loader to check.

### Alternative 3: Manifest-Like Multi-Spec File

This shape would allow one JSON file to hold multiple sweep specs.

Pros:

- future batch ergonomics;
- one file could organize related local sweep definitions.

Cons:

- premature scale/platform behavior;
- higher loader complexity;
- increases risk of batch, scheduler, queue, or result-organization semantics
  entering before authorized.

### Selected Conservative V1 Direction

The conservative v1 direction is a single-spec wrapper object. The wrapper is
design guidance only, not schema authority, not a canonical artifact contract,
and not a `tools.registry` validated artifact family.

## Proposed Local JSON Shape

The proposed v1 material is one JSON object per file:

```json
{
  "spec_version": "wp12t-design-v1",
  "materialization_kind": "local_parameter_sweep_spec",
  "locality": {
    "local_only": true,
    "research_only": true,
    "non_authoritative": true,
    "creates_committed_evidence": false
  },
  "boundary_markers": [
    "additive_to_in_memory_parameter_sweep_spec",
    "not_canonical_research_artifact",
    "not_tools_registry_validated",
    "not_query_layer_exposed",
    "no_runtime_or_downstream_authority"
  ],
  "parameter_sweep_spec": {
    "sweep_id": "SWEEP-LOCAL-EXAMPLE",
    "candidate_id": "H-EXAMPLE",
    "evaluation_purpose": "local reusable sweep definition",
    "data_refs": ["local_fixture:example"],
    "timeframe": "1h",
    "evaluation_window": {
      "start": "2026-04-01T00:00:00Z",
      "end": "2026-04-02T00:00:00Z"
    },
    "base_parameters": {
      "mode": "example"
    },
    "sweep_parameters": {
      "threshold": [1, 2, 3]
    },
    "pipeline_version": "local_example_v1",
    "static_metadata": {
      "source_package": "future local caller"
    }
  }
}
```

The `parameter_sweep_spec` body maps to the current in-memory
`ParameterSweepSpec` concepts:

- `sweep_id`: local sweep identity.
- `candidate_id`: candidate context, not approval or promotion.
- `evaluation_purpose`: human-readable local purpose.
- `data_refs`: local references for the intended local run context.
- `timeframe`: intended evaluation timeframe.
- `evaluation_window`: expected `start` and `end` strings.
- `base_parameters`: parameters shared by every point.
- `sweep_parameters`: axis names and ordered values.
- `pipeline_version`: local pipeline/version context.
- `static_metadata`: optional string metadata.

This proposed shape is not a committed schema. It is not a canonical artifact
contract. It is not a `tools.registry` validated artifact family. WP-12u or a
later package must still implement and test any loader behavior separately. Any
later schema, validator, or query exposure requires separate Main
authorization.

## Locality And Path Posture

JSON sweep-spec files are local research material only. They must not be
placed in canonical `research/` evidence artifact directories and must not
become EXP, REP, OL, REC, LCH, registry, advisory, shadow, summary, or other
canonical corpus artifacts.

The recommended posture is caller-provided local paths at runtime or
untracked local work roots. This package creates no committed local spec files
and does not settle a canonical path convention.

## Relationship To In-Memory `ParameterSweepSpec`

JSON materialization is additive. The existing in-memory
`ParameterSweepSpec` API remains valid.

WP-12t does not deprecate, supersede, or replace the in-memory API. A future
loader should convert local JSON material into the existing in-memory
`ParameterSweepSpec` and then use the already established helper semantics if
that later package authorizes the vertical slice.

If a future design concludes that JSON should supersede in-memory semantics,
that requires a separate Main decision and is not authorized in this tranche.

## Future Loader Semantics For WP-12u

A future WP-12u loader, if separately authorized, should be local-only and
side-effect-free during load:

- read from an explicit caller-provided local file path;
- expect one top-level JSON object;
- support one spec per file for v1;
- check `materialization_kind` and `spec_version` before conversion;
- check local-only and boundary marker posture;
- convert deterministically into `ParameterSweepSpec`;
- preserve ordered axis values from JSON arrays;
- reject ambiguous, malformed, missing, unsupported, or duplicate material;
- accept no execution side effects during load;
- not run sweeps by itself unless WP-12u explicitly scopes that vertical
  slice;
- not write files unless a later package explicitly scopes output behavior.

Duplicate fields are not representable after standard JSON parsing in Python,
so a future loader that needs duplicate-key detection should use a parser mode
that can detect duplicates before object materialization. If duplicate-key
detection is not implemented in WP-12u, that limitation must be explicit in
that package.

Extra top-level fields should be rejected in v1 unless the future package
explicitly defines a local extension policy. Extra fields inside
`static_metadata` may be accepted only as inert string metadata and must not
be interpreted as authority.

## Error And Malformed-Material Policy

At design level, a future loader should treat malformed material as local
input failure, not as validator authority:

- Invalid JSON: fail before conversion and write nothing.
- Non-object top-level JSON: fail before conversion and write nothing.
- Missing required fields: fail with field-specific reasons and write nothing.
- Unexpected extra top-level fields: fail in v1.
- Unsupported `materialization_kind` or `spec_version`: fail before reading the
  spec body as executable intent.
- Non-local or ambiguous path claims: fail or ignore as inert text, depending
  on the field; never treat them as authority to read or write outside the
  caller-provided path.
- Malformed axes: fail for non-object `sweep_parameters`, non-array axis
  values, empty axes, invalid names, or base/sweep overlap.
- Duplicate axis values: fail using stable JSON serialization for equality,
  consistent with current helper behavior.
- Invalid boundary markers: fail before conversion.
- Unknown fields inside `static_metadata`: accept only inert string metadata
  or fail if non-string; do not create behavior from metadata.

This policy is not a formal schema and does not create a canonical validator.

## Boundary And Non-Authority Posture

JSON sweep specs and local sweep outputs are:

- local-only;
- research-only;
- non-authoritative;
- no-committed-evidence;
- not canonical research artifacts;
- not bridges to EXP, REP, OL, REC, LCH, registry, advisory, shadow, summary,
  or evidence families;
- not query-layer exposed;
- not `tools.registry` validated;
- not scoring, ranking, recommendation, approval, promotion, demotion,
  readiness, lifecycle, policy, runtime, paper/live, OMS, risk, safe-mode,
  exchange, broker, order, or downstream authority.

## Open / Deferred Items

- JSON loader implementation.
- JSON spec instance files.
- JSON spec validation helper.
- Formal schema.
- `tools.registry` validator.
- Query-layer exposure.
- Exact local path conventions.
- Larger sweep limits.
- Richer parameter value support.
- Result organization and index design.
- Per-point registry indexing.
- Dashboard, agent, and scheduler behavior.
- Monte Carlo and robustness work.
- Evidence bridge.
- Runtime, paper, and live integration.

## Non-Claims

WP-12t does not create implementation, tests, JSON spec instances, schemas,
validators, query-layer exposure, CLI, config, dependency, data changes,
committed outputs, evidence artifacts, evidence bridge, dashboard, agent,
scheduler, daemon, queue, watcher, trigger, Monte Carlo, runtime, paper/live,
OMS, risk, safe-mode, exchange, broker, order behavior, protected-path
behavior, or downstream authority.

WP-12t does not create optimizer authority, best-parameter authority, ranking
authority, scoring authority, recommendation authority, approval authority,
promotion authority, demotion authority, readiness authority, lifecycle
authority, policy authority, runtime authority, paper/live authority, or
evidence authority.
