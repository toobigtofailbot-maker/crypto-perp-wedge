# Strategy Spec / DSL Expressiveness-Readiness Design

## 1. Scope

WP-S2c-166 / WP-12gm is a Tier 1 documentation-only methodology-prerequisite design package.

It defines Strategy Spec / DSL expressiveness-readiness criteria before any future Strategy Spec artifact schema, parser/compiler behavior, validator, query view, artifact instance, runner, agent, dashboard, or implementation package.

This package creates only this document and updates `docs/project_status.md`.

It creates no implementation authorization and no authority to create schemas, validators, query views, artifact instances, code, tests, tools, runners, sweeps, dashboards, agents, prompts, storage paths, runtime behavior, paper/live behavior, protected-path changes, recommendation authority, approval authority, readiness authority, transition authority, ranking/scoring authority, or human-gate execution.

## 2. Repo-Truth And Decision Basis

Repo truth for this design is refreshed `main` after WP-S2c-165 / WP-12gl.

Primary basis:

- WP-S2c-151 locks Strategy Spec as the future human-reviewable surface and Strategy DSL as constrained representation discipline.
- WP-S2c-158 locks future variant population manifests as the required pre-registration surface and locks complete result-population preservation.
- WP-S2c-159, WP-S2c-160, and WP-S2c-161 preserve anti-overfit review, advisory ranking, and Scope 6 / R2S as human-review support only.
- WP-S2c-162 preserves future agents as support-only.
- WP-S2c-164 defers implementation and requires Strategy Spec / DSL expressiveness-readiness criteria before artifact implementation.
- WP-S2c-165 defines the lab validity floor, backtest-realism taxonomy, bounded-search governance, walk-forward-first MVP validation posture, and DSR / PSR / MinTRL prerequisite posture.
- EXP / REP, trial-log, OL, REC, and DEC remain canonical evidence and decision surfaces.
- D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6, WP-S2c-100, WP-S2c-113, and permanent human gates remain preserved.

Current merged repo truth wins over external research, memory, summaries, handoffs, or generic best practice.

## 3. Design Objective

The objective is to define what future Strategy Spec / DSL expressiveness must be ready to represent at the design level before any artifact implementation is reconsidered.

The criteria should let later packages reason about whether intended MVP strategy concepts can be represented clearly enough for human review, bounded variant generation, search governance, result lineage, validity-floor review, and later implementation design.

The design does not decide exact fields, grammar, operator vocabulary, nested-condition mechanics, schema, storage, parser/compiler behavior, validator behavior, query behavior, examples, or executable semantics.

## 4. Non-Authority Boundary

This design has no execution, implementation, policy, ranking, recommendation, approval, readiness, transition, paper/live, runtime, or protected-path authority.

Strategy Spec / DSL is not runtime code, not a broker/exchange/order interface, not a config surface, not a paper/live interface, and not a policy or approval surface.

Expressiveness readiness defines what future artifact design must be able to reason about, not how it will be implemented.

Human gates remain human gates.

Advisory ranking remains human-review support only.

Scope 6 / R2S remains human-gated.

Implementation remains unauthorized.

## 5. Relationship To WP-S2c-164 And WP-S2c-165

WP-S2c-164 deferred Strategy Research Lab implementation and required prerequisite design before any implementation tranche can be reconsidered.

This document answers the Strategy Spec / DSL expressiveness-readiness prerequisite identified by WP-S2c-164.

WP-S2c-165 defines validity-floor, backtest-realism, bounded-search, walk-forward-first, and DSR / PSR / MinTRL prerequisite posture. This document complements that design by requiring future strategy representation to keep assumptions visible enough for those later reviews.

This document does not satisfy remaining prerequisites such as agent orchestration readiness or dashboard/operator-review constraints, and it does not authorize implementation.

## 6. External Research Input Handling

External research is design input only. It is not repo truth and cannot override committed repo decisions.

No standalone external research file was found in repo-local search. This document uses the summarized external input from the active package and the external findings already summarized in WP-S2c-165.

