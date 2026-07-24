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

## Validation and preservation

- Focused reservation tests: `19 passed`. Protected KDAUTH, Gate C-VP, Gate-Q,
  queue, dispatch/execution-contract, and retained-history regressions:
  `346 passed, 6` accepted Windows symlink skips. Coverage includes a synthetic
  reservation-before-KDAUTH success crossing, clean rollback,
  integrity-critical, missing-terminal, retained-deletion, control-surface
  collision, exact-byte, partial-append, and query-registration coverage.
- Query contract checks: `3 passed, 63 deselected`; the new view is registered
  with the exact closed columns, is empty on the real repository, and is
  non-empty for synthetic integrity-critical/missing-terminal/
  missing-prior-reservation cases.
- Registry validation: all 25 `tools.registry.validate_*` modules passed. The
  funding validator used its supported read-only `--data-root` override to the
  primary checkout because the clean worktree intentionally lacks the
  gitignored Parquet; the first default-path invocation disclosed that missing
  local file and is not pass evidence.
- JSON/Draft-7: 1,171 tracked JSON files, 12 JSONL files / 27,585 non-empty
  lines, and all 43 Draft-7 schemas parse and validate.
- Integrity: all 60 `v_integrity_*` views executed; 59 are empty and the sole
  non-empty row is the unchanged locked
  `v_integrity_strategy_spec_legacy_hash_scope_reproducibility` disclosure.
  The new reservation view is empty on real repo state.
- `full-release-balanced-v1`: all 154 tracked test files were assigned exactly
  once across 48 shards; missing, duplicate, and untracked assignments were
  zero; every shard completed and passed with no failure or timeout. The
  dedicated query shard passed in 1,013.125 seconds.
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
