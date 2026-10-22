# Extreme Hermes F1/F2 canary and exact F0 rollback

The active Compose builds the exact stable `v2026.9.24 / v0.21.5` image plus
upstream `59559b858fb1a4578f51029112099462a431c3f1`. This package is a bounded
non-capital capability proof. Physical Cases A-K and full-release validation
remain mandatory before publication; no Stage 5B or scientific autonomy is active.

Select `start.ps1 -Mode F1F2` explicitly with a fresh external home. The launcher
requires Browserbase variables in its process, `.no-bundled-skills`, merged PR
#733 (`200276fd4407e4a13a912a6b475ab9ab38a1de70`) in HEAD ancestry, and
Docker/Compose. It accepts a new supervised work branch descended from that
implementation. Supply secrets only through the existing
operator environment/auth store. At the first missing live credential gate use
WP Revision 2 §6.3. No DSN/token/key belongs in Git or operator output.

`-Mode F0` selects the unchanged `compose.f0.yaml`, old image, config and SOUL.
Stop the F1F2 deployment before starting F0. F0 needs no Browserbase secret.
`-InstallSchedules` is rejected for F1F2; schedule_plan.json remains inert there.

The director inherits upstream s6 supervision and drops runtime reasoning to
UID 10000. Bootstrap-only CHOWN/DAC_OVERRIDE/FOWNER/SETUID/SETGID capabilities
support volume ownership and that drop; runtime acceptance must confirm it.
The SSH sandbox begins with ALL capabilities dropped and adds only CHOWN,
SETUID, SETGID and SYS_CHROOT for workspace ownership,
sshd privilege separation and unprivileged login. Acceptance must verify each
is necessary. There is no SYS_ADMIN or Docker socket. SSH receives public key
material only, port 2222 is internal, and the cpw home is /workspace.

Both canary and execution bridges are internal with gateway mode `isolated`:
no host bridge IP/default egress route. The sandbox attaches only to execution.
Hermes gets the private key read-only; keygen has no network. Browserbase runs
remote sessions with built-in tools and private/local fallback disabled.
Search is OpenAI-native and search-only. The existing nine CPW skills remain
read-only; writable skills/memory live solely in the external home.

F1/F2 sets TMPDIR, TMP and TEMP to /tmp on its existing 256 MiB container tmpfs.
HERMES_HOME remains external and persistent. Linux ControlMaster sockets stay
off the Windows-backed home; multiplexing remains enabled. Ordinary delegated
leaves inherit approved parent tools/MCP minus hard child blocks. Case J requires
strict subset, credential/filesystem containment and one completed task, rather
than zero inherited approved MCP tools.

During physical acceptance create exactly these fresh profiles:

```text
hermes profile create research-scout --no-skills
hermes profile create research-critic --no-skills
```

Use no clone/clone-all, channel credentials or static API-key mirroring. Author
narrow profile role/configuration in external state, permit only model OAuth root
fallback, and verify no Browserbase/SSH/Research Memory/broker/live credential
is reachable. Verify persistence after restart and headless access. Profile and
delegation containment require live proof; documentation is not that proof.

For headless specialist execution, strip director-only credentials from the
child process environment before selecting the profile. This preserves the
upstream model OAuth root fallback without copying auth state into profiles:

```text
docker compose -f tools/hermes/compose.yaml exec -T --user 10000:10000 hermes env -u BROWSERBASE_API_KEY -u BROWSERBASE_PROJECT_ID -u TERMINAL_SSH_KEY -u TERMINAL_SSH_HOST -u TERMINAL_SSH_USER -u TERMINAL_SSH_PORT -u RESEARCH_MEMORY_READONLY_DSN -u OPENAI_API_KEY hermes -p research-scout chat -q "Bounded non-authoritative research question" --quiet --source tool
```

Use the same command with `research-critic` for the second specialist. Their
external configurations allow only memory and session search; acceptance must
also check that credentials are absent and out-of-scope calls are denied.

## Manual research opportunity cycle

Use PowerShell 7.2+ and a new dedicated worktree descended from merged #733.
Inspect `docker compose ls` first. Choose a unique project and fresh external
home; never reuse another package's home, profiles, or Compose project. Authenticate
the fresh director home with native `hermes auth add openai-codex`; do not copy
auth stores, `.env` files or credentials from another deployment. Existing
Browserbase variables remain mandatory. No new purchase is authorized.

```powershell
$env:COMPOSE_PROJECT_NAME = 'cpw-hermes-research-turn-01'
$env:HERMES_PROJECT_HOME = 'C:\Hermes\research-turn-01' # fresh, external
./tools/hermes/start.ps1 -Mode F1F2 -HermesProjectHome $env:HERMES_PROJECT_HOME -HermesModel 'gpt-6.1'
# In this project's director container, authenticate and create both profiles:
docker compose -f tools/hermes/compose.yaml exec -T --user 10000:10000 hermes hermes auth add openai-codex --no-browser
docker compose -f tools/hermes/compose.yaml exec -T --user 10000:10000 hermes hermes profile create research-scout --no-skills
docker compose -f tools/hermes/compose.yaml exec -T --user 10000:10000 hermes hermes profile create research-critic --no-skills
```

