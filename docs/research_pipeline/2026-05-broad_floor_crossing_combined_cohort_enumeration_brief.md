# Broad-Floor-Crossing Combined-Cohort Enumeration Brief

## 1. Scope

WP-S2c-83 is the combined-cohort floor-crossing enumeration surface inside
bundled WP-12dt / WP-S2c-83+84.

This is a Tier 1 documentation-only consumer brief. It creates no REP, OL,
REC, EXP, lifecycle, registry, trial-log, schema, validator, central
query-layer, bridge-code, bridge-output, config, dependency, data, runtime,
paper/live, OMS, risk, safe-mode, execution, or protected-path change.

The brief enumerates current all-repo floor-crossed exact segments using the
locked REC-5 exact-segment discipline:

```text
candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

It records structural inventory facts only. It does not decide whether broad
floor crossing is achieved or not achieved. It does not assess Phase 3
sufficiency or create downstream authority.

## 2. Repo-Truth Basis

Reference block:

- Refreshed `main` is at `eadd9fb`, the WP-12ds / WP-S2c-82 merge commit.
- PR #268 / WP-12ds is merged.
- `docs/project_status.md` records WP-12ds / WP-S2c-82 as the latest
  branch-state before this package.
- A2C-001 cohort phase is closed by
  `docs/research_pipeline/2026-05-a2c001_cohort_phase_closure_decision.md`.
- A2C-002 cohort phase is closed by
  `docs/research_pipeline/2026-05-a2c002_cohort_phase_closure_decision.md`.
- A2C-002 cohort-completion and cohort-phase closure checkpoints exist.
- `v_reconciliation_candidate_pipeline_summary`, grouped by
  `candidate_id / outcome_kind / pipeline_version /
  expectation_source_type` with `COUNT(*) >= 3`, returns 14 floor-crossed
  exact segments across six candidates.
- `v_reconciliation_overview` provides the REC artifact traceability recorded
  below.
- No post-WP-12ds research artifact diff was found on the package base.
- Path B, A2C-003, Phase 3, approval/readiness/lifecycle,
  policy/scoring/ranking/recommendation, broad-floor-crossing decision,
  runtime, bridge further work, and downstream authority remain unauthorized.

## 3. Corrected 14/12/2 Interpretation Basis

The prior nine-segment premise was stale. Repo-truth diagnostic corrected the
basis to:

- 14 all-repo floor-crossed exact segments across six candidates;
- 12 selected closed-runway exact segments;
- 2 separate H-004 post-WP-5b Track F / historical exact segments.

The 14 all-repo row count is a structural inventory fact only. The 12 selected
closed-runway row count is a structural subset fact only.

The two H-004 post-WP-5b rows are included in the all-repo inventory and
excluded from the selected closed-runway subset.

## 4. Locked Interpretation Discipline

REC-5 floor remains `n >= 3` per exact segment only.

Exact-segment floor state does not merge candidates, cohorts, expectation
sources, pipeline versions, lifecycle states, approval states, or future
decision surfaces.

This brief does not rank, score, compare, recommend, infer evidence quality,
or make cross-segment or cross-cohort interpretive claims. A2C-001-origin and
A2C-002-origin rows are separated only as structural origin facts.

## 5. All-Repo Floor-Crossed Exact-Segment Inventory

| candidate_id | outcome_kind | pipeline_version | expectation_source_type | floor_count | floor_status | trace_rec_ids | origin_class |
|---|---|---|---|---:|---|---|---|
| H-001 | research_oos | pre_wp_5b | d2_006_gates | 3 | REC-5 floor met | REC-0012, REC-0027, REC-0028 | A2C-001 selected closed runway |
| H-001 | research_oos | pre_wp_5b | exp_success_criteria | 3 | REC-5 floor met | REC-0001, REC-0029, REC-0030 | A2C-001 selected closed runway |
| H-002 | research_oos | pre_wp_5b | d2_006_gates | 3 | REC-5 floor met | REC-0014, REC-0039, REC-0041 | A2C-002 selected closed runway |
| H-002 | research_oos | pre_wp_5b | exp_success_criteria | 3 | REC-5 floor met | REC-0003, REC-0040, REC-0042 | A2C-002 selected closed runway |
| H-003 | research_oos | pre_wp_5b | d2_006_gates | 3 | REC-5 floor met | REC-0015, REC-0043, REC-0045 | A2C-002 selected closed runway |
| H-003 | research_oos | pre_wp_5b | exp_success_criteria | 3 | REC-5 floor met | REC-0004, REC-0044, REC-0046 | A2C-002 selected closed runway |
| H-004 | research_oos | post_wp_5b | d2_006_gates | 3 | REC-5 floor met | REC-0022, REC-0023, REC-0024 | H-004 post-WP-5b Track F / historical surface |
| H-004 | research_oos | post_wp_5b | exp_success_criteria | 3 | REC-5 floor met | REC-0011, REC-0025, REC-0026 | H-004 post-WP-5b Track F / historical surface |
| H-004 | research_oos | pre_wp_5b | d2_006_gates | 3 | REC-5 floor met | REC-0016, REC-0047, REC-0049 | A2C-002 selected closed runway |
| H-004 | research_oos | pre_wp_5b | exp_success_criteria | 3 | REC-5 floor met | REC-0005, REC-0048, REC-0050 | A2C-002 selected closed runway |
| H-005 | research_oos | pre_wp_5b | d2_006_gates | 3 | REC-5 floor met | REC-0013, REC-0031, REC-0032 | A2C-001 selected closed runway |
| H-005 | research_oos | pre_wp_5b | exp_success_criteria | 3 | REC-5 floor met | REC-0002, REC-0033, REC-0034 | A2C-001 selected closed runway |
| H-006 | research_oos | pre_wp_5b | d2_006_gates | 3 | REC-5 floor met | REC-0017, REC-0035, REC-0037 | A2C-001 selected closed runway |
| H-006 | research_oos | pre_wp_5b | exp_success_criteria | 3 | REC-5 floor met | REC-0006, REC-0036, REC-0038 | A2C-001 selected closed runway |

## 6. Selected Closed-Runway Subset

| basis | exact_segment_count | candidate_count | included_origin_classes | excluded_origin_classes | interpretation_status |
|---|---:|---:|---|---|---|
| all-repo floor-crossed inventory | 14 | 6 | A2C-001 selected + A2C-002 selected + H-004 post-WP-5b Track F | none | structural inventory only |
| selected closed-runway subset | 12 | 6 | A2C-001 selected + A2C-002 selected | H-004 post-WP-5b Track F | structural subset only |

The selected closed-runway subset consists of six A2C-001 rows and six A2C-002
rows. The two non-selected all-repo additional rows are H-004 post-WP-5b Track
F / historical rows.

## 7. Candidate Coverage Inventory

Six candidates appear in the all-repo floor-crossed exact-segment inventory:

- H-001
- H-002
- H-003
- H-004
- H-005
- H-006

H-004 appears under two separate `pipeline_version` values:

- `pre_wp_5b`, as A2C-002 selected closed-runway rows;
- `post_wp_5b`, as Track F / historical rows outside the selected
  closed-runway subset.

## 8. Cohort-Origin Inventory

Structural origin facts:

- A2C-001 selected closed-runway rows: H-001, H-005, and H-006, two exact
  segments each, six rows total.
- A2C-002 selected closed-runway rows: H-002, H-003, and H-004 pre-WP-5b, two
  exact segments each, six rows total.
- H-004 post-WP-5b Track F / historical rows: H-004 post-WP-5b, two exact
  segments total.

These origin labels do not create cross-cohort comparative inference.

## 9. Structural Observations

Fact: current repo truth contains 14 all-repo floor-crossed exact segments
across six candidates.

Fact: 12 of those rows are selected closed-runway exact segments from closed
A2C-001 and A2C-002 cohort phases.

Fact: the remaining two rows are separate H-004 post-WP-5b Track F /
historical exact segments.

Fact: every row in the inventory is at REC count `3`.

Fact: H-004 pre-WP-5b and post-WP-5b floor states remain separate by
`pipeline_version`.

## 10. What Is Not Inferred

This brief does not infer:

- broad floor crossing achieved or not achieved;
- Phase 3 sufficiency;
- Path B authorization;
- A2C-003 authorization;
- Phase 3 authorization;
- candidate approval, readiness, lifecycle completion, promotion, demotion, or
  archive action;
- policy, scoring, ranking, recommendation, or evidence-quality scoring;
- cross-segment inference;
- cross-cohort A2C-001 versus A2C-002 comparative inference;
- H-004 pre-WP-5b versus post-WP-5b comparative inference;
- bridge effectiveness;
- AUTO bridge canonical-write-path design;
- runtime, paper/live, OMS, risk, safe-mode, execution, or downstream
  authority.

## 11. Next Surface

The paired surface in this bundled package is WP-S2c-84, the H-004
pipeline-version split consumer brief.

After merge, Side may continue to WP-S2c-85+86 bundled expectation-source
coverage and tranche checkpoint under Main's authorized tranche only after
refreshed-main preflight, unless a stop trigger fires.

## 12. Validation

Validation basis for this brief:

- Query/count verification confirmed 14 all-repo floor-crossed exact segments
  across six candidates.
- Query/count verification confirmed 12 selected closed-runway exact segments:
  six A2C-001 selected rows and six A2C-002 selected rows.
- Query/count verification confirmed two additional H-004 post-WP-5b Track F /
  historical rows.
- `v_reconciliation_overview` confirmed the REC trace IDs listed in this
  brief.
- H-004 pre-WP-5b and post-WP-5b rows remain structurally separate by
  `pipeline_version`.
- Package validation is execution validation only and creates no new artifact,
  query, validator, schema, test, runtime, bridge, or downstream authority.
