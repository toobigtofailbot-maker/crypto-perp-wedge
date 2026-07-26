# Canonical Dispatch and Execution Control Plane

Status: locked Option-C design and schema contract for `WP-CANON-DISPATCH-CONTROL-PLANE-DESIGN-LOCK-01`.

This contract defines durable state for a one-shot offline-research dispatch. It creates no writer, dispatcher, runner adapter, scheduler, production dispatch, production execution event, or Result Population. Capitalized requirement words are normative.

## Decision and boundary

Option C is selected:

1. one immutable dispatch JSON record owns dispatch identity, exact authorization, and exact input/output bindings;
2. one append-only JSONL stream per run owns invocation start, every attempt outcome, and one terminal execution event;
3. the admitted queue item and admission audit remain immutable admission history;
4. provisional runner outputs remain scratch detail;
5. only a later separately gated Result Population package may create canonical scientific evidence.

Option A, a separate immutable dispatch record plus a separate immutable run record, is rejected. A run unfolds through start, progress, failure, and terminal state. Writing one immutable run record only at the end would lose in-flight and crash-visible state, while updating that record during the run would violate immutability. Option B, a mutable execution-state document, is rejected because it would erase prior progress and failure transitions. Option C therefore keeps dispatch immutable and records unfolding execution through append-only events.

The queue item and admission audit remain immutable admission history. Queue or admission mutation is forbidden under every topology; it was not the definition of Option A.

Dispatch and execution records are authoritative control-plane history only. They MUST NOT replace or claim authority for a Result Population, EXP, REP, outcome ledger, recommendation, decision, ranking, readiness, promotion, candidate lifecycle, scheduler, runtime, paper, or live surface. They MUST NOT contain GO, NO-GO, winner, candidate-worthy, readiness, or recommendation semantics.

## Directories and identities

| Artifact | Authoritative path | Identity |
| --- | --- | --- |
| Dispatch record | `research/queue/dispatch_records/<dispatch_id>.dispatch_record.json` | `DSP-YYYYMMDD-XXXXXXXX` |
| Execution stream | `research/queue/execution_events/<run_id>.execution_events.jsonl` | `RUN-YYYYMMDD-XXXXXXXX` |
| Execution event | one JSON object plus LF in the run stream | `EXEC-EVENT-<run_id>-NNNNNN` |
| Exact Karl dispatch authorization | `research/queue/dispatch_authorizations/<authorization_id>.dispatch_authorization.json` | family/revision scoped `KDAUTH-<FAMILY>-R<REVISION>-NNNN` |
| Dispatch-authorization lifecycle audit | `research/queue/dispatch_authorization_audit/dispatch_authorization_events.jsonl` | `KDAUTH-EVENT-<authorization_id>-NNNNNN` |

`XXXXXXXX` is eight uppercase alphanumeric characters. The dispatch date MUST equal the UTC date of `created_at`. Event sequence numbers start at 1, are contiguous and strictly increasing, and are rendered as six digits in the event ID. Paths are repo-relative POSIX paths with no traversal, backslashes, empty components, or symlink escape.

IDs, exact target paths, run IDs, event IDs, and queue-item/authorization pairs are permanently single-use. Removal of a file does not free an identity. A future writer MUST scan all current dispatch records, every execution line, durable Karl authorization sources, and retained repository history before crossing. An identity found in any one source is consumed. Missing or ambiguous history fails closed.

No production directory or instance is created by this design package.

## Exact dispatch authorization

Normative schemas:

- `research/schemas/canon_dispatch_authorization.schema.json`;
- `research/schemas/canon_dispatch_authorization_audit_event.schema.json`.

The authorization family mirrors the existing Gate-Q and standalone Gate C-VP
approval posture. It is a closed Draft 7 JSON artifact approved by Karl for one
exact, pre-declared, single-use dispatch. Its target path is derived from its
family/revision-scoped identifier. For H-004-R2 the identifier form is
`KDAUTH-H004-R2-NNNN`.

The artifact binds:

- the exact admitted queue-item bytes and state plus exact Gate-Q whole-file and
  semantic-core hashes;
- the pre-declared dispatch ID/path and run ID/execution-stream path;
- the exact frozen Stage-A dispatcher packet bytes and byte length;
- exact Strategy Spec, external-content-readiness, variant-planning approval,
  Variant Manifest, Sweep Plan, and Gate-Q lineage;
