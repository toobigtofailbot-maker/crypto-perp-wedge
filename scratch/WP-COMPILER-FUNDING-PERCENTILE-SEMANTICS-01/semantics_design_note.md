# Semantics Design Note

`rolling_empirical_percentile_v1` is a closed `composed_operand` variant. It accepts one `data_ref` source and one literal or parameter-bound positive integer lookback.

For bar `t`, the output is:

`count(window_value <= current_value) / window_count`

The window contains the current bar and the preceding `lookback - 1` bars only. This is weak-rank tie handling: all values tied with the current value count in the numerator. `min_periods_policy` is fixed to `full_window`; `tie_policy` is fixed to `weak_rank`; `nan_policy` is fixed to `null_output`. A window with missing observations does not emit a percentile. No expanding, whole-sample, future-row, expression, or fitted behavior exists.

The transform source must be declared in `timeframe_and_data.host_data_refs` and present in the compiler frame. The runner retains only declared columns and continues to reject non-full-history availability at its existing boundary.

`max_holding_period.bars` accepts the existing closed `{ "parameter_ref": "..." }` value-binding shape. The resolved value must be a non-boolean integer in `[1, 100000]`. Literal behavior and the existing compiler-owned holding-state semantics are unchanged.
