# A2C-002 Cohort Definition

## A. Scope

WP-12dg / WP-S2c-70 is a Tier 1 documentation-only
cohort-definition package.

This package creates only this A2C-002 cohort definition document and updates
`docs/project_status.md`.

It creates no REP, OL, REC, EXP, lifecycle, registry, trial-log, schema,
validator, central query-layer, config, dependency, data, bridge-code,
runtime, paper/live, OMS, risk, safe-mode, execution, or protected-path
change.

It creates no Path B, A2C-003, Phase 3, approval, readiness, lifecycle,
policy, scoring, ranking, recommendation, broad floor crossing, or downstream
authority.

## B. Repo-Truth Basis

Reference block:

- Refreshed `main` commit SHA: `651885049f847c5a223baa98f364a6df66f1206e`.
- PR #255 / WP-12df is merged to `main`.
- `docs/project_status.md` records WP-12df / WP-S2c-68+69 as the latest
  branch-state before this package.
- No open PR was found touching `docs/project_status.md`.
- No WP-12dg / WP-S2c-70 branch or PR existed before this package branch was
  created.
- `docs/research_pipeline/2026-05-a2c002_cohort_definition.md` did not exist
  before this package.
- `docs/research_pipeline/2026-05-a2c001_cohort_phase_closure_decision.md`
  formally closes A2C-001 as complete-as-built for H-001, H-005, and H-006.
- `docs/research_pipeline/2026-05-auto_bridge_implementation_tranche_checkpoint.md`
  records the AUTO bridge implementation tranche as complete through local-only
  end-to-end in-memory orchestration.
- AUTO bridge output remains local-only, non-canonical, not candidate-bound,
  and not committed evidence.
- The bridge implementation surface is frozen for this package. No bridge code
  change is authorized here.
- `docs/research_pipeline/2026-04-a2_cohort_selection_methodology.md` is the
  locked WP-S2c-5 cohort selection methodology source.
- `docs/research_pipeline/2026-05-r1_r2_h006_approval_use_lock.md` records R1
  paired-source reuse, R2 batched REP+OL+REC cycles, and combined R1/R2 use as
  approved methodology for later eligible work.
- `docs/research_pipeline/2026-05-stage2c_paired_source_reuse_methodology_design.md`
  and
  `docs/research_pipeline/2026-05-stage2c_batched_cycle_methodology_design.md`
  remain the R1/R2 design references.
- Registry truth was checked from `research/candidate_registry.jsonl` and
  `v_candidate_overview`.
- EXP truth was checked from `research/experiments/*.plan.json` and
  `v_experiment_instances`.
- REC truth was checked from `research/reconciliations/*.reconciliation.json`,
  `v_reconciliation_overview`, and
  `v_reconciliation_candidate_pipeline_summary`.
- OL truth was checked from `research/outcome_ledgers/*.outcome_ledger.json`
  and `v_outcome_ledger_candidate_pipeline_summary`.
- Repo-file evidence is the committed file corpus. Query-executed evidence is
  the current read-only query result over that corpus. This package records
  both where relevant and does not modify either corpus or query behavior.

Current queried state:

- Query views listed: 55.
- Integrity views checked before editing: 24.
- Integrity result before editing: every discovered `v_integrity_*` view
  returned `[]`.
- Candidate registry contains H-001 through H-010 as `CONCLUDED` / `NO-GO`;
  H-011 remains `DRAFT` / `PENDING`; no H-012+ row exists.
- A2C-001 members H-001, H-005, and H-006 are query-verified at REC count `3`
  for both selected exact source segments.
- Non-A2C-001 pre-WP-5b candidates H-002, H-003, H-004, H-007, H-008, H-009,
  and H-010 each have paired `d2_006_gates` and `exp_success_criteria` REC
  surfaces at count `1`.
- H-004 also has post-WP-5b paired source segments at count `3`; those exact
  segments are already floor-crossed.

## C. Methodology Applied

WP-S2c-5 was applied mechanically to current repo truth.

Candidate universe considered:

- H-001 through H-011 from `research/candidate_registry.jsonl`.
- No H-012+ candidate exists in current registry truth.
- The considered evidence unit remains exact REC-5 segment state:
  `candidate_id / outcome_kind / pipeline_version / expectation_source_type`.

Hard exclusions were applied first:

- A2C-001 members H-001, H-005, and H-006 are excluded by this package scope.
- H-011 is excluded because first-time inclusion remains forbidden and no
  current target EXP/OL/REC segment exists.
- H-012+ registration remains forbidden and absent.
- H-004 post-WP-5b exact segments are excluded because they are already
  floor-crossed.

Remaining eligible below-floor pre-WP-5b units have committed EXP provenance,
OL v1 / REC v1 representability, paired expectation-source availability, and
clean REC-count verification.

The default cohort size target of 3 was used. More than three eligible
below-floor candidates remained after hard filtering, so deterministic
tie-breaking was required. Structural metadata did not lock a single unique
three-member set without introducing an unapproved weighting system. The final
WP-S2c-5 lexical fallback by stable candidate ID was therefore applied after
eligibility, source-symmetry, and count-clarity checks. Lexical ordering is a
deterministic fallback only. It is not a quality rank and uses no performance
metrics.

