# Cross-Candidate Diagnostic Brief

**Date:** 2026-05-30
**Scope:** Current committed cross-candidate state from the extended read-only query layer.
**Evidence source:** Q01..Q12 outputs generated from committed query files.
**Does not introduce:** Any new candidate.
**Does not recommend:** A specific next candidate.
**Does not determine:** Candidate readiness or transition eligibility.

## 1. Methodology

This brief uses the package-local SQL files under `research/briefs/2026-05-cross_candidate_diagnostic_brief/queries/` and the generated JSON outputs under `research/briefs/2026-05-cross_candidate_diagnostic_brief/outputs/`. The candidate inventory, concluded-candidate posture, gate patterns, information-input coverage, query-layer footprint, integrity sweeps, and Scope 6 zero-instance checks come from Q01 through Q12 (`Q01`, `outputs/Q01.json`; `Q12`, `outputs/Q12.json`).

The SQL files were executed through the existing read-only query CLI by `research/briefs/2026-05-cross_candidate_diagnostic_brief/run_all_queries.py`. The brief treats the committed Q*.json outputs as its current-state evidence source and does not use prior prose as a substitute for query results.

## 2. What Changed Since WP-6e

For comparison to the WP-6e brief at `research/briefs/2026-04-cross_candidate_diagnostic.md`, the current registry-facing inventory returns ten `CONCLUDED` / `baseline_tested` candidates, H-001 through H-010, and one `DRAFT` / `reserved` registry row, H-011 (`Q01`, `outputs/Q01.json`).

The current query-layer footprint exposed to this brief contains 68 `v_*` views grouped as 8 candidate/experiment views, 9 lifecycle/evidence views, 14 advisory/shadow views, 24 non-Scope-6 integrity views, 5 Scope 6 base/link views, and 8 Scope 6 integrity views (`Q12`, `outputs/Q12.json`). Q07 lists the same registered view names and shows the Scope 6 base/link and Scope 6 integrity views in the read-only query surface (`Q07`, `outputs/Q07.json`).

## 3. Current Candidate Population / Status Distribution

Q01 returns ten concluded baseline-tested candidates and one draft reserved candidate (`Q01`, `outputs/Q01.json`). The concluded population is H-001 through H-010; H-011 is present only as a reserved draft row (`Q01`, `outputs/Q01.json`).

The concluded rows span nine strategy-family/timeframe/verdict groups. Every concluded group has `overall_verdict = NO-GO`; momentum on `1h` is the only returned concluded group with two candidates, H-005 and H-008 (`Q02`, `outputs/Q02.json`).

## 4. Outcome And Gate-Pattern Snapshot

The registry verdict distribution is ten `NO-GO` concluded candidates, and the outcome-ledger summary currently exposes 26 `research_oos` / `pre_wp_5b` artifacts across ten candidates plus 5 `research_oos` / `post_wp_5b` artifacts for H-004 (`Q03`, `outputs/Q03.json`). This is descriptive evidence only and does not re-verdict any candidate.

Q04 aggregates gate-result rows across the current experiment-report corpus. Gate 3 has 27 failures and zero passes across 27 gate-result rows; Gate 7 has 27 passes and zero failures across 27 gate-result rows (`Q04`, `outputs/Q04.json`). Q04 also shows Gate 1 and Gate 3 each failed for ten distinct candidates in the returned D2-006 gate-result rows (`Q04`, `outputs/Q04.json`). Gate counts here describe committed report rows and do not imply readiness.

## 5. Search-Space And Information-Input Coverage

Q05 returns the current strategy-family/timeframe coverage matrix. The matrix includes the ten concluded candidate rows and the reserved H-011 `cross_asset_regime` / `weekly` row with zero `NO-GO`, `PASS`, `CONDITIONAL`, or `INCONCLUSIVE` counts (`Q05`, `outputs/Q05.json`). Coverage is not a priority queue.

