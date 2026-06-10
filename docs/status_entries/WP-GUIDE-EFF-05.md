# WP-GUIDE-EFF-05 — Final PR readiness gate for placeholder-free review artifacts

**Package class:** T1 — docs/process/guidance
**Branch:** `docs/guide-eff-05-final-pr-readiness-gate`
**PR:** https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/423

## Scope summary

Adds a final PR-readiness gate to shared Claude Code / Codex guidance so coding-agent PRs do not reach Side/Main review with placeholder PR bodies, stale status-fragment PR fields, pending validation text, or non-authority wording drift. Triggered by WP-F5A / PR #422, which required multiple follow-ups for issues the final-readiness gate would have caught.

## Changed files

| File | Change |
|---|---|
| `docs/ai/codex/WP_DRAFTING_STANDARD.md` | Added Section 15 "Final PR Readiness Gate"; updated merge-readiness reviewer checklist |
| `docs/ai/codex/WP_EXECUTION_REPORT.md` | Expanded compact/expanded shape section E and G to require PR-body placeholder scan and status-fragment finality; added note that PR body is part of the review evidence surface |
| `docs/ai/codex/COMPACT_WP_TEMPLATE.md` | Added Section 11a "Final PR Readiness Gate"; added "Semantic Text Audit for Non-Authority Packages" block; updated reviewer checklist |
| `docs/status_entries/README.md` | Added "Status Fragment Finality Rules" section |
| `docs/status_entries/WP-GUIDE-EFF-05.md` | This file (new) |
| `docs/project_status.md` | Appended compact WP-GUIDE-EFF-05 pointer |

## Validation summary

```
git status --short
(clean)

git diff --check
(clean — CRLF warning only, expected on Windows, exit 0)

python -m tools.registry.validate_result_populations
OK: result-population artifacts under .../research/result_populations validate

python -m tools.research_query.run --list-views
55 v_integrity_* views discovered.

All 55 v_integrity_* views: clean (0 rows)
  v_integrity_agent_output_refs:                          (no rows)
  v_integrity_bucket_mapping_refs:                        (no rows)
  v_integrity_candidate_refs:                             (no rows)
  v_integrity_decision_refs:                              (no rows)
  v_integrity_lifecycle_approval_completeness:            (no rows)
  v_integrity_lifecycle_change_refs:                      (no rows)
  v_integrity_lifecycle_fast_track_completeness:          (no rows)
  v_integrity_lifecycle_transition_graph:                 (no rows)
  v_integrity_macro_window_agent_output_refs:             (no rows)
  v_integrity_outcome_ledger_derivation:                  (no rows)
  v_integrity_outcome_ledger_refs:                        (no rows)
  v_integrity_outcome_ledger_scope:                       (no rows)
  v_integrity_outcome_ledger_window_bounds:               (no rows)
  v_integrity_overlay_shadow_refs:                        (no rows)
  v_integrity_plan_report_pairs:                          (no rows)
  v_integrity_pre_gate_advisory_snapshot_refs:            (no rows)
  v_integrity_r2s_approval_candidate_refs:                (no rows)
  v_integrity_r2s_rec5_candidate_consistency:             (no rows)
  v_integrity_reconciliation_derivation:                  (no rows)
  v_integrity_reconciliation_expectation_source:          (no rows)
  v_integrity_reconciliation_realized_metrics:            (no rows)
  v_integrity_reconciliation_refs:                        (no rows)
  v_integrity_reconciliation_scope:                       (no rows)
  v_integrity_release_refs:                               (no rows)
  v_integrity_result_population_append_only_violation:    (no rows)
  v_integrity_result_population_audit_in_identity_scope:  (no rows)
  v_integrity_result_population_authority_key_violation:  (no rows)
  v_integrity_result_population_canonical_evidence_violation: (no rows)
  v_integrity_result_population_canonical_write_violation: (no rows)
  v_integrity_result_population_denominator_mismatch:     (no rows)
  v_integrity_result_population_missing_variant_rows:     (no rows)
  v_integrity_result_population_non_authority_violation:  (no rows)
  v_integrity_result_population_offline_boundary_violation: (no rows)
  v_integrity_result_population_outcome_count_mismatch:   (no rows)
  v_integrity_result_population_parent_hash_chain_mismatch: (no rows)
  v_integrity_result_population_unknown_outcome_category: (no rows)
  v_integrity_s2p_approval_candidate_refs:                (no rows)
  v_integrity_s2p_shadow_evidence_candidate_consistency:  (no rows)
  v_integrity_s2p_shadow_evidence_refs:                   (no rows)
  v_integrity_scope6_authority_flags:                     (no rows)
  v_integrity_scope6_preservation_flags:                  (no rows)
  v_integrity_shadow_evidence_candidate_refs:             (no rows)
  v_integrity_shadow_signal_summary_derivation:           (no rows)
  v_integrity_shadow_signal_summary_v2_derivation:        (no rows)
  v_integrity_strategy_spec_bounds:                       (no rows)
  v_integrity_strategy_spec_hash_readiness:               (no rows)
  v_integrity_strategy_spec_non_authority:                (no rows)
  v_integrity_sweep_plan_denominator:                     (no rows)
  v_integrity_sweep_plan_no_computation:                  (no rows)
  v_integrity_sweep_plan_non_authority:                   (no rows)
  v_integrity_sweep_plan_parent_manifest:                 (no rows)
  v_integrity_variant_manifest_denominator:               (no rows)
  v_integrity_variant_manifest_hash_readiness:            (no rows)
  v_integrity_variant_manifest_non_authority:             (no rows)
  v_integrity_variant_manifest_supersession:              (no rows)

python tools/dev/diff_scope_summary.py
Tracked changed files: none. Staged changed files: none. Untracked files: none.
Forbidden-path matches: none. Exit: ok.

Full pytest
Not run; not used as merge evidence. (T1 docs-only package; no code, schema, or test changes)

Final rebase / mergeability gate
git fetch origin && git rebase origin/main: branch already up to date, no conflicts.
git status --short: clean.
git diff --check: clean.
git diff --name-only origin/main...HEAD: 6 files, matching expected scope exactly.
GitHub: mergeable=MERGEABLE, mergeStateStatus=CLEAN.
```

## Boundary summary

WP-GUIDE-EFF-05 does **not**:
- Implement PR-body automation, scripts, helpers, validators, CI, or GitHub Actions
- Modify validation commands or weaken validation requirements
- Make status fragments a repo-truth replacement or demote `docs/project_status.md`
- Rewrite historical `docs/project_status.md` entries
- Touch F5B/F5C implementation
- Touch dashboard collector, renderer, generator, or generated output
- Touch schemas, validators, tests, result populations, data artifacts, query-layer, strategy specs, variant manifests, sweep plans, runtime, paper/live, OMS, risk, broker/exchange, configs, dependencies, or protected paths
- Add ranking/recommendation/readiness/promotion/execution authority
- Alter startup read order or rename `docs/ai/codex/`

## Merge status

Open PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/423

## Next dependency / runway note

F5B (collector) remains gated on WP-F5A / PR #422 merge (already done) and separate Main authorization. This guidance package is a T1 prerequisite for F5B/F5C only in the sense that F5B/F5C packages will inherit the strengthened final-readiness contract.
