# Shadow-Log Diagnostic Brief v2

**Date:** 2026-04-21
**Scope:** Committed overlay shadow-log evidence exposed by the current query layer after the additive PGAS-source extension.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-shadow_log_diagnostic_v2/`.
**Does not introduce:** Shadow-log entries, query-layer changes, policy changes, or runtime behavior.
**Does not recommend:** Overlay influence, promotion, demotion, or non-shadow execution use.

## 1. Purpose

This brief is the second diagnostic consumption of committed overlay shadow-log evidence through the current read-only query layer. It mirrors the first brief’s evidence-consumption discipline while extending the scope to the now-expanded corpus that includes both the historical BMAP-source path and the additive PGAS-source path (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`; `Q06`, `outputs/Q06.json`).

The purpose remains interpretation discipline, not policy action. This brief records what the current committed evidence says, whether the zero-override boundary remains clean, whether the source references remain clean, and whether the expanded corpus is sufficient for inference (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`).

## 2. Evidence Scope

Q01 reads `v_overlay_shadow_logs_overview`, the entry-level view over committed overlay shadow logs. It returns two rows: the historical BMAP-source row `OSH-0001` and the additive PGAS-source row `OSH-0002` (`Q01`, `outputs/Q01.json`).

Q02 reads `v_overlay_shadow_logs_latest`, the latest-per-lineage view. It returns one latest row for the BMAP lineage and one latest row for the PGAS lineage, so both advisory-source paths remain visible in the current committed corpus (`Q02`, `outputs/Q02.json`).

Q03 reads `v_overlay_shadow_agreement_summary`, the aggregate agreement/disagreement view segmented by `advisory_source`. It returns two aggregate rows, both `MISMATCH`: one for `BMAP` and one for `PGAS`, each with `entry_count = 1` and `override_true_count = 0` (`Q03`, `outputs/Q03.json`).

Q04 reads `v_overlay_shadow_override_audit`, the zero-override audit view. It returns an empty JSON array, so this diagnostic run found no rows where override behavior, fail-open preservation, or advisory-only status violated the audit view (`Q04`, `outputs/Q04.json`).

Q05 reads `v_integrity_overlay_shadow_refs`, the shadow-reference integrity view. It returns an empty JSON array, so this diagnostic run found no unresolved or mismatched overlay-shadow references exposed by that integrity view (`Q05`, `outputs/Q05.json`).

Q06 reads `v_pre_gate_advisory_snapshots_overview` filtered to `PGAS-0002`, the exact pre-gate advisory snapshot referenced by the PGAS-source shadow row. It returns one row showing `combination_rule_applied = MACRO_AWARE_FLOOR`, `combined_bucket = ALLOW_REDUCED`, `macro_window_flag = true`, `deterministic = true`, and `advisory_only = true` (`Q06`, `outputs/Q06.json`).

## 3. Query Inventory

- `queries/Q01_shadow_overview.sql` stores the entry-level shadow-log query. Its output is `outputs/Q01.json`.
- `queries/Q02_shadow_latest.sql` stores the latest-per-lineage shadow-log query. Its output is `outputs/Q02.json`.
- `queries/Q03_shadow_agreement_summary.sql` stores the advisory-source-segmented agreement/disagreement query. Its output is `outputs/Q03.json`.
- `queries/Q04_shadow_override_audit.sql` stores the zero-override audit query. Its output is `outputs/Q04.json`.
- `queries/Q05_shadow_integrity_refs.sql` stores the shadow-reference integrity query. Its output is `outputs/Q05.json`.
- `queries/Q06_pre_gate_snapshot_overview.sql` stores the PGAS grounding query for `PGAS-0002`. Its output is `outputs/Q06.json`.

The outputs were produced by `research/briefs/2026-04-shadow_log_diagnostic_v2/run_all_queries.py`, which executes the stored SQL through the existing read-only query CLI and writes JSON outputs beside the query files (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`; `Q06`, `outputs/Q06.json`).

## 4. Current Committed Evidence State

