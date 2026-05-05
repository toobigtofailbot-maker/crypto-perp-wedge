# Outcome Ledger v1 Stability Lock (WP-9t)

## Purpose

This document is the documentation-only stability lock for the consumed
outcome-ledger v1 baseline and completed outcome-ledger consumer set.

It locks the current schema, validator, query-layer, artifact, helper, and
consumer state as a descriptive research surface. It follows the lifecycle and
SSS stability-lock precedent: record the consumed baseline, preserve explicit
boundaries, and prevent silent retroactive reinterpretation.

WP-9t creates no policy, REC/reconciliation, promotion/demotion, paper/live,
evidence-quality scoring, runtime, deployment, OMS, risk, safe-mode, execution,
or protected-path authority.

## Locked Package Set

The consumed outcome-ledger v1 package set is:

- WP-9k: outcome-ledger schema v1 and companion artifact documentation.
- WP-9l: outcome-ledger validator, central query-layer relation, overview
  views, and integrity views.
- WP-9m: first seed outcome-ledger artifact and retrospective backfill
  methodology.
- WP-9n: retrospective REP-derived backfill to `OL-0001` through `OL-0011`.
- WP-9o: offline REP-derived outcome-ledger ingestion helper.
- WP-9p: per-candidate outcome-path consumer.
- WP-9q: per-pipeline-version consumer.
- WP-9r: per-strategy-family consumer.
- WP-9s: consumer set synthesis over the completed WP-9p / WP-9q / WP-9r
  consumer set.

The package set is descriptive. It does not authorize REC/reconciliation,
promotion policy, paper/live semantics, evidence scoring, or runtime behavior.

## Locked Corpus Baseline

The locked outcome-ledger v1 corpus baseline is:

- schema version: `v1`
- outcome kind: `research_oos`
- lifecycle state during window: `in_research`
- committed OL artifacts: `OL-0001` through `OL-0011`
- 11 OL rows
- 10 OL-covered candidates
- 11 source REP artifacts
- 11 source EXP artifacts
- 8 represented strategy families
- 2 pipeline versions
- 10 `pre_wp_5b` rows
- 1 `post_wp_5b` row
- 0 advisory links

These are corpus inventory facts only. They do not rank candidates, families,
or pipeline versions.

## Locked Query / Integrity Surface

The locked central query surface includes:

- `outcome_ledgers` relation
- `v_outcome_ledger_overview`
- `v_outcome_ledger_candidate_pipeline_summary`
- four outcome-ledger integrity views:
  - `v_integrity_outcome_ledger_refs`
  - `v_integrity_outcome_ledger_window_bounds`
  - `v_integrity_outcome_ledger_derivation`
  - `v_integrity_outcome_ledger_scope`

At lock time all four outcome-ledger integrity views are empty. All discovered
`v_integrity_*` views are empty at lock time. Lifecycle regression remains 30
rows with transition counts 10 / 10 / 10.

WP-9t does not modify the query layer.

## Locked Consumer Surfaces

The consumed descriptive consumer surfaces are:

- WP-9p covers the per-candidate axis.
- WP-9q covers the per-pipeline-version axis.
- WP-9r covers the per-strategy-family axis.
- WP-9s covers synthesis across the completed consumer set.

All four surfaces are descriptive research consumers only. They do not create
ranking, recommendation, promotion, demotion, policy, REC/reconciliation,
paper/live, evidence-scoring, runtime, or deployment authority.

## H-004 Structural Exception

H-004 is the central structural exception in the locked OL v1 corpus:

- only two-entry candidate
- only cross-pipeline candidate
- only `post_wp_5b` contributor
- part of the `trend_following` family split

The two H-004 entries are:

```text
OL-0005 / REP-0005 / EXP-0005 / pre_wp_5b
OL-0011 / REP-0011 / EXP-0011 / post_wp_5b
```

The H-004 split is structural only. It creates no improvement, degradation,
comparability, recommendation, promotion, demotion, or policy claim.

## OL-4 Locked Floor Discipline

The locked OL-4 consumer inference floor remains:

```text
n >= 3 per candidate / outcome_kind / pipeline_version
```

