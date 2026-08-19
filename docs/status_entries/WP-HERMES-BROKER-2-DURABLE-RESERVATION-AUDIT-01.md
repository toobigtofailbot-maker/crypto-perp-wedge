# WP-HERMES-BROKER-2-DURABLE-RESERVATION-AUDIT-01

## Package State

- Title: Hermes BROKER-2 Durable PostgreSQL Reservation / Nonce Burn / Authority Audit
- Branch: `codex/wp-hermes-broker-2-durable-reservation-audit-01`
- Refreshed base: `832e4332166bf2dc644f1b13b238c2b9024f3e09`
- Implementation and exact T3 evidence head:
  `57f7d7ca9ecee6d54bd677ba6c2794b29653acaf`
- Final review head: the documentation-only commit containing this fragment. A
  commit cannot embed its own content-derived SHA; the exact immutable PR head is
  recorded in [PR #710](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/710)
  and in the execution report after that commit is created.
- Package class: T3 authority-crossing durable broker-state package
- Result: BROKER-2 durable reservation/audit boundary complete; no dispatch

BROKER-2 stops at durable `reserved` or `rejected`. It creates no dispatch
request, dispatcher, callable adapter, adapter invocation, network/runtime side
effect, Prefect path, retry/reconciliation state, production signing material, or
BROKER-3 behavior. BROKER-3, BROKER-4, H3-1, and H4 are not started.

## Changed Files

The final package is limited to these ten authorized paths:

- `tools/hermes/broker/migrations.py`
- `tools/hermes/broker/migrations/0001_broker_authority.sql`
- `tools/hermes/broker/state.py`
- `tools/hermes/broker/store.py`
- `tools/hermes/broker/reservation.py`
- `tests/test_hermes_broker_postgres.py`
- `tests/test_hermes_broker_reservation.py`
- `tests/test_hermes_broker_verification.py`
- `docs/status_entries/WP-HERMES-BROKER-2-DURABLE-RESERVATION-AUDIT-01.md`
- `docs/project_status.md`

The existing BROKER-1 production files `models.py`, `crypto.py`, `registry.py`,
`retention.py`, `serialization.py`, `verification.py`, and `acceptance.py` remain
byte-for-byte unchanged from the refreshed base. `requirements.txt` and
`requirements.lock.txt` are unchanged; the already-pinned `psycopg[binary]==3.3.4`
dependency is reused.

At the locked base, the BROKER-1 static boundary test globally rejected the
literals `psycopg` and `reserve(` across all broker production modules. Side's
narrow correction made that test phase-aware without changing BROKER-1 behavior:
`psycopg` is permitted only in `migrations.py` and `store.py`, while `reserve(` is
permitted only in `store.py` and `reservation.py`. The complete original global
no-dispatch/no-runtime/no-dynamic-execution token set remains enforced across the
broker package. The corrected test passed before production mutation and the
complete BROKER-1 suite later passed unchanged.

## PostgreSQL Contract

- PostgreSQL test server: official PostgreSQL 17.10 x64 binaries installed
  outside the repository; temporary loopback-only, non-default-port cluster
- Isolated test database: `hermes_broker_test`
- Schema: `hermes_broker`
- Migration: `0001_broker_authority.sql`
- Migration SHA-256:
  `a771a5c9ec8e83bf54da4a4ad42cd87184eb0f29cb4fb141de823f98eda23c9d`
- First application: applied `0001_broker_authority`
- Second application: reported `0001_broker_authority` already applied
- Same-version changed bytes: rejected by checksum validation

The five locked logical tables are:

- `broker_approval`
- `broker_reservation`
- `broker_authority_audit`
- `broker_trusted_key`
- `broker_action_state`

`schema_migrations` is the broker-owned migration ledger, not an additional
logical authority table. Catalog inspection proved the five logical tables, the
migration ledger, the four immutable-table triggers, and the action-state
transition guard. No dispatch table exists.

The raw nonce burn is enforced by named global unique constraint
`uq_broker_reservation_single_use_nonce`. Derived action-hash-plus-nonce
idempotency is enforced by named constraint
`uq_broker_reservation_idempotency_key`. One approval may have only one durable
reservation.

The closed action-state vocabulary is exactly `submitted`, `verified`,
`reserved`, and `rejected`. The only DB-guarded transitions are:

- `submitted -> verified`
- `submitted -> rejected`
- `verified -> reserved`
- `verified -> rejected`

`reserved` and `rejected` are terminal. The closed authority-audit vocabulary is
exactly `claim_submitted`, `claim_verified`, `claim_rejected`, and
`nonce_reserved`. Approval, reservation, audit, and trusted-key rows reject
update/delete at the DB boundary.

`broker_trusted_key` is the sole BROKER-2 production source for trusted public
keys and revocation state. The loader selects the complete maximum
`registry_epoch`, rejects missing or mixed-version snapshots, materializes the
unchanged BROKER-1 `TrustedKeyRegistry`, and passes it to unchanged
`verify_approval(...)`. The table has no private-key column, the service accepts
no private key or caller-supplied trusted-key registry, and no private key is
stored in PostgreSQL or tracked repository state.

## Physical Reservation Evidence

- Normal A1 reservation committed exactly one reservation, one nonce burn, and
  one `nonce_reserved` event, then returned terminal `reserved` with
  `downstream_side_effect=false`.
- Exact same action hash plus exact same nonce returned the existing reservation
  with `idempotent_existing=true`; it created no second reservation, burn, event,
  or state transition.
- Two concurrent identical attempts converged on one physical reservation and
  one event. A repeated isolated race run also passed.
- Two concurrent different actions using one raw nonce produced exactly one
  `reserved` result and one `rejected / nonce_already_reserved` result at the
  named DB uniqueness boundary, with one physical reservation and one burn.
- Transaction-time expiry after BROKER-1 verification transitioned
  `verified -> rejected / expired_before_reservation` and produced no reservation
  or nonce burn.
- A test-only deferred constraint trigger forced reservation COMMIT failure. An
  independent reconnect proved durable state remained `verified`, with only
  `claim_submitted` and `claim_verified`, no reservation, no `nonce_reserved`, and
  a reusable nonce. Removing the trigger allowed exact resubmission to reserve
  once.
- A fresh store/service after a committed reservation returned the same durable
  reservation idempotently. A different action could not reuse the nonce,
  proving the burn survives process-equivalent reconnect/crash.
- Missing durable key state, revoked signer, and stale registry version all
  failed closed before reservation.
- A correctly Ed25519-signed retained A0 artifact returned
  `rejected / a0_forbidden` and produced no reservation or burn.

## Boundary Proof

AST and per-file scans found no subprocess, shell, HTTP/network client, Prefect,
dynamic import/eval/exec, canonical-dispatch, runtime, or automatic-retry import
or call in the new production surface. There is no dispatcher parameter, callable
adapter, dispatch return field, or downstream result. The bounded result contains
only reservation/rejection identity and always states
`downstream_side_effect=false`. Project-Evidence remains exactly eight MCP tools.

## Validation Evidence

- Focused BROKER-2 reservation tests: 8 passed, 0 skipped.
- Focused BROKER-2 PostgreSQL integration tests: 6 passed, 0 skipped.
- Additional isolated PostgreSQL concurrency rerun: 1 passed.
- BROKER-1 crypto/retention/verification suite: 66 passed.
- Adjacent dispatch-reservation suite: 65 passed, 4 existing Windows
  symlink/junction capability skips.
- Adjacent dispatch-authorization suite: 113 passed, 1 existing Windows symlink
  capability skip.
- Execution-readiness suite: 9 passed.
- Project-Evidence MCP suite: 30 passed.
- Compileall, Ruff check, Ruff format check, `git diff --check`, migration catalog
  checks, exact changed-file inspection, and forbidden-scope scans passed.

The successful exact T3 invocation at implementation head
`57f7d7ca9ecee6d54bd677ba6c2794b29653acaf` was:

```text
python tools/dev/verify.py --validation-preset full-release --full-pytest-sharded --pytest-shard-profile full-release-balanced-v1 --json
```

It used `full-release-balanced-v1` version 1, 48 shards, four workers, and the
unchanged 1,800-second per-shard timeout. Assignment manifest:
`sha256:0da94a4e99ee49302f2c68edaa4a368dc7becf741753b930068d05b9fff7456e`.
All 176 discovered tracked test files were assigned and executed exactly once:
176 assigned, 176 unique, zero missing, duplicate, untracked, incomplete, or
timed-out assignments. All 48 shards passed with 3,568 passed and 21 skipped;
the slowest was shard 41 at 1,135.625 seconds.

The first exact attempt stopped after the exclusive shard exposed nondeterministic
DuckDB 1.5.2 JSON timestamp inference in unchanged
`tests/test_research_query.py`: a whole-second format was inferred before reading
RP-0007's valid fractional timestamp. BROKER-2 changes no query-layer, Result
Population, or research-query test bytes. Fresh read-only reproduction could read
the affected views, and a clean retry of the exact unmodified full-release command
passed every shard. The failed attempt remains disclosed rather than being
reclassified as a pass.

Passing JSON evidence is retained outside the repository at
`C:\Users\dersu\.codex\diagnostics\wp-hermes-broker-2\full-release-57f7d7ca9ecee6d54bd677ba6c2794b29653acaf.json`
(172,766 bytes; SHA-256
`9b0bbc99799d9c1c892d09374f3f04a83372a3ffa8426c5335a1b11b6e0b8637`).
The first-attempt failure JSON is retained beside it with SHA-256
`4690d9fbd98c34661ae8ef33f832480c68059b010b4affffe8e8af0587ce421b`.

The final status tail is documentation-only, so it does not invalidate the exact
implementation-head T3 evidence. Final-head focused reservation/PostgreSQL tests,
BROKER-1 verification smoke, migration idempotency smoke, diff/scope checks, and
implementation-blob identity comparison provide publication evidence.

## Protected Boundary and Next Gate

This package creates durable reservation authority only. It changes no
runtime/paper/live, exchange/order/capital, OMS, risk, safe-mode, kill-switch,
reconciliation, canonical/KDAUTH writer, candidate/promotion, scientific, or
Prefect behavior. It introduces no production A1 registry action, private signing
material, or operator signing UX.

BROKER-2 must merge at the exact Side-reviewed final PR head, and Side's
post-merge report must be forwarded to Main, before BROKER-3 may start. BROKER-3,
BROKER-4, H3-1, and H4 remain not started.
