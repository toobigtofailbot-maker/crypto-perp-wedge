# Item 6 Robustness Report - RP-0007

Derived non-authoritative robustness diagnostic.

## Report Identity

- input_result_population_id: RP-0007
- input_path: research/result_populations/RP-0007.result_population.json
- report_scope: derived_non_authoritative_item6_robustness_reporting
- psr_status: withheld_missing_inputs
- dsr_status: withheld_missing_inputs
- min_trl_status: withheld_missing_inputs

## Parent Lineage

- strategy_spec_id: STRAT-SPEC-0007
- variant_manifest_id: VM-0007
- sweep_plan_id: SWEEP-PLAN-0007
- result_population_id: RP-0007
- complete_population_lineage_preserved: True

## Data Provenance

- data_catalog_ref: research/data_slices/binance_usdtm_btcusdt_1d/binance_usdtm_btcusdt_1d_20200101_20260411.catalog_slice.json#sha256:51fc09918841cd3ac353efe375af91a4732080571f9b1af634f5d1a426217adb
- data_slice_identity: binance_usdtm_btcusdt_ohlcv_1d:identity_sha256:05ce3d5fdb5186ae36f612e2c51393eaecb110a66b0c3506e5583f3acedd443f
- timeframe: 1d
- data_stream: ohlcv
- missing_data_policy: block_if_missing
- irreparable_gap_count: 0
- data_unavailable_count: 0
- data_posture: committed_offline_result_population_data_posture
- provenance_caveat: RP-0007 is a committed offline result population; this derived diagnostic is descriptive only and does not claim strategy edge.

## Committed Denominator Snapshot

- committed_denominator: 81
- outcome_counts_sum: 81
- result_row_count: 81
- denominator_basis: committed_pre_registered_population_count
- DSR and multiple-testing-aware metrics must use the committed denominator, not only successful variants.
- Failed, errored, invalid, excluded, filtered, data_unavailable, not_attempted, and aborted variants remain denominator members in future populations.
- No winner-only denominator.
- No executed-only denominator.

## Outcome Distribution

- successful: 81
- failed: 0
- invalid: 0
- excluded: 0
- errored: 0
- aborted: 0
- filtered: 0
- data_unavailable: 0
- not_attempted: 0
- counts_sum: 81

## Trial Accounting

- trial_log_path: research/trial_log.jsonl
- trial_log_state: present
- trial_count_source: valid_rows_in_committed_trial_log_jsonl
- countable_trial_denominator: 32
- valid_trial_rows: 32
- invalid_trial_rows: 0
- unique_trial_ids: 32
- duplicate_trial_ids: []
- hypothesis_counts: {"H-001": 5, "H-002": 3, "H-003": 3, "H-004": 8, "H-005": 5, "H-006": 3, "H-007": 1, "H-008": 1, "H-009": 1, "H-010": 1, "H-012": 1}
- n_obs_min: 19
- n_obs_max: 110063
- missing_required_field_counts: {}
- The denominator is the full count of valid trial-log rows, not a winner-only or successful-only subset.
- The trial log does not expose failed, unavailable, aborted, or unlogged attempted trials beyond rows that exist in the JSONL file.
- Duplicate trial_id values, if present, are surfaced as diagnostics rather than silently removed from the denominator.

## Available Metric Summary

- available_metric_fields: drawdown, exposure, fees, funding, pnl, return_pct, sharpe, slippage, trade_count, win_rate

