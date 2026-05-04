# Outcome Ledger Consumer Set Synthesis Brief (WP-9s)

## 1. Purpose

This brief synthesizes the completed WP-9p / WP-9q / WP-9r outcome-ledger
consumer set over the OL v1 retrospective corpus. It follows the lifecycle
consumer-set synthesis precedent by reading the completed consumer axes
together, preserving their shared boundaries, and recording what the current
corpus does and does not support.

WP-9s is read-only synthesis. It has no policy, REC/reconciliation,
promotion/demotion, paper/live, evidence-quality scoring, runtime, deployment,
OMS, risk, safe-mode, or live-trading authority.

## 2. Scope and Inputs

The input scope is the committed outcome-ledger corpus `OL-0001` through
`OL-0011`. The query bundle uses the central research query layer only and does
not load outcome-ledger JSON directly.

WP-9s synthesizes:

- WP-9p: per-candidate outcome path.
- WP-9q: per-pipeline-version view.
- WP-9r: per-strategy-family view.

The committed query bundle is under
`research/briefs/2026-04-outcome_ledger_consumer_set_synthesis/queries/`, and
the raw JSON outputs are under
`research/briefs/2026-04-outcome_ledger_consumer_set_synthesis/outputs/`.

`Q01` reports 11 OL rows, 10 OL-covered candidates, 11 source REP artifacts,
11 source EXP artifacts, 2 pipeline versions, 8 represented strategy families,
10 `pre_wp_5b` rows, 1 `post_wp_5b` row, and 0 advisory links
(`outputs/Q01.json`).

This package does not modify outcome-ledger artifacts, source EXP/REP
artifacts, registry rows, lifecycle artifacts, schemas, validators,
query-layer files, ingestion-helper code, runtime paths, policy artifacts, or
protected execution paths.

## 3. Consumer Axes Covered

`Q02` summarizes the completed consumer axes (`outputs/Q02.json`):

- `per_candidate`: 10 represented candidates and 11 OL rows; H-004 is the only
  two-entry candidate.
- `per_pipeline_version`: 2 represented pipeline versions and 11 OL rows;
  H-004 is the only cross-pipeline candidate and the only `post_wp_5b`
  contributor.
- `per_strategy_family`: 8 represented strategy families and 11 OL rows;
  `trend_following` and `momentum` are the current multi-entry families.

Each axis is descriptive only. No axis creates ranking, recommendation,
promotion, policy, evidence-scoring, or runtime authority. No axis lowers OL-4.

## 4. Stable Descriptive Corpus Facts

`Q01` records the stable descriptive corpus shape (`outputs/Q01.json`):

- 11 OL rows.
- 10 OL-covered candidates.
- 11 source REP artifacts.
- 11 source EXP artifacts.
- 2 pipeline versions.
- 8 represented strategy families.
- 10 `pre_wp_5b` rows.
- 1 `post_wp_5b` row.
- 0 advisory links.

These are inventory facts only. They do not rank candidates, families, or
pipeline versions.

## 5. H-004 Structural Exception

`Q03` centralizes H-004 across the completed axes (`outputs/Q03.json`).

H-004 is:

- the only two-entry candidate;
- the only cross-pipeline candidate;
- the only `post_wp_5b` contributor;
- part of the `trend_following` family split.

The two entries are:

```text
OL-0005 / REP-0005 / EXP-0005 / pre_wp_5b
OL-0011 / REP-0011 / EXP-0011 / post_wp_5b
```

The H-004 split is structural only. WP-9s makes no improvement, degradation,
comparability, recommendation, or promotion claim from the two rows.

## 6. OL-4 Floor Synthesis

`Q04` reports 11 candidate / outcome_kind / pipeline_version segments, with
all 11 below the OL-4 `n >= 3` floor and 0 at or above floor
(`outputs/Q04.json`).

Every current segment remains `INSUFFICIENT_EVIDENCE`. Grouping by candidate,
pipeline version, or strategy family does not lower OL-4. There is no
retrospective special-case lowering and no cross-window inference below floor.

## 7. Supported Descriptive Uses

`Q05` records supported descriptive uses (`outputs/Q05.json`). WP-9s supports:

- corpus inventory;
- per-candidate path inspection;
- pipeline-version distribution inspection;
- strategy-family distribution inspection;
- H-004 structural exception inspection;
- EXP/REP lineage inspection;
- OL-4 floor marking.

These uses are descriptive and consumer-time only.

## 8. Unsupported / Future-Dependent Claims

`Q05` also records unsupported or future-dependent claims (`outputs/Q05.json`).
WP-9s does not support:

- REC/reconciliation;
- promotion/demotion policy;
- paper/live semantics;
- evidence-quality scoring;
- strategy-family ranking;
- pipeline-version performance comparison;
- cross-window inference;
- runtime/deployment authority;
- candidate recommendation.

Those claims require later explicit packages where applicable.

## 9. Lineage and Advisory Posture

`Q06` reports that all 11 OL rows have EXP/REP lineage, 0 rows are missing
EXP/REP lineage, 0 advisory links exist, and 0 rows carry advisory links
(`outputs/Q06.json`).

The advisory field remains forward-compatible but unexercised in the current
retrospective corpus. WP-9s draws no REC/advisory conclusion from the empty
advisory state.

## 10. What WP-9s Shows

WP-9s shows that OL v1 is structurally consumable across the three completed
consumer axes. The current corpus is coherent, validated, centrally queryable,
and descriptively modest.

The synthesis also shows that H-004 is the central structural exception and
that OL-4 floor discipline is enforceable across per-candidate,
per-pipeline-version, and per-strategy-family consumption.

## 11. What WP-9s Does Not Show

WP-9s is not the outcome-ledger stability lock; that remains WP-9t. It does not
show or create:

- REC/reconciliation;
- promotion/demotion policy;
- paper/live semantics;
- evidence scoring;
- runtime/deployment implication;
- candidate or family ranking;
- automatic comparability across pipeline versions;
- cross-window inference.

## 12. Validation and Reproducibility

Reproducibility assets:

- Query bundle:
  `research/briefs/2026-04-outcome_ledger_consumer_set_synthesis/queries/`
- Output bundle:
  `research/briefs/2026-04-outcome_ledger_consumer_set_synthesis/outputs/`
- Helper:
  `research/briefs/2026-04-outcome_ledger_consumer_set_synthesis/run_all_queries.py`

Validation commands run for WP-9s:

```powershell
.\.venv\Scripts\python.exe research\briefs\2026-04-outcome_ledger_consumer_set_synthesis\run_all_queries.py
git diff -- research\briefs\2026-04-outcome_ledger_consumer_set_synthesis\outputs
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

All outcome-ledger integrity views returned `[]`; all discovered
`v_integrity_*` views returned `[]`; lifecycle overview remained 30 rows; and
lifecycle transitions remained 10 / 10 / 10. The changed-file set is limited
to the WP-9s brief/bundle and the narrow project-status entry.
