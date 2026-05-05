# REC v1 Stability Lock (WP-9z)

## Purpose

This document is the documentation-only stability lock over the completed REC
v1 baseline.

It locks the current REC schema, validator, query-layer, artifact, and consumer
state as a descriptive research surface. It follows the lifecycle, SSS, and
outcome-ledger stability-lock precedent: record the consumed baseline, preserve
explicit boundaries, and prevent silent retroactive reinterpretation.

WP-9z creates no policy, recommendation, promotion/demotion, paper/live,
evidence-quality scoring, runtime, deployment, OMS, risk, safe-mode, execution,
or protected-path authority.

## Locked Package Set

The consumed REC v1 package set is:

- WP-9u: REC v1 schema and REC-1 through REC-6 decisions.
- WP-9v: REC validator, central query-layer relation, overview views, and
  integrity views.
- WP-9w: `REC-0001` seed and retrospective backfill methodology.
- WP-9x: retrospective backfill to `REC-0002` through `REC-0011`.
- WP-9y: REC consumer synthesis over the completed REC v1 corpus.

The package set is descriptive. It does not authorize promotion policy,
paper/live semantics, evidence scoring, ranking, recommendation, or runtime
behavior.

## Locked REC Corpus Baseline

The locked REC v1 corpus baseline is:

- schema version: `v1`
- outcome kind: `research_oos`
- committed REC artifacts: `REC-0001` through `REC-0011`
- 11 REC rows
- 10 REC-covered candidates
- 11 source OL rows
- 10 `pre_wp_5b` rows
- 1 `post_wp_5b` row
- 11 `exp_success_criteria` expectation-source rows
- 0 `d2_006_gates` expectation-source rows
- 3 `none_met` verdict rows
- 7 `partially_met` verdict rows
- 1 `insufficient_evidence` verdict row

These are corpus inventory facts only. They do not rank candidates, verdicts,
strategy families, or pipeline versions.

## Locked Query / Integrity Surface

The locked central query surface includes:

- `reconciliations` relation
- `v_reconciliation_overview`
- `v_reconciliation_candidate_pipeline_summary`
- five REC integrity views:
  - `v_integrity_reconciliation_refs`
  - `v_integrity_reconciliation_scope`
  - `v_integrity_reconciliation_expectation_source`
  - `v_integrity_reconciliation_derivation`
  - `v_integrity_reconciliation_realized_metrics`

At lock time all five REC integrity views are empty. All discovered
`v_integrity_*` views are empty at lock time. Lifecycle regression remains 30
rows with transition counts 10 / 10 / 10. Outcome-ledger regression remains 11
rows with the H-004 split preserved.

WP-9z does not modify the query layer.

## Locked Consumer Surface

WP-9y provides the current REC consumer synthesis through:

- `research/briefs/2026-04-rec_v1_consumer_synthesis.md`
- six-query SQL bundle under
  `research/briefs/2026-04-rec_v1_consumer_synthesis/queries/`
- committed JSON outputs under
  `research/briefs/2026-04-rec_v1_consumer_synthesis/outputs/`
- package-local regeneration helper
  `research/briefs/2026-04-rec_v1_consumer_synthesis/run_all_queries.py`

The WP-9y consumer surface is locked as descriptive consumer output. Supported
uses are descriptive only. No consumer output creates authority for policy,
ranking, recommendation, promotion, demotion, paper/live, evidence scoring,
runtime, or deployment.

## H-004 Structural Split

H-004 remains structurally split as two separate REC rows:

```text
REC-0005 / OL-0005 / H-004 / pre_wp_5b / exp_success_criteria / partially_met
REC-0011 / OL-0011 / H-004 / post_wp_5b / exp_success_criteria / insufficient_evidence
```

The split remains structural only. It creates no pre/post comparison, no
improvement or degradation inference, no pipeline-performance conclusion, and
no promotion, paper/live, policy, ranking, recommendation, or runtime
inference.

## REC-5 Locked Floor Discipline

The locked REC-5 consumer inference floor remains:

