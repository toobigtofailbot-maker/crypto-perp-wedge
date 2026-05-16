# Local Run Registry Vertical Slice (WP-12m / AUTO-12)

## Package Metadata

- Package label: WP-12m / AUTO-12.
- Package title: Local Run Registry Vertical Slice.
- Package class: Tier 3 local automation infrastructure vertical slice.
- Effective base: refreshed `main` after merged WP-12l / AUTO-11.
- Implementation module: `tools/research_automation/local_run_registry.py`.
- Test module: `tests/research_automation/test_local_run_registry.py`.

WP-12m is the first narrow implementation slice for the local run registry
concept described by WP-12l.

## Purpose

WP-12m implements a minimal helper that indexes explicit caller-provided local
dry-run and local batch-run output roots. When all validation passes, it writes
one local `local_run_registry.json` file under a caller-provided registry
output root.

The registry file is local output material only. It is not repo truth,
committed evidence, a formal schema, a central query-layer contract, a
registry validator, or downstream authority.

## Scope

The slice creates one library helper, one focused test module, and this
vertical-slice document. It updates `docs/project_status.md` with a narrow
branch-state entry.

The helper reads only explicit source roots passed by the caller and writes
only `local_run_registry.json` under an existing caller-provided registry
output root.

## Non-Goals

WP-12m does not create schemas, registry validators, query-layer exposure, CLI
behavior, configs, dependencies, data files, committed output, evidence
artifacts, dashboards, agents, schedulers, daemons, queues, watchers, triggers,
parameter sweeps, Monte Carlo behavior, evidence bridges, runtime behavior,
paper/live behavior, OMS behavior, risk behavior, safe-mode behavior,
exchange/broker/order behavior, protected-path behavior, policy, scoring,
ranking/recommendation, approval, promotion, demotion, readiness, lifecycle,
or downstream authority.

## Dependency Foundation

WP-12d writes local dry-run files under caller-provided output directories:
`run_request.json`, `manifest.json`, `output_bundle.json`, and
`validation_report.json`.

WP-12f writes local batch manifest material under an existing caller-provided
output root when validation passes.

WP-12h writes `local_batch_run_summary.json` under caller-provided batch
output roots after local batch execution.

WP-12j validates local batch-run summary material without creating schemas,
query surfaces, or authority.

WP-12k integrates local summary validation so successful local batch runs write
`local_batch_run_summary.json` and
`local_batch_run_summary_validation.json`.

WP-12l defines the future registry as local-only, research-only,
non-authoritative, not repo truth, not committed evidence, not a central query
layer, not a dashboard backend yet, not an agent control surface, and not
runtime, paper/live, OMS, risk, or safe-mode authority.

## Implementation Surface

The implementation is standard-library-only except for importing the existing
WP-12j `validate_local_batch_run_summary_file(...)` helper.

It does not import or call `run_local_dry_run(...)`, `run_local_batch(...)`,
`build_batch_manifest(...)`, runtime code, paper/live code, OMS code, risk
code, safe-mode code, exchange/broker/order code, scheduler code, dashboard
code, agent code, query-layer code, schema code, or registry-validator code.

## Public Helper

The public helper is:

```python
build_local_run_registry(source_roots, registry_output_root)
```

`source_roots` are explicit caller-provided local output roots.
`registry_output_root` must already exist and be a directory. The helper does
not create parent directories.

## Registry Record Fields

Records include source kind, package and implementation identifiers, output
root, local relative source paths, run or batch identifiers when present,
candidate and evaluation-purpose fields when present, validation state, local
failure reasons, boundary markers, source file hashes, and notes.

These dataclass fields are implementation structures only. They are not a
schema, registry-validator contract, query-layer contract, or artifact grammar.

## Registry Output File

The helper writes exactly `local_run_registry.json` under
`registry_output_root` only when all source roots pass validation.

The output includes implementation and package identifiers, record count,
records, failure reasons, local-only markers, no-committed-evidence markers,
protected-boundary state, and checked boundaries.

## Source Detection

A source root is detected as `local_dry_run` when it contains
`validation_report.json`.

A source root is detected as `local_batch_run` when it contains both
`local_batch_run_summary.json` and
`local_batch_run_summary_validation.json`.

A root with both signatures is ambiguous and fails without writing the
registry. A root with neither signature fails without writing the registry.

## Dry-Run Indexing Behavior

