# Lifecycle Per-Evidence-Artifact-Type Consumer Brief (WP-9h)

**Date:** 2026-04-29
**Scope:** Third bounded lifecycle consumer over the populated `LCH-0001` through `LCH-0030` corpus.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-lifecycle_per_evidence_artifact_type_consumer/`.
**Primary semantic source:** `lifecycle_changes`, `v_lifecycle_change_overview`, `v_lifecycle_state_transitions`, and LCH integrity views through the central query layer.
**Does not introduce:** LCH instances, schema changes, validator changes, query-layer changes, registry changes, evidence-artifact changes, outcome-ledger content, REC content, reconciliation content, promotion policy, deployment artifacts, or runtime behavior.
**Does not recommend:** Policy action, promotion/demotion action, paper/live eligibility, fast-track action, runtime influence, evidence-quality ranking, candidate-quality ranking, or outcome-learning conclusion.

## 1. Purpose

This brief is the third bounded consumer over the populated lifecycle layer. It reads committed `LCH-0001` through `LCH-0030` through the central query layer and segments the current lifecycle corpus by evidence artifact type.

The purpose is diagnostic: show what the lifecycle layer reveals when the unit of analysis is evidence-artifact lineage rather than candidate path or transition edge. This package establishes the per-evidence-artifact-type lifecycle consumer pattern, following WP-9f's per-candidate lifecycle consumer and WP-9g's per-transition-edge lifecycle consumer.

## 2. Scope and Sources

The committed LCH scope is `LCH-0001` through `LCH-0030`, covering candidates H-001 through H-010 (`outputs/Q01.json`, `outputs/Q05.json`). The evidence-ref scope is every `evidence_artifact_refs` value attached to the committed LCH corpus (`outputs/Q01.json`, `outputs/Q06.json`).

The query bundle reads:

- `lifecycle_changes`
- `v_lifecycle_change_overview`
- `v_lifecycle_state_transitions`
- `v_integrity_lifecycle_change_refs`
- `v_integrity_lifecycle_transition_graph`
- `v_integrity_lifecycle_approval_completeness`
- `v_integrity_lifecycle_fast_track_completeness`

The reproducible bundle is stored under `research/briefs/2026-04-lifecycle_per_evidence_artifact_type_consumer/`. The helper runs SQL through `tools.research_query.run --sql`; it does not register local DuckDB relations, bypass the central query layer, or read LCH files directly.

This brief does not modify LCH instances, source evidence artifacts, schemas, validators, registry rows, query-layer files, runtime paths, policy artifacts, protected execution paths, or WP-9f / WP-9g brief, query, output, or helper files.

## 3. Query Bundle

The bundle follows the current repo-local diagnostic idiom: `run_all_queries.py` iterates `queries/Q*.sql` and writes `outputs/Q01.json` through `outputs/Q06.json`.

- `queries/Q01.sql` -> `outputs/Q01.json`: current lifecycle evidence-ref inventory.
- `queries/Q02.sql` -> `outputs/Q02.json`: evidence artifact type distribution.
- `queries/Q03.sql` -> `outputs/Q03.json`: evidence artifact type by transition-edge matrix.
- `queries/Q04.sql` -> `outputs/Q04.json`: per-candidate evidence composition.
- `queries/Q05.sql` -> `outputs/Q05.json`: evidence-lineage alignment with WP-9f / WP-9g current-LCH baselines.
- `queries/Q06.sql` -> `outputs/Q06.json`: integrity and boundary snapshot.

All factual claims below cite those stored outputs.

## 4. Evidence Artifact Type Distribution Summary

The current LCH corpus contains 32 evidence refs across 5 known evidence artifact types (`outputs/Q01.json`, `outputs/Q02.json`, `outputs/Q05.json`, `outputs/Q06.json`).

The represented artifact types are HYPOTHESIS path, REP, DEC path, DCH, and REL (`outputs/Q02.json`). The corpus contains zero unknown / `other` evidence refs (`outputs/Q03.json`, `outputs/Q05.json`, `outputs/Q06.json`).

HYPOTHESIS-path evidence has 10 refs and covers all 10 candidates. REP evidence has 10 refs and covers all 10 candidates. DEC-path evidence has 10 refs and covers all 10 candidates (`outputs/Q02.json`).

DCH and REL each appear once, each covers only H-005, and each is attached to the archival transition (`outputs/Q02.json`, `outputs/Q04.json`). This makes DCH / REL presence a current-corpus H-005 archival exception, not a general lifecycle evidence pattern.

## 5. Evidence Type / Transition Edge Lineage

The `proposed->in_research` edge is supported by HYPOTHESIS-path evidence in the current corpus (`outputs/Q03.json`). The `in_research->research_concluded` edge is supported by REP evidence (`outputs/Q03.json`).

The `research_concluded->archived` edge is supported by DEC-path evidence, plus the H-005 DCH / REL exception (`outputs/Q03.json`, `outputs/Q04.json`). No transition edge has an unexpected evidence type in the current corpus, and no edge has `other` evidence refs (`outputs/Q03.json`).

This is a descriptive lineage finding. It is not an evidence-quality ranking, candidate-quality ranking, promotion signal, or policy recommendation.

## 6. Per-Candidate Evidence Composition

All ten candidates have one HYPOTHESIS path, one REP ID, and one DEC path in the committed lifecycle evidence refs (`outputs/Q04.json`). All non-H-005 candidates have 3 evidence refs, with zero DCH refs and zero REL refs (`outputs/Q04.json`).

H-005 has 5 evidence refs: one HYPOTHESIS path, one REP ID, one DEC path, one DCH ref, and one REL ref (`outputs/Q04.json`). H-005 is the only candidate where `has_cross_family_exception` is true (`outputs/Q04.json`).

This per-candidate evidence composition does not change any candidate status, H-005 status, historical decision, cited evidence artifact, or runtime behavior.

## 7. H-005 Cross-Family Exception

H-005 is the only current cross-family lifecycle evidence exception in the committed LCH corpus (`outputs/Q04.json`, `outputs/Q05.json`). The exception is attached to the `research_concluded->archived` transition, not to the `proposed->in_research` or `in_research->research_concluded` transitions (`outputs/Q03.json`, `outputs/Q04.json`).

The exception links `research/decisions/DEC-0005.md`, `DCH-0001`, and `REL-0001` on the archival transition (`outputs/Q04.json`). It should be preserved as a descriptive observation only.

Do not infer that H-005 is higher quality, lower quality, more important, policy-relevant, promotion-relevant, or operationally different because it has extra evidence refs.

## 8. Boundary and Non-Claims

This brief makes no evidence-quality ranking, candidate-quality ranking, lifecycle policy recommendation, promotion or demotion implication, paper/live eligibility implication, fast-track conclusion, outcome-learning conclusion, REC claim, reconciliation claim, runtime authority, or deployment authority (`outputs/Q06.json`).

`Q06` records zero LCH integrity rows across the LCH reference, transition-graph, approval-completeness, and fast-track-completeness integrity views. It also records zero fast-track rows, zero non-retrospective rows, zero linked advisory refs, zero strong-candidate criteria refs, and zero unknown evidence types (`outputs/Q06.json`).

This package does not modify LCH artifacts, source evidence, schemas, validators, central query-layer files, registry rows, WP-9f outputs or conclusions, WP-9g outputs or conclusions, outcome-ledger structures, reconciliation structures, promotion policy, deployment artifacts, runtime behavior, automated promotion, live scaling, or protected execution paths.

## 9. Forward Observations

WP-9h establishes the evidence-artifact-type lifecycle consumer axis. It complements WP-9f's per-candidate baseline and WP-9g's per-transition-edge baseline (`outputs/Q05.json`).

The current lifecycle consumer set now has three single-axis consumers: per-candidate path, per-transition edge, and per-evidence-artifact-type lineage. That prepares a later lifecycle consumer synthesis, but this brief does not produce that synthesis.

WP-9h cannot yet answer lifecycle synthesis, fast-track versus standard-track comparison, paper/live lifecycle behavior, evidence quality scoring, outcome-learning behavior, strategy-performance links, lifecycle policy, or promotion thresholds. None of those claims are supported by the current committed LCH corpus (`outputs/Q05.json`, `outputs/Q06.json`).