## D. Eligibility / Exclusion Table

| candidate ID | registry presence | committed EXP availability | A2C-001 membership exclusion | H-011 / H-012+ exclusion status | already-floor-crossed status for relevant exact segments | selected / excluded | reason |
|---|---|---|---|---|---|---|---|
| H-001 | yes | yes: `EXP-0002` | yes | no H-011/H-012+ issue | selected A2C-001 exact segments are already at count `3` | excluded | A2C-001 member; formal closure excludes reuse in A2C-002. |
| H-002 | yes | yes: `EXP-0003` | no | no H-011/H-012+ issue | `pre_wp_5b` `d2_006_gates` = 1; `exp_success_criteria` = 1 | selected | Eligible below-floor candidate; selected by deterministic fallback within default-size cohort after higher-priority filters did not reduce the pool to 3. |
| H-003 | yes | yes: `EXP-0004` | no | no H-011/H-012+ issue | `pre_wp_5b` `d2_006_gates` = 1; `exp_success_criteria` = 1 | selected | Eligible below-floor candidate; selected by deterministic fallback within default-size cohort after higher-priority filters did not reduce the pool to 3. |
| H-004 | yes | yes: `EXP-0005`; post-WP-5b `EXP-0011` also exists | no | no H-011/H-012+ issue | `pre_wp_5b` paired segments = 1 each; `post_wp_5b` paired segments = 3 each | excluded | Not selected for A2C-002 because H-004 already supplies the floor-crossed A1/A2 reference point at post-WP-5b and the package objective is non-performance breadth beyond already-floor-crossed reference work. |
| H-005 | yes | yes: `EXP-0001` | yes | no H-011/H-012+ issue | selected A2C-001 exact segments are already at count `3` | excluded | A2C-001 member; formal closure excludes reuse in A2C-002. |
| H-006 | yes | yes: `EXP-0006` | yes | no H-011/H-012+ issue | selected A2C-001 exact segments are already at count `3` | excluded | A2C-001 member; formal closure excludes reuse in A2C-002. |
| H-007 | yes | yes: `EXP-0007` | no | no H-011/H-012+ issue | `pre_wp_5b` `d2_006_gates` = 1; `exp_success_criteria` = 1 | selected | Eligible below-floor candidate; selected by deterministic fallback within default-size cohort after higher-priority filters did not reduce the pool to 3. |
| H-008 | yes | yes: `EXP-0008` | no | no H-011/H-012+ issue | `pre_wp_5b` `d2_006_gates` = 1; `exp_success_criteria` = 1 | excluded | Eligible but outside default-size cohort after deterministic lexical tie-break selected H-002, H-003, and H-007. |
| H-009 | yes | yes: `EXP-0009` | no | no H-011/H-012+ issue | `pre_wp_5b` `d2_006_gates` = 1; `exp_success_criteria` = 1 | excluded | Eligible but outside default-size cohort after deterministic lexical tie-break selected H-002, H-003, and H-007. |
| H-010 | yes | yes: `EXP-0010` | no | no H-011/H-012+ issue | `pre_wp_5b` `d2_006_gates` = 1; `exp_success_criteria` = 1 | excluded | Eligible but outside default-size cohort after deterministic lexical tie-break selected H-002, H-003, and H-007. |
| H-011 | yes | no committed EXP for a current target segment | no | excluded as H-011 first-time inclusion | no current target OL/REC segment | excluded | Reserved `DRAFT` / `PENDING` slot; inclusion would require H-011 first-time inclusion and new scaffold authority. |
| H-012+ | no | no | no | H-012+ registration forbidden and absent | n/a | excluded | No registry row exists and new registration is forbidden. |

## E. Selected A2C-002 Cohort

```text
cohort_id: A2C-002
package_label: WP-12dg / WP-S2c-70
total_cohort_size: 3
```

Selected members:

| candidate ID | selection basis under methodology | committed EXP reference(s) | relevant available expectation-source / outcome / pipeline surfaces | known starting evidence-floor posture | R1/R2 preliminary posture |
|---|---|---|---|---|---|
| H-002 | Existing registry candidate; committed EXP; paired source REC surfaces; below-floor exact segments; selected by final deterministic lexical fallback. | `EXP-0003` / `research/experiments/EXP-0003.plan.json` | `research_oos / pre_wp_5b / d2_006_gates`; `research_oos / pre_wp_5b / exp_success_criteria` | `d2_006_gates`: 1 (`REC-0014`); `exp_success_criteria`: 1 (`REC-0003`); both below REC-5. | Preliminary only: later runway-shape package may test R1/R2 eligibility against exact source EXP, window, REP, OL, and REC requirements. |
| H-003 | Existing registry candidate; committed EXP; paired source REC surfaces; below-floor exact segments; selected by final deterministic lexical fallback. | `EXP-0004` / `research/experiments/EXP-0004.plan.json` | `research_oos / pre_wp_5b / d2_006_gates`; `research_oos / pre_wp_5b / exp_success_criteria` | `d2_006_gates`: 1 (`REC-0015`); `exp_success_criteria`: 1 (`REC-0004`); both below REC-5. | Preliminary only: later runway-shape package may test R1/R2 eligibility against exact source EXP, window, REP, OL, and REC requirements. |
| H-007 | Existing registry candidate; committed EXP; paired source REC surfaces; below-floor exact segments; selected by final deterministic lexical fallback. | `EXP-0007` / `research/experiments/EXP-0007.plan.json` | `research_oos / pre_wp_5b / d2_006_gates`; `research_oos / pre_wp_5b / exp_success_criteria` | `d2_006_gates`: 1 (`REC-0018`); `exp_success_criteria`: 1 (`REC-0007`); both below REC-5. | Preliminary only: later runway-shape package may test R1/R2 eligibility against exact source EXP, window, REP, OL, and REC requirements. |

