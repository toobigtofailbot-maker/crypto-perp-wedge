# Cross-Candidate Diagnostic Brief

**Date:** 2026-04-19
**Scope:** Ten concluded candidates H-001..H-010
**Evidence source:** Query layer (`tools/research_query/`) run against committed registry and experiment artifacts.
**Does not introduce:** Any new candidate.
**Does not recommend:** A specific next candidate.

## 1. Methodology

Evidence in this brief is derived from the WP-6d query layer, using nine committed SQL queries and their raw JSON outputs under `research/briefs/2026-04-cross_candidate_diagnostic/`. The candidate population is the concluded-candidate set returned by Q01: H-001 through H-010, each at `pipeline_stage = baseline_tested` with one referenced trial (`Q01`, `outputs/Q01.json`).

The queries were run through the existing read-only CLI, not by walking decision records. Reviewers can reproduce the outputs with `research/briefs/2026-04-cross_candidate_diagnostic/run_all_queries.py`. Before and after the query run, checksums were compared for the registry, trial log, experiment JSON artifacts, query-layer files, and schemas; no protected artifact changed during analysis.

Every factual claim below cites a specific Q## output file. Existing research briefs cover related territory, but this brief treats the query outputs as the source of truth.

## 2. What Was Tested

Q01 returns ten concluded baseline-tested candidates, each with one trial reference (`Q01`, `outputs/Q01.json`). The tested candidates span eight strategy-family labels: `basis_mean_reversion`, `breakout`, `funding_directional`, `funding_momentum_composite`, `mean_reversion`, `momentum`, `multi_tf_alignment`, and `trend_following` (`Q02`, `outputs/Q02.json`).

The concluded baselines occupy four primary timeframes: `30m`, `1h`, `4h`, and `1d` (`Q08`, `outputs/Q08.json`). The `4h` rows include H-001, H-002, H-007, and H-010; the `1h` rows include H-005 and H-008; the `30m` rows include H-006 and H-009; the `1d` rows include H-003 and H-004 (`Q08`, `outputs/Q08.json`).

The exercised information streams include OHLCV streams at `30m`, `1h`, `4h`, and `1d`, plus `funding_8h`, `index_price_4h`, `mark_price_4h`, `premium_index_1h`, and `premium_index_4h` (`Q07`, `outputs/Q07.json`). `funding_8h` appears for five candidates, `ohlcv_4h` for four, `ohlcv_1h` for three, `ohlcv_1d` for two, and `ohlcv_30m` for two (`Q07`, `outputs/Q07.json`). Mark, index, and premium streams appear only in the H-008 or H-010 rows returned by Q07 (`Q07`, `outputs/Q07.json`).

## 3. Outcome Distribution

All concluded candidates are `NO-GO` in the verdict-by-family query (`Q02`, `outputs/Q02.json`). The `momentum` and `trend_following` families each have two `NO-GO` candidates; each other returned family has one `NO-GO` candidate (`Q02`, `outputs/Q02.json`). This makes the observed failure distribution broad across the tested family labels, rather than concentrated in only one family (`Q02`, `outputs/Q02.json`).

No candidate passed Gate 1. Q03 returns ten rows with `gate1_pass = false`, and the best OOS Sharpe is H-004 at 0.746191460507614 against a Gate 1 threshold of `1.0` (`Q03`, `outputs/Q03.json`). The remaining positive Sharpe rows are H-010 at 0.46477526210643, H-005 at 0.3751092454780985, and H-002 at 0.07581376350868253; the other six rows are negative (`Q03`, `outputs/Q03.json`).

No candidate passed Gate 3. Q04 returns ten rows with `gate3_pass = false` against a Gate 3 threshold of `0.2` (`Q04`, `outputs/Q04.json`). The smallest returned OOS max drawdown is H-004 at 0.697949870640699, and the largest is H-008 at 39.2885145105369 (`Q04`, `outputs/Q04.json`). These are historical report metrics from the committed retrospective reports; this brief does not infer post-fix counterfactual drawdown values (`Q04`, `outputs/Q04.json`).

The trade-count distribution is lower on `1d` and higher on the intraday rows. Q05 returns `timeframe_avg_trades = 38.0` for `1d`, 236.75 for `4h`, 1537.0 for `30m`, and 3072.5 for `1h` (`Q05`, `outputs/Q05.json`). Cost-drag values are mixed rather than monotonic by timeframe: `timeframe_avg_cost_drag` is 0.24951047167244045 for `1d`, 1.9743365283840664 for `4h`, 3.35335 for `30m`, and 0.5374000000000001 for `1h` (`Q05`, `outputs/Q05.json`). Q05 supports a descriptive turnover pattern, but not a causal claim that shorter timeframe alone caused worse cost drag (`Q05`, `outputs/Q05.json`).

## 4. Gate Failure Patterns

Gate failure was most uniform at Gate 1 and Gate 3. Q06 shows Gate 1 with `n_pass = 0` and `n_fail = 10`, and Gate 3 with `n_pass = 0` and `n_fail = 10` (`Q06`, `outputs/Q06.json`). Gate 7 was the only universally passed gate, with `n_pass = 10` and `n_fail = 0` (`Q06`, `outputs/Q06.json`).

