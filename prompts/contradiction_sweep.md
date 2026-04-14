# Contradiction Sweep Template

Use this template when newly landed docs or code need to be checked against
the existing corpus for contradictions.  Run after any merge to `main` that
adds or changes design decisions, architecture docs, or locked truth files.

---

## When to run

- After merging a new execution brief's deliverables
- After any change to `docs/decisions.md`
- After updating `docs/onboarding/**` or `docs/architecture/**`
- Before drafting a new execution brief that touches an area with existing decisions

---

## Step 1 — Identify the landing set

List the files changed in the recent merge:

```bash
git diff --name-only HEAD~1 HEAD
```

For each changed file, record:
- File path
- What it adds / changes (one line per file)

---

## Step 2 — Extract key claims

For each new or changed file, extract explicit claims:

- Quantitative thresholds (e.g. "OOS Sharpe >= 1.0", "max DD <= 20%")
- Named components (e.g. "backtester uses next_bar_open execution")
- Decision identifiers referenced (e.g. "D2-003A", "D2-006")
- Technology choices (e.g. "DuckDB + Polars", "no CCXT in Phase 2")
- Scope boundaries ("Phase 1 protected", "deferred to WP-X")

---

## Step 3 — Grep for related content in existing corpus

Run targeted searches against the repo.  Adjust patterns for your landing set.

### Decision references

```bash
grep -r "D2-003\|D2-004\|D2-006\|D2-009\|D2-010\|D2-012" \
  docs/ .claude/ prompts/ --include="*.md" -l
```

### Promotion gate thresholds

```bash
grep -r "Sharpe\|drawdown\|walk.forward\|cost.drag\|parameter.sensitiv" \
  docs/ lib/ tests/ --include="*.md" --include="*.py" -n
```

### Technology choices

```bash
grep -r "ccxt\|CCXT\|graphify\|Graphify\|superpowers\|duckdb\|polars" \
  . --include="*.py" --include="*.txt" --include="*.md" -i
```

### Execution model

```bash
grep -r "next_bar_open\|bar.close.*signal\|lookahead\|fill.price" \
  . --include="*.py" --include="*.md" -n
```

### Phase 1 boundaries

```bash
grep -r "src/\|overlay\|ledger\|OMS\|paper.trader" \
  lib/ tests/ prompts/ .claude/ --include="*.py" --include="*.md" -n
```

---

## Step 4 — Evaluate each hit

For each grep hit, apply the following decision tree:

```
Is the hit in the same file as the new landing?
  YES -> skip (internal consistency)
  NO -> continue

Does the hit state the same claim as the new landing?
  YES, same value -> CONSISTENT ✓
  YES, different value -> CONTRADICTION → log it (Step 5)
  NO, different topic -> skip

Is the hit in a locked file (docs/decisions.md, docs/onboarding/**)?
  YES + contradiction -> ESCALATE to Main immediately
  NO + contradiction -> log for author resolution
```

---

## Step 5 — Log contradictions

For each contradiction found:

```
CONTRADICTION #{n}
File A (new/changed): <path>:<line>
  Claim: "<exact quote>"

File B (existing):    <path>:<line>
  Claim: "<exact quote>"

Conflict type:
  [ ] Numeric threshold differs
  [ ] Named component behaviour differs
  [ ] Decision ID referenced inconsistently
  [ ] Technology choice conflicts
  [ ] Scope boundary conflicts

Severity:
  [ ] BLOCKING — locked truth contradicted; must resolve before merge
  [ ] HIGH — affects correctness of downstream packages
  [ ] LOW — wording inconsistency only; does not affect behaviour

Resolution options:
  1. Update <File A> to match <File B> (preferred if B is locked truth)
  2. Update <File B> to match <File A> (requires Main approval if B is locked)
  3. Clarify that both are intentional (document rationale)
```

---

## Step 6 — Resolution decision tree

```
Contradiction involves docs/decisions.md or docs/onboarding/**?
  YES -> ESCALATE to Main; do not attempt to resolve
  NO  -> continue

Contradiction involves a numeric gate threshold?
  YES -> check against D2-006 (promotion gates) as ground truth
         D2-006 takes precedence; update any file that contradicts it
  NO  -> continue

Contradiction is a wording inconsistency only (same meaning)?
  YES -> update to use canonical phrasing from decisions.md
  NO  -> escalate to Main for a ruling
```

---

## Step 7 — Report

Return a structured sweep result:

```
CONTRADICTION SWEEP RESULT
Date: <ISO date>
Landing set: <list of new/changed files>

Files searched: <count>
Grep hits reviewed: <count>

Contradictions found: <count>
  Blocking: <count>
  High: <count>
  Low: <count>

Contradiction log:
  #{n}: <one-line summary> — Severity: <level> — Resolution: <option>

All clear: YES | NO

Required actions before next merge:
  1.
  2.
```