External Lab Architecture Fit findings used as rationale include: Strategy Spec should remain typed, declarative, non-executable, side-effect-free, host-data-bounded, and separate from runtime code; dangerous expressiveness includes arbitrary code, user-defined functions, recursion, loops, unrestricted custom functions, arbitrary host callbacks, external calls, self-modifying rules, hidden strategy mutation, and imperative control flow; and automated research pipelines should preserve provenance, lineage, failed/rejected variants, experiment tracking, and separation of ideation, specification, variation, testing, review, and deployment.

External Lab Validity Core linkages used as rationale include: expressiveness readiness should support later validity-floor, bounded-search, result-population, and DSR / PSR / MinTRL review by making assumptions explicit and audit-friendly; Strategy Spec expressiveness must not enable hidden search expansion, post-result mutation, arbitrary executable logic, or winner-only framing.

These findings support design boundaries only. They do not authorize schemas, validators, query views, parser/compiler behavior, artifacts, agents, dashboards, code, storage, runners, sweeps, or implementation.

## 7. Strategy Spec / DSL Expressiveness-Readiness Definition

Strategy Spec / DSL expressiveness readiness is the future ability to represent intended MVP strategy concepts clearly enough for human review, bounded variant generation, search governance, result lineage, validity-floor review, and later implementation design.

It means future artifact design can describe strategy intent, assumptions, variant axes, and review questions without collapsing into executable strategy code.

It does not mean executable strategy code, runtime compatibility, complete coverage of all future strategies, parser/compiler readiness, schema readiness, artifact readiness, approval, promotion, readiness, transition authority, or gate execution.

Readiness is a prerequisite design concept only.

## 8. Core Representation Principles

Future Strategy Spec / DSL representation should remain:

- typed;
- declarative;
- non-executable;
- side-effect-free;
- host-data-bounded;
- auditable;
- deterministic as a description;
- separated from runtime code and broker/exchange/order behavior;
- explicit about data, timeframe, cost, slippage, and funding assumptions where relevant;
- suitable for bounded variant derivation only after later authorization;
- suitable for human review and uncertainty surfacing.

The representation must make assumptions visible enough for later validity-floor, backtest-realism, bounded-search, result-population, and Scope 6 / R2S review.

## 9. MVP-Critical Pattern Families

Likely MVP-critical pattern families for future readiness are:

- multi-signal entries;
- explicit exits;
- sizing and risk-parameter expression;
- regime filters;
- multi-timeframe references;
- trend-following;
- mean reversion;
- breakout logic;
- funding / carry concepts;
- basis / spread concepts;
- risk overlays;
- cooldowns;
- no-trade filters;
- time / session filters.

Each family matters because the Strategy Research Lab target lifecycle expects future Strategy Specs to represent reviewable entry, exit, risk, data, timeframe, and assumption structure before bounded variants and sweeps are planned.

Future human review should see what the strategy intends, which assumptions are material, which parameters or choices may become bounded variant axes, which data/timeframe/cost/funding assumptions matter, and which limitations should qualify validity or backtest-realism review.

Implementation details remain deferred.

## 10. Deferred Pattern Families

Likely deferred pattern families may be useful later but should not be assumed MVP-ready unless Main/Karl later authorizes them:

- complex path-dependent order management;
- order-book / queue-position strategies;
- high-frequency microstructure logic;
- portfolio optimization;
- multi-asset allocation engines;
- ML model inference inside specs;
- external data calls;
- cross-venue execution logic;
- adaptive strategy mutation;
- reinforcement-learning policies;
- self-tuning strategies;
- event-driven callbacks.

These are future design topics, not permanent bans, unless they overlap with rejected or dangerous expressiveness.

Deferral means the MVP representation should not depend on these patterns for initial artifact implementation readiness.

## 11. Rejected / Dangerous Expressiveness

Rejected or out-of-bounds expressiveness includes:

- arbitrary Python, shell, SQL, or other executable code in Strategy Specs;
- unrestricted custom functions;
- user-defined callbacks;
- recursion;
- loops;
- arbitrary host callbacks;
- external network, file, or process calls;
- runtime side effects;
- mutable global state;
- self-modifying rules;
- hidden strategy mutation after results;
- imperative order-routing instructions;
- broker/exchange/order API directives;
- config or dependency changes through specs;
- live, paper, or runtime controls;
- any expression that can execute gates or update readiness.

These patterns are incompatible with the WP-S2c-151 non-executable declarative lock unless Main/Karl later reopens the architecture.

## 12. Multi-Signal Entry Readiness

Future readiness should support reviewable multi-signal entry concepts such as combining price action, volatility, trend, funding, basis, regime, or time filters.

Human review should see each signal's role, whether it is required or confirming, the source data and timeframe assumption, and which signals may become bounded variant axes.

Validity and search review should see how multiple signals increase search space and multiple-testing exposure.

Implementation must defer exact boolean grammar, operator names, nesting mechanics, precedence rules, schema fields, and executable evaluation semantics.

## 13. Exit And Lifecycle Expression Readiness

Future readiness should support explicit exit concepts, including signal reversal, stop or risk exit concepts, time-based exits, maximum holding periods, invalidation rules, and lifecycle assumptions such as flat, long, short, or position-state references where reviewable.

Human review should see why and when a strategy is expected to leave exposure, how exits relate to entries, and whether exits create path-dependency or intrabar assumptions.

Validity review should see whether exits rely on bar-path ordering, liquidity, slippage, funding timing, or optimistic fill assumptions.

Implementation mechanics for state handling, stop evaluation, intrabar sequencing, and runner behavior remain deferred.

## 14. Sizing And Risk-Parameter Expression Readiness

Future readiness should support reviewable sizing and risk-parameter concepts such as fixed notional, fractional equity intent, maximum exposure, stop distance, profit target, leverage assumption, volatility adjustment, and no-parameter declarations where applicable.

Human review should see parameter units, bounded ranges or no-parameter posture, economic rationale, and risk assumptions.

Validity review should see fees, slippage, funding, liquidity, order-size, liquidation, maintenance-margin, and D-0001-related assumptions where relevant.

This document does not define exact risk formulas, risk caps, schema fields, runner integration, or runtime risk behavior.

## 15. Regime Filter And Multi-Timeframe Readiness

Future readiness should support regime filters and multi-timeframe references as declared reviewable dependencies.

Regime filters may describe trend/range, volatility, funding, basis, session, drawdown, or other host-provided context if later authorized.

Multi-timeframe references should declare primary timeframe and confirmation timeframe intent within locked research timeframe posture where applicable.

Human review should see data availability, alignment assumptions, lookahead risk, and whether a confirmation timeframe expands tested surface area.

Implementation details for resampling, alignment, missing-data handling, and exact timeframe operators remain deferred.

## 16. Trend / Mean-Reversion / Breakout Readiness

Future readiness should support common MVP strategy families:

- trend-following logic, where exposure follows directional persistence;
- mean-reversion logic, where exposure assumes deviation normalization;
- breakout logic, where exposure follows range expansion or threshold crossing.

Human review should see the mechanism, directionality, data inputs, parameter families, invalidation logic, and expected failure modes.

Validity review should see whether the pattern is cost-sensitive, sample-size-sensitive, regime-concentrated, or dependent on optimistic bar-path assumptions.

No exact indicators, thresholds, field names, formulas, or executable semantics are locked here.

## 17. Funding / Carry / Basis / Spread Concept Readiness

Future readiness should support reviewable funding, carry, basis, premium, and spread concepts where host-provided data and repo authorization support them.

Human review should see which stream is referenced, whether the concept is directional or filter-like, the timeframe relationship, and how costs or funding timing affect the thesis.

Validity review should see data gaps, mark/index/premium provenance, funding-rate timing, cost drag, and whether the concept depends on unavailable external or cross-venue data.

