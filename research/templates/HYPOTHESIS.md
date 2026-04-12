# Hypothesis Template

> **How to use this template:**
> 1. Copy this file to `research/hypotheses/YYYY-MM-HXXX_short_name/HYPOTHESIS.md`
> 2. Fill in ALL fields below BEFORE running any backtests
> 3. The hypothesis ID becomes the prefix for all trial_log entries
> 4. Do not modify this template after trials begin — create a new hypothesis instead

---

## Metadata

- **ID:** H-YYYY-MM-XXX (e.g., H-2026-04-001)
- **Title:** [Short descriptive title]
- **Author:** [Name]
- **Date created:** [YYYY-MM-DD]
- **Status:** DRAFT | TESTING | CONCLUDED

---

## Economic Rationale

[Explain WHY this strategy should work. What market inefficiency or behavioral pattern does it exploit? Reference academic papers, market microstructure reasoning, or empirical observations. This section must be written BEFORE any testing.]

---

## Timeframe Declaration

- **Primary timeframe:** [One of: 15m, 30m, 1h, 4h, 1d — per D2-013]
- **Confirmation timeframes:** [Must be coarser than primary, or "None" — per D2-015]

---

## Testable Prediction

[State the specific, falsifiable prediction. Example: "A 20/50 EMA crossover on 1h BTCUSDT generates positive risk-adjusted returns net of costs over the test period."]

---

## Success Criteria

All of the following must be met (per D2-006):

- [ ] OOS Sharpe ≥ 1.0 net of costs
- [ ] DSR > 1.0 at 95% CI
- [ ] Max drawdown ≤ 20% per walk-forward fold
- [ ] Parameter sensitivity: Sharpe within 70% of baseline at ±25% shift
- [ ] Cost drag ≤ 50% of gross PnL
- [ ] No single 90-day window > 60% of total PnL
- [ ] Walk-forward efficiency (OOS/IS) > 0.5

---

## Kill Criteria

[Under what conditions will you abandon this hypothesis? Be specific. Example: "If OOS Sharpe < 0.3 after first walk-forward fold, kill immediately."]

---

## Required Data

- **Instrument:** BTCUSDT USDT-M Perpetual
- **Data source:** data.binance.vision + Binance REST API (per D2-003)
- **Date range:** [Start] to [End]
- **Streams needed:** [OHLCV, funding rates, mark price, etc.]

---

## Free Parameters

List all tunable parameters. **Maximum 5 per D2-006.**

| Parameter | Description | Default | Range to test |
|-----------|-------------|---------|---------------|
| 1. | | | |
| 2. | | | |
| 3. | | | |
| 4. | | | |
| 5. | | | |

---

## Expected Trial Count

- **Estimated number of backtest runs:** [Number]
- **Rationale:** [How did you estimate this? Parameter grid size × walk-forward folds?]

This number will be used for DSR calculation. Underestimating inflates apparent significance.

---

## Experiment Notebook

- **Location:** `research/hypotheses/[this directory]/experiment.ipynb`
- **Created:** [Date when notebook is created]

---

## Decision Record

- **Location:** `research/decisions/DEC-XXXX.md` (created after testing concludes)
- **Outcome:** [GO | NO-GO | REVISE — filled after testing]