Q06 returns nine information-input labels. `funding_8h` appears for five candidates, `ohlcv_4h` for four, `ohlcv_1h` for three, `ohlcv_1d` and `ohlcv_30m` for two each, and `index_price_4h`, `mark_price_4h`, `premium_index_1h`, and `premium_index_4h` for one candidate each (`Q06`, `outputs/Q06.json`). Input coverage is not scored or ranked.

## 6. Scope 6 Query-Layer Exercise

The Scope 6 base views currently return zero rows for `v_r2s_approval_records`, `v_shadow_evidence_retention`, and `v_s2p_approval_records` (`Q09`, `outputs/Q09.json`). This is the expected healthy zero-instance state unless repo truth later adds Scope 6 artifact instances.

The Scope 6 inventory view returns 11 registry rows and zero total R2S approval-record, shadow-evidence-retention, and S2P approval-record counts; the S2P-to-shadow-evidence link view returns zero rows (`Q10`, `outputs/Q10.json`). Empty Scope 6 views are a query-layer exercise result, not a candidate finding.

## 7. Data Integrity / Read-Only Checks

Q08 returns an empty array for the full discovered `v_integrity_*` sweep encoded in Q08.sql (`Q08`, `outputs/Q08.json`). Q11 returns an empty array for the Scope 6 integrity subset covering R2S, shadow-evidence, S2P, authority-flag, and preservation-flag checks (`Q11`, `outputs/Q11.json`).

Clean integrity outputs do not approve, promote, transition, or determine readiness for any candidate. They only show that the committed query-layer integrity views used in this package returned no rows (`Q08`, `outputs/Q08.json`; `Q11`, `outputs/Q11.json`).

## 8. Query-Layer Observations

Q07 lists the registered `v_*` views and classifies Scope 6 base/link and Scope 6 integrity views separately (`Q07`, `outputs/Q07.json`). Q12 groups the current footprint into six categories and reports 68 total `v_*` views across those categories (`Q12`, `outputs/Q12.json`).

The Scope 6 footprint consists of five base/link views and eight Scope 6 integrity views in Q12 (`Q12`, `outputs/Q12.json`). View presence grants no readiness, approval, transition, promotion, ranking, scoring, recommendation, policy, runtime, or human-gate execution authority.

## 9. Scope-Explicit Non-Findings

This brief does not recommend, rank, score, select, approve, promote, transition, or determine readiness for any candidate. Q01 through Q12 describe inventory, artifacts, view footprint, Scope 6 zero-instance behavior, and integrity results only (`Q01`, `outputs/Q01.json`; `Q12`, `outputs/Q12.json`).

The zero rows in the Scope 6 base views do not mean a candidate failed or passed a Scope 6 review; they mean no Scope 6 approval-record or shadow-evidence-retention instances are present in the current committed query-layer state (`Q09`, `outputs/Q09.json`; `Q10`, `outputs/Q10.json`). The empty Scope 6 integrity output does not approve future transitions (`Q11`, `outputs/Q11.json`).

This brief may inform future Main/Karl routing, but it does not decide routing, readiness, approval, or transition.

## 10. Artifacts In This Directory

- `queries/Q01.sql` through `queries/Q12.sql`: the exact read-only SQL files run for this brief.
- `outputs/Q01.json` through `outputs/Q12.json`: committed deterministic query outputs.
- `run_all_queries.py`: package-local helper for regenerating Q01 through Q12 outputs.

## 11. What This Brief Enables For Future Packages

Future packages can cite this brief as a query-output-backed snapshot of the current cross-candidate inventory, Scope 6 zero-instance query behavior, and integrity-sweep state (`Q01`, `outputs/Q01.json`; `Q08`, `outputs/Q08.json`; `Q09`, `outputs/Q09.json`; `Q11`, `outputs/Q11.json`). Any future routing, approval, transition, readiness, implementation, or policy decision remains outside this brief.
