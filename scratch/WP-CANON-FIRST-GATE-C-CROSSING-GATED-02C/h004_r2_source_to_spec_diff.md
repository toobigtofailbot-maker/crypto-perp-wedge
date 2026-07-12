# H-004-R2 source-to-spec classification

- Exact Karl-authorized source: BTCUSDT perpetual, 1d, both directions, same-bar three-condition entries, pullback recross exits, ATR(14), parameterized max holding, cooldown 10, four exact parameter sets/defaults, EMA ordering, 1x baseline, 4 bps fees, 2 bps slippage, funding, and every exclusion.
- Deterministic normalization: prose was translated to schema-native side-labelled groups, `indicator_ref` EMA operands, `parameter_ref` exit bindings, bounded parameter objects, and the existing realism enums.
- Repo capability fact: `ema` and `atr` catalog built-ins; `crosses_above`/`crosses_below`; `entry_controls.min_bars_between_entries`; parameterized ATR multiplier; parameterized maximum holding.
- Fixed values: EMA(200), ATR(14), cooldown 10, 1.0 leverage/notional assumption, fees, slippage, and existing offline funding convention are not free parameters.
- Omitted unsupported claims: no performance likelihood, intrabar stop, guaranteed stop fill, take profit, trailing stop, adaptive sizing, live data, queue, execution, candidate, promotion, runtime, paper, or live authority.

The generic formalizer parameter names are not used as the final contract. The frozen Strategy Spec contains exactly the four authorized parameter names and no hidden degree of freedom.
