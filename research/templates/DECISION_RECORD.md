# Decision Record Template

> **How to use this template:**
> 1. Copy this file to `research/decisions/DEC-XXXX.md`
> 2. Fill in after hypothesis testing is complete
> 3. Link to the hypothesis spec and experiment notebook
> 4. This record is the permanent audit trail for the decision

---

## Decision ID

**DEC-XXXX**

---

## Date

[YYYY-MM-DD]

---

## Hypothesis Reference

- **Hypothesis ID:** [H-YYYY-MM-XXX]
- **Hypothesis location:** `research/hypotheses/[directory]/HYPOTHESIS.md`
- **Experiment notebook:** `research/hypotheses/[directory]/experiment.ipynb`

---

## Context

[Brief summary of what was tested and why. 2-3 sentences.]

---

## Evidence Summary

### Promotion Gate Results

| Gate | Required | Achieved | Pass/Fail |
|------|----------|----------|-----------|
| OOS Sharpe ≥ 1.0 | ≥ 1.0 | [value] | |
| DSR > 1.0 (95% CI) | > 1.0 | [value] | |
| Max DD ≤ 20% | ≤ 20% | [value] | |
| Param sensitivity | ≥ 70% | [value] | |
| Cost drag | ≤ 50% | [value] | |
| No 90-day window > 60% | < 60% | [value] | |
| Free parameters | ≤ 5 | [count] | |
| Walk-forward efficiency | > 0.5 | [value] | |

### Trial Log Summary

- **Total trials logged:** [count]
- **Trial log location:** `research/trial_log.jsonl`
- **Trial ID range:** [first] to [last]

### Key Observations

[Bullet points of important findings from the experiment]

---

## Options Considered

1. **GO:** Promote to shadow mode
2. **NO-GO:** Archive hypothesis, do not promote
3. **REVISE:** Modify hypothesis and re-test

---

## Decision

**[GO | NO-GO | REVISE]**

---

## Rationale

[Explain why this decision was made. Reference specific evidence.]

---

## Conditions (if GO)

[Any conditions that must be met during shadow mode. Example: "Monitor for Sharpe degradation below 0.5."]

---

## Next Steps (if REVISE)

[What specific changes to the hypothesis? New hypothesis ID required?]

---

## Reviewer

- **Reviewed by:** [Name]
- **Review date:** [YYYY-MM-DD]
