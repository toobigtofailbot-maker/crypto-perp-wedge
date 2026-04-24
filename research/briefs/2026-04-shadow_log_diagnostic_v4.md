# Shadow-Log Diagnostic Brief v4

**Date:** 2026-04-23
**Scope:** Committed overlay shadow-log evidence exposed by the current query layer after the helper-produced corpus expansion through `OSH-0006`.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-shadow_log_diagnostic_v4/`.
**Does not introduce:** Shadow-log entries, query-layer changes, policy changes, or runtime behavior.
**Does not recommend:** Overlay influence, promotion, demotion, or non-shadow execution use.

## 1. Purpose

This brief is the fourth diagnostic consumption of committed overlay shadow-log evidence through the current read-only query layer. It mirrors the third brief's evidence-consumption discipline while extending the scope to the expanded committed corpus that now contains six shadow rows across both the pre-diversified historical mismatch lineages and the new diversified first-match lineages (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`; `Q06`, `outputs/Q06.json`).

The purpose remains interpretation discipline, not policy action. This brief records what the current committed evidence says at `n = 6`, whether the zero-override boundary remains clean, whether the source references remain clean, how the diversified lineages differ from the historical lineages, and whether the expanded corpus is sufficient for inference (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`; `Q06`, `outputs/Q06.json`).

## 2. Evidence Scope

Q01 reads `v_overlay_shadow_logs_overview`, the entry-level view over committed overlay shadow logs. It returns six rows: the historical BMAP-source rows `OSH-0001` and `OSH-0003`, the historical PGAS-source rows `OSH-0002` and `OSH-0004`, and the diversified rows `OSH-0005` and `OSH-0006` (`Q01`, `outputs/Q01.json`).

Q02 reads `v_overlay_shadow_logs_latest`, the latest-per-lineage view. It returns four rows, preserving separate latest visibility for the pre-diversified and diversified lineages at both advisory sources: `OSH-0003`, `OSH-0005`, `OSH-0004`, and `OSH-0006` (`Q02`, `outputs/Q02.json`).

Q03 reads `v_overlay_shadow_agreement_summary`, the aggregate agreement/disagreement view segmented by `advisory_source`. It returns four aggregate rows: `BMAP MATCH` with `entry_count = 1`, `BMAP MISMATCH` with `entry_count = 2`, `PGAS MATCH` with `entry_count = 1`, and `PGAS MISMATCH` with `entry_count = 2`; each row also reports `override_true_count = 0` (`Q03`, `outputs/Q03.json`).

Q04 reads `v_overlay_shadow_override_audit`, the zero-override audit view. It returns an empty JSON array, so this diagnostic run found no rows where override behavior, fail-open preservation, or advisory-only status violated the audit view (`Q04`, `outputs/Q04.json`).

Q05 reads `v_integrity_overlay_shadow_refs`, the shadow-reference integrity view. It returns an empty JSON array, so this diagnostic run found no unresolved or mismatched overlay-shadow references exposed by that integrity view (`Q05`, `outputs/Q05.json`).

Q06 reads `v_pre_gate_advisory_snapshots_overview` filtered to `PGAS-0002` and `PGAS-0003`, the exact pre-gate advisory snapshots needed to ground the pre-diversified and diversified PGAS-source lineages. It returns two rows showing the earlier `ALLOW_REDUCED` plus `macro_window_flag = true` state and the newer `ALLOW` plus `macro_window_flag = false` state (`Q06`, `outputs/Q06.json`).

## 3. Query Inventory

- `queries/Q01_shadow_overview.sql` stores the entry-level shadow-log query. Its output is `outputs/Q01.json`.
- `queries/Q02_shadow_latest.sql` stores the latest-per-lineage shadow-log query. Its output is `outputs/Q02.json`.
- `queries/Q03_shadow_agreement_summary.sql` stores the advisory-source-segmented agreement/disagreement query. Its output is `outputs/Q03.json`.
- `queries/Q04_shadow_override_audit.sql` stores the zero-override audit query. Its output is `outputs/Q04.json`.
- `queries/Q05_shadow_integrity_refs.sql` stores the shadow-reference integrity query. Its output is `outputs/Q05.json`.
- `queries/Q06_pre_gate_snapshot_overview.sql` stores the PGAS grounding query for `PGAS-0002` and `PGAS-0003`. Its output is `outputs/Q06.json`.

The outputs were produced by `research/briefs/2026-04-shadow_log_diagnostic_v4/run_all_queries.py`, which executes the stored SQL through the existing read-only query CLI and writes JSON outputs beside the query files (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`; `Q06`, `outputs/Q06.json`).

## 4. Current Committed Evidence State

The current entry-level evidence contains six committed shadow-log rows (`Q01`, `outputs/Q01.json`). The historical pre-diversified BMAP lineage is visible through `OSH-0001` and `OSH-0003`, both with `advisory_source = BMAP`, `source_bucket_mapping_id = BMAP-0001`, `source_pre_gate_advisory_snapshot_id = null`, `observed_overlay_bucket = ALLOW`, `mapped_bucket = ALLOW_REDUCED`, `size_multiplier = 0.5`, and `comparison_result = MISMATCH` (`Q01`, `outputs/Q01.json`).

The historical pre-diversified PGAS lineage is visible through `OSH-0002` and `OSH-0004`, both with `advisory_source = PGAS`, `source_bucket_mapping_id = BMAP-0001`, `source_pre_gate_advisory_snapshot_id = PGAS-0002`, `observed_overlay_bucket = ALLOW`, `mapped_bucket = ALLOW_REDUCED`, `size_multiplier = 0.5`, and `comparison_result = MISMATCH` (`Q01`, `outputs/Q01.json`).

