# WP-REPO-BASELINE-STALE-TEST-RECONCILE-01

## Status

READY FOR PR REVIEW. Six post-STRAT-SPEC-0007 baseline nodes are reconciled with test-only changes: five stale current-state expectations now match merged repo truth, and the one gitignored-local D4A dependency skips only after committed RP/catalog lineage is validated.

## Scope

Changed test surfaces are limited to `tests/test_external_simulator_pilot.py`, `tests/test_lab_operator_surface.py`, and `tests/test_research_query.py`. Compact package evidence is under `scratch/WP-REPO-BASELINE-STALE-TEST-RECONCILE-01/`.

## Validation

- Focused: external simulator `6 passed, 1 skipped`; operator surface `12 passed`; research query `65 passed`.
- Adjacent: `520 passed` across 28 explicit files.
- Deterministic full suite: two identical collections, 2,849 nodes across 157 files; eight sequential LPT file shards; 2,842 passed, 7 skipped, 0 failed, 0 errors. The skip set is the refreshed-base six-node environment set plus only the authorized external-simulator node.

## Boundary

No production, query-layer, simulator, operator/dashboard, canonical, authority, queue, execution, result, candidate, runtime, paper/live, OMS, risk, reconciliation, configuration, dependency, or deployment behavior changed. STRAT-SPEC-0007 remains `review_requested`, non-authoritative, and visibly `not_computed` in the exact hash-readiness integrity row.
