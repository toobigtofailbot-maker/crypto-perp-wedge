# Third Cross-Candidate Diagnostic Brief

**Date:** 2026-06-01
**Scope:** Current committed cross-candidate state with H-012 included.
**Evidence source:** Committed Q01..Q14 SQL and JSON outputs in `research/briefs/2026-06-third_cross_candidate_diagnostic_brief/`.
**Does not introduce:** Any new candidate.
**Does not recommend:** A specific next candidate.
**Does not recommend:** Continuing or stopping Path B.
**Does not determine:** Candidate readiness or transition eligibility.

## 1. Methodology

This brief uses the package-local SQL files under `research/briefs/2026-06-third_cross_candidate_diagnostic_brief/queries/` and the generated JSON outputs under `research/briefs/2026-06-third_cross_candidate_diagnostic_brief/outputs/`. Q01 through Q14 cover current candidate inventory, the WP-S2c-119 diff snapshot, H-012 artifact-chain evidence, D2-006 gate patterns, information-input coverage, outcome-ledger and reconciliation posture, Scope 6 zero-instance behavior, integrity-view row counts, query-layer footprint, and REC-5 exact-segment counts (Q01, outputs/Q01.json; Q14, outputs/Q14.json).

The SQL files were executed through the existing read-only query CLI by `research/briefs/2026-06-third_cross_candidate_diagnostic_brief/run_all_queries.py`. Current-state claims below cite committed Q*.json outputs; prior design and checkpoint documents remain context only and are not substitutes for current query output.

## 2. What Changed Since WP-S2c-119

Q03 records the WP-S2c-119 reference count as ten concluded candidates, the current concluded-candidate count as eleven, and the concluded-candidate delta as one (Q03, outputs/Q03.json). The same output identifies the delta row as H-012 and records H-012 as `CONCLUDED` / `NO-GO` / `baseline_tested` with `EXP-0012`, `REP-0032`, `OL-0032`, `REC-0051`, and `research/decisions/DEC-0011.md` in the artifact chain (Q03, outputs/Q03.json).

Q03 also records one H-011 reserved draft row and one H-012 concluded row (Q03, outputs/Q03.json). The query output does not mutate or reinterpret the WP-S2c-119-era state; it only places the current committed state beside the prior reference count used for this diff snapshot.

## 3. Current Candidate Population / Status Distribution

Q01 returns eleven `CONCLUDED` / `NO-GO` / `baseline_tested` candidates: H-001 through H-010 plus H-012 (Q01, outputs/Q01.json). Q01 also returns one `DRAFT` / `PENDING` / `reserved` row for H-011, with no decision record and zero trial IDs (Q01, outputs/Q01.json).

The concluded-candidate distribution contains ten strategy-family/timeframe/verdict rows, all with `overall_verdict = NO-GO`; `momentum` / `1h` is the only returned concluded group with two candidates, H-005 and H-008 (Q02, outputs/Q02.json). H-012 appears as one `trend_following` / `15m` / `NO-GO` concluded row (Q02, outputs/Q02.json).

## 4. H-012 Delta And Artifact Chain

Q07 records H-012 as `CONCLUDED` / `NO-GO` / `baseline_tested`, with strategy family `trend_following`, timeframe `15m`, and information inputs `ohlcv_15m` and `funding_8h` (Q07, outputs/Q07.json). Q07 links H-012 to `EXP-0012`, `REP-0032`, `OL-0032`, `REC-0051`, and `research/decisions/DEC-0011.md` (Q07, outputs/Q07.json).

For H-012, Q07 records `REP-0032` as `NO-GO`, `REC-0051` as `none_met`, 1 of 8 D2-006 gates passed, OOS Sharpe `-0.8317508855081367`, max drawdown `1.0`, final equity `0.0`, liquidation `true`, and 160 trades (Q07, outputs/Q07.json). Those values describe current committed evidence only; they do not re-verdict H-012 or create any readiness or transition authority.

## 5. Outcome And D2-006 Gate-Pattern Snapshot

Q04 returns D2-006 gate-result rows across the current report corpus and includes the H-012 `REP-0032` summary row with 8 gate rows, 1 pass, and 7 failures (Q04, outputs/Q04.json). Across the D2-006 rows returned by Q04, Gate 3 has 28 failures and zero passes, while Gate 7 has 28 passes and zero failures (Q04, outputs/Q04.json).

Q04 also shows H-012 as the only row under the exact Gate 6 label `D2-006-G6: No single 90-day window > 60% of total PnL`, with one failure and zero passes (Q04, outputs/Q04.json). This label distinction is a query-output observation, not a methodology change or readiness implication.

## 6. Search-Space And Information-Input Coverage

Q05 returns the current strategy-family/timeframe matrix. It includes H-012 as the only `trend_following` / `15m` row, with one candidate, one concluded row, and one `NO-GO` count (Q05, outputs/Q05.json). Q05 also keeps H-011 visible as the only `cross_asset_regime` / `weekly` row, with one non-concluded row and zero concluded rows (Q05, outputs/Q05.json).

Q06 returns ten information-input labels. `funding_8h` appears for six candidates including H-012, and `ohlcv_15m` appears for one candidate, H-012 (Q06, outputs/Q06.json). The same output records `ohlcv_4h` for four candidates, `ohlcv_1h` for three, `ohlcv_1d` and `ohlcv_30m` for two each, and the mark/index/premium inputs for one candidate each (Q06, outputs/Q06.json).

