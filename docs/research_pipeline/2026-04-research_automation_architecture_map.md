# Research Automation Architecture Map (WP-12b / AUTO-01)

## Package Metadata

- Package label: WP-12b / AUTO-01.
- Package title: Research Automation Architecture Map.
- Package class: Tier 1 documentation-only architecture map.
- Effective base: refreshed `main` after merged WP-12a.
- Created artifact: this architecture-map document only.
- Modified status surface: `docs/project_status.md` only.

WP-12b creates no automation implementation, runner, batch runner, parameter
sweep, Monte Carlo engine, scheduler, dashboard, agent, paper/live bridge,
implementation artifact, research evidence artifact, schema, validator,
query-layer change, test change, runtime behavior, config change, dependency
change, data change, or protected-path change.

## Purpose

WP-12b / AUTO-01 maps the intended research automation system before any
automation implementation begins.

The purpose is to reduce drift when later Tier 3 automation slices begin. This
map defines component responsibilities, evidence handoffs, validation
expectations, and protected boundaries at architecture level only.

This document implements no code and authorizes no runtime, paper/live, OMS,
risk, safe-mode, execution, deployment, policy, scoring, ranking, or
recommendation work.

## Scope

This map may describe future intended components and boundaries for:

- local experiment-runner interface;
- local dry-run execution adapter;
- batch runner;
- parameter sweep system;
- Monte Carlo / robustness system;
- result store / run registry;
- dashboard data surfaces;
- agent orchestration scaffolds;
- validation hooks;
- artifact and evidence handoffs;
- future package sequence.

The map is non-authoritative for implementation details that require later
package-level repo truth. Later packages must still define exact files,
interfaces, validations, changed-file scope, and boundary authority.

## Non-Goals

AUTO-01 does not:

- implement runner code;
- implement batch execution;
- implement parameter sweeps;
- implement Monte Carlo;
- implement dashboards;
- implement agents;
- introduce schemas;
- modify validators;
- modify query-layer views;
- create artifacts;
- run experiments;
- add dependencies, configs, or data;
- touch runtime, paper/live, OMS, risk, safe-mode, execution, or deployment;
- authorize Tier 4 work.

## Current Foundation

Stage 2 first sub-stage is locked complete-as-executed by WP-11c. It proved one
exact segment through selection, REP -> OL -> REC mechanics, REC-5 crossing, and
a descriptive consumer brief.

WP-12a installed the tiered automation-build operating model. It permits
AUTO-01 as a Tier 1 documentation package after WP-12a merges, provided AUTO-01
stays inside the operating model and implements no code.

The repo currently contains artifact families and validators that future
automation must respect, including EXP, REP, OL, REC, LCH, registry, advisory,
shadow, and summary families. Existing research-query surfaces and integrity
views are authoritative read-only context for later automation packages.

The system is not yet an automated research machine. Future automation should
produce evidence through explicit interfaces and later authorized package
boundaries, not by mutating prior artifacts.

## Target Research Automation Architecture

The intended high-level flow is:

```text
strategy / candidate input
-> experiment-runner interface
-> local dry-run execution
-> batch manifest
-> parameter sweep expansion
-> Monte Carlo / robustness jobs
-> result store / run registry
-> evidence artifact production candidates
-> dashboard data surfaces
-> agent-readable summaries
-> human review gates
```

Paper/live integration is outside this architecture and remains Tier 4. No
exchange, broker, order-routing, runtime, or protected execution behavior is
included in AUTO-01.

## Component Map

### Strategy / Candidate Source

Responsibility: provide an explicit research candidate or strategy definition
for local research evaluation.

Input/output boundary: consumes authorized candidate or strategy context and
emits a runner-consumable research intent in a later package-defined shape.

Must not do yet: select candidates, create cohorts, make performance-based
approval claims, or create policy/scoring/ranking/recommendation authority.

### Experiment Runner Interface

Responsibility: define the future contract between candidate intent and local
research execution.

Input/output boundary: accepts validated research intent and produces a local
run request plus manifest metadata in a later package-defined format.

Must not do yet: execute code in WP-12b, contact external trading systems,
write committed artifacts automatically, or mutate configs/dependencies.

### Execution Adapter For Local Dry Runs

Responsibility: perform local research-only dry runs after a later Tier 3 slice
authorizes implementation.

Input/output boundary: consumes run requests and local research data, then emits
raw run outputs, diagnostics, and manifest references.

Must not do yet: contact exchanges/brokers, generate orders, touch paper/live
runtime paths, or commit REP/OL/REC artifacts automatically.

### Batch Manifest

Responsibility: describe multiple local research jobs under explicit limits.

Input/output boundary: consumes one or more run requests and emits a bounded
batch definition with resource and failure-accounting fields.

Must not do yet: create a scheduler, daemon, queue, 24/7 automation loop, or
agent-controlled execution surface.

