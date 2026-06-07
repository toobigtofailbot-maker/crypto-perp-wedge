# WP-G2 / Process - Status Fragment Refactor

## WP Id / Title

WP-G2 / Process - Status Fragment Refactor.

## Branch / PR

- Branch: `codex/wp-g2-status-fragment-refactor`
- PR: pending at package execution time

## Package Class

T1 process / documentation.

## Scope Summary

Introduces a forward-looking status-fragment process under `docs/status_entries/` so future parallel WPs can record package-level status without using `docs/project_status.md` as a high-churn branch-state log.

## Changed Files

- `docs/status_entries/README.md`
- `docs/status_entries/WP-G2.md`
- `docs/ai/codex/WP_DRAFTING_STANDARD.md`
- `docs/project_status.md`

## Validation Summary

Package validation is expected to include:

- `git diff --check`
- `python -m tools.registry.validate_result_populations`
- `python -m tools.research_query.run --list-views`
- all discovered `v_integrity_*` views clean / zero rows
- `python tools/dev/diff_scope_summary.py`
- `git diff --cached --check`
- `git diff --cached --name-only`

## Boundary Summary

Docs/process only. No code, tests, schemas, tools, research artifacts, data artifacts, runtime, paper, live, OMS, reconciliation, risk, safe-mode, kill-switch, broker, exchange, order path, dependency, or CI changes are introduced.

The status-fragment process is a workflow convention only. It creates no execution authority, research authority, promotion authority, policy authority, or protected-path authority.

## Merge Status

Pending PR at package execution time.

## Next Dependency / Runway Note

After merge, future parallel WPs should prefer `docs/status_entries/<WP_ID>.md` for per-WP branch-state detail and should update `docs/project_status.md` only for milestone summaries, major runway changes, major accepted decisions, or explicit package scope.
