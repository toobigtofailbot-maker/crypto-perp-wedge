# Phase-B Pivot Design 01

## A. Status and authority boundary

Status: docs-only design for `WP-PHASEB-PIVOT-DESIGN-01`.

This document does not freeze a Strategy Spec, does not create a Variant
Manifest, does not create a Sweep Plan, does not write a canonical or scratch
result population, does not register or rank a candidate, does not authorize
walk-forward, and does not create paper/live/runtime authority. It does not
touch compiler, schema, catalog, runner, `lib/`, OMS, risk, reconciliation,
broker/exchange, safe mode, data acquisition, or live-trading paths.

The next step requires Main/Karl review. Nothing here is a trading
recommendation or deployment recommendation.

## B. Evidence-based pivot rationale

Fact:

- `RP-7520` is the canonical dynamic-sizing evidence for `STRAT-SPEC-0002` /
  `VM-0002` / `SWEEP-PLAN-0002`, with denominator `10`, `10` result rows, and
  `10` successful runner completions.
- `RP-7134` is the canonical Phase-B v1 evidence for `STRAT-SPEC-0003` /
  `VM-0003` / `SWEEP-PLAN-0003`, with denominator `8`, `8` result rows, and
  `8` successful runner completions.
- The Phase-B trial screen records `RP-7134` as valid deterministic evidence
  and `NO-GO` under the frozen screen.
- The Phase-B v1 failure decomposition classifies the dominant aggregate
  failure mode as `fundamental gross-negative expectancy`.
- `RP-7134` reduced churn and explicit cost versus `RP-7520`, but every
  `RP-7134` row still had near-terminal net loss, near-terminal drawdown,
  negative Sharpe, and negative gross-return approximation.

Inference:

- The first Phase-B fade family did not fail only because of cost or lack of
  throttle.
- The next controlled lab hypothesis should change the economic premise rather
  than keep optimizing a centerline fade.

Decision:

- Deprioritize BTCUSDT 15m centerline mean-reversion fading for the next
  design package.
- Use a with-move trend/momentum design as the next reviewable hypothesis
  family.

This does not claim trend/momentum is profitable, ranked, ready, or tradable.
It only identifies a narrow next lab design surface.

## C. Intended hypothesis family

Primary hypothesis family: both-direction SMA crossover trend continuation.

Economic rationale:

- A fast moving average crossing a slower moving average is a simple
  with-move continuation trigger. It attempts to hold exposure in the direction
  of a local trend transition rather than betting on a snapback to a centerline.
- The design is toolbox-driven because it uses already merged closed
  vocabulary: `sma`, `crosses_above`, `crosses_below`, side-labeled
  both-direction entry/exit groups, optional trend confirmation conditions, and
  a fixed entry throttle.

Long/short symmetry:

- Long entry: fast SMA crosses above slow SMA, optionally with close above a
  trend SMA in the same long-side entry group.
- Short entry: fast SMA crosses below slow SMA, optionally with close below a
  trend SMA in the same short-side entry group.
- The design should remain symmetric unless Main/Karl separately decide that a
  BTC long-only or short-only research question is warranted. No one-sidedness
  is selected here.

Entry shape:

- Use explicit side-labeled `entry_logic.direction = "both"` groups.
- Long side requires `fast_sma crosses_above slow_sma`.
- Short side requires `fast_sma crosses_below slow_sma`.
- Optional trend confirmation is side-specific inside the entry groups, not in
  shared `filters.groups`, because current both-direction compiler filters are
  shared across both sides and reject side labels.

Exit shape:

- Long exit on `fast_sma crosses_below slow_sma`.
- Short exit on `fast_sma crosses_above slow_sma`.
- A max holding period is expressible but rejected for the default first design
  because it would add another timing hypothesis before the crossover shape is
  reviewed.

Trend/filter shape:

- Default includes side-specific trend confirmation inside each entry group:
  long requires `close > trend_sma`; short requires `close < trend_sma`.
- No separate volatility regime filter is selected for the first design.

Throttle/frequency control:

- Use fixed `entry_logic.entry_controls.min_bars_between_entries`.
- Do not sweep throttle unless a future package adds or confirms VM/Sweep Plan
  binding for entry controls.

Cost and churn expectations:

- Crossovers should usually trade less often than continuous threshold fade
  triggers, but this is an expectation to measure, not a claim.
- The future screen must compare trade count and explicit cost burden to
  prior Phase-B evidence without winner-only retention.

Why this is not another fade:

- The entry trigger follows a directional moving-average transition.
- The design does not enter because price is far from an average and does not
  target reversion to a centerline.
