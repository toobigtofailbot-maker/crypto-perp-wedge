# Outcome Ledger Artifact (WP-9k)

## Purpose

The outcome ledger records per-candidate, per-evaluation-window outcomes.

Outcome ledger v1 supports research out-of-sample outcomes only. It is a
structured derivation surface from REP and related outcome source artifacts.
REP remains the authoritative research record.

The outcome ledger supports later aggregate query, REC/reconciliation,
promotion policy, and forward-flow lifecycle evidence. WP-9k does not implement
those later systems.

## Scope

WP-9k adds:

- outcome-ledger schema only
- this companion document
- OL decisions in the Phase 9 decision record
- schema-family inventory registration when supported by repo idiom

WP-9k adds no validator, outcome-ledger instances, query-layer integration,
tests, helper, methodology, retrospective backfill, REC/reconciliation,
promotion or demotion policy, paper/live values, evidence-quality scoring,
runtime behavior, deployment behavior, or protected-path behavior.

## Version And Schema Posture

Outcome ledger v1 uses:

- `schema_version: "v1"`
- `outcome_kind: "research_oos"` only
- `lifecycle_state_during_window: "in_research"` only

Paper and live outcome kinds require outcome-ledger v2 or later explicit
versioned work. Per-trade granularity and evidence-quality scoring also require
v2 or later additive work.

This record does not claim outcome-ledger v1 is final forever.

## Field Semantics

- `schema_version`: explicit schema marker, fixed to `v1`.
- `outcome_id`: stable `OL-NNNN` outcome-ledger identifier.
- `candidate_id`: `H-NNN` candidate registry reference.
- `lifecycle_state_during_window`: candidate lifecycle state during the
  evaluation window; v1 allows `in_research` only.
- `evaluation_window_start` and `evaluation_window_end`: evaluation-window
  boundaries. Null is allowed where current EXP/REP repo truth preserves the
  no-formal-split convention.
- `outcome_kind`: outcome class; v1 allows `research_oos` only.
- `metrics`: REP-derived OOS metrics using existing REP names such as
  `sharpe`, `max_drawdown`, `n_obs`, `trades`, `hit_rate`,
  `profit_factor`, `final_equity`, `total_pnl`, `gross_pnl`,
  `fees_paid`, `slippage_paid`, `funding_paid`, `cost_drag_fraction`,
  `dsr`, `walk_forward_efficiency`, `gates_passed`, and `gates_total`.
  REP-variant diagnostic fields are optional and are not invented by OL.
- `data_provenance`: source data references and source-data window boundaries
  available from EXP/REP evidence.
- `derivation_record`: required disclosure of derivation method, source REP ID,
  source artifact path, and derivation timestamp.
- `pipeline_version`: required pipeline-semantics disclosure label. WP-9k
  labels are `pre_wp_5b` and `post_wp_5b` because current repo truth documents
  pre/post-WP-5b semantics textually but has no canonical machine labels.
- `linked_artifacts`: related artifact identifiers or repo-relative paths.
  Reference resolution is deferred to WP-9l.
- `linked_advisory_artifacts`: optional one-way advisory lineage hook. It has
  no execution, ranking, approval, or policy authority.
- `retrospective_flag`: marks entries derived retrospectively from already
  committed evidence.
- `retrospective_disclosure`: required when `retrospective_flag` is true.
- `notes`: optional human context.

## Decision References

Outcome ledger v1 depends on existing Phase 9 decisions:

- Decision 4: per-evaluation-window outcome granularity.
- Decision 8: optional linked advisory artifact hook.
- Decision 9: future promotion/demotion policy depends on outcomes, but is not
  implemented here.
- Decision 10: explicit schema-versioning discipline.

WP-9k also records OL-1 through OL-6:

- OL-1: v1 supports `research_oos` only.
- OL-2: retrospective REP backfill is accepted after schema and validator
  support are merged.
- OL-3: `derivation_record` and `pipeline_version` are required.
- OL-4: consumer inference requires at least 3 evaluation windows per candidate
  / outcome_kind / pipeline_version before cross-window inference.
- OL-5: v1 has required `pipeline_version`, optional
  `linked_advisory_artifacts`, no paper/live, no per-trade granularity, and no
  evidence-quality scoring.
- OL-6: outcome-ingestion helper is mid-tranche and absent from WP-9k.

## Reproducibility Contract

Every outcome-ledger entry must disclose its derivation basis.

`pipeline_version` records the pipeline semantics under which metrics were
produced. Entries with different `pipeline_version` values are not
automatically comparable.

H-004 has a known REP split: `REP-0005` records historical retrospective
pre-WP-5b evidence, while `REP-0011` records the later post-WP-5b forward-flow
re-execution. Future outcome-ledger backfill is expected to produce distinct
entries under different `pipeline_version` values for that split.

Byte-identical recomputation is interpreted under the disclosed pipeline
semantics and available committed source artifacts. WP-9k does not implement
recomputation tooling.

## Non-Claims

Outcome ledger v1 creates no:

- promotion or demotion authority
- policy authority
- REC/reconciliation authority
- paper/live semantics
- fast-track semantics
- runtime, OMS, risk, deployment, or live-trading authority
- evidence-quality scoring
- modification to REP or lifecycle artifacts
- validator or query-layer behavior
- outcome-ledger instances

## Forward Sequence

Expected next packages:

```text
WP-9l: validator + query-layer + integrity views
WP-9m: synthetic instance + backfill methodology
WP-9n: retrospective REP backfill
WP-9o: outcome-ingestion helper
```
