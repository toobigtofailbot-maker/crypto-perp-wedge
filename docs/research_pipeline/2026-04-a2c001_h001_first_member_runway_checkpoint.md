# A2C-001 H-001 First-Member Runway Checkpoint / Stability Lock

## Scope

WP-12bc / WP-S2c-20 is documentation-only and checkpoint/stability-lock only.

This package records the current committed H-001 first-member runway state inside
A2C-001. It creates no new evidence artifacts and changes no runtime,
implementation, query-layer, validator, schema, configuration, dependency, data,
paper/live, OMS, risk, safe-mode, exchange, broker, execution, or protected-path
behavior.

Committed file scope for this package is this document and
`docs/project_status.md` only.

## Verified repo-truth inputs

Repo truth consumed by this checkpoint:

- EXP: `EXP-0002`.

D2 segment:

- `REP-0016` / `OL-0016` / `REC-0027`.
- `REP-0017` / `OL-0017` / `REC-0028`.
- `REC-0012` as the pre-existing seed REC for H-001 `d2_006_gates`.

EXP-success segment:

- `REC-0001` as the pre-existing seed REC for H-001
  `exp_success_criteria`.
- `REP-0018` / `OL-0018` / `REC-0029`.
- `REP-0019` / `OL-0019` / `REC-0030`.

Repo-truth notes:

- `REC-0030` derives from `OL-0019`.
- `REC-0030` targets
  `H-001 / research_oos / pre_wp_5b / exp_success_criteria`.
- `REC-0030` increased that exact segment count from `2` to `3`.
- `EXP-0002` remains the committed EXP provenance for the H-001 runway
  artifacts listed above.

## H-001 exact-segment evidence state

Current exact-segment state:

```text
H-001 / research_oos / pre_wp_5b / d2_006_gates = 3
H-001 / research_oos / pre_wp_5b / exp_success_criteria = 3
```

Both segments reached REC-5 floor count `3`.

These two floor crossings are exact-segment floor crossings only. They do not
combine into candidate-level approval, cohort-level approval, Path B authority,
runtime authority, paper/live authority, lifecycle authority, readiness,
promotion, demotion, recommendation, ranking, policy, scoring, or downstream
authority.

## D2-006 gates segment

- Exact segment: `H-001 / research_oos / pre_wp_5b / d2_006_gates`.
- Count: `3`.
- REC set: `REC-0012`, `REC-0027`, `REC-0028`.
- Floor status: REC-5 count reached.
- Boundary: no candidate-level, cohort-level, policy, readiness,
  promotion/demotion, runtime, paper/live, or downstream authority.

## EXP success criteria segment

- Exact segment: `H-001 / research_oos / pre_wp_5b / exp_success_criteria`.
- Count: `3`.
- REC set: `REC-0001`, `REC-0029`, `REC-0030`.
- Floor status: REC-5 count reached.
- Boundary: no candidate-level, cohort-level, policy, readiness,
  promotion/demotion, runtime, paper/live, or downstream authority.

## What is locked

This checkpoint locks only these facts:

- H-001 first-member runway reached the exact-segment evidence floor for the two
  specified expectation sources.
- The `d2_006_gates` exact segment floor-crossed at count `3`.
- The `exp_success_criteria` exact segment floor-crossed at count `3`.
- The locked state is descriptive evidence inventory only.
- Any future A2C-001 expansion must be separately authorized.

## What is not authorized

This checkpoint does not authorize:

- candidate-level approval;
- cohort-level approval;
- Path B;
- runtime;
- paper/live;
- OMS;
- risk;
- safe mode;
- exchange/broker/execution behavior;
- config/dependency/data changes;
- H-005/H-006 work;
- paired-source reuse;
- AUTO successor work;
- policy/scoring/ranking/recommendation;
- approval/promotion/demotion/readiness/lifecycle authority;
- downstream authority.

It also creates no REP, OL, REC, EXP, LCH, schema, validator, query-layer,
implementation, config, dependency, data, runtime, paper/live, OMS, risk,
safe-mode, Path B, H-005/H-006, paired-source reuse, scoring, ranking,
recommendation, readiness, lifecycle, promotion/demotion, or downstream-authority
material.

## Main report-back requirement

After WP-12bc / WP-S2c-20 merges, Side must report back to Main because the
H-001 first-member runway checkpoint has completed.

Required report-back format:

```text
Main,

WP-12bc / WP-S2c-20 is merged.

Delivered:
- Added the H-001 first-member runway checkpoint / stability lock.
- Recorded that both H-001 exact segments in A2C-001 reached REC-5 floor count:
  - H-001 / research_oos / pre_wp_5b / d2_006_gates = 3
  - H-001 / research_oos / pre_wp_5b / exp_success_criteria = 3
- Confirmed this is exact-segment evidence only.

Validation:
- [insert actual validation summary from PR body: query views, integrity views, validators/tests, diff checks, changed files]

Boundary:
- No REP, OL, REC, EXP, LCH, schema, validator, query-layer, implementation, config, dependency, data, runtime, paper/live, OMS, risk, safe mode, Path B, paired-source reuse, H-005/H-006, policy/scoring/ranking/recommendation, approval, promotion/demotion, readiness, lifecycle, or downstream authority was created.
- Floor-crossing is limited to the two H-001 exact segments and does not create candidate-level or cohort-level authority.

State after merge:
- H-001 first-member runway is complete at the exact-segment evidence floor.
- H-001 d2_006_gates: REC-5 floor crossed at count 3.
- H-001 exp_success_criteria: REC-5 floor crossed at count 3.
- A2C-001 broader cohort is not complete unless Main/Karl or repo truth says otherwise.
- H-005/H-006 remain not authorized unless Main/Karl explicitly opens that next track.

Decision needed:
- Please decide the next track:
  A. Continue A2C-001 by opening H-005/H-006 strict exact-segment evidence packages.
  B. Pause and perform a cohort-level interpretation/stability document first.
  C. Open a different A2 architecture / Path B / automation decision track.
  D. Stop/defer further A2C-001 expansion.

Request:
- If possible, provide several capsules at once so Side can continue efficiently inside the approved next envelope without asking Main after every WP.
```

## Future-decision boundary

After this checkpoint, Main/Karl must decide the next track.

Open options only:

```text
A. Continue A2C-001 by opening H-005/H-006 strict exact-segment evidence packages.
B. Pause and perform a cohort-level interpretation/stability document first.
C. Open a different A2 architecture / Path B / automation decision track.
D. Stop/defer further A2C-001 expansion.
```

This document does not select among these options, recommend one, or imply that
H-005/H-006, Path B, cohort-level interpretation, or any next package is
authorized.

## Validation

Validation results recorded for WP-12bc / WP-S2c-20:

- `git diff --check`: passed.
- Pre-staging changed-file scope: limited to `docs/project_status.md` and
  `docs/research_pipeline/2026-04-a2c001_h001_first_member_runway_checkpoint.md`.
- Query views listed: 55.
- Integrity views checked: 24 discovered `v_integrity_*` views; all returned
  `[]`.
- Registry validators: 14 `tools.registry.validate_*` modules passed.
- Scoped pytest:
  `.\.venv\Scripts\python.exe -m pytest tests -q -k "registry or research_query or reconciliation or outcome_ledger or lifecycle or experiment"`
  initially timed out at 304 seconds during the parallel validation run, then
  passed on rerun with 242 passed and 314 deselected in 258.11 seconds.
- Full pytest: `.\.venv\Scripts\python.exe -m pytest -q` initially timed out
  at 304 seconds during the parallel validation run, then passed on rerun with
  556 passed and 4 warnings in 275.89 seconds.
