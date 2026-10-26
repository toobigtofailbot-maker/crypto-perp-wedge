# 02J CPW non-holdout authority and guarded synthetic admission

Owner: Karl's 2026-10-25 consolidated software-only authorization in the execution
WP. Base: `1731d6bd75f403d5a40c4cc9c9ff7eb4cc0e3602`, merged PR #763.
Branch: `codex/wp-extreme-hermes-02j-cpw-nonholdout-authority-01`.

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
02B–02H consumer behavior and DON/FLOW/LOB fixtures remain unchanged.

## Acceptance traceability and validation

| WP requirement | Evidence | State |
| --- | --- | --- |
| §2 refreshed truth / one clean worktree | #763 merged; exact base above; separate managed worktree | satisfied |
| §4A durable independent authority | new module, migration 0003, role SQL; PostgreSQL control/role/audit tests | implemented; final verification outstanding |
| §4B pre-open, ancestry, current controls | metadata/refusal tripwires, sealed handle checks, transaction tests | implemented; final verification outstanding |
| §4C synthetic guarded byte positive | new test module, including exact-head integration and derived/feature dependencies | implemented; final verification outstanding |
| §4C native 02G handoff | outside the selected safe consumer; original refusal retained | not applicable; optional in WP |
| §5 focused/adjacent/PostgreSQL/security/T3 release | execution report and exact-head logs | final verification outstanding |
| §6 one unmerged PR / hosted smoke / Side 23 | execution report and posted PR evidence | publication outstanding |

Early failures are retained outside Git, not presented as passes: a reused Hermes
container shadowed the repo namespace; a standalone Python lacked Linux sealing
constants; the test tripwire initially blocked permitted schema metadata; Linux
02F fixtures interpreted committed backslash paths as filenames; a child process
lacked packages installed for another interpreter. Validation uses native Windows
for existing compatibility fixtures and standard Linux Python for sealing proof.
The original PostgreSQL catalog checksum remains locked after excluding only the
new table and explicitly authorized audit-enum additions. New table and trigger
membership are checked separately. No baseline lock is weakened.

Ponytail, WP inspection/readiness/test-plan, runtime-boundary, one-shot review,
verification and PR-evidence skills apply to the actual files and final head.
Systematic debugging resolved fixture/environment failures; security review
examines SQL privileges, issuer authentication, pinned identity, race order and
exception boundaries. The locator's Python 3.14 import collision was corrected
with `-P`, without editing installed skills. Skill output is not a certificate.

## Review and remaining gates

Candidate only; not yet ready for Side 23. No merge is authorized. Required
validation and exact-head publication evidence must be completed before readiness.
Karl alone decides merge after Side 23 review. Real physical history/custodian
designation, scientific approval, Stage 5B, paper/live and capital remain separate
future gates. No real historical/holdout bytes, credentials, VPS, Research Memory
records, runtime, OMS, risk, overlay, safe mode, configs or live paths were used
or changed. `docs/project_status.md` and the 02I proposal are unchanged.
