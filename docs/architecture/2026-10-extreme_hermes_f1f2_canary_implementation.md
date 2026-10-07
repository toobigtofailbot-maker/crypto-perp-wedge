# WP-EXTREME-HERMES-01 — F1/F2 implementation and acceptance record

Controlling package: executable Revision 2. Exact base:
`11214acfb6d8af44586c50089eb9965063a505ee`.
Branch: `codex/wp-extreme-hermes-01-f1f2-canary-01`.

Implementation is in progress. This preliminary record is not final physical
acceptance, publication, or Side exact-head review evidence. All Cases A–K must
pass before one PR is published. Self-merge is forbidden.

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
proof is pending; config text is not acceptance.

The director inherits upstream s6 and reasoning runs as UID 10000. Its root
filesystem is read-only, /run is an executable tmpfs required by s6, lazy
installation and config migration are disabled. Its limited bootstrap caps
support ownership and runtime UID/GID dropping; runtime capability verification
remains part of final acceptance. No host ports or Docker socket are provided.

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
headless model access, OAuth root fallback and isolation are pending.

Delegation is capped at two children / depth one, no orchestrator, no
auto-approval, no inherited MCP toolsets. Its live bounded task is pending.
HERMES-02 changes only its fixed executable to the inherited PATH command
hermes; its exact argument vector, shell=False, timeout, single-call/session
extraction and intent validation remain intact. Physical Prefect-worker proof
and F0 rollback startup are still pending.

## Preliminary physical observations

These are individual observations, not final Case A–K PASS declarations.

- Terminal reported execution-sandbox, UID/GID 10001, /workspace. Actual
  write_file/read_file round-tripped a benign workspace file; execute_code
  reported remote:true, the sandbox hostname and UID 10001. Cleanup removed
  the file.
- Sandbox paths /opt/data, /opt/hermes, /project, director SSH private volume
  and Docker socket were absent. Named credential environment variables were
  absent. Connections to public 1.1.1.1, metadata 169.254.169.254, representative
  RFC1918 endpoints, host.docker.internal and Project-Evidence failed.
- Plugin and MCP canaries returned the fixed deterministic object. Runtime
  discovery showed the existing 14 explicit Project-Evidence tools, its two
  preserved resource wrappers, and one additional canary MCP tool. Browser
  definitions remain absent until its live credential gate is satisfied.
- Writable skill create/read/patch worked. Ledger entry 5d8b0b63010c recorded
  the patch; hermes curator rollback 5d8b0b63010c --yes restored exact prior
  bytes. The skill was then deleted. Audit/rollback entries remain in external
  state only.
- The real memory tool with its agent-loop store wrote/read back one benign
  item from external state and removed it, restoring the empty prior entries.
- SSH host-key changes failed closed during an intentional sandbox rebuild;
  server keys now persist in their dedicated root-only volume. Strict host-key
  checking was retained. Sandbox/director restart preserved the host identity; terminal/file/Python and network-denial checks passed again. Both profile homes persisted.

## Validation and gates

Focused deployment/canary/HERMES-02 checks passed 45 tests (one existing MCP
Pydantic settings warning). Adjacent Hermes/Project-Evidence/research-memory
checks passed 175 tests. Ruff passed and start.ps1 parsed without errors.
The exact two ignored H-004 corpus inputs were verified against runbook sizes
and SHA-256, copied byte-for-byte, and kept untracked under h004-clean.
The preliminary full-release process was interrupted across the environment
restart and left no result; it is not a pass. Full-release must be rerun at the
accepted implementation head after live acceptance.

Browserbase variables are PRESENT in the current execution process. A real
Browserbase session navigated to example.com and returned a snapshot. Localhost,
IPv4/IPv6 loopback, RFC1918 and metadata attempts failed closed. No local
Chromium or real browser-profile snapshot was observed. The session was released
(provider status COMPLETED, HTTP 200). Basic stealth worked; residential proxies
were unavailable, an optional feature disclosure. Live inventory excludes
browser_exec, Computer Use, catalog management and web_extract.
Refreshed origin/main is still the exact base, no PR is open, and latest stable
is still v2026.9.24. Hermes-managed openai-codex OAuth is READY and live native
search completed. Both headless specialists passed with stripped director
credentials; one leaf delegation completed at depth 1 with nested spawning
denied and no inherited MCP. Karl authorized reuse of existing official
PostgreSQL 17.10 Windows binaries for an isolated external loopback-only cluster
on port 60619. Separate research_memory_test/research_memory databases use SCRAM;
local DSNs are DPAPI-protected. Repo migrations/bootstrap and the fixed reader
role were applied. Identity, read-only default, four-table SELECT and DML denial
passed physically; three PostgreSQL integration tests passed unskipped. The
container can reach the host loopback service through Docker Desktop's existing
host.docker.internal route. No secret value is recorded.
No PR has been published. Final Cases A–K and exact-head evidence are pending.

## F0 preservation

compose.f0.yaml is the exact pre-package Compose byte copy; config.yaml,
SOUL.md and schedule_plan.json remain unchanged. Rollback keeps the original
v2026.8.13 digest and Project-Evidence-only posture. F0 needs no Browserbase
credential and requires no Hermes reasoning. Physical rollback remains a gate.

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
