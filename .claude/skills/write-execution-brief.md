# SKILL: write-execution-brief

**Purpose:** Produce a complete, self-contained execution WP aligned to current shared repo guidance that a coding agent can pick up and execute without consulting any other document.

**Canonical sources (in authority order):**

1. `docs/ai/codex/WP_DRAFTING_STANDARD.md` — repo-standard for WP structure, validation, stop conditions, and review.
2. `docs/ai/codex/COMPACT_WP_TEMPLATE.md` — compact WP form and context-budget requirements.
3. Active Main/Karl authorization and current repo truth.
4. `prompts/execution_brief.md` — compatibility wrapper only; not canonical by itself.

When producing a WP, follow the shared drafting standard, not the local wrapper prompt.

Before drafting any WP, refresh current WP drafting guidance from `docs/ai/codex/WP_DRAFTING_STANDARD.md` and, when compact delivery is relevant, `docs/ai/codex/COMPACT_WP_TEMPLATE.md`. Do not rely only on memory, prior chat summaries, stale local prompts, or older WPs.

---

## Required Sections (In Order)

Every execution WP must contain all of the following sections. Do not omit any section even if it seems obvious.

### 1. Package Identity

```text
WP id:
Title:
Suggested branch:
Effective base: main
Package class: T0 / T1 / T2 / T3 / T4
Execution mode:
Expected PR title: (must begin with package label followed by `:`)
```

### 2. Authorization Source

Who authorized the package and what was authorized. Name the Main/Karl context, decision, or explicit request.

### 3. Objective

One short paragraph. State the exact deliverable, what exists after execution that did not exist before, and the non-authority posture (what this package does not create authority for).

### 4. Why Now

One short paragraph. State the dependency rationale: required prior merges, packages blocked until this lands, and why no reordering is valid.

### 5. Hard Dependencies

Explicit list:

- Required prior merged PRs or artifacts.
- Required file existence checks.
- Required absence checks (no open conflicting PR on shared files).
- Already-done check: if the objective is already met in current repo state, stop and report instead of duplicating.

### 6. Requirement Compatibility / Impossibility Check

**Mandatory for material dashboard, schema, validator, collector, and renderer
requirements and for protected T3/T4 packages where compatibility is material.
Recommended for all T2+ packages with material semantic change.**

Before implementation, verify each material behavior is compatible with current repo mechanisms and allowed changed-file scope:

| Required behavior | Controlling repo mechanism | Files likely needed | Allowed in this WP? | Compatible? | Action |
|---|---|---:|---:|---:|---|
| `<behavior>` | `<mechanism>` | `<paths>` | yes/no | yes/no | implement / stop / split / ask Main |

Stop before implementation if any row is not compatible under allowed scope. Do not broaden scope silently.

### 7. Preflight

Mandatory isolated-worktree setup. See `docs/ai/codex/WP_DRAFTING_STANDARD.md` §4 for required commands and clean-start-state check.

### 8. Context Budget / Files to Inspect

Five required fields (see `docs/ai/codex/COMPACT_WP_TEMPLATE.md`):

```text
P0 — Read first:
P0 — Read for this package:
P1 — Read only if blocked:
P2 — Do not read / do not touch:
P1 — Search terms if paths changed:
```

P0 is mandatory, P1 is conditional, and P2 is irrelevant or forbidden.

### 9. Scope

Exhaustive list of files to create or modify. Nothing not on this list may be touched.

### 10. Forbidden Scope

Exhaustive list of:

- Forbidden file paths and directories.
- Forbidden behavior and authority changes (no runtime/paper/live/OMS/risk drift, no schema/validator/query changes unless explicitly scoped, etc.).

### 11. Implementation Requirements

Package-specific edits only. Required wording, artifact fields, or doc sections. For code files: function signatures, dataclass fields, invariants. The coding agent should not need to infer anything.

### 12. Validation Requirements

Exact commands and expected evidence, using the package-class validation profile:

- T0 docs/status/comments: scope and docs checks, including `git diff --check`;
  no pytest by default.
- T1 tests/read-only query additions/exact persistence/non-canonical research
  automation: focused and adjacent tests plus relevant validators/integrity; no
  full suite by default.
