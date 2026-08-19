# WP-HERMES-BROKER-3-DRY-RUN-DISPATCH-01

## Package State

- Title: Hermes BROKER-3 Dry-Run Dispatch / Projection / Audit Proof
- Branch: `claude/hermes-broker-3-dry-run-cbf022`
- Locked base: `4a9774e2345c8399710610d6c2c56736d9d50461` (merge of PR #710 / BROKER-2)
- Implementation and exact T3 full-release evidence head:
  `853fddb8bc532e19b83ef356500286bd0eb96b42`
- Final review head: the documentation-only commit containing this fragment. A
  commit cannot embed its own content-derived SHA; the exact immutable PR head is
  recorded in the pull request and in the execution report after this commit is
  created.
- Package class: T3 authority-crossing / protected dispatch-boundary proof
- Result: BROKER-3 inert dry-run dispatch/projection/audit boundary complete; zero
  real side effect

BROKER-3 extends the durable BROKER-2 reserved boundary into an inert
`verify -> reserve -> burn -> project -> dry-run dispatch -> audit` loop driven by
one structurally inert no-op adapter. It creates no real adapter, no production
registry action, no dispatch-capable registry entry, no production signing
material, no Prefect path, no network/subprocess/file mutation, no runtime/paper/
live/OMS/risk/reconciliation/canonical behavior, and no downstream side effect.
BROKER-4, H3-1, and H4 are not started.

## Changed Files

The final package is limited to these thirteen authorized paths:

- `tools/hermes/broker/projection.py` (new)
- `tools/hermes/broker/dry_run_adapter.py` (new)
- `tools/hermes/broker/dispatch.py` (new)
- `tools/hermes/broker/migrations/0002_broker_dry_run_dispatch.sql` (new)
- `tools/hermes/broker/state.py` (modified)
- `tools/hermes/broker/store.py` (modified)
- `tests/test_hermes_broker_dispatch.py` (new)
- `tests/test_hermes_broker_dispatch_postgres.py` (new)
- `tests/test_hermes_broker_verification.py` (modified)
- `tests/test_hermes_broker_reservation.py` (modified)
- `tests/test_hermes_broker_postgres.py` (modified)
- `docs/status_entries/WP-HERMES-BROKER-3-DRY-RUN-DISPATCH-01.md` (new)
- `docs/project_status.md` (modified)

BROKER-1 production modules (`models.py`, `crypto.py`, `registry.py`,
`retention.py`, `serialization.py`, `verification.py`, `acceptance.py`) and the
BROKER-2 protected implementation files (`reservation.py`, `migrations.py`,
`migrations/0001_broker_authority.sql`) are byte-for-byte unchanged from the
locked base, confirmed by `git diff`. `requirements.txt` and
`requirements.lock.txt` are unchanged; no dependency was added. `registry.py` and
`production_registry()` are unchanged and `production_registry()` remains empty
(zero actions).

## Proof Action / Registry / Adapter Contract

BROKER-3 uses one proof-only, test-only-tooling identity implemented in
`projection.py`:

- action type: `broker3.proof.dry_run_noop_v1`
- proof registry version: `broker3-proof-registry-v1`
- adapter id: `broker3-dry-run-noop`
- adapter version: `1.0.0`

The proof action subclasses the strict BROKER-1 `ExecutableAction`, requires A1,
uses only `AffectedDomain.TEST_ONLY_TOOLING`, is `proof_only=True`, remains
`dispatch_capable=False` in the unchanged BROKER-1 registry model, and carries no
callable, endpoint, command, network, or file path. It lives in a separate proof
registry; `production_registry()` remains empty.

## Fixed Typed Projection

`build_dry_run_projection(...)` produces one immutable `DryRunProjection` from
exact typed fields only. `DryRunProjectedParameters` is a closed schema of exactly
`challenge`, `requested_dry_run_outcome`, `fixture_id`, and `operation`; there is
no `**dict` / metadata / kwargs passthrough. Extra action parameters fail closed
at strict model validation before projection. Projection fails closed on an
unknown action type, a wrong registry version, and a wrong adapter id or version.
A0 fails at BROKER-1 materialization/verification before projection. Prepared
payload objects and generic prose are rejected before projection. The projection
binds the executable action id/sha256, approval id, reservation id, single-use
nonce, action type, registry version, adapter id/version, the exact typed
projected parameters, the projection schema version
(`hermes_broker_dry_run_projection_v1`), the projection SHA-256, and `dry_run=true`
using the unchanged broker canonical JSON serializer.

## Deterministic Dispatch Identity

`derive_dispatch_id(projection)` derives `BROKER-DIS-<lowercase sha256 prefix>`
deterministically from the reservation id, executable action SHA-256, single-use
nonce, action type, adapter id/version, and projection SHA-256, using a versioned
identity schema. It uses no uuid, wall-clock, process, or environment input; the
same reserved projection always derives the same dispatch id, and a conflicting
identity fails closed at the durable store.

## Structurally Inert No-Op Adapter

`dry_run_adapter.py` implements exactly one pure deterministic function,
`dry_run_noop(projection)`, that accepts only the typed `DryRunProjection`, returns
a deterministic completed or failed dry-run result per the closed proof input, and
always states `downstream_side_effect=false`. It has no network, socket, HTTP,
child-process, shell, filesystem write, canonical writer, Prefect, Codex, Governor,
MCP, runtime/paper/live, OMS/risk/reconciliation, exchange/order/capital,
environment, clock, randomness, uuid, database, or retry surface. A focused AST
test asserts the adapter module imports only `__future__`, `typing`, `pydantic`,
and the local `models`/`projection` modules. Production code statically selects the
fixed no-op adapter; tests may monkeypatch the module-level function only to count
or simulate a crash.

## PostgreSQL Migration / State / Audit

- Migration: `0002_broker_dry_run_dispatch.sql`
- Migration SHA-256:
  `10a52397b01fbad3af30a21a7dc7484ba95b7433ab06ed6ca451fb7486e57791`
- `0001_broker_authority.sql` is unchanged; the checksum-locked runner discovers
  and applies `0002` unchanged.

`0002` extends the existing `hermes_broker` schema and creates no new table. It
adds nullable `dispatch_id` to `broker_action_state` and `broker_authority_audit`,
replaces the state and audit CHECK vocabularies with the final closed sets, adds
audit reason/dispatch-binding constraints, and replaces the action-state
transition guard. The BROKER-2 nonce and idempotency uniqueness constraints
(`uq_broker_reservation_single_use_nonce`,
`uq_broker_reservation_idempotency_key`) and the immutable-table guards are
preserved unchanged.

Final closed action-state vocabulary (exactly eight):
`submitted`, `verified`, `reserved`, `rejected`, `dispatched`, `completed`,
`failed`, `reconcile_required`.

Final DB-guarded transitions:

- `submitted -> verified`
- `submitted -> rejected`
- `verified -> reserved`
- `verified -> rejected`
- `reserved -> dispatched`
- `dispatched -> completed`
- `dispatched -> failed`
- `dispatched -> reconcile_required`

Terminal: `rejected`, `completed`, `failed`, `reconcile_required`. `dispatched`
requires `reservation_id` and `dispatch_id` and no reason; `completed` requires
`reservation_id` and `dispatch_id` and no reason; `failed` and
`reconcile_required` require `reservation_id`, `dispatch_id`, and a nonempty
reason; `reservation_id` and `dispatch_id` are immutable once set.

Final closed authority-audit vocabulary (exactly eight):
`claim_submitted`, `claim_verified`, `claim_rejected`, `nonce_reserved`,
`dispatch_requested`, `dispatch_completed`, `dispatch_failed`,
`reconcile_required`. `actor` remains exactly `broker`; audit stays canonical JSON
+ SHA-256 and append-only. The four dispatch-layer events require `dispatch_id`
and `reservation_id`; `dispatch_failed` and `reconcile_required` require a nonempty
reason; `dispatch_requested` and `dispatch_completed` reject a reason.

## Crash-Safe Ordering and Reconcile

The public entrypoint `BrokerDryRunDispatchService.dispatch_dry_run(...)` reuses
the unchanged BROKER-2 `BrokerReservationService`, then commits the
`dispatch_requested` audit and the `reserved -> dispatched` transition in one
transaction that completes before any no-op invocation, then invokes the fixed
no-op adapter exactly once, then commits the `dispatch_completed`/`dispatch_failed`
finalization. A process end between the dispatch-request commit and finalization
leaves a durable burned nonce, `state=dispatched`, a `dispatch_id`, a
`dispatch_requested` event, and no completion event. `reconcile_stranded_dispatch(...)`
is an explicit recovery classification that transitions
`dispatched -> reconcile_required` with reason `dry_run_dispatch_completion_unknown`,
invokes no adapter, performs no retry, and never unburns or reissues the nonce.
There is no background worker, poller, scheduler, Prefect flow, or automatic
recovery loop.

## Result Contract

`BrokerDispatchResult` allows only `completed`, `failed`, `reconcile_required`, and
`rejected`, always states `downstream_side_effect=false`, and carries no order id,
exchange response, external/Prefect task id, or runtime payload.

## Physical Dry-Run Evidence (real isolated PostgreSQL 17.10)

Focused physical proofs in `tests/test_hermes_broker_dispatch_postgres.py`:

- Full completed loop: valid A1 verified and reserved, one nonce burn, committed
  `dispatch_requested`, exactly one no-op invocation, `dispatch_completed`,
  terminal `completed`, audit order
  `claim_submitted, claim_verified, nonce_reserved, dispatch_requested, dispatch_completed`,
  one reservation / one burn, `downstream_side_effect=false`.
- Deterministic failed loop: same prefix, deterministic `dispatch_failed`,
  terminal `failed`, one reservation / one burn, no real side effect.
- Burned nonce never redispatches: exact replay returns the same terminal identity
  with `idempotent_existing=true`, no second no-op invocation, no second
  `dispatch_requested`, no second burn.
- Conflicting action on the burned nonce: rejected `nonce_already_reserved`, no
  `dispatch_requested`, no adapter invocation for the loser.
- Crash / stranded / reconcile: a monkeypatched crashing no-op leaves durable
  `dispatched` with a burned nonce and no terminal event; a fresh store/service
  explicitly classifies `dispatched -> reconcile_required` once with no adapter
  invocation and no retry.
- Reconcile terminal replay: replaying the full loop after `reconcile_required`
  invokes no adapter, creates no second `dispatch_requested`, and re-burns nothing.
- A0 valid-signature adversary: rejected `a0_forbidden` with zero reservation,
  burn, dispatch event, or adapter invocation; A0 never reaches projection or the
  adapter.
- Direct prepared-plan/prose input: rejected before dispatch with no dispatch event
  and no adapter invocation.
- DB transition enforcement: direct illegal transitions
  (`reserved -> completed|failed|reconcile_required`, `dispatched -> reserved`,
  `completed|failed|reconcile_required|rejected -> dispatched`) are rejected.
- DB audit closedness: unknown event type rejected; dispatch events require
  `dispatch_id`/`reservation_id`; `dispatch_failed`/`reconcile_required` require a
  reason; `dispatch_requested`/`dispatch_completed` reject a reason.
- Migration: `0001` then `0002` apply in order, rerun reports both already applied,
  modified bytes under either version are rejected, and no dispatch table exists.

## No-Real-Side-Effect / Boundary Proof

The static broker boundary test (`test_hermes_broker_verification.py`) scans the
whole broker package. It keeps every global prohibition (subprocess, `os.system`,
HTTP clients, Prefect, `src.runtime`/`src.execution`, `tools.canon_intake`,
dynamic import/eval/exec, `create_task`, `automatic_retry`) and the phase-aware
`psycopg`/`reserve(` owners, and adds a phase-aware `dispatch(` seam permitted only
in `dispatch.py` and `store.py`. The pure `projection.py` and `dry_run_adapter.py`
contain no `dispatch(`, no `psycopg`, and no forbidden capability. Focused unit
proofs (`test_hermes_broker_dispatch.py`) assert the exact proof registry identity,
the empty production registry, deterministic projection and canonical hash,
fail-closed rejection paths, deterministic no-op results with
`downstream_side_effect` literally `false`, the minimal adapter import surface,
deterministic dispatch-id derivation, the exact eight-value state and audit
vocabularies, and result closedness.

## Validation Evidence

PostgreSQL: retained official PostgreSQL 17.10 x64 binaries reused; a temporary
isolated loopback-only cluster on a non-default local port with database
`hermes_broker_test` was created outside the repository/worktree via
`HERMES_BROKER_TEST_DSN`. No password or full DSN is recorded here.

- Focused unit (`tests/test_hermes_broker_dispatch.py`): 17 passed, 0 skipped.
- Focused PostgreSQL (`tests/test_hermes_broker_dispatch_postgres.py`): 10 passed,
  0 skipped.
- Combined broker suite (crypto, retention, verification, reservation, postgres,
  dispatch, dispatch-postgres) with the DSN set: 97 passed, 0 skipped.
- Required broker PostgreSQL files rerun with skip reporting: 24 passed, 0 skipped.
- Adjacent suites: `test_execution_readiness.py` and `test_project_evidence_mcp.py`
  39 passed; `test_dispatch_authorization_reservation.py` and
  `test_dispatch_authorization.py` 177 passed, 5 skipped after one
  environment-only baseline failure was independently established and resolved
  (see below).
- `python -m compileall`, `ruff check`, `ruff format --check`, `git diff --check`,
  and `tools/dev/diff_scope_summary.py` all pass on the changed files.

Exact T3 full-release at implementation head
`853fddb8bc532e19b83ef356500286bd0eb96b42`:

```text
python tools/dev/verify.py --validation-preset full-release --full-pytest-sharded --pytest-shard-profile full-release-balanced-v1 --json
```

`overall_status=pass` with an empty `failures` list. Profile
`full-release-balanced-v1` version 1, 48 shards, 4 workers, 1,800-second per-shard
timeout. Assignment manifest
`sha256:4e0978f07b9f238d1a87fd03b21eb22f36a5e8889b5e96ef60a1029eae63c842`. All 178
discovered tracked test files were assigned and executed exactly once: 178
discovered, 178 assigned, 178 unique, zero missing, duplicate, untracked,
not-run, incomplete, or timed-out. `all_shards_selected`,
`all_selected_shards_executed`, `all_shards_complete`, and `all_shards_passed` are
all true; the slowest shard was shard 41 at 1,167.109 seconds. The required broker
PostgreSQL tests were unskipped: shard 10 executed
`tests/test_hermes_broker_dispatch_postgres.py` in 43.234 s, shard 11 executed
`tests/test_hermes_broker_postgres.py` in 48.328 s, and shard 12 executed
`tests/test_hermes_broker_reservation.py` in 23.391 s — runtimes only reachable
with the DSN present and the physical tests running.

## Environment-Only Baseline Disclosure

Before the local data directory was provisioned, one adjacent test,
`tests/test_dispatch_authorization.py::test_exact_post_kdauth_boundary_and_no_downstream_artifacts_created`,
failed with `1d dataset must be a regular non-symlink file`. This is a pre-existing
Windows worktree provisioning condition: the required 1d dataset lives under the
git-ignored `data/processed/**` tree, which `git worktree` does not populate. The
identical failure reproduces on the clean locked base
`4a9774e2345c8399710610d6c2c56736d9d50461` with zero BROKER-3 changes present, and
the test passes once the git-ignored local `data/` tree is provisioned into the
worktree. BROKER-3 changes no `tools/canon_intake` byte and no data byte. This is
an environment-only baseline condition, independent of BROKER-3, and was not
worked around by weakening any test.

## Implementation-Head / Final-Head Evidence

The full-release above ran at implementation head
`853fddb8bc532e19b83ef356500286bd0eb96b42`. This final status tail is
documentation-only and changes no production, test, or migration byte; every
code/migration/test blob at the final review head equals its blob at the
implementation head. Final-head smoke over the BROKER-3 focused unit, BROKER-3
PostgreSQL, BROKER-2 reservation/PostgreSQL, migration apply/already-applied, and
diff/scope checks provides publication evidence.

## Protected Boundary and Next Gate

BROKER-3 creates the inert dry-run dispatch proof only. It adds no Prefect, real
adapter, production registry action, production private key, signing UX,
exchange/order/capital action, runtime/paper/live action, OMS, risk,
reconciliation executor, canonical writer, or Codex/Governor invocation, and no
network/subprocess/file side effect. `production_registry()` remains empty.

BROKER-3 must merge at the exact Side-reviewed final PR head, and the merged
BROKER-3 report must be forwarded to Main, before any next package. BROKER-4,
H3-1, and H4 are not started; the first real A1 action still requires Karl's exact
approval and a separate Main-issued H3-1 capsule.
