# Repo Truth Discovery

Package: `WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01`

Base branch: `origin/main`

Base commit: `71687c1c519700867831d8e964f92f18b12dc2a7`

## Facts

- `origin/main` includes the merged revised signoff/freeze package.
- The signed revised frozen set source exists at `scratch/WP-LAB-REAL-TRAFFIC-REVISED-SIGNOFF-FREEZE-01/revised_frozen_hypothesis_set.json`.
- The Karl signoff record exists at `scratch/WP-LAB-REAL-TRAFFIC-REVISED-SIGNOFF-FREEZE-01/karl_signoff_record.json`.
- The freeze-fidelity audit exists at `scratch/WP-LAB-REAL-TRAFFIC-REVISED-SIGNOFF-FREEZE-01/freeze_fidelity_audit.json` and records `audit_result: pass`.
- The frozen set contains exactly `LAB-RT-HYP-001`, `LAB-RT-HYP-002R`, `LAB-RT-HYP-003R`, and `LAB-RT-HYP-004R`.
- Main authorization is recorded in the frozen-set source as `authorized_as_is`.
- Karl authorization is recorded as `I authorize everything.`
- The frozen-set source preserves the package-level non-promotion posture and stop-and-surface rule for GO-like evidence.
- `LAB-RT-HYP-003R` must carry `pass_with_caution` context and be interpreted against `RP-7134 / STRAT-SPEC-0003`.
- `LAB-RT-HYP-004R` must carry `pass_with_caution` context and be interpreted against `RP-2592 / RP-3731 / RP-6236`.
- `LAB-RT-HYP-004R` requires `session_hours_utc` to remain an explicit denominator axis or equivalent load-bearing gate, `weekend_allowed=false` to remain fixed, and a cosmetic session wrapper is forbidden.
- Current schema/compiler truth includes `atr_normalized_candle_ratio_v1` with `candle_range_atr_ratio` and `candle_body_atr_ratio`.
- A read-only Python probe with the repo virtualenv found:
  - validator composition types: `rolling_empirical_percentile_v1`, `scale_by_one_minus_parameter`, `scale_by_one_plus_parameter`, `z_score`
  - compiler composition types: `atr_normalized_candle_ratio_v1`, `rolling_empirical_percentile_v1`, `scale_by_one_minus_parameter`, `scale_by_one_plus_parameter`, `z_score`
- The offline runner validates parent Strategy Specs with `validate_strategy_specs()` before running.

## Inference

`LAB-RT-HYP-002R` and `LAB-RT-HYP-004R` can now be mapped to a compiler concept, but they cannot pass the current Strategy Spec validator/runner preflight using that exact concept. Executing them would require a validator/schema/runner-surface alignment change, or a weakened substitute for the frozen ATR-normalized axes.

## Decision

Block before execution. Preserve the full four-hypothesis denominator as blocked/unexecuted evidence rather than running a partial or weakened batch.

## Open Question

Whether a later explicitly authorized package should align the Strategy Spec validator with the already-merged ATR-normalized candle schema/compiler surface before retrying this frozen set.
