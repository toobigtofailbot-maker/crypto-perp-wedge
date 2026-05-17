# Parameter Sweep Design (WP-12p / AUTO-15)

## Package Metadata

- Package label: WP-12p / AUTO-15.
- Package title: Parameter Sweep Design.
- Package class: Tier 1 documentation-only architecture design.
- Effective base: refreshed `main` after merged WP-12o / AUTO-14.
- Created artifact: this design document only.
- Modified status surface: `docs/project_status.md` only.

WP-12p creates no implementation, code, tests, schema, validator,
query-layer exposure, CLI, config, dependency, data, committed output,
evidence artifact, result-store implementation, dashboard, agent, scheduler,
daemon, queue, watcher, trigger, parameter sweep execution, Monte Carlo,
evidence bridge, runtime, paper/live, OMS, risk, safe-mode,
exchange/broker/order, protected-path behavior, policy, scoring, ranking,
recommendation, approval, promotion, demotion, readiness, lifecycle, or
downstream authority.

## Purpose

WP-12p designs a future local parameter sweep capability that may exercise the
WP-12d through WP-12o local automation foundation.

This package is architecture-only and documentation-only. It does not implement
parameter sweep execution. It does not create a sweep specification file, output
file, schema, validator, query view, CLI, result store, local output artifact,
or committed evidence artifact.

## Scope

The design defines how a future local parameter sweep should:

- specify a bounded deterministic parameter grid;
- fan out sweep points into local batch-run-compatible work;
- preserve sweep-point identity and parameter metadata;
- aggregate outputs structurally without interpretive authority;
- flow through the existing local batch and local registry chain;
- remain local-only, research-only, non-authoritative, and no-committed-evidence.

## Non-Goals

WP-12p does not implement parameter sweep behavior. It does not add code,
tests, schemas, validators, query-layer exposure, CLI behavior, result stores,
dashboards, agents, schedulers, daemons, queues, watchers, triggers, parameter
sweep execution, Monte Carlo behavior, evidence bridges, runtime behavior,
paper/live behavior, OMS behavior, risk behavior, safe-mode behavior,
exchange/broker/order behavior, configs, dependencies, data files, committed
outputs, evidence artifacts, protected-path behavior, or downstream authority.

WP-12p does not authorize optimizer framing, best parameter selection, ranking,
scoring, recommendation, approval, promotion, demotion, readiness, lifecycle
authority, policy action, runtime action, paper/live action, cross-segment
inference, cross-candidate inference, cross-pipeline-version inference, or
automatic evidence promotion.

## Dependency Foundation

WP-12d through WP-12o created a validated local automation chain:

- WP-12d created local dry-run output material.
- WP-12f created local batch manifest material.
- WP-12h created local batch-run summary material.
- WP-12j created local batch summary validation.
- WP-12k integrated batch summary validation before summary persistence.
- WP-12m created a local run registry builder.
- WP-12n created local run registry validation.
- WP-12o integrated local registry validation before registry persistence.

WP-12m, WP-12n, and WP-12o closed the local registry builder-validator loop:
`build_local_run_registry(...)` builds the in-memory registry payload, validates
that payload with `validate_local_run_registry(...)`, and writes
`local_run_registry.json` only if validation passes.

The local automation foundation is complete enough for its scoped purpose and
should now be exercised through actual use. Main 3.0 instructed that more
preemptive validation or hardening should stop unless real use exposes a
failure mode.

## Architecture Decision Summary

The recommended v1 direction is a finite deterministic local parameter sweep
that is:

- human-initiated;
- local-only;
- research-only;
- non-authoritative;
- bounded to one research question, one strategy context, and one compatible
  batch-run framework boundary;
- represented by future local JSON sweep specification material under
  caller-provided local output roots or caller-provided local input paths;
- expanded into static batch-compatible work;
- aggregated structurally only.

The design explicitly defers Monte Carlo, dashboards, agents, evidence bridge,
runtime, paper/live, OMS, risk, safe-mode, exchange/broker/order, and protected
path behavior.

## Why Parameter Sweep Is Next

