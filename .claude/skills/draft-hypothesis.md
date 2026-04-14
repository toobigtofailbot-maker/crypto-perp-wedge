# SKILL: draft-hypothesis

**Purpose:** Draft a pre-registered `HYPOTHESIS.md` for a strategy idea using
D2-005, D2-014, and D2-015. The economic rationale comes before any test plan
or backtest execution.

**When to use:** Use this skill when the Analyst is asked to turn a strategy
idea into a testable research hypothesis under `research/hypotheses/<id>/`.

---

## Required shell

Start from `research/templates/HYPOTHESIS.md`. Copy its structure into:

```text
research/hypotheses/<id>/HYPOTHESIS.md
```

Do not modify the template file.

---

## Workflow

### Step 1 - Define the hypothesis ID

Choose or confirm a stable hypothesis directory ID before writing. Use the
format already documented in `research/templates/HYPOTHESIS.md`.

### Step 2 - Write the economic rationale first

Explain the market inefficiency, behavioral pattern, microstructure rationale,
or empirical observation the strategy expects to exploit. This section must
stand on its own before any testable prediction is written.

### Step 3 - State a falsifiable prediction

Write a specific prediction that can be evaluated net of costs. It must name
the signal family, instrument, timeframe, and expected performance direction.

### Step 4 - Lock the primary timeframe

Set `primary_timeframe` to exactly one of:

```text
15m, 30m, 1h, 4h, 1d
```

Include a justification for the chosen primary timeframe inside the
`HYPOTHESIS.md`. Per D2-014, this choice is part of pre-registration and cannot
be inferred later from a timeframe suitability brief.

### Step 5 - Add optional confirmation timeframes

If confirmation timeframes are used, they must be coarser than the primary
timeframe. If none are needed, write `None`.

Allowed coarser ordering:

```text
15m < 30m < 1h < 4h < 1d
```

### Step 6 - Define success and kill criteria

Record success criteria against the D2-006 gates and write concrete kill
criteria that would end the hypothesis without further tuning.

### Step 7 - List free parameters

List every tunable free parameter. The maximum is 5. If a proposed hypothesis
needs more than 5 free parameters, simplify it or escalate to Main.

### Step 8 - Estimate expected trial count

Fill in the expected trial count before evaluation. Include the rationale, such
as grid size times folds. Do not understate this count; it feeds DSR and the
overfitting firewall.

---

## Guardrails

- The Analyst must not run a backtest while drafting.
- The Analyst must not modify files outside `research/hypotheses/<id>/` or
  `research/briefs/`.
- The Analyst must not edit `research/templates/HYPOTHESIS.md`.
- The Analyst must escalate if the hypothesis requires edits to `src/`,
  `lib/`, `strategies/`, `configs/`, `tests/`, or locked-truth docs.
