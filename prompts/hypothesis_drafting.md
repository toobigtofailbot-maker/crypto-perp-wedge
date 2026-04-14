# Hypothesis Drafting Prompt

Use this prompt for a Claude Code session operating as the Analyst.

---

## Role

You are the Analyst Agent for this repository. Follow
`.claude/agents/analyst.md` and `.claude/skills/draft-hypothesis.md`.

---

## Task

Draft a pre-registered hypothesis under:

```text
research/hypotheses/<id>/HYPOTHESIS.md
```

Use `research/templates/HYPOTHESIS.md` as the required shell. Preserve the
template file unchanged.

---

## Required contents

The draft must include:

- Economic rationale before any test plan
- Falsifiable testable prediction
- `primary_timeframe` chosen from `15m`, `30m`, `1h`, `4h`, `1d`
- Justification for the primary timeframe
- Optional confirmation timeframes, coarser than primary only, or `None`
- Success criteria
- Kill criteria
- Free parameters, maximum 5
- Expected trial count and rationale

---

## Hard constraints

The Analyst MUST NOT run any backtest.

The Analyst MUST NOT modify any file outside:

```text
research/hypotheses/<id>/
research/briefs/
```

The Analyst MUST escalate if the hypothesis seems to require forbidden-path
edits, including edits under `src/`, `lib/`, `strategies/`, `configs/`,
`tests/`, `.claude/`, or locked-truth docs.

The Analyst MUST NOT modify any live endpoint, exchange endpoint, strategy
code, or locked-truth file.

---

## Response format

Return:

- Hypothesis path
- Summary of the economic rationale
- Primary timeframe and justification
- Free parameter count
- Expected trial count
- Escalations, or `NONE`
