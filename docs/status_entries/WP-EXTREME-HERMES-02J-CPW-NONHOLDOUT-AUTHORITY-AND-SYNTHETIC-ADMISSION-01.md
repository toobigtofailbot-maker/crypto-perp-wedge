# 02J CPW non-holdout authority and guarded synthetic admission

Owner: Karl's 2026-10-25 consolidated software-only authorization in the execution
WP. Base: `1731d6bd75f403d5a40c4cc9c9ff7eb4cc0e3602`, merged PR #763.
Branch: `codex/wp-extreme-hermes-02j-cpw-nonholdout-authority-01`.
PR: [#765](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/765),
**DRAFT / BLOCKED / unmerged**. Semantic head:
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
02B–02H consumer behavior and DON/FLOW/LOB fixtures remain unchanged.

## Acceptance traceability and validation

| WP requirement | Evidence | State |
| --- | --- | --- |
| §2 refreshed truth / one clean worktree | #763 merged; exact base above; separate managed worktree | satisfied |
| §4A durable independent authority | new module, migration 0003, role SQL; PostgreSQL control/role/audit tests | satisfied for software/fixtures |
| §4B pre-open, ancestry, current controls | metadata/refusal tripwires, sealed handle checks, transaction tests | satisfied for supported sealed fixtures |
| §4C synthetic guarded byte positive | new test module, including exact-head integration and derived/feature dependencies | satisfied; no historical qualification |
| §4C native 02G handoff | outside the selected safe consumer; original refusal retained | not applicable; optional in WP |
| §5 focused/adjacent/PostgreSQL/security/T3 release | Linux 96 passed; Windows focused/adjacent 182 passed / 19 Linux-only skips; full-release failed as below | blocked on mandatory T3 |
| §6 one unmerged PR / hosted smoke / Side 23 | draft PR #765; exact final head/CI in execution report | draft publication; Side 23 readiness NO |

The required `full-release-balanced-v1` invocation at the semantic head assigned
all 222 tracked files exactly once across 48 shards. Its exclusive query shard
completed in 1010 seconds: **83 passed, 3 failed**, no timeout. The native verifier
correctly stopped; the other **47 shards did not run**. Standard diff/scope,
Result Population validation and query-view discovery checks passed. This is
**not** complete or passing T3/full-suite evidence.

The stable Windows focused/adjacent run completed in 1810.08 seconds at the
semantic head: **182 passed, 19 skipped**. The skips are Linux-specific physical
sealing cases, all covered by the independent Linux run (**96 passed**, including
70 new boundary cases and 26 existing PostgreSQL tests). Windows default-denial,
02E–02H native fixture/refusal regressions and unchanged DON/FLOW/LOB behavior pass.

Both candidate and exact clean base `1731d6b` reproduce these three failures:

- `test_dispatch_authorization_crossing_reservation_integrity_is_empty_on_main`
- `test_execution_stream_integrity_matches_repo_or_local_evidence_context`
- `test_current_integrity_views_empty_under_pre_execution_refinement`

The H-004 integrity context reports
`crossing_committed_required_validation_input_unavailable` /
`canonical_1d_dataset_unavailable`. No historical input was hydrated, synthetic
replacement impersonated a canonical dataset, test skipped, or production gate
weakened. The affected query tests, query layer and dispatch validators have no
diff. WP sections 3/5 do not authorize their repair or real historical access;
this mandatory validation conflict needs an explicit software-only scope/gate
resolution. A clean-base reproduction is disclosure, not a waiver.

New Python files pass Ruff and formatting. The older PostgreSQL test file retains
the same 28 lint findings as clean base, with no new lint findings; its existing
whole-file formatting debt is retained. Changed-file secret scan found zero
secrets. Scope/diff checks pass; existing migration Git bytes are unchanged.

Early failures are retained outside Git, not presented as passes: a reused Hermes
container shadowed the repo namespace; a standalone Python lacked Linux sealing
constants; the test tripwire initially blocked permitted schema metadata; Linux
02F fixtures interpreted committed backslash paths as filenames; a child process
lacked packages installed for another interpreter. Validation uses native Windows
for existing compatibility fixtures and standard Linux Python for sealing proof.
The original PostgreSQL catalog checksum remains locked after excluding only the
new table and explicitly authorized audit-enum additions. New table and trigger
membership are checked separately. No baseline lock is weakened.
An early Windows combined run was invalidated by a HEAD commit while fixtures
cached the prior identity. Its failures are retained, not counted as passing
evidence. Later validation kept the semantic HEAD fixed.

Ponytail, WP inspection/readiness/test-plan, runtime-boundary, one-shot review,
verification and PR-evidence skills apply to the actual files and final head.
Systematic debugging resolved fixture/environment failures; security review
examines SQL privileges, issuer authentication, pinned identity, race order and
exception boundaries. The locator's Python 3.14 import collision was corrected
with `-P`, without editing installed skills. Skill output is not a certificate.

## Review and remaining gates

**READY FOR SIDE 23 REVIEW: NO.** The draft preserves reviewable implementation
and honest blocked evidence. No merge is authorized. Required T3 validation must
be completed before readiness; hosted smoke cannot replace it. The final A–I
report records final head, focused/adjacent counts and hosted state.
Karl alone decides merge after Side 23 review. Real physical history/custodian
designation, scientific approval, Stage 5B, paper/live and capital remain separate
future gates. No real historical/holdout bytes, credentials, VPS, Research Memory
records, runtime, OMS, risk, overlay, safe mode, configs or live paths were used
or changed. `docs/project_status.md` and the 02I proposal are unchanged.
