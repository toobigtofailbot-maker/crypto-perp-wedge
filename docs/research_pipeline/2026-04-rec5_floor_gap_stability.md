# REC-5 Floor-Gap Stability Lock (WP-10e)

## Purpose

This document is the documentation-only stability lock after the WP-10d
cross-expectation-source REC consumer.

It freezes the current REC-5 floor-gap posture over the completed dual-source
REC corpus. It does not correct REC artifacts, implement policy, rank or
recommend candidates, create paper/live semantics, score evidence quality, or
touch runtime, deployment, config, dependency, OMS, risk, safe-mode, execution,
or protected-path behavior.

## Locked Inputs

The locked input set is:

- WP-10a: post-REC architecture checkpoint.
- WP-10b: first D2-006 REC seed and D2 methodology.
- WP-10c: D2-006 retrospective bulk backfill.
- WP-10d: cross-expectation-source REC consumer.
- REC v1 stability lock.
- outcome-ledger v1 stability lock.
- lifecycle stability lock.

These inputs are consumed as repo-truth baselines only. They do not create
policy, promotion, demotion, ranking, recommendation, paper/live, evidence
scoring, or runtime authority.

## Corpus Snapshot

The locked REC corpus snapshot is:

- 22 REC rows.
- committed REC artifacts: `REC-0001` through `REC-0022`.
- 11 `exp_success_criteria` rows.
- 11 `d2_006_gates` rows.
- 11 source OL rows.
- 10 represented candidates.
- 20 `pre_wp_5b` rows.
- 2 `post_wp_5b` rows.
- 0 advisory links.
- 0 lifecycle links.

The verdict distribution by expectation source is:

| Expectation source | Verdict | Rows |
|---|---:|---:|
| `d2_006_gates` | `none_met` | 5 |
| `d2_006_gates` | `partially_met` | 6 |
| `exp_success_criteria` | `insufficient_evidence` | 1 |
| `exp_success_criteria` | `none_met` | 3 |
| `exp_success_criteria` | `partially_met` | 7 |

These are corpus inventory facts only. They do not rank candidates, verdicts,
strategy families, expectation sources, or pipeline versions.

## REC-5 Floor Definition

The locked REC-5 floor definition is:

