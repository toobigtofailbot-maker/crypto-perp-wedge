# WP-V2-INTEGRATION-01A-HERMES-02-BOUNDED-HANDOFF-01

- Branch: `codex/wp-v2-integration-01a-hermes-02-bounded-handoff-01`
- Exact base: `e05a7289ddd04560b27179f2bb0b4dbd3a98af4d`
- Implementation / physical-proof and full-release head:
  `f7529380108b2e1c4e9b2a53cc827e67775c7001`
- Final head: the commit containing this status-only factual tail; its immutable
  SHA is recorded in the PR body and exact-head report because a Git commit
  cannot contain its own object ID.
- Pull request: recorded in the PR body and exact-head report after publication
- Package class: T2 plus mandatory physical acceptance and full release
- Self-merge: no

## Scope

This package implements the manual/default-off Prefect -> fixed host Docker
command -> pinned Hermes -> Project-Evidence v4 -> exact read-only Research
Memory -> exact read-only persisted tool-result extraction -> strict
`BoundedResearchIntent v1` handoff. The final model-authored stdout is bounded
operational diagnostic material only. The package stops after host-side
validation.

No Search Governor, Optuna, runner, canonical, candidate/promotion, H2/H2.5
consumer, autonomous scheduler, runtime/risk, paper/live, or capital authority
is added. This branch is held for Side 21 exact-head review and may not be
self-merged.

## Exact changed files

Exactly the authorized 19 tracked files differ from the exact base:

1. `docs/architecture/2026-10-hermes_bounded_research_handoff_implementation.md`
2. `docs/project_status.md`
3. `docs/status_entries/WP-V2-INTEGRATION-01A-HERMES-02-BOUNDED-HANDOFF-01.md`
4. `tests/test_hermes_deployment_contract.py`
5. `tests/test_hermes_domain_tools.py`
6. `tests/test_hermes_research_intent.py`
7. `tests/test_prefect_hermes_research_intake.py`
8. `tests/test_project_evidence_mcp.py`
9. `tools/hermes/Dockerfile.project-evidence`
10. `tools/hermes/README.md`
11. `tools/hermes/config/SOUL.md`
12. `tools/hermes/config/config.yaml`
13. `tools/hermes/skills/cpw-domain-tools/SKILL.md`
14. `tools/mcp/project_evidence/memory_reader.py`
15. `tools/mcp/project_evidence/research_intent.py`
16. `tools/mcp/project_evidence/server.py`
17. `tools/mcp/project_evidence/service.py`
18. `tools/prefect_integration/__init__.py`
19. `tools/prefect_integration/hermes_research_intake.py`

No dependency, Research Memory migration/schema/writer, Search Governor,
Optuna, runner, canonical/query, candidate, runtime/risk, paper/live, or
capital file changed.

## Validation

- Ruff on the changed Python files: PASS.
- Focused intent/intake suite: `56 passed`.
- Adjacent Hermes, Prefect, Project-Evidence, and Research Memory suite:
  `268 passed`; the three PostgreSQL tests also passed against the isolated
  database after its validation process was restarted.
- Mandatory `full-release-balanced-v1`: PASS at the implementation/physical
  head. All 56 required commands passed with no timeout or failure. All 48 of
  48 shards ran and passed; all 190 tracked test files were assigned exactly
  once, with no missing, duplicate, untracked, or incomplete assignment.
  Aggregate shard result was `3956 passed, 24 skipped`; skips were existing
  test-declared optional dependency/data, explicit physical-history, and
  Windows symlink/junction/redirect capability gates. Assignment manifest:
  `sha256:e8edb05c71020a71bc06609c40f025f7638b8d4f1a554a4f8367be07f77dbd90`.
  Slowest shard was 41 at 1121.031 seconds, within the 1800-second profile
  timeout.

## Physical acceptance

Cases A-E passed against the exact implementation head with Prefect 3.8.6,
its isolated PostgreSQL-backed local server, a process work pool/worker, the
fixed host Compose command, Project-Evidence v4, and pinned Hermes image
`nousresearch/hermes-agent:v2026.8.13@sha256:68e15ae2a6d894d0ccbd9f8aacbbe13d4d28fa5dc9b6a303970b67bb2499b1a6`.

- Case A: flow `73998a51-d2c9-44c4-8c6c-fe941a9980cf`, Hermes session
  `20261006_002332_fdb2fd`; exactly one target tool call/result, known-memory
  match true, current evidence resolved, semantic hash recomputed, all authority
  flags false, and final stdout demonstrably differed from the accepted exact
  persisted tool result.
- Case B: flow `3227bea7-fbf1-41d1-87d4-b46f851410d1`, session
  `20261006_002617_fd3b19`; exactly one invocation, unseen-memory match false,
  empty records, and `index_not_truth=true`.
- Case C: with no worker/runner process, flow
  `474d88a8-4855-454d-b379-28fd56a1141a` remained scheduled/late with no new
  Hermes session. Restarting the same worker completed it once in session
  `20261006_003015_4cb1fb`, with exactly one target call/result and no duplicate
  project side effect.
- Case D: implementation-controlled malformed-envelope and host-cross-check
  tests rejected prose/fences, malformed JSON, unknown or widened authority,
  wrong repo/fingerprint/content hashes, and inconsistent redundant persisted
  representations before success.
- Case E: exact-head containers rebuilt and inspected; flow
  `25130a14-ab63-4c49-b109-c59ddb204841`, session
  `20261006_004539_508f76`, passed after restart with one target call/result.
  The live manifest was v4 with exactly 14 tools. Hermes had no repo mount,
  Docker socket, or published port; both containers dropped all capabilities
  and used `no-new-privileges`.

The Research Memory role proved `default_transaction_read_only=on`, no table
mutation privilege, no schema-create privilege, and successful SELECT access.
Every physical case left the proposal outbox empty, created no `.cpw` handoff,
and contacted no Search Governor, Optuna, runner, canonical writer, H2/H2.5
consumer, runtime, paper/live, or capital path.

The validation-only local copies of the two required H004 Parquet inputs and
one known gitignored D4A normalized CSV used by the mandatory release suite are
not tracked and are removed during physical cleanup. No H004 execution stream
was copied or used.

This branch is held for Side 21 exact-head review. Self-merge remains forbidden.
