# Real-Runner Reconciliation Plan

## Status

This package executes nothing. The plan below applies only if Karl approves a later Stage 1 triage run.

## Authority

Only the repo-owned offline research runner can be trusted for Stage 1 continue/no-go judgment. Vectorbt is optional, non-canonical, and cannot confirm a finalist, satisfy a gate, rank a candidate, or write canonical evidence.

## Route

Stage 1 must use one of these approved execution routes:

1. Manually authored scratch Strategy Spec / Variant Manifest / Sweep Plan inputs that validate under current repo validators and run through `tools.research_runner.run_offline_sweep`.
2. A separately authorized adapter-extension package that teaches the funding bridge to generate the exact same frozen 108-row denominator before any run.

The current funding formalizer bridge is not enough by itself because it generates the old 36-row two-exit funding denominator and does not add the ATR-stop risk layer.

## Required Reconciliation

If vectorbt is used:

- process rows in variant-id order, not metric rank order;
- write only scratch/non-canonical preview output;
- report all 108 planned rows or mark the denominator incomplete;
- compare vectorbt preview rows to real-runner rows by variant id, outcome availability, return direction, drawdown ordering bucket, trade-count order-of-magnitude, and signal checksum where available;
- treat material unexplained divergence as NO-GO or blocked, never as a reason to pick the favorable engine.

If vectorbt is unavailable or its semantics cannot represent the risk layer honestly, Stage 1 must be real-runner-only.

## Real Runner Minimum Evidence

The real-runner output must prove:

- all 108 planned rows are present or explicitly accounted for;
- input warmup begins no later than `2023-07-05T00:00:00Z`;
- evaluation rows are restricted to `2024-01-01T00:00:00Z` through `2025-01-01T00:00:00Z`;
- funding payments/accounting remain off unless a later package explicitly authorizes funding-PnL work;
- dynamic sizing is fixed at `target_leverage=1.0`;
- no canonical Result Population or candidate lifecycle record is written unless a later package explicitly authorizes it.

## Continue Authority

Passing sidecar triage alone cannot send the hypothesis to Stage 2. A continue decision requires real-runner evidence that satisfies the frozen stop/go criteria.
