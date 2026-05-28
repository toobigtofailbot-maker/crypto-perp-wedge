# Phase 3 Implementation Authorization Design Opening

## 1. Scope

WP-S2c-101 / WP-12eh is a Tier 1 documentation-only opening package.

It opens the Phase 3 implementation authorization decision surface.

It creates only this document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-narrow.

This package does not authorize Phase 3 implementation.

## 2. Repo-truth basis

WP-12eg / WP-S2c-100 is merged.

WP-S2c-100 locked approval/readiness criteria in repo truth. The locked criteria cover global criteria, research-to-shadow criteria, shadow-to-paper criteria, human-gate preservation criteria, drift-rejection criteria, and the refined criteria from WP-S2c-99-refine.

Deferred packaging points remain outside WP-S2c-100:

- approval-record artifact location/schema for research-to-shadow;
- shadow-evidence retention location/artifact grammar;
- approval-record artifact location/schema for shadow-to-paper.

WP-S2c-88 through WP-S2c-93 Phase 3 architecture sketches exist and remain documentation-only sketches. The Phase 3 architecture sketch checkpoint closed that sketch tranche without authorizing implementation.

Main selected the Phase 3 implementation authorization decision tranche after WP-S2c-100.

Phase 3 implementation, transition authorization, runtime/protected-path work, Tier 4 contact, AUTO bridge further work, A2C-003, Path B, and downstream authority remain unauthorized.

## 3. Why this tranche is next

The Phase 3 architecture sketch tranche mapped the implementation surfaces: opening, shadow deployment, monitoring/dashboard, paper bridge, live boundary, and checkpoint.

WP-S2c-100 then locked the approval/readiness criteria that govern whether those surfaces may later be authorized.

Implementation planning should not begin before authorization scope is surfaced and Karl resolves the authorization decision. This package opens the design and decision surface only.

## 4. Locked criteria basis

The locked global criteria preserve no-authority and no-automatic-transition boundaries. Locked criteria may inform human review, but they cannot replace, bypass, automate, weaken, or reinterpret human approval. Criteria locking does not determine candidate readiness and does not authorize implementation, runtime, paper/live, exchange/broker/order, or Tier 4 contact.

The locked research-to-shadow criteria require D2-006 pass evidence as prerequisite evidence, preserve REC-5 exact-segment discipline, require the REC-5 floor before segment-level inference, preserve broad-floor-crossing evidence as descriptive input only, require human approval before transition, and keep candidate-level readiness bounded by exact-segment evidence, D2-006 evidence, and human approval.

The locked shadow-to-paper criteria preserve the D2-007 minimum shadow window, D2-007 parity thresholds, shadow-window evidence discipline, mismatch diagnostics as decision support only, human approval before transition, and Phase 1 paper runtime protection.

The locked human-gate preservation criteria keep permanent human gates human-controlled for hypothesis approval, decision records/go-no-go decisions, shadow promotion, live promotion, risk parameter changes, kill decisions, and novel strategy-family introduction. Automation may prepare evidence only when separately authorized; it may not approve gates.

The locked drift-rejection criteria reject dashboard-as-authority, parity-as-auto-paper-readiness, D2-006-as-auto-shadow-promotion, score/rank/recommendation-as-promotion-authority, agentic execution of gates, and any conversion of permanent human gates into advisory-only steps.

These locked criteria constrain future authorization and implementation packages.

## 5. Phase 3 architecture sketch basis

WP-S2c-88 opened the Phase 3 architecture design surface and identified shadow deployment, monitoring/dashboard, paper-trading bridge, live-trading boundary, and checkpoint surfaces.

WP-S2c-89 sketched shadow deployment and shadow adapter/parity boundaries while preserving `SignalProvider`, D2-006, D2-007, Phase 1 paper runtime, OMS, reconciliation, risk, safe-mode, kill-switch, and Tier 4 boundaries.

WP-S2c-90 sketched monitoring/dashboard as derived read-only visibility from repo truth and runtime truth, with dashboard output barred from becoming authority.

WP-S2c-91 sketched paper-trading bridge architecture as a future question only, preserving the Phase 1 paper runtime and `SignalProvider` boundary.

WP-S2c-92 sketched the live-trading boundary and recorded that Phase 3 sketches must not cross into real-capital trading, exchange/broker/order contact, autonomous live deployment, live readiness claims, live promotion criteria, or Phase 4+ implementation.

WP-S2c-93 checkpointed the Phase 3 architecture sketch tranche as complete-as-built for documentation-only architecture sketching.

All of these surfaces are documentation-only sketches. None authorized implementation.

