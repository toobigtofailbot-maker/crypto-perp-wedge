# Batch Run Summary Format Design (WP-12i / AUTO-08)

## Package Metadata

- Package label: WP-12i / AUTO-08.
- Package title: Batch Run Summary Format Design.
- Package class: Tier 1 documentation-only design package.
- Effective base: refreshed `main` after merged WP-12h / AUTO-07.
- Created artifact: this design document only.
- Modified status surface: `docs/project_status.md` only.

AUTO-08 is design-only. It creates no implementation, schema, validator,
query-layer change, tests, CLI, runner change, batch manifest code change,
local dry-run runner code change, config, dependency, data, committed output,
evidence artifact, result store, dashboard, agent, scheduler, daemon, queue,
watcher, trigger, parameter sweep, Monte Carlo, evidence bridge, runtime
behavior, paper/live bridge, or protected-path change.

## Purpose

AUTO-08 defines the future local batch-run summary format boundary after
WP-12h. The purpose is to make the current `local_batch_run_summary.json`
surface easier for later packages to reason about without turning it into an
authoritative schema, validator contract, evidence artifact, lifecycle surface,
or downstream consumption interface.

This document describes future design intent only. Any package that wants to
change implementation, add validation, expose query-layer reads, create
committed evidence, or consume summaries through result-store, dashboard, or
agent surfaces requires separate authorization.

## Scope

This design may describe future expectations for:

- the local batch-run summary identity boundary;
- observed WP-12h batch-level and item-level fields;
- manifest and dry-run reference boundaries;
- failure accounting categories;
- blocked, failed, skipped, and succeeded item semantics;
- output location, reproducibility, and determinism categories;
- local-only and non-authoritative downstream handoff rules;
- stop rules for authority leakage and protected-boundary drift;
- a minimal later validation slice outline.

All descriptions are documentation-only. This package does not define a formal
repo-truth schema.

## Non-Goals

AUTO-08 does not:

- modify `tools/research_automation/local_batch_runner.py`;
- modify `tools/research_automation/batch_manifest.py`;
- modify `tools/research_automation/local_dry_run_runner.py`;
- create implementation, schema, validator, query-layer change, tests, or CLI;
- create committed output or evidence artifacts;
- create result-store, dashboard, agent, scheduler, daemon, queue, watcher,
  trigger, parameter-sweep, Monte Carlo, evidence-bridge, runtime, paper/live,
  OMS, risk, safe-mode, exchange, broker, order, or protected-path behavior;
- create policy, scoring, ranking, recommendation, candidate approval,
  strategy approval, promotion, demotion, readiness, lifecycle transition,
  paper/live readiness, runtime authority, or downstream authority.

## Dependency Foundation

WP-12a installed the tiered automation-build operating model and blocked
paper/live, runtime, OMS, risk, safe-mode, execution, deployment, protected
paths, policy, scoring, ranking, and recommendation work unless a later package
explicitly authorizes them.

WP-12b mapped research automation boundaries, including future batch execution,
result stores, dashboards, agent orchestration, validation, and protected
runtime separation.

WP-12c defined future runner interface boundaries for research intent, run
requests, manifests, local dry-run output, diagnostics, validation,
reproducibility, and downstream handoffs.

WP-12d implemented `run_local_dry_run(intent, output_dir)` as a local
research-only dry-run runner that writes non-authoritative run material only
under a caller-provided output directory.

WP-12e defined the future batch manifest format boundary as documentation only.

WP-12f implemented `build_batch_manifest(...)` as a local batch manifest helper
that validates explicit caller-provided batch items and writes only
`batch_manifest.json` and `batch_validation_report.json` under an existing
caller-provided output root when validation passes.

WP-12g defined the future batch runner design boundary as documentation only.

WP-12h implemented `run_local_batch(items, output_root, resource_limits,
static_metadata=None)` as one narrow local in-process batch runner vertical
slice. It uses WP-12f manifest validation, calls WP-12d local dry-run
functionality through explicit local function calls, and writes local
non-authoritative batch-run material only under caller-provided output roots.

## Current WP-12h Summary Surface

Current repo truth shows WP-12h writes `local_batch_run_summary.json` only after
manifest validation passes. If manifest validation fails, the runner does not
call `run_local_dry_run(...)`, does not create per-item directories, and does
not write a batch summary.

The observed WP-12h implementation structures are local dataclasses, not
repo-truth schemas:

- `LocalBatchItemResult`;
- `LocalBatchRunSummary`;
- `LocalBatchRunResult`.

The observed summary categories are batch identity, implementation identity,
package label, item count, success item count, failed item count, skipped item
count, blocked item count, failure reasons, item results, manifest file
references, summary file reference, checked boundaries, local-only marker,
research-only marker, non-authoritative marker, committed-evidence marker, and
protected-boundary marker.

## Summary Identity Boundary

Summary presence is not authority.

