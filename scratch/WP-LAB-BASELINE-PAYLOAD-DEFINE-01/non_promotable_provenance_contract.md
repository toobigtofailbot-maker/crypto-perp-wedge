# Non-Promotable Provenance Contract

## Permanent Semantics

`construction_payload` and `non_promotable` are permanent provenance semantics. They are not temporary review labels, experiment statuses, or fields that later consumers may remove to rescue a result.

Required hard semantics for every baseline in this package:

- `construction_payload`: true
- `non_promotable`: true
- `candidate_eligible`: false
- `promotion_eligible`: false
- `paper_live_eligible`: false
- `edge_claim_allowed`: false
- `canonical_crossing_allowed`: false

## Later Gate Behavior

Later gates must treat these payloads as hard blocks. A passing metric, favorable robustness artifact, dashboard highlight, agent output, or operator-visible summary must not make the payload eligible for candidate lifecycle, promotion, crossing, paper, shadow, or live use.

## Crossing And Candidate Machinery

Crossing and candidate machinery must reject these payloads by construction. Any attempt to register, promote, cross, paper-trade, live-trade, rank as edge, or claim readiness for these payloads is a lab defect.

## Dashboard And Operator Surfaces

Dashboard, reporting, and operator surfaces must label the payloads as fixtures/test payloads only. They must not appear in real candidate queues, GO-evidence panels, readiness queues, capital/paper/live views, or promotion surfaces.

## Agent Loops

Agent loops must not reinterpret these payloads as candidate opportunities. They may use them only to verify plumbing behavior, denominator handling, invalid/no-trade/loss handling, and rejection guardrails.

## Non-Removal Rule

No downstream package may remove, overwrite, soften, or ignore these flags to rescue a baseline. If a future artifact schema cannot preserve the semantics, the consumer must stop or record a blocker rather than convert the payload into an eligible strategy artifact.
