# Prerequisite Chain Consolidation / Implementation Roadmap

## 1. Scope

WP-S2c-169 / WP-12gp is a Tier 1 documentation-only consolidation and roadmap package.

It closes the current Strategy Research Lab prerequisite design chain for Main review and prepares decision support for a later implementation-roadmap decision.

It creates only this document and updates `docs/project_status.md`.

It creates no implementation authorization, no WP-S2c-170 authorization, no schema, validator, query view, artifact, code, test, tool, runner, sweep, dashboard, prompt, agent, storage path, runtime behavior, paper/live behavior, protected-path change, recommendation, approval, readiness, transition, ranking/scoring authority, or human-gate execution.

## 2. Repo-Truth And Decision Basis

Repo truth for this consolidation is refreshed `main` after WP-S2c-168 / WP-12go.

Primary prerequisite-chain sources are:

- WP-S2c-164 implementation-deferral / methodology-prerequisite lock.
- WP-S2c-165 lab validity floor / backtest-realism / bounded-search prerequisite design.
- WP-S2c-166 Strategy Spec / DSL expressiveness-readiness design.
- WP-S2c-167 provenance / audit / lineage prerequisite design.
- WP-S2c-168 agent orchestration readiness prerequisite design.

Supporting lab-chain sources include WP-S2c-147, WP-S2c-151, WP-S2c-152 through WP-S2c-163, WP-S2c-158 through WP-S2c-162, Scope 6 / R2S packaging locks, D2-006 methodology, EXP / REP, trial-log, OL, REC, DEC, and current protected-boundary guidance.

Current merged repo truth wins over external research, memory, summaries, handoffs, or generic best practice.

## 3. Consolidation Objective

The objective is to consolidate the completed prerequisite chain, prevent default continuation into more prerequisite design, and prepare Main to decide the implementation roadmap and possible first tranche.

The document provides decision support only. It does not lock the roadmap and does not select an implementation option as final.

## 4. Non-Authority Boundary

This roadmap is not authority.

It does not authorize implementation, WP-S2c-170 drafting, backtest-realism implementation, protected-path modification, schemas, validators, query views, artifacts, parser/compiler behavior, code, tests, tools, runners, sweeps, dashboards, agents, prompts, storage paths, runtime behavior, paper/live behavior, recommendation, approval, readiness, transition, ranking/scoring authority, or human-gate execution.

Human gates remain human gates.

Advisory ranking remains human-review support only.

Scope 6 / R2S remains human-gated.

Implementation remains unauthorized until a later explicit gated decision package and a scoped implementation package authorize exact surfaces.

## 5. Prerequisite-Chain Summary

The prerequisite chain now covers:

- implementation deferral and prerequisite locks;
- lab validity floor;
- crypto-perp backtest-realism taxonomy;
- bounded search governance;
- walk-forward-first MVP validation posture;
- DSR / PSR / MinTRL prerequisite posture;
- Strategy Spec / DSL expressiveness-readiness;
- provenance / audit / lineage;
- agent orchestration readiness.

This coverage is complete enough for Main review of the implementation roadmap. It does not mean implementation is ready or authorized.

## 6. WP-S2c-164 Implementation-Deferral Lock

WP-S2c-164 locked that Strategy Research Lab implementation is deferred and unauthorized.

It required prerequisite design before any implementation tranche can be reconsidered. It identified the need to design lab validity floor, crypto-perp backtest realism, bounded search governance, walk-forward-first MVP validation posture, DSR / PSR / MinTRL interpretive support, Strategy Spec / DSL expressiveness-readiness, agent orchestration readiness, and dashboard/operator-review constraints.

It preserved existing lab locks, canonical evidence surfaces, permanent human gates, and protected runtime boundaries.

## 7. WP-S2c-165 Validity / Realism / Search / DSR Prerequisite Summary

WP-S2c-165 defined the lab validity floor as review-support sufficiency, not approval or gate authority.

It positioned crypto-perp backtest realism as foundational, including fees, funding, slippage and fills, liquidity and order-size realism, mark/index mechanics, liquidation and maintenance margin, exchange constraints, and bar-path assumptions.

It preferred constrained manual grids and constrained random search as MVP-compatible design postures unless Main later authorizes another method. It established walk-forward-first as default future MVP validation posture unless Main/Karl replaces it.

It kept DSR / PSR / MinTRL as interpretive support requiring full-population context, with exact formulas, thresholds, denominators, storage, validators, and implementation deferred.