Before that floor is met, cross-window inference remains
`INSUFFICIENT_EVIDENCE`.

All 11 current candidate / outcome_kind / pipeline_version segments are below
floor. All 11 current segments remain `INSUFFICIENT_EVIDENCE`.

Grouping by candidate, pipeline version, or strategy family does not lower
OL-4. There is no retrospective special-case lowering and no cross-window
inference below floor.

## Locked Supported Descriptive Uses

The locked supported descriptive uses are:

- corpus inventory
- per-candidate path inspection
- pipeline-version distribution inspection
- strategy-family distribution inspection
- H-004 structural exception inspection
- EXP/REP lineage inspection
- OL-4 floor marking
- deterministic future REP-derived OL drafting through the helper, subject to
  review and validation

These uses remain descriptive and research-side only.

## Locked Unsupported / Future-Dependent Claims

The locked unsupported and future-dependent claim areas are:

- REC/reconciliation
- promotion/demotion policy
- paper/live semantics
- evidence-quality scoring
- strategy-family ranking
- candidate recommendation
- pipeline-version performance comparison
- cross-window inference
- runtime/deployment authority
- OMS/risk/safe-mode/execution authority
- protected-path authority

These require explicit later work where applicable. They are not implied by the
OL v1 corpus, consumers, or this stability lock.

## Mutation / Evolution Rules

Later packages must follow these rules:

- No retroactive mutation of committed OL artifacts without an explicit scoped
  package and rationale.
- No schema v1 semantic change without explicit schema-versioned work.
- No validator or query-layer semantic change without an explicit scoped
  package and regression checks.
- No consumer-output rewrite unless source corpus or query semantics
  intentionally change through an approved package.
- New OL artifacts append by ID and must pass validator and integrity checks.
- Future REC/reconciliation must consume the locked baseline and must not
  silently redefine it.
- Future promotion/policy must consume the locked baseline and must not infer
  authority from it.
- Future paper/live support must be versioned and explicit.

This lock does not claim outcome ledger v1 is final forever. It records the
consumed v1 baseline for current repo state.

## Validation Snapshot

WP-9t validation records the following results:

- outcome-ledger validator: PASS
- `v_outcome_ledger_overview`: 11 rows
- `v_outcome_ledger_candidate_pipeline_summary`: H-004 split preserved
- `v_integrity_outcome_ledger_refs`: `[]`
- `v_integrity_outcome_ledger_window_bounds`: `[]`
- `v_integrity_outcome_ledger_derivation`: `[]`
- `v_integrity_outcome_ledger_scope`: `[]`
- all discovered `v_integrity_*` views: `[]`
- `v_lifecycle_change_overview`: 30 rows
- `v_lifecycle_state_transitions`: 10 / 10 / 10
- existing validators: PASS
- targeted tests: PASS
- full pytest: PASS
- `git diff --check`: PASS

The validation command set is:

```powershell
.\.venv\Scripts\python.exe -m tools.registry.validate_outcome_ledger
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_outcome_ledger_overview --json
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_outcome_ledger_candidate_pipeline_summary --json
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_integrity_outcome_ledger_refs --json
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_integrity_outcome_ledger_window_bounds --json
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_integrity_outcome_ledger_derivation --json
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_integrity_outcome_ledger_scope --json
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
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_lifecycle_change_overview --json
.\.venv\Scripts\python.exe -m tools.research_query.run --view v_lifecycle_state_transitions --json
.\.venv\Scripts\python.exe -m pytest tests -q -k "outcome_ledger or outcome or registry or research_query"
.\.venv\Scripts\python.exe -m pytest -q
git diff --check
```

## What WP-9t Enables Next

WP-9t does not itself start REC/reconciliation, promotion policy, paper/live
extension, evidence-quality scoring, runtime work, or protected-path work.

It enables a later architecture decision for the next tranche by locking the
current descriptive OL v1 baseline as a dependency boundary.

Plausible future tranches after WP-9t include:

- REC/reconciliation architecture
- promotion/demotion policy architecture
- paper/live outcome-ledger extension
- evidence-quality scoring

Those require Main 3.0 / architecture confirmation before Codex work packages.
