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

### Implementation (patched in follow-up to PR #579 review)

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

**Corrected call chain:**
```
run_offline_sweep
  → _validate_evaluation_window(evaluation_start, evaluation_end, ohlcv)
        [fails closed if evaluation_end extends beyond last_bar + one_period]
  → _build_result_population(..., evaluation_start, evaluation_end)
    → _execute_rows / _execute_rows_parallel (..., evaluation_start, evaluation_end)
      → _execute_variant_worker (..., evaluation_start, evaluation_end)
        → _run_canonical_15m_backtest(..., evaluation_start, evaluation_end)
            _slice_execution_input_for_evaluation_end(execution_input, evaluation_end)
                # OHLCV truncated to rows strictly < evaluation_end
                # funding truncated consistently
            compile_signal(truncated_frame)     # warmup + evaluation only, no post-window
            _mask_signal_before_window(signal, evaluation_start)
            run_backtest(masked_signal, truncated_frame)
        → _metrics_from_backtest_windowed(result, freq, evaluation_start, evaluation_end)
            # result contains only warmup+evaluation trades; no post-window contamination
            slice equity_curve to [evaluation_start, evaluation_end)
            compute returns, drawdown, sharpe, pnl from slice
```

---

### Pre-window position guard

**Approach: truncate frame + mask signal before evaluation_start.**

`_slice_execution_input_for_evaluation_end(execution_input, evaluation_end)`:
- Returns a new `_ExecutionInput` with OHLCV rows truncated to `index < evaluation_end`.
- Funding frame sliced consistently: `[first_bar, evaluation_end)`.
- Preserves the full warmup prefix so rolling indicator state is correctly established.
- Applied before `compile_signal` so the signal compiler never sees post-window bars.

`_mask_signal_before_window(signal, evaluation_start)`:
- Returns a copy of the signal with all values at `index < evaluation_start` set to 0.0.
- Does not modify the original signal.
- Applied after `compile_signal` on the truncated frame.

**Combined guarantee:**
- Pre-window bars (warmup): signal = 0.0 → no position can open.
- Post-window bars: not present in truncated frame → no position can open, no costs accumulate.
- `result.trades_df`, `result.fees_paid`, `result.funding_paid`, `result.slippage_paid`
  after a windowed run reflect only evaluation-window activity `[evaluation_start, evaluation_end)`.

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
- `trade_count` = `len(result.trades_df)` — window-scoped because backtest was truncated
- `fees`, `funding`, `slippage` = from `result.*_paid` — window-scoped because backtest was truncated
- `win_rate`, `exposure` — window-scoped for the same reason

No post-window trades or costs can appear in any reported metric field.

---

### Fail-closed conditions

`_validate_evaluation_window` raises `OfflineSweepError` if:
1. `evaluation_start >= evaluation_end`
2. `evaluation_start < ohlcv.index[0]` (warmup prefix missing from frame)
3. `evaluation_end > ohlcv.index[-1] + inferred_period` (frame ends before evaluation_end — partial window)
4. Fewer than 2 OHLCV bars fall within `[evaluation_start, evaluation_end)`

`_slice_execution_input_for_evaluation_end` raises `OfflineSweepError` if:
5. Fewer than 2 OHLCV rows remain after truncation

`_metrics_from_backtest_windowed` raises `OfflineSweepError` if:
6. Fewer than 2 equity curve points in the evaluation window

`run_offline_sweep` raises `OfflineSweepError` if:
7. Only one of `evaluation_start`/`evaluation_end` is provided
8. Evaluation window is provided without canonical input data

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
