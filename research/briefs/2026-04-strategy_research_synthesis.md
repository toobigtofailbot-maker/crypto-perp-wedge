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

Longer timeframes may reduce noise and cost drag, while smaller timeframes can provide the more frequent daily opportunity needed for an eventual portfolio. Shorter timeframes may still work, but usually require stronger filtering and better trade selection.

**Implication:** Keep 1d in scope as the slower / lower-turnover layer while expanding meaningful intraday research across 1h, 30m, and later 15m. Do not treat any timeframe as proven before it survives repo evaluation gates.

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
| 15m | Planning / Candidate Expansion Target | In scope for later candidate registration because portfolio goals include frequent intraday opportunities; cost drag requires especially strong filtering |
| 30m | Active Intraday Candidate Layer | Candidate tier now pre-registered cautiously; higher cost-drag risk requires controlled research |
| 1h | Active Intraday Candidate Layer | Candidate tier now pre-registered cautiously; balance between signal count and cost drag |
| 4h | Cold Storage | H-001 / H-002 failures; revisit only with materially different logic |
| 1d | Slower Candidate Layer | Lower-turnover foundation layer within a broader multi-timeframe portfolio map |

### Why These Strategies?

| Hypothesis | Strategy | Selection Rationale |
|------------|----------|---------------------|
| H-003 | 1d BB Mean Reversion (Long-Only) | Plausible candidate family for filtered reversion with BTC upward drift respected |
| H-004 | 1d Dual MA + Volatility Regime | Foundation trend-following logic enhanced with a regime filter |
| H-005 | 1h MACD + Price Structure | Research-informed momentum candidate using structure confirmation to filter weaker crossovers |
| H-006 | 30m BB Squeeze Breakout | Intraday volatility-breakout candidate using compression logic to control trade selection |

### Portfolio Construction Direction

The end-state target is not one strategy. The research program should build toward a basket of independently validated strategies across multiple locked timeframes.

Smaller timeframes may eventually host more candidate diversity because they can produce more frequent entries, which better matches the desired daily opportunity set. This is a research-priority statement, not an edge claim: no timeframe gets a free pass, and every candidate must survive the same pre-registration, backtest, trial-log, shadow, and promotion discipline.

---

## H-001 / H-002 Failure Lessons Applied

| Lesson | Application in New Candidates |
|--------|-------------------------------|
| Simple baseline logic failed | New candidates use richer structure while preserving interpretability |
| No strong regime framing | New candidates include directional, volatility, or structure-aware framing |
| 4h did not survive baseline gates | Keep 4h in Cold Storage while researching materially different logic on other locked timeframes |
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

## Candidate Coverage Map

- H-003 - 1d slower-timeframe layer
- H-004 - 1d slower-timeframe layer
- H-005 - 1h active intraday layer
- H-006 - 30m active intraday layer
- 15m - in-scope future intraday expansion target

---

## Next Steps

1. Pre-register H-003 and H-004 as the primary 1d candidates (WP-3a1)
2. Pre-register H-005 and H-006 as secondary / exploratory candidates (WP-3a2)
3. Execute baseline backtests in a later package
4. Evaluate results and produce decision records
5. Only surviving candidates proceed to sweeps / deeper research
