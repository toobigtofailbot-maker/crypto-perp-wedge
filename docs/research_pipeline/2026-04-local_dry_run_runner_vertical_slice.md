# Local Dry-Run Runner Vertical Slice (WP-12d / AUTO-03)

## Package Metadata

- Package label: WP-12d / AUTO-03.
- Package title: Local Dry-Run Runner Vertical Slice.
- Package class: Tier 3 automation infrastructure, first implementation vertical
  slice.
- Effective base: refreshed `main` after merged WP-12c / AUTO-02.
- Implementation module: `tools/research_automation/local_dry_run_runner.py`.
- Test module: `tests/research_automation/test_local_dry_run_runner.py`.

This WP is the explicit narrow Tier 3 authorization for AUTO-03 only: one local
in-process dry-run runner vertical slice.

## Objective

WP-12d implements the first local research-only dry-run runner slice. It accepts
one explicit local research intent fixture from the caller, converts it into one
run request representation, produces one manifest representation, one output
bundle representation, and one validation/failure-accounting report.

The slice is intentionally small. It is a local implementation proof, not a
framework.

## Dependency Basis

WP-12a installed the tiered automation-build operating model and blocked PAPER,
LIVE, and Tier 4 work until later explicit authorization.

WP-12b mapped the future research automation architecture and identified
AUTO-03 only as a possible later implementation package after interface design.

WP-12c defined the experiment-runner interface boundary for research intent,
run requests, manifests, local dry-run outputs, diagnostics, validation,
reproducibility, and protected-boundary preservation. It did not implement
AUTO-03.

WP-12d is the separate authorization for the narrow AUTO-03 implementation
slice described here.

## Implemented Local-Only Slice

The runner exposes one in-process API:
`run_local_dry_run(intent, output_dir)`.

The caller supplies all research intent and static metadata. The runner derives
deterministic identifiers from that explicit input, writes only under the
caller-provided output directory, and returns the same structures in memory.

The output directory receives:

- `run_request.json`;
- `manifest.json`;
- `output_bundle.json`;
- `validation_report.json`.

These files are local dry-run output material only. They are not committed
evidence artifacts and have no execution authority.

## Boundary Shape

The local implementation structures are dataclasses, not repo-truth schemas.

The intent boundary contains caller-provided candidate context, evaluation
purpose, data references, timeframe, evaluation window, parameters, pipeline
version, and static metadata.

The run request boundary preserves the translated local instructions and marks
the request deterministic, local-only, and non-authoritative.

The manifest boundary preserves request identity, intent identity, static
metadata, output file names, and protected-boundary status.

The output bundle boundary preserves a tiny deterministic summary and
diagnostics. It records that no committed evidence artifact is created.

The validation report boundary records pass/fail state, failure reasons, and
checked protected boundaries.

## Non-Authoritative Evidence Boundary

Runner output material is not an EXP, REP, OL, REC, LCH, registry, advisory,
shadow, summary, or evidence artifact. This package creates no committed run
output and no result-store authority.

Any future conversion from runner output material into committed evidence would
require a separate explicitly authorized evidence bridge package with exact
changed files and validation.

## Protected Runtime / Paper / Live Boundary

AUTO-03 does not authorize batch execution, parameter sweeps, Monte Carlo,
result stores, dashboards, agents, evidence bridges, schedulers, daemons,
queues, paper/live, runtime, OMS, risk, safe-mode, exchange/broker/order paths,
configs, dependencies, schemas, validators, central query-layer files, or
committed evidence artifacts.

The runner must not inspect repo-wide state, environment variables, global
config, network, current git branch, live data, or system paths outside the
caller-provided output directory except for deterministic static metadata
explicitly passed in the intent/request or safely derived without side effects.

## What AUTO-03 Does Not Implement

AUTO-03 does not implement:

- CLI operation;
- batch execution;
- parameter sweeps;
- Monte Carlo or robustness testing;
- result store or run registry;
- dashboard surface;
- agent orchestration;
- evidence bridge;
- scheduler, daemon, queue, watcher, polling loop, or trigger;
- paper/live bridge;
- runtime, OMS, risk, safe-mode, exchange, broker, or order behavior;
- policy, scoring, ranking, recommendation, strategy approval, promotion,
  demotion, readiness, or lifecycle authority.

## Validation Summary

Package validation is expected to include targeted
`tests/research_automation` coverage, all registry validators, all
`v_integrity_*` query views, selected package-related tests, full pytest,
`git diff --check`, changed-file scope review, and a restricted-term semantic
scan.

Every integrity view must return `[]`.

## Future Options

Possible future packages remain non-authoritative and require separate
authorization. They may include a batch manifest format, parameter-sweep MVP,
result-store/run-registry design, or dashboard data surface only if they
preserve protected boundaries and define exact changed-file scope.

## Stop / Escalation Notes

Future work must stop and escalate if safe implementation would require
configs, dependencies, data, schemas, validators, central query-layer files,
committed evidence artifacts, runtime, paper/live, OMS, risk, safe-mode,
exchange/broker/order paths, schedulers, daemons, queues, policy, scoring,
ranking, recommendation, approval, promotion, demotion, readiness, or lifecycle
authority.