### Parameter Sweep Planner

Responsibility: expand approved candidate definitions into controlled parameter
grids or search spaces.

Input/output boundary: consumes explicit candidate parameters and emits bounded
run requests for later local execution.

Must not do yet: claim optimality, approve a strategy, recommend promotion,
infer live readiness, or bypass anti-overfit rules.

### Monte Carlo / Robustness Planner

Responsibility: define later stress and robustness jobs.

Input/output boundary: consumes run outputs or candidate definitions and emits
robustness job requests or summaries in a later authorized format.

Must not do yet: implement simulation engines, promote candidates, or authorize
paper/live use.

### Result Store / Run Registry

Responsibility: retain raw run outputs, metadata, reproducibility fields, and
validation status for future research automation.

Input/output boundary: consumes local run outputs and emits read-only lookup
surfaces for dashboards, summaries, and later evidence-bridge packages.

Must not do yet: become REP/OL/REC truth, policy authority, scoring authority,
ranking authority, or recommendation authority.

### Evidence Artifact Bridge

Responsibility: define a future authorized bridge from validated run outputs to
evidence artifact candidates.

Input/output boundary: consumes validated result-store entries and emits
candidate material for separately authorized EXP/REP/OL/REC package work.

Must not do yet: automatically create or mutate committed artifacts.

### Dashboard Data-Surface Layer

Responsibility: expose read-only research automation status and outputs after
later dashboard packages exist.

Input/output boundary: consumes result-store or validated query surfaces and
emits read-only dashboard data.

Must not do yet: control trading, runtime, paper/live behavior, or
recommendation decisions.

### Agent Orchestration Layer

Responsibility: provide later orchestration and summarization helpers after
runners, stores, and dashboard surfaces are stable.

Input/output boundary: consumes approved envelopes and validated surfaces, then
proposes bounded jobs or summaries for human review.

Must not do yet: directly control runtime, paper/live systems, execution, OMS,
risk, safe mode, policy, scoring, ranking, or recommendation.

### Validation Gate

Responsibility: enforce package-specific and run-specific checks before outputs
are trusted by later surfaces.

Input/output boundary: consumes manifests, run outputs, metadata, and artifact
candidate material, then emits pass/fail validation evidence.

Must not do yet: replace existing validators, weaken integrity views, or bypass
required tests.

### Human Review Gate

Responsibility: preserve human review before evidence promotion, package merges,
or any future boundary crossing.

Input/output boundary: consumes validated summaries and package diffs, then
supports merge/follow-up/blocked decisions.

Must not do yet: automate approval, strategy selection, paper/live transition,
or protected boundary crossing.

## Artifact And Evidence Interfaces

Runner outputs are not automatically REP artifacts. Batch results are not
automatically OL or REC artifacts. Result-store records are non-authoritative
until a later package explicitly defines and validates their role.

Evidence artifact creation remains a separate authorized package boundary.
Result stores may feed later REP, OL, or REC creation only if a package
explicitly authorizes that bridge and validates the exact changed-file set.

Committed artifacts remain additive and preserved unless a future
backward-compatible correction is explicitly scoped. Existing validators and
integrity views remain authoritative gates for committed artifact families.

## Runner Boundary

The future runner is local research execution only.

It should be deterministic where practical, manifest-producing, and explicit
about data inputs, code version, candidate context, parameters, resource limits,
and output locations.

The runner must not:

- contact exchanges or brokers;
- create orders or route signals;
- touch runtime, OMS, risk, safe-mode, paper/live, or deployment paths;
- change configs or dependencies without explicit package authorization;
- automatically commit EXP, REP, OL, REC, LCH, registry, or evidence artifacts.

## Batch Execution Boundary

Batch execution means multiple local research jobs under a manifest.

Future batch packages should define explicit resource limits, job identity,
failure accounting, deterministic output locations, and validation expectations.
Resumability is a later design concern.

There is no scheduling daemon, no 24/7 automation, no job queue, and no agent
control in AUTO-01.

## Parameter Sweep Boundary

Parameter sweeps are controlled parameter-grid or search-space expansions tied
to explicit candidate or strategy definitions.

They are not a claim of optimality, not performance-based strategy approval,
and not paper/live readiness. Later packages must define anti-overfit rules,
validation rules, allowed data inputs, resource limits, and output semantics
before a parameter sweep MVP can merge.

Parameter sweeps must not automatically promote, recommend, approve, rank, or
score strategies.

## Monte Carlo / Robustness Boundary

Monte Carlo and robustness testing are later stress and robustness layers.
Potential future methods may include trade-order reshuffling, return resampling,
cost/slippage stress, walk-forward or regime splits, drawdown stress, and
parameter-stability maps.

No Monte Carlo or robustness engine is implemented here. Robustness outputs
must not be used for promotion, paper/live transition, runtime action, or
strategy approval until later explicit authority exists.

