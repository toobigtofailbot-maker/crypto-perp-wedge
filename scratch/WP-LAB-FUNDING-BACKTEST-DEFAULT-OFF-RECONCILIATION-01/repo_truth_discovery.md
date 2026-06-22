# Repo-Truth Discovery

## Current Default Funding Behavior

Before this package, `lib/backtest.py::run_backtest()` always iterated the supplied funding events and applied eligible events to an open position. There was no funding enable/disable argument, so non-empty funding input meant funding was implicitly on.

## Where Funding Is Applied

Funding is applied in the bar loop before close-marked unrealized PnL and before the current bar's next-open fill handling. Eligible funding timestamps satisfy `previous_bar_timestamp < funding_timestamp <= current_bar_timestamp` while a position is open.

## Tests Expecting Funding By Default

`tests/test_backtest.py` contained funding fixtures and direct calls that omitted a funding switch while expecting non-zero `funding_paid`, including the hand-calculated long fixture, entry-price and mark-price notional fixtures, short credit behavior, multiple-event alignment, size scaling, dynamic sizing, consolidated realism assumptions, and the funding bar-path regression.

## Sign Convention

For a positive funding rate, longs pay and shorts receive. Equity cashflow is `-position * funding_rate * funding_notional`; `funding_paid` is the negative of that cashflow, so a paid cost is positive and a received credit is negative.

## Alignment Convention

Funding events apply in the left-open, right-closed interval `(previous_bar_timestamp, current_bar_timestamp]`. An event at the position's entry-bar timestamp remains excluded because funding is processed before that bar's fill.

## Metadata Fields

Before this package, `BacktestResult.params` recorded `funding_notional_mode` (`entry_price` or `mark_price`) but no funding enable/disable mode. `BacktestResult.funding_paid` records net funding paid, with positive values representing cost.

## Affected Fixtures and Artifacts

The affected executable fixtures are in `tests/test_backtest.py`. Canonical Result Populations under `research/result_populations/` use zero-funding runner inputs and are not package edit targets. The Result Population schema, validator, query layer, runner, and canonical Result Populations require no change for the narrow default-off reconciliation.
