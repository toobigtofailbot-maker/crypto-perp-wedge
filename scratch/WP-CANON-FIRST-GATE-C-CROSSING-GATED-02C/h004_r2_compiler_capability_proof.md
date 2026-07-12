# H-004-R2 compiler capability proof

- PASS — EMA built-in exists in the merged indicator catalog/compiler.
- PASS — ATR built-in and close-evaluated ATR-stop support exist.
- PASS — `crosses_above` and `crosses_below` are supported.
- PASS — fixed entry cooldown is supported by `entry_controls.min_bars_between_entries`.
- PASS — ATR multiplier accepts `{"parameter_ref":"atr_multiplier"}`.
- PASS — maximum holding accepts `{"parameter_ref":"max_holding_bars"}`.
- PASS — exactly four free parameters, below the five-parameter cap.
- PASS — schema-native Strategy Spec validation passed without modifying implementation, schema, catalog, or compiler files.
- PASS — compile-only validation used 260 synthetic completed daily OHLCV rows and default parameter values; it did not run a backtest or research execution.

Current compiler conventions recorded in the spec: ATR is captured from the entry signal bar and applied to the next-open pre-fee/slippage entry reference; stops evaluate close at bar close. Maximum holding checks `held_bars >= bound`; the counter begins on the signal/position state bar. Any signal, ATR, or time exit may flatten, and the compiler prevents same-bar reversal under this configured exit posture.
