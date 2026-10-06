# Extreme Hermes Capability Coverage and Orchestration Ownership

## Status and authority

- Status: **LOCKED ADDENDUM / CAPABILITY-ROADMAP AUTHORITY**.
- Package: `WP-EXTREME-HERMES-D2-025-CAPABILITY-COVERAGE-01`.
- Decision: `D2-025 — Extreme Hermes Capability Coverage and Orchestration Ownership`.
- Exact base: `c40dc2caf7d725c12163a3841d6bf55b65546291`.
- Authority class: architecture and roadmap only.

This record is an addendum to D2-024. D2-024 remains controlling for the
Extreme Hermes target, broad-capability-sandbox/narrow-authority-gateway model,
F0-F7, permanent restrictions, external isolation, and roadmap. This addendum
makes capability coverage and orchestration ownership explicit so later
packages do not mistake the first canary for the final capability ceiling.

> **Hermes becomes an always-on autonomous research director and persistent
> research organization, not merely a research interface.**

This record activates nothing. It changes no deployed Hermes version,
configuration, tool surface, Bot, plugin, MCP server, routine, schedule,
Computer Use surface, code, dependency, scientific policy, protected runtime,
paper/live behavior, credential, or capital authority.

## Capability coverage authority

The full useful capability set remains on the roadmap even when a capability
is deliberately absent from the F1/F2 canary. A future package must not
silently remove a capability merely because it is sequenced later.

| Capability | Roadmap state | Locked decision |
| --- | --- | --- |
| Web / search | **F1/F2 canary** | Core external research/scouting. Public internet only; private/LAN/metadata remain blocked. |
| Browser | **F1/F2 canary** | Preferred for interactive web research when APIs/MCP are insufficient. |
| Terminal | **F1/F2 canary** | Only through an isolated research execution sandbox, never the credential-bearing director environment. |
| Python / code | **F1/F2 canary** | Only through an isolated research execution sandbox. |
| Files | **F1/F2 canary** | Broad sandbox file freedom; protected repo/runtime paths remain unavailable for write. |
| Persistent sessions | **F1/F2 canary** | Required for director continuity and long-running research. |
| Built-in Hermes memory | **F1/F2 canary** | Operational/working memory only; never scientific truth. |
| External memory provider | **Later Stage 5B — conditional** | Only reviewed/pinned providers that measurably improve recall; never replace Research Memory or CPW lineage. |
| Session search | **F1/F2 canary** | Retrieval over prior Hermes sessions; non-authoritative. |
| Skills | **F1/F2 canary** | Reusable procedural research knowledge in isolated Hermes skill stores. |
| Self-improving skills | **F1/F2 canary, controlled writes first** | Prove create/update/audit/rollback; skill content cannot grant tools, credentials, or authority. |
| Ephemeral delegation | **F1/F2 canary** | Flat and bounded first. |
| Persistent Bot Mode specialists | **F1/F2 canary** | Explicitly adopted; small representative persistent research team first. |
| Bot-to-Bot / group collaboration | **F1/F2 canary** | Bounded pilot; useful for specialist review and director synthesis. |
| Nested delegation | **Later Stage 5B — conditional** | Only if measured benefit justifies complexity/cost; bound depth/concurrency. |
| Hermes cron / routines | **Later Stage 5B** | Intelligence wake-ups, monitoring, scouting, follow-up reasoning, alerts, daily/weekly reports. |
| Plugins | **F1/F2 canary — curated only** | Reviewed/pinned/allowlisted; no arbitrary self-install/update. |
| MCP integrations | **F1/F2 canary — curated only** | Expand beyond Project-Evidence with reviewed research/data/observability/dev MCPs; authority APIs remain narrow. |
| Computer Use | **Later Stage 5B — conditional** | Browser/API/MCP preferred; only adopt where GUI materially adds value, in a dedicated GUI sandbox. |
| Git / repo inspection | **F1/F2 canary** | Read/inspect repo and Git state. |
| Git / repo engineering writes | **Lab Engineer / F6** | Non-protected research tooling only, disposable worktrees/branches, tests and PR preparation; human merge required. |
| Observability / alerts | **Later Stage 5B** | Persistent lab/data/strategy-health supervision; read-only canary probes may precede activation. |
| Reporting | **Later Stage 5B** | Scheduled daily/weekly reports and useful alerts; manual generation may be proven earlier. |

