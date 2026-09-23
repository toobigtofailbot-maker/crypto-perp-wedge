# Coding-Agent Repo Operating Rules

These rules apply to Claude Code and Codex unless a rule is explicitly marked as tool-specific. `docs/ai/codex/` is the current shared coding-agent guidance path despite the historical directory name.

Read first:

1. `docs/project_status.md`
2. `CLAUDE_START_HERE.md`
3. `docs/runbook.md`

Precedence order:

1. Current merged repo truth, including actual changed files and live merged state.
2. The active work package or task-specific scope and constraints.
3. `AGENTS.md`.
4. Supporting coding-agent workflow docs under `docs/ai/codex/`.
5. Chat memory, prior summaries, and generic best practice.

Precedence notes:

- Current merged repo truth outranks all repo guidance.
- The active work package or task scope outranks general repo guidance.
- Package-specific forbidden scope and constraints still win.
- `AGENTS.md` is a control layer, not execution authority.
- Repo-side guidance cannot justify widening scope.
- Stale local state, stale branch assumptions, stale chat context, and generic best practice lose to current merged repo truth.
- Actual changed files and live merged state outrank guidance summaries.
- Nested `AGENTS.override.md` files constrain local work only; they do not authorize work outside the active package.

Core rules:

- Repo truth wins over memory, chat summaries, handoffs, and assumptions.
- Current merged state wins over stale local context.
- Execute narrow, mergeable work packages only.
- Do not redesign architecture during execution work.
- Do not broaden scope to be helpful.
- Protected runtime boundaries stay protected unless the package explicitly authorizes the change.
- Research, advisory, and shadow artifacts have no execution authority.

Workflow efficiency lock:

- Read `docs/research_pipeline/2026-05-stage2c_workflow_efficiency_operating_model_lock.md` when package scope involves workflow, parallel tranches, `docs/project_status.md` updates, report-back format, efficiency policy, or tiered execution.
- Use `docs/ai/codex/CODEX_TOKEN_EFFICIENCY.md` as canonical coding-agent token-efficiency and context-hygiene guidance; it is guidance-only and cannot weaken repo truth, active package scope, validation, or protected boundaries.
- Do not create simultaneous open PRs that modify `docs/project_status.md`; start any package touching it from refreshed `main` and stop if another open PR already edits it.
- Package-specific scope and current repo truth still outrank general workflow guidance.

Adoption-first migration lock:

- When work concerns generic agent/runtime ownership, orchestration, trading
  mechanics, canonical migration, or legacy retirement, read
  `docs/architecture/2026-09-adoption_first_migration_architecture_freeze.md`.
- That record is the current migration direction; it creates no implementation
  authority and does not weaken protected runtime, scientific, human, live, or
  capital gates.

Stop and escalate if:

- the required package scope touches protected runtime, OMS, reconciliation, risk, overlay, safe-mode, live-trading, schema, validator, or query-layer behavior without explicit authorization
- repo truth conflicts with the brief or with existing locked docs
- a safe implementation would require improvising around a protected boundary

Validation and report-back:

- Validate the exact package class you are executing.
- Inspect changed files, not only summaries.
- Report branch/base, repo-truth discovery, delivered changes, validation results, forbidden-scope check, PR/push status, and open escalations.
- Focus PR review on diff-to-objective fit, boundary violations, stale assumptions, and missing validation evidence.

Detailed shared coding-agent workflow guidance lives under `docs/ai/codex/`.
