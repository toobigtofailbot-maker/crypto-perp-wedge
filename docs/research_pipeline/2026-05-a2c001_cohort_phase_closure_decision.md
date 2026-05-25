# A2C-001 Cohort-Phase Closure Decision

## A. Scope

WP-12da / WP-S2c-59 is a Tier 1 documentation-only closure decision package.

Committed file scope is only:

- `docs/research_pipeline/2026-05-a2c001_cohort_phase_closure_decision.md`
- `docs/project_status.md`

This package creates no REP, OL, REC, EXP, lifecycle, registry, trial-log,
schema, validator, query-layer, canonical-corpus, config, dependency, data,
runtime, paper/live, OMS, risk, safe-mode, exchange, broker, execution, or
protected-path change.

This package records formal A2C-001 cohort-phase closure only. It creates no
Path B, A2C-002, approval, readiness, lifecycle, AUTO bridge implementation,
policy, scoring, ranking, recommendation, broad floor-crossing, Phase 3, or
downstream authority.

## B. Verified Repo-Truth Inputs

Repo-file evidence and preflight:

- PR #249 / WP-12cz is merged to `main` at merge commit
  `d455aa9ad714770997fef9ca7c567693c50fe05c`.
- Local `main` and `origin/main` were both at
  `d455aa9ad714770997fef9ca7c567693c50fe05c` during preflight.
- `docs/project_status.md` records WP-12cz / WP-S2c-58 as the latest
  branch-state before this package.
- No open PR was found touching `docs/project_status.md`.
- No WP-12da / WP-S2c-59 branch or PR existed before this package branch was
  created.
- This closure decision document did not exist before this package.
- `git diff d455aa9ad714770997fef9ca7c567693c50fe05c..HEAD --name-only`
  returned no committed file changes after WP-12cz.
- No schema, validator, central query-layer, canonical-corpus, config,
  dependency, data, runtime, or protected-path change is required for this
  closure decision.

Reference block - A2C-001 evidence and decision state:

- `docs/research_pipeline/2026-05-a2c001_cohort_completion_checkpoint.md`
  records evidence-level A2C-001 cohort completion from repo truth and states
  that it does not claim formal cohort-phase closure.
- `docs/research_pipeline/2026-05-a2c001_reopening_h005_status_reconciliation.md`
  records the WP-12cy reopening record and reconciles that no H-005 strict
  evidence packages remain under current repo truth.
- `docs/research_pipeline/2026-05-a2c001_stop_defer_hold_lock.md`,
  `docs/research_pipeline/2026-05-a2c001_post_deferral_closeout_index.md`,
  and
  `docs/research_pipeline/2026-05-a2c001_deferral_no_approval_decision_lock.md`
  record A2C stop/defer, closeout, and no-approval state.
- `docs/research_pipeline/2026-05-a2c001_cohort_interpretation_stability.md`
  records the selected-member exact-segment evidence floor inventory as
  complete descriptive evidence inventory.
- `docs/research_pipeline/2026-05-post_a2c_active_track_selection_gate.md`
  and `docs/research_pipeline/2026-05-post_a2c_lessons_decision_review.md`
  record that no post-A2C substantive track or future-track selection was
  created by those packages.

A2C-001 cohort definition:

- `research/candidate_registry.jsonl` contains H-001, H-005, and H-006 as
  `CONCLUDED` / `NO-GO` with pipeline stage `baseline_tested`.
- H-011 remains `DRAFT` / `PENDING` with pipeline stage `reserved`.
- No H-012+ registration exists in the inspected registry.
- A2C-001 cohort remains H-001, H-005, and H-006 only.
- This package does not modify the candidate registry.

Repo-file evidence for selected exact-segment counts:

- `docs/research_pipeline/2026-04-a2c001_h001_first_member_runway_checkpoint.md`
  records H-001 selected exact segments at count `3` for `d2_006_gates` and
  `exp_success_criteria`.
- `docs/research_pipeline/2026-05-a2c001_h005_runway_checkpoint.md` records
  H-005 selected exact segments at count `3` for `d2_006_gates` and
  `exp_success_criteria`.
- `docs/research_pipeline/2026-05-a2c001_h006_runway_checkpoint.md` records
  H-006 selected exact segments at count `3` for `d2_006_gates` and
  `exp_success_criteria`, and records the A2C-001 selected-member
  exact-segment evidence floor inventory as complete.
- `docs/research_pipeline/2026-05-a2c001_cohort_interpretation_stability.md`
  and
  `docs/research_pipeline/2026-05-a2c001_cohort_completion_checkpoint.md`
  record the same six selected exact-segment counts.

Query-executed evidence from `v_reconciliation_candidate_pipeline_summary`:

```text
H-001 / research_oos / pre_wp_5b / d2_006_gates = 3
H-001 / research_oos / pre_wp_5b / exp_success_criteria = 3
H-005 / research_oos / pre_wp_5b / d2_006_gates = 3
H-005 / research_oos / pre_wp_5b / exp_success_criteria = 3
H-006 / research_oos / pre_wp_5b / d2_006_gates = 3
H-006 / research_oos / pre_wp_5b / exp_success_criteria = 3
```