Parameter sweep is the natural next user of the local automation foundation.
Sweeps produce repeated and varied local workloads that can exercise batch-run
and registry behavior without crossing protected runtime boundaries.

Design must precede implementation because sweep specification format,
fan-out semantics, aggregation semantics, combinatorics limits, reproducibility
rules, and authority boundaries are architecture decisions.

Monte Carlo, dashboards, agents, and evidence bridge work remain deferred.

## Intended Near-Term Destination

The near-term destination is faster local research iteration with structured
multi-parameter experiment running:

- a researcher specifies parameter ranges;
- future automation runs sweep points;
- structured local outputs land in the validated local registry chain;
- the researcher consumes outputs through existing local files and tools.

This is not automated experiment generation, multi-strategy orchestration at
scale, Monte Carlo, a dashboard, an agent, evidence promotion, or paper-trading
readiness.

## Sweep Concept

A future parameter sweep is a human-initiated local research activity. It is
finite and deterministic. It operates within one research question, one strategy
context, and one compatible local batch-run framework boundary.

A sweep is a collection of sweep points. Each point has explicit parameter
values and a stable point identity. A sweep point is local work input, not a
claim about quality or suitability.

A sweep is not an optimizer, recommender, approval mechanism, evidence-promotion
mechanism, runtime decision surface, or paper/live decision surface.

## Research-Question Boundary

V1 applies only to research questions already expressible through the existing
local batch-run framework.

V1 must not invent new research-question semantics. It must not combine
cross-segment, cross-pipeline-version, cross-candidate, or cross-strategy
inference. If a research question's structure is ambiguous, a future
implementation package must stop instead of guessing.

## Parameter Specification Model

Alternative A: inline ad hoc parameter lists directly inside future runner
calls. This is simple, but it makes sweep intent harder to inspect, reproduce,
or reuse.

Alternative B: local JSON sweep specification under caller-provided output
roots or caller-provided input paths. This is inspectable, deterministic,
file-based, compatible with the local-only boundary, and avoids executing
Python as specification.

Alternative C: committed sweep specification artifacts in the repo. This would
blur local research output with repo truth and could imply a stronger artifact
authority than the local automation tranche currently has.

Alternative D: Python-code-defined sweep definitions. This is flexible, but it
turns specification into executable code and increases ambiguity around
deterministic inspection.

The recommended v1 approach is Alternative B: future local JSON sweep
specification material under caller-provided local output roots or
caller-provided local input paths, not committed to the repo. WP-12p does not
create that JSON file, shape, schema, or validator.

## Sweep Enumeration And Determinism

Future v1 should enumerate sweep points deterministically and preserve stable
ordering. The same sweep specification and same code/data state should produce
the same point list in the same order.

Stable point IDs should be derived from deterministic hashes over sweep spec
identity, parameter values, and package or implementation identifiers. Point
identity must not use timestamps or random UUIDs.

Future implementation must reject ambiguous parameter grids and duplicate
parameter combinations.

## Fan-Out Semantics Alternatives

Alternative A: sweep-as-batch-of-runs. One sweep expands into many existing
local batch-run-compatible work items. This reuses the current local batch and
registry chain.

Alternative B: sweep-as-batch-of-batches. One sweep manages multiple batch
manifests or batch outputs. This may become useful later, but it adds nesting
before the first vertical slice has proven the simpler shape.

Alternative C: sweep-as-distinct artifact type with its own execution model.
This would create parallel execution semantics and a broader surface before
repo truth shows the need.

Alternative D: adaptive sweep where later points depend on prior results. This
introduces interpretation and control flow that is out of v1 scope.

## Selected Fan-Out Approach And Rationale

The selected v1 approach is static deterministic sweep-as-batch-compatible
fan-out.

Each sweep point should be independently expressible as existing local
batch-run-compatible work. Future implementation should reuse local batch-run
mechanics rather than creating a parallel runner if feasible.

V1 should not include adaptive sweeps, scheduler behavior, queue behavior,
daemon behavior, watcher behavior, trigger behavior, or new execution authority.
Batch-of-batches remains deferred until after the first vertical slice exposes a
real need.

