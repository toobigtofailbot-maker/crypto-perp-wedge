# H-004-R2 material-difference proof

H-004 is the concluded daily dual-SMA trend baseline with a rolling realized-volatility percentile regime filter, continuous crossover-style trend exposure, four historical parameter roles (`fast_ma`, `slow_ma`, `rv_lookback`, `rv_percentile`), no cooldown/ATR/time-exit combination, a NO-GO decision, and an archive recommendation.

H-004-R2 is a new preregistered question. It uses an EMA trend regime, and its entry event is close crossing back through a short pullback EMA after a countertrend pullback while fast EMA and price remain on the correct side of fixed EMA(200). Distinct pullbacks can create repeated continuation entries after the fixed 10-bar cooldown. It removes the realized-volatility percentile filter and adds ATR(14) and bounded maximum-holding exits. Its four parameter roles are pullback EMA horizon, trend-fast EMA horizon, ATR multiplier, and maximum-holding bars.

- Not renamed H-004: indicator type, regime definition, entry event, re-entry topology, exit topology, and all four parameter roles differ.
- Not H-004 plus a stop: H-004-R2 replaces continuous dual-SMA crossover exposure with a pullback-recovery cross inside an established EMA trend.
- New economic mechanism: temporary countertrend pullbacks followed by recovery may offer continuation entries while slow information diffusion and persistent positioning sustain multi-week momentum.
- New entry event: completed-bar close crosses the pullback EMA, gated by fast EMA versus EMA(200) and close versus EMA(200).
- New risk/staleness containment: fixed 10-bar cooldown, parameterized ATR(14) exit, and parameterized maximum holding exit.
- Prior evidence does not answer this question: H-004 tested dual-SMA plus volatility-regime exposure, not repeated EMA pullback recoveries with cooldown and ATR/time exits.

No likely-success claim is made. H-004 remains a concluded NO-GO.