## Browser execution isolation

Upstream Hermes Browser Use can expose `browser_exec`, which executes
model-written Python and is gated by terminal capability. The project must not
assume that giving the director browser access while withholding an ordinary
terminal prevents local browser code execution.

Browser research is allowed, but model-written browser execution must not run
in or gain access to the credential-bearing Hermes director environment.
`EXTREME-HERMES-01` must select and prove an accepted topology, such as a
reviewed cloud/remote browser backend, browser execution inside the isolated
research execution sandbox, or an equivalent independently reviewed topology.
This docs package does not choose the final browser backend.

Physical acceptance must inspect the live effective browser/tool behavior;
configuration labels are not proof. It must prove browser-execution code cannot
reach director `HERMES_HOME`, director/provider authentication material,
private/LAN/metadata/control-plane networks except an explicitly reviewed
narrow internal exception, or protected repo/runtime write surfaces.

## Persistent research organization

Extreme Hermes uses both persistent specialist Bots/profiles and ephemeral
delegated subagents. Persistent Bot Mode is a first-class research-organization
primitive, not an optional UI convenience.

The target organization may include Director / Supervisor, Strategy Discovery,
Statistical Critic, Data / Feature Researcher, Strategy Health Analyst,
Robustness Reviewer, Market / Academic Research Scout, and Lab Improvement
Engineer roles. This is a target model, not a requirement to create every role
in `EXTREME-HERMES-01`.

The F1/F2 canary should prove only a small representative roster sufficient to
validate profile isolation, role-specific instructions, memory, skills, models
where useful, tool/MCP access, Bot-to-Bot messaging, bounded group
collaboration, director synthesis, and credential separation. No Bot may widen
its own tool, MCP, credential, authority, or protected-path access.

Specialist Bots receive only explicitly reviewed minimum credentials.
Automatic credential copying or cloning from the director profile is disabled:
no Bot receives live/exchange/capital credentials or automatically receives
the director's complete provider/API-key set. Each Bot's provider/model and
tool/MCP credentials are independently reviewed. Bot creation or cloning must
not silently widen credential access, and delegated children cannot acquire or
widen credentials beyond those held by their parent.

`EXTREME-HERMES-01` physical acceptance must create a representative specialist
Bot/profile with automatic main-profile key copying disabled, inspect its
effective credential store and environment, prove director-only secrets are
absent and only approved minimum credentials are present, and repeat the proof
with a second role having a different minimum credential set. It must also
prove clone/profile creation does not restore director-wide keys and ephemeral
delegates cannot gain credentials their parent lacks.

The persistent specialist organization is built on the underlying Hermes
profile/Bot primitive and must remain CLI/service/headless compatible. Hermes
Desktop Bot Mode is optional operator UI only. The future research VPS must be
able to operate the organization without an interactive Desktop session through
supported profile/service/gateway mechanisms, with profile-scoped
configuration, memory, skills, tools/MCP, credentials, routines, and supported
Bot/profile communication. Desktop may support configuration, visualization,
inspection, manual intervention, and group-chat UI, but it must not become a
runtime dependency for the autonomous factory.

## Persistent Bots and ephemeral delegation

Ephemeral delegated subagents serve short investigations, parallel literature
or repo scans, one-off statistical critique, bounded review, and temporary
decomposition. The initial canary uses flat delegation, low fixed concurrency,
and no nested orchestration.

Persistent Bots serve work where continuity improves research quality:
specialist memory, recurring role identity, recurring routines, persistent
domain skills, long-lived responsibility, Bot-to-Bot collaboration, and group
deliberation. The target is a persistent research organization, not one
director that only spawns disposable helpers.

Nested delegation remains conditional. It may be introduced only when measured
benefit exceeds flat delegation plus persistent Bots and when depth,
concurrency, cost, runtime, inherited capabilities, failure visibility, and
auditability are bounded.

## Hermes routines and Prefect ownership

Hermes cron/routines own **intelligence wake-ups**: overnight market or
research scans; paper, repository, release, data-health, strategy-health,
experiment-result, unresolved-research, and lab-bottleneck review; alerts; and
daily or weekly reports. After Stage 5B activation, a wake-up may lead Hermes
to request the next legal research action through CPW.

