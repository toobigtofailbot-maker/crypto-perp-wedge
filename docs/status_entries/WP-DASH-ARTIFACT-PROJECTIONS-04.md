# WP-DASH-ARTIFACT-PROJECTIONS-04 — Read-only real artifact projections

- Base: `main` @ `1969251`
- Branch: `codex/wp-dash-artifact-projections-04`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/642
- GitHub state: ready for review
- Decision: scoped implementation complete and ready for review. The repository-wide
  stale-count test failure is reproducible on clean current `main` and unrelated to this PR.

## Delivered

Added `GET /api/research/result-populations/{id}/artifact-projections`. The route projects:

- 66 exact `variant_result_rows` across all 8 committed Result Populations as summarized
  trade diagnostics;
- two committed WFO `fold_results` arrays, 2 folds each, linked to `RP-2592` by exact
  strategy-spec / variant-manifest / sweep-plan lineage;
- the committed seeded Monte Carlo `bootstrap_ci` summary for `RP-2592`, covering 10
  metrics and recording the source report's 1,000-sample count.

Each real projection carries source path, file SHA-256, source field, linkage, and applicable
row/fold/path/sample counts. Tests compare every projected payload to its exact committed
source field and recompute the returned file hash.

Equity curves, drawdown time series, raw Monte Carlo sample distributions, per-trade return
distributions, and trade lists remain explicitly unavailable. The API provides reasons and
no data member for those classes; it does not zero-fill or reconstruct them.

## Changed files

- `tools/operator_dashboard_api/app.py`
- `tools/operator_dashboard_api/readers.py`
- `tools/operator_dashboard_api/README.md`
- `tests/test_operator_dashboard_api.py`
- `docs/status_entries/WP-DASH-ARTIFACT-PROJECTIONS-04.md`
- `scratch/WP-DASH-ARTIFACT-PROJECTIONS-04/artifact_inventory.md`
- `scratch/WP-DASH-ARTIFACT-PROJECTIONS-04/projection_contract.md`
- `scratch/WP-DASH-ARTIFACT-PROJECTIONS-04/no_fabrication_evidence.md`
- `scratch/WP-DASH-ARTIFACT-PROJECTIONS-04/validation_summary.txt`

## Validation

- Focused API tests: 14 passed.
- Research-query view listing: 124 views.
- Result-population validator: pass.
- Candidate-registry validator: pass.
- Diff-scope summary: no forbidden-path matches.
- Diff checks: clean.
- Full suite with `--maxfail=1`: 1 failed, 1136 passed before stop. The failure is
  `test_batch_boundary_reflects_coverage_gap_closure` expecting 8 subjects while current
  merged artifacts produce 9. It reproduces identically in a clean detached `origin/main`
  worktree at the original base `1969251` and refreshed `origin/main` at `42cd688`; this
  package does not touch that subsystem or its inputs.

## Boundary and follow-up

Read-only API and evidence only. No canonical artifact, schema, validator, query behavior,
frontend, runner, backtest, bridge, gate, pipeline, runtime, paper/live, OMS, risk,
reconciliation, safe-mode, broker/exchange, scheduler, notification, control, approval,
ranking, recommendation, readiness, or promotion behavior changed.

A follow-up UI package is justified for the real `RP-2592` WFO folds and Monte Carlo
confidence summaries, and for the already-real summarized trade diagnostics. Equity,
drawdown time-series, per-trade-return, raw-Monte-Carlo-sample, and trade-list charts remain
unjustified until real committed source arrays exist.
