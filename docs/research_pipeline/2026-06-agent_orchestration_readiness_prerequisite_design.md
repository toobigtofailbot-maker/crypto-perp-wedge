# Agent Orchestration Readiness Prerequisite Design

## 1. Scope

WP-S2c-168 / WP-12go is a Tier 1 documentation-only prerequisite design package.

It defines future Strategy Research Lab agent orchestration readiness as support-workflow design only.

This package creates only this document and updates `docs/project_status.md`.

It does not authorize lab implementation, agent implementation, `.claude/` changes, prompts, schemas, validators, query views, artifacts, code, tests, tools, runners, sweeps, dashboards, storage paths, runtime behavior, paper/live behavior, protected-path changes, recommendation authority, approval authority, readiness authority, transition authority, ranking/scoring authority, or human-gate execution.

## 2. Repo-Truth And Decision Basis

Repo truth for this design is refreshed `main` after WP-S2c-167 / WP-12gn.

Primary basis:

- WP-S2c-147 defines the Strategy Research Lab lifecycle from idea intake to advisory ranked output.
- WP-S2c-151 locks Strategy Spec as the future human-reviewable surface and Strategy DSL as constrained, declarative, non-executable representation discipline.
- WP-S2c-158 locks future variant population manifests as pre-registration surfaces and locks complete result-population preservation.
- WP-S2c-159 through WP-S2c-161 preserve anti-overfit review, advisory ranking, and Scope 6 / R2S as human-review support only.
- WP-S2c-162 defines lab-agent roles as bounded support-only concepts.
- WP-S2c-164 defers lab implementation and requires prerequisite design before any implementation tranche.
- WP-S2c-165 and WP-S2c-166 define validity, backtest-realism, bounded-search, walk-forward-first, DSR / PSR / MinTRL, and Strategy Spec / DSL expressiveness-readiness prerequisites.
- WP-S2c-167 defines provenance, audit, lineage, agent operation provenance, and partial-failure / recovery provenance as evidence-trail concepts only.
- EXP / REP, trial-log, OL, REC, and DEC remain canonical evidence and decision surfaces.
- D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6, WP-S2c-100, WP-S2c-113, and permanent human gates remain preserved.

Current merged repo truth wins over external research, memory, summaries, handoffs, or generic best practice.

## 3. Design Objective

The objective is to define what must be true before future bounded lab-support agents can be coordinated safely.

The design covers handoff protocols, shared-state discipline, provenance integration, human-in-the-loop checkpoints, partial-completion and failure recovery, conflict handling, fail-closed behavior, and permission boundaries.

It does not choose an implementation architecture, define exact agent prompts, create tool permissions, create orchestration code, create workflows, create state machines, create task queues, or authorize any artifact-writing surface.

## 4. Non-Authority Boundary

Agent orchestration readiness is not authority.

Agents are support-only.

Orchestration is support workflow only.

No agent or orchestration path can approve, promote, reject canonically, execute gates, alter readiness, trigger transitions, update registry state, mutate canonical evidence, run sweeps, rank with authority, recommend execution, contact runtime, contact paper/live paths, or touch protected paths.

Human gates remain human gates.

Advisory ranking remains human-review support only.

Scope 6 / R2S remains human-gated.

Bot proposes; humans decide where repo truth requires human review.

Implementation remains unauthorized.

## 5. Relationship To WP-S2c-162 And WP-S2c-167

WP-S2c-162 defines bounded future lab-agent roles and what those roles must never decide, execute, or authorize.

WP-S2c-167 defines the provenance trail that future support outputs and agent operations must preserve.

This document connects those two prior designs by defining readiness criteria for coordinating support roles without turning them into approvers, artifact authorities, runner operators, dashboard operators, or runtime actors.

It does not modify either prior design.

## 6. Agent Orchestration Readiness Definition

Agent orchestration readiness is the future ability to coordinate bounded support roles while preserving provenance, human review, scope control, and fail-closed behavior.

It means future packages can reason about handoff, shared context, partial failure, disagreement, and human review before any implementation is considered.

It does not mean autonomous agents, agent implementation, prompt creation, `.claude/` changes, tool creation, artifact writes, runner invocation, dashboard operation, approval, promotion, readiness, transition, gate execution, or runtime/paper/live authority.

Readiness is a prerequisite design concept only.

## 7. Bounded Lab-Agent Roles

