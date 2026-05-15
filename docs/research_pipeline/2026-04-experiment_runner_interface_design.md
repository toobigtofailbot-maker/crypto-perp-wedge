# Experiment Runner Interface Design (WP-12c / AUTO-02)

## Package Metadata

- Package label: WP-12c / AUTO-02.
- Package title: Experiment Runner Interface Design.
- Package class: Tier 1 documentation-only interface-design package.
- Effective base: refreshed `main` after merged WP-12b / AUTO-01.
- Created artifact: this interface-design document only.
- Modified status surface: `docs/project_status.md` only.

WP-12c creates no runner, implementation artifact, research evidence artifact,
schema, manifest format, validator, query-layer change, test change, runtime
behavior, CLI, config change, dependency change, data change, or protected-path
change.

## Purpose

WP-12c / AUTO-02 defines the intended future interface boundary for a local
research experiment runner before any runner code exists.

The purpose is to make later Tier 3 runner work safer by separating design
intent from implementation authority. This document describes future research
intent inputs, run requests, manifest responsibilities, local dry-run output
bundles, diagnostics, validation expectations, reproducibility fields, and
handoff boundaries at architecture level only.

AUTO-02 is design-only. It does not implement the runner and does not create a
repo-truth schema, manifest format, CLI, validator, query surface, or artifact
contract.

## Scope

This design may describe future intended boundaries for:

- research intent input;
- local run request content;
- manifest preservation responsibilities;
- local dry-run execution outputs;
- diagnostics and failure accounting;
- reproducibility and determinism fields;
- validation evidence future runner packages must emit;
- artifact, result-store, dashboard, and agent handoff limits;
- a minimal later vertical-slice outline.

All descriptions are future-facing. Any sample field categories are
illustrative design intent only unless a later package explicitly adopts them
through implementation, validation, and changed-file scope.

## Non-Goals

AUTO-02 does not:

- implement runner code;
- create a CLI or library interface;
- create JSON schemas, Python dataclasses, or executable examples;
- define a final manifest wire format;
- modify validators or integrity views;
- modify query-layer files;
- create EXP, REP, OL, REC, LCH, registry, advisory, shadow, summary, or other
  evidence artifacts;
- create committed run outputs;
- add dependencies, configs, or data;
- touch runtime, paper/live, OMS, risk, safe-mode, execution, or deployment;
- authorize policy, scoring, ranking, recommendation, approval, promotion,
  demotion, readiness, or lifecycle transition authority.

## Dependency Foundation

WP-12a installed the tiered automation-build operating model. Under that model,
Tier 1 packages may define safe architecture and interface intent when they
remain documentation-only and preserve protected boundaries.

WP-12b / AUTO-01 mapped the future research automation architecture. It records
AUTO-02 as the likely next Tier 1 interface-design package if AUTO-01 merges
cleanly and remains inside WP-12a.

AUTO-02 depends on those documents as boundary sources only. They do not
authorize implementation, artifacts, schemas, validators, query changes,
runtime contact, paper/live contact, or protected-path changes.

## Runner Role In The AUTO Architecture

The future experiment runner is intended to be a local research-only bridge
between an authorized research intent and deterministic local dry-run outputs.

In the AUTO architecture, the runner should eventually:

- accept a validated research intent and package-defined run request;
- preserve manifest metadata that identifies inputs, versions, and outputs;
- execute local dry-run research work only after a later Tier 3 package
  authorizes implementation;
- emit raw output material, diagnostics, validation evidence, and
  reproducibility references;
- stop downstream use when validation or failure accounting says the run is not
  usable.

The runner is not intended to be an evidence artifact author, result-store
authority, dashboard authority, agent authority, strategy approval system,
order generator, exchange connector, broker connector, scheduler, daemon, or
runtime control surface.

## Interface Principles

Future runner interfaces should be explicit, deterministic where practical,
local-first, and auditable.

The interface should preserve:

- clear separation between research intent, run request, manifest, and output
  bundle;
- stable identity for each local dry run;
- enough metadata to reproduce or reject a run later;
- validation evidence before any downstream surface consumes output material;
- failure states that block downstream use rather than silently degrade trust;
- no automatic conversion of runner outputs into committed evidence artifacts.

The interface should avoid:

- implicit defaults that affect research results without being preserved;
- hidden data selection;
- hidden parameter mutation;
- automatic artifact creation;
- any paper/live, runtime, OMS, risk, safe-mode, execution, deployment, policy,
  scoring, ranking, or recommendation authority.

## Research Intent Input Boundary

A future research intent should identify what is being evaluated and why, not
how a runner implementation is called.

At architecture level, a future intent should identify:

- candidate or strategy context;
- evaluation purpose;
- permitted data references or data family;
- declared timeframe and evaluation scope;
- parameter context or parameter family;
- expected research pipeline version or comparable provenance handle;
- constraints that limit local dry-run behavior;
- reproducibility references needed to connect the intent to later outputs.

