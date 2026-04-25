# SSS v2 Fixture Consumer 01

**Date:** 2026-04-25
**Scope:** Third bounded consumer brief over the committed SSS v2 fixture-identity instance `SSS-0004`.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-sss_v2_fixture_consumer_01/`.
**Primary semantic source:** `v_shadow_signal_summaries_v2_overview` over committed `SSS-0004`.
**Structural comparison context only:** WP-7u fixture-identity v1 readout, WP-8b advisory-source v2 consumer, and WP-8e advisory-lineage v2 consumer.
**Does not introduce:** A new SSS instance, schema changes, validator changes, query-layer changes, helper changes, advisory-artifact changes, fixtures, shadow rows, or runtime behavior.
**Does not recommend:** Policy action, runtime influence, override action, source ranking, fixture ranking, cadence, or cross-v2-instance synthesis.

## 1. Purpose

This brief is the third bounded downstream consumer over committed SSS v2 content. It consumes `SSS-0004`, the fixture-identity-form v2 summary over the committed overlay-shadow corpus, and records only what the committed artifact shows at the current floor-limited corpus size.

The brief does not create or modify any SSS instance. It does not re-derive signal meaning from raw overlay-shadow rows. It reads the already committed v2 instance through the canonical central query-layer surface and records the current floor-limited evidence state without changing any schema, validator, helper, query-layer, or protected runtime path.

## 2. Evidence Source

The primary evidence source for this package is `SSS-0004` as exposed through `v_shadow_signal_summaries_v2_overview`. Integrity is checked through `v_integrity_shadow_signal_summary_v2_derivation`, which returns an empty result for the current committed v2 summaries.

WP-7u is used only for structural comparison context. Its v1 fixture-identity readout consumed `SSS-0001` through `v_shadow_signal_summaries_overview`, where fixture rows remained sliced out of the broader advisory-lineage and fixture-aware summary form.

WP-8b and WP-8e are also context only. WP-8b consumed `SSS-0002`, the advisory-source-only v2 instance. WP-8e consumed `SSS-0003`, the advisory-lineage-form v2 instance, through the central v2 query-layer views. WP-8g follows the WP-8e central-query-layer pattern and does not use any local temporary SSS v2 relation workaround.

## 3. Query Bundle

The bundle follows the current repo-local diagnostic idiom: `run_all_queries.py` iterates `queries/Q*.sql` and writes `outputs/Q01.json` through `outputs/Q05.json`.

- `Q01`: fixture-level overview of committed `SSS-0004` rows through `v_shadow_signal_summaries_v2_overview`
- `Q02`: explicit floor-status summary for `SSS-0004`
- `Q03`: structural comparison between `SSS-0004` and the WP-7u v1 fixture readout shape
- `Q04`: structural comparison across advisory-source `SSS-0002`, advisory-lineage `SSS-0003`, and fixture-identity `SSS-0004`
- `Q05`: descriptive forward observations only

All five queries use central query-layer views. The helper calls `tools.research_query.run --sql` and does not locally register SSS v2 files as temporary relations.

## 4. What SSS-0004 Shows

`SSS-0004` is a fixture-identity-form v2 summary with one segment key: `fixture_identity` (`Q01`, `outputs/Q01.json`).

It realizes two fixture segments:

- `_02`: `match_count = 2`, `mismatch_count = 2`, `abstention_count = 0`, `observation_count = 4`, `rate_denominator = 4`
- `canonical`: `match_count = 2`, `mismatch_count = 4`, `abstention_count = 0`, `observation_count = 6`, `rate_denominator = 6`

Both segments remain below the locked floor of 10 observations. Agreement and disagreement rates are therefore `null` for both segments, and both segments have `signal_outcome = INSUFFICIENT_EVIDENCE` (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`).

No agreement-rate inference is supported at the current corpus size.

## 5. Comparison With WP-7u

WP-7u consumed the fixture-identity slice as a v1 readout over `SSS-0001`. That readout exposed the same two fixture identities, but each fixture identity remained represented by four rows split across advisory lineage because the committed v1 summary retained its broader segment form.

