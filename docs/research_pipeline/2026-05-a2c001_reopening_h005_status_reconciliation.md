# A2C-001 Reopening Record + H-005 Remaining-Work Status Reconciliation

## A. Scope

WP-12cy / WP-S2c-57 is docs-only.

This package records Track F reopening authority and reconciles H-005
remaining-work status only. It is Phase 1 of the reopened A2C-001 track.

This package:

- does not produce REP, OL, or REC artifacts;
- does not append to `research/trial_log.jsonl`;
- does not complete H-005;
- does not start H-006;
- does not claim A2C-001 completion or cohort-phase closure;
- does not authorize Path B;
- does not modify schemas, validators, central query-layer views, canonical
  corpus artifacts, configs, dependencies, data, runtime, or protected paths;
- does not create policy/scoring/ranking/recommendation,
  approval/readiness/lifecycle, or downstream authority.

Committed file scope is only:

- `docs/research_pipeline/2026-05-a2c001_reopening_h005_status_reconciliation.md`
- `docs/project_status.md`

## B. Verified Repo-Truth Inputs

Repo-file evidence and direct inspection:

- PR #247 / WP-12cx is merged to `main` at merge commit
  `b6c59d3`.
- Refreshed `main` includes WP-12cx before this package branch was created.
- `docs/project_status.md` records WP-12cx / WP-S2c-56 as the latest
  branch-state.
- `docs/project_status.md` records WP-12cx as docs-only, creating
  `docs/research_pipeline/2026-05-auto_bridge_design_tranche_checkpoint.md`
  and updating `docs/project_status.md` only.
- WP-12cx summarizes the completed AUTO bridge design tranche from WP-12cr
  through WP-12cw; records implementation remains unauthorized; records no
  post-checkpoint track was selected by that package; asks Main/Karl/user to
  decide whether to stop/defer, continue design, authorize implementation,
  redirect, or keep paused; asks Main for a one-sentence whole-project WP
  estimate; preserves the WP-12ct, WP-12cu, WP-12cv, and WP-12cw locks; does
  not implement the bridge; does not reactivate AUTO; does not make AUTO
  outputs canonical; does not reopen A2C-001; does not authorize Path B; does
  not create approval/readiness/lifecycle/downstream authority; and requires
  Side to stop and report back for next-track selection after merge.
- Current instruction authority selects Track F: reopen A2C-001 under explicit
  criteria.
- Current instruction authority authorizes WP-S2c-57 as Phase 1 track
  reopening plus H-005 status reconciliation.
- Current instruction authority requires mandatory Main re-engagement after
  WP-S2c-57 report-back before any Phase 2 H-005 evidence work.
- No open PR was found touching `docs/project_status.md`.
- No WP-12cy / WP-S2c-57 branch or PR existed before this package branch was
  created.
- This document did not exist before this package.

A2C-001 stop/defer repo-file evidence:

- `docs/research_pipeline/2026-05-a2c001_deferral_no_approval_decision_lock.md`
  records A2C-001 as not approved, not ready, and not lifecycle-complete.
- `docs/research_pipeline/2026-05-a2c001_post_deferral_closeout_index.md`
  records post-deferral closeout/archive state and states future movement
  requires explicit separate authorization.
- `docs/research_pipeline/2026-05-a2c001_stop_defer_hold_lock.md` records
  A2C-001 in stop/defer hold with no active next A2C-001 execution track.
- `docs/research_pipeline/2026-05-post_a2c_active_track_selection_gate.md`
  records no active post-A2C substantive execution track and no A2C-001
  reopen.
- `docs/research_pipeline/2026-05-post_a2c_lessons_decision_review.md`
  preserves the stop/defer hold and does not select a next substantive track.

A2C-001 cohort definition from repo truth:

- A2C-001 selected members remain H-001, H-005, and H-006.
- H-011 is not included as an A2C-001 member.
- No H-012+ registration exists in `research/candidate_registry.jsonl`.
- This package does not modify the candidate registry.

Candidate registry direct inspection:

| candidate_id | status | overall_verdict | strategy_family | timeframe | pipeline_stage |
|---|---|---|---|---|---|
| H-001 | CONCLUDED | NO-GO | funding_directional | 4h | baseline_tested |
| H-005 | CONCLUDED | NO-GO | momentum | 1h | baseline_tested |
| H-006 | CONCLUDED | NO-GO | breakout | 30m | baseline_tested |
| H-011 | DRAFT | PENDING | cross_asset_regime | weekly | reserved |

