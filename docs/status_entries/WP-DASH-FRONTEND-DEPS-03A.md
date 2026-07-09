# WP-DASH-FRONTEND-DEPS-03A — Operator dashboard frontend dependency maintenance

Status: READY_FOR_REVIEW (with documented follow-up)
Class: narrow frontend dependency maintenance (dependency patch only; no dashboard feature work)
Base: `main`

## Objective
Patch the isolated `operator_dashboard_frontend/` Next.js dependency stack away from the security advisory surfaced during `WP-DASH-FRONTEND-SHELL-03F` validation, while preserving the existing read-only, local-first dashboard shell behavior.

## Change
- `operator_dashboard_frontend/package.json`
  - `next`: `14.2.5` → `14.2.35`
  - `eslint-config-next`: `14.2.5` → `14.2.35`
- `operator_dashboard_frontend/package-lock.json` regenerated via `npm install`.
- No `src/**` changes were required (no compatibility fixes needed).
- React / React-DOM unchanged (`18.3.1`).

## Patch selection
`14.2.35` is the latest release of the `14.2.x` line and npm's recommended remediation. It is a within-major/minor patch (Rule 1). It resolves the **critical** auth-bypass advisory class and the bundled-postcss moderate. Remaining **high**-severity residual advisories require `next@16.2.10` (breaking major jump), which is explicitly **not applied** here per Rule 3 and the "no unsafe major/minor jump" stop condition; a separate justified follow-up package is recommended for the Next 16 evaluation.

## Audit
- before (`npm audit --omit=dev`): 2 vulnerabilities (1 moderate, 1 **critical**), 26 aggregated next advisories, auth-bypass present.
- after  (`npm audit --omit=dev`): 2 vulnerabilities (1 moderate, 1 **high**), 14 aggregated next advisories; residual needs `next@16.2.10` (breaking).
- Net: critical → high; auth-bypass + bundled-postcss resolved.

## Validation
Frontend (from `operator_dashboard_frontend/`):
- `npm install`: PASS
- `npm run typecheck`: PASS
- `npm run lint`: PASS (no warnings/errors)
- `npm run build`: PASS

Backend / repo (from worktree root, main-repo venv):
- `pytest tests/test_operator_dashboard_api.py -q`: PASS (11 passed)
- `tools.research_query.run --list-views`: PASS
- `tools.registry.validate_result_populations`: PASS
- `tools.registry.validate_candidate_registry`: PASS
- `tools/dev/diff_scope_summary.py`: PASS (only `package.json` / `package-lock.json`; no forbidden-path matches)
- `git diff --check` / `git diff --cached --check`: clean

No-control scan (`operator_dashboard_frontend/src`): no mutation calls, no forms/submit/control buttons, no Agent Inbox write, no run/approve/execute/promote/cross/trade/paper-live/scheduler/notification controls introduced. Shell remains read-only.

## Boundary
Dependency maintenance only. No feature/control/API/backend/runtime/paper-live/protected-path changes. See `scratch/WP-DASH-FRONTEND-DEPS-03A/non_authority_assertions.json`.

## Evidence
- `scratch/WP-DASH-FRONTEND-DEPS-03A/dependency_audit_before.md`
- `scratch/WP-DASH-FRONTEND-DEPS-03A/dependency_patch_decision.md`
- `scratch/WP-DASH-FRONTEND-DEPS-03A/no_control_evidence.md`
- `scratch/WP-DASH-FRONTEND-DEPS-03A/non_authority_assertions.json`
- `scratch/WP-DASH-FRONTEND-DEPS-03A/validation_summary.txt`
