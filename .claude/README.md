# Claude Code / Codex Operating Rules

This file defines operating constraints for Claude Code and Codex sessions working in this repository.

## Current-State Anchor

Read order for every architecture, execution, implementation, or review task:

1. `docs/project_status.md`
2. `CLAUDE_START_HERE.md`
3. `docs/runbook.md`
4. `docs/architecture/LONG_TERM_SCOPE.md` when the task touches longer-horizon roadmap, automation, agent, dashboard, or self-improvement scope
5. Only the additional files needed for the current task

Treat the repo as the source of truth. If chat context, memory, or a brief conflicts with current repo files, prefer repo truth and report the mismatch. If the mismatch affects scope, locked decisions, or validation, stop and escalate instead of improvising.

## Scope Discipline

1. Work only on the branch named in the current execution brief.
2. Edit only files listed in the allowed scope for the current package.
3. Never modify protected runtime, data, tests, configs, scripts, architecture docs, agents, skills, or prompt files unless the current package explicitly allows it.
4. Do not make architecture decisions. Escalate ambiguity that changes behavior, boundaries, or locked truth.
5. Preserve deterministic execution and auditability.

Default package flow is Main Architecture -> Claude Code / Codex direct execution. Separate Karl Architecture review/handoff is optional, not default; if an additional architecture ruling is explicitly requested, wait for that ruling before executing.

## Protected Boundaries

Do not touch without explicit package scope and locked architecture approval:

- `docs/architecture/**`
- `docs/decisions.md`
- OMS truth / reconciliation truth
- Kill-switch semantics
- D-0001 hard caps
- Overlay bounds `{ALLOW, ALLOW_REDUCED=0.5, BLOCK}` and fail-open behavior
- Paper ledger accounting math
- Files under `src/`, `tests/`, `configs/`, `scripts/`, or `data/` unless explicitly listed in the brief
- Existing `.claude/skills/*` and `.claude/agents/*` unless explicitly listed in the brief

## Validation And Report-Back

Run the validation gates from the execution brief before reporting complete. Report-back must include:

- Branch and PR or compare URL.
- Files changed.
- Validation gates with raw evidence or exact summaries.
- Forbidden-scope confirmation.
- No-data/no-artifact confirmation where relevant.
- Dependencies added: `NONE` or an explicit list.
- Open escalations.

Use `prompts/report_back.md` unless the brief supplies a stricter format.

## Token Efficiency And Model Use

Phase 2 uses the locked Advisor Strategy from D2-009:

| Tier | Model | Use case |
|---|---|---|
| Advisor | Opus | Architecture decisions, contradiction sweeps, scope rulings, complex brief review, escalation review |
| Executor | Sonnet | Default implementation sessions: writing code, running tests, committing, creating PRs |
| Classifier | Haiku | Log parsing, alert classification, batch labelling, fast triage |

No third-party model routers are used in Phase 2.

## Agent Boundaries

No agent or Claude Code / Codex session may:

- Execute trades or modify positions.
- Change risk parameters.
- Modify overlay logic, ledger math, or D-0001 caps without explicit architecture approval.
- Push to `main` without PR review.
- Override promotion gates or approve its own evaluation.

## Local Workflow Assets

Agent definitions:

- `.claude/agents/analyst.md`
- `.claude/agents/engineer.md`
- `.claude/agents/auditor.md`
- `.claude/agents/watchdog.md`

Workflow skills:

- `.claude/skills/write-execution-brief.md`
- `.claude/skills/review-report-back.md`
- `.claude/skills/draft-hypothesis.md`
- `.claude/skills/run-evaluation.md`
- `.claude/skills/timeframe-suitability-brief.md`

Prompt templates:

- `prompts/execution_brief.md`
- `prompts/report_back.md`
- `prompts/pr_review.md`
- `prompts/contradiction_sweep.md`
- `prompts/hypothesis_drafting.md`
- `prompts/evaluation_review.md`
