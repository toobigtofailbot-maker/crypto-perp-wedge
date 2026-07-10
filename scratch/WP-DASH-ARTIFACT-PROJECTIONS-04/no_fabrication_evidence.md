# No-fabrication evidence

For every available projection, `tests/test_operator_dashboard_api.py` loads the source
path returned by the API, recomputes its file SHA-256, and compares the projected payload
to the exact named source field:

- summarized trade diagnostics = `variant_result_rows`;
- WFO folds = `fold_results`;
- Monte Carlo robustness summary = `bootstrap_ci`.

No equity curve or drawdown point series was derived from aggregate PnL, return, or
drawdown. No trade list was inferred from `trade_count`. No per-trade returns were inferred
from per-variant metrics. No raw Monte Carlo distribution was reconstructed from its
checksum or confidence interval. No missing series is represented by an empty data array.

The readers perform file reads and deterministic projection only. They do not invoke a
runner, backtest, bridge, gate, pipeline, scheduler, provider, broker, exchange, paper/live,
runtime, or protected execution path.
