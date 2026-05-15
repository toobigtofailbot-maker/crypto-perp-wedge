# Batch Manifest Format Design (WP-12e / AUTO-04)

## Package Metadata

- Package label: WP-12e / AUTO-04.
- Package title: Batch Manifest Format Design.
- Package class: Tier 1 documentation-only design package.
- Effective base: refreshed `main` after merged WP-12d / AUTO-03.
- Created artifact: this design document only.
- Modified status surface: `docs/project_status.md` only.

AUTO-04 is design-only. It creates no batch runner, scheduler, queue, daemon,
watcher, trigger, CLI, schema, validator, query-layer change, test, config,
dependency, data, result store, dashboard, agent, parameter sweep, Monte
Carlo, evidence bridge, committed output, runtime behavior, paper/live bridge,
or protected-path change.

## Purpose

AUTO-04 defines the future boundary for grouping multiple local research
dry-run requests under a batch manifest.

The purpose is to reduce implementation drift before any later Tier 3 batch
runner work. This document defines what a future batch manifest should
preserve, how it should relate to WP-12d local dry-run material, and what
validation and failure accounting later packages must provide before any
downstream use.

This document is not a manifest format, not a repo-truth schema, and not an
implementation authorization.

## Scope

This design may describe future intended boundaries for:

- local research-only batch identity;
- batch items that reference one future run request or intent-derived local
  run unit;
- resource-limit categories;
- output-location constraints;
- validation evidence;
- failure accounting;
- reproducibility metadata;
- non-authoritative downstream handoffs;
- a minimal later implementation slice outline.

All sample field categories are illustrative design intent only. They are not
final field names, final types, required keys, default rules, serialization
rules, repo-truth schemas, validators, or wire formats.

## Non-Goals

AUTO-04 does not:

- implement batch execution;
- modify or wrap the WP-12d local dry-run runner;
- implement scheduler, queue, daemon, watcher, trigger, polling loop, or CLI
  behavior;
- define final field names, final types, or final storage paths;
- create schema, validator, query-layer, config, dependency, data, result-store,
  dashboard, agent, parameter-sweep, Monte Carlo, or evidence-bridge behavior;
- create committed output or evidence artifacts;
- create, mutate, replace, promote, or demote EXP, REP, OL, REC, LCH,
  registry, advisory, shadow, summary, or evidence artifacts;
- touch runtime, paper/live, OMS, risk, safe-mode, exchange, broker, order,
  execution, deployment, or protected paths;
- create policy, scoring, ranking, recommendation, approval, promotion,
  demotion, readiness, lifecycle, paper/live, or runtime authority.

## Dependency Foundation

WP-12a installed the tiered automation-build operating model. It keeps
paper/live, runtime, OMS, risk, safe-mode, execution, deployment, protected
paths, policy, scoring, ranking, and recommendation boundaries blocked unless a
later package explicitly authorizes them.

WP-12b mapped the research automation architecture. It identified batch
manifests as a future local research automation boundary, not as a scheduler,
daemon, queue, result store, dashboard, agent, or evidence bridge.

WP-12c defined the future experiment-runner interface boundary for research
intent, run request, manifest, local dry-run output, diagnostics, validation,
reproducibility, and downstream handoffs.

WP-12d implemented one narrow local dry-run runner vertical slice. It exposes
`run_local_dry_run(intent, output_dir)` as a local in-process API that accepts
explicit caller-provided intent, writes only under a caller-provided output
directory, and emits non-authoritative run request, manifest, output bundle,
and validation report material.

AUTO-04 depends on WP-12a through WP-12d as boundary sources only. It does not
extend implementation authority.

## Batch Manifest Role In The AUTO Architecture

A future batch manifest should be a planning and preservation surface for a set
of local research-only run units.

Its role is to describe which local run requests belong together, what
resource and output constraints apply, what validation evidence is required,
and how failures are accounted for before anything downstream may consume the
batch material.

A batch manifest is not the batch runner. It is not a scheduler, queue, daemon,
watcher, trigger, result store, dashboard, agent, evidence artifact, strategy
approval surface, or runtime control surface.

## Batch Manifest Principles

Future batch manifests should preserve:

- explicit identity for the batch;
- explicit identity for each item;
- local research-only boundaries;
- bounded resource expectations;
- deterministic output-location intent;
- validation evidence before downstream use;
- failure states that block downstream use when necessary;
- reproducibility metadata sufficient to rerun, compare, or reject a batch;
- non-authoritative status until a later package defines concrete
  implementation and validation.

They should avoid:

- implicit expansion of scope;
- hidden parameter mutation;
- hidden data selection;
- automatic evidence artifact creation;
- automatic result-store, dashboard, or agent publication;
- any policy, scoring, ranking, recommendation, approval, promotion, demotion,
  readiness, lifecycle, paper/live, or runtime authority.

