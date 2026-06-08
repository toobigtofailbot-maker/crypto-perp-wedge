# Compact Coding-Agent WP Template Guidance

## Scope and non-authority

This document is guidance-only for drafting shorter coding-agent work-package prompts (Claude Code or Codex). It does not replace active WP scope, reduce validation, authorize implementation or tooling, resume WP-S2c-30, apply R1/R2, or create runtime, paper/live, OMS, risk, safe-mode, config, dependency, schema, validator, query-layer, evidence, policy, approval, readiness, lifecycle, promotion/demotion, or downstream authority.

Repo truth and active package scope always win over this guidance. Compact prompts are safe only when they preserve executable scope control.

## When to use this template

Use this template for future Side/coding-agent WPs when stable repo guidance can be referenced instead of repeated. A compact WP must remain executable without guessing.

Do not use compact drafting to omit decisions, protected-boundary facts, validation gates, manual-step requirements, or package-specific stop triggers.

## Source-of-truth requirements

Compact prompts may reference:

- `AGENTS.md`;
- `docs/ai/codex/CODEX_TOKEN_EFFICIENCY.md`;
- `docs/research_pipeline/2026-05-stage2c_workflow_efficiency_operating_model_lock.md`;
- package-specific prior artifacts or docs.

References do not override current merged repo truth. Cached status, memory, summaries, compressed notes, and old handoffs do not replace current branch inspection.

## Minimum WP sections

Every compact WP must include:

- package identity;
- objective;
- why now;
- dependencies and repo-truth checks;
- repo files to inspect;
- allowed changed files;
- forbidden scope;
- implementation requirements;
- validation requirements;
- stop and escalation conditions;
- Codex report-back format;
- next-step authority;
- manual-step disclosure.

## Compact package skeleton

```text
# WP-[id] / WP-S2c-[id] — CODING-AGENT EXECUTION PACKAGE
[Title]

## 1. Package Identity
- Label, title, suggested branch, effective base, package class, execution mode.

## 2. Objective
- One short statement of the exact deliverable and non-authority posture.

## 3. Why Now
- Package-specific reason this is next, including sequencing constraints.

## 4. Dependencies / Repo Truth to Verify
- Refreshed-main preflight.
- Required merged prior PRs/files/artifacts.
- Required absence of conflicting branch/PR, especially `docs/project_status.md` PRs when touched.

## 5. Files to Inspect
- Startup anchors and exact package-relevant files.
- Current diffs/changed files before final report.

## 6. Scope
- Files to create or modify.
- Final changed-file set.
- Any package-specific allowed exceptions.

## 7. Forbidden Scope
- Protected paths and forbidden artifact/code/tooling families.
- Explicit non-authority for runtime, schemas, validators, query layer, configs, data, and dependencies when applicable.

## 8. Implementation Requirements
- Package-specific edits only.
- Required wording, artifact fields, or doc sections.

## 9. Validation Requirements
- Exact commands or validators.
- Integrity views, registry validators, scoped pytest, and full pytest unless a repo-approved validation-tier document changes the requirement.

## 10. Stop / Escalation Conditions
- Dependency failures.
- Scope expansion.
- Validation failure.
- Protected-boundary or authority tension.

## 11. Commit / PR / Report-Back
- Commit message, PR title/body sections, and required report-back sections.
- Required validation counts and changed-file evidence.

## 12. Manual Steps
- State `None` or list exact user steps, timing, optional/required status, repo dependency effect, and what Codex must not do before completion.
```

## What may be referenced instead of repeated

Stable guidance can be referenced rather than pasted when the active WP still states the package-specific effect. Examples:

- repo precedence and startup anchors;
- token-efficiency and context-hygiene rules;
- workflow-efficiency tier model;
- project-status overlap guardrail;
- standard protected-boundary categories;
- standard concise report-back expectations;
- package-specific prior design documents.

Future WPs should be shorter by referencing stable guidance, not by omitting decisions.

## What must remain package-specific

Each WP must still state:

- exact package identity and branch;
- exact objective and why-now rationale;
- hard dependencies and absence checks;
- files to inspect;
- allowed changed-file set;
- forbidden scope and protected-boundary implications;
- implementation requirements;
- validation commands and expected evidence;
- stop triggers;
- report-back format;
- next-step authority;
- manual-step status.

