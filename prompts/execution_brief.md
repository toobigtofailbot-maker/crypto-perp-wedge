# Execution Brief Wrapper

This file is a compatibility wrapper only. It is not canonical by itself.

**Canonical sources for WP drafting:**

- `docs/ai/codex/WP_DRAFTING_STANDARD.md` — the repo-standard for coding-agent WP drafting, validation, stop conditions, and review.
- `docs/ai/codex/COMPACT_WP_TEMPLATE.md` — compact WP form for future Side/coding-agent packages.
- Active Main/Karl authorization and current repo truth always override templates.

Before drafting a WP, refresh `docs/ai/codex/WP_DRAFTING_STANDARD.md` and, when compact delivery is relevant, `docs/ai/codex/COMPACT_WP_TEMPLATE.md`. Do not rely only on memory, prior chat summaries, stale local prompts, or older WPs.

---

## Modern WP Skeleton (Quick Reference)

Every execution WP must include all of the following sections. For full requirements see `docs/ai/codex/WP_DRAFTING_STANDARD.md`.

### 1. Package Identity

- WP id, title, suggested branch, effective base, package class, execution mode.
- Expected PR title: must begin with the package label followed by `:`.

### 2. Authorization Source

- Who authorized the package and what was authorized.

### 3. Objective

- Exact deliverable and non-authority posture.

### 4. Why Now

- Dependency rationale; required prior merges; packages blocked until this one lands.

### 5. Hard Dependencies

- Required prior merges; required file/artifact existence checks; required absence checks.

### 6. Requirement Compatibility / Impossibility Check

Before implementation, verify each material behavior is compatible with current repo mechanisms and allowed changed-file scope:

| Required behavior | Controlling repo mechanism | Files likely needed | Allowed in this WP? | Compatible? | Action |
|---|---|---:|---:|---:|---|
| `<behavior>` | `<schema/validator/collector/renderer/test/doc>` | `<paths>` | yes/no | yes/no | implement / stop / split |

Stop before implementation if any required behavior is not compatible under allowed scope. Do not broaden scope silently.

### 7. Preflight

- Mandatory isolated-worktree setup commands (see `docs/ai/codex/WP_DRAFTING_STANDARD.md` §4).
- Required clean start state: branch = WP branch, `git status --short` = clean.

### 8. Context Budget / Files to Inspect

Five required fields:

```text
P0 — Read first:
P0 — Read for this package:
P1 — Read only if blocked:
P2 — Do not read / do not touch:
P1 — Search terms if paths changed:
```

P0 is mandatory, P1 is conditional, and P2 is irrelevant or forbidden.

### 9. Scope

- Files to create or modify (exhaustive list).

### 10. Forbidden Scope

- Forbidden files/paths; forbidden behavior/authority.

### 11. Implementation Requirements

- Package-specific edits only.
- Required wording, artifact fields, or doc sections.

### 12. Validation Requirements

- Exact commands or validators.
- T0 docs/process: T0 scope/docs checks; no pytest by default.
- T1: focused and adjacent tests plus relevant validators/integrity; no full
  suite by default.
- T2: affected-contract, focused, adjacent, validator, and integrity evidence;
  full suite only when blast radius or the active package gate requires it.
- T3/T4: full protected rigor and applicable exact-head/human gates.
- Use `docs/ai/codex/VALIDATION_POLICY.md` and
  `docs/ai/codex/WP_DRAFTING_STANDARD.md` §10 for the authoritative details.

### 13. Stop / Escalation Conditions

- Dependency failures; scope expansion; validation failure; protected-boundary tension.

### 14. Final Rebase / GitHub Mergeability Gate

- Rebase onto `origin/main`.
- Rerun required validation.
- Confirm GitHub `mergeable=true`.

### 15. Final PR Readiness Gate

Before reporting ready-for-review, confirm:

- PR title begins with the package label followed by `:`.
- Active-WP Requirement Traceability checklist is present in final report/status/PR body or clearly referenced, with active-WP requirement, source section, evidence location, and status.
- Required active-WP validation ran unless the active WP explicitly classifies it as optional or not merge evidence.
- Final console report, PR body, status fragment, and project-status pointer agree on validation, draft state, mergeability, blockers, skipped checks, and changed-file scope.
- PR body has no GitHub template placeholders, unchecked template checkboxes, or stale `TBD` / `pending` / `to be added` / `background run` text.
- Status fragment contains the actual PR URL.
- Status fragment validation summary is final.
- Contradiction scan completed for follow-up/blocker-resolution packages.
- Semantic text audit completed for non-authority packages.
- GitHub reports PR `mergeable=true` and `isDraft=false` for normal (non-blocked) PRs.

### 16. Draft-State Rule

- Normal clean PRs must be opened non-draft (ready for review) unless the active WP explicitly authorizes draft/blocked state.
- Blocked PRs must keep GitHub draft-state, PR body, and status fragment consistent.

### 17. Commit / PR / Report-Back

- Commit message; PR title; PR body sections (A. Scope, B. Changed files, C. Validation, D. Boundary check, E. PR status).
- Report-back format: see `docs/ai/codex/WP_EXECUTION_REPORT.md`.

### 18. Manual Steps

- State `None` or list exact user steps, timing, optional/required status, and repo dependency effect.

---

## Authority Reference

Full WP drafting standard: `docs/ai/codex/WP_DRAFTING_STANDARD.md`
Compact WP guidance: `docs/ai/codex/COMPACT_WP_TEMPLATE.md`
Report-back shapes: `docs/ai/codex/WP_EXECUTION_REPORT.md`
