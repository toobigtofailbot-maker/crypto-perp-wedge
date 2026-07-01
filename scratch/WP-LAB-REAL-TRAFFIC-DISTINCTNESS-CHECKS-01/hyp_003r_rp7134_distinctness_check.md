# LAB-RT-HYP-003R RP-7134 Distinctness Check

## Result

`pass_with_caution`, pending Main verification.

## Repo-Truth Basis

Inspected the revised proposal, freshness matrix, concluded-family inventory, `RP-7134`, `STRAT-SPEC-0003`, `VM-0003`, `SWEEP-PLAN-0003`, `WP-RESEARCH-EDGE-SMA-FAMILY-01`, its repo-truth discovery artifact, the indicator catalog, and compiler references.

## Mechanical Check

RP-7134 / STRAT-SPEC-0003 is a 15m both-direction z-score mean-reversion family. Its entry signal is close versus SMA centerline scaled by STDDEV, with fixed +/-1.5 z-score thresholds, a shared SMA trend gate, and SMA-centerline exits.

HYP-003R proposes rolling candle-VWAP distance reversion. Its declared anchor is rolling VWAP from OHLCV high/low/close/volume, its normalization is ATR distance, its trigger confirmation is RSI exhaustion, and its exit is return to VWAP or RSI neutral.

## Overlap

The overlap is real: both are 15m normalized-distance mean-reversion ideas. This is why the result is cautionary rather than a clean low-risk pass.

## Decision

As written, HYP-003R is mechanically distinct from RP-7134 because anchor, normalization, gate, trigger, exit, and denominator axes differ. If a future formalized path cannot preserve rolling VWAP, ATR distance, RSI confirmation, and VWAP/RSI exits, and instead maps to SMA/stddev z-score with SMA-centerline exits, it should be treated as duplicate and dropped.
