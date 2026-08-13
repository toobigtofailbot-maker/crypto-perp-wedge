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

Before drafting a WP, refresh `docs/ai/codex/WP_DRAFTING_STANDARD.md` and this file when compact delivery is relevant. Do not rely only on memory, prior chat summaries, stale local prompts, or older WPs.

## Context Budget / Files to Inspect

Every compact WP must include a `Context Budget / Files to Inspect` section with these required fields:

```text
P0 — Read first:
P0 — Read for this package:
P1 — Read only if blocked:
P2 — Do not read / do not touch:
P1 — Search terms if paths changed:
```

P0 is mandatory context, P1 is conditional context used when dependency or
contradiction analysis requires it, and P2 is irrelevant or forbidden for the
package.

The Context Budget is package-specific. It may use file counts, line ranges, named sections, or search terms where useful, but it is not a global numeric cap and cannot override repo-truth inspection, validation, changed-file inspection, or stop-condition investigation.

## Compact WP Default

Use compact WP form by default when stable repo guidance can be referenced instead of repeated, but do not omit package-specific objective, dependencies, allowed files, forbidden files, validation, stop conditions, report-back, manual steps, or next-step authority.

## Delta from Defaults

Every compact WP should state what differs from standard guidance:

- additional files to inspect;
- narrower or broader validation;
- special forbidden paths;
- manual steps;
- package-specific stop triggers;
- unusual report-back requirements.

The `Delta from defaults` section must not be used to skip required startup anchors, validation, or protected-boundary checks.

## Minimum WP sections

Every compact WP must include:

- package identity;
- objective;
- why now;
- dependencies and repo-truth checks;
- `Context Budget / Files to Inspect` with all five required fields;
- repo files to inspect;
- allowed changed files;
- forbidden scope;
- implementation requirements;
- validation requirements;
- stop and escalation conditions;
- Codex report-back format;
- next-step authority;
- manual-step disclosure;
- `Delta from defaults` (when using compact WP format).

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
- State the T0-T4 blast-radius tier from `docs/ai/codex/VALIDATION_POLICY.md`.
- Name mandatory focused tests, adjacent tests, relevant validators/integrity
  views, and whether broad/full-suite evidence is required and why.
- Full suite only when the tier, blast radius, milestone/release boundary,
  protected gate, or active package requires it.

## 10. Stop / Escalation Conditions
- Dependency failures.
- Scope expansion.
- Validation failure.
- Protected-boundary or authority tension.

## 11. Commit / PR / Report-Back
- Commit message, PR title/body sections, and required report-back sections.
- Required validation counts and changed-file evidence.

## 11a. Final PR Readiness Gate
Before reporting ready-for-review, confirm:
- PR title begins with the package label followed by `:`.
- PR body contains no GitHub template placeholders, unchecked template checkboxes, or stale `TBD` / `pending` / `to be added` / `background run` text.
- Status fragment contains the actual PR URL.
- Status fragment validation summary is final (no pending/background language; skipped validation marked `Not run; not used as merge evidence.`).
- Changed-file scope was verified after final status-fragment metadata updates.
- Semantic text audit completed when package scope includes non-authority, anti-ranking, no-readiness, no-promotion, no-execution, or dashboard-as-non-authority constraints (see audit block below).
- GitHub reports PR mergeable/clean.