For dry-run roots, the helper reads `validation_report.json` and, when present,
`run_request.json`, `manifest.json`, and `output_bundle.json`.

It extracts run, candidate, evaluation-purpose, validation, local failure, path
reference, boundary marker, and source-hash information where present.

Failed dry-run validation may be indexed only as a failed local record when
boundary markers remain preserved. Such records are not evidence and do not
mark protected-boundary success.

## Batch-Run Indexing Behavior

For batch-run roots, the helper reads `local_batch_run_summary.json` and
`local_batch_run_summary_validation.json` and, when present,
`batch_manifest.json` and `batch_validation_report.json`.

It requires the local summary validation report to pass and also validates the
summary through the WP-12j helper. Failed or blocked item accounting is
preserved as local descriptive information only.

## Validation Behavior

Validation fails without writing when:

- the registry output root is missing or not a directory;
- any source root is missing or not a directory;
- a source root is ambiguous or unrecognized;
- a required source file contains invalid JSON;
- required marker fields drift;
- parsed path references are absolute or traversal references;
- batch summary validation fails.

## Failure Behavior

On validation failure, the helper returns a failed in-memory result, writes no
registry file, creates no directories, and does not mutate source outputs.

Failure reasons are local diagnostic strings only.

## Path And Hash Handling

The helper records source file references as paths relative to each source
root. Parsed local path references are rejected if they are empty, absolute,
Windows-drive references, contain backslashes, or traverse with `..`.

Source file hashes are SHA-256 digests for files actually indexed.

## Determinism

The registry avoids wall-clock timestamps, random UUIDs, and filesystem-wide
search. Record identifiers are deterministic SHA-256-derived values from
source kind, relevant identifiers, relative paths, source file hashes,
implementation id, and package label.

## Local-Only / Non-Authoritative Boundary

All records and result structures preserve:

- `local_only=True`;
- `research_only=True`;
- `non_authoritative=True`;
- `creates_committed_evidence=False`.

The registry file is local output material only. It is not committed evidence
and not repo truth.

## No Schema / Registry-Validator / Query-Layer Boundary

WP-12m creates no schema, registry validator, central query-layer surface, or
query-layer contract. The JSON output is helper output only.

## No Dashboard / Agent / Scheduler Boundary

WP-12m creates no dashboard, dashboard backend, agent surface, scheduler,
daemon, queue, watcher, trigger, polling loop, job service, or agent control
surface.

## No Parameter Sweep / Monte Carlo Boundary

WP-12m creates no parameter sweep, parameter search, Monte Carlo, robustness
engine, simulation behavior, or downstream interpretation surface.

## No Evidence Bridge Boundary

WP-12m creates no bridge from local output material to EXP, REP, OL, REC, LCH,
registry, advisory, shadow, summary, or evidence artifacts.

## Protected Runtime / Paper / Live Boundary

WP-12m does not contact or authorize runtime, paper/live, OMS, risk, safe-mode,
exchange, broker, order, execution, deployment, live-trading, or protected-path
behavior.

## Test Coverage Summary

Tests cover valid dry-run indexing, valid batch-run indexing, mixed-root
indexing, exact registry write location, local boundary markers, source file
hashes, deterministic output, invalid registry roots, missing source roots,
unrecognized roots, ambiguous roots, invalid JSON, batch validation drift,
failed dry-run indexing, and contained `tmp_path` writes.

## Stop / Escalation Rules

Future work must stop and escalate if it would create schemas, registry
validators, query-layer exposure, CLI behavior, configs, dependencies, data,
committed output, evidence artifacts, dashboards, agents, schedulers, daemons,
queues, watchers, triggers, parameter sweeps, Monte Carlo behavior, evidence
bridges, runtime behavior, paper/live behavior, OMS behavior, risk behavior,
safe-mode behavior, exchange/broker/order behavior, protected-path behavior,
policy, scoring, ranking/recommendation, approval, promotion, demotion,
readiness, lifecycle, or downstream authority.

## Non-Claims

WP-12m creates no formal schema, registry validator, query-layer contract,
dashboard authority, agent authority, scheduler authority, parameter-sweep
authority, Monte Carlo authority, evidence authority, runtime authority,
paper/live authority, OMS authority, risk authority, safe-mode authority,
exchange/broker/order authority, protected-path authority, policy authority,
scoring authority, ranking/recommendation authority, approval authority,
promotion authority, demotion authority, readiness authority, lifecycle
authority, or downstream authority.
