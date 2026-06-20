# EXT-ADOPTION-DECISION-01 - External Repo Adoption Decision

## WP Id / Title

- WP id: `EXT-ADOPTION-DECISION-01`
- Title: Formalize external-repo adoption architecture decision

## Branch / PR

- Branch: `ext/adoption-decision-01`
- PR: `https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/520`
- Base: refreshed `origin/main` at `2348f89b8b0281e8bde48ce40d22d992a3158b16`

## Package Class

T1 docs / architecture decision.

## Scope Summary

This package creates the repo-owned external-repo adoption decision record after
the external integration/evaluation runway completed through PRs #514 through
#519. It records final dispositions for CCXT funding, robustness MC,
workflow-gen, analytics metrics, vectorbt, and Nautilus.

It does not implement integration, simulator, data, runner, dashboard, runtime,
paper/live, or candidate lifecycle behavior.

## Changed Files

- `docs/architecture/2026-06-external_repo_adoption_decision.md`
- `docs/status_entries/EXT-ADOPTION-DECISION-01.md`
- `docs/project_status.md`

## Validation Summary

- `python -m tools.research_query.run --list-views`: PASS.
- `python tools/dev/diff_scope_summary.py`: PASS; changed files are docs-only and no forbidden runtime/protected matches were reported.
- `git diff --check`: PASS.
- `python -m tools.registry.validate_result_populations`: PASS.
- `python tools/dev/verify.py --validation-preset docs-only --integrity-views --json --max-output-chars 6000 --timeout-seconds 600`: PASS; all discovered `v_integrity_*` views were clean.
- Full pytest: Not run; docs-only decision package and not used as merge evidence.

## Boundary Summary

- Runtime / paper / live touched: NO.
- OMS / risk / reconciliation / safe-mode / kill-switch / broker / exchange / order paths touched: NO.
- Private APIs / credentials / account / balance / position / order methods used: NO.
- Canonical Result Population / Strategy Spec / Variant Manifest / Sweep Plan mutation: NO.
- Runner / backtester / `lib/backtest.py` mutation or replacement: NO.
- Dependency files changed: NO.
- Promotion / readiness / screen-gate / candidate-evidence authority created: NO.
- Nautilus canonical authority granted now: NO.
- Vectorbt canonical authority granted now: NO.
- Funding wired into backtest: NO.

## Merge Status

- PR state: ready for review.
- Final rebase: completed against `origin/main`.
- Push status: pushed to `origin/ext/adoption-decision-01`.
- GitHub mergeability: `MERGEABLE`.

## Active-WP Requirement Traceability

| Active-WP requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Create adoption architecture decision | Objective / files to create | `docs/architecture/2026-06-external_repo_adoption_decision.md` | satisfied |
| Preserve six component dispositions | Objective / decision document requirements | Decision summary and per-component sections | satisfied |
| Preserve Nautilus shelved trigger and gaps | Objective / Nautilus preservation | Nautilus section | satisfied |
| Add per-WP status fragment | Scope / status entries rule | `docs/status_entries/EXT-ADOPTION-DECISION-01.md` | satisfied |
| Compact project-status pointer only | Scope / files to modify | `docs/project_status.md` | satisfied |
| Avoid implementation and protected boundaries | Forbidden scope / global forbidden scope | Changed-file list and boundary summary | satisfied |
| Run required docs validation | Validation | Validation Summary | satisfied |

## Next Dependency / Runway Note

The external-repo adoption runway is closed as a docs-only architecture decision.
The lab-completion path continues via walk-forward / OOS canonicalization and
results-surface work. Those follow-ons remain separate packages.
