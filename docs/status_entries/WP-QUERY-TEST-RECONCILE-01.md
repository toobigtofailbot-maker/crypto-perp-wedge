# WP-QUERY-TEST-RECONCILE-01 - blocked query-test reconciliation

## Trigger

`WP-QUERY-TEST-RECONCILE-01` was opened to reconcile
`tests/test_research_query.py` after `RP-7134` entered the canonical
result-population corpus in PR #470. The package was based on `origin/main`
after PR #472 (`79ca260`), with `RP-7134` and `WP-VERIFY-02` present.

## Diagnosis

Focused reproduction with the repo virtualenv:

```text
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_research_query.py -vv --tb=short --continue-on-collection-errors
```

Result: 8 failed, 55 passed.

Per-test classification:

- `test_strategy_spec_relation_first_instance_repo_state`: stale corpus
  expectation. Current repo truth contains `STRAT-SPEC-0001`,
  `STRAT-SPEC-0002`, and `STRAT-SPEC-0003`.
- `test_variant_sweep_relations_first_instance_repo_state`: stale corpus
  expectation. Current repo truth contains `VM-0001`, `VM-0002`, and `VM-0003`.
- `test_variant_sweep_views_expose_first_instance_repo_state`: stale corpus
  expectation. Current repo truth includes `VM-0003` for
  `STRAT-SPEC-0003` with committed/declared/population counts of 8 and search
  family `SF-PHASEB-ZSCORE-TREND-15M-0001`.
- `test_first_canonical_15m_result_population_views_under_first_parent_instances`:
  stale corpus expectation. Current repo truth contains five result populations:
  `RP-2134`, `RP-4492`, `RP-6688`, `RP-7134`, and `RP-7520`; `RP-7134` maps to
  `STRAT-SPEC-0003` / `VM-0003` / `SWEEP-PLAN-0003` with denominator, result
  row count, and outcome count sum all equal to 8.
- `test_named_views_present`: genuine query-layer conversion defect. Querying
  `v_strategy_spec_condition_groups` against current repo corpus raises
  DuckDB `ConversionException` with malformed JSON input `z_score`.
- `test_strategy_spec_views_expose_first_instance_repo_state`: genuine
  query-layer conversion defect. Querying `v_strategy_spec_condition_groups`
  against current repo corpus raises DuckDB `ConversionException` with malformed
  JSON input `value`.
- `test_querying_strategy_spec_views_does_not_modify_research_files`: genuine
  query-layer conversion defect. The read-only view smoke reaches
  `v_strategy_spec_condition_groups` and raises the same `z_score` conversion
  failure before file-modification checks can complete.
- `test_no_research_files_modified`: genuine query-layer conversion defect. The
  all-view read-only smoke reaches `v_strategy_spec_condition_groups` and raises
  the same `z_score` conversion failure before file-modification checks can
  complete.

`STRAT-SPEC-0003` validates under `tools.registry.validate_strategy_specs`.
The failure is therefore not an invalid Strategy Spec artifact and is not a
hardcoded result-population count issue. It is a query-layer conversion problem
surfaced by the valid post-RP-7134 corpus, specifically composed z-score
operands in `STRAT-SPEC-0003`.

## Changes Made

No test, query-layer, result-population, Strategy Spec, Variant Manifest, Sweep
Plan, schema, validator, compiler, runner, runtime, paper/live, OMS, risk, or
data files were changed.

This status fragment was added to record the blocked diagnosis.

## Why Tests Were Not Reconciled

The stale expectations are safe to reconcile later, but green focused/full
pytest cannot be reached through test reconciliation alone while
`v_strategy_spec_condition_groups` raises during normal current-corpus queries.
Changing `tools/research_query/` is forbidden by this package. Weakening or
skipping the failing view-smoke tests would materially reduce query conversion
coverage and would violate the package instructions.

## Validation

- `python -m pytest tests/test_research_query.py -q`: timed out after the first
  2-minute system-Python attempt.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_research_query.py -q`:
  timed out after 5 minutes with no final result.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_research_query.py -x -vv --tb=short`:
  failed at `test_named_views_present` with DuckDB malformed JSON input
  `z_score`.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_research_query.py -vv --tb=short --continue-on-collection-errors`:
  8 failed, 55 passed.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q --tb=short`:
  timed out after 20 minutes and was not used as merge evidence.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_strategy_specs`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_variant_sweep_artifacts`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_indicator_catalogs`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_result_populations`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/verify.py --help`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/verify.py --integrity-views --integrity-max-workers 4 --timeout-seconds 300 --max-output-chars 6000`:
  pass; 55 integrity views clean.
- `git diff --check`: pass after this status fragment was added.
- `git diff --cached --check`: pass after this status fragment was added.
- `python tools/dev/diff_scope_summary.py --check-forbidden`: pass after this
  status fragment was added; untracked file limited to this status fragment and
  no forbidden-path matches.

## Boundaries

- `tools/research_query/` changed: no.
- Result populations changed: no.
- Strategy Specs changed: no.
- Variant Manifests changed: no.
- Sweep Plans changed: no.
- Compiler/schema/catalog/lib/runner changed: no.
- Runtime, paper/live, OMS/risk/reconciliation, broker/exchange paths changed:
  no.
- Candidate authority, ranking, readiness, promotion, recommendation, policy, or
  runtime authority created: no.

## Standing Rule Handling

No obvious active canonical-write checklist/template path was found that should
be modified from this blocked package without broadening scope. Standing rule
recorded here only: any package adding or changing a canonical result population
must run `tests/test_research_query.py` and full pytest, or explicitly report
why full pytest could not be run.

## Next State

Blocked. Recommended next package: a narrow query-layer defect package
authorized to modify `tools/research_query/` so
`v_strategy_spec_condition_groups` can read valid composed operands from
`STRAT-SPEC-0003` without DuckDB JSON conversion errors. After that lands, rerun
this test-reconciliation package to update stale current-corpus expectations for
`STRAT-SPEC-0003`, `VM-0003`, and `RP-7134`.
