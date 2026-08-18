# WP-HERMES-BROKER-1-VERIFICATION-CORE-01

## Package State

- Branch: `codex/wp-hermes-broker-1-verification-core-01`
- Refreshed base: `61c9c6196908f3c511a0e17dd9ae444a67c45829`
  (merged PR #708 / H2.5 PREPARE)
- Implementation and T3 evidence head:
  `a807f925614bac0e643074a5866fb2eda43a6b26`
- Package class: T3 authority-crossing verification core
- Result: BROKER-1 verification core complete; verification only

Only BROKER-1 is proven. This package creates deterministic authority
verification and stops at an inert allow/reject decision. It creates no database,
reservation, nonce burn, authority-audit database, dispatcher, downstream adapter,
Prefect integration, real H3 action, or H4 authority. BROKER-2 and BROKER-3 remain
required before H3-1; BROKER-4, H3-1, and H4 are not started.

## Stable Prepared-Artifact Retention

`tools/hermes/broker/retention.py` requires the explicit
`HERMES_BROKER_ARTIFACT_ROOT` contract, or the equivalent required CLI argument,
and rejects roots inside the repository or active worktree. Existing path
components, the stable root, the fixed `prepared/` directory, source files, and
destinations are checked for symlinks and Windows reparse points. Retained names
are closed to
`HERMES-PREP-<YYYYMMDDTHHMMSSZ>-<16-lowercase-hex>.prepared.json`.

`BrokerArtifactStore.retain_from_outbox()` validates the source as the exact
canonical H2.5 outer record, exclusive-creates the destination, copies exact bytes,
flushes and file-fsyncs, reopens the retained file, and proves source/retained byte
hash equality. A second write is rejected. Directory fsync is completed where the
platform supports it and is explicitly recorded as unsupported on Windows. The
operator CLI is `python -m tools.hermes.broker.retention`; verification lookup is
read-only and never creates a missing store.

Physical acceptance used this stable external root:

`C:\Users\dersu\HermesBrokerArtifacts\BROKER-1\a807f925614bac0e643074a5866fb2eda43a6b26`

It retains exactly these proof artifacts:

| Class | Prepared record | Prepared payload SHA-256 | Exact retained-byte SHA-256 |
| --- | --- | --- | --- |
| A1 | `HERMES-PREP-20260817T235910Z-cec5a507a7c742cf` | `fb100193681f565587bb40d6bad788cb7a04185c9710953640c8d4be903fc270` | `6eb89e17f052f558c04a73c067b30da2b36b8efddf4dcd7335d592924adbabe9` |
| A0 | `HERMES-PREP-20260817T235910Z-27ae3ba62b9443bf` | `f79add3aafa8dd71d47bfedddc2325193c765f0724c915abb6470575f923ab6c` | `7d1d28dc456bf35bdf51b7fc97b36a50e7cf67f2a73261258c04dc10969cfe46` |

The acceptance removed the source-worktree fixture files after retention and
successfully reverified the A1 retained payload hash. Exact-byte preservation,
read-after-source-removal independence, no overwrite, traversal rejection, regular
file enforcement, maximum size, noncanonical-byte rejection, and a real Windows
junction/reparse rejection are green.

Retained lookup validates the closed H2.5 outer/source/inert-authority shape,
validates the nested `PreparedPayload`, and independently recomputes
`prepared_payload_sha256` through the unchanged exact merged H2.5 function
`tools.hermes.prepare.serialization.canonical_json_bytes`. Broker-local action and
claim serialization does not redefine the H2.5 hash.

## Closed Registry and Executable Action

The registry is `tools/hermes/broker/registry.py`, schema
`hermes_broker_action_registry_v1`. The production registry version is
`broker1-production-empty-v1` and has zero entries. There is no real H3 action and
no A0 entry. Registry construction rejects non-A1 classes, every reused H2 A0
domain, dispatch-capable entries, non-proof entries, duplicates, and mismatched
versions. Entries contain type/schema identities only; they contain no callable,
dynamic import, command, endpoint, or dispatch path.

Physical acceptance uses one separate proof-only identity:

- registry: `broker1-proof-registry-v1`;
- action type: `broker1.proof.verify_identity_v1`;
- adapter identity: `broker1-proof-non-dispatchable`;
- adapter version: `1.0.0`.

`ExecutableAction` has exact schema/action/prepared/source/repo/registry/adapter
identities, fixed A1 authority, human/Hermes authorship flags, strict typed target,
scope, and parameters, exact hard budget, applicable hard count/quantity, and exact
hard timeout. All Pydantic models are immutable and extra-forbidden. A prepared
plan, prose object, generic dictionary, unknown action, extra field, generic
parameter passthrough, or A0-linked object cannot validate as an executable action.

The executable-action hash is lowercase SHA-256 over
`broker_canonical_json_v1`: validated JSON-compatible data, lexicographically
sorted keys, compact separators, UTF-8, `ensure_ascii=false`, finite non-float
values only, LF, exactly one trailing newline, and fixed depth/item/byte limits.
The scope digest applies the same contract to the typed scope.

## Approval and Ed25519 Verification

`ApprovalClaimPayload` is the strict schema
`hermes_broker_approval_claim_v1`. Its exact fields are domain separator,
approval/action/prepared/source identities and hashes, repo SHA, A1 authority,
action/registry/adapter identities, scope digest, budget, applicable
count/quantity, timeout, issued/not-before/expiry timestamps, single-use nonce,
signer key ID, and key-registry version. It permits no generic claims or metadata.

The domain separator is exactly `hermes-broker-approval-v1`. Ed25519 authenticates:

`b"hermes-broker-approval-v1\x00" + broker_canonical_json_v1(unsigned payload)`

The signature is strict 128-character lowercase hex; the public key is strict
64-character lowercase hex. Algorithm negotiation is absent and only `ed25519` is
accepted.

PyCA `cryptography==50.0.0` supplies Ed25519 verification. `requirements.txt` now
pins that exact version; `requirements.lock.txt` already resolved 50.0.0 and did
not change. The isolated Python 3.11.9 validation environment resolved
`cryptography 50.0.0`, `cffi 2.1.1`, and `pycparser 3.0`; `pip check` passed.

The trusted-key schema is `hermes_broker_trusted_keys_v1`. Each key carries exact
key ID, `ed25519`, lowercase-hex encoding/public key, active or revoked state,
added/revoked timestamps, revocation reason, and fixture-only marker. The registry
carries an exact version and rejects duplicate IDs. Physical proof used
`broker1-proof-keys-v1` and an external ephemeral Ed25519 private key. No private
key is passed into broker configuration or Hermes, persisted in the acceptance
root, or present in tracked repository state.

Known-good signing, wrong key, key-ID/public-key mismatch, unknown key, revoked
key, one-bit message mutation, one-bit signature mutation, malformed public key,
malformed signature, duplicate key ID, private-material extra field, and
unsupported algorithm cases all fail closed as required.

## Lineage, Freshness, and Decision

Verification binds the claim exactly to the validated action ID/hash, retained
prepared ID/hash, source proposal ID/hash, A1 class, action type, scope digest,
budget, applicable count/quantity, timeout, current repo SHA, registry version,
adapter ID/version, and key-registry version. Retained H2.5 payload verification
then rechecks source proposal lineage, source repo SHA, prepared repo SHA, and both
source/current A1 authority classifications.

Approval timestamps require whole-second UTC, ordered issued/not-before/expiry
values, expiry strictly after issue, and a maximum lifetime of 3,600 seconds. The
broker rejects too-early and expired claims and uses an exclusive expiry boundary.
BROKER-1 validates nonce syntax and binding only; it does not reserve or burn a
nonce.

`BrokerDecision` is the immutable `hermes_broker_decision_v1` schema. Its closed
reason codes are `verified`, `unknown_action_type`, `a0_forbidden`,
`prepared_artifact_invalid`, `prepared_hash_mismatch`, `source_lineage_mismatch`,
`action_hash_mismatch`, `claim_binding_mismatch`, `unknown_signer`,
`revoked_signer`, `invalid_signature`, `not_yet_valid`, `expired`,
`approval_lifetime_exceeded`, `repo_stale`, `registry_stale`, `adapter_stale`,
`key_registry_stale`, `malformed_action`, `malformed_claim`, and
`unsupported_algorithm`.

The valid physical A1 case returned `allow / verified`. It also returned
`reservation_created=false`, `dispatch_request_created=false`, and
`downstream_side_effect=false`. A correctly Ed25519-signed A0-linked claim returned
`reject / a0_forbidden`; the separate proof signing guard also refused A0. Thus a
valid signature cannot make A0 executable.

The physical matrix additionally returned deterministic rejection for direct
prepared-plan input, generic prose/dictionary input, hash tamper, revoked key,
stale registry, stale adapter, wrong repo, too-early claim, and expired claim. Unit
coverage adds every field binding, malformed outer/nested artifacts, missing or
symlinked retention, action/claim shape, key, algorithm, time-order, and lifetime
variant required by the package.

## No-Authority Proof

The BROKER-1 package contains no PostgreSQL broker state, approval/reservation
table, nonce burn, authority-audit database, retry/reconciliation state, dispatcher,
dispatch request, callable adapter, network/HTTP, subprocess/shell, Prefect, Codex
task, Search Governor invocation, repository/canonical writer, KDAUTH integration,
runtime/paper/live action, OMS, risk, reconciliation, exchange/order/capital action,
promotion/GO path, or scientific authority. The production registry has zero
actions. Project-Evidence remains exactly eight MCP tools; broker verification is
not exposed to Hermes as a ninth tool.

## Validation Evidence

- Focused BROKER-1 tests: 66 passed.
- Adjacent Hermes, evidence, registry, dispatch-boundary, and execution-boundary
  tests: 721 passed, 6 environment-dependent skips.
- Physical acceptance: A1 allow, valid-signature A0 deny, direct-plan/prose deny,
  hash/key/version/repo/time denies, exact retention, no overwrite, source-removal
  independence, and no side effect all passed.
- Ruff check/format, compileall, JSON/YAML parsing, `git diff --check`, exact changed
  file inspection, protected-path inspection, dependency resolution, and `pip check`
  passed.
- Project-Evidence discovery remains exactly eight tools.

The successful exact T3 invocation at implementation head `a807f925...` was:

```text
python tools/dev/verify.py --validation-preset full-release --full-pytest-sharded --pytest-shard-profile full-release-balanced-v1 --json
```

It used profile `full-release-balanced-v1` version 1, 48 shards, four workers, and
assignment manifest
`sha256:9ee1d903f451a8c901ee2614d4579fea576cf2e1915d461b17dc0ee5c69fdd70`.
All 174 discovered files were assigned exactly once: 174 assigned, 174 unique,
zero missing, duplicate, untracked, incomplete, or timed-out assignments. All 48
shards passed with `all_shards_passed=true`; aggregate pytest output was 3,554
passed and 21 skipped. Wall time was 51 minutes 17 seconds; the slowest shard was
shard 0 at 900.063 seconds, below the unchanged 1,800-second profile timeout.

Complete JSON evidence is retained outside the repository at
`C:\Users\dersu\.codex\diagnostics\wp-hermes-broker-1\controlled-full-release-a807f925.json`
(176,906 bytes, SHA-256
`405e9d7fa3c015e8c35cb0dca187d262c48612b51e0567a63b7fca2f4a601848`).
Its separate stderr artifact is empty. The verifier returned exit 0 and left no
pytest or verifier process.

The earlier timeout target moved from shards 41/43 under four workers to 30/31
under a diagnostic single-worker run, while every exact file set passed directly
on both implementation head and detached exact `origin/main`, and all selected
profile reruns passed well below timeout. The controlled exact profile proves this
was validation-host/orchestration behavior, not a BROKER-1 semantic regression.

The final status commit is documentation-only and therefore does not invalidate
the exact implementation-head T3 evidence under the repository's reusable
validation policy. Exact-head T0 scope, diff, docs consistency, and focused smoke
checks are required before publication.

BROKER-2, BROKER-3, BROKER-4, H3-1, and H4 remain not started.
