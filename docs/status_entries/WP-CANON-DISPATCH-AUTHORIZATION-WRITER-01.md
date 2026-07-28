# WP-CANON-DISPATCH-AUTHORIZATION-WRITER-01

- Package class: protected control-plane KDAUTH writer plus one narrow
  read-only integrity sentinel.
- Base: `711687eafab5889b7130f09731ec24ed2e4a75db`.
- Branch/worktree:
  `codex/wp-canon-dispatch-authorization-writer-01` at
  `C:\GitHub\crypto-perp-wedge-wp-canon-dispatch-authorization-writer-01`.
- Retained-worktree proof: pre-refresh `HEAD` was
  `73ae69308a348816e16870f2d233855bb2a7575d`; status, staged diff, and branch
  diff were empty; ahead/behind versus the then-cached `origin/main` was
  `0/0`. After `git fetch --prune origin`, current `origin/main` was exact
  reservation-ledger merge `711687eafab5889b7130f09731ec24ed2e4a75db`.
  The branch rebased cleanly with no unique commit or conflict.
- GitHub preflight: zero open PRs; no overlapping or equivalent KDAUTH writer
  or dispatch-without-consumption sentinel existed.

## Delivered capability

The writer accepts an exact regular review-path proposal, independent reviewed
whole-file SHA-256, exact approving actor, and fresh schema-valid attempt ID.
It performs complete candidate validation and current-plus-retained collision
scans before and inside the shared crossing lock. The independent review hash
and byte length are checked against the pre-lock proposal, in-lock reread,
exclusive-created target, `authorization_created`, and committed reservation
terminal. `authorization_core_sha256` remains a distinct semantic-core binding.

Under one instance of the merged repository-wide lock, the writer:

1. durably publishes `attempt_reserved` through the ledger's public lock-held
   API before any KDAUTH target or lifecycle mutation;
2. exclusive-creates, flushes/fsyncs, rereads, and byte-compares the target;
3. appends, flushes/fsyncs, rereads, and validates one exact
   `authorization_created`;
4. performs writer-time active-lifecycle validation;
5. appends and rereads one `crossing_committed` terminal that binds the exact
   raw creation line;
6. returns success only after the shared lock exits cleanly.

A fully proven pre-append failure may restore the exact prior lifecycle bytes,
prove target absence and durability, and append one
`crossing_rolled_back_clean`. Partial write, fsync, append, terminal, rollback,
or cleanup uncertainty remains integrity-critical, preserves evidence, burns
all identities, and requires operator inspection. Reservation history is never
deleted, truncated, rewritten, repaired, or reused.

The separate lifecycle API rereads and validates the exact authoritative
KDAUTH, complete audit, current and retained history, next event identity, and
closed state under the same lock. Exact consumption additionally requires a
schema-valid durable dispatch with matching KDAUTH, queue, Gate-Q, run, runner,
artifact, dataset, denominator, budget, execution, and output bindings. It does
not implement or invoke a dispatch writer.

The additive
`v_integrity_dispatch_authorization_dispatch_without_consumption` view reports
only a valid canonical dispatch whose exact committed KDAUTH lacks its exact
matching `authorization_consumed` event. Mismatched consumption remains
visible. Created, revoked, or superseded authorizations without a dispatch
remain empty; repeated initialization is stable and read-only.

## Same-PR path-TOCTOU closure

PR #674 now anchors both mutable KDAUTH surfaces before reservation. The
canonical target and lifecycle-audit parents must already exist beneath the
repository root as real directory chains with no symlink, junction, or reparse
component. Missing parents stop before `attempt_reserved`; the writer does not
create them.

The final in-lock validation opens and retains stable parent handles. On
POSIX, final operations use `dir_fd` plus `O_NOFOLLOW`; on Windows they use
no-reparse directory handles and `NtCreateFile` relative to the retained parent
handle. Exclusive target creation, audit open/create and append, byte rereads,
identity checks, rollback truncate/delete, and directory durability all remain
relative to those anchors. Target and audit file handles remain open through
the relevant reservation terminal.

A post-reservation parent or final-component substitution is
integrity-critical. The writer verifies both the retained object identity and
the current canonical path identity before each protected mutation and before
the terminal. It never writes through the redirected location and never
classifies substitution as a clean rollback. Clean rollback remains available
only while the original anchors and exact final-component identities are
proven, with handle-relative restoration and durability.

The correction changes exactly the writer, its focused tests, and this status
entry. Direct synthetic regressions replace the target parent, audit parent,
and target final component after successful reservation publication, and
prove no redirected write. Separate target/audit missing-parent cases prove
failure before reservation. The existing positive, pre-reservation link,
rollback, partial-write, concurrency, lifecycle, and sentinel coverage remains
passing.

## Exact tracked scope

Created:

- `tools/canon_intake/dispatch_authorization_writer.py`
- `tests/test_dispatch_authorization_writer.py`
- this status entry

Modified:

- `tools/canon_intake/dispatch_authorization.py`
- `tests/test_dispatch_authorization.py`
- `tools/research_query/query_layer.py`
- `tools/research_query/views.sql`
- `tests/test_research_query.py`
- `docs/architecture/canon_dispatch_execution_control_plane.md`

The Karl mechanism packet remains untracked at
`scratch/WP-CANON-DISPATCH-AUTHORIZATION-WRITER-01/karl_reviewed_bytes_binding_packet.md`.

## Boundary

This package creates capability and synthetic fixtures only. It creates no
production reservation, KDAUTH, lifecycle event, dispatch, execution event,
runner invocation, run, Result Population, scheduler/autonomy, runtime,
paper/live, OMS, risk, reconciliation, broker, exchange, credential, order,
position, balance, or capital action. Every schema, the reservation module,
queue/Gate-Q/admission/VPAPP writers, canonical 1d/funding artifacts, runner,
dependencies, configs, workflows, protected runtime surfaces, production
control-plane artifact families, and `docs/project_status.md` remain unchanged.

## Validation

Final exact-head validation evidence is recorded in the PR and execution
report. The same-PR correction's focused writer suite passes all 36 tests,
including the post-reservation junction/reparse cases on Windows. The sentinel
is empty on real repository state; the sole accepted non-empty integrity result
remains the pre-existing locked legacy Strategy Spec hash-scope
reproducibility disclosure.

## Next authority

Karl's enforcement-mechanism review and merge decision remain human gates.
After merge, the separately authorized dispatch-writer package may be resumed;
it does not start automatically. No production KDAUTH, Stage A, dispatch,
Stage B, execution event, runner, Result Population, evaluation, advisory,
replay, or broader query-read-model work follows from this package.
