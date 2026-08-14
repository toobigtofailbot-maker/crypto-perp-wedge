# WP-CANON-H004-EVALUATION-ADVISORY-01 evidence index

This directory contains read-only, advisory evaluation evidence over canonical
`RP-0007`. The source Result Population remains unchanged at 81 / 81 rows.
Nothing here admits a candidate, recommends a winner, changes a gate, or creates
promotion, paper/live, runtime, OMS, risk, reconciliation, order, exchange, or
capital authority.

## Evidence map

- `evaluation_plan.json`: predeclared inputs, WFO protocol, seeds, and
  non-authority constraints.
- `wfo_oos_advisory.json`: dry-run, two-window IS/OOS replay carrying all 81
  variants into every window. The ephemeral replay Result Population was not
  persisted and is not canonical evidence.
- `item6/`: existing anti-overfit report output. PSR, DSR, and MinTRL remain
  withheld because their required inputs are absent.
- `robustness_mc/`: seeded bootstrap over the 81 aggregate variant rows plus
  parameter sensitivity. This is not per-trade or chronological-path Monte
  Carlo; per-trade resampling is explicitly queued rather than fabricated.
- `robustness_depth/`: aggregate cost, funding, and slippage stress outputs.
  Regime and per-trade dimensions are explicitly unavailable.

The milestone interpretation is recorded in
`docs/research_pipeline/2026-08-h004_rp0007_m1_evaluation_advisory.md`.
