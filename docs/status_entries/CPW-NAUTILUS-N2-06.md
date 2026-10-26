# CPW-NAUTILUS-N2-06 — native rc7 funding settlement and liquidation characterization

Karl's full authorization, verbatim: "I approve everything so please proceed and always include my full authorization"

Karl's bundle authorization, verbatim: "I authorize this bundle execution plan, start now!"

## Scope and exact provenance

T2 private isolated offline fixture. Base: `b4ff62b99ffcf93a896de85f796d2bf88b87b52b`
(#761 N3-05 and #762 merged; no open PR at start). Branch
`claude/cpw-nautilus-n2-06-funding-liquidation-01`. Tested code commit
`5485ca0c99ddfaa7172ea099510cdc40e45d4df3`; this fragment is added afterwards and is docs-only.
Side B owns the independent exact-head review; Karl alone decides merge.

The allowed files are exactly five:
- modified: the fixture `src/main.rs`, `run_proof.py` and `README.md`;
- added: `tests/test_nautilus_n2_06_funding_liquidation.py` and this fragment.

Fixture hashes (normalized to LF; unchanged since #750):
- `Cargo.toml`: `e0319023…0630d207`
- `Cargo.lock`: `b1447750…49ec1709d`

Native source is rc7 `55c0e82053142bce3a5cba4de4221d3929c2d3bc`, crates 0.66.0. The registry
`exchange.rs`, `engine.rs`, `config.rs` and `matching_engine/mod.rs` are byte-identical to that
checkout. The installed Python Nautilus 1.231.0 is not touched or integrated.
**An rc7 result here is not N1 1.231.0 parity, cross-version integration or production readiness.**

## What changed

The fixture gains controlled **inputs only**:
- native `FundingRateUpdate` data with a boundary at 1.5 s, between the 1 s and 2 s quotes;
- the venue switch `liquidation_enabled`;
- fixed script orders: long, short or flat q=1 at 100, or short 100 at 100 followed by the
  unchanged N1-02 adverse closes 195, 200 and 250.

The native exchange owns everything else: settlement timing, price basis, sign, cash and
position adjustment, the liquidation trigger, and the liquidation order and fill.

Supporting changes:
- A passive typed `subscribe_any` subscriber retains each native `FundingSettlement`.
- A native run error is retained for N2-06 scenarios only.
- Restore refuses any checkpoint that has a run error (`NATIVE_RUN_FAILED`).
- No cash or equity clamp, synthetic event, injected liquidation, ledger or upstream patch.

Controller Stage D runs after the unchanged N2-05 Stages A–C on the same frozen binary:
1. Every scenario is produced twice. The stable native economics must be identical across the
   pair (UUIDs, PIDs and run IDs excluded).
2. Each case gets exactly one verdict, derived from native observations compared with the
   unchanged CPW references in `tests/test_nautilus_n1_02_parity.py`.
3. Each successful terminal state is restored twice through the existing read-only N2-05 path.

## Measured outcome

**`N2_06_NATIVE_CHARACTERIZED_FUNDED_RESTORE_UNSUPPORTED`** — one counted matrix:
- binary `1ebbead3a97553085d02ea0ca905f022f564627431a19bba41e2ee67b5f8d301`;
- new owned network-none container, image `sha256:031c1c78…`;
- 1565.86 s, controller exit 0;
- 42 genuine native producers, 63 restore/control cases, 80 distinct restore/resume PIDs.

The N2-05 regression `N2_05_NATIVE_CONTINUITY_PASSED` held on the same binary. Across every case:
- zero raw or semantic Redis deltas and unchanged redb hashes;
- all producer stores and receipts are byte-identical afterwards;
- the native Portfolio `RPUSHX` was denied 9 times by the read-only ACL user.

Funding: q=1 at mid 100, fees of 4 bps per fill are reported separately, settlement ts
1 800 000 001 500 000 000.

| Case | Native observation | CPW reference | Verdict | Restore |
| --- | --- | --- | --- | --- |
| long +0.01 | one settlement 0.01 @ 100.00; FUNDING adjustment −1.00; equity 9998.96 | −1 | PROVEN | refused (native) |
| long −0.01 | +1.00; equity 10000.96 | +1 | PROVEN | refused (native) |
| short +0.01 | +1.00; equity 10000.96 | +1 | PROVEN | refused (native) |
| short −0.01 | −1.00; equity 9998.96 | −1 | PROVEN | refused (native) |
| flat ±0.01 | no settlement event, no adjustment; equity 9999.92 | 0 | PROVEN | admitted exact |
| duplicate (two updates before the boundary, one after) | exactly one settlement, −1.00 | −1 once | PROVEN | refused (native) |
| missing rate / rate without boundary | no settlement, no cash | 0 | PROVEN | open exposure reconstructed exact |
| stale boundary (update 1.6 s, boundary 1.5 s) | native run error `Late funding boundary`; no cash | fail closed | PROVEN | `NATIVE_RUN_FAILED` |
| cross-instrument (ETH rate) | native run error `Funding settlement failed`; no BTC cash | fail closed | PROVEN | `NATIVE_RUN_FAILED` |

Liquidation: short 100 @ 100, NETTING Margin, leverage 1. Native maintenance margin is 500,
based on entry price; the CPW maintenance-mode figure at 195 is 975.

| Close | `liquidation_enabled=true` | CPW reference | Verdict | `false` (same path) | Verdict |
| --- | --- | --- | --- | --- | --- |
| 195 | native `LIQUIDATION-SIM-*` BUY 100 @ 195 at the first stress bar; flat; equity 488.20 | liquidated at bar 1, equity 0 | BOUNDED_DIVERGENCE | short 100 survives; balance 9996, margin 500 | PROVEN |
| 200 | BUY 100 @ 200 at bar 1; equity −12.00 | 0 | BOUNDED_DIVERGENCE | survives | PROVEN |
| 250 | BUY 100 @ 250 at bar 1; equity −5014.00 | 0 | BOUNDED_DIVERGENCE | survives | PROVEN |

The divergence comes from native rules, not from anything this fixture does:
- the trigger uses entry-price maintenance margin;
- liquidation fills at market with fees;
- there is no zero-equity floor.

Nothing is repaired.

**Funded-state restore is `UNSUPPORTED_PINNED`.** It fails closed with zero mutation:
- Native `RedisCacheDatabase::update_position` (`infrastructure/src/redis/cache.rs:1892`) persists
  the position's last fill again after the funding adjustment. The adjustment itself is not
  persisted.
- The native loader (`redis/queries.rs`) then rejects the record with `Duplicate fill event`.
- The controller assigns this verdict only when all of the following hold: the producer's own
  records show the duplicate with no adjustment record; restore refuses with
  `CURRENT_IDENTITY_MISMATCH`; and the native load rebuilds no position.

Liquidated states (closed) and unfunded open states restore exactly, twice each. Open states
remain `OPEN_EXPOSURE_RECONSTRUCTED_NO_RESUME`.

Adversarial controls:
- An unsigned tampered funded receipt was refused with `UNVERIFIED_AUTHORITY_RECEIPT`.
- Re-signed source and lock bindings were refused with `SOURCE_IDENTITY` and `LOCK_IDENTITY`.
- A missing funded or liquidated position record was refused with `REDIS_PRODUCER_PAIR_MISMATCH`.
- A re-signed missing position, and a re-signed altered liquidation order, were refused with
  `NATIVE_CURRENT_ARCHIVE_ERROR`.
- A receipt claiming resume/order authority still yields
  `OPEN_EXPOSURE_RECONSTRUCTED_NO_RESUME / NO_NEW_ORDERS / NO_RESUME`.
- `resume` exits non-zero before any admission.

## Validation and evidence limits

- **Cargo** (locked, offline, fresh copy of the tested commit): check PASS; test 9 passed
  (including the new `failed_native_run_refuses`); build PASS.
- **Pinned image** `cpw-n3-02-proof:pinned` (CPython 3.12.10 / Nautilus 1.231.0 / PyArrow
  25.0.1, network none, read-only repo):
  - N2-06 focused: 29 passed;
  - N2-05 + N2-04: 44 passed;
  - N1-02 oracle, unaltered: 39 passed;
  - native-cache guards: 6 passed.
- **Host** `.venv`: paper broker, ledger and state suites 18 passed; paper-state validator PASS.
- **Hygiene**: Ruff F/I clean on the new test; `git diff --check` clean.
- **Pre-existing**: Ruff I001 on `run_proof.py` imports (also present at base) is not changed here.
- **Not run**: the 13 N2-02 owned-Redis physical tests are outside this package. Full pytest and
  full release were not run (T2).
- **Earlier counted attempts** are retained under `counted-attempt-*`, not counted, and disclosed:
  - attempt 1 failed N2-05 Stage A, because a producer `BusTap` displaced native event-store
    capture (fixed in `b2ed8d9`);
  - attempt 2 was aborted by the executor to apply a review fix (`5485ca0`);
  - attempt 3 refused at start on a stray Redis left by the abort (the guard held).
- **Diagnostics** `diagnostic-*` are not acceptance evidence.
- **Fixture limits**: one deterministic BTCUSDT-PERP fixture, top-of-book funding price with no
  mark feed, single position, no partial-liquidity, multi-currency or venue funding.

Evidence is outside Git at `C:/Users/dersu/Downloads/CPW-N2-06-evidence-20261025`:
- `physical-n2-06/results.json`, sha256 `4d18286f…4fb95e1a`;
- `counted-04-final-logs/` (controller, cargo, source/binary hashes, toolchain, process check).

## Boundaries and next dependency

The following are all unchanged: protected runtime, OMS, reconciliation, risk, overlays,
safe mode, configs, schema, validators, the query layer, credentials and secrets,
live/order/capital paths, N1 and N3 adapters, Lane A, CI and `docs/project_status.md`.

Simulated orders exist only inside the isolated backtest fixture. There is no exchange network,
signing, venue order or resume.

Posture: `NO_NEW_ORDERS / NO_RESUME / NOT_PAPER_OR_LIVE_READY`.

Next decisions belong to Main/Karl and are not made here:
- N1 1.231.0 residuals: accept, review a pin path, or commission CPW-owned economic policy;
- whether native funded-state persistence must be solved before any N2 funding claim;
- A2, which remains Draftable: NO.