Query-executed REC sets from `v_reconciliation_overview`:

```text
H-001 d2_006_gates: REC-0012, REC-0027, REC-0028
H-001 exp_success_criteria: REC-0001, REC-0029, REC-0030
H-005 d2_006_gates: REC-0013, REC-0031, REC-0032
H-005 exp_success_criteria: REC-0002, REC-0033, REC-0034
H-006 d2_006_gates: REC-0017, REC-0035, REC-0037
H-006 exp_success_criteria: REC-0006, REC-0036, REC-0038
```

R1/R2 status:

- `docs/research_pipeline/2026-05-r1_r2_h006_approval_use_lock.md` records R1
  paired-source reuse, R2 batched REP+OL+REC cycles, and combined R1/R2 use as
  approved methodology for H-006 onward when eligibility holds.
- R1/R2 is forward-applicable methodology. It is not retroactively reapplied
  by this closure decision.

AUTO bridge and Path B status:

- `docs/research_pipeline/2026-05-auto_bridge_design_tranche_checkpoint.md`
  records the AUTO bridge design tranche as checkpointed.
- AUTO remains paused, local-only, research-only, non-authoritative, and
  non-canonical.
- AUTO bridge implementation remains unauthorized.
- Existing pre-bridge AUTO outputs remain non-canonical and are not evidence
  for this closure decision.
- Path B remains deferred / unauthorized in the inspected stop/defer,
  post-A2C, WP-12cy, WP-12cz, and AUTO bridge documents.
- No post-closure direction has been selected in repo truth.

## C. Closure Decision

A2C-001 cohort phase is formally closed as complete-as-built.

Closure is based on evidence-level completion across H-001, H-005, and H-006 at
REC-5 floor for selected exact expectation-source segments.

Closure is structural and repo-state based.

Closure satisfies SS-D-3's cohort-phase closure precondition for downstream
decision consideration.

Closure does not authorize any downstream path.

## D. Closure Boundary

Closure applies only to the A2C-001 / SS-D-1 cohort phase.

SS-D-2 / Path B phase remains unauthorized.

SS-D-3 condition is satisfied, but conditional clauses it gates remain
unauthorized.

SS-D-4 / forbidden scopes remain unchanged.

Closure does not claim broad floor crossing, Phase 3 readiness, approval,
lifecycle transition, or policy/scoring/ranking/recommendation authority.

## E. Member Summary

| cohort member | selected expectation-source segment(s) | exact count | supporting checkpoint / REC sets / query views | closure status |
|---|---|---:|---|---|
| H-001 | `research_oos / pre_wp_5b / d2_006_gates`; `research_oos / pre_wp_5b / exp_success_criteria` | 3 each | H-001 checkpoint; `REC-0012`, `REC-0027`, `REC-0028`; `REC-0001`, `REC-0029`, `REC-0030`; `v_reconciliation_candidate_pipeline_summary`; `v_reconciliation_overview` | closed as complete-as-built for selected exact segments |
| H-005 | `research_oos / pre_wp_5b / d2_006_gates`; `research_oos / pre_wp_5b / exp_success_criteria` | 3 each | H-005 checkpoint; WP-12cy reconciliation; `REC-0013`, `REC-0031`, `REC-0032`; `REC-0002`, `REC-0033`, `REC-0034`; `v_reconciliation_candidate_pipeline_summary`; `v_reconciliation_overview` | closed as complete-as-built for selected exact segments |
| H-006 | `research_oos / pre_wp_5b / d2_006_gates`; `research_oos / pre_wp_5b / exp_success_criteria` | 3 each | H-006 checkpoint; `REC-0017`, `REC-0035`, `REC-0037`; `REC-0006`, `REC-0036`, `REC-0038`; `v_reconciliation_candidate_pipeline_summary`; `v_reconciliation_overview` | closed as complete-as-built for selected exact segments |

## F. R1/R2 Status

R1/R2 methodology remains committed and forward-applicable.

A2C-001 reached completion under the strict pattern before further R1/R2
exercise was needed.

This is not a defect, rollback, or unused-methodology claim.

Future cohorts may use R1/R2 if separately authorized and eligible.

## G. Post-Closure Direction Options

Neutral options for Main/Karl/user:

1. Path B architecture discussion / authorization consideration.
2. A2C-002 or future cohort authorization.
3. AUTO bridge implementation authorization.
4. Approval/readiness discussion with explicit criteria.
5. Phase 3 architecture sketch / transition-gate analysis.
6. Bounded repo-maintenance / operating-model work.
7. Hold / pause.

No option is selected by this package.

## H. What Is Locked

This package locks only:

- A2C-001 cohort phase is formally closed as complete-as-built.
- H-001/H-005/H-006 exact-segment REC-5 floor status is recorded as closure
  basis.
- SS-D-3 cohort-phase closure precondition is satisfied for future decision
  consideration.
- No H-005/H-006 evidence packages remain necessary inside A2C-001 under
  current repo truth.
- AUTO remains paused/non-canonical.
- Path B remains unauthorized until separately selected.
- Post-closure direction remains Main/Karl/user decision.