- Exits are opposite-signal invalidations, not centerline recapture exits.

Rejected/deferred options:

- Fallback if the primary were blocked: use a level-state SMA continuation
  shape with long entry when `fast_sma > slow_sma`, short entry when
  `fast_sma < slow_sma`, and exits on the opposite inequality. This fallback
  uses older `gt`/`lt` vocabulary but is not selected because current
  `crosses_above` / `crosses_below` support gives a cleaner event trigger.
- Breakout channel / Donchian continuation is deferred because current merged
  compiler/catalog vocabulary does not expose rolling high-low or channel
  breakout primitives.
- Trend-aligned pullback continuation is rejected for this package because it
  risks smuggling the failed fade premise back into the next design.
- Momentum-strength slope confirmation is deferred because no slope primitive
  is currently confirmed in the closed compiler vocabulary.

## D. Closed-spec shape sketch

Design intent only. This is not a frozen Strategy Spec, not a canonical
artifact, not a Variant Manifest, not a Sweep Plan, and not executable
authority.

Sketch:

```text
entry_logic.direction: both

parameters:
  fast_lookback_bars: integer, future finite axis
  slow_lookback_bars: integer, future finite axis, constrained > fast
  trend_lookback_bars: integer, future finite axis, optional/default fixed
  min_bars_between_entries: fixed literal unless future A3 sweep binding exists

long entry group:
  side: long
  all:
    SMA(close, fast_lookback_bars) crosses_above SMA(close, slow_lookback_bars)
    close > SMA(close, trend_lookback_bars)

short entry group:
  side: short
  all:
    SMA(close, fast_lookback_bars) crosses_below SMA(close, slow_lookback_bars)
    close < SMA(close, trend_lookback_bars)

long exit group:
  side: long
  all:
    SMA(close, fast_lookback_bars) crosses_below SMA(close, slow_lookback_bars)

short exit group:
  side: short
  all:
    SMA(close, fast_lookback_bars) crosses_above SMA(close, slow_lookback_bars)
```

Future finite axes should preserve the `<= 5` free-parameter posture. A
reasonable pre-registration surface would likely start with fast, slow, and
optional trend lookbacks only, plus fixed throttle.

## E. Compile-feasibility note

Answer: YES, the intended primary design can be expressed with current merged
schema/compiler/catalog vocabulary, provided a future full Strategy Spec uses
the required artifact fields and a finite parameter grid with valid lookback
constraints.

Confirmed supported from repo inspection:

- Strategy Spec operator enum includes `crosses_above` and `crosses_below`.
- `tools/research_runner/spec_signal_compiler.py` supports `crosses_above`
  and `crosses_below` with immediately prior/current bar semantics.
- Indicator catalog and compiler builtins include `sma`, `ema`, `atr`, and
  `stddev`.
- Indicator lookbacks may bind through `bars_parameter_ref`.
- `entry_logic.direction = "both"` is supported through explicit side-labeled
  long/short root entry groups.
- Side-labeled exit groups are supported for both-direction specs.
- Shared `filters.groups` support trend/regime-style entry gates, but are
  unlabeled/shared under both-direction compiler behavior.
- Fixed `entry_logic.entry_controls.min_bars_between_entries` is supported.
- `exit_logic.max_holding_period` is supported but not selected here.
- `z_score` composed operands are supported, but not needed for this primary
  crossover design.

Unsupported or uncertain for this design:

- No ATR-stop, fixed stop-loss, trailing stop, or intrabar stop-consumption
  primitive is confirmed.
- ATR exists as an indicator series, but that is not an ATR-stop exit
  mechanism.
- No slope or momentum-strength primitive is confirmed.
- No rolling high-low / Donchian / breakout channel primitive is confirmed.
- No current evidence confirms VM/Sweep Plan axis binding for
  `entry_controls.min_bars_between_entries`; fixed literal throttle is safe.
- Side-specific filters in `filters.groups` are not supported for both
  direction; side-specific trend confirmation should live inside side-labeled
  entry groups.

Compile probe:

```text
Command: in-memory synthetic probe using C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe
Result: COMPILE_PROBE_PASS
Output: unique_values=0.0,1.0; nonzero_count=4
```

The default `python` on PATH lacked `pandas`, so the probe was rerun with the
repo virtualenv. The probe wrote no files and created no canonical artifact.

## F. Primitive-gap list

Required before pre-registration:

- Finite parameter-axis decision for fast/slow/trend lookbacks, including
  constraints that prevent invalid `fast >= slow` combinations.
