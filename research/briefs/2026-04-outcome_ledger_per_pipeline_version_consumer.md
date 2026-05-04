# Outcome Ledger Per-Pipeline-Version Consumer Brief (WP-9q)

**Date:** 2026-05-04
**Scope:** Second bounded consumer over the committed OL v1 retrospective corpus.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-outcome_ledger_per_pipeline_version_consumer/`.
**Primary semantic source:** `outcome_ledgers`, `v_outcome_ledger_overview`, `v_outcome_ledger_candidate_pipeline_summary`, and outcome-ledger integrity views through the central query layer.
**Does not introduce:** OL artifacts, schema changes, validator changes, query-layer changes, ingestion-helper changes, registry changes, lifecycle changes, REC/reconciliation content, promotion policy, evidence scoring, deployment artifacts, or runtime behavior.
**Does not recommend:** Policy action, promotion/demotion action, paper/live eligibility, evidence-quality scoring, REC/reconciliation action, runtime influence, or deployment action.

## 1. Purpose

This brief is the second bounded consumer over the OL v1 retrospective corpus. It reads the committed outcome-ledger entries by the `pipeline_version` axis and demonstrates that the outcome ledger can be consumed by versioned pipeline semantics.

The package follows the WP-9p consumer-brief pattern: SQL queries are stored, raw JSON outputs are committed, and claims are tied to those outputs. The brief has no policy, REC/reconciliation, promotion/demotion, paper/live, evidence-scoring, runtime, or deployment authority.

## 2. Scope and Inputs

The committed input scope is `OL-0001` through `OL-0011`. The query bundle reads only through the central research query layer and does not load outcome-ledger JSON directly.

`Q01` reports 11 OL rows across 2 pipeline versions, 10 candidates, 11 source REP artifacts, 11 source EXP artifacts, and 0 advisory links (`outputs/Q01.json`). The corpus shape is 10 `pre_wp_5b` rows and 1 `post_wp_5b` row (`outputs/Q01.json`).

This package commits the query bundle and outputs under `research/briefs/2026-04-outcome_ledger_per_pipeline_version_consumer/`. It does not modify outcome-ledger artifacts, source EXP/REP artifacts, registry rows, lifecycle artifacts, schemas, validators, query-layer files, ingestion-helper code, runtime paths, policy artifacts, or protected execution paths.

## 3. Pipeline-Version Corpus Summary

`Q01` and `Q02` report two represented pipeline versions (`outputs/Q01.json`, `outputs/Q02.json`):

- `pre_wp_5b`: 10 OL rows across 10 candidates, with 10 source REP artifacts and 10 source EXP artifacts.
- `post_wp_5b`: 1 OL row for H-004 only, with 1 source REP artifact and 1 source EXP artifact.

`Q02` shows that `pre_wp_5b` contains H-001 through H-010, while `post_wp_5b` contains only H-004 (`outputs/Q02.json`).

This is structural coverage. It is not a pipeline quality ranking, performance ranking, promotion/demotion signal, evidence-quality score, or recommendation.

## 4. Cross-Pipeline Candidate Overlap

`Q03` surfaces H-004 as the only current candidate represented in more than one pipeline version (`outputs/Q03.json`):

- `OL-0005` links `REP-0005` and `EXP-0005` under `pre_wp_5b`.
- `OL-0011` links `REP-0011` and `EXP-0011` under `post_wp_5b`.

This structurally exercises OL-3 reproducibility-under-versioned-pipeline-semantics: each H-004 entry discloses its source REP/EXP lineage and `pipeline_version`.

The two H-004 rows are single-window facts. This brief does not assert improvement or degradation between them and does not treat pre-WP-5b and post-WP-5b metrics as automatically comparable.

## 5. Inference-Floor Discipline

OL-4 requires at least 3 evaluation windows per candidate / outcome_kind / pipeline_version before cross-window inference. `Q04` operationalizes that consumer-time rule with `inference_floor = 3` (`outputs/Q04.json`).

Every current candidate / outcome_kind / pipeline_version segment has `window_count = 1`, so every segment is marked `INSUFFICIENT_EVIDENCE` (`outputs/Q04.json`). The allowed claim type for every current segment is single-window factual observation only.

This brief makes no cross-window inference below the OL-4 floor. There is no retrospective special-case lowering of the floor.

## 6. Metric Surface by Pipeline Version

`Q05` exposes schema-supported metrics as single-window facts grouped by pipeline version (`outputs/Q05.json`). The current metric surface includes Sharpe, max drawdown, observation count, trades, hit rate, profit factor, final equity, PnL/cost fields, DSR, walk-forward efficiency, and gate counts where present in the OL `metrics` object.

These metrics are not aggregated into pipeline-version performance claims. This brief does not rank pipeline versions, does not claim cross-pipeline improvement or degradation, does not support promotion/demotion conclusions, does not encode evidence-quality scoring, and does not permit cross-window inference below the OL-4 floor.

## 7. Linked Artifact Lineage by Pipeline Version

`Q06` reports the source lineage for each OL entry (`outputs/Q06.json`). Every outcome-ledger entry links two artifacts: one EXP artifact and one REP artifact. The `derivation_record.source_artifact_id` is the corresponding REP artifact, and `derivation_record.source_artifact_path` points to the committed report path.

`Q06` also reports 0 linked advisory artifacts for every current OL entry (`outputs/Q06.json`). Decision 8 forward-compatibility exists through the optional advisory-link field, but the current retrospective corpus does not exercise advisory linkage.

This is a lineage posture only. It does not create a REC/reconciliation conclusion, advisory-quality conclusion, promotion signal, or runtime signal.

## 8. What WP-9q Shows

WP-9q shows that the OL v1 corpus is queryable by pipeline version through the central query layer. It makes the corpus imbalance explicit, with 10 `pre_wp_5b` rows and 1 `post_wp_5b` row (`outputs/Q01.json`).

It also shows that H-004's cross-pipeline split is structurally observable, source EXP/REP lineage remains inspectable per pipeline version, and OL-4 floor discipline remains enforceable with `pipeline_version` as a required axis (`outputs/Q03.json`, `outputs/Q04.json`, `outputs/Q06.json`).

## 9. What WP-9q Does Not Show

WP-9q does not provide per-strategy-family analysis; that is WP-9r if `strategy_family` is queryable. It does not provide outcome-ledger synthesis; that is WP-9s. It does not provide a stability lock; that is WP-9t.

This brief makes no REC/reconciliation claim, no promotion/demotion policy claim, no paper/live semantics claim, no evidence-scoring claim, no runtime/deployment implication, and no automatic-comparability claim across pipeline versions.

## 10. Validation and Reproducibility

The reproducible query bundle is stored under `research/briefs/2026-04-outcome_ledger_per_pipeline_version_consumer/`:

- queries: `research/briefs/2026-04-outcome_ledger_per_pipeline_version_consumer/queries/`
- outputs: `research/briefs/2026-04-outcome_ledger_per_pipeline_version_consumer/outputs/`
- helper: `research/briefs/2026-04-outcome_ledger_per_pipeline_version_consumer/run_all_queries.py`

Validation commands run for WP-9q:

```powershell
.\.venv\Scripts\python.exe research\briefs\2026-04-outcome_ledger_per_pipeline_version_consumer\run_all_queries.py
git diff -- research\briefs\2026-04-outcome_ledger_per_pipeline_version_consumer\outputs
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
git status --short
```

At package completion, the helper regenerated outputs deterministically with no output diff after rerun, all outcome-ledger integrity views and all discovered `v_integrity_*` views were empty, lifecycle overview remained 30 rows, lifecycle transitions remained 10 / 10 / 10, targeted tests passed, full pytest passed, and protected-path hashes were unchanged outside the authorized WP-9q files.
