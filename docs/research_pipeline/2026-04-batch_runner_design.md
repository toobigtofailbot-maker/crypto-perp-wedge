# Batch Runner Design (WP-12g / AUTO-06)

## Package Metadata

- Package label: WP-12g / AUTO-06.
- Package title: Batch Runner Design.
- Package class: Tier 1 documentation-only design package.
- Effective base: refreshed `main` after merged WP-12f / AUTO-05.
- Created artifact: this design document only.
- Modified status surface: `docs/project_status.md` only.

AUTO-06 is design-only. It creates no implementation, batch runner, CLI, tests,
schema, validator, query-layer change, config, dependency, data, committed
output, evidence artifact, result store, dashboard, agent, scheduler, daemon,
queue, watcher, trigger, parameter sweep, Monte Carlo, evidence bridge, runtime
behavior, paper/live bridge, or protected-path change.

## Purpose

AUTO-06 defines the future boundary for a local batch runner before any batch
runner implementation is authorized.

The purpose is to prevent implementation drift after WP-12f. WP-12f created a
local batch manifest helper only. This document describes how a future batch
runner may consume that material and call local dry-run functionality if a later
Tier 3 package separately authorizes the implementation.

This document is not a runner specification, executable contract, schema,
validator, CLI design, result-store design, dashboard design, agent design, or
runtime authorization.

## Scope

This design may describe future intended boundaries for:

- accepting a validated WP-12f-style batch manifest;
- validating all batch items before execution;
- allocating per-item output directories under a caller-authorized batch output
  root;
- calling local dry-run functionality only through an explicitly authorized
  interface;
- collecting per-item local output material;
- producing a local batch execution summary;
- producing failure accounting;
- preserving non-authoritative status;
- stopping on protected-boundary drift;
- outlining a minimal later Tier 3 implementation slice.

All future behavior in this document is design intent only. A later package must
define exact files, interfaces, validation evidence, changed-file scope, and
authorization before implementation.

## Non-Goals

AUTO-06 does not:

- implement batch execution;
- create a batch runner;
- create a CLI;
- create tests;
- create a schema or validator;
- modify query-layer behavior;
- modify configs, dependencies, or data;
- create committed output or evidence artifacts;
- create result-store, dashboard, agent, scheduler, daemon, queue, watcher,
  trigger, parameter-sweep, Monte Carlo, evidence-bridge, runtime, paper/live,
  OMS, risk, safe-mode, exchange, broker, order, or protected-path behavior;
- score, rank, recommend, approve, promote, demote, infer readiness, or create
  lifecycle transition authority.

## Dependency Foundation

WP-12a installed the tiered automation-build operating model. It keeps
paper/live, runtime, OMS, risk, safe-mode, execution, deployment, protected
paths, policy, scoring, ranking, and recommendation boundaries blocked unless a
later package explicitly authorizes them.

WP-12b mapped the research automation architecture. It identified batch
execution as a future local research automation boundary, not as a scheduler,
daemon, queue, result store, dashboard, agent, evidence artifact, or runtime
control surface.

WP-12c defined the future experiment-runner interface boundary for research
intent, run request, manifest, local dry-run output, diagnostics, validation,
reproducibility, and downstream handoffs.

WP-12d implemented one narrow local dry-run runner vertical slice. It exposes
`run_local_dry_run(intent, output_dir)` as a local in-process API that accepts
explicit caller-provided intent, writes only under a caller-provided output
directory, and emits non-authoritative run request, manifest, output bundle,
and validation report material.

WP-12e defined the future batch manifest format boundary as documentation only.

WP-12f implemented a local batch manifest builder/validator only. It exposes
`build_batch_manifest(items, output_root, resource_limits, static_metadata=None)`,
requires an existing caller-provided output root, validates local batch items
and resource limits, writes only `batch_manifest.json` and
`batch_validation_report.json` under that output root when validation passes,
and writes nothing when validation fails. WP-12f does not call, wrap, import, or
modify `run_local_dry_run(...)`.

AUTO-06 depends on these packages as boundary sources only. It does not extend
implementation authority.

## Relationship To WP-12d Local Dry-Run Runner

WP-12d is the current local dry-run execution unit. A future batch runner may
call WP-12d local dry-run functionality, or a later compatible local dry-run
interface, only after a separate Tier 3 package explicitly authorizes that
implementation.

The future relationship should be one-way and bounded:

- the batch runner consumes validated batch items;
- each batch item maps to one local dry-run request or compatible local run
  unit;
- each item receives a caller-authorized output directory;
- local dry-run outputs remain local research-only and non-authoritative;
- failed local dry-run items are recorded through explicit failure accounting.

