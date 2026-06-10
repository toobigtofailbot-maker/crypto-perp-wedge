# SKILL: review-report-back

**Purpose:** Systematically verify a completed execution report-back before accepting or rejecting the work. Produces an APPROVE / REQUEST CHANGES / ESCALATE recommendation with explicit reasoning for every check.

**When to use:** After a coding agent delivers a report-back for any execution WP. Run this review before merging any execution PR.

**Authority reference:** `docs/ai/codex/WP_EXECUTION_REPORT.md` and `docs/ai/codex/WP_DRAFTING_STANDARD.md`.

---

## Review Checklist (Run in Order)

### Step 1 — Validate Report-Back Structure

The active WP's report-back format wins. If the active WP specifies A–H sections or another explicit shape, check for those. For clean T1 packages with no WP-specified format, check for the compact A–E shape from `docs/ai/codex/WP_EXECUTION_REPORT.md`.

Confirm the report-back contains:

- [ ] Scope statement (what changed, what did not).
- [ ] Exact changed-file list.
- [ ] Validation result (commands, pass/fail, counts).
- [ ] Boundary/forbidden-scope confirmation.
- [ ] PR status:
  - [ ] Branch and base.
  - [ ] Actual PR title (with package label prefix).
  - [ ] PR URL.
  - [ ] GitHub `isDraft` (actual value from `gh pr view`).
  - [ ] GitHub `mergeable` (actual value from `gh pr view`).
- [ ] Final PR readiness gate result (see Step 5).
- [ ] Ready-for-review decision: YES or NO.

If any required item is missing → **REQUEST CHANGES**: ask the coding agent to complete the report-back before proceeding.

---

### Step 2 — Verify Validation Evidence

For each validation command or gate required by the active WP:

1. Confirm the command ran.
2. Confirm the result matches expected output (exit code, keyword, count).
3. Mark PASS or FAIL.

Failure modes to watch for:

- Gate output missing or replaced with "N/A" → **REQUEST CHANGES**.
- Gate shows non-zero exit code or failure → investigate before accepting.
- Gate output truncated ("..." or "see logs") → **REQUEST CHANGES**: require explicit output.
- Skipped validation not classified as `Not run; not used as merge evidence.` → **REQUEST CHANGES**.

---

### Step 3 — Confirm Changed-File Scope

Verify the changed-file list matches the WP's allowed scope:

- [ ] Every changed file is explicitly in the WP's allowed scope.
- [ ] No forbidden files touched (runtime, paper/live, OMS, risk, schemas, validators, tests, tools, scripts, configs, data, CI unless explicitly allowed).
- [ ] No untracked or generated outputs committed.
- [ ] No data files committed (Parquet, ZIP, CSV) unless explicitly scoped.

Any violation of forbidden scope → **ESCALATE** immediately.

---

### Step 4 — Confirm Protected Boundaries

Check:

- [ ] No protected runtime or paper/live paths touched.
- [ ] No unauthorized schema/validator/query-layer changes.
- [ ] No dependency additions unless explicitly scoped by active WP.

```powershell
git diff --name-only origin/main...HEAD | Select-String "^src/|^configs/|^docs/decisions|^docs/architecture"
```

Any hit on protected paths → **ESCALATE**.

---

### Step 5 — Final PR Readiness Gate

- [ ] PR title begins with the package label followed by `:`.
- [ ] PR body contains no GitHub template placeholders, unchecked template checkboxes, or stale `TBD` / `pending` / `to be added` / `background run` text.
- [ ] Status fragment contains the actual PR URL (not a placeholder).
- [ ] Status fragment validation summary is final (no pending/background language).
- [ ] GitHub `isDraft: false` for normal non-blocked PRs.
- [ ] GitHub `mergeable: true` / clean.

For follow-up or blocker-resolution packages, also check:

- [ ] Contradiction scan was completed: stale blocked/draft/pending/not-ready/prior-option language removed from PR body, status fragment, and changed docs.

For non-authority packages:

- [ ] Semantic text audit was completed (see `docs/ai/codex/COMPACT_WP_TEMPLATE.md`).

**Do not approve when PR body or status fragment contradicts GitHub state.**

---

### Step 6 — Semantic Fit and Authority Check

- [ ] Objective stated in the WP is satisfied.
- [ ] No architecture redesign outside WP scope.
- [ ] No stale blocked/draft/pending claims.
- [ ] No ranking/recommendation/readiness/promotion/execution authority introduced unless explicitly scoped.

---

## Decision Tree

```
All steps PASS, diff clean, no forbidden scope, no contradictions, final readiness gate met
  → APPROVE: the PR is merge-ready

Any validation gate FAIL or gate output missing
  → REQUEST CHANGES: enumerate exactly what needs to be fixed; provide paste-ready follow-up prompt

Forbidden scope touched OR protected boundary violated
  → ESCALATE to Main immediately; do not merge; do not revise

Final readiness gate not met (placeholder PR body, stale status fragment, isDraft mismatch)
  → REQUEST CHANGES: provide paste-ready follow-up prompt

Ambiguity about whether a change is within scope
  → ESCALATE to Main for a scope ruling
```

---

## When Not Merge-Ready

If the PR is not merge-ready, this review must provide:

1. Exact reason the PR is not ready.
2. A paste-ready follow-up prompt that resolves the blocker.
3. A self-diagnosis:
   - Why it happened.
   - Preventable: YES / NO.
   - What should have caught it earlier.
   - Immediate process change.
   - Durable guidance change needed: YES / NO.

Claude Code cannot approve or merge its own PRs. The APPROVE decision here authorizes Side/Main to merge, not the coding agent itself.

---

## Report Format

After completing the checklist, return a structured review result:

```text
REVIEW RESULT
Decision: APPROVE | REQUEST CHANGES | ESCALATE

Structure check: PASS | FAIL — <note>

Validation evidence:
  <command>: PASS | FAIL — <note>
  ...

Diff scope: CLEAN | VIOLATIONS — <list violations>

Protected boundaries: CLEAN | VIOLATIONS — <list>

Final readiness gate: PASS | FAIL — <detail>

Contradictions: NONE | <list>

Authority check: CLEAN | VIOLATIONS — <list>

Required actions (for REQUEST CHANGES):
  1. <specific action>
  2. <specific action>

Paste-ready follow-up prompt (for REQUEST CHANGES):
  <prompt text>

Self-diagnosis (for REQUEST CHANGES):
  Why it happened:
  Preventable: YES / NO
  Should have caught by:
  Immediate process change:
  Durable guidance change needed: YES / NO

Escalation reason (for ESCALATE):
  <description>
```

---

## Model Selection Note

Use Opus for reviews involving architecture-level contradictions, authority scope questions, or semantic audit judgment calls. Use Sonnet for mechanical gate verification.

See `.claude/README.md` → Advisor Strategy for the model selection policy.
