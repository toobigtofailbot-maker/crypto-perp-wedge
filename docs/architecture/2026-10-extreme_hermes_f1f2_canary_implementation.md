# WP-EXTREME-HERMES-01 — F1/F2 implementation and acceptance record

Controlling package: executable Revision 2 and Side 22 Case J / SSH-temp follow-ups.
Base: `11214acfb6d8af44586c50089eb9965063a505ee`.
Branch: `codex/wp-extreme-hermes-01-f1f2-canary-01`.
Final semantic implementation/validation head: `cba25971c8365f331d2e2240fb639949de1ff3cc`.
Final documentation commit records evidence only. Hold for Side 22 exact-head
review; Codex does not declare merge readiness. Self-merge is forbidden.

## Repo and upstream facts

Fresh preflight confirmed the exact origin/main base, no open PR, an absent
package branch before creation, and a clean dedicated worktree. Docker 29.8.0,
Compose v5.5.1, pinned image pull, and the existing Python validation environment
were usable before tracked mutation. External live credentials are deferred
under Revision 2 §6.3; their absence does not authorize substitution.

Official upstream release/API and pulled image checks confirmed:

- stable tag `v2026.9.24`, product `0.21.5`;
- source `f97608f178d1ffeca59860195ab7da295f7c8e5f`;
- index `sha256:fca358f12efd65bfaaca05884166f15c0e2788375ca30d77061ac1ebc96452b7`;
- amd64 `sha256:2fd023efbb8d3d2b0ce1a73d028b07370cff34f567cfe0e999553e8c327ea283`;
- required fix `59559b858fb1a4578f51029112099462a431c3f1` is not an ancestor
  of stable (comparison: diverged, ahead 1 / behind 162).

The vendored patch preserves the exact five-file upstream semantic diff:
three runtime files and two adversarial test files. The original official diff
SHA-256 was `81aef04fd168596fc5f1549308ed6d6d48b524232dae4aa0f8b2d0fbee8abe08`.
One whitespace-only adaptation removes the space marking an empty context
line so the CPW diff passes whitespace validation; no source addition/deletion
changes. Adapted patch SHA-256:
`1294e8e88663691f49e4b78d074460f91f9097afbd23a0e005a161f20fe78a6e`.
The build checks source identity, patch hash and stable preimage before apply.
The rebuilt derived image config ID is
`sha256:eaa63f75cfc283e96f7bc53b2cb093e01039408ff5712c3d77f946e5d92f6bfa`.
Its two upstream adversarial test modules passed: **9 tests**. Pytest was
installed only into a separate validation image, never the runtime image.

## Delivered boundaries

The scratch-supported migration reached schema 46; F0 configuration was not
migrated in place. F1/F2 deliberately allowlists the required research toolsets.
OpenAI-native search is search-only. Browserbase uses built-in browser tools,
backend off, no private/local fallback and no real profile. Live browser/search
proof passed at the physical-validation head; config text alone is not acceptance.

The director inherits upstream s6 and reasoning runs as UID 10000. Its root
filesystem is read-only, /run is an executable tmpfs required by s6, lazy
installation and config migration are disabled. Its limited bootstrap caps
support ownership and runtime UID/GID dropping; physical verification found the reasoning gateway
at UID 10000 with zero effective capabilities. No host ports or Docker socket are provided.

The repo-owned SSH sandbox has only an internal isolated execution bridge,
an external named workspace, a public authorized-key volume, and a private
server-host-key volume. Server keys persist across restart, are root-only, and
are never mounted into the director. A networkless one-shot generates the
client keypair; the director receives its private key read-only. The sandbox
receives no repo mount, director home or credential environment. SSH forwarding,
password/root login, user environment and user RC are disabled. Its bootstrap
caps are CHOWN, SETUID, SETGID, SYS_CHROOT; DAC_OVERRIDE was removed after proof
it was unnecessary. File write safety names external state and /workspace only.

The inert plugin registers only `cpw_canary_ping`. The isolated MCP server
registers only `canary_ping`, has no credential/repo mounts, and enables no
sampling/elicitation/prompts/resources. Project-Evidence semantics and its
existing 14 explicit tools remain unchanged; existing read-resource/list-resource
wrappers remain enabled by the preserved resources:true setting.

Nine CPW skills remain read-only. New skills use /opt/data/writable-skills,
also declared as an external discovery directory using upstream-supported
configuration. Curator/background consolidation is off. Two fresh profiles,
research-scout and research-critic, were created with --no-skills, --no-alias
and no cloning. Their external configs allow only memory/session-search; live
headless model access, OAuth root fallback and isolation passed after restart.


