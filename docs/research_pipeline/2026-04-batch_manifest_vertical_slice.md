# Batch Manifest Vertical Slice (WP-12f / AUTO-05)

## Package Metadata

- Package label: WP-12f / AUTO-05.
- Package title: Batch Manifest Vertical Slice.
- Package class: Tier 3 local automation infrastructure, narrow implementation
  slice.
- Effective base: refreshed `main` after merged WP-12e / AUTO-04.
- Implementation module: `tools/research_automation/batch_manifest.py`.
- Test module: `tests/research_automation/test_batch_manifest.py`.

WP-12f is the explicit narrow Tier 3 authorization for one local
research-only batch manifest helper.

## Objective

WP-12f implements manifest building and validation only. It accepts explicit
caller-provided local research batch items, validates the item set, validates
resource-limit categories, validates output-root containment, and emits an
in-memory manifest plus validation report.

When validation passes, the helper writes exactly two local JSON files under
the caller-provided output root:

- `batch_manifest.json`;
- `batch_validation_report.json`.

The output root must already exist and be a directory. Missing output roots or
file-path output roots fail validation with no writes and no parent creation.

## Dependency Basis

WP-12a installed the tiered automation-build operating model and blocked
paper/live, runtime, OMS, risk, safe-mode, execution, deployment, protected
paths, policy, scoring, ranking, and recommendation work unless later explicit
authorization exists.

WP-12b mapped the research automation architecture and identified batch
manifests as a future local research-only boundary.

WP-12c defined runner interface boundaries for research intent, run requests,
manifests, diagnostics, validation, reproducibility, and downstream handoffs.

WP-12d implemented one local dry-run runner vertical slice. WP-12f does not
call, wrap, import, or modify `run_local_dry_run(...)`.

WP-12e defined the batch manifest format design as documentation only. WP-12f
is the separate authorization for this minimal manifest-only implementation
slice.

## Implemented Local-Only Slice

The helper exposes one in-process API:
`build_batch_manifest(items, output_root, resource_limits, static_metadata=None)`.

The implementation uses local dataclasses only. They are implementation
structures, not repo-truth schemas:

- `BatchManifestItem`;
- `BatchResourceLimits`;
- `BatchManifest`;
- `BatchValidationReport`;
- `BatchManifestBuildResult`.

The helper derives deterministic batch and item identifiers from explicit
caller-provided input and static metadata. It does not inspect repo-wide state,
environment variables, global config, network, current git branch, live data,
or system paths outside the caller-provided output root.

## Non-Authoritative Boundary

Batch manifest outputs are local research-only material and non-authoritative.
They are not EXP, REP, OL, REC, LCH, registry, advisory, shadow, summary, or
evidence artifacts. They create no committed evidence artifact and provide no
downstream authority.

The validation report records that no execution occurred, no committed
evidence artifact was created, output paths were contained under the output
root, resource limits were checked, and protected runtime boundaries were not
contacted.

## What AUTO-05 Does Not Implement

AUTO-05 does not implement:

- batch execution;
- a call, wrapper, or modification around `run_local_dry_run(...)`;
- schema or validator behavior;
- CLI behavior;
- scheduler, queue, daemon, watcher, trigger, polling loop, or service
  behavior;
- parameter sweep;
- Monte Carlo or robustness engine;
- result store or run registry;
- dashboard;
- agent;
- evidence bridge;
- committed output or evidence artifact;
- config, dependency, or data change;
- runtime, paper/live, OMS, risk, safe-mode, exchange, broker, order,
  execution, deployment, or protected-path behavior;
- policy, scoring, ranking, recommendation, approval, promotion, demotion,
  readiness, or lifecycle authority.

## Future Authorization Boundary

Any future execution, result-store, dashboard, agent, parameter-sweep, Monte
Carlo, evidence bridge, or committed artifact package requires separate
explicit authorization with exact changed-file scope and validation evidence.

Future work must stop and escalate if safe implementation would require
protected runtime, OMS, reconciliation, risk, overlay, safe-mode, live-trading,
schema, validator, query-layer, config, dependency, data, scheduler, daemon,
queue, watcher, trigger, evidence artifact, or committed output behavior
outside a later approved package.
