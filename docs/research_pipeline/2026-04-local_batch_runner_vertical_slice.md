# Local Batch Runner Vertical Slice (WP-12h / AUTO-07)

## Package Metadata

- Package label: WP-12h / AUTO-07.
- Package title: Local Batch Runner Vertical Slice.
- Package class: Tier 3 local automation infrastructure, narrow
  implementation slice.
- Effective base: refreshed `main` after merged WP-12g / AUTO-06.
- Implementation module: `tools/research_automation/local_batch_runner.py`.
- Test module: `tests/research_automation/test_local_batch_runner.py`.

WP-12h is the first narrow Tier 3 local batch runner vertical slice. It is
explicit authorization for AUTO-07 only.

## Objective

WP-12h implements one local in-process batch runner slice. It consumes explicit
caller-provided batch items, uses WP-12f batch manifest validation, calls WP-12d
local dry-run functionality only through an explicit local function path, and
writes local batch-run material only under a caller-provided output root.

The output root must already exist and be a directory. The runner does not
create the root or its parents.

## Implemented Local-Only Slice

The runner exposes one in-process API:
`run_local_batch(items, output_root, resource_limits, static_metadata=None)`.

The implementation uses local dataclasses only. They are implementation
structures, not repo-truth schemas:

- `LocalBatchItemResult`;
- `LocalBatchRunSummary`;
- `LocalBatchRunResult`.

The runner calls `build_batch_manifest(...)` first. If manifest validation
fails, it does not call `run_local_dry_run(...)`, does not create per-item
directories, and does not write a batch summary.

When manifest validation passes, it creates deterministic per-item output
directories under the caller-provided output root, calls `run_local_dry_run(...)`
once per item, and writes `local_batch_run_summary.json` under that output root.

Top-level item output directories may be created directly under the existing
output root. Nested item output directories are created only when their
immediate parent directory already exists. Missing item-directory parents are
recorded as blocked item results; the runner does not create those parent
directories.

## Non-Authoritative Boundary

WP-12h output material is local-only, research-only, and non-authoritative. It
creates no committed evidence artifact and no downstream authority.

Batch-run material is not an EXP, REP, OL, REC, LCH, registry, advisory,
shadow, summary, or evidence artifact. Any future conversion from local
batch-run material into committed evidence requires a separate explicitly
authorized package.

## Protected Runtime / Paper / Live Boundary

WP-12h creates no schema, validator, query-layer change, CLI, scheduler, daemon,
queue, watcher, trigger, result store, dashboard, agent, parameter sweep, Monte
Carlo, evidence bridge, config, dependency, data, runtime, paper/live, OMS,
risk, safe-mode, exchange/broker/order, or protected-path behavior.

It creates no policy, scoring, ranking, recommendation, approval, promotion,
demotion, readiness, lifecycle, paper/live, or runtime authority.

The runner must not inspect repo-wide state, current git branch, environment
variables, global config, network, live data, or system paths outside the
caller-provided output root. All runtime-relevant metadata comes from explicit
input or deterministic static metadata passed by the caller.

## Validation Summary

Package validation is expected to include targeted `tests/research_automation`
coverage, registry validators, all `v_integrity_*` query views, scoped
regression tests, full pytest, `git diff --check`, changed-file scope review,
and restricted-term semantic review.

Every integrity view must return `[]`.

## Future Authorization Boundary

Any next package requires separate authorization.

Future parameter sweeps, Monte Carlo, result stores, dashboards, agents,
schedulers, daemons, queues, watchers, triggers, CLIs, schemas, validators,
query-layer changes, configs, dependencies, data, evidence bridges, committed
artifacts, runtime, paper/live, OMS, risk, safe-mode, exchange/broker/order,
protected paths, or downstream authority remain outside WP-12h.