Summary presence is not execution authority, evidence authority, lifecycle
authority, candidate approval, strategy approval, paper/live readiness, or a
recommendation. Summary presence does not authorize result-store, dashboard, or
agent consumption. Summary presence does not authorize query-layer exposure,
committed artifact creation, runtime, paper/live, OMS, risk, safe-mode,
exchange, broker, order, scheduler, daemon, queue, watcher, trigger,
deployment, or protected-path behavior.

The future summary identity boundary may preserve a batch identifier,
implementation identifier, package label, and summary file name only as local
descriptive references.

## Batch-Level Fields Boundary

The observed WP-12h `LocalBatchRunSummary` fields are:

- `batch_id`;
- `implementation_id`;
- `package_label`;
- `item_count`;
- `success_item_count`;
- `failed_item_count`;
- `skipped_item_count`;
- `blocked_item_count`;
- `failure_reasons`;
- `item_results`;
- `manifest_files`;
- `summary_file`;
- `checked_boundaries`;
- `local_only`;
- `research_only`;
- `non_authoritative`;
- `creates_committed_evidence`;
- `protected_boundary_preserved`.

These names describe the current WP-12h implementation surface. They are not a
formal schema, stable public API, validator contract, query-layer contract, or
evidence artifact grammar.

## Item-Level Fields Boundary

The observed WP-12h `LocalBatchItemResult` fields are:

- `item_id`;
- `source_id`;
- `status`;
- `output_path`;
- `dry_run_run_id`;
- `dry_run_written_files`;
- `failure_reasons`;
- `local_only`;
- `research_only`;
- `non_authoritative`;
- `creates_committed_evidence`;
- `protected_boundary_preserved`.

These names describe item-level local result material only. They must not be
used as candidate status, strategy status, lifecycle state, promotion state,
paper/live readiness, or evidence authority without a later approved package.

## Manifest Reference Boundary

The summary may reference WP-12f manifest output files through observed
`manifest_files` values such as `batch_manifest.json` and
`batch_validation_report.json`.

Manifest references are provenance aids only. They do not make a manifest
authoritative, do not prove execution readiness, and do not authorize reruns,
watchers, schedulers, query exposure, evidence conversion, or downstream
consumption.

## Dry-Run Reference Boundary

Item results may reference dry-run output through `dry_run_run_id` and
`dry_run_written_files`.

Dry-run references are local descriptive links to WP-12d output material. They
are not EXP, REP, OL, REC, LCH, registry, advisory, shadow, summary, or
evidence artifacts. They do not authorize paper/live readiness, runtime use,
candidate approval, strategy approval, or lifecycle transition.

## Failure Accounting Boundary

Future summary-format work should keep failure accounting explicit and local.
Current WP-12h categories include:

- invalid output root: no manifest result, no writes, summary returned in
  memory with failure reason `output_root must be an existing directory`;
- invalid manifest input: manifest validation failure, no dry-run calls, no
  summary file write;
- output-path containment failure: manifest validation failure with no writes;
- resource-limit failure: manifest validation failure with no dry-run calls;
- blocked item output directory: item status `blocked`, summary file written,
  and failure reason `item output directory parent must already exist`;
- dry-run validation failure: item status `failed` with dry-run failure reasons;
- successful item: item status `succeeded`.

These are observed implementation categories, not a complete future taxonomy.

## Blocked / Failed / Skipped Semantics

Current WP-12h observes:

- `succeeded` for item dry-runs whose validation report passes;
- `failed` for item dry-runs whose validation report does not pass;
- `blocked` for item output directories whose immediate parent is missing;
- `skipped_item_count` is present and currently set to `0` in the summary.

Future packages may define additional skipped semantics only with separate
authorization. They must not treat skipped, failed, or blocked items as
successful evidence.

## Output Location Boundary

`local_batch_run_summary.json` is written only under the caller-provided output
root after manifest validation passes. WP-12h requires the output root to
already exist and be a directory.

The summary path is local output material. It must not be committed as an
evidence artifact by AUTO-08, and its presence must not authorize committed
artifact creation by later packages without separate approval.

## Reproducibility Boundary

Future summary-format work may preserve reproducibility categories such as:

- batch identifier;
- implementation identifier;
- package label;
- source manifest file references;
- item identity set;
- dry-run run identifiers;
- dry-run written file references;
- output root relative paths;
- checked boundary markers;
- failure accounting state.

These categories support local reasoning only. AUTO-08 does not define hashes,
retention policy, schema rules, validator behavior, or evidence conversion.

## Determinism Boundary

WP-12h derives deterministic local material from explicit caller-provided batch
items, resource limits, static metadata, and WP-12d/WP-12f local helpers.

Future summary-format work should preserve deterministic representation where
possible, but deterministic local output is still non-authoritative. Determinism
does not convert the summary into evidence, policy, scoring, ranking,
recommendation, approval, promotion, demotion, readiness, lifecycle, paper/live,
runtime, or protected-path authority.

## Local-Only / Non-Authoritative Boundary

The summary and item results must continue to mark local-only, research-only,
non-authoritative, no committed evidence, and protected-boundary preservation
state explicitly.

