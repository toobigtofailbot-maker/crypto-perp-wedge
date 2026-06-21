# WP-LAB-ROBUSTNESS-DEPTH-01 Advisory Robustness Depth Report

## Boundary

- Advisory only; scratch only; non-canonical.
- No screen-gate, promotion, readiness, candidate-evidence, paper/live, or runtime authority is created.
- Missing inputs are reported and not fabricated.

## Inputs

- Source commit: `4da388a289fb0df4547d204e17b05b151f1cb595`
- Seed: `1729`
- Input: `research/result_populations/RP-2592.result_population.json`
- Input checksum: `sha256:d548bfe884b8ad3ec749627da60f54fff9d54d58032eb779342fa56111c713b8`

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
- Output checksum: `sha256:2a062e32df42e9566a187ee7415b66b52c6ca31d75b0b5f1ff775daaf4857d16`
