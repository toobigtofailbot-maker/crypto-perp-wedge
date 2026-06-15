# WP-VERIFY-02 - Authorized canonical-write advisory handling and integrity-wrapper throughput

## Branch / PR

- Branch: `tools/verify-02-authorized-canonical-integrity`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/472

## Package Class

- T3 tooling / tests.

## Scope Summary

- Adds an explicit diff-scope allowance for named new canonical result-population
  writes only when the caller passes
  `--authorized-canonical-result-population-write <path>`.
- The allowance is path-exact and pattern-bound to
  `research/result_populations/RP-<digits>.result_population.json`.
- Existing result-population mutations remain forbidden because paths already
  present in `HEAD` are rejected.
- Other protected paths, including `lib/`, `src/`, runner, script, config, data,
  and broad `research/` paths, remain forbidden by default.
- `tools/dev/verify.py` passes the explicit canonical-write allowance through to
  `tools/dev/diff_scope_summary.py`.
- `tools/dev/verify.py --integrity-views` now executes discovered
  `v_integrity_*` views with bounded parallel subprocess workers, records per-view
  name, status, row count, elapsed seconds, and error text, and reports final
  output in deterministic sorted view order.

## Changed Files

- `tools/dev/diff_scope_summary.py`
- `tools/dev/verify.py`
- `tests/test_diff_scope_summary.py`
- `tests/test_verify.py`
- `docs/status_entries/WP-VERIFY-02.md`

## Validation Summary

- `git diff --check`: pass.
- `git diff --cached --check`: pass with no staged files at time of run.
- `python tools/dev/diff_scope_summary.py --check-forbidden`: pass; no
  forbidden-path matches for the working diff.
- `python tools/dev/verify.py --help`: pass.
- `python tools/dev/verify.py --timeout-seconds 300 --max-output-chars 6000`:
  pass.
- `python -m tools.registry.validate_strategy_specs`: pass.
- `python -m tools.registry.validate_variant_sweep_artifacts`: pass.
- `python -m tools.registry.validate_indicator_catalogs`: pass.
- `python -m tools.registry.validate_result_populations`: pass.
- `python -m tools.research_query.run --list-views`: pass.
- `python -m tools.research_query.run --list-views | Select-String
  '^v_integrity_' | Measure-Object`: pass; 55 integrity views discovered.
- `python -m pytest tests/test_diff_scope_summary.py -q`: pass, 15 passed.
- `python -m pytest tests/test_verify.py -q`: pass, 11 passed.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest
  tests/test_diff_scope_summary.py tests/test_verify.py -q`: pass, 26 passed.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/verify.py
  --integrity-views --timeout-seconds 300 --max-output-chars 6000 --json`:
  pass; 55 discovered integrity views returned zero rows.

## Non-Evidence Runs

- `python -m pytest -q` with system Python: failed during collection because
  system Python lacks repo dependencies including `binance`, `numpy`, and
  `pandas`; not used as merge evidence.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`: ran
  full suite and failed with 8 failures in `tests/test_research_query.py`
  against current `origin/main` corpus/query expectations after PR #470
  introduced `STRAT-SPEC-0003`, `VM-0003`, and `RP-7134`, plus existing
  `v_strategy_spec_condition_groups` JSON conversion errors. These files and
  query-layer semantics are outside WP-VERIFY-02 scope and were not changed.

## Boundary Summary

- Canonical artifacts changed: no.
- Result populations changed: no.
- Strategy Specs, Variant Manifests, and Sweep Plans changed: no.
- Compiler, schema/catalog, runner, `lib/`, runtime, paper/live, OMS/risk,
  broker/exchange, configs, and data changed: no.
- Candidate, ranking, readiness, promotion, policy, paper/live, or runtime
  authority created: no.
- Protected-path detection weakened globally: no.

## VERIFY-01 Reconciliation

- `docs/status_entries/WP-VERIFY-01.md` is present but still says PR #458 is
  ready for review.
- Current `origin/main` includes PR #470 and the WP-VERIFY-01 helper surfaces
  are present, so WP-VERIFY-02 treats VERIFY-01 as landed repo truth and
  supersedes only the two follow-up issues: canonical-write advisory handling
  and integrity-wrapper throughput.
- This package does not rewrite the WP-VERIFY-01 status fragment.

## Merge Status

- Draft PR #472 is open.
- Package implementation and focused validation are complete.
- Full-pytest merge-readiness is constrained by unrelated current-main
  `tests/test_research_query.py` failures outside this package scope.

## Next Dependency / Runway Note

- Any stale Phase-B query test reconciliation should be handled by a separate
  package with explicit query-test scope.
