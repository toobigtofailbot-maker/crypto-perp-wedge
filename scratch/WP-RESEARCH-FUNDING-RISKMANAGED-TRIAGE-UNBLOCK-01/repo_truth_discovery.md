# Repo Truth Discovery
## Package: WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-UNBLOCK-01

### Source blocker being addressed

PR #578 recorded that `WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-RUN-01` is blocked with:

**Primary blocker:** The current `tools/research_runner/run_offline_sweep.py` has no
authorized route that compiles the funding-percentile signal with the required 180-day
warmup prefix while restricting reported metrics to `2024-01-01T00:00:00Z` through
`2025-01-01T00:00:00Z`.

**Secondary blockers:**
1. `exit_logic.atr_stop` is a parent Strategy Spec property, so the 108-row denominator
   requires multiple scratch parent specs or a wrapper.
2. The active worktree does not contain the runner-consumable BTCUSDT 15m
   funding-feature CSV needed for `canonical-15m` execution.

---

### Which runner path currently scores the full supplied frame

`tools/research_runner/run_offline_sweep.py` — the `--canonical-15m` path.

When called via `run_offline_sweep(canonical_15m=True, ohlcv_input_path=...)`:
- Loads the full CSV frame via `_canonical_15m_execution_input`.
- Compiles signal on the full frame in `_run_canonical_15m_backtest`.
- Calls `run_backtest` on the full frame.
- Computes metrics from the full `result.equity_curve` in `_metrics_from_backtest`.

Before this package, there were **no** `evaluation_start`/`evaluation_end` parameters
anywhere in the public API or internal call chain.

---

### Whether an evaluation-window mechanism already existed

**None existed before this package.** Inspected:
- `run_offline_sweep` public function signature: no eval window args.
- `_build_result_population`: no eval window.
- `_execute_rows`, `_execute_rows_parallel`, `_execute_variant_worker`: no eval window.
- `_run_canonical_15m_backtest`: no eval window.
- CLI `_build_parser`: no `--evaluation-start`/`--evaluation-end` args.
- Walk-forward path: slices IS/OOS before compiling, which does not satisfy the
  warmup-prefix requirement (signal state is not carried across the slice boundary).

---

### How warmup rows can be used for signal state without becoming scored result rows

**Approach implemented in this package:**

1. The signal compiler (`compile_signal`) is called on the **full frame** (warmup + evaluation).
   Rolling indicators such as `rolling_empirical_percentile_v1` with a 180-day lookback
   build their state from all warmup bars before evaluation_start.

2. After compilation, `_mask_signal_before_window(signal, evaluation_start)` forces all
   signal values before `evaluation_start` to `0.0`. This prevents the backtest from
   opening any position during the warmup prefix.

3. `run_backtest` runs on the full frame with the masked signal. No warmup trades occur.

4. `_metrics_from_backtest_windowed` slices `result.equity_curve` to
   `[evaluation_start, evaluation_end)` and computes metrics from that slice only.

Result: warmup bars establish indicator state; warmup rows contribute zero P&L, zero
drawdown, zero trade count to the reported metrics.

---

### How pre-window positions are prevented

Because `_mask_signal_before_window` zeros all signal values before `evaluation_start`,
the backtester cannot open a position during the warmup prefix. The backtester
(`lib/backtest.py`) opens positions only when signal is nonzero at the next-bar fill
logic. With signal = 0.0 throughout warmup, the equity curve is flat and no trades
appear in `result.trades_df` before `evaluation_start`.

---

### Whether ATR parent-spec scoping requires multiple scratch parent specs or a wrapper

**Multiple scratch parent specs are required** (or a separately authorized wrapper).

The current `validate_strategy_specs.py` and the existing `run_offline_sweep` path bind
`exit_logic.atr_stop` at the parent Strategy Spec level. There is no variant-level
`atr_stop` field in the current grammar.

The route plan (see `atr_parent_spec_route_plan.md`) proposes three separate scratch
parent Strategy Specs (no-ATR, ATR-2.0, ATR-3.0), each producing 36 rows, combined
by the new `tools/research_runner/atr_denominator_bundler.py` into one 108-row table.

A full implementation of the three scratch specs and their denominator assembly is
**not** executed in this package — that is deferred to the next authorized package
(WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-STAGE1-RETRY-01 or similar).

---

### Whether runner-consumable funding-feature data exists locally

**Not found** in the active worktree or the main checkout.

- Main checkout OHLCV: `data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv` — PRESENT in main checkout.
- Raw funding Parquet: `data/raw/binance_um_perp_BTCUSDT_funding_8h_2019-09-10_2026-04-12_2026-04-12T1655Z.parquet` — PRESENT.
- Runner-consumable funding-feature CSV (OHLCV + `funding_rate` column): **MISSING**.

See `funding_feature_data_preflight.json` for the materialization command.

---

### Whether this package can unblock Stage-1 retry without touching protected paths

**Partially.** This package:
- Implements the evaluation-window runner semantics (primary blocker resolved).
- Creates a route plan and bundler for the ATR denominator problem.
- Documents the funding-feature data preflight.

It does **not** execute the Stage-1 run, create the three scratch Strategy Specs/
manifests/sweep plans, or materialize the funding-feature CSV. Those remain for the
next authorized package.

`ready_for_stage1_retry: false` — see `stage1_retry_readiness.json`.
