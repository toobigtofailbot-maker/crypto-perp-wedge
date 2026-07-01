# Concluded Family Inventory

Package: `WP-LAB-REAL-TRAFFIC-FRESH-REPLACEMENTS-01`

The machine-readable inventory is `concluded_family_inventory.json`. This markdown view summarizes the freshness constraints used for replacement screening.

| Family / RP | Source | Archetype | Timeframe | Status | Freshness constraint |
| --- | --- | --- | --- | --- | --- |
| `H-001` | candidate registry / REP / DEC | funding directional | 4h | CONCLUDED / NO-GO | No funding-directional retunes. |
| `H-002` / `REP-0003` | `REP-0003` | Donchian trend following | 4h | CONCLUDED / NO-GO | No simple Donchian retunes. |
| `H-003` | registry / REP / DEC | Bollinger mean reversion | 1d | CONCLUDED / NO-GO | No generic price-band fade retunes. |
| `H-004` | registry / REP family | MA trend plus volatility regime | 1d | CONCLUDED / NO-GO | No simple MA trend/regime retunes. |
| `H-005` | registry / REP family | MACD momentum | 1h | CONCLUDED / NO-GO | New momentum must not copy MACD/price-structure. |
| `H-006` | registry / REP family | Bollinger squeeze breakout | 30m | CONCLUDED / NO-GO | Breakout replacements must not be Bollinger squeeze retunes. |
| `H-007` | registry / REP | funding plus momentum | 4h | CONCLUDED / NO-GO | No funding-confirmed momentum. |
| `H-008` | registry / REP | premium-confirmed momentum | 1h | CONCLUDED / NO-GO | No premium-confirmed momentum. |
| `H-009` | registry / REP | MTF trend alignment | 30m | CONCLUDED / NO-GO | No MTF trend-alignment retunes. |
| `H-010` | registry / REP | basis/premium mean reversion | 4h | CONCLUDED / NO-GO | No derivative-stream basis/premium fades. |
| `H-012` / `REP-0032` | `REP-0032` | 15m Donchian with funding filter | 15m | CONCLUDED / NO-GO | No Donchian/funding-filtered trend retunes. |
| `RP-2134` / `RP-4492` | RP + `STRAT-SPEC-0001` | long-only SMA-distance | 15m | NO-GO evidence family | No SMA-distance/band centerline fades. |
| `RP-6688` / `RP-7520` | RP + `STRAT-SPEC-0002` | both-direction SMA-band fade | 15m | NO-GO evidence family | No SMA-band fade retunes. |
| `RP-7134` | RP + `STRAT-SPEC-0003` | z-score trend-gated fade | 15m | NO-GO evidence family | No z-score/SMA/stddev fade retunes. |
| `RP-2592` | RP + `STRAT-SPEC-0004` | SMA crossover continuation | 15m | NO-GO evidence family | No SMA crossover continuation. |
| `RP-3731` | RP + `STRAT-SPEC-0005` | SMA crossover plus ATR stop | 15m | NO-GO evidence family | ATR stop does not make SMA crossover fresh. |
| `RP-6236` | RP + `STRAT-SPEC-0006` | 4h SMA crossover plus ATR stop | 4h | NO-GO evidence family | Higher-timeframe SMA crossover is still constrained. |
| ORB family | `WP-ONLINE-ORB-15M-PREREG-01` | UTC opening-range breakout retest | 15m | prereg/scratch poor, not canonical | PR #598 `HYP-002` duplicate rejected. |
| SMA freshness-blocked attempt | `WP-RESEARCH-EDGE-SMA-FAMILY-01` | SMA/stddev duplicate | 15m | BLOCKED | Freshness check failed before bridge execution. |
| Funding carry/fade scratch families | funding status entries | funding carry/fade/risk-managed | mixed | concluded/blocked scratch context | No funding replacements in this batch. |

Decision: the replacement packet screens out ORB, SMA crossover, z-score/SMA-band fade, funding, and Donchian retunes. Broad breakout, VWAP-distance, and session-filtered continuation are only accepted where their trigger/economic rationale is structurally distinct from these entries.
