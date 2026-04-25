# SSS v2 Advisory-Source Consumer 01

**Date:** 2026-04-24
**Scope:** First bounded consumer brief over the committed SSS v2 advisory-source-only instance `SSS-0002`.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-sss_v2_advisory_source_consumer_01/`.
**Primary semantic source:** `research/shadow_signal_summaries_v2/SSS-0002.shadow_signal_summary.json`.
**Structural comparison context only:** `research/briefs/2026-04-shadow_signal_advisory_source_slice_01.md` plus its committed `Q03` and `Q04` outputs.
**Does not introduce:** A new SSS instance, schema changes, validator changes, query-layer changes, helper changes, advisory-artifact changes, fixtures, shadow rows, or runtime behavior.
**Does not recommend:** Policy action, runtime influence, override action, source ranking, cadence, or cross-v2-instance synthesis.

## 1. Purpose

This brief is the first bounded downstream consumer over a committed SSS v2 instance. Its scope is intentionally narrow: read `SSS-0002` as the primary evidence source, prove that a first-class advisory-source-only v2 instance is consumable through the established bounded-consumer idiom, and describe only what the committed artifact says at the current corpus size.

The brief does not re-derive signal meaning from raw overlay-shadow rows. It consumes the already committed v2 instance and records the current floor-limited evidence state without changing any schema, validator, helper, query-layer, or protected runtime path.

## 2. Evidence Source

The primary evidence source for this package is `research/shadow_signal_summaries_v2/SSS-0002.shadow_signal_summary.json`. That file is the first committed SSS v2 instance and uses `schema_version: "v2"` with `segmentation_axes: ["advisory_source"]`.

WP-7w is used only for structural comparison context. The relevant v1 comparison artifact is `research/briefs/2026-04-shadow_signal_advisory_source_slice_01.md`, specifically the committed `Q03` and `Q04` outputs that summarize the v1 advisory-source readout over `SSS-0001`. Those WP-7w artifacts are not the primary evidence source for this brief.

## 3. Query Bundle

The bundle follows the current repo-local brief idiom: `run_all_queries.py` iterates `queries/Q*.sql` and writes `outputs/Q01.json` through `outputs/Q05.json`.

- `Q01`: source-level overview of the committed `SSS-0002` segment rows
- `Q02`: explicit floor-status summary for each realized v2 advisory source
- `Q03`: structural comparison between `SSS-0002` and the WP-7w v1 advisory-source readout
- `Q04`: explicit consumer constraints for this first v2 consumer
- `Q05`: descriptive forward observations only

Because the current central query layer exposes only v1 SSS content, this bundle uses a local read-only DuckDB helper that registers temporary relations from the committed v2 instance and the committed WP-7w outputs. No `tools/research_query/` file is modified.

## 4. What SSS-0002 Shows

`SSS-0002` is an advisory-source-only single-axis summary that realizes exactly two source segments in deterministic lexical order: `BMAP` and `PGAS` (`Q01`, `outputs/Q01.json`).

The committed segment values are identical across the two realized sources (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`):

- `BMAP`: `match_count = 2`, `mismatch_count = 3`, `abstention_count = 0`, `observation_count = 5`, `rate_denominator = 5`, `signal_outcome = INSUFFICIENT_EVIDENCE`
- `PGAS`: `match_count = 2`, `mismatch_count = 3`, `abstention_count = 0`, `observation_count = 5`, `rate_denominator = 5`, `signal_outcome = INSUFFICIENT_EVIDENCE`

Both realized sources therefore remain descriptive visibility rows only. The v2 artifact proves that advisory source can now exist as a first-class segment key in a committed SSS instance, but it does not convert the current floor-limited corpus into sufficient evidence.

## 5. Comparison With WP-7w

WP-7w consumed the advisory-source dimension as a v1 readout over the existing four-axis `SSS-0001` instance. `SSS-0002` changes that structure by making `advisory_source` itself the segment key in a dedicated v2 instance (`Q03`, `outputs/Q03.json`).

The structural comparison is therefore narrow and explicit:

- `SSS-0002` is a dedicated v2 instance with `schema_version = "v2"` and `advisory_source` as a first-class segment key.
- WP-7w is a v1 advisory-source readout over `SSS-0001`, not a dedicated source-only instance.
- Both forms currently realize two source rows, `BMAP` and `PGAS`.
- Floor outcomes do not differ at current corpus size. Both the v2 instance and the WP-7w readout remain below floor for both realized sources (`Q03`, `outputs/Q03.json`).

That means v2 makes a new source-only instance shape structurally possible without changing the underlying evidence state.

## 6. Honest Floor-Crossing Record

No realized source segment is above the locked floor of 10 observations in `SSS-0002` (`Q02`, `outputs/Q02.json`).

- `BMAP`: `observation_count = 5`, below floor, usable rates unavailable, `signal_outcome = INSUFFICIENT_EVIDENCE`
- `PGAS`: `observation_count = 5`, below floor, usable rates unavailable, `signal_outcome = INSUFFICIENT_EVIDENCE`

The usable agreement and disagreement rates remain `null` for both sources because both segments are below floor. The honest current record is therefore that SSS v2 is instantiated and consumable once, while the current evidence remains floor-limited.

## 7. Non-Claims

This package does not claim:

- runtime, policy, override, OMS, risk, or execution authority
- any schema or validator change
- any query-layer or helper change
- any new SSS instance beyond the already committed `SSS-0002`
- any cadence or multi-instance trend mechanism

The consumer is descriptive only. It records what the committed v2 artifact shows and what it still cannot support.

## 8. Forward Observation

The first v2 consumer supports descriptive forward observations only (`Q05`, `outputs/Q05.json`):

- further single-axis v2 instances remain structurally possible under the committed v2 schema
- cross-v2-instance synthesis would require additional committed v2 instances and additional bounded consumers first
- stronger source-level statements would require corpus growth or later floor-crossing evidence
- a future additive v2 query-layer package is possible because this bundle relied on local temporary DuckDB relations instead of central registered query views

These observations are not a scope proposal, ranking, or execution implication.

## 9. Explicit Conclusion

SSS v2 is now both instantiated and consumed once. The v2 artifact resolves the source-only instance-shape constraint that WP-7w could address only as a v1 readout, while the current source evidence remains below the locked floor of 10 observations for both realized sources (`Q03`, `outputs/Q03.json`; `Q02`, `outputs/Q02.json`).

The first v2 consumer therefore demonstrates structural consumability, not sufficient source-level signal evidence. Additional v2 instances, more committed consumers, or corpus growth remain possible future directions only.

## 10. Artifacts In This Directory

- `queries/Q01..Q05*.sql`: exact read-only SQL used for this brief
- `outputs/Q01.json` through `outputs/Q05.json`: committed query results
- `run_all_queries.py`: convenience helper to regenerate the outputs through a local read-only DuckDB relation setup
