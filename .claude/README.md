# Claude Code Operating Rules

This document defines the operating constraints for all Claude Code sessions working on this repository.

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
