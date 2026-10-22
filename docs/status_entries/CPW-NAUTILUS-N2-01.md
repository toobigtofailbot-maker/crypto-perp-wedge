# CPW-NAUTILUS-N2-01 — Offline sandbox and event-replay proof

Bounded N2-01 engineering proof only: `proof_only`, `non_authoritative`,
`never_live_or_capital`. Full N2 acceptance and trading activation remain unproven.

## Scope and provenance

- Authorizer: Karl's explicit execution request and attached N2-01 WP.
- T2; new Lane B worktree:
  `C:/Users/dersu/.codex/worktrees/cpw-nautilus-n2-01-lane-b/crypto-perp-wedge`.
- Branch: `codex/cpw-nautilus-n2-01-sandbox-proof`.
- Refreshed base: `5aa381bfc31d009809a8093379c9a0f31651d597` (#741 merged).
- Initial authenticated GitHub search: zero open PRs; no file collision.
- Environment: CPython 3.12.10 / NautilusTrader 1.231.0. All 20 committed
  dependency pins match; installed native binaries and sandbox sources match
  wheel RECORD SHA256 entries. No package installation or dependency change.
- Requested model/effort: GPT 6.1 Sol / HIGH. This chat's tools cannot change
  or independently verify the active model/effort; no verified-model claim.

Exactly four added files: private `tools/nautilus_adapter/paper_sandbox.py`,
`tests/test_nautilus_n2_sandbox.py`, `tests/test_nautilus_n2_restart.py`, and this
fragment. No package export, public dispatcher, production service, CPW writer,
N1 modification, or architecture change.

## Observed capability

Native route: `SandboxExecutionClient` → its `SimulatedExchange` /
`BacktestExecClient`, through actual `ExecutionEngine`, `MessageBus`, `Cache`,
and `Portfolio`. No BacktestEngine episode or mocked execution component.
Closed synthetic venue `N2PROOF`; 1x leverage; quantity increment .001 BTC,
maximum order 2 BTC, maximum held position 1 BTC; USDT settlement; seed 20261021.
Test clocks fix quote/order times at 2026-01-01 plus one-second steps.
The constructor's initial native account event has timestamp zero and is retained.
No external client, endpoint, credential or economic-mode configuration surface.
Network connect/connect_ex/sendto/DNS are denied during execution. Windows
asyncio constructs its local wakeup socket before that guard.

| Scenario | Actual observations | Final native equity / fees (USDT) |
| --- | --- | --- |
| flat / unchanged | No orders/fills; initial AccountState retained | 10000 / 0 |
| round_trip | BUY 1@100, unchanged at105, SELL 1@110; submitted, filled, position opened/closed, account events | 10009.916 / .084 |
| reversal | BUY1@100, SELL2@110, BUY1@90; native NETTING closes/reopens | 10029.836 / .164 |
| cancel | Resting BUY1 limit50 at mark100; submitted/accepted/canceled; no fill | 10000 / 0 |

Market orders do not emit OrderAccepted on this pinned path. Cancellation proves
native acceptance separately. No rejected order is manufactured or claimed.
Native reversal republishes one identical AccountState between PositionClosed
and PositionOpened. Both publications remain in the journal with an explicit
`native_republication_of` link; this is not another economic effect. Other
duplicate events and all duplicate economic trade IDs fail closed.

Native event UUIDs are retained, and vary across sessions. Ordered object/trade
IDs, immutable economic fields and derived publication observation keys repeat.
The derived keys are explicitly proof-only, never exchange IDs. Every event has
sequence, source/version/scenario, native timestamps/identity, content hash and
previous hash. Completed records flush/fsync/close separately; a completed
manifest binds event bytes, environment, fixture, native checkpoints and count.

Native account balance, portfolio realized/unrealized PnL and cached positions
are source observations. Fees are sums of actual native commission events;
equity is derived as native balance plus native unrealized PnL. Independent replay
calculates its own quantity, average, fees, PnL, orders and equity, then checks
every native checkpoint. All bounded monetary comparisons use exact Decimal,
zero tolerance. Native monetary serialization remains unmodified.

CPW `PaperBroker()` without a ledger path and immutable `LedgerState.apply_fill`
are read-only reference oracles. Zero spread/slippage and 4 bps fees yield exact
equity/fees/quantity/unrealized parity for every controlled checkpoint. CPW cash
is a spot-like cash measure, whereas native balance is a margin balance; compare
equity, not those raw cash fields. CPW realized PnL is gross; native portfolio
realized PnL is net of commission. A separate reference-arithmetic check retains
the known fee-basis distinction: reference100, execution100.01, quantity1 gives
CPW fee .04 versus execution-notional fee .040004. This is not a new native
nonzero-slippage proof or a policy correction.

## Reconstruction and limits

For each scenario, an actual producer OS process closes its evidence, then two
independent replay processes consume its trusted manifest digest. Distinct PIDs,
identical projection bytes and unchanged input hashes are recorded. Replay's
import hook rejects Nautilus, `src`, and `lib`; no adapter or native engine can
load, no order can be submitted, and no trial/result identity is generated.
PID receipts vary; the projection bytes are stable for the same retained journal.

Corrupt/truncated/reordered/missing streams, duplicate native/economic identities,
unknown order references, source/version/scenario drift, invalid currency/units,
nonfinite amounts, inconsistent account snapshots and untrusted manifest bindings
reject. Semantic negative controls recompute the outer chain to exercise actual
contract checks, not merely byte-hash detection.

This proves event-replay reconstruction only. Native TradingNode/cache durability,
crash recovery, status-report reconciliation, missing/external fill discovery,
venue reconnect, nonzero perpetual funding settlement and enforced margin/
liquidation remain separate N2/N3 dependencies. The pinned sandbox's four status
report APIs return None/empty. No cache database, exchange adapter, cash override,
shadow production ledger, native-source patch or version migration was added.

## Validation and requirement traceability

Local seeded focused validation: **64 passed, zero skips, 37.62s**. Local CI
smoke selection: **109 passed, 107.52s**. Paper-state fixture validator passed.

- WP §5A: four physical fixtures, each repeated; native journal/checkpoint and
  CPW reference evidence in focused test logs and retained episode manifests.
- WP §5B: separate processes per fixture; `process-receipt.json` binds PIDs,
  producer manifest, replay projections and immutable file hashes.
- WP §5C: closed fixtures and network/pin/lock/binary/amount negatives plus
  journal byte and rehashed semantic corruption controls.
- WP §3/§7: exact four-file scope, diff-check, read-only paper-state validator,
  adjacent tests and unchanged N1 blobs; public PR checks reconciled separately.
- WP §6: pre-draft/readiness/minimum-test-plan/one-shot/boundary/evidence locator
  scripts were run and reported SOURCE_LOCATED only. Their native checklists,
  Ponytail, Ponytail review, systematic debugging, and verification instructions
  were applied. These are not independent certification engines.
- WP §8: sanitized external A–I report and SHA256-indexed evidence ZIP; no merge.

Adjacent validation: 78 passed for N1-02, paper broker/ledger/position flow,
execution-evidence contract and paper-state suites. The 16 adapter unit tests
pass separately on an exact-base external source snapshot with the verified
29,300,290-byte D4 CSV, SHA256
`c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`.
These adapter sources are unchanged on this branch. The checkout lacks this
ignored CSV: four missing-file failures reproduce on clean base. An initial
combined run also violated an existing import-isolation test's process premise;
separate processes resolve that failure. No worktree data was hydrated.

The first focused run had three failures: account republication was initially
classified as a duplicate and the cancellation oracle omitted native account
updates. Both were corrected against retained source observations; failed logs
are preserved. Upstream N1 Pandas deprecation warnings remain disclosed.
No environmental skips count as required N2 physical proof.

Full repository pytest is not required by this bounded T2 WP: no production
consumer/import/export, protected writer, schema or query behavior changes.
N1-01's historical 8/8 physical replay is reused only with unchanged source/test/
lock blob coverage; it is not rerun or represented as new N2 evidence.

Evidence root: `C:/Users/dersu/AppData/Local/Temp/cpw-nautilus-n2-01-evidence`.
Final tested code identity, test totals, public head/checks and PR URL are recorded
in the completion record below and the external A–I execution report.

Boundary review: Lane A, project_status, `src/**`, configs, OMS, reconciliation,
risk, overlays, safe mode, science/CANON, dependencies and CI remain untouched.
All synthetic proof sessions close. No paper/live service, trading activation,
capital action, deployment, merge or authority promotion occurs.
