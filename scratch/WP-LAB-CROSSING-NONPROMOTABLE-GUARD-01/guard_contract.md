# Non-Promotable Crossing Guard Contract

## Decision

`tools/candidate_lifecycle/canonical_crossing_build.py` now rejects construction and non-promotable payloads before authorizing fixture crossing.

## Rejection Conditions

The guard rejects with `reason_code=reject_by_construction` when any of these are present:

- `construction_payload=true`
- `non_promotable=true`
- `candidate_eligible=false`
- `promotion_eligible=false`
- `paper_live_eligible=false`
- `canonical_crossing_allowed=false`
- `edge_claim_allowed=false`
- a PR #583 baseline ID
- a PR #583 baseline catalog ID reference that does not preserve the required non-promotable semantics

## Rejection Output

Rejected outputs record:

- `status=rejected`
- `reason_code=reject_by_construction`
- `candidate_lifecycle_written=false`
- `canonical_crossing_written=false`
- `promotion_or_readiness_created=false`
- `paper_live_eligible=false`
- `operator_gate_pending=false`
- `edge_claim_allowed=false`

## Boundary

This guard hardens the existing fixture crossing surface only. It does not create a real candidate, register a candidate, execute real crossing, write a canonical Result Population, run a strategy, or touch paper/live/runtime, OMS, risk, reconciliation, order, broker, exchange, credential, provider/API, or data paths.