## Result Store / Run Registry Boundary

The result store / run registry is a future non-authoritative store for raw run
outputs and metadata.

It may later support dashboards, agent-readable summaries, and evidence-bridge
packages. It must preserve reproducibility fields, code/data identifiers,
manifest references, validation metadata, failure metadata, and output shape
metadata.

It must not become policy authority, scoring authority, ranking authority, or
recommendation authority without explicit later design and authorization.

## Dashboard Data-Surface Boundary

Dashboards are later read-only monitoring surfaces over research automation
status and outputs.

Initial dashboard work should be limited to research automation status, run
metadata, validation state, and output summaries from approved surfaces.

Dashboards must not provide trading control, runtime control, paper/live
control, order control, policy authority, scoring authority, ranking authority,
or recommendation authority.

## Agent Orchestration Boundary

Agents are later orchestration and summarization helpers after runners, result
stores, and dashboards exist.

Agents may propose jobs only inside approved envelopes. Agents may summarize
results only from committed artifacts, validated result-store surfaces, or
other later authorized read-only surfaces.

Agents must not directly control runtime, paper/live systems, OMS, risk,
safe-mode, execution, policy, scoring, ranking, or recommendation authority.

## Validation And Failure-Mode Model

Future automation packages should define validation for:

- refreshed-main and clean-tree preflight;
- manifest shape and reference validation;
- dry-run validation;
- output shape validation;
- resource-limit checks;
- deterministic/reproducibility checks where practical;
- failure accounting;
- artifact-preservation checks;
- no protected-path drift;
- exact changed-file checks;
- semantic scans for authority leakage;
- unit and integration coverage before Tier 3 code merges.

Failure modes should be explicit. Failed jobs, partial batches, invalid
manifests, invalid outputs, missing data, non-deterministic outputs, resource
limit violations, and integrity-view rows must stop downstream use until a
later package resolves them.

## Protected Runtime / Paper / Live Boundary

AUTO-01 does not authorize Tier 4.

Paper/live, OMS, risk, safe-mode, execution, deployment, operational
monitoring, exchange/broker contact, order generation, trading signal
execution, runtime config mutation, and live data automation beyond later
explicitly authorized research data flows remain blocked.

No future Tier 1, Tier 2, or Tier 3 package may treat this architecture map as
permission to cross those protected boundaries.

## First Implementation Sequence After AUTO-01

The likely next sequence remains non-authoritative but useful:

```text
AUTO-02 - Experiment Runner Interface Design
AUTO-03 - Local Dry-Run Runner Vertical Slice
AUTO-04 - Batch Manifest Format
AUTO-05 - Parameter Sweep MVP
AUTO-06 - Result Store / Run Registry
AUTO-07 - First Dashboard Data Surface
```

AUTO-02 may be drafted after AUTO-01 only if AUTO-01 merges cleanly and AUTO-02
remains Tier 1 documentation / interface design with no implementation.

If AUTO-02 would need code, dependencies, configs, data, protected paths,
runtime-adjacent behavior, or Tier 4 scope, future work must stop and escalate
under WP-12a.

WP-12b does not draft AUTO-02.

## Open Architecture Questions For Later Packages

Later packages must resolve:

- where result stores should live;
- whether a new schema is needed for run manifests;
- whether a runner should be a CLI, library, or both;
- how to prevent overfitting in parameter sweeps;
- how to represent Monte Carlo outputs;
- how dashboards should be served;
- when agents are allowed to propose jobs;
- how resource limits are enforced;
- what data inputs are allowed;
- when paper/live bridges can be discussed.

AUTO-01 records these as open questions only.

## Stop / Escalation Rules

Future packages must stop and escalate if they would:

- implement code before the relevant design is authorized;
- add dependencies, configs, or data;
- touch runtime, paper/live, OMS, risk, safe-mode, execution, or deployment;
- create policy/scoring/ranking/recommendation authority;
- create artifacts without explicit artifact package scope;
- mutate committed artifacts;
- modify schemas, validators, query-layer files, or tests without explicit
  scope;
- broaden beyond the automation envelope;
- weaken protected boundaries;
- treat runner outputs, result-store rows, dashboards, or agent summaries as
  committed evidence without an explicit bridge package.

## Non-Claims

WP-12b creates no:

- implementation;
- runner;
- scheduler;
- parameter sweep;
- Monte Carlo engine;
- dashboard;
- agent;
- paper/live bridge;
- runtime behavior;
- config, dependency, or data change;
- schema, validator, query-layer, or test change;
- EXP, REP, OL, REC, LCH, or registry artifact;
- research evidence artifact;
- consumer brief;
- strategy recommendation;
- live/paper readiness;
- policy, scoring, ranking, or recommendation authority;
- AUTO-02 package.