## Relationship To WP-12d Local Dry-Run Runner

WP-12d created the first local dry-run runner slice. A future authorized batch
runner may call the WP-12d local runner or a later compatible runner interface
once a separate implementation package defines that behavior.

AUTO-04 does not modify `tools/research_automation/local_dry_run_runner.py`.
AUTO-04 does not wrap `run_local_dry_run(...)`, add tests, create a CLI, write
batch outputs, or implement batch execution.

The future relationship is one-way and bounded: a batch runner may consume
validated batch items and invoke local research-only run units, but batch
manifest presence alone must not execute a run.

## Batch Identity Boundary

A future batch manifest should carry a stable batch identity that is
deterministic from explicit manifest content and relevant static metadata.

At architecture level, identity should preserve categories such as:

- manifest version category;
- batch purpose;
- source package or source intent reference;
- repo version reference;
- implementation version reference, once implementation exists;
- item identity set;
- static metadata that materially affects reproducibility.

AUTO-04 does not define the exact batch id algorithm, field names, digest
length, serialization, or collision handling. Later implementation must define
those details and validation evidence.

## Batch Item Boundary

Each future batch item should represent exactly one future local run request or
one intent-derived local run unit.

At architecture level, each item should preserve categories such as:

- item identity;
- source intent or run-request reference;
- candidate or strategy context;
- data reference category;
- timeframe and evaluation scope;
- parameter context;
- expected output-location intent;
- validation and failure state.

Batch items must not create strategy authority. Item sequence, grouping, or
presence must not imply scoring, ranking, recommendation, approval, promotion,
demotion, readiness, lifecycle transition, or paper/live suitability.

## Resource-Limit Boundary

A future batch manifest should describe bounded resource categories before
execution is attempted.

Future categories may include:

- maximum item count;
- maximum local jobs;
- maximum concurrency;
- timeout budget;
- per-item timeout category;
- failure threshold;
- output-size or retention boundary;
- local-only execution constraints.

These are categories only. AUTO-04 does not set final limits, defaults,
enforcement behavior, retry behavior, scheduler behavior, queue behavior, or
runtime behavior.

Any future resource-limit violation must be explicit failure accounting and
must block downstream use until a later package defines a safe resolution.

## Failure-Accounting Boundary

Future batch packages should account for failures at both manifest and item
level.

Failure categories should include:

- invalid manifest;
- invalid item;
- skipped item;
- per-item failure;
- partial batch;
- resource-limit violation;
- output-location violation;
- validation failure;
- reproducibility metadata failure;
- protected-boundary drift.

Failure accounting must be explicit, durable within the later authorized output
surface, and blocking where downstream use would otherwise infer success.

AUTO-04 does not define final status vocabulary or storage behavior.

## Output-Location Boundary

A future batch manifest should describe output-location intent without allowing
writes outside later authorized batch output roots.

Future implementation must define a batch output root and constrain every item
output path beneath it. It must not write to committed research artifact
families, source code paths, configs, dependency files, data directories,
runtime paths, paper/live paths, or protected paths unless a later package
explicitly authorizes that exact changed-file scope.

Output locations are preservation targets for local research material only.
They are not REP, OL, REC, LCH, registry, advisory, shadow, summary, or
evidence artifact locations by implication.

## Validation Model

Future batch implementation must emit validation evidence before downstream
use.

At architecture level, validation should cover:

- manifest completeness;
- item completeness;
- manifest/item reference consistency;
- resource-limit compliance;
- output-location containment;
- per-item run material completeness if execution is later authorized;
- failure-accounting completeness;
- reproducibility metadata completeness;
- non-authoritative downstream boundaries;
- no automatic evidence artifact creation;
- no protected-boundary drift.

Failed validation must stop downstream consumption. Integrity-view failures,
validator failures, or semantic authority leakage must stop the package that
produces them.

AUTO-04 does not create a validator or validation command.

## Determinism And Reproducibility Expectations

Future batch packages should preserve enough metadata to rerun, compare, or
reject a batch.

At architecture level, reproducibility categories should include:

- repo version reference;
- future batch implementation version reference;
- manifest version category;
- input references;
- item identity set;
- local runner implementation reference;
- research pipeline version or comparable provenance handle;
- static metadata that materially affects results;
- deterministic seed or randomness policy if later packages introduce
  stochastic behavior;
- validation state and failure state.

AUTO-04 does not define exact field names, field types, hashing rules, or
storage location.

## Artifact And Evidence Boundary

Batch manifests and batch outputs are not evidence artifacts.

Batch manifest entries must not automatically create, mutate, replace, promote,
or demote EXP, REP, OL, REC, LCH, registry, advisory, shadow, summary, or
evidence artifacts.

Any future conversion from validated batch output material to committed
evidence requires a separate explicitly authorized evidence bridge package with
exact changed files, validators, integrity checks, semantic boundary review,
and preserved source references.

