# Blocked Reason

Package `WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-RUN-01` is blocked before strategy execution.

The frozen packet passed the required integrity checks, but the exact Stage-1 run cannot be expressed through the current repo-owned offline runner without code or data-path work that this package forbids.

Primary blocker: the current `tools/research_runner/run_offline_sweep.py` path has no authorized route that compiles the funding-percentile signal with the required warmup prefix while restricting reported metrics to `2024-01-01T00:00:00Z` through `2025-01-01T00:00:00Z`. Running only the 2024 rows would violate the 180-day warmup requirement. Running warmup plus 2024 rows would score warmup rows. The existing walk-forward route slices the execution input before compiling/backtesting, so it does not preserve warmup state for the OOS signal.

Secondary blockers:

- `exit_logic.atr_stop` is a parent Strategy Spec property in the current grammar, so the frozen no-ATR / ATR-2.0 / ATR-3.0 denominator would require multiple scratch parent spec sets or a separately authorized wrapper/adapter to preserve the single 108-row denominator honestly.
- The active worktree did not contain the ignored runner-consumable BTCUSDT 15m funding-feature CSV required for a declared `funding_rate` canonical-15m run. The main checkout had base 15m D4A OHLCV and raw funding Parquets, but this package does not authorize data materialization or writes outside the package scratch root.

No strategy run, sidecar preview, canonical Result Population, candidate lifecycle write, runtime/paper/live path, OMS/risk/reconciliation/order/exchange path, funding accounting change, or code change occurred.