- the exact canonical 1d catalog/data identity, direct-public-snapshot posture,
  canonical cadence and column contract, completed-bar findings, lineage
  validator source identity, and rebuilt-catalog validation identity;
- funding mode `on`, the exact funding provenance/data identity, event
  semantics, and no-fill/no-interpolation posture;
- structured runner module/source/version identity, never a command;
- denominator, budget, seed, workers, one-shot/no-retry posture, and scratch
  plus execution-event output targets;
- the complete no-downstream-authority declaration.

The exact approval statement is:

> Karl approves one single-use offline research dispatch for the exact queue
> item, dispatch ID, run ID, frozen dispatcher packet, lineage, dataset,
> funding identity, runner, budget, and output targets bound by this artifact,
> and grants no downstream authority.

The complete `authorization_core` is hashed with
`repo_canonical_json_v1`, stored as `authorization_core_sha256`, and scoped as
`dispatch_authorization_core_v1`. The authorization file does not contain its
own whole-file hash. Consumers compute SHA-256 over the exact bytes, including
the required final LF, and bind both that hash and the byte length.

The exact authorization serialization is UTF-8 without BOM, lexicographically
sorted keys, two-space JSON indentation, no trailing spaces, and exactly one
trailing LF. CRLF, a missing or double LF, bytes after the LF, or any
serialization drift fails closed. Lifecycle-audit lines use
`repo_canonical_json_v1` plus one LF.

Freshness is content-bound only. `approved_at` is mandatory, parseable, and
timezone-aware, but there is no expiry, same-day requirement, Git-time
comparison, or wall-clock window. Any bound identity, field, byte length, or
hash drift requires a new authorization.

The canonical 1d binding is the route merged by
`WP-RUNNER-1D-CANONICAL-ROUTE-01`: catalog and Parquet bytes are bound
separately, the tracked lineage validator source is bound by exact path,
SHA-256, and byte length, and `validation_identity` binds the catalog hash,
validator path/hash, and successful exact catalog rebuild. The KDAUTH runner
binding likewise names `tools.research_runner.run_offline_sweep`, its tracked
source bytes, and `wp-s2c-190-build-test-v1`. These are content bindings only;
this contract does not invoke the merged route.

The lifecycle vocabulary is closed:

- `authorization_created`, exactly once and first;
- `authorization_superseded`, only before consumption and referencing a new
  authorization;
- `authorization_revoked`, only before consumption and permanently terminal;
- `authorization_consumed`, exactly once and permanently terminal.

The lifecycle stream is append-only canonical JSONL. It never rewrites,
truncates, deletes, or repairs a prior line. A malformed or partial tail fails
closed. Superseded, revoked, or consumed authorizations are permanently
unusable. Deletion does not release an authorization ID/path, dispatch ID, run
ID, queue target, queue/authorization pair, or target path. A new attempt
requires fresh authorization, dispatch, and run identities.

KDAUTH alone does not create a dispatch, start or invoke a runner, create an
execution event, authorize retry/recovery, or grant Result Population,
ranking, recommendation, candidate, readiness, promotion, scheduler, runtime,
paper/live, OMS, risk, reconciliation, broker, exchange, order, position,
balance, capital, or notification authority.

## Protected KDAUTH crossing reservations

Normative schema:
`research/schemas/canon_dispatch_authorization_crossing_reservation_event.schema.json`.

KDAUTH crossing attempts use a separate authoritative append-only reservation
ledger. It does not extend or change the closed KDAUTH lifecycle vocabulary.
The authoritative root is
`research/queue/dispatch_authorization_reservations/`, with exactly one stream
per attempt at
`<attempt_id>.crossing_reservation.jsonl`. Attempt IDs use
`KDAUTH-XING-YYYYMMDD-XXXXXXXX`; event IDs are the derived
`<attempt_id>-000001` reservation and optional `<attempt_id>-000002` terminal.
Each stream contains exactly one first `attempt_reserved` event and zero or one
terminal, never more than two lines and never an event after the terminal.

The protected order is:

1. acquire the repository-wide KDAUTH crossing lock at
   `research/queue/dispatch_authorization_audit/.dispatch_authorization.lock`;
2. validate the exact reviewed proposal and all references;
3. durably publish and prove the complete `attempt_reserved` line through a
   no-overwrite, ID-derived reservation path;
4. only then create the KDAUTH target and append `authorization_created`;
5. append exactly one reservation terminal under the same still-held lock;
6. release the lock.