Summary presence is not evidence authority. Summary presence does not authorize
result-store, dashboard, agent, query-layer, committed artifact, evidence
bridge, runtime, paper/live, OMS, risk, safe-mode, exchange, broker, order,
scheduler, daemon, queue, watcher, trigger, deployment, or protected-path
behavior.

## No Committed Evidence Boundary

AUTO-08 creates no committed output or evidence artifact.

`local_batch_run_summary.json` is local batch-run material only. It is not an
EXP, REP, OL, REC, LCH, registry, advisory, shadow, summary, or evidence
artifact. Any future bridge from local summary material to committed evidence
requires a separate package with exact changed files, validation, integrity
checks, semantic authority review, and preserved source references.

## Result-Store / Dashboard / Agent Boundary

AUTO-08 creates no result store, dashboard, or agent.

No result store, dashboard, or agent may infer policy, scoring, ranking,
recommendation, approval, promotion, demotion, readiness, lifecycle,
paper/live, runtime, OMS, risk, safe-mode, execution, exchange, broker, order,
or protected-path authority from batch-run summaries.

Future result-store, dashboard, or agent consumption requires separate
authorization that defines exact read surfaces, validation, non-authoritative
status, and stop rules.

## Protected Runtime / Paper / Live Boundary

AUTO-08 does not authorize Tier 4 or protected runtime contact.

Summary presence does not authorize runtime, paper/live, OMS, risk, safe-mode,
exchange, broker, order, scheduler, daemon, queue, watcher, trigger,
deployment, live-trading, or protected-path behavior. Any future package that
requires these surfaces must stop unless explicit authorization exists.

## Candidate / Strategy Authority Boundary

Summary presence is not candidate approval, strategy approval, paper/live
readiness, or a recommendation.

The summary must not be used to score policy, rank candidates, recommend
action, approve strategy work, promote or demote candidates, infer readiness,
create lifecycle transition authority, or automate approval. Any such use
requires separate explicit authorization.

## Minimal Future Validation Slice Outline

A later package may define a minimal summary validation slice only after
separate authorization. That slice should remain local and non-authoritative
and may check:

- required observed batch-level fields are present;
- required observed item-level fields are present;
- count fields match item statuses;
- manifest references are local relative references;
- dry-run references remain local relative references;
- local-only, research-only, non-authoritative, no-committed-evidence, and
  protected-boundary markers are present;
- no result-store, dashboard, agent, query-layer, evidence, runtime,
  paper/live, OMS, risk, safe-mode, scheduler, daemon, queue, watcher, trigger,
  exchange, broker, order, deployment, or protected-path authority is implied.

That later slice must not create schema, validator, query-layer, test, runner,
or artifact changes unless the package explicitly authorizes them.

## Open Questions For Later Packages

Later packages must decide:

- whether a formal schema is needed;
- whether a validator is needed;
- whether skipped item semantics should be implemented;
- whether summary retention rules are needed;
- whether local batch summaries should ever feed a result-store read model;
- whether dashboards or agents may read validated summaries;
- whether an evidence bridge is justified;
- what exact validation command and test scope should cover summary material.

These are open questions only. AUTO-08 does not answer them.

## Stop / Escalation Rules

Future work must stop and escalate if it would:

- treat summary presence as execution, evidence, lifecycle, candidate,
  strategy, paper/live, recommendation, or downstream authority;
- create or modify implementation, schema, validator, query-layer, test,
  runner, CLI, config, dependency, data, committed output, or evidence
  artifacts outside explicit package scope;
- create result-store, dashboard, agent, scheduler, daemon, queue, watcher,
  trigger, parameter-sweep, Monte Carlo, evidence-bridge, runtime, paper/live,
  OMS, risk, safe-mode, exchange, broker, order, deployment, or protected-path
  behavior;
- create or mutate EXP, REP, OL, REC, LCH, registry, advisory, shadow, summary,
  or evidence artifact families;
- create policy, scoring, ranking, recommendation, approval, promotion,
  demotion, readiness, or lifecycle authority;
- require protected runtime, OMS, reconciliation, risk, overlay, safe-mode,
  live-trading, schema, validator, query-layer, config, dependency, data,
  scheduler, daemon, queue, watcher, trigger, evidence artifact, or committed
  output behavior without separate authorization;
- produce validation failures, integrity-view rows, semantic authority leakage,
  or changed-file scope drift.

## Non-Claims

WP-12i creates no:

- implementation;
- schema;
- validator;
- query-layer change;
- tests;
- CLI;
- runner change;
- batch manifest code change;
- local dry-run runner code change;
- config, dependency, or data change;
- committed output;
- evidence artifact;
- result store or run registry;
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
- EXP, REP, OL, REC, LCH, registry, advisory, shadow, summary, or evidence
  artifact mutation;
- candidate approval;
- strategy approval;
- policy, scoring, ranking, recommendation, approval, promotion, demotion,
  readiness, lifecycle, paper/live, runtime, or downstream authority.
