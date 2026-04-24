# Shadow-Signal Advisory-Source Slice Readout 01

**Date:** 2026-04-24
**Scope:** Committed shadow-signal summary evidence for the advisory-source slice only over `SSS-0001`.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-shadow_signal_advisory_source_slice_01/`.
**Primary semantic source:** `v_shadow_signal_summaries_overview` over the committed `shadow_signal_summaries` relation.
**Does not introduce:** Shadow rows, signal semantics, schema changes, validator changes, helper changes, query-layer changes, fixtures, advisory artifacts, or runtime behavior.
**Does not recommend:** Policy action, runtime influence, source ranking, fixture ranking, lineage ranking, or cross-axis interpretation.

## 1. Purpose

This brief is the third bounded consumer of the committed shadow-signal summary layer. Its scope is intentionally narrow: read the advisory-source slice only and describe what the current committed summary layer says about the realized source values without redefining signal semantics. With this source readout in place, the current three-consumer set is complete.

The package consumes the already-locked Option A signal-definition family through `SSS-0001` and `v_shadow_signal_summaries_overview`. It does not re-derive signal meaning from raw overlay shadow rows. The point of the package is to prove that the summary layer is consumable through the advisory-source axis using committed evidence only.

## 2. Query Bundle

The bundle follows the current repo-local diagnostic idiom: `run_all_queries.py` iterates `queries/Q*.sql` and writes `outputs/Q01.json` through `outputs/Q05.json`.

- `Q01`: segment-level summary overview for the source slice
- `Q02`: realized committed segment rows grouped by advisory source
- `Q03`: advisory-source rollup counts
- `Q04`: explicit source-level insufficiency check against the locked floor of 10
- `Q05`: structural comparison across source, fixture-identity, and lineage partitions

All five queries read the committed shadow-signal summary surface. `v_integrity_shadow_signal_summary_derivation` remains the integrity/drift surface for package validation, not the primary evidence source for the readout itself.

## 3. Slice Definition

The slice is bounded strictly to advisory source over the existing committed `SSS-0001` rows:

- `BMAP`
- `PGAS`

This package reads the advisory-source dimension already encoded on the committed segment rows. It does not redefine v1 segmentation, emit a new summary instance, or alter the locked segment key that still includes advisory lineage and fixture identity.

## 4. What The Advisory-Source Readout Shows

The current committed summary family realizes 8 total segment rows for this slice: 4 with `advisory_source = BMAP` and 4 with `advisory_source = PGAS` (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`). Those 8 rows are the existing `SSS-0001` segments viewed through the source dimension, not newly synthesized source-only segments.

Q03 rolls those segment rows into 2 source readout rows, one for each realized committed advisory source (`Q03`, `outputs/Q03.json`):

- `BMAP`: `segment_count = 4`, `total_observation_count = 5`, `insufficient_segment_count = 4`, `sufficient_segment_count = 0`
- `PGAS`: `segment_count = 4`, `total_observation_count = 5`, `insufficient_segment_count = 4`, `sufficient_segment_count = 0`

Because both realized source readouts remain below the locked floor of 10 observations, neither source currently yields a usable agreement or disagreement rate. Q03 therefore reports `agreement_rate = null` and `disagreement_rate = null` for both sources (`Q03`, `outputs/Q03.json`).

Q04 makes the floor impact explicit at the advisory-source readout level. Both current sources still have `observation_count < 10`, so both source rows remain `insufficient_evidence = true` and `signal_outcome = INSUFFICIENT_EVIDENCE` (`Q04`, `outputs/Q04.json`).

## 5. Honest Constraint Statement

The advisory-source readout is feasible because `advisory_source` is already encoded directly on each committed `SSS-0001` segment row and exposed through `v_shadow_signal_summaries_overview`. That is enough to support a bounded descriptive consumer over the current committed summary family.

A new advisory-source-only SSS instance is not available under locked v1 semantics. The v1 segment key remains the explicit combination of `advisory_source`, `source_bucket_mapping_id`, `source_pre_gate_advisory_snapshot_id`, and `fixture_identity`, so a first-class source-only summary instance would be a different summary shape rather than a restatement of current `SSS-0001`.

## 6. Structural Comparison To WP-7u And WP-7v

The three bounded consumers now expose three structural partitions of the same committed `SSS-0001` content (`Q05`, `outputs/Q05.json`):

- source slice: 2 readout rows, both insufficient
- fixture slice: 2 readout rows, both insufficient
- lineage slice: 4 readout rows, all insufficient

The consumers therefore produce different structural views over the same committed summary family, but they do not yet produce different sufficient signal classifications. None of the three current partitions crosses the floor of 10 observations. The honest comparison is structural difference in partition shape, not ranked difference in signal strength.

## 7. Floor Status

No advisory-source readout is above the locked floor of 10 observations in the current `SSS-0001` corpus window (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`). Both `BMAP` and `PGAS` currently sit at 5 observations.

That means no source-level agreement rate is currently reportable as a sufficient signal state. The current readout is descriptive evidence of source visibility and shared insufficiency, not sufficient source-level agreement or disagreement classification.

## 8. Forward Observation

The completed three-consumer set now supports a narrow forward observation only. If stronger source-, fixture-, or lineage-level signal statements are desired later, corpus growth would be required to lift more of the current readouts above the locked floor.

If future work requires first-class source-only segmentation, that would point toward SSS v2 schema evolution rather than reinterpretation of the current v1 instance. A different future consumer kind, such as cross-SSS-instance trend analysis, would likewise require additional committed SSS instances rather than more aggressive interpretation of `SSS-0001`.

This package does not commit scope for any of those directions. It records only that the current three-consumer set is now complete and that the present corpus remains below the evidentiary threshold for stronger source-level claims.

## 9. Explicit Conclusion

The first advisory-source slice is consumable through the committed shadow-signal summary layer as the third bounded downstream consumer. Under the current corpus, both realized advisory-source readouts remain below the locked floor of 10 observations and therefore remain `INSUFFICIENT_EVIDENCE` rather than sufficient signal states (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`).

The current source slice yields a complete descriptive readout over the committed `SSS-0001` content, not a new source-only summary instance. The three-consumer set is now complete, but all three current partitions still share insufficient evidence under the locked floor rule. This package encodes no policy inference, no runtime influence, and no cross-axis ranking.

## 10. Artifacts In This Directory

- `queries/Q01..Q05*.sql`: exact read-only SQL used for this brief.
- `outputs/Q01.json` through `outputs/Q05.json`: committed JSON outputs from the stored SQL.
- `run_all_queries.py`: convenience helper to regenerate the outputs through the read-only query CLI.