The reservation API deliberately exposes lock-held operations so the later
KDAUTH writer can keep the same lock instance across reservation, KDAUTH
target/lifecycle mutation, and terminal append. No KDAUTH target or lifecycle
mutation may begin before the reservation commit is proven durable.

The terminal vocabulary is closed:

- `crossing_committed` binds the exact resulting KDAUTH bytes/core and exact
  raw `authorization_created` lifecycle line;
- `crossing_rolled_back_clean` proves target absence and exact lifecycle-audit
  length restoration at terminal-write time while retaining the reservation;
- `crossing_integrity_critical` records closed failure/uncertainty and
  target/audit state classifications and always requires operator inspection.

Every committed reservation permanently consumes its attempt, authorization,
dispatch, run, target-path, queue-item/authorization, reviewed-content, and
core-hash identity bindings. Success, clean rollback, integrity-critical
failure, a missing terminal, and deletion all retain the burn. Current streams
and committed retained Git history are grouped by exact attempt ID and derived
stream path. Append-only prefixes collapse to the single longest valid logical
attempt; non-prefix rewrites and competing longest versions fail closed.
Distinct logical attempts are globally compared, and any collision on an
authorization, dispatch, run, target-path, queue/authorization,
reviewed-content, or authorization-core identity fails closed. Reservation
history is never rewritten, truncated, deleted, repaired in place, or
interpreted as retry/recovery authority.

The authoritative path remains lexical while resolved confinement is checked
separately. A dangling symlink, supported Windows junction/reparse point,
redirecting component, or non-file entry at a reserved target is not absence.
Clean rollback and initial publication both reject those entries without
following them. A terminal timestamp cannot precede its reservation or initial
event; a committed terminal cannot precede the exact linked
`authorization_created`, which must remain strictly later than
`attempt_reserved`.

Clean-rollback terminal publication and later replay have deliberately
different audit-length checks. Under the held crossing lock, immediately
before terminal append, the canonical shared lifecycle audit must have exactly
the recorded final length. During later read-only validation, the canonical
audit may be longer because unrelated KDAUTH events can append legally, but it
must never be shorter than the recorded final length and must contain no
matching `authorization_created`. Later unrelated append-only growth does not
invalidate the historical rollback or release its permanently burned
identities.

Committed-crossing publication and replay also have deliberately different
current-lifecycle requirements. Under the held crossing lock, immediately
before appending `crossing_committed`, the exact KDAUTH must still be in its
created, consumable lifecycle state. Later read-only replay proves the
historical committed crossing from the exact KDAUTH content, complete valid
lifecycle audit, original `authorization_created` bindings, chronology, and
raw-line link independently of current consumability. A later lawful
`authorization_consumed`, `authorization_revoked`, or
`authorization_superseded` terminal permanently prevents reuse but does not
invalidate the earlier committed crossing.

Read-only integrity visibility is exposed through
`v_integrity_dispatch_authorization_crossing_reservations`. It surfaces
integrity-critical and unterminated attempts, invalid sequences/bindings,
committed crossings without the exact creation event, and any
`authorization_created` event without an earlier exact reservation. It uses
the same current-plus-retained logical-attempt model, so deleted unresolved or
integrity-critical attempts remain visible and cross-attempt protected-identity
collisions use the closed
`reservation_identity_collision_across_attempts` finding. The reservation
ledger is control-plane integrity history only: it is not Karl's approval, a
KDAUTH artifact or lifecycle event, a dispatch/execution record, scientific
evidence, runner/scheduler/runtime authority, or paper/live,
OMS/risk/reconciliation, broker/exchange/order/capital authority.

This reservation capability is a prerequisite only. The retained protected
KDAUTH-writer package must be refreshed after this ledger merges and must wire
the exact reservation-before-mutation sequence under the same lock. This
package does not resume or implement that writer.

## Immutable dispatch record

Normative schema: `research/schemas/canon_dispatch_record.schema.json`.

The record MUST bind:

- its derived dispatch ID/path, creation timestamp, and the sole state `dispatched`;
- one exact admitted queue item ID/path and raw-file SHA-256;
- the exact Gate-Q ID/path, full-file SHA-256, core SHA-256, core scope, and canonicalization;
- one fresh exact Karl authorization, including its ID, source path/hash, actor, time, scope, queue item, dispatch ID, and run ID;
- one run ID and derived execution-stream path;
- structured runner module, source path, version, and source SHA-256, never a command string;
- exact Strategy Spec, Variant Manifest, Sweep Plan, and dataset identities and hashes;
- denominator, budget, seed, workers, one-shot/no-retry posture, and exact scratch/event output targets;
- immutable/single-use posture and the complete non-authority declaration.