The diversified BMAP lineage is visible through `OSH-0005`, with `advisory_source = BMAP`, `source_bucket_mapping_id = BMAP-0002`, `source_pre_gate_advisory_snapshot_id = null`, `observed_overlay_bucket = ALLOW`, `mapped_bucket = ALLOW`, `size_multiplier = 1.0`, and `comparison_result = MATCH` (`Q01`, `outputs/Q01.json`).

The diversified PGAS lineage is visible through `OSH-0006`, with `advisory_source = PGAS`, `source_bucket_mapping_id = BMAP-0002`, `source_pre_gate_advisory_snapshot_id = PGAS-0003`, `observed_overlay_bucket = ALLOW`, `mapped_bucket = ALLOW`, `size_multiplier = 1.0`, and `comparison_result = MATCH` (`Q01`, `outputs/Q01.json`).

Q06 grounds the PGAS lineage change directly. `PGAS-0002` records `source_bucket_mapping_id = BMAP-0001`, `mapped_bucket = ALLOW_REDUCED`, `macro_window_flag = true`, `combination_rule_applied = MACRO_AWARE_FLOOR`, and `combined_bucket = ALLOW_REDUCED`, while `PGAS-0003` records `source_bucket_mapping_id = BMAP-0002`, `mapped_bucket = ALLOW`, `macro_window_flag = false`, `combination_rule_applied = MACRO_AWARE_FLOOR`, and `combined_bucket = ALLOW` (`Q06`, `outputs/Q06.json`).

The latest-per-lineage view does not collapse one path into another. Q02 returns `OSH-0003` as the current latest pre-diversified BMAP row, `OSH-0005` as the current latest diversified BMAP row, `OSH-0004` as the current latest pre-diversified PGAS row, and `OSH-0006` as the current latest diversified PGAS row (`Q02`, `outputs/Q02.json`).

## 5. MATCH vs MISMATCH

In this diagnostic brief, `MATCH` means the committed shadow-log comparison class says the observed overlay bucket and the advisory mapped bucket agreed. `MISMATCH` means the committed comparison class says they differed. The current committed corpus contains both classes: four `MISMATCH` rows in the historical pre-diversified lineages and two `MATCH` rows in the diversified lineages (`Q01`, `outputs/Q01.json`; `Q03`, `outputs/Q03.json`).

The historical disagreement pattern remains consistent across both pre-diversified source lineages. In each historical lineage the observed overlay bucket is `ALLOW` while the advisory-side mapped bucket is `ALLOW_REDUCED` (`Q01`, `outputs/Q01.json`; `Q06`, `outputs/Q06.json`).

The diversified lineages are the first committed `MATCH` rows. In both diversified rows the observed overlay bucket is `ALLOW`, the advisory-side mapped bucket is also `ALLOW`, and the diversified PGAS lineage is grounded by `PGAS-0003`, which records the non-macro-window `ALLOW` state rather than the earlier macro-window-true `ALLOW_REDUCED` state (`Q01`, `outputs/Q01.json`; `Q03`, `outputs/Q03.json`; `Q06`, `outputs/Q06.json`).

A `MATCH` or `MISMATCH` remains diagnostic evidence only. In the current output set neither class coincides with override behavior: Q04 returns no zero-override audit rows, and Q03 reports `override_true_count = 0` for every advisory-source comparison class (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`).

## 6. Evidence Sufficiency

The current corpus is larger than the prior brief's `n = 4`, but it is still small. Q03 reports exactly one `MATCH` row and two `MISMATCH` rows for `BMAP`, and exactly one `MATCH` row and two `MISMATCH` rows for `PGAS`, for a total corpus size of `n = 6` (`Q03`, `outputs/Q03.json`).

That is enough to show that the evidence path now records both disagreement and agreement classes, that the diversified advisory-state rows are the first committed `MATCH` rows, and that the pre-diversified historical lineages remain queryable alongside the diversified lineages in both overview and latest-per-lineage form (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`).

It is not enough to infer a stable agreement rate, disagreement rate, source-specific quality level, durable signal, or policy direction. Clean Q04 and Q05 outputs support a clean diagnostic boundary for this run, but they do not make `n = 6` decision-sufficient evidence (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`).

## 7. Explicit Conclusion

The shadow evidence path is working across both historical mismatch lineages and the first diversified match lineages now represented in the committed corpus. Entry-level evidence is queryable, latest-per-lineage evidence remains separated by lineage, and aggregate evidence is segmented by `advisory_source` plus comparison class (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`).

The honest current evidence conclusion is: both disagreement and agreement classes are now present; the diversified rows are the first committed `MATCH` rows; zero overrides remain absent; integrity remains clean (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`).

The current evidence is still insufficient for policy inference because the aggregate evidence volume is `n = 6`. No overlay policy change, promotion, demotion, runtime influence, or non-shadow influence is justified by this output set, and the diversified path should not be treated as validated or decision-sufficient from one committed `MATCH` row per source family (`Q03`, `outputs/Q03.json`; `Q06`, `outputs/Q06.json`).

## 8. Evidence-Limited Follow-up Note

Continue accumulating shadow evidence through the existing committed artifact path, then review the aggregate views again later. The next review should keep the same distinction used here: the historical pre-diversified mismatch lineages and the diversified first-match lineages are both visible, but current `n = 6` evidence is still insufficient for policy inference (`Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`).

## 9. Artifacts in This Directory

- `queries/Q01..Q06*.sql`: exact read-only SQL used for this brief.
- `outputs/Q01..Q06.json`: committed JSON outputs from the stored SQL.
- `run_all_queries.py`: convenience helper to regenerate the JSON outputs through the read-only query CLI.
