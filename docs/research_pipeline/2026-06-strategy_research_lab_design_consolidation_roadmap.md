# Strategy Research Lab Design Consolidation / Roadmap

## 1. Scope

WP-S2c-163 / WP-12gj is a Tier 1 documentation-only consolidation package.

It consolidates the Strategy Research Lab design tranche from idea intake through human-reviewed advisory output and prepares Main/Karl decision support before any possible WP-S2c-164 implementation-authorization decision.

This document does not implement the Strategy Research Lab. It does not authorize implementation, WP-S2c-164 drafting, schemas, validators, query views, artifact instances, code, tests, tools, agents, dashboards, runners, sweeps, result stores, runtime changes, paper/live changes, promotion, readiness, transition, approval, recommendation, ranking/scoring authority, or human-gate execution.

## 2. Repo-truth basis

Repo truth for this consolidation is the current merged `main` state after WP-S2c-162.

Primary lab-tranche sources inspected:

- `docs/research_pipeline/2026-06-strategy_research_lab_target_operating_model.md`
- `docs/research_pipeline/2026-06-strategy_dsl_locking_decision.md`
- `docs/research_pipeline/2026-06-concept_ingestion_design_opening.md`
- `docs/research_pipeline/2026-06-concept_to_spec_authoring_approval_discipline.md`
- `docs/research_pipeline/2026-06-variant_generation_design_opening.md`
- `docs/research_pipeline/2026-06-sweep_orchestration_design.md`
- `docs/research_pipeline/2026-06-result_population_storage_design.md`
- `docs/research_pipeline/2026-06-variant_storage_consolidation.md`
- `docs/research_pipeline/2026-06-variant_storage_locking_decision.md`
- `docs/research_pipeline/2026-06-anti_overfit_dsr_population_design.md`
- `docs/research_pipeline/2026-06-advisory_ranking_artifact_design.md`
- `docs/research_pipeline/2026-06-scope6_r2s_integration_design.md`
- `docs/research_pipeline/2026-06-lab_agent_roles_operating_boundaries.md`

Supporting evidence and gate sources inspected:

- `docs/research_pipeline/2026-05-scope6_packaging_locking_decision.md`
- `docs/research_pipeline/2026-04-rec_d2_006_gates_methodology.md`
- `docs/research_pipeline/2026-04-experiment_artifacts.md`
- `docs/research_pipeline/2026-04-outcome_ledger_artifact.md`
- `docs/research_pipeline/2026-04-reconciliation_artifact.md`
- `docs/research_pipeline/2026-04-decision_change_artifact.md`
- `docs/research_pipeline/README.md`

The expected exact trial-log design path `docs/research_pipeline/2026-04-trial_log.md` is absent in repo truth. Trial-log discipline is instead represented by `docs/runbook.md`, `docs/project_status.md`, `docs/research_pipeline/2026-04-experiment_artifacts.md`, the lab-tranche documents, and the committed `research/trial_log.jsonl` artifact family.

Merged repo truth wins if external research, summaries, or memory conflict with committed files.

## 3. Consolidated lab lifecycle

The consolidated lab lifecycle is layered:

1. idea intake;
2. concept review;
3. human-reviewed Strategy Spec drafting;
4. bounded variant population design;
5. variant population pre-registration;
6. sweep planning;
7. separately authorized offline research execution only;
8. result population preservation;
9. anti-overfit / DSR diagnostic review;
10. advisory ranking for human review;
11. Scope 6 / R2S review support;
12. downstream human-gated decisions through existing or later authorized surfaces.

Each layer is separate. An idea is not a concept, a concept is not a Strategy Spec, a Strategy Spec is not a candidate, a variant population is not evidence, a result population is not a decision, advisory ranking is not approval, and agent assistance is not authority.

## 4. Locked decisions

Locked or established posture from the tranche:

- Strategy Spec is the future human-reviewable artifact/surface.
- Strategy DSL means constrained representation discipline, not executable code, parser/compiler, runtime interface, or trading engine.
- Future canonical Strategy Spec format direction is JSON-compatible canonical content with an optional non-canonical Markdown companion.
- Strategy Spec clauses are non-executable and declarative.
- `research/candidate_registry.jsonl` is rejected as Strategy Spec storage.
- Variant population manifest is locked as the required future pre-registration surface before sweep execution.
- Complete result-population preservation is required across attempted, failed, invalid, excluded, errored, aborted, filtered, data-unavailable, and successful variants.
- EXP / REP, trial-log, OL, REC, and DEC remain canonical evidence and decision surfaces with no parallel decision authority.
- The hybrid result model is locked: canonical evidence remains authoritative; any future intermediate result-population surface may only be evidence input / index with no authority.
- Anti-overfit / DSR review is diagnostic only and must operate at full-population level rather than surviving-winner level.
- Advisory ranking is human-review support only.
- Scope 6 / R2S integration is human-review support only and cannot be replaced by advisory ranking.
- Lab agents may only support drafting, summarizing, completeness checking, review-packet preparation, warning surfacing, and conflict reporting if later authorized.
- Human gates remain human gates.
- WP-S2c-164 remains Karl-gated.

## 5. Deferred decisions

Deferred decisions include:

- exact schemas, validators, and query views;
- artifact paths, storage paths, file names, IDs, and examples;
- parser/compiler behavior;
- exact Strategy Spec artifact format;
- concept artifact format;
- variant manifest format;
- sweep plan and run manifest format;
- result population format;
- advisory ranking artifact format;
- Scope 6 / R2S packet format;
- agent prompts, orchestration, tool permissioning, and implementation;
- dashboard/operator-review design;
- implementation tranche sequence;
- exact validation commands for future implementation packages;
- exact MVP search method;
- exact backtest realism thresholds;
- exact DSR / PSR / MinTRL implementation;
- exact walk-forward, CPCV, bootstrap, Monte Carlo, or robustness protocol.

This document classifies those items for Main/Karl review but does not decide them.

## 6. Current non-authority boundaries

The lab tranche has no authority to:

- execute strategies, sweeps, backtests, optimizers, runners, or dashboards;
- create or modify runtime, paper/live, broker, exchange, order, OMS, reconciliation, risk, overlay, safe-mode, kill-switch, config, dependency, or protected-path behavior;
- create schemas, validators, query views, code, tests, tools, prompts, artifacts, or storage paths;
- approve candidates, Strategy Specs, variants, R2S, S2P, paper/live readiness, promotions, transitions, or gate satisfaction;
- create ranking/scoring/recommendation authority.

Main/Karl retain authority to decide project changes, implementation authorization, methodology locks, protected-boundary unlocks, and future package sequence.

## 7. Idea / concept / Strategy Spec layer

Idea intake may later capture source claims, market mechanism, data needs, timeframe hints, assumptions, ambiguities, and exclusions. Intake cannot create candidates, evidence, EXP plans, trial-log rows, code, or execution authority.

Concept review should separate reviewable thesis from unsupported claims. Concepts remain upstream of Strategy Specs and can be rejected or returned for clarification before spec drafting.

Strategy Spec authoring is intended to produce human-reviewable declarative strategy logic. Approval, if later designed, means clear enough for variant planning only. It does not mean candidate registration, EXP authority, D2-006 satisfaction, Scope 6 readiness, paper/live approval, or runtime authority.

## 8. Variant population layer

Variant population design is future controlled derivation from an approved Strategy Spec.

The locked posture requires pre-registration before sweep execution. A future variant population should define bounded parameter ranges, invalid combinations, exclusions, data assumptions, cost assumptions, trial budget, lineage, and amendment posture.

Single best variants are not the target unit for honest review. The population itself must be explicit enough to audit the universe that was tested.

## 9. Sweep orchestration layer

Sweep orchestration is a future offline-research planning layer.

It depends on a pre-registered variant population and a later explicit execution-authorization surface. It should preserve trial-budget accounting, failure/abort handling, result capture, provenance, and linkage to canonical evidence.

This consolidation does not authorize runner invocation, local-run-registry writes, local-sweep-result writes, result aggregation, parameter sweeps, optimizer execution, or any runtime/protected-path contact.

