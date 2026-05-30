# Path B Execution Design Opening

## 1. Scope

WP-S2c-124 / WP-12fd is a Tier 1 documentation-only opening package.
It opens the bounded Path B execution tranche under locked Option B.

This package creates only this opening document and updates
`docs/project_status.md`.

Validation profile: CS12 T1-doc-narrow.

This package creates no candidate registration, hypothesis pre-registration,
EXP/REP, trial-log entry, OL/REC, DEC, artifact, query, test, tool change,
schema change, validator change, runtime/protected-path change, readiness
determination, transition authorization, or human-gate execution.

## 2. Repo-truth basis

WP-S2c-123 is merged and locked Option B as-written. It rejected Options A, D,
and E, and deferred Options C and F. It also states that Option B locking does
not itself authorize Path B execution.

Main 4.0 has now approved bounded Path B execution under locked Option B.

WP-S2c-119 produced the second cross-candidate diagnostic brief. That brief
showed pipeline-empty state and diagnostic-only findings.

Current Scope 6 surface is complete at schema, validator, and query-layer
level:

- WP-S2c-100 locked refined approval/readiness criteria.
- WP-S2c-104 locked implementation authorization and deferred monitoring,
  dashboard, and paper bridge.
- WP-S2c-113 locked Scope 6 artifact families.
- WP-S2c-114 introduced Scope 6 schemas.
- WP-S2c-115 introduced Scope 6 validators.
- WP-S2c-117 introduced Scope 6 query-layer views.

Existing canonical artifacts and existing briefs are historical records and
are not modified by this package.

## 3. Execution authorization status

Path B execution authorization is approved and bounded.

Authorization is limited to locked Option B's narrow
current-taxonomy/current-timeframe-discipline design surface.

This opening package does not itself execute anything.

Candidate registration and hypothesis pre-registration are reserved for
WP-S2c-126 after WP-S2c-125 design and pre-draft verification.

Initial authorization covers one candidate only. Multiple-candidate batch
registration is not authorized.

## 4. Locked Option B execution surface

The exact locked Option B wording is:

- Path B may be prepared as a narrow current-taxonomy/current-timeframe
  discipline route that examines under-covered strategy-family, timeframe, and
  information-input combinations already permitted by repo truth.
- The route must not add information-input taxonomy labels, modify
  timeframe-status discipline, contact Tier 4/protected paths, register
  candidates, pre-register hypotheses, run backtests, or create artifacts
  unless a later execution-authorization package explicitly permits those
  actions.
- Any later execution design must preserve D2-006, D2-007, REC-5, permanent
  human gates, WP-S2c-100 locked criteria, and Path B execution
  non-authorization until separately resolved.

D2-006, D2-007, REC-5, permanent human gates, locked taxonomy/timeframe
discipline, and Phase 1 paper runtime protection remain unchanged.

## 5. Diagnostic basis

WP-S2c-119 is the diagnostic evidence source for this opening.

At opening level, the diagnostic basis is:

- ten concluded baseline-tested candidates;
- one reserved draft row;
- zero active R2S/S2P approval-surface candidates;
- all concluded groups are NO-GO in the diagnostic brief's current-state
  framing;
- search-space coverage is sparse by strategy-family/timeframe;
- information-input coverage is concentrated in existing crypto-perp internal
  streams;
- Q08 and Q11 integrity sweeps were clean in the brief.

These facts motivate a narrow re-prime route. They do not select a candidate
or imply readiness.

## 6. Execution tranche objective

The tranche objective is to re-prime the research pipeline with one initial
Path B candidate under locked Option B.

The tranche may produce pre-registered research evidence through the canonical
sequence only after later packages authorize each surface.

The intended evidence should be consumable by future R2S human-approval
moments if the evidence warrants it.

The tranche does not declare candidate readiness, propose transitions, create
R2S/S2P approval records, or create shadow-evidence retention artifacts.

## 7. Allowed execution surfaces by later package

Later packages may cover the following surfaces without this package executing
them:

- WP-S2c-125: design-only candidate-selection surface.
- WP-S2c-126: candidate registry row plus HYPOTHESIS.md and initial
  experiment.ipynb, after pre-draft verification.
- WP-S2c-127: EXP creation.
- WP-S2c-128: backtest + trial-log + REP.
- WP-S2c-129: OL + REC.
- WP-S2c-130: DEC.
- WP-S2c-131: tranche checkpoint.

