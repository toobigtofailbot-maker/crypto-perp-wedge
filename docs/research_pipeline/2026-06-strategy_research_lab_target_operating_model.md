# Strategy Research Lab Target Operating Model

## V2 prospective supersession

`D2-020` prospectively replaces this design's initial-maturity per-Spec,
per-variant, per-sweep, and per-hypothesis approval assumptions with
Karl-approved bounded-envelope authority for legal in-envelope research, but
only after Stage 5B is implemented, validated, explicitly activated, and a
valid approved envelope exists. Until then, the current authorization posture
remains operational.

Preregistration, full denominator and result-population preservation,
provenance, anti-overfit/multiple-testing discipline, WFO/OOS, final-holdout
isolation, scientific gates, and human candidate promotion remain unchanged.
See `docs/architecture/2026-10-bounded_autonomous_research_v2_architecture.md`.

## 1. Scope

WP-S2c-147 / WP-12ft is a Tier 1 documentation-only package.

It creates the substantive Strategy Research Lab target operating model promised
by WP-S2c-146. The model defines how the lab should move from idea intake to
advisory ranked output while preserving existing research, evidence, and human
gate discipline.

This package creates no implementation, schema, validator, query view, artifact
instance, Strategy DSL, code, test, runtime change, ranking authority, scoring
authority, recommendation authority, promotion authority, transition authority,
paper/live authority, or human-gate execution authority.

## 2. Authorization and repo-truth basis

WP-S2c-146 opened the Strategy Research Lab design tranche and identified
WP-S2c-147 as the next sequential lab package.

Current repo truth records Track 3 as paused after WP-S2c-139. WP-S2c-140
onward remains deferred, not rescinded.

The lab must consume, not replace, the existing research and evidence
architecture: candidate registry, EXP / REP artifacts, append-only trial log,
OL / REC / DEC surfaces, read-only query layer, D2-006, D2-007, REC-5,
Phase 9 / D2-011 discipline, Scope 6 packaging, and permanent human gates.

All future lab implementation remains unauthorized until later explicit
locking and implementation authorization.

## 3. Purpose and success definition

The lab's purpose is to increase research throughput from user ideas, research
papers, articles, strategy notes, and observed online strategies while
preserving locked evidence discipline.

Success means a safe, auditable operating model for moving from idea to
advisory ranked output:

- ideas are captured without becoming execution authority;
- concepts are separated from specs, variants, evidence, and decisions;
- specs and variant populations are reviewed before execution;
- results are filtered for robustness rather than selected by single best
  backtest;
- advisory rankings are routed to human review only.

Success does not mean automatic strategy deployment, candidate promotion, paper
or live trading, gate satisfaction, readiness, transition, policy action, or
runtime contact.

## 4. Operating principles

- Repo truth first: current committed files outrank summaries, memory, and
  prior handoffs.
- Idea/spec/variant separation: an idea is not a concept, a concept is not a
  strategy spec, a strategy spec is not a candidate, and a variant population is
  not evidence.
- Pre-registration before execution: strategy specs, variant populations, trial
  budgets, data assumptions, and exclusion rules must be locked before any
  later authorized execution.
- Hash and provenance discipline: later lab surfaces must preserve source,
  version, data, parameter, and artifact lineage.
- Advisory ranking only: ranking may order research outputs for review but
  cannot approve, promote, transition, score for policy, or recommend trading.
- Anti-overfit by design: the lab must treat breadth, trial count, and
  robustness as first-class constraints.
- No live authority: the lab cannot contact exchange, broker, order, runtime,
  paper/live, OMS, risk, safe-mode, or protected execution paths.
- Human-gated transitions: specs, variant populations, downstream routing, and
  any later R2S/S2P/paper/live movement require human review where repo truth
  requires it.
- Bounded autonomy: automation may prepare drafts, plans, runs, summaries, and
  diagnostics only after later authorization.
- Auditability over speed: every later step should be reproducible and
  inspectable even when that reduces throughput.

## 5. Lifecycle overview

The target lab lifecycle is:

1. Idea intake from user, paper, article, strategy note, or observed online
   strategy.
2. Concept record creation and rejection-or-advance review.
3. Human-reviewed strategy spec authoring.
4. Variant population design.
5. Variant population pre-registration.
6. Sweep planning.
7. Controlled offline research execution only when later authorized.
8. Result aggregation.
9. Anti-overfit and multiple-testing filtering.
10. Advisory ranking brief.
11. Human review.
12. Possible later routing into candidate registration, EXP / REP, OL / REC /
    DEC, Scope 6, or approval paths under separate authorization.