## 10. Result population / storage layer

Result population is a future complete record of all variants and run outcomes from an authorized sweep.

WP-S2c-158 locks complete preservation for attempted, failed, invalid, excluded, errored, aborted, filtered, data-unavailable, and successful variants. Winner-only retention is rejected.

Exact result-population storage is deferred. Any future intermediate surface may only be evidence input / index and must link back to canonical EXP / REP, trial-log, OL, REC, and DEC where applicable.

## 11. Anti-overfit / DSR layer

Anti-overfit / DSR review is diagnostic and upstream of advisory ranking.

It should later examine the complete population, not a surviving-winner subset. Current design families include liquidation/ruin events, weak risk-adjusted outcomes, single-event dependency, parameter cliffs, walk-forward divergence, regime instability, cost/slippage/funding fragility, drawdown or tail-risk concentration, sample-size weakness, pre-registration mismatch, and trial-budget irregularities.

Exact formulas, thresholds, denominators, and robustness mechanics remain deferred.

## 12. Advisory ranking layer

Advisory ranking is future human-review support.

It may later order or group variants or candidate families for review, preserve evidence lineage, show blockers, and expose uncertainty. It must not hide overfit diagnostics behind a single score.

`Ranked higher` can only mean higher review priority. It cannot mean recommendation, approval, promotion, readiness, transition, gate satisfaction, or runtime authority.

## 13. Scope 6 / R2S integration layer

Scope 6 / R2S remains a human-gated review and decision pathway.

Future advisory outputs may feed review-priority context, warnings, blockers, D2-006 posture, REC-5 posture, Phase 9 / D2-011 posture, canonical evidence references, and unresolved questions into human review.

Advisory output cannot approve R2S, create readiness, trigger transition machinery, update candidate registry state, contact shadow/paper/live/runtime paths, or satisfy human gates.

## 14. Lab-agent role boundary layer

Future lab agents may support only draft, summarize, check, packet-preparation, lineage, warning, blocker, and conflict-surfacing work if later authorized.

Potential roles include research intake, concept extraction, Strategy Spec drafting/checking, variant proposal support, sweep planning support, result review support, anti-overfit review support, advisory ranking support, Scope 6 / R2S packet support, and audit/completeness checking.

Agents must not approve, reject as canonical decisions, update registry state, create canonical artifacts without explicit scope, execute runners, compute authority-bearing metrics, rank as authority, satisfy gates, or contact runtime/protected paths.

## 15. Canonical evidence and decision surfaces

Canonical surfaces remain:

- EXP for plans;
- REP for research result reports;
- `research/trial_log.jsonl` for trial evidence where applicable;
- OL for structured outcome-ledger derivation;
- REC for expected-vs-realized reconciliation;
- DEC and human decision records for decisions where repo truth defines them.

Future lab surfaces may feed or summarize those surfaces only after later authorization. They must not create a parallel evidence store or decision store.

## 16. Human gates and protected boundaries

Permanent human gates remain unchanged.

D2-006, D2-007, REC-5, Phase 9 / D2-011, WP-S2c-100 locked criteria, WP-S2c-113 Scope 6 packaging, and protected runtime boundaries remain governing constraints.

No runtime, paper/live, broker/exchange/order, OMS, reconciliation, risk, overlay, safe-mode, kill-switch, config, dependency, or protected-path contact is created or authorized.

## 17. Side Research input summary

Side Research input available to this package is external input, not repo truth and not implementation authority.

External Lab Validity Core findings used here as decision-prep considerations:

- crypto perpetual backtest realism can materially depend on fees, funding, mark/index mechanics, maintenance margin, leverage brackets, symbol filters, order constraints, slippage, liquidity, partial fills, stale fills, latency, liquidation, and bar-path assumptions;
- bar-based backtests may be acceptable for research-stage review only under explicit small-order, conservative-fill, and non-intrabar-dependent assumptions;
- search method does not remove overfit or selection-bias risk;
- constrained manual grids and constrained random search are stronger MVP candidates than adaptive optimizers because they are easier to pre-register and audit;
- walk-forward-first validation appears practical as an MVP outer-validation posture;
- DSR / PSR / MinTRL-style review may help interpret multiple trials, Sharpe credibility, and sample sufficiency if enough result-population and return-path context is stored;
- bootstrap, Monte Carlo, and permutation tests may be later robustness tools but should not be forced into this package;
- advisory ranking is not clean unless realism, full-population completeness, search lineage, robustness, and multiple-testing context are visible;
- operator/dashboard surfaces should expose blockers and uncertainty rather than hiding them behind ranks or single scores.