This document creates no new data authority, data fetch, schema, query view, or cross-venue execution design.

## 18. Risk Overlay / Cooldown / No-Trade / Time-Filter Readiness

Future readiness should support declarative risk overlay concepts, cooldowns, no-trade filters, and time/session filters as reviewable strategy assumptions.

Human review should see whether a filter limits exposure, reduces churn, avoids known weak regimes, or controls path-dependent behavior.

Validity review should see whether a filter creates hidden search expansion, post-result rescue behavior, sparse sample issues, or regime overfitting.

These concepts must not modify the protected runtime overlay output set, D-0001 hard risk caps, safe-mode behavior, or paper/live runtime controls.

Exact filter grammar, cooldown state mechanics, and implementation behavior remain deferred.

## 19. Host-Data And Data-Dependency Boundaries

Future specs should reference only host-provided, declared, reviewable data surfaces.

They must not fetch data, create external calls, mutate data, write artifacts, read arbitrary files, or make undeclared assumptions.

Data, timeframe, funding, cost, slippage, mark/index/premium, and provenance assumptions should remain visible for validity-floor and backtest-realism review.

Unavailable, unauthorized, or externally fetched data dependencies should block, defer, or qualify progression rather than being hidden in Strategy Spec logic.

This package creates no data path, data catalog change, query view, or data-access behavior.

## 20. State And Path-Dependency Boundaries

Future specs may need to describe simple declarative state concepts at the design level, such as cooldown state, position state, prior signal state, maximum holding period, or exposure lifecycle.

Those simple concepts may be MVP-compatible if they remain non-executable, reviewable, and host-interpreted only after later implementation authorization.

Complex stateful logic should remain deferred, including queue-position models, intrabar path dependency, adaptive state machines, event callbacks, self-modifying policies, and execution-order state machines.

Future review must distinguish assumptions that can be honestly tested with bar-based research from assumptions that require later volume, depth, microstructure, or execution-aware design.

No state implementation mechanics are defined here.

## 21. Search / Variant-Generation Relationship

Expressiveness readiness must support bounded variant generation and search governance without enabling hidden search expansion.

Future specs should make possible variant axes, parameter bounds, invalid combinations, exclusions, no-parameter declarations, and amendment posture explicit enough for later variant-population design.

The Strategy Spec should not silently generate unlimited variants, mutate after results, add unregistered filters, or hide exploratory attempts.

This package does not create variant manifests, parameter grids, search schemas, search algorithms, sweep plans, runner behavior, or trial-budget implementation.

## 22. Validity-Floor And Backtest-Realism Relationship

Strategy Spec / DSL expressiveness must preserve enough declared assumptions for future lab validity-floor and backtest-realism review.

Those assumptions include data/timeframe support, fees, funding, slippage, cost assumptions, bar-path limitations, liquidity and order-size assumptions, mark/index mechanics, liquidation sensitivity, and limitations around path-dependent or microstructure-sensitive strategies.

A spec that depends on unmodeled fills, queue position, unavailable data, optimistic intrabar sequencing, or hidden leverage assumptions should be qualified, blocked, or deferred by later review.

This document modifies no validity-floor state, threshold, formula, or validator behavior.

## 23. Result-Population / Lineage Relationship

Future Strategy Spec / DSL artifacts should be lineage anchors for concept-to-spec flow, variant population, sweep planning or run manifests, result population, advisory ranking, Scope 6 / R2S review packets, and canonical evidence references if later authorized.

Lineage should make it possible to audit how a source idea became a Strategy Spec, which variants were derived, which results were retained, and which evidence supported later review.

Complete result-population preservation from WP-S2c-158 remains required for future sweep outputs.

This package does not create artifact IDs, storage paths, lineage fields, validators, query views, result populations, EXP, REP, trial-log rows, OL, REC, or DEC entries.

## 24. Agent And Dashboard Future-Consumption Boundary

Future agents and dashboards may later consume Strategy Spec / DSL expressiveness metadata as review support, warning/blocker context, completeness checks, or packet-preparation input only if later authorized.

