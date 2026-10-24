# CPW-NAUTILUS-N3-01 — Linux native offline Binance USD-M report proof

Karl's full authorization: “I approve everything so please proceed and always include my full authorization”

T2, synthetic offline evidence only. Base `e6074075017f23d9e960ed0a44d606beb0d2aaec`
contains merged N2-05/#750. Dedicated branch
`codex/cpw-nautilus-n3-01-cloud-linux-01`; sole open Lane A #752 is file-disjoint.
The Linux continuation and import-boundary correction control this proof.
Passive imports from the unmodified native wheel are inventoried; runtime
construction/invocation, credentials, signing and networking remain forbidden.

Exactly four new files: proof module, focused tests, finite synthetic BTCUSDT
tape, and this fragment. Existing adapters, locks, N2 Rust fixture, protected
src/lib/OMS/reconciliation/risk/safe-mode paths, Lane A, CI and project_status
are unchanged. No public adapter registration or downstream authority.

## Physical behavior

Official Linux wheels, CPython 3.12.10, NautilusTrader 1.231.0, PyArrow 25.0.1.
All 20 Windows-lock package versions match; the native Linux wheel additionally
pins uvloop 0.22.1. Wheel bytes/origins and installed source hashes are retained
in external evidence. No package source or committed dependency was changed.

- One genuine native CryptoPerpetual; tick 0.10, step 0.001, min/max quantity
  0.001/1000.000, minimum notional 5 USDT. These are synthetic fixture filters,
  not a current exchange query. Native provider conversion uses only its real
  in-memory instrument store and a fixed clock; no HTTP client is constructed.
- 27 genuine native reports: 13 order, 8 fill, 6 position observations, including
  snapshot/duplicate diagnostics. NEW → PARTIAL → FILLED, separate canceled
  reduce-only order. Counted trades 501/502: 0.004/0.006 BTC at 60000.00,
  maker/taker fees 0.048/0.180 USDT. Exactly two counted fills.
- Native positions are FLAT/LONG/SHORT with quantities 0/.010/.010. Source
  signed amounts remain 0/+.010/-.010; no invented signed native quantity.
- Three read-only snapshot cases: consistent; missing fill 502 and position
  drift; external open order 303. Identical and conflicting duplicate receipts
  never add a second counted fill. This projection is not native account
  economic idempotency. Every case retains
  `RECONCILIATION_REQUIRED / NO_NEW_ORDERS / NO_RESUME`.
- Raw UUID report IDs remain diagnostic; only those UUIDs are excluded from
  deterministic observations. REST fills supply no native client ID. Native WS
  acceptance time uses supplied event time; native position ts_last uses
  supplied observation time. Both limitations are explicitly recorded.

## Validation and limits

58 focused tests passed with zero skips. Two fresh-process semantic comparisons
use guards installed before target import and a Linux seccomp socket syscall
filter; a native socket negative control returns EPERM. Guards reject Python
socket/DNS/HTTP, subprocess/shell, signing, credential access, protected imports,
external writes and the upstream Python Trader constructor entry before its body.
Static checks prohibit direct authority bindings/constructor calls. Inventory
hashes passive upstream modules. These are bounded audit/profile/source checks
plus denied network syscalls, not proof against every possible native behavior.

Adjacent execution-evidence/N2 continuity contracts: 46 passed. Expanded adjacent
selection: 58 passed, four failures from the absent pre-existing gitignored D4A
CSV. The same four failures reproduce on clean unchanged base; affected adapter
and test files are byte-identical. No fake dataset was created. Result-population
validator passed using the existing repository venv. Full pytest/full release:
NOT RUN — scoped T2 offline adapter; no broad dependency or protected-code change.
Expensive N1 RP-2592/N2 Rust matrices are unchanged and were not rerun.

Native proof does not establish Windows portability, functioning reconnect,
venue reconciliation, missing-fill recovery, funding/liquidation/accounting
parity, full N2/N3 ownership or paper/live/capital readiness.
`WINDOWS_NATIVE_IMPORT_UNPROVEN_HOST_SAC_BLOCKED` remains historical host debt.

External A–I report and SHA-256-indexed evidence live outside Git under
`/workspace/n3-01-resumed-evidence`. Final semantic commit, Cloud smoke,
compile/scope checks, exact-head PR state and archive digest are recorded there.
No GitHub Actions dispatch or purchased compute; publication commits carry
`[skip ci]`. Side B reviews the exact PR head; Karl alone merges. No self-merge.

## Publication and requirement traceability

PR: [#753](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/753),
open non-draft for independent Side B review. Tested semantic commit:
`69038f01bc85196296cc7e7779bd7861fc27e366`. Cloud developer-tool smoke:
109 passed; focused: 58 passed; py_compile, exact allowlist/scope and diff checks
passed. This publication-only documentation commit preserves all three tested
module/test/tape blobs; their SHA-256 identities and final PR head are recorded
in the external A–I report and `final-head.json`.

At semantic-head publication GitHub reported mergeable=true, zero commit status
contexts and zero workflow runs. Hosted checks were not launched. Available
access did not establish branch-protection requirements; no mandatory check is
waived and no merge-ready declaration is made. Review readiness is independent
of Karl's merge decision.

| Active requirement | Source | Evidence | Disposition |
| --- | --- | --- | --- |
| Native reports/filter/identity/duplicate/snapshot mechanics | original §5.A–F | module, fixture, 27 raw reports per final run | satisfied |
| Malformed, enum, amount, identity and ordering refusal | original §5.G | 33 recorded negatives and 58 focused tests | satisfied |
| Passive imports allowed; forbidden behavior rejected | correction §§1–2 | source audit, audit/profile sentinels, seccomp fresh runs | satisfied within stated coverage |
| Repeat semantics and no input/source mutation | original §5.I | two distinct retained process receipts and before/after hashes | satisfied |
| T2 focus/adjacent/Cloud/scope validation | original §8; Linux addendum §4 | 58/46/109 passes; four extra CSV failures reproduced on base | satisfied with disclosed environment limit |
| External A–I and archive; final PR state | original §§8.9,10 | external report, SHA256SUMS, exact-head GitHub receipts | retained outside Git |
| Windows/full N2/N3/live authority | original §9; addendum §§4–5 | explicit limitations above | excluded |
