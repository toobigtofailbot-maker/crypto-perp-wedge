# Strategy Landscape Brief: BTCUSDT Perpetual Futures

**Date:** 2026-04-14
**Author:** Claude Code / Codex (WP-2b-combined)
**Status:** ADVISORY (per D2-016)
**Purpose:** Inform hypothesis selection across Phase 2 locked timeframes

## Summary

This brief assesses which strategy families are worth testing for BTCUSDT perpetual futures across the locked timeframe set (15m, 30m, 1h, 4h, 1d), based on:
- structural properties of Binance USDT-M perpetuals
- cost realism under our assumptions
- overfit risk relative to our available history
- current research-priority constraints in Phase 2

## Strategy Family Assessment by Timeframe

### 15m / 30m
**Verdict: DEFER for Phase 2**

Cost drag is likely too high relative to expected edge under current assumptions. No 15m/30m hypothesis should be pre-registered in Phase 2 without explicit cost justification.

### 1h
**Verdict: SECONDARY - test if 4h proves viable**

| Family | Plausibility | Cost Drag | Priority |
|--------|--------------|-----------|----------|
| Trend-following | HIGH | MEDIUM | Defer to 4h first |
| Momentum | MEDIUM | MEDIUM | Subsumes into trend |
| Funding-informed | MEDIUM | LOW | Better aligned at 4h |

### 4h (PRIMARY RESEARCH TIMEFRAME)
**Verdict: PRIMARY - H-001 and H-002 target this timeframe**

| Family | Plausibility | Cost Drag | Priority |
|--------|--------------|-----------|----------|
| Trend-following (Donchian) | HIGH | LOW | **H-002** |
| Funding-directional | HIGH | LOW | **H-001** |
| Basis/premium-driven | MEDIUM | LOW | Future candidate (H-003) |

### 1d
**Verdict: CONFIRMATION TIMEFRAME**

1d is best used as a regime filter or confirmation timeframe. Could support standalone trend strategy, but sample count is smaller and therefore less attractive as the first primary timeframe.

## Active Hypotheses

| ID | Strategy Family | Timeframe | Status |
|----|-----------------|-----------|--------|
| H-001 | Funding-directional (symmetric long/short) | 4h | DRAFT - ready for execution |
| H-002 | Donchian trend-following | 4h | DRAFT - ready for execution |

## Recommendations

1. Execute H-001 and H-002 in parallel or near-parallel - they test different market inefficiencies.
2. Use 4h as the primary timeframe for both.
3. Defer 15m/30m unless explicit cost justification emerges.
4. Consider 1d confirmation for H-002 in a later variant.
5. Queue basis/premium strategy as H-003 after H-001 / H-002 results are known.

## Limitations

This brief is advisory per D2-016. It does not bypass the D2-014 pre-registration requirement.

The current market context may inform priority but should not override full-history testing.

## Notes

- This brief is a repo control artifact, not a live trading recommendation.
- Strategy priority is driven by implementability, realism, and research value, not marketplace hype.
