# Bounded Research Agent Authority Model

## Status / Authority Boundary

`WP-LAB-AGENT-BOUNDARY-DESIGN-01` is a docs-only, Karl-gated design package.

This document designs a future bounded research-agent authority model. It does
not implement agents, orchestrators, schedulers, queues, LangGraph, Prefect,
Claude Agent SDK integration, automation code, ToolContext code, schemas,
validators, query behavior, runtime behavior, or dashboard controls.

This document grants no canonical-write authority, candidate registration,
promotion, freeze, approval, readiness, paper/live, runtime, OMS, risk,
reconciliation, safe-mode, kill-switch, broker, exchange, order, capital,
credential, private-endpoint, or dependency authority.

This document requires Karl blessing before any agent implementation WP starts.

## Repo-Truth Basis

Facts:

- `docs/project_status.md`, `CLAUDE_START_HERE.md`, `docs/runbook.md`, and
  `AGENTS.md` preserve current repo truth over memory and chat summaries.
- `docs/architecture/2026-06-side12-external-adoption-pilot-plan.md` preserves
  external tools as scratch-only, advisory, repo-controlled, and unable to
  grant canonical, runtime, paper/live, promotion, approval, ranking,
  recommendation, or execution authority.
- `docs/status_entries/WP-PILOT-NOTIFICATIONS-APPROVALS-01.md` and
  `docs/status_entries/WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01.md` are absent on
  current `origin/main` at the time of this package.
- `docs/status_entries/WP-LAB-IDEA-INTAKE-FORMALIZATION-01.md` records a
  deterministic, local, draft-only formalizer whose outputs carry
  draft/non-authority flags and whose draft-to-preregistration path remains a
  human-gated future option.
- `docs/status_entries/WP-LAB-WALKFORWARD-RUN-01.md` records a deterministic
  scratch-only walk-forward helper; the first canonical walk-forward run still
  requires explicit GO and Karl gate.
- `docs/architecture/candidate_lifecycle_design.md` records candidate lifecycle
  records as evidence indexes and human-review workflow records only, with no
  execution authority.
- `docs/architecture/2026-06-two_lane_sandbox_wall.md` preserves the wall
  between canonical research/evidence and sandbox or paper engineering.
- `docs/research_pipeline/2026-05-permanent_human_gate_preservation_sketch.md`
  states that no bot, agent, dashboard, monitor, validator, bridge, report,
  score, recommendation, or automation may execute a permanent human gate.
- `docs/dashboard/README.md` states that dashboard surfaces are display-only
  and confer no ranking, recommendation, readiness, promotion, approval, or
  execution authority.

Inference:

- Future research agents can safely reduce operator toil only if they are
  treated as tool users inside a constrained context, not as owners of repo
  authority.
- The same governance rules that protect canonical evidence from a bad work
  package must also protect canonical evidence from a bad agent.

Decision:

- Agents are agent-operated, not agent-authorized.
- Agent output may inform human review only after repo-owned validation and
  boundary checks.
- Any future agent must run behind an explicit ToolContext-style enforcement
  layer before it can receive file, command, network, issue, PR, or notification
  capability.

Open question:

- The exact future storage path, schema, validator, and query surfaces for
  agent audit logs remain deferred to later implementation packages.

## Principle

Agents are agent-operated, not agent-authorized.

Repo governance that protects canonical evidence from a bad WP also protects it
from a bad agent. A future agent may gather context, propose drafts, run
scratch-only tooling, summarize evidence, or notify humans only inside a
bounded capability set. It may not decide, approve, promote, freeze, register,
execute, hide failures, or rewrite repo truth.

## Future Agent Role Taxonomy

The role names below are design labels. They are not implementation classes,
agent prompts, schemas, or executable contracts.