H-001, H-005, and H-006 status from repo truth:

- H-001 checkpoint:
  `docs/research_pipeline/2026-04-a2c001_h001_first_member_runway_checkpoint.md`
  records both selected exact segments at count `3`.
- H-005 checkpoint:
  `docs/research_pipeline/2026-05-a2c001_h005_runway_checkpoint.md` records
  both selected exact segments at count `3`.
- H-006 checkpoint:
  `docs/research_pipeline/2026-05-a2c001_h006_runway_checkpoint.md` records
  both selected exact segments at count `3`.

Query-executed evidence:

```text
H-001 / research_oos / pre_wp_5b / d2_006_gates = 3
H-001 / research_oos / pre_wp_5b / exp_success_criteria = 3
H-005 / research_oos / pre_wp_5b / d2_006_gates = 3
H-005 / research_oos / pre_wp_5b / exp_success_criteria = 3
H-006 / research_oos / pre_wp_5b / d2_006_gates = 3
H-006 / research_oos / pre_wp_5b / exp_success_criteria = 3
```

Query-executed REC sets:

```text
H-001 d2_006_gates: REC-0012, REC-0027, REC-0028
H-001 exp_success_criteria: REC-0001, REC-0029, REC-0030
H-005 d2_006_gates: REC-0013, REC-0031, REC-0032
H-005 exp_success_criteria: REC-0002, REC-0033, REC-0034
H-006 d2_006_gates: REC-0017, REC-0035, REC-0037
H-006 exp_success_criteria: REC-0006, REC-0036, REC-0038
```

AUTO and Path B repo-file evidence:

- WP-12cx records AUTO remains paused, local-only, research-only,
  non-authoritative, and non-canonical.
- `docs/research_pipeline/2026-05-auto_bridge_retroactivity_posture.md`
  records existing pre-bridge AUTO outputs as permanently non-canonical and
  not eligible for retroactive canonical transformation.
- `docs/research_pipeline/2026-05-auto_bridge_provenance_canonical_target_design.md`
  records future-output-only provenance and canonical-target posture as
  design-only.
- `docs/research_pipeline/2026-05-auto_bridge_schema_validator_query_validation_design.md`
  records no schema, validator, or central query-layer authority for AUTO
  bridge work under the current design tranche.
- `docs/research_pipeline/2026-05-auto_bridge_implementation_tranche_boundary.md`
  records an implementation boundary but does not authorize implementation.
- A2C stop/defer and AUTO bridge files preserve Path B as deferred /
  unauthorized.

R1/R2 and H-006 methodology repo-file evidence:

- `docs/research_pipeline/2026-05-stage2c_paired_source_reuse_methodology_design.md`
  designs R1 paired-source reuse and states H-005 remains strict.
- `docs/research_pipeline/2026-05-stage2c_batched_cycle_methodology_design.md`
  designs R2 batched REP+OL+REC cycles and states H-005 remains strict.
- `docs/research_pipeline/2026-05-r1_r2_h006_approval_use_lock.md` approves
  R1, R2, and combined R1+R2 use for H-006 onward when eligibility holds,
  while preserving no approval/readiness/lifecycle, Path B, runtime,
  schema/validator/query-layer, or downstream authority.

Research artifact direct inspection:

- `research/trial_log.jsonl` contains baseline H-005 and H-006 rows plus
  H-005 strict-runway rows for REP-0020 through REP-0023 and H-006 R1+R2 rows
  for REP-0024 and REP-0025.
- H-005 strict-runway artifacts present and inspected include:
  - EXP: `EXP-0001`
  - REP: `REP-0020`, `REP-0021`, `REP-0022`, `REP-0023`
  - OL: `OL-0020`, `OL-0021`, `OL-0022`, `OL-0023`
  - REC: `REC-0031`, `REC-0032`, `REC-0033`, `REC-0034`
- H-006 R1+R2 artifacts present and inspected include:
  - EXP: `EXP-0006`
  - REP: `REP-0024`, `REP-0025`
  - OL: `OL-0024`, `OL-0025`
  - REC: `REC-0035`, `REC-0036`, `REC-0037`, `REC-0038`

Inferred remaining work:

- H-005 strict exact-segment evidence work has no remaining evidence package
  count under current repo truth because both selected exact segments are
  already recorded and query-verified at count `3`.

