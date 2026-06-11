# PR Merge-Readiness Review Checklist

This file is a compatibility wrapper aligned to `docs/ai/codex/WP_DRAFTING_STANDARD.md` and `docs/ai/codex/WP_EXECUTION_REPORT.md`. The former WP-1b-specific content (backtest/evaluation/Gate 8/DSR/promotion-gates checks) has been removed. Use this checklist for any current WP merge-readiness review.

---

## Section 1 — PR Metadata

- **PR Title:**
- **Package label prefix present** (title begins with `WP-<id>:` or similar):
- **Branch:**
- **Base:**
- **Actual `isDraft`** (from `gh pr view --json isDraft`):
- **Actual `mergeable`** (from `gh pr view --json mergeable`):
- **PR URL:**
- **Status fragment URL / path:**

---

## Section 2 — Scope

Verify changed files match the active WP's allowed scope.

```powershell
git diff --name-only origin/main...HEAD
```

| Changed file | In WP allowed scope? | Notes |
|---|---|---|
| _(paste diff output)_ | | |

- [ ] All changed files are in the WP's allowed scope.
- [ ] No forbidden files touched (runtime, paper/live, OMS, risk, schemas, validators, tests, tools, scripts, configs, data, CI unless explicitly allowed by active WP).
- [ ] No untracked or generated outputs committed.

**BLOCKING** — any scope violation must be corrected before merge.

---

## Section 3 — Validation

- [ ] Package-required validation commands ran.
- [ ] All required commands passed, or failures are correctly classified.
- [ ] Skipped or unavailable validation is explicitly marked `Not run; not used as merge evidence.` or classified with exact environment-only failure details.
- [ ] No real validation failure is hidden or reclassified as environment-only without justification.

Paste validation evidence or summary:

```text
<validation output / counts>
```

**BLOCKING** — any unclassified validation failure blocks merge.

---

## Section 4 — Semantic Fit

- [ ] Objective stated in the WP is satisfied by the changed files.
- [ ] No architecture redesign outside WP scope.
- [ ] No stale blocked/draft/pending claims in PR body or status fragment.
- [ ] No placeholders, unchecked template checkboxes, or `TBD` / `pending` / `to be added` / `background run` text remaining in PR body or status fragment.
- [ ] Active-WP Requirement Traceability checklist exists or is clearly referenced, with active-WP requirement, source section, evidence location, and satisfied / not applicable / blocked status.
- [ ] Required active-WP validation was not skipped or downgraded unless the active WP explicitly permits it.

---

## Section 5 — Boundary Check

- [ ] No protected runtime/paper/live/OMS/risk path changes.
- [ ] No unauthorized schema/validator/query-layer/artifact/data changes.
- [ ] No dependency additions unless explicitly scoped by active WP.
- [ ] No data files committed (Parquet, ZIP, CSV) unless explicitly scoped.

---

## Section 6 — Authority Check

- [ ] No ranking, recommendation, readiness, promotion, or execution authority introduced unless explicitly scoped by active WP.
- [ ] Non-authority packages include appropriate non-authority / display-only language where required.

For non-authority packages, verify semantic text audit was completed (search for terms such as `best`, `highest`, `winner`, `recommended`, `readiness`, `promotion`, `approved`, `execute`, `trade`). Each hit must be classified as a fixture negative, forbidden-wording doc, neutral required reference, or drift requiring rewording.

---

## Section 7 — Final Readiness Gate

- [ ] PR body placeholder scan: no GitHub template placeholders, unchecked template checkboxes, or stale pending/TBD text.
- [ ] Status fragment contains the actual PR URL (not `TBD` or `pending`).
- [ ] Status fragment validation summary is final.
- [ ] Contradiction scan completed (for follow-up or blocker-resolution packages): stale blocked/draft/not-ready/prior-option language removed from PR body, status fragment, and changed docs.
- [ ] Final console report, PR body, status fragment, and project-status pointer agree on validation, draft state, mergeability, blockers, skipped checks, and changed-file scope.
- [ ] GitHub `isDraft: false` for normal non-blocked PRs (or draft state is consistent with blocked status everywhere).
- [ ] GitHub `mergeable: true` / clean.

**Do not merge** when PR body or status fragment contradicts GitHub state (e.g., PR body says "blocked" but GitHub `isDraft=false`; or PR is draft but body says ready for review).

---

## Section 8 — Decision

- [ ] **APPROVE** — all sections pass; merge is safe.
- [ ] **REQUEST CHANGES** — list specific required fixes below, and provide a paste-ready follow-up prompt.
- [ ] **ESCALATE** — forbidden scope touched or protected boundary violated; do not merge; escalate to Main.

### Required changes (if any):

1.
2.
3.

### Paste-ready follow-up prompt (if REQUEST CHANGES):

```text
<paste-ready prompt here>
```

### Self-diagnosis (if REQUEST CHANGES):

```text
Why it happened:
Preventable: YES / NO
What should have caught it:
Immediate process change:
Durable guidance change needed: YES / NO
```

---

*Aligned to `docs/ai/codex/WP_DRAFTING_STANDARD.md` and `docs/ai/codex/WP_EXECUTION_REPORT.md`.*
