# A2C-002 Runway Shape

## A. Scope

WP-12dh / WP-S2c-71 is a Tier 1 documentation-only runway-shape package.

This package creates only this A2C-002 runway-shape document and updates
`docs/project_status.md`.

It creates no REP, OL, REC, EXP, lifecycle, registry, trial-log, schema,
validator, central query-layer, config, dependency, data, bridge-code,
bridge-output, runtime, paper/live, OMS, risk, safe-mode, execution, or
protected-path change.

It creates no Path B, A2C-003, Phase 3, approval, readiness, lifecycle,
policy, scoring, ranking, recommendation, broad floor crossing, or downstream
authority.

## B. Repo-Truth Basis

Reference block:

- Refreshed `main` commit SHA:
  `7452229ca32761b5ed31c94b0b1bdd6ded19e5c4`.
- PR #256 / WP-12dg is merged to `main`.
- `docs/project_status.md` records WP-12dg / WP-S2c-70 as the latest
  branch-state before this package.
- No open PR was found touching `docs/project_status.md`.
- No WP-12dh / WP-S2c-71 branch or PR existed before this package branch was
  created.
- `docs/research_pipeline/2026-05-a2c002_runway_shape.md` did not exist before
  this package.
- `docs/research_pipeline/2026-05-a2c002_cohort_definition.md` locks A2C-002
  as H-002, H-003, and H-004.
- `docs/research_pipeline/2026-05-a2c001_cohort_phase_closure_decision.md`
  formally closes A2C-001 as complete-as-built for H-001, H-005, and H-006.
- `docs/research_pipeline/2026-05-auto_bridge_implementation_tranche_checkpoint.md`
  records the AUTO bridge implementation tranche as complete through local-only
  end-to-end in-memory orchestration.
- AUTO bridge output remains local-only, non-canonical, not candidate-bound,
  and not committed evidence.
- The bridge implementation surface is frozen for this package. No bridge code
  change is authorized here.
- `docs/research_pipeline/2026-05-r1_r2_h006_approval_use_lock.md` records R1
  paired-source reuse, R2 batched REP+OL+REC cycles, and combined R1/R2 use as
  approved methodology for H-006 onward and later eligible work.
- `docs/research_pipeline/2026-05-stage2c_paired_source_reuse_methodology_design.md`
  and
  `docs/research_pipeline/2026-05-stage2c_batched_cycle_methodology_design.md`
  remain the R1/R2 design references.
- Registry truth was checked from `research/candidate_registry.jsonl` and
  `v_candidate_overview`.
- EXP truth was checked from `research/experiments/*.plan.json`,
  `research/experiments/*.report.json`, and `v_experiment_instances`.
- REC truth was checked from `research/reconciliations/*.reconciliation.json`,
  `v_reconciliation_overview`, and
  `v_reconciliation_candidate_pipeline_summary`.
- OL truth was checked from `research/outcome_ledgers/*.outcome_ledger.json`,
  `v_outcome_ledger_overview`, and
  `v_outcome_ledger_candidate_pipeline_summary`.
- Repo-file evidence is the committed file corpus. Query-executed evidence is
  the current read-only query result over that corpus. This package records
  both where relevant and does not modify either corpus or query behavior.

Current queried state:

- Query views listed: 55.
- Integrity views checked before editing: 24.
- Integrity result before editing: every discovered `v_integrity_*` view
  returned `[]`.
- Candidate registry contains H-002, H-003, and H-004 as `CONCLUDED` /
  `NO-GO`.
- H-002 has committed `EXP-0003` / `REP-0003` provenance.
- H-003 has committed `EXP-0004` / `REP-0004` provenance.
- H-004 pre-WP-5b has committed `EXP-0005` / `REP-0005` provenance.
- H-002, H-003, and H-004 each have paired selected pre-WP-5b REC surfaces:
  `research_oos / pre_wp_5b / d2_006_gates` and
  `research_oos / pre_wp_5b / exp_success_criteria`.
- Each selected exact segment currently has REC count `1`.
- H-004 also has post-WP-5b paired exact segments at count `3`; those segments
  are not selected for A2C-002 runway work.
- No `research/experiments`, `research/outcome_ledgers`,
  `research/reconciliations`, or `research/trial_log.jsonl` file change exists
  after the WP-12dg merge commit on this package base.

## C. Selected Cohort Recap

| member | committed EXP / REP reference | selected exact source segments | starting REC count | target floor count |
|---|---|---|---:|---:|
| H-002 | `EXP-0003` / `REP-0003` | `research_oos / pre_wp_5b / d2_006_gates`; `research_oos / pre_wp_5b / exp_success_criteria` | 1 each | 3 each |
| H-003 | `EXP-0004` / `REP-0004` | `research_oos / pre_wp_5b / d2_006_gates`; `research_oos / pre_wp_5b / exp_success_criteria` | 1 each | 3 each |
| H-004 | `EXP-0005` / `REP-0005` for the selected pre-WP-5b unit | `research_oos / pre_wp_5b / d2_006_gates`; `research_oos / pre_wp_5b / exp_success_criteria` | 1 each | 3 each |

