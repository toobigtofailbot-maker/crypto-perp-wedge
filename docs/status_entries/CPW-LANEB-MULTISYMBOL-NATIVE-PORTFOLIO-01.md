# CPW-LANEB-MULTISYMBOL-NATIVE-PORTFOLIO-01

P1 builds on PR #772 and is based on main at `7c6b8e58d1066fd657957a43f46298fb4e0b87d4`.
P1 adds opt-in offline portfolio fixture execution through the paper trader,
with a single native TradingNode, CPWSIM margin account and netting cache.
The pinned Binance provider parses verified public USD-M instrument metadata
offline. CPW owns request admission, fixture risk veto, and HOLD. Nautilus
owns order, fill, position and account effects.

Karl's Option 1 limits P1-G to read-only recovery of a single uninterrupted
position lifecycle per symbol, with a possible close, alongside multi-cycle
in-process execution. The physical test compares supported pre-crash native
orders, fills, positions and account state to a fresh process under a read-only
ACL. A separate physical seven-fill case requires explicit HOLD refusal, zero
execution effects and unchanged durable bytes. HOLD leaves the producer frozen
with NO_NEW_ORDERS and NO_RESUME.

Complete multi-cycle historical recovery is deferred. In the prior seven-fill
counterexample, native reload lost a closed BTC cycle and disagreed on
archive-sensitive realized PnL by 0.08009996 USDT. Full economic history and
authenticated venue reconciliation remain future operational-readiness gates.
Fixture quotes and fees are simulated. Funding and exchange execution remain
outside this proof.

The external Lane B report carries the exact validation results and limitations.