## I. What Is Not Authorized

This package does not authorize:

- Path B;
- A2C-002;
- a new cohort definition;
- H-011 first-time inclusion;
- H-012+ registration;
- candidate, selected-candidate, or cohort approval;
- approval, readiness, lifecycle, promotion, or demotion;
- broad floor crossing for Phase 3 transition;
- policy, scoring, ranking, recommendation, or evidence-quality scoring;
- downstream authority;
- REP, OL, REC, EXP, lifecycle, registry, query, or trial-log artifacts;
- schema, validator, central query-layer, or canonical-corpus changes;
- config, dependency, data, helper, implementation, or test changes;
- runtime, paper/live, OMS, risk, safe-mode, exchange, broker, order, or
  execution behavior;
- AUTO bridge implementation or AUTO output canonicalization.

## J. Main/Karl Re-Engagement Requirement

Mandatory Main/Karl/user re-engagement is required after merge.

Side must not draft another WP until Main/Karl/user selects the post-closure
direction.

The next decision is post-closure direction, not evidence production.

## K. Validation

Actual validation results for WP-12da / WP-S2c-59:

- `git diff --check`: passed with no output.
- Pre-staging changed-file scope:
  - `git diff --name-only`: `docs/project_status.md`; the new closure
    decision document was untracked at that point.
  - `git status --short`: `M docs/project_status.md`,
    `?? .codex/environments/`, and
    `?? docs/research_pipeline/2026-05-a2c001_cohort_phase_closure_decision.md`.
  - `git ls-files --others --exclude-standard`:
    `.codex/environments/environment.toml` and
    `docs/research_pipeline/2026-05-a2c001_cohort_phase_closure_decision.md`.
  - `.codex/environments/environment.toml` was pre-existing local Codex app
    material and was not staged.
- `tools/dev/diff_scope_summary.py --allowed-file docs/project_status.md
  --allowed-file
  docs/research_pipeline/2026-05-a2c001_cohort_phase_closure_decision.md
  --json`: exited `ok`; it reported no forbidden matches, the expected
  tracked change to `docs/project_status.md`, the expected untracked closure
  decision document, no trial-log touch, and the pre-existing untracked
  `.codex/environments/environment.toml` as an allowed-file violation.
- `python -m tools.research_query.run --list-views`: passed and listed 55
  query views.
- `v_integrity_*`: clean (24); every discovered integrity view ran with JSON
  output and returned `[]`.
- Exact count verification used `v_reconciliation_candidate_pipeline_summary`
  and confirmed:
  - `H-001 / research_oos / pre_wp_5b / d2_006_gates = 3`.
  - `H-001 / research_oos / pre_wp_5b / exp_success_criteria = 3`.
  - `H-005 / research_oos / pre_wp_5b / d2_006_gates = 3`.
  - `H-005 / research_oos / pre_wp_5b / exp_success_criteria = 3`.
  - `H-006 / research_oos / pre_wp_5b / d2_006_gates = 3`.
  - `H-006 / research_oos / pre_wp_5b / exp_success_criteria = 3`.
- REC set verification used `v_reconciliation_overview` and confirmed:
  - H-001 `d2_006_gates`: `REC-0012`, `REC-0027`, `REC-0028`.
  - H-001 `exp_success_criteria`: `REC-0001`, `REC-0029`, `REC-0030`.
  - H-005 `d2_006_gates`: `REC-0013`, `REC-0031`, `REC-0032`.
  - H-005 `exp_success_criteria`: `REC-0002`, `REC-0033`, `REC-0034`.
  - H-006 `d2_006_gates`: `REC-0017`, `REC-0035`, `REC-0037`.
  - H-006 `exp_success_criteria`: `REC-0006`, `REC-0036`, `REC-0038`.
- Candidate registry posture verification used `v_candidate_overview` and
  direct registry inspection. H-001, H-005, and H-006 each have status
  `CONCLUDED`, overall verdict `NO-GO`, and pipeline stage `baseline_tested`;
  H-011 remains `DRAFT` / `PENDING`; no H-012+ entry exists.
- `tests/test_research_query_experiment_views.py` is absent from current
  tracked repo truth. No test file was created or modified.
- Registry validators: all 14 `tools/registry/validate_*.py` modules passed.
- Targeted query tests:
  `.\.venv\Scripts\python.exe -m pytest tests/test_research_query_outcome_ledger_views.py tests/test_research_query_reconciliation_views.py -q`
  passed with 19 passed.
- Helper tests:
  `.\.venv\Scripts\python.exe -m pytest tests/test_diff_scope_summary.py tests/test_validation_summary.py tests/test_code_index.py tests/test_status_snapshot.py -q`
  passed with 61 passed.
- Scoped regression:
  `.\.venv\Scripts\python.exe -m pytest tests -q -k "registry or research_query or reconciliation or outcome_ledger or lifecycle or experiment or diff_scope_summary or validation_summary or code_index or status_snapshot"`
  passed with 303 passed and 314 deselected.
- Full pytest:
  `.\.venv\Scripts\python.exe -m pytest -q`
  passed with 617 passed and 4 warnings.
