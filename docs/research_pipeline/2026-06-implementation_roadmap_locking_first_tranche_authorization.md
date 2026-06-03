# Implementation Roadmap Locking / First-Tranche Authorization

## 1. Scope

WP-S2c-170 / WP-12gq is a Tier 1 documentation-only major-decision package.

It locks the Strategy Research Lab implementation roadmap after WP-S2c-169 and authorizes the backtest-realism tranche in structure only.

It creates only this decision document and updates `docs/project_status.md`.

It creates no implementation, code, tests, schemas, validators, query views, tools, runners, sweeps, artifacts, dashboard, agent, prompt, `.claude/` change, runtime behavior, paper/live behavior, protected-path change, approval authority, readiness authority, recommendation authority, ranking/scoring authority, transition authority, or human-gate execution.

## 2. Repo-Truth And Main Resolution Basis

Repo truth for this decision is refreshed `main` after WP-S2c-169 / WP-12gp, merged by PR #346 at merge commit `bdee37b1e318470d2899c3673cfc05c7cc005557`.

Primary basis:

- WP-S2c-164 locked lab implementation deferral and required prerequisite design before any implementation tranche.
- WP-S2c-165 defined the lab validity floor, crypto-perp backtest-realism taxonomy, bounded-search governance, walk-forward-first MVP validation posture, and DSR / PSR / MinTRL prerequisite posture.
- WP-S2c-166 defined Strategy Spec / DSL expressiveness-readiness.
- WP-S2c-167 defined provenance / audit / lineage prerequisite discipline.
- WP-S2c-168 defined agent orchestration readiness.
- WP-S2c-169 consolidated the prerequisite chain and surfaced roadmap lock candidates and first-tranche authorization questions.

Main reviewed the WP-S2c-169 roadmap content and resolved: draft WP-S2c-170; lock the roadmap; authorize backtest realism as the first tranche; treat `lib/backtest.py` and `lib/evaluation.py` as possible tranche scope only under protected-path discipline; make WP-S2c-171 a read-only audit and per-edit scope design package; and keep WP-S2c-172+ gated until Main reviews the exact protected-path edit scope.

Current merged repo truth wins over external research, memory, summaries, handoffs, or generic best practice.

## 3. Decision Objective

This decision records the implementation-roadmap lock and opens the first tranche only as a controlled structure.

It resolves the WP-S2c-169 lock candidates, closes automatic prerequisite design, sets backtest realism as the first implementation tranche, and preserves a two-stage protected-path discipline before any code edit.

## 4. Non-Authority Boundary

Roadmap lock is not implementation.

Backtest-realism tranche authorization is not direct edit authorization.

This document does not authorize direct edits to `lib/backtest.py`, `lib/evaluation.py`, or any other implementation file.

This document does not authorize WP-S2c-172+ drafting, protected-path modification, code changes, test changes, schema changes, validator changes, query-view changes, runner work, sweep execution, dashboard/operator work, agent work, runtime contact, paper/live contact, recommendation, approval, readiness, transition, ranking/scoring authority, or human-gate execution.

Human gates remain human gates.

Advisory ranking and agent outputs remain human-review support only.

## 5. Roadmap Locks

Main locks the WP-S2c-169 Section H roadmap candidates as decisions:

1. The WP-S2c-164 through WP-S2c-169 prerequisite chain is complete for implementation-roadmap decision.
2. Further prerequisite design is not warranted by default and requires Main re-engagement.
3. Backtest realism is the first implementation tranche.
4. Broader lab implementation follows only after backtest realism or after Main resolves alternate sequencing.
5. First implementation authorization is scoped and does not authorize unrelated lab components.
6. Protected-path changes are allowed only where explicitly scoped.
7. Human gates and protected boundaries remain unchanged.
8. Advisory ranking and agent outputs remain human-review support only.

These locks do not implement any tranche.

## 6. Prerequisite Chain Completion Lock

The WP-S2c-164 through WP-S2c-169 prerequisite chain is complete enough for implementation-roadmap decision-making.

Completion here means the chain has addressed implementation deferral, lab validity floor, backtest realism, bounded search, walk-forward-first posture, DSR / PSR / MinTRL prerequisite posture, Strategy Spec / DSL expressiveness-readiness, provenance / audit / lineage, agent orchestration readiness, and roadmap consolidation.

It does not mean implementation is generally authorized.

## 7. Further Prerequisite Design Closeout

Further prerequisite design is not automatic.

Any additional prerequisite design requires Main re-engagement and a concrete unresolved blocker.