AUTO-06 does not modify `tools/research_automation/local_dry_run_runner.py`,
wrap `run_local_dry_run(...)`, add tests, create a CLI, or implement batch
execution.

## Relationship To WP-12f Batch Manifest Helper

WP-12f creates manifest material only. A future batch runner may consume a
validated WP-12f-style manifest, but manifest presence alone must not execute
anything.

A future runner should treat WP-12f manifest material as input to be checked,
not as authority. The future runner must validate every item before execution,
confirm output-root containment, confirm resource-limit compatibility, and stop
if manifest material would imply authority outside the later approved package.

AUTO-06 does not modify `tools/research_automation/batch_manifest.py`, create a
new manifest format, create a schema, or create a validator.

## Batch Runner Role In The AUTO Architecture

A future local batch runner is a bounded orchestrator for multiple local
research-only dry-run units.

Its intended role is to:

- accept explicit local batch input;
- verify the batch is valid before item execution;
- coordinate per-item local dry-run calls through an approved interface;
- preserve item outputs and failure accounting under a caller-authorized output
  root;
- summarize local batch execution without creating evidence authority;
- stop when protected-boundary drift appears.

The future runner is not a scheduler, daemon, queue, watcher, trigger, result
store, dashboard, agent, evidence bridge, strategy approval surface, order
generator, runtime control surface, or paper/live bridge.

## Future Runner Input Boundary

A future runner should accept only explicit caller-provided input. At minimum,
that input should include:

- a validated WP-12f-style batch manifest or later approved compatible shape;
- a caller-authorized batch output root;
- resource-limit expectations;
- static metadata needed for reproducibility;
- an explicitly authorized local dry-run interface reference.

The runner must not infer execution authority from a file existing on disk, a
manifest being present in a directory, a config value, a scheduler event, an
agent request, or a dashboard action. Input must remain explicit per invocation
under a later Tier 3 package.

## Future Runner Execution Boundary

Future execution should be local research-only and per-item bounded.

A later implementation should:

- validate all batch-level and item-level input before any item runs;
- allocate deterministic per-item output directories under the batch output
  root;
- call local dry-run functionality only through an explicitly authorized
  interface;
- collect per-item local output material;
- record success, skipped, failed, and blocked items explicitly;
- stop or mark blocked if an item would require protected-boundary contact.

A future runner must not execute merely because a manifest exists. It must not
contact runtime, paper/live, OMS, risk, safe-mode, exchange, broker, order,
deployment, scheduler, daemon, queue, watcher, trigger, or protected-path
surfaces.

## Output Root And File-Write Boundary

A future batch runner should write only under a caller-authorized batch output
root. The output root must be explicit for the invocation and validated before
execution.

Future writes should be limited to local batch-run material such as:

- per-item local dry-run output directories;
- a local batch execution summary;
- local failure accounting;
- local validation evidence;
- reproducibility metadata for the batch invocation.

The runner must not write committed evidence artifacts or mutate EXP, REP, OL,
REC, LCH, registry, advisory, shadow, summary, or evidence artifact families. It
must not write source code paths, dependency files, configs, data directories,
runtime paths, paper/live paths, or protected paths unless a later package
explicitly authorizes exact changed-file scope.

## Validation And Failure Accounting Boundary

A future batch runner must make validation and failure accounting explicit.

Validation should cover:

- manifest completeness;
- item completeness;
- item-to-output-directory containment;
- resource-limit compatibility;
- local dry-run interface authorization;
- per-item output completeness;
- reproducibility metadata completeness;
- no committed evidence artifact creation;
- no protected-boundary drift;
- non-authoritative downstream status.

Failure accounting should distinguish invalid batch input, invalid item,
skipped item, per-item failure, partial batch, resource-limit violation,
output-location violation, reproducibility failure, validation failure, and
protected-boundary drift.

Failed validation must stop downstream consumption. A future runner must not
silently treat partial output as success.

## Determinism And Reproducibility Expectations

A future batch runner should preserve enough information to rerun, compare, or
reject a local batch.

Future reproducibility categories should include:

- repo version reference;
- batch runner implementation reference;
- source manifest reference;
- local dry-run implementation reference;
- item identity set;
- output-root reference;
- resource-limit settings;
- static metadata that materially affects results;
- deterministic seed or randomness policy if later packages introduce
  stochastic behavior;
- validation and failure state.

AUTO-06 does not define exact field names, hashing rules, storage location, or
serialization.

## No-Execution-By-Manifest-Presence Rule

Manifest presence is not execution authority.

A future runner must not watch directories, poll for manifests, trigger when a
file appears, auto-run based on a committed manifest, or infer execution from
the existence of `batch_manifest.json`.

