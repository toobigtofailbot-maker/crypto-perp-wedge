# H-FUNDING-FADE-RISKMANAGED-01 Pre-Run Triage Gate

## Status

This is a pre-run approval artifact for `H-FUNDING-FADE-RISKMANAGED-01`.

It freezes the Stage 1 triage design before any risk-managed funding-fade result is produced. No strategy run, backtest, sweep, canonical Result Population write, candidate lifecycle write, approval, promotion, paper/live/runtime action, funding accounting change, or private provider/API access occurred in this package.

## Fact

Current repo truth records `H-FUNDING-RATE-POSITIONING-FADE-01` as a scratch-only, non-canonical NO-GO under the tested price-PnL funding-rate signal interpretation. The prior run preserved the full 36-row denominator across rolling funding percentile lookbacks of 30, 90, and 180 days, symmetric 0.10/0.90 and 0.05/0.95 entry tails, two exit modes, and maximum holds of 16, 32, and 96 bars.

The prior failure mode was primary risk-screen failure: all 36 completed full-history rows exceeded the 20% drawdown screen, with full-history drawdown ranges of 85.68% to 100% for fixed max-hold and 80.72% to 100% for midline-or-max-hold. Funding payments were not wired and `funding_cost_mode` was off, so the evidence is not a funding-carry-PnL conclusion.

Current merged repo truth also contains:

- closed `exit_logic.atr_stop` Strategy Spec grammar and compiler handling;
- enabled `exit_logic.max_holding_period` parameter binding;
- offline runner support for opt-in `dynamic_equity_target_leverage`;
- a non-canonical vectorbt sidecar that may preview but cannot confirm results.

## Decision

Select `H-FUNDING-FADE-RISKMANAGED-01` as the first resumed bounded research-lab edge-search hypothesis because the prior funding-fade result had an interpretable, isolated failure mode: drawdown was extreme while the signal definition and full denominator were already frozen and visible.

The Stage 1 design tests whether an a-priori offline risk layer changes that failure mode. It does not retune the funding signal and does not claim funding-carry economics.

## Frozen Hypothesis

`H-FUNDING-FADE-RISKMANAGED-01` keeps the prior signal family fixed:

- direction: positive funding extreme implies contrarian short; negative funding extreme implies contrarian long;
- primary timeframe: BTCUSDT 15m;
- rolling funding-percentile lookbacks: 30d, 90d, 180d (`2880`, `8640`, `17280` 15m bars);
- symmetric entry tails: `0.10/0.90` and `0.05/0.95`;
- existing exit modes: `fixed_max_hold_only` and `midline_reversion_or_max_hold`;
- existing max-hold values: `16`, `32`, `96` bars;
- funding payments: not enabled for this Stage 1 price-PnL triage.

The new variable risk-control layer is limited to an ATR stop with fixed ATR lookback `14` and ATR multipliers `2.0` and `3.0`, plus control rows with no ATR stop for same-window comparison. Dynamic equity target leverage at `1.0` is fixed as the sizing measurement mode, not swept.

## Window

Stage 1 evaluation window is `2024-01-01T00:00:00Z` inclusive through `2025-01-01T00:00:00Z` exclusive.

Required input/warmup prefix begins no later than `2023-07-05T00:00:00Z` so the 180-day funding percentile can be available at the evaluation boundary without shortening the declared evaluation denominator.

The window was selected from calendar and market-regime coverage, not strategy return, Sharpe, drawdown, variant PnL, or winner cells. It is a completed mixed one-year period, not the most recent year by default and not a favorable backtest result selection.

## Denominator

Stage 1 planned denominator:

- 36 same-window no-new-risk-control comparison rows;
- 72 ATR-stop risk-managed rows (`36` frozen signal cells x `2` ATR multipliers);
- 108 total planned rows.

Every planned row must be reported. Winner-only reporting is forbidden. An isolated single-cell pass is an overfit signature, not a GO.

## Stop / Go Summary

GO to Stage 2 only if all of the following are true:

- full denominator is complete;
- at least one ATR-stop multiplier has median drawdown no greater than `35%` and worst-row drawdown below `50%` across the declared evaluation rows;
- that ATR-stop slice improves median drawdown by at least `20` absolute percentage points versus the same-window no-ATR comparison slice for the same signal cells;
- median net return for that ATR-stop slice remains positive and at least `4` ATR-managed rows have positive net return;
- the effect appears across at least two funding lookbacks and both entry-tail pairs, not only one isolated cell;
- real-runner reconciliation does not contradict any sidecar triage preview.

NO-GO if any of the following occur:

- denominator is incomplete;
- drawdown remains screen-failing under the thresholds above;
- risk controls reduce drawdown only by killing returns;
- only one isolated parameter cell passes;
- vectorbt and real runner materially diverge and the divergence cannot be explained before decision;
- funding-PnL/accounting changes are required to interpret the result.

## Boundary

This hypothesis is test traffic for the generic Side 12 lab, not a funding-specific lab pivot. The pattern is reusable: repo-truth discovery, frozen hypothesis, declared window, bounded risk layer, denominator preservation, real-runner reconciliation, and explicit stop/go criteria can be applied to other strategy families.

Stage 1 is allowed to produce scratch-only triage evidence after Karl approval. It is not allowed to write canonical artifacts, candidate lifecycle records, promotion/readiness claims, runtime/paper/live paths, OMS/risk/reconciliation/order/exchange paths, funding accounting changes, private provider/API calls, or autonomous execution authority.

## Open Question

The existing funding formalizer bridge still hard-codes the old two-exit funding adapter shape and does not by itself generate the ATR-stop risk-managed denominator. Stage 1 can still be expressed through manually authored scratch Strategy Spec / Variant Manifest / Sweep Plan inputs validated by the existing runner stack, or by a separately authorized adapter-extension package. The sign-off packet requires Karl to choose that execution route before any run.
