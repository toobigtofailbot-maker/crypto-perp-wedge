# Online OHLCV Hypothesis Parameter Lock

This document is non-authoritative research-intake memory. It preserves three online-derived BTCUSDT OHLCV strategy hypotheses and compact first-test parameter envelopes. It does not authorize implementation, Strategy Spec creation, compiler changes, runner changes, canonical execution, Result Population writes, candidate registration, walk-forward/OOS, paper/live execution, runtime behavior, OMS/risk changes, broker/exchange connectivity, capital movement, or autonomous agent action.

## Scope

Fact:

- This is a docs-only parameter-lock surface for three online BTCUSDT OHLCV strategy hypotheses.
- The hypotheses are preserved for possible future feasibility/design review only.
- The envelopes below are compact first-test shapes, not executable artifacts.

Decision:

- Do not create Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, candidates, or paper/live/runtime authority from this document.
- Any future implementation requires a separate authorized package.

Open question:

- Whether current Strategy Spec, compiler, runner, and data capabilities can express these shapes must be checked later by a dedicated feasibility/design package.

## ORB Break-And-Retest

Hypothesis:
BTCUSDT may show exploitable continuation after a fixed daily opening range is broken and then retested, if entries are close-confirmed and constrained to one trade per session.

First-test envelope:

- timeframe: 30m bars
- session anchor: UTC 00:00
- opening range: first 30m bar
- breakout: close beyond range by 0.1 ATR
- retest window: {2, 4} bars
- retest tolerance: 0.1 ATR
- stop: opposite range side
- target: {1R, 2R}
- time exit: session-end exit
- max trades: 1 per session
- no-trade days: preserved
- free parameters: retest window, target
- expected first-test variants: ~4

Required implementation prerequisites:

- session/opening-range primitive
- close-confirmed breakout primitive
- retest-window and tolerance primitive
- one-trade-per-session guard
- complete denominator preservation

Boundary:

- This section does not rank, freeze, test, or approve the hypothesis.
- This section does not authorize opening-range, breakout, retest, stop, target, or session logic implementation.

## No-Wick Trend Pullback

Hypothesis:
BTCUSDT no-wick trend candles may identify directional impulse, and a deterministic midpoint pullback may offer continuation entries when aligned with a simple trend filter.

First-test envelope:

- timeframe: 1h bars
- trend filter: close vs EMA50
- wick tolerance: <= 10% of candle range
- body threshold: body >= 60% of range
- pullback: retest signal-candle midpoint
- entry: next open after confirmation
- stop: {signal-candle extreme, 1.5 ATR}
- target: {1.5R, 2R}
- time exit: allowed
- max position: one active position per symbol/timeframe
- free parameters: stop, target
- expected first-test variants: ~4

Required implementation prerequisites:

- candle-shape/wick predicate
- body-ratio predicate
- trend filter binding
- pullback confirmation rule
- complete denominator preservation

Boundary:

- This section does not rank, freeze, test, or approve the hypothesis.
- This section does not authorize candle-shape predicates, pullback logic, stop logic, target logic, or trend-filter implementation.

## Deterministic ORB-Derived Bias Variant

Hypothesis:
A deterministic ORB variant may perform better if breakouts are only taken in the direction of a higher-timeframe bias, without proprietary classifiers or martingale.

First-test envelope:

- timeframe: 30m bars
- opening range: 30m
- bias: 4h trend, close vs 4h SMA50
- breakout: close beyond OR high/low by 0.1 ATR
- retest: none
- stop: opposite OR side
- target: {1R, 2R}
- time exit: session-end exit
- no martingale
- max trades: 1 per session
- free parameters: target only unless Main later adds another bounded axis
- expected first-test variants: ~2

Required implementation prerequisites:

- session/opening-range primitive
- higher-timeframe deterministic trend-bias reference
- close-confirmed breakout primitive
- one-trade-per-session guard
- complete denominator preservation

Boundary:

- This section does not rank, freeze, test, or approve the hypothesis.
- This section does not authorize opening-range, higher-timeframe bias, breakout, stop, target, or session logic implementation.

## Shared Constraints

Shared constraints:

- no proprietary classifiers
- no martingale
- no discretionary defended levels
- no same-bar entry/exit assumptions
- no hidden no-trade-day deletion
- no winner-only reporting
- no candidate/paper/live authority
- no implementation until a separate package authorizes primitives and testing

## Future Implementation Note

The eventual implementation should not be bundled with this package. A later feasibility/design package must inspect current Strategy Spec, compiler, runner, and data capabilities before any primitive or screen package is drafted. The shared primitive set is likely: deterministic session/opening-range, close-confirmed breakout, retest/tolerance, one-trade-per-session, candle-shape/wick predicate, body-ratio predicate, and optional higher-timeframe trend-bias reference.

Future option:

- A later `ONLINE-OHLCV-PRIMITIVE-FEASIBILITY-01` or equivalent package could determine whether these primitives belong in Strategy Spec grammar, compiler support, runner behavior, or a different research-intake path.

## Boundary Recap

- Strategy Spec created: NO.
- Variant Manifest created: NO.
- Sweep Plan created: NO.
- Result Population written: NO.
- Candidate registered: NO.
- Walk-forward/OOS authorized: NO.
- Compiler/schema/validator/query/runner/data changed: NO.
- Paper/live/runtime/capital authority created: NO.
- Protected path touched: NO.
