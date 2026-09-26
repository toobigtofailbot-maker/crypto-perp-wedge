# Prefect P1/P2/P3 Acceptance Contract

## Status and package

- Package: `CPW-PREFECT-01`.
- Status: accepted only after all package validation passes and the PR merges.
- Prefect pin: exactly `3.8.6`.
- Proof Python: CPython `3.11.9`.
- Scope: acceptance/proof only; no orchestration cutover or operational ownership transfer.

## Proof environment

The acceptance suite uses the version-pinned, test-only
`prefect.testing.utilities.prefect_test_harness`. It starts a local subprocess
Prefect API server backed by a temporary SQLite database. It uses no Prefect
Cloud account, credentials, deployment, work pool, worker, schedule, or daemon.

The test harness is an internal Prefect testing utility accepted only for this
3.8.6 proof. It is not a production or downstream orchestration contract.
Later implementation packages must separately select and prove production
server, deployment, and worker surfaces.

## Accepted proof meanings

### P1 — concurrency and scientific accounting

Three synthetic trials execute as real concurrently submitted Prefect tasks.
Deterministic coordination forces operational completion order `T3, T2, T1`
while CPW reconstruction preserves declared order `T1, T2, T3`. The CPW
scientific-accounting validator confirms the exact three-trial denominator.
Separate flow runs produce identical normalized scientific payloads while their
Prefect flow/task identities differ.

Meaning: Prefect may own generic concurrent task mechanics without owning trial
identity, frozen ordering, status validity, or denominator meaning.

### P2 — pause/resume transport

A real flow enters a backend-visible `PAUSED` state through
`pause_flow_run(wait_for_input=...)`. Before resume, no downstream effect
exists. `resume_flow_run(...)` transports an arbitrary mapping; the existing
CPW `validate_prereg_approval` function alone determines semantic validity.
The valid engineering fixture continues exactly once. Wrong actor, packet hash,
scope, statement, missing timestamp, and broad-authority inputs all fail after a
real pause and create no continuation. A second resume creates no duplicate.

Meaning: Prefect owns pause/resume state and transport only. CPW continues to
own the exact actor, scope, statement, packet-hash, timestamp, and non-authority
semantics.

### P3A — retry versus scientific identity

One real Prefect task run fails its first attempt and succeeds on its second
through `retries=1` and runtime `run_count`. Both attempts retain one frozen CPW
scientific trial identity, and the CPW validator accepts one ledger row with
denominator one.

### P3B — fresh-flow recovery of a proof effect

Flow A exclusively creates one deterministic JSON effect in a caller-provided
pytest temporary directory and deliberately fails after creation. Fresh flow B
validates and reuses the exact existing bytes without rewriting them. A
same-identity conflicting payload fails closed without overwrite.

P3B is only a generic restart/recovery/idempotency proof over a noncanonical,
non-authoritative test effect. It is not acceptance of canonical persistence,
crossing, receipts, writers, or canonical idempotency and grants Prefect no such
authority.

## Owner matrix

| Mechanism or meaning | Owner after this package |
| --- | --- |
| Acceptance flow/task execution and concurrent scheduling | Prefect test backend |
| Acceptance retry and operational run state | Prefect test backend |
| Acceptance pause/resume transport and state | Prefect test backend |
| Scientific trial identity, ordering, status validity, and denominator | CPW research domain |
| Approval actor, scope, statement, hash, timestamp, and authority limits | CPW research domain |
| Search legality, budgets, holdout, and duplicate policy | Search Governor, unchanged |
| Canonical writes/evidence and candidate promotion | Existing CPW/human owners, unchanged |
| Runtime, paper/live, trading, OMS, risk, reconciliation, and capital | Existing protected owners, unchanged |

## Non-authority and runway

This package creates no deployment, work pool, worker, schedule, Cloud
connection, current-system cutover, canonical evidence, candidate claim,
promotion authority, paper/live authority, or capital authority. The lab
scheduler shell, `research_automation`, and `lab_pipeline` remain current and
unchanged until a later separately authorized cutover.

Successful merge makes `CPW-PREFECT-02` technically eligible for separate
drafting and authorization only. It does not authorize that package or any
consumer migration automatically.