## 12. Manual Steps
- State `None` or list exact user steps, timing, optional/required status, repo dependency effect, and what Codex must not do before completion.
```

## Requirement Compatibility / Impossibility Check

**Mandatory for material dashboard, schema, validator, collector, and renderer requirements and for protected T3/T4 packages where compatibility is material. Recommended for all T2+ packages with material semantic change.**

Before implementation, include a compatibility matrix in the compact WP:

```text
| Required behavior | Controlling repo mechanism | Files likely needed | Allowed in this WP? | Compatible? | Action |
|---|---|---:|---:|---:|---|
| <behavior> | <schema/validator/collector/renderer/test/doc> | <paths> | yes/no | yes/no | implement / stop / split / ask Main |
```

If any required behavior is not compatible under allowed scope, the WP must either split a prior unblock package, explicitly accept the limitation as known debt, or define a stop condition. Do not broaden scope silently.

## Follow-Up / Blocker Resolution Contradiction Scan

For follow-up WPs and blocker-resolution packages, the compact WP must include the contradiction scan requirement in its final PR readiness gate section:

When a follow-up resolves a blocker or changes earlier package scope, the coding agent must search PR body, status fragment, and changed docs for stale claims from the prior state:

```text
blocked, draft, decision required, pending, to be added, background run, not ready,
no schema change, no validator change, old error text, prior Option A/B language, TBD
```

Every hit must be removed or classified (removed / historical note / required reference) before the PR is reported ready-for-review.

When Side/Main review determines a follow-up is needed, the review/report-back must include a paste-ready follow-up prompt, self-diagnosis, whether the issue was preventable, what should have caught it, immediate process change, and whether a durable repo/process/WP-guidance package is needed. If the failure was preventable or likely to recur, Side/Main should draft or request a narrow improvement WP after the immediate blocker is resolved.

## Active-WP Requirement Traceability Gate

Before reporting ready-for-review, reconcile the final PR against the active WP.

The final report/status/PR body must include or reference a compact checklist with:

- active-WP requirement;
- source section in the active WP;
- evidence location;
- status: satisfied / not applicable / blocked.

Required validation from the active WP cannot be skipped or downgraded to "Not run; not used as merge evidence" unless the active WP explicitly says that validation is optional or not used as merge evidence.

If final console report, PR body, status fragment, or project-status pointer disagree on validation, draft state, mergeability, blockers, skipped checks, or changed-file scope, the PR is not ready.

If a required item is missing, report not-ready and include a paste-ready follow-up prompt.

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

Compact WPs must not omit refreshed-main preflight, project-status open-PR
conflict checks when `docs/project_status.md` is touched, changed-file scope
checks, or the focused, adjacent, validator, integrity, and broad/full-suite
evidence required by the package's T0-T4 tier and active gate.

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

T0 docs-only compact WPs may use concise implementation wording, but they still
need exact changed-file scope, project-status conflict checks when status is
touched, docs checks where supported, package-required targeted validators, and
protected-boundary review. Pytest and unrelated registry/query integrity are not
required by default.

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
- focused and adjacent tests required by the tier;
- relevant integrity views and registry validators required by the tier;
- broad/full pytest when the tier, blast radius, milestone/release boundary,
  protected gate, or active package requires it;
- project-status overlap checks when status is touched;
- package-specific dependencies;
- package-specific stop triggers;
- report-back requirements;
- manual-step disclosure.

Compact prompts must not imply that summaries, compressed logs, cached status, memory, or prior chat can replace command execution or current merged repo truth.

## Semantic Text Audit for Non-Authority Packages

When a package's changed text includes non-authority, anti-ranking, no-readiness, no-promotion, no-execution, or dashboard-as-non-authority constraints, search changed docs, fixtures, and report text for terms such as:

```text
best, highest, lowest, fewest, winner, top, leaderboard, rank, selected, recommended,
recommendation, readiness, ready_for, promotion, approved, execute, trade
```

Every hit must be classified as:

- invalid negative fixture or test (expected to be rejected by the validator);
- explicit forbidden-wording documentation (describing what is prohibited);
- neutral reference required by the package; or
- drift requiring rewording.

Valid descriptive output should be population-level unless row-level emphasis is explicitly authorized. Keep this as guidance; do not introduce a script requirement.

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
- no helper/tooling, R1/R2, H-006, WP-S2c-30, Path B, runtime, policy, readiness, lifecycle, promotion/demotion, or downstream authority is silently introduced;
- final PR readiness gate was applied: PR body is placeholder-free, status fragment has the actual PR URL, validation summary is final, semantic audit completed for non-authority packages.
