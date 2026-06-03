# Lab Validity Floor / Backtest-Realism / Bounded-Search Prerequisite Design

## 1. Scope

WP-S2c-165 / WP-12gl is a Tier 1 documentation-only methodology-prerequisite design package.

It defines design concepts for the Strategy Research Lab validity floor, crypto-perp backtest-realism taxonomy, bounded search governance, walk-forward-first MVP validation posture, and DSR / PSR / MinTRL prerequisite posture.

This package creates only this document and updates `docs/project_status.md`.

It creates no implementation authorization and no authority to create schemas, validators, query views, artifacts, code, tests, tools, runners, sweeps, dashboards, agents, prompts, storage paths, runtime behavior, paper/live behavior, protected-path changes, recommendation authority, approval authority, readiness authority, transition authority, ranking/scoring authority, or human-gate execution.

## 2. Repo-Truth And Decision Basis

Repo truth for this design is refreshed `main` after WP-S2c-164 / WP-12gk.

Primary basis:

- WP-S2c-164 locks Strategy Research Lab implementation deferral and identifies WP-S2c-165 as the first prerequisite design package.
- WP-S2c-147 through WP-S2c-163 define the lab lifecycle, Strategy Spec / DSL posture, concept-to-spec discipline, variant population pre-registration, sweep orchestration, result-population preservation, anti-overfit / DSR review, advisory ranking, Scope 6 / R2S boundaries, and agent-role boundaries.
- WP-S2c-158 locks future variant population manifests as the required pre-registration surface and locks complete result-population preservation.
- EXP / REP, trial-log, OL, REC, and DEC remain canonical evidence and decision surfaces.
- D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6, WP-S2c-100, WP-S2c-113, and permanent human gates remain preserved.

Current merged repo truth wins over external research, memory, summaries, handoffs, or generic best practice.

## 3. Design Objective

The objective is to convert the WP-S2c-164 prerequisite lock into a concrete design basis for future packages without authorizing implementation.

The design should let later packages know what evidence-quality and diagnostic concepts must be addressed before future lab output can be treated as clean enough for downstream human-review packet support.

## 4. Non-Authority Boundary

This design has no execution, implementation, policy, ranking, recommendation, approval, readiness, transition, paper/live, runtime, or protected-path authority.

The lab validity floor is a future evidence and diagnostic sufficiency design. It is not a runtime gate, approval gate, recommendation system, execution authority, or human-gate executor.

Human gates remain human gates.

Implementation remains unauthorized.

## 5. Relationship To WP-S2c-164

WP-S2c-164 deferred lab implementation and required prerequisite design before any implementation tranche can be reconsidered.

This document answers the first prerequisite cluster:

- lab validity floor;
- crypto-perp backtest-realism taxonomy;
- bounded search governance;
- walk-forward-first MVP validation posture;
- DSR / PSR / MinTRL prerequisite posture.

This document does not satisfy the remaining prerequisite chain by itself and does not authorize any implementation package.

## 6. External Research Input Handling

External research is design input only. It is not repo truth and cannot override committed repo decisions.

External Lab Validity Core findings used as rationale include: crypto-perp realism depends on fees, funding, fills, liquidity, order size, mark/index mechanics, liquidation, exchange constraints, and bar-path assumptions; search efficiency is not validity; constrained manual grids and constrained random search are safer MVP postures than adaptive search; walk-forward-first is practical for MVP validation; and full population retention is prerequisite for DSR / PSR / MinTRL-style interpretation.

External Lab Architecture Fit findings used as rationale include: Strategy Spec should remain typed, declarative, non-executable, side-effect-free, host-data-bounded, and separate from runtime code; dangerous expressiveness includes arbitrary code, user-defined functions, recursion, loops, external calls, arbitrary callbacks, self-modifying rules, and imperative control flow; and agent workflows should prefer explicit, durable, auditable human-in-the-loop workflows over open-ended autonomous loops.

These findings support design boundaries only. They do not authorize DSL schemas, agents, orchestration, dashboards, code, storage, or implementation.

