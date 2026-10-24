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
