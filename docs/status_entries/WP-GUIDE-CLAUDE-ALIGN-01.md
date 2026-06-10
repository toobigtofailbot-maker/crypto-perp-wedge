# WP-GUIDE-CLAUDE-ALIGN-01 — Align Claude local prompts with shared guidance

- **Package class:** T1 docs/process/guidance
- **Branch:** claude/practical-neumann-ca75f4
- **PR:** [#426](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/426)
- **Scope summary:** Aligns Claude-specific local prompts and skills with the current shared coding-agent guidance after F5A/F5B/F5C exposed repeated finality and stale-template drift. Edits stale local files in place; does not delete any file. Adds requirement-compatibility/impossibility gate and follow-up blocker-resolution contradiction scan to shared guidance.

---

## Inspection / Edit-vs-Delete Decision

Files inspected:

- `.claude/README.md` — retained and updated; was missing wrapper-only discipline and final-readiness checks.
- `.claude/skills/write-execution-brief.md` — retained and updated; was calling `prompts/execution_brief.md` canonical.
- `.claude/skills/review-report-back.md` — retained and updated; had stale Gate 8/DSR/WP-1b checks and missing final-readiness gate.
- `prompts/execution_brief.md` — retained and replaced; was presenting itself as a canonical template rather than a wrapper.
- `prompts/report_back.md` — retained and replaced; had only a weak generic `[COMPLETE | BLOCKED | FAILED]` / `[YES | NO]` shape with no PR metadata, draft-state check, or contradiction scan.
- `prompts/pr_review.md` — retained and replaced; contained WP-1b-specific backtest/evaluation/Gate 8/DSR/promotion-gates checklists with no applicability to current WPs.

Files not deleted: all prompt and `.claude` files retained as in-place compatibility wrappers. Deletion risks broken references from `.claude/README.md` local-asset list.

Future cleanup candidates: none identified at this time.

---

## Changed Files

Modified:

- `.claude/README.md`
- `.claude/skills/write-execution-brief.md`
- `.claude/skills/review-report-back.md`
- `prompts/execution_brief.md`
- `prompts/report_back.md`
- `prompts/pr_review.md`
- `docs/ai/codex/WP_DRAFTING_STANDARD.md`
- `docs/ai/codex/WP_EXECUTION_REPORT.md`
- `docs/ai/codex/COMPACT_WP_TEMPLATE.md`
- `docs/project_status.md`

Created:

- `docs/status_entries/WP-GUIDE-CLAUDE-ALIGN-01.md` (this file)

---

## Guidance Changes

- **`.claude/README.md`:** Added wrapper-only discipline (`.claude/*` and `prompts/*` cannot override shared guidance, repo truth, `AGENTS.md`, or `docs/ai/codex/*`). Replaced the stale "Use `prompts/report_back.md` unless..." line with a three-level precedence rule (active WP → `WP_EXECUTION_REPORT.md` → `prompts/report_back.md` as fallback). Added final-readiness discipline block (isDraft, mergeable, PR body placeholder scan, status-fragment PR URL finality, contradiction scan, semantic audit). Added draft-state consistency discipline.

- **`prompts/report_back.md`:** Fully replaced stale generic `[COMPLETE | BLOCKED | FAILED]` / `[YES | NO]` template. Now a compatibility wrapper pointing to `docs/ai/codex/WP_EXECUTION_REPORT.md`. Includes compact A–E and expanded A–I shapes, final PR readiness evidence fields (isDraft, mergeable, placeholder scan, status-fragment URL, contradiction scan result), expanded shape trigger list, and paste-ready follow-up prompt requirement when not merge-ready.

- **`prompts/execution_brief.md`:** Fully replaced stale canonical-template language. Now a compatibility wrapper pointing to `docs/ai/codex/WP_DRAFTING_STANDARD.md` and `docs/ai/codex/COMPACT_WP_TEMPLATE.md`. Includes a modern WP skeleton with compatibility/impossibility check (§6), final PR readiness gate (§15), draft-state rule (§16), and contradiction scan.

- **`prompts/pr_review.md`:** Fully replaced WP-1b-specific content (backtest/evaluation/Gate 8/DSR/promotion-gates/CCXT/test-name checks). Now a current merge-readiness review checklist aligned to `docs/ai/codex/WP_DRAFTING_STANDARD.md` and `docs/ai/codex/WP_EXECUTION_REPORT.md`. Contains 8 review sections covering PR metadata (with actual isDraft/mergeable), scope, validation, semantic fit, boundary, authority, final readiness gate (with contradiction scan and semantic audit), and decision (with paste-ready follow-up prompt for REQUEST CHANGES).

- **`.claude/skills/write-execution-brief.md`:** Removed stale "see `prompts/execution_brief.md` for the canonical template" wording. Rewritten with `docs/ai/codex/WP_DRAFTING_STANDARD.md` and `docs/ai/codex/COMPACT_WP_TEMPLATE.md` as canonical sources. Added §6 (Requirement Compatibility / Impossibility Check), §15 (Final PR Readiness Gate with contradiction scan), §16 (Draft-State Rule). Removed stale baseline-full-pytest-as-mandatory-preflight for T1 packages. Added anti-patterns for missing compatibility check and contradiction scan.

- **`.claude/skills/review-report-back.md`:** Removed stale Gate 8 / DSR / WP-1b / "existing prompt templates not modified" / "existing tests not modified" checks. Added actual PR metadata requirements (isDraft, mergeable, PR URL, branch/base). Added final PR readiness gate step (Step 5) covering placeholder scan, status-fragment URL, isDraft, mergeable, contradiction scan for follow-up packages, and semantic audit for non-authority packages. Added decision rule: when not merge-ready, provide paste-ready follow-up prompt and self-diagnosis. Clarified that Claude Code cannot approve/merge its own PRs.

- **`docs/ai/codex/WP_DRAFTING_STANDARD.md`:** Added §15 (Requirement Compatibility / Impossibility Check) — mandatory for dashboard/schema/validator/collector/renderer packages, recommended for all T3. Added §16 (Follow-Up / Blocker Resolution Contradiction Scan) — mandatory for follow-up WPs. Renumbered old §15 (Final PR Readiness Gate) to §17 and old §16 (Future WP Reference Rule) to §18.

- **`docs/ai/codex/WP_EXECUTION_REPORT.md`:** Added "Draft-State Consistency Rule" section requiring actual GitHub `isDraft` in final readiness evidence and consistency across GitHub state, PR body, and status fragment. Added "Follow-Up / Blocker Resolution Contradiction Scan" section requiring the contradiction scan in report-backs for follow-up packages. Added "If Not Merge-Ready" section requiring paste-ready follow-up prompt.

- **`docs/ai/codex/COMPACT_WP_TEMPLATE.md`:** Added "Requirement Compatibility / Impossibility Check" section with required matrix format. Added "Follow-Up / Blocker Resolution Contradiction Scan" section for compact WPs.

---

## Validation Summary

```text
git status --short: clean (no unexpected files)
git diff --check: clean
git diff --name-only origin/main...HEAD: 11 files within allowed scope
Stale-term audit: see Stale-Template Audit section below
python -m tools.registry.validate_result_populations: Not run; not used as merge evidence (T1 docs package).
python -m tools.research_query.run --list-views: Not run; not used as merge evidence (T1 docs package).
python tools/dev/diff_scope_summary.py: Not run; not used as merge evidence (T1 docs package).
Full pytest: Not run; not required for T1 docs/process/guidance package.
```

---

## Stale-Template Audit

Search terms: `canonical template`, `WP-1b`, `Ready For Merge`, `existing prompt templates not modified`, `existing tests not modified`, `Gate 8`, `DSR`, `promotion gates`, `[YES | NO]`, `[COMPLETE | BLOCKED | FAILED]`

Files scanned: `.claude/README.md`, `.claude/skills/write-execution-brief.md`, `.claude/skills/review-report-back.md`, `prompts/execution_brief.md`, `prompts/report_back.md`, `prompts/pr_review.md`

Results:

- `WP-1b`: removed from `prompts/pr_review.md` (was in footer `*Generated by prompts/pr_review.md — WP-1b execution review*`). New footer aligns to current shared guidance.
- `[YES | NO]`: removed from `prompts/report_back.md` (was the sole ready-for-merge evidence marker). Replaced with full final readiness evidence fields.
- `[COMPLETE | BLOCKED | FAILED]`: removed from `prompts/report_back.md`. Report-back shape now follows `docs/ai/codex/WP_EXECUTION_REPORT.md`.
- `Gate 8` / `DSR` / `promotion gates` / `existing prompt templates not modified` / `existing tests not modified`: removed from `.claude/skills/review-report-back.md` and `prompts/pr_review.md`.
- `canonical template` / `follow this template exactly`: removed from `.claude/skills/write-execution-brief.md` (was pointing to `prompts/execution_brief.md` as canonical).
- `Ready For Merge`: not found as a stale header; `prompts/report_back.md` previously had it as a standalone section with `[YES | NO]`, now replaced with full final readiness evidence.

No stale terms remain in an instructional position. All removals verified in replaced file contents.

---

## Boundary Summary

- docs/process/guidance only.
- No helper/tooling/CI implementation.
- No validation weakening.
- No dashboard implementation.
- No schema/validator/test changes.
- No prompt deletion.
- No runtime/paper/live/OMS/risk/protected-path changes.
- No code changes.
- No data artifact changes.

---

## Merge Status

PR: [#426](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/426) — open, non-draft, `mergeable: MERGEABLE`. Ready for review.

---

## Next Dependency / Runway Note

This package is guidance-only. It does not replace F5C execution or review. After this package merges, future Claude Code WPs should be less likely to fall back to stale local templates. If Claude still produces draft/PR-body/status-fragment mismatch after this merge, the next escalation should be tool-operation specific rather than repo-guidance specific.
