# WP-ROBUST-C2-DESIGN - Walk-forward / OOS windowing design

- Package class: T1 docs-only methodology design.
- Branch: `docs/robust-c2-walkforward-oos-design`.
- Dedicated worktree: `C:\GitHub\crypto-perp-wedge-WP-ROBUST-C2-DESIGN`.
- Base: `origin/main` after PR #459 merge (`1c092f3`).
- Recovery / isolation: A1 remained dirty and untouched at
  `C:\GitHub\crypto-perp-wedge` on `express/a1-zscore-volnorm-distance`. C2
  work was isolated in the dedicated C2 worktree and branch.
- Scope summary: Creates a docs-only future walk-forward / OOS windowing design
  for the research lab, covering purpose, terminology, chronology/no-lookahead
  constraints, full-population retention, denominator honesty, future artifact
  implications, validation expectations, explicit deferrals, and relationship
  to WP-ROBUST-C1.
- Created design file:
  `docs/research_pipeline/2026-06-walkforward_oos_windowing_design.md`.
- README pointer: Adds one compact index entry for the new design note in
  `docs/research_pipeline/README.md`.
- Project-status update: Adds a compact WP-ROBUST-C2-DESIGN branch-state line
  to `docs/project_status.md`.
- Repo-truth discovery summary: Existing repo truth includes walk-forward-first
  as future MVP validation posture in the lab validity-floor design, OOS fields
  in existing EXP/REP/OL surfaces, result-population storage references to
  future folds/windows, and WP-ROBUST-C1 read-only robustness diagnostics. No
  equivalent dedicated walk-forward / OOS windowing design file was found.
- Boundary summary: Docs/status/index only. No tools, tests, lib, src,
  research schemas, result populations, Strategy Specs, variant manifests,
  sweep plans, data catalog, canonical data, runner, backtester, query-layer
  behavior, candidate lifecycle, ranking, promotion, readiness, dashboard
  implementation, paper/live/runtime, OMS/risk/reconciliation, broker/exchange,
  collateral, or autonomous behavior changed or authorized.
- Validation summary: `git diff --check` passed; `git diff --cached --check`
  passed before staging; `git diff --name-only` showed the tracked
  docs/status scope before untracked files were staged; `python
  tools/dev/diff_scope_summary.py --check-forbidden` passed with no
  forbidden-path matches; `python -m tools.registry.validate_result_populations`
  passed; `python -m tools.research_query.run --list-views` passed; system
  `python -m pytest -q` failed at collection because Python 3.14 lacked local
  dependencies (`binance`, `numpy`, `pandas`); venv full pytest passed with
  `1385 passed, 1 skipped, 6 warnings`.
- Next authority: This package authorizes no implementation or canonical write.
  Future window protocol, schema/validator, runner, query, and canonical
  result-population work requires separately scoped Main/Karl authorization.
