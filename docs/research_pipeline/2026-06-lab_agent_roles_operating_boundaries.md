# Lab Agent Roles / Operating Boundaries

## V2 prospective supersession

`D2-020` prospectively supersedes advisory-only restrictions only for legal
in-envelope research operations after Stage 5B is implemented, validated,
explicitly activated, and a valid Karl-approved bounded research envelope
exists. Hermes/agents may then propose and cause permitted jobs to execute
through deterministic CPW scientific machinery and Prefect orchestration.

Agents still do not own scientific truth, durable lineage, holdout state,
candidate promotion, protected execution, risk, paper/live, or capital
authority. Until the effective-date conditions are satisfied, this document's
current advisory/default-off limits remain operational. See
`docs/architecture/2026-10-bounded_autonomous_research_v2_architecture.md`.

## 1. Scope

WP-S2c-162 / WP-12gi is a Tier 1 documentation-only substantive design
package.

It defines the future Strategy Research Lab agent-role model and operating
boundaries after WP-S2c-161 Scope 6 / R2S integration design.

It creates no agent implementation, agent prompt, tool, schema, validator,
query view, artifact instance, runner, dashboard, storage path, code, test,
runtime behavior, approval authority, ranking/scoring authority, readiness
authority, transition authority, paper/live authority, or human-gate execution
authority.

## 2. Authorization and repo-truth basis

Current repo truth records WP-S2c-161 as merged and identifies WP-S2c-162 as the
next sequential lab package unless Main/Karl directs otherwise.

WP-S2c-147 defines the Strategy Research Lab target operating model from idea
intake through advisory ranked output while preserving existing evidence,
decision, and human-gate boundaries.

WP-S2c-151 locks Strategy Spec terminology and the Strategy DSL as constrained
representation discipline, not executable code or runtime interface.

WP-S2c-158 locks variant/storage principles: future variant population
manifest as pre-registration surface, complete result-population preservation,
canonical EXP / REP / trial-log / OL / REC / DEC authority, and no parallel
decision authority.

WP-S2c-159 defines anti-overfit / DSR review as upstream diagnostic discipline
only.

WP-S2c-160 defines advisory ranking as human-review support only.

WP-S2c-161 defines Scope 6 / R2S integration as human-review support only and
hands off agent-consumption boundaries to WP-S2c-162.

WP-S2c-100 locked criteria, WP-S2c-113 Scope 6 packaging lock, D2-006, D2-007,
REC-5, Phase 9 / D2-011, canonical evidence surfaces, and permanent human gates
remain preserved.

## 3. Design objective

The objective is to define what future lab agents may support and what they
must never decide, execute, or authorize.

Future agents may later help draft support text, summarize source material,
extract concepts, prepare Strategy Spec drafts for human review, check
completeness, surface warnings, blockers, and uncertainty, prepare
human-review packets, compare draft content against repo truth, preserve
lineage and evidence references, and report conflicts or missing information
only if later packages explicitly authorize the relevant surface.

Agent outputs are advisory/supporting material only.

Agents create no authority.

## 4. Lifecycle placement

The agent-role model spans the Strategy Research Lab lifecycle:

1. idea intake;
2. concept extraction;
3. Strategy Spec / DSL representation;
4. variant generation;
5. sweep planning;
6. result population preservation;
7. anti-overfit / DSR review;
8. advisory ranking;
9. Scope 6 / R2S human-review integration.

The model is a boundary design, not implementation. It does not create agent
interfaces, storage, prompts, tools, schemas, validators, query views, or
artifact instances.

## 5. Agent role taxonomy

Future support roles may include:

- research intake agent;
- concept extraction agent;
- Strategy Spec drafter;
- Strategy Spec reviewer / checker;
- variant generator assistant;
- sweep planner assistant;
- result reviewer assistant;
- anti-overfit / DSR reviewer assistant;
- advisory ranking assistant;
- Scope 6 / R2S review-packet assistant;
- audit / completeness checker.

Each role is a future support boundary only. Role names do not imply an
implemented agent, permission grant, artifact type, storage path, or authority.

## 6. Research intake agent boundary

A future research intake agent may support capture of raw strategy ideas,
source claims, assumed market behavior, proposed data needs, timeframe hints,
and unresolved questions.

It may summarize source material and separate repo facts from external claims,
inferred statements, and assumptions.

It must never approve an idea, create a candidate, update candidate registry
state, create a concept artifact, create a Strategy Spec, infer execution
authority, contact runtime or protected paths, or treat intake as evidence.

## 7. Concept extraction agent boundary

A future concept extraction agent may support conversion of raw intake into
reviewable concept text, including thesis, instrument/timeframe assumptions,
entry/exit/risk concepts, data requirements, known unsupported claims, and
questions for human review.

