# Hermes Bounded Research Handoff Implementation

## Authority and status

D2-022 and
`docs/architecture/2026-10-hermes_research_integration_handoff_lock.md` are the
controlling authority. This record describes V2-INTEGRATION-01A implementation;
it does not redefine that decision. Physical acceptance and full-release
validation passed at implementation head
`f7529380108b2e1c4e9b2a53cc827e67775c7001`.

## Implemented topology

The manual/default-off path is human-triggered Prefect deployment -> local
process pool/worker -> one zero-retry task -> a fixed host `docker compose exec`
argument vector -> the existing pinned Hermes container -> one `hermes chat -q
--quiet --source tool` turn -> Project-Evidence only -> read-only extraction of
the exact persisted bounded-builder result from that Hermes session -> strict
host validation -> return of a non-authoritative intent. There is no schedule,
trigger, successor flow, output file, handoff queue, or `.cpw` artifact.

The operator supplies only a strict `cpw_bounded_research_request_v1` JSON
object. Code owns the prompt, compose file, service, executable, subcommand,
flags, timeout, and stdout/stderr limits. The fixed timeout is 300 seconds;
stdout is limited to 1,000,000 bytes and stderr to 64,000 bytes.

The stderr session identity selects one external Hermes `state.db` session.
The adapter opens that ordinary, non-linked database through stdlib `sqlite3`
with a `mode=ro` URI and executes one ordered `SELECT` over active messages. It
requires exactly one `cpw_build_bounded_research_intent` call and exactly one
result linked by its persisted `tool_call_id`. The linked result envelope and
strict intent are parsed deterministically. The pinned runtime may persist its
redundant `structuredContent` representation beside the string `result`; when
present, both representations must decode to the identical intent or the handoff
fails closed. Hermes `SessionDB` is not imported
or instantiated, and the extractor performs no PRAGMA, DML, DDL, checkpoint,
schema reconciliation, or migration.

Hermes final stdout remains size-bounded operational diagnostic material. It
is neither the accepted handoff nor research truth, so model-authored
rephrasing cannot replace or modify the exact Project-Evidence result. The
prompt still asks Hermes to return that result exactly as behavioral guidance.

## Request, intent, and content identity

`BoundedResearchRequestV1` accepts a safe request ID, bounded research question,
structured hypothesis identity, exact Project-Evidence URIs, and reasoning-only
constraints. Instrument scope is not caller input and is fixed to
`BTCUSDT_BINANCE_USDTM_PERP`.

Hermes submits only `BoundedResearchIntentDraftInput`: the fixed request
identity plus bounded reasoning. Project-Evidence resolves evidence, normalizes
the hypothesis through the existing `HypothesisDefinition`, computes the
existing `hypothesis-v1` fingerprint, performs the exact read-only memory
lookup, and emits `cpw_bounded_research_intent_v1`.

The semantic `content_sha256` is `sha256:` plus SHA-256 of canonical UTF-8 JSON
using sorted keys, compact separators, ASCII escaping, and NaN rejection. It
covers repo identity, normalized hypothesis, reasoning, resolved evidence,
memory context, and fixed non-authority fields. Hermes session identity and all
Prefect/Docker/process/timestamp identifiers are excluded.

## Evidence and Research Memory boundary

Each caller URI is re-resolved by `EvidenceResourceCatalog`; caller paths and
hashes are unavailable. `lookup_definition` selects only the exact existing
fingerprint under `default_transaction_read_only=on` and `SET TRANSACTION READ
ONLY`. The reader still rejects any role with table mutation privileges. A
memory hit remains `index_not_truth=true`; stale, missing, unsafe, or
hash-mismatched repo evidence cannot surface a resolved classification.

The Project-Evidence image copies only `tools/research_memory/__init__.py` and
the pure `fingerprint.py` identity implementation. It does not copy the
repository, migrations, repo-source bootstrap, runner, or write helpers.

## Project-Evidence and Hermes surface

Manifest `project_evidence_mcp_v4` exposes exactly 14 tools: the unchanged eight
direct base tools, unchanged five compute-only CPW domain tools, and one separate
bounded integration handler, `cpw_build_bounded_research_intent`. The only
Project-Evidence write surface remains `proposal_outbox`; the new handler writes
nothing. Hermes keeps its exact pinned image, disabled escalation toolsets,
non-parallel tool calls, no repo mount, no Docker socket, and no published port.

## Environment and operational ownership

The worker inherits a bounded host environment required by the established
Compose deployment. Research Memory DSN and model credentials are neither flow
parameters nor results and are not logged. `PROJECT_REPO_SHA` must equal the
worktree HEAD. Prefect owns deployment/task/run state and worker-off recovery
only; all Prefect and Hermes identifiers remain operational.

## Explicit non-authority

The intent fixes canonical-write, approval, candidate/promotion, Search
Governor, final-holdout, scheduler/autonomy, runner/backtest, runtime/risk,
paper/live, and capital authority to false, with no automatic consumers. 01A
does not invoke Search Governor, Optuna, a runner, H2/H2.5 consumers, canonical
writers, runtime, paper/live, or capital paths. V2-INTEGRATION-01B remains a
future separately researched and authorized package.

## Physical acceptance

Mandatory Cases A-E passed using the pinned Hermes image, Project-Evidence v4,
an isolated DB-enforced read-only Research Memory role, Prefect 3.8.6 with
PostgreSQL, and the required process pool/worker topology. Known and unseen
memory cases each produced exactly one persisted bounded-builder call/result;
worker-off submission produced no Hermes session until the same worker resumed;
malformed and authority-widening controlled outputs failed closed; and the
rebuilt exact-head container surface retained 14 tools, no Hermes repo mount,
no Docker socket, and no published Hermes port.

The mandatory `full-release-balanced-v1` profile also passed at that exact
head: 56 of 56 required commands and 48 of 48 shards passed, with exact-once
assignment of all 190 tracked test files and no missing, duplicate, timed-out,
failed, or incomplete shard. These results establish implementation acceptance
only. They create no merge, scientific, execution, scheduling, runtime,
paper/live, or capital authority, and Side exact-head review remains required.
