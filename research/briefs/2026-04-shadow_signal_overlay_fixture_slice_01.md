# Shadow-Signal Overlay-Fixture Slice Readout 01

**Date:** 2026-04-24
**Scope:** Committed shadow-signal summary evidence for the overlay-input fixture-identity slice only (`canonical` versus `_02`) over `SSS-0001`.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-shadow_signal_overlay_fixture_slice_01/`.
**Primary semantic source:** `v_shadow_signal_summaries_overview` over the committed `shadow_signal_summaries` relation.
**Does not introduce:** Shadow rows, signal semantics, schema changes, validator changes, helper changes, query-layer changes, fixtures, advisory artifacts, or runtime behavior.
**Does not recommend:** Policy action, override behavior, runtime influence, source ranking, fixture ranking, or cross-slice interpretation.

## 1. Purpose

This brief is the first bounded consumer of the committed shadow-signal summary layer. Its scope is intentionally narrow: read the overlay-input fixture-identity slice only, compare `canonical` versus `_02`, and describe what the current committed summary layer says without redefining signal semantics.

The package consumes the already-locked Option A signal-definition family through `SSS-0001` and `v_shadow_signal_summaries_overview`. It does not re-derive signal meaning ad hoc from raw overlay shadow rows. The point of the package is to prove that the summary layer is load-bearing as a descriptive interface for a bounded downstream slice.

## 2. Query Bundle

The bundle follows the current repo-local diagnostic idiom: `run_all_queries.py` iterates `queries/Q*.sql` and writes `outputs/Q01.json` through `outputs/Q05.json`.

- `Q01`: segment-level summary overview for the fixture slice
- `Q02`: realized segment rows split by fixture identity
- `Q03`: fixture-identity rollup counts
- `Q04`: explicit insufficiency check against the locked floor of 10
- `Q05`: side-by-side lineage comparison for `canonical` versus `_02`

All five queries read the committed shadow-signal summary surface. `v_integrity_shadow_signal_summary_derivation` remains the integrity/drift surface for package validation, not the primary evidence source for the readout itself.

## 3. Slice Definition

The slice is bounded strictly to overlay-input fixture identity:

- `canonical` = `tests/fixtures/context_snapshot_sample.json` + `configs/fmp_macro_flags.json`
- `_02` = `tests/fixtures/context_snapshot_sample_02.json` + `configs/fmp_macro_flags_02.json`

No third fixture bucket is included. No cross-axis comparison beyond this fixture-identity slice is introduced in this package.

## 4. Current Observations

The current committed summary family realizes 8 total segment rows for this slice: 4 `canonical` and 4 `_02` (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`).

Q03 shows that both fixture identities currently remain below the locked floor in the same structural way (`Q03`, `outputs/Q03.json`):

- `canonical`: `segment_count = 4`, `insufficient_segment_count = 4`, `sufficient_segment_count = 0`
- `_02`: `segment_count = 4`, `insufficient_segment_count = 4`, `sufficient_segment_count = 0`

Because all realized segments remain below the floor of 10 observations, both fixture identities currently have zero sufficient agreement, disagreement, or mixed signal states (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`).

Q04 makes the floor impact explicit at the segment level. Every current segment still has `observation_count < 10`, so every row remains `insufficient_evidence = true` and `signal_outcome = INSUFFICIENT_EVIDENCE` (`Q04`, `outputs/Q04.json`).

Q05 compares `canonical` versus `_02` side by side for each realized advisory lineage. The current corpus yields four lineage rows, and `signal_outcome_stable_across_fixture_identity = true` for all four because every lineage remains `INSUFFICIENT_EVIDENCE` on both fixture identities (`Q05`, `outputs/Q05.json`).

## 5. What The Slice Shows And Does Not Show

The honest current readout is shared insufficiency, not sufficient signal differentiation. The slice does show that fixture-identity consumption is already possible through the committed summary layer, and that the same bounded lineage comparison can be expressed without changing the query layer or reinterpreting raw shadow rows.

The slice does not yet show sufficient fixture-specific agreement, disagreement, or mixed signal states. It also does not justify any claim that fixture identity is unimportant. Under the locked floor rule, the current conclusion is only that more evidence is required before fixture-identity signal states can be compared meaningfully.

## 6. Explicit Conclusion

The first overlay-input fixture-identity slice is consumable through the committed shadow-signal summary layer. Under the current corpus, all 8 realized fixture-slice segments remain below the locked floor of 10 observations and therefore remain `INSUFFICIENT_EVIDENCE` rather than sufficient signal states (`Q01`, `outputs/Q01.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`).

The current slice yields structural symmetry in floor handling and shared insufficiency across `canonical` and `_02`, not sufficient signal separation. This package encodes no policy inference, no runtime influence, and no claim that future fixture importance has been disproved.

## 7. Artifacts In This Directory

- `queries/Q01..Q05*.sql`: exact read-only SQL used for this brief.
- `outputs/Q01.json` through `outputs/Q05.json`: committed JSON outputs from the stored SQL.
- `run_all_queries.py`: convenience helper to regenerate the outputs through the read-only query CLI.
