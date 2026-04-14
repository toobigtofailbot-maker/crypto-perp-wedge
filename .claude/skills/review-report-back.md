# SKILL: review-report-back

**Purpose:** Systematically verify a completed execution report-back before
accepting or rejecting the work.  Produces an accept / revise / escalate
recommendation with explicit reasoning for every gate.

**When to use:** After an Execution chat delivers a report-back for any
execution brief.  Run this review before merging any execution PR.

---

## Review checklist (run in order)

### Step 1 — Validate the report-back structure

Confirm the report-back contains all required sections:

- [ ] Status: COMPLETE | BLOCKED | FAILED
- [ ] Branch name
- [ ] PR URL (or compare URL)
- [ ] Base commit SHA on main
- [ ] Files created (with line counts)
- [ ] Files updated (with line counts)
- [ ] All validation gate outputs pasted verbatim
- [ ] Dependencies added / justification
- [ ] Forbidden-scope confirmation: YES
- [ ] Open items escalated to Main
- [ ] Ready for merge: YES | NO

If any section is missing → **REVISE**: ask the Execution chat to complete
the report-back before proceeding.

---

### Step 2 — Verify every validation gate output

For each gate in the execution brief:

1. Read the **expected output** from the brief.
2. Compare to the **pasted actual output** in the report-back.
3. Mark PASS or FAIL.
4. Note any discrepancy.

Failure modes to watch for:

- Gate output missing or replaced with "N/A" → **REVISE**
- Gate shows non-zero exit code → **FAIL** → investigate before accepting
- Gate output truncated ("..." or "see logs") → **REVISE**: require verbatim paste
- Gate passes but output looks suspicious (0 tests run, empty diff) → **ESCALATE**

---

### Step 3 — Confirm git diff touches only allowed scope

Run (or ask the Execution chat to paste output of):

```bash
git diff --stat main
```

For each changed file, check against the brief's ALLOWED SCOPE list:

- [ ] Every changed file is explicitly in ALLOWED SCOPE
- [ ] No file under `src/**` was touched
- [ ] No file under `docs/architecture/**` was touched
- [ ] No file under `docs/onboarding/**` was touched
- [ ] `docs/decisions.md` was not touched
- [ ] `configs/**` was not touched
- [ ] Existing test files were not modified (only new test files created)
- [ ] Existing prompt templates not modified
- [ ] No data files committed (Parquet, ZIP, CSV)

Any violation of FORBIDDEN SCOPE → **ESCALATE** immediately.

---

### Step 4 — Confirm no protected-boundary file was touched

Check specifically for Phase 1 protected files:

```bash
git diff --name-only main | grep -E "^src/" || echo "CLEAN"
git diff --name-only main | grep -E "^configs/" || echo "CLEAN"
git diff --name-only main | grep "docs/decisions.md" || echo "CLEAN"
```

All must return CLEAN.  Any hit → **ESCALATE**.

---

### Step 5 — Flag contradictions

Review the brief's scope and the actual diff for logical contradictions:

- Does the implementation match the file specifications in the brief?
- Are all public function signatures present as specified?
- Are all dataclass fields present?
- Are all validation-gate hard rules enforced (asserts, no-lookahead, etc.)?
- Does `requirements.txt` contain only the explicitly allowed additions?
- Is CCXT absent from all dependency files? → **ESCALATE** if present

If implementation deviates from spec without explicit justification → **REVISE**
with specific corrections required.

---

### Step 6 — Smoke-check the Gate 8 end-to-end output

If Gate 8 is a smoke end-to-end run:

- Confirm the GateReport JSON is present and well-formed.
- Confirm all 8 gate IDs are present.
- Confirm numeric values are finite (no NaN, Inf, or None).
- Confirm the overall_pass field is a boolean.

Malformed GateReport → **REVISE**.

---

## Decision tree

```
All gates PASS, diff clean, no forbidden scope, no contradictions
  -> ACCEPT: approve PR and merge

Any gate FAIL or gate output missing
  -> REVISE: enumerate exactly what needs to be fixed and re-submitted

Forbidden scope touched OR protected boundary file modified
  -> ESCALATE to Main immediately; do not merge; do not revise

Ambiguity in whether a change is within scope
  -> ESCALATE to Main for a scope ruling

Execution chat exceeded scope or added deferred items
  -> REVISE: revert out-of-scope changes; re-submit
```

---

## Report format

After completing the checklist, return a structured review result:

```
REVIEW RESULT
Decision: ACCEPT | REVISE | ESCALATE

Gate verification:
  Gate 1 (name): PASS | FAIL — <note>
  Gate 2 (name): PASS | FAIL — <note>
  ... (all gates)

Diff scope: CLEAN | VIOLATIONS — <list violations>

Protected boundaries: CLEAN | VIOLATIONS — <list>

Contradictions: NONE | <list with brief descriptions>

Required actions (for REVISE):
  1. <specific action>
  2. <specific action>

Escalation reason (for ESCALATE):
  <description>
```

---

## Model selection note

Use **Opus** for reviews that involve architecture-level contradictions or
scope ambiguity.  Use **Sonnet** for mechanical gate verification.
See `.claude/README.md` → Advisor Strategy.