| Role | Purpose | Allowed future output posture | Explicit non-authority |
|---|---|---|---|
| Research scout | Finds repo-relevant prior docs, current artifacts, open blockers, and external public references when later authorized. | Notes, source lists, gap summaries, draft issue text. | No evidence selection, ranking, recommendation, candidate registration, or canonical writes. |
| Idea formalizer | Converts a human-provided idea into a structured draft using repo grammar and current capability limits. | Draft research-idea records, rejection reasons, upgrade-dependent labels, scratch workflow inputs. | No preregistration, Strategy Spec creation, candidate registration, freeze, or approval. |
| Draft generator | Prepares draft Strategy Spec, Variant Manifest, Sweep Plan, report, PR, or issue text for human review. | Scratch drafts or PR/issue drafts only if a later package grants that surface. | No canonical artifact mutation, no self-merge, no approval, no hidden failed variants. |
| Non-canonical runner | Invokes approved scratch-only validators, dry-runs, compile probes, or non-canonical run helpers. | Scratch reports, logs, deterministic run summaries, blocker diagnostics. | No trial-log writes, no canonical result populations, no canonical walk-forward evidence. |
| Robustness diagnostician | Produces advisory robustness, concentration, cost, sensitivity, or overfit diagnostics from already authorized inputs. | Scratch/advisory diagnostic reports with full-denominator disclosure. | No screen-gate pass/fail authority, no readiness, no ranking, no promotion. |
| Candidate-review packet preparer | Bundles existing evidence links and open questions for a human candidate review gate. | Review packet drafts, checklist summaries, missing-evidence lists. | No candidate registration, lifecycle transition, approval, demotion, rejection, or freeze. |
| Notification assistant | Sends or drafts human notifications about blockers, needed approvals, completed validations, or review queues when later authorized. | Human-readable notifications and audit records. | No auto-approval, no dashboard execution controls, no paper/live or runtime trigger. |

## Allowed Future Actions

These are future options only. A later implementation package must explicitly
authorize the role, tool surface, paths, and validation profile before any of
these actions can run.

Allowed future actions may include:

- research and summarize current repo truth;
- propose next steps as drafts;
- classify ideas against current repo capability and forbidden scope;
- generate scratch artifacts under approved scratch paths;
- run non-canonical validations and dry-runs;
- run compile probes without writing canonical artifacts;
- summarize committed evidence and missing prerequisites;
- diagnose blockers and validation failures;
- prepare human review packets;
- notify humans or draft notification content;
- open draft issues or draft PRs only if a later package explicitly grants that
  capability and records the required audit event.

Allowed actions must preserve:

- deterministic behavior where practical;
- complete-denominator and no-file-drawer posture;
- source references and provenance;
- explicit scratch/non-canonical/advisory labels;
- repo-truth precedence over model output;
- human gates for every authority-bearing decision.

## Hard Prohibitions

No future agent may do any of the following unless a later Karl-blessed repo
truth explicitly changes the prohibition for a narrow surface:

- write canonical artifacts;
- freeze canonical artifacts;
- register a candidate without a human gate;
- promote, demote, reject, retire, approve, or declare readiness for a
  candidate;
- approve paper, shadow, live, runtime, or capital use;
- start, stop, pause, reset, or control paper/live/runtime paths;
- use private endpoints;
- use credentials or secrets;
- call order, account, balance, position, margin, leverage, transfer, broker,
  exchange, OMS, reconciliation, or risk-cap methods;
- change OMS, risk, reconciliation, capital, safe-mode, kill-switch, event-log,
  overlay, broker, exchange, order, or live-trading semantics;
- change paper ledger accounting math;
- change protected runtime configs or live-trading paths;
- delete, rewrite, hide, or suppress failed evidence;
- report winners only;
- convert dashboard displays into approval or execution controls;
- change dependency files unless an active package explicitly authorizes that
  dependency work;
- bypass validators, integrity checks, or package report-back requirements;
- treat LLM output, score output, ranking output, notification output,
  dashboard output, query output, or a passing validation as authority.

## Gate Model