This package performs none of those actions.

## 8. Forbidden surfaces

This package and the opened tranche do not authorize:

- taxonomy modification;
- timeframe_status modification;
- data catalog modification;
- external data, paid data, Tier 4, protected-path, runtime, paper/live
  contact;
- schemas/validators/query-view changes;
- candidate registration in this package;
- hypothesis pre-registration in this package;
- backtest execution;
- research artifacts;
- cross-segment inference below REC-5 floor;
- ranking/scoring/recommendation;
- candidate readiness;
- transition authorization;
- R2S/S2P approval-record instance creation;
- shadow-evidence retention artifact instance creation;
- monitoring/dashboard;
- paper bridge;
- AUTO bridge;
- A2C-003;
- multiple-candidate batch registration;
- C-shape or F-shape framing;
- reopening A/D/E.

## 9. Candidate-selection questions deferred to WP-S2c-125

The following questions are unresolved here and deferred to WP-S2c-125:

- Which specific strategy-family is under-covered and permitted?
- Which specific timeframe is under-covered and present in locked
  timeframe_status?
- Which information_inputs labels are permitted by locked taxonomy?
- Which data source is present in the locked data catalog?
- What economic rationale supports the candidate?
- What testable predictions and success/failure criteria are appropriate?
- What is the expected free-parameter count under D2-006?
- What is the expected DSR-aware trial-count budget?
- Whether H-011 remains the correct reserved slot is not resolved here;
  verify later.

## 10. Source-verification requirements for WP-S2c-125 and WP-S2c-126

WP-S2c-125 must use actual repo-truth source files to confirm taxonomy,
timeframe, and data catalog.

WP-S2c-126 must perform pre-draft verification by direct file inspection:

- reserved candidate slot exists;
- selected information_inputs labels exist verbatim in locked taxonomy;
- selected timeframe exists verbatim in locked timeframe_status;
- selected data source exists in locked data catalog.

Failure to verify halts and reports back.

No silent reinterpretation is allowed.

## 11. Tranche sequence and dependencies

The authorized sequence is:

1. WP-S2c-124 - execution design opening.
2. WP-S2c-125 - candidate-selection design.
3. WP-S2c-126 - candidate registration + hypothesis pre-registration.
4. WP-S2c-127 - EXP creation.
5. WP-S2c-128 - backtest + trial-log + REP.
6. WP-S2c-129 - OL + REC.
7. WP-S2c-130 - DEC.
8. WP-S2c-131 - tranche checkpoint.

Each package depends on the previous package's merged repo truth.

## 12. Required validation posture

WP-S2c-124 and WP-S2c-125 use CS12 T1-doc-narrow.

WP-S2c-126 through WP-S2c-129 use T3-implementation with full pytest required.

WP-S2c-130 uses T1-doc-major-decision with full pytest required.

WP-S2c-131 uses T1-doc-narrow.

Full pytest is not required for WP-S2c-124 unless repo guidance or a stop
trigger escalates.

## 13. Stop conditions

Stop if any of the following arise:

- any tension with locked Option B wording;
- any need to modify locked taxonomy, timeframe_status, data catalog, schemas,
  validators, query views, or locked decisions;
- any selection pressure that would require C-shape or F-shape framing;
- any attempt to reopen A/D/E;
- any attempt to register multiple candidates;
- any candidate-selection claim without source verification;
- any ranking/scoring/recommendation framing;
- any readiness or transition assertion;
- any cross-segment inference below REC-5 floor;
- any Tier 4/protected-path/runtime/paper/live contact;
- Karl/user override.

## 14. Explicit non-authorizations

This package does not authorize:

- candidate registration;
- hypothesis pre-registration;
- experiment plan;
- backtest execution;
- trial-log entries;
- REP;
- OL/REC;
- DEC;
- R2S approval record;
- S2P approval record;
- shadow-evidence retention artifact;
- candidate readiness;
- transition;
- multiple candidates;
- taxonomy/timeframe/data-catalog changes;
- tools/tests/schema/validator/query-layer changes;
- monitoring/dashboard;
- paper bridge;
- AUTO bridge;
- A2C-003;
- Tier 4/protected-path contact.

## 15. Validation / next-package posture

WP-S2c-124 uses CS12 T1-doc-narrow.

After merge, Side may draft WP-S2c-125 after refreshed-main preflight and no
stop trigger.

WP-S2c-125 remains design-only and must not register a candidate.
