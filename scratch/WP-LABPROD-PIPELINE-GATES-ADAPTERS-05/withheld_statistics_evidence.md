# Withheld Statistics Evidence

## Current Withheld Fields

Current product runner output does not include committed WFO/OOS windows. The WFO/OOS adapter therefore marks these fields as withheld:

- `mean_oos_sharpe`;
- `minimum_oos_sharpe`;
- `maximum_oos_drawdown`;
- `walkforward_split_periods`;
- `purge_bars`;
- `embargo_bars`.

## Representation

The adapter records:

```text
withheld_missing_walkforward_oos_inputs
```

The adapter does not:

- fill withheld statistics with zero;
- fabricate estimates;
- silently drop withheld rows;
- turn withheld WFO/OOS fields into pass/fail authority.

## Downstream Caveats

The existing robustness and candidate-review agents preserve missing diagnostic inputs:

- missing fold/OOS inputs remain `missing_fold_inputs`;
- missing per-trade rows keep `fabricated_per_trade_data = false`;
- funding stress remains explicit as not applicable/missing/performed based on visible inputs.
