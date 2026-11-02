# 02J CPW non-holdout authority and guarded synthetic admission

Owner: Karl's 2026-10-25 consolidated software-only authorization in the execution
WP. Base: `1731d6bd75f403d5a40c4cc9c9ff7eb4cc0e3602`, merged PR #763.
Branch: `codex/wp-extreme-hermes-02j-cpw-nonholdout-authority-01`.
PR: [#765](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/765),
**DRAFT / BLOCKED on mandatory T3 / unmerged**. Initial boundary validation head:
`74a0038d90a36c844aa61b36529ea726640e9767`.

## Delivered boundary

The new CPW module extends the existing D2-026 transaction/audit boundary with
strict owner-controlled custodian/designation/revocation records and signed,
exact-request custody evidence. Migration 0003 is additive; 0001/0002 bytes are
unchanged. The separate NOLOGIN owner role receives control-table insert;
the research writer receives select only. No role membership, trusted issuer,
private key, actual custodian or historical partition is provisioned.

Requests bind the registered envelope, current Git code, protocol, manifests,
campaign/domain/holdout audit lineage, bounded intervals and every transitive
physical input. Unknown fields, missing ancestry, stale/revoked evidence,
incomplete bars, hidden warmup and protected overlap fail closed. Completed use
advances the same campaign audit; reuse of an attestation ID fails before read.
Replacement appends revocation of the old immutable ID and a new designation.

Only sealed anonymous Linux handles are supported. All handles are duplicated,
authenticated against the signed identity and checked for immutable seals before
any byte read. No pathname, full-parent fallback, compiler/model callback or raw
byte release exists. The global authority lock remains held through byte use and
audit commit; concurrent revocation and contamination serialize against that use.
Crash/retry preserves the domain. Windows and unsupported Linux primitives deny.
Failed Linux writes can advance ctime; stale identity is conservatively refused.

The positive validates a closed synthetic CSV grammar, including a declared
15m-parent/30m-derived/row-local-feature chain. It is software evidence, not
historical OHLCV/canonical-loader parity. Results remain science `NOT_READY`,
SearchContract `NOT_ISSUABLE`, `NATIVE_HANDOFF_NOT_INTEGRATED`. All existing
02Bâ€“02H consumer behavior and DON/FLOW/LOB fixtures remain unchanged.

## Acceptance traceability and validation

### Karl-authorized scope amendment, 2026-11-01

Karl explicitly authorized `tests/test_research_query.py` solely to correct the
three demonstrated clean-base expectations for `canonical_1d_dataset_unavailable`.
The test now asserts the complete, exact H-004 unavailable-input finding when
the canonical input is absent. It expects no execution-stream finding for a
dispatch that cannot be validated; the actual uncertainty remains visible in
crossing-reservation integrity. Every view still uses full result-set equality,
so extra findings or changed identity/reason/security flags fail the tests.

The three corrected tests pass; an assertion-sensitivity probe rejects eight
missing/extra/misbound finding variants and preserves the previous available-input
expectation. The helper inspects file presence only and opens no historical data.
No production query/dispatch/validation file changed. The prior scope escalation
is resolved by this explicit amendment. The amended full-release result below
is current; the original 83-pass/3-failure query result is historical evidence.

| WP requirement | Evidence | State |
| --- | --- | --- |
| §2 repository truth | #763 merged at original base; #764 merged at `c144c821d1decc48253b60901bf44377811954b0`; incorporated by normal merge `f7819c4` | refreshed; eight-file WP diff |
| §4A authority | module, additive migration 0003, role SQL; PostgreSQL audit/role tests | software/fixtures satisfied |
| §4B pre-open | sealed handle checks, metadata/refusal tripwires, ancestry and transaction tests | supported sealed fixtures satisfied |
| §4C synthetic positive | guarded exact-code consumer and derived/feature dependencies | satisfied; no historical qualification |
| §4C native 02G handoff | original historical refusal preserved | optional; not integrated |
| §5 focused/adjacent/PostgreSQL/security | Linux 96 passed; Windows 182 passed / 19 Linux-specific skips; amendment query 3 passed | covered; exact heads in A–I report |
| §5 mandatory T3 | amended native full-release completed all 48 shards: 36 passed, 12 failed | FAIL; cannot waive |
| §6 one PR / Side 23 | draft PR #765; exact final head and smoke in A–I report | readiness NO |

### Completed amended release and genuine scope conflict

At frozen head `38c2d08b86c8040a699ba6681df3502f3057fb0a`, native
`tools/dev/verify.py --validation-preset full-release --full-pytest-sharded
--pytest-shard-profile full-release-balanced-v1` assigned all 222 tracked files
exactly once and executed every shard. Assignment manifest:
`sha256:661af921dbfd1534de4b30115cb868117e0658571c08535cb82ca8b482b616c2`.
Query shard passed **86/86**. Total: **4,560 passed, 52 failed, 110 errors,
45 skipped**. No shard timed out. This is completed execution, not passing T3.

Seven failures in `test_takerflow_feature_materialization.py`,
`test_nautilus_research_adapter.py`, and `test_dispatch_authorization.py`
require the absent canonical D4 CSV or 1d Parquet. The exact clean base
`1731d6b` reproduced **all seven failures** in 41.25 seconds. Their source
and production dependencies are outside the WP diff. The takerflow test opens
real May-2024 history; the dispatch test explicitly replays real H-004.
Hydrating those data, substituting invented canonical evidence, disabling tests,
or changing additional test/validation paths is not authorized. This is a new,
concrete mandatory-validation/scope conflict; Karl's three-expectation amendment
is fully implemented and is not being requested again.

Other failed shards expose validation-environment requirements (CPython 3.12,
pinned Nautilus, Linux libseccomp and Windows symlink privilege). These are not
claimed as production regressions or repaired. Resolving those alone cannot
satisfy T3 while the independently reproduced historical-data conflict remains.
No broad run is repeated just to rediscover the absent datasets. New main adds
one file-disjoint native test; the 222-file release result predates that merge
and is not final-main full-suite proof.

Linux authority/PostgreSQL at `38c2d08`: **96 passed**, 49.37 seconds.
Windows focused/adjacent at `74a0038`: **182 passed / 19 Linux-only skips**,
1810.08 seconds. Linux covers the physical sealing cases. Existing 02E–02H
fixture/refusal and DON/FLOW/LOB regressions retain their evidence. New Python
files pass Ruff/format; existing PostgreSQL and query files retain respectively
28 and 3 baseline lint findings, with no new findings. Changed-file secrets:
zero at amendment head; final-tail checks and exact-head synthetic proof are
recorded in the final A–I report. Migration 0001/0002 Git bytes are unchanged.

Original failed logs remain retained outside Git: the old 83/3 query failure,
namespace/interpreter/checkout-mode fixture setup failures, and the early run
invalidated by a HEAD commit. None count as passing evidence. The completed
amended release kept HEAD fixed for its entire execution.

## Review and remaining gates

**READY FOR SIDE 23 REVIEW: NO.** Required T3 proof is absent. PR #765 remains
draft and unmerged. Scope resolution for the seven historical-dependent tests
(or an explicit owner resolution of the validation contract) is required;
this document grants neither permission nor a waiver. No real data access is
proposed. Side 23 exact-head review and Karl's merge decision remain gates.
Real custody designation, scientific approval, Stage 5B, paper/live and capital
remain separate future authorities. No runtime, OMS, risk, overlay, safe-mode,
config, live, production query/dispatch or existing validator path changed.
`docs/project_status.md` and the 02I proposal remain unchanged.