- T2 schema/validator/contract/query-SQL/broad production code: focused,
  adjacent, affected-contract, validator, and integrity evidence; full suite
  only when blast radius or an active gate requires it.
- T3 canonical crossing/protected writer/dispatch authorization and T4
  runtime/paper-live/OMS/reconciliation/risk/capital: full protected rigor and
  applicable exact-head/Karl gates.
- See `docs/ai/codex/WP_DRAFTING_STANDARD.md` §10 for the full validation profile by class.

Do not require baseline full pytest as a pre-flight gate for T0 docs packages
unless the active package explicitly requires it.

### 13. Stop / Escalation Conditions

Numbered list. Unambiguous conditions: "any forbidden file touched" is valid; "something feels wrong" is not.

Always include:

- open conflicting PR;
- worktree dirty before start;
- forbidden file or path touched;
- validation failure for non-environment reason;
- repo truth contradicts brief scope.

### 14. Final Rebase / GitHub Mergeability Gate

Rebase commands and confirmation that GitHub reports `mergeable=true` before calling the PR merge-ready.

### 15. Final PR Readiness Gate

Before reporting ready-for-review, confirm:

- PR title begins with the package label followed by `:`.
- Active-WP Requirement Traceability checklist is present in final report/status/PR body or clearly referenced, with active-WP requirement, source section, evidence location, and status.
- Required active-WP validation ran unless the active WP explicitly classifies it as optional or not merge evidence.
- Final console report, PR body, status fragment, and project-status pointer agree on validation, draft state, mergeability, blockers, skipped checks, and changed-file scope.
- PR body has no GitHub template placeholders, unchecked template checkboxes, or stale `TBD` / `pending` / `to be added` / `background run` text.
- Status fragment contains the actual PR URL.
- Status fragment validation summary is final.
- Contradiction scan completed for follow-up or blocker-resolution packages: search PR body, status fragment, and changed docs for stale blocked/draft/pending/not-ready/prior-option language. Every hit must be removed or classified before ready-for-review.
- Semantic text audit completed for non-authority packages (see `docs/ai/codex/COMPACT_WP_TEMPLATE.md`).
- GitHub `isDraft=false` and `mergeable=true` for normal non-blocked PRs.

### 16. Draft-State Rule

Normal clean PRs must be opened non-draft (ready for review) unless the active WP explicitly authorizes draft/blocked state. Blocked PRs must keep GitHub draft-state, PR body, and status fragment consistent.

### 17. Commit / PR / Report-Back

```text
Commit message: <message>
PR title: <WP-id: title>
PR body sections: A. Scope, B. Changed files, C. Validation, D. Boundary check, E. PR status
Report-back format: see docs/ai/codex/WP_EXECUTION_REPORT.md
```

When drafting correction or follow-up packages, require the report-back or review to include: paste-ready follow-up prompt, self-diagnosis, whether the issue was preventable, what should have caught it, immediate process change, and whether a durable repo/process/WP-guidance package is needed.

### 18. Manual Steps

State `None` or list exact user steps, timing, optional/required status, and repo dependency effect.

---

## Writing Rules

1. No ambiguity about scope. If a file is not in the explicit allowed list, it is forbidden.
2. Pre-flight commands must be copy-pasteable and runnable as written.
3. Validation gates must produce a machine-readable pass/fail signal.
4. File specs must be complete for code files: every public function, every dataclass field, every invariant.
5. Stop conditions must be unambiguous.
6. Compatibility/impossibility check must be present for material T2+ packages
   and protected T3/T4 packages as specified above.
7. Final PR readiness gate and contradiction scan must be included for follow-up packages.
8. Active-WP Requirement Traceability must be included before ready-for-review.
9. WP drafting must start from refreshed shared guidance, not memory or older packages.

---

## Anti-Patterns to Avoid

- Vague scope ("update as needed", "improve the code").
- Missing forbidden list.
- Gates that depend on external state not present in the validation environment.
- Briefs that require the coding agent to read other documents to understand what to do.
- Calling `prompts/execution_brief.md` canonical — it is a compatibility wrapper only.
- Requiring baseline full pytest as mandatory preflight for T0 docs-only packages.
- Missing compatibility/impossibility check for schema, validator, or dashboard packages.
- Missing contradiction scan for follow-up or blocker-resolution packages.
