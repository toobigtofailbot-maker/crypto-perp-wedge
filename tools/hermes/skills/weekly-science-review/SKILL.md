---
name: weekly-science-review
description: Produce a weekly evidence-linked science review.
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [research, reporting, weekly]
    category: research
    requires_toolsets: [mcp-project-evidence]
---

# Weekly Science Review

## Procedure

1. Resolve repo SHA and project status through Project-Evidence MCP.
2. Inspect relevant experiment and Result Population evidence at that SHA.
3. Report denominator/evidence coverage, known failures, unresolved blockers,
   and evidence-quality limitations.
4. Format: FACT; INFERENCE; BLOCKER/FAILURE; OPEN QUESTION; source ledger.
5. Mark mutable Research Memory content as index-only unless exact repo evidence
   resolves every supporting reference.
6. State UNKNOWN when evidence is missing or ambiguous.

## Authority boundary

This is descriptive criticism, not scientific truth, ranking, recommendation,
readiness, promotion, freeze, dispatch, execution, runtime, or risk authority.
It cannot mutate project state or self-enable tools.
It cannot self-enable any broader capability.

## Verification

Every factual conclusion has repo SHA and evidence lineage; all inferences are
explicit and no missing evidence is converted into a fact.