## 8. WP-S2c-166 Strategy Spec / DSL Expressiveness Prerequisite Summary

WP-S2c-166 defined Strategy Spec / DSL expressiveness-readiness as the ability to represent intended MVP strategy concepts clearly enough for human review, bounded variant generation, search governance, result lineage, validity-floor review, and later implementation design.

The representation remains typed, declarative, non-executable, side-effect-free, host-data-bounded, auditable, and separated from runtime code.

MVP-critical pattern families include multi-signal entries, exits, sizing and risk parameters, regime filters, multi-timeframe references, trend-following, mean reversion, breakouts, funding/carry, basis/spread, risk overlays, cooldowns, no-trade filters, and time/session filters.

Dangerous expressiveness such as arbitrary executable code, callbacks, recursion, loops, external calls, runtime side effects, broker/exchange/order directives, and hidden strategy mutation remains rejected.

## 9. WP-S2c-167 Provenance / Audit / Lineage Prerequisite Summary

WP-S2c-167 defined provenance, audit, and lineage discipline for the future lab chain from source idea or concept through Strategy Spec, variant population, sweep/run planning, result population, anti-overfit review, advisory ranking, Scope 6 / R2S handoff, and later human decision records where authorized.

It requires failed, invalid, excluded, errored, aborted, filtered, data-unavailable, incomplete, retried, amended, and superseded branches to remain visible where current lab designs require preservation.

It framed parent references, hash-pinning, trial-log linkage, EXP / REP / OL / REC / DEC linkage, agent operation provenance, partial-completion provenance, amendment posture, and auditability as evidence-trail concepts only.

## 10. WP-S2c-168 Agent Orchestration Readiness Prerequisite Summary

WP-S2c-168 defined readiness criteria for coordinating future bounded support roles without turning agents or orchestration into approvers, artifact authorities, runner operators, dashboard operators, or runtime actors.

It covered handoff protocols, shared-state discipline, provenance integration, human-in-the-loop checkpoints, partial-completion and failure recovery, conflict and uncertainty handling, fail-closed behavior, and permissioning / read-write boundaries.

It kept agents support-only and rejected agent approval, agent promotion, gate execution, hidden shared state, agent consensus as approval, runner triggering, runtime contact, paper/live contact, `.claude/` changes, prompts, and implementation authority.

## 11. Prerequisite Completeness Assessment

The prerequisite chain is complete enough for Main review because it now covers the core methodology and operating-boundary questions that WP-S2c-164 required before implementation-roadmap reconsideration.

The chain covers implementation deferral, lab validity floor, crypto-perp backtest-realism taxonomy, bounded search governance, walk-forward-first MVP validation, DSR / PSR / MinTRL prerequisite posture, Strategy Spec / DSL expressiveness-readiness, provenance / audit / lineage, and agent orchestration readiness.

This does not mean implementation is ready or authorized. It means the prerequisite-design material is ready for Main to decide whether and how to lock the implementation roadmap and first implementation tranche.

## 12. Remaining Unresolved Decisions

Main must still resolve:

- whether to lock backtest realism as the first implementation tranche;
- exact first-tranche scope;
- whether `lib/backtest.py` and/or `lib/evaluation.py` are in scope;
- protected-path preservation requirements;
- exact validation requirements for first implementation;
- whether any implementation package must first add tests, diagnostics, or documentation-only acceptance criteria;
- whether a standalone research-findings brief is still needed for referenceability;
- whether dashboard/operator uncertainty display remains deferred;
- whether any candidate implementation tranches should be rejected or deferred.

## 13. Anti-Bloat Closeout Posture

The prerequisite chain should close at WP-S2c-169.

No further prerequisite design is authorized by default.

Any additional prerequisite gap discovered after WP-S2c-169 should be reported to Main, not auto-expanded into another prerequisite WP.

Dashboard/operator uncertainty display remains deferred unless Main explicitly redirects.

Robustness/search/DSL follow-ups should not be added unless a specific unresolved implementation blocker is found.

## 14. Implementation-Roadmap Principles

Roadmap principles:

- repo truth wins;
- implementation must be package-scoped;
- protected-path changes require explicit authorization;
- backtest realism should precede broader lab implementation if Main accepts the roadmap;
- lab implementation must not begin before the roadmap is locked;
- implementation should proceed in narrow tranches;
- no artifact/schema/validator/query/code/agent/dashboard/runtime work may be smuggled into decision docs;
- validation must match tier and risk;
- human gates remain absolute.

