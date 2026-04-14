# SKILL: timeframe-suitability-brief

**Purpose:** Produce an advisory timeframe suitability brief under D2-016 for a
strategy family before or alongside hypothesis drafting.

**When to use:** Use this skill when the Analyst is asked which locked
timeframes structurally suit a strategy family, without selecting the final
hypothesis timeframe.

---

## Output path

Write the brief to:

```text
research/briefs/TFS-<slug>.md
```

Create `research/briefs/` on first use if needed.

---

## Required coverage

Discuss all five locked timeframes:

```text
15m, 30m, 1h, 4h, 1d
```

For each timeframe, assess structural fit for the strategy family using data
properties from the merged dataset, such as:

- Bar density and expected sample size
- Funding-event alignment
- Cost drag risk from turnover
- Susceptibility to D2-003A irreparable gaps
- Signal horizon and expected holding period
- Regime stability and walk-forward fold practicality

---

## Required sections

1. Strategy family
2. Dataset properties referenced
3. Timeframe-by-timeframe suitability notes
4. Risks and caveats
5. Advisory conclusion
6. Non-selection statement

The non-selection statement must say that the brief is advisory only and must
not be used to pre-select the hypothesis timeframe. Per D2-014, the primary
timeframe is locked inside `HYPOTHESIS.md`.

---

## Forbidden use

- Do not use this brief to choose the primary timeframe for a hypothesis.
- Do not backfill a hypothesis timeframe from this brief after testing.
- Do not edit `research/templates/HYPOTHESIS.md`.
- Do not run backtests while writing this brief.