They must not approve specs, promote candidates, execute gates, mutate specs outside package scope, run backtests or sweeps, produce recommendation authority, update readiness, trigger transitions, or contact runtime/paper/live/protected paths.

Dashboards, if later authorized, should expose uncertainty, blockers, lineage, and assumptions rather than hiding them behind a single score.

No agent, prompt, dashboard, operator surface, tool, or implementation is created here.

## 25. Implementation-Readiness Implications

Before Strategy Spec artifact implementation can be reconsidered, future packages should preserve this design posture:

- MVP-critical pattern families are representable as reviewable declarations;
- deferred pattern families are not assumed MVP-ready;
- rejected expressiveness remains out of bounds;
- host-data dependencies and assumptions are explicit;
- simple state concepts are separated from complex path dependency;
- variant axes and bounds are visible enough for pre-registration;
- validity, backtest-realism, result-population, and lineage needs are visible;
- canonical evidence surfaces and human gates remain preserved.

This document is prerequisite design only and does not make implementation ready.

## 26. Deferred Implementation Details

Deferred details include exact schema fields, field names, enum values, operator vocabulary, nested-condition mechanics, grammar, examples, fixtures, validators, query views, storage paths, artifact IDs, parser/compiler behavior, host interpreter behavior, runner integration, data-binding mechanics, formula definitions, thresholds, split mechanics, variant-manifest mapping, EXP/trial-log mapping, dashboard views, agent workflows, prompts, and implementation sequence.

Any future implementation requires explicit Main/Karl direction and a scoped package.

## 27. Rejected Alternatives

Rejected alternatives:

- treating Strategy Spec as executable code;
- treating Strategy DSL as parser/compiler implementation authority;
- embedding arbitrary code or callbacks in specs;
- using specs as broker/exchange/order directives;
- using specs as config or dependency mutation surfaces;
- allowing specs to fetch external data or read arbitrary files;
- allowing hidden post-result mutation;
- allowing unbounded search by expressive loophole;
- treating Strategy Spec approval as candidate approval, EXP authority, sweep authority, recommendation, ranking, readiness, transition, paper/live approval, runtime approval, or gate satisfaction;
- treating advisory ranking as recommendation or approval;
- allowing dashboards, agents, scores, or specs to execute human gates;
- implementation authorization from this prerequisite design.

## 28. Future Package Dependencies

Future packages may need to design or lock:

- exact Strategy Spec artifact grammar;
- exact Strategy Spec storage path and ID posture;
- exact schema fields and validators;
- exact query/read-model surfaces;
- exact operator vocabulary and nested-condition limits;
- host-data binding discipline;
- concept-to-spec storage and linking;
- variant-manifest storage and Strategy Spec mapping;
- result-population linkage;
- EXP / REP / trial-log mapping;
- agent orchestration readiness;
- dashboard/operator-review constraints;
- implementation authorization sequence.

Each future package must start from refreshed repo truth and preserve protected boundaries.

## 29. Validation Posture

This package uses CS12 T1-doc-major-decision validation unless current repo truth requires a different profile.

Validation proves changed-file scope and repo consistency only. It does not create implementation authority.

Expected validation includes refreshed-main preflight, exact changed-file scope checks, forbidden-path diff checks, query-view listing, all discovered `v_integrity_*` views, registry/artifact/outcome/reconciliation validators, repo-conventional scoped pytest for research pipeline and integrity surfaces, full pytest, staged diff checks, and clean final status.

## 30. Next-Package Posture

After merge, Side may draft the next prerequisite design package after refreshed-main preflight and no stop trigger, unless Main/Karl directs otherwise.

Implementation remains unauthorized.

No schema, validator, query view, artifact, parser/compiler, code, test, tool, runner, sweep, dashboard, agent, prompt, storage path, runtime/paper/live, protected-path, approval, readiness, transition, recommendation, ranking/scoring, or human-gate execution package is authorized by WP-S2c-166.
