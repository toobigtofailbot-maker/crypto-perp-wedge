# Lifecycle Per-Candidate Consumer Brief (WP-9f)

**Date:** 2026-04-29
**Scope:** First bounded lifecycle consumer over the populated `LCH-0001` through `LCH-0030` corpus.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-lifecycle_per_candidate_consumer/`.
**Primary semantic source:** `lifecycle_changes`, `v_lifecycle_change_overview`, `v_lifecycle_state_transitions`, and LCH integrity views through the central query layer.
**Does not introduce:** LCH instances, schema changes, validator changes, query-layer changes, registry changes, evidence-artifact changes, outcome-ledger content, REC content, reconciliation content, promotion policy, deployment artifacts, or runtime behavior.
**Does not recommend:** Policy action, promotion/demotion action, paper/live eligibility, fast-track action, runtime influence, or outcome-learning conclusion.

## 1. Purpose

This brief is the first bounded consumer over the populated lifecycle layer. It reads committed `LCH-0001` through `LCH-0030` through the central query layer and segments the current lifecycle corpus by per-candidate lifecycle path.

The purpose is diagnostic: prove that the lifecycle layer is queryable as analytical content, not only valid as a structural artifact family. This package establishes the per-candidate lifecycle consumer pattern for later bounded consumers over other lifecycle axes.

## 2. Scope and Sources

The committed scope is `LCH-0001` through `LCH-0030`, covering candidates H-001 through H-010 (`outputs/Q01.json`, `outputs/Q05.json`). The query bundle reads:

- `lifecycle_changes`
- `v_lifecycle_change_overview`
- `v_lifecycle_state_transitions`
- `v_integrity_lifecycle_change_refs`
- `v_integrity_lifecycle_transition_graph`
- `v_integrity_lifecycle_approval_completeness`
- `v_integrity_lifecycle_fast_track_completeness`

The reproducible bundle is stored under `research/briefs/2026-04-lifecycle_per_candidate_consumer/`. The helper runs SQL through `tools.research_query.run --sql`; it does not register local DuckDB relations, bypass the central query layer, or read LCH files directly.

This brief does not modify LCH instances, source evidence artifacts, schemas, validators, registry rows, query-layer files, runtime paths, policy artifacts, or protected execution paths.

## 3. Query Bundle

The bundle follows the current repo-local diagnostic idiom: `run_all_queries.py` iterates `queries/Q*.sql` and writes `outputs/Q01.json` through `outputs/Q06.json`.

- `queries/Q01.sql` -> `outputs/Q01.json`: current lifecycle corpus inventory.
- `queries/Q02.sql` -> `outputs/Q02.json`: per-candidate ordered lifecycle path.
- `queries/Q03.sql` -> `outputs/Q03.json`: per-candidate artifact timestamp gaps.
- `queries/Q04.sql` -> `outputs/Q04.json`: per-candidate evidence artifact distribution.
- `queries/Q05.sql` -> `outputs/Q05.json`: path uniformity and transition coverage summary.
- `queries/Q06.sql` -> `outputs/Q06.json`: integrity and boundary snapshot.

All factual claims below cite those stored outputs.

## 4. Per-Candidate Lifecycle Path Summary

The current lifecycle corpus contains 30 LCH rows across 10 candidates (`outputs/Q01.json`, `outputs/Q05.json`). Each candidate has exactly three transitions (`outputs/Q02.json`, `outputs/Q05.json`).

Every candidate follows the same ordered path (`outputs/Q02.json`):

```text
proposed -> in_research -> research_concluded -> archived
```

The stored transition-edge form is:

```text
proposed->in_research | in_research->research_concluded | research_concluded->archived
```

This is expected for the current corpus because `LCH-0001` through `LCH-0030` are a retrospective backfill for historical concluded / NO-GO candidates H-001 through H-010.

## 5. Path Uniformity Finding

All ten candidates follow the same retrospective path (`outputs/Q02.json`, `outputs/Q05.json`).

This is a structural finding about the committed backfill. It is not evidence that future candidates will follow the same path. It does not say anything yet about paper, live, fast-track, halted, or recovery paths because none are present in the committed LCH corpus (`outputs/Q05.json`, `outputs/Q06.json`).

The current transition coverage summary has 3 distinct transition edges, 10 rows per transition edge, and 1 distinct per-candidate path (`outputs/Q05.json`).

## 6. Timing Characteristics

Timing fields in this brief are based on artifact commit-introduction timestamps used by retrospective LCH `decided_at`. Treat gaps as artifact timestamp gaps only. Do not read them as real operational lifecycle durations.

`Q03` reports a fixed timing interpretation of `artifact_commit_timestamp_gap_not_operational_duration` for every candidate (`outputs/Q03.json`). It also shows that the archival artifact timestamp precedes the research-conclusion artifact timestamp for all ten candidates in the current backfill (`outputs/Q03.json`). That is an artifact timestamp ordering effect, not a lifecycle contradiction and not evidence about historical process speed.

The current timing view is useful for checking timestamp consistency and for designing future forward-flow timing analyses, but it is not a reliable measure of actual historical lifecycle duration.

This brief does not infer process speed, research quality, candidate quality, operational readiness, promotion readiness, or evidence strength from these timestamp gaps.

## 7. Evidence Artifact Distribution

Every candidate cites one HYPOTHESIS path, one REP ID, and one DEC path (`outputs/Q04.json`).

H-005 additionally cites `DCH-0001` and `REL-0001` on the archival transition represented by `LCH-0015`; `Q04` surfaces the H-005 archival exception refs as `DCH-0001 | REL-0001 | research/decisions/DEC-0005.md` (`outputs/Q04.json`). Other candidates have zero DCH refs and zero REL refs (`outputs/Q04.json`).

This makes H-005 the only current cross-family lifecycle evidence exception in the committed LCH corpus. The exception does not change H-005 status, the historical H-005 decision, the cited evidence artifacts, or any runtime behavior.

## 8. Boundary and Non-Claims

This brief makes no lifecycle policy recommendation. It has no promotion or demotion implication, no paper/live eligibility implication, no fast-track conclusion, no outcome-learning conclusion, no REC claim, no reconciliation claim, no runtime authority, and no deployment authority (`outputs/Q06.json`).

`Q06` records zero LCH integrity rows across the LCH reference, transition-graph, approval-completeness, and fast-track-completeness integrity views. It also records zero fast-track rows, zero non-retrospective rows, zero linked advisory refs, and zero strong-candidate criteria refs (`outputs/Q06.json`).

This package does not modify LCH artifacts, source evidence, schemas, validators, central query-layer files, registry rows, outcome-ledger structures, reconciliation structures, promotion policy, deployment artifacts, runtime behavior, automated promotion, live scaling, or protected execution paths.

## 9. Forward Observations

WP-9f establishes the per-candidate lifecycle consumer pattern and gives a baseline for future forward-flow candidates. It also motivates later bounded lifecycle consumers over:

- per-transition-edge behavior
- per-evidence-artifact-type distribution

Those later consumers would prepare an eventual lifecycle synthesis after multiple consumer axes exist.

WP-9f cannot yet answer transition-edge-level timing distribution beyond candidate path summary, evidence-artifact-type lineage synthesis, fast-track versus standard-track comparison, paper/live lifecycle behavior, outcome-learning behavior, or strategy-performance links. None of those claims are supported by the current committed LCH corpus (`outputs/Q05.json`, `outputs/Q06.json`).
