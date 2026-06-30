# WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01 Synthetic Population Manifest

This is a fixture-only lab factory test. It is not market evidence, not a
backtest, not a sweep, not edge-search, not a candidate, and not a trading
recommendation.

## Population

- baseline_id: `known_losing_baseline`
- strategy_family_count: 1
- row_count_planned: 600
- row_count_materialized: 600
- favorable_numeric_rows: 36

## Status Buckets

| Status | Rows |
| --- | ---: |
| blocked | 50 |
| completed | 300 |
| failed | 100 |
| insufficient | 50 |
| invalid | 50 |
| withheld | 50 |

## Boundary

Every row has `construction_payload=true`, `non_promotable=true`,
`candidate_eligible=false`, `promotion_eligible=false`,
`paper_live_eligible=false`, `canonical_crossing_allowed=false`,
`edge_claim_allowed=false`, and `crossing_expected=reject_by_construction`.
Numerically favorable synthetic rows remain candidate-ineligible by
construction.