Unresolved unknown:

- The current instruction brief expected a remaining-H-005 reconciliation
  surface. Current repo truth instead indicates no remaining H-005 strict
  evidence packages are needed. This package records that reconciliation and
  requires Main confirmation before any Phase 2 package is drafted.

## C. Reopening Decision Record

Track F is selected: reopen A2C-001 under explicit criteria.

Reopening is limited to the criteria and boundaries recorded in this document.

A2C-001 was previously stopped/deferred and is now reopened only for the
authorized evidence-track sequence and status-reconciliation decision surface.

Reopening does not erase or modify prior stop/defer records.

Reopening does not claim A2C-001 completion.

Reopening does not claim cohort-phase closure.

Reopening does not authorize Path B.

Reopening does not authorize approval/readiness/lifecycle transition.

Reopening does not authorize runtime, paper-live, OMS, risk, safe-mode, or
implementation work.

Reopening does not authorize AUTO bridge implementation.

Reopening does not authorize schema, validator, or query-layer changes.

## D. A2C-001 Cohort Definition Lock

A2C-001 cohort definition remains locked to H-001, H-005, and H-006.

No member addition, removal, or substitution is authorized.

H-011 first-time inclusion is not authorized.

H-012+ registration is not authorized.

No new cohort definition is authorized.

Candidate registry is not modified.

## E. H-001 Status Snapshot

Current candidate registry status for H-001:

```text
candidate_id = H-001
status = CONCLUDED
overall_verdict = NO-GO
strategy_family = funding_directional
timeframe = 4h
pipeline_stage = baseline_tested
```

Relevant checkpoint/evidence docs:

- `docs/research_pipeline/2026-04-a2c001_h001_first_member_runway_checkpoint.md`
- `docs/research_pipeline/2026-05-a2c001_cohort_interpretation_stability.md`
- `docs/research_pipeline/2026-05-a2c001_post_deferral_closeout_index.md`
- `docs/research_pipeline/2026-05-a2c001_stop_defer_hold_lock.md`

Repo-file and query-executed evidence record:

```text
H-001 / research_oos / pre_wp_5b / d2_006_gates = 3
H-001 / research_oos / pre_wp_5b / exp_success_criteria = 3
```

No H-001 evidence work remains for this reopened track under current repo
truth. This package does not modify H-001 artifacts.

## F. H-005 Status Reconciliation

Last merged H-005 package / WP label from repo truth:

- WP-12cf / WP-S2c-38 created
  `docs/research_pipeline/2026-05-a2c001_h005_runway_checkpoint.md`.
- That checkpoint records the current committed H-005 strict exact-segment
  runway state inside A2C-001.

H-005 artifact and segment state:

| segment | repo-file REC set | query count | floor status |
|---|---|---:|---|
| `H-005 / research_oos / pre_wp_5b / d2_006_gates` | `REC-0013`, `REC-0031`, `REC-0032` | 3 | floor reached |
| `H-005 / research_oos / pre_wp_5b / exp_success_criteria` | `REC-0002`, `REC-0033`, `REC-0034` | 3 | floor reached |

Last H-005 strict-runway IDs:

- Last H-005 REP: `REP-0023`.
- Last H-005 OL: `OL-0023`.
- Last H-005 REC: `REC-0034`.

H-005 strict-runway status:

- Repo-file evidence says H-005 has reached the selected exact-segment floor
  for both selected expectation-source segments.
- Query-executed evidence independently returned both H-005 selected exact
  segments at `reconciliation_count = 3`.
- No H-005 package appears partial, in-flight, or uncommitted from current
  repo truth.

Supporting H-005 docs/artifacts:

- `docs/research_pipeline/2026-05-a2c001_h005_runway_checkpoint.md`
- `research/experiments/EXP-0001.plan.json`
- `research/experiments/REP-0020.report.json`
- `research/experiments/REP-0021.report.json`
- `research/experiments/REP-0022.report.json`
- `research/experiments/REP-0023.report.json`
- `research/outcome_ledgers/OL-0020.outcome_ledger.json`
- `research/outcome_ledgers/OL-0021.outcome_ledger.json`
- `research/outcome_ledgers/OL-0022.outcome_ledger.json`
- `research/outcome_ledgers/OL-0023.outcome_ledger.json`
- `research/reconciliations/REC-0031.reconciliation.json`
- `research/reconciliations/REC-0032.reconciliation.json`
- `research/reconciliations/REC-0033.reconciliation.json`
- `research/reconciliations/REC-0034.reconciliation.json`
- H-005 rows in `research/trial_log.jsonl`.