The current entry-level evidence contains two committed shadow-log rows (`Q01`, `outputs/Q01.json`). The historical BMAP-source row is `OSH-0001`, which records `advisory_source = BMAP`, `source_bucket_mapping_id = BMAP-0001`, `source_pre_gate_advisory_snapshot_id = null`, `observed_overlay_bucket = ALLOW`, `mapped_bucket = ALLOW_REDUCED`, `size_multiplier = 0.5`, and `comparison_result = MISMATCH` (`Q01`, `outputs/Q01.json`).

The additive PGAS-source row is `OSH-0002`, which records `advisory_source = PGAS`, `source_bucket_mapping_id = BMAP-0001`, `source_pre_gate_advisory_snapshot_id = PGAS-0002`, `observed_overlay_bucket = ALLOW`, `mapped_bucket = ALLOW_REDUCED`, `size_multiplier = 0.5`, and `comparison_result = MISMATCH` (`Q01`, `outputs/Q01.json`).

Q06 grounds the additive PGAS path directly. The referenced snapshot `PGAS-0002` records `combination_rule_applied = MACRO_AWARE_FLOOR`, `combined_bucket = ALLOW_REDUCED`, `macro_window_flag = true`, `deterministic = true`, and `advisory_only = true` (`Q06`, `outputs/Q06.json`).

The latest-per-lineage view does not collapse one path into the other. Q02 still returns one latest row for `BMAP` and one latest row for `PGAS`, both currently `MISMATCH` (`Q02`, `outputs/Q02.json`).

## 5. MATCH vs MISMATCH

In this diagnostic brief, `MATCH` means the committed shadow-log comparison class says the observed overlay bucket and the advisory mapped bucket agreed. `MISMATCH` means the committed comparison class says they differed. The current committed corpus contains two rows and both are `MISMATCH`: the historical BMAP-source row `OSH-0001` and the additive PGAS-source row `OSH-0002` (`Q01`, `outputs/Q01.json`; `Q03`, `outputs/Q03.json`).

The current disagreement pattern is the same on both visible source paths. In each case the observed overlay bucket is `ALLOW` while the advisory-side mapped bucket is `ALLOW_REDUCED` (`Q01`, `outputs/Q01.json`).

A `MISMATCH` remains disagreement evidence only. In the current output set it does not coincide with override behavior: Q04 returns no zero-override audit rows, and Q03 reports `override_true_count = 0` for both the BMAP and PGAS `MISMATCH` classes (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`).

## 6. Evidence Sufficiency

The current corpus is larger than the first brief’s `n = 1`, but it is still small. Q03 reports exactly one BMAP-source `MISMATCH` row and one PGAS-source `MISMATCH` row, for a total corpus size of `n = 2` (`Q03`, `outputs/Q03.json`).

That is enough to show that the evidence path now captures both the historical BMAP-source lineage and the additive PGAS-source lineage. It is not enough to infer a stable agreement rate, disagreement rate, source-specific failure mode, or policy direction (`Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`).

The zero-row Q04 and Q05 outputs support a clean diagnostic boundary for this run, but they do not increase the evidence volume for policy inference. Clean override and integrity surfaces mean the current evidence is structurally clean, not decision-sufficient (`Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`).

## 7. Explicit Conclusion

The shadow evidence path is working at both source paths currently represented in the committed corpus. Entry-level evidence is queryable, latest-per-lineage evidence remains visible, and aggregate evidence is segmented by `advisory_source` (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`).

The honest current evidence conclusion is: two mismatches, zero overrides, clean integrity (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`).

The current evidence is still insufficient for policy inference because the aggregate evidence volume is `n = 2`. No overlay policy change, promotion, demotion, or non-shadow influence is justified by this output set, and the additive PGAS path should not be treated as better or worse from two observations (`Q03`, `outputs/Q03.json`).

## 8. Next-Step Recommendation

Continue accumulating shadow evidence through the existing committed artifact path, then review the aggregate views again after more observations exist. The next review should keep the same distinction used here: both the historical BMAP-source path and the additive PGAS-source path are now visible, but current `n = 2` evidence is still insufficient for policy inference (`Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`).

## 9. Artifacts in This Directory

- `queries/Q01..Q06*.sql`: exact read-only SQL used for this brief.
- `outputs/Q01..Q06.json`: committed JSON outputs from the stored SQL.
- `run_all_queries.py`: convenience helper to regenerate the JSON outputs through the read-only query CLI.
