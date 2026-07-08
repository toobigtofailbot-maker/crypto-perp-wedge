# Lab Data / Simulator Readiness Display

Read-only readiness display only; no data acquisition, runner/compiler behavior change, execution, candidate, crossing, promotion, paper/live/runtime, provider/API, credential, dependency, config, or protected-path authority.

## Taxonomy

- `testable_now_with_current_public_history`: 4
- `testable_now_with_current_caveats`: 1
- `needs_local_full_history_materialization`: 3
- `needs_vendor_or_captured_history`: 4
- `needs_runner_or_compiler_support`: 1
- `needs_simulator_realism_upgrade`: 0
- `go_gated_or_paper_phase_only`: 1
- `protected_or_out_of_scope`: 0
- `unknown_needs_review`: 0

## Items

### OHLCV-only indicators

- `subject_id`: `READINESS-OHLCV-INDICATORS`
- `feature_or_family`: `ohlcv_indicators`
- `status`: `testable_now_with_current_public_history`
- `reason_code`: `OHLCV_INDICATOR_COMPILER_AND_OFFLINE_RUNNER_PRESENT`
- `blocker_detail`: None for closed OHLCV builtin families on the offline research path; still not paper/live or promotion authority.
- `next_prerequisite_category`: `none_for_offline_research_display`
- `non_authority_flags`: `read_only_display_only`, `not_data_acquisition_authority`, `not_vendor_or_api_authority`, `not_runner_or_compiler_change_authority`, `not_simulator_change_authority`, `not_strategy_execution_authority`, `not_candidate_authority`, `not_crossing_or_promotion_authority`, `not_paper_live_runtime_authority`, `not_provider_api_or_credential_authority`, `not_scheduler_or_autonomy_authority`

### Funding-rate feature history

- `subject_id`: `READINESS-FUNDING-RATE-FEATURE-HISTORY`
- `feature_or_family`: `funding_rate_feature`
- `status`: `needs_local_full_history_materialization`
- `reason_code`: `FUNDING_FEATURE_PUBLIC_HISTORY_CONDITIONAL_BUT_RUNNER_CSV_MISSING`
- `blocker_detail`: Funding-rate values are cataloged as conditional public-archive history, but the runner-consumable full-history feature CSV is not created by this display.
- `next_prerequisite_category`: `local_full_history_materialization`
- `non_authority_flags`: `read_only_display_only`, `not_data_acquisition_authority`, `not_vendor_or_api_authority`, `not_runner_or_compiler_change_authority`, `not_simulator_change_authority`, `not_strategy_execution_authority`, `not_candidate_authority`, `not_crossing_or_promotion_authority`, `not_paper_live_runtime_authority`, `not_provider_api_or_credential_authority`, `not_scheduler_or_autonomy_authority`

### Funding PnL / cost realism

- `subject_id`: `READINESS-FUNDING-PNL-COST-REALISM`
- `feature_or_family`: `funding_cost_realism`
- `status`: `needs_runner_or_compiler_support`
- `reason_code`: `FUNDING_CASHFLOW_CORE_OPT_IN_BUT_CANONICAL_RUNNER_PATH_NOT_WIRED`
- `blocker_detail`: Backtest core can model opt-in funding cashflows, but current canonical runner inputs do not supply real funding events for a full funding-carry PnL claim.
- `next_prerequisite_category`: `runner_support_and_local_funding_materialization`
- `non_authority_flags`: `read_only_display_only`, `not_data_acquisition_authority`, `not_vendor_or_api_authority`, `not_runner_or_compiler_change_authority`, `not_simulator_change_authority`, `not_strategy_execution_authority`, `not_candidate_authority`, `not_crossing_or_promotion_authority`, `not_paper_live_runtime_authority`, `not_provider_api_or_credential_authority`, `not_scheduler_or_autonomy_authority`

### Taker-flow archive-derived support

- `subject_id`: `READINESS-TAKER-FLOW-ARCHIVE`
- `feature_or_family`: `taker_flow`
- `status`: `needs_local_full_history_materialization`
- `reason_code`: `TAKER_FLOW_ARCHIVE_DERIVATION_CONDITIONAL_NOT_MATERIALIZED`
- `blocker_detail`: Repo truth permits conditional archive derivation for taker-flow features, but this package does not materialize archive-derived columns or acquire trade archives.
- `next_prerequisite_category`: `local_full_history_materialization`
- `non_authority_flags`: `read_only_display_only`, `not_data_acquisition_authority`, `not_vendor_or_api_authority`, `not_runner_or_compiler_change_authority`, `not_simulator_change_authority`, `not_strategy_execution_authority`, `not_candidate_authority`, `not_crossing_or_promotion_authority`, `not_paper_live_runtime_authority`, `not_provider_api_or_credential_authority`, `not_scheduler_or_autonomy_authority`

### Open interest