## Result Aggregation Semantics Alternatives

Alternative A: concatenate per-point summaries only. This is simple, but it
does not clearly preserve sweep dimensions, point identity, and references.

Alternative B: structural aggregation with sweep dimension metadata and
per-point references. This preserves identity, parameters, output references,
validation status, registry references, and failure reasons without adding
interpretive authority.

Alternative C: interpretive aggregation with metrics, winners, thresholds,
recommendations, or ranking. This is out of scope because it turns local
research output into authority.

Alternative D: cross-sweep or cross-question aggregation. This is out of scope
for v1 because it invites inference across boundaries that the local automation
foundation has not authorized.

## Selected Aggregation Approach And Rationale

The selected v1 approach is structural aggregation only.

Future aggregation may preserve:

- sweep identity;
- sweep point identity;
- parameter values;
- per-point local output references;
- per-point validation status;
- local registry references;
- failure reasons;
- descriptive counts such as total points, succeeded points, failed points,
  blocked points, and skipped points.

Future aggregation must not identify a best point, winner, rank, score,
recommendation, approval, promotion, demotion, readiness, lifecycle action, or
policy action. It must not create cross-sweep, cross-question, cross-candidate,
cross-segment, or cross-pipeline-version inference.

## Sweep Size / Combinatorics Boundary

V1 should be intentionally small. WP-12q, if separately authorized, should use
one worked example with a bounded small sweep.

Future implementation should calculate point count before execution and stop on
excessive combinations. Large sweeps, thousands of points, high-dimensional
grids, parallel execution, scheduling, and distributed execution are out of v1
scope.

If a future vertical slice needs a hard limit, it should choose a conservative
default and document it in that package.

## Reproducibility Boundary

Sweep enumeration must be deterministic. Parameter values must be serialized
consistently. The same sweep specification and same code/data state should
produce the same point identities and output structure.

Future implementation must not rely on implicit environment discovery beyond
existing local automation boundaries. It must not use nondeterministic ordering.

## Relationship To Batch Manifests

Future sweep design may produce or consume batch-compatible manifest material.
WP-12p does not modify `tools/research_automation/batch_manifest.py`.

V1 should avoid making a sweep specification a thin accidental wrapper over a
batch manifest without explicit rationale. If mapping to batch manifest
material is needed, the mapping must preserve sweep point identity and
parameter metadata.

## Relationship To Local Batch Runs

Future sweep execution should reuse existing local batch-run mechanics rather
than creating a parallel runner if feasible. WP-12p does not modify
`tools/research_automation/local_batch_runner.py`.

Each sweep point should flow through existing local validation and persistence
boundaries.

## Relationship To Local Run Registry

Future sweep outputs should land in or be indexed by the existing local
registry chain if separately implemented. WP-12p does not modify
`tools/research_automation/local_run_registry.py` or
`tools/research_automation/local_run_registry_validation.py`.

Registry entries remain local-only, research-only, non-authoritative, and
no-committed-evidence.

## Relationship To Future Monte Carlo / Robustness Work

Monte Carlo is a future special case of sweep-like enumeration over seeds or
perturbations. It is explicitly deferred.

WP-12p must not design Monte Carlo-specific semantics into v1. Future Monte
Carlo requires separate architecture authorization.

## Relationship To Future Dashboards

Dashboards are deferred. WP-12p does not create visualization surfaces,
dashboard data, dashboard backend behavior, or dashboard authority.

A dashboard should consume mature local outputs only in a later tranche with
separate authorization.

## Relationship To Future Agents / Orchestration

Agents and orchestration are hard-deferred. WP-12p does not authorize agents
that pick parameters, decide ranges, interpret outputs, control jobs, or manage
sweep execution.

The human remains the sweep specification author and initiator.

## Relationship To Future Evidence Bridge

Evidence bridge work is hard-deferred.

Sweep outputs do not become EXP, REP, OL, REC, LCH, registry, advisory, shadow,
summary, canonical evidence, or committed evidence. No automatic promotion may
be based on sweep results.

