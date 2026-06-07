# WP-F1 / Dashboard Track - Local Static Dashboard Architecture and Design Standard

## WP Id / Title

WP-F1 / Dashboard Track - Local static dashboard architecture, constraints,
and design standard.

## Branch / PR

- Branch: `codex/dashboard-f1-local-static-architecture-design`
- PR: pending

## Package Class

T1 docs/design.

## Scope Summary

WP-F1 locks the local/offline static-first dashboard posture, read-only and
non-authority boundaries, collector -> dashboard_data contract -> renderer
separation, no-server/no-build/no-CDN/no-network constraints, three-page MVP
scope, future page gates, visual design standard, dependency classes,
generated-output policy, dashboard namespace policy, start-before-D5 posture,
and F2/F3/F4/F5/F6 sequence.

The package locks constraints, not a named renderer tool. It does not
implement a dashboard.

## Changed Files

- `docs/architecture/2026-06-local_static_dashboard_design.md`
- `docs/status_entries/WP-F1.md`

## Validation Summary

Package validation is expected to include:

- `git diff --check`
- `python -m tools.registry.validate_result_populations`
- `python -m tools.research_query.run --list-views`
- all discovered `v_integrity_*` views clean / zero rows
- `python tools/dev/diff_scope_summary.py`
- `git diff --cached --check`
- `git diff --cached --name-only`

Full pytest is not required for this T1 docs/design package.

## Boundary Summary

Design-only. No code, schema, validator, dashboard generator, renderer
implementation, templates, CSS/JS assets, generated dashboard output,
dashboard_data output, dependency change, CI change, test change, data artifact,
research artifact, result population, runtime, paper/live, broker/exchange,
order path, credentials, secrets, config, OMS, reconciliation, risk,
safe-mode, kill-switch, query-layer, or protected-path behavior is added.

Dashboard output remains presentation only. The dashboard may display gates,
facts, warnings, staleness, links, hashes, and validation summaries, but it
cannot satisfy gates, approve, promote, rank as authority, recommend execution,
trigger execution, or mutate artifacts.

## Merge Status

Pending PR at package execution time.

## Next Dependency / Runway Note

F2 must define and validate the `dashboard_data` contract before F3 chooses and
implements a static renderer. F3 must prove the selected renderer satisfies the
F1 constraints. F5 waits for D5. F6 waits for paper runtime plus read-only
paper-state snapshots.
