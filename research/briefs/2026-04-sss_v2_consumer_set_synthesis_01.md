# SSS v2 Consumer-Set Synthesis 01

**Date:** 2026-04-28
**Scope:** Committed synthesis over the completed three-consumer SSS v2 set spanning advisory-source, advisory-lineage, and fixture-identity single-axis consumers.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-sss_v2_consumer_set_synthesis_01/` plus the three committed bounded SSS v2 consumer briefs.
**Primary semantic source:** `v_shadow_signal_summaries_v2_overview` over committed `SSS-0002`, `SSS-0003`, and `SSS-0004`, as consumed by the committed WP-8b, WP-8e, and WP-8g briefs.
**Integrity source:** `v_integrity_shadow_signal_summary_v2_derivation`, which returns `[]` for the current committed SSS v2 summaries.
**Does not introduce:** A new SSS instance, signal-semantics changes, schema changes, validator changes, helper changes, query-layer changes, fixtures, advisory artifacts, shadow rows, or runtime behavior.
**Does not recommend:** Policy action, runtime influence, axis ranking, scope commitment, or a preferred next package.

## 1. Purpose And Scope

This brief is the committed synthesis over the completed three-consumer set for SSS v2. It exists as a distinct record from the individual consumer briefs so the repo has one place that states what the set as a whole demonstrates, what it does not demonstrate, and which forward directions are structurally supported without committing scope.

The synthesis consumes committed consumer outputs and committed central SSS v2 query-layer content. It does not re-derive signal meaning from raw overlay-shadow rows and it does not redefine the locked floor-10 semantics. The evidence base is the completed consumer trio:

- `2026-04-sss_v2_advisory_source_consumer_01.md`
- `2026-04-sss_v2_advisory_lineage_consumer_01.md`
- `2026-04-sss_v2_fixture_consumer_01.md`

This package changes no SSS instance, schema, validator, query-layer implementation, helper, runtime path, policy, or execution behavior.

## 2. Query Bundle

The bundle follows the current repo-local brief idiom: `run_all_queries.py` iterates `queries/Q*.sql` and writes `outputs/Q01.json` through `outputs/Q05.json`.

- `Q01`: compact inventory of the three committed v2 consumer axes and consumed SSS v2 instances
- `Q02`: structural partition summary across the three v2 single-axis instances
- `Q03`: aggregate floor-status summary across the consumed v2 single-axis set
- `Q04`: explicit single-axis consumer limit summary
- `Q05`: forward-observation support table

All five queries are read-only SQL over existing central v2 surfaces. No query-layer change is required, and `v_integrity_shadow_signal_summary_v2_derivation` remains the integrity/drift surface rather than the primary evidence source for this brief.

## 3. What Each V2 Consumer Axis Revealed At Current Corpus Size And Floor = 10

The completed v2 consumer set is structurally complete for the three committed v2 single-axis instances but remains evidentially floor-limited. Q01 inventories three consumer axes over three committed summary artifacts, with the locked `floor_required = 10` applying to each segment (`Q01`, `outputs/Q01.json`).

The advisory-source consumer reads `SSS-0002`, the dedicated advisory-source-only v2 instance consumed by WP-8b. It has `2` realized segments, `0` above-floor segments, `2` below-floor segments, `2` null-rate segments, and `2` `INSUFFICIENT_EVIDENCE` outcomes. The realized source rows remain `BMAP = 5` observations and `PGAS = 5` observations (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`).

The advisory-lineage consumer reads `SSS-0003`, the advisory-lineage v2 instance consumed by WP-8e. It has `4` realized segments, `0` above-floor segments, `4` below-floor segments, `4` null-rate segments, and `4` `INSUFFICIENT_EVIDENCE` outcomes. The realized lineage observation totals remain `3 / 2 / 3 / 2` (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`).

The fixture-identity consumer reads `SSS-0004`, the fixture-identity v2 instance consumed by WP-8g. It has `2` realized segments, `0` above-floor segments, `2` below-floor segments, `2` null-rate segments, and `2` `INSUFFICIENT_EVIDENCE` outcomes. The realized fixture rows remain `_02 = 4` observations and `canonical = 6` observations (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`).

## 4. Axis Comparison

