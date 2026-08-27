# WP-HERMES-H3-1-FIRST-ASK-AND-ACT-01

## Package State

- Title: Hermes H3-1 First Real A1 Read-Only Ask-and-Act
- Branch: `claude/hermes-h3-1-first-action-acfd72`
- Locked base: `08abff2ac2f368f603f217cce7867eb78a4dfa8b` (merge of PR #711 / BROKER-3),
  confirmed by read-only refresh to contain the BROKER-3 merge before build.
- Implementation and exact T3 full-release evidence head:
  `39290f76fb87df5416326579efcacad70906f451`
- Final review head: the documentation-only commit containing this fragment. A
  commit cannot embed its own content-derived SHA; the exact immutable PR head is
  recorded in the pull request and in the execution report after this commit.
- Package class: T3 authority-executing / first-real-side-effect crossing
- Result: the first real Hermes ask-and-act action is built and held for Side's
  exact-head review. It is a single bounded read-only diagnostic executed through
  the independently-proven broker on Karl's exact per-action approval. Zero
  mutation of repo, canonical, or any protected surface.

H3-1 registers the first — and structurally the only permitted — dispatch-capable
production action and runs it through the unchanged BROKER-1/2/3 loop end to end:
`verify -> reserve -> burn -> project -> read-only dispatch -> read -> audit`. The
one real effect is a bounded, deterministic, read-only summary of committed
`docs/status_entries/WP-HERMES-*.md` evidence at the bound repo SHA, plus one inert
external result-record write. No repo, canonical, or protected surface is mutated.

## Changed Files

The final package is limited to these authorized paths:

- `tools/hermes/broker/registry.py` (modified — read-only lock + one production action)
- `tools/hermes/broker/h3_readonly.py` (new — action model, projection, result model)
- `tools/hermes/broker/adapters/__init__.py` (new)
- `tools/hermes/broker/adapters/readonly_repo_evidence.py` (new — the read-only adapter)
- `tools/hermes/broker/readonly_result_store.py` (new — inert external result retention)
- `tools/hermes/broker/readonly_dispatch.py` (new — H3-1 dispatch orchestration)
- `tools/hermes/broker/signing.py` (new — WYSIWYS approval signing)
- `tests/test_hermes_h3_1_readonly.py` (new — focused unit)
- `tests/test_hermes_h3_1_readonly_postgres.py` (new — physical PostgreSQL)
- `tests/test_hermes_broker_verification.py` (modified — recursive static boundary,
  one-production-entry assertion)
- `tests/test_hermes_broker_dispatch.py` (modified — one-production-entry assertion)
- `docs/status_entries/WP-HERMES-H3-1-FIRST-ASK-AND-ACT-01.md` (new)
- `docs/project_status.md` (modified)

BROKER-1/2/3 production and migration files (`models.py`, `crypto.py`,
`verification.py`, `reservation.py`, `dispatch.py`, `dry_run_adapter.py`,
`projection.py`, `store.py`, `state.py`, `retention.py`, `serialization.py`,
`acceptance.py`, `migrations.py`, `migrations/0001_broker_authority.sql`,
`migrations/0002_broker_dry_run_dispatch.sql`) are byte-for-byte unchanged from the
locked base, confirmed by `git diff --stat`. `requirements.txt` /
`requirements.lock.txt` are unchanged; no dependency was added. No new migration is
introduced: the existing durable state/audit schema already carries the full closed
eight-state lifecycle, arbitrary `action_type`/`adapter_id` strings, generic
canonical audit, global nonce burn, and public-key-only trust that H3-1 needs.

## Action / Registry / Adapter Contract

One real, production, read-only A1 action defined in `h3_readonly.py`:

- action type: `h3_1.readonly.repo_evidence_summary_v1`
- production registry version: `h3-1-readonly-registry-v1`
- adapter id: `h3-1-readonly-repo-evidence`
- adapter version: `1.0.0`
- affected domain: `bounded_investigation` (never an A0 domain)

`production_registry()` now returns exactly this one entry. `RegistryEntry` is
locked so the registry cannot express anything more dangerous than a read-only
action: every entry must be `read_only=True` (a mutating action can never be
registered at all), and an entry is exactly one of `proof_only` (non-dispatching)
or `dispatch_capable` (real, read-only) — never both, never a dispatch-capable
proof, never dispatch-capable without read-only. A1 is still required and A0
domains are still absent. The one real entry is `dispatch_capable=True`,
`proof_only=False`, `read_only=True`, and carries no callable, endpoint, command,
network, or file path (the adapter is selected by fixed identity, not stored in the
entry).

The action model `H3ReadonlyExecutableAction` subclasses the unchanged BROKER-1
`ExecutableAction`, requires `authority_class=A1` and `human_authored=True`, fixes
the target to `docs/status_entries`, fixes the scope operation, and bounds the
parameters (`filename_prefix`, `filename_suffix`, `max_files<=512`,
`max_file_bytes<=2_000_000`). Extra/unknown fields fail closed at strict model
validation; a wrong `action_type` literal, wrong evidence root, or prose/prepared
plan is rejected before projection (Lock 20).

## What-You-See-Is-What-You-Sign (WYSIWYS)

`signing.py` makes `human_authored=true` a real cryptographic binding.
`build_wysiwys_surface(action, claim_payload)` fails closed unless the claim
exactly binds the action (action SHA-256, all lineage ids/hashes, scope digest,
bounds, timeout, A1), then exposes the exact canonical executable-action bytes and
their SHA-256 and the exact Ed25519 signing-message bytes and their SHA-256.
`sign_wysiwys_surface(surface, private_key)` signs exactly those bytes and re-proves
that `approval_signed_bytes(signed) == surface.signing_message_bytes`, that the
hash matches, and that the signature verifies. Hash-equality holds end to end:

```
surface.action_sha256 == broker_sha256(action)
                      == claim.payload.executable_action_sha256
                      == projection.executable_action_sha256
                      == dispatch_completed audit executable_action_sha256
                      == result_record.executable_action_sha256
surface.signing_message_bytes == approval_signed_bytes(signed_claim)
```

A one-field tamper after signing changes the action hash, so the signed claim no
longer binds it and the broker rejects with `action_hash_mismatch` before dispatch.
The private key is supplied only at signing time and is never stored, logged, or
returned; the broker holds only the public key.

## Fixed Typed Projection and Dispatch Identity

`build_h3_readonly_projection(...)` produces one immutable `H3ReadonlyProjection`
from exact typed fields only. `H3ReadonlyProjectedParameters` is a closed schema of
exactly `evidence_root_relpath`, `filename_prefix`, `filename_suffix`, `max_files`,
`max_file_bytes`, and `operation`; there is no `**dict`/metadata/kwargs passthrough.
Projection fails closed on an unknown action type, wrong registry version, or wrong
adapter id/version; A0 fails at BROKER-1 materialization/verification before
projection. `derive_dispatch_id(projection)` derives a deterministic `BROKER-DIS-`
identity from the reservation id, action SHA-256, nonce, action type, adapter
id/version, and projection SHA-256, with no uuid/clock/process/environment input.

## Structurally Read-Only Adapter

`adapters/readonly_repo_evidence.py` performs only read operations. It enumerates
committed `docs/status_entries/WP-HERMES-*.md` at the bound repo SHA (the working
tree is pinned to the bound SHA by the unchanged BROKER-1 `repo_sha ==
current_repo_sha` gate; the adapter trusts that gate and never spawns a child
process or touches git objects), reads each matched regular file read-only
(`O_RDONLY`) with a symlink/reparse guard, a path-escape guard, and a per-file byte
cap, and returns a deterministic `H3ReadonlyResultRecord` (per-file relpath, byte
size, SHA-256; count; total). A count-cap or byte-cap breach returns a deterministic
`failed` record; a structural safety breach raises and fails closed. The record
always asserts `mutation_side_effect=false`, `protected_surface_touched=false`,
`network_access=false`, `child_process_spawned=false`, and
`wrote_repo_or_canonical=false`.

Adversarial read-only proof: an AST test asserts the adapter imports only
`__future__`, `hashlib`, `os`, `stat`, `pathlib`, and the local `h3_readonly`
module (the allowlist alone excludes every network/subprocess/dynamic module), and
that no concrete write/exec/mutation call (`os.system(`, `O_WRONLY`, `O_CREAT`,
`O_TRUNC`, `.write(`, `.unlink(`, `.rename(`, `.mkdir(`, `os.remove(`, `shutil.`)
appears anywhere in the source. A runtime test proves the repo evidence bytes and
mtimes are unchanged after a read and that no file is created. The static broker
boundary scan was tightened to recurse into the adapters subpackage, so the adapter,
the result store, the projection, and the signing module are all covered and none
contains a globally-prohibited capability, `psycopg`, `reserve(`, or `dispatch(`.

## Inert Result Retention, Crash-Safety, and Reconcile

`readonly_result_store.py` writes the single result record to a stable root that
must be *outside* the repository and every worktree, with exclusive-create
no-overwrite semantics and a symlink/reparse guard — proving the read-only action
writes nothing inside the repo. `readonly_dispatch.py` reuses the unchanged BROKER-2
`BrokerReservationService` and durable store: it commits the `dispatch_requested`
audit and the `reserved -> dispatched` transition before any adapter read, then
reads once, then writes the result record once, then commits
`dispatch_completed`/`dispatch_failed` with the result record id, SHA-256, and
retention path bound into the audit evidence. A process end between the
dispatch-request commit and finalization leaves a durable burned nonce,
`state=dispatched`, a `dispatch_id`, a `dispatch_requested` event, no completion
event, and no result file. `reconcile_stranded_dispatch(...)` explicitly classifies
`dispatched -> reconcile_required`, invokes no adapter read, writes no result, and
never unburns or reissues the nonce. There is no background worker, poller,
scheduler, Prefect flow, or automatic recovery loop.

## Result Contract

`BrokerReadonlyDispatchResult` allows only `completed`, `failed`,
`reconcile_required`, and `rejected`, always states `mutation_side_effect=false` and
`protected_surface_touched=false`, requires a result-record binding on a fresh
completion, and carries no order id, exchange response, external/Prefect task id, or
runtime payload.

## Physical Read-Only Evidence (real isolated PostgreSQL 17.10)

Focused physical proofs in `tests/test_hermes_h3_1_readonly_postgres.py` against a
temporary isolated loopback-only PostgreSQL 17.10 cluster on a non-default local
port with database `hermes_broker_test`, created outside the repository/worktree via
`HERMES_BROKER_TEST_DSN` (no password or full DSN recorded here):

- Full completed loop with the real WYSIWYS-signed claim: valid A1 verified and
  reserved, one nonce burn, committed `dispatch_requested`, exactly one read-only
  adapter invocation, exactly one inert result-record file, `dispatch_completed`,
  terminal `completed`, audit order
  `claim_submitted, claim_verified, nonce_reserved, dispatch_requested, dispatch_completed`,
  one reservation / one burn, the audited action SHA-256 equal to the signed and
  recomputed action SHA-256, and the repo evidence tree unchanged.
- Single-use replay: exact replay returns the same terminal identity with
  `idempotent_existing=true`, no second read, no second `dispatch_requested`, no
  second burn, and no second result file.
- Valid-signature A0 adversary: rejected `a0_forbidden` with zero reservation,
  burn, dispatch event, adapter read, or result file; A0 never reaches projection.
- Direct prose/prepared-plan input: rejected before dispatch with no dispatch event,
  no read, and no result file.
- Conflicting action on the burned nonce: rejected `nonce_already_reserved` with no
  `dispatch_requested` and no adapter read for the loser.
- Crash / stranded / reconcile: a crashing read leaves durable `dispatched` with a
  burned nonce, no terminal event, and no result file; a fresh store/service
  explicitly classifies `dispatched -> reconcile_required` once with no adapter
  read; the full replay after reconcile invokes no read, creates no second
  `dispatch_requested`, and re-burns nothing.

## Key Custody

Software Ed25519 key, generated outside the repository. The private key is supplied
only at signing time and never committed, imaged, tracked, placed in broker config,
or given to Hermes; the broker holds only the public key in `broker_trusted_key`
(`fixture_only=false` for the production helper). Hardware custody (HSM/Yubikey) is
recorded as required before any future *mutating* action; it is not required for
this read-only action.

## Validation Evidence

- Focused unit (`tests/test_hermes_h3_1_readonly.py`): 19 passed, 0 skipped.
- Focused PostgreSQL (`tests/test_hermes_h3_1_readonly_postgres.py`): 6 passed,
  0 skipped.
- Combined Hermes broker + proposals + prepare + deployment suites with the DSN set
  (crypto, retention, verification, reservation, postgres, dispatch,
  dispatch-postgres, h3-1, h3-1-postgres, prepare, proposals, deployment-contract):
  230 passed, 0 skipped.
- `python -m compileall`, `ruff check`, and `ruff format --check` pass on all
  changed files; `git diff --check` is clean.

Exact T3 full-release at implementation head
`39290f76fb87df5416326579efcacad70906f451`:

```text
python tools/dev/verify.py --validation-preset full-release --full-pytest-sharded --pytest-shard-profile full-release-balanced-v1 --json
```

`overall_status=pass` with an empty `failures` list. Profile
`full-release-balanced-v1` version 1, 48 shards, 4 parallel workers, 1,800-second
per-shard timeout. Assignment manifest
`sha256:5a6a77707cecfad4505a50e52ba4aff9137318bcb00c424adfe10dec12d734e7`. All 180
discovered tracked test files were assigned and executed exactly once under
exclusive isolation: 180 discovered, 180 assigned, 180 unique, zero missing,
duplicate, untracked, or not-run. `exact_coverage`, `all_shards_selected`,
`all_selected_shards_executed`, `all_shards_complete`, and `all_shards_passed` are
all true; the slowest shard was shard 41 at 1,251.188 seconds. The required broker
PostgreSQL tests were unskipped — shard 10 executed
`tests/test_hermes_broker_dispatch_postgres.py` in 105.547 s, shard 11 executed
`tests/test_hermes_broker_postgres.py` in 57.328 s, shard 12 executed
`tests/test_hermes_broker_reservation.py` in 24.344 s, and shard 17 executed the new
`tests/test_hermes_h3_1_readonly_postgres.py` in 33.000 s — runtimes only reachable
with the DSN present and the physical tests running. The tracked-file count rose from
178 (BROKER-3) to 180, exactly the two new H3-1 test files.

## The Two Gates and Next Step

1. Side exact-head review before merge. Side is offline; the built package is opened
   ready-for-review and held, and does not merge until Side performs the independent
   exact-head T3 review (as with BROKER-1/2/3). If Side is unavailable at merge time
   the package stays draft/held; it is not self-merged.
2. Karl exact per-action approval before first execution. Building and merging the
   capability is not executing it. The first real run requires Karl to sign the exact
   action via the WYSIWYS flow and the broker to verify that exact signed hash. Main
   confirms the WYSIWYS binding and read-only proof, then surfaces the exact canonical
   action bytes and SHA-256 to Karl for signing.

No A0 action, no second real action, no A2 standing authority, no H4, no Prefect
(BROKER-4 stays separate), no protected/canonical/mutation/network/subprocess path,
and no auto-execution are introduced.
