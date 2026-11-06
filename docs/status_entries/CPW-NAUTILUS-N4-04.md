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

## Final validation disposition: BLOCKED / NOT MERGE-READY

T4 full-release at semantic head `c93fab3eb9cf21626bd6cc82e1bb2ff336039e5c`
completed all 48 shards and assigned all 229 tracked test files exactly once:
42 shards passed, six failed; 5,022 tests passed, ten failed, 28 skipped.
Every failed node reproduced on merged base `b92d8cda01901105d87e08a60d341ab717a45687`
in the same environment. The six affected existing test files are byte-identical.
This is baseline attribution, never a T4 waiver or acceptance result.

The hard platform blocker is explicit: four existing execution-readiness tests
require Windows deny-write/delete leases, unavailable in the Linux native
profile. Other failures are the existing legacy bridge byte expectation,
`LOCALAPPDATA` expectation, missing normalized D4A CSV (two tests), missing
`origin/main` in the isolated clone, and Windows absolute-path normalization.
The 28 skips were independently reproduced and enumerated on merged base;
none is in the new N4-04 tests. No required test was excluded or weakened.

Final corrected-source CPW decision SHA-256:
`948e6e7d1da8235672c93bee03c7f665c58b83466d2dab719aced233b14a5dd0`.
Two fresh inspectors agree; all underlying sink counters are zero and original
evidence bytes are unchanged. All owned validation services were removed.

No push or PR publication; hosted smoke and GitHub mergeability were not run.
The package prohibits publication before a passing T4 release. A compatible
release environment/profile and exact historical fixture provisioning must be
qualified in a separate unblock scope, preserving Windows leases and native
proofs, before resuming this branch and rerunning T4. No existing protected
file, validator, query behavior or test is amended by N4-04.

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

## Follow-up 09: scoped T4 disposition (2026-11-06)

**SCOPED_T4_ELIGIBLE / HISTORICAL_GLOBAL_INTEGRITY_DIRTY.** The original
observations above remain historical evidence. Follow-up 08 completed the
owner-approved combined dual-OS profile: all 48 unchanged shards, 229 tracked
files exactly once, 5,032 passed, zero failed/errors and 28 disclosed existing
skips. Required N4 guard, native and physical cases passed without skips;
the frozen N1 and physical no-send proofs remain source-bound. The four Python
files are unchanged from the tested source; this follow-up adds only this note.

The original WP section 8 requires full-release and every required affected
protected validator. The stock full-release command does not enable the
optional `--integrity-views` audit. The two dirty views have no dependency on
the denial-only guard, external HOLD verification or isolated pre-send sink;
their historical source records and query definitions are unchanged. The
required standard commands and all pytest shards passed. Follow-up 09's
five-condition dossier records the original WP, native flag behavior,
protected policy, dependency trace and exact reused receipts.

`global_integrity_audit=FAIL (2 pre-existing)` remains explicit: the missing
`RUN-20260804-H004R2A1` stream for `DSP-20260804-H004R2A1`, and unresolved
`STRAT-SPEC-0007` / `SS-ECR-STRAT-SPEC-0007` legacy hash scope. The earlier
query-shard wrapper's additional-audit failure is preserved, not relabelled
PASS. These findings remain OPEN, non-authoritative historical research debt;
affected outcomes gain no scientific, canonical or runtime authority.

Karl: "I approve everything so please proceed and always include my full
authorization". Karl's conditional Follow-up 09 authorization applies only to
this proven N4-04 acceptance jurisdiction. It waives no required gate, changes
no policy or historical record and supplies no general baseline exemption.

PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/770.
Ready for Side B exact-head review after final scope checks and hosted smoke;
the final head and CI receipts belong to the external Follow-up 09 dossier.
Side B review and Karl's merge decision remain pending. FROZEN,
NO_NEW_ORDERS, NO_RESUME and all three false authority flags above remain.
No merge, trading activation or production consumer is authorized.