It may identify missing information or contradictions.

It must never canonically accept, reject, or approve a concept; create concept
artifact instances without explicit WP authorization; authorize Strategy Spec
drafting; update registry state; create EXP / REP / trial-log / OL / REC / DEC
content; or run any test, backtest, sweep, or optimization.

## 8. Strategy Spec drafter boundary

A future Strategy Spec drafter may support human-reviewable Strategy Spec draft
text after the required concept-to-spec authorization exists.

It may organize declarative logic, assumptions, provenance, allowed timeframe
context, data dependencies, and review questions according to the WP-S2c-151
Strategy Spec / DSL lock.

It must never make the Strategy Spec executable, create parser/compiler
behavior, decide final schema fields, approve the Strategy Spec, create
candidate approval, create EXP authority, authorize variants or sweeps, or
contact runtime/protected paths.

## 9. Strategy Spec reviewer boundary

A future Strategy Spec reviewer / checker may compare a draft Strategy Spec
against repo-truth requirements, concept provenance, locked mandatory field
groups, non-executable posture, missing assumptions, and forbidden claims.

It may flag incompleteness, inconsistency, unsupported assertions, or authority
leakage for human review.

It must never approve a Strategy Spec, reject it as a canonical decision, mark
it ready for downstream execution, change review status, update registry state,
or satisfy a human gate.

## 10. Variant generator boundary

A future variant generator assistant may support drafting bounded variant
population proposals from an approved Strategy Spec when later artifact and
authorization packages explicitly allow that surface.

It may help identify parameter families, bounded ranges, lineage, constraints,
and pre-registration questions.

It must never create a variant manifest unless a later WP explicitly authorizes
that artifact type, silently expand a variant universe, mutate a Strategy Spec,
choose winners, approve variants, trigger sweeps, run optimizations, or create
ranking/recommendation authority.

## 11. Sweep planner boundary

A future sweep planner assistant may support draft sweep-plan text and
completeness checks after a pre-registered variant population exists and after
later authorization defines the sweep-planning surface.

It may identify required data slices, trial-budget accounting, failure/abort
handling, lineage expectations, and result-preservation requirements.

It must never invoke runners, execute backtests, execute sweeps, write
local-run-registry or local-sweep-result files, aggregate results, bypass
pre-registration, or contact runtime/protected paths.

## 12. Result reviewer boundary

A future result reviewer assistant may support checking that a future result
population preserves attempted, failed, invalid, excluded, errored, aborted,
filtered, data-unavailable, and successful variants.

It may flag missing lineage, incomplete result capture, metric-preservation
gaps, or canonical evidence-linking questions.

It must never create result-population artifacts without explicit WP
authorization, filter to survivors only, delete failed results, choose winners,
update EXP / REP / trial-log / OL / REC / DEC, or create decision authority.

## 13. Anti-overfit / DSR reviewer boundary

A future anti-overfit / DSR reviewer assistant may support review of
population-level overfit warnings, multiple-testing concerns, sample-size
limits, walk-forward divergence, parameter cliffs, cost/funding fragility,
tail-risk concentration, and REC-5 exact-segment posture.

It may surface warnings and blockers for human review.

It must never compute DSR unless a later WP explicitly authorizes calculation
behavior, change D2-006 thresholds, dilute REC-5, approve a candidate, rank a
candidate, recommend promotion, or satisfy a gate.

## 14. Advisory ranking assistant boundary

A future advisory ranking assistant may support preparing advisory ordering
context for human review from complete population evidence and approved
diagnostic surfaces.

It may summarize why items appear in an advisory order, list blockers, preserve
lineage, and mark insufficient evidence.

It must never create recommendation authority, ranking authority, scoring
authority, promotion authority, readiness authority, transition authority,
candidate approval, paper/live approval, runtime authority, or human-gate
execution. It must not hide overfit diagnostics behind a single score.

## 15. Scope 6 / R2S review-packet assistant boundary

A future Scope 6 / R2S review-packet assistant may support assembling
human-review packet text from canonical evidence, advisory ranking context,
warnings, blockers, D2-006 posture, REC-5 exact-segment posture, Phase 9 /
D2-011 posture, and Scope 6 packaging requirements.

It may help humans see what to review, why, and with which unresolved issues.

It must never approve R2S, create an R2S approval record unless a later WP
explicitly authorizes that artifact type, update readiness, trigger
transitions, execute gates, contact shadow/paper/live/runtime paths, or create
S2P/paper/live authority.

## 16. Audit / completeness checker boundary

A future audit / completeness checker may support checking draft lab artifacts
or packets for missing source references, stale repo truth, incomplete lineage,
unsupported assertions, forbidden authority claims, and changed-file/scope
questions.

It may report pass/fail-style completeness findings as review support.

