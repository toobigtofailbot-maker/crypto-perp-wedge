# SSS v2 Advisory-Lineage Consumer 01

**Date:** 2026-04-25
**Scope:** Second bounded consumer brief over the committed SSS v2 advisory-lineage instance `SSS-0003`.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-sss_v2_advisory_lineage_consumer_01/`.
**Primary semantic source:** `v_shadow_signal_summaries_v2_overview` over committed `SSS-0003`.
**Structural comparison context only:** WP-7v advisory-lineage v1 readout and WP-8b advisory-source v2 consumer.
**Does not introduce:** A new SSS instance, schema changes, validator changes, query-layer changes, helper changes, advisory-artifact changes, fixtures, shadow rows, or runtime behavior.
**Does not recommend:** Policy action, runtime influence, override action, source ranking, lineage ranking, cadence, or cross-v2-instance synthesis.

## 1. Purpose

This brief is the second bounded downstream consumer over committed SSS v2 content. It consumes `SSS-0003`, the advisory-lineage-form v2 summary over the committed overlay-shadow corpus, and records only what the committed artifact shows at the current floor-limited corpus size.

The brief does not create or modify any SSS instance. It does not re-derive signal meaning from raw overlay-shadow rows. It reads the already committed v2 instance through the canonical central query-layer surface and records the current floor-limited evidence state without changing any schema, validator, helper, query-layer, or protected runtime path.

## 2. Evidence Source

The primary evidence source for this package is `SSS-0003` as exposed through `v_shadow_signal_summaries_v2_overview`. Integrity is checked through `v_integrity_shadow_signal_summary_v2_derivation`, which returns an empty result for the current committed v2 summaries.

WP-7v is used only for structural comparison context. Its v1 advisory-lineage readout consumed `SSS-0001` through `v_shadow_signal_summaries_overview`, where lineage rows remained split by overlay-input fixture identity.

WP-8b is also context only. It consumed `SSS-0002`, the advisory-source-only v2 instance. WP-8b used a local temporary DuckDB relation workaround because central SSS v2 query-layer support did not yet exist. That workaround is obsolete for this package. WP-8e uses the central v2 query-layer views introduced after WP-8b.

## 3. Query Bundle

The bundle follows the current repo-local diagnostic idiom: `run_all_queries.py` iterates `queries/Q*.sql` and writes `outputs/Q01.json` through `outputs/Q05.json`.

- `Q01`: lineage-level overview of committed `SSS-0003` rows through `v_shadow_signal_summaries_v2_overview`
- `Q02`: explicit floor-status summary for `SSS-0003`
- `Q03`: structural comparison between `SSS-0003` and the WP-7v v1 advisory-lineage readout shape
- `Q04`: structural comparison between advisory-source-only `SSS-0002` and advisory-lineage-form `SSS-0003`
- `Q05`: descriptive forward observations only

All five queries use central query-layer views. The helper calls `tools.research_query.run --sql` and does not locally register SSS v2 files as temporary relations.

## 4. What SSS-0003 Shows

`SSS-0003` is an advisory-lineage-form v2 summary with three segment keys: `advisory_source`, `source_bucket_mapping_id`, and `source_pre_gate_advisory_snapshot_id` (`Q01`, `outputs/Q01.json`).

It realizes four lineage segments:

- `BMAP / BMAP-0001 / null`: `match_count = 0`, `mismatch_count = 3`, `abstention_count = 0`, `observation_count = 3`, `rate_denominator = 3`
- `BMAP / BMAP-0002 / null`: `match_count = 2`, `mismatch_count = 0`, `abstention_count = 0`, `observation_count = 2`, `rate_denominator = 2`
- `PGAS / BMAP-0001 / PGAS-0002`: `match_count = 0`, `mismatch_count = 3`, `abstention_count = 0`, `observation_count = 3`, `rate_denominator = 3`
- `PGAS / BMAP-0002 / PGAS-0003`: `match_count = 2`, `mismatch_count = 0`, `abstention_count = 0`, `observation_count = 2`, `rate_denominator = 2`

All four segments remain below the locked floor of 10 observations. Agreement and disagreement rates are therefore `null` for every segment, and every segment has `signal_outcome = INSUFFICIENT_EVIDENCE` (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`).

