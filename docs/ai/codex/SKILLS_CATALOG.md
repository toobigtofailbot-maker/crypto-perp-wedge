# Codex Skills Catalog

No confirmed repo-local Codex skill install path is currently available in this repository. The visible skill assets are machine-local Codex skills outside the repo and existing `.claude/skills/*` files for Claude workflow. Treat the skills below as repo-side specifications for now, not installed Codex skills.

## `repo-truth-discovery`

- Purpose: verify current branch state, startup docs, protected boundaries, and relevant repo facts before planning or execution.
- When to use: at the start of any work package, review, or escalation.
- Must not do: rely on memory or stale chat summaries in place of current repo inspection.
- Priority: now.

## `wp-execution-package-runner`

- Purpose: execute one locked work package with scope control, branch discipline, validation, and report-back.
- When to use: during Code Mode implementation of an approved package.
- Must not do: redesign architecture, broaden scope, or touch forbidden paths without explicit authorization.
- Priority: now.

## `protected-boundary-review`

- Purpose: scan a proposed or completed diff for protected-path and protected-semantics violations.
- When to use: before editing sensitive areas and during final review.
- Must not do: approve runtime, risk, overlay, or live-trading changes by implication.
- Priority: now.

## `artifact-family-producer`

- Purpose: produce bounded research or reporting artifact families that follow repo conventions.
- When to use: artifact-focused packages with explicit allowed scope.
- Must not do: claim execution authority or alter runtime behavior.
- Priority: later.

## `diagnostic-brief-builder`

- Purpose: assemble diagnostic briefs from current repo evidence without overstating conclusions.
- When to use: evidence synthesis, audits, and bounded reporting packages.
- Must not do: recommend policy or runtime changes unless the package explicitly requests that analysis.
- Priority: later.

## `pr-merge-readiness-review`

- Purpose: evaluate whether a branch is ready for PR or merge review based on changed files, validation, and scope discipline.
- When to use: before push, PR creation, or final reviewer handoff.
- Must not do: substitute for direct inspection of the actual diff.
- Priority: now.

## `blocked-run-triage`

- Purpose: classify blocked runs by missing repo truth, protected-boundary conflict, validation failure, or environment mismatch.
- When to use: when execution cannot proceed safely.
- Must not do: improvise around blockers or weaken protections to keep momentum.
- Priority: now.

## `current-state-test-maintenance`

- Purpose: maintain tests that encode current repo contracts when a package explicitly changes those contracts.
- When to use: schema, validator, query, helper, or other code packages that legitimately require current-state test updates.
- Must not do: rewrite tests to hide regressions or avoid validation debt.
- Priority: later.