It must never become a validator unless a later WP implements one, approve or
reject artifacts, modify files autonomously, override human review, or become a
policy authority.

## 17. Human-review handoff requirements

Future agent outputs must hand off to humans with:

- source and repo-truth references where future artifact design requires them;
- explicit distinction between fact, inference, decision, open question, and
  future option;
- unsupported-claim and missing-information disclosure;
- lineage back to source ideas, concepts, Strategy Specs, variant populations,
  sweep plans, result populations, and canonical evidence where those surfaces
  later exist;
- warnings and blockers that are visible rather than suppressed;
- clear non-authority language.

Human reviewers remain responsible for approvals, gate decisions, readiness
decisions, transition decisions, and any Main/Karl-gated authorization.

## 18. Agent uncertainty and stop-condition behavior

Future agent outputs must surface uncertainty rather than hide it.

Agents must stop or escalate when repo truth is missing, contradictory, stale,
unsupported, or insufficient for the requested support task.

Agents must not fill gaps with plausible but unverified assumptions.

If evidence is insufficient, the output must mark insufficient evidence or stop.

## 19. Agent disagreement / conflict handling

Agent disagreement is a review signal, not a decision.

Conflicting agent outputs must be surfaced to humans with the source of the
conflict and the affected lifecycle step.

No majority vote, score, rank, supervisor agent, or agent consensus may approve,
promote, transition, execute gates, update readiness, or contact runtime.

If repo truth conflicts with an agent output, repo truth wins.

## 20. Repo-truth and evidence-use requirements

Future agent outputs must follow the repo-truth hierarchy:

1. current merged repo truth, including actual changed files and live merged
   state;
2. active package scope and constraints;
3. AGENTS.md;
4. supporting Codex workflow docs;
5. chat memory, prior summaries, and generic best practice.

Future agents must preserve source, provenance, and lineage. They must
distinguish repo facts from external claims, inferred statements, and unresolved
assumptions.

Research/workbench artifacts and advisory outputs have no execution authority
unless a later approved path explicitly grants a bounded surface.

## 21. Tool permissioning boundary

Future agents may receive only the minimum tool access required by a later
authorized package.

Documentation support does not imply filesystem write access, schema access,
query-layer access, runner access, dashboard access, browser/external access,
or runtime access.

Tool permissioning must fail closed around protected paths, runtime paths,
configs, dependencies, data, schemas, validators, query views, tests, tools,
research artifacts, and artifact instances unless the active WP explicitly
authorizes the exact surface.

## 22. Artifact creation boundary

Agents must not create artifact instances unless a later WP explicitly
authorizes that artifact type, path, schema/storage posture, validation, and
changed-file scope.

Agents must not modify candidate registry state, EXP, REP, trial-log, OL, REC,
DEC, HYPOTHESIS.md, concept artifacts, Strategy Spec artifacts, variant
manifests, sweep plans, run manifests, result populations, advisory ranking
artifacts, Scope 6 artifacts, R2S approval records, shadow-evidence retention
artifacts, or S2P approval records unless explicit package scope authorizes the
specific operation.

Agent-authored support text is not canonical evidence unless a later approved
artifact path records it through the repo's artifact grammar.

## 23. Runtime and protected-path prohibition

Agents must not contact, modify, or influence runtime, paper/live, broker,
exchange, order, OMS, reconciliation, risk, overlay, safe-mode, kill-switch,
configs, dependencies, protected paths, Tier 4 paths, monitoring/dashboard,
AUTO, A2C-003, C/F, or A/D/E paths.

Agents must not trigger R2S, S2P, paper, live, runtime, transition simulation,
backtest, sweep, optimization, runner command, local-run-registry write, or
local-sweep-result write.

## 24. Relationship to WP-S2c-158 / 159 / 160 / 161

WP-S2c-158 remains the variant/storage lock. Agent roles cannot weaken
pre-registration, complete result-population preservation, canonical evidence
surfaces, or the hybrid result model.

WP-S2c-159 remains the anti-overfit / DSR design. Agent roles cannot turn
diagnostic review into ranking, approval, promotion, or gate execution.

WP-S2c-160 remains the advisory ranking design. Agent roles cannot turn
advisory ordering into recommendation, ranking authority, readiness, or
transition authority.

WP-S2c-161 remains the Scope 6 / R2S integration design. Agent roles cannot
approve R2S, satisfy gates, update readiness, trigger transitions, or contact
runtime/protected paths.

## 25. Relationship to future WP-S2c-163 / 164

WP-S2c-163 should consolidate the Strategy Research Lab design tranche and
surface implementation-roadmap / decision options after refreshed-main
preflight and no stop trigger.

WP-S2c-164 remains Karl-gated. It must not be drafted before WP-S2c-163 merge,
Main/Karl report-back, and explicit Main/Karl direction.

