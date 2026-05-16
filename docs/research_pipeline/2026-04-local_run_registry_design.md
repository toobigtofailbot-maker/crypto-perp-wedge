# Local Run Registry Design (WP-12l / AUTO-11)

## Package Metadata

- Package label: WP-12l / AUTO-11.
- Package title: Local Run Registry Design.
- Package class: Tier 1 documentation-only design package.
- Effective base: refreshed `main` after merged WP-12k / AUTO-10.
- Created artifact: this design document only.
- Modified status surface: `docs/project_status.md` only.

WP-12l creates no implementation, registry file, schema, validator,
query-layer exposure, tests, CLI, config, dependency, data, committed output,
evidence artifact, result store implementation, dashboard, agent, scheduler,
daemon, queue, watcher, trigger, parameter sweep, Monte Carlo, evidence bridge,
runtime, paper/live, OMS, risk, safe-mode, exchange/broker/order,
protected-path behavior, or downstream authority.

## Purpose

WP-12l defines the intended future local run registry / result index boundary.
It is a Tier 1 documentation-only design package.

The future registry concept exists to help later packages index local dry-run
and local batch-run output material without turning those outputs into repo
truth, committed evidence, schema truth, query-layer truth, dashboard
authority, agent authority, strategy approval, runtime authority, paper/live
authority, or downstream authority.

WP-12l does not implement the registry and does not create or commit local run
outputs.

## Scope

This design may describe a future registry that indexes local output material
from:

- WP-12d local dry-run runner outputs;
- WP-12f batch manifest outputs;
- WP-12h / WP-12k local batch-run outputs;
- `local_batch_run_summary.json`;
- `local_batch_run_summary_validation.json`.

All scope is design-only. No storage, reader, writer, validator, query view, or
run output is created here.

## Non-Goals

WP-12l does not:

- implement code;
- create a registry file;
- create a schema;
- add tests;
- add validators;
- expose query-layer reads;
- add a CLI;
- create a result store implementation;
- create a dashboard or agent surface;
- create parameter sweep or Monte Carlo behavior;
- create committed evidence;
- create EXP, REP, OL, REC, LCH, registry, advisory, shadow, summary, or
  evidence artifacts;
- modify runtime, paper/live, OMS, risk, safe-mode, exchange/broker/order,
  configs, dependencies, data, or protected paths;
- authorize policy, scoring, ranking, recommendation, approval, promotion,
  demotion, readiness, lifecycle, or downstream authority.

## Dependency Foundation

WP-12d created local dry-run output material under caller-provided output
directories. The dry-run runner writes `run_request.json`, `manifest.json`,
`output_bundle.json`, and `validation_report.json` as local-only,
research-only, non-authoritative material.

WP-12f created local batch manifest material. The manifest helper writes
`batch_manifest.json` and `batch_validation_report.json` only under an existing
caller-provided output root when validation passes.

WP-12h created local batch-run summary material. The local batch runner writes
`local_batch_run_summary.json` under the caller-provided batch output root
after manifest validation passes and local batch execution completes.

WP-12j created the local batch-run summary validation helper. The helper
validates observed WP-12h summary shape and boundary markers only.

WP-12k integrated summary validation into successful local batch runs. A
successful local batch run now writes `local_batch_run_summary.json` and
`local_batch_run_summary_validation.json` together after summary validation
passes.

Those outputs are local-only, research-only, non-authoritative, and not
committed evidence.

## Why A Local Run Registry Is Next

After WP-12k, successful local batch runs have both a summary and a local
summary validation report. The next design risk is how later packages will find
and reference those local run outputs.

A local run registry design should come before implementing result storage,
dashboards, agents, parameter sweeps, Monte Carlo work, or evidence bridges.
Without this boundary, later packages may accidentally turn local output
material into authority.

WP-12l addresses only the boundary. It does not choose a storage format or
implement a registry.

## Local Run Registry Concept

The future local run registry is a local-only index over caller-provided output
roots.

The future registry may help locate local dry-run outputs, local batch-run
outputs, manifest files, summary files, and validation states. It may later be
append-only if a separate implementation package authorizes that behavior.

