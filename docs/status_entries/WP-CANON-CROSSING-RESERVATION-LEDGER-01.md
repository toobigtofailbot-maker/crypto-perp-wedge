# WP-CANON-CROSSING-RESERVATION-LEDGER-01

- Package class: protected control-plane integrity history; additive closed
  Draft-7 schema, protected append-only writer/validator, and read-only
  integrity visibility.
- Base: `73ae69308a348816e16870f2d233855bb2a7575d`.
- Branch/worktree:
  `codex/wp-canon-crossing-reservation-ledger-01` at
  `C:\GitHub\crypto-perp-wedge-wp-canon-crossing-reservation-ledger-01`.
- Preflight: `origin/main` equaled the authorized base; the primary checkout
  and retained KDAUTH-writer worktree were clean; GitHub had zero open PRs and
  no overlapping reservation/incident capability was present.

## Locked decisions implemented

Main's twelve package locks are preserved:

1. crossing reservations are separate from the closed KDAUTH lifecycle;
2. `attempt_reserved` is durable before any KDAUTH target/audit mutation;
3. one repository-wide KDAUTH crossing lock spans reservation, later KDAUTH
   mutation, and terminal append;
4. the attempt ID and per-attempt path are ID-derived and single-use;
5. the first line is published complete through an exclusive temporary file
   and atomic no-overwrite hard-link placement;
6. the terminal is one canonical append under the same lock;
7. success, clean rollback, integrity-critical failure, and missing terminal
   all permanently burn the complete identity tuple;
8. rollback never truncates, deletes, or repairs reservation history;
9. current KDAUTH/lifecycle/dispatch/execution surfaces and retained Git
   history participate in collision enforcement;
10. the independent reviewed-whole-file hash/length remains distinct from the
    authorization-core hash;
11. unresolved, critical, invalid, and missing-prior-reservation states remain
    visible through one closed integrity view;
12. the ledger grants no KDAUTH, approval, dispatch, execution, evidence,
    retry, runner, scheduler/runtime, paper/live, OMS/risk/reconciliation, or
    broker/exchange/order/capital authority.

## Delivered contract

- Authority root:
  `research/queue/dispatch_authorization_reservations/`.
- Stream:
  `<attempt_id>.crossing_reservation.jsonl`, with exactly one
  `attempt_reserved` and zero or one closed terminal.
- Attempt/event identities:
  `KDAUTH-XING-YYYYMMDD-XXXXXXXX`,
  `<attempt_id>-000001`, and `<attempt_id>-000002`.
- Schema:
  `canon_dispatch_authorization_crossing_reservation_event_v1`.
- Protected module:
  `tools/canon_intake/dispatch_authorization_reservation.py`.
- Shared lock:
  `research/queue/dispatch_authorization_audit/.dispatch_authorization.lock`.
- Integrity view:
  `v_integrity_dispatch_authorization_crossing_reservations`.

Initial publication writes, fsyncs, and rereads one non-authoritative
package-owned temporary file, atomically hard-links it to the absent final
path without overwrite, rereads the final bytes, and fsyncs the containing
directory where supported. Windows directory-fsync unavailability is returned
explicitly as `not_supported_on_platform`; it is not misreported as verified.
Any failure after publication is integrity-critical and never deletes the
final stream.

Terminal append rereads and validates the one-line stream, proves exact common
bindings and the selected cross-surface outcome, appends one canonical line,
flushes/fsyncs, then rereads the exact two-line stream. No terminal failure
truncates or deletes the initial reservation.

## PR #673 fail-closed follow-up

The same PR now collapses current and retained append-only versions into one
logical state per exact attempt ID and derived stream path. A valid one-line
prefix followed by its two-line terminal is one attempt. Non-prefix rewrites,
ambiguous longest versions, and protected identity collisions across distinct
logical attempts fail closed. KDAUTH validation requires exactly one committed
logical attempt with complete bindings equal to the KDAUTH and its exact
`authorization_created` event; zero or multiple matches fail closed.

Integrity collection uses that same current-plus-retained model. Deleted
integrity-critical and genuinely unterminated attempts remain visible, while a
retained one-line prefix cannot create a false missing-terminal finding after
a valid terminal exists. Cross-attempt collisions use the closed finding
`reservation_identity_collision_across_attempts` and reason
`protected_identity_collision_across_distinct_attempts`.

Lexical authoritative paths are preserved separately from resolved
confinement. Dangling symlinks, supported Windows junction/reparse points,
redirecting components, and non-file target entries are rejected without being
followed. Terminal chronology is closed across `reserved_at`, initial
`occurred_at`, exact `authorization_created.occurred_at`, and committed
terminal `occurred_at`. No reservation schema amendment was required.

## Validation and preservation

- Same-PR reservation/KDAUTH follow-up: `122 passed, 5 skipped`. Four new skips
  are limited to specific symlink fixtures that this Windows environment
  cannot create; the Windows junction/reparse fixture executed and passed.
  The fifth skip is the pre-existing KDAUTH symlink-fixture limitation. No
  skip or xfail bypasses a failing semantic assertion.
- Protected KDAUTH, Gate C-VP, Gate-Q, queue, external-readiness,
  dispatch/execution-contract, and retained-history regressions:
  `399 passed, 10 skipped`; the additional five skips are pre-existing
  protected-writer symlink-fixture limitations on Windows.
- Query-focused checks: `3 passed, 112 deselected`; the view is empty on the
  real repository and non-empty with the closed cross-attempt collision type
  and reason for synthetic duplicates.
- Registry validation: all 25 `tools.registry.validate_*` modules passed. The
  funding validator used its supported read-only `--data-root` override to the
  primary checkout because the clean worktree intentionally lacks the
  gitignored Parquet.
- JSON/Draft-7: 1,171 tracked JSON files, 12 JSONL files / 27,585 non-empty
  lines, and all 43 Draft-7 schemas parse and validate.
- Integrity: all 60 `v_integrity_*` views executed; 59 are empty and the sole
  non-empty row is the unchanged locked
  `v_integrity_strategy_spec_legacy_hash_scope_reproducibility` disclosure.
  The new reservation view is empty on real repo state.
- Same-PR `full-release-balanced-v1`: all 154 tracked test files are assigned
  exactly once across 48 shards; missing, duplicate, and untracked assignments
  are zero; every selected shard completes and passes with no failure, error,
  or timeout.
- Existing protected KDAUTH/lifecycle/dispatch/execution schemas are unchanged.
- Queue/Gate-Q/VPAPP writers, canonical 1d/funding identities, runner,
  dependencies, configs, runtime, paper/live, OMS/risk/reconciliation, and
  production control-plane artifact families are unchanged.
- No production reservation, KDAUTH, lifecycle event, dispatch, execution
  event, run, Result Population, or runner invocation was created.
- The retained
  `C:\GitHub\crypto-perp-wedge-wp-canon-dispatch-authorization-writer-01`
  worktree remains untouched.

Next action after merge only: refresh and resume the retained protected
KDAUTH-writer package, wire reservation-before-mutation under this same lock,
retain the independent reviewed-bytes binding, and add the separately scoped
dispatch-without-consumption reconciliation. This package does not perform
that continuation.