This flow is conceptual. It does not create any of the future artifact surfaces
or execute any part of the lifecycle.

## 6. Stage 0 — Idea intake

Idea inputs may include:

- user-provided strategy ideas;
- research papers;
- market articles;
- strategy notes;
- observed public or online strategies;
- post-mortems from failed candidates;
- query-layer observations that suggest under-explored surfaces.

Intake should capture source, claim, assumed market mechanism, market context,
required data, timeframe assumptions, expected directionality, risk premise,
unsupported assumptions, ambiguities, and known exclusions.

Intake cannot create execution authority. Ambiguous, unsupported, or
incomplete ideas become concept questions, not code, candidates, schemas,
backtests, EXP plans, or trial-log rows.

## 7. Stage 1 — Concept record

A concept record is a future artifact surface. This package does not create the
surface, schema, instance, validator, query view, or storage path.

A future concept record should summarize:

- strategy idea and source lineage;
- economic mechanism;
- required inputs;
- expected directionality;
- primary timeframe and possible confirmation timeframes;
- assumptions that must be tested;
- exclusions and disallowed interpretations;
- data availability questions;
- open questions for human review.

Concepts are not candidates and are not evidence. A concept can be rejected
before strategy spec authoring. Rejection at concept level is a useful outcome
when the source claim is unclear, data needs are unauthorized, or the mechanism
would violate protected boundaries.

## 8. Stage 2 — Strategy spec authoring and approval

A strategy spec is a future artifact surface. This package does not create the
surface, schema, instance, validator, query view, or Strategy DSL.

A future spec should formalize entry logic, exit logic, position direction,
risk assumptions, data requirements, timeframe assumptions, cost and slippage
assumptions, holding-window assumptions, filters, invalidation rules, and
parameters that may vary in later variant populations.

Spec approval is human-gated at initial lab maturity. Spec approval means the
spec is clear enough for later bounded variant planning. It is not candidate
promotion, paper/live approval, R2S approval, S2P approval, D2-006 satisfaction,
REC-5 satisfaction, readiness, transition, recommendation, or runtime
authority.

## 9. Stage 3 — Variant population design and pre-registration

A variant population is a future artifact surface. This package does not create
the surface, schema, instance, validator, query view, or storage path.

A future variant population should define bounded parameter ranges,
risk/reward variants, stop and take-profit choices, maximum hold windows,
filter choices, exclusion rules, cost assumptions, data assumptions, trial
budget, and failure-accounting posture.

Variant population must be pre-registered before execution to reduce
cherry-picking. Parameter-grid breadth must be bounded and justified. The
population should include hash-pinned inputs and provenance conceptually so the
executed universe can be audited against the approved universe.

Variant planning must not hide excluded variants or silently replace the
population after observing results.

## 10. Stage 4 — Sweep planning and execution boundary

Sweep planning may use existing parameter-sweep, batch-runner, local-run
registry, and local-sweep-result precedent. Those surfaces show how to keep
local automation deterministic, explicit, local-only, research-only, and
non-authoritative.

Actual sweep execution remains unauthorized by this package. Future sweep
execution must be separately authorized and must route through existing
evidence systems or later explicitly designed lab execution surfaces. A sweep
plan must not infer authority from a file's existence, an agent request, a
dashboard action, a scheduler, or a stored manifest.

No runtime, paper/live, OMS, risk, safe-mode, exchange, broker, order API,
protected-path, Tier 4, monitoring/dashboard, paper bridge, or AUTO bridge
contact is authorized here.

## 11. Stage 5 — Result aggregation and anti-overfit filtering

Result aggregation must distinguish raw performance from robust evidence.

Filtering must account for:

- trial count and multiple testing burden;
- DSR or another later locked multiple-testing-aware threshold;
- holdout and out-of-sample discipline;
- walk-forward stability;
- parameter sensitivity and stability;
- modeled costs, slippage, funding, and cost drag;
- drawdown and liquidation risk;
- trade count sufficiency;
- PnL concentration by window;
- regime concentration;
- failure counts and excluded variants;
- pipeline-version and exact-segment separation where applicable.

No single best backtest may be treated as candidate approval. Population-level
inference must preserve no-cross-segment inference constraints where repo truth
requires them, including REC-5 exact-segment floor discipline.

## 12. Stage 6 — Advisory ranking brief

An advisory ranking brief is a future artifact surface. This package does not
create the surface, schema, instance, validator, query view, ranking formula,
score, or storage path.