The target floor remains exact-segment-local. No cohort-level, candidate-level,
or broad floor-crossing claim is made here.

## D. Runway Shape Summary

| member | selected exact segments | starting count | required additional cycles | planned cycle labels | intended package pattern | expected checkpoint after completion |
|---|---|---:|---:|---|---|---|
| H-002 | `d2_006_gates`; `exp_success_criteria` under `research_oos / pre_wp_5b` | 1 each | 2 | H-002 cycle 1; H-002 cycle 2 | one atomic REP+OL+two-REC package per cycle if R1/R2 eligibility holds; strict/manual fallback if not | H-002 completion checkpoint |
| H-003 | `d2_006_gates`; `exp_success_criteria` under `research_oos / pre_wp_5b` | 1 each | 2 | H-003 cycle 1; H-003 cycle 2 | one atomic REP+OL+two-REC package per cycle if R1/R2 eligibility holds; strict/manual fallback if not | H-003 completion checkpoint |
| H-004 | `d2_006_gates`; `exp_success_criteria` under `research_oos / pre_wp_5b` | 1 each | 2 | H-004 cycle 1; H-004 cycle 2 | one atomic REP+OL+two-REC package per cycle if R1/R2 eligibility holds; strict/manual fallback if not | H-004 completion checkpoint |

Expected logical package sequence:

- WP-S2c-72: H-002 cycle 1.
- WP-S2c-73: H-002 cycle 2.
- WP-S2c-74: H-002 completion checkpoint.
- WP-S2c-75: H-003 cycle 1.
- WP-S2c-76: H-003 cycle 2.
- WP-S2c-77: H-003 completion checkpoint.
- WP-S2c-78: H-004 cycle 1.
- WP-S2c-79: H-004 cycle 2.
- WP-S2c-80: H-004 completion checkpoint.
- WP-S2c-81: A2C-002 cohort-completion checkpoint.
- WP-S2c-82: A2C-002 cohort-phase closure decision, with mandatory
  Main/Karl/user re-engagement after closure report-back.

These are planned logical cycle labels and package surfaces, not future
artifact IDs. Future packages must recompute actual REP, OL, REC, trial-log,
window, and count state from refreshed repo truth.

## E. Per-Member Cycle Shape

### H-002

- Cycle 1 expected movement: selected exact segments move from count `1` to
  count `2`.
- Cycle 2 expected movement: selected exact segments move from count `2` to
  count `3` / REC-5 floor.
- Intended R1 shape: one OL reused across the two expectation-source RECs,
  subject to later eligibility verification for same candidate, same EXP
  provenance, same outcome kind, same pipeline version, same evaluation
  window, same actual bar window when present, same data/config lineage, same
  source REP, same source OL, and no REC conflict.
- Intended R2 shape: one atomic REP+OL+two-REC package per cycle, subject to
  later eligibility verification and full validation.
- Strict/manual fallback: if R1 or R2 cannot apply cleanly, future packages
  must stop and use only separately authorized strict/manual artifact
  discipline.

### H-003

- Cycle 1 expected movement: selected exact segments move from count `1` to
  count `2`.
- Cycle 2 expected movement: selected exact segments move from count `2` to
  count `3` / REC-5 floor.
- Intended R1 shape: one OL reused across the two expectation-source RECs,
  subject to later eligibility verification for same candidate, same EXP
  provenance, same outcome kind, same pipeline version, same evaluation
  window, same actual bar window when present, same data/config lineage, same
  source REP, same source OL, and no REC conflict.
- Intended R2 shape: one atomic REP+OL+two-REC package per cycle, subject to
  later eligibility verification and full validation.
- Strict/manual fallback: if R1 or R2 cannot apply cleanly, future packages
  must stop and use only separately authorized strict/manual artifact
  discipline.

### H-004

- Cycle 1 expected movement: selected pre-WP-5b exact segments move from count
  `1` to count `2`.
- Cycle 2 expected movement: selected pre-WP-5b exact segments move from count
  `2` to count `3` / REC-5 floor.
- Intended R1 shape: one OL reused across the two expectation-source RECs,
  subject to later eligibility verification for same candidate, same selected
  pre-WP-5b EXP provenance, same outcome kind, same pipeline version, same
  evaluation window, same actual bar window when present, same data/config
  lineage, same source REP, same source OL, and no REC conflict.
- Intended R2 shape: one atomic REP+OL+two-REC package per cycle, subject to
  later eligibility verification and full validation.
