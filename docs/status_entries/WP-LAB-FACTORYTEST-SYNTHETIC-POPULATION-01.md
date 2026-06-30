# WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01

## Branch State

`WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01` adds a fixture-only synthetic
factory test for lab scale-correctness. It uses exactly one PR #583 construction
payload lineage, `known_losing_baseline`, and materializes 600 deterministic
scratch-only rows under
`scratch/WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01/`.

The population preserves the full denominator and status mix:

- completed: 300
- failed: 100
- invalid: 50
- blocked: 50
- insufficient: 50
- withheld: 50

Thirty-six rows are numerically favorable by synthetic fixture metrics, but
every row remains `construction_payload=true`, `non_promotable=true`,
`candidate_eligible=false`, `promotion_eligible=false`,
`paper_live_eligible=false`, `canonical_crossing_allowed=false`, and
`edge_claim_allowed=false`. All rows retain `candidate_review_expected=no_candidate`
and `crossing_expected=reject_by_construction`.

## Implementation Route

The package adds a narrow helper under `tools/lab_factorytest/**` and focused
tests under `tests/test_lab_factorytest_synthetic_population.py`. The helper
reads only prerequisite fixture contracts and writes only the package scratch
directory. It does not import or call the research runner, backtester, candidate
lifecycle writer, crossing builder, runtime, paper/live, OMS, risk,
reconciliation, broker, exchange, order, provider/API, or data-acquisition
surfaces.

## Evidence Artifacts

- `scratch/WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01/repo_truth_discovery.md`
- `scratch/WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01/synthetic_population_manifest.json`
- `scratch/WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01/synthetic_population_manifest.md`
- `scratch/WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01/denominator_accounting.json`
- `scratch/WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01/gate_outcome_summary.json`
- `scratch/WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01/non_promotable_assertions.json`
- `scratch/WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01/factorytest_result.json`
- `scratch/WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01/external_runway_usage.md`
- `scratch/WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01/validation_summary.txt`

## Boundary

This package creates no Strategy Spec, Variant Manifest, Sweep Plan, canonical
Result Population, candidate registry entry, candidate lifecycle record,
promotion/readiness record, crossing output, trading recommendation, data
artifact, dependency change, schema change, runner/compiler change, real
backtest, real sweep, real walk-forward/OOS run, real robustness/MC run, or
edge-search output.

The external adoption runway is recorded but not used: workflow-gen, vectorbt,
robustness MC, analytics metrics, CCXT, and Nautilus were not imported or run.