A future advisory ranking brief may order research results for human review.
It should include uncertainty, robustness evidence, excluded variants, failure
modes, known data caveats, trial budget, multiple-testing adjustment posture,
and links to canonical evidence surfaces.

Ranking is advisory only. It cannot create promotion authority, readiness
authority, transition authority, candidate approval, paper/live approval,
policy action, scoring authority, recommendation authority, runtime authority,
or human-gate execution.

## 13. Stage 7 — Human review and downstream gate routing

Human review decides whether any lab output should become a candidate, a future
research-to-shadow input, a Scope 6 review input, or another later
approval-path item.

Any movement to R2S, S2P, paper, live, runtime, protected paths, or Tier 4
remains under existing locked gates and future explicit authorization.
D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6, and permanent human gates
remain governing boundaries.

Lab output can inform future decisions but cannot execute them.

## 14. Actor and responsibility model

User: provides ideas, direction, and explicit authorization decisions where
required.

Lab intake agent: extracts source claims, assumptions, context, required data,
and open questions. It cannot create candidates, specs, schemas, code, or
evidence authority.

Spec authoring agent: drafts structured specs for human review. It cannot
approve specs, execute tests, modify strategy code, or touch protected paths.

Variant planner: proposes bounded variant populations and trial budgets. It
cannot execute sweeps, change pre-registered populations after results, or
claim optimal parameters.

Execution orchestrator: future role only. It may run authorized offline
research sweeps after later implementation authorization. It cannot contact
runtime, paper/live, exchange, broker, OMS, risk, safe-mode, or protected paths.

Evidence aggregator: summarizes results, provenance, failures, and canonical
artifact links. It cannot create decision authority or suppress failed
variants.

Robustness reviewer: flags overfit, multiple-testing, sensitivity,
concentration, and cost-drag issues. It cannot approve candidates.

Karl / Main / human reviewer: approves specs, variant populations, downstream
gate movement, and boundary changes where repo truth requires human authority.

Side / Codex package executor: changes repo files only inside explicit work
package scope after refreshed-main preflight and stops on boundary conflicts.

## 15. Conceptual artifact surface map

Future surfaces are conceptual only in this package:

| Surface | Posture |
|---|---|
| Concept record | New future artifact surface for idea source, mechanism, assumptions, exclusions, and open questions. |
| Strategy spec | New future artifact surface or DSL-adjacent surface for reviewed strategy logic and assumptions. |
| Variant population manifest | New future artifact surface for bounded, pre-registered parameter and filter universe. |
| Sweep plan | Future bridge surface from approved variant population to authorized offline execution plan. |
| Sweep run manifest | Future execution-accounting surface if later authorized; local/research-only unless separately promoted. |
| Result population index | Future structural aggregation surface for sweep results and variant lineage. |
| Robustness report | Future evidence-summary surface for DSR, sensitivity, cost, drawdown, and concentration checks. |
| Advisory ranking brief | Future advisory-only human-review surface for ordering research outputs. |
| Gate-routing note | Future bridge note to existing candidate, EXP / REP, OL / REC / DEC, or Scope 6 paths when later authorized. |

None of these surfaces exists as a schema, instance, validator, query view, or
canonical artifact because of WP-S2c-147.

## 16. Relationship to existing EXP / REP / trial-log / OL / REC / DEC

Existing EXP / REP, trial-log, OL, REC, and DEC surfaces remain the canonical
evidence chain.

Lab surfaces should either feed that chain or summarize outputs from that
chain. They must not create parallel decision authority or parallel evidence
truth.

Future design must decide whether variant sweeps map to one EXP with many
trials, multiple EXPs, another bounded artifact layer, or a combination that
preserves pre-registration and trial-accounting discipline. No mapping is
locked here.

Any later bridge from lab outputs to committed evidence must preserve REP as
the authoritative research result record, trial-log append discipline, OL as a
structured derivation from committed source evidence, REC as expected-vs-
realized reconciliation, and DEC as human-readable decision record.

## 17. Human gates and safe-autonomy levels

Current project posture remains L0 / L1 until later packages authorize more.

| Level | Meaning |
|---|---|
| L0 | Manual design only. Humans author and review all lab design. No execution. |
| L1 | Assisted concept and spec drafting. No execution, no schema, no artifact instance, no authority. |
| L2 | Human-approved variant population generation. No autonomous execution. |
| L3 | Human-approved sweep execution in offline research only after later implementation authorization. |
| L4 | Advisory ranking and candidate recommendation for human review only, with no self-executing authority. |
| L5 | Out of scope: automatic paper/live/promotion, automatic transition, automatic human-gate satisfaction, runtime action, or policy action. |