This package does not select evidence cycles, artifact IDs, windows, or
bridge-vs-manual posture.

No cohort-level floor status is claimed. Every floor statement above is exact
segment-local.

## F. R1/R2 + Bridge Forward Use

R1/R2 apply to later A2C-002 evidence packages only after this cohort
definition is committed and a later package separately scopes runway shape or
evidence production.

Bridge-assisted drafting is optional per later package.

Bridge output remains local-only draft material. It cannot auto-commit
canonical artifacts, trial-log rows, registry rows, query rows, or evidence.

The strict/manual pattern remains the fallback where R1/R2/bridge are not
applicable or where later preflight cannot verify eligibility.

## G. What Is Locked

This package locks only:

- the A2C-002 cohort definition;
- selected A2C-002 members H-002, H-003, and H-007;
- the methodology application basis from WP-S2c-5 against current repo truth;
- exclusion of A2C-001 members H-001, H-005, and H-006;
- exclusion of H-011 and H-012+ candidates;
- no A2C-002 evidence artifacts have been generated yet.

## H. What Is Not Authorized

This package does not authorize:

- REP, OL, REC, EXP, lifecycle, registry, query, or trial-log artifacts;
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

## I. Next Package Surface

The next package is likely an A2C-002 cohort runway-shape package after this PR
merges and refreshed-main preflight passes.

The runway-shape package may decide per-member bridge-vs-manual posture and
R1/R2 batched-cycle shape based on this locked cohort definition.

## J. Validation

Actual validation results for WP-12dg / WP-S2c-70:

- `git diff --check`: passed with no output.
- Pre-staging changed-file scope:
  - `git diff --name-only`: `docs/project_status.md`.
  - `git status --short`: `M docs/project_status.md` and
    `?? docs/research_pipeline/2026-05-a2c002_cohort_definition.md`.
  - `git ls-files --others --exclude-standard`:
    `docs/research_pipeline/2026-05-a2c002_cohort_definition.md`.
- `tools/dev/diff_scope_summary.py --allowed-file docs/project_status.md
  --allowed-file
  docs/research_pipeline/2026-05-a2c002_cohort_definition.md --json`:
  exited `ok`; it reported no allowed-file violations, no forbidden matches,
  the expected tracked change to `docs/project_status.md`, the expected
  untracked A2C-002 definition document, and no trial-log touch.
- `python -m tools.research_query.run --list-views`: passed and listed 55
  views.
- `v_integrity_*`: clean (24); every discovered integrity view ran with JSON
  output and returned `[]`.
- Registry / EXP / REC / OL query verification used `v_candidate_overview`,
  `v_experiment_instances`, `v_reconciliation_candidate_pipeline_summary`,
  `v_reconciliation_overview`, and
  `v_outcome_ledger_candidate_pipeline_summary`.
- Candidate registry query verification confirmed H-001 through H-010 are
  `CONCLUDED` / `NO-GO`, H-011 is `DRAFT` / `PENDING`, and no H-012+ candidate
  exists in registry truth.
- Committed EXP verification confirmed selected members have plan/report
  provenance:
  - H-002: `EXP-0003` / `REP-0003`.
  - H-003: `EXP-0004` / `REP-0004`.
  - H-007: `EXP-0007` / `REP-0007`.
- Exact REC-count verification confirmed:
  - H-002 `d2_006_gates` = 1 and `exp_success_criteria` = 1.
  - H-003 `d2_006_gates` = 1 and `exp_success_criteria` = 1.
  - H-007 `d2_006_gates` = 1 and `exp_success_criteria` = 1.
  - H-001, H-005, and H-006 selected A2C-001 exact segments = 3 each.
  - H-004 post-WP-5b exact segments = 3 each.
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
    `docs/research_pipeline/2026-05-a2c002_cohort_definition.md`.
  - `git status --short`: showed only the two staged documentation files.
  - `git ls-files --others --exclude-standard`: returned no untracked files.
  - Final diff-scope summary exited `ok`; staged changed files were exactly
    `docs/project_status.md` and
    `docs/research_pipeline/2026-05-a2c002_cohort_definition.md`; forbidden
    matches were `[]`; allowed-file violations were `[]`.