```text
n >= 3 per candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

Expectation-source counts are not combined. Pre/post pipeline versions are not
combined. H-004 pre/post rows are not combined. Dual-source coverage does not
satisfy REC-5.

There is no retrospective special-case lowering and no policy, promotion,
demotion, ranking, recommendation, paper/live, evidence-scoring, or runtime
implication.

## Current Floor-Gap State

Every current source segment has `reconciliation_count = 1`. Every current
segment is below floor. All current cross-reconciliation inference remains
unsupported. No candidate has a REC-5-satisfied segment. No expectation source
has a REC-5-satisfied segment.

Compact segment examples:

| Candidate | Pipeline version | Expectation source | REC rows | REC-5 posture |
|---|---|---|---:|---|
| H-001 | `pre_wp_5b` | `exp_success_criteria` | 1 | below floor |
| H-001 | `pre_wp_5b` | `d2_006_gates` | 1 | below floor |
| H-004 | `pre_wp_5b` | `exp_success_criteria` | 1 | below floor |
| H-004 | `pre_wp_5b` | `d2_006_gates` | 1 | below floor |
| H-004 | `post_wp_5b` | `exp_success_criteria` | 1 | below floor |
| H-004 | `post_wp_5b` | `d2_006_gates` | 1 | below floor |

## Cross-Expectation-Source Coverage

Every locked OL v1 row now has both expectation sources represented:

- one `exp_success_criteria` REC row.
- one `d2_006_gates` REC row.

Coverage is side-by-side descriptive evidence only. Source pairs do not imply
source superiority, source preference, ranking, recommendation, policy
readiness, promotion, demotion, paper/live readiness, or runtime authority.

Coverage is necessary context for later sufficient-evidence expansion. It is
not sufficient evidence and does not satisfy REC-5.

## H-004 Split Posture

The four H-004 REC rows are:

```text
REC-0005 / OL-0005 / H-004 / pre_wp_5b / exp_success_criteria / partially_met
REC-0011 / OL-0011 / H-004 / post_wp_5b / exp_success_criteria / insufficient_evidence
REC-0016 / OL-0005 / H-004 / pre_wp_5b / d2_006_gates / partially_met
REC-0022 / OL-0011 / H-004 / post_wp_5b / d2_006_gates / partially_met
```

The split is structural only. It creates no pre/post comparison, no improvement
or degradation inference, no pipeline-version performance comparison, and no
promotion, demotion, ranking, recommendation, paper/live, policy, evidence
scoring, or runtime inference.

## D2 Comparison-Surface Anomaly Register

`REC-0017` and `REC-0019` correctly skip cost-drag pass/fail comparison
because `gross_pnl <= 0`. Both rows have `overall_verdict = none_met`.

`REC-0012` is a pre-WP-10c seed that still compares cost drag despite
`gross_pnl <= 0`. WP-10d surfaces `REC-0012` as:

```text
compared_despite_non_positive_gross_pnl_pre_wp10c_seed_requires_followup
```

WP-10e locks this as an open anomaly and follow-up candidate, not accepted
clean semantics. WP-10e does not modify `REC-0012`. Any correction must be a
separate explicitly scoped artifact-correction package.

No policy, scoring, ranking, recommendation, paper/live, promotion, demotion,
or runtime inference may use the anomaly.

## Supported Descriptive Uses

The supported descriptive uses are:

- corpus inventory.
- floor-gap inspection.
- cross-source coverage inspection.
- REC-to-OL mapping inspection.
- H-004 structural split inspection.
- D2 comparison-surface exception inspection.
- planning sufficient-evidence expansion.

These uses remain descriptive and research-side only.

## Unsupported / Future-Dependent Claims

The unsupported and future-dependent claim areas are:

- policy.
- promotion/demotion.
- ranking/recommendation.
- paper/live readiness.
- evidence-quality scoring.
- strategy-family performance conclusions.
- pipeline-version performance comparisons.
- cross-window inference.
- runtime/deployment authority.
- OMS/risk/safe-mode/execution authority.
- protected-path authority.

These require later explicit packages where applicable. They are not implied by
the dual-source REC corpus, WP-10d outputs, or this stability lock.

## Mutation / Evolution Rules

Later packages must follow these rules:

- do not lower REC-5 silently.
- do not combine expectation sources to satisfy REC-5.
- do not combine pre/post pipeline versions to satisfy REC-5.
- do not use dual-source coverage as evidence-floor satisfaction.
- do not reinterpret the `REC-0012` anomaly as clean without explicit
  correction.
- future REC artifact corrections require an explicit package with
  preservation and validation.
- future policy, paper/live, scoring, ranking, recommendation, or runtime work
  requires a later architecture decision.

## Next Package Boundary

WP-10f should be a Phase 9 -> Phase 10 transition architecture decision
document. WP-10f must not implement Phase 10.

WP-10f must explicitly decide whether to:

- carry the `REC-0012` anomaly as known debt.
- schedule a corrective artifact package.
- require forward-flow evidence before policy.
- keep all downstream outputs descriptive-only.

No policy package may proceed from WP-10e alone.

## Validation Snapshot

WP-10e validation records the following results:

- REC validator: PASS.
- `v_reconciliation_overview`: 22 rows.
- `v_reconciliation_candidate_pipeline_summary`: 22 segments, all
  `reconciliation_count = 1`.
- REC integrity views: `[]`.
- all discovered `v_integrity_*` views: `[]`.
- outcome-ledger validator: PASS.
- `v_outcome_ledger_overview`: 11 rows.
- lifecycle validator: PASS.
- `v_lifecycle_change_overview`: 30 rows.
- `v_lifecycle_state_transitions`: 10 / 10 / 10.
- targeted tests: PASS.
- full pytest: PASS.
- `git diff --check`: PASS.

The validation command set is:

```powershell
.\.venv\Scripts\python.exe -m tools.registry.validate_reconciliations
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_reconciliation_overview --json
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_reconciliation_candidate_pipeline_summary --json
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_integrity_reconciliation_refs --json
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_integrity_reconciliation_scope --json
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_integrity_reconciliation_expectation_source --json
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_integrity_reconciliation_derivation --json
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_integrity_reconciliation_realized_metrics --json
.\.venv\Scripts\python.exe -m tools.registry.validate_registry
.\.venv\Scripts\python.exe -m tools.registry.validate_experiment_artifacts
.\.venv\Scripts\python.exe -m tools.registry.validate_decision_changes
.\.venv\Scripts\python.exe -m tools.registry.validate_release_notes
.\.venv\Scripts\python.exe -m tools.registry.validate_agent_outputs
.\.venv\Scripts\python.exe -m tools.registry.validate_macro_window_agent_outputs
.\.venv\Scripts\python.exe -m tools.registry.validate_bucket_mappings
.\.venv\Scripts\python.exe -m tools.registry.validate_pre_gate_advisory_snapshots
.\.venv\Scripts\python.exe -m tools.registry.validate_overlay_shadow_logs
.\.venv\Scripts\python.exe -m tools.registry.validate_shadow_signal_summaries
.\.venv\Scripts\python.exe -m tools.registry.validate_shadow_signal_summary_v2
.\.venv\Scripts\python.exe -m tools.registry.validate_lifecycle_changes
.\.venv\Scripts\python.exe -m tools.registry.validate_outcome_ledger
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_lifecycle_change_overview --json
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_lifecycle_state_transitions --json
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_outcome_ledger_overview --json
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_outcome_ledger_candidate_pipeline_summary --json
.\.venv\Scripts\python.exe -m pytest tests -q -k "reconciliation or registry or research_query or outcome_ledger"
.\.venv\Scripts\python.exe -m pytest -q
git diff --check
```

## Non-Claims

WP-10e does not create:

- REC artifact correction.
- REC-5 satisfaction.
- policy.
- promotion/demotion.
- ranking/recommendation.
- paper/live semantics.
- evidence-quality scoring.
- schema.
- validator.
- query-layer view.
- artifact instance.
- runtime/deployment/OMS/risk/safe-mode/execution authority.
- protected-path authority.
