# A2C-001 Cohort Interpretation / Stability

## Scope

WP-12ck / WP-S2c-43 is docs-only and cohort interpretation/stability only.

Committed file scope is only:

- `docs/research_pipeline/2026-05-a2c001_cohort_interpretation_stability.md`
- `docs/project_status.md`

This package creates no evidence artifacts and no runtime, implementation,
query-layer, validator, schema, configuration, dependency, data, paper/live,
OMS, risk, safe-mode, exchange, broker, execution, or protected-path change.

It is an interpretation and stability record for the current A2C-001
selected-member exact-segment evidence floor inventory. It is not an approval,
readiness, lifecycle, promotion, demotion, Path B, runtime, paper/live, policy,
scoring, ranking, recommendation, or downstream-authority package.

## Verified Repo-Truth Inputs

Repo truth consumed by this package:

- WP-12cj / PR #233 is merged to `main`; refreshed `main` is at merge commit
  `4e0813d68f97bcd3d41aaf1123fbee90afc62f09`.
- `docs/project_status.md` records WP-12cj / WP-S2c-42 as the latest
  branch-state and says that after merge Side must ask/confirm the next project
  track, with cohort-level interpretation/stability listed as a possible next
  track.
- No open PR touched `docs/project_status.md` during package preflight.
- No WP-12ck / WP-S2c-43 branch or PR existed before this package branch was
  created.
- Current A2C-001 selected members remain H-001, H-005, and H-006 under the
  committed A2C-001 methodology and current checkpoint docs.
- H-001, H-005, and H-006 remain research / non-runtime candidates in current
  repo truth.

Prior selected-member checkpoint docs:

- H-001 checkpoint:
  `docs/research_pipeline/2026-04-a2c001_h001_first_member_runway_checkpoint.md`
- H-005 checkpoint:
  `docs/research_pipeline/2026-05-a2c001_h005_runway_checkpoint.md`
- H-006 checkpoint:
  `docs/research_pipeline/2026-05-a2c001_h006_runway_checkpoint.md`

Query-verified exact counts:

```text
H-001 / research_oos / pre_wp_5b / d2_006_gates = 3
H-001 / research_oos / pre_wp_5b / exp_success_criteria = 3
H-005 / research_oos / pre_wp_5b / d2_006_gates = 3
H-005 / research_oos / pre_wp_5b / exp_success_criteria = 3
H-006 / research_oos / pre_wp_5b / d2_006_gates = 3
H-006 / research_oos / pre_wp_5b / exp_success_criteria = 3
```

Query-verified REC sets:

```text
H-001 d2_006_gates: REC-0012, REC-0027, REC-0028
H-001 exp_success_criteria: REC-0001, REC-0029, REC-0030
H-005 d2_006_gates: REC-0013, REC-0031, REC-0032
H-005 exp_success_criteria: REC-0002, REC-0033, REC-0034
H-006 d2_006_gates: REC-0017, REC-0035, REC-0037
H-006 exp_success_criteria: REC-0006, REC-0036, REC-0038
```

REC-0037 D2 DSR strict-operator correction remains valid:

- `expectation_source_type = d2_006_gates`
- `metric_name = dsr`
- `expected_operator = gt`
- `expected_value = 1.0`
- `realized_value = 1.0`
- `comparison_verdict = not_met`
- comparison notes state that equality does not strictly exceed the threshold.

## Selected-Member Exact-Segment Evidence Floor Inventory

selected-member exact-segment evidence floor inventory

```text
A2C-001 selected-member exact-segment evidence floor inventory:
- H-001 / research_oos / pre_wp_5b / d2_006_gates = 3
- H-001 / research_oos / pre_wp_5b / exp_success_criteria = 3
- H-005 / research_oos / pre_wp_5b / d2_006_gates = 3
- H-005 / research_oos / pre_wp_5b / exp_success_criteria = 3
- H-006 / research_oos / pre_wp_5b / d2_006_gates = 3
- H-006 / research_oos / pre_wp_5b / exp_success_criteria = 3
```