The next broadest failures were Gate 4 with `n_fail = 8`, Gate 6 with `n_fail = 7`, and Gates 2 and 8 with `n_fail = 6` each (`Q06`, `outputs/Q06.json`). Gate 5 split the population evenly, with `n_pass = 5` and `n_fail = 5` (`Q06`, `outputs/Q06.json`). The decisive common filters were therefore Sharpe and drawdown, with parameter sensitivity and concentration failures also appearing across most candidates (`Q06`, `outputs/Q06.json`).

## 5. Search-Space Coverage

The concluded baseline matrix covers four primary timeframes but not weekly baselines. Q08 contains one `cross_asset_regime` / `weekly` row, but that row has `n_concluded_baselines = 0`, `n_non_concluded_slots = 1`, and `candidate_ids = H-011` (`Q08`, `outputs/Q08.json`). Q08 therefore records a reserved weekly slot, not a tested weekly candidate (`Q08`, `outputs/Q08.json`).

The family-timeframe matrix is sparse by design. Trend-following appears on both `1d` and `4h`; momentum appears on `1h` with two concluded baselines; all other concluded family-timeframe rows have one concluded baseline each (`Q08`, `outputs/Q08.json`). No row in Q08 shows a concluded cross-asset baseline (`Q08`, `outputs/Q08.json`).

The information-input query shows no exercised cross-asset data stream. Q07 lists funding, OHLCV, mark price, index price, and premium-index inputs, but no gold, macro, equity-index, or other cross-asset input label (`Q07`, `outputs/Q07.json`). The exercised non-OHLCV streams are still crypto-perp internal streams: funding, mark, index, and premium (`Q07`, `outputs/Q07.json`).

## 6. Data Integrity

Q09 combines `v_integrity_plan_report_pairs` and `v_integrity_candidate_refs`. It returns an empty JSON array, so the committed plan/report pairings and candidate references have no rows in the integrity views (`Q09`, `outputs/Q09.json`). The diagnostic findings above therefore rest on internally consistent query-layer inputs as exposed by WP-6d (`Q09`, `outputs/Q09.json`).

## 7. Query Layer Observations

The existing views made the main diagnostic questions directly answerable. Candidate inventory came from `v_concluded_candidates`, verdict distribution from `v_concluded_candidates`, OOS metrics from `v_oos_metrics_by_candidate`, gate outcomes from `v_gate_results_flat`, information inputs from `v_information_inputs`, family-timeframe coverage from `v_candidate_overview`, and integrity checks from the two integrity views (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q06`, `outputs/Q06.json`; `Q07`, `outputs/Q07.json`; `Q08`, `outputs/Q08.json`; `Q09`, `outputs/Q09.json`).

Some questions required ad-hoc SQL on top of the views rather than a single named view. Gate-threshold interpretation in Q03 and Q04 required joining OOS metrics to `v_gate_results_flat`; per-gate pass/fail counts in Q06 required grouping the flattened gate rows (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q06`, `outputs/Q06.json`).

The query layer could express the absence of concluded weekly and cross-asset baselines through existing rows. Q08 shows the weekly cross-asset row only as a non-concluded slot, and Q07 shows no exercised cross-asset information input (`Q07`, `outputs/Q07.json`; `Q08`, `outputs/Q08.json`).

## 8. Scope-Explicit Non-Findings

This brief does not recommend a specific next candidate. The query outputs describe the tested population, gate outcomes, information-input coverage, and family-timeframe coverage only (`Q01`, `outputs/Q01.json`; `Q06`, `outputs/Q06.json`; `Q07`, `outputs/Q07.json`; `Q08`, `outputs/Q08.json`).

This brief does not prescribe schema or view changes. Section 7 records how the existing views were used and where ad-hoc SQL was needed (`Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q06`, `outputs/Q06.json`).

This brief does not re-verdict any existing candidate. Q02 returns only `NO-GO` verdict rows for the concluded candidate families, and Q01 returns the same concluded baseline-tested population used for the diagnostic scope (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`).

## 9. Artifacts in This Directory

- `queries/Q01..Q09.sql`: the exact queries run.
- `outputs/Q01..Q09.json`: the committed query results.
- `run_all_queries.py`: convenience re-run helper.

## 10. What This Brief Enables (For a Future Package)

Any future candidate registration can cite this brief's coverage findings to explain how it differs from the tested population, without this brief selecting that candidate (`Q07`, `outputs/Q07.json`; `Q08`, `outputs/Q08.json`). Any future bounded research consumer can use this artifact package as an example of structured query outputs feeding a human-authored diagnostic synthesis (`Q01`, `outputs/Q01.json`; `Q09`, `outputs/Q09.json`). Any future Diagram 2 stage-3 artifact can treat this stage-1 and stage-2 instance as upstream evidence, while leaving proposal content to a separate scoped package (`Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q06`, `outputs/Q06.json`).