Before invoking models, author each fresh external profile's `config.yaml` with
the accepted restricted configuration below, and a `SOUL.md` limiting it to
analysis of supplied source materials. Do not clone profiles or mirror auth.
Verify no director credential is present in either profile. Both specialists
use upstream model OAuth root fallback only; the wrapper strips director-only
credentials from their process environments.

```yaml
_config_version: 46
model: {provider: openai-codex, default: '${HERMES_MODEL}'}
toolsets: [memory, session_search]
platform_toolsets: {cli: [memory, session_search]}
agent: {max_turns: 4, coding_context: 'off'}
plugins: {enabled: []}
mcp_servers: {}
skills: {project_discovery: false}
curator: {enabled: false, consolidate: false}
auxiliary: {background_review: {enabled: false}}
delegation: {max_concurrent_children: 2, max_spawn_depth: 1, orchestrator_enabled: false, oneshot_max_children: 2, subagent_auto_approve: false, inherit_mcp_toolsets: false}
```

With the project still selected and profiles verified:

```powershell
./tools/hermes/research_turn.ps1 -OutputRoot 'C:\HermesReports\turn-01' `
  -RepoSha (git rev-parse HEAD) -RepoBranch (git branch --show-current) `
  -Theme 'BTCUSDT perpetual opportunities using existing five-timeframe evidence'
```

The output parent must exist; the destination must be new and external. The
command verifies exact repo identity and running service/worktree/home ownership,
then invokes director source collection, `research-scout`, `research-critic`,
and director synthesis once each, synchronously. Prompts travel through stdin,
never a shell. Each invocation has a timeout and no automatic retries. Native
session IDs, tool observations, source index, scout/critic outputs, brief and
artifact hashes are finalized by one directory rename. This is operational
evidence, not canonical scientific evidence. Inspect the sources and tool
observations before accepting usefulness; script completion alone is insufficient.

A missing/failed result or detected credential text returns nonzero and retains
a FAILED manifest and sanitized observations. A failure stops only the verified
project's director, including in-flight execs. It never publishes a success brief
for an incomplete cycle. Finish cleanup with `docker compose -f
tools/hermes/compose.yaml down` while the same unique project is selected;
leave unrelated services untouched. For another supervised cycle select a new
output directory. No schedules, trials, Prefect consumers, or scientific jobs
are invoked. F0 rollback still uses the unchanged `-Mode F0` surface described
above, with its own original home/project.

The following sections retain the historical F0 deployment description.

# Hermes H0/H1, H2/H2.5, and Typed CPW Domain Tools

This directory is the repo-owned deployment/configuration surface for pinned
Hermes Agent `v2026.8.13` (v0.20.1). The image is pinned by both tag and
multi-architecture digest:

```text
nousresearch/hermes-agent:v2026.8.13@sha256:68e15ae2a6d894d0ccbd9f8aacbbe13d4d28fa5dc9b6a303970b67bb2499b1a6
```

The Project-Evidence sidecar is built from a digest-pinned Python 3.11 image
and the repo lock file. Hermes gets no repository mount. The sidecar receives
only explicit read-only evidence mounts; it does not receive `src/`, `lib/`,
`configs/`, `secrets/`, `research/queue/`, dispatch/KDAUTH, OMS, risk,
reconciliation, paper/live, exchange, order, capital, or credential paths.

## Boundary

Project-Evidence is default-deny and exposes:

- explicit evidence URIs, never caller paths;
- four predeclared in-memory DuckDB queries, never caller SQL;
- parameterized Research Memory alias lookup through a DB-enforced read-only
  role whose mutation privileges are checked at connection time;
- a normalized allowlisted release/security watch with free-form upstream text
  discarded;
- exactly one project write surface: `scratch/hermes_proposal_outbox/`.

The outbox is proposal/prepared-record-only, gitignored, exclusive-create,
symlink/traversal
resistant, source/repo-SHA linked, and marked `not_authority=true`. Nothing in
runner, dispatch, KDAUTH, promotion, readiness, runtime, or protected code reads
the outbox. Hermes state under its separate `HERMES_HOME` is not project state.

H2 evolves the existing `submit_proposal` input into a strict seven-type
contract. Every proposal binds exact resource/query evidence identities, separates
FACT/INFERENCE/OPEN QUESTION, declares an A0/A1/A2 class from closed affected
domains, and requests only human review for a separate future work package.
Project-Evidence re-resolves every declared path/hash before persistence. A0 is
mandatory for protected or ambiguous scope; A2 is limited to explicitly low-risk
proposal domains and grants no standing authority. The outer outbox record and
the typed proposal both require human review and have no automatic consumer.

