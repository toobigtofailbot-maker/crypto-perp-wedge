# Report-Back Wrapper

This file is a compatibility wrapper only. It is not the authority for report-back format.

**Precedence:**

1. Active WP report-back format wins if the WP specifies one.
2. If the active WP is silent, use `docs/ai/codex/WP_EXECUTION_REPORT.md` as the authority.
3. This file provides a fallback compact shape for reference only.

---

## Default Compact Report-Back

Use this compact shape by default for clean T0 packages and clean
low-semantic-risk T1 packages when the active WP specifies no stricter format:

```text
A. Scope
B. Changed files
C. Validation
D. Boundary check
E. PR status / decision
```

Each section must be concrete and audit-friendly:

- A. State what changed and what did not change.
- B. List exact created and modified files.
- C. State commands run, pass/fail result, and short counts. Do not paste full passing logs.
- D. Confirm protected paths remained untouched and no forbidden-scope files were touched.
- E. State branch, PR number/URL, actual PR title, GitHub `isDraft`, GitHub `mergeable`, and whether the PR is ready for review.

---

## Expanded Report-Back Shape

Use the expanded shape when any of the following apply:

- validation failed or was skipped;
- GitHub mergeability is not clean;
- scope differs from the expected changed-file list;
- forbidden or protected files were touched;
- repo truth changed the package scope;
- manual recovery, rebase, detached HEAD, or conflict resolution occurred;
- the package is T2, T3, or T4 and has material semantic risk.

```text
A. Branch / base
B. Repo-truth discovery
C. Delivered changes
D. Validation results
E. Failed or skipped validation detail
F. Forbidden-scope check
G. PR / push status
H. Open escalations
I. Ready for review
```

---

## Final PR Readiness Evidence

Include these fields in section E (compact) or G (expanded) before reporting ready-for-review:

- Actual PR title (must begin with the package label followed by `:`).
- GitHub `isDraft`: must be `false` for normal non-blocked PRs.
- GitHub `mergeable`: must be clean/true.
- Active-WP Requirement Traceability: include or reference a compact checklist with active-WP requirement, source section, evidence location, and status of satisfied / not applicable / blocked.
- Active-WP required validation: required commands ran unless the active WP explicitly classifies them as optional or not merge evidence.
- Consistency check: final console report, PR body, status fragment, and project-status pointer agree on validation, draft state, mergeability, blockers, skipped checks, and changed-file scope.
- PR body placeholder scan: no GitHub template placeholders, unchecked template checkboxes, or stale `TBD` / `pending` / `to be added` / `background run` text.
- Status-fragment PR URL: must be the actual PR URL, not a placeholder.
- Status-fragment validation finality: validation summary is final; skipped validation marked `Not run; not used as merge evidence.`
- Contradiction scan result: when a follow-up resolves a prior blocker, confirm stale blocked/draft/pending/not-ready/prior-option language was removed from PR body, status fragment, and changed docs.
- Semantic audit result: required for non-authority packages (see `docs/ai/codex/COMPACT_WP_TEMPLATE.md`).

---

## If Not Merge-Ready

If the PR is not merge-ready, the report-back must include:

- exact reason the PR is not ready;
- a paste-ready follow-up prompt that resolves the blocker;
- self-diagnosis, whether the issue was preventable, what should have caught it, immediate process change, and whether a durable repo/process/WP-guidance package is needed.

---

## Authority Reference

Full tier-aware report-back guidance lives in `docs/ai/codex/WP_EXECUTION_REPORT.md`.