Coverage is descriptive only. Q05 and Q06 do not rank strategy families, score information inputs, select a next candidate, or recommend Path B continuation or termination (Q05, outputs/Q05.json; Q06, outputs/Q06.json).

## 7. Outcome-Ledger / Reconciliation / REC-5 Posture

Q08 records one H-012 outcome-ledger segment for `research_oos` / `post_wp_5b` and one H-012 reconciliation segment for `research_oos` / `post_wp_5b` / `d2_006_gates`, with reconciliation verdict `none_met` (Q08, outputs/Q08.json). Q14 records the same H-012 exact segment count as 1 and `rec5_floor_satisfied = false` (Q14, outputs/Q14.json).

The broader REC corpus in Q14 includes some exact segments with count 3 and `rec5_floor_satisfied = true`, and other exact segments with count 1 and `rec5_floor_satisfied = false` (Q14, outputs/Q14.json). This brief makes no cross-segment inference from those rows; H-012's segment remains H-012 / `research_oos` / `post_wp_5b` / `d2_006_gates` = 1 (Q14, outputs/Q14.json).

## 8. Scope 6 Query-Layer Exercise

Q10 records zero rows in `v_r2s_approval_records`, zero rows in `v_shadow_evidence_retention`, and zero rows in `v_s2p_approval_records` (Q10, outputs/Q10.json). Q11 records zero rows in `v_s2p_shadow_evidence_links` and zero total R2S approval, shadow-evidence-retention, and S2P approval counts across the candidate packaging overview (Q11, outputs/Q11.json).

Q12 records zero issue rows across the eight Scope 6 integrity views returned in that query (Q12, outputs/Q12.json). Empty Scope 6 base, link, and integrity outputs are a zero-instance query-layer exercise only; they do not approve, transition, promote, or determine readiness for any candidate.

## 9. Data Integrity / Read-Only Checks

Q09 records 32 discovered `v_integrity_*` views and an issue count of zero for every row, including `v_integrity_plan_report_pairs` (Q09, outputs/Q09.json). Q12 separately records zero issue rows across the Scope 6 integrity subset (Q12, outputs/Q12.json).

Clean integrity row counts show that the committed integrity views used in this package returned no issue rows (Q09, outputs/Q09.json; Q12, outputs/Q12.json). They do not grant candidate approval, readiness, transition, promotion, ranking, scoring, recommendation, policy, runtime, or human-gate execution authority.

## 10. Query-Layer Observations

Q13 records 68 total `v_*` views in the current read-only query layer (Q13, outputs/Q13.json). The same output classifies 32 integrity views, five Scope 6 base/link views, twelve advisory/shadow views, twelve candidate/experiment views, and seven lifecycle/evidence views (Q13, outputs/Q13.json).

Q09 confirms that the WP-S2c-127b-refined `v_integrity_plan_report_pairs` surface is part of the integrity sweep and has issue count zero in this current run (Q09, outputs/Q09.json). Q13 confirms the Scope 6 query surfaces remain present in the view footprint (Q13, outputs/Q13.json).

## 11. Deferred Items Unchanged

The package design and checkpoint context keep C/F deferred, monitoring/dashboard deferred, the paper bridge unauthorized, AUTO bridge frozen, and A2C-003 unauthorized. This brief does not convert those deferred items into query-derived metrics.

The current query outputs instead bound what this package actually exercised: candidate inventory, H-012 artifact-chain evidence, D2-006 gate rows, outcome/reconciliation rows, REC-5 exact segments, Scope 6 zero-instance views, integrity row counts, and query-layer footprint (Q01, outputs/Q01.json; Q14, outputs/Q14.json).

## 12. Scope-Explicit Non-Findings

This brief does not recommend, rank, score, select, approve, promote, transition, or determine readiness for any candidate. Q01 through Q14 describe current inventory, artifacts, gate rows, information inputs, exact-segment counts, Scope 6 zero-instance behavior, integrity rows, and view footprint only (Q01, outputs/Q01.json; Q14, outputs/Q14.json).

The H-012 `NO-GO` and `none_met` rows are current committed evidence-state records, not a new recommendation by this brief (Q07, outputs/Q07.json; Q14, outputs/Q14.json). The Scope 6 zero-instance rows do not mean a candidate passed or failed a Scope 6 review; they mean the current committed query layer returns no Scope 6 approval-record, shadow-evidence-retention, or S2P-link instances (Q10, outputs/Q10.json; Q11, outputs/Q11.json).

## 13. Artifacts In This Directory

- `queries/Q01.sql` through `queries/Q14.sql`: the exact read-only SQL files run for this brief.
- `outputs/Q01.json` through `outputs/Q14.json`: committed deterministic query outputs.
- `run_all_queries.py`: package-local helper for regenerating Q01 through Q14 outputs.

## 14. What This Brief Enables For Main/Karl Routing

This brief gives Main/Karl a query-output-backed snapshot of the current cross-candidate state after H-012: eleven concluded `NO-GO` candidates, one H-011 reserved draft row, H-012's post-WP-S2c-119 artifact chain, H-012's D2-006 and REC-5 posture, Scope 6 zero-instance behavior, and clean integrity row counts (Q01, outputs/Q01.json; Q03, outputs/Q03.json; Q07, outputs/Q07.json; Q09, outputs/Q09.json; Q14, outputs/Q14.json).

Post-brief direction remains outside this artifact. After merge, Side must stop and report back to Main/Karl for any next route, and no further work package is authorized by this brief.
