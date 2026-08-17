---
name: prepared-project-plan
description: Prepare one hash-stable inert human-review plan.
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [prepare, proposal, readonly]
    category: research
    requires_toolsets: [mcp-project-evidence]
---

# Prepared Project Plan

## When to use

Use only when a human asks for one of the seven H2.5 prepared payload types.
The source must be a real compatible H2 proposal already present in the fixed
proposal outbox. Prepared content is not authority.

## Procedure

1. Read `project_evidence_manifest` and bind the exact prepared repo SHA.
2. Select the exact source H2 proposal ID supplied by the human or by prior
   visible proposal-tool output. Never invent a proposal ID or parent hash.
3. Re-read every evidence URI needed for the prepared FACTs. Copy the current
   exact repo SHA, path, and SHA-256 into ordered anchors. Research Memory and
   dependency/security watch observations are hints or advisory context only;
   neither may be a direct FACT anchor.
4. Separate FACT, INFERENCE, and OPEN QUESTION. Use `UNKNOWN` where exact repo
   evidence does not support a value.
5. Fill one strict prepared body, exact hard budget and timeout, any applicable
   count/quantity bound, outputs, validation, and rollback/stop conditions.
6. Preserve the source A0/A1/A2 class exactly. For A0, set
   `permanent_non_executable=true` and `protected_human_gate_only=true`.
7. Keep all authority flags inert: no self-approval, direct execution, standing
   authority, approval token, broker, dispatch, or automatic consumer.
8. Call `submit_prepared_payload` once. On rejection, do not weaken validation,
   change class, fabricate evidence, or create a substitute parent.

## Type boundaries

- Strategy Lab is a future lab-only draft with no candidate, promotion, or GO.
- Search Governor Campaign is a legal-search draft with no holdout access,
  Governor call, or winner semantics.
- Codex Work Package creates no task, branch, commit, push, or pull request.
- Prefect Workflow creates no deployment and invokes no flow or task.
- Bounded Diagnostic is a read-only diagnostic concept and executes nothing.
- Data Hydration performs no network access and hydrates nothing.
- Dependency Maintenance installs or updates nothing. Watch observations remain
  advisory and cannot become FACT evidence.

## Authority boundary

This skill can only read exact Project-Evidence and submit one validated inert
prepared record to the existing outbox. It cannot approve, mint a token, call a
broker, dispatch, invoke external systems, write project or canonical evidence,
run diagnostics, hydrate data, install dependencies, trade, or enable tools.
It cannot self-enable broader authority. A0 remains permanently proposal-only.
H3 and H4 are not started.

## Verification

Accept success only when the tool returns the source proposal ID and content
hash, prepared payload SHA-256, exact repo SHA and class, `not_authority=true`,
all eligibility flags false, and `automatic_consumers=[]`. Otherwise report
`UNKNOWN` and take no follow-up action.