## 15. Backtest-Realism-First Sequencing

Backtest-realism-first sequencing is decision support for Main, not implementation authorization.

It is positioned first because WP-S2c-165 identified realism as foundational to lab validity, future advisory ranking and result review depend on credible backtest assumptions, and broader lab orchestration should inherit realism discipline rather than retrofit it later.

Likely affected surfaces may include `lib/backtest.py` and `lib/evaluation.py`. Those are implementation / protected-path-adjacent research-engine files and require explicit authorization before any modification.

This package does not authorize changes to those files.

## 16. Candidate Implementation Tranche Map

Candidate roadmap options:

1. Roadmap locking / first-tranche authorization decision package.
2. Backtest-realism implementation tranche.
3. Strategy Spec / artifact grammar tranche.
4. Variant manifest / sweep plan artifact grammar tranche.
5. Offline research runner / result population tranche.
6. Robustness / DSR / PSR / MinTRL support tranche.
7. Advisory ranking / Scope 6 packet-support tranche.
8. Agent assistance surfaces tranche.
9. Dashboard/operator review surfaces tranche.
10. Later paper/runtime bridge only after separate gates.

These are candidates only. The only sequencing recommendation surfaced here is that backtest realism should be proposed as the first implementation tranche for Main decision.

## 17. Candidate Tranche Dependencies

Roadmap locking must precede implementation.

Backtest-realism implementation depends on Main choosing exact files, exact permitted semantics, exact tests, and protected-path preservation notes.

Strategy Spec / artifact grammar depends on WP-S2c-151 and WP-S2c-166 and must preserve non-executable declarative posture.

Variant manifest / sweep plan grammar depends on WP-S2c-158, WP-S2c-165, and WP-S2c-167 and must preserve pre-registration and complete population lineage.

Offline runner / result population work depends on locked artifact/storage surfaces and must remain offline research only.

Robustness and DSR / PSR / MinTRL support depends on complete result-population preservation and explicit formula/threshold authorization.

Advisory ranking / Scope 6 packet support depends on canonical evidence references, warning/blocker posture, and human-review boundaries.

Agent and dashboard surfaces depend on explicit future support-surface authorization and must remain non-authoritative.

Paper/runtime bridge work requires separate gates and is not a lab-roadmap default.

## 18. Candidate Tranche Validation Expectations

Validation should scale with the tranche risk.

Roadmap and decision packages require exact changed-file scope, forbidden-path checks, integrity views, registry/artifact/outcome/reconciliation validators, and repo-conventional scoped pytest.

Backtest-realism implementation likely requires targeted unit tests around `lib/backtest.py` and `lib/evaluation.py`, regression tests for current research-pipeline behavior, integrity views, validators, and full pytest unless Main explicitly chooses a different validation profile.

Artifact grammar, validators, and query surfaces require schema self-checks, validator tests, query integrity checks, changed-file scope checks, and full pytest where repo convention requires it.

Runner, result-population, agent, dashboard, or paper/runtime bridge tranches require stronger package-specific validation and explicit protected-boundary review.

## 19. Candidate Protected-Path Considerations

For a likely backtest-realism implementation tranche, possible read/modify surfaces may include `lib/backtest.py` and `lib/evaluation.py` only if later explicitly authorized.

No runtime, paper/live, broker/exchange/order, OMS, reconciliation, risk, overlay, safe-mode, kill-switch, config, dependency, data, or protected-path behavior may be altered by implication.

Phase 1 paper runtime protection, deterministic execution, D-0001, D2-008, OMS, reconciliation, kill-switch, and protected runtime boundaries must be preserved.

Any protected-path contact requires explicit package scope and stop-condition handling before editing.

## 20. Roadmap Lock-Candidate Wording

Candidate wording for Main review only:

- Lock the WP-S2c-164 through WP-S2c-169 prerequisite chain as complete for implementation-roadmap decision.
- Lock that further prerequisite design is not warranted by default and requires Main re-engagement.
- Lock backtest realism as the proposed first implementation tranche.
- Lock that broader lab implementation follows only after backtest realism or after Main resolves an alternate sequencing.
- Lock that first implementation authorization is scoped and does not authorize unrelated lab components.
- Lock that protected-path changes are allowed only where explicitly scoped.
- Lock that human gates and protected boundaries remain unchanged.
- Lock that advisory ranking and agent outputs remain human-review support only.