- Decision whether `trend_lookback_bars` is an axis or fixed literal.
- Decision whether fixed `min_bars_between_entries` is part of the Strategy
  Spec or deferred from the first pre-registration.

Optional / future improvement:

- ATR-stop or fixed stop-loss primitive. Not required before first
  pre-registration if Main/Karl accept opposite-signal exits as the first
  controlled design.
- A3 throttle sweep binding if throttle should be swept rather than fixed.
- Slope / momentum-strength primitive for stronger continuation confirmation.
- Volatility regime filter, likely using existing `stddev`/`atr` comparisons
  first if a future design needs it.
- Breakout channel / rolling high-low primitive for Donchian-style breakout
  designs.

Rejected for now:

- ATR-stop as a blocker for this first momentum pre-registration. The primary
  design can be honestly tested with opposite-signal invalidation exits. A stop
  may be valuable later, but requiring it now would broaden this design beyond
  the smallest non-fade hypothesis.
- Trailing stop. It requires stateful stop semantics and likely runner/backtest
  design beyond this package.
- Rolling channel breakout. The current closed vocabulary does not provide the
  required high-low reference operation.
- Slope confirmation. No closed slope primitive is confirmed.

ATR-stop decision:

- ATR as an indicator is available.
- ATR-stop as an executable risk exit is not confirmed.
- The selected crossover continuation design does not require ATR-stop before
  first pre-registration if Main/Karl accept that the first test is about
  opposite-signal continuation/invalidation, not stop-managed trend following.

## G. Future success-screen framing

A future pre-registration should define operational criteria without locking
thresholds in this docs-only design.

The screen should measure:

- Denominator: complete pre-registered population retained; no
  successful-only, winner-only, or post-hoc cleanup denominator.
- Cost: net-of-cost metrics, explicit fees/slippage/funding burden, and
  cost-to-initial-equity compared with `RP-7134` and `RP-7520`.
- Churn: trade count distribution and percent of rows above a future churn
  ceiling; not just best-row frequency.
- Performance: population-level net return, Sharpe, and positive-row counts.
- Drawdown: population-level max drawdown and tail-row behavior.
- Sensitivity: axis-span checks across fast/slow/trend lookbacks, with
  invalid combinations retained or excluded only by pre-declared rules.
- Robustness: C3/DSR posture if the future package has required trial-accounting
  inputs; otherwise explicitly mark not evaluable and do not fabricate DSR.
- Comparability: preserve dynamic equity target leverage at `target_leverage=1`
  unless a later package explicitly changes the measurement model.

Open decision:

- Main/Karl must decide the exact GO / NO-GO thresholds during future
  pre-registration. This design should not lock them prematurely.

## H. Future pre-registration shape

A future `WP-PHASEB-MOMENTUM-PREREG-01` would freeze:

- Strategy Spec id to be assigned later.
- Both-direction SMA crossover continuation Strategy Spec body.
- Variant Manifest axes for fast/slow/trend lookbacks, with invalid
  combination handling declared before execution.
- Sweep Plan denominator and selected variant set.
- Cost, sizing, slippage, funding, liquidation, and data-slice assumptions.
- BTCUSDT 15m OHLCV D4/D4A data lineage unless Main/Karl choose a different
  allowed timeframe before pre-registration.
- Fixed throttle value, unless A3 sweep binding is separately authorized.
- Success screen thresholds and denominator retention rules.
- Explicit statement whether stop-loss/ATR-stop is absent, optional metadata,
  or a prerequisite. Under this design, absent/opposite-signal exit is the
  default.

This package creates none of those artifacts.

## I. Decision surface

Main/Karl options:

1. Proceed to a momentum pre-registration using the SMA crossover continuation
   design, with no ATR-stop prerequisite and fixed throttle.
2. First build a required primitive such as ATR-stop only if Main/Karl decide
   stop-managed trend following is essential before the first momentum trial.
3. Revise the design, for example by using EMA instead of SMA or removing the
   trend confirmation condition.
4. Pause strategy hypotheses and prioritize tooling such as VERIFY-02 or other
   integrity/runway work.

Recommended default for review: Option 1, because it is the narrowest
non-fade design that current merged closed vocabulary can express today.

## Boundary recap

- Strategy Spec created: NO.
- Variant Manifest created: NO.
- Sweep Plan created: NO.
- Canonical result population written: NO.
- Existing result population changed: NO.
- Compiler/schema/catalog/lib/runner changed: NO.
- Walk-forward/candidate/paper/live/runtime authority created: NO.
