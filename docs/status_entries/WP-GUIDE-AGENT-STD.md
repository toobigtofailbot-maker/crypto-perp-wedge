# WP-GUIDE-AGENT-STD — Shared Coding-Agent Workflow Guidance Standard

## WP id / title

WP-GUIDE-AGENT-STD — Shared Coding-Agent Workflow Guidance Standard

## Branch / PR

Branch: `docs/shared-coding-agent-guidance-standard`
PR: Docs: Standardize shared coding-agent workflow guidance (ready for review, not draft)

## Package class

T1 docs/guidance cleanup

## Scope summary

Terminology-only guidance cleanup. Standardizes repo guidance so Claude Code and Codex follow the same shared coding-agent workflow by default unless a rule is explicitly tool-specific. No workflow rule was weakened. No runtime, schema, validator, query, test, artifact, or protected path changed.

## Changed files

- `AGENTS.md` — title and body updated to coding-agent wording; shared-guidance path clarified
- `CLAUDE_START_HERE.md` — title updated; token-efficiency reference updated; shared-path pointer added
- `.claude/README.md` — clarified as thin Claude-specific entrypoint; shared-guidance layer pointer added
- `docs/ai/codex/README.md` — clarified as current shared coding-agent guidance path; Model/Boundaries/Use sections updated
- `docs/ai/codex/WP_DRAFTING_STANDARD.md` — title and generic "Codex WP" wording updated to "coding-agent WP"
- `docs/ai/codex/COMPACT_WP_TEMPLATE.md` — title and generic "Codex WP" wording updated to "coding-agent WP"
- `docs/ai/codex/CODEX_TOKEN_EFFICIENCY.md` — title updated; applicability note added; Codex-specific content preserved
- `docs/ai/codex/WP_EXECUTION_REPORT.md` — report-back header updated to "coding-agent"
- `docs/onboarding/WORKFLOW.md` — token-efficiency reference updated to "coding-agent"
- `docs/status_entries/WP-GUIDE-AGENT-STD.md` — this file (status fragment)

## Validation summary

T1 docs-only package. No code, tests, schemas, tools, data artifacts, research artifacts, or runtime paths changed. Full pytest not required for T1 class.

- `git diff --check`: clean
- `git status --short`: only expected changed files
- No runtime, query, schema, validator, or artifact touched

## Boundary summary

- This is docs/guidance only; no workflow rule was weakened.
- No runtime, schema, validator, query, test, artifact, or protected path changed.
- `docs/ai/codex/` remains the current shared coding-agent guidance path for now; no directory rename occurred.
- `.claude/` remains a thin Claude-specific entrypoint; no duplicate Claude mirror docs were created.
- `.claude/agents/*` and `.claude/skills/*` were not touched.
- Historical status entries and research artifacts were not touched.

## Merge status

PR open, ready for review.

## Next dependency / runway note

Path migration from `docs/ai/codex/` to a neutral directory name is a separate future WP if desired. No path migration was done here.