This wording is candidate wording only. WP-S2c-169 does not lock it.

## 21. First-Tranche Authorization Decision Support

Main must resolve these points before WP-S2c-170 can be drafted:

1. Should WP-S2c-170 lock the roadmap?
2. Should WP-S2c-170 authorize a first implementation tranche?
3. Should the first tranche be backtest realism?
4. What files/surfaces are allowed for the first tranche?
5. What files/surfaces are explicitly forbidden?
6. What validation profile is required?
7. What preservation notes must be included?
8. Should the first implementation tranche be split into smaller WPs?
9. Should a standalone research-findings brief be created before implementation?
10. Should any roadmap candidate be deferred or rejected?

## 22. Research-Findings Referenceability Posture

Research findings are referenceable enough for Main decision support through WP-S2c-165, WP-S2c-166, WP-S2c-167, and WP-S2c-168.

WP-S2c-165 preserves external Lab Validity Core findings as input, not repo truth. WP-S2c-166 preserves external architecture-fit rationale around non-executable DSL boundaries. WP-S2c-167 and WP-S2c-168 convert lineage and orchestration concerns into repo-local prerequisite design.

A standalone research-findings brief is optional only if Main decides referenceability is insufficient. This package does not create one.

## 23. Deferred Dashboard/Operator Uncertainty-Display Posture

Dashboard/operator uncertainty display remains deferred.

Future dashboards may be useful for blockers, warnings, lineage, validity-floor posture, and uncertainty only after a concrete consumer exists and Main authorizes that surface.

No dashboard/operator design is warranted by default before the implementation-roadmap decision.

## 24. Rejected / Deferred Alternatives

Rejected or deferred alternatives:

- continuing prerequisite design indefinitely;
- adding dashboard/operator design before there is a concrete consumer;
- adding robustness/search/DSL follow-up WPs without a real unresolved implementation blocker;
- treating this document as implementation authorization;
- treating backtest-realism-first sequencing as already authorized implementation;
- modifying `lib/backtest.py`, `lib/evaluation.py`, or any implementation/protected path here;
- creating schemas, validators, query views, artifacts, code, tests, tools, runners, sweeps, dashboards, agents, prompts, or `.claude/` changes here;
- weakening human gates;
- allowing advisory ranking to become approval/recommendation/promotion/readiness;
- allowing agents to become approvers or gate executors;
- allowing runtime/paper/live/protected-path contact from this roadmap.

## 25. Main Report-Back Requirements

After WP-S2c-169 merges, Side must report back to Main with a copy-paste-ready message that includes:

- repo-truth state;
- prerequisite chain completion;
- consolidated roadmap options;
- lock-candidate wording;
- first-tranche authorization questions;
- forbidden boundaries;
- explicit ask for Main direction.

Main must review the consolidated roadmap and resolve the next direction before WP-S2c-170 is drafted.

## 26. WP-S2c-170 Gated Posture

WP-S2c-170 remains gated.

It must not be drafted automatically after WP-S2c-169.

WP-S2c-170 may be drafted only after Main resolves whether to lock the roadmap, whether to authorize a first implementation tranche, what that tranche includes, and what validation/preservation rules govern it.

## 27. Future Package Dependencies

Future packages depend on Main direction after this closeout.

If Main locks a backtest-realism-first roadmap, the next package may be a gated decision package that authorizes or scopes the first implementation tranche.

If Main chooses more decision work, that work must be bounded to the unresolved decision, not default continuation of prerequisite design.

If Main rejects or defers implementation, no implementation package should be drafted.

## 28. Validation Posture

This package uses CS12 T1-doc-narrow validation unless current repo truth requires broader validation.

Validation proves changed-file scope, forbidden-path cleanliness, query/integrity health, registry/artifact/outcome/reconciliation validator health, and scoped research-pipeline test health.

Validation does not create implementation authority.

## 29. Next-Package Posture

After merge, Side must report back to Main before WP-S2c-170 is drafted.

Further prerequisite design is not warranted by default and requires Main re-engagement.

Implementation remains unauthorized.

WP-S2c-170 remains gated and not automatic.

No schema, validator, query view, artifact, parser/compiler, code, test, tool, runner, sweep, dashboard, prompt, agent, `.claude/` change, storage path, runtime/paper/live behavior, protected-path change, transition, approval, readiness, recommendation, ranking/scoring authority, or human-gate execution package is authorized by WP-S2c-169.