The expected Lab Architecture Fit external research output covering DSL expressiveness, agent orchestration, and automated strategy-research pipeline SOTA was not available to this package. Sections below use repo-truth design material only for those topics.

## 18. Lab validity floor considerations

Possible future lab validity floor topics for Main/Karl decision:

- backtest realism taxonomy for crypto perpetuals;
- explicit fees, funding, slippage, liquidity, liquidation, exchange constraint, and bar-path assumption disclosure;
- bounded search governance and pre-registered search family;
- full search-family lineage and result-population retention;
- walk-forward-first validation as possible MVP posture;
- DSR / PSR / MinTRL support as required, optional, or deferred;
- CPCV, bootstrap, Monte Carlo, and permutation testing as later or conditional strengthening;
- advisory-ranking validity floor before any human-review packet can be treated as clean;
- operator/dashboard uncertainty display if dashboard surfaces are later authorized.

These are external findings and inferences. They are not hard repo rules unless Main/Karl later lock them or current repo truth already requires them.

## 19. DSL expressiveness considerations

Repo truth locks Strategy Spec / DSL as constrained, non-executable representation discipline and defers exact operator vocabulary and nested-condition mechanics.

Future expressiveness-readiness questions include whether the Strategy Spec format must represent:

- multi-signal entries;
- nested logic;
- time and signal exits;
- dynamic sizing;
- regime filters;
- multi-timeframe logic;
- trend-following;
- mean reversion;
- breakouts;
- funding/carry;
- basis/spread concepts;
- risk overlays;
- cooldowns;
- no-trade filters;
- time/session filters.

This document does not expand the DSL, choose fields, choose operators, define nesting syntax, create examples, or authorize parser/compiler behavior.

## 20. Agent orchestration considerations

Repo truth defines agent role boundaries but not orchestration.

Future orchestration options for decision support may include:

- sequential pipeline;
- supervisor/worker model;
- graph workflow;
- state machine;
- human-in-the-loop checkpoints;
- audit trail;
- partial-failure recovery;
- disagreement handling;
- permissioning;
- explicit prevention of agent-as-approver.

No agent implementation, prompt, permission model, state machine, graph, tool, or orchestration system is authorized here. Any future orchestration must fail closed around protected paths and preserve human gates.

## 21. Automated strategy-research pipeline SOTA considerations

No Lab Architecture Fit research output was available. This section uses external Lab Validity Core input plus repo-truth boundaries.

Possible future lessons for Main/Karl decision:

- automated strategy generation increases false-discovery and overfit risk unless variant universe, trial budget, and result population are preserved;
- symbolic regression, genetic programming, evolutionary search, Bayesian optimization, Hyperband, and other adaptive methods may improve compute efficiency but require stronger audit and selection-bias controls;
- LLM-assisted research should remain support only, not approval or execution authority;
- experiment tracking and auditability should be first-class;
- false-discovery control should use full-population context, not winner-only review;
- human review remains required;
- bounded strategy generation is safer than open-ended autonomous search;
- full-population preservation and rejection of winner-only review are core design requirements.

No SOTA method is authorized or selected here.

## 22. Implementation-readiness map

Likely readiness categories before implementation authorization:

| Category | Current posture | Readiness gap |
|---|---|---|
| Strategy Spec / DSL artifact | Conceptual groups and non-executable posture locked | exact schema, fields, storage, examples, validator |
| Concept / Strategy Spec approval path | Discipline designed | artifact format, status enum, human approval mechanics |
| Variant manifest | Required future pre-registration surface locked | exact manifest format, IDs, storage, amendment semantics |
| Sweep plan / run manifest | Designed as future offline-research boundary | exact surfaces, runner boundary, abort/failure handling |
| Result population | Complete preservation locked | storage format, metric preservation, lineage links |
| Full-population lineage | Required by WP-S2c-158/159 | exact denominator and mapping to EXP/trial-log |
| Backtest realism | External validity concern identified | repo-locked taxonomy and thresholds absent |
| Search governance | Bounded/pre-registered posture established | MVP search method and adaptive-search rules undecided |
| Anti-overfit / DSR / PSR / MinTRL | Diagnostic posture designed | formulas, thresholds, denominators, return-path storage |
| Advisory ranking warnings | Human-review support designed | artifact schema, blocker/warning enums, no-score discipline |
| Scope 6 / R2S handoff | Human-review boundary designed | exact packet shape and approval-record references |
| Agent boundary / permissioning | Role boundaries designed | implementation, prompts, tools, orchestration, fail-closed controls |
| Validation and audit | Current repo validation discipline exists | future package-specific validators and scoped tests |
| Dashboard/operator review | External uncertainty-display concern identified | dashboard constraints and no-authority UX undecided |
| Runtime/paper/live exclusion | Protected boundary locked | remains excluded until separate gated packages |

## 23. Potential implementation tranches

Possible future tranches, if Main/Karl later authorize implementation work:

- Tranche A: concept and Strategy Spec artifact grammar.
- Tranche B: variant manifest and sweep-plan artifact grammar.
- Tranche C: offline research runner boundary and result-population storage.
- Tranche D: robustness, anti-overfit, and DSR / PSR / MinTRL support.
- Tranche E: advisory ranking artifact and human-review packet.
- Tranche F: bounded agent assistance surfaces.
- Tranche G: dashboard/operator-review surfaces.
- Tranche H: later paper/runtime bridge, only after separate gates.

These are options only. They are unranked and do not authorize WP-S2c-164 or implementation packages.

## 24. Risks and unresolved questions

Key risks:

- implementation could blur planning artifacts with evidence or decisions;
- advisory ranking could be misread as recommendation or approval;
- incomplete result populations could hide failed variants;
- adaptive search could increase selection bias without clear lineage;
- bar-based backtests could overstate edge if realism assumptions are weak;
- agent outputs could be treated as approvers if permissioning and handoff language are weak;
- dashboard surfaces could compress uncertainty into misleading ranks;
- exact EXP / REP / trial-log mapping for variant populations remains unresolved.

Unresolved questions remain Main/Karl decision inputs, not decisions made here.

## 25. Items that should be adopted now as process discipline

Safe process discipline already consistent with repo truth:

- keep fact, inference, decision, open question, and future option separate;
- preserve repo-truth precedence over external research and memory;
- keep lab surfaces non-executable and non-authoritative;
- preserve canonical evidence and decision surfaces;
- preserve complete result-population intent for future sweep work;
- expose warnings, blockers, and uncertainty;
- reject winner-only review;
- require explicit Main/Karl direction before WP-S2c-164 drafting.

These are documentation/process disciplines, not implementation changes.

## 26. Items that should be decided by Main/Karl

Main/Karl should decide:

- whether WP-S2c-164 should be drafted next;
- whether WP-S2c-164 should lock implementation authorization, implementation deferral, or additional design prerequisites;
- whether a lab validity floor is required before implementation;
- whether backtest-realism taxonomy must be locked before implementation;
- whether bounded search governance must be locked before implementation;
- whether walk-forward-first validation is required for MVP implementation;
- whether DSR / PSR / MinTRL support is required, optional, or deferred;
- whether Strategy Spec / DSL expressiveness-readiness criteria are required before implementation;
- whether agent orchestration readiness must be decided before implementation;
- whether dashboard/operator-review constraints must be decided before implementation;
- whether additional design WPs are required before WP-S2c-164;
- which external research findings should be adopted, deferred, rejected, or converted into future WPs.

## 27. Items that should be deferred

Items to defer unless explicitly pulled into WP-S2c-164 or later authorized tranches:

- exact artifact schemas, validators, query views, paths, IDs, examples, and storage;
- exact parser/compiler behavior;
- exact Strategy Spec operator vocabulary and nesting mechanics;
- exact variant/sweep/result/advisory/R2S packet formats;
- exact DSR / PSR / MinTRL implementation;
- exact robustness test suite;
- exact search method;
- agent implementation and orchestration;
- dashboard/operator UX;
- offline runner integration;
- paper/runtime bridge.

## 28. Items that should be rejected

Rejected or should-remain-rejected alternatives:

- executable Strategy Specs or arbitrary code in specs;
- Strategy Spec storage in the candidate registry;
- winner-only result retention;
- advisory rank as recommendation, approval, readiness, transition, or gate authority;
- agent approval, agent consensus approval, or supervisor-agent approval;
- automatic promotion or R2S based on rank, score, warning state, or agent output;
- hidden search-family expansion after results;
- result-population surfaces as parallel decision authority;
- runtime, paper/live, broker/exchange/order, OMS, risk, overlay, safe-mode, kill-switch, config, or protected-path contact from lab surfaces.

## 29. Forbidden implementation authority

This document creates no authority for:

- WP-S2c-164 drafting;
- implementation packages;
- schemas, validators, query views, parsers, compilers, tools, tests, code, fixtures, or dependency changes;
- concept artifacts, Strategy Spec artifacts, variant manifests, sweep plans, run manifests, result populations, advisory ranking artifacts, Scope 6 artifacts, approval records, or dashboard surfaces;
- candidate registration/update, EXP, REP, trial-log, OL, REC, DEC, or HYPOTHESIS.md changes;
- backtests, sweeps, optimizers, result aggregation, local-run-registry writes, or local-sweep-result writes;
- policy, ranking/scoring, recommendation, approval, readiness, promotion, demotion, transition, or gate execution;
- runtime, paper/live, broker/exchange/order, OMS, reconciliation, risk, overlay, safe-mode, kill-switch, config, dependency, data, monitoring, dashboard, AUTO, A2C-003, Track 3 / WP-S2c-140 reactivation, or protected-path contact.

## 30. WP-S2c-164 preparation

WP-S2c-164 remains Karl-gated.

This document prepares decision support only. It should be used to decide whether WP-S2c-164 should be drafted and what kind of decision it should record.

Possible WP-S2c-164 postures:

- lock implementation authorization for a narrow first tranche;
- lock implementation deferral and require additional design prerequisites;
- lock a methodology/validity floor before implementation;
- split decisions into one or more additional documentation packages before implementation.

No option is selected here.

## 31. Main/Karl decision questions

1. Should WP-S2c-164 be drafted next after Main/Karl report-back?
2. If yes, what should WP-S2c-164 lock: implementation authorization, implementation deferral, or additional design prerequisites?
3. Should implementation authorization require a lab validity floor?
4. Should implementation authorization require a backtest-realism taxonomy?
5. Should implementation authorization require bounded search governance?
6. Should implementation authorization require walk-forward-first validation?
7. Should DSR / PSR / MinTRL support be required, optional, or deferred?
8. Should the Strategy Spec / DSL need expressiveness-readiness criteria before implementation?
9. Should lab-agent orchestration readiness be decided before implementation?
10. Should dashboard/operator review constraints be decided before implementation?
11. Are additional design WPs required before WP-S2c-164?
12. Which research findings should be adopted, deferred, rejected, or converted into future WPs?

## 32. Validation posture

This package uses CS12 T1-doc-narrow validation unless repo truth or package discovery requires broader validation.

Expected validation includes diff whitespace checks, exact changed-file scope checks, forbidden-path diff checks, query-view listing, integrity views, current registry/artifact/outcome/reconciliation validators, and repo-conventional scoped pytest for research pipeline, registry, artifact, outcome, reconciliation, and integrity surfaces.

Full pytest is not expected for this package class unless current repo truth or validation results require it.

## 33. Next-package posture

After merge, Side must report back to Main/Karl before any WP-S2c-164 draft.

WP-S2c-164 remains Karl-gated and must not be drafted without explicit Main/Karl direction.

Implementation packages remain unauthorized.