The registry is:

- non-authoritative;
- research-only;
- local-only;
- not repo truth;
- not committed evidence;
- not a central query layer;
- not a dashboard backend yet;
- not an agent control surface;
- not a strategy approval surface;
- not runtime, paper/live, OMS, risk, or safe-mode authority.

## Inputs The Future Registry May Index

A later implementation may index caller-provided paths to local output material
such as:

- dry-run `run_request.json`;
- dry-run `output_bundle.json`;
- dry-run `validation_report.json`;
- `batch_manifest.json`;
- `batch_validation_report.json`;
- `local_batch_run_summary.json`;
- `local_batch_run_summary_validation.json`.

These are possible future inputs only. WP-12l does not read or write them.

## Candidate Future Record Fields

A future record may include descriptive fields such as:

- `registry_record_id`;
- `source_kind`, such as `local_dry_run` or `local_batch_run`;
- `package_label`;
- `implementation_id`;
- `output_root`;
- `relative_paths`;
- `run_id` or `batch_id`;
- `candidate_id`, if present;
- evaluation purpose, if present;
- `created_at` or `recorded_at`;
- validation status;
- failure reasons;
- `local_only`;
- `research_only`;
- `non_authoritative`;
- `creates_committed_evidence`;
- `protected_boundary_preserved`;
- source file hashes, if later authorized;
- repo version ref, if available;
- notes.

This list is design intent only. It is not a schema, stable API, validator
contract, query-layer contract, or artifact grammar.

## Storage Boundary

The future registry should prefer caller-provided local output roots and
explicit caller-provided storage choices.

WP-12l creates no committed registry file, no repository-level persistent
result database, no default central store, and no `.gitignore` or config
change.

A later implementation package must choose storage format, storage location,
retention expectations, and write behavior explicitly.

## Append / Update Boundary

Future registry records should avoid mutating source output files. The
registry should not rewrite local dry-run output, batch manifests, batch
summaries, or summary validation reports.

Future registry work should not rewrite prior committed repo artifacts.

A later implementation must define append and update rules separately.
Validation failures must not be hidden by overwriting prior local records.

## Validation Boundary

A future implementation should validate that:

- source files exist;
- source file references are local relative paths where applicable;
- local-only, research-only, non-authoritative, no-committed-evidence, and
  protected-boundary markers are preserved;
- summary validation reports pass before indexing successful batch summaries;
- invalid or failed runs can be indexed only as failed local records, not
  evidence;
- protected boundary drift blocks downstream use.

Validation remains a local integrity check. It does not create evidence
authority, dashboard authority, agent authority, strategy approval, paper/live
authority, runtime authority, or downstream authority.

## Relationship To Dry-Run Outputs

The future registry may index WP-12d dry-run metadata, run requests, output
bundles, and validation reports.

Indexing dry-run metadata does not make dry-run output an EXP, REP, OL, REC,
LCH, registry, advisory, shadow, summary, or evidence artifact. It does not
authorize query-layer exposure, dashboards, agents, evidence bridges, runtime,
paper/live, OMS, risk, safe-mode, exchange, broker, order, or protected-path
behavior.

## Relationship To Batch-Run Outputs

The future registry may index WP-12f batch manifest paths and WP-12h / WP-12k
batch summary paths.

Indexing batch-run material does not make it evidence. The registry would
record local descriptive references only, and those references remain
research-only and non-authoritative.

## Relationship To Batch Summary Validation Reports

`local_batch_run_summary_validation.json` is local integrity evidence only. It
records that a local summary matched the observed shape and boundary markers.

Passing validation may allow local indexing only if a later implementation
package authorizes registry behavior.

Passing validation does not authorize dashboards, agents, evidence bridges,
runtime, paper/live, OMS, risk, safe-mode, exchange/broker/order behavior, or
downstream authority.

## Relationship To Future Parameter Sweeps

Future parameter sweeps should not be implemented until registry and storage
semantics are clear.

Parameter sweeps must not claim optimality, approval, promotion, scoring,
ranking, recommendation, readiness, paper/live authority, runtime authority, or
downstream authority.

