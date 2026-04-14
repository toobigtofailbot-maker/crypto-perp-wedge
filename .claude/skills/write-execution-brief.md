# SKILL: write-execution-brief

**Purpose:** Produce a complete, self-contained execution brief that an
Execution chat can pick up and execute without consulting any other document.

**When to use:** Any time Main or Architecture chat needs to hand a bounded
unit of work to an Execution agent.  See `prompts/execution_brief.md` for the
canonical template this skill produces.

---

## Required sections (in order)

Every execution brief must contain all of the following sections.  Do not omit
any section even if it seems obvious.

### 1. Package header block

```
PACKAGE ID: <WP-X.Y or similar identifier>
IMPLEMENTS: <D2-XXX decision IDs this package delivers>
PARTIAL:    <D2-XXX items partially addressed (optional)>
```

### 2. Objective

One paragraph.  State what will exist after execution that does not exist now,
and why it matters to the research pipeline.  Be concrete about deliverables.

### 3. Why it comes next

One paragraph.  State the dependency rationale.  Name the packages that must
have landed first, the packages blocked until this one lands, and why no
reordering is valid.

### 4. Scope — IN vs OUT

Two explicit bulleted lists:

- **IN SCOPE** — every file create/update allowed
- **OUT OF SCOPE** — every deferred item that might be tempting

If an item is not explicitly IN SCOPE it is OUT OF SCOPE.

### 5. Pre-flight checklist

Shell commands the Execution chat must run and pass **before editing any file**:

- `git status` / `git branch --show-current`
- `git checkout main && git pull --ff-only`
- `git checkout -b <branch-name>`
- baseline test run (e.g. `.venv/Scripts/python.exe -m pytest -q`)
- any dataset / file presence checks

If any pre-flight item fails, the Execution chat must STOP and report the
blocker before editing.

### 6. File specifications

For every file in ALLOWED SCOPE, provide:

- **Path** (exact)
- **Action** (`CREATE` or `UPDATE — append only` or `UPDATE — specific section`)
- **Public surface** or structural description (for code files: function
  signatures, dataclass fields, return types)
- **Hard rules / invariants** (asserts, no-lookahead, no-mock, etc.)

Reference `prompts/execution_brief.md` for the template format.

### 7. Allowed scope (exhaustive list)

List every file path that may be touched.  Nothing else.

### 8. Forbidden scope (exhaustive list)

List every file or directory that must not be touched.  Group by:

- Phase 1 protected (`src/**`, `configs/**`, existing tests)
- Phase 2 locked truth (`docs/decisions.md`, `docs/onboarding/**`, etc.)
- Out-of-scope items (deferred packages, external installs, etc.)

### 9. Validation gates

Numbered list.  For each gate:

- **Gate N — Short name**
- Command to run
- Expected output (exit code, keyword in stdout, etc.)
- What FAIL means (stop vs. warn)

### 10. Done criteria

Bullet list.  All validation gates pass, PR approved, merged to main.
Include tag requirement (or "No tag").

### 11. Branch / PR block

```
Branch: <branch-name>
PR title: <title>
Approver: <name>
Base: main
```

### 12. Report-back format

Paste the exact report-back template the Execution chat must fill in.
See `prompts/report_back.md` for the canonical template.

### 13. Stop and escalation conditions

Numbered list of conditions that require the Execution chat to STOP
immediately and escalate rather than attempting a workaround.

---

## Writing rules

1. **No ambiguity about scope.**  If a file is not in the explicit ALLOWED list,
   it is forbidden.  Write the forbidden list so completely that an over-eager
   agent cannot rationalise touching anything extra.

2. **Pre-flight must be runnable as written.**  Copy-pasteable shell commands only.
   Test them mentally against the actual repo state before including them.

3. **Validation gates must be automatable.**  Every gate must produce a machine-
   readable pass/fail signal (exit code or expected string in stdout).  Do not
   write gates that require human judgement.

4. **File specs must be complete.**  For code files: every public function,
   every dataclass field, every invariant.  The Execution chat should not need
   to infer anything.

5. **Stop conditions must be unambiguous.**  "Any pre-flight failure" is a
   valid stop condition.  "Something feels wrong" is not.

6. **Advisor / executor model for complex decisions.**  If the brief involves a
   design decision that requires architecture-level reasoning, note in the
   brief that the Execution chat should pause and escalate rather than guess.
   See `.claude/README.md` → Advisor Strategy for the model selection policy.

---

## Anti-patterns to avoid

- Vague scope ("update as needed", "improve the code")
- Missing forbidden list
- Gates that depend on external state not present in CI
- Briefs that require the Execution chat to read other documents to understand
  what to do
- Allowing CCXT, Graphify, Superpowers, or any deferred Phase 2 item

---

## Example reference

See `prompts/execution_brief.md` for a complete, annotated example of the
execution brief format.  All briefs produced by this skill should follow that
template exactly.
