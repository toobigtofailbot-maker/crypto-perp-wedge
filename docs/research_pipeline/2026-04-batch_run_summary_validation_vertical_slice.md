# Batch Run Summary Validation Vertical Slice (WP-12j / AUTO-09)

## Package Metadata

- Package label: WP-12j / AUTO-09.
- Package title: Batch Run Summary Local Validation Vertical Slice.
- Package class: Tier 3 local automation infrastructure vertical slice.
- Effective base: refreshed `main` after merged WP-12i / AUTO-08.
- Implementation module: `tools/research_automation/batch_run_summary_validation.py`.
- Test module: `tests/research_automation/test_batch_run_summary_validation.py`.

WP-12j implements a minimal local validation helper only. It creates no formal
schema, registry validator, query-layer exposure, CLI, runner change, batch
manifest change, dry-run runner change, local batch runner change, config,
dependency, data, committed output, evidence artifact, result store, dashboard,
agent, scheduler, daemon, queue, watcher, trigger, parameter sweep, Monte
Carlo, evidence bridge, runtime, paper/live, OMS, risk, safe-mode,
exchange/broker/order, protected-path behavior, or downstream authority.

## Purpose

WP-12j validates caller-provided local `local_batch_run_summary.json` material
against the observed WP-12h summary shape and boundary markers.

Passing validation means only that the local summary matches the expected local
shape and non-authoritative boundary markers. Passing validation does not
authorize evidence creation, result-store consumption, dashboard consumption,
agent consumption, parameter sweep, Monte Carlo, scheduler, daemon, queue,
watcher, trigger, runtime, paper/live, OMS, risk, safe-mode,
exchange/broker/order, or protected-path behavior.

## Scope

The helper checks local summary mappings and caller-provided JSON files. It is
standard-library-only, local-only, research-only, and non-authoritative.

It may report missing fields, invalid status values, inconsistent counts,
non-local path references, invalid JSON, non-object JSON, and boundary marker
drift.

## Non-Goals

WP-12j does not:

- define a formal schema or stable public artifact grammar;
- create a registry validator or query-layer contract;
- call `run_local_batch(...)`, `run_local_dry_run(...)`, or
  `build_batch_manifest(...)`;
- create, mutate, promote, approve, recommend, rank, score, or lifecycle any
  EXP, REP, OL, REC, LCH, registry, advisory, shadow, summary, or evidence
  artifact;
- create result-store, dashboard, agent, scheduler, daemon, queue, watcher,
  trigger, parameter-sweep, Monte Carlo, evidence-bridge, runtime, paper/live,
  OMS, risk, safe-mode, exchange, broker, order, or protected-path behavior.

## Dependency Foundation

WP-12i documents `local_batch_run_summary.json` as local-only, research-only,
non-authoritative material after WP-12h. WP-12i also records that the observed
WP-12h dataclasses are implementation structures, not repo-truth schemas.

WP-12h writes `local_batch_run_summary.json` only under the caller-provided
output root after manifest validation passes. It writes local
non-authoritative batch-run material and creates no committed evidence
artifact.

## Validation Helper Interface

The implementation exposes:

- `BatchRunSummaryValidationReport`;
- `validate_local_batch_run_summary(summary)`;
- `validate_local_batch_run_summary_file(path)`.

The file helper reads JSON from a caller-provided path, writes nothing, creates
no directories, and delegates object payloads to the mapping helper. Invalid
JSON and non-object JSON return failed reports.

## Batch-Level Checks

The helper requires the observed WP-12h batch fields:

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

These checks are local shape checks only, not a formal schema.

## Item-Level Checks

The helper requires the observed WP-12h item fields:

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

These checks do not make an item a candidate state, strategy state, lifecycle
state, approval, recommendation, or evidence artifact.

## Count Consistency Checks

The helper checks:

- `item_count == len(item_results)`;
- `success_item_count == count(status == "succeeded")`;
- `failed_item_count == count(status == "failed")`;
- `blocked_item_count == count(status == "blocked")`;
- `skipped_item_count == count(status == "skipped")`.

## Status Semantics

Allowed item statuses are:

- `succeeded`;
- `failed`;
- `blocked`;
- `skipped`.

These statuses are local batch-run statuses only. They do not encode evidence
quality, candidate approval, strategy approval, readiness, promotion, demotion,
or lifecycle authority.

## Path / Reference Locality Checks

The helper rejects empty, absolute, or traversal path references for:

- `summary_file`;
- values in `manifest_files`;
- item `output_path`;
- values in item `dry_run_written_files`.

Path validation uses standard-library path handling and treats summary JSON
references as POSIX-style local relative references.

## Boundary Marker Checks

At batch and item level, the helper requires:

- `local_only is True`;
- `research_only is True`;
- `non_authoritative is True`;
- `creates_committed_evidence is False`.

The report itself also remains local-only, research-only, non-authoritative,
and no-committed-evidence.

## File Validation Helper Behavior

`validate_local_batch_run_summary_file(...)` reads the caller-provided file and
returns a failed report for expected invalid content. It does not write files,
create directories, call runners, inspect repo-wide state, or turn local output
into committed evidence.

## Test Coverage Summary

Focused tests cover valid successful, failed-item, and blocked-item summaries;
missing batch and item fields; count mismatch; unknown status; absolute and
traversal paths; authority marker drift; invalid JSON; non-object JSON; valid
file helper behavior; and a contained `tmp_path` integration check against
WP-12h-generated summary output.

## Local-Only / Non-Authoritative Boundary

The helper validates local summary material only. Passing validation is not
evidence authority, downstream authority, candidate approval, strategy
approval, paper/live readiness, recommendation, promotion, demotion, readiness,
or lifecycle authority.

## No Schema / Registry-Validator / Query-Layer Boundary

WP-12j does not create a formal schema, registry validator, central query-layer
surface, or downstream consumption interface. The helper is a local Python
utility for the observed WP-12h summary shape.

## No Result-Store / Dashboard / Agent Boundary

WP-12j creates no result store, run registry, dashboard, or agent. No such
surface may infer policy, scoring, ranking, recommendation, approval,
promotion, demotion, readiness, lifecycle, paper/live, runtime, OMS, risk,
safe-mode, exchange, broker, order, or protected-path authority from the
helper.

## Protected Runtime / Paper / Live Boundary

WP-12j does not contact or authorize runtime, paper/live, OMS, risk, safe-mode,
exchange, broker, order, scheduler, daemon, queue, watcher, trigger,
deployment, live-trading, or protected-path behavior.

## Stop / Escalation Rules

Future work must stop and escalate if it would:

- treat validation as evidence, lifecycle, candidate, strategy, paper/live,
  recommendation, or downstream authority;
- create or modify schemas, registry validators, query-layer surfaces, CLIs,
  runners, configs, dependencies, data, committed outputs, or evidence
  artifacts outside explicit package scope;
- create result-store, dashboard, agent, scheduler, daemon, queue, watcher,
  trigger, parameter-sweep, Monte Carlo, evidence-bridge, runtime, paper/live,
  OMS, risk, safe-mode, exchange, broker, order, deployment, or protected-path
  behavior;
- create policy, scoring, ranking, recommendation, approval, promotion,
  demotion, readiness, or lifecycle authority.

## Non-Claims

WP-12j creates no:

- formal schema;
- registry validator;
- query-layer contract;
- evidence authority;
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
- policy, scoring, ranking, recommendation, approval, promotion, demotion,
  readiness, lifecycle, paper/live, runtime, or downstream authority.