WP-12l does not create parameter sweep behavior.

## Relationship To Future Monte Carlo / Robustness Work

Future Monte Carlo / robustness outputs should use a separate later design.

A future registry may index robustness run material only if separately
authorized. WP-12l does not define robustness record shape, robustness
validation, simulation behavior, or downstream interpretation.

## Relationship To Future Dashboards

Dashboards are later read-only surfaces over approved registry or result
surfaces.

WP-12l does not create dashboard data, dashboard UI, dashboard backend,
dashboard query surfaces, or dashboard authority.

Dashboards must not infer policy, scoring, ranking, recommendation, approval,
promotion, demotion, readiness, lifecycle, runtime, paper/live, OMS, risk,
safe-mode, exchange, broker, order, or protected-path authority from local
registry records.

## Relationship To Future Agents

Agents are later summarization or orchestration helpers only after validated
surfaces exist.

WP-12l does not authorize agent job control, agent write control, autonomous
execution, policy, scoring, ranking, recommendation, approval, promotion,
demotion, readiness, lifecycle, runtime, paper/live, OMS, risk, safe-mode,
exchange, broker, order, or protected-path authority.

## Relationship To Evidence Artifacts

Registry records are not EXP, REP, OL, REC, LCH, registry, advisory, shadow,
summary, or evidence artifacts.

Any future bridge from local registry records to evidence artifacts requires a
separate explicitly authorized package with exact changed-file scope,
validation, integrity-view checks, semantic authority review, and preserved
source references.

## Protected Runtime / Paper / Live Boundary

WP-12l authorizes no exchange, broker, or order contact.

WP-12l authorizes no paper/live behavior, runtime behavior, OMS behavior, risk
behavior, safe-mode behavior, deployment behavior, or protected-path behavior.

No future package may treat this design as permission to cross protected
runtime, paper/live, OMS, risk, safe-mode, exchange, broker, order, execution,
deployment, config, dependency, data, schema, validator, query-layer, or
protected-path boundaries.

## Open Questions For Later Packages

Later packages must decide:

- exact storage format;
- storage location;
- whether a schema is needed;
- whether the helper should be library-only or a CLI later;
- how to handle record IDs;
- how to handle source file hashes;
- whether the registry should index failed runs;
- whether the registry should support multiple output roots;
- how dashboards should consume it later;
- how agents may read it later;
- when parameter sweeps may use it.

These are open questions only.

## Likely Next Package After WP-12l

As a non-binding future option, WP-12m may be a Tier 3 local run registry
vertical slice if WP-12l merges cleanly.

WP-12m would need separate authorization and must remain local-only,
standard-library-only, non-authoritative, and no-committed-evidence.

WP-12l does not draft or implement WP-12m.

## Stop / Escalation Rules

Future work must stop and escalate if it would:

- implement code in WP-12l;
- create storage, schemas, validators, query views, tests, configs,
  dependencies, data, committed outputs, or artifacts;
- treat local registry records as evidence;
- authorize dashboards, agents, parameter sweeps, Monte Carlo, evidence
  bridges, runtime, paper/live, OMS, risk, safe-mode, exchange/broker/order,
  protected paths, policy, scoring, ranking, recommendation, approval,
  promotion, demotion, readiness, lifecycle, or downstream authority.

## Non-Claims

WP-12l creates no:

- implementation;
- registry file;
- schema;
- tests;
- validators;
- query-layer exposure;
- CLI;
- result store implementation;
- dashboard;
- agent;
- scheduler, daemon, queue, watcher, or trigger;
- parameter sweep;
- Monte Carlo or robustness engine;
- evidence bridge;
- runtime behavior;
- paper/live bridge;
- OMS, risk, safe-mode, exchange, broker, order, execution, deployment, or
  protected-path behavior;
- config, dependency, or data change;
- committed output;
- EXP, REP, OL, REC, LCH, registry, advisory, shadow, summary, or evidence
  artifact mutation;
- policy, scoring, ranking, recommendation, approval, promotion, demotion,
  readiness, lifecycle, paper/live, runtime, or downstream authority.
