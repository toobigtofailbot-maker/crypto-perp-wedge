# Codex Repo Operating Rules

Read first:

1. `docs/project_status.md`
2. `CLAUDE_START_HERE.md`
3. `docs/runbook.md`

Core rules:

- Repo truth wins over memory, chat summaries, handoffs, and assumptions.
- Current merged state wins over stale local context.
- Execute narrow, mergeable work packages only.
- Do not redesign architecture during execution work.
- Do not broaden scope to be helpful.
- Protected runtime boundaries stay protected unless the package explicitly authorizes the change.
- Research, advisory, and shadow artifacts have no execution authority.

Stop and escalate if:

- the required package scope touches protected runtime, OMS, reconciliation, risk, overlay, safe-mode, live-trading, schema, validator, or query-layer behavior without explicit authorization
- repo truth conflicts with the brief or with existing locked docs
- a safe implementation would require improvising around a protected boundary

Validation and report-back:

- Validate the exact package class you are executing.
- Inspect changed files, not only summaries.
- Report branch/base, repo-truth discovery, delivered changes, validation results, forbidden-scope check, PR/push status, and open escalations.
- Focus PR review on diff-to-objective fit, boundary violations, stale assumptions, and missing validation evidence.

Detailed Codex workflow guidance lives under `docs/ai/codex/`.