| variant_id | outcome | attempted | sharpe | return_pct | pnl | drawdown | trade_count |
|---|---|---:|---:|---:|---:|---:|---:|
| VAR-000001 | successful | True | 0.788939315832 | 5.64773472011 | 56477.3472011 | 0.664129854834 | 101 |
| VAR-000002 | successful | True | 0.788939315832 | 5.64773472011 | 56477.3472011 | 0.664129854834 | 101 |
| VAR-000003 | successful | True | 0.788939315832 | 5.64773472011 | 56477.3472011 | 0.664129854834 | 101 |
| VAR-000004 | successful | True | 0.788939315832 | 5.64773472011 | 56477.3472011 | 0.664129854834 | 101 |
| VAR-000005 | successful | True | 0.788939315832 | 5.64773472011 | 56477.3472011 | 0.664129854834 | 101 |
| VAR-000006 | successful | True | 0.788939315832 | 5.64773472011 | 56477.3472011 | 0.664129854834 | 101 |
| VAR-000007 | successful | True | 0.788939315832 | 5.64773472011 | 56477.3472011 | 0.664129854834 | 101 |
| VAR-000008 | successful | True | 0.788939315832 | 5.64773472011 | 56477.3472011 | 0.664129854834 | 101 |
| VAR-000009 | successful | True | 0.788939315832 | 5.64773472011 | 56477.3472011 | 0.664129854834 | 101 |
| VAR-000010 | successful | True | 0.838531597789 | 6.87669590159 | 68766.9590159 | 0.701069053053 | 97 |
| VAR-000011 | successful | True | 0.838531597789 | 6.87669590159 | 68766.9590159 | 0.701069053053 | 97 |
| VAR-000012 | successful | True | 0.838531597789 | 6.87669590159 | 68766.9590159 | 0.701069053053 | 97 |
| VAR-000013 | successful | True | 0.838531597789 | 6.87669590159 | 68766.9590159 | 0.701069053053 | 97 |
| VAR-000014 | successful | True | 0.838531597789 | 6.87669590159 | 68766.9590159 | 0.701069053053 | 97 |
| VAR-000015 | successful | True | 0.838531597789 | 6.87669590159 | 68766.9590159 | 0.701069053053 | 97 |
| VAR-000016 | successful | True | 0.838531597789 | 6.87669590159 | 68766.9590159 | 0.701069053053 | 97 |
| VAR-000017 | successful | True | 0.838531597789 | 6.87669590159 | 68766.9590159 | 0.701069053053 | 97 |
| VAR-000018 | successful | True | 0.838531597789 | 6.87669590159 | 68766.9590159 | 0.701069053053 | 97 |
| VAR-000019 | successful | True | 0.808418640291 | 6.30785818429 | 63078.5818429 | 0.701069053053 | 97 |
| VAR-000020 | successful | True | 0.808418640291 | 6.30785818429 | 63078.5818429 | 0.701069053053 | 97 |
| VAR-000021 | successful | True | 0.808418640291 | 6.30785818429 | 63078.5818429 | 0.701069053053 | 97 |
| VAR-000022 | successful | True | 0.808418640291 | 6.30785818429 | 63078.5818429 | 0.701069053053 | 97 |
| VAR-000023 | successful | True | 0.808418640291 | 6.30785818429 | 63078.5818429 | 0.701069053053 | 97 |
| VAR-000024 | successful | True | 0.808418640291 | 6.30785818429 | 63078.5818429 | 0.701069053053 | 97 |
| VAR-000025 | successful | True | 0.808418640291 | 6.30785818429 | 63078.5818429 | 0.701069053053 | 97 |
| VAR-000026 | successful | True | 0.808418640291 | 6.30785818429 | 63078.5818429 | 0.701069053053 | 97 |
| VAR-000027 | successful | True | 0.808418640291 | 6.30785818429 | 63078.5818429 | 0.701069053053 | 97 |
| VAR-000028 | successful | True | 0.869085769483 | 6.83113057866 | 68311.3057866 | 0.6233393598 | 75 |
| VAR-000029 | successful | True | 0.903446374088 | 8.16096573564 | 81609.6573564 | 0.651247228503 | 75 |
| VAR-000030 | successful | True | 0.874703335217 | 7.36995010926 | 73699.5010926 | 0.640704014089 | 75 |
| VAR-000031 | successful | True | 0.869085769483 | 6.83113057866 | 68311.3057866 | 0.6233393598 | 75 |
| VAR-000032 | successful | True | 0.903446374088 | 8.16096573564 | 81609.6573564 | 0.651247228503 | 75 |
| VAR-000033 | successful | True | 0.874703335217 | 7.36995010926 | 73699.5010926 | 0.640704014089 | 75 |
| VAR-000034 | successful | True | 0.869085769483 | 6.83113057866 | 68311.3057866 | 0.6233393598 | 75 |
| VAR-000035 | successful | True | 0.903446374088 | 8.16096573564 | 81609.6573564 | 0.651247228503 | 75 |
| VAR-000036 | successful | True | 0.874703335217 | 7.36995010926 | 73699.5010926 | 0.640704014089 | 75 |
| VAR-000037 | successful | True | 0.877157479389 | 7.05847062383 | 70584.7062383 | 0.676602321741 | 73 |
| VAR-000038 | successful | True | 0.908197572817 | 8.3883057808 | 83883.057808 | 0.706894855756 | 73 |
| VAR-000039 | successful | True | 0.881016457951 | 7.59729015442 | 75972.9015442 | 0.695450747119 | 73 |
| VAR-000040 | successful | True | 0.877157479389 | 7.05847062383 | 70584.7062383 | 0.676602321741 | 73 |
| VAR-000041 | successful | True | 0.908197572817 | 8.3883057808 | 83883.057808 | 0.706894855756 | 73 |
| VAR-000042 | successful | True | 0.881016457951 | 7.59729015442 | 75972.9015442 | 0.695450747119 | 73 |
| VAR-000043 | successful | True | 0.877157479389 | 7.05847062383 | 70584.7062383 | 0.676602321741 | 73 |
| VAR-000044 | successful | True | 0.908197572817 | 8.3883057808 | 83883.057808 | 0.706894855756 | 73 |
| VAR-000045 | successful | True | 0.881016457951 | 7.59729015442 | 75972.9015442 | 0.695450747119 | 73 |
| VAR-000046 | successful | True | 0.881420053832 | 7.14257842546 | 71425.7842546 | 0.676602321741 | 73 |
| VAR-000047 | successful | True | 0.91142858527 | 8.47241358244 | 84724.1358244 | 0.706894855756 | 73 |
| VAR-000048 | successful | True | 0.884605286679 | 7.68139795606 | 76813.9795606 | 0.695450747119 | 73 |
| VAR-000049 | successful | True | 0.881420053832 | 7.14257842546 | 71425.7842546 | 0.676602321741 | 73 |
| VAR-000050 | successful | True | 0.91142858527 | 8.47241358244 | 84724.1358244 | 0.706894855756 | 73 |
| VAR-000051 | successful | True | 0.884605286679 | 7.68139795606 | 76813.9795606 | 0.695450747119 | 73 |
| VAR-000052 | successful | True | 0.881420053832 | 7.14257842546 | 71425.7842546 | 0.676602321741 | 73 |
| VAR-000053 | successful | True | 0.91142858527 | 8.47241358244 | 84724.1358244 | 0.706894855756 | 73 |
| VAR-000054 | successful | True | 0.884605286679 | 7.68139795606 | 76813.9795606 | 0.695450747119 | 73 |
| VAR-000055 | successful | True | -0.575395918865 | -1 | -10000 | 1 | 9 |
| VAR-000056 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000057 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000058 | successful | True | -0.575395918865 | -1 | -10000 | 1 | 9 |
| VAR-000059 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000060 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000061 | successful | True | -0.575395918865 | -1 | -10000 | 1 | 9 |
| VAR-000062 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000063 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000064 | successful | True | -0.575395918865 | -1 | -10000 | 1 | 9 |
| VAR-000065 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000066 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000067 | successful | True | -0.575395918865 | -1 | -10000 | 1 | 9 |
| VAR-000068 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000069 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000070 | successful | True | -0.575395918865 | -1 | -10000 | 1 | 9 |
| VAR-000071 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000072 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000073 | successful | True | -0.575395918865 | -1 | -10000 | 1 | 9 |
| VAR-000074 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000075 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000076 | successful | True | -0.575395918865 | -1 | -10000 | 1 | 9 |
| VAR-000077 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000078 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000079 | successful | True | -0.575395918865 | -1 | -10000 | 1 | 9 |
| VAR-000080 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |
| VAR-000081 | successful | True | -0.590141102741 | -1 | -10000 | 1 | 9 |

