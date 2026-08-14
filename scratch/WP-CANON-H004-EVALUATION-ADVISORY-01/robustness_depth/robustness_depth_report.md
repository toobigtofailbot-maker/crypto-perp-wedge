# WP-LAB-ROBUSTNESS-DEPTH-01 Advisory Robustness Depth Report

## Boundary

- Advisory only; scratch only; non-canonical.
- No screen-gate, promotion, readiness, candidate-evidence, paper/live, or runtime authority is created.
- Missing inputs are reported and not fabricated.

## Inputs

- Source commit: `6994e9000aa6dcf56a7f1a4a08712ba778ea8bbe`
- Seed: `1729`
- Input: `research/result_populations/RP-0007.result_population.json`
- Input checksum: `sha256:ff1104cebcb2775f3f64d2e5bec72b3aaaeeb4187740978e79a26a4819ee2308`

## Stress Dimensions

- Exercised: `cost, funding, slippage`
- Cost stress: `exercised`
- Funding stress: `exercised`
- Slippage stress: `exercised`
- Regime stress: `blocked_input_gap`
- Per-trade resampling: `unavailable_missing_per_trade_rows`

## Missing Inputs

- Missing inputs: `['per_trade_rows', 'variant_result_rows[].regime_label_or_equivalent']`
- Per-trade note: `per-trade resampling not exercised`
- Future per-trade requirement: `provide real per_trade_rows/trade_rows/trades with finite pnl, realized_pnl, net_pnl, or return_pct`
- No fabricated trade rows: `True`

## Conclusion

- Canonical artifact mutated: `False`
- Gate/readiness authority created: `False`
- Output checksum: `sha256:64db0c29a5feca94163ba685dbeb28e2b3ae79f3d691a6f649c66d5cf291a4ea`
