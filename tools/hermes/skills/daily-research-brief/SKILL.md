---
name: daily-research-brief
description: Produce a daily evidence-linked project brief.
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [research, reporting, daily]
    category: research
    requires_toolsets: [mcp-project-evidence]
---

# Daily Research Brief

## Procedure

1. Start with `project_evidence_manifest` and `project://status`.
2. Read only evidence needed for changes, blockers, failures, and open questions.
3. Use predeclared queries only when their complete input references are shown.
4. Format: repo SHA; FACT; INFERENCE; BLOCKER/FAILURE; OPEN QUESTION; sources.
5. Cite URI/query, path, artifact SHA-256, and repo SHA for every load-bearing
   project fact.
6. If evidence cannot resolve, state UNKNOWN. Never fill gaps from memory.

## Authority boundary

The brief is non-authoritative. It cannot create promotion/readiness, approve a
candidate, mutate an artifact, schedule work, or change dependencies. Do not
use project-readiness or execution language unless quoting an existing repo fact
with its exact source and clearly labeling it as a quotation.
This skill cannot self-enable any broader capability.

## Verification

No uncited project facts, fabricated science, or unsupported status transitions
appear in the brief.
