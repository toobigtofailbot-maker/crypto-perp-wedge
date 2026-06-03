# Lab Implementation Deferral / Prerequisite Lock

## 1. Scope

WP-S2c-164 / WP-12gk is a Tier 1 documentation-only Karl-gated decision and methodology-prerequisite lock.

It records the Main/Karl direction after WP-S2c-163: Strategy Research Lab implementation is not authorized yet, implementation remains deferred, and additional methodology/design prerequisites must be designed and locked before any implementation tranche can be reconsidered.

This package creates only this document and updates `docs/project_status.md`.

This package creates no implementation authority, no WP-S2c-164 implementation authorization, and no authority to create schemas, validators, query views, artifacts, runners, sweeps, code, tests, dashboards, agents, prompts, storage paths, strategy execution, backtests, optimizers, result aggregation, transition machinery, runtime/paper/live contact, ranking authority, recommendation authority, approval authority, readiness authority, or human-gate execution.

## 2. Decision Authority And Repo-Truth Basis

Repo truth for this decision is the refreshed `main` state after WP-S2c-163.

WP-S2c-163 consolidated the Strategy Research Lab design tranche into decision support for Main/Karl, used available Side Research as external input only, and noted that Lab Architecture Fit research was not available.

The execution direction for WP-S2c-164 states that this package must be an implementation-deferral / methodology-prerequisite lock, not an implementation authorization package.

Current merged repo truth, this active package scope, `AGENTS.md`, and supporting Codex workflow docs remain the governing precedence order. External research, chat memory, and prior summaries are not repo truth.

## 3. Decision Summary

Decisions locked here:

- Strategy Research Lab implementation is deferred.
- WP-S2c-164 does not authorize implementation.
- Additional Tier 1 design packages are required before any implementation tranche.
- A lab validity floor must be designed before implementation.
- A crypto-perp backtest-realism taxonomy must be designed before implementation.
- Bounded search governance must be designed before implementation.
- Future MVP research execution posture must be walk-forward-first unless Main/Karl later explicitly replaces it.
- DSR / PSR / MinTRL-style interpretive support must be accounted for as design prerequisites.
- Strategy Spec / DSL expressiveness-readiness criteria must be designed before artifact implementation.
- Agent orchestration readiness must be designed before any agent implementation.
- Dashboard/operator-review constraints must be designed before any dashboard or operator-review surface.
- Missing Lab Architecture Fit research is an input gap, not a reason to wait indefinitely.

## 4. Implementation Deferral Lock

No implementation authorization is granted by WP-S2c-164.

Implementation remains unauthorized until:

- the prerequisite design chain is complete;
- protected-boundary review remains clean;
- Main/Karl gives later explicit implementation direction; and
- a future scoped work package authorizes exact implementation files, validation, and boundaries.

This package does not select an exact implementation tranche. It does not authorize a first artifact, schema, validator, query view, runner, dashboard, agent, parser/compiler, code path, or storage path.

## 5. Required Prerequisite Design Packages

At least one additional Tier 1 design package must be completed after WP-S2c-164 before any implementation tranche.

The expected next design package, unless Main/Karl directs otherwise, is:

```text
WP-S2c-165: Lab validity floor / backtest-realism / bounded-search prerequisite design
```

WP-S2c-165 may combine closely related prerequisite topics where doing so improves efficiency without weakening clarity or safety:

- lab validity floor;
- crypto-perp backtest-realism taxonomy;
- bounded search governance;
- walk-forward-first MVP validation posture;
- DSR / PSR / MinTRL design prerequisites.

Future prerequisite design packages remain documentation-only unless separately authorized. They must not implement schemas, validators, query views, artifacts, code, tests, dashboards, agents, runners, runtime behavior, paper/live behavior, or protected-path changes.

## 6. Lab Validity Floor Prerequisite

A future Tier 1 design package must define what evidence and diagnostic posture is required before lab outputs can be treated as clean enough for implementation consumption or human-review packet support.

This lock does not define the validity floor itself.

The future floor should distinguish between:

- sufficient evidence for human review support;
- insufficient or blocked evidence;
- incomplete result-population support;
- unresolved realism assumptions;
- unresolved search-lineage or trial-budget concerns;
- outputs that may be summarized but not consumed by downstream review packets.

The future floor must preserve canonical evidence surfaces and human gates. It must not become approval, recommendation, ranking, readiness, transition, or runtime authority.

## 7. Crypto-Perp Backtest-Realism Taxonomy Prerequisite

Future design must define a crypto-perp backtest-realism taxonomy before implementation.

The taxonomy must address at least:

- fees;
- funding;
- slippage and fills;
- liquidity and order-size realism;
- mark/index considerations;
- liquidation and maintenance margin;
- exchange constraints;
- bar-path assumptions.

Exact thresholds, formulas, storage paths, validators, query views, runner behavior, and implementation are deferred.

The taxonomy must not modify D-0001 hard risk caps, paper ledger accounting, runtime behavior, OMS, reconciliation, overlays, configs, or live-trading paths.

## 8. Bounded Search Governance Prerequisite

