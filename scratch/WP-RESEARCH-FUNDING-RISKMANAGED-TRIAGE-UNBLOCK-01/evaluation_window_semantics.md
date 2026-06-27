# Evaluation Window Semantics
## Package: WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-UNBLOCK-01

### Contract

```
evaluation_start (inclusive): 2024-01-01T00:00:00Z
evaluation_end   (exclusive): 2025-01-01T00:00:00Z
warmup_start_no_later_than:   2023-07-05T00:00:00Z  (180-day funding-percentile lookback)
```

The input CSV passed to `--ohlcv-input` must cover from at least `warmup_start_no_later_than`
through the end of the evaluation window (2025-01-01T00:00:00Z).

---

### Implementation (added in this package)

**New public API parameters:**

```python
run_offline_sweep(
    ...
    evaluation_start: pd.Timestamp | None = None,
    evaluation_end:   pd.Timestamp | None = None,
)
```

CLI equivalents:
```
--evaluation-start 2024-01-01T00:00:00Z
--evaluation-end   2025-01-01T00:00:00Z
```

**Call chain:**
```
run_offline_sweep
  → _validate_evaluation_window(evaluation_start, evaluation_end, ohlcv)
  → _build_result_population(..., evaluation_start, evaluation_end)
    → _execute_rows / _execute_rows_parallel (..., evaluation_start, evaluation_end)
      → _execute_variant_worker (..., evaluation_start, evaluation_end)
        → _run_canonical_15m_backtest(..., evaluation_start, evaluation_end)
            compile_signal(full_frame)          # warmup + evaluation rows
            _mask_signal_before_window(signal, evaluation_start)
            run_backtest(masked_signal, full_frame)
        → _metrics_from_backtest_windowed(result, freq, evaluation_start, evaluation_end)
            slice equity_curve to [evaluation_start, evaluation_end)
            compute returns, drawdown, sharpe, pnl from slice
```

---

### Pre-window position guard

**Approach selected: mask entries before evaluation_start.**

Function `_mask_signal_before_window(signal, evaluation_start)`:
- Returns a copy of the signal with all values at index < evaluation_start set to 0.0.
- Does not modify the original signal.
- Applied after `compile_signal` so indicator/feature state is computed on the full frame.

**Why this approach:**
The backtest engine (`lib/backtest.py`) opens positions only when the signal is nonzero.
With signal = 0.0 throughout the warmup prefix, the backtester cannot open a pre-window
position. No `force_flat_at_window_start` or position-carry logic is needed.

**Guarantee:** `result.trades_df` after a windowed run contains only trades whose entry
bar is ≥ evaluation_start. The fees, slippage, and funding in `result.*_paid` therefore
belong entirely to evaluation-window trades.

---

### Metrics restriction

Function `_metrics_from_backtest_windowed(result, freq, evaluation_start, evaluation_end)`:

```python
eval_curve = result.equity_curve.loc[
    (result.equity_curve.index >= evaluation_start)
    & (result.equity_curve.index < evaluation_end)
]
```

- `pnl = eval_curve.iloc[-1] - eval_curve.iloc[0]`
- `return_pct = pnl / eval_curve.iloc[0]`  (baseline = equity at evaluation_start)
- `drawdown` = from `lib.evaluation.max_drawdown(eval_curve)` on the sliced curve
- `sharpe` = from sliced `returns = eval_curve.pct_change().dropna()`
- `trade_count` = `len(result.trades_df)` (all trades are evaluation-window trades)
- `fees`, `funding`, `slippage` = from `result.*_paid` (all evaluation-window costs)

---

### Fail-closed conditions

`_validate_evaluation_window` raises `OfflineSweepError` if:
1. `evaluation_start >= evaluation_end`
2. `evaluation_start < ohlcv.index[0]` (warmup prefix missing from frame)
3. Fewer than 2 OHLCV bars fall within `[evaluation_start, evaluation_end)`

`_metrics_from_backtest_windowed` raises `OfflineSweepError` if:
4. Fewer than 2 equity curve points in the evaluation window

`run_offline_sweep` raises `OfflineSweepError` if:
5. Only one of `evaluation_start`/`evaluation_end` is provided
6. Evaluation window is provided without canonical input data

---

### Boundary semantics

- `evaluation_start`: **inclusive** — the bar at exactly `2024-01-01T00:00:00Z` IS included.
- `evaluation_end`:   **exclusive** — the bar at exactly `2025-01-01T00:00:00Z` is NOT included.
- The last evaluation bar is the last 15m bar with `timestamp < 2025-01-01T00:00:00Z`,
  i.e., `2024-12-31T23:45:00Z`.

---

### Provenance recording

When an evaluation window is active, the following notes are added to
`data_coverage_notes` in the result population payload:

```
evaluation_window_start=2024-01-01T00:00:00Z
evaluation_window_end=2025-01-01T00:00:00Z
evaluation_window_warmup_masked=true
pre_window_entries_blocked_by_signal_mask
```

These are text strings in the existing list field; no schema change is required.

---

### Backward compatibility

When `evaluation_start=None` and `evaluation_end=None` (the default), the runner
behaves identically to the pre-package state:
- `_mask_signal_before_window` is not called.
- `_metrics_from_backtest` (full-frame) is called instead of the windowed variant.
- All existing tests pass without modification.