- `subject_id`: `READINESS-OPEN-INTEREST`
- `feature_or_family`: `open_interest`
- `status`: `needs_vendor_or_captured_history`
- `reason_code`: `OPEN_INTEREST_NOT_PUBLIC_FULL_HISTORY`
- `blocker_detail`: Current open interest is snapshot/recent-only in repo truth; trades or aggregate trades cannot reconstruct true open interest.
- `next_prerequisite_category`: `vendor_or_captured_history`
- `non_authority_flags`: `read_only_display_only`, `not_data_acquisition_authority`, `not_vendor_or_api_authority`, `not_runner_or_compiler_change_authority`, `not_simulator_change_authority`, `not_strategy_execution_authority`, `not_candidate_authority`, `not_crossing_or_promotion_authority`, `not_paper_live_runtime_authority`, `not_provider_api_or_credential_authority`, `not_scheduler_or_autonomy_authority`

### Long/short ratio

- `subject_id`: `READINESS-LONG-SHORT-RATIO`
- `feature_or_family`: `long_short_ratio`
- `status`: `needs_vendor_or_captured_history`
- `reason_code`: `LONG_SHORT_RATIO_PUBLIC_REST_RECENT_ONLY`
- `blocker_detail`: Public long/short ratio endpoints are recent-only under the committed availability labels and cannot support full-history evidence without an override dataset.
- `next_prerequisite_category`: `vendor_or_captured_history`
- `non_authority_flags`: `read_only_display_only`, `not_data_acquisition_authority`, `not_vendor_or_api_authority`, `not_runner_or_compiler_change_authority`, `not_simulator_change_authority`, `not_strategy_execution_authority`, `not_candidate_authority`, `not_crossing_or_promotion_authority`, `not_paper_live_runtime_authority`, `not_provider_api_or_credential_authority`, `not_scheduler_or_autonomy_authority`

### Liquidation volume/history

- `subject_id`: `READINESS-LIQUIDATION-HISTORY`
- `feature_or_family`: `liquidation_history`
- `status`: `needs_vendor_or_captured_history`
- `reason_code`: `LIQUIDATION_VOLUME_VENDOR_ONLY_AND_NOT_COMPILER_VISIBLE`
- `blocker_detail`: The catalog keeps liquidation_volume vendor-only for history and not compiler-visible; simulator liquidation assumptions are not liquidation-volume data.
- `next_prerequisite_category`: `vendor_or_captured_history_then_runner_or_compiler_support`
- `non_authority_flags`: `read_only_display_only`, `not_data_acquisition_authority`, `not_vendor_or_api_authority`, `not_runner_or_compiler_change_authority`, `not_simulator_change_authority`, `not_strategy_execution_authority`, `not_candidate_authority`, `not_crossing_or_promotion_authority`, `not_paper_live_runtime_authority`, `not_provider_api_or_credential_authority`, `not_scheduler_or_autonomy_authority`

### L2 / order-book features

- `subject_id`: `READINESS-L2-ORDERBOOK`
- `feature_or_family`: `order_book_microstructure`
- `status`: `needs_vendor_or_captured_history`
- `reason_code`: `NO_COMMITTED_L2_HISTORY_OR_COMPILER_BINDING`
- `blocker_detail`: No repo-truth full-history L2 source or Strategy Spec/compiler binding exists for order-book features.
- `next_prerequisite_category`: `vendor_or_captured_history_and_runner_or_compiler_support`
- `non_authority_flags`: `read_only_display_only`, `not_data_acquisition_authority`, `not_vendor_or_api_authority`, `not_runner_or_compiler_change_authority`, `not_simulator_change_authority`, `not_strategy_execution_authority`, `not_candidate_authority`, `not_crossing_or_promotion_authority`, `not_paper_live_runtime_authority`, `not_provider_api_or_credential_authority`, `not_scheduler_or_autonomy_authority`

### Mark / index / premium index fields

- `subject_id`: `READINESS-MARK-INDEX-PREMIUM-FIELDS`
- `feature_or_family`: `mark_index_premium_fields`
- `status`: `needs_local_full_history_materialization`
- `reason_code`: `CONDITIONAL_PUBLIC_ARCHIVE_FIELDS_NEED_ALIGNED_RUNNER_COLUMNS`
- `blocker_detail`: These fields are conditional public-archive data features for signal use when aligned and materialized; the backtester still marks/liquidates on close, not external mark/index data.
- `next_prerequisite_category`: `local_full_history_materialization_for_signal_features_or_simulator_realism_upgrade_for_marking`
- `non_authority_flags`: `read_only_display_only`, `not_data_acquisition_authority`, `not_vendor_or_api_authority`, `not_runner_or_compiler_change_authority`, `not_simulator_change_authority`, `not_strategy_execution_authority`, `not_candidate_authority`, `not_crossing_or_promotion_authority`, `not_paper_live_runtime_authority`, `not_provider_api_or_credential_authority`, `not_scheduler_or_autonomy_authority`

### UTC/session/time-derived fields