This inventory is recorded as complete only because query verification confirmed
all six exact counts remain `3`.

## Member Evidence-State Table

| candidate_id | exact segment source | count | REC set | floor status | checkpoint source |
|---|---:|---:|---|---|---|
| H-001 | `d2_006_gates` | 3 | `REC-0012`, `REC-0027`, `REC-0028` | floor reached | H-001 checkpoint |
| H-001 | `exp_success_criteria` | 3 | `REC-0001`, `REC-0029`, `REC-0030` | floor reached | H-001 checkpoint |
| H-005 | `d2_006_gates` | 3 | `REC-0013`, `REC-0031`, `REC-0032` | floor reached | H-005 checkpoint |
| H-005 | `exp_success_criteria` | 3 | `REC-0002`, `REC-0033`, `REC-0034` | floor reached | H-005 checkpoint |
| H-006 | `d2_006_gates` | 3 | `REC-0017`, `REC-0035`, `REC-0037` | floor reached | H-006 checkpoint |
| H-006 | `exp_success_criteria` | 3 | `REC-0006`, `REC-0036`, `REC-0038` | floor reached | H-006 checkpoint |

## Cohort Interpretation

The selected-member exact-segment evidence floor inventory is complete as
descriptive evidence inventory.

A2C-001 has reached the selected-member exact-segment evidence-floor closure
point defined by the current selected-member inventory.

The evidence-floor closure point is a decision surface, not a decision.

The repository now has enough descriptive selected-member floor evidence for
Main/Karl to choose the next strategic track.

This interpretation does not approve A2C-001, any selected member, or any
cohort-level action. It does not create readiness, lifecycle, promotion,
demotion, Path B, runtime, paper/live, OMS, risk, safe-mode, policy, scoring,
ranking, recommendation, or downstream authority.

## Stability Assessment

This assessment is limited to documentation and evidence-state stability.

- Count stability: all selected-member exact segments are at REC-5 floor count
  `3`.
- Source symmetry stability: each selected member has both `d2_006_gates` and
  `exp_success_criteria` exact segments represented at count `3`.
- Checkpoint stability: H-001, H-005, and H-006 each have a dedicated
  checkpoint/state document.
- Boundary stability: prior checkpoints and this package preserve
  no-approval, no-runtime, and no-downstream boundaries.

This assessment does not claim strategy performance stability, production
stability, risk stability, readiness/lifecycle stability, or any investment,
trading, ranking, or recommendation conclusion.

## Known Limitations / Non-Claims

This package does not evaluate whether the candidate strategies are good, bad,
tradable, deployable, or portfolio-suitable.

It does not aggregate metrics into a cohort score.

It does not compare candidates by performance.

It does not create a go/no-go decision.

It does not complete A2C-001 as a lifecycle object.

It does not authorize Path B.

It does not authorize approval/readiness/lifecycle/promotion/demotion.

## What Is Locked

This package locks only:

- Current A2C-001 selected-member exact-segment evidence floor inventory is
  recorded as complete because it was query-verified.
- H-001, H-005, and H-006 selected-member exact segments are each at count `3`
  for both selected expectation sources because they were query-verified.
- The state is descriptive evidence inventory only.
- Future strategic movement requires separate explicit authorization.

## What Is Not Authorized

This package does not authorize:

- candidate-level approval;
- selected-candidate approval;
- cohort-level approval;
- A2C-001 completion;
- Path B;
- runtime;
- paper/live;
- OMS;
- risk;
- safe mode;
- exchange/broker/execution behavior;
- config/dependency/data changes;
- additional evidence production;
- R1/R2 implementation changes;
- schema/validator/query-layer changes;
- policy/scoring/ranking/recommendation;
- approval/promotion/demotion/readiness/lifecycle authority;
- downstream authority.

It also creates no REP, OL, REC, EXP, LCH, trial-log, registry, schema,
validator, query-layer, implementation, config, dependency, data, runtime,
paper/live, OMS, risk, safe-mode, Path B, policy, scoring, ranking,
recommendation, readiness, lifecycle, promotion, demotion, or
downstream-authority material.

