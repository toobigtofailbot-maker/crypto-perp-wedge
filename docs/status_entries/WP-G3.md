# WP-G3 - Usage-Efficient Validation Standard

## WP id / title

WP-G3 / Usage-efficient validation standard.

## Branch / PR

Branch: `codex/wp-g3-usage-efficient-validation-standard`

PR: #405.

## Package class

T1 process/documentation.

## Scope summary

WP-G3 adds usage-efficient validation guidance to the Codex WP drafting standard. It requires staged validation, focused tests before full pytest, concise validation reporting, full pytest once-final for implementation WPs, and explicit handling of environment-only missing gitignored data failures. Scope is docs/process only.

## Changed files

- `docs/ai/codex/WP_DRAFTING_STANDARD.md`
- `docs/status_entries/WP-G3.md`

## Validation summary

T1 validation passed:

- `git diff --check`
- `python -m tools.registry.validate_result_populations`
- `python -m tools.research_query.run --list-views`
- all discovered `v_integrity_*` views clean / zero rows (`55`)
- `python tools/dev/diff_scope_summary.py`

Full pytest is not required for this T1 docs/process-only package.

## Boundary summary

No code, tests, schemas, tools, research artifacts, data artifacts, runtime/paper/live paths, broker/exchange/order paths, OMS, reconciliation, risk, safe-mode, kill-switch, dependencies, or CI config are changed. The package changes process guidance only and creates no execution, evidence, policy, promotion, approval, or downstream authority.

## Merge status

Ready-for-review PR open; GitHub mergeability check confirmed clean / mergeable.

## Next dependency / runway note

Future WPs should apply the staged validation standard after this package merges. The standard does not weaken package-specific validation, repo-truth inspection, protected boundaries, final rebase, or GitHub mergeability requirements.