The intent must not select a candidate for promotion, approve a strategy,
recommend action, rank alternatives, score policy, infer paper/live readiness,
or create lifecycle transition authority.

## Run Request Boundary

A future run request should translate a validated research intent into the
minimum local instructions needed for a deterministic research dry run.

At architecture level, a future run request should carry:

- run identity;
- intent reference;
- local data input references;
- candidate or strategy parameter values;
- evaluation window or scope;
- expected output location intent;
- resource and failure-accounting limits;
- reproducibility and environment references;
- validation expectations for the requested run.

AUTO-02 does not define final field names, types, required keys, default rules,
or a wire format. Those remain later package decisions.

## Manifest Boundary

A future manifest should preserve enough context to audit the local dry run and
connect outputs back to the request that produced them.

At architecture level, a future manifest should preserve:

- request identity and intent identity;
- repository version reference;
- research pipeline or implementation version reference;
- data references and data integrity handles;
- parameter values and evaluation scope;
- local environment metadata needed for reproducibility;
- output bundle references;
- diagnostics and validation summary references;
- terminal failure state when the run is not usable downstream.

The manifest is a preservation surface, not an evidence artifact. AUTO-02 does
not create a repo-truth manifest format.

## Local Dry-Run Execution Boundary

Future local dry-run execution should be research-only and bounded by the
request and manifest.

The future dry-run execution boundary should:

- consume only permitted local research inputs;
- produce local research output material;
- preserve deterministic references where practical;
- stop and mark failure when required inputs, parameters, data, or validation
  conditions are invalid;
- avoid any contact with exchange, broker, order, paper/live, runtime, OMS,
  risk, safe-mode, execution, deployment, scheduler, daemon, or queue surfaces.

AUTO-02 does not implement local dry-run execution.

## Output Bundle Boundary

A future output bundle should contain the raw material and metadata emitted by a
local dry run before any evidence bridge exists.

At architecture level, a future output bundle should contain:

- raw local run result material;
- metrics or summaries produced by the local research run;
- diagnostic records;
- validation state;
- failure accounting;
- manifest reference;
- reproducibility references;
- output completeness markers.

Runner outputs are not REP artifacts, OL artifacts, REC artifacts, registry
artifacts, or authoritative evidence. A later bridge package must explicitly
authorize and validate any conversion from runner output material to committed
evidence artifacts.

## Diagnostics And Failure Accounting

Future runner packages should make failures explicit and blocking.

Failure accounting should identify:

- invalid or incomplete research intent;
- invalid or incomplete run request;
- missing, stale, or disallowed local data reference;
- parameter or scope mismatch;
- local dry-run failure;
- partial output bundle;
- output completeness failure;
- manifest/reference mismatch;
- non-deterministic or insufficient reproducibility reference;
- validation failure;
- resource-limit violation;
- protected-boundary drift;
- integrity-view rows from downstream validation.

Any blocking failure state must prevent downstream use until a later package
resolves it.

## Reproducibility And Determinism Expectations

Future runner implementations should preserve enough information to rerun,
compare, or reject a local dry run.

At architecture level, future reproducibility fields should include:

- repository version reference;
- runner implementation version reference;
- research pipeline version or equivalent provenance;
- input data references and integrity handles;
- request and manifest identity;
- candidate or strategy context;
- parameter values;
- evaluation window or scope;
- local environment metadata that materially affects results;
- deterministic seed or randomness policy if later implementations introduce
  stochastic behavior;
- validation status and failure state.

AUTO-02 does not decide exact field names, storage location, or serialization.

## Validation Model

Future runner packages must emit validation evidence before downstream use.

At architecture level, validation should cover:

- request and manifest shape;
- intent/request/manifest reference consistency;
- permitted local data references;
- output bundle completeness;
- diagnostics and failure accounting;
- reproducibility metadata completeness;
- no automatic evidence artifact creation;
- no protected-path drift;
- no runtime, paper/live, OMS, risk, safe-mode, execution, deployment, policy,
  scoring, ranking, recommendation, approval, promotion, demotion, readiness,
  or lifecycle authority leakage.

Validation evidence should be explicit pass/fail material tied to the run or
package that produced it. Failed validation must stop downstream use.

## Artifact And Evidence Handoff Boundary

Future runner outputs may provide candidate material for later evidence work,
but they are not evidence artifacts by themselves.

Runner output material must not automatically create, mutate, replace, or
authorize EXP, REP, OL, REC, LCH, registry, advisory, shadow, or summary
artifacts.

A later evidence bridge package must explicitly define:

- which validated runner output material may be consumed;
- which committed artifact family may be authored;
- how source references are preserved;
- what validators and integrity views must pass;
- the exact changed-file set;
- how non-authoritative runner outputs remain distinguishable from committed
  evidence artifacts.

## Result-Store Handoff Boundary

