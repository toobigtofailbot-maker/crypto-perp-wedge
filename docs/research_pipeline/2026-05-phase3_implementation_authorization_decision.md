# Phase 3 Implementation Authorization Decision

## 1. Scope

WP-S2c-104 / WP-12ej is a Tier 1 documentation-only major-decision package.

It records the Phase 3 implementation authorization decision in repo truth.

It creates only this document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-major-decision. Full pytest is required.

This package does not implement any authorized scope.

This package does not authorize transition, candidate readiness determination, Tier 4 contact, paper/live, live trading, or protected-path changes.

## 2. Repo-truth basis

WP-12ei / WP-S2c-102+103 is merged.

WP-S2c-101 opened the Phase 3 implementation authorization decision tranche.

WP-S2c-102+103 created the authorization-scope sketches for shadow adapter, parity tooling, monitoring, dashboard, and paper bridge scope.

WP-S2c-100 locked approval/readiness criteria in repo truth.

WP-S2c-88 through WP-S2c-93 Phase 3 architecture sketches exist and remain the architecture-sketch basis.

WP-S2c-100 locked criteria, D2-006, D2-007, REC-5, Phase 9 Decision 9, Phase 9 Decision 6, permanent human gates, and Phase 1 paper runtime protection remain locked and unmodified.

Permanent human gates remain absolute.

Tier 4 boundaries remain absolute.

AUTO bridge remains frozen at WP-S2c-68.

A2C-001/002 are closed; A2C-003 and Path B remain unauthorized unless separately selected.

Monitoring/dashboard, paper bridge, packaging/schema/artifact locations, transition decisions, candidate readiness, Phase 4/live trading, and post-WP-S2c-104 implementation planning are not selected by this package except as explicitly resolved below.

## 3. Decision authority and resolution source

Main/Karl reviewed the two merged authorization-scope sketches and resolved the five real scope groups plus deferred packaging items.

Karl/user delegated routing judgment to Main for this decision.

Main resolved:

- Scope 1 shadow adapter implementation: AUTHORIZE bounded.
- Scope 2 parity tooling implementation: AUTHORIZE bounded.
- Scope 3 monitoring implementation: DEFER.
- Scope 4 dashboard implementation: DEFER.
- Scope 5 paper bridge implementation: KEEP UNAUTHORIZED.
- Scope 6 deferred packaging/schema/artifact questions: DEFER outside WP-S2c-104.

No other scope is authorized by this decision.

## 4. Authorization summary

| Scope | Resolution |
|---|---|
| Shadow adapter implementation | AUTHORIZE bounded |
| Parity tooling implementation | AUTHORIZE bounded |
| Monitoring implementation | DEFER |
| Dashboard implementation | DEFER |
| Paper bridge implementation | KEEP UNAUTHORIZED |
| Deferred packaging/schema/artifact questions | DEFER outside WP-S2c-104 |

## 5. Authorized scope 1 — shadow adapter implementation

Shadow adapter implementation scope is authorized as observational tooling around the locked SignalProvider Protocol. Authorized work may implement a non-executing shadow observation surface that observes SignalProvider-compatible candidate signals without generating orders, without invoking paper or live execution, and without contacting exchange/broker/order surfaces, paper/live runtime, OMS, reconciliation, risk, safe-mode, or kill-switch. Authorized work preserves D2-007 shadow discipline, WP-S2c-100 locked criteria including S2P-1 14-day window, S2P-2 parity thresholds, S2P-3 completion evidence requirements, S2P-7 paper runtime protection, HG-1 through HG-6, DR-1 through DR-9, the locked SignalProvider Protocol surface, and Phase 1 paper runtime protection. Authorized work does not authorize research-to-shadow transition, shadow-to-paper transition, candidate readiness determination, or any human gate execution. Implementation lands as Tier 3 code under tools/ or a new dedicated subdirectory. Implementation does not modify lib/, src/, configs/, .claude/, data/, or any protected path. Implementation may add tests under tests/. Implementation may not bundle with non-implementation packages and must use T3-implementation validation profile with full pytest.

