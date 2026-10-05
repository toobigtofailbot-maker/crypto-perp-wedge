# Prefect Local JSON-Sweep Consumer Cutover

## Status and bounded scope

CPW-PREFECT-02 cuts over one consumer only:
`tools.research_automation.local_json_sweep_spec_loader.run_local_json_parameter_sweep`.
The operational call graph is human operator -> ad-hoc Prefect deployment run ->
self-hosted Prefect server -> process pool/worker -> `cpw-local-json-sweep` flow ->
contained `.cpw/active` paths -> the unchanged CPW JSON sweep helper and its
existing parameter-sweep, batch, dry-run, and local-registry implementation.

Before accepted merge, the direct helper remains the operational oracle and the
Prefect route is shadow proof. After accepted merge, the supported operational
invocation for this selected consumer is
`cpw-local-json-sweep/cpw-local-json-sweep-v1`; Prefect owns its operational
flow state and run history. The direct helper remains the implementation,
test, and rollback seam, not a simultaneous generic orchestration owner.

## Ownership and authority

| Concern | Owner after accepted cutover |
| --- | --- |
| Selected consumer invocation, queueing, worker execution, and run history | Prefect |
| JSON parsing, sweep/point identity, ordering, batch execution, dry-run behavior, registry, and local artifact meaning | Existing CPW research automation |
| Scientific identity, denominator, holdout/leakage/WFO/OOS, robustness, Search Governor, and promotion | CPW, unchanged |
| Canonical evidence and crossing authority | Existing CPW/human owners, unchanged |
| Approval, paper/live, runtime, risk, trading, and capital | Existing protected/human owners, unchanged |

Prefect operational IDs remain in Prefect history and do not enter CPW sweep,
point, dry-run, batch, registry, scientific, or canonical identities.

## Deployment and storage contract

- Flow: `cpw-local-json-sweep`, retries `0`, result persistence disabled.
- Deployment: `cpw-local-json-sweep-v1`, registered from an explicit local
  worktree with its version set to the exact Git commit SHA.
- Work pool: `cpw-research-local-process`, type `process`, concurrency limit `1`.
- First-cutover topology: one loopback self-hosted Prefect server using an
  isolated PostgreSQL validation database and one process worker with limit `1`.
- Schedules, triggers, autonomous dispatch, Prefect Cloud, and API keys: none.

Inputs resolve through `tools.research_storage.workspace.resolve_workspace_path`
under `.cpw/active/<spec-namespace>/<spec-artifact-path>`. Each output uses a
fresh `.cpw/active/prefect/local-json-sweep/<consumer-run-id>/` namespace with
only `sweep-output/` and `registry-output/`. Existing non-empty namespaces fail
before helper invocation and are never cleaned, overwritten, or recycled.

Prefect history is operational history, not CPW scientific or canonical truth.
The flow returns only a compact in-memory operational mapping and writes no
wrapper-specific result artifact. Direct-helper and Prefect execution must
produce the same recursive CPW artifact file set and exact bytes for the locked
four-point fixture.

## Cutover, rollback, and deferred work

Cutover occurs only after exact artifact parity, physical PostgreSQL/server/
deployment/worker proof, worker-off queue recovery, server-restart persistence,
fail-closed invalid/duplicate cases, full-release validation, mergeability,
Side exact-head acceptance, and Karl's separate merge decision.

If the selected route becomes unusable, stop new Prefect runs, retain Prefect
history, and explicitly restore the direct helper as a temporary human-operated
route using a fresh namespace. Never reuse partial output or operate both routes
as supported owners. Repair requires a separately valid same-scope package.

Inner batch-item orchestration, remaining-consumer migration, and global legacy
scheduler/run-state retirement are deferred. Stage 5B/autonomy, Hermes,
Research Memory, Search Governor/Optuna integration, paper/live/runtime, and
capital remain inactive and unauthorized. A remaining-consumer and legacy-
retirement assessment is required before any broader ownership claim.