Any future bridge from local sweep outputs to evidence artifacts requires a
separate explicit architecture decision and package authorization.

## Forbidden Inference And Authority Boundaries

Future parameter sweep work must explicitly forbid:

- optimizer framing;
- best parameter selection;
- ranking;
- scoring;
- recommendation;
- approval;
- promotion or demotion;
- readiness or lifecycle authority;
- policy action;
- runtime action;
- paper/live action;
- cross-segment inference;
- cross-candidate inference;
- cross-pipeline-version inference;
- automatic promotion into evidence artifacts.

## Operational Stop Rules

Future implementation must stop if:

- the sweep specification is ambiguous;
- the parameter grid is empty;
- parameter combinations duplicate;
- sweep point count exceeds the v1 bound;
- the research question cannot be expressed through the existing batch-run
  framework;
- implementation would require scheduler, daemon, queue, watcher, or trigger
  behavior;
- implementation would require Monte Carlo semantics;
- implementation would require dashboard, agent, evidence bridge, runtime,
  paper/live, OMS, risk, safe-mode, exchange/broker/order, protected-path, or
  downstream authority behavior.

## Likely WP-12q Vertical Slice, Non-Binding

WP-12q may be a Tier 2 or Tier 3 local implementation vertical slice if WP-12p
merges cleanly and is accepted.

WP-12q should implement the minimal parameter sweep mechanism per WP-12p, use
one small worked example against one research question, and produce validated
local registry entries through the existing WP-12d through WP-12o chain.

WP-12q is not authorized by WP-12p. It requires separate package drafting and
acceptance. WP-12p does not draft WP-12q.

## Parameter Sweep Tranche Definition Of Done

The non-binding Main 3.0 runway for this tranche is:

- WP-12p design committed with selected alternatives and rationale.
- WP-12q executes one sweep against one research question.
- WP-12r executes a second sweep with meaningfully different parameter shape.
- WP-12s closes, checkpoints, or stability-locks the tranche.

This is architecture planning only. It does not authorize WP-12q, WP-12r, or
WP-12s.

## Risks And Mitigations

Risk: sweep specification format coupling to batch manifest format. Mitigation:
keep sweep specification and batch manifest mapping conceptually separate until
a later implementation package chooses the exact v1 shape.

Risk: aggregation semantics drifting into interpretation. Mitigation: allow
only structural aggregation and non-interpretive counts, and explicitly forbid
best/winner/ranking/scoring/recommendation/approval/promotion/demotion/
readiness/lifecycle language as authority.

Risk: sweep size and registry growth. Mitigation: keep v1 intentionally small,
calculate point count before execution, and stop on excessive combinations.

Risk: reproducibility under sweep. Mitigation: require deterministic
enumeration, stable serialization, stable point IDs, no timestamps for identity,
and no nondeterministic ordering.

Risk: coupling to ambiguous research-question structure. Mitigation: v1 applies
only to questions already expressible through the existing local batch-run
framework, and future implementation must stop instead of guessing.

## Open Questions For Later Packages

Later packages must decide:

- exact local sweep spec file name and shape;
- whether a small helper should be library-only or have a CLI later;
- exact v1 point-count limit;
- exact output root layout;
- whether sweep aggregate output is one file or local registry indexing only;
- how failed or blocked sweep points are represented;
- how to support different parameter types;
- when to consider parallelism;
- when to consider Monte Carlo;
- when to consider dashboard consumption.

## Non-Claims

WP-12p creates no implementation, output, schema, validator, query-layer
exposure, CLI, result-store implementation, dashboard, agent, scheduler,
parameter sweep execution, Monte Carlo, evidence bridge, runtime, paper/live,
OMS, risk, safe-mode, exchange/broker/order, protected-path behavior, committed
evidence, or downstream authority.

WP-12p does not create optimizer authority, best-parameter authority, ranking
authority, scoring authority, recommendation authority, approval authority,
promotion authority, demotion authority, readiness authority, lifecycle
authority, policy authority, runtime authority, paper/live authority, or
evidence authority.
