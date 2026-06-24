# H-FUNDING-RATE-POSITIONING-FADE-01

Economic rationale: Extreme perpetual `funding_rate` is a positioning/crowding signal. Strong positive funding implies long-side crowding; strong negative funding implies short-side crowding. Extreme crowding may mean-revert after positioning stress. A contrarian price strategy using `funding_rate` therefore tests a data-derived mechanism not covered by prior price-only NO-GO results.

Direction: positive extreme => short; negative extreme => long.

Allowed family: rolling funding-rate percentile lookbacks of 30d, 90d, and 180d; entry absolute percentiles 0.90 and 0.95; exit below absolute percentile 0.50 or fixed maximum hold; maximum holds 16, 32, and 96 bars; contrarian only.

Forbidden post-result changes: threshold search, trend-following direction, future funding observations, use before observability, winner narrowing, denominator shrinkage, funding-payment claims, or carry-P&L claims.

This pre-registration was recorded before any strategy result. No strategy run occurred because current repo semantics cannot express the family honestly.