Delegation: max children two, depth one, leaf role, orchestrator and auto-approval
off. Normal model-facing delegate_task inherits approved parent tools minus hard
child blocks. Parent 47 / child 44 tools; no child-only tool or MCP tool; both have
17 approved MCP tools. delegate_task, memory and skill_manage are removed. Nested
spawning and over-two-child requests are denied. Model auth remains the same
openai-codex OAuth class. Browserbase remains backend-only for the explicitly
inherited approved browser surface. Sandbox execution has no director credentials,
Research Memory DSNs, SSH private-key mount, protected repo or Docker surface.

The original zero-MCP Case J assertion was an expectation defect, not proof of
widening. inherit_mcp_toolsets=false applies only to explicitly narrowed internal
children, not normal delegate_task; it was removed as a misleading global control.
No delegation source patch or per-child toolset surgery was introduced.

The normal-CLI SSH failure was reproduced as a linked Unix-socket failure under
Windows-backed /opt/data/cache/scratch; equivalent sockets worked in native /tmp.
F1/F2 Compose now sets TMPDIR/TMP/TEMP=/tmp, retaining the existing 256 MiB tmpfs.
Mechanical proof confirmed temp variables, tmpfs, tempfile.gettempdir(), and normal
SSHEnvironment ControlMaster sockets under /tmp/hermes-ssh. HERMES_HOME remains
external persistent state. No upstream SSH patch, multiplexing disablement,
mount/port expansion, dependency, provider or topology change was needed.

HERMES-02 changes only its fixed executable to inherited PATH command hermes.
Argument vector, shell=False, 300-second timeout, single-call/session extraction
and request/repo/fingerprint/content-hash checks remain unchanged. Supported
tools.tool_search.enabled=off advertises the same allowlisted direct schemas,
avoiding the batched disclosure envelope rejected by the strict extractor.

## Physical acceptance and finality

B/C/J and process-worker K plus rollback passed at the final semantic head.
A/D/E/H/I evidence at f5f9bac9f5a808e9201184386523028726f735de remains valid per
the Side 22 follow-up: the correction does not change relevant source/image,
browser/search, skill/memory or profile semantics. Plugin/MCP/container boundaries
were also refreshed. Memory/skill atomic writes use temporary files beside
their persistent targets; profile creation stages beside its target. These
exercised persistence paths do not depend on process TMPDIR.

| Case | Result | Evidence |
|---|---|---|
| A | PASS | Exact stable source/digests and five-file backport; unchanged runtime image; 9 upstream adversarial tests. |
| B | PASS | Live 47-tool director inventory; forbidden browser/Computer Use/install/Docker/broker/live tools absent. |
| C | PASS | Normal SSH under /tmp; terminal/file/Python in sandbox UID 10001; private paths/credentials absent; public/private/metadata/host/PE network denied. |
| D | PASS | Real Browserbase navigation/snapshot; private/loopback/metadata rejection; no local Chromium/profile; session released COMPLETED. |
| E | PASS | Native Codex search transport with one completed provider search. |
| F | PASS | Only inert CPW plugin, fixed deterministic response, no effectful handler/import. |
| G | PASS | 14 PE tools plus two preserved resource wrappers; one canary MCP tool, no canary resources/prompts/mounts/credentials. |
| H | PASS | Ledger 0f6528eebda7 rollback restored exact bytes; benign memory cleaned; nine read-only skill mounts reverified. |
| I | PASS | Exactly two fresh distinct persistent profiles; headless OAuth fallback; narrow memory/session_search without director credentials. |
| J | PASS | One real leaf task completed; strict 44-of-47 tool and same-17 MCP subset; credential/filesystem proof passed before task; nested/over-two-child denied. |
| K | PASS | Real process-worker handoff, strict extraction, no successor/outbox; exact F0 rollback without reasoning/Browserbase. |

Accepted K flow: 75322716-6834-4f1e-83be-3ccf2608fec0.
Session: 20261007_162055_a172fb. One invocation/session, one task, one target
builder call/result. Only read_project_resource and the builder were called.
An earlier attempt completed strict extraction but violated the validation
fixture's two-tool constraint by reading approved read-only cpw-domain-tools;
it is not counted as acceptance. The explicit transport-only retry passed the
unchanged assertion. No production code or gate was weakened.

F1/F2 is stopped and exact F0 is active. F0 model-facing progressive wrappers
are tool_search/tool_describe/tool_call, backed only by the original 14 PE tools
and two existing resource wrappers. No broad F1/F2 tool; zero rollback reasoning.

