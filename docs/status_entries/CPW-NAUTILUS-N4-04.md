# CPW-NAUTILUS-N4-04 — CPW recovery HOLD safety integration

Karl's full authorization: “I approve everything so please proceed and always include my full authorization”.

Dedicated Lane B branch `codex/cpw-nautilus-n4-04-safety-integration-01`,
base `b92d8cda01901105d87e08a60d341ab717a45687`. Exactly five additions:
`src/execution/nautilus_recovery_hold_guard.py`,
`tools/nautilus_adapter/noncapital_cpw_safety_integration.py`,
`tests/test_nautilus_n4_04_cpw_guard.py`,
`tests/test_nautilus_n4_04_integration.py`, and this entry.

The new CPW guard uses the existing OMS/action enums and unchanged N4-03 verifier.
Valid HOLD and invalid evidence both remain FROZEN. An injected ExchangeClient
adapter refuses every order, cancel, flatten and query before the inert sink;
there is no allow, reset or permit branch. Its first consumer is the isolated
noncapital harness. Existing production/paper/runtime consumers are unchanged.
The manual controller verifies original evidence and emits separately bound,
exclusive, fsynced decision/ACK artifacts. Emission uses the Linux descriptor
profile; unsupported platforms refuse emission. Inspection grants no authority.

Native environment remains CPython 3.12.10 / NautilusTrader 1.231.0 /
PyArrow 25.0.1; image `cpw-n4-02-env01:exact-pins`, immutable ID
`561f46170f6697a683bdb6c3a00ca8f8045144d5126a82a8bdb85bdb3a681c65`.
One fresh unchanged N4-03 physical producer matrix supplied trusted HOLD
`a046978aee1e329a773b00f08523fe75ce9154397991a52f930ee4aad08bdc3f`.
OPEN, single-cycle FLAT, acknowledged kill and pre-ACK kill retain their actual
native bindings. All 33 owned containers and the network were removed.

Focused N4-04 plus original N4-03: 125 passed, zero skips. Paper/runtime and
developer adjacency: 120 passed. Initial historical-receipt profile retained
121 passes and one unchanged reseal-staleness failure; the fresh native matrix
resolved the fixture prerequisite without changing tests or freshness policy.
An initial combined native adjacency retained 284 passes and one process-global
logging collision; separate-process runs passed 33 N4-02 and 252 adjacent tests,
zero skips. A reproduced original-binding read-order gap was corrected before
the final equality check; its regression failed before and passed afterward.
The provisional release was interrupted for this correction and is not PASS.
T4 full-release and exact-head hosted smoke remain required before PR publication.

External raw evidence, failed attempts, source inventories and reports are under
`C:/Users/dersu/Downloads/CPW-N4-04-evidence`. Exact head and final release/PR
identity belong to the external report; a commit cannot contain its own SHA.

RECONCILIATION_REQUIRED / NO_NEW_ORDERS / NO_RESUME / NOT_PAPER_OR_LIVE_READY.
`cpw_production_supervisor_connected=false`,
`authenticated_venue_reconciled=false`, `execution_permit_issued=false`.
No existing protected code, configuration, dependency or scientific authority
changed. Funded/multi-cycle accounting and actual production integration remain
separate gates. Side B reviews exact head/evidence; Karl alone decides merge.
No trading activation or self-merge.