## Required validation block

Compact WPs must not omit refreshed-main preflight, project-status open-PR conflict checks when `docs/project_status.md` is touched, changed-file scope checks, integrity views, registry validators, scoped pytest, or full pytest unless a future repo-approved validation-tier document explicitly changes the rule.

Validation-output summaries are allowed only as reporting compression. They cannot replace command execution. `v_integrity_*: clean (N)` is allowed only when all discovered integrity views actually ran with JSON output and returned `[]`.

## Required stop-condition block

Every compact WP must stop on:

- failed dependency or refreshed-main preflight;
- conflicting open branch or PR;
- another open PR touching `docs/project_status.md` when the package edits it;
- changed files outside the allowed set;
- required edits outside package scope;
- validation failure;
- integrity rows;
- protected runtime, paper/live, OMS, risk, safe-mode, config, dependency, schema, validator, query-layer, data, or implementation boundary questions;
- wording that weakens repo truth, validation, forbidden scope, protected boundaries, or package-specific authority;
- package-specific stop triggers.

## Required report-back block

Every compact WP must require a report-back that states:

- branch and base;
- repo-truth discovery;
- delivered changes;
- validation results with concrete counts where applicable;
- changed-file and untracked-file scope;
- boundary and forbidden-scope check;
- manual steps;
- next-step authority;
- PR/push status;
- ready-for-review decision.

## Docs-only package notes

Docs-only compact WPs may use concise implementation wording, but they still need exact changed-file scope, project-status conflict checks when status is touched, integrity views, registry validators where repo convention requires them, scoped pytest, and full pytest unless later repo truth changes validation tiers.

Docs-only packages do not create implementation, evidence, runtime, policy, approval, readiness, lifecycle, promotion/demotion, or downstream authority unless the active WP explicitly and validly says otherwise.

## Research artifact package notes

Research artifact WPs must remain explicit about artifact IDs, source artifacts, exact segment, expected count movement, validators, query/integrity checks, trial-log effects, and downstream non-authority.

Compact wording must not hide REP, OL, REC, EXP, LCH, registry, schema, validator, query-layer, lifecycle, readiness, or evidence-authority facts.

## Helper/tooling package notes

Helper or tooling WPs require explicit package authority. They must state the helper boundary, default behavior, inputs/outputs, write behavior, validation, no-runtime-influence posture, and protected-path non-contact.

This compact template does not implement helpers, wrappers, indexes, memory files, automation, RTK/RTX/manual compression, diff-summary helpers, validation wrappers, or code-index tooling. Those require later package scope and validation.

## Manual-step disclosure

Every future WP must state whether manual user steps are required.

If manual steps are required, the WP must say:

- what the user must do;
- when the user must do it;
- whether the step is optional or required;
- whether it creates a repo dependency;
- what Codex must not do without the manual step.

For packages involving external tools such as RTK/RTX or manual command compression, Codex must not assume the user has installed or configured them. Optional manual compression creates no repo dependency unless separately approved, validation still runs normally, and compressed output is report assistance only.

For WP-S2c-29b, manual steps are: None.

## Forbidden compression

Compact prompts must not omit or weaken:

- repo-truth inspection;
- refreshed-main preflight;
- changed-file inspection;
- allowed changed-file set;
- forbidden runtime/protected boundaries;
- integrity views;
- registry validators;
- scoped pytest;
- full pytest unless a future repo-approved validation-tier document changes it;
- project-status overlap checks when status is touched;
- package-specific dependencies;
- package-specific stop triggers;
- report-back requirements;
- manual-step disclosure.

Compact prompts must not imply that summaries, compressed logs, cached status, memory, or prior chat can replace command execution or current merged repo truth.

## Reviewer checklist

Reviewers should verify:

- the WP is executable without guessing;
- package-specific scope remains explicit;
- referenced guidance is stable and applicable;
- changed-file set is exact;
- protected-boundary facts are visible;
- validation commands are still required;
- stop triggers are package-specific and complete;
- manual steps are stated as `None` or fully disclosed;
- no helper/tooling, R1/R2, H-006, WP-S2c-30, Path B, runtime, policy, readiness, lifecycle, promotion/demotion, or downstream authority is silently introduced.
