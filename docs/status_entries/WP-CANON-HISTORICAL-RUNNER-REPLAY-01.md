# WP-CANON-HISTORICAL-RUNNER-REPLAY-01

Status: implementation and mandatory T3 validation complete on the dedicated
protected-package branch after fast-forward integration of merged PR #719.
The package is ready for Side 20 exact-head review and remains unmerged.

## Scope and outcome

- Added explicit current-consumability and historical-consumed-replay
  validation postures for KDAUTH, committed reservations, durable dispatches,
  and execution-history readers.
- Current/precreation/writer/consumption paths still require the exact current
  runner path, bytes, hash, length, UTF-8 content, embedded version, and
  path/symlink protections.
- Historical replay requires the exact permanent `authorization_consumed`
  lifecycle, immutable KDAUTH/manifest/dispatch bindings, and exact committed
  reservation/creation links. It omits only current mutable runner-byte
  dereference and grants no creation, consumption, retry, recovery, dispatch,
  or runner authority.
- H-004 KDAUTH, manifest, dispatch, audit, runner binding, and historical
  authority remain unchanged. No H-004 execution occurred.

## Changed paths

- `tools/canon_intake/dispatch_authorization.py`
- `tools/canon_intake/dispatch_authorization_reservation.py`
- `tools/canon_intake/execution_event.py`
- `tests/test_dispatch_authorization.py`
- `tests/test_dispatch_authorization_reservation.py`
- `tests/test_execution_event.py`
- `tests/test_dispatch_writer.py`
- `docs/architecture/canon_dispatch_execution_control_plane.md`
- `docs/status_entries/WP-CANON-HISTORICAL-RUNNER-REPLAY-01.md`

## Validation

- Preserved branch fast-forwarded from
  `34f8bddc2971b79aed8b26da07dbecaff10c0c7b` to merged main
  `92a12a252f37b5c073d67303876d5d0968cb7aa0`. PR #719 changed only
  `tools/agent_inbox_intake/service.py` and `tests/test_agent_inbox_intake.py`.
- The protected tracked-patch SHA-256 remained
  `ecde2df917b6af93f459c20431214ad6d33d0347` across the fast-forward, and all
  nine package-file hashes remained byte-identical.
- Final focused authorization/reservation/dispatch/execution-event suite:
  `256 passed, 5 skipped`.
- Adjacent CANON dispatch suites: `180 passed, 3 skipped`.
- Isolated research-query suite: `82 passed`.
- Real H-004 evolved-runner replay, strict-current rejection, immutable
  binding drift, permanent-consumption, read-only history, and no-authority
  adversarial coverage all passed inside the focused suite.
- Mandatory full release exited zero. Profile `full-release-balanced-v1`
  completed all 48 / 48 shards with exact 185 / 185 unique tracked test-file
  assignment, zero missing or duplicate assignments, and zero timeouts. The
  slowest shard was shard 41 at 896.641 seconds, below the 1,800-second limit.

## Boundary and next authority

No runtime, OMS, reconciliation, risk, overlay, safe-mode, config, live-trading,
schema, query-layer, or H-004 artifact path changed. This package does not
resume CPW-RESEARCH-02 and must not be self-merged. Side 20 exact-head review
and Karl merge remain required.
