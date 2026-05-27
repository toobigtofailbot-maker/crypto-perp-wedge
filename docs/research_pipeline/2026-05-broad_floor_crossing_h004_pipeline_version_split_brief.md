# Broad-Floor-Crossing H-004 Pipeline-Version Split Brief

## 1. Scope

WP-S2c-84 is the H-004 pipeline-version split surface inside bundled WP-12dt /
WP-S2c-83+84.

This is a Tier 1 documentation-only consumer brief. It creates no REP, OL,
REC, EXP, lifecycle, registry, trial-log, schema, validator, central
query-layer, bridge-code, bridge-output, config, dependency, data, runtime,
paper/live, OMS, risk, safe-mode, execution, or protected-path change.

The brief enumerates H-004 floor-crossed exact segments by `pipeline_version`
and preserves pre-WP-5b and post-WP-5b as structurally separate surfaces.

## 2. Repo-Truth Basis

Reference block:

- Refreshed `main` is at `eadd9fb`, the WP-12ds / WP-S2c-82 merge commit.
- PR #268 / WP-12ds is merged.
- `docs/project_status.md` records WP-12ds / WP-S2c-82 as the latest
  branch-state before this package.
- `v_reconciliation_candidate_pipeline_summary` confirms H-004 has four
  floor-crossed exact segments at REC count `3`.
- `v_reconciliation_overview` provides REC artifact traceability for the H-004
  rows.
- H-004 pre-WP-5b selected A2C-002 rows and H-004 post-WP-5b Track F /
  historical rows remain separate by `pipeline_version`.
- No post-WP-12ds research artifact diff was found on the package base.
- Path B, A2C-003, Phase 3, approval/readiness/lifecycle,
  policy/scoring/ranking/recommendation, broad-floor-crossing decision,
  runtime, bridge further work, and downstream authority remain unauthorized.

## 3. Corrected H-004 Split Basis

The corrected repo-truth basis includes four H-004 floor-crossed exact
segments:

- two selected A2C-002 pre-WP-5b rows;
- two post-WP-5b Track F / historical rows.

The two H-004 post-WP-5b rows are included in the all-repo 14 inventory and
excluded from the 12 selected closed-runway subset.

The split is structural only. It does not compare, score, rank, or reinterpret
H-004 evidence across pipeline versions.

## 4. Locked Pipeline-Version Discipline

H-004 pre-WP-5b and post-WP-5b exact segments must not be merged.

The exact-segment key remains:

```text
candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

Changing `pipeline_version` changes the exact segment. H-004 having two
floor-crossed pipeline-version surfaces does not create candidate approval,
readiness, lifecycle, policy, scoring, ranking, recommendation, runtime, or
downstream authority.

## 5. H-004 Floor-Crossed Segment Inventory

| candidate_id | outcome_kind | pipeline_version | expectation_source_type | floor_count | floor_status | trace_rec_ids | origin_class | selected_closed_runway_subset | separation_note |
|---|---|---|---|---:|---|---|---|---|---|
| H-004 | research_oos | post_wp_5b | d2_006_gates | 3 | REC-5 floor met | REC-0022, REC-0023, REC-0024 | H-004 post-WP-5b Track F / historical surface | no | Separate post-WP-5b surface; included in all-repo 14 and excluded from selected closed-runway 12. |
| H-004 | research_oos | post_wp_5b | exp_success_criteria | 3 | REC-5 floor met | REC-0011, REC-0025, REC-0026 | H-004 post-WP-5b Track F / historical surface | no | Separate post-WP-5b surface; included in all-repo 14 and excluded from selected closed-runway 12. |
| H-004 | research_oos | pre_wp_5b | d2_006_gates | 3 | REC-5 floor met | REC-0016, REC-0047, REC-0049 | A2C-002 selected closed runway | yes | Separate pre-WP-5b selected A2C-002 surface. |
| H-004 | research_oos | pre_wp_5b | exp_success_criteria | 3 | REC-5 floor met | REC-0005, REC-0048, REC-0050 | A2C-002 selected closed runway | yes | Separate pre-WP-5b selected A2C-002 surface. |

## 6. Pre-WP-5b Structural Surface

H-004 pre-WP-5b floor-crossed rows are:

- `H-004 / research_oos / pre_wp_5b / d2_006_gates`
- `H-004 / research_oos / pre_wp_5b / exp_success_criteria`

These rows are A2C-002 selected closed-runway rows. They are part of the 12
selected closed-runway subset and part of the 14 all-repo inventory.

This is a structural origin fact only.

## 7. Post-WP-5b Structural Surface

H-004 post-WP-5b floor-crossed rows are:

- `H-004 / research_oos / post_wp_5b / d2_006_gates`
- `H-004 / research_oos / post_wp_5b / exp_success_criteria`

These rows are H-004 post-WP-5b Track F / historical rows. They are part of
the 14 all-repo inventory and outside the 12 selected closed-runway subset.

This is a structural origin fact only.

## 8. Separation Rules

H-004 pre-WP-5b and post-WP-5b rows must remain separate by
`pipeline_version`.

The post-WP-5b rows must not be used to satisfy, replace, reinterpret, or
amend selected A2C-002 pre-WP-5b evidence.

The pre-WP-5b rows must not be used to reinterpret the post-WP-5b Track F /
historical surface.

The two surfaces must not be merged, compared, scored, ranked, or used for
performance-based claims.

## 9. What Is Not Inferred

This brief does not infer:

- H-004 approval, readiness, lifecycle completion, promotion, demotion, or
  archive action;
- broad floor crossing achieved or not achieved;
- Phase 3 sufficiency;
- Path B authorization;
- A2C-003 authorization;
- Phase 3 authorization;
- policy, scoring, ranking, recommendation, or evidence-quality scoring;
- comparative performance between H-004 pre-WP-5b and post-WP-5b evidence;
- cross-segment inference;
- bridge effectiveness;
- AUTO bridge canonical-write-path design;
- runtime, paper/live, OMS, risk, safe-mode, execution, or downstream
  authority.

## 10. Next Surface

This split brief pairs with WP-S2c-83, the combined-cohort enumeration brief.

After merge, Side may continue to WP-S2c-85+86 bundled expectation-source
coverage and tranche checkpoint under Main's authorized tranche only after
refreshed-main preflight, unless a stop trigger fires.

## 11. Validation

Validation basis for this brief:

- Query/count verification confirmed H-004 has four floor-crossed exact
  segments at REC count `3`.
- Query/count verification confirmed two H-004 pre-WP-5b selected A2C-002 rows
  and two H-004 post-WP-5b Track F / historical rows.
- `v_reconciliation_overview` confirmed the REC trace IDs listed in this
  brief.
- H-004 pre-WP-5b and post-WP-5b rows remain structurally separate by
  `pipeline_version`.
- Package validation is execution validation only and creates no new artifact,
  query, validator, schema, test, runtime, bridge, or downstream authority.