## 7. Lab Validity Floor Definition

The lab validity floor is the minimum future evidence and diagnostic posture needed before lab outputs can be treated as clean enough for downstream human-review packet support.

It is a review-support sufficiency concept. It does not approve candidates, recommend execution, rank with authority, satisfy D2-006, satisfy REC-5, create readiness, or trigger transitions.

The floor should require visibility into backtest-realism assumptions, result-population completeness, search lineage, walk-forward / OOS posture, robustness diagnostics, and DSR / PSR / MinTRL prerequisite posture before clean advisory consumption.

## 8. Validity-Floor States

Future design may distinguish conceptual states such as:

- sufficient for human-review support;
- qualified or usable with warning;
- blocked from clean advisory consumption;
- insufficient evidence;
- incomplete result population;
- missing search lineage;
- unresolved backtest-realism assumptions;
- unresolved walk-forward / OOS posture;
- unresolved DSR / PSR / MinTRL posture;
- not applicable or deferred.

These are design concepts only, not schema fields, enum values, validator behavior, query behavior, dashboard labels, or implementation contracts.

## 9. Crypto-Perp Backtest-Realism Taxonomy

Future taxonomy should cover at least fees, funding, slippage and fills, liquidity and order-size realism, mark/index mechanics, liquidation and maintenance margin, exchange constraints, bar-path assumptions, stale fill / latency assumptions where relevant, and order-type / time-in-force constraints where relevant.

For each category, future human review should see why the category matters, which assumptions were used, what could qualify the result, what could block clean advisory consumption, and which details remain deferred to implementation.

This package defines no formulas, thresholds, storage paths, validators, runner behavior, or engine mechanics.

## 10. Bar-Based Backtest Assumption Posture

Bar-based backtests may be acceptable for research-stage human-review support only under explicit assumptions:

- order size is small relative to available liquidity or capacity;
- fill and slippage assumptions are conservative;
- results do not rely on optimistic intrabar stop/limit sequencing;
- timeframe and data support are declared;
- fees, funding, and cost assumptions are disclosed;
- limitations for path-dependent or microstructure-sensitive strategies are declared.

Strategies depending materially on queue position, aggressive intrabar fills, high turnover, liquidation timing, funding/carry mechanics, or larger taker size may require later volume/depth/order-book-aware design before clean advisory consumption.

## 11. Backtest Realism Blocker / Qualifier Categories

Future review should distinguish qualifiers from blockers.

Potential qualifiers include conservative approximations, known fee/funding assumptions, bounded liquidity assumptions, declared bar-path limitations, or incomplete but transparent stress coverage.

Potential blockers include missing fees or funding where material, optimistic fill assumptions, hidden intrabar path dependency, unrealistic order size, unavailable data, unmodeled liquidation risk, exchange-constraint mismatch, unsupported order type assumptions, or result dependence on latency/queue mechanics that the model cannot represent.

Exact blocker labels, thresholds, and enforcement mechanics remain deferred.

## 12. Bounded Search Governance

Future bounded search governance should define how search is pre-registered, constrained, preserved, and interpreted.

Required design concepts include search family identity, parent Strategy Spec reference, variant population reference, parameter bounds, invalid combinations and exclusions, trial budget, amendment posture, search rule or generator rule, retention of failed/invalid/excluded/errored/aborted/filtered/data-unavailable/successful trials, lineage from concept to Strategy Spec to variant population to sweep plan/run to result population, and effective-trial-count / denominator posture for later DSR-like interpretation.

Search efficiency is not validity. Faster search does not reduce multiple-testing burden or remove selection-bias risk.

## 13. Allowed MVP Search Postures

Constrained manual grids and constrained random search are the preferred MVP-compatible design postures unless Main/Karl later authorizes another method.

These postures are preferred because they are easier to pre-register, bound, preserve, and audit. They still require full lineage, trial-budget accounting, and result-population retention.

This package does not authorize any search implementation or sweep execution.

## 14. Deferred Or Unauthorized Search Postures

