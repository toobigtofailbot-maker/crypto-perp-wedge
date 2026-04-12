# Report-Back Template

> Fill in this template after completing an execution brief. Paste the completed report into the Architecture chat.

---

## Work Package

**WP-X:** [Name from execution brief]

---

## Branch

`[branch-name]`

---

## Files Changed

```
[Paste output of: git diff --stat]
```

---

## Validation Gates

| Gate | Command | Result | Output |
|------|---------|--------|--------|
| 1 | `[command]` | PASS/FAIL | [output or summary] |
| 2 | `[command]` | PASS/FAIL | [output or summary] |
| ... | | | |

---

## Evidence Checklist

- [ ] [Evidence item 1 from execution brief]
- [ ] [Evidence item 2]
- [ ] ...

---

## Issues Encountered

[None / List any issues and how they were resolved]

---

## Escalation Items

[None / List anything that requires Architecture chat decision]

---

## Ready for Review

- [ ] All gates pass
- [ ] All evidence items checked
- [ ] No forbidden files modified
- [ ] PR opened with correct title