Prefect owns **durable scientific/research workflow execution**: experiment
execution, workers, queues, operational retries, durable flow/run state,
restart/recovery, and long-running scientific jobs.

Hermes cron is not a parallel scientific scheduler, scientific retry owner,
experiment-state authority, substitute for Prefect run state, substitute for
Search Governor legality, or substitute for CPW lineage. This decision does
not activate autonomous cron research.

## Plugin governance

Plugins are an intended extensibility mechanism and are privileged because
they execute inside Hermes. Every enabled plugin must be reviewed, explicitly
allowlisted, provenance-recorded, capability- and hook-reviewed,
credential-reviewed, and pinned to an exact immutable source where technically
available. Hermes may not arbitrarily self-install or self-update plugins, and
unreviewed project-local plugin execution is forbidden.

No plugin may create scientific, protected-runtime, live, or capital authority.
`EXTREME-HERMES-01` may prove this governance with one benign reviewed plugin
or equivalent controlled fixture; it need not install a broad collection.

## Curated MCP expansion

Project-Evidence-only MCP is a proof boundary, not the permanent ceiling.
Future curated MCPs may support research systems, data systems, observability,
development, documentation, and other research-support services.

Each MCP requires reviewed server provenance, reviewed/pinned version or source
where possible, explicit configuration and tool filters, explicit credential
handling, and live effective-tool inventory verification. Hermes may not
dynamically install arbitrary MCP servers, and MCP output is not automatically
scientific truth. Authority-bearing CPW interfaces remain narrow, typed, and
fail-closed. Project-Evidence remains important without being the permanent
total MCP surface.

## Memory ownership hierarchy

| Layer | Purpose | Authority |
| --- | --- | --- |
| Hermes built-in memory | Director working context, operational preferences, lab operating context, and learned non-scientific facts. | **Non-authoritative.** |
| Persistent Bot memory | Role-specific accumulated working context and specialist continuity. | **Non-authoritative.** |
| Session search | Retrieval over prior Hermes sessions. | **Non-authoritative.** |
| Skills | Procedural memory, reusable methods, and how-to knowledge. | **Non-authoritative.** |
| Optional external memory provider | Improved retrieval/organization when a reviewed provider demonstrates measurable value. | **Non-authoritative; conditional after Stage 5B and never a replacement for Research Memory or CPW lineage.** |
| Research Memory | Experiment/research-history retrieval and deduplication context. | **Non-authoritative research index; CPW revalidates evidence before scientific use.** |
| CPW durable scientific lineage | Campaign, search, trial, holdout, budget, and contamination history. | **Authoritative scientific truth.** |

No Hermes memory layer may overwrite, reset, reinterpret, or replace CPW
durable scientific lineage.

## Self-improving skills

Self-improving skills are an intended capability. Hermes should eventually be
able to create reusable research skills, improve them after repeated failures
or successes, build specialist workflows, retain investigation procedures, and
improve edge-search methods and research-factory operation.

The F1/F2 canary permits create/update only in isolated Hermes skill storage,
with write approval, auditable changes, and demonstrated rollback. Validation
must prove that skill content cannot widen tools, MCP, credentials, filesystem
scope, scientific authority, or protected-runtime authority. Later packages
may relax approval cadence only after this containment is proven.

Skills improve how Hermes works. They do not redefine what is scientifically
true or legal.

## Computer Use posture

Computer Use is preserved as a conditional future capability and is excluded
from the first `EXTREME-HERMES-01` F1/F2 canary. The preference order is API,
MCP, browser automation, then Computer Use only when a GUI adds material value.

Any later adoption requires a dedicated GUI sandbox, a reviewed bounded
capability manifest, no protected host desktop, no exchange/broker/live-capital
application access, no protected credentials, explicit physical acceptance,
and independent security review of the GUI boundary. Deferral reflects the
larger OS/UI attack surface, authenticated-app exposure, and platform/session
complexity; it is not permanent rejection.

## Multi-agent depth

The F1/F2 canary includes persistent Bots, flat delegated subagents, low fixed
concurrency, no nested delegation, and no capability widening by children.
Delegated children also cannot widen or acquire credentials beyond the parent.

