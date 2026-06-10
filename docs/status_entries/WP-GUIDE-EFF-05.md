# WP-GUIDE-EFF-05 — Final PR readiness gate for placeholder-free review artifacts

**Package class:** T1 — docs/process/guidance
**Branch:** `docs/guide-eff-05-final-pr-readiness-gate`
**PR:** TBD (will be updated after PR is opened)

## Scope summary

Adds a final PR-readiness gate to shared Claude Code / Codex guidance so coding-agent PRs do not reach Side/Main review with placeholder PR bodies, stale status-fragment PR fields, pending validation text, or non-authority wording drift. Triggered by WP-F5A / PR #422, which required multiple follow-ups for issues the final-readiness gate would have caught.

## Changed files

| File | Change |
|---|---|
| `docs/ai/codex/WP_DRAFTING_STANDARD.md` | Added Section 15 "Final PR Readiness Gate"; updated merge-readiness reviewer checklist |
| `docs/ai/codex/WP_EXECUTION_REPORT.md` | Expanded compact/expanded shape section E and G to require PR-body placeholder scan and status-fragment finality; added note that PR body is part of the review evidence surface |
| `docs/ai/codex/COMPACT_WP_TEMPLATE.md` | Added Section 11a "Final PR Readiness Gate"; added "Semantic Text Audit for Non-Authority Packages" block; updated reviewer checklist |
| `docs/status_entries/README.md` | Added "Status Fragment Finality Rules" section |
| `docs/status_entries/WP-GUIDE-EFF-05.md` | This file (new) |
| `docs/project_status.md` | Appended compact WP-GUIDE-EFF-05 pointer |

## Validation summary

```
git status --short
(clean before edits — confirmed at preflight)

git diff --check
(clean)

python -m tools.registry.validate_result_populations
Not run; not used as merge evidence. (T1 docs-only package; no registry artifact changes)

python -m tools.research_query.run --list-views / v_integrity_* views
Not run; not used as merge evidence. (T1 docs-only package; no query-layer changes)

python tools/dev/diff_scope_summary.py
Not run; not used as merge evidence. (T1 docs-only package)

Full pytest
Not run; not used as merge evidence. (T1 docs-only package; no code, schema, or test changes)

Final rebase / mergeability gate
Run before PR open; results updated in PR body.
```

## Boundary summary

WP-GUIDE-EFF-05 does **not**:
- Implement PR-body automation, scripts, helpers, validators, CI, or GitHub Actions
- Modify validation commands or weaken validation requirements
- Make status fragments a repo-truth replacement or demote `docs/project_status.md`
- Rewrite historical `docs/project_status.md` entries
- Touch F5B/F5C implementation
- Touch dashboard collector, renderer, generator, or generated output
- Touch schemas, validators, tests, result populations, data artifacts, query-layer, strategy specs, variant manifests, sweep plans, runtime, paper/live, OMS, risk, broker/exchange, configs, dependencies, or protected paths
- Add ranking/recommendation/readiness/promotion/execution authority
- Alter startup read order or rename `docs/ai/codex/`

## Merge status

Open PR — TBD (will be updated after PR is opened).

## Next dependency / runway note

F5B (collector) remains gated on WP-F5A / PR #422 merge (already done) and separate Main authorization. This guidance package is a T1 prerequisite for F5B/F5C only in the sense that F5B/F5C packages will inherit the strengthened final-readiness contract.
