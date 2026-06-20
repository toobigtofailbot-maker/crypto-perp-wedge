# WP-PILOT-PURGEDCV-01 Fold Comparison Report

Recommendation: `borrow`
Dependency available: `False`
Material fold difference observed: `True`

## Conclusion

- Can this improve fold rigor? `True`.
- Borrow repo-native? `True`.
- Keep purgedcv as dependency/sidecar? `False`.
- Future WP: `WP-WALKFORWARD-PURGE-EMBARGO-HELPER-01: implement a repo-native helper and focused validator strengthening without changing runner/backtester semantics`.
- Smallest surface: a pure fold-boundary helper that emits explicit purge/embargo fields for walkforward_fold_manifest instances, plus validator checks that evaluation starts after selection end plus required purge.

## Boundary Difference

| fold | naive selection | purged/embargoed selection | eval start | bars removed |
|---|---|---|---|---:|
| FOLD-001 | 2026-01-01T00:00:00Z to 2026-01-05T00:00:00Z | 2026-01-01T00:00:00Z to 2026-01-04T21:00:00Z | 2026-01-05T00:00:00Z | 12 |
| FOLD-002 | 2026-01-06T00:00:00Z to 2026-01-10T00:00:00Z | 2026-01-06T02:00:00Z to 2026-01-09T21:00:00Z | 2026-01-10T00:00:00Z | 20 |
| FOLD-003 | 2026-01-11T00:00:00Z to 2026-01-15T00:00:00Z | 2026-01-11T02:00:00Z to 2026-01-14T21:00:00Z | 2026-01-15T00:00:00Z | 20 |
| FOLD-004 | 2026-01-16T00:00:00Z to 2026-01-20T00:00:00Z | 2026-01-16T02:00:00Z to 2026-01-19T21:00:00Z | 2026-01-20T00:00:00Z | 20 |

## Leakage Risks Addressed

- adjacent training labels with horizons that overlap the first evaluation bars
- feature warmup or rolling-stat lookback contamination at the IS/OOS boundary
- post-test bleed where rows immediately after an evaluation window enter the next selection window
- implicit zero-gap assumptions that are hard to audit once fold boundaries are materialized

## Unknowns

- whether purgedcv's exact API and maintenance posture match the repo's explicit manifest grammar
- the correct purge horizon for each future label/feature family
- whether multi-timeframe or overlapping-label candidates require fold-level or sample-level purging
- how validator checks should encode purge/embargo without changing existing zero-instance compatibility
- whether any future canonical runner path should consume manifest purge/embargo fields directly

## Non-Authority

- scratch_only
- non_canonical
- not_walkforward_contract
- not_canonical_evidence
- not_runner_change
- not_promotion
- not_readiness
- not_paper_live
