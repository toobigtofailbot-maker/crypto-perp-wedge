# WP-E4 / Engineering Block 1 - Paper-Bot Scaffolding Design

## WP Id / Title

WP-E4 / Engineering Block 1 - Paper-Bot Scaffolding Design.

## Branch / PR

- Branch: `codex/engineering-block-1-e4-paper-bot-scaffolding-design`
- PR: #401

## Package Class

T1 design / documentation.

## Scope Summary

Designs sandbox-only paper-bot scaffolding inside the E1 two-lane sandbox wall.
The design defines future components, manual operator approval, allowed input
sources, forbidden automatic authority sources, separate sandbox state and
provenance recording, local paper position/order simulation concepts, stop and
safe-state concepts, E2 operator-surface relationship, E3 alert/briefing
relationship, and the future implementation authorization boundary.

## Changed Files

- `docs/architecture/2026-06-paper_bot_scaffolding_design.md`
- `docs/project_status.md`
- `docs/status_entries/WP-E4.md`

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

Design-only. No paper-runtime code, dashboard code, alert code,
scheduler/daemon, credentials, secrets, config changes, broker/exchange/order
or live API contact, order lifecycle code, OMS/reconciliation/risk/kill-switch
or safe-mode implementation, schema/query/validator/tool/test/dependency/data
changes, strategy artifact mutation, result-population mutation, or authority
semantics are added.

Any paper-runtime implementation after E4 requires separate Main/Karl-reviewed
authorization of the sandbox-runtime boundary before code lands.

## Merge Status

Pending PR at package execution time.

## Next Dependency / Runway Note

Post-E4 implementation work is not authorized by this package. Main/Karl must
review and authorize the sandbox-runtime boundary before any paper-runtime
implementation package, including exact files and paths, state artifact shape,
validation/tests, and whether any protected Phase 1 runtime surfaces can be
reused.
