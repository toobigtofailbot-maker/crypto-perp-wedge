# WP-PLAN-SIDE12-ADOPTION-LOCK-01 - Side 12 external adoption pilot plan lock

## WP Id / Title

- WP id: `WP-PLAN-SIDE12-ADOPTION-LOCK-01`
- Title: Lock Side 12 external adoption pilot plan
- Decision: `COMPLETE`

## Branch / PR

- Branch: `plan/side12-adoption-lock-01`
- Dedicated worktree: `C:\GitHub\crypto-perp-wedge-worktrees\plan-side12-adoption-lock-01`
- Base: `origin/main` at `0ca18b9`
- Rebase result: clean worktree created from refreshed `origin/main`
- PR: `https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/526`

## Package Class

Docs/status plan lock.

## Repo-Truth Discovery

- Startup anchors read: `docs/project_status.md`, `CLAUDE_START_HERE.md`,
  `docs/runbook.md`, and `AGENTS.md`.
- Required status entries read:
  `docs/status_entries/README.md`,
  `docs/status_entries/EXT-ADOPTION-DECISION-01.md`,
  `docs/status_entries/WP-LAB-WALKFORWARD-RUN-01.md`,
  `docs/status_entries/WP-LAB-DASHBOARD-EXPANSION-01.md`, and
  `docs/status_entries/WP-LAB-IDEA-INTAKE-FORMALIZATION-01.md`.
- Existing architecture/adoption docs searched and read:
  `docs/architecture/2026-06-external_repo_adoption_decision.md`,
  `docs/onboarding/PHASE2_BASELINE.md` D2-010 references, and
  `docs/decisions.md` D2-010 references.
- Repo convention found: `docs/architecture/` exists and has no README index,
  so no architecture README update was required.

## Scope Summary

This package adds a docs-only plan lock for Side 12 external-repo research
triage. It records pilot-now, skip-now, next-wave, defer, preserve/reference,
and simulator dispositions; locks the adopt/sidecar/borrow/preserve/reject
criteria; records the active pilot runway; and preserves the protected-boundary
posture for external-tool outputs.

It reconciles the active package's LangGraph deferral wording with current
merged repo truth by recording no current adoption and preserving D2-010's
Phase 2 rejection unless a later approved package changes repo truth.

## Changed Files

- `docs/architecture/2026-06-side12-external-adoption-pilot-plan.md`
- `docs/status_entries/WP-PLAN-SIDE12-ADOPTION-LOCK-01.md`

## Validation Summary

- Focused tests: not applicable; this is a docs/status-only plan lock with no
  package-specific code or validator changes.
- `python tools/dev/diff_scope_summary.py`: PASS before and after staging; only
  the two scoped docs files were reported and no forbidden-path matches were
  found.
- `git diff --check`: PASS.
- `git diff --cached --check`: PASS after staging.
- `python -m tools.research_query.run --list-views`: PASS; view discovery
  completed.
- `python -m pytest -q` with ambient Python 3.14: FAIL during collection in
  5.52 seconds because the ambient interpreter lacks repo dependencies
  (`binance`, `pandas`, and `numpy`); not used as passing merge evidence.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`: FAIL in
  approximately 210 seconds after reaching 49% progress; one visible failure
  surfaced before termination.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q -x`: FAIL
  in 50.65 seconds at
  `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage`
  because `fixture["normalized_data_local_exists"]` was `False` instead of
  `True`. This is the isolated-worktree local-data availability expectation
  disclosed in recent repo status fragments, not a docs/status-plan failure.
  The rerun reached 518 passed, 1 skipped, and 1 failed before stopping after
  the first failure.

## Boundary Summary

- Canonical writes: NO.
- Runner/backtester mutation or replacement: NO.
- `lib/backtest.py` semantics changed: NO.
- Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, trial
  log, and canonical walk-forward evidence mutated: NO.
- External tools granted canonical, candidate, readiness, promotion, ranking,
  recommendation, approval, dashboard-control, paper/live, or runtime
  authority: NO.
- Runtime / paper / live paths touched: NO.
- OMS / risk / reconciliation / safe-mode / kill-switch / broker / exchange /
  order / capital paths touched: NO.
- Private credentials or authenticated APIs used: NO.
- Dependency files changed: NO.
- `docs/project_status.md` changed: NO.

## Active-WP Requirement Traceability

| Active-WP requirement | Evidence location | Status |
|---|---|---|
| Create Side 12 adoption plan lock | `docs/architecture/2026-06-side12-external-adoption-pilot-plan.md` | satisfied |
| Record current adoption posture | Current Adoption Posture section | satisfied |
| Record tool disposition table | Tool Disposition Table section | satisfied |
| Record active pilot runway | Active Pilot Runway section | satisfied |
| Record repo-owned surfaces | Repo-Owned Surfaces That Stay Repo-Owned section | satisfied |
| Record adopt/sidecar/borrow/preserve/reject criteria | Criteria section | satisfied |
| Include required boundary block | Required Boundary Block section | satisfied |
| Record WP savings expectation | WP Savings Expectation section | satisfied |
| Avoid forbidden files and protected boundaries | Changed files and Boundary Summary | satisfied |

## Merge Status

- Local branch validation: completed with full-suite limitation disclosed above.
- Push status: pushed to `origin/plan/side12-adoption-lock-01`.
- PR state: ready for review.
- GitHub mergeability: `gh pr view 526 --json mergeable,mergeStateStatus`
  reports `mergeable=MERGEABLE` and `mergeStateStatus=CLEAN`.

## Next Dependency / Runway Note

The active pilots remain separate packages:
`WP-PILOT-PURGEDCV-01`, `WP-PILOT-OPTUNA-SEARCH-SIDECAR-01`, and
`WP-PILOT-NOTIFICATIONS-APPROVALS-01`. This plan does not implement or validate
those pilots.
