# Shadow-Log Diagnostic Brief v3

**Date:** 2026-04-22
**Scope:** Committed overlay shadow-log evidence exposed by the current query layer after the helper-produced corpus expansion through `OSH-0004`.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-shadow_log_diagnostic_v3/`.
**Does not introduce:** Shadow-log entries, query-layer changes, policy changes, or runtime behavior.
**Does not recommend:** Overlay influence, promotion, demotion, or non-shadow execution use.

## 1. Purpose

This brief is the third diagnostic consumption of committed overlay shadow-log evidence through the current read-only query layer. It mirrors the second brief's evidence-consumption discipline while extending the scope to the expanded committed corpus that now contains four shadow rows across both the historical BMAP-source lineage and the historical/additive PGAS-source lineage (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`; `Q06`, `outputs/Q06.json`).

The purpose remains interpretation discipline, not policy action. This brief records what the current committed evidence says at `n = 4`, whether the zero-override boundary remains clean, whether the source references remain clean, and whether the expanded corpus is sufficient for inference (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`).

## 2. Evidence Scope

Q01 reads `v_overlay_shadow_logs_overview`, the entry-level view over committed overlay shadow logs. It returns four rows: the historical BMAP-source row `OSH-0001`, the historical/additive PGAS-source row `OSH-0002`, and the helper-produced expansion rows `OSH-0003` and `OSH-0004` (`Q01`, `outputs/Q01.json`).

Q02 reads `v_overlay_shadow_logs_latest`, the latest-per-lineage view. It returns one latest row for the BMAP lineage and one latest row for the PGAS lineage, so both advisory-source paths remain visible in the current committed corpus after the helper-produced expansion (`Q02`, `outputs/Q02.json`).

Q03 reads `v_overlay_shadow_agreement_summary`, the aggregate agreement/disagreement view segmented by `advisory_source`. It returns two aggregate rows, both `MISMATCH`: one for `BMAP` and one for `PGAS`, each with `entry_count = 2`, `mismatch_count = 2`, and `override_true_count = 0` (`Q03`, `outputs/Q03.json`).

Q04 reads `v_overlay_shadow_override_audit`, the zero-override audit view. It returns an empty JSON array, so this diagnostic run found no rows where override behavior, fail-open preservation, or advisory-only status violated the audit view (`Q04`, `outputs/Q04.json`).

Q05 reads `v_integrity_overlay_shadow_refs`, the shadow-reference integrity view. It returns an empty JSON array, so this diagnostic run found no unresolved or mismatched overlay-shadow references exposed by that integrity view (`Q05`, `outputs/Q05.json`).

Q06 reads `v_pre_gate_advisory_snapshots_overview` filtered to `PGAS-0002`, the exact pre-gate advisory snapshot referenced by the PGAS-source shadow lineage. It returns one row showing `combination_rule_applied = MACRO_AWARE_FLOOR`, `combined_bucket = ALLOW_REDUCED`, `macro_window_flag = true`, `deterministic = true`, and `advisory_only = true` (`Q06`, `outputs/Q06.json`).

## 3. Query Inventory

- `queries/Q01_shadow_overview.sql` stores the entry-level shadow-log query. Its output is `outputs/Q01.json`.
- `queries/Q02_shadow_latest.sql` stores the latest-per-lineage shadow-log query. Its output is `outputs/Q02.json`.
- `queries/Q03_shadow_agreement_summary.sql` stores the advisory-source-segmented agreement/disagreement query. Its output is `outputs/Q03.json`.
- `queries/Q04_shadow_override_audit.sql` stores the zero-override audit query. Its output is `outputs/Q04.json`.
- `queries/Q05_shadow_integrity_refs.sql` stores the shadow-reference integrity query. Its output is `outputs/Q05.json`.
- `queries/Q06_pre_gate_snapshot_overview.sql` stores the PGAS grounding query for `PGAS-0002`. Its output is `outputs/Q06.json`.

The outputs were produced by `research/briefs/2026-04-shadow_log_diagnostic_v3/run_all_queries.py`, which executes the stored SQL through the existing read-only query CLI and writes JSON outputs beside the query files (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`; `Q06`, `outputs/Q06.json`).

## 4. Current Committed Evidence State

