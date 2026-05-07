# Candidate-Selection Eligibility Matrix Brief (WP-10k)

## 1. Purpose

WP-10k is a read-only documentation/query-consumer package after the WP-10j
candidate-selection rule design. It applies the WP-10j eligibility rules to
current repo-truth query surfaces and emits a descriptive eligibility matrix.

WP-10k does not select candidates for execution, rank candidates, score
candidates, recommend strategies, promote or demote candidates, create cohorts
for execution, create EXP, REP, OL, or REC artifacts, satisfy REC-5, implement
policy, add paper/live semantics, or touch runtime, deployment, OMS, risk,
safe-mode, execution, configs, dependencies, or protected paths.

## 2. Inputs

The package consumes these existing repo-truth surfaces:

- WP-10j candidate-selection rule design:
  `docs/research_pipeline/2026-04-candidate_selection_rule_design.md`.
- Candidate registry overview from `v_candidate_overview`.
- REC overview and segment summary from `v_reconciliation_overview` and
  `v_reconciliation_candidate_pipeline_summary`.
- OL overview and segment summary from `v_outcome_ledger_overview` and
  `v_outcome_ledger_candidate_pipeline_summary`.
- Lifecycle overview and transitions from `v_lifecycle_change_overview` and
  `v_lifecycle_state_transitions`.
- Validator and integrity-view results from the current branch.

The package-local reproducibility assets are:

- Query bundle:
  `research/briefs/2026-04-candidate_selection_eligibility_matrix/queries/`
- Output bundle:
  `research/briefs/2026-04-candidate_selection_eligibility_matrix/outputs/`
- Runner:
  `research/briefs/2026-04-candidate_selection_eligibility_matrix/run_all_queries.py`

## 3. Current machine state

The refreshed branch state records:

- WP-10j is merged and recorded in `docs/project_status.md`.
- `docs/research_pipeline/2026-04-candidate_selection_rule_design.md` exists.
- REC corpus is `REC-0001` through `REC-0022`.
- REC row count is 22.
- REC expectation-source distribution is 11 `exp_success_criteria` rows and
  11 `d2_006_gates` rows.
- Every current REC-5 segment has `reconciliation_count = 1`.
- OL corpus is `OL-0001` through `OL-0011`.
- OL row count is 11.
- Candidate registry overview exposes `H-001` through `H-011`.
- OL and REC coverage covers `H-001` through `H-010`.
- `H-011` has registry presence but no current OL/REC coverage.
- Lifecycle overview has 30 rows, with transition counts 10 / 10 / 10.
- H-004 remains structurally split under both expectation sources.
- `REC-0012`, `REC-0017`, and `REC-0019` skip D2 cost-drag comparison when
  `gross_pnl <= 0`.
- No D2 non-positive-gross-PnL anomaly remains.

## 4. Eligibility matrix summary

`Q03` emits the hard eligibility gate matrix. For current REC-backed target
segments, the matrix preserves the WP-10j target segment identity:

```text
candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

Every current REC-backed segment is marked
`eligible_for_future_evidence_planning` because the candidate exists in the
registry, lifecycle provenance exists, OL/REC target evidence exists, the
target segment is identifiable, the segment remains below REC-5, and no
forbidden scope is required for descriptive future evidence planning.

`H-011` is marked `not_applicable` with
`no_current_ol_rec_target_segment` because it has registry presence but no
current OL/REC target segment. This does not demote H-011 or select another
candidate; it only records current evidence-surface absence.

## 5. REC-5 gap summary

`Q02` records one row per current REC-5 segment. All current segments have:

```text
reconciliation_count = 1
rec5_target = 3
additional_observations_needed = 2
rec5_status = BELOW_FLOOR
```

WP-10k does not satisfy REC-5. It does not combine expectation sources,
pipeline versions, or H-004 split rows to satisfy REC-5.

## 6. H-004/separation summary

`Q05` records the four current H-004 REC rows:

```text
REC-0005 / OL-0005 / H-004 / pre_wp_5b / exp_success_criteria
REC-0011 / OL-0011 / H-004 / post_wp_5b / exp_success_criteria
REC-0016 / OL-0005 / H-004 / pre_wp_5b / d2_006_gates
REC-0022 / OL-0011 / H-004 / post_wp_5b / d2_006_gates
```

Each row has `combined_for_rec5 = false` and
`comparison_claim_supported = false`. The H-004 split remains structural only;
WP-10k makes no improvement, degradation, pre/post performance comparison,
ranking, recommendation, policy, paper/live, or runtime claim.

## 7. Forbidden output confirmation

`Q06` records that these output fields are forbidden and excluded from WP-10k
outputs:

```text
rank
score
recommendation
promotion_status
paper_live_readiness
policy_action
runtime_action
```

The WP-10k matrix uses only the allowed descriptive fields from WP-10j and does
not create policy, scoring, ranking, paper/live, or runtime authority.

## 8. Next package boundary

WP-10k supports only descriptive candidate-selection eligibility matrix /
rule-application posture and evidence-generation architecture detail as future
bounded package classes.

WP-10k does not authorize EXP planning without Main 3.0 approval and does not
authorize policy, scoring, ranking, paper/live, runtime, deployment, OMS, risk,
safe-mode, execution, config, dependency, or protected-path work.

## 9. Validation snapshot

Validation for this package includes:

- Core validators:
  `validate_registry`, `validate_reconciliations`, `validate_outcome_ledger`,
  and `validate_lifecycle_changes`.
- All existing `tools.registry.validate_*` validators used in recent packages.
- Required central query views:
  `v_candidate_overview`, `v_reconciliation_overview`,
  `v_reconciliation_candidate_pipeline_summary`,
  `v_outcome_ledger_overview`,
  `v_outcome_ledger_candidate_pipeline_summary`,
  `v_lifecycle_change_overview`, and `v_lifecycle_state_transitions`.
- All discovered `v_integrity_*` views, expected `[]`.
- Package-local query regeneration twice, expected deterministic output.
- Targeted pytest selection, full pytest, `git diff --check`, and final
  changed-file inspection.

## 10. Non-claims

WP-10k does not create:

- candidate selection;
- candidate ranking or recommendation;
- EXP, REP, OL, or REC artifacts;
- REC-5 satisfaction;
- policy;
- promotion or demotion;
- paper/live semantics;
- evidence-quality scoring;
- schema;
- validator;
- query-layer view;
- runtime, deployment, OMS, risk, safe-mode, or execution authority;
- protected-path authority.