The three consumers expose different single-axis partition forms over the same committed source corpus window, `OSH-0001` through `OSH-0010`. The structural comparison is `2 / 4 / 2` segments for advisory-source-only, advisory-lineage, and fixture-identity respectively (`Q02`, `outputs/Q02.json`).

That difference is structural, not ranked. `SSS-0002` exposes `advisory_source` as the segment key. `SSS-0003` exposes advisory lineage through `advisory_source`, `source_bucket_mapping_id`, and `source_pre_gate_advisory_snapshot_id`. `SSS-0004` exposes `fixture_identity` as the segment key (`Q02`, `outputs/Q02.json`).

No axis currently produces any sufficient segment. Q03 reports `total_segments = 8`, `above_floor_segments = 0`, `below_floor_segments = 8`, `null_rate_segments = 8`, and `insufficient_evidence_segments = 8` across the consumed v2 single-axis set (`Q03`, `outputs/Q03.json`).

## 5. Honest Limits Of Single-Axis V2 Consumers

The current three-consumer set demonstrates that SSS v2 single-axis consumption is feasible through committed central query-layer views and committed summary content. It does not demonstrate cross-axis interaction effects, because each committed v2 consumer intentionally holds scope to one single-axis instance (`Q04`, `outputs/Q04.json`).

The set also does not demonstrate temporal trends. The three committed v2 instances share one corpus window over `OSH-0001` through `OSH-0010`, so there is no multi-window sequence from which to read change over time (`Q01`, `outputs/Q01.json`; `Q04`, `outputs/Q04.json`).

Rare-segment effects are not demonstrable from the current set. All eight consumed v2 single-axis segments remain below the locked floor, so the current outputs expose structural visibility and count preservation rather than sufficient axis-level agreement or disagreement states (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`).

The set also does not support agreement-rate inference. Agreement and disagreement rates remain `null` for all consumed v2 single-axis segments, and every segment retains `signal_outcome = INSUFFICIENT_EVIDENCE` (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`).

## 6. Aggregate Floor-Crossing Record

The aggregate consumed v2 single-axis record remains fully floor-limited at current corpus size `n = 10` (`Q03`, `outputs/Q03.json`):

- total v2 single-axis segments consumed: `8`
- above-floor segments: `0`
- below-floor segments: `8`
- null-rate segments: `8`
- insufficient-evidence segments: `8`

The current corpus size is the dominant evidence constraint. The consumer set demonstrates structural coverage over three committed v2 axes, not sufficient signal evidence.

## 7. Forward Observation

The completed v2 consumer set supports descriptive forward observations only (`Q05`, `outputs/Q05.json`).

Cross-version synthesis is now structurally possible because the repo has committed v1 and v2 consumer-set records. This brief does not perform cross-version synthesis.

An SSS v2 stability lock is now structurally supportable after three committed v2 single-axis consumers and this synthesis record. This brief does not create a stability-lock artifact.

SSS v3 schema evolution remains a later option if the target becomes cross-axis or temporal forms. This brief does not design or scope v3.

Corpus growth remains the dominant evidence constraint for any stronger signal classification. This brief does not create corpus-growth machinery, cadence, or a preferred next package.

## 8. Explicit Conclusion

The SSS v2 single-axis consumer set is structurally complete for the three committed v2 instances. `SSS-0002` demonstrates advisory-source-only v2 consumption, `SSS-0003` demonstrates advisory-lineage v2 consumption, and `SSS-0004` demonstrates fixture-identity v2 consumption through the central query-layer surface (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`).

The set demonstrates central-query-layer consumption over three axes. It does not demonstrate sufficient signal evidence: all eight consumed v2 single-axis segments remain below floor, all eight retain null usable rates, and all eight remain `INSUFFICIENT_EVIDENCE` (`Q03`, `outputs/Q03.json`).

Any next architectural step must preserve that distinction between structural consumability and sufficient signal evidence.

## 9. Artifacts In This Directory

- `queries/Q01..Q05*.sql`: exact read-only SQL used for this brief
- `outputs/Q01.json` through `outputs/Q05.json`: committed query results
- `run_all_queries.py`: convenience helper to regenerate the outputs through the central read-only query CLI