Bayesian optimization, Hyperband, evolutionary or genetic search, symbolic search, open-ended LLM-generated strategy expansion, portfolio optimizer search, and adaptive pruning remain unauthorized until later explicitly designed and authorized.

If later authorized, adaptive methods must still preserve lineage, denominator accounting, failed and pruned trial visibility, amendment posture, and full result-population context.

## 15. Full Search-Family Lineage Requirements

Future search-family lineage should preserve the complete path from source idea to concept, Strategy Spec, variant population, search family, sweep plan or run manifest, result population, canonical EXP / REP and trial-log references where applicable, OL, REC, DEC, and any human-review packet context.

Lineage gaps should qualify or block clean advisory consumption depending on materiality.

Exact identifiers, paths, hashes, fields, validators, and query surfaces remain deferred.

## 16. Result-Population Completeness Requirements

Future result populations must preserve the complete tested universe, not only winners.

Completeness should include attempted variants, not-attempted variants and reasons, failed variants, invalid combinations, exclusions, errored variants, aborted runs, filtered variants, data-unavailable cases, timeout/resource failures, retries/reruns where applicable, and successful variants.

Incomplete result populations should block or qualify anti-overfit review and advisory consumption.

## 17. Walk-Forward-First MVP Validation Posture

Walk-forward-first is the default future MVP validation design posture unless Main/Karl later replaces it.

Design concepts include chronological train/test separation, no future leakage, explicit future window definitions, result comparison across windows, treatment of unstable or window-dependent performance, relationship to full result-population retention, relationship to DSR / PSR / MinTRL design, and advisory warnings or blockers for poor or unresolved OOS posture.

This document does not define split windows, thresholds, data requirements, validators, or implementation mechanics.

## 18. DSR / PSR / MinTRL Prerequisite Posture

DSR-like review requires full population context and search-lineage information.

PSR-like review may support candidate-level Sharpe credibility, but cannot replace population-level multiple-testing posture.

MinTRL-like review may support sample sufficiency interpretation.

Exact formulas, thresholds, denominator rules, return-path storage, storage fields, validators, and implementation remain deferred.

These outputs remain interpretive support only and cannot become approval, recommendation, ranking authority, readiness, transition, paper/live, runtime, or gate execution.

## 19. Robustness And Stress-Test Considerations

Future design should consider cost/funding/slippage stress, parameter sensitivity, regime stability, drawdown and tail-risk concentration, sample-size and trade-count sufficiency, single-event or single-trade dependency, pre-registration mismatch, trial-budget irregularities, and incomplete evidence.

CPCV, purged CV, bootstrap, Monte Carlo, and permutation tests are later or conditional strengthening options, not mandatory MVP implementation.

Exact robustness protocols, thresholds, and mechanics remain deferred.

## 20. Advisory-Ranking Consumption Boundary

Advisory ranking may consume future validity-floor signals as warnings, blockers, qualifiers, or explanatory context only.

Validity-floor signals cannot approve a candidate, recommend execution, create readiness, promote or transition, satisfy D2-006, satisfy D2-007, satisfy REC-5, satisfy Scope 6, satisfy Phase 9 / D2-011, execute human gates, update candidate registry state, or contact runtime/paper/live/protected paths.

`Ranked higher` remains review priority only.

## 21. Scope 6 / R2S Consumption Boundary

Scope 6 / R2S review may later use validity-floor signals as human-review packet context only.

Validity-floor signals cannot create or update R2S approval records, shadow-evidence retention artifacts, S2P approval records, transition machinery, paper/live readiness, or human-gate execution.

Scope 6 / R2S remains human-gated.

## 22. Dashboard / Operator-Review Future Boundary

Future dashboards or operator-review surfaces, if later authorized, may display validity-floor signals as blockers, warnings, qualifiers, uncertainty, and lineage context.

They must not hide uncertainty behind a single score, execute approvals, update readiness, recommend trading, trigger transitions, write artifacts without explicit scope, or contact runtime/paper/live/protected paths.

No dashboard or operator-review surface is created here.