## Validation

Validation results for WP-12ck / WP-S2c-43:

- `git diff --check`: passed.
- Pre-staging changed-file scope:
  - `git diff --name-only`: `docs/project_status.md`.
  - `git status --short`: `M docs/project_status.md` and
    `?? docs/research_pipeline/2026-05-a2c001_cohort_interpretation_stability.md`.
  - `git ls-files --others --exclude-standard`:
    `docs/research_pipeline/2026-05-a2c001_cohort_interpretation_stability.md`.
- Advisory diff/scope helper:
  `.\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py --allowed-file docs/project_status.md --allowed-file docs/research_pipeline/2026-05-a2c001_cohort_interpretation_stability.md --json`
  passed with no allowed-file violations and no forbidden matches.
- Query views listed: 55.
- `v_integrity_*`: clean (24); every discovered integrity view ran with JSON
  output and returned `[]`.
- Exact count verification used
  `v_reconciliation_candidate_pipeline_summary` and confirmed:
  - `H-001 / research_oos / pre_wp_5b / d2_006_gates = 3`.
  - `H-001 / research_oos / pre_wp_5b / exp_success_criteria = 3`.
  - `H-005 / research_oos / pre_wp_5b / d2_006_gates = 3`.
  - `H-005 / research_oos / pre_wp_5b / exp_success_criteria = 3`.
  - `H-006 / research_oos / pre_wp_5b / d2_006_gates = 3`.
  - `H-006 / research_oos / pre_wp_5b / exp_success_criteria = 3`.
- REC set verification used `v_reconciliation_overview` and confirmed:
  - H-001 `d2_006_gates`: `REC-0012`, `REC-0027`, `REC-0028`.
  - H-001 `exp_success_criteria`: `REC-0001`, `REC-0029`,
    `REC-0030`.
  - H-005 `d2_006_gates`: `REC-0013`, `REC-0031`, `REC-0032`.
  - H-005 `exp_success_criteria`: `REC-0002`, `REC-0033`,
    `REC-0034`.
  - H-006 `d2_006_gates`: `REC-0017`, `REC-0035`, `REC-0037`.
  - H-006 `exp_success_criteria`: `REC-0006`, `REC-0036`,
    `REC-0038`.
- REC-0037 known correction verification used direct file inspection and
  confirmed `expectation_source_type = d2_006_gates`, `metric_name = dsr`,
  `expected_operator = gt`, `expected_value = 1.0`, `realized_value = 1.0`,
  `comparison_verdict = not_met`, and comparison notes stating equality does
  not strictly exceed the threshold.
- Registry validators: 14 `tools.registry.validate_*` modules passed.
- Targeted query tests:
  `.\.venv\Scripts\python.exe -m pytest tests/test_research_query_reconciliation_views.py tests/test_research_query_outcome_ledger_views.py -q`
  passed with 19 passed in 42.97 seconds.
- Helper tests:
  `.\.venv\Scripts\python.exe -m pytest tests/test_diff_scope_summary.py tests/test_validation_summary.py tests/test_code_index.py tests/test_status_snapshot.py -q`
  passed with 61 passed in 21.42 seconds.
- Scoped regression:
  `.\.venv\Scripts\python.exe -m pytest tests -q -k "registry or research_query or reconciliation or outcome_ledger or lifecycle or experiment or diff_scope_summary or validation_summary or code_index or status_snapshot"`
  passed with 303 passed and 314 deselected in 287.80 seconds.
- Full pytest: `.\.venv\Scripts\python.exe -m pytest -q` passed with 617
  passed and 4 warnings in 288.87 seconds.

## Future Decision Boundary

Main/Karl must make the next project-track decision explicitly.

Open options:

```text
A. Main/Karl authorizes a separate A2C-001 approval/readiness discussion package.
B. Main/Karl authorizes a Path B architecture discussion package.
C. Main/Karl authorizes another bounded research/documentation track.
D. Main/Karl stops/defer further A2 work.
```

This document does not select among these options.