Dashboard/operator uncertainty display, robustness/search/DSL follow-ups, and additional lab-support design do not continue by default from this package.

## 8. Backtest-Realism First-Tranche Lock

Backtest realism is locked as the first implementation tranche.

The tranche is authorized in structure only because credible future lab output depends on realistic research backtest assumptions before broader lab implementation inherits those assumptions.

The first tranche must begin with read-only audit and exact modification-scope design, not code changes.

## 9. Two-Stage Protected-Path Discipline

The protected-path discipline is locked:

- roadmap authorization does not equal edit authorization;
- `lib/backtest.py` and `lib/evaluation.py` may be in tranche scope, but actual edits are not authorized by WP-S2c-170;
- WP-S2c-171 must inspect relevant files read-only and produce exact per-edit scope;
- Main must review the protected-path edit scope surfaced at WP-S2c-171 report-back;
- WP-S2c-172+ may draft only after that review clears exact scope;
- protected-path edits must land in small reviewable increments;
- each implementation package requires T3-implementation validation, full pytest, and determinism/regression evidence.

## 10. WP-S2c-171 Authorization

After WP-S2c-170 merges, Side may draft WP-S2c-171 after refreshed-main preflight and no stop trigger.

WP-S2c-171 is authorized as Tier 1 documentation-only.

WP-S2c-171 must be read-only against `lib/backtest.py`, `lib/evaluation.py`, and any implementation-adjacent source it inspects.

WP-S2c-171 may create one new `docs/research_pipeline/` design document and update `docs/project_status.md`.

WP-S2c-171 must produce a realism audit and per-edit modification-scope design. It must not edit `lib/`, `src/`, `configs/`, protected paths, code, tests, schemas, validators, query views, artifacts, runners, dashboards, agents, runtime, paper/live paths, or data.

## 11. WP-S2c-172+ Gated Posture

WP-S2c-172+ are not draftable automatically after WP-S2c-170.

WP-S2c-172+ are not draftable automatically after WP-S2c-171.

They require:

- WP-S2c-171 merge;
- Side report-back to Main;
- Main review of the exact protected-path edit scope;
- Main authorization of the next specific edit package or capsule set.

## 12. Backtest-Realism Tranche Scope Envelope

The backtest-realism tranche may investigate, and only after later review possibly implement, improvements around:

- fees;
- funding timing / funding treatment;
- slippage / fills;
- liquidity and order-size realism;
- liquidation / maintenance margin;
- exchange constraints;
- mark/index assumptions;
- bar-path assumptions;
- deterministic preservation;
- regression / before-after evidence.

This envelope is decision-level only. It defines no exact edits, formulas, thresholds, tests, schemas, storage paths, or implementation mechanics.

## 13. Protected-Path Preservation Requirements

Any future backtest-realism implementation package must preserve:

- Phase 1 paper runtime protection;
- deterministic execution;
- D-0001;
- D2-008;
- OMS boundaries;
- reconciliation boundaries;
- kill-switch boundaries;
- Tier 4 boundaries;
- runtime / paper-live separation;
- no broker/exchange/order behavior change by implication;
- no OMS/reconciliation/risk/safe-mode/kill-switch behavior change by implication;
- no config, dependency, data, AUTO bridge, A2C-003, Track 3 / WP-S2c-140, or protected-path behavior change by implication;
- permanent human gates;
- locked decisions.

Any protected-path contact requires explicit package scope and stop-condition handling before editing.

## 14. Validation Posture

Backtest-realism implementation packages must use T3-implementation validation, full pytest, and determinism/regression evidence.

They must include exact changed-file scope checks, forbidden-path checks, targeted tests for modified behavior, before/after evidence where behavior changes, full pytest, and explicit boundary review.

This roadmap package creates no implementation validation burden beyond its Tier 1 documentation-only major-decision validation.

## 15. Tranches 3-7 Queued Posture

Tranches 3 through 7 remain queued in roadmap order and require future authorization:

3. Strategy Spec / artifact grammar tranche.
4. Variant manifest / sweep plan artifact grammar tranche.
5. Offline research runner / result population tranche.
6. Robustness / DSR / PSR / MinTRL support tranche.
7. Advisory ranking / Scope 6 packet-support tranche.

No tranche 3-7 work is authorized by this package.

## 16. Tranches 8-9 Deferral

Tranches 8 and 9 are deferred until lab core exists:

8. Agent assistance surfaces.
9. Dashboard/operator review surfaces.

No agent or dashboard/operator implementation or design continuation is authorized by this package.

