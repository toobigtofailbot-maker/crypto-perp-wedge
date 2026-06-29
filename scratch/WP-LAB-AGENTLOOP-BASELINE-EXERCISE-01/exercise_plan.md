# Exercise Plan

Package: `WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01`

Selected route: fixture-only baseline loop exercise using existing contracts and the merged crossing guard.

Selected baseline: `known_losing_baseline`.

Steps:

1. Consume PR #583 baseline catalog semantics for `construction_payload=true`, `non_promotable=true`, and all eligibility flags false.
2. Consume PR #584 gate expectations as caveats only: WFO/OOS and robustness/MC are fail, insufficient, or withheld, with no retuning and no numeric override.
3. Create a package-local scratch no-candidate review result that preserves denominator/gate caveats and withholds unavailable metrics.
4. Exercise PR #585 `tools/candidate_lifecycle/canonical_crossing_build.py` in a temporary fixture root, using a baseline candidate-review packet that references the PR #583 baseline.
5. Record the observed `reject_by_construction` crossing rejection without writing canonical candidate lifecycle artifacts.

No schema, runner, compiler, result-population, candidate-registry, data, runtime, paper/live, OMS, risk, reconciliation, broker, exchange, order, or protected path changes are part of this plan.