Future support roles may include these design concepts:

- concept summarization support;
- Strategy Spec drafting support;
- completeness-check support;
- variant-idea organization support;
- sweep-plan review-packet support;
- result-population review support;
- anti-overfit / DSR review support;
- advisory-ranking packet support;
- Scope 6 / R2S packet-preparation support;
- provenance / lineage consistency-check support.

These roles inherit the WP-S2c-162 support-only boundary.

Role names do not create agents, prompts, files, permissions, tools, artifact authority, storage paths, dashboards, runtime behavior, or implementation authority.

## 8. Preferred Orchestration Posture

The preferred future orchestration posture is explicit, auditable, bounded, and human-in-the-loop.

Possible future models may include a sequential pipeline, graph workflow, supervisor/checker pattern, state machine, or task queue with human checkpoints.

This package does not choose one of those as implementation architecture.

Any future model must preserve repo-truth precedence, visible handoffs, scoped permissions, stop conditions, and human review.

No workflow, state machine, task queue, code, agent config, or prompt file is created here.

## 9. Handoff Protocols

Future support handoffs should identify:

- input context;
- repo-truth sources inspected;
- assumptions;
- warnings;
- blockers;
- uncertainty;
- what is complete;
- what is incomplete;
- what failed;
- what contradicted repo truth or another support output;
- what was escalated;
- required human review afterward.

Handoffs must not silently convert draft/support material into canonical artifacts.

Handoffs must not imply approval.

Handoffs should preserve fact, inference, decision, open question, and future option as separate categories.

## 10. Shared-State Discipline

Support agents may share bounded context only where later authorized.

Shared state should be explicit, auditable, and provenance-linked.

Shared state must not become a hidden artifact store, parallel registry, shadow decision store, or mutable canonical evidence surface.

Stale, missing, contradictory, or conflicting shared state should trigger warning, escalation, or stop behavior rather than silent overwrite.

Shared state must not replace current merged repo truth.

## 11. Provenance And Audit Integration

Future orchestration must preserve the WP-S2c-167 provenance posture.

Agent operation provenance should show:

- support role;
- input sources;
- output prepared;
- cited repo-truth sources;
- completion, partial-completion, failure, or escalation posture;
- human review required afterward;
- parent/child relation to any future support packet where later authorized.

Agent provenance remains support context only.

It does not approve, promote, rank, transition, satisfy gates, or create canonical evidence.

## 12. Human-In-The-Loop Checkpoints

Future orchestration must return to human review before:

- Strategy Spec approval or lock;
- variant population pre-registration;
- sweep or run authorization;
- result-population consumption as clean;
- advisory ranking being treated as review-ready;
- Scope 6 / R2S handoff;
- any readiness, transition, promotion, demotion, paper/live, runtime, or protected-path action.

Human checkpoints cannot be replaced by agent consensus, orchestration state, a score, a dashboard display, a validator pass, or provenance completeness.

## 13. Partial-Completion And Failure Recovery

Partial completion must remain visible.

Failed, contradicted, abandoned, invalid, errored, or incomplete support steps must not be hidden.

Retries, reruns, amendments, and supersessions should preserve parent lineage where later authorized.

Abandoned branches should remain visible where they affect search interpretation, result-population completeness, trial-budget accounting, anti-overfit review, advisory ranking, or human-review packet context.

Failure must fail closed when repo truth is missing, protected boundaries are implicated, canonical surfaces are unclear, or package scope is insufficient.

## 14. Conflict / Uncertainty / Disagreement Handling

Conflicting agent outputs should be surfaced, not averaged into false consensus.

Uncertainty should remain visible.

Disagreements should route to human review or a stop condition.

Agent consensus is not approval.

No score, vote, majority of agents, supervisor output, checker output, or orchestration state can satisfy gates.

If repo truth conflicts with agent output, repo truth wins.

## 15. Fail-Closed Behavior

Future orchestration must fail closed around:

- missing, stale, or contradictory repo truth;
- protected boundaries;
- canonical evidence uncertainty;
- schema, validator, query-view, or artifact ambiguity;
- runner, sweep, dashboard, runtime, paper/live, broker/exchange/order, config, dependency, data, AUTO bridge, A2C-003, Track 3 / WP-S2c-140, or protected-path implications;
- package scope that does not explicitly authorize the requested surface.

Fail-closed means stop, warn, or escalate. It does not mean improvise around the boundary.

