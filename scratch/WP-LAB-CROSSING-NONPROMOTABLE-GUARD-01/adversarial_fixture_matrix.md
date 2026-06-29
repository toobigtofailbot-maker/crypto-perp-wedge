# Adversarial Fixture Matrix

## Covered Rejections

- `construction_payload=true` with excellent metrics: rejected.
- `non_promotable=true` with excellent metrics: rejected.
- `candidate_eligible=false`: rejected.
- `promotion_eligible=false`: rejected.
- `canonical_crossing_allowed=false`: rejected.
- `paper_live_eligible=false`: rejected.
- `edge_claim_allowed=false`: rejected.
- `known_losing_baseline`: rejected.
- `known_neutral_or_no_trade_baseline`: rejected.
- `known_degenerate_or_invalid_baseline`: rejected.
- baseline catalog reference with missing construction provenance: rejected, not passed.

## Negative Assertions

The adversarial tests assert no write to `research/candidate_registry.jsonl`, no canonical Result Population write, no fake registry crossing output on rejected inputs, no readiness/promotion/operator-GO state, no paper/live/runtime path contact, and no `BUILD_FIXTURE_CANONICAL_CROSSING` action requested after provenance rejection.