Later packages may add richer Bot groups, a broader specialist roster,
director synthesis, orchestrator children, or nested delegation only when
measurements demonstrate material research-quality or productivity value.
They must bind maximum spawn depth, concurrent children, token/cost budget,
runtime budget, inherited capability containment, failure visibility, and
auditability.

## Observability, alerts, and reporting

Before Stage 5B, only read-only/manual proofs are permitted; no always-on
autonomous monitoring authority is implied. After separately authorized Stage
5B activation, Hermes should supervise data health, strategy health,
experiment failures, lab bottlenecks, research queue state, relevant external
research, and dependency/security/release changes, producing actionable alerts,
daily briefs, weekly reviews, and unresolved-research follow-ups.

Reports summarize and interpret authoritative evidence. They are not
scientific authority.

## Relationship to D2-024 and `EXTREME-HERMES-01`

D2-024 remains controlling and its permanent scientific, protected-runtime,
and economic boundaries are unchanged. D2-025 adds capability-completeness and
ownership detail and prevents first-canary exclusions from becoming silent
permanent omissions.

`EXTREME-HERMES-01` should target a representative F1/F2 canary: web/search,
browser, sandbox terminal/Python/files, persistent sessions, built-in memory,
session search, skills, controlled self-improving-skill proof, flat delegation,
a small persistent Bot roster, bounded Bot-to-Bot/group proof, curated plugin
governance proof, curated MCP expansion proof, repo/research inspection, and
Project-Evidence / Research Memory context.

The first canary excludes Stage 5B, autonomous scientific execution,
autonomous cron research, nested delegation, broad external-memory-provider
adoption, Computer Use, Lab Engineer code writes, paper/live, and economic
authority. These are sequencing decisions, not permanent rejection.

## Upstream tool-scope constraint and live-behavior proof

Hermes `v2026.9.24 / v0.21.5` must not be accepted unchanged merely because it
is a stable release. The project has independently verified that the upstream
tool-scope fix associated with issue `#121089` and commit
`59559b858fb1a4578f51029112099462a431c3f1` is not contained in that stable
tag. `EXTREME-HERMES-01` must select either a later reviewed stable release
that contains the required fix or an explicitly reviewed pinned build/backport
containing the required fix. This docs package does not select the final
version; the implementation package must refresh upstream truth immediately
before selecting the canary pin.

Hermes YAML/toolset configuration is defense-in-depth only. The F1/F2 canary
must validate the actual effective and reachable tool surface. A capability
marked disabled in configuration that remains reachable is a failed canary
unless external isolation renders it physically harmless and Side 21
explicitly accepts that exact behavior.

## Security review and draftability dependency

For the `EXTREME-HERMES-01` F1/F2 canary, Karl has explicitly waived an
external independent reviewer as a mandatory prerequisite. Side 21 security
review plus mandatory physical canary acceptance is the controlling
pre-implementation security gate.

No security requirement is removed. Side 21 must ensure the final work package
and physical acceptance cover:

- director versus execution-sandbox separation;
- no Docker socket;
- no live, exchange, or capital credentials;
- filesystem and protected-path isolation;
- network/private/LAN/metadata blocking;
- browser-execution isolation;
- live effective-tool-schema verification;
- Bot minimum-credential isolation and disabled automatic director-key cloning;
- delegation containment;
- plugin and MCP governance;
- memory and skill non-authority;
- headless/VPS Bot operation; and
- rollback.

External independent security challenge remains a useful later gate and should
be performed before `EXTREME-HERMES-02` / Stage 5B autonomous scientific
activation, or earlier if Side 21 detects a material unresolved security
uncertainty. It is deferred, not permanently abandoned, unless Karl explicitly
changes that later gate.

After D2-025 merges and Side 21 confirms the final implementation package
contains the accepted security controls and physical acceptance tests,
`EXTREME-HERMES-01` may be `Draftable: YES` without another broad research
round.

## Zero activation

D2-025 grants no Hermes upgrade, tool enablement, Bot creation, plugin/MCP
installation, cron/routine activation, Computer Use activation, Stage 5B,
autonomous scientific execution, code/runtime change, paper/live access,
exchange/order authority, credential authority, or capital authority.