- Strict/manual fallback: if R1 or R2 cannot apply cleanly, future packages
  must stop and use only separately authorized strict/manual artifact
  discipline.

H-004's post-WP-5b floor-crossed segments are not part of this selected runway
and do not satisfy or replace the selected pre-WP-5b counts.

## F. Bridge / Manual Posture

| member | preliminary posture | reason | future-cycle preflight required | package action now |
|---|---|---|---|---|
| H-002 | bridge-eligible preliminary | selected member has committed EXP/REP provenance, paired pre-WP-5b source shape, count `1` exact segments, and no observed repo-truth bridge blocker | yes | no bridge invocation |
| H-003 | bridge-eligible preliminary | selected member has committed EXP/REP provenance, paired pre-WP-5b source shape, count `1` exact segments, and no observed repo-truth bridge blocker | yes | no bridge invocation |
| H-004 | bridge-eligible preliminary | selected pre-WP-5b member unit has committed EXP/REP provenance, paired pre-WP-5b source shape, count `1` exact segments, and no observed repo-truth bridge blocker; post-WP-5b evidence remains separate | yes | no bridge invocation |

Bridge-assisted drafting is optional planning support for later cycle packages
only. Bridge output remains local-only draft material. Canonical artifacts in
later packages must be authored and committed through normal per-artifact
discipline. Bridge output cannot bypass schema, validator, trial-log, REC, OL,
REP, query, integrity, or exact changed-file validation.

Bridge code is frozen under this tranche. If a later bridge-assisted cycle
cannot produce canonical-validation-passing artifacts without bridge
modification, Side must stop and report rather than modify bridge code.

## G. Validation / Stop Conditions For Future Cycle Packages

Future A2C-002 cycle packages must stop if any of the following occurs:

- selected member or selected exact segment mismatch;
- missing EXP/REP provenance;
- unable to verify starting REC count;
- REC-5 floor count cannot be verified as `3`;
- R1 ineligible and strict fallback also blocked;
- R2 ineligible and per-artifact fallback also blocked;
- bridge draft cannot support canonical-validation-passing artifacts without
  bridge modification;
- canonical schema versioning need;
- validator, central query-layer, bridge-code, config, dependency, data, or
  protected-path change needed;
- trial-log inconsistency;
- any integrity view rows;
- performance-based interpretation pressure;
- Path B, A2C-003, Phase 3, runtime, approval, readiness, lifecycle,
  policy, scoring, ranking, recommendation, broad floor crossing, or
  downstream authority pressure.

## H. What Is Locked

This package locks only:

- A2C-002 runway shape;
- selected member order: H-002, H-003, then H-004, unless future repo truth
  forces a stop;
- selected exact segments:
  `research_oos / pre_wp_5b / d2_006_gates` and
  `research_oos / pre_wp_5b / exp_success_criteria`;
- expected two-cycle per-member path from count `1` to count `3`;
- intended R1/R2 planning posture for future eligible cycle packages;
- preliminary bridge-eligible planning posture for later optional
  bridge-assisted drafting;
- no evidence artifacts generated yet.

## I. What Is Not Authorized

This package does not authorize:

- REP, OL, REC, EXP, lifecycle, registry, query, or trial-log artifacts;
- bridge invocation;
- bridge output writing;
- bridge code changes;
- bridge output canonicalization;
- schema changes;
- validator changes;
- central query-layer changes;
- config, dependency, data, runtime, paper/live, OMS, risk, safe-mode,
  exchange, broker, order, execution, or protected-path changes;
- Path B;
- A2C-003;
- Phase 3;
- approval, readiness, lifecycle, promotion, or demotion;
- policy, scoring, ranking, recommendation, or evidence-quality scoring;
- broad floor crossing;
- downstream authority.

## J. Next Package Surface

The next package is likely the A2C-002 H-002 cycle 1 canonical artifact
package after this PR merges and refreshed-main preflight passes.

The next package may use CS8 atomic cycle discipline and optional
bridge-assisted draft production only if future preflight confirms R1/R2 and
bridge posture eligibility. It must recompute selected member state, exact
counts, windows, artifact IDs, trial-log state, integrity state, and changed
file scope from refreshed repo truth.

## K. Validation

Actual validation results for WP-12dh / WP-S2c-71:

- `git diff --check`: passed with no output.
- Pre-staging changed-file scope:
  - `git diff --name-only`: `docs/project_status.md`; the new runway-shape
    document was untracked at that point.
  - `git status --short`: `M docs/project_status.md` and
    `?? docs/research_pipeline/2026-05-a2c002_runway_shape.md`.
  - `git ls-files --others --exclude-standard`:
    `docs/research_pipeline/2026-05-a2c002_runway_shape.md`.
