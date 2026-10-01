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
| Dispatch manifest | `research/queue/dispatch_manifests/<manifest_id>.dispatch_manifest.json` | `DMAN-H004-R2-NNNN` |
| Dispatch record | `research/queue/dispatch_records/<dispatch_id>.dispatch_record.json` | `DSP-YYYYMMDD-XXXXXXXX` |
| Execution stream | `research/queue/execution_events/<run_id>.execution_events.jsonl` | `RUN-YYYYMMDD-XXXXXXXX` |
| Execution event | one JSON object plus LF in the run stream | `EXEC-EVENT-<run_id>-NNNNNN` |
| Exact Karl dispatch authorization | `research/queue/dispatch_authorizations/<authorization_id>.dispatch_authorization.json` | family/revision scoped `KDAUTH-<FAMILY>-R<REVISION>-NNNN` |
| Dispatch-authorization lifecycle audit | `research/queue/dispatch_authorization_audit/dispatch_authorization_events.jsonl` | `KDAUTH-EVENT-<authorization_id>-NNNNNN` |

`XXXXXXXX` is eight uppercase alphanumeric characters. The dispatch date MUST equal the UTC date of `created_at`. Event sequence numbers start at 1, are contiguous and strictly increasing, and are rendered as six digits in the event ID. Paths are repo-relative POSIX paths with no traversal, backslashes, empty components, or symlink escape.

IDs, exact target paths, run IDs, event IDs, and queue-item/authorization pairs are permanently single-use. Removal of a file does not free an identity. A future writer MUST scan all current dispatch records, every execution line, durable Karl authorization sources, and retained repository history before crossing. An identity found in any one source is consumed. Missing or ambiguous history fails closed.

## Non-circular dispatch manifest

Normative schema:
`research/schemas/canon_dispatch_manifest.schema.json`.

The immutable manifest is non-authorizing commitment evidence. It exists
before KDAUTH and commits the exact queue, dispatch/run identities, creation
timestamp, full lineage, canonical 1d and funding identities, runner,
denominator, budget, execution parameters, exact scratch run directory, every
exact provisional-result leaf, and execution-event target. Root-only,
wildcard, duplicate, omitted, ambiguous, circular, self-hash, and future-KDAUTH
representations are invalid.

Manifest bytes use the existing sorted two-space UTF-8 JSON plus one LF
serialization. The manifest contains neither its whole-file hash/length nor
any KDAUTH reference. Its protected writer validates before and in-lock,
scans current and retained identity history, and exclusive-creates only the
ID-derived target. It creates no KDAUTH, dispatch, execution event, runner
invocation, retry, or downstream authority.

The dependency graph is strict:

`manifest -> KDAUTH manifest commitment -> byte-derived dispatch record`.

KDAUTH commits the existing manifest ID, whole-file SHA-256, and byte length.
The dispatch record is deterministically derived from the validated manifest
plus the already-existing exact KDAUTH bytes. No object commits bytes of an
object whose serialization depends on it.

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
- the exact immutable dispatch-manifest ID, whole-file SHA-256, and byte
  length;
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
> item, dispatch ID, run ID, immutable dispatch manifest, lineage, dataset,
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

Runner validation has two explicit lifecycle-aware postures. Current
consumability is content-fresh against mutable current code: precreation review,
active KDAUTH validation, dispatch creation, and dispatch consumption require
the current runner path, bytes, hash, length, UTF-8 content, embedded version,
and path/symlink protections to match exactly. Historical consumed replay first
proves the exact immutable KDAUTH, manifest, dispatch, reservation, creation,
and permanent-consumption bindings, then validates the historical runner
module/path/version/hash/length bindings without dereferencing today's mutable
runner bytes. This preserves what was authorized without freezing the source
file forever. It is not retroactive authorization for changed code, a new
dispatch, consumption, retry/recovery, or runner invocation.

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
created, consumable lifecycle state and current runner bytes must match.
Later read-only historical replay succeeds only for the exact permanently
`authorization_consumed` lifecycle. It proves the historical committed
crossing from the exact KDAUTH content, complete valid lifecycle audit,
original `authorization_created` and `authorization_consumed` bindings,
chronology, raw-line link, and durable dispatch binding without consulting
today's runner bytes. Revoked, superseded, created-but-unconsumed, malformed,
or non-permanent lifecycle states cannot use this replay posture.

KDAUTH validation dispatches the existing `require_audit` and `scan_history`
arguments as an explicit phase contract:

| Validation context | `require_audit` | `scan_history` | Reservation rule |
| --- | --- | --- | --- |
| Semantic-only internal validation | false | false | No lifecycle or history scan; returns `not_recorded` |
| Writer-time active lifecycle | true | false | Current lifecycle must be created; the reservation writer separately proves its held-lock one-line attempt |
| Existing precreation-review compatibility | false | true | Complete current-plus-retained reservation scan must find zero protected-identity collisions; no committed terminal is required or accepted as freshness |
| Authoritative active KDAUTH | true | true | Current lifecycle must be created and exactly one exact committed crossing must be proven; every other collision fails |
| Historical consumed replay | required internally | separate reservation replay | Exact original creation, committed reservation, dispatch, and permanent consumption are required; only current mutable runner-byte dereference is omitted |