## 17. Tranche 10 Separate-Gate Posture

Tranche 10, later paper/runtime bridge work, stays behind separate gates.

It is not a lab-roadmap default and is not authorized by this decision.

Any paper/runtime bridge, shadow/paper/live, exchange/broker/order, OMS, reconciliation, risk, safe-mode, kill-switch, config, data, dependency, or Tier 4 work requires separate explicit Main/Karl authorization and package scope.

## 18. Rejected / Deferred Alternatives

Rejected or deferred alternatives:

- continuing prerequisite design by default;
- treating roadmap authorization as code edit authorization;
- treating backtest-realism tranche structure as direct permission to modify `lib/backtest.py` or `lib/evaluation.py`;
- drafting WP-S2c-172+ before WP-S2c-171 report-back and Main protected-path scope review;
- bundling unrelated lab components into the first tranche;
- implementing schemas, validators, query views, artifacts, runners, sweeps, dashboards, agents, prompts, or `.claude/` changes here;
- weakening human gates, protected paths, pre-registration, full-population retention, D2-006, D2-007, REC-5, Scope 6, Phase 9 / D2-011, WP-S2c-100, WP-S2c-113, WP-S2c-151, WP-S2c-158, WP-S2c-159, WP-S2c-160, WP-S2c-161, WP-S2c-164, or permanent human gates.

Nothing is rejected as a possible future authorized tranche solely by this decision.

## 19. Human Gates And Locked-Decision Preservation

This decision preserves:

- permanent human gates;
- canonical EXP / REP, trial-log, OL, REC, and DEC surfaces;
- D2-006;
- D2-007;
- REC-5 exact-segment discipline;
- Phase 9 / D2-011;
- Scope 6;
- WP-S2c-100 locked criteria;
- WP-S2c-113 Scope 6 packaging lock;
- WP-S2c-151 Strategy Spec / DSL lock;
- WP-S2c-158 variant/storage lock;
- WP-S2c-159 anti-overfit / DSR population design;
- WP-S2c-160 advisory ranking design;
- WP-S2c-161 Scope 6 / R2S integration design;
- WP-S2c-162 lab agent role boundaries;
- WP-S2c-164 implementation-deferral prerequisite lock;
- WP-S2c-165 through WP-S2c-169 prerequisite-chain decisions and designs;
- Phase 1 paper runtime protection;
- D-0001 hard risk caps;
- D2-008 overlay semantics and output set;
- OMS, reconciliation, kill-switch, safe-mode, and Tier 4 boundaries;
- Track 3 paused state and WP-S2c-140 onward deferred state.

## 20. Main Re-Engagement Requirements

Main re-engagement is required before:

- any additional prerequisite design not already authorized;
- WP-S2c-172+ drafting;
- any exact protected-path edit;
- any broader lab implementation tranche;
- any tranche sequencing change;
- any schema, validator, query-view, runner, artifact, dashboard, agent, prompt, runtime, paper/live, or protected-path package not separately authorized;
- any change that would affect human gates or locked decisions.

## 21. Future Package Dependencies

Future package dependencies:

- WP-S2c-171 depends on WP-S2c-170 merge, refreshed-main preflight, no conflicting PR, and no stop trigger.
- WP-S2c-172+ depend on WP-S2c-171 merge, Side report-back, Main review of exact protected-path edit scope, and explicit Main authorization of the next edit package or capsule set.
- Tranches 3-7 depend on later explicit authorization.
- Tranches 8-9 depend on lab core existing and later explicit authorization.
- Tranche 10 depends on separate gates and is not automatically downstream of lab roadmap work.

## 22. Validation Posture For This Package

This package uses T1-doc-major-decision validation with full pytest required.

Validation must prove:

- exact changed-file scope;
- forbidden paths untouched;
- query views list successfully;
- all discovered `v_integrity_*` views return clean results;
- registry / experiment artifact / outcome ledger / reconciliation validators pass;
- repo-conventional scoped pytest passes;
- full pytest passes;
- staged diff checks pass;
- final status is clean before PR.

Validation proves scope and repo consistency only. It creates no implementation authority.

## 23. Next-Package Posture

After WP-S2c-170 merges, Side may draft WP-S2c-171 after refreshed-main preflight and no stop trigger.

WP-S2c-171 is read-only audit and per-edit modification-scope design only.

WP-S2c-172+ remain gated until WP-S2c-171 scope is surfaced and Main reviews it.

Implementation edits remain unauthorized until protected-path scope review clears a specific package.
