# Lifecycle Consumer Set Synthesis (WP-9i)

**Date:** 2026-04-30
**Scope:** Bounded synthesis over the completed three-consumer lifecycle set for the populated `LCH-0001` through `LCH-0030` corpus.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-lifecycle_consumer_set_synthesis/` plus the WP-9f, WP-9g, and WP-9h committed lifecycle consumer outputs.
**Primary semantic source:** `lifecycle_changes`, `v_lifecycle_change_overview`, `v_lifecycle_state_transitions`, and LCH integrity views through the central query layer.
**Does not introduce:** LCH instances, schema changes, validator changes, query-layer changes, registry changes, evidence-artifact changes, outcome-ledger content, REC content, reconciliation content, promotion policy, deployment artifacts, or runtime behavior.
**Does not recommend:** Policy action, promotion/demotion action, paper/live eligibility, fast-track action, runtime influence, evidence-quality ranking, candidate-quality ranking, or outcome-learning conclusion.

## 1. Purpose

This brief synthesizes the three bounded lifecycle consumers now committed over the populated lifecycle layer:

- WP-9f: per-candidate lifecycle path
- WP-9g: per-transition-edge characteristics
- WP-9h: per-evidence-artifact-type lineage

It reads the current committed LCH state through the central query layer and references the prior committed consumer outputs. It is descriptive only. It consolidates what the current lifecycle layer supports, what it does not support, and which dependencies remain before any later outcome-learning, REC/reconciliation, promotion-policy, lifecycle stability-lock, or forward-flow work.

## 2. Scope and Sources

The committed LCH scope is `LCH-0001` through `LCH-0030`, covering historical candidates H-001 through H-010 (`outputs/Q01.json`, `outputs/Q03.json`). The source consumer set is:

- WP-9f: `research/briefs/2026-04-lifecycle_per_candidate_consumer.md` and `research/briefs/2026-04-lifecycle_per_candidate_consumer/outputs/`
- WP-9g: `research/briefs/2026-04-lifecycle_per_transition_edge_consumer.md` and `research/briefs/2026-04-lifecycle_per_transition_edge_consumer/outputs/`
- WP-9h: `research/briefs/2026-04-lifecycle_per_evidence_artifact_type_consumer.md` and `research/briefs/2026-04-lifecycle_per_evidence_artifact_type_consumer/outputs/`

The WP-9i query bundle reads:

- `lifecycle_changes`
- `v_lifecycle_change_overview`
- `v_lifecycle_state_transitions`
- `v_integrity_lifecycle_change_refs`
- `v_integrity_lifecycle_transition_graph`
- `v_integrity_lifecycle_approval_completeness`
- `v_integrity_lifecycle_fast_track_completeness`
- all currently discovered `v_integrity_*` views for the integrity snapshot

The reproducible bundle is stored under `research/briefs/2026-04-lifecycle_consumer_set_synthesis/`. The helper runs SQL through `tools.research_query.run --sql`; it does not register local DuckDB relations, bypass the central query layer, or read LCH files directly.

This package does not modify LCH instances, source evidence artifacts, schemas, validators, registry rows, query-layer files, runtime paths, policy artifacts, protected execution paths, or WP-9f / WP-9g / WP-9h brief, query, output, or helper files.

## 3. Query Bundle

The bundle follows the repo-local lifecycle consumer idiom: `run_all_queries.py` iterates `queries/Q*.sql` and writes `outputs/Q01.json` through `outputs/Q06.json`.

- `queries/Q01.sql` -> `outputs/Q01.json`: current lifecycle corpus synthesis inventory.
- `queries/Q02.sql` -> `outputs/Q02.json`: consumer-axis comparison matrix.
- `queries/Q03.sql` -> `outputs/Q03.json`: cross-axis structural consistency.
- `queries/Q04.sql` -> `outputs/Q04.json`: timing and retrospective-boundary synthesis.
- `queries/Q05.sql` -> `outputs/Q05.json`: forward-readiness and missing-capability matrix.
- `queries/Q06.sql` -> `outputs/Q06.json`: integrity and boundary snapshot.

All factual claims below cite those stored outputs or the prior consumer output bundles.

## 4. Three-Axis Consumer Summary

The current lifecycle corpus contains 30 LCH rows across 10 candidates, 3 transition edges, 32 evidence refs, 5 known evidence artifact types, and 0 unknown evidence refs (`outputs/Q01.json`). All three consumers read the same `LCH-0001` through `LCH-0030` corpus (`outputs/Q01.json`; `outputs/Q02.json`).

WP-9f exposes the per-candidate axis: 10 candidates share 1 uniform retrospective path (`outputs/Q02.json`; `research/briefs/2026-04-lifecycle_per_candidate_consumer/outputs/Q02.json`; `research/briefs/2026-04-lifecycle_per_candidate_consumer/outputs/Q05.json`).

WP-9g exposes the per-transition-edge axis: 3 transition edges each contain 10 rows / 10 candidates (`outputs/Q02.json`; `research/briefs/2026-04-lifecycle_per_transition_edge_consumer/outputs/Q02.json`; `research/briefs/2026-04-lifecycle_per_transition_edge_consumer/outputs/Q05.json`).

WP-9h exposes the per-evidence-artifact-type axis: 32 evidence refs classify into 5 known evidence artifact types, with 0 unknown refs (`outputs/Q01.json`; `outputs/Q02.json`; `research/briefs/2026-04-lifecycle_per_evidence_artifact_type_consumer/outputs/Q02.json`; `research/briefs/2026-04-lifecycle_per_evidence_artifact_type_consumer/outputs/Q06.json`).

All three axes are mutually consistent in the current corpus: the structural consistency row passes all checks (`outputs/Q03.json`).

## 5. Cross-Axis Structural Findings

The current lifecycle corpus covers 10 historical candidates and each candidate has 3 lifecycle transitions (`outputs/Q01.json`; `outputs/Q03.json`). All candidates share the same retrospective path (`outputs/Q03.json`):

```text
proposed -> in_research -> research_concluded -> archived
```

The stored edge sequence is:

```text
proposed->in_research | in_research->research_concluded | research_concluded->archived
```

Each of the three transition edges covers all 10 candidates (`outputs/Q03.json`). Evidence lineage aligns with the transition structure: HYPOTHESIS-path refs attach to `proposed->in_research`, REP refs attach to `in_research->research_concluded`, and DEC-path refs attach to `research_concluded->archived` (`outputs/Q03.json`; `research/briefs/2026-04-lifecycle_per_evidence_artifact_type_consumer/outputs/Q03.json`).

H-005 is the only current DCH/REL cross-family archival exception, and there are no unknown evidence refs in the current corpus (`outputs/Q01.json`; `outputs/Q03.json`).

## 6. Timing and Retrospective Boundary Synthesis

The timing fields in the lifecycle consumer set are retrospective artifact commit-introduction timestamps. Timing gaps are artifact timestamp gaps only. They are not operational lifecycle durations (`outputs/Q04.json`; `research/briefs/2026-04-lifecycle_per_candidate_consumer/outputs/Q03.json`; `research/briefs/2026-04-lifecycle_per_transition_edge_consumer/outputs/Q03.json`).

The archival edge has 10 negative artifact timestamp gaps in the current retrospective corpus (`outputs/Q04.json`). These negative archival-edge gaps are artifact timestamp ordering effects, not lifecycle contradictions and not evidence about historical process speed (`outputs/Q04.json`; `research/briefs/2026-04-lifecycle_per_transition_edge_consumer/outputs/Q03.json`).

The lifecycle consumer set can validate timestamp availability and artifact ordering characteristics for the retrospective backfill, but it cannot measure historical operational lifecycle duration. Do not infer process speed, research quality, candidate quality, operational readiness, promotion readiness, or evidence strength from timing (`outputs/Q04.json`).

## 7. H-005 Exception Synthesis

H-005 is the only current cross-family lifecycle evidence exception in the committed LCH corpus (`outputs/Q03.json`; `research/briefs/2026-04-lifecycle_per_evidence_artifact_type_consumer/outputs/Q04.json`; `research/briefs/2026-04-lifecycle_per_evidence_artifact_type_consumer/outputs/Q05.json`).

The exception is attached to the archival transition, `research_concluded->archived`, and links DEC-path, DCH, and REL evidence (`outputs/Q03.json`; `research/briefs/2026-04-lifecycle_per_evidence_artifact_type_consumer/outputs/Q03.json`; `research/briefs/2026-04-lifecycle_per_evidence_artifact_type_consumer/outputs/Q04.json`).

This is a descriptive lineage observation only. Do not infer that H-005 is higher quality, lower quality, more important, policy-relevant, promotion-relevant, or operationally different because it has extra evidence refs.

## 8. Current Support vs Missing Capabilities

The current lifecycle consumer set supports descriptive lifecycle analysis only (`outputs/Q05.json`). Supported descriptive capabilities are:

- current LCH corpus inventory
- per-candidate retrospective path view
- per-transition-edge aggregate view
- evidence-artifact-type lineage view
- H-005 evidence exception identification
- lifecycle integrity and boundary validation

The current corpus does not support future candidate forward-flow behavior, paper/live lifecycle behavior, fast-track versus standard-track comparison, halted/recovery behavior, outcome-learning linkage, REC/reconciliation linkage, promotion/demotion threshold inference, evidence-quality scoring, or runtime/deployment authority (`outputs/Q05.json`).

Every capability row in the WP-9i support matrix has `policy_authority = false` (`outputs/Q05.json`).

## 9. Boundary and Non-Claims

This brief makes no lifecycle policy recommendation, no promotion/demotion implication, no paper/live eligibility implication, no fast-track conclusion, no outcome-learning conclusion, no REC or reconciliation claim, no evidence-quality ranking, no candidate-quality ranking, no runtime authority, and no deployment authority (`outputs/Q04.json`; `outputs/Q05.json`; `outputs/Q06.json`).

`Q06` records zero rows for the four lifecycle integrity views and zero rows across all 15 discovered `v_integrity_*` views. It also records zero fast-track rows, zero non-retrospective rows, zero linked advisory refs, zero strong-candidate criteria refs, 30 LCH rows, 32 evidence refs, 0 unknown evidence types, and 3 source consumer briefs (`outputs/Q06.json`).

This package does not modify LCH artifacts, source evidence, schemas, validators, central query-layer files, registry rows, WP-9f outputs or conclusions, WP-9g outputs or conclusions, WP-9h outputs or conclusions, outcome-ledger structures, reconciliation structures, promotion policy, deployment artifacts, runtime behavior, automated promotion, live scaling, or protected execution paths.

## 10. Forward Observations

WP-9i synthesizes the completed lifecycle consumer set over per-candidate path, per-transition-edge characteristics, and per-evidence-artifact-type lineage (`outputs/Q02.json`; `outputs/Q03.json`).

The project can next choose between lifecycle stability lock, outcome-learning architecture/scaffold, REC/reconciliation architecture, or a forward-flow lifecycle package for future candidates. This synthesis does not choose among those options and does not commit scope (`outputs/Q05.json`).

The synthesis clarifies that outcome-learning and promotion semantics require additional architecture decisions and artifacts before implementation (`outputs/Q05.json`). WP-9i cannot yet answer outcome performance linkage, live/paper behavior, fast-track behavior, promotion policy, automated strategy adjustment, or deployment decisions (`outputs/Q05.json`).

## 11. Artifacts In This Directory

- `queries/Q01.sql` through `queries/Q06.sql`: exact read-only SQL used for this brief
- `outputs/Q01.json` through `outputs/Q06.json`: committed query results
- `run_all_queries.py`: convenience helper to regenerate the outputs through the central read-only query CLI
