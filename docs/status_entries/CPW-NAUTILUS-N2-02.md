# CPW-NAUTILUS-N2-02 — Native Redis durability and restart characterization

**PARTIAL — not merge-ready. No PR, push, merge, activation, or ownership transfer.**
Native account/order/current-position persistence is genuine. Complete native
NETTING history and portfolio realized-PnL restoration fails on the pinned engine.

## Scope and provenance

Karl authorized this bounded T2 proof. Dedicated Lane B worktree:
`C:/Users/dersu/.codex/worktrees/cpw-nautilus-n2-02-lane-b/crypto-perp-wedge`.
Branch: `codex/cpw-nautilus-n2-02-native-restart-01`.
Refreshed base: `884483db2bf3d071bd87107a0854c18f4b4b8e9f` (#743 merged).
Initial open PR count was zero; later Lane A #745 has disjoint changed files.
Root checkout and other lanes remain unchanged.

Exactly four additions: private `tools/nautilus_adapter/native_cache_restart.py`,
`tests/test_nautilus_n2_02_native_cache.py`,
`tests/test_nautilus_n2_02_restart.py`, and this entry. No public export or
production consumer. Existing N1/N2-01 code, tests and lock remain unchanged.

Physical environment: established isolated CPython 3.12.10 / NautilusTrader
1.231.0. All 20 lock entries and installed native binaries/sandbox/cache/kernel
sources are checked against wheel RECORD. No dependency or native-source patch.
Existing Redis Python client 8.1.0 is used without installation. Requested model
and effort were GPT 6.1 Sol / HIGH; this chat cannot independently verify or
change those settings, so no verified-model claim is made.

Owned temporary Redis 7.4.2 container `cpw-n2-02-redis-20261022`, unique volume,
initial DBSIZE zero, bound only to `127.0.0.1:16482`. Official image
`redis:7.4.2-bookworm`, immutable repository digest
`sha256:fbdbaea47b9ae4ecc2082ecdb4e1cea81e32176ffb1dcf643d422ad07427e5d9`.
AOF enabled with `appendfsync always`; no shared Redis or Lane A service access.

## Actual native route and observations

TradingNode creates the real NautilusKernel/Redis cache and LiveExecutionEngine.
The native SandboxLiveExecClientFactory builds the offline N2PROOF client;
bounded local quotes and the engine's actual command/event queues produce fills.
This is a controlled kernel/engine bootstrap, not full TradingNode.run_async
startup, exchange synchronization, or a paper-runtime cutover.

Cache configuration uses `persist_account_events=True`, `use_instance_id=False`,
`flush_on_start=False`, JSON encoding and `load_cache=True`. Native Redis records
originate from execution, never journal replay or injected account snapshots.
The acknowledged checkpoint requires actual native event-ID read-back, required
record keys, stable record hashes and successful AOF status. The adapter's
`flush()` deletes data and is never used as a write-drain operation.

| Case | Native execution | Account equity / fees (USDT) | Reload |
| --- | --- | --- | --- |
| round_trip | 2 fills; 1 resting accepted/canceled order | 10009.916 / .084 | account, all orders, current position and native portfolio PnL conserved |
| reversal | 3 fills; 2 open/close cycles; 1 canceled order | 10029.836 / .164 | account, all orders and latest position conserved; historical snapshot/PnL lost |

Both cases repeat with identical normalized economic/order-event projections.
The immutable CPW LedgerState and PaperBroker without a ledger path provide
read-only equity/quantity/fee oracles. CPW spot-like cash is not asserted equal
to the native margin balance; CPW gross realized PnL is compared net of fees.

## Material native limitation — full acceptance fails

Measured reversal producer: native portfolio realized PnL **29.836 USDT**,
including one prior closed-position snapshot with realized PnL **9.916 USDT**.
Fresh native reload: that snapshot is absent and native portfolio realized PnL
is **19.92 USDT**. Account equity remains **10029.836 USDT**. The current
position object and all order/fill identities reload exactly; this does not
prove complete historical portfolio recovery.

Pinned source explains the observation: `ExecutionEngine._reopen_position()`
calls `Cache.snapshot_position()`, which stores a copied closed position in the
in-memory `_position_snapshots` map. Native cache loading restores ordinary
positions but does not repopulate that snapshot map. Optional snapshot-state
writes are a different API; no native history-loader proof is claimed.

The proof records both original and restarted native history. Reversal reload
emits `PARTIAL_NATIVE_HISTORY_LOSS` and exits **2**. Behavioral tests assert this
real limitation; passing characterization tests are not full WP acceptance.
No missing PnL is filled from a custom journal, synthetic snapshot or CPW ledger.

## Process recovery and refusal

Healthy stop and post-checkpoint TerminateProcess cases use actual separate OS
interpreters, fresh instance UUIDs, original retained manifests and unchanged
Redis hashes. The controller verifies Popen PID equals checkpoint producer PID
before killing only that owned handle. Windows venv launchers have a different
PID, so the crash controller directly uses the venv's pinned base interpreter
with its existing package directory.

Two independent post-crash restarts per scenario preserve current-state
identities without new economic effects. Native command/event counters remain
zero. Repeated read-only restart is allowed; every resume request is refused
with `RECONCILIATION_UNVERIFIED / NO_NEW_ORDERS`.

The pinned four sandbox status-report methods return None/empty. A separate
disposable native-client reconstruction resets the simulated account to 10000
USDT. Recovery therefore builds no execution client and never submits an order.
The valid-state namespaces remain unmodified during every negative control.
Corrupt/truncated/missing native records are rejected by trusted record hashes
before native deserialization; no native corrupt-record repair is claimed.

## Validation, traceability and next decision

Final focused characterization: **29 passed, zero skipped, 158.74s**. These
tests include the expected reversal history loss and exit-2 refusal; full WP
acceptance remains PARTIAL. Adjacent suites: **140 passed**, with 98 pre-existing
Pandas warnings. Local CI smoke selection: **109 passed**. Paper-state fixture
validator: PASS. Research-adapter tests reproduce **4 failed / 12 passed** on
both this checkout and exact base without the ignored CSV; all **16 passed**
in the external exact-base snapshot with the verified retained CSV. No worktree
data was hydrated. Full pytest/full-release is not required by this disjoint T2
WP and was not run. Hosted smoke was not run because no PR is permitted yet.

Final exact-byte characterization results, command logs, source hashes, process
receipts, negative matrix, scope checks and local commit identity are retained
in the external `EXECUTION_REPORT_A-I.md` and SHA256-indexed evidence ZIP under
`C:/Users/dersu/AppData/Local/Temp/cpw-nautilus-n2-02-evidence`.

- WP §4A/B: physical pinned environment, isolated Redis, both native scenarios,
  repeated economics and CPW references observed.
- WP §4C: real healthy/crash current-cache restoration observed; complete
  reversal history/portfolio-PnL conservation **fails** as described above.
- WP §4D: namespace, empty/missing/corrupt/truncated records, checkpoint/source/
  expiry, identity/fee/nonfinite/duplicate, startup flush, repeated restart,
  native venue reset and resume-refusal controls are covered.
- WP §5: focused characterization, adjacent suites, paper-state validator,
  local smoke, four-file scope and unchanged-source checks are recorded.
- WP §7: success-gated publication is withheld. No PR URL or hosted final-head
  smoke exists; neither is represented as a passed gate.

Skills applied: installed pre-draft/readiness/migration-parity/minimum-test-plan/
boundary/one-shot/evidence/PR-reconcile instructions and SOURCE_LOCATED locators;
Ponytail, systematic debugging, Ponytail review and verification instructions.
Locators grant no authority and are not acceptance certificates. Post-patch
security validation is inapplicable: this is a new proof, not a security patch.

**Decision required:** a separately authorized upstream/pinned-native remediation
for closed NETTING history restoration through the native cache loader, followed
by rerunning this proof. Native patch/version change is outside this WP. This
finding does not authorize a custom second accounting owner.

Unacknowledged in-flight writes, Redis/server/host crash, open-exposure restart,
remote reconciliation, missing external fills, funding settlement and enforced
liquidation/margin are unproven. Full N2 ownership remains blocked; N3 and human
paper/live activation remain later dependencies. All protected CPW paths,
configs, OMS, risk, reconciliation, overlays, safe mode, canonical authority,
project_status and CI are untouched. No trading activation or merge occurs.