Preservation note:

- G-3, G-5, HG-3, HG-5, S2P-7, and DR-7 remain preserved.
- D2-007 remains unchanged.
- SignalProvider Protocol remains unchanged.
- Phase 1 paper runtime protection remains intact.
- No automatic transition, Tier 4 contact, agentic gate execution, or paper runtime mutation is authorized.

## 6. Authorized scope 2 — parity tooling implementation

Parity tooling implementation scope is authorized as observational measurement of D2-007 shadow-window and parity evidence against locked D2-007 thresholds: PnL deviation no more than 10%, trade-count deviation no more than 5%, and at least 14 calendar days. Authorized work may implement tooling that computes parity observations, disclosure of interruptions, invalid observations, missing data, observation resets, and human-reviewable parity evidence. Mismatch diagnostics implemented under this scope are decision-support only; they may not become ranking, scoring, recommendation, policy authority, readiness authority, or automated paper-transition authority. Authorized work preserves D2-007 thresholds without modification, WP-S2c-100 locked criteria particularly S2P-1, S2P-2, S2P-3, S2P-4, S2P-5, DR-5, DR-6, and Phase 1 paper runtime protection. Authorized work does not authorize shadow-to-paper transition, candidate readiness determination, or paper/live contact. Implementation lands as Tier 3 code under tools/ or the shadow adapter's subdirectory, with the same protected-path restrictions as Scope 1. Implementation may not bundle with non-implementation packages and must use T3-implementation validation profile with full pytest.

Preservation note:

- S2P-4 and S2P-5 remain preserved: parity and mismatch diagnostics are decision-support only.
- DR-5 remains preserved: no dashboard/monitor/report authority.
- DR-6 remains preserved: no scoring/ranking/recommendation authority.
- HG-3 and HG-5 remain preserved: no automatic transition and no automation approving gates.
- D2-007 thresholds remain unchanged.
- No paper/live contact is authorized.

## 7. Deferred scope 3 — monitoring implementation

Monitoring implementation is DEFERRED.

The defer is soft, not a permanent rejection.

Reason: the sketch does not yet disambiguate repo-state monitoring from runtime monitoring, and runtime monitoring is more Tier-4-adjacent.

Monitoring's discipline floor is already bound by DR-5 and WP-S2c-100 locked criteria.

Monitoring can return when its substantive scope is clearer in a later Main/Karl-authorized package.

This package authorizes no monitoring implementation.

## 8. Deferred scope 4 — dashboard implementation

Dashboard implementation is DEFERRED.

The defer is soft, not a permanent rejection.

Reason: dashboard shape is naturally downstream of monitoring being defined and must follow LONG_TERM_SCOPE dashboard-from-repo-truth discipline.

DR-5 remains binding regardless of eventual dashboard form.

This package authorizes no dashboard implementation.

## 9. Unauthorized scope 5 — paper bridge implementation

Paper bridge implementation is KEEP UNAUTHORIZED.

Reason: authorizing any paper bridge implementation now risks crossing Phase 1 execution-core protection boundaries.

Paper bridge work is downstream of shadow adapter and parity tooling proving themselves under locked D2-007 thresholds, downstream of shadow-to-paper criteria being exercised against real evidence, and downstream of a separate paper-bridge architecture decision that names exactly what Phase 1 paper runtime touches and how.

This is stronger than DEFER; it explicitly keeps paper bridge outside the current authorization tranche.

This package authorizes no paper bridge implementation, bridge invocation, output file creation, paper/live contact, or Phase 1 paper runtime change.

## 10. Deferred scope 6 — packaging/schema/artifact questions

The following remain deferred outside WP-S2c-104:

- approval-record artifact location/schema for research-to-shadow;
- shadow-evidence retention location/artifact grammar;
- approval-record artifact location/schema for shadow-to-paper.

These are downstream packaging questions for later schema-tranche or implementation-adjacent packages.

Side does not author schemas under this authorization.