## 23. Relationship To Strategy Spec / DSL Expressiveness

The Strategy Spec / DSL lock remains unchanged: Strategy Spec is the future human-reviewable artifact/surface, and Strategy DSL is constrained representation discipline, not executable code or a runtime interface.

Validity-floor design supports that boundary by requiring search and realism assumptions to stay declarative, typed, host-data-bounded, side-effect-free, and reviewable.

Dangerous expressiveness remains out of bounds: arbitrary code, user-defined functions, recursion, loops, arbitrary callbacks, external calls, self-modifying rules, and imperative control flow.

This document creates no Strategy Spec schema, example, parser, compiler, storage path, or artifact.

## 24. Relationship To Agent Orchestration

Future agents may support drafting, summarizing, completeness checking, warning/blocker surfacing, packet preparation, and conflict reporting only if later authorized.

Validity-floor and bounded-search concepts may give future agents checklist material, but agents must not approve, reject, rank with authority, execute sweeps, compute authority-bearing metrics, mutate artifacts outside scope, satisfy gates, or contact runtime/protected paths.

Open-ended autonomous agent loops remain unauthorized.

## 25. Implementation-Readiness Implications

Before implementation can be reconsidered, future packages must preserve this design posture:

- validity floor as review-support sufficiency, not authority;
- crypto-perp realism assumptions visible before clean advisory consumption;
- bounded search pre-registration and full result-population retention;
- walk-forward-first MVP validation unless Main/Karl changes it;
- DSR / PSR / MinTRL support as interpretive prerequisites with formulas deferred;
- canonical evidence surfaces and human gates preserved.

This document is prerequisite design only and does not make implementation ready.

## 26. Deferred Implementation Details

Deferred details include exact schema fields, enum values, validators, query views, storage paths, artifact IDs, examples, formulas, thresholds, split windows, return-path storage, denominator rules, runner behavior, search algorithms, optimizer mechanics, dashboard views, agent workflows, prompts, and implementation sequence.

Any future implementation requires explicit Main/Karl direction and a scoped package.

## 27. Rejected Alternatives

Rejected alternatives:

- treating search efficiency as validity;
- treating a single best backtest as clean evidence;
- winner-only result retention;
- hidden failed or excluded variants;
- adaptive search without later explicit design and authorization;
- bar-based backtests with optimistic intrabar assumptions as clean;
- DSR / PSR / MinTRL as approval, recommendation, ranking, readiness, transition, paper/live, runtime, or gate authority;
- advisory ranking as recommendation or approval;
- dashboards, agents, scores, or validity-floor states executing human gates;
- implementation authorization from this prerequisite design.

## 28. Future Package Dependencies

Future packages may need to design or lock Strategy Spec / DSL expressiveness readiness, agent orchestration readiness, dashboard/operator-review constraints, exact validity-floor artifact grammar if later authorized, exact backtest-realism fields if later authorized, search-family and result-population storage if later authorized, walk-forward mechanics if later authorized, and DSR / PSR / MinTRL formulas if later authorized.

Each future package must start from refreshed repo truth and preserve protected boundaries.

## 29. Validation Posture

This package uses CS12 T1-doc-major-decision validation.

Validation proves changed-file scope and repo consistency only. It does not create implementation authority.

Expected validation includes refreshed-main preflight, exact changed-file scope checks, forbidden-path diff checks, query-view listing, all discovered `v_integrity_*` views, registry/artifact/outcome/reconciliation validators, repo-conventional scoped pytest for research pipeline and integrity surfaces, full pytest, staged diff checks, and clean final status.

## 30. Next-Package Posture

After merge, Side may draft the next prerequisite design package after refreshed-main preflight and no stop trigger, unless Main/Karl directs otherwise.

Implementation remains unauthorized.

No schema, validator, query view, artifact, code, test, tool, runner, sweep, dashboard, agent, prompt, storage path, runtime/paper/live, protected-path, approval, readiness, transition, recommendation, ranking/scoring, or human-gate execution package is authorized by WP-S2c-165.
