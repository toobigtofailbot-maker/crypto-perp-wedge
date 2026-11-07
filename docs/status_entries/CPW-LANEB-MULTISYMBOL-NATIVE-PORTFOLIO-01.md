# CPW-LANEB-MULTISYMBOL-NATIVE-PORTFOLIO-01

Baseline is PR #772 at `4822cc303cce790ba792d8a6e41829ff17f35419`.
P1 adds opt-in offline portfolio fixture execution through the paper trader,
with a single native TradingNode, CPWSIM margin account and netting cache.
The pinned Binance provider parses verified public USD-M instrument metadata
offline. CPW owns request admission, fixture risk veto, and HOLD. Nautilus
owns order, fill, position and account effects.

Recovery is read-only, supports a single uninterrupted position lifecycle
per symbol, and refuses resized and reopened histories. The physical test
compares supported pre-crash orders, fills, positions and account state to a
fresh process under the read-only ACL. The native reopened-position snapshot
is missing after reload in the observed expanded case. Fixture quotes and fees
are simulated. Funding, venue reconciliation, and exchange execution remain
outside this proof.

The external Lane B report carries the exact validation results and limitations.
