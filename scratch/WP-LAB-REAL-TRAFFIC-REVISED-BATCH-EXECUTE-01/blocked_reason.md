# Blocked Reason

Decision: `blocked`

The package blocked before real research execution.

## Fact

The signed revised frozen set exists on `origin/main` at `scratch/WP-LAB-REAL-TRAFFIC-REVISED-SIGNOFF-FREEZE-01/revised_frozen_hypothesis_set.json`. It contains exactly `LAB-RT-HYP-001`, `LAB-RT-HYP-002R`, `LAB-RT-HYP-003R`, and `LAB-RT-HYP-004R`.

Main verification and Karl signoff are present. The freeze-fidelity audit records pass.

## Blocking Fact

The current closed compiler/runner surfaces cannot express every frozen mechanic exactly:

- `LAB-RT-HYP-002R` requires `range_atr_min`: candle high-low range normalized by ATR as a denominator axis.
- `LAB-RT-HYP-004R` requires `body_atr_min`: candle body normalized by ATR as a denominator axis, while preserving load-bearing `session_hours_utc`.

The repo supports EMA, ATR, RSI, RVOL, rolling VWAP, timestamp-derived fields, session refs, candle-shape body/wick ratios, and ATR stops. It does not expose a closed high-low-range / ATR or candle-body / ATR operand or primitive. Using body/range candle-shape predicates instead would change the frozen mechanics.

## Decision

The batch is blocked before execution. No partial run was performed.

## Boundary

No schema, compiler, runner, result-population, candidate lifecycle, crossing, paper/live/runtime, OMS, risk, reconciliation, broker, exchange, dependency, or data path was changed.

## Future Option

A later explicitly authorized package could add a closed ATR-normalized candle range/body primitive or equivalent closed composition route, then retry the frozen batch without retuning.