H2.5 adds exactly one tool, `submit_prepared_payload`, for seven closed inert
plan types. It independently finds a compatible H2 parent by proposal ID in
this fixed outbox, validates the nested H2 object, recomputes the parent content
hash over Hermes canonical UTF-8 JSON bytes with sorted keys and exactly one
trailing LF, re-resolves current evidence, preserves the parent's A0/A1/A2
class, and writes a distinct `HERMES-PREP-*.prepared.json` record. The prepared
payload hash covers only the nested validated payload, never its own hash or
outer metadata. A0 also requires `permanent_non_executable=true` and
`protected_human_gate_only=true`.

PREPARE is still inert human-review content. There is no executable payload,
approval token, broker, dispatcher, automatic consumer, Governor/Prefect/Codex
invocation, project or canonical mutation, dependency update, network hydration,
diagnostic execution, or runtime/trading action. H3 and H4 remain unstarted.

HERMES-01 adds five strict compute-only Project-Evidence tools for capability
assessment, reasoned-draft formalization, preregistration packet construction,
approval-requirement description, and trial-denominator validation. Hermes
provides generic reasoning; framework-neutral CPW domain functions remain the
single owner of research/scientific semantics. Project-Evidence re-resolves
repo inputs and binds every result to the exact repo SHA, repo path, and
artifact hash. Model content is untrusted reasoning input, not evidence. The
tools write no artifact and grant no canonical, approval, execution,
candidate/promotion, scheduler/Prefect, runtime/risk, paper/live, or capital
authority. H2/H2.5 behavior is unchanged. HERMES-02 01A adds one manually
triggered, fixed-command, non-authoritative bounded research-intent handoff.
Project-Evidence resolves exact evidence and performs exact read-only Research
Memory dedup before emitting a strict intent; the handoff stops before Governor,
Optuna, runner, canonical, promotion, runtime, paper/live, or capital authority.
HERMES-03 canary/runtime consolidation remains future work.

## One-time PostgreSQL role setup

Run `research_memory_readonly_role.sql` as the Research Memory database owner,
then set authentication for the fixed `hermes_research_memory_reader` role by
your normal secret-management process. Do not place its DSN in the repository
or the Hermes model-credential file. Pass only that role's DSN to `start.ps1`.

The sidecar sets `default_transaction_read_only=on`, issues `SET TRANSACTION
READ ONLY`, and refuses service if the role has any mutation privilege on the
four Research Memory tables. An absent DSN leaves the rest of MCP available and
causes Research Memory lookups to fail as UNKNOWN; it never falls back to a
write-capable DSN.

## Start

Use a project-specific home outside the repository. Authenticate that home with
the pinned Hermes native `openai-codex` device flow (`hermes auth add
openai-codex`), which stores its ChatGPT/Codex OAuth state only under the
external Hermes home. The deployment does not require or read
`OPENAI_API_KEY`.

```powershell
.\tools\hermes\start.ps1 `
  -Mode F0 `
  -HermesProjectHome C:\Hermes\crypto-perp-wedge `
  -HermesModel '<Codex model available to the authenticated plan>' `
  -ResearchMemoryReadOnlyDsn $env:RESEARCH_MEMORY_READONLY_DSN `
  -InstallSchedules
```

The script resolves the exact Git SHA/branch, rejects a repo-contained or linked
Hermes home, validates Compose, starts the pinned services, and idempotently
adds the three repo-owned schedule-plan jobs by name. It prints no DSN or model
credential. Compose runs the pinned Hermes CLI directly as its built-in
`hermes` user (UID/GID 10000) with Docker as the external supervisor; this
avoids granting the image's optional `s6` bootstrap any extra capabilities.

## Physical acceptance (required on the deployment host)

This repo cannot prove that a host has Docker, model credentials, or Research
PostgreSQL connectivity. On the intended Docker-capable host, run the command
above, then verify:

```powershell
docker compose -f tools\hermes\compose.yaml ps
docker compose -f tools\hermes\compose.yaml exec -T hermes hermes cron list
```

Exercise `project_evidence_manifest`, one allowed resource, one denied resource,
one allowed query, one denied query, one Research Memory lookup, one mutation
attempt (which must be rejected by the DB role), and one proposal. Restart both
containers and repeat the manifest/mount inspection. Do not report physical H0
acceptance until those checks pass.

## Reporting samples

`samples/daily-research-brief.md` and `samples/weekly-science-review.md` are
deterministic repo-only acceptance outputs anchored to base SHA
`12ea35c8a6cfc60fc439527104ad9a67a162e4fb`. They intentionally mark physical
deployment state UNKNOWN rather than fabricating it.