## 5. Comparison With WP-7v

WP-7v consumed the advisory-artifact-lineage slice as a v1 readout over `SSS-0001`. That readout exposed the same four realized lineages, but each lineage remained split into fixture-specific rows (`canonical` and `_02`) because the committed v1 summary retained its broader segment form.

`SSS-0003` changes the structure by making advisory lineage the dedicated v2 instance grain. `Q03` shows one v2 row per realized lineage, while the v1 readout has two fixture-split rows per lineage. Total observation counts match by lineage, and both forms remain fully below floor.

The current analytic difference is therefore minimal. V2 structurally exposes the lineage-form instance directly, but the current corpus still supports only insufficiency statements.

## 6. Comparison With WP-8b / SSS-0002

WP-8b consumed `SSS-0002`, an advisory-source-only v2 instance. `SSS-0003` uses the same corpus window and the same derivation method, but it exposes a finer advisory-lineage grain (`Q04`, `outputs/Q04.json`).

The structural comparison is narrow:

- `SSS-0002`: two advisory-source rows, one for `BMAP` and one for `PGAS`
- `SSS-0003`: four advisory-lineage rows, keyed by source plus upstream artifact identifiers
- both cover `OSH-0001` through `OSH-0010`
- both remain fully below floor, with null usable rates and only `INSUFFICIENT_EVIDENCE` outcomes

This package therefore demonstrates canonical central-query-layer consumption of lineage-form SSS v2 content, not stronger signal evidence.

## 7. Honest Floor-Crossing Record

No realized `SSS-0003` segment crosses the locked floor of 10 observations (`Q02`, `outputs/Q02.json`).

- segment count: `4`
- above-floor segments: `0`
- below-floor segments: `4`
- null-rate segments: `4`
- insufficient-evidence outcomes: `4`

The honest current record is that advisory-lineage SSS v2 is instantiated and consumable, while the present corpus remains too small for sufficient signal classification.

## 8. Non-Claims

This package does not claim:

- policy, runtime, override, OMS, risk, or execution authority
- any source or lineage ranking
- any cadence or corpus-growth directive
- any schema, validator, query-layer, or helper change
- any new SSS instance beyond the already committed `SSS-0003`
- any cross-v2-instance synthesis

The consumer is descriptive only. It records what the committed v2 artifact shows and what it still cannot support.

## 9. Forward Observation

The second v2 consumer supports descriptive forward observations only (`Q05`, `outputs/Q05.json`):

- central SSS v2 query-layer support is now load-bearing for downstream consumers
- all current v2 segments remain below the locked floor
- corpus growth remains the binding evidence constraint for stronger segment-level signal classifications
- possible later directions include an overlay-input-fixture v2 instance, a third bounded v2 consumer, or later v2 synthesis after additional committed evidence

These observations are not recommendations, rankings, schedules, or scope commitments.

## 10. Explicit Conclusion

SSS v2 has now been consumed over advisory-source and advisory-lineage axes. `SSS-0002` demonstrated advisory-source-only v2 consumption, and `SSS-0003` now demonstrates advisory-lineage-form v2 consumption through the canonical central query-layer surface.

Both remain floor-limited. WP-8e demonstrates central-query-layer consumability of lineage-form SSS v2 content, not sufficient signal evidence.

## 11. Artifacts In This Directory

- `queries/Q01..Q05*.sql`: exact read-only SQL used for this brief
- `outputs/Q01.json` through `outputs/Q05.json`: committed query results
- `run_all_queries.py`: convenience helper to regenerate the outputs through the central read-only query CLI
