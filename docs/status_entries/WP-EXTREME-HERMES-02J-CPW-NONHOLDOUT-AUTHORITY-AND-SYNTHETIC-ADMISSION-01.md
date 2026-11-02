# 02J CPW non-holdout authority and guarded synthetic admission

Owner: Karl's 2026-10-25 consolidated software-only authorization in the execution
WP. Base: `1731d6bd75f403d5a40c4cc9c9ff7eb4cc0e3602`, merged PR #763.
Branch: `codex/wp-extreme-hermes-02j-cpw-nonholdout-authority-01`.
PR: [#765](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/765),
**DRAFT / authorized conditional software validation in progress / unmerged**. Initial boundary validation head:
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
02BÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“02H consumer behavior and DON/FLOW/LOB fixtures remain unchanged.

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
| Ã‚Â§2 repository truth | #763 merged at original base; #764 merged at `c144c821d1decc48253b60901bf44377811954b0`; incorporated by normal merge `f7819c4` | refreshed; eight-file WP diff |
| Ã‚Â§4A authority | module, additive migration 0003, role SQL; PostgreSQL audit/role tests | software/fixtures satisfied |
| Ã‚Â§4B pre-open | sealed handle checks, metadata/refusal tripwires, ancestry and transaction tests | supported sealed fixtures satisfied |
| Ã‚Â§4C synthetic positive | guarded exact-code consumer and derived/feature dependencies | satisfied; no historical qualification |
| Ã‚Â§4C native 02G handoff | original historical refusal preserved | optional; not integrated |
| Ã‚Â§5 focused/adjacent/PostgreSQL/security | Linux 96 passed; Windows 182 passed / 19 Linux-specific skips; amendment query 3 passed | covered; exact heads in AÃ¢â‚¬â€œI report |
| Ã‚Â§5 mandatory T3 | amended native full-release completed all 48 shards: 36 passed, 12 failed | FAIL; cannot waive |
| Ã‚Â§6 one PR / Side 23 | draft PR #765; exact final head and smoke in AÃ¢â‚¬â€œI report | readiness NO |

### Completed amended release and genuine scope conflict

At frozen head `38c2d08b86c8040a699ba6681df3502f3057fb0a`, native
`tools/dev/verify.py --validation-preset full-release --full-pytest-sharded
--pytest-shard-profile full-release-balanced-v1` assigned all 222 tracked files
exactly once and executed every shard. Assignment manifest:
`sha256:661af921dbfd1534de4b30115cb868117e0658571c08535cb82ca8b482b616c2`.
Query shard passed **86/86**. Total: **4,560 passed, 52 failed, 110 errors,
45 skipped**. No shard timed out. This is completed execution, not passing T3.

### Same-PR supported-toolchain continuation, 2026-11-01

All **162 original failed/error nodes** were classified by their full earliest
causal tracebacks before repaired execution: absent D4 CSV 5; absent 1d Parquet 2;
unsupported CPython 106; missing pinned Nautilus 44; Python 3.12 filesystem API 1;
Windows symlink privilege 1; missing Linux libseccomp 3. No blanket baseline
claim was made for the 155 environment nodes.

At `f8cc896e004bba1420a8927266734dac98e3b789`, all **155 environment nodes now
PASS**, matched by exact JUnit node. The supported Linux CPython 3.12.10 image
verifies all 20 committed native lock versions and installed wheel RECORD.
Missing Git, colorama, Redis client, Docker CLI, supplemental repo dependencies
and Compose plugin were supplied only inside disposable validation environments.
The existing dedicated, labeled, loopback Redis 7.4.2 synthetic proof fixture was
verified, started for isolated random test namespaces, then restored to stopped.
No dependency pin, production source, platform guard or test expectation changed.

All nine original affected native shard assignments were exercised directly:
17: 92 passed; 18: 130 passed / 1 missing-Compose failure, followed by the fixed
Compose test passing; 21: 180 passed / 1 existing explicit-physical skip;
22: 121 passed; 23: 246 passed; 24: 203 passed; 25: 105 passed / 15 Linux fixture
setup errors; 26: 149 passed; 27: 67 passed. These are diagnostic pytest runs,
not one native full-release PASS. Initial missing-prerequisite logs are retained.

The 15 additional queue-input fixture errors reproduce on **current clean main
`c144c82` in the same Linux environment** (3 passed / 15 errors). Committed
Windows backslash paths become basenames on POSIX, so fixture setup tries to
mkdir its already-created source directory. Unmodified Windows rerun: **18/18
passed**, 476.20 seconds. No platform monkeypatch or fixture/catalog rewrite.
The native verifier does not authorize combining this split-platform evidence
into one passing T3 certificate.

The seven data-dependent nodes also reproduce on **current clean main in the
same corrected Linux environment**, with identical absent-source visibility:
PR **7 failed**, 6.46 seconds; clean main **7 failed**, 5.97 seconds. One takerflow
test reads an exact real May-2024 discrepancy; two dispatch tests require whole
1d file/hash/lineage. Four fake-executor tests already mock hash/count/loader/
compiler but still demand the authentic canonical path's presence. A fabricated
canonical placeholder remains prohibited. No existing approved nonhistorical
route satisfies these seven original assertions.

Committed metadata covers full 2020-01-01 through 2026-04-11 historical objects;
02I explicitly states that opaque holdout IDs do not map to physical intervals.
Whole-object holdout exclusion and eligible real-data validation isolation are
**not proved**. No real dataset was opened, copied, materialized or hashed.
The smallest remaining owner gate is an explicit software-only T3 validation-
contract decision for these exact historical checks and split-platform evidence;
otherwise any authentic-data option first requires specific permission and
independent proof of eligible holdout-safe isolation. No waiver is inferred.
No expensive full-release rerun was started with these prerequisites unresolved.

Linux authority/PostgreSQL at `38c2d08`: **96 passed**, 49.37 seconds.
Windows focused/adjacent at `74a0038`: **182 passed / 19 Linux-only skips**,
1810.08 seconds. Linux covers the physical sealing cases. Existing 02EÃ¢â‚¬â€œ02H
fixture/refusal and DON/FLOW/LOB regressions retain their evidence. New Python
files pass Ruff/format; existing PostgreSQL and query files retain respectively
28 and 3 baseline lint findings, with no new findings. Changed-file secrets:
zero at amendment head; final-tail checks and exact-head synthetic proof are
recorded in the final AÃ¢â‚¬â€œI report. Migration 0001/0002 Git bytes are unchanged.

Original failed logs remain retained outside Git: the old 83/3 query failure,
namespace/interpreter/checkout-mode fixture setup failures, and the early run
invalidated by a HEAD commit. None count as passing evidence. The completed
amended release kept HEAD fixed for its entire execution.

## Karl-approved bounded software-validation amendment

On 2026-11-01 Karl explicitly approved the attached same-PR 02J-only validation
contract amendment. It supersedes the earlier request for a validation-contract
decision above; those paragraphs retain historical evidence, not a new approval
request. Current merged main is PR #766 at `77a5a84`; its three Lane B additions
were incorporated by file-disjoint normal merge `36677ef`. No Lane B file edited.

Two additional authorized test paths bring this WP diff to ten files. The queue-
input fixture normalizes committed Windows separators only when constructing its
synthetic parent path. Production catalogs/path guards and every assertion remain
unchanged. Both amended modules pass **34/34 Linux** and **34/34 Windows**; the
original 15 Linux fixture errors now pass. Negative hash/gap/truncation/parent,
window, mutation, network/science/writer cases remain enforced.

Four fake-executor tests use a clearly named temporary synthetic CSV containing
their existing mocked frame. Existing hash/count/loader/compiler mocks and all
assertions are unchanged; no new production monkeypatch is introduced. These
prove envelope/provenance behavior only. Separate unmocked probes reject those
synthetic bytes as canonical history at the SHA guard and reject a missing file;
actual count/loader helpers are exercised on synthetic bytes. No canonical path,
real history identity or production integrity check is bypassed or provisioned.

The three genuine historical discrepancy/dispatch tests remain unchanged. The
external, report-only exact-node driver retains all 48 original shard assignments
as immutable reference, accounts for newly merged test files, records every node,
command, OS, pin, raw JUnit/JSON/log hash and explicit historical exclusion. Only
those three exact nodes may be `UNEXECUTED_HISTORICAL_DATA_DEPENDENCY`; they are
never passed, silently skipped or scientifically verified. Native verifier,
profile, pytest defaults, CI and global T3 policy remain unchanged.

The stable candidate will run the complete eligible software suite and standard
non-physical command set. `02J_SOFTWARE_RELEASE_CONDITIONAL_ACCEPTED` may be
reported only after all eligible checks pass with no unexplained regression.
The prior unmodified T3 remains FAIL; current-head unmodified T3 is NOT VERIFIED.
This amendment grants no physical data, science/Stage 5B, trading or merge
permission. PR #765 remains draft until the actual conditional evidence is
reconciled in the final exact-head A–I report. Side 23/Karl retain review/merge.
