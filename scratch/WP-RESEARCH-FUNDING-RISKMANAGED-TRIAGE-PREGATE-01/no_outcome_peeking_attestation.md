# No Outcome-Peeking Attestation

No strategy run, backtest, sweep, sidecar triage, or result inspection occurred in this package.

The selected hypothesis was chosen from current repo truth:

- the prior funding-fade family already exists;
- its full denominator was preserved;
- its failure mode was drawdown;
- current merged grammar can express an offline ATR-stop risk layer.

The Stage 1 window was selected from calendar and non-strategy market-regime coverage, not from `H-FUNDING-FADE-RISKMANAGED-01` strategy return, Sharpe, drawdown, variant PnL, or winner cells.

The signal parameters are frozen from the prior concluded family. The only variable risk-control addition is an ATR-stop multiplier set of `2.0` and `3.0`, selected from a-priori volatility-stop rationale and current primitive capability. Dynamic equity target leverage is fixed at `1.0` and is not swept.

The denominator plan preserves all 108 rows, including same-window no-ATR comparison rows. Winner-only reporting is forbidden. A single passing cell is explicitly treated as an overfit signature rather than a continue signal.

Funding-with-risk-management is test traffic for the generic Side 12 lab. It is not a funding-specific lab pivot and does not imply future hypotheses must be funding strategies.