```text
n >= 3 per candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

All current segments have `reconciliation_count = 1`. All current segments
remain below floor. All current cross-reconciliation inference remains
`INSUFFICIENT_EVIDENCE`.

Grouping by candidate, verdict, pipeline, strategy, or retrospective corpus
does not lower REC-5. There is no retrospective special-case lowering and no
cross-reconciliation inference below floor.

## Verdict Semantics Lock

REC verdicts are descriptive per-REC comparison results:

- `partially_met` is not policy eligibility.
- `none_met` is not rejection policy.
- `insufficient_evidence` is descriptive insufficiency, not failure.

The verdict distribution does not create ranking, recommendation, promotion,
demotion, paper/live, policy, runtime, or deployment authority.

## Supported Descriptive Uses

The locked supported descriptive uses are:

- REC corpus inventory.
- REC-to-OL mapping inspection.
- Per-candidate REC path inspection.
- Verdict distribution inspection.
- Expectation-source distribution inspection.
- H-004 split inspection.
- REC-5 floor marking.
- Comparison-surface inspection limited to deterministic mapped metrics and
  preserved qualitative/gate-reference criteria.

These uses remain descriptive and research-side only.

## Unsupported / Future-Dependent Claims

The locked unsupported and future-dependent claim areas are:

- promotion/demotion policy
- candidate recommendation
- ranking
- paper/live readiness
- evidence-quality scoring
- strategy-family performance conclusions
- pipeline-version performance comparison
- cross-window inference below REC-5
- runtime/deployment authority
- OMS/risk/safe-mode/execution authority
- protected-path authority

These require explicit later work where applicable. They are not implied by the
REC v1 corpus, consumers, or this stability lock.

## Mutation / Evolution Rules

Later packages must follow these rules:

- No retroactive mutation of committed REC artifacts without an explicit scoped
  package and rationale.
- No REC schema v1 semantic change without explicit schema-versioned work.
- No REC validator or query-layer semantic change without an explicit scoped
  package and regression checks.
- No REC consumer-output rewrite unless source corpus or query semantics
  intentionally change through an approved package.
- New REC artifacts append by ID and must pass validator and integrity checks.
- Future promotion/policy must consume this locked baseline and must not
  silently redefine it.
- Future paper/live support must be versioned and explicit.
- Future evidence-quality scoring must use a separate schema and methodology.
- Runtime, deployment, OMS, risk, safe-mode, and execution authority remains
  forbidden absent separate protected runtime architecture.

This lock does not claim REC v1 is final forever. It records the consumed v1
baseline for current repo state.

## Validation Snapshot

WP-9z validation records the following results:

- REC validator: PASS
- `v_reconciliation_overview`: 11 rows
- `v_reconciliation_candidate_pipeline_summary`: H-004 split preserved
- `v_integrity_reconciliation_refs`: `[]`
- `v_integrity_reconciliation_scope`: `[]`
- `v_integrity_reconciliation_expectation_source`: `[]`
- `v_integrity_reconciliation_derivation`: `[]`
- `v_integrity_reconciliation_realized_metrics`: `[]`
- all discovered `v_integrity_*` views: `[]`
- outcome-ledger validator: PASS
- `v_outcome_ledger_overview`: 11 rows
- `v_outcome_ledger_candidate_pipeline_summary`: H-004 split preserved
- `v_lifecycle_change_overview`: 30 rows
- `v_lifecycle_state_transitions`: 10 / 10 / 10
- existing validators: PASS
- targeted tests: PASS
- full pytest: PASS
- `git diff --check`: PASS

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

## What WP-9z Enables Next

WP-9z does not start policy.

WP-9z enables a Main 3.0 architecture checkpoint by locking the current
descriptive REC v1 baseline as a dependency boundary.

Plausible future tranches after WP-9z require Main 3.0 decision:

- promotion/demotion policy architecture
- paper/live REC/outcome extension
- evidence-quality scoring
- ranking/recommendation architecture
- strategy-family/pipeline-version sufficient-evidence work

Codex packages for those should not be drafted until the next architecture
decision is made.
