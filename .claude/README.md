# Claude Code Operating Rules

This document defines the operating constraints for all Claude Code sessions working on this repository.

---

## Current-state anchor
Before starting any new architecture, execution, implementation, or review task, read:
- `docs/project_status.md`

Treat that file as the primary current-state status anchor for the repo.

Use it to confirm:
- latest merged work packages
- locked boundaries
- open items
- immediate next architecture need

If `docs/project_status.md` and chat context differ, prefer repo truth and update workflow from the repo state.

This rule is meant to reduce context drift and unnecessary long prompt repetition.

---

## Core Constraints

1. **Only edit files listed in the current execution brief.** Never modify files outside the allowed scope.

2. **Run validation gates before reporting back.** Every report-back must include gate outputs.

3. **Never touch protected boundaries:**
   - `docs/architecture/**` — OMS, reconciliation, safe mode, execution policy, event log schema
   - D-0001 hard caps in `docs/decisions.md`
   - Overlay bounds and fail-open behavior (P1-A, P1-C)
   - Ledger math in `src/paper/ledger_state.py`
   - Any file under `src/`, `tests/`, `configs/`, `scripts/` unless explicitly listed in the execution brief

4. **Do not make architecture decisions.** If the execution brief is ambiguous or requires a decision not covered, STOP and report back. Do not improvise.

5. **Branch discipline:** Always work on the branch specified in the execution brief. Never commit directly to main.

---

## Token Efficiency (D2-009)

- **Interactive work:** Claude Pro subscription
- **Automated queries:** API + prompt caching
- **Complex decisions:** Advisor Strategy (Opus advisor + Sonnet executor)
- **Classification/alerts:** Haiku

When in doubt, prefer Sonnet for code generation.

---

## Agent Boundaries (D2-011)

No agent or Claude Code session may:
- Modify overlay logic, ledger math, or D-0001 caps
- Push to main without PR review
- Execute trades or modify positions
- Change risk parameters

---

## Report-Back Requirements

Every session must report back using the template in `prompts/report_back.md`:
- Files changed (git diff --stat)
- Validation gate outputs
- Evidence checklist
- Issues encountered
- Escalation items

---

## Advisor Strategy (D2-009)

Phase 2 uses a three-tier model selection policy.  **No third-party model
routers** are used in Phase 2.

### When to use each model

| Tier | Model | Use case |
|------|-------|----------|
| Advisor | **Opus** (claude-opus-4-6) | Architecture decisions, contradiction sweeps, scope rulings, reviewing complex execution briefs before issuing them, evaluating report-backs with escalation flags |
| Executor | **Sonnet** (claude-sonnet-4-6) | Default for all Claude Code implementation sessions: writing code, running tests, committing, creating PRs |
| Classifier | **Haiku** (claude-haiku-4-5) | Log parsing, alert classification, high-volume batch labelling, fast triage of trade events |

### Advisor + Executor workflow

Use the Opus-as-Advisor + Sonnet-as-Executor pattern when:
- A design question has no clear answer in `docs/decisions.md`
- Two plausible implementations exist with different architectural trade-offs
- A contradiction sweep surfaces a conflict in locked truth
- An escalation is received from an Execution chat

Steps:
1. **Advisor (Opus):** Open a separate conversation.  Present the ambiguity.
   Get a ruling or design decision.  Document the decision in `docs/decisions.md`
   if it is durable.
2. **Executor (Sonnet):** Proceed with the execution brief once the ambiguity
   is resolved.  Do not improvise on architecture questions.

### What Haiku handles

- Parsing JSONL event logs for anomalies
- Classifying funding-rate regime (positive / negative / neutral)
- Batch-labelling candle patterns for hypothesis screening
- Triage of alerts from the paper trader

### Policy: no third-party routers in Phase 2

Phase 2 does not use LangChain, AutoGen, or any external orchestration
framework for routing between models.  Routing is done manually by the human
operator using the three-tier policy above.  This policy is locked per D2-009
and may not be changed by an Execution chat.

---

## Agents and skills

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

- `prompts/pr_review.md`
- `prompts/contradiction_sweep.md`
- `prompts/hypothesis_drafting.md`
- `prompts/evaluation_review.md`
