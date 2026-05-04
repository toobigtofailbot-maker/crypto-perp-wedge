# Outcome Ledger Per-Strategy-Family Consumer Brief (WP-9r)

**Date:** 2026-05-04
**Scope:** Third bounded consumer over the committed OL v1 retrospective corpus.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-outcome_ledger_per_strategy_family_consumer/`.
**Primary semantic source:** `outcome_ledgers` joined to `candidates.strategy_family` through the central query layer.
**Does not introduce:** OL artifacts, schema changes, validator changes, query-layer changes, ingestion-helper changes, registry changes, lifecycle changes, REC/reconciliation content, promotion policy, evidence scoring, deployment artifacts, or runtime behavior.
**Does not recommend:** Strategy-family ranking, family performance conclusions, policy action, promotion/demotion action, paper/live eligibility, evidence-quality scoring, REC/reconciliation action, runtime influence, or deployment action.

## 1. Purpose

This brief is the third bounded consumer over the OL v1 retrospective corpus. It reads the committed outcome-ledger entries through the candidate-registry `strategy_family` axis and demonstrates that outcome-ledger entries can be consumed with registry family context through the central query layer.

The package follows the WP-9p and WP-9q consumer-brief pattern: SQL queries are stored, raw JSON outputs are committed, and claims are tied to those outputs. The brief has no policy, REC/reconciliation, promotion/demotion, paper/live, evidence-scoring, runtime, or deployment authority.

## 2. Scope and Inputs

The committed input scope is `OL-0001` through `OL-0011`. The query bundle reads `outcome_ledgers` and joins candidate-registry strategy-family context through the central `candidates` relation. It does not load JSON locally and does not modify the query layer.

`Q01` reports 11 OL rows across 10 OL-covered candidates and 8 represented strategy families (`outputs/Q01.json`). The same output reports 11 source REP artifacts, 11 source EXP artifacts, and 0 advisory links.

This package commits the query bundle and outputs under `research/briefs/2026-04-outcome_ledger_per_strategy_family_consumer/`. It does not modify outcome-ledger artifacts, source EXP/REP artifacts, registry rows, lifecycle artifacts, schemas, validators, query-layer files, ingestion-helper code, runtime paths, policy artifacts, or protected execution paths.

## 3. Strategy-Family Corpus Summary

`Q01` and `Q02` report 8 represented strategy families across 10 OL-covered candidates and 11 OL rows (`outputs/Q01.json`, `outputs/Q02.json`).

The represented family structure is:

- `trend_following`: 2 candidates and 3 OL rows.
- `momentum`: 2 candidates and 2 OL rows.
- `basis_mean_reversion`, `breakout`, `funding_directional`, `funding_momentum_composite`, `mean_reversion`, and `multi_tf_alignment`: each 1 candidate and 1 OL row.

This is structural coverage. It is not a strategy-family quality ranking, performance ranking, promotion/demotion signal, evidence-quality score, or recommendation.

## 4. Multi-Entry Families

`Q03` identifies the current multi-entry families as `trend_following` and `momentum` (`outputs/Q03.json`).

`trend_following` has 3 OL rows because it contains H-002 plus H-004's two outcome-ledger entries: `OL-0005` / `REP-0005` / `EXP-0005` under `pre_wp_5b`, and `OL-0011` / `REP-0011` / `EXP-0011` under `post_wp_5b`. `momentum` has 2 OL rows because it contains H-005 and H-008.

These are multi-entry structural observations only. They do not assert family superiority, inferiority, robustness, or comparability.

## 5. Strategy-Family / Pipeline-Version Matrix

`Q04` reports the strategy-family / pipeline-version matrix (`outputs/Q04.json`). All represented families have `pre_wp_5b` OL rows. `trend_following` is the only represented family that also appears under `post_wp_5b`.

The `post_wp_5b` `trend_following` row is driven by H-004's `OL-0011` / `REP-0011` entry. H-004 therefore remains visible as a split trend-following candidate, while H-002 and H-004 together form the `pre_wp_5b` trend-following surface.

This brief does not treat pre-WP-5b and post-WP-5b metrics as automatically comparable. It makes no cross-family or cross-pipeline performance conclusion.

## 6. Inference-Floor Discipline

OL-4 requires at least 3 evaluation windows per candidate / outcome_kind / pipeline_version before cross-window inference. `Q05` operationalizes that consumer-time rule with `inference_floor = 3` (`outputs/Q05.json`).

Every current strategy_family / candidate_id / outcome_kind / pipeline_version segment has `window_count = 1`, so every segment is marked `INSUFFICIENT_EVIDENCE` (`outputs/Q05.json`). The allowed claim type for every current segment is single-window factual observation only.

Strategy-family grouping does not lower the OL-4 floor. There is no retrospective special-case lowering, and no cross-window inference is made below floor.

## 7. Metric Surface and Lineage by Strategy Family

`Q06` exposes schema-supported metrics as single-window facts grouped by strategy family (`outputs/Q06.json`). The current metric surface includes Sharpe, max drawdown, observation count, trades, hit rate, profit factor, final equity, PnL/cost fields, DSR, walk-forward efficiency, and gate counts where present in the OL `metrics` object.

`Q06` also keeps source lineage inspectable for every OL entry. Each row has one source REP and one source EXP, and every row reports `linked_artifact_count = 2`. Each current row reports `linked_advisory_artifact_count = 0`, so the retrospective corpus has no advisory lineage links.

These metrics are raw single-window facts. This brief does not compute strategy-family aggregate performance, rank strategy families, encode evidence-quality scoring, or infer below the OL-4 floor.

## 8. What WP-9r Shows

WP-9r shows that the OL v1 corpus is queryable by strategy family through the central query layer. It makes family coverage explicit across 8 represented strategy families, 10 OL-covered candidates, and 11 OL rows (`outputs/Q01.json`).

It also shows that singleton and repeat-family structure is observable, `trend_following` and `momentum` are the current multi-entry families, H-004 remains visible as a split trend-following candidate, and OL-4 floor discipline remains enforceable despite family grouping (`outputs/Q03.json`, `outputs/Q04.json`, `outputs/Q05.json`).

## 9. What WP-9r Does Not Show

WP-9r does not provide outcome-ledger synthesis; that is WP-9s. It does not provide an outcome-ledger stability lock; that is WP-9t.

This brief makes no REC/reconciliation claim, no promotion/demotion policy claim, no paper/live semantics claim, no evidence-scoring claim, no runtime/deployment implication, no strategy-family ranking, no strategy-family performance conclusion, and no automatic-comparability claim across families or pipeline versions.

## 10. Validation and Reproducibility

The reproducible query bundle is stored under `research/briefs/2026-04-outcome_ledger_per_strategy_family_consumer/`:

- queries: `research/briefs/2026-04-outcome_ledger_per_strategy_family_consumer/queries/`
- outputs: `research/briefs/2026-04-outcome_ledger_per_strategy_family_consumer/outputs/`
- helper: `research/briefs/2026-04-outcome_ledger_per_strategy_family_consumer/run_all_queries.py`

Validation commands run for WP-9r:

```powershell
.\.venv\Scripts\python.exe research\briefs\2026-04-outcome_ledger_per_strategy_family_consumer\run_all_queries.py
git diff -- research\briefs\2026-04-outcome_ledger_per_strategy_family_consumer\outputs
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

At package completion, the helper regenerated outputs deterministically with no output diff after rerun, all outcome-ledger integrity views and all discovered `v_integrity_*` views were empty, lifecycle overview remained 30 rows, lifecycle transitions remained 10 / 10 / 10, targeted tests passed, full pytest passed, and protected-path hashes were unchanged outside the authorized WP-9r files.