Remaining H-005 strict-pattern work:

- No additional H-005 strict REP/OL/REC evidence packages are determinable as
  remaining from current repo truth.
- The only remaining H-005-related work before further sequencing is mandatory
  Main confirmation of this Phase 1 reconciliation.
- If Main believes H-005 remaining evidence work still exists, the discrepancy
  must be resolved before Phase 2 is drafted.

## G. H-005 Remaining-Work Plan Surface

If Main later identifies remaining H-005 work, H-005 continues under the
original strict pattern only.

R1/R2 does not apply to H-005 unless later explicitly authorized.

The next H-005 evidence package must not be drafted until Main confirms this
Phase 1 status reconciliation.

No tentative next REP/OL/REC IDs are listed because current repo truth
indicates no H-005 strict evidence packages remain.

Any future H-005 IDs must be recomputed from refreshed repo truth before
evidence execution.

No REP/OL/REC artifacts are created in this package.

No trial-log rows are appended in this package.

## H. H-006 Runway Authorization Surface

H-006 later uses the approved R1+R2 methodology only if eligible under repo
truth at execution time.

R1+R2 for H-006 must preserve paired-source reuse, batched-cycle methodology,
atomic artifact validation, independent REC verdicts, cost-drag-skip behavior
where applicable, and no silent fallback.

H-006 does not start in this package.

Repo truth already contains an H-006 checkpoint recording both selected H-006
exact segments at count `3`; any later H-006 package count is a planning
estimate only until refreshed repo truth and Main authority are confirmed.

H-006 cannot create candidate approval, A2C-001 completion, cohort-phase
closure, Path B, approval/readiness/lifecycle, or downstream authority.

## I. Reopened Track Sequencing

Planning envelope only:

Phase 1:

- WP-S2c-57 / current package: reopening + H-005 status reconciliation.
- Mandatory Main re-engagement after report-back.

Phase 2:

- H-005 strict completion packages only if Main confirms a repo-truth H-005
  gap after this reconciliation.
- No R1/R2 for H-005 under current authority.

Phase 3:

- H-005 checkpoint package only if Main confirms further H-005 strict
  completion work and that work lands.

Phase 4:

- H-006 R1+R2 runway only if refreshed repo truth and Main authority show
  further H-006 work is actually needed and eligible.

Phase 5:

- A2C-001 cohort evidence-completion checkpoint / closure-decision surface.
- Mandatory Main/Karl re-engagement.
- Do not call it cohort-phase closure unless separately authorized and
  supported by canonical evidence.

This sequence is not approval, not readiness, not Path B, and not runtime
authority.

## J. Validation And Integrity Expectations

All packages require refreshed-main preflight.

Integrity views must return zero rows at Phase 1 discovery and be restated in
report-back.

Tier 1 packages require full pytest unless explicitly reduced by user/Main/Karl
authority.

Tier 2/3 evidence packages require full pytest, registry validators,
per-artifact validation, trial-log validation if applicable, and zero-row
integrity views after commits.

H-006 R1+R2 packages require atomic artifact discipline: all cycle artifacts
validate or none commit.

No validation discipline is reduced by this package.

## K. Stop Conditions

Stop if:

- H-005 actual stopped-state differs from expected repo truth;
- H-005 counts are ambiguous, conflicting, or not reproducible from repo truth;
- an H-005 package appears partial, in-flight, or uncommitted;
- H-005 remaining work requires schema/validator/query-layer changes;
- H-006 R1/R2 eligibility fails;
- H-006 EXP referenced by future REPs is absent or unsuitable for locked
  methodology;
- paired-source eligibility fails for any H-006 segment;
- batched-cycle artifact ordering surfaces validation problems;
- OL or REC artifact profile requires schema versioning;
- trial-log state conflicts with artifact state;
- A2C-001 cohort definition needs modification;
- Path B, AUTO bridge implementation, runtime, paper/live, protected paths,
  configs, dependencies, data changes, approval/readiness/lifecycle,
  policy/scoring/ranking/recommendation, or downstream authority would be
  needed to land cleanly;
- any integrity view returns rows;
- any registry validator fails;
- any targeted/scoped/full pytest fails.

