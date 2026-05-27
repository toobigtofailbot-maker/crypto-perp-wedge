# Broad-Floor-Crossing Expectation-Source Coverage Brief

## 1. Scope

WP-S2c-85 is the expectation-source coverage surface inside bundled WP-12du /
WP-S2c-85+86.

This is a Tier 1 documentation-only consumer brief. It creates no REP, OL,
REC, EXP, lifecycle, registry, trial-log, schema, validator, central
query-layer, bridge-code, bridge-output, config, dependency, data, runtime,
paper/live, OMS, risk, safe-mode, execution, or protected-path change.

The brief records structural expectation-source coverage for current
floor-crossed exact segments only. It does not decide whether broad floor
crossing is achieved or not achieved. It does not assess Phase 3 sufficiency
or create downstream authority.

## 2. Repo-Truth Basis

Reference block:

- Refreshed `main` is at `9944ade`, the WP-12dt / WP-S2c-83+84 merge commit.
- PR #269 / WP-12dt is merged.
- `docs/project_status.md` records WP-12dt / WP-S2c-83+84 as the latest
  branch-state before this package.
- `docs/research_pipeline/2026-05-a2c001_cohort_phase_closure_decision.md`
  formally closes A2C-001 as complete-as-built for selected exact segments.
- `docs/research_pipeline/2026-05-a2c002_cohort_phase_closure_decision.md`
  formally closes A2C-002 as complete-as-built for selected exact segments.
- `docs/research_pipeline/2026-05-broad_floor_crossing_combined_cohort_enumeration_brief.md`
  records the corrected 14/12/2 structural inventory basis.
- `docs/research_pipeline/2026-05-broad_floor_crossing_h004_pipeline_version_split_brief.md`
  records H-004 pre-WP-5b and post-WP-5b separation by `pipeline_version`.
- `v_reconciliation_candidate_pipeline_summary`, grouped by
  `candidate_id / outcome_kind / pipeline_version /
  expectation_source_type` with `COUNT(*) >= 3`, confirms 14 floor-crossed
  exact segments across six candidates.
- `v_reconciliation_overview` provides the REC artifact traceability recorded
  below.
- No post-WP-12dt canonical research artifact diff was found on the package
  base.
- Path B, A2C-003, Phase 3, approval/readiness/lifecycle,
  policy/scoring/ranking/recommendation, broad-floor-crossing decision,
  runtime, AUTO bridge canonical-write-path, bridge further work, and
  downstream authority remain unauthorized.

## 3. Corrected 14/12/2 Basis

WP-12dt corrected the structural interpretation basis to:

- 14 all-repo floor-crossed exact segments across six candidates;
- 12 selected closed-runway exact segments;
- 2 separate H-004 post-WP-5b Track F / historical exact segments.

The two H-004 post-WP-5b rows are included in the all-repo inventory and
excluded from the selected closed-runway subset.

This brief consumes that corrected basis and adds only the expectation-source
coverage dimension.

## 4. Locked Expectation-Source Discipline

REC-5 floor remains `n >= 3` per exact segment only.

The exact-segment key remains:

```text
candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

`expectation_source_type` is part of the exact segment key. It must not be
collapsed, merged, ranked, scored, or treated as interchangeable across
`d2_006_gates` and `exp_success_criteria`.

Expectation-source coverage is structural coverage only. It does not compare
source quality, claim source superiority, or support cross-segment inference.

## 5. Expectation-Source Coverage Inventory

| basis | expectation_source_type | exact_segment_count | candidate_count | pipeline_version_coverage | trace_summary | interpretation_status |
|---|---|---:|---:|---|---|---|
| all-repo floor-crossed inventory | d2_006_gates | 7 | 6 | post_wp_5b, pre_wp_5b | H-001, H-002, H-003, H-004 pre-WP-5b, H-004 post-WP-5b, H-005, H-006 | structural coverage only |
| all-repo floor-crossed inventory | exp_success_criteria | 7 | 6 | post_wp_5b, pre_wp_5b | H-001, H-002, H-003, H-004 pre-WP-5b, H-004 post-WP-5b, H-005, H-006 | structural coverage only |
| selected closed-runway subset | d2_006_gates | 6 | 6 | pre_wp_5b | H-001, H-002, H-003, H-004 pre-WP-5b, H-005, H-006 | structural subset only |
| selected closed-runway subset | exp_success_criteria | 6 | 6 | pre_wp_5b | H-001, H-002, H-003, H-004 pre-WP-5b, H-005, H-006 | structural subset only |
| H-004 post-WP-5b Track F / historical surface | d2_006_gates | 1 | 1 | post_wp_5b | H-004 post-WP-5b only | structural separate surface only |
| H-004 post-WP-5b Track F / historical surface | exp_success_criteria | 1 | 1 | post_wp_5b | H-004 post-WP-5b only | structural separate surface only |

## 6. Selected Closed-Runway Coverage

The selected closed-runway subset contains 12 exact segments: six
`d2_006_gates` rows and six `exp_success_criteria` rows.

| candidate_id | pipeline_version | expectation_source_type | floor_count | trace_rec_ids | origin_class | included_in_selected_closed_runway_subset |
|---|---|---|---:|---|---|---|
| H-001 | pre_wp_5b | d2_006_gates | 3 | REC-0012, REC-0027, REC-0028 | A2C-001 selected closed runway | yes |
| H-001 | pre_wp_5b | exp_success_criteria | 3 | REC-0001, REC-0029, REC-0030 | A2C-001 selected closed runway | yes |
| H-002 | pre_wp_5b | d2_006_gates | 3 | REC-0014, REC-0039, REC-0041 | A2C-002 selected closed runway | yes |
| H-002 | pre_wp_5b | exp_success_criteria | 3 | REC-0003, REC-0040, REC-0042 | A2C-002 selected closed runway | yes |
| H-003 | pre_wp_5b | d2_006_gates | 3 | REC-0015, REC-0043, REC-0045 | A2C-002 selected closed runway | yes |
| H-003 | pre_wp_5b | exp_success_criteria | 3 | REC-0004, REC-0044, REC-0046 | A2C-002 selected closed runway | yes |
| H-004 | pre_wp_5b | d2_006_gates | 3 | REC-0016, REC-0047, REC-0049 | A2C-002 selected closed runway | yes |
| H-004 | pre_wp_5b | exp_success_criteria | 3 | REC-0005, REC-0048, REC-0050 | A2C-002 selected closed runway | yes |
| H-005 | pre_wp_5b | d2_006_gates | 3 | REC-0013, REC-0031, REC-0032 | A2C-001 selected closed runway | yes |
| H-005 | pre_wp_5b | exp_success_criteria | 3 | REC-0002, REC-0033, REC-0034 | A2C-001 selected closed runway | yes |
| H-006 | pre_wp_5b | d2_006_gates | 3 | REC-0017, REC-0035, REC-0037 | A2C-001 selected closed runway | yes |
| H-006 | pre_wp_5b | exp_success_criteria | 3 | REC-0006, REC-0036, REC-0038 | A2C-001 selected closed runway | yes |

## 7. H-004 Post-WP-5b Coverage

H-004 post-WP-5b Track F / historical coverage contains two exact segments.
They are part of the all-repo 14 inventory and outside the selected
closed-runway 12 subset.

| candidate_id | pipeline_version | expectation_source_type | floor_count | trace_rec_ids | origin_class | included_in_selected_closed_runway_subset |
|---|---|---|---:|---|---|---|
| H-004 | post_wp_5b | d2_006_gates | 3 | REC-0022, REC-0023, REC-0024 | H-004 post-WP-5b Track F / historical surface | no |
| H-004 | post_wp_5b | exp_success_criteria | 3 | REC-0011, REC-0025, REC-0026 | H-004 post-WP-5b Track F / historical surface | no |

H-004 pre-WP-5b and post-WP-5b states remain separate by `pipeline_version`.

## 8. Structural Observations

Fact: all-repo floor-crossed inventory contains seven `d2_006_gates` rows and
seven `exp_success_criteria` rows.

Fact: selected closed-runway coverage contains six `d2_006_gates` rows and
six `exp_success_criteria` rows.

Fact: H-004 post-WP-5b Track F / historical coverage contains one
`d2_006_gates` row and one `exp_success_criteria` row.

Fact: each listed row is an exact segment at REC count `3`.

Fact: expectation-source coverage symmetry is a structural distribution fact
only. It is not an expectation-source quality comparison.

## 9. What Is Not Inferred

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
- expectation-source quality comparison;
- `d2_006_gates` versus `exp_success_criteria` superiority;
- bridge effectiveness;
- AUTO bridge canonical-write-path design;
- runtime, paper/live, OMS, risk, safe-mode, execution, or downstream
  authority.

## 10. Next Surface

The paired surface in this bundled package is WP-S2c-86, the
broad-floor-crossing interpretation tranche checkpoint.

WP-S2c-86 consumes this expectation-source coverage brief and records the
tranche checkpoint as structural documentation only.

## 11. Validation

Validation basis for this brief:

- Query/count verification confirmed 14 all-repo floor-crossed exact segments
  across six candidates.
- Query/count verification confirmed 12 selected closed-runway exact segments.
- Query/count verification confirmed two H-004 post-WP-5b Track F /
  historical rows.
- Query/count verification confirmed all-repo expectation-source distribution:
  seven `d2_006_gates` rows and seven `exp_success_criteria` rows.
- Query/count verification confirmed selected closed-runway
  expectation-source distribution: six `d2_006_gates` rows and six
  `exp_success_criteria` rows.
- Query/count verification confirmed H-004 post-WP-5b distribution: one
  `d2_006_gates` row and one `exp_success_criteria` row.
- `v_reconciliation_overview` confirmed the REC trace IDs listed in this
  brief.
- H-004 pre-WP-5b and post-WP-5b rows remain structurally separate by
  `pipeline_version`.
- Package validation is execution validation only and creates no new artifact,
  query, validator, schema, test, runtime, bridge, or downstream authority.
