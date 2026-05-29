# Phase 3 Implementation Tranche Planning

## 1. Scope

WP-S2c-105 / WP-12ek is a Tier 1 documentation-only planning package.

It plans the bounded Phase 3 Tier 3 implementation tranche authorized by WP-S2c-104 for shadow adapter and parity tooling implementation.

This package creates only this document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-narrow.

This package creates no implementation code, directories, tests, artifacts, schemas, validators, query-layer changes, runtime changes, transition authority, candidate readiness determination, or Tier 4 contact.

## 2. Repo-truth basis

WP-12ej / WP-S2c-104 is merged.

WP-S2c-104 authorizes bounded future Tier 3 shadow adapter and parity tooling implementation.

WP-S2c-104 defers monitoring and dashboard implementation.

WP-S2c-104 keeps paper bridge implementation unauthorized.

WP-S2c-104 defers Scope 6 packaging/schema/artifact questions outside WP-S2c-104.

WP-S2c-100 locked approval/readiness criteria remain binding.

WP-S2c-88 through WP-S2c-93 Phase 3 architecture sketches remain the architecture basis.

The `SignalProvider` Protocol is locked and consumed read-only.

D2-007 thresholds remain locked and unmodified.

Phase 1 paper runtime protection remains absolute.

Permanent human gates and Tier 4 boundaries remain absolute.

Repo-local implementation idiom already includes `tools/shadow/` with advisory-only shadow helper surfaces. That existing directory is the planned documentation-level default for later bounded Tier 3 code unless a later package finds a stronger current repo-truth reason to stop and report.

## 3. Authorization basis from WP-S2c-104

Shadow adapter implementation may be planned only as observational tooling around the locked `SignalProvider` Protocol.

Future shadow adapter implementation may observe `SignalProvider`-compatible candidate signals but may not generate orders, invoke paper/live execution, contact exchange/broker/order surfaces, contact paper/live runtime, or contact OMS/reconciliation/risk/safe-mode/kill-switch.

Parity tooling implementation may be planned only as observational measurement of D2-007 shadow-window and parity evidence under locked thresholds: PnL deviation <= 10%, trade-count deviation <= 5%, and at least 14 calendar days.

Mismatch diagnostics are decision-support only and cannot become ranking, scoring, recommendation, policy authority, readiness authority, or automated paper-transition authority.

Future implementation lands as Tier 3 code under `tools/` or a new dedicated subdirectory, with tests under `tests/`.

No protected-path modification is allowed.

## 4. Implementation tranche sequence

- WP-S2c-105: planning.
- WP-S2c-106: shadow adapter module implementation.
- WP-S2c-107: parity tooling implementation.
- WP-S2c-108: evidence and disclosure surface implementation.
- WP-S2c-109: integration tests and end-to-end shadow observation surface.
- WP-S2c-110: tranche checkpoint.

No bundling is planned in this tranche.

WP-S2c-106 through WP-S2c-109 are T3-implementation packages with full pytest.

WP-S2c-110 is T1-doc-narrow.

Mandatory Main re-engagement is required after WP-S2c-110.

## 5. Planned subdirectory layout

The planned future implementation layout is `tools/shadow/`, because current repo truth already has that advisory-only shadow tooling directory and no stronger naming idiom is present.

This package does not create any directory or implementation file.

Planned future files may include:

- `tools/shadow/__init__.py`
- `tools/shadow/adapter.py`
- `tools/shadow/parity.py`
- `tools/shadow/evidence.py`
- `tools/shadow/orchestrate.py`, only if needed in WP-S2c-109 and still bounded

Planned future tests may include:

- `tests/test_shadow_adapter.py`
- `tests/test_shadow_parity.py`
- `tests/test_shadow_evidence.py`
- `tests/test_shadow_integration.py`

These paths are planning targets for later packages only. They are not created now and have no execution authority from this package.

## 6. Planned module boundaries

Shadow adapter module:

- observes `SignalProvider`-compatible candidate signals;
- remains non-executing;
- generates no orders;
- invokes no paper/live execution;
- has no Tier 4 contact;
- has no protected-path contact.

Parity tooling module:

- computes D2-007 parity observations;
- computes PnL deviation and trade-count deviation;
- applies locked threshold comparison without modifying thresholds;
- remains decision-support only.

Evidence/disclosure module:

- produces non-canonical local human-review evidence;
- records lineage references;
- records interruptions, invalid observations, missing data, and observation resets;
- does not create canonical artifacts or schemas.

Integration/orchestration utility:

- exists only if needed in WP-S2c-109;
- wires local modules for tests or local bounded flow;
- cannot contact execution surfaces or produce canonical artifacts.

## 7. SignalProvider interface contract

The future adapter consumes the locked `SignalProvider` Protocol as read-only.

The future adapter must not modify `src/signal/provider.py` or any Protocol definition.

Future tests may use local fakes/stubs under `tests/` to represent `SignalProvider`-compatible signal outputs.

No dependency on runtime/paper/live execution surfaces may be introduced.

Any future implementation tension with `SignalProvider` requires stopping and reporting.

## 8. Planned test surface

WP-S2c-106 tests:

- observation correctness;
- non-executing behavior;
- interface contract with the locked `SignalProvider` Protocol;
- no order/execution/contact behavior.

WP-S2c-107 tests:

- PnL deviation calculation;
- trade-count deviation calculation;
- 14-calendar-day window handling;
- threshold comparison against locked D2-007 thresholds;
- decision-support-only output.

WP-S2c-108 tests:

- non-canonical evidence shape;
- lineage completeness;
- interruption/invalid/missing/reset disclosure;
- no canonical artifact shape;
- no ranking/scoring/recommendation/readiness/transition authority.

WP-S2c-109 tests:

- end-to-end local shadow adapter -> parity tooling -> evidence/disclosure flow;
- non-executing behavior end-to-end;
- evidence correctness and disclosure completeness;
- D2-007 threshold behavior end-to-end.

All implementation packages use T3-implementation with full pytest.

## 9. Non-canonical local evidence-output shape

Future local evidence output is planned as a plain local decision-support shape only.

This package does not define a schema file, canonical artifact location, registry integration, query-layer exposure, approval-record artifact location/schema, or Scope 6 deferred packaging resolution.

Planning-level fields may include:

- candidate reference;
- observation window start/end;
- D2-007 threshold values used as references only;
- PnL deviation observation;
- trade-count deviation observation;
- interruption/invalid/missing/reset disclosure;
- lineage references to local input observations;
- generated timestamp;
- explicit `decision_support_only: true`;
- explicit `canonical: false`;
- explicit no-readiness/no-transition/no-approval statement.

These are planning-level fields, not a schema and not an implementation in this package.

## 10. Disclosure surface

Future evidence/disclosure surface must disclose:

- interruptions;
- invalid observations;
- missing data;
- observation resets.

Disclosure is for human review only.

Disclosure cannot automate approval, readiness, transition, ranking, scoring, recommendation, or policy authority.

## 11. Lineage and retention posture

Lineage tracking is planned for local evidence only.

Local lineage may reference local observation inputs and computation inputs.

This package does not define final retention policy, canonical retention location, artifact grammar, or repo-truth query exposure.

Scope 6 packaging questions remain deferred outside this tranche unless Main later authorizes them.

Evidence in WP-S2c-108 is planned as non-canonical local evidence under WP-S2c-104 authorization.

## 12. Per-package sizing

WP-S2c-106:

- create shadow adapter module under the planned subdirectory;
- create tests under `tests/`;
- add a `docs/project_status.md` entry;
- use T3-implementation with full pytest.

WP-S2c-107:

- create parity tooling module under the planned subdirectory;
- create tests under `tests/`;
- add a `docs/project_status.md` entry;
- use T3-implementation with full pytest.

WP-S2c-108:

- create evidence/disclosure module under the planned subdirectory;
- create tests under `tests/`;
- add a `docs/project_status.md` entry;
- use T3-implementation with full pytest.

WP-S2c-109:

- create integration tests;
- optionally create a small orchestration utility under the planned subdirectory only if needed and still bounded;
- add a `docs/project_status.md` entry;
- use T3-implementation with full pytest.

WP-S2c-110:

- create tranche checkpoint doc;
- add a `docs/project_status.md` entry;
- use T1-doc-narrow;
- stop and report to Main after merge.

## 13. Boundary discipline

Permanent human gates are absolute.

Tier 4 boundaries are absolute.

D2-006, D2-007, REC-5, Phase 9 Decision 9, WP-S2c-100 locked criteria, Phase 9 Decision 6, tiered-promotion semantics, and human-approval semantics remain unchanged.

The `SignalProvider` Protocol is consumed, not modified.

Phase 1 paper runtime protected execution-core remains untouched.

Monitoring, dashboard, and paper bridge remain outside this tranche.

Scope 6 packaging/schema/artifact questions remain deferred.

No runtime/protected-path work is authorized.

No transition authority is created.

No candidate readiness determination is created.

No scoring/ranking/recommendation/policy authority is created.

AUTO bridge remains frozen; A2C-003 and Path B remain unauthorized.

## 14. What this planning package does not authorize

This planning package does not authorize:

- implementation code;
- tool/module/test file creation;
- directory creation under `tools/` or `tests/`;
- runtime/protected-path changes;
- `SignalProvider` Protocol modification;
- D2-007 threshold modification;
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
- research-to-shadow transition;
- shadow-to-paper transition;
- paper-to-live or live transition;
- candidate readiness determination;
- candidate approval or promotion;
- paper/live contact;
- live trading or real-capital trading;
- exchange/broker/order/live API/execution/Tier 4 contact;
- human-gate automation, bypass, weakening, replacement, reinterpretation, or agentic execution;
- performance ranking/scoring/recommendation/policy authority;
- AUTO bridge further work;
- A2C-003 or Path B work except as deferred context;
- post-WP-S2c-110 direction.

## 15. Validation / next-package posture

WP-S2c-105 uses CS12 T1-doc-narrow.

WP-S2c-106 is next after WP-S2c-105 merges, if refreshed-main preflight is clean and no stop trigger fires.

WP-S2c-106 uses T3-implementation with full pytest.

Side may auto-draft WP-S2c-106 after WP-S2c-105 merge.