This decision creates no schema, artifact path, canonical artifact, output file, validator, query-layer, bridge code/output, runtime, config, dependency, or data change.

## 11. What this authorization decision changes

It creates repo-truth authorization for future Tier 3 implementation planning and implementation packages for bounded shadow adapter scope and bounded parity tooling scope.

It allows subsequent Main-authorized planning to size the first Phase 3 implementation tranche for shadow adapter and parity tooling.

It binds any future implementation packages to the exact preservation notes and forbidden boundaries recorded in this document.

It records monitoring/dashboard as deferred, paper bridge as unauthorized, and packaging/schema/artifact questions as deferred outside WP-S2c-104.

## 12. What this authorization decision does not authorize

This authorization decision does not authorize:

- implementation code in this WP;
- monitoring implementation;
- dashboard implementation;
- paper bridge implementation;
- paper bridge invocation;
- paper bridge output files;
- approval-record artifact locations/schemas;
- shadow-evidence retention location/artifact grammar;
- schemas;
- validators;
- query-layer changes;
- canonical artifacts;
- bridge code/output changes;
- runtime/protected-path work;
- research-to-shadow transition;
- shadow-to-paper transition;
- paper-to-live or live transition;
- candidate readiness determination;
- candidate approval or promotion;
- paper/live contact;
- live trading or real-capital trading;
- exchange/broker/order/live API/execution/Tier 4 contact;
- D2-006, D2-007, REC-5, Phase 9, WP-S2c-100 locked criteria, tiered-promotion, human-approval, or permanent-human-gate modification;
- human-gate automation, bypass, weakening, replacement, reinterpretation, or agentic execution;
- performance ranking/scoring/recommendation/policy authority;
- AUTO bridge further work;
- A2C-003 or Path B work except as deferred context;
- post-authorization implementation tranche planning or implementation sequencing;
- downstream authority beyond the two bounded authorized scopes recorded here.

## 13. Required next authority

After merge, Side must report back to Main/Karl/user for post-authorization direction.

No post-WP-S2c-104 implementation planning package may be auto-drafted until Main/Karl/user explicitly authorizes the next direction.

Expected next direction, informational only and not selected by this WP, is first Phase 3 implementation tranche planning for shadow adapter and parity tooling.

The next Main request should ask for compact Codex-ready WP capsules for the selected post-authorization path, as many as safely possible.

## 14. Validation profile

This package uses CS12 T1-doc-major-decision because it records the Phase 3 implementation authorization decision and creates a major boundary decision.

Full pytest is required.

## 15. Validation

Pre-edit verification confirmed:

- PR #284 / WP-12ei is merged at `7b722665ef9673d88438c8e7a2c317e79861b739`.
- Refreshed `main` includes the WP-12ei merge.
- `docs/project_status.md` records WP-12ei / WP-S2c-102+103 as the latest branch-state before this package.
- No open PR was reported.
- No remote or local `codex/wp-12ej-phase3-implementation-authorization-decision` branch was found before this package branch.
- No WP-12ej / WP-S2c-104 PR was found before drafting.
- Searches for WP-12ej, WP-S2c-104, and Phase 3 implementation authorization decision found no started or merged authorization-decision package.
- This authorization decision document did not exist before this package.
- WP-S2c-100 through WP-S2c-103 authorization/criteria source documents exist.
- WP-S2c-88 through WP-S2c-93 Phase 3 architecture sketch/checkpoint source documents exist.
- Main/Karl's per-scope resolution is available in handoff context: shadow adapter AUTHORIZE bounded; parity tooling AUTHORIZE bounded; monitoring DEFER; dashboard DEFER; paper bridge KEEP UNAUTHORIZED; packaging/schema/artifact questions DEFER outside WP-S2c-104.
- No schema, validator, central query-layer, committed-state test, config, dependency, data, runtime, protected-path, bridge-code, bridge-output, canonical artifact, D2-006, D2-007, REC-5, Phase 9, tiered-promotion, human-approval, permanent-human-gate, event-log schema, or SignalProvider modification is required.

Package validation results are recorded in the execution report-back and PR.