- `tools/dev/diff_scope_summary.py --allowed-file docs/project_status.md
  --allowed-file docs/research_pipeline/2026-05-a2c002_runway_shape.md
  --json`: exited `ok`; it reported no allowed-file violations, no forbidden
  matches, the expected tracked change to `docs/project_status.md`, the
  expected untracked runway-shape document, and no trial-log touch.
- `python -m tools.research_query.run --list-views`: passed and listed 55
  views.
- `v_integrity_*`: clean (24); every discovered integrity view ran with JSON
  output and returned `[]`.
- Registry / EXP / REC / OL query verification used `v_candidate_overview`,
  `v_experiment_instances`, `v_reconciliation_candidate_pipeline_summary`,
  `v_reconciliation_overview`, and
  `v_outcome_ledger_candidate_pipeline_summary`.
- Candidate registry query verification confirmed:
  - H-002: `CONCLUDED` / `NO-GO`, `trend_following`, `4h`.
  - H-003: `CONCLUDED` / `NO-GO`, `mean_reversion`, `1d`.
  - H-004: `CONCLUDED` / `NO-GO`, `trend_following`, `1d`.
- Committed EXP verification confirmed selected members have plan/report
  provenance:
  - H-002: `EXP-0003` / `REP-0003`.
  - H-003: `EXP-0004` / `REP-0004`.
  - H-004 pre-WP-5b: `EXP-0005` / `REP-0005`.
- Exact REC-count verification confirmed:
  - H-002 `d2_006_gates` = 1 and `exp_success_criteria` = 1.
  - H-003 `d2_006_gates` = 1 and `exp_success_criteria` = 1.
  - H-004 pre-WP-5b `d2_006_gates` = 1 and `exp_success_criteria` = 1.
  - H-004 post-WP-5b exact segments = 3 each and are not selected here.
- REC-5 floor verification confirmed
  `docs/research_pipeline/2026-04-reconciliation_artifact.md` and
  `docs/research_pipeline/2026-04-rec_v1_stability.md` retain the
  `n >= 3` exact-segment floor; A2C-001 selected exact segments query at
  count `3`.
- No post-WP-12dg research artifact or trial-log file change was found by
  `git diff --name-only 7452229ca32761b5ed31c94b0b1bdd6ded19e5c4..HEAD --
  research/experiments research/outcome_ledgers research/reconciliations
  research/trial_log.jsonl`.
- AUTO bridge implementation surface verification confirmed
  `tools/research_automation/bridge/` contains the frozen intake, transform,
  validate, candidate-artifact, and orchestrate modules.
- `tests/test_research_query_experiment_views.py` is absent from current
  tracked repo truth. No test file was created.
- Registry validators:
  `Get-ChildItem tools/registry -Filter "validate_*.py" | ForEach-Object {
  .\.venv\Scripts\python.exe -m ("tools.registry." + $_.BaseName) }`
  passed for all 14 validators.
- Targeted query tests:
  `.\.venv\Scripts\python.exe -m pytest
  tests/test_research_query_outcome_ledger_views.py
  tests/test_research_query_reconciliation_views.py -q`
  passed with 19 passed.
- Helper tests:
  `.\.venv\Scripts\python.exe -m pytest tests/test_diff_scope_summary.py
  tests/test_validation_summary.py tests/test_code_index.py
  tests/test_status_snapshot.py -q`
  passed with 61 passed.
- Bridge tests:
  `.\.venv\Scripts\python.exe -m pytest
  tests/research_automation/test_bridge_intake.py
  tests/research_automation/test_bridge_transform.py
  tests/research_automation/test_bridge_validate.py
  tests/research_automation/test_bridge_candidate_artifact.py
  tests/research_automation/test_bridge_orchestrate.py -q`
  passed with 116 passed.
- Scoped regression:
  `.\.venv\Scripts\python.exe -m pytest tests -q -k "research_automation or
  registry or research_query or reconciliation or outcome_ledger or lifecycle
  or experiment or diff_scope_summary or validation_summary or code_index or
  status_snapshot"` passed with 520 passed and 213 deselected.
- Full pytest:
  `.\.venv\Scripts\python.exe -m pytest -q` passed with 733 passed and 4
  warnings.
- Staged checks:
  - `git diff --cached --check`: passed with no output.
  - `git diff --cached --name-only`: returned exactly
    `docs/project_status.md` and
    `docs/research_pipeline/2026-05-a2c002_runway_shape.md`.
  - `git status --short`: showed only the two staged documentation files.
  - `git ls-files --others --exclude-standard`: returned no untracked files.
  - Final diff-scope summary exited `ok`; staged changed files were exactly
    `docs/project_status.md` and
    `docs/research_pipeline/2026-05-a2c002_runway_shape.md`; forbidden matches
    were `[]`; allowed-file violations were `[]`.