A future result store or run registry may retain local run outputs, manifests,
diagnostics, validation states, and reproducibility metadata.

Result-store records are not authoritative evidence unless a later bridge
package explicitly authorizes and validates that role. Result-store records
must not become REP, OL, REC, registry, policy, scoring, ranking,
recommendation, approval, promotion, demotion, readiness, lifecycle, paper/live,
or runtime authority by implication.

Future result-store packages must define exact storage location, schema or
shape, validation, query/read surfaces, retention behavior, and handoff rules.

## Dashboard / Agent Handoff Boundary

Future dashboards may consume only read-only validated surfaces after later
dashboard packages define exact data surfaces.

Future agents may consume only committed artifacts, validated result-store
surfaces, or other later authorized read-only surfaces. Agents may summarize or
propose bounded research work only inside an approved envelope.

Dashboards and agents must remain non-authoritative until later packages define
exact surfaces. They must not control runtime, paper/live systems, OMS, risk,
safe-mode, execution, deployment, orders, brokers, exchanges, policy, scoring,
ranking, recommendation, approval, promotion, demotion, readiness, or lifecycle
transitions.

## Protected Runtime / Paper / Live Boundary

AUTO-02 does not authorize Tier 4.

Paper/live, runtime, OMS, risk, safe-mode, execution, deployment, operational
monitoring, exchange contact, broker contact, order generation, order routing,
runtime config mutation, and protected-path behavior remain blocked unless a
later package receives explicit authorization.

No future Tier 1, Tier 2, or Tier 3 package may treat this interface design as
permission to cross those protected boundaries.

## Candidate / Strategy Authority Boundary

The future runner interface may evaluate authorized research intent. It must
not create strategy authority.

The runner interface must not:

- select candidates;
- create cohorts;
- approve strategies;
- score policy;
- rank candidates;
- recommend strategy action;
- promote or demote a candidate;
- infer paper/live readiness;
- create lifecycle transition authority;
- create automated approval.

Any future candidate, strategy, cohort, policy, scoring, ranking,
recommendation, approval, promotion, demotion, readiness, or lifecycle decision
requires separate explicit authorization.

## Minimal Future Vertical Slice Outline

AUTO-03 may be a possible later Tier 3 local dry-run runner vertical-slice
package if separately authorized.

At most, such a later package candidate may include:

- one minimal local research intent fixture or equivalent authorized input;
- one local run request path;
- one manifest/output preservation path;
- one local dry-run output bundle;
- validation evidence for the request, manifest, output bundle, failure state,
  and protected-boundary preservation.

Such a future vertical slice should exclude result-store authority, dashboard
surfaces, agent orchestration, parameter sweeps, Monte Carlo, batch execution,
paper/live, runtime, OMS, risk, safe-mode, execution, deployment, policy,
scoring, ranking, recommendation, approval, promotion, demotion, readiness, and
lifecycle transition work unless separately authorized.

AUTO-02 does not draft or implement AUTO-03.

## Open Interface Questions For Later Packages

Later packages must decide:

- whether the runner is exposed as a CLI, library, or both;
- where future run requests and manifests live;
- whether a schema is needed for run requests or manifests;
- how local output bundles are named and retained;
- how reproducibility metadata is serialized;
- how failure accounting is represented;
- how result-store records differ from committed evidence artifacts;
- how dashboard read surfaces are limited;
- when agents may propose jobs;
- which validation commands become mandatory for runner packages;
- how resource limits are enforced.

These are open questions only. AUTO-02 does not make these implementation
decisions.

## Stop / Escalation Rules

Future packages must stop and escalate if they would:

- implement runner code without Tier 3 authorization;
- add schemas, validators, query-layer files, tests, configs, dependencies, or
  data without explicit scope;
- create or mutate committed evidence artifacts without explicit artifact
  package scope;
- touch runtime, paper/live, OMS, risk, safe-mode, execution, deployment, or
  protected paths;
- create scheduler, daemon, queue, or agent-controlled operation without
  explicit authorization;
- create policy, scoring, ranking, recommendation, approval, promotion,
  demotion, readiness, or lifecycle authority;
- treat runner outputs, result-store rows, dashboards, or agent summaries as
  committed evidence without an explicit bridge package;
- require an architecture decision that WP-12a, WP-12b, or AUTO-02 leaves open.

## Non-Claims

WP-12c creates no:

- runner;
- implementation;
- CLI;
- library interface;
- schema;
- manifest format;
- validator;
- query-layer change;
- test;
- config, dependency, or data change;
- runtime behavior;
- scheduler, daemon, or queue;
- EXP, REP, OL, REC, LCH, registry, advisory, shadow, summary, or evidence
  artifact;
- result store or run registry;
- dashboard;
- agent;
- paper/live bridge;
- order, broker, or exchange contact;
- policy, scoring, ranking, recommendation, approval, promotion, demotion,
  readiness, or lifecycle authority;
- AUTO-03 package.