## Validation and environment

Focused 45 passed (one existing Pydantic warning). Adjacent 178 passed including
three unskipped live PostgreSQL tests. Prior upstream backport tests: 9 passed.
Fresh full-release PASS at `cba25971c8365f331d2e2240fb639949de1ff3cc`: all 56 command results passed, all 48 full-release-balanced-v1 shards passed, exact tracked test-file coverage verified, zero failures.
The earlier interrupted run had no accepted result. The first complete run
failed five tests because the worktree lacked the canonical D4 normalized CSV.
Two existing repo-provenance-named copies matched committed SHA-256
c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab.
The 220128-row file was copied byte-for-byte into the existing ignored validation
path; no data was generated or substituted. A fresh full-release supersedes
those earlier non-accepted runs.
Exact 16-created + 8-modified closure and forbidden-path preservation checked
against the required base; git diff --check passes. No tracked semantic change
follows this validation head.

Existing official PostgreSQL 17.10 Windows binaries were reused for an isolated
external 127.0.0.1:60619 SCRAM cluster. Separate research_memory_test/research_memory,
repo migrations/bootstrap, fixed hermes_research_memory_reader, default read-only,
four-table SELECT and INSERT/UPDATE/DELETE denial passed physically. DSNs remain
DPAPI-protected outside the repo and injected into validation processes. Prefect
used its separate local-validation database on the same isolated cluster.
Browserbase PRESENT/VALIDATED; OAuth READY/VALIDATED; Research Memory DSNs
READY/VALIDATED. User-scope Browserbase cleanup reminder: YES. No secret value
recorded. Optional residential proxies unavailable; tirith unavailable with
upstream pattern fallback. No substitution.

## F0 preservation

compose.f0.yaml is the exact pre-package Compose byte copy; config.yaml,
SOUL.md and schedule_plan.json remain unchanged. Rollback keeps the original
v2026.8.13 digest and Project-Evidence-only posture. F0 needs no Browserbase
credential and requires no Hermes reasoning. Physical rollback passed without model reasoning or Browserbase credentials.

- `compose.f0.yaml` SHA-256: `0ba9dc88352c7d8b79da5e2a4a9b3eeb3c4b6127b858048516a7fa62a514b49a`.
- `config/config.yaml` SHA-256: `7993c5fcdaa9df3a7c42a698a61d22b92feca49f83e08d714c159bb976326899`.
- `config/SOUL.md` SHA-256: `77ebe8acfe70ccab45592fa4b5dd9e08f10b54287faedb0b3546efbad0bc81ac`.

## Authority

Capability proof grants no Stage 5B, autonomous scientific research, scientific
policy/lineage authority, canonical writer, candidate promotion, protected
runtime/OMS/reconciliation/risk/overlay/safe-mode, paper/live, exchange/order,
or capital authority. Search Governor and CPW retain their existing ownership.
Prefect owns durable operational flow state only. Side 22 exact-head review
is required; Codex does not declare merge readiness.

## Exact file closure

The following is the complete base-to-implementation closure (A=create, M=modify).
No protected, schema, query-layer, dependency-lock, or other forbidden path changed.

```text
A	docs/architecture/2026-10-extreme_hermes_f1f2_canary_implementation.md
M	docs/project_status.md
A	docs/status_entries/WP-EXTREME-HERMES-01.md
A	tests/test_extreme_hermes_canaries.py
M	tests/test_hermes_deployment_contract.py
M	tests/test_prefect_hermes_research_intake.py
A	tools/hermes/Dockerfile.canary-mcp
A	tools/hermes/Dockerfile.execution-sandbox
A	tools/hermes/Dockerfile.extreme
M	tools/hermes/README.md
A	tools/hermes/canary_mcp_server.py
A	tools/hermes/canary_plugin/__init__.py
A	tools/hermes/canary_plugin/plugin.yaml
A	tools/hermes/compose.f0.yaml
M	tools/hermes/compose.yaml
A	tools/hermes/config/SOUL.f1f2.md
A	tools/hermes/config/config.f1f2.yaml
A	tools/hermes/execution_sandbox/entrypoint.sh
A	tools/hermes/execution_sandbox/keygen.sh
A	tools/hermes/execution_sandbox/sshd_config
M	tools/hermes/start.ps1
A	tools/hermes/upstream_patches/59559-tool-scope.patch
M	tools/hermes/upstream_watch.json
M	tools/prefect_integration/hermes_research_intake.py
```