## 16. Permissioning And Read/Write Boundaries

Default future agent access should be read-only access to repo truth unless a future package explicitly authorizes a write surface.

No direct writes are allowed to canonical evidence, registries, artifacts, schemas, validators, query views, dashboards, `.claude/`, configs, dependencies, runtime paths, paper/live paths, protected paths, or data unless a future package explicitly authorizes the exact operation.

No network or external calls are allowed unless explicitly authorized.

No background action, scheduler action, autonomous continuation, hidden retry, or package-scope continuation is authorized.

Minimum necessary permissioning should be the default future design principle.

## 17. Canonical Evidence And Artifact Boundaries

Agents and orchestration cannot create or mutate canonical evidence unless a future explicit package authorizes a specific artifact surface.

Even then, human gates and validators remain separate.

No agent may update EXP / REP, trial-log, OL, REC, DEC, candidate registry, Scope 6 artifacts, R2S approval records, S2P approval records, or shadow-evidence retention artifacts in this package.

Agent support text is not canonical evidence unless later recorded through an approved artifact grammar under scoped package authority.

## 18. Strategy Spec / DSL Boundary

Future agents may assist with draft text or completeness checking only if later authorized.

They must not turn Strategy Spec into executable DSL, add arbitrary code, expand expressiveness beyond WP-S2c-166, mutate Strategy Specs after results, approve specs, or create parser/compiler behavior.

The WP-S2c-151 Strategy Spec / DSL lock remains unchanged.

Strategy Spec approval, where later designed, remains human review for variant-planning clarity only.

## 19. Variant / Sweep / Result-Population Boundary

Future agents may assist with review packet preparation only if later authorized.

They must not pre-register variants, create variant manifests, create sweep plans, create run manifests, run sweeps, invoke runners, prune results, hide failed variants, select winners, mutate result populations, or update trial-budget posture.

WP-S2c-158 complete result-population preservation remains unchanged.

Sweep planning is not sweep execution.

## 20. Advisory Ranking And Scope 6 / R2S Boundary

Future agents may assist with warnings, blockers, summaries, lineage checks, and packet preparation only if later authorized.

They must not rank as recommendation, approve, promote, satisfy Scope 6 / R2S, update approval records, trigger readiness, execute gates, or create transition authority.

Advisory ranking remains review priority only.

Scope 6 / R2S remains human-gated and separate from advisory support.

## 21. Runtime / Paper-Live / Protected-Path Boundary

No agent or orchestration path may contact runtime, paper/live, broker/exchange/order, OMS, reconciliation, risk, overlay, safe-mode, kill-switch, configs, dependencies, monitoring, dashboards, data, AUTO bridge, A2C-003, Track 3 / WP-S2c-140, or protected paths unless future explicit Main authorization and package scope permit it.

WP-S2c-168 gives no such permission.

This package creates no runtime behavior, paper/live behavior, protected-path change, dashboard/operator action, scheduler, runner, sweep, transition machinery, approval, readiness, or human-gate execution.

## 22. `.claude/agents/` Future-Reference Posture

Repo truth currently includes `.claude/agents/` as read-only context.

This package does not modify `.claude/`.

It does not create or update agent definitions.

It does not authorize agent prompts, role files, orchestration configuration, or tool permission manifests.

Any future `.claude/agents/` change requires separate explicit package authorization.

## 23. MVP Agent-Support Surfaces

MVP-compatible future support surfaces may be considered only after later authorization and should remain narrow:

- support summaries of source ideas and concept assumptions;
- draft Strategy Spec review packets;
- completeness-check findings;
- variant population review questions;
- sweep-plan review packet checks;
- result-population completeness checks;
- anti-overfit / DSR warning summaries;
- advisory-ranking review packets;
- Scope 6 / R2S packet-preparation checklists;
- provenance and lineage consistency findings.

These are support surfaces only.

They are not schemas, artifacts, validators, query views, dashboards, prompts, tools, storage paths, or implementation in this package.

## 24. Deferred Agent-Support Surfaces

Deferred surfaces include exact orchestration architecture, exact permission model, exact agent prompts, exact support packet format, exact shared-state model, exact audit log format, exact failure taxonomy, exact dashboard/operator review surface, exact validator integration, exact query integration, exact artifact creation path, and exact implementation sequence.

Any deferred surface requires explicit future package scope and refreshed repo-truth inspection.

