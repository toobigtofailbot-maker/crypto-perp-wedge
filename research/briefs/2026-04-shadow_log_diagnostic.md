# Shadow-Log Diagnostic Brief

**Date:** 2026-04-20
**Scope:** Committed overlay shadow-log evidence exposed by the current query layer.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-shadow_log_diagnostic/`.
**Does not introduce:** Shadow-log entries, query-layer changes, policy changes, or runtime behavior.
**Does not recommend:** Overlay influence, promotion, demotion, or non-shadow execution use.

## 1. Purpose

This brief is the first diagnostic consumption of committed overlay shadow-log evidence through the aggregate shadow-signal views. It reads the existing query layer only and turns the current agreement/disagreement evidence into a reproducible diagnostic note (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`).

The purpose is interpretation discipline, not policy action. The brief records what the current committed evidence says, whether the zero-override boundary remains clean, and whether the evidence volume is enough for inference (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`).

## 2. Evidence Scope

Q01 reads `v_overlay_shadow_logs_overview`, the entry-level view over committed overlay shadow logs. It returns one row: `OSH-0001`, linked to `BMAP-0001` and `AOUT-0001` (`Q01`, `outputs/Q01.json`).

Q02 reads `v_overlay_shadow_agreement_summary`, the aggregate agreement/disagreement view. It returns one aggregate row for `MISMATCH` with `entry_count = 1`, `match_count = 0`, `mismatch_count = 1`, and `override_true_count = 0` (`Q02`, `outputs/Q02.json`).

Q03 reads `v_overlay_shadow_override_audit`, the zero-override audit view. It returns an empty JSON array, so this diagnostic run found no rows where override behavior, fail-open preservation, or advisory-only status violated the audit view (`Q03`, `outputs/Q03.json`).

Q04 reads `v_integrity_overlay_shadow_refs`, the shadow-reference integrity view. It returns an empty JSON array, so this diagnostic run found no unresolved or mismatched overlay-shadow references exposed by that integrity view (`Q04`, `outputs/Q04.json`).

## 3. Query Inventory

- `queries/Q01_shadow_overview.sql` stores the entry-level shadow-log query. Its output is `outputs/Q01.json`.
- `queries/Q02_shadow_agreement_summary.sql` stores the aggregate agreement/disagreement query. Its output is `outputs/Q02.json`.
- `queries/Q03_shadow_override_audit.sql` stores the zero-override audit query. Its output is `outputs/Q03.json`.
- `queries/Q04_shadow_integrity_refs.sql` stores the shadow-reference integrity query. Its output is `outputs/Q04.json`.

The outputs were produced by `research/briefs/2026-04-shadow_log_diagnostic/run_all_queries.py`, which executes the stored SQL through the existing read-only query CLI and writes JSON outputs beside the query files (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`).

## 4. Current Committed Evidence State

The committed entry-level evidence contains one shadow-log row: `OSH-0001`. The row records `observed_overlay_bucket = ALLOW`, `mapped_bucket = ALLOW_REDUCED`, `size_multiplier = 0.5`, and `comparison_result = MISMATCH` (`Q01`, `outputs/Q01.json`).

The same row records `override_applied = false`, `fail_open_preserved = true`, and `advisory_only = true` (`Q01`, `outputs/Q01.json`). The aggregate view reports `override_true_count = 0` for the current `MISMATCH` class (`Q02`, `outputs/Q02.json`).

The aggregate evidence currently spans one observation timestamp: `first_observed_at = 2026-04-19T17:00:00Z` and `last_observed_at = 2026-04-19T17:00:00Z` (`Q02`, `outputs/Q02.json`).

## 5. MATCH vs MISMATCH

In this diagnostic brief, `MATCH` means the committed shadow-log comparison class says the observed overlay bucket and advisory mapped bucket agreed. `MISMATCH` means the committed comparison class says they differed. The current entry is a `MISMATCH` because Q01 records `observed_overlay_bucket = ALLOW` and `mapped_bucket = ALLOW_REDUCED` for `OSH-0001` (`Q01`, `outputs/Q01.json`).

A `MISMATCH` is disagreement evidence only. In the current output set it does not coincide with override behavior: Q03 returns no zero-override audit rows, and Q02 reports `override_true_count = 0` (`Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`).

## 6. Evidence Sufficiency

The current evidence is sparse. Q02 reports exactly one committed shadow-log entry in the aggregate summary, and that one row belongs to the `MISMATCH` class (`Q02`, `outputs/Q02.json`).

One observed mismatch is enough to prove that the evidence path can record disagreement, but it is not enough to infer a stable agreement rate, disagreement rate, failure mode, or policy direction. The current outputs contain no matching observations, no repeated observations, and no distribution across time beyond the single timestamp returned by Q02 (`Q02`, `outputs/Q02.json`).

The zero-row Q03 and Q04 outputs support a clean diagnostic boundary for this run, but they do not increase the evidence volume for agreement/disagreement inference (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`).

## 7. Explicit Conclusion

The shadow evidence path is working: committed shadow-log evidence is queryable at entry level and aggregate level (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`).

Disagreement has been observed: the single committed row is `MISMATCH`, with observed overlay `ALLOW` and mapped advisory `ALLOW_REDUCED` (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`).

The current evidence is insufficient for policy inference because the aggregate evidence volume is `n = 1`. No overlay policy change, promotion, demotion, or non-shadow influence is justified by this output set (`Q02`, `outputs/Q02.json`).

The current zero-override and reference-integrity surfaces are clean for this diagnostic run: Q03 and Q04 both return empty JSON arrays (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`).

## 8. Next-Step Recommendation

Continue accumulating shadow evidence through the existing committed artifact path, then review the aggregate views again after more observations exist. The next review should keep the same distinction used here: disagreement evidence can motivate later inspection, but current `n = 1` evidence cannot justify overlay policy change or execution influence (`Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`).

## 9. Artifacts in This Directory

- `queries/Q01..Q04*.sql`: exact read-only SQL used for this brief.
- `outputs/Q01..Q04.json`: committed JSON outputs from the stored SQL.
- `run_all_queries.py`: convenience helper to regenerate the JSON outputs through the read-only query CLI.