- `subject_id`: `READINESS-UTC-TIME-FIELDS`
- `feature_or_family`: `time_session_fields`
- `status`: `testable_now_with_current_public_history`
- `reason_code`: `TIMESTAMP_FIELDS_AND_SESSION_PRIMITIVES_PRESENT`
- `blocker_detail`: No data blocker for UTC-derived fields when source bars exist; complex session behavior remains offline research only.
- `next_prerequisite_category`: `none_for_offline_research_display`
- `non_authority_flags`: `read_only_display_only`, `not_data_acquisition_authority`, `not_vendor_or_api_authority`, `not_runner_or_compiler_change_authority`, `not_simulator_change_authority`, `not_strategy_execution_authority`, `not_candidate_authority`, `not_crossing_or_promotion_authority`, `not_paper_live_runtime_authority`, `not_provider_api_or_credential_authority`, `not_scheduler_or_autonomy_authority`

### Donchian / breakout family

- `subject_id`: `READINESS-DONCHIAN-BREAKOUT`
- `feature_or_family`: `donchian_breakout`
- `status`: `testable_now_with_current_public_history`
- `reason_code`: `DONCHIAN_AND_CROSSOVER_COMPILER_SUPPORT_PRESENT`
- `blocker_detail`: No data blocker for closed Donchian/OHLCV breakout variants on the offline research path; not a candidate or promotion claim.
- `next_prerequisite_category`: `none_for_offline_research_display`
- `non_authority_flags`: `read_only_display_only`, `not_data_acquisition_authority`, `not_vendor_or_api_authority`, `not_runner_or_compiler_change_authority`, `not_simulator_change_authority`, `not_strategy_execution_authority`, `not_candidate_authority`, `not_crossing_or_promotion_authority`, `not_paper_live_runtime_authority`, `not_provider_api_or_credential_authority`, `not_scheduler_or_autonomy_authority`

### SMA / StdDev mean-reversion

- `subject_id`: `READINESS-SMA-STDDEV-MEAN-REVERSION`
- `feature_or_family`: `sma_stddev_mean_reversion`
- `status`: `testable_now_with_current_public_history`
- `reason_code`: `SMA_STDDEV_ZSCORE_COMPILER_SUPPORT_PRESENT`
- `blocker_detail`: No data blocker for closed SMA/StdDev OHLCV variants on the offline research path; trial/candidate authority remains separate.
- `next_prerequisite_category`: `none_for_offline_research_display`
- `non_authority_flags`: `read_only_display_only`, `not_data_acquisition_authority`, `not_vendor_or_api_authority`, `not_runner_or_compiler_change_authority`, `not_simulator_change_authority`, `not_strategy_execution_authority`, `not_candidate_authority`, `not_crossing_or_promotion_authority`, `not_paper_live_runtime_authority`, `not_provider_api_or_credential_authority`, `not_scheduler_or_autonomy_authority`

### EMA / RVOL / rolling VWAP / session families

- `subject_id`: `READINESS-EMA-RVOL-VWAP-SESSION`
- `feature_or_family`: `ema_rvol_vwap_session`
- `status`: `testable_now_with_current_caveats`
- `reason_code`: `SUPPORTED_BUILTINS_WITH_CAVEATED_VWAP_AND_SESSION_SEMANTICS`
- `blocker_detail`: EMA/RVOL/session are closed offline compiler surfaces; rolling VWAP is a candle approximation and must not be represented as true trade-level VWAP.
- `next_prerequisite_category`: `none_for_offline_research_display_or_taker_trade_history_for_true_vwap`
- `non_authority_flags`: `read_only_display_only`, `not_data_acquisition_authority`, `not_vendor_or_api_authority`, `not_runner_or_compiler_change_authority`, `not_simulator_change_authority`, `not_strategy_execution_authority`, `not_candidate_authority`, `not_crossing_or_promotion_authority`, `not_paper_live_runtime_authority`, `not_provider_api_or_credential_authority`, `not_scheduler_or_autonomy_authority`

### Simulator realism / paper-shadow phase boundary

- `subject_id`: `READINESS-SIMULATOR-PAPER-SHADOW-BOUNDARY`
- `feature_or_family`: `simulator_realism_boundary`
- `status`: `go_gated_or_paper_phase_only`
- `reason_code`: `PAPER_LIVE_RUNTIME_REMAINS_PROTECTED_AND_HUMAN_GATED`
- `blocker_detail`: Offline simulator realism disclosures do not authorize paper/shadow/live, runtime, OMS, risk, broker/exchange, or autonomous dispatch.
- `next_prerequisite_category`: `protected_phase_gate`
- `non_authority_flags`: `read_only_display_only`, `not_data_acquisition_authority`, `not_vendor_or_api_authority`, `not_runner_or_compiler_change_authority`, `not_simulator_change_authority`, `not_strategy_execution_authority`, `not_candidate_authority`, `not_crossing_or_promotion_authority`, `not_paper_live_runtime_authority`, `not_provider_api_or_credential_authority`, `not_scheduler_or_autonomy_authority`
