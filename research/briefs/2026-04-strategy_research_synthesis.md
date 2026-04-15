# Strategy Research Synthesis: Post H-001/H-002 Candidate Selection

**Date:** 2026-04-15
**Context:** H-001 and H-002 baseline failures (4h -> Cold Storage)
**Purpose:** Document research-informed selection of next hypothesis batch

---

## Key Research Findings

### Finding 1: Momentum > Simple Mean-Reversion for Bitcoin

Bitcoin appears to show stronger trend persistence than simple short-horizon mean reversion. Pure unfiltered mean-reversion has weak baseline evidence in our current process. Filtered mean-reversion may still be viable.

**Implication:** Strategies should be momentum-aligned or use mean-reversion only with strong filters / context.

### Finding 2: Timeframe Matters Significantly

Longer timeframes appear more robust and less exposed to cost drag. Shorter timeframes may still work, but usually require stronger filtering and better trade selection.

**Implication:** Start with 1d as the primary next research tier, then 1h as a secondary later tier. 30m remains exploratory. Defer 15m for now.

### Finding 3: Volatility-Based Strategies Are Plausible Candidates

Bollinger Band compression / expansion and volatility-aware strategies appear repeatedly in BTC strategy research and practitioner logic.

**Implication:** BB-based strategies are plausible candidates, especially BB Mean Reversion with directional bias and volatility-aware logic.

### Finding 4: Multi-Indicator Confirmation Improves Candidate Quality

Single-indicator strategies are more fragile. Two-component logic, such as momentum + structure, trend + regime, or BB + context, is more plausible for robust research candidates.

**Implication:** New candidates should use at least two signal/context components where justified.

### Finding 5: Regime Filtering Is Common in Serious Strategy Design

Trend, volatility, or regime filters are common in more professional systems and can help avoid structurally weak environments.

**Implication:** New candidates should include at least one regime/context filter where it improves plausibility.

---

## Candidate Selection Rationale

### Why These Timeframes?

| Timeframe | Status | Rationale |
|-----------|--------|-----------|
| 15m | Deferred | Cost drag concern; defer until longer timeframes prove viable |
| 30m | Exploratory Later | Candidate tier exists, but not in this primary pre-registration package |
| 1h | Secondary Later | Candidate tier exists, but not in this primary pre-registration package |
| 4h | Cold Storage | H-001 / H-002 failures; revisit only with materially different logic |
| 1d | Primary | Strongest current candidate tier for next research batch |

### Why These Strategies?

| Hypothesis | Strategy | Selection Rationale |
|------------|----------|---------------------|
| H-003 | 1d BB Mean Reversion (Long-Only) | Plausible candidate family for filtered reversion with BTC upward drift respected |
| H-004 | 1d Dual MA + Volatility Regime | Foundation trend-following logic enhanced with a regime filter |

---

## H-001 / H-002 Failure Lessons Applied

| Lesson | Application in New Candidates |
|--------|-------------------------------|
| Simple baseline logic failed | Both new candidates use richer structure |
| No strong regime framing | New candidates include directional or regime-aware framing |
| 4h did not survive baseline gates | Primary pivot to 1d |
| Need stronger foundation before optimization | New candidates chosen for robustness and interpretability |

---

## Research Sources

This synthesis uses cautious, research-informed candidate selection based on:

- external strategy research / backtest studies
- academic and practitioner discussions of BTC trend, volatility, and mean-reversion behavior
- professional strategy writeups and strategy/backtest idea sources
- synthesis used for candidate generation, not as proof of profitability in our system

External backtest literature suggests plausibility for these strategy families, but all claims remain to be validated in our stack against the repo's data, cost assumptions, trial-log discipline, and D2-006 promotion gates.

---

## Prioritization

1. H-003 - primary
2. H-004 - primary
3. 1h candidates - next tier
4. 30m candidates - exploratory tier
5. 15m - deferred

---

## Next Steps

1. Pre-register H-003 and H-004 (this package)
2. Register secondary / exploratory candidates later
3. Execute baseline backtests in a later package
4. Evaluate results and produce decision records
5. Only surviving candidates proceed to sweeps / deeper research