The current entry-level evidence contains four committed shadow-log rows (`Q01`, `outputs/Q01.json`). The historical BMAP-source lineage is visible through `OSH-0001` and the later helper-produced BMAP row `OSH-0003`, both with `advisory_source = BMAP`, `source_bucket_mapping_id = BMAP-0001`, `source_pre_gate_advisory_snapshot_id = null`, `observed_overlay_bucket = ALLOW`, `mapped_bucket = ALLOW_REDUCED`, `size_multiplier = 0.5`, and `comparison_result = MISMATCH` (`Q01`, `outputs/Q01.json`).

The historical/additive PGAS-source lineage is visible through `OSH-0002` and the later helper-produced PGAS row `OSH-0004`, both with `advisory_source = PGAS`, `source_bucket_mapping_id = BMAP-0001`, `source_pre_gate_advisory_snapshot_id = PGAS-0002`, `observed_overlay_bucket = ALLOW`, `mapped_bucket = ALLOW_REDUCED`, `size_multiplier = 0.5`, and `comparison_result = MISMATCH` (`Q01`, `outputs/Q01.json`).

Q06 grounds the PGAS lineage directly. The referenced snapshot `PGAS-0002` records `combination_rule_applied = MACRO_AWARE_FLOOR`, `combined_bucket = ALLOW_REDUCED`, `macro_window_flag = true`, `deterministic = true`, and `advisory_only = true` (`Q06`, `outputs/Q06.json`).

The latest-per-lineage view does not collapse one path into the other. Q02 returns `OSH-0003` as the current latest BMAP row and `OSH-0004` as the current latest PGAS row, and both latest rows are currently `MISMATCH` (`Q02`, `outputs/Q02.json`).

## 5. MATCH vs MISMATCH

In this diagnostic brief, `MATCH` means the committed shadow-log comparison class says the observed overlay bucket and the advisory mapped bucket agreed. `MISMATCH` means the committed comparison class says they differed. The current committed corpus contains four rows and all four are `MISMATCH`: `OSH-0001`, `OSH-0002`, `OSH-0003`, and `OSH-0004` (`Q01`, `outputs/Q01.json`; `Q03`, `outputs/Q03.json`).

The current disagreement pattern is the same across both visible source lineages. In each case the observed overlay bucket is `ALLOW` while the advisory-side mapped bucket is `ALLOW_REDUCED` (`Q01`, `outputs/Q01.json`).

A `MISMATCH` remains disagreement evidence only. In the current output set it does not coincide with override behavior: Q04 returns no zero-override audit rows, and Q03 reports `override_true_count = 0` for both the BMAP and PGAS `MISMATCH` classes (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`).

## 6. Evidence Sufficiency

The current corpus is larger than the prior brief's `n = 2`, but it is still small. Q03 reports exactly two BMAP-source `MISMATCH` rows and two PGAS-source `MISMATCH` rows, for a total corpus size of `n = 4` (`Q03`, `outputs/Q03.json`).

That is enough to show that the evidence path now captures two committed rows per visible advisory-source lineage and that both the historical BMAP lineage and the historical/additive PGAS lineage remain queryable in both overview and latest-per-lineage form (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`).

It is not enough to infer a stable agreement rate, disagreement rate, source-specific failure mode, durable signal, or policy direction. Clean Q04 and Q05 outputs support a clean diagnostic boundary for this run, but they do not make `n = 4` decision-sufficient evidence (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`).

## 7. Explicit Conclusion

The shadow evidence path is working at both source paths currently represented in the committed corpus. Entry-level evidence is queryable, latest-per-lineage evidence remains visible, and aggregate evidence is segmented by `advisory_source` (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`).

The honest current evidence conclusion is: four mismatches, zero overrides, clean integrity (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`).

The current evidence is still insufficient for policy inference because the aggregate evidence volume is `n = 4`. No overlay policy change, promotion, demotion, runtime influence, or non-shadow influence is justified by this output set, and the PGAS path should not be treated as better or worse from four observations (`Q03`, `outputs/Q03.json`).

## 8. Evidence-Limited Follow-up Note

Continue accumulating shadow evidence through the existing committed artifact path, then review the aggregate views again later. The next review should keep the same distinction used here: the historical BMAP lineage and the historical/additive PGAS lineage are both visible, but current `n = 4` evidence is still insufficient for policy inference (`Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`).

## 9. Artifacts in This Directory

- `queries/Q01..Q06*.sql`: exact read-only SQL used for this brief.
- `outputs/Q01..Q06.json`: committed JSON outputs from the stored SQL.
- `run_all_queries.py`: convenience helper to regenerate the JSON outputs through the read-only query CLI.