Future design must define bounded search governance before implementation.

The design must define how these items are pre-registered and preserved:

- search families;
- trial budgets;
- parameter bounds;
- lineage;
- exclusions;
- failed runs;
- invalid runs;
- errored or aborted runs;
- amendment posture.

Adaptive methods such as Bayesian optimization, Hyperband, evolutionary or genetic search, symbolic search, and LLM-generated strategy expansion remain unauthorized unless later explicitly designed and authorized.

Search efficiency must not be treated as validity. Faster search does not reduce multiple-testing burden, survivorship-bias risk, or the need for full-population retention.

## 9. Walk-Forward-First MVP Validation Prerequisite

Future MVP research execution design must use a walk-forward-first validation posture unless Main/Karl later explicitly replaces it.

Walk-forward-first is locked here as the default future design posture, not as an implemented split mechanic.

CPCV, purged CV, bootstrap, Monte Carlo, and permutation testing may remain later or conditional strengthening options.

Exact split mechanics, windows, data requirements, thresholds, result storage, validators, and implementation are deferred.

## 10. DSR / PSR / MinTRL Prerequisite Posture

Future design must account for DSR, PSR, and MinTRL-style interpretive support before implementation can proceed.

This support is prerequisite design, not formula implementation.

Future design must decide how these concepts relate to:

- complete result-population retention;
- multiple-testing denominator posture;
- trial budgets;
- walk-forward windows;
- return-path storage requirements;
- sample-size and trade-count sufficiency;
- advisory warnings and blockers;
- human-review packet support.

Exact formulas, denominator rules, thresholds, return-path storage requirements, validators, query views, and implementation are deferred.

DSR / PSR / MinTRL outputs, if later implemented, must remain interpretive support only. They do not create approval, recommendation, readiness, ranking, transition, paper/live, runtime, or gate-execution authority.

## 11. Strategy Spec / DSL Expressiveness-Readiness Prerequisite

Future design must define criteria for whether the Strategy Spec / DSL can represent the intended MVP strategy classes before artifact schemas or parser/compiler behavior are implemented.

At minimum, those criteria should consider whether the future Strategy Spec / DSL can represent:

- multi-signal entries;
- nested logic;
- exits;
- sizing;
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

This package does not add fields, schemas, examples, parser/compiler behavior, executable semantics, or Strategy Spec artifacts.

The WP-S2c-151 Strategy Spec / DSL lock remains unchanged: Strategy Spec is a future human-reviewable artifact/surface, Strategy DSL is constrained representation discipline, and logic remains non-executable and declarative.

## 12. Agent Orchestration Readiness Prerequisite

Future design must define agent orchestration readiness before any agent implementation.

The design must cover:

- orchestration model;
- permissioning;
- stop and escalation behavior;
- disagreement handling;
- audit trail;
- human-in-the-loop checkpoints;
- fail-closed behavior;
- boundary handling around protected paths, artifacts, schemas, validators, query views, dashboards, runners, and runtime surfaces.

Agent outputs remain support-only and non-authoritative.

No agent implementation, prompt, tool permission manifest, orchestration code, scheduler, graph, state machine, or artifact-writing authority is created here.

## 13. Dashboard / Operator-Review Constraint Prerequisite

Future design must define dashboard/operator-review constraints before any dashboard or operator-review surface.

The design must define how future views expose:

- blockers;
- uncertainty;
- validation posture;
- search lineage;
- result-population completeness;
- backtest-realism assumptions;
- DSR / PSR / MinTRL interpretation posture;
- non-authority language.

Dashboard/operator outputs, if later designed, must remain review support only. They must not become approval, recommendation, readiness, transition, ranking/scoring, paper/live, runtime, policy, or human-gate execution authority.

No dashboard, UI, operator workflow, query view, storage path, or implementation is created here.

## 14. Missing Lab Architecture Fit Research Input Gap

Lab Architecture Fit research was not available to WP-S2c-163 and remains an input gap.

This gap is not a reason to wait indefinitely.

The missing areas are converted into bounded design prerequisites:

- Strategy Spec / DSL expressiveness readiness;
- agent orchestration readiness;
- automated strategy-research pipeline architecture / SOTA risk posture.

This package does not invent external research findings. Future design may use later research if it becomes available, but repo-truth locks and active package scope remain authoritative.

## 15. Relationship To WP-S2c-163 Consolidation

WP-S2c-163 is the consolidation and decision-support basis for this lock.

It identified implementation-readiness gaps, research input gaps, and Main/Karl decision questions.

WP-S2c-164 resolves those questions only to this extent:

- implementation is deferred;
- prerequisites are required;
- additional Tier 1 design packages must precede implementation;
- missing Lab Architecture Fit research does not block indefinitely, but missing areas become bounded design prerequisites.

This package does not reopen, rewrite, or supersede WP-S2c-163.

## 16. Relationship To Existing Lab Locks

Existing locks remain in force:

- WP-S2c-151 Strategy Spec / DSL lock;
- WP-S2c-158 variant/storage lock;
- WP-S2c-159 anti-overfit / DSR design;
- WP-S2c-160 advisory ranking design;
- WP-S2c-161 Scope 6 / R2S integration design;
- WP-S2c-162 lab agent role boundaries;
- WP-S2c-100 approval/readiness criteria lock;
- WP-S2c-113 Scope 6 packaging lock;
- D2-006;
- D2-007;
- REC-5;
- Phase 9 / D2-011;
- canonical EXP / REP, trial-log, OL, REC, and DEC surfaces;
- permanent human gates.

This package adds an implementation-deferral and methodology-prerequisite lock. It does not modify prior locked criteria, thresholds, artifact grammar, schema behavior, validator behavior, query behavior, or evidence authority.

## 17. Forbidden Implementation And Authority Boundaries

This package creates no authority to create or modify:

- schemas;
- validators;
- query views;
- artifacts or artifact instances;
- runners;
- sweeps;
- code;
- tests;
- tools;
- dashboards;
- agents;
- prompts;
- storage paths;
- Strategy Spec artifacts;
- variant manifests;
- sweep plans;
- run manifests;
- result populations;
- advisory ranking artifacts;
- Scope 6 artifacts;
- approval records;
- candidate registry;
- trial-log;
- EXP / REP / OL / REC / DEC;
- `HYPOTHESIS.md`;
- notebooks;
- configs;
- data;
- runtime, paper, live, broker, exchange, order, OMS, reconciliation, risk, overlay, safe-mode, or kill-switch paths.

This package creates no implementation, strategy execution, backtest, optimizer execution, result aggregation, transition machinery, readiness authority, approval authority, recommendation authority, ranking/scoring authority, policy authority, runtime authority, paper/live authority, or human-gate execution.

Human gates remain human gates.

Advisory ranking remains human-review support only.

Agent outputs remain support-only.

Dashboard/operator outputs, if later designed, must remain review support only.

## 18. Required Next Design-Package Posture

After merge, Side may draft WP-S2c-165 only after refreshed-main preflight, no open PR or `docs/project_status.md` conflict, and no stop trigger.

Default next package:

```text
WP-S2c-165: Lab validity floor / backtest-realism / bounded-search prerequisite design
```

WP-S2c-165 must remain Tier 1 documentation-only unless Main/Karl directs otherwise.

It must not implement schemas, validators, query views, artifacts, code, tests, dashboards, agents, runners, runtime behavior, paper/live behavior, or protected-path changes.

Implementation remains blocked until the prerequisite design chain is complete and Main/Karl explicitly authorizes a scoped implementation package.

## 19. Rejected Alternatives

Rejected alternatives:

- immediate lab implementation from WP-S2c-164;
- implementation authorization based only on WP-S2c-163 consolidation;
- waiting indefinitely for missing Lab Architecture Fit research;
- treating search efficiency as validity;
- adaptive search without later explicit design and authorization;
- winner-only review;
- DSR / PSR / MinTRL as approval, recommendation, or readiness authority;
- Strategy Spec / DSL artifact implementation before expressiveness-readiness criteria;
- agent implementation before orchestration readiness;
- dashboard/operator surfaces before review constraints;
- advisory ranking as recommendation or approval;
- dashboards, agents, scores, or ranks executing human gates;
- runtime, paper/live, broker/exchange/order, OMS, risk, overlay, safe-mode, config, dependency, or protected-path contact from lab design surfaces.

## 20. Deferred Implementation Details

Deferred details include:

- exact lab validity floor criteria;
- exact backtest-realism thresholds and formulas;
- exact search-family taxonomy;
- exact trial-budget denominator rules;
- exact walk-forward split mechanics;
- exact CPCV, purged CV, bootstrap, Monte Carlo, or permutation usage;
- exact DSR / PSR / MinTRL formulas and thresholds;
- return-path storage requirements;
- Strategy Spec / DSL fields, examples, schema, parser, compiler, and storage;
- agent orchestration implementation, prompts, tools, and permissioning;
- dashboard/operator UX and data model;
- artifact paths, schemas, validators, query views, examples, IDs, and storage;
- runner integration;
- implementation package sequencing.

## 21. Validation Posture

This package uses CS12 T1-doc-major-decision validation.

Full pytest is required unless current repo truth explicitly says otherwise.

Required validation includes refreshed-main preflight, exact changed-file scope checks, forbidden-path diff checks, query-view listing, all discovered `v_integrity_*` views, registry/artifact/outcome/reconciliation validators, repo-conventional scoped pytest for research pipeline and integrity surfaces, full pytest, staged diff checks, and clean final status.

Validation checks prove scope and repo consistency only. They do not create implementation authority.

## 22. Next-Package Posture

After merge, Side may draft WP-S2c-165 as the first prerequisite design package after refreshed-main preflight and no stop trigger, unless Main/Karl directs otherwise.

Implementation remains unauthorized.

No implementation package may be drafted from this lock alone.

No Track 3, AUTO, A2C-003, paper bridge, monitoring/dashboard, runtime, paper/live, schema, validator, query-layer, artifact, runner, or protected-path package is authorized by WP-S2c-164.