## 25. Forbidden Agent Roles

Forbidden agent roles include:

- autonomous open-ended agent loop;
- agent as approver;
- agent as promoter;
- agent as gate executor;
- agent as registry writer;
- agent as canonical evidence mutator;
- agent as Strategy Spec approver;
- agent as variant pre-registrar;
- agent as sweep or runner trigger;
- agent as result-pruner or winner selector;
- agent as advisory-ranking authority;
- agent as Scope 6 / R2S approver;
- agent as readiness or transition authority;
- agent as runtime, paper/live, broker/exchange/order, OMS, reconciliation, risk, overlay, safe-mode, kill-switch, dashboard, config, dependency, data, AUTO bridge, A2C-003, or protected-path actor.

These roles are rejected for this package and for future orchestration unless Main/Karl later explicitly reopens a boundary.

## 26. Audit Questions For Future Orchestration

Future orchestration design should let reviewers answer:

- Which support role acted?
- What current repo-truth sources were inspected?
- What input context was used?
- What output was prepared?
- What assumptions, warnings, blockers, uncertainty, and failures were disclosed?
- What parent/child lineage exists?
- What human review is required next?
- Did any support output conflict with repo truth or another output?
- Did shared state remain explicit and auditable?
- Did a missing or protected surface fail closed?
- Did any support step imply authority it did not have?

These are audit questions only, not validator contracts.

## 27. Deferred Implementation Details

Deferred implementation details include exact schema fields, field names, enum values, IDs, storage paths, examples, fixtures, validators, query views, integrity views, prompts, agent definitions, tool permission manifests, state machines, graphs, queues, audit logs, shared-state stores, dashboard views, runner integration, network policy, escalation automation, human-review packet formats, warning/blocker labels, and implementation sequence.

Any future implementation requires explicit Main/Karl direction and a scoped package.

## 28. Rejected Alternatives

Rejected alternatives:

- autonomous open-ended agent loop;
- agent-as-approver;
- agent-as-promoter;
- agent-as-gate-executor;
- agent-as-registry-writer;
- agent-as-canonical-evidence-mutator;
- agent-triggered sweeps or runners;
- agent-triggered runtime/paper/live activity;
- agent-controlled dashboard/operator action;
- hidden shared state;
- agent consensus as approval;
- majority vote as gate satisfaction;
- automatic transition from advisory ranking to Scope 6 / R2S approval;
- prompt-only safety for protected boundaries;
- `.claude/` changes from this package;
- implementation authorization from this prerequisite design.

These alternatives are rejected because they weaken repo-truth precedence, evidence discipline, human gates, protected boundaries, or non-authority posture.

## 29. Future Package Dependencies

Future packages may need to design or lock:

- exact dashboard/operator-review constraints;
- exact support packet shape;
- exact orchestration architecture, if implementation is later authorized;
- exact agent permissioning and stop behavior;
- exact shared-state and audit-log posture;
- exact human-review checkpoint packet formats;
- exact provenance references for agent operations;
- exact artifact-creation boundaries for any later agent-assisted write package;
- exact validation, query, or dashboard consumption behavior if later authorized.

Each future package must start from refreshed repo truth and preserve protected boundaries.

## 30. Validation Posture

This package uses CS12 T1-doc-narrow validation unless current repo truth requires a broader profile.

Validation proves changed-file scope and repo consistency only. It does not create implementation authority.

Expected validation includes refreshed-main preflight, exact changed-file scope checks, forbidden-path diff checks, query-view listing, all discovered `v_integrity_*` views, registry/artifact/outcome/reconciliation validators, repo-conventional scoped pytest for research pipeline and integrity surfaces, staged diff checks, and clean final status.

Full pytest is not required unless current repo truth, validation failure, repo-local convention, or package-specific discovery requires it.

## 31. Next-Package Posture

After merge, Side may draft WP-S2c-169 as the prerequisite-chain consolidation and implementation roadmap after refreshed-main preflight and no stop trigger, unless Main redirects.

Implementation remains unauthorized.

WP-S2c-170 remains gated and must not be drafted automatically.

No schema, validator, query view, artifact, parser/compiler, code, test, tool, runner, sweep, dashboard, agent, prompt, storage path, runtime/paper/live, protected-path, approval, readiness, transition, recommendation, ranking/scoring, or human-gate execution package is authorized by WP-S2c-168.
