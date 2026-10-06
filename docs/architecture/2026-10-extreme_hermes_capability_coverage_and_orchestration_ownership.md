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

## Independent review and draftability dependency

The independent `EXTREME-HERMES-01` security review remains mandatory and
separate. It must cover director/execution-sandbox separation, terminal/file/
code isolation, Bot profile isolation and collaboration, plugin governance,
MCP provenance/tools/credentials, memory/session search, self-improving skills,
delegation containment, network/egress, filesystem/mounts, provider/auth
credentials, live tool-schema verification, rollback, and Computer Use
deferral. This decision neither replaces nor satisfies that gate.

After D2-025 is merged unchanged and the independent review returns PASS or
PASS WITH REQUIRED CORRECTIONS incorporated into the planned package, Side
should perform only a narrow final draftability check. Unless the review finds
a material architecture flaw or repo truth changes, the expected result is
`EXTREME-HERMES-01 Draftable: YES`; no broad new research round is required.

## Zero activation

D2-025 grants no Hermes upgrade, tool enablement, Bot creation, plugin/MCP
installation, cron/routine activation, Computer Use activation, Stage 5B,
autonomous scientific execution, code/runtime change, paper/live access,
exchange/order authority, credential authority, or capital authority.