Exactly-one committed proof applies only to authoritative active KDAUTH
validation. `scan_history=False` is a bounded internal seam, not authority to
create, reserve, dispatch, execute, retry, or recover. Precreation compatibility
still reads the authoritative ID-derived KDAUTH path; validation of proposal
bytes from a non-authoritative review path remains deferred to the retained
protected KDAUTH-writer package. No mode releases a reserved identity or grants
retry/recovery authority.

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

## Protected KDAUTH writer and lifecycle append

`tools/canon_intake/dispatch_authorization_writer.py` implements the protected
crossing capability without creating a production authorization. Its public
writer accepts a regular non-symlink proposal path, an independently supplied
whole-file SHA-256, a fresh reservation-attempt ID, the exact approving actor,
and a repository root. The review hash is never inferred from a filename,
sidecar, Git object, authorization-core hash, target, or review packet.

Before locking, and again after acquiring the repository-wide KDAUTH crossing
lock, the writer rereads the proposal, checks byte-for-byte equality, validates
the complete KDAUTH contract from the review path, performs the current plus
retained precreation collision scan, and proves the ID-derived target absent.
The proposal bytes, including their one final LF, must equal the independent
review hash and length at both checks.

Under the same held lock the crossing order is fixed:

1. publish and prove one durable `attempt_reserved` through the reservation
   ledger's public lock-held API;
2. exclusive-create, flush/fsync, reread, and byte-compare the ID-derived
   KDAUTH target;
3. append, flush/fsync, reread, and validate exactly one
   `authorization_created` line whose whole-file hash and byte length equal the
   reviewed bytes;
4. validate the active writer-time lifecycle without weakening the four merged
   validator contexts;
5. append and prove one `crossing_committed` terminal whose raw lifecycle-line
   hash and length bind that exact creation line;
6. release the shared lock only after the terminal is proven.

A provably pre-append failure after reservation may restore the exact prior
lifecycle-audit bytes, prove target absence and rollback durability, and append
one `crossing_rolled_back_clean`. Partial writes, append uncertainty, fsync
uncertainty, terminal uncertainty, rollback uncertainty, or lock-cleanup
failure are integrity-critical. Evidence remains in place, identities remain
burned, and automatic retry, reuse, deletion of reservation history, rewrite,
or repair is forbidden.

The separate lifecycle append API acquires the same lock, rereads the exact
authoritative KDAUTH and complete audit, validates the closed state and
current-plus-retained history, derives the next event identity and sequence,
and appends one canonical terminal lifecycle line. Consumption additionally
requires an exact schema-valid durable dispatch record with matching KDAUTH,
queue, Gate-Q, run, runner, artifact, dataset, denominator, budget, execution,
and output bindings. This API does not implement the dispatch writer.

Read-only integrity visibility is exposed through
`v_integrity_dispatch_authorization_dispatch_without_consumption`. It emits
only for a valid canonical dispatch with an exact readable committed KDAUTH
when no exact matching `authorization_consumed` event exists. A mismatched
consumption event does not clear the finding. The view never creates or repairs
files and grants no authorization, dispatch, execution, runner, retry,
scientific-evidence, runtime, paper/live, or capital authority.

## Immutable dispatch record

Normative schema: `research/schemas/canon_dispatch_record.schema.json`.

The record MUST bind:

- its derived dispatch ID/path, creation timestamp, and the sole state `dispatched`;
- the exact manifest ID/path/hash/length, canonicalization, and locked
  derivation version;
- one exact admitted queue item ID/path and raw-file SHA-256;
- the exact Gate-Q ID/path, full-file SHA-256, core SHA-256, core scope, and canonicalization;
- one fresh exact Karl authorization, including its ID, source path/hash, actor, time, scope, queue item, dispatch ID, and run ID;
- one run ID and derived execution-stream path;
- structured runner module, source path, version, and source SHA-256, never a command string;
- exact Strategy Spec, Variant Manifest, Sweep Plan, and dataset identities and hashes;
- denominator, budget, seed, workers, one-shot/no-retry posture, and exact scratch/event output targets;
- immutable/single-use posture and the complete non-authority declaration.

The validator recomputes the complete record from manifest plus KDAUTH and
requires exact canonical byte equality. No writer-selected default, ambient
value, alternate leaf beneath an allowed root, or assertion of derivation is
accepted. The record MUST NOT contain progress, attempt outcomes, counts, a
terminal state, a mutable status, a retry instruction, a canonical Result
Population target, or a free-form executable command.
`dispatch_state="dispatched"` records only that the durable one-shot dispatch
crossing occurred; it does not mean a process started or finished.

Read-only durable-dispatch and execution-history inspection uses the historical
consumed-replay posture only after exact permanent consumption is proven.
Writer-time dispatch creation and consumption continue to use current-source
validation. No caller-facing generic bypass flag exists, and the historical
reader cannot create or consume a dispatch or invoke a runner.

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
- any later runner-adapter capability needed to consume a manifest-derived
  dispatch without broadening the merged canonical 1d route;
- the one-shot H-004-R2 dispatch and any later canonical Result Population handoff.

None may be inferred from this contract lock.

## Traceability

`WP-CANON-H004-DISPATCH-GATED-01` Stage A stopped at base
`1c22edf602f748ed03d9304c66b4b40cd6f0d601` because the repo had no durable
dispatch/execution-state contract. Its twelve preserved uncommitted evidence
files remain read-only. The canonical 1d route has since merged, but no
refreshed Stage A has created an exact production dispatch manifest. This
contract resolves non-circular representation and validation semantics only.
A real production manifest and KDAUTH remain impossible until a later
separately authorized refreshed Stage A and protected crossing package.
