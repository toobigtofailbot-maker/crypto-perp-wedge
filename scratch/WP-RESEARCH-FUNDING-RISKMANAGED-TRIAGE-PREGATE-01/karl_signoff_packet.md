# Karl Sign-Off Packet

## Selected Hypothesis

`H-FUNDING-FADE-RISKMANAGED-01`: prior funding positioning-fade signal, unchanged, with an a-priori offline risk layer.

## Chosen Window

Evaluation window: `2024-01-01T00:00:00Z` inclusive through `2025-01-01T00:00:00Z` exclusive.

Warmup input must begin no later than `2023-07-05T00:00:00Z` for the 180-day funding percentile.

## Frozen Risk-Control Ranges

- Same-window no-ATR control: 36 rows.
- ATR stop: lookback `14`, multipliers `2.0` and `3.0`, close-evaluated at bar close from next-bar-open entry reference.
- Sizing: `dynamic_equity_target_leverage`, fixed `target_leverage=1.0`.
- Existing signal/max-hold grid remains frozen: 30/90/180d lookbacks, two tail pairs, two exit modes, max holds 16/32/96.

## Denominator Size

108 planned rows:

- 36 no-ATR comparison rows;
- 72 ATR-stop risk-managed rows.

All rows must be reported.

## Why No Outcome-Peeking Occurred

This package ran no strategy, backtest, sweep, or sidecar. The window and ranges were selected from repo truth, calendar/regime coverage, existing primitive capability, and risk-control rationale, not from risk-managed strategy results.

## How The Result Will Be Judged

GO to Stage 2 requires a complete denominator, positive median net return, median drawdown `<= 35%`, worst-row drawdown `< 50%`, at least `20` absolute percentage points median drawdown improvement versus same-window no-ATR rows, evidence across neighboring grid cells, and real-runner reconciliation.

NO-GO if drawdown remains screen-failing, risk controls only kill returns, only one isolated cell passes, denominator is incomplete, sidecar and real-runner diverge materially, or funding-PnL/accounting changes are required.

## Stage 1 Is Allowed To Do

- Produce scratch-only triage evidence after approval.
- Use manually authored scratch runner inputs, or a separately authorized adapter-extension route.
- Optionally use vectorbt as non-canonical preview only.
- Reconcile any preview to the real runner before a continue decision.

## Stage 1 Is Not Allowed To Do

- Retune the funding signal.
- Write canonical Result Populations.
- Write candidate lifecycle records.
- Declare approval, promotion, readiness, ranking, or recommendation.
- Touch paper/live/runtime, OMS, risk, reconciliation, order, broker, exchange, funding accounting, configs, private providers, or API credentials.

## No-Run Statement

No strategy run has occurred in this package.
