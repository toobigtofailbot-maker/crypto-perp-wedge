# WP-COMPILER-FEATURES-DATA-DERIVED-01 Branch State

## Authorization

- Main-authorized under the lab-capability completion path.
- This is not Karl authorization for funding, cost, or backtest semantics.

## Scope Summary

- Adds a closed build-test compiler allowlist for these aligned input-frame fields: `funding_rate`, `funding_mark_price`, `mark_price`, `index_price`, `premium_index`, `open_interest`, `open_interest_value`, `top_trader_position_long_short_ratio`, `top_trader_account_long_short_ratio`, `global_long_short_account_ratio`, `taker_buy_sell_ratio`, `taker_buy_volume`, and `taker_sell_volume`.
- Preserves the existing `data_ref` grammar and the required OHLCV input columns.
- The Strategy Spec schema is unchanged because `data_ref.field` is already a non-empty string and the compiler owns the closed field allowlist.

## Dependency Summary

- Depends on merged PR #535 / `WP-LAB-DATA-EXPANSION-01` for public perp-native source coverage and normalized sample evidence.
- Depends on merged PR #537 / `WP-COMPILER-INDICATORS-VOLUME-01` and preserves `rvol_v1` and candle-based `rolling_vwap_v1` behavior.

## Feature Availability Summary

| Compiler field | Availability | Source limitation |
|---|---|---|
| `funding_rate` | `backfillable` | Preserved public funding history. |
| `funding_mark_price` | `backfillable` | Funding-history `markPrice`; compiler-facing name distinguishes it from aligned mark-price kline values. |
| `mark_price` | `backfillable` | Preserved mark-price kline history. |
| `index_price` | `backfillable` | Preserved index-price kline history. |
| `premium_index` | `backfillable` | Preserved premium-index kline history. |
| `open_interest` | `recent_only` | Current open interest or coverage-limited public history. |
| `open_interest_value` | `recent_only` | Coverage-limited public open-interest statistics. |
| `top_trader_position_long_short_ratio` | `recent_only` | Public endpoint history is limited to the latest 30 days. |
| `top_trader_account_long_short_ratio` | `recent_only` | Public endpoint history is limited to the latest 30 days. |
| `global_long_short_account_ratio` | `recent_only` | Public endpoint history is limited to the latest 30 days. |
| `taker_buy_sell_ratio` | `recent_only` | Public endpoint history is limited to the latest 30 days. |
| `taker_buy_volume` | `recent_only` | Public endpoint history is limited to the latest 30 days. |
| `taker_sell_volume` | `recent_only` | Public endpoint history is limited to the latest 30 days. |

Recent-only fields are usable only for windows containing valid, timestamp-aligned source columns. Compiler visibility does not imply full-history Strategy Spec testability, canonical readiness, or vendor-data approval.

## Semantic Summary

- Data-derived refs are direct input values only. The compiler assumes that upstream work has already aligned each supplied column to the OHLCV index.
- `funding_rate` is a feature only; it does not change funding cost, PnL, fills, accounting, or candidate readiness.
- Mark, index, premium, open-interest, long/short, and taker fields are feature values only.
- The compiler performs no fetch, timestamp alignment, forward-fill, backfill, or interpolation. A referenced allowed field that is absent from the input frame fails closed.
- True trade-level VWAP, liquidation data, and L2/order-book fields remain unimplemented. Existing `rolling_vwap_v1` remains a candle-based approximation.

## Boundary Summary

- No dependency or data-ingestion changes.
- No canonical Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, trial logs, or lifecycle artifacts.
- No runner/backtester, funding-cost, PnL, fee, slippage, or accounting changes.
- No runtime, paper, live, shadow, OMS, risk, reconciliation, safe-mode, broker, exchange, config, or credential changes.
- No private endpoints or credentials.
- No promotion or readiness authority.

## Validation Status

- Focused pytest (`test_validate_strategy_specs.py`, `test_validate_indicator_catalogs.py`, and `test_spec_signal_compiler.py`): PASS, 353 passed.
- Strategy Spec validator: PASS.
- Indicator Catalog validator: PASS.
- Result Population validator: PASS.
- Query view discovery: PASS.
- Diff scope summary: PASS; the three expected package files only and no forbidden-path matches.
- `git diff --check`: PASS.
- Full pytest: environment caveat, 1 unrelated failure; 1,858 passed, 1 skipped, 6 warnings. `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage` expected the gitignored local D4A normalized-data file in this isolated worktree. This known worktree-local fixture limitation is documented in prior merged status entries and does not involve package-changed files.
