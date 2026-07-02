# Repo Truth Discovery

Package: `WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01`

Base branch: `origin/main`

Base commit: `2cea22d66ab4dffcb1ee43fcdb72ac3ae5341b6e`

## Facts

- `origin/main` includes merge commit `2cea22d66ab4dffcb1ee43fcdb72ac3ae5341b6e`, titled as the merge of `lab/real-traffic-revised-signoff-freeze-01`.
- The signed revised frozen set source exists at `scratch/WP-LAB-REAL-TRAFFIC-REVISED-SIGNOFF-FREEZE-01/revised_frozen_hypothesis_set.json`.
- The Karl signoff record exists at `scratch/WP-LAB-REAL-TRAFFIC-REVISED-SIGNOFF-FREEZE-01/karl_signoff_record.json`.
- The freeze-fidelity audit exists at `scratch/WP-LAB-REAL-TRAFFIC-REVISED-SIGNOFF-FREEZE-01/freeze_fidelity_audit.json` and records `audit_result: pass`.
- The frozen set contains exactly:
  - `LAB-RT-HYP-001`
  - `LAB-RT-HYP-002R`
  - `LAB-RT-HYP-003R`
  - `LAB-RT-HYP-004R`
- Main authorization is recorded in the frozen-set source as `authorized_as_is`.
- Karl authorization is recorded as `I authorize everything.`
- The frozen-set source preserves the package-level non-promotion posture and stop-and-surface rule for GO-like evidence.
- The required caution contexts are present:
  - `LAB-RT-HYP-003R` must carry `pass_with_caution` context and be interpreted against `RP-7134 / STRAT-SPEC-0003`.
  - `LAB-RT-HYP-004R` must carry `pass_with_caution` context and be interpreted against `RP-2592 / RP-3731 / RP-6236`.
- The required `LAB-RT-HYP-004R` load-bearing condition is present: `session_hours_utc` must remain an explicit denominator axis or equivalent load-bearing gate, `weekend_allowed=false` must remain fixed, and a cosmetic session wrapper is forbidden.
- The current compiler surface includes closed support for EMA, ATR, RSI, RVOL, rolling VWAP, Donchian, candle-shape primitives, UTC timestamp-derived data refs, session-window primitive refs, ATR stops, and `min_bars_between_entries`.
- The current compiler surface does not expose a closed arithmetic/composition route for the exact frozen `range_atr_min` or `body_atr_min` mechanics. The available composed operands are limited to parameter scaling, z-score, and rolling empirical percentile forms, and candle-shape primitives express body/wick ratios against candle range, not candle range or body normalized by ATR.
- Exact execution of `LAB-RT-HYP-002R` requires the frozen `range_atr_min` denominator axis.
- Exact execution of `LAB-RT-HYP-004R` requires the frozen `body_atr_min` denominator axis and load-bearing session filter.

## Inference

The batch cannot execute the signed frozen four-hypothesis set through existing supported repo surfaces without either:

- changing schema/compiler/runner behavior to add the missing closed ATR-normalized range/body primitive or arithmetic composition, which is forbidden by this package; or
- weakening/retuning the frozen mechanics by substituting another available predicate, which would violate freeze fidelity.

## Decision

Block before execution. Preserve the full four-hypothesis denominator as blocked/unexecuted evidence rather than running a partial or weakened batch.

## Open Question

Whether a later explicitly authorized package should add a closed ATR-normalized candle range/body primitive or composition route before retrying this frozen set.