If any stop condition fires, Codex must stop and report before commit unless
the stop condition is merely recorded as a discovered unresolved status in this
Phase 1 doc and does not require unsafe changes. If unsure, stop before commit.

## L. What This Package Locks

This package locks only:

- Track F reopening is recorded as selected by Main.
- Phase 1 status-reconciliation package was executed.
- A2C-001 reopening is limited to the explicit criteria and boundaries in this
  document.
- H-005 remaining-work status is recorded from repo truth.
- Current repo truth indicates no H-005 strict evidence packages remain before
  Main confirmation.
- Phase 2 H-005 work requires Main confirmation after this report-back.
- A2C-001 cohort remains H-001, H-005, H-006.
- AUTO remains paused and non-canonical.
- Path B remains deferred/unauthorized.
- No implementation/runtime/approval/readiness/lifecycle/downstream authority
  is created.

## M. What Is Not Authorized

This package does not authorize:

- H-005 evidence execution;
- H-005 completion claim;
- H-006 evidence execution;
- H-006 R1/R2 package execution;
- A2C-001 completion;
- cohort-phase closure;
- A2C-001 approval;
- A2C-001 readiness;
- Path B;
- AUTO bridge implementation;
- AUTO output canonicalization;
- runtime;
- paper/live;
- OMS;
- risk;
- safe mode;
- exchange/broker/order/execution behavior;
- config/dependency/data changes;
- schema authority;
- validator authority;
- central query-layer exposure;
- canonical-corpus modification;
- REP/OL/REC artifact creation in this package;
- trial-log append in this package;
- EXP scaffold authoring;
- H-011 first-time inclusion;
- H-012+ registration;
- new cohort definition;
- policy/scoring/ranking/recommendation;
- evidence-quality scoring;
- approval/promotion/demotion/readiness/lifecycle transition authority;
- downstream authority.

## N. Main Re-Engagement Requirement

Mandatory Main re-engagement is required after WP-S2c-57 report-back.

Side must not draft the first Phase 2 H-005 strict-completion evidence package
until Main confirms the H-005 remaining-work status and authorizes Phase 2
continuation from the reconciled repo truth.

If H-005 status is ambiguous or conflicts, Side must ask Main for
clarification rather than drafting Phase 2.

Because current repo truth indicates no H-005 strict evidence work remains,
Side must also ask Main whether Phase 2 is unnecessary, should be replaced by a
different checkpoint/decision surface, or should proceed only after Main
identifies a concrete repo-truth gap.

## O. Validation

Actual validation results for WP-12cy / WP-S2c-57:

- `git diff --check`: passed.
- `git diff --name-only`: returned `docs/project_status.md` before staging;
  the new reconciliation document was still untracked at that point.
- `git status --short`: showed only `docs/project_status.md`, the new
  reconciliation document, and pre-existing untracked
  `.codex/environments/environment.toml`.
- `git ls-files --others --exclude-standard`: showed the new reconciliation
  document and pre-existing untracked `.codex/environments/environment.toml`.
- `tools/dev/diff_scope_summary.py --allowed-file docs/project_status.md
  --allowed-file
  docs/research_pipeline/2026-05-a2c001_reopening_h005_status_reconciliation.md
  --json`: exited `ok`; it reported no forbidden matches, no trial-log touch,
  and the only allowed-file violation was the pre-existing untracked
  `.codex/environments/environment.toml`.
- `python -m tools.research_query.run --list-views`: passed and listed 55
  query views.
- Every discovered `v_integrity_*` view was run with `--json`; all 24 returned
  `[]`.
- Registry validators: all 14 `tools/registry/validate_*.py` modules passed.
- Original package instruction referenced
  `tests/test_research_query_experiment_views.py`; that file is absent from
  current tracked repo truth. No test file was created or modified.
- Corrected available research-query subset:
  `python -m pytest tests/test_research_query_outcome_ledger_views.py
  tests/test_research_query_reconciliation_views.py -q`: `19 passed`.
- Helper tests:
  `python -m pytest tests/test_diff_scope_summary.py
  tests/test_validation_summary.py tests/test_code_index.py
  tests/test_status_snapshot.py -q`: `61 passed`.
- Scoped regression:
  `python -m pytest tests -q -k "registry or research_query or
  reconciliation or outcome_ledger or lifecycle or experiment or
  diff_scope_summary or validation_summary or code_index or status_snapshot"`:
  `303 passed, 314 deselected`.
- Full pytest: `617 passed, 4 warnings`.