| Gate class | Examples | Required owner | Agent posture |
|---|---|---|---|
| Karl-gated actions | Canonical writes, first canonical walk-forward run, candidate registration, promotion/freeze, funding-into-backtest cost-model changes, agent authority expansion, paper/live/runtime work. | Karl, with Main/user involvement where repo truth requires it. | Agent may prepare evidence packet only. It cannot execute the gate. |
| Main-gated actions | Work-package scoping, package sequencing, repo-owned design acceptance, external-tool adoption posture, non-protected implementation scope. | Main or explicitly delegated human reviewer. | Agent may summarize options, constraints, and blockers. |
| Human approval queue actions | Draft issue/PR submission, approval request notification, review packet completion, operator attention notices. | Named human or approved queue owner. | Agent may draft or notify only after a later package grants the surface. |
| Audit-only actions | Scratch run summaries, blocked-action records, read-only inspections, dry-run diagnostics. | ToolContext audit policy and package reviewer. | Agent may perform within allowlist and must emit an audit record. |
| Blocked actions | Runtime/paper/live control, private endpoints, credentials, order/account/balance/position methods, hidden deletion, winner-only reporting, dashboard execution controls. | No owner inside this design. | Agent must stop, record the blocked action, and report escalation need. |

Gate failures must be preserved as evidence. A blocked action record is not a
failure to be hidden; it is an audit artifact for boundary review.

## Enforcement Concept

This section is non-code design only.

### ToolContext

Future agents should receive a ToolContext object or equivalent enforcement
wrapper before they receive any tool. The context should bind:

- package id;
- role id;
- branch and worktree;
- base commit;
- allowed command classes;
- allowed read paths;
- allowed write paths;
- blocked paths;
- network posture;
- credential posture;
- canonical-write posture;
- dry-run or scratch-only mode;
- audit-log destination;
- human approval interrupt policy.

ToolContext must be constructed from repo truth and active package scope, not
from agent preference.

### Capability allowlist

Capabilities should be closed by default. A role receives only the capabilities
it needs for the active package.

Example capability families:

- `read_repo_docs`;
- `search_repo`;
- `read_non_secret_files`;
- `write_scratch`;
- `run_read_only_validation`;
- `run_scratch_tool`;
- `draft_issue`;
- `draft_pr`;
- `send_notification`.

Capabilities that should be absent by default:

- canonical artifact write;
- dependency mutation;
- network access;
- authenticated API access;
- runtime control;
- broker/exchange access;
- dashboard control creation;
- merge or release action.

### Path allowlist and blocklist

Future implementations should combine a narrow allowlist with a hard blocklist.

Allowed path classes may include:

- active package docs paths;
- package-specific scratch paths;
- read-only repo docs and source paths required for discovery;
- generated local logs under an explicitly approved scratch location.

Blocked path classes must include, at minimum:

- runtime, paper, live, OMS, risk, reconciliation, safe-mode, kill-switch,
  broker, exchange, order, and capital paths;
- canonical Strategy Specs, Variant Manifests, Sweep Plans, Result Populations,
  trial log, canonical walk-forward evidence, and candidate registry paths,
  unless a later package explicitly grants a narrow human-gated write path;
- dependency files unless explicitly scoped;
- credential, secret, `.env`, and private config paths;
- `docs/project_status.md` unless explicitly scoped and collision-checked.

### Write-mode restrictions

Supported future write modes should be explicit:

- `read_only`: no writes;
- `scratch_only`: writes only to approved scratch paths;
- `draft_docs`: writes only to approved docs/status paths in a docs package;
- `draft_issue_pr`: drafts external text only, with no merge/approval action;
- `canonical_write`: blocked unless a specific future Karl-gated package grants
  a human-approved, validator-backed write surface.

`canonical_write` must never be inferred from a role name or a successful run.

### Dry-run and scratch-only modes

Dry-run mode should be the default for any tool that can otherwise write. A
future agent may request write escalation only through a human approval
interrupt and only if the active package allows that path.

Scratch-only mode must label outputs as:

- scratch-only;
- non-canonical;
- advisory;
- not ranking authority;
- not recommendation authority;
- not readiness authority;
- not approval authority;
- not promotion authority;
- not paper/live/runtime authority.

### Audit log