Implementation packages remain unauthorized.

## 26. Deferred implementation details

Deferred details include:

- agent implementation;
- agent prompts;
- agent orchestration;
- tool permission manifests;
- artifact creation permissions;
- schemas and validators;
- query views;
- parser/compiler behavior;
- storage paths;
- dashboards;
- runner integration;
- calculation formulas;
- exact review packet formats;
- exact human-review workflow roles;
- exact stop/escalation automation;
- any runtime integration.

## 27. Rejected and out-of-scope alternatives

Agent-as-approver is rejected because human approval remains required where
repo truth requires it.

Agent-as-promoter is rejected because promotion and readiness authority remain
separate human-gated surfaces.

Autonomous R2S approval is rejected because Scope 6 / R2S remains a human-review
pathway.

Autonomous paper/live transition is rejected because D2-007, Phase 1 runtime
protections, Tier 4 boundaries, and permanent human gates remain unchanged.

Autonomous ranking-to-execution flow is rejected because advisory ranking is
human-review support only.

Hidden strategy mutation is rejected because Strategy Spec, variant, sweep, and
result lineage must remain explicit.

Unbounded strategy generation is rejected because future variants must derive
from approved Strategy Specs through bounded, pre-registered populations.

Agent-created evidence without artifact authorization is rejected because
canonical evidence surfaces remain EXP / REP / trial-log / OL / REC / DEC where
repo truth defines them.

Agent-created artifact instances without explicit WP scope are rejected because
artifact authority requires package authorization, path, validation, and scope.

Agent-updated candidate registry state is rejected because registry state is a
canonical repo surface, not agent discretion.

Agent execution of human gates is rejected because human gates cannot be
satisfied by agent output.

Runtime/protected-path access is rejected because protected runtime boundaries
remain strict.

Implementation before WP-S2c-164 authorization is rejected because this package
is documentation-only and implementation remains Karl-gated.

## 28. Protected boundaries

Protected boundaries preserved here include:

- OMS truth / reconciliation truth;
- kill-switch semantics;
- D-0001 hard risk caps;
- overlay output set and fail-open behavior;
- paper ledger accounting math;
- runtime, paper/live, broker, exchange, order, risk, safe-mode, configs, and
  dependency paths;
- D2-006;
- D2-007;
- REC-5 exact-segment discipline;
- Phase 9 / D2-011;
- Scope 6;
- WP-S2c-100 locked criteria;
- WP-S2c-113 Scope 6 packaging lock;
- WP-S2c-151 Strategy Spec / DSL lock;
- WP-S2c-158 variant/storage lock;
- WP-S2c-159 anti-overfit / DSR design;
- WP-S2c-160 advisory ranking design;
- WP-S2c-161 Scope 6 / R2S integration design;
- canonical evidence and decision surfaces;
- permanent human gates.

## 29. Stop conditions

Stop if any future agent role would require touching runtime, OMS,
reconciliation, risk, overlay, safe-mode, live-trading, schemas, validators,
query-layer behavior, configs, dependencies, data, code, tests, tools, artifact
instances, registry, trial-log, EXP, REP, OL, REC, DEC, dashboards, or
protected paths without explicit package authorization.

Stop if any content lets agents approve, promote, reject canonically, update
readiness, trigger transitions, satisfy gates, update registry state, create
authority, run calculations, run tests/backtests/sweeps/optimizations, or
contact runtime/protected paths.

Stop if repo truth conflicts with agent output or if evidence is insufficient
for the requested support task.

## 30. Validation posture

This package uses CS12 T1-doc-narrow validation unless current repo truth
requires more.

Expected validation includes diff whitespace checks, exact changed-file scope,
forbidden-path diff checks, query view listing, integrity views, registry /
artifact validators, scoped pytest for research pipeline / registry / artifact
/ outcome / reconciliation / integrity surfaces, and staged diff checks.

No full pytest is required unless current repo truth, validation failure,
repo-local convention, or package-specific discovery requires it.

## 31. Non-authority boundary

This design creates no strategy authority, recommendation authority, approval
authority, runtime authority, paper/live authority, ranking/scoring authority,
promotion authority, transition authority, readiness authority, implementation
authority, artifact authority, evidence authority, policy authority, or
human-gate execution authority.

Agent outputs are advisory/supporting material only.

## 32. Next-package posture

After merge, Side may draft WP-S2c-163 under Main lab-tranche authorization
after refreshed-main preflight and no stop trigger, unless Main/Karl directs
otherwise.

WP-S2c-163 should consolidate the Strategy Research Lab design tranche and
surface implementation-roadmap / decision options.

WP-S2c-164 remains Karl-gated and must not be drafted yet.

Implementation packages remain unauthorized.
