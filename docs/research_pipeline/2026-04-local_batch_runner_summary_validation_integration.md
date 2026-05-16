# Local Batch Runner Summary Validation Integration (WP-12k / AUTO-10)

## Package Metadata

- Package label: WP-12k / AUTO-10.
- Package title: Local Batch Runner Summary Validation Integration.
- Package class: Tier 3 local automation infrastructure integration.
- Effective base: refreshed `main` after merged WP-12j / AUTO-09.
- Modified runner: `tools/research_automation/local_batch_runner.py`.
- Modified tests: `tests/research_automation/test_local_batch_runner.py`.

WP-12k integrates the WP-12j local batch-run summary validation helper into the
WP-12h local batch runner success path. It creates no formal schema, registry
validator, query-layer exposure, CLI, config, dependency, data, committed
evidence artifact, result store, dashboard, agent, scheduler, daemon, queue,
watcher, trigger, parameter sweep, Monte Carlo, evidence bridge, runtime,
paper/live, OMS, risk, safe-mode, exchange/broker/order, protected-path
behavior, or downstream authority.

## Purpose

WP-12h already writes `local_batch_run_summary.json` after manifest-valid local
batch runs. WP-12j added a local helper that validates observed WP-12h summary
shape and boundary markers. WP-12k connects those two surfaces so successful
summary-producing batch runs validate the just-built summary before persisted
summary output is written.

Passing validation remains a local integrity check only. It is not evidence
authority, lifecycle authority, candidate approval, strategy approval,
paper/live readiness, recommendation, promotion, demotion, or downstream
authority.

## Implementation Boundary

The local batch runner now exposes:

- `SUMMARY_VALIDATION_FILE_NAME = "local_batch_run_summary_validation.json"`;
- `LocalBatchRunResult.summary_validation_report`;
- successful writes of `local_batch_run_summary_validation.json` beside
  `local_batch_run_summary.json`.

On successful summary-producing runs, the runner builds the existing
`LocalBatchRunSummary`, validates `asdict(summary)` through the WP-12j helper,
and writes the summary plus validation report only if validation passes.

The existing summary JSON shape is preserved. The validation report is local
output material only and is not a committed evidence artifact.

## Failure Behavior

WP-12k preserves existing no-summary behavior for invalid output roots and
manifest validation failures. Those paths write no summary file, write no
summary validation report file, and return `summary_validation_report=None`.

If summary validation fails after a manifest-valid local batch run, the runner
returns the failed local validation report, writes no `local_batch_run_summary.json`,
writes no `local_batch_run_summary_validation.json`, and marks result-level
protected-boundary preservation as false. Manifest files may already exist
because manifest validation remains the earlier local step.

## Local-Only / Non-Authoritative Boundary

The summary validation report marks local-only, research-only,
non-authoritative, and no-committed-evidence status. The report does not turn
local batch output into EXP, REP, OL, REC, LCH, registry, advisory, shadow,
summary, or evidence artifacts.

The report does not authorize result-store, dashboard, agent, scheduler,
daemon, queue, watcher, trigger, parameter-sweep, Monte Carlo, evidence-bridge,
runtime, paper/live, OMS, risk, safe-mode, exchange, broker, order, deployment,
or protected-path behavior.

## Stop / Escalation Rules

Future work must stop and escalate if it would:

- treat a passing local summary validation report as evidence, lifecycle,
  candidate, strategy, paper/live, recommendation, or downstream authority;
- create or modify schemas, registry validators, query-layer surfaces, CLIs,
  configs, dependencies, data, committed outputs, or evidence artifacts outside
  explicit package scope;
- create result-store, dashboard, agent, scheduler, daemon, queue, watcher,
  trigger, parameter-sweep, Monte Carlo, evidence-bridge, runtime, paper/live,
  OMS, risk, safe-mode, exchange, broker, order, deployment, or protected-path
  behavior;
- create policy, scoring, ranking, recommendation, approval, promotion,
  demotion, readiness, or lifecycle authority.

## Non-Claims

WP-12k creates no:

- formal schema;
- registry validator;
- query-layer contract;
- CLI;
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
