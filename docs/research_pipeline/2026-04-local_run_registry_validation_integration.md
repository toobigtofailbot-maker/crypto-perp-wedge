# Local Run Registry Validation Integration (WP-12o / AUTO-14)

## Package Metadata

- Package label: WP-12o / AUTO-14.
- Package title: Local Run Registry Validation Integration.
- Package class: Tier 3 local automation integration slice.
- Effective base: refreshed `main` after merged WP-12n / AUTO-13.
- Implementation module: `tools/research_automation/local_run_registry.py`.
- Test module: `tests/research_automation/test_local_run_registry.py`.

## Purpose

WP-12o integrates the WP-12n local registry validation helper into the WP-12m
`build_local_run_registry(...)` success path before writing
`local_run_registry.json`.

Passing validation means only that local registry material matches the expected
local shape and boundary markers. It does not create repo truth, committed
evidence, a formal schema, a central query-layer contract, evidence authority,
or downstream authority.

## Scope

The package modifies the local registry builder and its focused tests, creates
this integration document, and updates `docs/project_status.md` with a narrow
branch-state entry.

The builder still reads only explicit caller-provided local output roots and
writes only `local_run_registry.json` under an existing caller-provided
registry output root.

## Non-Goals

WP-12o does not create schemas, tools.registry validators, query-layer
exposure, CLI behavior, configs, dependencies, data files, committed output,
evidence artifacts, dashboards, agents, schedulers, daemons, queues, watchers,
triggers, parameter sweeps, Monte Carlo behavior, evidence bridges, runtime
behavior, paper/live behavior, OMS behavior, risk behavior, safe-mode behavior,
exchange/broker/order behavior, protected-path behavior, policy, scoring,
ranking/recommendation, approval, promotion, demotion, readiness, lifecycle,
or downstream authority.

## Dependency Foundation

WP-12m added `tools/research_automation/local_run_registry.py`, which builds
one local `local_run_registry.json` under an existing caller-provided registry
output root.

WP-12n added `tools/research_automation/local_run_registry_validation.py`,
which validates caller-supplied WP-12m local registry material and returns a
`LocalRunRegistryValidationReport`.

## Integration Behavior

`build_local_run_registry(...)` now builds records and the final registry
payload before writing, then validates that in-memory payload with
`validate_local_run_registry(...)`.

The builder writes `local_run_registry.json` only when that validation report
passes.

## Result Object Update

`LocalRunRegistryResult` now includes:

```python
registry_validation_report: LocalRunRegistryValidationReport | None
```

Pre-payload failures return `None`. Registry-payload validation success or
failure returns the corresponding report.

## Successful Write Behavior

On success, the builder returns the sorted records, the passing validation
report, the registry file path, and the same `written_files` mapping as WP-12m.

`local_run_registry.json` remains the only written file.

## Validation-Failure Behavior

If final payload validation fails, the builder writes no
`local_run_registry.json`, returns no written files, returns the failed
validation report, copies the report failure reasons into the result, and marks
`protected_boundary_preserved=False`.

The local-only, research-only, non-authoritative, and no-committed-evidence
markers remain preserved on the result.

## Pre-Payload Failure Behavior

Invalid registry output roots, empty source roots, missing source roots,
unrecognized source roots, ambiguous source roots, and source indexing failures
continue to write nothing and return `registry_validation_report=None`.

These failures occur before a final registry payload exists.

## Import-Cycle Avoidance

`local_run_registry_validation.py` imports constants from
`local_run_registry.py`.

WP-12o avoids a runtime circular import by using `TYPE_CHECKING` for the report
type and importing `validate_local_run_registry(...)` inside
`build_local_run_registry(...)` only after the final registry payload has been
built.

## Registry JSON Shape Preservation

WP-12o does not add top-level fields to `local_run_registry.json`.

The validation report is returned in memory on `LocalRunRegistryResult`; it is
not written as a separate file.

## Determinism

WP-12o adds no timestamps, UUIDs, filesystem-wide search, or nondeterministic
ordering.

The existing deterministic registry payload and record ordering remain the
write input when validation passes.

## Test Coverage Summary

Tests cover successful validation-report return, exact single-file registry
write behavior, preserved registry JSON shape, pre-payload failure behavior
with no validation report, forced final validation failure with no write, and
contained `tmp_path` writes.

Existing WP-12m local registry tests and WP-12n validation tests remain in
place.

## Local-Only / Non-Authoritative Boundary

WP-12o integrates a local validation helper into a local registry builder only.
The registry output remains local-only, research-only, non-authoritative, and
no-committed-evidence output material.

The validation report does not turn local registry material into repo truth,
committed evidence, an artifact family, dashboard authority, agent authority,
or downstream authority.

## No Schema / Tools.Registry Validator / Query-Layer Boundary

WP-12o creates no formal schema, no tools.registry validator, no central
query-layer exposure, and no query-layer contract.

The JSON output remains helper output material only.

## No Dashboard / Agent / Scheduler Boundary

WP-12o creates no dashboard, dashboard backend, agent surface, scheduler,
daemon, queue, watcher, trigger, polling loop, job service, or agent control
surface.

## No Parameter Sweep / Monte Carlo Boundary

WP-12o creates no parameter sweep, parameter search, Monte Carlo, robustness
engine, simulation behavior, or downstream interpretation surface.

## No Evidence Bridge Boundary

WP-12o creates no bridge from local registry material to EXP, REP, OL, REC,
LCH, registry, advisory, shadow, summary, or evidence artifacts.

## Protected Runtime / Paper / Live Boundary

WP-12o does not contact or authorize runtime, paper/live, OMS, risk,
safe-mode, exchange, broker, order, execution, deployment, live-trading, or
protected-path behavior.

## Architecture Checkpoint After WP-12o

After WP-12o merges, the WP-12m/WP-12n/WP-12o local registry loop is complete
enough for a separate chat-level Main 3.0 architecture report-back and
next-direction decision.

WP-12o does not draft or implement that Main 3.0 report-back.

## Stop / Escalation Rules

Future work must stop and escalate if it would create schemas, tools.registry
validators, query-layer exposure, CLI behavior, configs, dependencies, data,
committed output, evidence artifacts, dashboards, agents, schedulers, daemons,
queues, watchers, triggers, parameter sweeps, Monte Carlo behavior, evidence
bridges, runtime behavior, paper/live behavior, OMS behavior, risk behavior,
safe-mode behavior, exchange/broker/order behavior, protected-path behavior,
policy, scoring, ranking/recommendation, approval, promotion, demotion,
readiness, lifecycle, or downstream authority.

## Non-Claims

WP-12o creates no formal schema, tools.registry validator, query-layer
contract, result store, dashboard authority, agent authority, scheduler
authority, parameter-sweep authority, Monte Carlo authority, evidence
authority, runtime authority, paper/live authority, OMS authority, risk
authority, safe-mode authority, exchange/broker/order authority,
protected-path authority, policy authority, scoring authority,
ranking/recommendation authority, approval authority, promotion authority,
demotion authority, readiness authority, lifecycle authority, or downstream
authority.