Spec approval and variant population approval are human-gated at initial
maturity. R2S, S2P, paper/live movement, risk parameter changes, kill
decisions, and novel strategy-family introductions remain human-gated under
repo truth.

## 18. Anti-overfit and multiple-testing controls

Future lab implementation must include:

- pre-registered variant universe;
- explicit trial budget;
- holdout and out-of-sample discipline;
- walk-forward testing;
- DSR or later locked multiple-testing-aware thresholding;
- sensitivity and parameter-stability checks;
- cost, slippage, funding, and liquidation stress;
- trade-count and PnL-concentration checks;
- failure accounting for all variants;
- rejection of isolated winners;
- no hidden hand-selection;
- no cross-segment inference where REC-5 or pipeline-version separation blocks
  it;
- source, data, parameter, code, and artifact provenance.

The lab should treat many tried variants as evidence burden, not as a larger
chance to find a headline winner.

## 19. Implementation readiness criteria

Before implementation can be requested, later packages must lock:

- Strategy DSL or spec shape;
- concept and spec approval discipline;
- variant population storage and pre-registration semantics;
- sweep orchestration interface;
- anti-overfit / DSR population logic;
- advisory ranking artifact semantics;
- failure-accounting and excluded-variant requirements;
- relationship to EXP / REP / trial-log / OL / REC / DEC;
- Scope 6 interaction;
- protected-boundary review;
- Karl-gated implementation authorization.

Until those items are locked, lab implementation remains unauthorized.

## 20. Handoff to later lab tranche packages

The default later lab-tranche sequence is:

- WP-S2c-148 begins Strategy DSL design opening.
- WP-S2c-149, WP-S2c-150, and WP-S2c-151 continue, consolidate, and lock DSL.
- WP-S2c-152 and WP-S2c-153 cover concept ingestion and spec approval.
- WP-S2c-154 through WP-S2c-158 cover variant generation, orchestration,
  storage, and storage locking.
- WP-S2c-159 and WP-S2c-160 cover anti-overfit / DSR population logic and the
  advisory ranking artifact.
- WP-S2c-161 and WP-S2c-162 cover Scope 6 integration and lab agent roles.
- WP-S2c-163 and WP-S2c-164 consolidate and decide implementation
  authorization.

This package authorizes no parallel next packages. After merge, the default
next sequential package is WP-S2c-148 unless Main directs a different
authorized lab package.

## 21. Protected boundaries

This operating model preserves:

- Phase 1 paper runtime;
- D-0001 hard risk caps;
- D2-008 overlay semantics and output set;
- OMS, reconciliation, kill-switch, and safe-mode boundaries;
- SignalProvider Protocol;
- Tier 4 boundaries;
- `lib/`, `src/`, `configs/`, `.claude/`, and `data/`;
- AUTO frozen status;
- A2C-003 unauthorized status;
- C/F deferred status;
- A/D/E rejected status;
- Track 3 paused status;
- WP-S2c-140 deferred status;
- permanent human gates.

No future lab surface may weaken these boundaries without explicit later
authorization.

## 22. Stop conditions

Stop if any lab design or implementation package:

- implies implementation before authorization;
- requires schema, code, test, validator, query-view, tool, runtime, or
  protected-path changes outside scope;
- creates concept/spec/variant/sweep/ranking artifact instances without
  authorization;
- weakens pre-registration or human gates;
- makes ranking authoritative;
- creates readiness, transition, approval, promotion, paper/live, policy, or
  runtime authority;
- reactivates AUTO, Track 3, WP-S2c-140, the paper bridge,
  monitoring/dashboard, or A2C-003 without explicit authorization;
- touches runtime or protected paths;
- ignores D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6, or permanent human
  gates;
- fails validation.

## 23. Non-authority boundary

This document is planning and operating-model structure only.

It creates no lab implementation, strategy execution, candidate registration,
evidence generation, schema, validator, query view, Strategy DSL, concept
artifact, spec artifact, variant artifact, sweep artifact, ranking artifact,
approval record, shadow-evidence retention artifact, policy, readiness,
transition, recommendation, promotion, scoring, paper/live, runtime, or
human-gate execution authority.

## 24. Next-package posture

After merge, the default next sequential package is WP-S2c-148 Strategy DSL
design opening unless Main directs a different authorized lab package.

Do not draft implementation packages. Do not draft Track 3 continuation
packages. Do not draft WP-S2c-140 continuation work unless Main explicitly
reactivates Track 3 after refreshed-main preflight and direct repo-truth
inspection.
