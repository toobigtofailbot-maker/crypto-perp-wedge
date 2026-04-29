# Lifecycle Per-Transition-Edge Consumer Brief (WP-9g)

**Date:** 2026-04-29
**Scope:** Second bounded lifecycle consumer over the populated `LCH-0001` through `LCH-0030` corpus.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-lifecycle_per_transition_edge_consumer/`.
**Primary semantic source:** `lifecycle_changes`, `v_lifecycle_change_overview`, `v_lifecycle_state_transitions`, and LCH integrity views through the central query layer.
**Does not introduce:** LCH instances, schema changes, validator changes, query-layer changes, registry changes, evidence-artifact changes, outcome-ledger content, REC content, reconciliation content, promotion policy, deployment artifacts, or runtime behavior.
**Does not recommend:** Policy action, promotion/demotion action, paper/live eligibility, fast-track action, runtime influence, or outcome-learning conclusion.

## 1. Purpose

This brief is the second bounded consumer over the populated lifecycle layer. It reads committed `LCH-0001` through `LCH-0030` through the central query layer and segments the current lifecycle corpus by per-transition-edge characteristics.

The purpose is diagnostic: show what the lifecycle layer reveals when the unit of analysis is the transition edge rather than the candidate path. This package establishes the per-transition-edge lifecycle consumer pattern, following WP-9f's per-candidate lifecycle consumer.

## 2. Scope and Sources

The committed scope is `LCH-0001` through `LCH-0030`, covering candidates H-001 through H-010 (`outputs/Q01.json`, `outputs/Q05.json`). The query bundle reads:

- `lifecycle_changes`
- `v_lifecycle_change_overview`
- `v_lifecycle_state_transitions`
- `v_integrity_lifecycle_change_refs`
- `v_integrity_lifecycle_transition_graph`
- `v_integrity_lifecycle_approval_completeness`
- `v_integrity_lifecycle_fast_track_completeness`

The reproducible bundle is stored under `research/briefs/2026-04-lifecycle_per_transition_edge_consumer/`. The helper runs SQL through `tools.research_query.run --sql`; it does not register local DuckDB relations, bypass the central query layer, or read LCH files directly.

This brief does not modify LCH instances, source evidence artifacts, schemas, validators, registry rows, query-layer files, runtime paths, policy artifacts, protected execution paths, or WP-9f brief/output files.

## 3. Query Bundle

The bundle follows the current repo-local diagnostic idiom: `run_all_queries.py` iterates `queries/Q*.sql` and writes `outputs/Q01.json` through `outputs/Q06.json`.

- `queries/Q01.sql` -> `outputs/Q01.json`: current lifecycle corpus inventory by transition edge.
- `queries/Q02.sql` -> `outputs/Q02.json`: per-transition-edge count and candidate coverage.
- `queries/Q03.sql` -> `outputs/Q03.json`: per-transition-edge artifact timestamp gap characteristics.
- `queries/Q04.sql` -> `outputs/Q04.json`: per-transition-edge evidence artifact distribution.
- `queries/Q05.sql` -> `outputs/Q05.json`: transition-edge comparison and WP-9f baseline alignment.
- `queries/Q06.sql` -> `outputs/Q06.json`: integrity and boundary snapshot.

All factual claims below cite those stored outputs.

## 4. Per-Transition-Edge Coverage Summary

The current lifecycle corpus contains 30 LCH rows across 3 transition edges and 10 candidates (`outputs/Q01.json`, `outputs/Q05.json`). Each transition edge has exactly 10 rows and covers all 10 candidates (`outputs/Q02.json`, `outputs/Q05.json`).

The covered transition edges are (`outputs/Q02.json`):

```text
proposed->in_research
in_research->research_concluded
research_concluded->archived
```

The edge-level view is consistent with WP-9f's per-candidate uniform-path finding: the current LCH corpus has 10 candidates, 30 LCH rows, 3 transition edges, 1 distinct path, and all edges cover all candidates (`outputs/Q05.json`).

## 5. Edge Uniformity Finding

All three retrospective edges cover all ten candidates (`outputs/Q02.json`, `outputs/Q05.json`).

This is a structural finding about the committed H-001 through H-010 backfill. It is not evidence that future candidates will traverse all three edges. It does not say anything about paper, live, fast-track, halted, recovery, or promotion paths because none are present in the committed LCH corpus (`outputs/Q05.json`, `outputs/Q06.json`).

The current transition-edge coverage summary has 3 distinct transition edges, 10 rows per transition edge, and 10 candidates represented on each edge (`outputs/Q02.json`, `outputs/Q05.json`).

## 6. Edge Timing Characteristics

Timing fields in this brief are based on artifact commit-introduction timestamps used by retrospective LCH `decided_at`. Treat gaps as artifact timestamp gaps only. Do not read them as real operational lifecycle durations.

`Q03` reports a fixed timing interpretation of `artifact_commit_timestamp_gap_not_operational_duration` for the two gap-bearing target edges (`outputs/Q03.json`). The `in_research->research_concluded` target edge has 10 candidate-level gaps and zero negative gaps (`outputs/Q03.json`). The `research_concluded->archived` target edge has 10 candidate-level gaps, 10 negative gaps, and 10 archive-before-research artifact timestamp observations (`outputs/Q03.json`). Those archival-edge values are artifact timestamp ordering effects, not lifecycle contradictions and not evidence about historical process speed.

The transition-edge timing view is useful for checking artifact timestamp ordering and designing future forward-flow timing analyses, but it is not a reliable measure of historical lifecycle duration.

This brief does not infer process speed, research quality, candidate quality, operational readiness, promotion readiness, or evidence strength from these timestamp gaps.

## 7. Evidence Artifact Distribution by Edge

The `proposed->in_research` edge is supported by 10 HYPOTHESIS-path evidence refs (`outputs/Q04.json`). The `in_research->research_concluded` edge is supported by 10 REP evidence refs (`outputs/Q04.json`). The `research_concluded->archived` edge is supported by 10 DEC-path evidence refs, plus 1 DCH ref and 1 REL ref (`outputs/Q04.json`).

H-005 adds the only current DCH/REL exception on the archival edge. `Q04` surfaces the archival-edge exception refs as `DCH-0001 | REL-0001 | research/decisions/DEC-0005.md` (`outputs/Q04.json`). No edge has `other` evidence refs (`outputs/Q04.json`).

This edge-level evidence distribution does not change any candidate status, historical decision, cited evidence artifact, or runtime behavior.

## 8. Boundary and Non-Claims

This brief makes no lifecycle policy recommendation. It has no promotion or demotion implication, no paper/live eligibility implication, no fast-track conclusion, no outcome-learning conclusion, no REC claim, no reconciliation claim, no runtime authority, and no deployment authority (`outputs/Q06.json`).

`Q06` records zero LCH integrity rows across the LCH reference, transition-graph, approval-completeness, and fast-track-completeness integrity views. It also records zero fast-track rows, zero non-retrospective rows, zero linked advisory refs, and zero strong-candidate criteria refs (`outputs/Q06.json`).

This package does not modify LCH artifacts, source evidence, schemas, validators, central query-layer files, registry rows, WP-9f outputs or conclusions, outcome-ledger structures, reconciliation structures, promotion policy, deployment artifacts, runtime behavior, automated promotion, live scaling, or protected execution paths.

## 9. Forward Observations

WP-9g establishes the transition-edge lifecycle consumer axis. It complements WP-9f's per-candidate baseline and motivates the remaining per-evidence-artifact-type consumer before eventual lifecycle synthesis after multiple consumer axes exist.

WP-9g cannot yet answer evidence-artifact-type lineage synthesis, fast-track versus standard-track comparison, paper/live lifecycle behavior, outcome-learning behavior, strategy-performance links, lifecycle policy, or promotion thresholds. None of those claims are supported by the current committed LCH corpus (`outputs/Q05.json`, `outputs/Q06.json`).