Every future batch execution must require an explicit later-authorized
invocation path, explicit caller-provided input, and validation before any item
runs.

## Non-Authoritative Evidence Boundary

Future batch-run output material is local research-only and non-authoritative.

It is not EXP, REP, OL, REC, LCH, registry, advisory, shadow, summary, or an
evidence artifact. It must not create lifecycle transition authority. It must
not infer candidate approval, strategy approval, promotion, demotion,
paper/live readiness, policy action, score, rank, or recommendation.

Any future conversion from local batch output material to committed evidence
requires a separate explicitly authorized evidence bridge package with exact
changed files, validators, integrity checks, semantic boundary review, and
preserved source references.

## Result-Store / Dashboard / Agent Boundary

AUTO-06 creates no result store, dashboard, or agent.

A future result store, dashboard, or agent may consume batch material only after
separate packages define exact read-only surfaces and validation. Result stores
must remain non-authoritative unless a later package explicitly defines their
role. Dashboards must remain read-only. Agents may summarize or propose bounded
research work only inside an approved envelope.

No result store, dashboard, or agent may infer policy, scoring, ranking,
recommendation, approval, promotion, demotion, readiness, lifecycle,
paper/live, runtime, OMS, risk, safe-mode, execution, exchange, broker, or
order authority from batch-run material.

A future batch runner must not publish to result stores, dashboards, or agents
without separate authorization that defines exact surfaces, validation, and
non-authoritative status.

## Protected Runtime / Paper / Live Boundary

AUTO-06 does not authorize Tier 4.

Future batch-runner implementation must remain local research-only unless a
later package explicitly authorizes otherwise. It must not contact exchange,
broker, order, runtime, OMS, risk, safe-mode, paper/live, deployment,
operational monitoring, scheduler, daemon, queue, watcher, trigger, or
protected-path surfaces.

No future Tier 1, Tier 2, or Tier 3 package may treat this design as permission
to cross protected runtime, paper, live, OMS, risk, safe-mode, execution, or
deployment boundaries.

## Candidate / Strategy Authority Boundary

A future batch runner may evaluate authorized local research items. It must not
create candidate or strategy authority.

The future runner must not:

- infer candidate approval;
- infer strategy approval;
- score policy;
- rank candidates;
- recommend action;
- promote or demote candidates;
- infer paper/live readiness;
- create lifecycle transition authority;
- create automated approval.

Any candidate, strategy, cohort, policy, scoring, ranking, recommendation,
approval, promotion, demotion, readiness, lifecycle, paper/live, or runtime
decision requires separate explicit authorization.

## Minimal Future Implementation Slice Outline

A later Tier 3 AUTO package may implement a minimal local batch runner only
after separate authorization.

The minimal safe slice should be limited to:

- one explicit in-process local API or explicitly scoped CLI;
- one small local research-only fixture batch;
- consumption of one validated WP-12f-style manifest or approved compatible
  structure;
- pre-execution validation for every item;
- per-item output directories under a caller-authorized batch output root;
- calls to local dry-run functionality only through an approved interface;
- local batch execution summary material;
- local failure accounting;
- validation evidence proving outputs are non-authoritative and protected
  boundaries remain untouched.

That later slice should not include result store, dashboard, agent
orchestration, scheduler, daemon, queue, watcher, trigger, parameter sweep,
Monte Carlo, evidence bridge, committed output, paper/live, runtime, OMS, risk,
safe-mode, exchange, broker, order, policy, scoring, ranking, recommendation,
approval, promotion, demotion, readiness, or lifecycle work.

## Open Questions For Later Packages

Later packages must decide:

- whether the future runner is a library call, CLI, or both;
- the exact invocation contract;
- the exact batch summary shape;
- the exact failure status vocabulary;
- how item output directories are named;
- how partial-batch handling and retry handling are represented;
- whether a schema is needed;
- what validation command or tests are required;
- how local batch output retention works;
- when result-store, dashboard, or agent read surfaces may consume validated
  batch material.

These are open questions only. AUTO-06 does not make these implementation
decisions.

## Stop / Escalation Rules

Future work must stop and escalate if it would:

- implement a batch runner without separate Tier 3 authorization;
- execute because a manifest exists;
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
- require an architecture decision left open by WP-12a through WP-12f;
- produce validation failures, integrity-view rows, semantic authority leakage,
  or changed-file scope drift.

## Non-Claims

WP-12g creates no:

- implementation;
- batch runner;
- CLI;
- tests;
- schema;
- validator;
- query-layer change;
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
  readiness, or lifecycle authority.