## Result-Store / Dashboard / Agent Boundary

A future result store, dashboard, or agent may consume batch material only
after separate packages define exact read-only surfaces and validation.

Result stores must remain non-authoritative unless a later package explicitly
defines their role. Dashboards must remain read-only. Agents may summarize or
propose bounded research work only inside an approved envelope.

No result store, dashboard, or agent may infer policy, scoring, ranking,
recommendation, approval, promotion, demotion, readiness, lifecycle,
paper/live, runtime, OMS, risk, safe-mode, execution, exchange, broker, or
order authority from a batch manifest.

AUTO-04 creates no result store, dashboard, or agent.

## Protected Runtime / Paper / Live Boundary

AUTO-04 does not authorize Tier 4.

Batch execution, if later authorized, must remain local research-only and
bounded. It must not contact exchange, broker, order, runtime, OMS, risk,
safe-mode, paper/live, deployment, operational monitoring, scheduler, daemon,
queue, watcher, trigger, or protected-path surfaces unless a later package
explicitly authorizes that exact scope.

No future Tier 1, Tier 2, or Tier 3 package may treat this design as permission
to cross protected runtime, paper, live, OMS, risk, safe-mode, execution, or
deployment boundaries.

## Candidate / Strategy Authority Boundary

A future batch manifest may group local research run units. It must not create
candidate or strategy authority.

Batch manifests must not:

- approve strategies;
- select candidates;
- create cohorts;
- score policy;
- rank candidates;
- recommend action;
- promote or demote candidates;
- infer paper/live readiness;
- create lifecycle transition authority;
- create automated approval.

Any strategy approval, scoring, ranking, recommendation, promotion, demotion,
readiness, lifecycle transition, paper/live decision, or runtime decision
requires separate explicit authorization.

## Minimal Future Implementation Slice Outline

A later Tier 3 AUTO package may implement a minimal batch manifest slice only
after separate authorization.

The minimal safe slice should be limited to:

- one concrete batch manifest format;
- one small local research-only fixture batch;
- explicit manifest and item validation;
- explicit resource-limit checks;
- output-location containment under a package-authorized local output root;
- failure accounting for invalid manifest, invalid item, skipped item,
  per-item failure, partial batch, resource-limit violation, and
  protected-boundary drift;
- validation evidence proving outputs are non-authoritative.

That later slice should not include parameter sweeps, Monte Carlo, result
store, dashboard, agent orchestration, evidence bridge, committed output,
scheduler, daemon, queue, watcher, trigger, paper/live, runtime, OMS, risk,
safe-mode, exchange, broker, order, policy, scoring, ranking,
recommendation, approval, promotion, demotion, readiness, or lifecycle work.

## Open Questions For Later Packages

Later packages must decide:

- where non-committed batch output roots live;
- whether batch manifests are exposed through a CLI, library call, or both;
- whether a repo-truth schema is needed;
- what final field names, types, and status vocabulary are used;
- how deterministic batch ids are derived;
- how resource limits are enforced;
- how partial-batch handling and retry handling are represented;
- how validation evidence is stored;
- how batch material remains separate from committed evidence artifacts;
- when result-store, dashboard, or agent read surfaces may consume validated
  batch material.

These are open questions only. AUTO-04 does not make these implementation
decisions.

## Stop / Escalation Rules

Future work must stop and escalate if it would:

- implement batch execution without Tier 3 authorization;
- require schema, validator, query-layer, config, dependency, data, result
  store, dashboard, agent, evidence bridge, test, or committed output changes
  outside explicit package scope;
- create or mutate EXP, REP, OL, REC, LCH, registry, advisory, shadow, summary,
  or evidence artifacts;
- touch runtime, paper/live, OMS, risk, safe-mode, exchange, broker, order,
  execution, deployment, scheduler, daemon, queue, watcher, trigger, or
  protected paths;
- create policy, scoring, ranking, recommendation, approval, promotion,
  demotion, readiness, or lifecycle authority;
- require an architecture decision left open by WP-12a through WP-12d;
- produce validation failures, integrity-view rows, semantic authority leakage,
  or changed-file scope drift.

## Non-Claims

WP-12e creates no:

- implementation;
- batch runner;
- scheduler, queue, daemon, watcher, trigger, or CLI;
- schema, validator, query-layer change, or test;
- config, dependency, or data change;
- result store or run registry;
- dashboard;
- agent;
- parameter sweep;
- Monte Carlo or robustness engine;
- evidence bridge;
- committed output;
- EXP, REP, OL, REC, LCH, registry, advisory, shadow, summary, or evidence
  artifact;
- runtime behavior;
- paper/live bridge;
- OMS, risk, safe-mode, exchange, broker, order, execution, deployment, or
  protected-path behavior;
- policy, scoring, ranking, recommendation, approval, promotion, demotion,
  readiness, or lifecycle authority.