## 6. Initial authorization surface map

Shadow adapter and parity tooling authorization scope is expected to be sketched in WP-S2c-102. The question is what could be authorizable later while preserving locked criteria and protected boundaries, not what is authorized now.

Monitoring/dashboard and paper bridge authorization scope is expected to be sketched in WP-S2c-103, or bundled with WP-S2c-102 under E10 if Side chooses and refreshed repo truth remains clean. The question is what could be authorizable later, not what is authorized now.

The Phase 3 implementation authorization decision is expected in WP-S2c-104. WP-S2c-104 is Karl-gated and may record authorization only for scope Karl explicitly resolves in chat.

## 7. Pre-authorized / not-yet-authorized surfaces

No Phase 3 implementation surface is authorized by WP-S2c-101.

Some sketched surfaces may be eligible for later authorization review because they have architecture sketches and a locked criteria basis. Eligibility for later review is not authorization.

Some surfaces remain not-yet-authorized or explicitly deferred pending further decisions:

- approval-record artifact locations/schemas;
- shadow-evidence retention location/artifact grammar;
- Phase 4/live trading or paper-to-live work;
- Tier 4 contact;
- AUTO bridge canonical-write-path work unless separately revived;
- A2C-003 and Path B unless separately selected.

No implementation surface is called authorized by this package.

## 8. Tranche sequence

WP-S2c-101 is this opening package.

WP-S2c-102 is the shadow adapter plus parity tooling authorization-scope sketch.

WP-S2c-103 is the monitoring/dashboard plus paper bridge authorization-scope sketch.

WP-S2c-102 and WP-S2c-103 may be bundled under E10 if refreshed repo truth remains clean and scope can stay disciplined.

WP-S2c-104 is the Phase 3 implementation authorization decision. It is Karl-gated, uses T1-doc-major-decision posture, and requires full pytest.

Mandatory Main/Karl/user re-engagement occurs after WP-S2c-103 before WP-S2c-104 drafts.

Mandatory Main/Karl/user re-engagement occurs again after WP-S2c-104 for post-authorization direction.

## 9. Boundary discipline

This tranche is Tier 1 documentation-only until and unless WP-S2c-104 authorizes later implementation scope.

WP-S2c-101 through WP-S2c-103 do not authorize implementation.

WP-S2c-104 may record authorization only for scope Karl explicitly resolves in chat.

No implementation code or artifact changes occur in this tranche.

Permanent human gates remain absolute.

Tier 4 boundaries remain absolute.

Dashboard/monitoring outputs cannot become authority.

Criteria may inform human review but cannot replace human approval.

## 10. Open authorization-scope questions

- What shadow adapter and parity tooling scope could be authorized while preserving D2-007, `SignalProvider`, and paper runtime protection?
- What monitoring/dashboard scope could be authorized while preserving dashboard-from-repo-truth and DR-5?
- What paper bridge scope could be authorized while preserving Phase 1 paper runtime protection and no Tier 4 contact?
- Which packaging/artifact/schema questions remain deferred outside the authorization decision?
- What must Karl explicitly authorize, defer, or keep unauthorized at WP-S2c-104?

## 11. What is not authorized

This package does not authorize:

- Phase 3 implementation;
- shadow adapter implementation;
- parity tooling implementation;
- monitoring/dashboard implementation;
- paper bridge implementation;
- candidate readiness determination;
- research-to-shadow transition;
- shadow-to-paper transition;
- paper-to-live or live transition;
- live trading or real-capital trading;
- exchange/broker/order/live API/paper-live/Tier 4 contact;
- runtime / paper-live / OMS / reconciliation / risk / safe-mode / kill-switch / event-log schema / `SignalProvider` / config / dependency / data / protected-path changes;
- D2-006, D2-007, REC-5, Phase 9, WP-S2c-100 locked criteria, tiered-promotion, human-approval, or permanent-human-gate modification;
- performance ranking/scoring/recommendation authority;
- AUTO bridge further work;
- A2C-003 or Path B work except as deferred context;
- downstream authority.

## 12. Validation / checkpoint posture

WP-S2c-101 uses CS12 T1-doc-narrow.

WP-S2c-102 and WP-S2c-103 are expected to use T1-doc-narrow unless repo truth or stop triggers require escalation.

WP-S2c-102 and WP-S2c-103 may be bundled under E10 if scope remains disciplined.

WP-S2c-104 uses CS12 T1-doc-major-decision with full pytest and is Karl-gated.

Main/Karl/user re-engagement is mandatory after WP-S2c-103 and WP-S2c-104.