`SSS-0004` changes the structure by making fixture identity the dedicated v2 instance grain. `Q03` shows one v2 row per fixture identity, while the v1 readout has four fixture-split rows per fixture identity. Total observation counts, rate denominators, match counts, mismatch counts, and abstention counts match by fixture identity.

The current analytic difference is therefore minimal. V2 structurally exposes the fixture-form instance directly, but both fixture identities remain below floor in both forms.

## 6. Comparison With WP-8b / WP-8e

WP-8b consumed `SSS-0002`, an advisory-source-only v2 instance. WP-8e consumed `SSS-0003`, an advisory-lineage-form v2 instance. `SSS-0004` uses the same corpus window and derivation method, but it exposes fixture identity as the dedicated segment grain (`Q04`, `outputs/Q04.json`).

The structural comparison is narrow:

- `SSS-0002`: two advisory-source rows, one for `BMAP` and one for `PGAS`
- `SSS-0003`: four advisory-lineage rows, keyed by source plus upstream artifact identifiers
- `SSS-0004`: two fixture-identity rows, one for `_02` and one for `canonical`
- all three cover `OSH-0001` through `OSH-0010`
- all three remain fully below floor, with null usable rates and only `INSUFFICIENT_EVIDENCE` outcomes

This package therefore demonstrates canonical central-query-layer consumption of fixture-form SSS v2 content, not stronger signal evidence and not a ranking of axes.

## 7. Honest Floor-Crossing Record

No realized `SSS-0004` segment crosses the locked floor of 10 observations (`Q02`, `outputs/Q02.json`).

- segment count: `2`
- above-floor segments: `0`
- below-floor segments: `2`
- null-rate segments: `2`
- insufficient-evidence outcomes: `2`

Across the current consumed v2 single-axis instances, the floor-crossing record remains fully limited (`Q04`, `outputs/Q04.json`):

- `SSS-0002`: `2` below-floor segments
- `SSS-0003`: `4` below-floor segments
- `SSS-0004`: `2` below-floor segments
- total: `8` below-floor segments, `0` above-floor segments

There is no sufficient signal classification in the current v2 single-axis record.

## 8. Fixture-Variety Constraint

The current fixture-axis coverage is structurally non-degenerate because both `canonical` and `_02` are present in committed `SSS-0004`.

The corpus is still factually thin at `n = 10` source observations. That is an evidence-volume constraint, not a policy conclusion and not evidence that fixture identity is or is not important.

## 9. Non-Claims

This package does not claim:

- policy, runtime, override, OMS, risk, or execution authority
- any source, lineage, or fixture ranking
- any cadence or corpus-growth directive
- any schema, validator, query-layer, or helper change
- any new SSS instance beyond the already committed `SSS-0004`
- any cross-v2-instance synthesis

The consumer is descriptive only. It records what the committed v2 artifact shows and what it still cannot support.

## 10. Forward Observation

The third v2 consumer supports descriptive forward observations only (`Q05`, `outputs/Q05.json`):

- central SSS v2 query-layer support is now load-bearing for all three v2 single-axis consumers
- all current v2 segments remain below the locked floor
- corpus growth remains the binding evidence constraint for stronger segment-level signal classifications
- a later v2 synthesis brief becomes a natural future step after WP-8g

These observations are not recommendations, rankings, schedules, or scope commitments.

## 11. Explicit Conclusion

SSS v2 has now been consumed over advisory-source, advisory-lineage, and fixture-identity axes. `SSS-0002` demonstrated advisory-source-only v2 consumption, `SSS-0003` demonstrated advisory-lineage-form v2 consumption, and `SSS-0004` now demonstrates fixture-identity-form v2 consumption through the canonical central query-layer surface.

All remain floor-limited. WP-8g demonstrates canonical central-query-layer consumption of fixture-form SSS v2 content, not sufficient signal evidence.

## 12. Artifacts In This Directory

- `queries/Q01..Q05*.sql`: exact read-only SQL used for this brief
- `outputs/Q01.json` through `outputs/Q05.json`: committed query results
- `run_all_queries.py`: convenience helper to regenerate the outputs through the central read-only query CLI
