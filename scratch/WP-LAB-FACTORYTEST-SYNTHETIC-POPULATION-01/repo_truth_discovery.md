# WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01 Repo Truth Discovery

## Base

- base commit: `cbbca34fa62dabcb17c81bbf25c264f0dcb64b56`
- pre-existing untracked worktree noise observed before package work: `build/`

## Prerequisite Artifacts

- PR #583 artifacts: True
- PR #584 artifacts: True
- PR #585 artifacts: True
- PR #586 artifacts: True
- PR #587 artifacts: True

## Existing Helper Surfaces

- `tools/lab_state/**`: read-only coordinator state model and resolver.
- `tools/lab_dashboard/**`: read-only dashboard projection.
- `tools/lab_reporting/**`: read-only operator report shaping.
- `tools/candidate_lifecycle/canonical_crossing_build.py`: existing crossing
  guard surface, inspected but not called by this package.
- `tools/registry/**`: existing validators, used only through validation
  commands.
- `tools/dev/diff_scope_summary.py`: diff-scope validation utility.

## External Adoption Runway

- workflow-gen: repo has `tools/external_pilots/workflow_hyperopt_pilot.py` and
  historical scratch outputs; not used here.
- vectorbt: repo has non-canonical sidecar surfaces; not used here.
- robustness MC: repo has advisory robustness helpers, but this package runs no
  MC and uses synthetic status fixtures only.
- analytics metrics: repo has advisory analytics helpers; not used here.
- CCXT: repo has public-data adapter surfaces; not used here.
- Nautilus: repo has a mapping spike surface; not used here.

## Selected Route

Decision: create a package-local fixture generator under
`tools/lab_factorytest/**` plus focused tests, then materialize 600
scratch-only rows under `scratch/WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01/`.

The selected baseline is `known_losing_baseline`, from the PR #583 payload catalog.
This package uses exactly one non-promotable baseline family and performs no
edge-search.

## Files Intentionally Left Unchanged

- `research/candidate_registry.jsonl`
- `research/result_populations/**`
- `tools/research_runner/**`
- `lib/**`
- `configs/**`
- `data/**`
- paper/live/runtime, OMS, risk, reconciliation, broker, exchange, and order
  paths
