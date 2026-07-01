# Frozen Hypothesis Set Proposal

Package: `WP-LAB-REAL-TRAFFIC-ACCEPTANCE-BATCH-01`

Decision: `blocked_pending_karl_signoff`

This is a review packet only. It is not Karl sign-off, not an executed frozen set, not a Strategy Spec, not a Variant Manifest, not a Sweep Plan, not evidence, not a candidate lifecycle record, and not promotion/crossing/paper-live authority.

## Repo-Truth Basis

- PR #596 is merged in current history through merge commit `257abf5`.
- Current base for this packet is `0fbd7f240694045873e7b879da9c902172c59995`.
- The required signed set files are absent:
  - `scratch/WP-LAB-REAL-TRAFFIC-ACCEPTANCE-BATCH-01/karl_signed_frozen_hypothesis_set.md`
  - `scratch/WP-LAB-REAL-TRAFFIC-ACCEPTANCE-BATCH-01/frozen_hypothesis_set.json`
- Therefore no real research execution was performed.

## Proposed Set

| ID | Name | Supported route | Denominator |
| --- | --- | --- | ---: |
| `LAB-RT-HYP-001` | BTCUSDT 4h no-wick EMA retest continuation | `price_only_ohlcv.no_wick_ema_retest_4h` | 8 |
| `LAB-RT-HYP-002` | BTCUSDT 15m UTC opening-range breakout retest | `price_only_ohlcv.opening_range_breakout_retest_15m` | 8 |
| `LAB-RT-HYP-003` | BTCUSDT 15m SMA crossover trend continuation | `price_only_ohlcv.sma_crossover_trend_continuation_15m` | 4 |
| `LAB-RT-HYP-004` | BTCUSDT 15m volatility-normalized regime-gated mean reversion | `price_only_ohlcv.zscore_regime_gated_mean_reversion_15m` | 4 |

## Sign-Off Requirement

Before any execution package may run real research traffic, Karl/Main must explicitly sign or revise the frozen set and materialize:

- `scratch/WP-LAB-REAL-TRAFFIC-ACCEPTANCE-BATCH-01/karl_signed_frozen_hypothesis_set.md`
- `scratch/WP-LAB-REAL-TRAFFIC-ACCEPTANCE-BATCH-01/frozen_hypothesis_set.json`

Any later signed set should preserve no outcome-peeking, no retuning after results, full denominator retention, and the non-promotion posture.

## Boundary

This packet creates no candidate admission, no canonical crossing, no promotion/readiness, no paper/live/runtime contact, no notification sending, no autonomous scheduler activation, and no dependency or protected-path change.