The record MUST NOT contain progress, attempt outcomes, counts, a terminal state, a mutable status, a retry instruction, a canonical Result Population target, or a free-form executable command. `dispatch_state="dispatched"` records only that the durable one-shot dispatch crossing occurred; it does not mean a process started or finished.

## Append-only execution stream

Normative schema: `research/schemas/canon_execution_event.schema.json`.

Every LF-terminated line MUST decode as one UTF-8 JSON object and MUST validate independently. Every line binds the exact dispatch ID/path/raw hash, run ID, queue-item ID, stream path, timestamp, stable event ID/sequence, and actor/tool identity. All lines in a stream MUST share those bindings.

The closed event vocabulary is:

| Event | Required payload | Ordering rule |
| --- | --- | --- |
| `run_start` | invocation start, whether the runner process started, planned denominator, budget, seed, workers, no-auto-retry | exactly once at sequence 1 |
| `attempt_outcome` | contiguous attempt number, unique variant ID, retry ordinal 0, closed outcome/reason, budget and denominator counting truth | zero or more after start and before terminal |
| `run_terminal` | closed terminal state/reason, process-start truth, full denominator accounting, actual budget | exactly once and last |

An `attempt_outcome` is terminal for that one planned attempt. Because v1 admits no retry allowance, `retry_ordinal` MUST be 0 and a variant ID MUST NOT recur in the run. No `attempt_outcome` event may use `not_attempted`, and no attempt event is emitted for an unattempted denominator member. The terminal event MUST record the unattempted remainder. `attempts_recorded` and budget `actual` MUST exclude that remainder, while the full denominator MUST continue to include it.

The stream MUST never rewrite, truncate, reorder, or delete an earlier line. A partial or malformed tail is crash-visible integrity evidence and MUST NOT be silently repaired. Corrections require a separately authorized future protocol; none is defined here.

## Execution states

| From | Event | To | Required truth |
| --- | --- | --- | --- |
| no stream | `run_start` | invocation recorded | sequence 1; exact dispatch binding |
| invocation recorded | `attempt_outcome` | invocation in progress | process started; next sequence/attempt; unique variant |
| invocation recorded or in progress | `run_terminal` | terminal | exactly one closed terminal; all denominator members visible |
| terminal | any event | invalid | no event may follow terminal |

The closed terminal vocabulary is:

- `run_completed`: the process started; attempts, budget actual, and all non-`not_attempted` outcome counts equal the planned denominator; `not_attempted=0`.
- `run_failed_process_start`: the runner process did not start; actual attempts are 0; every planned member is `not_attempted`.
- `run_failed_midrun`: the process started and stopped before the denominator completed; actual attempts are strictly less than planned; the remainder is explicitly `not_attempted`.
- `run_blocked`: a fail-closed condition prevented or halted progress; completed attempt outcomes remain and every remainder is explicitly `not_attempted`.

`success`, `pass`, GO, candidate, ranking, recommendation, and readiness are not terminal states.

## Budget and denominator accounting

The denominator basis is `committed_pre_registered_population_count`. It MUST equal the Variant Manifest value, Sweep Plan value, dispatch planned count, and budget upper bound. The sole budget metric is `variant_attempts`; unit is `attempts`; every actual attempt counts; and `actual <= upper_bound` MUST hold.

V1 fixes `retry_allowance=0`. Since the upper bound equals the denominator, no retry fits inside the admitted budget. A recovery invocation is not a retry: it requires a fresh dispatch ID, run ID, target paths, and exact Karl authorization.

Every terminal event MUST account for the full planned population. The sum of all nine outcome counts MUST equal `population_accounted_total`, which MUST equal `planned`. The sum excluding `not_attempted` MUST equal `attempts_recorded` and budget `actual`. `not_attempted` MUST equal the unattempted remainder. These cross-field equations are semantic-validator requirements because Draft 7 cannot compare or sum sibling values.

The closed attempt-outcome categories are `successful`, `failed`, `invalid`, `excluded`, `errored`, `aborted`, `filtered`, and `data_unavailable`. Terminal denominator accounting uses those eight categories plus `not_attempted`. Failed, invalid, excluded, errored, aborted, filtered, unavailable, and unattempted members MUST remain visible; winner-only retention and silent drops are forbidden.

## Single-use, locking, and crossing requirements

A future dispatch writer MUST:

1. resolve the repository root and reject symlinked path components or escapes;
2. parse and validate the queue item, Gate-Q, authorization, runner, artifacts, dataset, denominator, budget, and proposed dispatch bytes;
3. scan dispatch IDs, run IDs, queue-item/authorization pairs, target paths, authorization history, execution events, and retained history for reuse;
4. acquire one repository-wide transient exclusive dispatch-crossing lock using an atomic `O_CREAT|O_EXCL`-equivalent primitive;
5. repeat every validation and reuse scan inside the lock immediately before creation;
6. exclusive-create the exact dispatch target, write the already validated bytes completely, flush, and fsync;
7. preserve any post-crossing file or failure evidence and release the lock without invoking a runner automatically.

The exclusive-create call is the dispatch crossing. A collision, partial write, fsync uncertainty, or lock-cleanup failure consumes the proposed identities and requires operator inspection. The writer MUST NOT delete, overwrite, truncate, reuse, or repair the target in place.

A future execution-event writer MUST use a per-run exclusive append lock. Under that lock it MUST reread and validate the entire existing stream, verify exact dispatch binding, enforce next sequence/event ID and legal ordering, append one complete canonical JSON line plus LF, flush, and fsync. It MUST NOT append after a terminal event or truncate a failed append.

## Failure and recovery matrix

| Failure point | Durable history | Required response | Forbidden response |
| --- | --- | --- | --- |
| validation/reuse check before crossing | no new dispatch | fix inputs and obtain fresh authority if content/identity changes | bypass validation |
| lock/collision/uncertain exclusive create | collision or uncertain target | fail closed; preserve evidence; new identities and fresh Karl authority | reuse or overwrite |
| after dispatch, before stream start | immutable dispatch only | operator inspection; append a non-running start and blocked/process-start terminal only when facts are provable | delete dispatch or auto-fire |
| runner process cannot start | dispatch, start, process-start terminal | stop | automatic second invocation |
| process fails midrun | dispatch, start, completed attempt lines, midrun terminal | preserve partial counts and remainder | resume silently or drop failures |
| fail-closed condition | existing lines plus blocked terminal when safely appendable | stop and preserve cause outside canonical evidence | mutate prior lines |
| crash leaves no terminal | incomplete stream remains visible | operator inspection; append a blocking terminal only if sequence/count facts are trustworthy, otherwise leave incomplete | infer completion or repair tail |
| completed run | completed terminal | later separately gated RP handoff may read scratch and control history | write canonical RP from this authority |

Any recovery run for the same queue item MUST use a new dispatch ID, run ID, paths, and fresh narrow Karl authority. The original dispatch and stream remain permanent. No scheduler, watcher, recurring worker, automatic retry, or automatic recovery is authorized.

## Scratch outputs and Result Population handoff

Runner output targets in the dispatch record MUST remain under package/run-specific scratch paths and are provisional detail. Scratch may contain metrics or diagnostics but has no canonical authority. Dispatch/execution history may prove which inputs ran and how attempts terminated; it does not itself prove strategy performance.

A later separately authorized Result Population package MAY read the immutable dispatch, complete execution stream, and scratch outputs. It MUST independently validate scientific evidence, denominator, lineage, and the Result Population schema/validator. It MUST NOT mutate queue, admission, dispatch, or execution history. This contract neither creates nor authorizes `RP-0007`.

## Future packages

Separate Karl/Main-authorized packages are required for:

- a protected exact dispatch-authorization writer and lifecycle-event append
  mechanism implementing this locked contract;
- a dispatch writer and execution-event writer implementing every lock, reuse, path, and failure rule above;
- read-only integrity/query views and a replay validator;
- any later runner-adapter capability needed to consume a reviewed production
  dispatcher packet without broadening the merged canonical 1d route;
- the one-shot H-004-R2 dispatch and any later canonical Result Population handoff.

None may be inferred from this contract lock.

## Traceability

`WP-CANON-H004-DISPATCH-GATED-01` Stage A stopped at base
`1c22edf602f748ed03d9304c66b4b40cd6f0d601` because the repo had no durable
dispatch/execution-state contract. Its twelve preserved uncommitted evidence
files remain read-only. The canonical 1d route has since merged, but no
refreshed Stage A has frozen the exact production dispatcher packet. This
Option-C lock and the KDAUTH contract resolve representation and validation
semantics only. A real production KDAUTH remains impossible until a later
separately authorized refreshed Stage A freezes that exact packet.