## PSR / DSR / MinTRL Readiness Assessment

- PSR: withheld_missing_inputs; rigorous numeric PSR cannot be computed from the available result-population fields.
- DSR: withheld_missing_inputs; rigorous numeric DSR cannot be computed from the available result-population fields.
- MinTRL: withheld_missing_inputs; rigorous numeric MinTRL cannot be computed from the available result-population fields.
- multiple_testing_inputs_present: {"committed_result_population_denominator": true, "declared_selection_rule": false, "effective_independent_trial_count": false, "return_distribution_moments": false, "trial_log_denominator": true}
- No fabricated PSR, DSR, or MinTRL numeric values are emitted.

## OOS / IS Efficiency

- status: withheld_missing_window_inputs
- metric: out_of_sample_sharpe / in_sample_sharpe
- computed_count: 0
- mean: null
- missing_input_warnings: ["walk-forward window rows", "in-sample Sharpe", "out-of-sample Sharpe", "positive finite in-sample Sharpe denominator"]
- authority: descriptive_only_not_ranking_not_promotion

## Missing Inputs

- per-bar or per-period return series: absent
- number of observations / effective sample length: absent
- skewness: absent
- kurtosis: absent
- benchmark Sharpe: absent
- annualization convention: absent
- selection rule: absent
- effective number of independent trials: absent

## Anti-Overfit Threshold Definitions

- committed_population_denominator: Definition only: use the committed pre-registered population count recorded in the result population; do not shrink to convenient subsets.
- trial_log_denominator: Definition only: use the full valid trial-log row count available at evaluation time when trial-log DSR posture is inspected.
- effective_independent_trials: Definition only: required for rigorous DSR or multiple-testing correction, but not derivable from current result-population or trial-log fields alone.
- benchmark_sharpe: Definition only: must be explicit before PSR, DSR, or MinTRL numeric computation.
- minimum_track_record_length: Definition only: requires observation count, benchmark Sharpe, target confidence, frequency, and distribution assumptions before computation.

## Non-Authority Declaration

- derived report only
- derived diagnostic only
- not ranking authority
- not readiness authority
- not recommendation authority
- not promotion authority
- not transition authority
- not paper/live/runtime authority
- not gate authority
- not result-population mutation
- RP-0007 is a committed offline result population; this derived diagnostic is descriptive only and does not claim strategy edge.

## Implementation Assumptions

- The input result_population JSON is read-only and is not mutated.
- Existing committed result-population fields are used as descriptive facts only.
- Missing formula-critical inputs require withholding rigorous numeric PSR / DSR / MinTRL values.
- No schema, query-layer, validator, ranking, readiness, recommendation, promotion, transition, paper/live, or runtime authority is created.
