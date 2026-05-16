# Local Run Registry Validation Slice (WP-12n / AUTO-13)

## Package Metadata

- Package label: WP-12n / AUTO-13.
- Package title: Local Run Registry Validation Slice.
- Package class: Tier 3 local automation validation slice.
- Effective base: refreshed `main` after merged WP-12m / AUTO-12.
- Implementation module: `tools/research_automation/local_run_registry_validation.py`.
- Test module: `tests/research_automation/test_local_run_registry_validation.py`.

## Purpose

WP-12n adds a minimal validation helper for WP-12m
`local_run_registry.json` material.

Passing validation means only that local registry material matches the expected
local shape and boundary markers. It does not create repo truth, committed
evidence, a formal schema, a central query-layer contract, evidence authority,
or downstream authority.

## Scope

The package creates one standard-library-only helper, one focused test module,
and this validation-slice document. It updates `docs/project_status.md` with a
narrow branch-state entry.

The helper validates caller-provided mappings and caller-provided JSON files
only.

## Non-Goals

WP-12n does not create a formal schema, tools.registry validator, query-layer
exposure, CLI behavior, configs, dependencies, data files, committed output,
evidence artifacts, dashboards, agents, schedulers, daemons, queues, watchers,
triggers, parameter sweeps, Monte Carlo behavior, evidence bridges, runtime
behavior, paper/live behavior, OMS behavior, risk behavior, safe-mode behavior,
exchange/broker/order behavior, protected-path behavior, policy, scoring,
ranking/recommendation, approval, promotion, demotion, readiness, lifecycle,
or downstream authority.

## Dependency Foundation

WP-12m added `tools/research_automation/local_run_registry.py`, which indexes
explicit caller-provided local dry-run and local batch-run output roots and
writes `local_run_registry.json` under an existing caller-provided registry
output root after validation passes.

WP-12m registry material is local-only, research-only, non-authoritative, and
no-committed-evidence output material.

## Validation Helper Interface

The public helper interface is:

```python
validate_local_run_registry(registry)
validate_local_run_registry_file(path)
```

The returned `LocalRunRegistryValidationReport` records pass/fail state,
failure reasons, record count, and boundary markers. The helper writes no
files, creates no directories, and does not call `build_local_run_registry`.

## Top-Level Registry Checks

The helper checks the WP-12m implementation and package identifiers, required
top-level fields, `record_count`, `records`, `failure_reasons`, boundary
markers, `protected_boundary_preserved`, and non-empty `checked_boundaries`.

`record_count` must equal the number of record mappings observed.

## Record-Level Checks

Each record must include the WP-12m record fields, including record identity,
source kind, package and implementation identifiers, output root, relative
paths, run or batch identifiers, validation state, boundary markers, source
file hashes, and notes.

Unknown extra fields are ignored. This helper is not a formal schema.

## Source-Kind Semantics

`local_dry_run` records must have a non-empty `run_id`, an empty `batch_id`,
and bool validation and protected-boundary fields. Failed dry-run records must
keep `protected_boundary_preserved=False`.

`local_batch_run` records must have a non-empty `batch_id`, an empty `run_id`,
and `validation_passed=True`. Protected-boundary state remains local
descriptive accounting only.

## Path-Reference Checks

`relative_paths` must be a non-empty mapping from non-empty string keys to
local relative POSIX path references.

Path references fail when they are empty, absolute, contain backslashes, use a
Windows drive prefix, or contain `..` traversal segments.

## Hash Checks

`source_file_hashes` must be a non-empty mapping. Its keys must exactly match
`relative_paths` keys.

Hash values must be 64-character hexadecimal SHA-256 strings. Lowercase and
uppercase hex are accepted.

## Boundary Marker Checks

The top-level registry and every record must preserve:

- `local_only=True`;
- `research_only=True`;
- `non_authoritative=True`;
- `creates_committed_evidence=False`.

For non-empty records, top-level `protected_boundary_preserved` must equal the
logical `all(...)` value across record protected-boundary states.

## File Validation Helper Behavior

`validate_local_run_registry_file(path)` reads exactly the caller-provided JSON
path and validates the decoded object.

It writes nothing, creates no directories, does not repair content, and does
not discover registry files by searching the filesystem.

## Failure Behavior

Expected invalid content returns a failed validation report with local
diagnostic strings. Invalid JSON, unreadable files, and non-object JSON return
failed reports instead of raising.

The helper does not mutate the input mapping.

## Test Coverage Summary

Tests cover valid builder-produced registry material, file-helper validation,
failed dry-run registry records, missing required fields, count mismatch,
unknown source kind, invalid batch validation state, dry-run boundary drift,
local-only and no-committed-evidence marker drift, invalid path references,
hash key mismatch, invalid hash values, invalid JSON, non-object JSON, and
contained `tmp_path` writes.

## Local-Only / Non-Authoritative Boundary

WP-12n validates local output material only. The validator does not turn
registry material into repo truth, committed evidence, an artifact family, a
dashboard backend, an agent surface, or downstream authority.

## No Schema / Registry-Validator / Query-Layer Boundary

WP-12n creates no formal schema, no tools.registry validator, no central
query-layer surface, and no query-layer contract.

The JSON output remains helper output material only.

## No Dashboard / Agent / Scheduler Boundary

WP-12n creates no dashboard, dashboard backend, agent surface, scheduler,
daemon, queue, watcher, trigger, polling loop, job service, or agent control
surface.

## No Parameter Sweep / Monte Carlo Boundary

WP-12n creates no parameter sweep, parameter search, Monte Carlo, robustness
engine, simulation behavior, or downstream interpretation surface.

## No Evidence Bridge Boundary

WP-12n creates no bridge from local registry material to EXP, REP, OL, REC,
LCH, registry, advisory, shadow, summary, or evidence artifacts.

## Protected Runtime / Paper / Live Boundary

WP-12n does not contact or authorize runtime, paper/live, OMS, risk,
safe-mode, exchange, broker, order, execution, deployment, live-trading, or
protected-path behavior.

## Likely Next Package After WP-12n

As a non-binding future option, WP-12o may integrate local registry validation
into `build_local_run_registry` output before writing.

WP-12n does not draft or implement WP-12o.

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

WP-12n creates no formal schema, tools.registry validator, query-layer
contract, dashboard authority, agent authority, scheduler authority,
parameter-sweep authority, Monte Carlo authority, evidence authority, runtime
authority, paper/live authority, OMS authority, risk authority, safe-mode
authority, exchange/broker/order authority, protected-path authority, policy
authority, scoring authority, ranking/recommendation authority, approval
authority, promotion authority, demotion authority, readiness authority,
lifecycle authority, or downstream authority.