Every agent action should be auditable. A future audit record should include:

| Field | Purpose |
|---|---|
| `timestamp_utc` | When the action was attempted. |
| `wp_id` | Active package id. |
| `agent_role` | Role receiving the capability. |
| `tool_name` | Tool or command family invoked. |
| `capability` | ToolContext capability used. |
| `mode` | Read-only, dry-run, scratch-only, draft-docs, or blocked. |
| `inputs` | Redacted input summary and source refs. |
| `outputs` | Output refs, checksums where relevant, or no-output marker. |
| `decision` | Allowed, blocked, or interrupted for human approval. |
| `reason` | Scope reason or block reason. |
| `non_authority` | Declaration that the record creates no gate, approval, promotion, paper/live, runtime, or execution authority. |

Audit logs must not contain secrets.

### Blocked-action record

When an agent attempts or is asked to perform a blocked action, ToolContext
should refuse the action and emit a blocked-action record containing:

- requested action;
- role;
- active package;
- violated capability or path rule;
- relevant forbidden boundary;
- whether human escalation is possible;
- no side effects performed.

Blocked actions should be reported to the human operator and preserved for
review.

### Human approval interrupt

Some actions are neither automatically allowed nor permanently blocked. A
future ToolContext should pause and request human approval for:

- draft issue or PR creation if not already granted by package scope;
- write escalation from dry-run to scratch-only;
- notification sending outside pre-approved channels;
- expanded read access to sensitive non-secret areas;
- any ambiguity about canonical or protected-path contact.

Human approval interrupts cannot approve protected runtime or canonical
authority unless a later Karl-gated package has already created that authority.

## Stop Conditions

Any future agent package must stop and escalate if safe implementation requires:

- touching runtime, paper, live, OMS, risk, reconciliation, safe-mode,
  kill-switch, broker, exchange, order, capital, credential, private endpoint,
  dependency, schema, validator, query-layer, canonical artifact, candidate
  registry, trial-log, or `docs/project_status.md` paths without explicit
  authorization;
- granting an agent authority to approve, promote, freeze, register, rank,
  recommend, or declare readiness;
- creating auto-approval;
- creating dashboard execution controls;
- hiding failed variants or reporting winners only;
- using live LLM/network/private APIs without a separately approved safe
  adapter and redaction policy;
- changing package intent from docs/design to implementation;
- relying on missing status entries or unmerged branch assumptions as current
  repo truth.

## Phase C Future Implementation Sequence

The following are future options, not current authorization.

1. `WP-LAB-AGENT-TOOLCONTEXT-01`: implement a minimal ToolContext enforcement
   wrapper with capability allowlist, path allowlist/blocklist, dry-run default,
   and blocked-action refusal.
2. `WP-LAB-AGENT-AUDIT-LOG-01`: add schema/validator and fixtures for
   append-only agent action and blocked-action audit records.
3. `WP-LAB-AGENT-IDEA-FORMALIZER-01`: wrap the existing deterministic idea
   formalization path behind ToolContext and audit logging, preserving
   draft-only output.
4. `WP-LAB-AGENT-RUNNER-NONCANONICAL-01`: allow a bounded role to run approved
   scratch-only compile probes or non-canonical validations, with no canonical
   writes and no trial-log writes.
5. `WP-LAB-AGENT-ROBUSTNESS-DIAG-01`: allow advisory robustness diagnostics
   over approved committed evidence, preserving no ranking or gate authority.
6. `WP-LAB-AGENT-CANDIDATE-REVIEW-01`: prepare human candidate-review packets
   from existing evidence links without candidate registration or lifecycle
   transition authority.
7. `WP-LAB-AGENT-NOTIFICATION-ASSISTANT-01`: notify humans about blocked
   actions, completed validations, or approval queues only after notification
   channel boundaries are locked.

Any future implementation split must start from refreshed repo truth and must
carry its own validation, boundary check, and Karl/Main gate posture.

## Acceptance / Blessing Statement

This document requires Karl blessing before any agent implementation WP starts.
